"""Serviço que calcula previsões e probabilidades Over/Under para a UI.

Este serviço implementa as recomendações:
- Centralizar cálculo no backend
- Negative Binomial para métricas com overdispersion
- Lambda de gols ataque/defesa (relativo à média da liga)
- Confiança incorporando incerteza via simulação (Monte Carlo)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple



from ..models import StatsResponse
from ..models.analysis import (
    OverUnderLine,
    OverUnderPartida,
    OverUnderStat,
    PrevisaoEstatistica,
    PrevisaoPartida,
    PrevisaoValor,
)
from ..utils.league_params import get_league_params


MandoFilter = Optional[Literal["casa", "fora"]]


@dataclass(frozen=True)
class _StatConfig:
    label: str
    icon: str
    step: float
    apply_mando: bool


_STAT_CONFIG: Dict[str, _StatConfig] = {
    "gols": _StatConfig(label="Gols", icon="goal", step=1.0, apply_mando=True),
    "escanteios": _StatConfig(
        label="Escanteios", icon="corner", step=1.0, apply_mando=True
    ),
    "finalizacoes": _StatConfig(label="Chutes", icon="shot", step=2.0, apply_mando=True),
    "finalizacoes_gol": _StatConfig(
        label="Chutes ao Gol", icon="target", step=1.0, apply_mando=True
    ),
    "cartoes_amarelos": _StatConfig(label="Cartões", icon="card", step=1.0, apply_mando=True),
    "faltas": _StatConfig(label="Faltas", icon="foul", step=2.0, apply_mando=True),
}


# Mesmos fatores do frontend (predictions.ts)
_STAT_HOME_FACTORS: Dict[str, Tuple[float, float]] = {
    "gols": (1.08, 0.92),
    "escanteios": (1.05, 0.97),
    "finalizacoes": (1.06, 0.95),
    "finalizacoes_gol": (1.06, 0.95),
    "cartoes_amarelos": (0.95, 1.08),
    "faltas": (0.96, 1.05),
}


_FORM_FACTOR_RANGE = 0.05
_POSITION_FACTOR_RANGE = 0.05


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _poisson_pmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0

    # exp(k*log(lam) - lam - log(k!))
    return math.exp(k * math.log(lam) - lam - math.lgamma(k + 1))


def _negbin_cdf(n: int, r: float, p: float) -> float:
    """CDF da Negative Binomial em implementação pura.

    Parametrização compatível com scipy.stats.nbinom (n=r, p=p):
    - r: número de sucessos (pode ser não-inteiro)
    - p: probabilidade de sucesso
    """

    if n < 0:
        return 0.0
    if r <= 0:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0

    # pmf(k=0) = p^r
    pmf = math.exp(r * math.log(p))
    cdf = pmf
    for k in range(0, n):
        # pmf(k+1) = pmf(k) * (k+r)/(k+1) * (1-p)
        pmf *= ((k + r) / (k + 1)) * (1.0 - p)
        cdf += pmf

    return _clamp(cdf, 0.0, 1.0)


def _confianca_label(c: float) -> Literal["Baixa", "Média", "Alta"]:
    if c >= 0.70:
        return "Alta"
    if c >= 0.50:
        return "Média"
    return "Baixa"


def _calc_confidence_cv(cv: float, n: int) -> float:
    confianca = 1.0 - cv
    if n < 5:
        confianca *= 0.8
    elif n >= 15:
        confianca *= 1.15
    elif n >= 10:
        confianca *= 1.1

    return _clamp(confianca, 0.30, 0.95)


def _round1(v: float) -> float:
    return round(v, 1)


def _should_apply_mando_adjustment(home_mando: MandoFilter, away_mando: MandoFilter) -> bool:
    # Se qualquer subfiltro de mando estiver ativo, a amostra ja foi segmentada no StatsService
    # (ou no merge do endpoint). Evita duplo-viés ao aplicar multiplicadores de mando novamente.
    if home_mando is not None or away_mando is not None:
        return False
    return True


def _calculate_form_factor(recent_form: Optional[List[str]]) -> float:
    if not recent_form:
        return 1.0

    last5 = recent_form[:5]
    points = 0
    for r in last5:
        if r == "W":
            points += 3
        elif r == "D":
            points += 1

    max_points = len(last5) * 3
    ratio = points / max_points if max_points else 0.5
    return (1 - _FORM_FACTOR_RANGE) + ratio * (2 * _FORM_FACTOR_RANGE)


def _bayesian_shrinkage(value: float, n: int, prior: float, k: int = 3) -> float:
    return (n * value + k * prior) / (n + k) if n + k > 0 else value


def _generate_centered_lines(mu: float, step: float) -> List[float]:
    center_line = math.floor(mu / step) * step + (step / 2)
    return [
        max(step / 2, center_line - step),
        center_line,
        center_line + step,
        center_line + 2 * step,
    ]


def _generate_dynamic_lines(mu: float, step: float, max_lines: int = 4) -> List[float]:
    base_lines = _generate_centered_lines(mu, step)
    lines: List[float] = []

    increment = base_lines[1] - base_lines[0] if len(base_lines) > 1 else 1.0
    max_attempts = len(base_lines) * 6

    current = 0
    while len(lines) < max_lines and current < max_attempts:
        base_idx = current % len(base_lines)
        multiplier = current // len(base_lines)
        line = base_lines[base_idx] + multiplier * len(base_lines) * increment
        lines.append(line)
        current += 1

    return lines[:max_lines]


def _dixon_coles_tau(h: int, a: int, lh: float, la: float, rho: float) -> float:
    if h == 0 and a == 0:
        return 1 - lh * la * rho
    if h == 1 and a == 0:
        return 1 - la * rho
    if h == 0 and a == 1:
        return 1 - lh * rho
    if h == 1 and a == 1:
        return 1 - rho
    return 1.0


def _score_prob_dc(h: int, a: int, lh: float, la: float, rho: float) -> float:
    return _poisson_pmf(h, lh) * _poisson_pmf(a, la) * _dixon_coles_tau(h, a, lh, la, rho)


def _over_prob_goals_dc(line: float, lh: float, la: float, rho: float) -> float:
    n = int(math.floor(line))
    p_under = 0.0
    for h in range(n + 1):
        for a in range(n - h + 1):
            p_under += _score_prob_dc(h, a, lh, la, rho)
    return 1.0 - p_under


def _nb_params_from_mu_alpha(mu: float, alpha: float) -> Tuple[float, float]:
    if alpha <= 0 or mu <= 0:
        return (1.0, 0.999999)

    p = 1.0 / (1.0 + alpha * mu)
    r = mu * p / (1.0 - p) if p < 1.0 else mu
    return (r, p)


def _over_prob_negbin(line: float, mu: float, alpha: float) -> float:
    n = int(math.floor(line))
    r, p = _nb_params_from_mu_alpha(mu, alpha)
    return 1.0 - _negbin_cdf(n, r, p)


def _estimate_alpha_from_mu_var(mu: float, var: float) -> float:
    # Var = mu + alpha * mu^2
    if mu <= 0:
        return 0.0
    alpha = (var - mu) / (mu * mu)
    return max(0.0, alpha)


def _simulate_prob_ci(
    mu: float,
    se: float,
    line: float,
    calc_over,
    n_simulations: int = 3000,
) -> Tuple[float, float, float, float]:
    if se <= 0 or n_simulations <= 100:
        p = calc_over(line, mu)
        return (p, p, p, 0.0)

    probs: List[float] = []
    for _ in range(n_simulations):
        m = max(0.1, random.gauss(mu, se))
        try:
            probs.append(calc_over(line, m))
        except Exception:
            continue

    if not probs:
        return (0.5, 0.0, 1.0, 1.0)

    probs.sort()
    n = len(probs)
    mean = sum(probs) / n
    lo = probs[int(n * 0.025)]
    hi = probs[int(n * 0.975)]
    return (mean, lo, hi, hi - lo)


class AnalysisService:
    PROBABILITY_CUTOFF = 0.98
    MAX_LINES = 4
    # z-score para intervalo central de 90% (P5-P95) assumindo normal aproximado
    PRED_INTERVAL_Z = 1.6448536269514722

    def build_previsoes(
        self,
        stats: StatsResponse,
        home_mando: MandoFilter,
        away_mando: MandoFilter,
    ) -> PrevisaoPartida:
        competition = stats.partida.competicao
        league = get_league_params(competition)
        apply_mando = _should_apply_mando_adjustment(home_mando, away_mando)

        n = stats.partidas_analisadas

        def mark_adjustment(name: str) -> None:
            ctx = getattr(stats, "contexto", None)
            if not ctx:
                return
            if getattr(ctx, "ajustes_aplicados", None) is None:
                return
            if name not in ctx.ajustes_aplicados:
                ctx.ajustes_aplicados.append(name)

        def fatigue_multiplier(team: str) -> float:
            ctx = getattr(stats, "contexto", None)
            if not ctx:
                return 1.0

            team_ctx = getattr(ctx, team, None)
            if not team_ctx:
                return 1.0

            dias = getattr(team_ctx, "dias_descanso", None)
            jogos_14d = getattr(team_ctx, "jogos_14d", None)

            penalty = 0.0
            if isinstance(dias, int):
                if dias <= 2:
                    penalty += 0.06
                elif dias == 3:
                    penalty += 0.03
            if isinstance(jogos_14d, int) and jogos_14d >= 4:
                penalty += 0.04

            penalty = _clamp(penalty, 0.0, 0.10)
            if penalty > 0:
                mark_adjustment("descanso")
            return 1.0 - penalty

        home_form_factor = _calculate_form_factor(stats.mandante.recent_form)
        away_form_factor = _calculate_form_factor(stats.visitante.recent_form)

        def mk_valor(valor: float, cv: float) -> PrevisaoValor:
            conf = _calc_confidence_cv(cv, n)
            return PrevisaoValor(
                valor=_round1(valor),
                confianca=conf,
                confiancaLabel=_confianca_label(conf),
            )

        def feitos_sofridos(stat_key: str, feitos_cv_weight: float = 0.5) -> PrevisaoEstatistica:
            home_stat = getattr(stats.mandante.estatisticas, stat_key)
            away_stat = getattr(stats.visitante.estatisticas, stat_key)

            lambda_home = (home_stat.feitos.media + away_stat.sofridos.media) / 2.0
            lambda_away = (away_stat.feitos.media + home_stat.sofridos.media) / 2.0

            cv_home = (home_stat.feitos.cv + away_stat.sofridos.cv) / 2.0
            cv_away = (away_stat.feitos.cv + home_stat.sofridos.cv) / 2.0

            if apply_mando and _STAT_CONFIG[stat_key].apply_mando:
                hf, af = _STAT_HOME_FACTORS.get(stat_key, (1.0, 1.0))
                lambda_home *= hf
                lambda_away *= af

            # Priors por liga (por time = total/2)
            if stat_key == "gols":
                prior = league.goals_mean_total / 2.0
            elif stat_key == "escanteios":
                prior = league.corners_mean_total / 2.0
            elif stat_key == "finalizacoes" or stat_key == "faltas":
                prior = 12.0
            elif stat_key == "finalizacoes_gol":
                prior = 4.0
            else:
                prior = 1.8

            lambda_home = _bayesian_shrinkage(lambda_home, n, prior)
            lambda_away = _bayesian_shrinkage(lambda_away, n, prior)

            # Forma
            lambda_home *= home_form_factor
            lambda_away *= away_form_factor

            # Descanso/congestão (pre-jogo): aplica em métricas de volume, não em disciplina.
            if stat_key in ("gols", "escanteios", "finalizacoes", "finalizacoes_gol"):
                lambda_home *= fatigue_multiplier("mandante")
                lambda_away *= fatigue_multiplier("visitante")

            total = lambda_home + lambda_away
            cv_total = (cv_home + cv_away) / 2.0

            return PrevisaoEstatistica(
                home=mk_valor(lambda_home, cv_home),
                away=mk_valor(lambda_away, cv_away),
                total=mk_valor(total, cv_total),
            )

        def simples(stat_key: str) -> PrevisaoEstatistica:
            home_stat = getattr(stats.mandante.estatisticas, stat_key)
            away_stat = getattr(stats.visitante.estatisticas, stat_key)

            lambda_home = home_stat.media
            lambda_away = away_stat.media

            cv_home = home_stat.cv
            cv_away = away_stat.cv

            if apply_mando and _STAT_CONFIG[stat_key].apply_mando:
                hf, af = _STAT_HOME_FACTORS.get(stat_key, (1.0, 1.0))
                lambda_home *= hf
                lambda_away *= af

            # Priors
            if stat_key == "cartoes_amarelos":
                prior = league.cards_mean_total / 2.0
            elif stat_key == "faltas":
                prior = 12.0
            else:
                prior = 1.0

            lambda_home = _bayesian_shrinkage(lambda_home, n, prior)
            lambda_away = _bayesian_shrinkage(lambda_away, n, prior)

            # Ajuste árbitro para cartões
            if stat_key == "cartoes_amarelos" and stats.arbitro is not None:
                media_arbitro = stats.arbitro.media_cartoes_temporada or stats.arbitro.media_cartoes_amarelos
                partidas = stats.arbitro.partidas_temporada or stats.arbitro.partidas
                if partidas >= 5 and media_arbitro and league.cards_mean_total > 0:
                    fator = media_arbitro / league.cards_mean_total
                    fator = _clamp(fator, 0.5, 1.8)
                    lambda_home *= fator
                    lambda_away *= fator

            lambda_home *= home_form_factor
            lambda_away *= away_form_factor

            total = lambda_home + lambda_away
            cv_total = (cv_home + cv_away) / 2.0

            return PrevisaoEstatistica(
                home=mk_valor(lambda_home, cv_home),
                away=mk_valor(lambda_away, cv_away),
                total=mk_valor(total, cv_total),
            )

        # Gols com lambda ataque/defesa (recomendação #3)
        def gols_attack_defense() -> PrevisaoEstatistica:
            home_g = stats.mandante.estatisticas.gols
            away_g = stats.visitante.estatisticas.gols

            side_mean = league.goals_mean_total / 2.0 if league.goals_mean_total > 0 else 1.35

            if apply_mando:
                base_home = side_mean * league.home_advantage_factor
                base_away = max(0.1, league.goals_mean_total - base_home)
            else:
                base_home = side_mean
                base_away = side_mean

            home_attack = home_g.feitos.media / side_mean if side_mean > 0 else 1.0
            home_def_weak = home_g.sofridos.media / side_mean if side_mean > 0 else 1.0
            away_attack = away_g.feitos.media / side_mean if side_mean > 0 else 1.0
            away_def_weak = away_g.sofridos.media / side_mean if side_mean > 0 else 1.0

            # Classificação (standings): ajuste leve em ataque/defesa (clampado).
            ctx = getattr(stats, "contexto", None)
            if ctx and getattr(ctx, "classificacao_mandante", None) and getattr(ctx, "classificacao_visitante", None):
                try:
                    teams_count = max(int(getattr(league, "teams_count", 20) or 20), 2)
                    pos_h = int(ctx.classificacao_mandante.posicao)
                    pos_a = int(ctx.classificacao_visitante.posicao)

                    def strength(pos: int) -> float:
                        # 1 -> 1.0 ; last -> 0.0
                        return _clamp(1.0 - ((pos - 1) / (teams_count - 1)), 0.0, 1.0)

                    sh = strength(pos_h)
                    sa = strength(pos_a)

                    attack_mult_h = 0.94 + 0.12 * sh
                    attack_mult_a = 0.94 + 0.12 * sa
                    def_mult_h = 1.06 - 0.12 * sh
                    def_mult_a = 1.06 - 0.12 * sa

                    home_attack *= attack_mult_h
                    away_attack *= attack_mult_a
                    home_def_weak *= def_mult_h
                    away_def_weak *= def_mult_a

                    mark_adjustment("classificacao")
                except Exception:
                    pass

            lambda_home = base_home * home_attack * away_def_weak
            lambda_away = base_away * away_attack * home_def_weak

            cv_home = (home_g.feitos.cv + away_g.sofridos.cv) / 2.0
            cv_away = (away_g.feitos.cv + home_g.sofridos.cv) / 2.0

            prior = league.goals_mean_total / 2.0
            lambda_home = _bayesian_shrinkage(lambda_home, n, prior)
            lambda_away = _bayesian_shrinkage(lambda_away, n, prior)

            lambda_home *= home_form_factor
            lambda_away *= away_form_factor

            # Descanso/congestão (gols)
            lambda_home *= fatigue_multiplier("mandante")
            lambda_away *= fatigue_multiplier("visitante")

            # H2H (ajusta total, preserva propor��o)
            total = lambda_home + lambda_away
            # Nota: h2h_all_comps nem sempre existe no StatsResponse (retrocompatibilidade).
            h2h = getattr(stats, "h2h_all_comps", None)
            if h2h and getattr(h2h, "total_matches", 0) >= 5:
                w = 0.30 if h2h.total_matches >= 10 else 0.15
                total_h2h = getattr(h2h, "avg_goals_per_match", None)
                if total_h2h is None:
                    total_h2h = getattr(h2h, "avg_goals", None)
                if total_h2h is None:
                    total_h2h = getattr(h2h, "avg_total_goals", None)
                try:
                    total_h2h = float(total_h2h)
                except (TypeError, ValueError):
                    total_h2h = None
                if total_h2h is not None and total_h2h > 0:
                    total = (1 - w) * total + w * total_h2h
                    mark_adjustment("h2h")

            ratio = (
                lambda_home / (lambda_home + lambda_away)
                if (lambda_home + lambda_away) > 0
                else 0.5
            )
            lambda_home = total * ratio
            lambda_away = total * (1.0 - ratio)

            cv_total = (cv_home + cv_away) / 2.0
            return PrevisaoEstatistica(
                home=mk_valor(lambda_home, cv_home),
                away=mk_valor(lambda_away, cv_away),
                total=mk_valor(total, cv_total),
            )

        return PrevisaoPartida(
            gols=gols_attack_defense(),
            escanteios=feitos_sofridos("escanteios"),
            finalizacoes=feitos_sofridos("finalizacoes"),
            finalizacoes_gol=feitos_sofridos("finalizacoes_gol"),
            cartoes_amarelos=simples("cartoes_amarelos"),
            faltas=simples("faltas"),
        )

    def build_over_under(
        self,
        stats: StatsResponse,
        previsoes: PrevisaoPartida,
        home_mando: MandoFilter,
        away_mando: MandoFilter,
    ) -> OverUnderPartida:
        competition = stats.partida.competicao
        league = get_league_params(competition)

        # Intervalos/confiança devem refletir o "pior lado" quando há amostras diferentes.
        def _safe_int(v: object) -> Optional[int]:
            if v is None:
                return None
            try:
                return int(v)
            except (TypeError, ValueError):
                return None

        nh = _safe_int(getattr(stats, "partidas_analisadas_mandante", None))
        na = _safe_int(getattr(stats, "partidas_analisadas_visitante", None))
        n_eff = min(
            [v for v in (nh, na) if isinstance(v, int) and v > 0]
            or [int(getattr(stats, "partidas_analisadas", 1) or 1)]
        )
        # Importante: não inflar n (ex: max(3, ...)) pois isso subestima incerteza em amostras curtas.
        n = max(1, int(n_eff))

        def build_stat(stat_key: str) -> OverUnderStat:
            cfg = _STAT_CONFIG[stat_key]

            if stat_key == "gols":
                rho = league.dixon_coles_rho
                lh = max(0.1, previsoes.gols.home.valor)
                la = max(0.1, previsoes.gols.away.valor)
                mu = lh + la

                def calc_over(line: float, m: float) -> float:
                    ratio = lh / (lh + la) if (lh + la) > 0 else 0.5
                    lh2 = m * ratio
                    la2 = m * (1 - ratio)
                    return _over_prob_goals_dc(line, lh2, la2, rho)

                lines_raw = _generate_dynamic_lines(mu, cfg.step, self.MAX_LINES)
                lines: List[OverUnderLine] = []

                cv_home = (stats.mandante.estatisticas.gols.feitos.cv + stats.visitante.estatisticas.gols.sofridos.cv) / 2.0
                cv_away = (stats.visitante.estatisticas.gols.feitos.cv + stats.mandante.estatisticas.gols.sofridos.cv) / 2.0
                cv_med = (cv_home + cv_away) / 2.0
                se = (cv_med * mu) / math.sqrt(n) if mu > 0 else 0.0
                pred_min = max(0.0, mu - (self.PRED_INTERVAL_Z * se))
                pred_max = max(0.0, mu + (self.PRED_INTERVAL_Z * se))

                uncertainties = []
                for line in lines_raw:
                    mean, lo, hi, unc = _simulate_prob_ci(mu, se, line, lambda l,mm=mu: calc_over(l, mm))
                    under = 1.0 - mean
                    if mean >= self.PROBABILITY_CUTOFF or under >= self.PROBABILITY_CUTOFF:
                        continue
                    uncertainties.append(unc)
                    lines.append(
                        OverUnderLine(
                            line=line,
                            over=round(mean, 3),
                            under=round(under, 3),
                            ci_lower=round(_clamp(lo, 0.0, 1.0), 3),
                            ci_upper=round(_clamp(hi, 0.0, 1.0), 3),
                            uncertainty=round(unc, 3),
                        )
                    )

                if not lines and lines_raw:
                    line = lines_raw[len(lines_raw) // 2]
                    mean = calc_over(line, mu)
                    lines.append(
                        OverUnderLine(line=line, over=round(mean, 3), under=round(1.0 - mean, 3))
                    )
                    uncertainties.append(1.0)

                base_conf = _calc_confidence_cv(cv_med, n)
                avg_unc = sum(uncertainties) / len(uncertainties) if uncertainties else 0.0
                confidence = _clamp(base_conf * (1.0 - avg_unc), 0.30, 0.95)

                return OverUnderStat(
                    label=cfg.label,
                    icon=cfg.icon,
                    lambda_=round(mu, 2),
                    lambdaHome=round(lh, 2),
                    lambdaAway=round(la, 2),
                    predMin=round(pred_min, 2),
                    predMax=round(pred_max, 2),
                    intervalLevel=0.9,
                    sigma=None,
                    distribution="poisson",
                    lines=lines,
                    confidence=round(confidence, 2),
                    confidenceLabel=_confianca_label(confidence),
                )

            # Não-gols: Negative Binomial (recomendação #2)
            prev = getattr(previsoes, stat_key)
            lh = max(0.1, prev.home.valor)
            la = max(0.1, prev.away.valor)
            mu = max(0.1, lh + la)

            # Variância combinada via CV (independência) - similar ao frontend
            # var = (cv * mean)^2
            if stat_key in ("cartoes_amarelos", "faltas"):
                cv_home = getattr(stats.mandante.estatisticas, stat_key).cv
                cv_away = getattr(stats.visitante.estatisticas, stat_key).cv
            else:
                home_stat = getattr(stats.mandante.estatisticas, stat_key)
                away_stat = getattr(stats.visitante.estatisticas, stat_key)
                cv_home = (home_stat.feitos.cv + away_stat.sofridos.cv) / 2.0
                cv_away = (away_stat.feitos.cv + home_stat.sofridos.cv) / 2.0

            var_home = (cv_home * lh) ** 2
            var_away = (cv_away * la) ** 2
            var_total = var_home + var_away

            alpha = _estimate_alpha_from_mu_var(mu, var_total)

            def calc_over(line: float, m: float) -> float:
                return _over_prob_negbin(line, m, alpha)

            lines_raw = _generate_dynamic_lines(mu, cfg.step, self.MAX_LINES)
            lines: List[OverUnderLine] = []

            cv_med = (cv_home + cv_away) / 2.0
            se = (cv_med * mu) / math.sqrt(n) if mu > 0 else 0.0
            pred_min = max(0.0, mu - (self.PRED_INTERVAL_Z * se))
            pred_max = max(0.0, mu + (self.PRED_INTERVAL_Z * se))

            uncertainties = []
            for line in lines_raw:
                mean, lo, hi, unc = _simulate_prob_ci(mu, se, line, calc_over)
                under = 1.0 - mean
                if mean >= self.PROBABILITY_CUTOFF or under >= self.PROBABILITY_CUTOFF:
                    continue

                uncertainties.append(unc)
                lines.append(
                    OverUnderLine(
                        line=line,
                        over=round(mean, 3),
                        under=round(under, 3),
                        ci_lower=round(_clamp(lo, 0.0, 1.0), 3),
                        ci_upper=round(_clamp(hi, 0.0, 1.0), 3),
                        uncertainty=round(unc, 3),
                    )
                )

            if not lines and lines_raw:
                line = lines_raw[len(lines_raw) // 2]
                mean = calc_over(line, mu)
                lines.append(OverUnderLine(line=line, over=round(mean, 3), under=round(1.0 - mean, 3)))
                uncertainties.append(1.0)

            base_conf = _calc_confidence_cv(cv_med, n)
            avg_unc = sum(uncertainties) / len(uncertainties) if uncertainties else 0.0
            confidence = _clamp(base_conf * (1.0 - avg_unc), 0.30, 0.95)

            return OverUnderStat(
                label=cfg.label,
                icon=cfg.icon,
                lambda_=round(mu, 2),
                lambdaHome=round(lh, 2),
                lambdaAway=round(la, 2),
                predMin=round(pred_min, 2),
                predMax=round(pred_max, 2),
                intervalLevel=0.9,
                sigma=None,
                distribution="negbin",
                lines=lines,
                confidence=round(confidence, 2),
                confidenceLabel=_confianca_label(confidence),
            )

        return OverUnderPartida(
            gols=build_stat("gols"),
            escanteios=build_stat("escanteios"),
            finalizacoes=build_stat("finalizacoes"),
            finalizacoes_gol=build_stat("finalizacoes_gol"),
            cartoes_amarelos=build_stat("cartoes_amarelos"),
            faltas=build_stat("faltas"),
        )
