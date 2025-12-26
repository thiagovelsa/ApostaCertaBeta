#!/usr/bin/env python3
"""
Download de Logos de Times Europeus
====================================

Baixa logos de todos os times da 1a e 2a divisao das 6 maiores ligas europeias
usando a API gratuita do TheSportsDB.

Uso:
    python download_logos.py --all              # Baixar todas as ligas
    python download_logos.py --country england  # Baixar apenas Inglaterra
    python download_logos.py --dry-run          # Testar sem baixar
    python download_logos.py --delay 5          # Intervalo de 5 segundos
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

# Configuracao
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
DEFAULT_DELAY = 3  # segundos entre requisicoes
MAX_RETRIES = 3
BACKOFF_MULTIPLIER = 2
INITIAL_BACKOFF = 5  # segundos
TARGET_SIZE = 256  # pixels

# Diretorios
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent
LOGOS_DIR = PROJECT_DIR / "frontend" / "logos"
PROGRESS_FILE = LOGOS_DIR / ".progress.json"
INDEX_FILE = LOGOS_DIR / "index.json"

# Mapeamento de ligas (nomes exatos da API TheSportsDB)
LEAGUES = {
    "england": {
        "premier-league": "English Premier League",
        "championship": "English League Championship"
    },
    "germany": {
        "bundesliga": "German Bundesliga",
        "2-bundesliga": "German 2. Bundesliga"
    },
    "italy": {
        "serie-a": "Italian Serie A",
        "serie-b": "Italian Serie B"
    },
    "spain": {
        "la-liga": "Spanish La Liga",
        "la-liga-2": "Spanish La Liga 2"
    },
    "france": {
        "ligue-1": "French Ligue 1",
        "ligue-2": "French Ligue 2"
    },
    "portugal": {
        "primeira-liga": "Portuguese Primeira Liga",
        "liga-portugal-2": "Portuguese LigaPro"
    }
}


def slugify(text: str) -> str:
    """Converte texto para slug (nome de arquivo seguro)."""
    text = text.lower().strip()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def load_progress() -> Dict:
    """Carrega progresso de downloads anteriores."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"downloaded": [], "failed": [], "last_updated": None}


def save_progress(progress: Dict) -> None:
    """Salva progresso atual."""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def verify_league_exists(league_name: str) -> bool:
    """Verifica se uma liga existe na API antes de buscar times."""
    url = f"{BASE_URL}/search_all_teams.php"
    params = {"l": league_name}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        teams = data.get("teams", [])
        return teams is not None and len(teams) > 0
    except Exception:
        return False


def fetch_teams(league_name: str, delay: float) -> Optional[List[Dict]]:
    """Busca times de uma liga na API do TheSportsDB."""
    url = f"{BASE_URL}/search_all_teams.php"
    params = {"l": league_name}

    for attempt in range(MAX_RETRIES):
        try:
            print(f"  Buscando times de '{league_name}'...")
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 429:
                backoff = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
                print(f"  [!] Rate limit! Aguardando {backoff}s...")
                time.sleep(backoff)
                continue

            response.raise_for_status()
            data = response.json()

            teams = data.get("teams", [])
            if teams:
                print(f"  [OK] Encontrados {len(teams)} times")
                time.sleep(delay)
                return teams
            else:
                print(f"  [!] Nenhum time encontrado para '{league_name}'")
                return []

        except requests.exceptions.RequestException as e:
            backoff = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
            print(f"  [!] Erro: {e}. Tentando novamente em {backoff}s...")
            time.sleep(backoff)

    print(f"  [X] Falha apos {MAX_RETRIES} tentativas")
    return None


def fetch_team_details(team_name: str, delay: float) -> Optional[Dict]:
    """Busca detalhes de um time especifico (inclui URL do badge)."""
    url = f"{BASE_URL}/searchteams.php"
    params = {"t": team_name}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 429:
                backoff = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
                print(f"    [!] Rate limit! Aguardando {backoff}s...")
                time.sleep(backoff)
                continue

            response.raise_for_status()
            data = response.json()

            teams = data.get("teams", [])
            if teams:
                time.sleep(delay)
                return teams[0]
            return None

        except requests.exceptions.RequestException as e:
            backoff = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
            if attempt < MAX_RETRIES - 1:
                time.sleep(backoff)

    return None


