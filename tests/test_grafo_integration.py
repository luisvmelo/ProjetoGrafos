import os
import pytest

from src.graphs.graph import construir_grafo_bairros


DATA_PATH = os.path.join("data", "adjacencias_bairros.csv")


@pytest.mark.skipif(
    not os.path.exists(DATA_PATH),
    reason="Arquivo data/adjacencias_bairros.csv não encontrado",
)
def test_construir_grafo_bairros_carrega_todos_os_dados():
    grafo = construir_grafo_bairros()

    # Esses valores vêm do README / saídas que você já mostrou:
    # Vertices: 94
    # Arestas: 944
    assert grafo.total_vertices() == 94
    assert grafo.total_arestas() == 944

    # sanity checks extras
    assert "Aflitos" in grafo.vertices
    assert "Boa Viagem" in grafo.vertices

    # deve existir pelo menos uma aresta ligando algum bairro a outro
    assert any(a["origem"] != a["destino"] for a in grafo.arestas)
