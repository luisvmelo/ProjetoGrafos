import pandas as pd
import unicodedata


def normalizar_nome(texto):
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    sem_hifen = sem_acento.replace('-', ' ').replace('  ', ' ').strip().upper()
    sem_hifen = sem_hifen.replace('TEREZINHA', 'TERESINHA')
    sem_hifen = sem_hifen.replace('HEMETERIO', 'HEMETERIO')
    return sem_hifen


df_bairros = pd.read_csv('medicos_por_bairro_com_indices.csv', encoding='utf-8-sig')


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


df_bairros['microrregiao'] = df_bairros['Bairro'].apply(
    lambda x: microrregiao_dict.get(normalizar_nome(x), 'N/A')
)



df_bairros['micro_principal'] = df_bairros['microrregiao'].apply(
    lambda x: x.split(' / ')[0].strip() if ' / ' in x else x
)


micro_agregado = df_bairros.groupby('micro_principal').agg({
    'unidades': 'sum',
    'medicos totais': 'sum',
    'população': 'sum'
}).reset_index()


micro_agregado.rename(columns={'micro_principal': 'microrregiao'}, inplace=True)


micro_agregado['Proporção médico população'] = (
    micro_agregado['medicos totais'] / micro_agregado['população']
)

micro_agregado['Indice OCDE'] = (
    micro_agregado['Proporção médico população'] / 0.0035
)


micro_agregado.rename(columns={
    'unidades': 'n_unidades',
    'medicos totais': 'medicos_totais'
}, inplace=True)


micro_agregado.to_csv('microregioes_saude.csv', index=False)

print("Índices de Microrregiões Recalculados:")
print(micro_agregado.to_string())
print(f"\n✓ Arquivo salvo: microregioes_saude.csv")
