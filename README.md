# Projeto Grafos - Bairros do Recife

Projeto que mapeia os bairros do Recife como um grafo, onde cada bairro é um vértice e as vias que conectam os bairros são as arestas. O objetivo é aplicar algoritmos de grafos para analisar a estrutura da cidade e calcular caminhos mínimos entre diferentes localizações.

- O grafo é não-direcionado
- Existem arestas paralelas
- Os pesos são distâncias em metros calculadas a partir de dados geográficos reais

## O que o projeto faz

O projeto pega dados geográficos dos bairros do Recife e cria um grafo completo onde:
- **Vértices**: 94 bairros da cidade
- **Arestas**: 944 vias que conectam os bairros (com múltiplas vias entre alguns pares)
- **Pesos**: Distâncias reais em metros entre os bairros

Com isso, conseguimos:
1. Visualizar a estrutura de conectividade da cidade
2. Calcular o caminho mais curto entre qualquer par de bairros
3. Analisar métricas do grafo (densidade, grau dos vértices, densidade ego)
4. Ver todas as vias que conectam cada par de bairros

## Visualização Interativa

O projeto gera uma visualização HTML totalmente interativa do grafo. Para abrir:

```bash
# Abra o arquivo no navegador
out/grafo_interativo.html
```

### Funcionalidades da visualização:

- **Zoom e navegação**: Use o scroll do mouse para zoom e arraste para mover o grafo
- **Tooltips**: Passe o mouse sobre um bairro para ver grau, microrregião e densidade ego
- **Busca de caminho**: Digite dois bairros nos campos de busca para calcular o menor caminho entre eles usando Dijkstra
- **Destaque de vizinhos**: Clique em um bairro para destacar todos os bairros adjacentes e as vias que os conectam
- **Caminho pré-calculado**: Botão para destacar o caminho entre Nova Descoberta e Boa Viagem (Setúbal)
- **Cores por microrregião**: Cada microrregião tem uma cor diferente, bairros em múltiplas microrregiões têm cores divididas
- **Todas as vias visíveis**: As 944 vias aparecem como curvas paralelas para evitar sobreposição

## Estrutura do Projeto

```
ProjetoGrafos/
├── data/                           # Dados de entrada
│   ├── adjacencias_bairros.csv    # Arestas do grafo (origem, destino, via, peso)
│   ├── bairros_unique.csv         # Lista de bairros normalizados
│   └── bvisualizacao_fcbairro.geojson  # Dados geográficos
│
├── out/                            # Arquivos gerados
│   ├── grafo_interativo.html      # Visualização interativa (ABRA ESTE!)
│   ├── recife_global.json         # Métricas globais do grafo
│   ├── recife_local.json          # Métricas locais (por bairro)
│   ├── distancias_enderecos.csv   # Caminhos calculados entre pares
│   └── percurso_nova_descoberta_setubal.json  # Detalhes de um caminho específico
│
└── src/
    ├── edges/                      # Scripts para gerar adjacências
    │   └── build_from_geojson_queen.py
    │
    └── graphs/                     # Core do projeto
        ├── graph.py                # Classe do grafo
        ├── algorithms.py           # Algoritmo de Dijkstra
        ├── metrics.py              # Cálculo de métricas
        ├── calcular_distancias_enderecos.py  # Calcula caminhos entre pares
        └── visualizar_grafo_completo.py      # Gera a visualização HTML
```

## Como rodar o projeto

### Pré-requisitos

```bash
pip install pandas
```

### 1. Calcular métricas do grafo

From Project Root run
```bash
python src/graphs/metricas.py
```

Gera `recife_global.json` e `recife_local.json` com:
- Ordem (número de vértices)
- Tamanho (número de arestas)
- Densidade do grafo
- Grau de cada bairro
- Densidade ego de cada vértice

### 2. Calcular caminhos entre endereços

```bash
python calcular_distancias_enderecos.py
```

Calcula o menor caminho (Dijkstra) entre 6 pares de endereços pré-definidos e salva em `distancias_enderecos.csv`.

### 3. Gerar visualização interativa

```bash
python src/graphs/visualizar_grafo_completo.py
```

Gera o arquivo `out/grafo_interativo.html` com toda a interatividade.

## Algoritmos Implementados

### Dijkstra

Implementado em `algorithms.py` e também em JavaScript no frontend da visualização. Calcula o menor caminho entre dois bairros considerando as distâncias reais das vias.

**Complexidade**: O(V²) no frontend, O(V²) no backend (sem heap)

**Saída**: Retorna o caminho, a distância total e as vias específicas utilizadas.

## Detalhes Técnicos

- **Layout da visualização**: Clustering por microrregião com disposição orgânica
- **Arestas paralelas**: Renderizadas com curvas de Bezier para mostrar todas as 944 vias
- **Detecção de clique vs arrasto**: Threshold de 5px para distinguir clique de drag
- **Canvas HTML5**: Renderização eficiente com zoom e pan suaves

## Exemplos de Uso

### Caminho mais curto entre Aflitos e Pina

```
Aflitos -> Graças -> Derby -> Boa Vista -> Santo Antônio -> São José -> Pina
Distância: 1991.66m
```

### Caminho mais curto entre Nova Descoberta e Boa Viagem

```
Nova Descoberta -> Brejo de Beberibe -> Alto José Bonifácio -> Alto Santa Teresinha ->
Bomba do Hemetério -> Arruda -> Campo Grande -> Santo Amaro -> Santo Antônio ->
São José -> Pina -> Boa Viagem
Distância: 2682.05m
```

Brandon Hunt
Lucas Rosati 
Luis Melo 
Ronaldo Tavares Souto Maior
