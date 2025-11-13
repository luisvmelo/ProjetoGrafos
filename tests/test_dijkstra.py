import math
import pytest

from src.graphs.graph import Grafo
from src.graphs.algorithms import dijkstra


def build_simple_graph():
    """
    Aflitos --100--> Espinheiro --50--> Boa Vista
         \                         ^
          \--300-------------------/
    """
    g = Grafo()
    g.adicionar_aresta("Aflitos", "Espinheiro", "Rua 1", 100.0)
    g.adicionar_aresta("Espinheiro", "Boa Vista", "Rua 2", 50.0)
    g.adicionar_aresta("Aflitos", "Boa Vista", "Rua 3", 300.0)
    return g


def test_dijkstra_encontra_caminho_minimo():
    grafo = build_simple_graph()

    caminho, distancia, vias = dijkstra(grafo, "Aflitos", "Boa Vista")

    # Caminho ótimo: Aflitos -> Espinheiro -> Boa Vista (100 + 50 = 150)
    assert caminho == ["Aflitos", "Espinheiro", "Boa Vista"]
    assert math.isclose(distancia, 150.0)

    # vias deve ser uma lista detalhando as ruas usadas
    assert isinstance(vias, list)
    assert len(vias) == 2  # duas arestas no caminho mínimo
    assert vias == ["Rua 1", "Rua 2"]


def test_dijkstra_origem_igual_destino():
    grafo = build_simple_graph()

    caminho, distancia, vias = dijkstra(grafo, "Aflitos", "Aflitos")

    assert caminho == ["Aflitos"]
    assert math.isclose(distancia, 0.0)
    assert vias == []  # nenhum deslocamento → nenhuma via
