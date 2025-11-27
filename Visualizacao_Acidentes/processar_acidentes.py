import os
from pathlib import Path
import pandas as pd
import unicodedata
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV = BASE_DIR / 'Visualizacao_Acidentes' / 'acidentes2024 (1) - acidentes2024 (1).csv'

csv_path_env = os.getenv('ACIDENTES_CSV_PATH')
if csv_path_env:
    acidentes_csv_path = Path(csv_path_env)
    if not acidentes_csv_path.is_absolute():
        acidentes_csv_path = BASE_DIR / acidentes_csv_path
else:
    acidentes_csv_path = DEFAULT_CSV

df_acidentes = pd.read_csv(acidentes_csv_path, encoding='utf-8')

print(f"Total de acidentes: {len(df_acidentes)}")
print(f"\nColunas: {df_acidentes.columns.tolist()}")
print(f"\nPrimeiras linhas:")
print(df_acidentes.head())


def normalizar_nome(texto):
    if pd.isna(texto):
        return ''
    texto = str(texto).strip()

    
    mapeamentos_especiais = {
        'Sitio dos Pintos   Sao Bras': 'Sítio dos Pintos',
        'Cohab   Ibura de Cima': 'Cohab',
        'Alto do Mandu   Sitio Grande': 'Alto do Mandu',
        'BAIRRO DO RECIFE': 'Recife',
        'POCO DA PANELA': 'Poço'
    }

    if texto in mapeamentos_especiais:
        texto = mapeamentos_especiais[texto]

    
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    
    normalizado = ' '.join(sem_acento.split())
    
    normalizado = normalizado.replace('Terezinha', 'Teresinha')
    normalizado = normalizado.replace('TEREZINHA', 'TERESINHA')
    
    return normalizado.title()


df_acidentes['bairro_normalizado'] = df_acidentes['bairro'].apply(normalizar_nome)


df_bairros_grafo = pd.read_csv('data/bairros_unique.csv', encoding='utf-8-sig', sep=';')
df_bairros_grafo['bairro_normalizado'] = df_bairros_grafo['bairro'].apply(normalizar_nome)


microrregiao_dict = {}
for _, row in df_bairros_grafo.iterrows():
    microrregiao_dict[row['bairro_normalizado']] = row['microrregião']


df_acidentes['microrregiao'] = df_acidentes['bairro_normalizado'].map(microrregiao_dict)


df_acidentes = df_acidentes[df_acidentes['microrregiao'].notna()].copy()

print(f"\nAcidentes em bairros do grafo: {len(df_acidentes)}")


acidentes_por_bairro = df_acidentes.groupby('bairro_normalizado').agg({
    'data': 'count',
    'natureza': lambda x: list(x)
}).rename(columns={'data': 'total_acidentes', 'natureza': 'naturezas'})


def calcular_proporcao_com_vitima(naturezas_list):
    counter = Counter(naturezas_list)
    com_vitima = counter.get('COM VÍTIMA', 0) + counter.get('COM VITIMA', 0)
    total = len(naturezas_list)
    return (com_vitima / total * 100) if total > 0 else 0

acidentes_por_bairro['com_vitima'] = acidentes_por_bairro['naturezas'].apply(
    lambda x: sum(1 for n in x if 'COM' in n and ('VÍTIMA' in n or 'VITIMA' in n))
)
acidentes_por_bairro['sem_vitima'] = acidentes_por_bairro['naturezas'].apply(
    lambda x: sum(1 for n in x if 'SEM' in n and ('VÍTIMA' in n or 'VITIMA' in n))
)
acidentes_por_bairro['perc_com_vitima'] = acidentes_por_bairro['naturezas'].apply(calcular_proporcao_com_vitima)
acidentes_por_bairro = acidentes_por_bairro.drop(columns=['naturezas'])


acidentes_por_bairro['microrregiao'] = acidentes_por_bairro.index.map(microrregiao_dict)

print("\nAcidentes por bairro (top 10):")
print(acidentes_por_bairro.sort_values('total_acidentes', ascending=False).head(10))


df_acidentes_com_micro = df_acidentes[df_acidentes['microrregiao'].notna()].copy()

acidentes_por_micro = df_acidentes_com_micro.groupby('microrregiao').agg({
    'data': 'count',
    'natureza': lambda x: list(x)
}).rename(columns={'data': 'total_acidentes', 'natureza': 'naturezas'})

acidentes_por_micro['com_vitima'] = acidentes_por_micro['naturezas'].apply(
    lambda x: sum(1 for n in x if 'COM' in n and ('VÍTIMA' in n or 'VITIMA' in n))
)
acidentes_por_micro['sem_vitima'] = acidentes_por_micro['naturezas'].apply(
    lambda x: sum(1 for n in x if 'SEM' in n and ('VÍTIMA' in n or 'VITIMA' in n))
)
acidentes_por_micro['perc_com_vitima'] = acidentes_por_micro['naturezas'].apply(calcular_proporcao_com_vitima)
acidentes_por_micro = acidentes_por_micro.drop(columns=['naturezas'])

print("\nAcidentes por microrregião:")
print(acidentes_por_micro.sort_values('total_acidentes', ascending=False))


acidentes_por_bairro.reset_index().to_csv('Visualizacao_Acidentes/acidentes_bairros.csv', index=False, encoding='utf-8-sig')
acidentes_por_micro.reset_index().to_csv('Visualizacao_Acidentes/acidentes_microrregioes.csv', index=False, encoding='utf-8-sig')

print("\n✓ Dados processados:")
print("  - Visualizacao_Acidentes/acidentes_bairros.csv")
print("  - Visualizacao_Acidentes/acidentes_microrregioes.csv")