def download_logo(url: str, dest_path: Path, delay: float) -> bool:
    """Baixa um logo de uma URL."""
    if not url:
        return False

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=30, stream=True)

            if response.status_code == 429:
                backoff = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
                print(f"    [!] Rate limit! Aguardando {backoff}s...")
                time.sleep(backoff)
                continue

            response.raise_for_status()

            # Salvar arquivo
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            time.sleep(delay)
            return True

        except requests.exceptions.RequestException as e:
            backoff = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt)
            if attempt < MAX_RETRIES - 1:
                print(f"    [!] Erro: {e}. Tentando novamente em {backoff}s...")
                time.sleep(backoff)

    return False


def process_league(
    country: str,
    league_slug: str,
    league_name: str,
    progress: Dict,
    index_data: Dict,
    delay: float,
    dry_run: bool = False
) -> Tuple[int, int]:
    """Processa uma liga: busca times e baixa logos."""
    print(f"\n{'='*60}")
    print(f"Liga: {league_name} ({country}/{league_slug})")
    print('='*60)

    teams = fetch_teams(league_name, delay)
    if teams is None:
        return 0, 1

    success_count = 0
    fail_count = 0

    for team in teams:
        team_name = team.get("strTeam", "Unknown")
        team_id = team.get("idTeam", "")

        team_slug = slugify(team_name)
        file_path = f"{country}/{league_slug}/{team_slug}.png"
        full_path = LOGOS_DIR / file_path

        # Verificar se ja foi baixado
        if file_path in progress.get("downloaded", []):
            print(f"  [SKIP] {team_name} (ja baixado)")
            continue

        if dry_run:
            print(f"  [DRY] {team_name} -> {file_path}")
            success_count += 1
            continue

        # Buscar detalhes do time para obter URL do badge
        print(f"  Buscando: {team_name}...", end=" ", flush=True)
        team_details = fetch_team_details(team_name, delay)

        if not team_details:
            print("[NAO ENCONTRADO]")
            progress.setdefault("failed", []).append({
                "team": team_name,
                "reason": "team_not_found",
                "league": league_name
            })
            fail_count += 1
            save_progress(progress)
            continue

        # Usar strBadge (nao strTeamBadge)
        badge_url = team_details.get("strBadge", "")
        team_id = team_details.get("idTeam", team_id)

        if not badge_url:
            print("[SEM BADGE]")
            progress.setdefault("failed", []).append({
                "team": team_name,
                "reason": "no_badge_url",
                "league": league_name
            })
            fail_count += 1
            save_progress(progress)
            continue

        print(f"Baixando...", end=" ", flush=True)

        if download_logo(badge_url, full_path, delay):
            print("[OK]")
            progress.setdefault("downloaded", []).append(file_path)

            # Adicionar ao indice
            index_data["teams"][team_slug] = {
                "name": team_name,
                "country": country,
                "league": league_slug,
                "file": file_path,
                "thesportsdb_id": team_id
            }

            success_count += 1
            save_progress(progress)
        else:
            print("[FALHOU]")
            progress.setdefault("failed", []).append({
                "team": team_name,
                "reason": "download_failed",
                "url": badge_url
            })
            fail_count += 1
            save_progress(progress)

    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description="Download de logos de times europeus via TheSportsDB"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Baixar todas as ligas"
    )
    parser.add_argument(
        "--country",
        type=str,
        choices=list(LEAGUES.keys()),
        help="Baixar apenas um pais especifico"
    )
    parser.add_argument(
        "--league",
        type=str,
        help="Baixar apenas uma liga especifica (ex: premier-league)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Intervalo entre requisicoes em segundos (default: {DEFAULT_DELAY})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular sem baixar arquivos"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Ignorar progresso anterior e comecar do zero"
    )

    args = parser.parse_args()

    if not (args.all or args.country or args.league):
        parser.print_help()
        print("\n[!] Especifique --all, --country ou --league")
        sys.exit(1)

    # Carregar ou resetar progresso
    if args.reset:
        progress = {"downloaded": [], "failed": [], "last_updated": None}
        print("[!] Progresso resetado")
    else:
        progress = load_progress()
        if progress.get("downloaded"):
            print(f"[i] Retomando: {len(progress['downloaded'])} logos ja baixados")

    # Inicializar indice
    if INDEX_FILE.exists() and not args.reset:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = {
            "teams": {},
            "metadata": {
                "total_teams": 0,
                "generated_at": None,
                "source": "TheSportsDB"
            }
        }

    # Determinar quais ligas processar
    leagues_to_process = []

    if args.all:
        for country, leagues in LEAGUES.items():
            for league_slug, league_name in leagues.items():
                leagues_to_process.append((country, league_slug, league_name))
    elif args.country:
        if args.country in LEAGUES:
            for league_slug, league_name in LEAGUES[args.country].items():
                if not args.league or args.league == league_slug:
                    leagues_to_process.append((args.country, league_slug, league_name))
    elif args.league:
        for country, leagues in LEAGUES.items():
            if args.league in leagues:
                leagues_to_process.append((country, args.league, leagues[args.league]))
                break

    if not leagues_to_process:
        print("[!] Nenhuma liga encontrada com os parametros especificados")
        sys.exit(1)

    # VERIFICAR TODAS AS LIGAS ANTES DE INICIAR
    print(f"\n{'#'*60}")
    print("# Verificando ligas na API...")
    print(f"{'#'*60}")

    valid_leagues = []
    invalid_leagues = []

    for country, league_slug, league_name in leagues_to_process:
        print(f"  Verificando: {league_name}...", end=" ", flush=True)
        if verify_league_exists(league_name):
            print("[OK]")
            valid_leagues.append((country, league_slug, league_name))
        else:
            print("[NAO ENCONTRADA]")
            invalid_leagues.append((country, league_slug, league_name))
        time.sleep(1)  # Pequeno delay entre verificacoes

    if invalid_leagues:
        print(f"\n[!] ATENCAO: {len(invalid_leagues)} liga(s) nao encontrada(s):")
        for country, league_slug, league_name in invalid_leagues:
            print(f"    - {league_name} ({country}/{league_slug})")

        if not valid_leagues:
            print("\n[X] Nenhuma liga valida encontrada. Abortando.")
            sys.exit(1)

        print(f"\n[i] Continuando com {len(valid_leagues)} liga(s) valida(s)...")

    leagues_to_process = valid_leagues

    print(f"\n{'#'*60}")
    print(f"# Download de Logos - TheSportsDB")
    print(f"# Ligas validas: {len(leagues_to_process)}")
    print(f"# Intervalo: {args.delay}s entre requisicoes")
    print(f"# Modo: {'DRY-RUN (simulacao)' if args.dry_run else 'DOWNLOAD'}")
    print(f"{'#'*60}")

    total_success = 0
    total_fail = 0

    for country, league_slug, league_name in leagues_to_process:
        success, fail = process_league(
            country,
            league_slug,
            league_name,
            progress,
            index_data,
            args.delay,
            args.dry_run
        )
        total_success += success
        total_fail += fail

    # Salvar indice final
    if not args.dry_run:
        index_data["metadata"]["total_teams"] = len(index_data["teams"])
        index_data["metadata"]["generated_at"] = datetime.now().isoformat()

        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Indice salvo: {INDEX_FILE}")

    # Resumo final
    print(f"\n{'='*60}")
    print("RESUMO")
    print('='*60)
    print(f"Logos baixados: {total_success}")
    print(f"Falhas: {total_fail}")
    print(f"Total no indice: {len(index_data['teams'])}")

    if progress.get("failed"):
        print(f"\nTimes com problemas ({len(progress['failed'])}):")
        for item in progress["failed"][-10:]:  # Ultimos 10
            print(f"  - {item.get('team', 'N/A')}: {item.get('reason', 'unknown')}")

    print(f"\nArquivos:")
    print(f"  Logos: {LOGOS_DIR}")
    print(f"  Indice: {INDEX_FILE}")
    print(f"  Progresso: {PROGRESS_FILE}")


if __name__ == "__main__":
    main()
