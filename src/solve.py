import json
import random
import sys
from src.graphs.io import carregar_dataset_parte2
from src.graphs.algorithms import bfs, dfs, dijkstra_parte2, bellman_ford, medir_tempo


def gerar_pares_teste(grafo, num_pares=5, seed=42):
    """Gera pares aleatorios de origem-destino para testes"""
    random.seed(seed)
    vertices = list(grafo.vertices)
    
    pares = []
    for _ in range(num_pares):
        origem = random.choice(vertices)
        destino = random.choice(vertices)
        while destino == origem:
            destino = random.choice(vertices)
        pares.append((origem, destino))
    
    return pares


def encontrar_pares_sem_pesos_negativos(grafo, num_pares=5):
    """Encontra pares com arestas DIRETAS de peso positivo (garantido para Dijkstra)"""
    pares_validos = []
    
    for aresta in grafo.arestas:
        if aresta['peso'] > 0:
            par = (aresta['origem'], aresta['destino'])
            if par not in pares_validos:
                pares_validos.append(par)
                if len(pares_validos) >= num_pares:
                    break
    
    return pares_validos[:num_pares]


def encontrar_casos_bellman_ford(grafo):
    """Encontra casos especificos para Bellman-Ford:
    1. Caso com peso negativo SEM ciclo negativo (aresta isolada)
    2. Caso COM ciclo negativo detectado
    """
    casos = []
    
    for aresta in grafo.arestas:
        if aresta['peso'] < 0:
            casos.append((aresta['origem'], aresta['destino']))
            break
    
    if 'estacao_999' in grafo.vertices:
        casos.append(('estacao_999', 'estacao_997'))
    else:
        vertices = list(grafo.vertices)
        if len(vertices) >= 2:
            casos.append((vertices[0], vertices[1]))
    
    return casos


