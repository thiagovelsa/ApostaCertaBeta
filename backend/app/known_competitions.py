"""
Known Competitions Fallback
===========================

Lista de competicoes conhecidas como fallback caso a API /calendar falhe.
IDs atualizados em 31/12/2025 via endpoint /stats/tournament/v1/calendar.
"""

# Competicoes principais com IDs da temporada 2025/2026
KNOWN_COMPETITIONS = [
    # Inglaterra
    {"id": "51r6ph2woavlbbpk8f29nynf8", "name": "Premier League", "country": "England"},
    {"id": "8v84l9nq3d5t0j4gb781i3l5c", "name": "Championship", "country": "England"},
    {"id": "7owam6thtzfmxox48uwh6j4sc", "name": "League One", "country": "England"},
    {"id": "bmmk637l2a33h90zlu36kx820", "name": "League Two", "country": "England"},
    
    # Espanha
    {"id": "80zg2v1cuqcfhphn56u4qpyqc", "name": "La Liga", "country": "Spain"},
    {"id": "4u7yjlhbahpojm39h34fh4yb0", "name": "La Liga 2", "country": "Spain"},
    
    # Italia
    {"id": "2ew4nzq478lpq23vujr5xpvw0", "name": "Serie A", "country": "Italy"},
    {"id": "16nwpdlqg8y6l8uj3o5hzn24x", "name": "Serie B", "country": "Italy"},
    
    # Alemanha
    {"id": "43gdfxo5fzg8x200pimtrz2e8", "name": "Bundesliga", "country": "Germany"},
    {"id": "1gq1cib9q3m02e0xwqgmyg6mo", "name": "2. Bundesliga", "country": "Germany"},
    
    # Franca
    {"id": "18r1kkgqn96c8xfbxlzf9l5go", "name": "Ligue 1", "country": "France"},
    {"id": "5kvx0lp2k3ck5qltkujyrqbf8", "name": "Ligue 2", "country": "France"},
    
    # Portugal
    {"id": "3mmqmb12j0e22c07zfjtq54lk", "name": "Primeira Liga", "country": "Portugal"},
    
    # Holanda
    {"id": "bu19nv0dq9ypylqomlvfnvw0", "name": "Eredivisie", "country": "Netherlands"},
    
    # Belgica
    {"id": "8xvywwxn3ofl9p9aw5t16xbgk", "name": "Pro League", "country": "Belgium"},
    
    # Turquia
    {"id": "4c75e7ewu3mzfwu6zwobkecqc", "name": "Super Lig", "country": "Turkey"},
    
    # Brasil
    {"id": "2blxf8tldvfwl2y5j83qodksc", "name": "Brasileirao Serie A", "country": "Brazil"},
    
    # USA
    {"id": "6i6n0jkbh9zzij6s8hq9cnvyo", "name": "Major League Soccer", "country": "USA"},
]


def get_fallback_competitions():
    """Retorna lista de competicoes conhecidas para fallback."""
    return KNOWN_COMPETITIONS.copy()
