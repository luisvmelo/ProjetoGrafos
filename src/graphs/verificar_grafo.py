import pandas as pd
from graph import construir_grafo_bairros

df_original = pd.read_csv('data/adjacencias_bairros.csv')
grafo = construir_grafo_bairros()

print("="*70)
print("VERIFICAÇÃO DO GRAFO")
print("="*70)

print(f"\n1. QUANTIDADE DE DADOS")
print(f"   CSV original: {len(df_original)} linhas")
print(f"   Grafo: {grafo.total_arestas()} arestas")
print(f"   Status: {'✓ OK' if len(df_original) == grafo.total_arestas() else '✗ ERRO'}")

bairros_unicos_csv = set(df_original['bairro_origem']).union(set(df_original['bairro_destino']))
print(f"\n2. VÉRTICES (BAIRROS)")
print(f"   Bairros únicos no CSV: {len(bairros_unicos_csv)}")
print(f"   Vértices no grafo: {grafo.total_vertices()}")
print(f"   Status: {'✓ OK' if len(bairros_unicos_csv) == grafo.total_vertices() else '✗ ERRO'}")

print(f"\n3. VERIFICAÇÃO DE ARESTAS ESPECÍFICAS")
amostra = df_original.head(10)
erros = 0
for _, row in amostra.iterrows():
    origem = row['bairro_origem']
    destino = row['bairro_destino']
    logradouro = row['logradouro']
    peso = row['peso']

    encontrada = False
    for aresta in grafo.arestas:
        if (aresta['origem'] == origem and aresta['destino'] == destino and
            aresta['logradouro'] == logradouro and aresta['peso'] == peso):
            encontrada = True
            break

    if encontrada:
        print(f"   ✓ {origem} -> {destino} via {logradouro}")
    else:
        print(f"   ✗ {origem} -> {destino} via {logradouro} (NÃO ENCONTRADA)")
        erros += 1

print(f"\n4. TESTE DE NÃO-DIRECIONAMENTO")
print(f"   Testando se as conexões são bidirecionais...")
bairro_teste = list(grafo.vertices)[0]
vizinhos = grafo.obter_vizinhos(bairro_teste)
if len(vizinhos) > 0:
    vizinho = vizinhos[0]['destino']
    vizinhos_reverso = grafo.obter_vizinhos(vizinho)
    encontrado = any(v['destino'] == bairro_teste for v in vizinhos_reverso)
    print(f"   {bairro_teste} -> {vizinho}: {'✓ Bidirecional' if encontrado else '✗ Unidirecional'}")

print(f"\n5. TODAS AS ARESTAS ESTÃO NO GRAFO?")
arestas_faltando = []
for _, row in df_original.iterrows():
    encontrada = False
    for aresta in grafo.arestas:
        if (aresta['origem'] == row['bairro_origem'] and
            aresta['destino'] == row['bairro_destino'] and
            aresta['logradouro'] == row['logradouro']):
            encontrada = True
            break
    if not encontrada:
        arestas_faltando.append(f"{row['bairro_origem']} -> {row['bairro_destino']}")

if len(arestas_faltando) == 0:
    print(f"   ✓ Todas as {len(df_original)} arestas estão presentes no grafo")
else:
    print(f"   ✗ {len(arestas_faltando)} arestas faltando")
    print(f"   Primeiras 5 faltando: {arestas_faltando[:5]}")

print(f"\n6. EXEMPLO DE VIZINHOS")
exemplos = ['Aflitos', 'Recife', 'Boa Viagem']
for bairro in exemplos:
    if bairro in grafo.vertices:
        vizinhos = grafo.obter_vizinhos(bairro)
        print(f"   {bairro} tem {len(vizinhos)} conexões")
        for v in vizinhos[:3]:
            print(f"      -> {v['destino']} via {v['logradouro']} ({v['peso']}m)")

print(f"\n{'='*70}")
print(f"RESULTADO: Grafo construído {'CORRETAMENTE' if erros == 0 and len(arestas_faltando) == 0 else 'COM PROBLEMAS'}")
print(f"{'='*70}")
