# 🔍 ANÁLISE COMPLETA DO PROJETO GRAFOS - BAIRROS DO RECIFE

## 📋 SUMÁRIO EXECUTIVO

**Projeto:** Sistema de Análise de Grafos para Mapeamento Urbano de Recife
**Equipe:** Brandon de Oliveira Hunt, Lucas Rosati Cavalcanti Pereira, Luis Eduardo Vieira Melo, Ronaldo Tavares Souto Maior
**Linguagem:** Python 3
**Tipo de Grafo:** Não-direcionado, com arestas paralelas e pesos reais
**Escala:** 94 vértices (bairros), 944 arestas (vias), 944 linhas no CSV

---

## 🏗️ ARQUITETURA E ESTRUTURA DO PROJETO

### Estrutura de Diretórios

```
ProjetoGrafos/
├── data/                    # 41MB de dados geográficos
│   ├── adjacencias_bairros.csv              # 49KB - DADOS PRINCIPAIS DO GRAFO
│   ├── adjacencias_provisorio.csv           # 5.3KB - Adjacências brutas
│   ├── bairros.geojson                      # 2.1MB - Geometrias dos bairros
│   ├── bairros_recife.xlsx                  # 5.9KB - Lista original de bairros
│   ├── bairros_unique.csv                   # 1.5KB - Bairros normalizados
│   ├── bvisualizacao_fctrechologradouro.geojson  # 17MB - Geometrias das vias
│   ├── distancias_vias.csv                  # 47KB - Distâncias calculadas
│   ├── enderecos.csv                        # 298B - Endereços de teste
│   ├── facequadra.csv                       # 23MB - Dados de quadras
│   └── vias_conectam_bairros_SELECIONADOS.csv    # 44KB - Vias por par
│
├── out/                     # Resultados gerados
│   ├── grafo_interativo.html               # Visualização interativa
│   ├── recife_global.json                  # Métricas globais
│   ├── recife_local.json                   # Métricas locais
│   ├── microrregioes.json                  # Métricas por microrregião
│   ├── ego_bairro.csv                      # 2.3KB - Ego-redes
│   ├── graus.csv                           # 1.3KB - Graus dos vértices
│   ├── distancias_enderecos.csv            # 2.5KB - Caminhos calculados
│   └── percurso_nova_descoberta_setubal.json    # Caminho específico
│
├── src/
│   ├── edges/               # Pipeline de construção de arestas
│   │   ├── adjacencias.py                  # Detecção de adjacências Queen
│   │   ├── vias_conectam.py                # Identificação de vias comuns
│   │   └── distancias.py                   # Cálculo de distâncias geométricas
│   │
│   └── graphs/              # Core do sistema de grafos
│       ├── graph.py                        # Classe principal Grafo
│       ├── algorithms.py                   # Algoritmo de Dijkstra
│       ├── metricas.py                     # Cálculo de métricas
│       ├── io.py                           # Normalização de dados
│       ├── calcular_distancias_enderecos.py    # Caminhos entre pares
│       ├── visualizar_grafo_completo.py    # Gerador de visualização
│       └── visualizar_percurso.py          # Visualizador de percurso
│
└── tests/                   # Suite de testes
    ├── test_grafo_unit.py                  # Testes unitários
    ├── test_grafo_integration.py           # Testes de integração
    └── test_dijkstra.py                    # Testes do algoritmo
```

---

## 📊 DADOS: ORIGEM, ESTRUTURA E PROCESSAMENTO

### 1. **DADOS DE ENTRADA (data/)**

#### **bairros_recife.xlsx** (Fonte Original)
- **Formato:** Excel com 6 colunas (microrregiões 1.1 a 6.3)
- **Conteúdo:** Lista não normalizada de bairros por microrregião
- **Problema:** Nomes inconsistentes, abreviações, bairros duplicados

#### **bairros_unique.csv** (Processado por io.py)
- **Formato:** CSV com separador `;` e encoding UTF-8-BOM
- **Estrutura:**
  ```
  bairro;microrregião
  Aflitos;3.1
  Beberibe;2.2 / 2.3  ← Bairro em múltiplas microrregiões
  ```
