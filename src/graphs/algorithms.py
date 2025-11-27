from collections import deque
import time


def bfs(grafo, origem):
    """Busca em Largura - explora por niveis, ignora pesos"""
    if origem not in grafo.vertices:
        return None
    
    visitados = set()
    fila = deque([(origem, 0)])
    ordem_visitacao = []
    niveis = {}
    distancias = {origem: 0}
    
    while fila:
        vertice_atual, nivel = fila.popleft()
        
        if vertice_atual in visitados:
            continue
        
        visitados.add(vertice_atual)
        ordem_visitacao.append(vertice_atual)
        
        if nivel not in niveis:
            niveis[nivel] = []
        niveis[nivel].append(vertice_atual)
        
        for destino, _ in grafo.obter_vizinhos(vertice_atual):
            if destino not in visitados:
                fila.append((destino, nivel + 1))
                if destino not in distancias:
                    distancias[destino] = nivel + 1
    
    return {
        'ordem_visitacao': ordem_visitacao,
        'niveis': niveis,
        'distancias': distancias,
        'total_visitados': len(visitados)
    }


def dfs(grafo, origem):
    """Busca em Profundidade - explora em profundidade, detecta ciclos"""
    if origem not in grafo.vertices:
        return None
    
    visitados = set()
    ordem_visitacao = []
    ciclos_detectados = []
    em_processamento = set()
    
    def dfs_recursivo(vertice, caminho_atual):
        if vertice in em_processamento:
            idx = caminho_atual.index(vertice)
            ciclo = caminho_atual[idx:] + [vertice]
            ciclos_detectados.append(ciclo)
            return
        
        if vertice in visitados:
            return
        
        visitados.add(vertice)
        em_processamento.add(vertice)
        ordem_visitacao.append(vertice)
        
        for destino, _ in grafo.obter_vizinhos(vertice):
            dfs_recursivo(destino, caminho_atual + [vertice])
        
        em_processamento.remove(vertice)
    
    dfs_recursivo(origem, [])
    
    return {
        'ordem_visitacao': ordem_visitacao,
        'ciclos_detectados': ciclos_detectados,
        'total_visitados': len(visitados),
        'tem_ciclos': len(ciclos_detectados) > 0
    }


def dijkstra(grafo, origem, destino):
    """Dijkstra original para a Parte 1 (grafo nao-direcionado de bairros)"""
    if origem not in grafo.vertices or destino not in grafo.vertices:
        return None, float('inf'), []

    distancias = {v: float('inf') for v in grafo.vertices}
    distancias[origem] = 0
    anteriores = {v: None for v in grafo.vertices}
    visitados = set()

    while len(visitados) < len(grafo.vertices):
        atual = None
        menor_distancia = float('inf')

        for v in grafo.vertices:
            if v not in visitados and distancias[v] < menor_distancia:
                menor_distancia = distancias[v]
                atual = v

        if atual is None or distancias[atual] == float('inf'):
            break

        visitados.add(atual)

        if atual == destino:
            break

        vizinhos = grafo.obter_vizinhos(atual)
        for vizinho in vizinhos:
            v = vizinho['destino']
            peso = vizinho['peso']

            if v not in visitados:
                nova_distancia = distancias[atual] + peso

                if nova_distancia < distancias[v]:
                    distancias[v] = nova_distancia
                    anteriores[v] = atual

    if distancias[destino] == float('inf'):
        return None, float('inf'), []

    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anteriores[atual]
    caminho.reverse()

    vias = []
    for i in range(len(caminho) - 1):
        bairro_atual = caminho[i]
        proximo_bairro = caminho[i + 1]

        vizinhos = grafo.obter_vizinhos(bairro_atual)
        for viz in vizinhos:
            if viz['destino'] == proximo_bairro:
                vias.append(viz['logradouro'])
                break

    return caminho, distancias[destino], vias


