import pandas as pd


def normalizar_bairro_transporte(nome):
    if pd.isna(nome):
        return nome

    
    mapeamentos = {
        'Cohab - Ibura de Cima': 'Cohab',
        'Alto Santa Terezinha': 'Alto Santa Teresinha',
        'Sítio dos Pintos - São Brás': 'Sítio dos Pintos',
        'Pau Ferro': 'Pau-ferro',
        'Pau ferro': 'Pau-ferro'
    }

    return mapeamentos.get(nome, nome)


print("Carregando dados...")
stop_times = pd.read_csv('/mnt/c/Users/luise/Downloads/gtfs/stop_times.txt')
stops_bairros = pd.read_csv('/mnt/c/Users/luise/Downloads/stops_bairros.csv')

print(f"Stop times: {len(stop_times)} registros")
print(f"Stops com bairro: {len(stops_bairros)} paradas")


print("\nFazendo merge de stop_times com stops_bairros...")
df = stop_times.merge(stops_bairros[['stop_id', 'bairro']], on='stop_id', how='left')


df = df[df['bairro'].notna()].copy()


df['bairro'] = df['bairro'].apply(normalizar_bairro_transporte)

print(f"Após remover paradas sem bairro: {len(df)} registros")


df = df.sort_values(['trip_id', 'stop_sequence'])

print("\nProcessando viagens para gerar pares de bairros...")


pares = []

for trip_id, group in df.groupby('trip_id'):
    
    bairros = group['bairro'].tolist()

    
    bairros_limpos = []
    for bairro in bairros:
        if not bairros_limpos or bairros_limpos[-1] != bairro:
            bairros_limpos.append(bairro)

    
    for i in range(len(bairros_limpos) - 1):
        origem = bairros_limpos[i]
        destino = bairros_limpos[i + 1]

        
        bairro_a = min(origem, destino)
        bairro_b = max(origem, destino)

        pares.append({
            'bairro_a': bairro_a,
            'bairro_b': bairro_b
        })

print(f"Total de pares gerados: {len(pares)}")


df_pares = pd.DataFrame(pares)
df_pares = df_pares.drop_duplicates(subset=['bairro_a', 'bairro_b'])

print(f"Pares únicos após remoção de duplicados: {len(df_pares)}")


df_pares.to_csv('Visualizacao_Transporte/arestas_bairros_onibus.csv', index=False, encoding='utf-8-sig')

print("\n✓ Arquivo salvo: Visualizacao_Transporte/arestas_bairros_onibus.csv")


print(f"\nEstatísticas:")
print(f"  Bairros únicos conectados: {len(set(df_pares['bairro_a'].unique()) | set(df_pares['bairro_b'].unique()))}")
print(f"  Conexões únicas: {len(df_pares)}")


print(f"\nPrimeiras conexões:")
print(df_pares.head(10))