- **Total:** 94 bairros únicos
- **Normalização aplicada:**
  - `Sto. → Santo`, `Sta. → Santa`, `Vl. → Vila`
  - Remoção de parênteses e pontuações
  - Capitalização consistente (exceto preposições: de, da, do, e, a)
  - Exemplo: `"STO. AMARO (CENTRO)"` → `"Santo Amaro"`

#### **bairros.geojson** (2.1MB)
- **Tipo:** GeoJSON com geometrias POLYGON e MULTIPOLYGON
- **Sistema de coordenadas:** Lat/Long (graus decimais)
- **Propriedade-chave:** `EBAIRRNOMEOF` (nome do bairro)
- **Uso:** Detecção de adjacências por contiguidade geométrica

#### **adjacencias_bairros.csv** (ARQUIVO CENTRAL - 945 linhas)
- **Estrutura:**
  ```csv
  bairro_origem,bairro_destino,logradouro,peso
  Alto José do Pinho,Mangabeira,Rua Aripibu,29.85
  ```
- **Característica crítica:** CADA LINHA = UMA ARESTA DO GRAFO
- **Total de arestas:** 944 (excluindo header)
- **Pesos:** Distâncias reais em metros (range: 29.85m a ~3000m)
- **Arestas paralelas:** Sim! Vários pares de bairros conectados por múltiplas vias
  ```
  Exemplo:
  Afogados,Mustardinha,Rua Orlandia,39.93
  Afogados,Mustardinha,Rua Maria Jose De Lima,47.02
  Afogados,Mustardinha,Rua Raimundo Jaco,86.96
  ↑ 3 vias diferentes conectando o mesmo par de bairros!
  ```

#### **vias_conectam_bairros_SELECIONADOS.csv**
- **Propósito:** Mapeamento detalhado de QUAIS vias conectam QUAIS bairros
- **Gerado por:** `vias_conectam.py`
- **Método:** Join entre facequadra.csv (23MB de dados de quadras) e adjacências
- **Exemplo:**
  ```
  Aflitos,Espinheiro,AV CONSELHEIRO ROSA E SILVA
  Aflitos,Espinheiro,RUA CONS PORTELA
  Aflitos,Espinheiro,RUA QUARENTA E OITO
  ```

#### **distancias_vias.csv** (47KB)
- **Gerado por:** `distancias.py` (processamento pesado!)
- **Método:** Análise geométrica linha por linha usando os 17MB do GeoJSON de trechos
- **Algoritmo:**
  1. Para cada via, extrai coordenadas LineString/MultiLineString
  2. Verifica se pontos da linha estão dentro dos polígonos dos bairros origem/destino
  3. Calcula comprimento euclidiano: `√((x₂-x₁)² + (y₂-y₁)²)`
  4. Usa propriedade `SdeLength_` quando disponível
  5. Agrega distâncias de trechos que conectam o par

---

## 🧩 ESTRUTURAS DE DADOS

### **Classe Grafo** (src/graphs/graph.py:3-46)

```python
class Grafo:
    def __init__(self):
        self.vertices = set()      # Set[str] - Nomes dos bairros
        self.arestas = []          # List[Dict] - Lista de dicionários
```

#### **Estrutura de vértice:**
- Tipo: String (nome do bairro)
- Armazenamento: Python `set` (O(1) para busca)
- Exemplo: `{"Aflitos", "Boa Viagem", "Casa Amarela", ...}`

#### **Estrutura de aresta:**
```python
{
    'origem': str,        # "Aflitos"
    'destino': str,       # "Espinheiro"
    'logradouro': str,    # "Rua Conselheiro Portela"
    'peso': float         # 39.05
}
```

#### **Por que lista de dicionários e não matriz de adjacências?**
1. **Grafo esparso:** 944 arestas para 94² = 8,836 possíveis pares
   - Densidade = 0.214 (apenas 21.4% das conexões possíveis existem)
   - Lista usa ~37KB vs matriz usaria ~70KB + complexidade
2. **Arestas paralelas:** Matriz não suporta múltiplas arestas por par
3. **Metadados ricos:** Cada aresta carrega logradouro e peso

### **Métodos principais:**

#### `adicionar_aresta(origem, destino, logradouro, peso)` (graph.py:9-17)
- **Automaticamente adiciona vértices** ao grafo se não existirem
- **Não verifica duplicatas** (permite arestas paralelas intencionalmente)
- **Complexidade:** O(1) - append em lista + add em set

