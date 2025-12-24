import json

# Carregar dados
with open('arsenal_full_data.json', 'r', encoding='utf-8') as f:
    data_false = json.load(f)

with open('arsenal_detailed_true.json', 'r', encoding='utf-8') as f:
    data_true = json.load(f)

# Extrair Arsenal de ambos
def extract_arsenal(data):
    arsenal_data = {}
    categories = ['total', 'home', 'away', 'firstHalfTotal', 'firstHalfHome', 'fistHalfAway']
    
    for category in categories:
        if category in data and 'ranking' in data[category]:
            for team in data[category]['ranking']:
                if team.get('contestantCode') == 'ARS':
                    arsenal_data[category] = team
                    break
    return arsenal_data

arsenal_false = extract_arsenal(data_false)
arsenal_true = extract_arsenal(data_true)

print("=" * 80)
print("COMPARAÇÃO: detailed=false vs detailed=true")
print("=" * 80)

# Comparar campos
fields_false = set()
fields_true = set()

for category in arsenal_false.keys():
    fields_false.update(arsenal_false[category].keys())

for category in arsenal_true.keys():
    fields_true.update(arsenal_true[category].keys())

print(f"\nCampos com detailed=false: {len(fields_false)}")
print(f"Campos com detailed=true: {len(fields_true)}")

# Campos novos
new_fields = fields_true - fields_false
print(f"\nCAMPOS NOVOS com detailed=true: {len(new_fields)}")

if new_fields:
    print("\n" + "=" * 80)
    print("CAMPOS ADICIONAIS ENCONTRADOS:")
    print("=" * 80)
    
    for field in sorted(new_fields):
        # Pegar exemplo
        example = None
        for category in arsenal_true.keys():
            if field in arsenal_true[category]:
                example = arsenal_true[category][field]
                break
        
        value_type = type(example).__name__
        if isinstance(example, str):
            display_value = f'"{example}"'
        else:
            display_value = str(example)
        
        print(f"\n  {field}")
        print(f"    Tipo: {value_type}")
        print(f"    Exemplo: {display_value}")
else:
    print("\n⚠️ NENHUM CAMPO ADICIONAL encontrado com detailed=true")

# Mostrar estrutura completa do total com detailed=true
print("\n" + "=" * 80)
print("ESTRUTURA COMPLETA - Arsenal (total) com detailed=true:")
print("=" * 80)
print(json.dumps(arsenal_true.get('total', {}), indent=2, ensure_ascii=False))

