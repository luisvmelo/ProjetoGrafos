import pandas as pd

# Função de normalização para compatibilizar com grafo base
def normalizar_bairro_transporte(nome):
    if pd.isna(nome):
        return nome

    # Mapeamentos específicos para dados de transporte
    mapeamentos = {
        'Cohab - Ibura de Cima': 'Cohab',
        'Alto Santa Terezinha': 'Alto Santa Teresinha',
        'Sítio dos Pintos - São Brás': 'Sítio dos Pintos',
        'Pau Ferro': 'Pau-ferro',
        'Pau ferro': 'Pau-ferro'
    }

    return mapeamentos.get(nome, nome)

# Carregar dados
print("Carregando dados...")
stop_times = pd.read_csv('/mnt/c/Users/luise/Downloads/gtfs/stop_times.txt')
stops_bairros = pd.read_csv('/mnt/c/Users/luise/Downloads/stops_bairros.csv')

print(f"Stop times: {len(stop_times)} registros")
print(f"Stops com bairro: {len(stops_bairros)} paradas")

# Merge para associar bairro a cada parada da viagem
print("\nFazendo merge de stop_times com stops_bairros...")
df = stop_times.merge(stops_bairros[['stop_id', 'bairro']], on='stop_id', how='left')

# Remover linhas sem bairro
df = df[df['bairro'].notna()].copy()

# Normalizar nomes de bairros para compatibilizar com grafo base
df['bairro'] = df['bairro'].apply(normalizar_bairro_transporte)

print(f"Após remover paradas sem bairro: {len(df)} registros")

# Ordenar por trip_id e stop_sequence
df = df.sort_values(['trip_id', 'stop_sequence'])

print("\nProcessando viagens para gerar pares de bairros...")

# Processar cada trip para gerar pares de bairros consecutivos
pares = []

for trip_id, group in df.groupby('trip_id'):
    # Pegar sequência de bairros
    bairros = group['bairro'].tolist()

    # Remover repetições consecutivas
    bairros_limpos = []
    for bairro in bairros:
        if not bairros_limpos or bairros_limpos[-1] != bairro:
            bairros_limpos.append(bairro)

    # Gerar pares consecutivos
    for i in range(len(bairros_limpos) - 1):
        origem = bairros_limpos[i]
        destino = bairros_limpos[i + 1]

        # Criar par não direcionado (sempre ordenado alfabeticamente)
        bairro_a = min(origem, destino)
        bairro_b = max(origem, destino)

        pares.append({
            'bairro_a': bairro_a,
            'bairro_b': bairro_b
        })

print(f"Total de pares gerados: {len(pares)}")

# Criar dataframe e remover duplicados
df_pares = pd.DataFrame(pares)
df_pares = df_pares.drop_duplicates(subset=['bairro_a', 'bairro_b'])

print(f"Pares únicos após remoção de duplicados: {len(df_pares)}")

# Salvar resultado
df_pares.to_csv('Visualizacao_Transporte/arestas_bairros_onibus.csv', index=False, encoding='utf-8-sig')

print("\n✓ Arquivo salvo: Visualizacao_Transporte/arestas_bairros_onibus.csv")

# Mostrar algumas estatísticas
print(f"\nEstatísticas:")
print(f"  Bairros únicos conectados: {len(set(df_pares['bairro_a'].unique()) | set(df_pares['bairro_b'].unique()))}")
print(f"  Conexões únicas: {len(df_pares)}")

# Mostrar primeiras linhas
print(f"\nPrimeiras conexões:")
print(df_pares.head(10))