#### `obter_vizinhos(vertice)` (graph.py:19-34)
- **Itera todas as arestas** procurando matches
- **Retorna:** Lista de dicionários `[{'destino': str, 'logradouro': str, 'peso': float}, ...]`
- **Trata não-direcionalidade:** Busca tanto `origem == vertice` quanto `destino == vertice`
- **Complexidade:** O(E) onde E = número de arestas
- **Problema de performance:** Para grafos maiores, deveria usar dicionário de adjacências

#### `obter_aresta(origem, destino)` (graph.py:35-40)
- **Retorna primeira aresta** encontrada entre os vértices (ignora paralelas!)
- **Complexidade:** O(E) no pior caso

---

## 🧮 ALGORITMOS IMPLEMENTADOS

### **1. DIJKSTRA** (src/graphs/algorithms.py:1-61)

#### **Implementação Escolhida: Versão Clássica sem Heap**

```python
def dijkstra(grafo, origem, destino):
    # Inicialização
    distancias = {v: float('inf') for v in grafo.vertices}
    distancias[origem] = 0
    anteriores = {v: None for v in grafo.vertices}
    visitados = set()
```

#### **Estruturas de dados internas:**
- `distancias`: Dict[str, float] - Melhor distância conhecida até cada vértice
- `anteriores`: Dict[str, str] - Vértice anterior no caminho ótimo
- `visitados`: Set[str] - Vértices já processados

#### **Loop principal** (algorithms.py:10-37):
```python
while len(visitados) < len(grafo.vertices):
    # 1. SELEÇÃO DO PRÓXIMO VÉRTICE (O(V))
    atual = None
    menor_distancia = float('inf')
    for v in grafo.vertices:
        if v not in visitados and distancias[v] < menor_distancia:
            menor_distancia = distancias[v]
            atual = v

    # 2. EARLY STOPPING
    if atual is None or distancias[atual] == float('inf'):
        break

    visitados.add(atual)

    # 3. OTIMIZAÇÃO: Para quando atinge destino
    if atual == destino:
        break

    # 4. RELAXAMENTO (O(grau(v)))
    vizinhos = grafo.obter_vizinhos(atual)
    for vizinho in vizinhos:
        v = vizinho['destino']
        peso = vizinho['peso']

        if v not in visitados:
            nova_distancia = distancias[atual] + peso
            if nova_distancia < distancias[v]:
                distancias[v] = nova_distancia
                anteriores[v] = atual
```

#### **Análise de Complexidade:**
- **Sem heap:** O(V²) para seleção + O(E) para relaxamentos = **O(V² + E)**
- **Com 94 vértices:** 94² = 8,836 operações + 944 relaxamentos ≈ 9,780 ops
- **Por que não usaram heap?**
  - Para grafos pequenos (V < 1000), overhead do heap > benefício
  - Implementação mais simples para fins educacionais
  - Heap reduziria para O((V + E) log V) ≈ 6,200 ops (~30% mais rápido)

#### **Reconstrução do caminho** (algorithms.py:42-47):
```python
caminho = []
atual = destino
while atual is not None:
    caminho.append(atual)
    atual = anteriores[atual]
caminho.reverse()  # [origem, ..., destino]
```

#### **Mapeamento de vias usadas** (algorithms.py:49-58):
```python
vias = []
for i in range(len(caminho) - 1):
    bairro_atual = caminho[i]
    proximo_bairro = caminho[i + 1]

    vizinhos = grafo.obter_vizinhos(bairro_atual)
    for viz in vizinhos:
        if viz['destino'] == proximo_bairro:
            vias.append(viz['logradouro'])
            break  # Pega primeira via (problema com paralelas!)
```

**⚠️ LIMITAÇÃO IDENTIFICADA:** Se existem múltiplas vias entre dois bairros, sempre retorna a primeira encontrada na lista, não necessariamente a do caminho ótimo!

#### **Retorno:**
```python
return (
    caminho,              # ['Aflitos', 'Graças', 'Espinheiro']
    distancias[destino],  # 569.53
    vias                  # ['Rua Teles Junior', 'Rua Conselheiro Portela']
)
```

#### **Casos de erro:**
- Vértice inexistente: `return None, float('inf'), []`
- Destino inalcançável: `return None, float('inf'), []`

