import pytest
from src.graphs.graph import GrafoDirecionado
from src.graphs.algorithms import bfs


def test_bfs_grafo_simples():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    grafo.adicionar_aresta('A', 'C', 1)
    grafo.adicionar_aresta('B', 'D', 1)
    grafo.adicionar_aresta('C', 'D', 1)
    
    resultado = bfs(grafo, 'A')
    
    assert resultado is not None
    assert resultado['total_visitados'] == 4
    assert 'A' in resultado['ordem_visitacao']
    assert len(resultado['niveis']) >= 1


def test_bfs_niveis_corretos():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    grafo.adicionar_aresta('A', 'C', 1)
    grafo.adicionar_aresta('B', 'D', 1)
    
    resultado = bfs(grafo, 'A')
    
    assert 'A' in resultado['niveis'][0]
    assert 'B' in resultado['niveis'][1]
    assert 'C' in resultado['niveis'][1]
    assert 'D' in resultado['niveis'][2]


def test_bfs_origem_invalida():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    
    resultado = bfs(grafo, 'Z')
    assert resultado is None


def test_bfs_ignora_pesos():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 100)
    grafo.adicionar_aresta('A', 'C', 1)
    
    resultado = bfs(grafo, 'A')
    
    assert 'B' in resultado['niveis'][1]
    assert 'C' in resultado['niveis'][1]

