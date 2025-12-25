"""
Constantes da Aplicacao
=======================

Valores fixos utilizados em toda a aplicacao.
"""

# Limiares para classificacao do Coeficiente de Variacao
CV_THRESHOLDS = {
    "muito_estavel": 0.15,
    "estavel": 0.30,
    "moderado": 0.50,
    "instavel": 0.75,
}

# IDs de Competicoes Suportadas (VStats API) - Temporada 2025/26
# Referencia: DOCUMENTACAO_VSTATS_COMPLETA.md Secao 3
# ATENCAO: IDs mudam a cada temporada! Verificar via /stats/tournament/v1/calendar
TOURNAMENT_IDS = {
    # Inglaterra - Premier League 2025/26 (2025-08-15 a 2026-05-24)
    "premier_league": "51r6ph2woavlbbpk8f29nynf8",
    # Espanha - La Liga 2025/26 (2025-08-15 a 2026-05-24)
    "la_liga": "80zg2v1cuqcfhphn56u4qpyqc",
    # Italia - Serie A 2025/26 (2025-08-23 a 2026-05-24)
    "serie_a": "emdmtfr1v8rey2qru3xzfwges",
    # Alemanha - Bundesliga 2025/26 (2025-08-22 a 2026-05-16)
    "bundesliga": "2bchmrj23l9u42d68ntcekob8",
    # Franca - Ligue 1 2025/26 (2025-08-15 a 2026-05-16)
    "ligue_1": "dbxs75cag7zyip5re0ppsanmc",
    # Competicoes Europeias UEFA 2025/26
    "champions_league": "2mr0u0l78k2gdsm79q56tb2fo",
    "europa_league": "7ttpe5jzya3vjhjadiemjy7mc",
}

# Lista de competicoes ativas (para endpoint /api/competicoes)
ACTIVE_COMPETITIONS = [
    {
        "id": TOURNAMENT_IDS["premier_league"],
        "nome": "Premier League",
        "pais": "Inglaterra",
        "tipo": "Liga",
    },
    {
        "id": TOURNAMENT_IDS["la_liga"],
        "nome": "La Liga",
        "pais": "Espanha",
        "tipo": "Liga",
    },
    {
        "id": TOURNAMENT_IDS["serie_a"],
        "nome": "Serie A",
        "pais": "Italia",
        "tipo": "Liga",
    },
    {
        "id": TOURNAMENT_IDS["bundesliga"],
        "nome": "Bundesliga",
        "pais": "Alemanha",
        "tipo": "Liga",
    },
    {
        "id": TOURNAMENT_IDS["ligue_1"],
        "nome": "Ligue 1",
        "pais": "Franca",
        "tipo": "Liga",
    },
    {
        "id": TOURNAMENT_IDS["champions_league"],
        "nome": "UEFA Champions League",
        "pais": "Europa",
        "tipo": "Copa",
    },
    {
        "id": TOURNAMENT_IDS["europa_league"],
        "nome": "UEFA Europa League",
        "pais": "Europa",
        "tipo": "Copa",
    },
]

# Mapeamento de estatisticas VStats -> nomes amigaveis
STAT_NAMES = {
    # Estatisticas Feitas
    "goals": "Gols",
    "wonCorners": "Escanteios",
    "totalScoringAtt": "Finalizacoes",
    "ontargetScoringAtt": "Finalizacoes no Gol",
    "totalYellowCard": "Cartoes Amarelos",
    "totalRedCard": "Cartoes Vermelhos",
    "fkFoulLost": "Faltas Cometidas",
    "saves": "Defesas",
    # Estatisticas Sofridas
    "goalsConceded": "Gols Sofridos",
    "lostCorners": "Escanteios Sofridos",
    "fkFoulWon": "Faltas Sofridas",
    "penaltyConceded": "Penaltis Concedidos",
}

# Categorias de estatisticas para exibicao
STAT_CATEGORIES = {
    "ataque": ["goals", "totalScoringAtt", "ontargetScoringAtt"],
    "defesa": ["goalsConceded", "saves"],
    "corners": ["wonCorners", "lostCorners"],
    "disciplina": ["totalYellowCard", "totalRedCard", "fkFoulLost"],
}

# Timeouts padrao para APIs externas (em segundos)
API_TIMEOUTS = {
    "vstats": 10,
    "thesportsdb": 5,
}
