# Projeto Grafos - Análise da Cidade do Recife

**Disciplina:** Grafos  
**Instituição:** CESAR School  
**Período:** 2025.2

**Grupo:**
- Brandon de Oliveira Hunt
- Lucas Rosati Cavalcanti Pereira
- Luis Eduardo Vieira Melo
- Ronaldo Tavares Souto Maior

---

## Documentação

- **README.md** (este arquivo): Instruções de instalação e execução
- **Manual.pdf**: Documentação técnica completa do projeto
- **Análise_parte2.pdf**: Análise crítica da Parte 2

---

## Visão Geral

Este projeto implementa e analisa algoritmos de grafos aplicados a dados reais da cidade do Recife:

- **Parte 1**: Análise dos 94 bairros do Recife (transporte, saúde, educação, acidentes)
- **Parte 2**: Comparação de 4 algoritmos clássicos (BFS, DFS, Dijkstra, Bellman-Ford)

**Características**:
- Implementação própria de todos os algoritmos (sem libs externas)
- Visualizações interativas em HTML5 Canvas
- Dados reais geográficos da cidade do Recife
- 16 testes unitários e de integração

---

## Instalação

### Requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passo 1: Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd ProjetoGrafos
```

### Passo 2: Criar Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```
---

## Como Executar

### Parte 1 - Análise dos Bairros do Recife

#### Gerar Métricas

```bash
python3 src/graphs/metricas.py
```

**Saída**:
- `out/parte1/recife_global.json` - Métricas globais do grafo
- `out/parte1/microrregioes.json` - Métricas por microrregião
- `out/parte1/ego_bairro.csv` - Densidade ego por bairro

#### Calcular Caminhos Entre Endereços

```bash
python3 src/graphs/calcular_distancias_enderecos.py
```

**Saída**:
- `out/parte1/distancias_enderecos.csv` - 6 caminhos calculados
- `out/parte1/percurso_nova_descoberta_setubal.json` - Detalhes de um caminho

#### Gerar Visualização Principal

```bash
python3 src/graphs/visualizar_grafo_completo.py
```

**Saída**:
- `out/parte1/grafo_interativo.html` - Visualização interativa completa

#### Gerar Visualizações Temáticas

```bash
# Acidentes de trânsito
cd Visualizacao_Acidentes
python3 visualizar_grafo_acidentes.py
cd ..

# Saúde
cd Visualizaçao_Saude
python3 visualizar_grafo_saude.py
cd ..

# Transporte
cd Visualizacao_Transporte
python3 visualizar_grafo_transporte.py
cd ..

# Educação
cd grafico_educacao_recife
python3 visualizar_grafo_educacao.py
python3 visualizar_educacao_quadrantes.py
cd ..
```

**Saída**: 5 arquivos HTML em `out/parte1/`:
- `grafo_acidentes.html`
- `grafo_saude_ocde.html`
- `grafo_transporte.html`
- `grafo_educacao.html`
- `grafo_educacao_quadrantes.html`

---

### Parte 2 - Comparação de Algoritmos

#### Executar Análise Completa

```bash
# Executar comparação completa
python3 -m src.cli --dataset ./data/dataset_parte2/ --comparar

# Gerar visualização HTML interativa
python3 -m src.cli --dataset ./data/dataset_parte2/ --visualizar
```

**Saída**:
- `out/parte2/parte2_report.json` - Relatório comparativo completo
- `out/parte2/amostra_grafo.html` - Visualização interativa HTML5 Canvas

**Características da visualização**:
- 50 vértices selecionados aleatoriamente do grafo completo
- Arestas coloridas (verde = positivas, vermelho = negativas)
- Interativa: zoom, pan, tooltips ao passar o mouse
- Gerada com código próprio (sem NetworkX)

**O que é testado**:
- BFS: 3 origens distintas
- DFS: 3 origens distintas + detecção de ciclos
- Dijkstra: 5 pares origem-destino (pesos ≥ 0)
- Bellman-Ford: 2 casos
  - Caso 1: Peso negativo SEM ciclo negativo
  - Caso 2: Ciclo negativo detectado


