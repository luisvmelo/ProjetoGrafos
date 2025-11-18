import pandas as pd
import numpy as np
from collections import defaultdict, deque

# Carregar dados
print("Carregando dados...")
df_adjacencias = pd.read_csv('data/adjacencias_bairros.csv', encoding='utf-8-sig')
df_empresas = pd.read_csv('Visualizacao_Empresas/empresas_bairros.csv', encoding='utf-8-sig')

print(f"Adjacências: {len(df_adjacencias)} arestas")
print(f"Empresas: {len(df_empresas)} bairros")

# Criar grafo light usando dicionário de adjacências
print("\nCriando grafo light (não ponderado)...")
grafo = defaultdict(set)

# Adicionar todas as arestas (grafo não direcionado)
for _, row in df_adjacencias.iterrows():
    origem = row['bairro_origem']
    destino = row['bairro_destino']

    # Adicionar apenas uma vez por par (grafo light)
    grafo[origem].add(destino)
    grafo[destino].add(origem)

todos_bairros = set(grafo.keys())
print(f"Grafo criado: {len(todos_bairros)} nós, {sum(len(v) for v in grafo.values()) // 2} arestas únicas")

# 1. Calcular grau (número de conexões)
print("\nCalculando grau de cada bairro...")
grau = {bairro: len(vizinhos) for bairro, vizinhos in grafo.items()}

# 2. Calcular centralidade de grau (normalizado)
print("Calculando centralidade de grau...")
n = len(todos_bairros)
centralidade_grau = {bairro: g / (n - 1) if n > 1 else 0 for bairro, g in grau.items()}

# 3. Calcular closeness centrality (BFS para distâncias)
print("Calculando closeness centrality...")

def calcular_closeness(grafo, bairro):
    """Calcula closeness centrality usando BFS"""
    distancias = {}
    visitados = set()
    fila = deque([(bairro, 0)])

    while fila:
        atual, dist = fila.popleft()
        if atual in visitados:
            continue
        visitados.add(atual)
        distancias[atual] = dist

        for vizinho in grafo.get(atual, []):
            if vizinho not in visitados:
                fila.append((vizinho, dist + 1))

    # Closeness = (n-1) / soma das distâncias
    soma_dist = sum(distancias.values())
    if soma_dist > 0:
        return (len(distancias) - 1) / soma_dist
    return 0

centralidade_closeness = {}
for i, bairro in enumerate(todos_bairros):
    if i % 20 == 0:
        print(f"  Processando {i}/{len(todos_bairros)}...")
    centralidade_closeness[bairro] = calcular_closeness(grafo, bairro)

# 4. Calcular betweenness centrality (simplificado - pode ser lento)
print("Calculando betweenness centrality (simplificado)...")

def calcular_betweenness(grafo, bairro):
    """Calcula betweenness centrality simplificado"""
    # Conta quantas vezes este bairro aparece em caminhos mínimos
    betweenness = 0

    # Para cada par de outros bairros, verificar se o bairro está no caminho
    outros = [b for b in todos_bairros if b != bairro]

    # Amostrar pares para não ser muito lento (amostra aleatória de 30 pares)
    np.random.seed(42)
    if len(outros) > 15:
        amostra = np.random.choice(outros, size=min(15, len(outros)), replace=False)
    else:
        amostra = outros

    for origem in amostra:
        # BFS para encontrar caminhos mínimos
        visitados = {origem}
        fila = deque([origem])
        pais = {origem: []}

        while fila:
            atual = fila.popleft()

            for vizinho in grafo.get(atual, []):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    pais[vizinho] = [atual]
                    fila.append(vizinho)
                elif len(pais.get(vizinho, [])) > 0:
                    # Caminho alternativo do mesmo comprimento
                    pais[vizinho].append(atual)

        # Contar se bairro está nos caminhos
        for destino in amostra:
            if destino != origem and destino in pais:
                # Verificar se bairro está no caminho de origem a destino
                caminho_atual = destino
                while caminho_atual != origem:
                    for pai in pais.get(caminho_atual, []):
                        if pai == bairro:
                            betweenness += 1
                            break
                    if len(pais.get(caminho_atual, [])) > 0:
                        caminho_atual = pais[caminho_atual][0]
                    else:
                        break

    return betweenness

centralidade_betweenness = {}
for i, bairro in enumerate(todos_bairros):
    if i % 10 == 0:
        print(f"  Processando {i}/{len(todos_bairros)}...")
    centralidade_betweenness[bairro] = calcular_betweenness(grafo, bairro)

# Normalizar betweenness
max_betweenness = max(centralidade_betweenness.values()) if centralidade_betweenness else 1
if max_betweenness > 0:
    centralidade_betweenness = {b: v / max_betweenness for b, v in centralidade_betweenness.items()}

# 5. Detectar comunidades usando algoritmo greedy de modularidade (simplificado)
print("\nDetectando comunidades usando algoritmo greedy...")

