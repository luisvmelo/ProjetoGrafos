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


class GrafoDirecionado:
    """Grafo direcionado para a Parte 2"""
    def __init__(self):
        self.adj_list = {}
        self.vertices = set()
        self.arestas = []
        
    def adicionar_vertice(self, vertice):
        if vertice not in self.adj_list:
            self.adj_list[vertice] = []
            self.vertices.add(vertice)
    
    def adicionar_aresta(self, origem, destino, peso, info=None):
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self.adj_list[origem].append((destino, peso))
        self.arestas.append({
            'origem': origem,
            'destino': destino,
            'peso': peso,
            'info': info
        })
    
    def obter_vizinhos(self, vertice):
        return self.adj_list.get(vertice, [])
    
    def total_vertices(self):
        return len(self.vertices)
    
    def total_arestas(self):
        return len(self.arestas)
    
    def obter_estatisticas(self):
        pesos = [aresta['peso'] for aresta in self.arestas]
        return {
            'num_vertices': len(self.vertices),
            'num_arestas': len(self.arestas),
            'peso_min': min(pesos) if pesos else 0,
            'peso_max': max(pesos) if pesos else 0,
            'peso_medio': sum(pesos) / len(pesos) if pesos else 0,
            'arestas_positivas': sum(1 for p in pesos if p > 0),
            'arestas_negativas': sum(1 for p in pesos if p < 0)
        }

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
