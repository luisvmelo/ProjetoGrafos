import pandas as pd
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.graphs.graph import construir_grafo_bairros

project_root = os.path.join(os.path.dirname(__file__), '../..')
data_dir = os.path.join(project_root, 'data')
out_dir = os.path.join(project_root, 'out/parte1')

def calcular_metricas_globais(grafo):
    ordem = grafo.total_vertices()

    pares_unicos = set()
    for aresta in grafo.arestas:
        par = tuple(sorted([aresta['origem'], aresta['destino']]))
        pares_unicos.add(par)
    tamanho = len(pares_unicos)

    if ordem < 2:
        densidade = 0.0
    else:
        densidade = (2 * tamanho) / (ordem * (ordem - 1))

    return {
        'ordem': ordem,
        'tamanho': tamanho,
        'densidade': round(densidade, 6)
    }

def calcular_metricas_microrregioes(grafo):
    bairros_path = os.path.join(data_dir, 'bairros_unique.csv')
    df_bairros = pd.read_csv(bairros_path, sep=';', encoding='utf-8-sig')

    microrregioes = {}
    for _, row in df_bairros.iterrows():
        bairro = row['bairro']
        micro = row['microrregião']

        if '/' in micro:
            micros = [m.strip() for m in micro.split('/')]
        else:
            micros = [micro.strip()]

        for m in micros:
            if m not in microrregioes:
                microrregioes[m] = []
            microrregioes[m].append(bairro)

    resultados = []
    for micro, bairros in sorted(microrregioes.items()):
        bairros_set = set(bairros)

        pares_unicos = set()
        for aresta in grafo.arestas:
            if aresta['origem'] in bairros_set and aresta['destino'] in bairros_set:
                par = tuple(sorted([aresta['origem'], aresta['destino']]))
                pares_unicos.add(par)

        ordem = len(bairros_set)
        tamanho = len(pares_unicos)

        if ordem < 2:
            densidade = 0.0
        else:
            densidade = (2 * tamanho) / (ordem * (ordem - 1))

        resultados.append({
            'microrregiao': micro,
            'ordem': ordem,
            'tamanho': tamanho,
            'densidade': round(densidade, 6)
        })

    return resultados

def calcular_ego_bairros(grafo):
    resultados = []

    for bairro in sorted(grafo.vertices):
        vizinhos = grafo.obter_vizinhos(bairro)

        vizinhos_unicos = set()
        for v in vizinhos:
            vizinhos_unicos.add(v['destino'])
        grau = len(vizinhos_unicos)

        ego_vertices = {bairro}
        ego_vertices.update(vizinhos_unicos)

        pares_unicos = set()
        for aresta in grafo.arestas:
            if aresta['origem'] in ego_vertices and aresta['destino'] in ego_vertices:
                par = tuple(sorted([aresta['origem'], aresta['destino']]))
                pares_unicos.add(par)

        ordem_ego = len(ego_vertices)
        tamanho_ego = len(pares_unicos)

        if ordem_ego < 2:
            densidade_ego = 0.0
        else:
            densidade_ego = (2 * tamanho_ego) / (ordem_ego * (ordem_ego - 1))

        resultados.append({
            'bairro': bairro,
            'grau': grau,
            'ordem_ego': ordem_ego,
            'tamanho_ego': tamanho_ego,
            'densidade_ego': round(densidade_ego, 6)
        })

    return resultados

if __name__ == '__main__':
    print("Carregando grafo...")
    grafo = construir_grafo_bairros()

    print("\n1. Calculando métricas globais (Recife)...")
    metricas_globais = calcular_metricas_globais(grafo)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'recife_global.json'), 'w', encoding='utf-8') as f:
        json.dump(metricas_globais, f, indent=2, ensure_ascii=False)
    print(f"   Ordem: {metricas_globais['ordem']}")
    print(f"   Tamanho: {metricas_globais['tamanho']}")
    print(f"   Densidade: {metricas_globais['densidade']}")

    print("\n2. Calculando métricas por microrregião...")
    metricas_micro = calcular_metricas_microrregioes(grafo)
    with open(os.path.join(out_dir, 'microrregioes.json'), 'w', encoding='utf-8') as f:
        json.dump(metricas_micro, f, indent=2, ensure_ascii=False)
    print(f"   Total de microrregiões: {len(metricas_micro)}")
    for m in metricas_micro[:5]:
        print(f"   {m['microrregiao']}: ordem={m['ordem']}, densidade={m['densidade']}")

    print("\n3. Calculando ego-redes por bairro...")
    ego_bairros = calcular_ego_bairros(grafo)
    df_ego = pd.DataFrame(ego_bairros)
    df_ego.to_csv(os.path.join(out_dir, 'ego_bairro.csv'), index=False, encoding='utf-8')
    print(f"   Total de bairros: {len(ego_bairros)}")
    print(f"   Primeiros 5 bairros:")
    for e in ego_bairros[:5]:
        print(f"   {e['bairro']}: grau={e['grau']}, densidade_ego={e['densidade_ego']}")

    print("\n✓ Todas as métricas foram calculadas com sucesso!")
    print("  - out/parte1/recife_global.json")
    print("  - out/parte1/microrregioes.json")
    print("  - out/parte1/ego_bairro.csv")