---

## Estrutura do Projeto

```
ProjetoGrafos/
├── README.md                    # Este arquivo
├── MANUAL_TECNICO.md           # Documentação técnica completa
├── PARTE2_ANALISE_CRITICA.md   # Análise crítica da Parte 2
├── requirements.txt             # Dependências
│
├── data/                        # 41MB de dados
│   ├── adjacencias_bairros.csv # Dados principais do grafo
│   ├── bairros.geojson         # Geometrias dos bairros
│   └── dataset_parte2/         # Dataset para Parte 2
│
├── out/
│   ├── parte1/                  # 11 arquivos gerados 
│   └── parte2/                  # 2 arquivos gerados
│
├── src/
│   ├── graphs/                  # Core do sistema
│   │   ├── graph.py            # Classe Grafo
│   │   ├── algorithms.py       # BFS, DFS, Dijkstra, Bellman-Ford
│   │   ├── metricas.py         # Cálculo de métricas
│   │   └── ...
│   ├── edges/                   # Pipeline de construção de arestas
│   ├── cli.py                   # Interface CLI
│   ├── solve.py                 # Orquestrador Parte 2
│   └── viz.py                   # Visualização HTML interativa 
│
├── tests/                       # 16 testes
│   ├── test_bfs.py
│   ├── test_dfs.py
│   ├── test_dijkstra.py
│   └── test_bellman_ford.py
│
├── Visualizacao_Acidentes/
├── Visualizaçao_Saude/
├── Visualizacao_Transporte/
└── grafico_educacao_recife/
```

---

## Como Visualizar os Resultados

### Abrir Visualizações HTML

```bash
# Parte 1
open out/parte1/grafo_interativo.html
open out/parte1/grafo_acidentes.html
open out/parte1/grafo_saude_ocde.html
open out/parte1/grafo_transporte.html
open out/parte1/grafo_educacao.html
open out/parte1/grafo_educacao_quadrantes.html

# Parte 2
open out/parte2/amostra_grafo.html
```

**Controles interativos (Parte 1)**:
- Arrastar: Move o mapa
- Scroll: Zoom in/out
- Clicar: Destaca conexões
- Campo de busca: Encontrar bairro
- Filtros: Por microrregião

**Controles interativos (Parte 2)**:
- Arrastar: Move o grafo
- Scroll: Zoom in/out
- Hover: Ver informações do vértice (nome e grau)
- Botões: Resetar visualização, Zoom +/-
- Cores: Verde (arestas positivas), Vermelho (arestas negativas)

---

## Exemplos de Uso

### Calcular Caminho Mínimo (Python)

```python
from src.graphs.graph import construir_grafo_bairros
from src.graphs.algorithms import dijkstra

# Carregar grafo
grafo = construir_grafo_bairros()

# Calcular caminho
resultado = dijkstra(grafo, "Nova Descoberta", "Boa Viagem")

print(f"Distância: {resultado['distancia']:.2f}m")
print(f"Caminho: {' -> '.join(resultado['caminho'])}")
```

### Executar BFS

```python
from src.graphs.algorithms import bfs

resultado = bfs(grafo, "Aflitos")

print(f"Total visitados: {resultado['total_visitados']}")
print(f"Níveis: {len(resultado['niveis'])}")
```

### Detectar Ciclos com DFS

```python
from src.graphs.algorithms import dfs

resultado = dfs(grafo, "Santo Amaro")

if resultado['ciclos_detectados']:
    print("Ciclos encontrados!")
    print(f"Total de ciclos: {len(resultado['ciclos'])}")
```

---

## Leitura Adicional

Para detalhes técnicos completos, consulte:

- **Manual.pdf**: Arquitetura, estruturas de dados, algoritmos detalhados, fontes
- **Análise_parte2.md**: Análise de desempenho, quando usar cada algoritmo

---

## Informações adicionais

**Projeto Acadêmico** - CESAR School 2024.2

**Dados**: Cidade do Recife (GeoJSON oficial)

**Tecnologias**: Python, Pandas, HTML5 Canvas, JavaScript