def calcular_modularidade(grafo, particao):
    """Calcula modularidade de uma partição"""
    m = sum(len(v) for v in grafo.values()) / 2  # Número de arestas
    if m == 0:
        return 0

    Q = 0
    for comunidade in set(particao.values()):
        nos_comunidade = [n for n, c in particao.items() if c == comunidade]

        for u in nos_comunidade:
            for v in nos_comunidade:
                if v in grafo.get(u, []):
                    Q += 1 - (len(grafo.get(u, [])) * len(grafo.get(v, []))) / (2 * m)
                else:
                    Q += 0 - (len(grafo.get(u, [])) * len(grafo.get(v, []))) / (2 * m)

    return Q / (2 * m)

# Inicializar: cada bairro em sua própria comunidade
particao = {bairro: i for i, bairro in enumerate(todos_bairros)}
melhor_modularidade = calcular_modularidade(grafo, particao)

print(f"Modularidade inicial: {melhor_modularidade:.4f}")

# Greedy: juntar comunidades que maximizam modularidade
melhorou = True
iteracao = 0
while melhorou and iteracao < 50:
    melhorou = False
    iteracao += 1

    # Para cada bairro, tentar mover para comunidade de vizinhos
    for bairro in list(todos_bairros):
        comunidade_original = particao[bairro]

        # Testar mover para comunidade de cada vizinho
        vizinhos_comunidades = set(particao[v] for v in grafo.get(bairro, []))

        for nova_comunidade in vizinhos_comunidades:
            if nova_comunidade != comunidade_original:
                # Testar mudança
                particao[bairro] = nova_comunidade
                nova_modularidade = calcular_modularidade(grafo, particao)

                if nova_modularidade > melhor_modularidade:
                    melhor_modularidade = nova_modularidade
                    melhorou = True
                    break
                else:
                    # Reverter
                    particao[bairro] = comunidade_original

        if melhorou:
            break

    if iteracao % 10 == 0:
        print(f"  Iteração {iteracao}: modularidade = {melhor_modularidade:.4f}")

# Renumerar comunidades de forma contígua
comunidades_unicas = sorted(set(particao.values()))
mapa_comunidades = {antiga: nova for nova, antiga in enumerate(comunidades_unicas)}
particao = {bairro: mapa_comunidades[com] for bairro, com in particao.items()}

num_comunidades = len(set(particao.values()))
print(f"\nComunidades detectadas: {num_comunidades}")
print(f"Modularidade final: {melhor_modularidade:.4f}")

# Criar DataFrame com todas as métricas
print("\nCriando DataFrame com métricas...")
metricas = []

for bairro in todos_bairros:
    metricas.append({
        'bairro': bairro,
        'grau': grau.get(bairro, 0),
        'centralidade_grau': centralidade_grau.get(bairro, 0),
        'centralidade_closeness': centralidade_closeness.get(bairro, 0),
        'centralidade_betweenness': centralidade_betweenness.get(bairro, 0),
        'cluster_conectividade': particao.get(bairro, -1)
    })

df_metricas = pd.DataFrame(metricas)

# Adicionar coluna para identificar top 20% em centralidade de grau
percentil_80 = df_metricas['centralidade_grau'].quantile(0.80)
df_metricas['top_20_percent'] = df_metricas['centralidade_grau'] >= percentil_80

# Merge com dados de empresas
print("\nMesclando com dados de empresas...")
df_final = df_empresas.merge(df_metricas, left_on='bairro_normalizado', right_on='bairro', how='left')

# Preencher valores nulos (bairros sem conectividade no grafo)
df_final['grau'] = df_final['grau'].fillna(0).astype(int)
df_final['centralidade_grau'] = df_final['centralidade_grau'].fillna(0)
df_final['centralidade_closeness'] = df_final['centralidade_closeness'].fillna(0)
df_final['centralidade_betweenness'] = df_final['centralidade_betweenness'].fillna(0)
df_final['cluster_conectividade'] = df_final['cluster_conectividade'].fillna(-1).astype(int)
df_final['top_20_percent'] = df_final['top_20_percent'].fillna(False)

# Remover coluna duplicada 'bairro'
if 'bairro' in df_final.columns:
    df_final = df_final.drop(columns=['bairro'])

# Salvar resultado
output_file = 'Visualizacao_Empresas/empresas_conectividade.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✓ Arquivo salvo: {output_file}")

# Mostrar estatísticas
print("\n" + "="*60)
print("ESTATÍSTICAS")
print("="*60)

print(f"\nTotal de bairros: {len(df_final)}")
print(f"Bairros com empresas: {len(df_final[df_final['total_empresas'] > 0])}")

print(f"\nComunidades detectadas: {num_comunidades}")
for cluster_id in sorted(set(particao.values())):
    bairros_cluster = [b for b, c in particao.items() if c == cluster_id]
    print(f"  Cluster {cluster_id}: {len(bairros_cluster)} bairros")

print(f"\nTop 10 bairros por centralidade de grau:")
top_bairros = df_final.nlargest(10, 'centralidade_grau')[['bairro_normalizado', 'grau', 'centralidade_grau', 'total_empresas', 'cluster_conectividade']]
print(top_bairros.to_string(index=False))

print(f"\nDistribuição de empresas por cluster:")
cluster_empresas = df_final[df_final['cluster_conectividade'] >= 0].groupby('cluster_conectividade')['total_empresas'].agg(['count', 'sum', 'mean'])
cluster_empresas.columns = ['num_bairros', 'total_empresas', 'media_empresas']
print(cluster_empresas.to_string())

print("\n" + "="*60)
