"""
Validacao de Seasonstats - Filtro "Geral"
=========================================
Valida todas as estatisticas disponiveis no endpoint seasonstats
para confirmar que os campos esperados existem.

Data: 24/12/2025
Referencia: PROJETO_SISTEMA_ANALISE.md secao 4.1 e 11
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass

BASE_URL = "https://vstats-back-bbdfdf0bfd16.herokuapp.com/api"

# IDs de teste
ARSENAL_ID = "4dsgumo7d4zupm2ugsvm4zm4d"
PREMIER_LEAGUE_2025_26 = "51r6ph2woavlbbpk8f29nynf8"


@dataclass
class FieldValidation:
    """Resultado da validacao de um campo"""
    field_name: str
    display_name: str
    expected: bool
    found: bool
    value: Optional[str]
    average: Optional[float]
    status: str  # "OK", "MISSING", "NOT_EXPECTED"


# Campos ESPERADOS no seasonstats
EXPECTED_FIELDS = {
    "Corners Won": "Escanteios Feitos",
    "Goals": "Gols Feitos",
    "Goals Conceded": "Gols Sofridos",
    "Total Shots": "Finalizacoes",
    "Total Shots Conceded": "Finalizacoes Sofridas",
    "Shots On Target ( inc goals )": "Finalizacoes ao Gol",  # Nome correto com espacos
    "Shots On Conceded Inside Box": "Finalizacoes ao Gol Sofridas (Dentro)",
    "Shots On Conceded Outside Box": "Finalizacoes ao Gol Sofridas (Fora)",
    "Yellow Cards": "Cartoes Amarelos",
}

# Campos opcionais (podem nao existir se valor for 0)
OPTIONAL_FIELDS = {
    "Red Cards": "Cartoes Vermelhos",  # Pode nao existir se time nao recebeu
}

# Campos que NAO devem existir (documentar claramente)
NOT_EXPECTED_FIELDS = {
    "Corners Conceded": "Escanteios Sofridos",
    "Lost Corners": "Escanteios Sofridos (alt)",
}


def fetch_seasonstats(team_id: str, tournament_id: str) -> Optional[Dict]:
    """Busca seasonstats de um time"""
    url = f"{BASE_URL}/stats/seasonstats/v1/team"
    params = {
        "ctst": team_id,
        "tmcl": tournament_id,
        "detailed": "yes"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro: Status {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar seasonstats: {e}")
        return None


def parse_stats(data: Dict) -> Dict[str, Dict]:
    """Converte array de stats em dicionario indexado por nome"""
    stats = {}
    for stat in data.get('stat', []):
        name = stat.get('name', '')
        stats[name] = {
            'value': stat.get('value', '0'),
            'average': float(stat.get('average', 0))
        }
    return stats


def validate_fields(stats: Dict[str, Dict]) -> List[FieldValidation]:
    """Valida presenca de todos os campos esperados"""
    validations = []

    # Validar campos esperados (obrigatorios)
    for field_name, display_name in EXPECTED_FIELDS.items():
        if field_name in stats:
            validations.append(FieldValidation(
                field_name=field_name,
                display_name=display_name,
                expected=True,
                found=True,
                value=stats[field_name]['value'],
                average=stats[field_name]['average'],
                status="OK"
            ))
        else:
            validations.append(FieldValidation(
                field_name=field_name,
                display_name=display_name,
                expected=True,
                found=False,
                value=None,
                average=None,
                status="MISSING"
            ))

    # Validar campos opcionais
    for field_name, display_name in OPTIONAL_FIELDS.items():
        if field_name in stats:
            validations.append(FieldValidation(
                field_name=field_name,
                display_name=display_name,
                expected=True,
                found=True,
                value=stats[field_name]['value'],
                average=stats[field_name]['average'],
                status="OK"
            ))
        else:
            validations.append(FieldValidation(
                field_name=field_name,
                display_name=display_name + " (opcional - time sem ocorrencias)",
                expected=True,
                found=False,
                value="0",
                average=0.0,
                status="OPTIONAL_MISSING"
            ))

    # Verificar campos que NAO devem existir
    for field_name, display_name in NOT_EXPECTED_FIELDS.items():
        if field_name in stats:
            validations.append(FieldValidation(
                field_name=field_name,
                display_name=display_name,
                expected=False,
                found=True,
                value=stats[field_name]['value'],
                average=stats[field_name]['average'],
                status="UNEXPECTED_FOUND"
            ))
        else:
            validations.append(FieldValidation(
                field_name=field_name,
                display_name=display_name,
                expected=False,
                found=False,
                value=None,
                average=None,
                status="NOT_EXPECTED"
            ))

    return validations


def print_report(validations: List[FieldValidation], team_name: str) -> None:
    """Imprime relatorio formatado"""
    print("\n" + "=" * 72)
    print("VALIDACAO: SEASONSTATS (FILTRO GERAL)")
    print("=" * 72)
    print(f"Time: {team_name}")
    print(f"Competicao: Premier League 2025/26")
    print("=" * 72)

    # Campos esperados
    print("\n--- CAMPOS ESPERADOS (DEVEM EXISTIR) ---\n")

    ok_count = 0
    optional_count = 0
    missing_count = 0

    for v in validations:
        if v.expected:
            if v.status == "OK":
                ok_count += 1
                print(f"[OK] {v.display_name}")
                print(f"     Campo: {v.field_name}")
                print(f"     Valor: {v.value} | Media: {v.average:.2f}")
                print()
            elif v.status == "OPTIONAL_MISSING":
                optional_count += 1
                print(f"[OK] {v.display_name}")
                print(f"     Campo: {v.field_name}")
                print(f"     Valor: 0 (time sem ocorrencias - OK)")
                print()
            else:
                missing_count += 1
                print(f"[MISSING] {v.display_name}")
                print(f"     Campo: {v.field_name}")
                print(f"     Status: NAO ENCONTRADO")
                print()

    # Campos que nao devem existir
    print("\n--- CAMPOS NAO ESPERADOS (DOCUMENTADOS) ---\n")

    for v in validations:
        if not v.expected:
            if v.status == "NOT_EXPECTED":
                print(f"[ESPERADO] {v.display_name}")
                print(f"     Campo: {v.field_name}")
                print(f"     Status: NAO ENCONTRADO (conforme esperado)")
                print(f"     Solucao: Agregar via get-match-stats")
                print()
            else:
                print(f"[INESPERADO] {v.display_name}")
                print(f"     Campo: {v.field_name}")
                print(f"     Status: ENCONTRADO (nao esperado!)")
                print(f"     Valor: {v.value} | Media: {v.average:.2f}")
                print()

    # Resumo
    total_expected = len(EXPECTED_FIELDS) + len(OPTIONAL_FIELDS)
    total_ok = ok_count + optional_count

    print("=" * 72)
    print(f"RESULTADO: {total_ok}/{total_expected} campos CONFIRMADOS ({100*total_ok/total_expected:.0f}%)")
    if optional_count > 0:
        print(f"         ({ok_count} presentes + {optional_count} opcionais sem ocorrencias)")
    print("=" * 72)

    if missing_count == 0:
        print("\nVALIDACAO BEM-SUCEDIDA - FILTRO GERAL PRONTO!")
    else:
        print(f"\nATENCAO: {missing_count} campo(s) faltando!")

    print("=" * 72)


def main():
    """Execucao principal"""
    print("=" * 72)
    print("INICIANDO VALIDACAO DE SEASONSTATS")
    print("=" * 72)

    # 1. Buscar dados
    print("\n1. Buscando dados da API...")
    data = fetch_seasonstats(ARSENAL_ID, PREMIER_LEAGUE_2025_26)

    if not data:
        print("[ERRO] Falha ao buscar dados da API")
        return False

    team_name = data.get('name', 'Arsenal')
    print(f"   [OK] Dados recebidos: {team_name}")

    # 2. Parsear estatisticas
    print("\n2. Parseando estatisticas...")
    stats = parse_stats(data)
    print(f"   [OK] Total de campos encontrados: {len(stats)}")

    # 3. Validar campos
    print("\n3. Validando campos...")
    validations = validate_fields(stats)
    print(f"   [OK] Validacao completa")

    # 4. Imprimir relatorio
    print_report(validations, team_name)

    # Verificar se todos os campos esperados foram encontrados
    missing_count = sum(1 for v in validations if v.expected and v.status == "MISSING")
    return missing_count == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
