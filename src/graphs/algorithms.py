def dijkstra(grafo, origem, destino):
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
