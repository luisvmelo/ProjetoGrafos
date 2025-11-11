import pandas as pd

df_facequadra = pd.read_csv('data/facequadra.csv', sep=';', on_bad_lines='skip')
df_adjacencias = pd.read_csv('data/adjacencias_bairros.csv')

df_facequadra = df_facequadra[['nomebairro', 'codlogradouro', 'nome_logradouro_concatenado']].copy()
df_facequadra = df_facequadra.drop_duplicates()

vias_conectam = []
for _, row in df_adjacencias.iterrows():
    bairro_origem = row['bairro origem']
    bairro_destino = row['bairro match']

    vias_origem = df_facequadra[df_facequadra['nomebairro'] == bairro_origem]
    vias_destino = df_facequadra[df_facequadra['nomebairro'] == bairro_destino]

    vias_comuns = pd.merge(
        vias_origem[['codlogradouro', 'nome_logradouro_concatenado']],
        vias_destino[['codlogradouro', 'nome_logradouro_concatenado']],
        on=['codlogradouro', 'nome_logradouro_concatenado']
    )

    for _, via in vias_comuns.iterrows():
        vias_conectam.append({
            'bairro_origem': bairro_origem,
            'bairro_destino': bairro_destino,
            'nome_logradouro': via['nome_logradouro_concatenado']
        })

df_resultado = pd.DataFrame(vias_conectam)
df_resultado = df_resultado.drop_duplicates()
df_resultado = df_resultado.sort_values(['bairro_origem', 'bairro_destino', 'nome_logradouro']).reset_index(drop=True)
df_resultado.to_csv('data/vias_conectam_bairros_SELECIONADOS.csv', index=False, encoding='utf-8')