---

### **2. ALGORITMO DE ADJACÊNCIA QUEEN** (src/edges/adjacencias.py)

#### **Propósito:** Detectar quais bairros são vizinhos geograficamente

#### **Método Queen (Xadrez):**
- Dois polígonos são adjacentes se **compartilham qualquer ponto** (vértice ou aresta)
- Mais permissivo que Rook (apenas arestas) ou Bishop (apenas vértices)

#### **Implementação:**

```python
def extrair_pontos(geometria):
    """Extrai TODOS os vértices de um polígono"""
    pontos = set()
    if geometria['type'] == 'Polygon':
        for coord in geometria['coordinates'][0]:
            pontos.add((round(coord[0], 6), round(coord[1], 6)))
            # ↑ Arredonda para 6 casas decimais (~11cm de precisão)
    elif geometria['type'] == 'MultiPolygon':
        for poligono in geometria['coordinates']:
            for coord in poligono[0]:
                pontos.add((round(coord[0], 6), round(coord[1], 6)))
    return pontos
```

#### **Detecção de adjacência:**
```python
for i, bairro_origem in enumerate(lista_bairros):
    pontos_origem = bairros_pontos[bairro_origem]

    for bairro_destino in lista_bairros[i+1:]:  # Evita duplicatas
        pontos_destino = bairros_pontos[bairro_destino]

        if pontos_origem & pontos_destino:  # Interseção de sets
            adjacencias.append({
                'bairro origem': bairro_origem,
                'bairro match': bairro_destino
            })
```

#### **Complexidade:** O(N²) onde N = 94 bairros = 4,371 comparações
#### **Otimização usada:** Set intersection (O(min(|A|, |B|))) é muito rápido

---

### **3. CÁLCULO DE DISTÂNCIAS GEOMÉTRICAS** (src/edges/distancias.py)

#### **Algoritmo Point-in-Polygon** (Ray Casting)

```python
def ponto_dentro_poligono(x, y, poligono):
    """Ray casting algorithm - Traça raio horizontal e conta interseções"""
    n = len(poligono)
    dentro = False
    j = n - 1

    for i in range(n):
        xi, yi = poligono[i][0], poligono[i][1]
        xj, yj = poligono[j][0], poligono[j][1]

        # Verifica se raio horizontal cruza a aresta (j, i)
        if ((yi > y) != (yj > y)) and \
           (x < (xj - xi) * (y - yi) / (yj - yi + 0.0001) + xi):
            dentro = not dentro
        j = i

    return dentro
```

**Princípio:** Se o raio cruza número ímpar de arestas, ponto está dentro

#### **Classificação de Trechos:**

```python
def classificar_trecho(coords, geom_origem, geom_destino):
    """Decide se um trecho de via conecta dois bairros"""
    pontos_origem = 0
    pontos_destino = 0

    # Conta quantos pontos estão em cada bairro
    for ponto in coords:
        if ponto_dentro_bairro(ponto, geom_origem):
            pontos_origem += 1
        elif ponto_dentro_bairro(ponto, geom_destino):
            pontos_destino += 1

    # CRITÉRIO 1: Tem pontos em AMBOS os bairros
    if pontos_origem > 0 and pontos_destino > 0:
        return True

    # CRITÉRIO 2: Pelo menos 5% em cada (tolerância para erros)
    proporcao_origem = pontos_origem / len(coords)
    proporcao_destino = pontos_destino / len(coords)
    if proporcao_origem > 0.05 and proporcao_destino > 0.05:
        return True

    # CRITÉRIO 3: 30%+ dos pontos estão em um dos bairros
    if (pontos_origem + pontos_destino) / len(coords) > 0.3:
        return True

    return False
```

**Complexidade total:** O(N × M × P) onde:
- N = pares de bairros (~1000)
- M = trechos de vias no GeoJSON (~100,000)
- P = pontos por trecho (~20)
- **Total:** ~2 bilhões de operações! (Por isso é lento)

---

## 📈 MÉTRICAS CALCULADAS

### **1. MÉTRICAS GLOBAIS** (metricas.py:5-23)

#### **Ordem:**
```python
ordem = grafo.total_vertices()  # 94 bairros
```

