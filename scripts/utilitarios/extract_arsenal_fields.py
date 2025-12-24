import json

with open('arsenal_full_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extrair Arsenal de cada categoria
arsenal_data = {}
categories = ['total', 'home', 'away', 'firstHalfTotal', 'firstHalfHome', 'fistHalfAway']

for category in categories:
    if category in data and 'ranking' in data[category]:
        for team in data[category]['ranking']:
            if team.get('contestantCode') == 'ARS':
                arsenal_data[category] = team
                break

# Coletar todos os campos únicos
all_fields = set()
for category, team_data in arsenal_data.items():
    all_fields.update(team_data.keys())

# Criar documento com todos os campos
print("=" * 80)
print("TODOS OS CAMPOS RETORNADOS PELA API PARA UM TIME")
print("=" * 80)
print(f"\nTotal de campos únicos: {len(all_fields)}")
print(f"Categorias disponíveis: {len(arsenal_data)}")
print("\n" + "=" * 80)

# Mostrar campos com exemplos de cada categoria
print("\n### CAMPOS POR CATEGORIA ###\n")

for category in categories:
    if category in arsenal_data:
        print(f"\n--- {category.upper()} ---")
        team_data = arsenal_data[category]
        
        for field in sorted(team_data.keys()):
            value = team_data[field]
            value_type = type(value).__name__
            
            # Formatar valor
            if isinstance(value, str):
                display_value = f'"{value}"'
            else:
                display_value = str(value)
            
            print(f"  {field:25s} ({value_type:8s}): {display_value}")

# Lista consolidada de todos os campos
print("\n" + "=" * 80)
print("\n### LISTA COMPLETA DE CAMPOS (ALFABÉTICA) ###\n")

for field in sorted(all_fields):
    # Pegar exemplo do primeiro lugar onde aparece
    example = None
    for category in categories:
        if category in arsenal_data and field in arsenal_data[category]:
            example = arsenal_data[category][field]
            break
    
    value_type = type(example).__name__
    if isinstance(example, str):
        display_value = f'"{example}"'
    else:
        display_value = str(example)
    
    print(f"  {field:25s} ({value_type:8s}): {display_value}")

print("\n" + "=" * 80)
print("\n### ESTRUTURA COMPLETA DO ARSENAL FC ###\n")
print(json.dumps(arsenal_data['total'], indent=2, ensure_ascii=False))

