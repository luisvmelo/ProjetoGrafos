import math
import pytest

from src.graphs.graph import Grafo, GrafoDirecionado
from src.graphs.algorithms import dijkstra, dijkstra_parte2


def build_simple_graph():
    g = Grafo()
    g.adicionar_aresta("Aflitos", "Espinheiro", "Rua 1", 100.0)
    g.adicionar_aresta("Espinheiro", "Boa Vista", "Rua 2", 50.0)
    g.adicionar_aresta("Aflitos", "Boa Vista", "Rua 3", 300.0)
    return g


def test_dijkstra_encontra_caminho_minimo():
    grafo = build_simple_graph()

    caminho, distancia, vias = dijkstra(grafo, "Aflitos", "Boa Vista")

    assert caminho == ["Aflitos", "Espinheiro", "Boa Vista"]
    assert math.isclose(distancia, 150.0)

    assert isinstance(vias, list)
    assert len(vias) == 2  
    assert vias == ["Rua 1", "Rua 2"]


def test_dijkstra_origem_igual_destino():
    grafo = build_simple_graph()

    caminho, distancia, vias = dijkstra(grafo, "Aflitos", "Aflitos")

    assert caminho == ["Aflitos"]
    assert math.isclose(distancia, 0.0)
    assert vias == [] 


def test_dijkstra_recusa_peso_negativo():
    grafo = GrafoDirecionado()
    grafo.adicionar_aresta('A', 'B', -5)
    
    with pytest.raises(ValueError, match="nao suporta pesos negativos"):
        dijkstra_parte2(grafo, 'A', 'B')
