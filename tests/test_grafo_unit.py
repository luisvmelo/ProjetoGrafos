import math
import pytest

from src.graphs.graph import Grafo


def test_adicionar_vertice_e_arestas():
    grafo = Grafo()

    grafo.adicionar_vertice("Aflitos")
    grafo.adicionar_aresta("Aflitos", "Espinheiro", "Rua Teste", 123.4)

    # vertices devem conter ambos Aflitos e Espinheiro
    assert "Aflitos" in grafo.vertices
    assert "Espinheiro" in grafo.vertices

    # deve ter exatamente 1 aresta
    assert grafo.total_arestas() == 1
    assert len(grafo.arestas) == 1

    aresta = grafo.arestas[0]
    assert aresta["origem"] == "Aflitos"
    assert aresta["destino"] == "Espinheiro"
    assert aresta["logradouro"] == "Rua Teste"
    assert math.isclose(aresta["peso"], 123.4)


def test_obter_vizinhos_retorna_ambas_direcoes():
    grafo = Grafo()
    grafo.adicionar_aresta("Aflitos", "Espinheiro", "Rua 1", 100)
    grafo.adicionar_aresta("Aflitos", "Derby", "Rua 2", 200)

    vizinhos_aflitos = grafo.obter_vizinhos("Aflitos")
    destinos = {v["destino"] for v in vizinhos_aflitos}

    assert destinos == {"Espinheiro", "Derby"}

    vizinhos_espinheiro = grafo.obter_vizinhos("Espinheiro")
    destinos_espinheiro = {v["destino"] for v in vizinhos_espinheiro}

    # como o grafo é não-direcionado, Espinheiro deve ver Aflitos como vizinho
    assert destinos_espinheiro == {"Aflitos"}


def test_obter_vizinhos_bairro_sem_arestas():
    grafo = Grafo()
    grafo.adicionar_vertice("Boa Vista")

    vizinhos = grafo.obter_vizinhos("Boa Vista")
    assert vizinhos == []  # sem arestas, sem vizinhos


def test_obter_aresta_simples():
    grafo = Grafo()
    grafo.adicionar_aresta("Aflitos", "Espinheiro", "Rua 1", 100)

    aresta = grafo.obter_aresta("Aflitos", "Espinheiro")
    assert aresta is not None
    assert aresta["origem"] == "Aflitos"
    assert aresta["destino"] == "Espinheiro"

    # deve funcionar independente da ordem origem/destino
    aresta2 = grafo.obter_aresta("Espinheiro", "Aflitos")
    assert aresta2 is not None
    assert aresta2["origem"] == "Aflitos"
    assert aresta2["destino"] == "Espinheiro"


def test_obter_aresta_inexistente():
    grafo = Grafo()
    grafo.adicionar_aresta("Aflitos", "Espinheiro", "Rua 1", 100)

    aresta = grafo.obter_aresta("Boa Vista", "Derby")
    assert aresta is None
