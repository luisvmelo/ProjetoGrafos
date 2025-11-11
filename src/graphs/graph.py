import pandas as pd

class Grafo:
    def __init__(self):
        self.vertices = set()
        self.arestas = []

    def adicionar_vertice(self, vertice):
        self.vertices.add(vertice)

    def adicionar_aresta(self, origem, destino, logradouro, peso):
        self.vertices.add(origem)
        self.vertices.add(destino)
        self.arestas.append({
            'origem': origem,
            'destino': destino,
            'logradouro': logradouro,
            'peso': peso
        })

    def obter_vizinhos(self, vertice):
        vizinhos = []
        for aresta in self.arestas:
            if aresta['origem'] == vertice:
                vizinhos.append({
                    'destino': aresta['destino'],
                    'logradouro': aresta['logradouro'],
                    'peso': aresta['peso']
                })
            elif aresta['destino'] == vertice:
                vizinhos.append({
                    'destino': aresta['origem'],
                    'logradouro': aresta['logradouro'],
                    'peso': aresta['peso']
                })
        return vizinhos

    def obter_aresta(self, origem, destino):
        for aresta in self.arestas:
            if (aresta['origem'] == origem and aresta['destino'] == destino) or \
               (aresta['origem'] == destino and aresta['destino'] == origem):
                return aresta
        return None

    def total_vertices(self):
        return len(self.vertices)

    def total_arestas(self):
        return len(self.arestas)

def construir_grafo_bairros():
    df = pd.read_csv('data/adjacencias_bairros.csv')

    grafo = Grafo()

    for _, row in df.iterrows():
        bairro_origem = row['bairro_origem']
        bairro_destino = row['bairro_destino']
        logradouro = row['logradouro']
        peso = row['peso']

        grafo.adicionar_aresta(bairro_origem, bairro_destino, logradouro, peso)

    return grafo

if __name__ == '__main__':
    grafo = construir_grafo_bairros()

    print(f"Grafo construído com sucesso!")
    print(f"Total de vértices (bairros): {grafo.total_vertices()}")
    print(f"Total de arestas (vias): {grafo.total_arestas()}")

    print("\nExemplo - Vizinhos de 'Aflitos':")
    vizinhos = grafo.obter_vizinhos('Aflitos')
    for v in vizinhos[:5]:
        print(f"  -> {v['destino']} via {v['logradouro']} (peso: {v['peso']})")
