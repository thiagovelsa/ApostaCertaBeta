# 📊 Documentação Técnica: Sistema de Probabilidades (ApostaMestre)

> **Versão:** 2.0  
> **Última Atualização:** 2026-02-10  
> **Fonte de verdade:** Backend (`GET /api/partida/{match_id}/analysis`)

Este documento descreve **como o sistema calcula hoje** previsões e probabilidades.

**Dica (auditoria/IA):** use `GET /api/partida/{match_id}/analysis?debug=1` para incluir `debug_amostra` (IDs/datas/pesos) das partidas efetivamente usadas no recorte.

---

## 📋 Índice

1. Visão Geral
2. Onde o cálculo acontece (hardcut)
3. Previsões (λ) por métrica
4. Over/Under por distribuição
5. Ajuste Dixon-Coles (gols)
6. Negative Binomial (overdispersion)
7. Intervalo de confiança e incerteza
8. Referências

---

## 1) Visão Geral

O ApostaMestre calcula:

- **Previsões (valores esperados)** por métrica: gols, escanteios, finalizações, finalizações no gol, cartões amarelos e faltas.
- **Probabilidades Over/Under** para linhas dinâmicas.

Notas importantes (consistência/intervalos):
- O backend calcula **média e CV** a partir de partidas individuais com **time-weighting** (Dixon-Coles decay) e usa `cv` como proxy de incerteza.
- O payload inclui amostra por lado (`partidas_analisadas_mandante`/`partidas_analisadas_visitante`) e um `n` efetivo (`partidas_analisadas` = menor lado) usado na confiança/intervalos.
- Se não houver partidas individuais suficientes (ou a VStats falhar ao retornar stats por partida), o backend faz fallback para agregados de temporada e registra `seasonstats_fallback` em `contexto.ajustes_aplicados`.

Modelo atual por métrica:

- **Gols**: Poisson com correção **Dixon-Coles** (placares baixos).
- **Demais métricas**: **Negative Binomial** (recomendado para overdispersion).

---

## 2) Onde o cálculo acontece (hardcut)

**Hardcut implementado:** frontend não deve calcular previsões/probabilidades.

- Backend retorna um payload consolidado em `GET /api/partida/{match_id}/analysis`.
- Frontend consome `previsoes` e `over_under` diretamente.

Arquivos principais:

- Backend:
  - `backend/app/api/routes/stats.py` (endpoint `/analysis`)
  - `backend/app/services/analysis_service.py` (cálculo)
  - `backend/app/models/analysis.py` (DTOs Pydantic)
  - `backend/app/utils/league_params.py` (parâmetros por liga)
- Frontend:
  - `frontend/src/services/statsService.ts` (chama `/analysis`)
  - `frontend/src/components/organisms/StatsPanel.tsx` (usa `stats.previsoes` / `stats.over_under`)

---

## 3) Previsões (λ) por métrica

### 3.1 Fórmula base (feitos/sofridos)

Para métricas com **feitos/sofridos** (ex.: escanteios, finalizações):

```
λ_home = (mandante.feitos + visitante.sofridos) / 2
λ_away = (visitante.feitos + mandante.sofridos) / 2
λ_total = λ_home + λ_away
```

### 3.2 Métricas simples

Para métricas simples (ex.: cartões amarelos, faltas):

```
λ_home = mandante.media
λ_away = visitante.media
λ_total = λ_home + λ_away
```

### 3.3 Ajuste de mando (quando aplicável)

O ajuste de mando só é aplicado quando **nenhum** subfiltro de mando estiver ativo (ou seja, `home_mando` e `away_mando` não são enviados). Se qualquer subfiltro estiver definido, o ajuste é desativado porque a amostra já está segmentada por casa/fora.

- Gols: home * 1.08, away * 0.92
- Escanteios: home * 1.05, away * 0.97
- Finalizações: home * 1.06, away * 0.95
- Finalizações no gol: home * 1.06, away * 0.95
- Cartões: home * 0.95, away * 1.08
- Faltas: home * 0.96, away * 1.05

### 3.4 Gols (ataque/defesa relativo à média da liga)

Para gols, o λ é calculado via **força de ataque/defesa** relativa à média da liga (recomendação #3):

- `side_mean = league.goals_mean_total / 2`
- `attack = gols_feitos_media / side_mean`
- `def_weak = gols_sofridos_media / side_mean`

```
λ_home = base_home * home_attack * away_def_weak
λ_away = base_away * away_attack * home_def_weak
```

Onde `base_home/base_away` deriva da média da liga com vantagem de mando.

### 3.5 H2H (gols)

Para gols, o sistema combina o total previsto com a média H2H quando há amostra mínima:

- >= 10 jogos: w = 0.30
- >= 5 jogos: w = 0.15

```
total = (1 - w) * total + w * media_h2h
```

---

## 4) Over/Under por distribuição

O backend calcula linhas dinâmicas centradas na média e remove linhas “óbvias” (probabilidade >= 0.98) garantindo ao menos 1 linha.

---

## 5) Ajuste Dixon-Coles (gols)

Para gols, a probabilidade do placar (h,a) é:

```
P(h,a) = Poisson(h; λ_home) * Poisson(a; λ_away) * τ(h,a)
```

O fator τ (Dixon-Coles) corrige 0-0, 1-0, 0-1, 1-1 e depende do ρ por liga.

---

## 6) Negative Binomial (overdispersion)

Para métricas não-gols, o sistema usa Negative Binomial (recomendação #2).

Uma parametrização comum é:

```
Var = mu + alpha * mu^2
```

Onde `alpha` é estimado a partir de `mu` e de uma variância aproximada (usando CV combinado).

---

## 7) Intervalo de confiança e incerteza

Além do valor pontual de probabilidade, cada linha pode incluir:

- `ci_lower` / `ci_upper`: intervalo aproximado (95%)
- `uncertainty`: largura do intervalo (`ci_upper - ci_lower`)

O backend estima a incerteza por simulação Monte Carlo variando `mu` (Normal com `se`).

Onde:
- `n = stats.partidas_analisadas` (amostra efetiva = menor lado).
- `se ≈ (cv_med * mu) / sqrt(n)` quando `mu > 0`.

**Importante:** o backend **não infla `n`** com pisos artificiais (ex.: `max(3, n)`), para não subestimar incerteza quando a amostra real é 1 ou 2 jogos.

Quando `seasonstats_fallback` estiver ativo, o `cv` é estimado (não há dados por partida) e a UI deve tratar a base como **“Temporada (agregado)”**.

---

## 8) Referências

1. Dixon, M. J., & Coles, S. G. (1997). *Modelling Association Football Scores and Inefficiencies in the Football Betting Market*.
2. Negative Binomial como alternativa para contagens com overdispersion.
