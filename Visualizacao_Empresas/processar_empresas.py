import pandas as pd
import unicodedata
from collections import Counter

# Carregar dados de empresas
df_empresas = pd.read_csv('Visualizacao_Empresas/empresas_recife.csv', encoding='utf-8')

print(f"Total de empresas: {len(df_empresas)}")
print(f"\nColunas: {df_empresas.columns.tolist()}")
print(f"\nPrimeiras linhas:")
print(df_empresas.head())

# Função de normalização para empresas
def normalizar_nome(texto):
    if pd.isna(texto):
        return ''
    texto = str(texto).strip()

    # Mapeamentos especiais ANTES da normalização
    mapeamentos_especiais = {
        'Sitio dos Pintos   Sao Bras': 'Sítio dos Pintos',
        'Cohab   Ibura de Cima': 'Cohab',
        'Alto do Mandu   Sitio Grande': 'Alto do Mandu'
    }

    if texto in mapeamentos_especiais:
        texto = mapeamentos_especiais[texto]

    # Remove acentos
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remove espaços extras, mas MANTÉM hífens
    normalizado = ' '.join(sem_acento.split())
    # Normalizar variações comuns
    normalizado = normalizado.replace('Terezinha', 'Teresinha')
    normalizado = normalizado.replace('TEREZINHA', 'TERESINHA')
    # Title Case
    return normalizado.title()

# Normalizar nomes de bairros
df_empresas['bairro_normalizado'] = df_empresas['nome_bairro'].apply(normalizar_nome)

# Carregar dados de bairros do grafo para pegar as microrregiões
df_bairros_grafo = pd.read_csv('data/bairros_unique.csv', encoding='utf-8-sig', sep=';')
# IMPORTANTE: Aplicar mesma normalização aos bairros do grafo
df_bairros_grafo['bairro_normalizado'] = df_bairros_grafo['bairro'].apply(normalizar_nome)

print(f"\n=== DEBUG: Verificando normalização ===")
print(f"Total bairros no grafo: {len(df_bairros_grafo)}")
print(f"Total bairros únicos em empresas: {df_empresas['bairro_normalizado'].nunique()}")
print(f"\nExemplos de normalização:")
exemplos = ['Fundão', 'Graças', 'Poço', 'São José', 'Santo Antônio', 'Ilha do Leite']
for ex in exemplos:
    match = df_bairros_grafo[df_bairros_grafo['bairro'] == ex]
    if not match.empty:
        print(f"  '{ex}' -> '{match.iloc[0]['bairro_normalizado']}'")

# Criar dicionário de bairro -> microrregião
microrregiao_dict = {}
for _, row in df_bairros_grafo.iterrows():
    microrregiao_dict[row['bairro_normalizado']] = row['microrregião']

# Adicionar microrregião aos dados de empresas
df_empresas['microrregiao'] = df_empresas['bairro_normalizado'].map(microrregiao_dict)

# Filtrar apenas empresas ativas e que estão em bairros conhecidos
df_empresas = df_empresas[
    (df_empresas['situacao_empresa'] == 'ATIVO') &
    (df_empresas['microrregiao'].notna())
].copy()

print(f"\nEmpresas ativas em bairros do grafo: {len(df_empresas)}")

# Contar empresas por bairro
empresas_por_bairro = df_empresas.groupby('bairro_normalizado').agg({
    'cnpj': 'count',
    'nome_grupo': lambda x: list(x)
}).rename(columns={'cnpj': 'total_empresas', 'nome_grupo': 'atividades'})

# Calcular top 3 atividades por bairro
def top_3_atividades(atividades_list):
    counter = Counter(atividades_list)
    top_3 = counter.most_common(3)
    return [{'atividade': ativ, 'quantidade': qtd} for ativ, qtd in top_3]

empresas_por_bairro['top_3_atividades'] = empresas_por_bairro['atividades'].apply(top_3_atividades)
empresas_por_bairro = empresas_por_bairro.drop(columns=['atividades'])

# Adicionar microrregião
empresas_por_bairro['microrregiao'] = empresas_por_bairro.index.map(microrregiao_dict)

print("\nEmpresas por bairro (top 10):")
print(empresas_por_bairro.sort_values('total_empresas', ascending=False).head(10))

# Contar empresas por microrregião
df_empresas_com_micro = df_empresas[df_empresas['microrregiao'].notna()].copy()

empresas_por_micro = df_empresas_com_micro.groupby('microrregiao').agg({
    'cnpj': 'count',
    'nome_grupo': lambda x: list(x)
}).rename(columns={'cnpj': 'total_empresas', 'nome_grupo': 'atividades'})

empresas_por_micro['top_3_atividades'] = empresas_por_micro['atividades'].apply(top_3_atividades)
empresas_por_micro = empresas_por_micro.drop(columns=['atividades'])

print("\nEmpresas por microrregião:")
print(empresas_por_micro.sort_values('total_empresas', ascending=False))

# Salvar CSVs processados
empresas_por_bairro.reset_index().to_csv('Visualizacao_Empresas/empresas_bairros.csv', index=False, encoding='utf-8-sig')
empresas_por_micro.reset_index().to_csv('Visualizacao_Empresas/empresas_microrregioes.csv', index=False, encoding='utf-8-sig')

print("\n✓ Dados processados:")
print("  - Visualizacao_Empresas/empresas_bairros.csv")
print("  - Visualizacao_Empresas/empresas_microrregioes.csv")