def dijkstra_parte2(grafo, origem, destino):
    """Dijkstra para Parte 2 - so funciona com pesos positivos"""
    if origem not in grafo.vertices or destino not in grafo.vertices:
        return None
    
    distancias = {v: float('inf') for v in grafo.vertices}
    distancias[origem] = 0
    anteriores = {v: None for v in grafo.vertices}
    visitados = set()
    
    while len(visitados) < len(grafo.vertices):
        atual = None
        menor_distancia = float('inf')
        
        for v in grafo.vertices:
            if v not in visitados and distancias[v] < menor_distancia:
                menor_distancia = distancias[v]
                atual = v
        
        if atual is None or distancias[atual] == float('inf'):
            break
        
        visitados.add(atual)
        
        if atual == destino:
            break
        
        for vizinho, peso in grafo.obter_vizinhos(atual):
            if peso < 0:
                continue
            
            if vizinho not in visitados:
                nova_distancia = distancias[atual] + peso
                
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    anteriores[vizinho] = atual
    
    def reconstruir_caminho(dest):
        if distancias[dest] == float('inf'):
            return None
        caminho = []
        atual = dest
        while atual is not None:
            caminho.append(atual)
            atual = anteriores[atual]
        caminho.reverse()
        return caminho
    
    caminho = reconstruir_caminho(destino)
    return {
        'distancia': distancias[destino],
        'caminho': caminho,
        'sucesso': caminho is not None
    }


def bellman_ford(grafo, origem, destino=None):
    """Bellman-Ford - funciona com pesos negativos e detecta ciclos negativos"""
    if origem not in grafo.vertices:
        return None
    
    distancias = {v: float('inf') for v in grafo.vertices}
    distancias[origem] = 0
    anteriores = {v: None for v in grafo.vertices}
    
    num_vertices = len(grafo.vertices)
    
    for i in range(num_vertices - 1):
        atualizado = False
        
        for aresta in grafo.arestas:
            u = aresta['origem']
            v = aresta['destino']
            peso = aresta['peso']
            
            if distancias[u] != float('inf') and distancias[u] + peso < distancias[v]:
                distancias[v] = distancias[u] + peso
                anteriores[v] = u
                atualizado = True
        
        if not atualizado:
            break
    
    ciclo_negativo = None
    vertices_no_ciclo = set()
    
    for aresta in grafo.arestas:
        u = aresta['origem']
        v = aresta['destino']
        peso = aresta['peso']
        
        if distancias[u] != float('inf') and distancias[u] + peso < distancias[v]:
            vertices_no_ciclo.add(v)
            vertices_no_ciclo.add(u)
            
            caminho_ciclo = [v]
            atual = anteriores[v]
            visitados_ciclo = set()
            
            while atual and atual not in visitados_ciclo:
                caminho_ciclo.append(atual)
                visitados_ciclo.add(atual)
                if atual == v:
                    break
                atual = anteriores[atual]
                if len(caminho_ciclo) > num_vertices:
                    break
            
            peso_ciclo = 0
            for i in range(len(caminho_ciclo) - 1):
                for aresta_ciclo in grafo.arestas:
                    if aresta_ciclo['origem'] == caminho_ciclo[i] and aresta_ciclo['destino'] == caminho_ciclo[i+1]:
                        peso_ciclo += aresta_ciclo['peso']
                        break
            
            ciclo_negativo = {
                'existe': True,
                'vertices': list(vertices_no_ciclo),
                'caminho': caminho_ciclo,
                'peso_total': peso_ciclo
            }
            break
    
    if ciclo_negativo is None:
        ciclo_negativo = {'existe': False}
    
    def reconstruir_caminho(dest):
        if distancias[dest] == float('inf'):
            return None
        caminho = []
        atual = dest
        visitados_caminho = set()
        
        while atual is not None:
            if atual in visitados_caminho:
                break
            caminho.append(atual)
            visitados_caminho.add(atual)
            atual = anteriores[atual]
            if len(caminho) > num_vertices:
                break
        
        caminho.reverse()
        return caminho
    
    if destino:
        caminho = reconstruir_caminho(destino)
        return {
            'distancia': distancias[destino],
            'caminho': caminho,
            'ciclo_negativo': ciclo_negativo,
            'sucesso': caminho is not None and not ciclo_negativo['existe']
        }
    
    return {
        'distancias': distancias,
        'anteriores': anteriores,
        'ciclo_negativo': ciclo_negativo
    }


def medir_tempo(funcao, *args, **kwargs):
    """Mede tempo de execucao em milissegundos"""
    inicio = time.perf_counter()
    resultado = funcao(*args, **kwargs)
    fim = time.perf_counter()
    tempo_ms = (fim - inicio) * 1000
    return resultado, tempo_ms
