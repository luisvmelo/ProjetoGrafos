import pandas as pd


metro_vlt_data = """mode,from,to
metro,Recife,Joana Bezerra
metro,Joana Bezerra,Afogados
metro,Afogados,Mangueira
metro,Mangueira,Cajueiro
metro,Cajueiro,Coqueiral
metro,Coqueiral,Tejipió
metro,Tejipió,Afogados
metro,Afogados,Floriano
metro,Floriano,Ipiranga
metro,Ipiranga,Imbiribeira
metro,Imbiribeira,Antonio Falcão
metro,Antonio Falcão,Shopping
metro,Shopping,Tancredo Neves
metro,Tancredo Neves,Aeroporto
metro,Aeroporto,Porta Larga
metro,Porta Larga,Cavaleiro
metro,Cavaleiro,Terminal Integrado
metro,Terminal Integrado,Jaboatão
vlt,Curado,Jorge Lins
vlt,Jorge Lins,Padre Zuzinha
vlt,Padre Zuzinha,Jardim Uchoa
vlt,Jardim Uchoa,Engenho Velho
vlt,Engenho Velho,Centro Médico
vlt,Centro Médico,Arraial
vlt,Arraial,Afogados
vlt,Afogados,Cavaleiro
vlt,Cavaleiro,Largo da Paz
vlt,Largo da Paz,Santa Luzia
vlt,Santa Luzia,Terminal Integrado
vlt,Terminal Integrado,Rodoviária
vlt,Rodoviária,Recife"""


from io import StringIO
df_metro_vlt = pd.read_csv(StringIO(metro_vlt_data))

print(f"Total de conexões metro/VLT: {len(df_metro_vlt)}")
print(f"\nModo: Metro = {len(df_metro_vlt[df_metro_vlt['mode'] == 'metro'])}, VLT = {len(df_metro_vlt[df_metro_vlt['mode'] == 'vlt'])}")



mapa_estacao_bairro = {
    'Recife': 'Recife',
    'Joana Bezerra': 'Ilha Joana Bezerra',
    'Afogados': 'Afogados',
    'Mangueira': 'Mangueira',
    'Cajueiro': 'Cajueiro',
    'Coqueiral': 'Coqueiral',
    'Tejipió': 'Tejipió',
    'Floriano': 'Boa Viagem',  
    'Ipiranga': 'Boa Viagem',  
    'Imbiribeira': 'Imbiribeira',
    'Antonio Falcão': 'Boa Viagem',  
    'Shopping': 'Boa Viagem',  
    'Tancredo Neves': 'Pina',  
    'Aeroporto': 'Imbiribeira',  
    'Porta Larga': 'Imbiribeira',  
    'Cavaleiro': None,  
    'Terminal Integrado': None,  
    'Jaboatão': None,  
    'Curado': 'Curado',
    'Jorge Lins': 'Curado',  
    'Padre Zuzinha': 'Engenho do Meio',  
    'Jardim Uchoa': 'Engenho do Meio',  
    'Engenho Velho': 'Engenho do Meio',  
    'Centro Médico': 'Afogados',  
    'Arraial': 'Afogados',  
    'Largo da Paz': None,  
    'Santa Luzia': None,  
    'Rodoviária': 'São José',  
}


df_metro_vlt['bairro_from'] = df_metro_vlt['from'].map(mapa_estacao_bairro)
df_metro_vlt['bairro_to'] = df_metro_vlt['to'].map(mapa_estacao_bairro)


df_metro_vlt = df_metro_vlt[(df_metro_vlt['bairro_from'].notna()) & (df_metro_vlt['bairro_to'].notna())].copy()

print(f"\nApós filtrar estações fora de Recife: {len(df_metro_vlt)} conexões")


pares_metro_vlt = []
for _, row in df_metro_vlt.iterrows():
    bairro_a = min(row['bairro_from'], row['bairro_to'])
    bairro_b = max(row['bairro_from'], row['bairro_to'])

    
    if bairro_a != bairro_b:
        pares_metro_vlt.append({
            'bairro_a': bairro_a,
            'bairro_b': bairro_b,
            'mode': row['mode']
        })

df_pares_metro_vlt = pd.DataFrame(pares_metro_vlt)


df_pares_metro_vlt = df_pares_metro_vlt.drop_duplicates(subset=['bairro_a', 'bairro_b'])

print(f"Pares únicos metro/VLT: {len(df_pares_metro_vlt)}")


df_onibus = pd.read_csv('Visualizacao_Transporte/arestas_bairros_onibus.csv', encoding='utf-8-sig')


df_onibus['mode'] = 'onibus'

print(f"\nConexões de ônibus: {len(df_onibus)}")


df_completo = pd.concat([df_onibus, df_pares_metro_vlt], ignore_index=True)


df_completo = df_completo.drop_duplicates(subset=['bairro_a', 'bairro_b'], keep='first')

print(f"\nTotal de conexões após merge: {len(df_completo)}")
print(f"  Ônibus: {len(df_completo[df_completo['mode'] == 'onibus'])}")
print(f"  Metro: {len(df_completo[df_completo['mode'] == 'metro'])}")
print(f"  VLT: {len(df_completo[df_completo['mode'] == 'vlt'])}")


df_completo.to_csv('Visualizacao_Transporte/arestas_bairros_transporte.csv', index=False, encoding='utf-8-sig')

print("\n✓ Arquivo salvo: Visualizacao_Transporte/arestas_bairros_transporte.csv")


print("\nConexões de metro:")
print(df_completo[df_completo['mode'] == 'metro'].head(10))

print("\nConexões de VLT:")
print(df_completo[df_completo['mode'] == 'vlt'].head(10))