#### **Tamanho:**
```python
# REMOVE duplicatas! Conta PARES ÚNICOS
pares_unicos = set()
for aresta in grafo.arestas:
    par = tuple(sorted([aresta['origem'], aresta['destino']]))
    pares_unicos.add(par)
tamanho = len(pares_unicos)  # Diferente de 944!
```

**Por que isso?** Grafo não-direcionado: aresta (A,B) = aresta (B,A)

#### **Densidade:**
```python
densidade = (2 * tamanho) / (ordem * (ordem - 1))
```

**Fórmula:** D = 2|E| / (|V|(|V|-1)) para grafos não-direcionados
**Interpretação:** Proporção de arestas existentes vs. todas possíveis

---

### **2. MÉTRICAS POR MICRORREGIÃO** (metricas.py:25-68)

Recife é dividido em **microrregiões** (1.1 a 6.3):
- 1.x = Centro
- 2.x = Norte
- 3.x = Noroeste
- 4.x = Oeste
- 5.x = Sudoeste
- 6.x = Sul

**Alguns bairros pertencem a múltiplas microrregiões!** (ex: `Beberibe;2.2 / 2.3`)

```python
# Parse de microrregiões compostas
if '/' in micro:
    micros = [m.strip() for m in micro.split('/')]
else:
    micros = [micro.strip()]

for m in micros:
    microrregioes[m].append(bairro)
```

Para cada microrregião, calcula:
- Ordem (bairros na microrregião)
- Tamanho (arestas internas)
- Densidade (quão conectada é internamente)

---

### **3. EGO-REDES** (metricas.py:70-106)

#### **Definição de Ego-rede:**
- **Ego:** Bairro focal
- **Alters:** Vizinhos diretos
- **Ego-rede:** Subgrafo induzido por {ego ∪ alters}

```python
def calcular_ego_bairros(grafo):
    for bairro in grafo.vertices:
        # 1. Identifica vizinhos únicos
        vizinhos = grafo.obter_vizinhos(bairro)
        vizinhos_unicos = set(v['destino'] for v in vizinhos)
        grau = len(vizinhos_unicos)

        # 2. Constrói ego-rede
        ego_vertices = {bairro}
        ego_vertices.update(vizinhos_unicos)

        # 3. Conta arestas dentro da ego-rede
        pares_unicos = set()
        for aresta in grafo.arestas:
            if aresta['origem'] in ego_vertices and \
               aresta['destino'] in ego_vertices:
                par = tuple(sorted([aresta['origem'], aresta['destino']]))
                pares_unicos.add(par)

        # 4. Calcula densidade da ego-rede
        ordem_ego = len(ego_vertices)
        tamanho_ego = len(pares_unicos)
        densidade_ego = (2 * tamanho_ego) / (ordem_ego * (ordem_ego - 1))
```

#### **Exemplo real (ego_bairro.csv:2):**
```
Aflitos,3,4,6,1.0
```
- **Grau:** 3 vizinhos
- **Ordem ego:** 4 vértices (Aflitos + 3 vizinhos)
- **Tamanho ego:** 6 arestas
- **Densidade ego:** 1.0 = **CLIQUE COMPLETO!** (Todos os vizinhos de Aflitos também se conectam entre si)

---

## 🎨 VISUALIZAÇÃO INTERATIVA

### **Geração** (visualizar_grafo_completo.py)

#### **1. Layout dos Nós:**

```python
# Posições fixas para clusters de microrregiões
posicoes_clusters = {
    '1.1': (1000, 1000), '1.2': (2500, 1000), '1.3': (4000, 1000),
    '2.1': (500, 2500),  '2.2': (2000, 2500), '2.3': (3500, 2500),
    # ... até 6.3
}

# Distribui bairros em círculo ao redor do centro da microrregião
for micro, bairros_micro in microrregioes_agrupadas.items():
    centro_cluster = posicoes_clusters.get(micro, (3000, 3000))
    n_bairros = len(bairros_micro)
    raio_cluster = 200 + (n_bairros * 30)  # Raio dinâmico

    for i, bairro in enumerate(bairros_micro):
        angulo = (2 * math.pi * i) / n_bairros
        jitter_x = random.uniform(-50, 50)  # Ruído para estética
        jitter_y = random.uniform(-50, 50)
        x = centro_cluster[0] + raio_cluster * math.cos(angulo) + jitter_x
        y = centro_cluster[1] + raio_cluster * math.sin(angulo) + jitter_y
```

