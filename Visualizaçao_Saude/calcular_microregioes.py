import pandas as pd
import unicodedata

# Função de normalização
def normalizar_nome(texto):
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    sem_hifen = sem_acento.replace('-', ' ').replace('  ', ' ').strip().upper()
    sem_hifen = sem_hifen.replace('TEREZINHA', 'TERESINHA')
    sem_hifen = sem_hifen.replace('HEMETERIO', 'HEMETERIO')
    return sem_hifen

# Carregar dados dos bairros
df_bairros = pd.read_csv('medicos_por_bairro_com_indices.csv', encoding='utf-8-sig')

# Carregar mapeamento de bairros para microrregiões
with open('../data/bairros_unique.csv', 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()[1:]
    microrregiao_dict = {}
    bairro_norm_to_original = {}

    for linha in linhas:
        partes = linha.strip().split(';')
        if len(partes) >= 2:
            bairro = partes[0]
            micro = partes[1]
            bairro_norm = normalizar_nome(bairro)
            microrregiao_dict[bairro_norm] = micro
            bairro_norm_to_original[bairro_norm] = bairro

# Adicionar microrregião ao dataframe (normalizar nomes)
df_bairros['microrregiao'] = df_bairros['Bairro'].apply(
    lambda x: microrregiao_dict.get(normalizar_nome(x), 'N/A')
)

# Separar bairros com múltiplas microrregiões
# Para cada bairro com múltiplas, usar apenas a primeira
df_bairros['micro_principal'] = df_bairros['microrregiao'].apply(
    lambda x: x.split(' / ')[0].strip() if ' / ' in x else x
)

# Agrupar por microrregião e somar
micro_agregado = df_bairros.groupby('micro_principal').agg({
    'unidades': 'sum',
    'medicos totais': 'sum',
    'população': 'sum'
}).reset_index()

# Renomear coluna
micro_agregado.rename(columns={'micro_principal': 'microrregiao'}, inplace=True)

# Calcular índices agregados
micro_agregado['Proporção médico população'] = (
    micro_agregado['medicos totais'] / micro_agregado['população']
)

micro_agregado['Indice OCDE'] = (
    micro_agregado['Proporção médico população'] / 0.0035
)

# Renomear colunas
micro_agregado.rename(columns={
    'unidades': 'n_unidades',
    'medicos totais': 'medicos_totais'
}, inplace=True)

# Salvar
micro_agregado.to_csv('microregioes_saude.csv', index=False)

print("Índices de Microrregiões Recalculados:")
print(micro_agregado.to_string())
print(f"\n✓ Arquivo salvo: microregioes_saude.csv")