def analisar_dataset(grafo):
    """Passo 1: Gera informacoes do dataset"""
    stats = grafo.obter_estatisticas()
    
    vertices_sample = list(grafo.vertices)[:10]
    tem_ciclo_negativo = False
    
    for origem in vertices_sample:
        resultado = bellman_ford(grafo, origem)
        if resultado and resultado.get('ciclo_negativo', {}).get('existe'):
            tem_ciclo_negativo = True
            break
    
    info = {
        "nome": "Rede de Transporte Urbano",
        "num_vertices": stats['num_vertices'],
        "num_arestas": stats['num_arestas'],
        "tipo": "direcionado, ponderado",
        "peso_min": stats['peso_min'],
        "peso_max": stats['peso_max'],
        "peso_medio": round(stats['peso_medio'], 2),
        "arestas_positivas": stats['arestas_positivas'],
        "arestas_negativas": stats['arestas_negativas'],
        "ciclos_negativos": 1 if tem_ciclo_negativo else 0,
        "descricao": "Rede de estacoes de transporte com tempos de viagem como pesos"
    }
    
    with open('out/parte2_dataset_info.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print("Dataset info salvo em out/parte2_dataset_info.json")
    return info


def testar_bfs(grafo, origens):
    """Testa BFS em multiplas origens"""
    resultados = []
    tempo_total = 0
    
    for i, origem in enumerate(origens, 1):
        resultado, tempo_ms = medir_tempo(bfs, grafo, origem)
        tempo_total += tempo_ms
        
        if resultado:
            resultados.append({
                'origem': origem,
                'total_visitados': resultado['total_visitados'],
                'tempo_ms': tempo_ms
            })
    
    return resultados, tempo_total


def testar_dfs(grafo, origens):
    """Testa DFS em multiplas origens"""
    resultados = []
    tempo_total = 0
    
    for i, origem in enumerate(origens, 1):
        resultado, tempo_ms = medir_tempo(dfs, grafo, origem)
        tempo_total += tempo_ms
        
        if resultado:
            resultados.append({
                'origem': origem,
                'total_visitados': resultado['total_visitados'],
                'tem_ciclos': resultado['tem_ciclos'],
                'tempo_ms': tempo_ms
            })
    
    return resultados, tempo_total


def testar_dijkstra(grafo, pares):
    """Testa Dijkstra em multiplos pares (apenas com pesos >= 0)"""
    resultados = []
    tempo_total = 0
    
    for i, (origem, destino) in enumerate(pares, 1):
        try:
            resultado, tempo_ms = medir_tempo(dijkstra_parte2, grafo, origem, destino)
            tempo_total += tempo_ms
            
            if resultado and resultado['sucesso']:
                resultados.append({
                    'origem': origem,
                    'destino': destino,
                    'distancia': resultado['distancia'],
                    'caminho_size': len(resultado['caminho']) if resultado['caminho'] else 0,
                    'tempo_ms': tempo_ms
                })
        
        except ValueError as e:
            continue
    
    return resultados, tempo_total


def testar_bellman_ford(grafo, pares):
    """Testa Bellman-Ford incluindo casos com pesos negativos"""
    resultados = []
    tempo_total = 0
    
    for i, (origem, destino) in enumerate(pares, 1):
        resultado, tempo_ms = medir_tempo(bellman_ford, grafo, origem, destino)
        tempo_total += tempo_ms
        
        if resultado:
            ciclo = resultado.get('ciclo_negativo', {})
            
            resultados.append({
                'origem': origem,
                'destino': destino,
                'distancia': resultado.get('distancia'),
                'ciclo_negativo': ciclo.get('existe', False),
                'tempo_ms': tempo_ms
            })
    
    return resultados, tempo_total


def gerar_relatorio_comparativo(resultados_dict):
    """Gera relatorio comparativo em JSON"""
    
    testes_bfs = []
    for r in resultados_dict['bfs']['resultados']:
        testes_bfs.append({
            "origem": r['origem'],
            "total_visitados": r['total_visitados'],
            "tempo_ms": round(r['tempo_ms'], 4)
        })
    
    testes_dfs = []
    for r in resultados_dict['dfs']['resultados']:
        testes_dfs.append({
            "origem": r['origem'],
            "total_visitados": r['total_visitados'],
            "ciclos_detectados": r['tem_ciclos'],
            "tempo_ms": round(r['tempo_ms'], 4)
        })
    
    testes_dijkstra = []
    for r in resultados_dict['dijkstra']['resultados']:
        testes_dijkstra.append({
            "origem": r['origem'],
            "destino": r['destino'],
            "distancia": r['distancia'],
            "tamanho_caminho": r['caminho_size'],
            "tempo_ms": round(r['tempo_ms'], 4)
        })
    
    testes_bellman = []
    for r in resultados_dict['bellman_ford']['resultados']:
        teste = {
            "origem": r['origem'],
            "destino": r['destino'],
            "ciclo_negativo_detectado": r['ciclo_negativo'],
            "tempo_ms": round(r['tempo_ms'], 4)
        }
        if not r['ciclo_negativo'] and r['distancia'] is not None:
            teste['distancia'] = r['distancia']
        testes_bellman.append(teste)
    
    relatorio = {
        "algoritmos": [
            {
                "nome": "BFS",
                "tempo_total_ms": round(resultados_dict['bfs']['tempo'], 3),
                "total_testes": len(resultados_dict['bfs']['resultados']),
                "suporta_pesos": False,
                "suporta_pesos_negativos": False,
                "detecta_ciclos_negativos": False,
                "notas": "Rapido, mas ignora peso das arestas. Util para exploracao por niveis.",
                "testes": testes_bfs
            },
            {
                "nome": "DFS",
                "tempo_total_ms": round(resultados_dict['dfs']['tempo'], 3),
                "total_testes": len(resultados_dict['dfs']['resultados']),
                "suporta_pesos": False,
                "suporta_pesos_negativos": False,
                "detecta_ciclos_negativos": True,
                "notas": "Bom para detectar ciclos simples, nao calcula caminhos minimos.",
                "testes": testes_dfs
            },
            {
                "nome": "Dijkstra",
                "tempo_total_ms": round(resultados_dict['dijkstra']['tempo'], 3),
                "total_testes": len(resultados_dict['dijkstra']['resultados']),
                "suporta_pesos": True,
                "suporta_pesos_negativos": False,
                "detecta_ciclos_negativos": False,
                "notas": "Rapido e eficiente para pesos positivos. Falha com pesos negativos.",
                "testes": testes_dijkstra
            },
            {
                "nome": "Bellman-Ford",
                "tempo_total_ms": round(resultados_dict['bellman_ford']['tempo'], 3),
                "total_testes": len(resultados_dict['bellman_ford']['resultados']),
                "suporta_pesos": True,
                "suporta_pesos_negativos": True,
                "detecta_ciclos_negativos": True,
                "notas": "Lento (O(VE)), mas detecta ciclos negativos. Critico para validacao.",
                "testes": testes_bellman
            }
        ]
    }
    
    import os
    os.makedirs('out/parte2', exist_ok=True)
    
    with open('out/parte2/parte2_report.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    return relatorio


def executar_analise_completa():
    """Funcao principal que executa toda a analise da Parte 2"""
    import os
    os.makedirs('out/parte2', exist_ok=True)
    
    grafo = carregar_dataset_parte2()
    
    pares_teste = gerar_pares_teste(grafo, num_pares=5)
    
    origens_teste = [pares_teste[0][0], pares_teste[1][0], pares_teste[2][0]]
    
    resultados_bfs, tempo_bfs = testar_bfs(grafo, origens_teste)
    
    resultados_dfs, tempo_dfs = testar_dfs(grafo, origens_teste)
    
    pares_dijkstra = encontrar_pares_sem_pesos_negativos(grafo, num_pares=5)
    if not pares_dijkstra or len(pares_dijkstra) < 5:
        pares_dijkstra = pares_teste[:5]
    resultados_dijkstra, tempo_dijkstra = testar_dijkstra(grafo, pares_dijkstra)
    
    casos_bellman = encontrar_casos_bellman_ford(grafo)
    if len(casos_bellman) < 2:
        casos_bellman = casos_bellman + pares_teste[:2]
    resultados_bellman, tempo_bellman = testar_bellman_ford(grafo, casos_bellman)
    
    resultados_dict = {
        'bfs': {'tempo': tempo_bfs, 'resultados': resultados_bfs},
        'dfs': {'tempo': tempo_dfs, 'resultados': resultados_dfs},
        'dijkstra': {'tempo': tempo_dijkstra, 'resultados': resultados_dijkstra},
        'bellman_ford': {'tempo': tempo_bellman, 'resultados': resultados_bellman}
    }
    
    relatorio = gerar_relatorio_comparativo(resultados_dict)
    
    with open('out/parte2/parte2_report.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print("out/parte2/parte2_report.json")


def executar_algoritmo_individual(dataset_path, algoritmo, source, target=None, out_dir='./out/parte2'):
    """Executa um algoritmo especifico com origem e destino definidos"""
    import os
    os.makedirs(out_dir, exist_ok=True)
    
    grafo = carregar_dataset_parte2(dataset_path)
    
    if source not in grafo.vertices:
        sys.exit(1)
    
    if target and target not in grafo.vertices:
        sys.exit(1)
    
    resultado = None
    tempo_ms = 0
    
    try:
        if algoritmo == 'BFS':
            resultado, tempo_ms = medir_tempo(bfs, grafo, source)
        
        elif algoritmo == 'DFS':
            resultado, tempo_ms = medir_tempo(dfs, grafo, source)
        
        elif algoritmo == 'DIJKSTRA':
            resultado, tempo_ms = medir_tempo(dijkstra_parte2, grafo, source, target)
        
        elif algoritmo == 'BELLMAN_FORD':
            resultado, tempo_ms = medir_tempo(bellman_ford, grafo, source, target)
        
        else:
            sys.exit(1)
        
        relatorio = {
            "algoritmos": [
                {
                    "nome": algoritmo,
                    "origem": source,
                    "destino": target,
                    "tempo_ms": round(tempo_ms, 4),
                    "suporta_pesos": algoritmo in ['DIJKSTRA', 'BELLMAN_FORD'],
                    "suporta_pesos_negativos": algoritmo == 'BELLMAN_FORD',
                    "detecta_ciclos_negativos": algoritmo in ['DFS', 'BELLMAN_FORD']
                }
            ]
        }
        
        if algoritmo == 'BFS' and resultado:
            relatorio['algoritmos'][0]['total_visitados'] = resultado['total_visitados']
            relatorio['algoritmos'][0]['distancia_saltos'] = resultado['distancias'].get(target, None)
        
        elif algoritmo == 'DFS' and resultado:
            relatorio['algoritmos'][0]['total_visitados'] = resultado['total_visitados']
            relatorio['algoritmos'][0]['tem_ciclos'] = resultado['tem_ciclos']
            relatorio['algoritmos'][0]['quantidade_ciclos'] = len(resultado['ciclos_detectados'])
        
        elif algoritmo == 'DIJKSTRA' and resultado:
            if resultado['sucesso']:
                relatorio['algoritmos'][0]['distancia'] = resultado['distancia']
                relatorio['algoritmos'][0]['tamanho_caminho'] = len(resultado['caminho'])
                relatorio['algoritmos'][0]['sucesso'] = True
            else:
                relatorio['algoritmos'][0]['sucesso'] = False
        
        elif algoritmo == 'BELLMAN_FORD' and resultado:
            ciclo = resultado.get('ciclo_negativo', {})
            relatorio['algoritmos'][0]['ciclo_negativo_detectado'] = ciclo.get('existe', False)
            
            if not ciclo.get('existe') and resultado['sucesso']:
                relatorio['algoritmos'][0]['distancia'] = resultado['distancia']
                relatorio['algoritmos'][0]['tamanho_caminho'] = len(resultado['caminho']) if resultado['caminho'] else 0
                relatorio['algoritmos'][0]['sucesso'] = True
            else:
                relatorio['algoritmos'][0]['sucesso'] = False
        
        if algoritmo in ['BFS', 'DFS']:
            nome_arquivo = f"{algoritmo.lower()}_{source}.json"
        else:
            nome_arquivo = f"{algoritmo.lower()}_{source}_{target}.json"
        
        output_file = f"{out_dir}/{nome_arquivo}"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"{output_file}")
        
    except ValueError as e:
        sys.exit(1)
    except Exception as e:
        sys.exit(1)
