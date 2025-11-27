import pytest
from src.graphs.graph import GrafoDirecionado
from src.graphs.algorithms import dfs


def test_dfs_grafo_simples():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    grafo.adicionar_aresta('B', 'C', 1)
    grafo.adicionar_aresta('C', 'A', 1)
    
    resultado = dfs(grafo, 'A')
    
    assert resultado is not None
    assert resultado['total_visitados'] >= 1
    assert 'A' in resultado['ordem_visitacao']


def test_dfs_detecta_ciclo():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    grafo.adicionar_aresta('B', 'C', 1)
    grafo.adicionar_aresta('C', 'A', 1)
    
    resultado = dfs(grafo, 'A')
    
    assert resultado['tem_ciclos'] == True


def test_dfs_sem_ciclo():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    grafo.adicionar_aresta('B', 'C', 1)
    
    resultado = dfs(grafo, 'A')
    
    assert resultado['tem_ciclos'] == False


def test_dfs_origem_invalida():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    
    resultado = dfs(grafo, 'Z')
    assert resultado is None