**Por que não force-directed?** Posições fixas garantem consistência entre execuções

#### **2. Cores:**

```python
cores_microrregioes = {
    '1.1': '#e74c3c',  # Vermelho
    '1.2': '#e67e22',  # Laranja
    # ... 19 cores distintas
}

# Bairros multi-microrregião = cores divididas em fatias de pizza
for i in range(len(node.cores)):
    startAngle = (i * 2 * Math.PI) / node.cores.length
    endAngle = ((i + 1) * 2 * Math.PI) / node.cores.length
    ctx.fillStyle = node.cores[i]
    ctx.arc(node.x, node.y, raio, startAngle, endAngle)
```

#### **3. Arestas Paralelas:**

```python
# Conta quantas arestas existem entre cada par
pares_contador = {}
for aresta in grafo.arestas:
    par = tuple(sorted([origem, destino]))
    pares_contador[par] += 1

# Renderiza cada aresta com curvatura diferente
for aresta in edges:
    if edge.curva_total === 1:
        # Linha reta
        ctx.lineTo(toNode.x, toNode.y)
    else:
        # Curva de Bezier quadrática
        offsetMax = Math.min(distancia * 0.3, 150)
        step = offsetMax / (edge.curva_total - 1)
        offset = (edge.curva_indice - (edge.curva_total - 1) / 2) * step

        perpX = -dy / distancia  // Vetor perpendicular
        perpY = dx / distancia

        midX = (fromNode.x + toNode.x) / 2 + perpX * offset
        midY = (fromNode.y + toNode.y) / 2 + perpY * offset

        ctx.quadraticCurveTo(midX, midY, toNode.x, toNode.y)
```

**Resultado:** Múltiplas vias aparecem como curvas paralelas!

#### **4. Interatividade JavaScript:**

##### **Zoom e Pan:**
```javascript
canvas.addEventListener('wheel', (e) => {
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const newScale = Math.max(0.1, Math.min(5, scale * delta))

    // Zoom centrado no cursor
    const worldX = (mouseX - offsetX) / scale
    const worldY = (mouseY - offsetY) / scale
    scale = newScale
    offsetX = mouseX - worldX * scale
    offsetY = mouseY - worldY * scale
})
```

##### **Dijkstra em JavaScript (frontend):**

Implementação DUPLICADA do algoritmo em JS para cálculo em tempo real!

```javascript
function calcularCaminhoLocal(origem, destino) {
    // Constrói grafo de adjacências
    const grafo = {}
    nodes.forEach(n => grafo[n.label] = [])
    edges.forEach(e => {
        grafo[from].push({destino: to, via: e.label, peso: e.peso})
        grafo[to].push({destino: from, via: e.label, peso: e.peso})
    })

    // Dijkstra idêntico ao Python
    const distancias = {}
    const anteriores = {}
    // ... mesmo algoritmo ...

    return {caminho, vias, custo}
}
```

**Por que duplicar?** Para não precisar de backend/API, tudo roda no browser

##### **Detecção Click vs Drag:**

```javascript
let mouseDownX = 0, mouseDownY = 0, hasMoved = false

canvas.addEventListener('mousedown', (e) => {
    mouseDownX = e.clientX - rect.left
    mouseDownY = e.clientY - rect.top
    hasMoved = false
})

canvas.addEventListener('mousemove', (e) => {
    const distMoved = Math.sqrt(
        Math.pow(currentX - mouseDownX, 2) +
        Math.pow(currentY - mouseDownY, 2)
    )

    if (distMoved > 5) {  // Threshold de 5px
        hasMoved = true
        // Inicia drag
    }
})

canvas.addEventListener('mouseup', (e) => {
    if (!hasMoved) {
        // Foi um clique! Seleciona bairro
    }
})
```

---

## 🧪 TESTES

### **1. Testes Unitários** (test_grafo_unit.py)

#### **test_adicionar_vertice_e_arestas:**
- Verifica construção básica do grafo
- Valida estrutura da aresta
- Confirma adição automática de vértices

