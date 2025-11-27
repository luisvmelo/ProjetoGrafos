import pytest
from src.graphs.graph import GrafoDirecionado
from src.graphs.algorithms import bellman_ford


def test_bellman_ford_caminho_simples():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 5)
    grafo.adicionar_aresta('B', 'C', 3)
    
    resultado = bellman_ford(grafo, 'A', 'C')
    
    assert resultado['sucesso'] == True
    assert resultado['distancia'] == 8
    assert resultado['caminho'] == ['A', 'B', 'C']


def test_bellman_ford_peso_negativo_sem_ciclo():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 10)
    grafo.adicionar_aresta('B', 'C', -5)
    
    resultado = bellman_ford(grafo, 'A', 'C')
    
    assert resultado['sucesso'] == True
    assert resultado['distancia'] == 5
    assert resultado['ciclo_negativo']['existe'] == False


def test_bellman_ford_ciclo_negativo():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 1)
    grafo.adicionar_aresta('B', 'C', 1)
    grafo.adicionar_aresta('C', 'A', -5)
    
    resultado = bellman_ford(grafo, 'A', 'C')
    
    assert resultado['ciclo_negativo']['existe'] == True


def test_bellman_ford_desconto():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 20)
    grafo.adicionar_aresta('A', 'C', 5)
    grafo.adicionar_aresta('C', 'D', -2)
    grafo.adicionar_aresta('D', 'B', 10)
    
    resultado = bellman_ford(grafo, 'A', 'B')
    
    assert resultado['distancia'] == 13


def test_bellman_ford_origem_invalida():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', 5)
    
    resultado = bellman_ford(grafo, 'Z', 'B')
    assert resultado is None

