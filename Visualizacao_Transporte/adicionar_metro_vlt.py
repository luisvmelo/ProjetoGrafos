import pandas as pd

# Dados de metro e VLT fornecidos pelo usuário
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

# Criar DataFrame a partir dos dados
from io import StringIO
df_metro_vlt = pd.read_csv(StringIO(metro_vlt_data))

print(f"Total de conexões metro/VLT: {len(df_metro_vlt)}")
print(f"\nModo: Metro = {len(df_metro_vlt[df_metro_vlt['mode'] == 'metro'])}, VLT = {len(df_metro_vlt[df_metro_vlt['mode'] == 'vlt'])}")

# Normalizar nomes de estações para bairros
# Mapear estações para bairros conhecidos
mapa_estacao_bairro = {
    'Recife': 'Recife',
    'Joana Bezerra': 'Ilha Joana Bezerra',
    'Afogados': 'Afogados',
    'Mangueira': 'Mangueira',
    'Cajueiro': 'Cajueiro',
    'Coqueiral': 'Coqueiral',
    'Tejipió': 'Tejipió',
    'Floriano': 'Boa Viagem',  # Estação Floriano fica em Boa Viagem
    'Ipiranga': 'Boa Viagem',  # Estação Ipiranga fica em Boa Viagem
    'Imbiribeira': 'Imbiribeira',
    'Antonio Falcão': 'Boa Viagem',  # Estação Antônio Falcão fica em Boa Viagem
    'Shopping': 'Boa Viagem',  # Shopping RioMar fica em Boa Viagem
    'Tancredo Neves': 'Pina',  # Estação Tancredo Neves fica em Pina
    'Aeroporto': 'Imbiribeira',  # Aeroporto fica em Imbiribeira
    'Porta Larga': 'Imbiribeira',  # Porta Larga fica próximo a Imbiribeira
    'Cavaleiro': None,  # Cavaleiro não é bairro de Recife
    'Terminal Integrado': None,  # TI não é bairro de Recife
    'Jaboatão': None,  # Jaboatão não é bairro de Recife
    'Curado': 'Curado',
    'Jorge Lins': 'Curado',  # Estação Jorge Lins fica no Curado
    'Padre Zuzinha': 'Engenho do Meio',  # Padre Zuzinha fica no Engenho do Meio
    'Jardim Uchoa': 'Engenho do Meio',  # Jardim Uchoa fica no Engenho do Meio
    'Engenho Velho': 'Engenho do Meio',  # Engenho Velho fica no Engenho do Meio
    'Centro Médico': 'Afogados',  # Centro Médico fica em Afogados
    'Arraial': 'Afogados',  # Arraial fica em Afogados
    'Largo da Paz': None,  # Largo da Paz não é bairro de Recife
    'Santa Luzia': None,  # Santa Luzia não é bairro de Recife
    'Rodoviária': 'São José',  # Rodoviária fica em São José
}

# Mapear estações para bairros
df_metro_vlt['bairro_from'] = df_metro_vlt['from'].map(mapa_estacao_bairro)
df_metro_vlt['bairro_to'] = df_metro_vlt['to'].map(mapa_estacao_bairro)

# Remover linhas onde algum bairro é None (fora de Recife)
df_metro_vlt = df_metro_vlt[(df_metro_vlt['bairro_from'].notna()) & (df_metro_vlt['bairro_to'].notna())].copy()

print(f"\nApós filtrar estações fora de Recife: {len(df_metro_vlt)} conexões")

# Criar pares não direcionados (ordenados alfabeticamente)
pares_metro_vlt = []
for _, row in df_metro_vlt.iterrows():
    bairro_a = min(row['bairro_from'], row['bairro_to'])
    bairro_b = max(row['bairro_from'], row['bairro_to'])

    # Evitar pares onde origem == destino
    if bairro_a != bairro_b:
        pares_metro_vlt.append({
            'bairro_a': bairro_a,
            'bairro_b': bairro_b,
            'mode': row['mode']
        })

df_pares_metro_vlt = pd.DataFrame(pares_metro_vlt)

# Remover duplicados
df_pares_metro_vlt = df_pares_metro_vlt.drop_duplicates(subset=['bairro_a', 'bairro_b'])

print(f"Pares únicos metro/VLT: {len(df_pares_metro_vlt)}")

# Carregar dados de ônibus existentes
df_onibus = pd.read_csv('Visualizacao_Transporte/arestas_bairros_onibus.csv', encoding='utf-8-sig')

# Adicionar coluna 'mode' aos dados de ônibus
df_onibus['mode'] = 'onibus'

print(f"\nConexões de ônibus: {len(df_onibus)}")

# Combinar todos os dados
df_completo = pd.concat([df_onibus, df_pares_metro_vlt], ignore_index=True)

# Remover duplicados (se um par já existe como ônibus, manter apenas ônibus)
df_completo = df_completo.drop_duplicates(subset=['bairro_a', 'bairro_b'], keep='first')

print(f"\nTotal de conexões após merge: {len(df_completo)}")
print(f"  Ônibus: {len(df_completo[df_completo['mode'] == 'onibus'])}")
print(f"  Metro: {len(df_completo[df_completo['mode'] == 'metro'])}")
print(f"  VLT: {len(df_completo[df_completo['mode'] == 'vlt'])}")

# Salvar arquivo completo
df_completo.to_csv('Visualizacao_Transporte/arestas_bairros_transporte.csv', index=False, encoding='utf-8-sig')

print("\n✓ Arquivo salvo: Visualizacao_Transporte/arestas_bairros_transporte.csv")

# Mostrar algumas conexões de cada tipo
print("\nConexões de metro:")
print(df_completo[df_completo['mode'] == 'metro'].head(10))

print("\nConexões de VLT:")
print(df_completo[df_completo['mode'] == 'vlt'].head(10))