#### **test_obter_vizinhos_retorna_ambas_direcoes:**
```python
grafo.adicionar_aresta("Aflitos", "Espinheiro", "Rua 1", 100)
vizinhos_espinheiro = grafo.obter_vizinhos("Espinheiro")
assert "Aflitos" in destinos_espinheiro  # Confirma não-direcionalidade
```

#### **test_obter_aresta_simples:**
```python
aresta2 = grafo.obter_aresta("Espinheiro", "Aflitos")
assert aresta2["origem"] == "Aflitos"  # Retorna sempre mesma aresta
```

---

### **2. Testes de Dijkstra** (test_dijkstra.py)

#### **Grafo de teste:**
```
Aflitos --100--> Espinheiro --50--> Boa Vista
     \                         ^
      \--300-------------------/
```

```python
def test_dijkstra_encontra_caminho_minimo():
    caminho, distancia, vias = dijkstra(grafo, "Aflitos", "Boa Vista")

    # Deve escolher Aflitos -> Espinheiro -> Boa Vista (150)
    # NÃO Aflitos -> Boa Vista (300)
    assert caminho == ["Aflitos", "Espinheiro", "Boa Vista"]
    assert math.isclose(distancia, 150.0)
    assert vias == ["Rua 1", "Rua 2"]
```

#### **test_dijkstra_origem_igual_destino:**
```python
caminho, distancia, vias = dijkstra(grafo, "Aflitos", "Aflitos")
assert caminho == ["Aflitos"]
assert distancia == 0.0
assert vias == []
```

---

### **3. Teste de Integração** (test_grafo_integration.py)

```python
def test_construir_grafo_bairros_carrega_todos_os_dados():
    grafo = construir_grafo_bairros()

    assert grafo.total_vertices() == 94
    assert grafo.total_arestas() == 944
    assert "Aflitos" in grafo.vertices
    assert any(a["origem"] != a["destino"] for a in grafo.arestas)
```

**Valida:** Parsing completo do CSV real de 945 linhas

---

## 🔬 FLUXO DE PROCESSAMENTO COMPLETO

### **Pipeline de Dados:**

```
1. NORMALIZAÇÃO
   bairros_recife.xlsx → [io.py] → bairros_unique.csv
   ↓
   - Remove abreviações
   - Capitaliza corretamente
   - Agrupa microrregiões

2. DETECÇÃO DE ADJACÊNCIAS
   bairros.geojson + bairros_unique.csv → [adjacencias.py] → adjacencias_provisorio.csv
   ↓
   - Extrai vértices de polígonos
   - Aplica adjacência Queen
   - 94 bairros → ~200 pares adjacentes

3. MAPEAMENTO DE VIAS
   adjacencias_provisorio.csv + facequadra.csv → [vias_conectam.py] → vias_conectam_bairros_SELECIONADOS.csv
   ↓
   - Join por codlogradouro
   - Identifica vias compartilhadas
   - ~1000 registros (múltiplas vias por par)

4. CÁLCULO DE DISTÂNCIAS
   vias_conectam_bairros_SELECIONADOS.csv + bvisualizacao_fctrechologradouro.geojson → [distancias.py] → distancias_vias.csv
   ↓
   - Point-in-polygon para cada trecho
   - Soma comprimentos
   - ~47KB de distâncias

5. CONSOLIDAÇÃO FINAL
   distancias_vias.csv → adjacencias_bairros.csv
   ↓
   - 944 arestas com pesos reais
   - Formato: origem, destino, via, peso
```

### **Pipeline de Análise:**

```
1. CONSTRUÇÃO DO GRAFO
   adjacencias_bairros.csv → [graph.py::construir_grafo_bairros()] → Grafo
   ↓
   - 94 vértices
   - 944 arestas

2. CÁLCULO DE MÉTRICAS
   Grafo → [metricas.py] → recife_global.json, microrregioes.json, ego_bairro.csv
   ↓
   - Densidade global
   - Métricas por microrregião
   - Ego-redes de 94 bairros

3. CAMINHOS ENTRE ENDEREÇOS
   Grafo → [calcular_distancias_enderecos.py] → distancias_enderecos.csv, percurso_nova_descoberta_setubal.json
   ↓
   - 6 pares pré-definidos
   - Dijkstra para cada
   - Caminho detalhado com vias

4. VISUALIZAÇÃO
   Grafo + ego_bairro.csv + percurso_*.json → [visualizar_grafo_completo.py] → grafo_interativo.html
   ↓
   - Layout por microrregião
   - 944 arestas curvas
   - Dijkstra em JavaScript
   - Interatividade completa
```

---

## 📊 RESULTADOS E INSIGHTS

### **Caminho Nova Descoberta → Boa Viagem (Setúbal)**

```
Distância: 2682.05m (≈2.7km)
Caminho: 12 bairros, 11 vias

Nova Descoberta
  --[Rua Urandi (62.85m)]-->
Brejo de Beberibe
  --[Rua Uriel De Holanda]-->
Alto José Bonifácio
  --[Rua Arlindo Cisneiros (72m)]-->
Alto Santa Teresinha
  --[Rua Alto do Tiro (41m)]-->
Bomba do Hemetério
  --[Rua Professor Manuel Torres]-->
Arruda
  --[Rua Petronila Botelho]-->
Campo Grande
  --[Rua Projetada (47.09m)]-->
Santo Amaro
  --[Rua Princesa Isabel]-->
Santo Antônio
  --[Rua Do Porao]-->
São José
  --[Avenida Antônio de Goes]-->
Pina
  --[Rua Delegado Tercio Soares De Aquino]-->
Boa Viagem
```

**Análise:** Atravessa 6 microrregiões diferentes (3.3 → 3.2 → 2.2 → 2.1 → 1.2 → 6.1)

### **Caminho Aflitos → Pina**

```
Distância: 1991.66m (≈2km)
Caminho: 7 bairros, 6 vias

Aflitos → Graças → Derby → Boa Vista → Santo Antônio → São José → Pina
```

**Insight:** Apenas 7 hops para percorrer ~2km, mostra boa conectividade da região central

### **Bairros com maior grau:**

```
Afogados: grau=10 (mais conectado)
Boa Vista: grau=9
Arruda: grau=9
```

### **Bairros com densidade ego = 1.0 (cliques):**

```
Aflitos: Todos os vizinhos se conectam entre si
```

**Interpretação:** Região altamente integrada, sem "ponte" única

---

## 🛠️ DEPENDÊNCIAS

```
pandas>=2.0.0    # Manipulação de DataFrames
openpyxl>=3.0.0  # Leitura de Excel
```

**Notável:**
- Sem NumPy! (usam math puro)
- Sem NetworkX! (implementação própria)
- Sem Matplotlib! (visualização em HTML/Canvas)

---

## ✅ CONCLUSÕES

### **Pontos Fortes:**

1. **Dados reais de alta qualidade:** GeoJSON oficial de Recife
2. **Pipeline completo:** De polígonos até visualização interativa
3. **Arestas paralelas:** Refletem realidade urbana (múltiplas vias)
4. **Implementação educacional:** Código limpo, bem documentado
5. **Visualização excepcional:** HTML self-contained, sem deps
6. **Testes abrangentes:** Unit + integration + algorithm

### **Limitações Técnicas:**

1. **Performance:** O(V²) Dijkstra poderia usar heap
2. **Obter vizinhos:** O(E) por chamada, deveria cachear
3. **Seleção de via:** Pega primeira via paralela arbitrariamente
4. **Escalabilidade:** Não suportaria 1000+ bairros sem refatoração

### **Decisões de Design Justificadas:**

1. **Lista vs Matriz:** Correto para grafo esparso com arestas paralelas
2. **Sem heap no Dijkstra:** Apropriado para V=94
3. **JavaScript duplicado:** Permite execução offline
4. **Layout fixo:** Consistência > organicidade

---

## 📝 RESUMO EXECUTIVO FINAL

Este é um **projeto acadêmico de teoria de grafos** aplicado a dados urbanos reais de Recife/PE. Mapeia 94 bairros como vértices e 944 vias como arestas ponderadas, implementando Dijkstra para cálculo de caminhos mínimos e gerando visualização interativa em HTML5 Canvas.

**Tamanho do projeto:** ~1000 linhas de Python + ~500 linhas de JavaScript
**Complexidade:** Média-alta (processamento geométrico pesado)
**Qualidade do código:** Alta (testes, documentação, estrutura limpa)
**Aplicabilidade:** Planejamento urbano, logística, educação em grafos

---

**Data da análise:** 2025-11-18
**Analista:** Claude (Anthropic)
