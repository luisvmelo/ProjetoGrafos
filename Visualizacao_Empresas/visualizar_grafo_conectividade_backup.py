import json
import math
import random
import pandas as pd
import os
import ast
import unicodedata

# Mudar para o diretório raiz do projeto
os.chdir('/home/luisevmelo/ProjetoGrafos-1')

# Importar classes necessárias
import sys
sys.path.append('src/graphs')
from graph import Grafo

# Função de normalização (mesma do processar_empresas.py)
def normalizar_nome(texto):
    if pd.isna(texto):
        return ''
    texto = str(texto).strip()

    # Mapeamentos especiais ANTES da normalização
    mapeamentos_especiais = {
        'Sitio dos Pintos   Sao Bras': 'Sítio dos Pintos',
        'Cohab   Ibura de Cima': 'Cohab',
        'Alto do Mandu   Sitio Grande': 'Alto do Mandu'
    }

    if texto in mapeamentos_especiais:
        texto = mapeamentos_especiais[texto]

    # Remove acentos
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remove espaços extras, mas MANTÉM hífens
    normalizado = ' '.join(sem_acento.split())
    # Normalizar variações comuns
    normalizado = normalizado.replace('Terezinha', 'Teresinha')
    normalizado = normalizado.replace('TEREZINHA', 'TERESINHA')
    # Title Case
    return normalizado.title()

# Construir grafo LIGHT (apenas um par de arestas por bairros)
def construir_grafo_light():
    df = pd.read_csv('data/adjacencias_bairros.csv')
    grafo = Grafo()

    # Usar set para rastrear pares únicos
    pares_unicos = set()

    for _, row in df.iterrows():
        origem = row['bairro_origem']
        destino = row['bairro_destino']
        par = tuple(sorted([origem, destino]))

        # Adicionar apenas uma aresta por par
        if par not in pares_unicos:
            pares_unicos.add(par)
            grafo.adicionar_aresta(
                origem,
                destino,
                row['logradouro'],
                row['peso']
            )

    return grafo

grafo = construir_grafo_light()

# Criar mapa de bairro original -> normalizado
bairro_original_para_normalizado = {b: normalizar_nome(b) for b in grafo.vertices}

# Carregar dados de conectividade (com métricas e clusters)
df_conectividade = pd.read_csv('Visualizacao_Empresas/empresas_conectividade.csv', encoding='utf-8-sig')

# Converter string de top_3_atividades para lista
df_conectividade['top_3_atividades'] = df_conectividade['top_3_atividades'].apply(ast.literal_eval)

# Criar dicionário de dados por bairro NORMALIZADO
dados_bairro = {}
for _, row in df_conectividade.iterrows():
    bairro_norm = row['bairro_normalizado']
    dados_bairro[bairro_norm] = {
        'total_empresas': row['total_empresas'],
        'top_3_atividades': row['top_3_atividades'],
        'microrregiao': row['microrregiao'],
        'grau': row['grau'],
        'centralidade_grau': row['centralidade_grau'],
        'centralidade_closeness': row['centralidade_closeness'],
        'centralidade_betweenness': row['centralidade_betweenness'],
        'cluster_conectividade': row['cluster_conectividade'],
        'top_20_percent': row['top_20_percent']
    }

# Carregar dados de microrregiões
df_micro = pd.read_csv('Visualizacao_Empresas/empresas_microrregioes.csv', encoding='utf-8-sig')
df_micro['top_3_atividades'] = df_micro['top_3_atividades'].apply(ast.literal_eval)

dados_micro = {}
for _, row in df_micro.iterrows():
    micro = str(row['microrregiao'])
    dados_micro[micro] = {
        'total_empresas': row['total_empresas'],
        'top_3_atividades': row['top_3_atividades']
    }

# Carregar dados de microrregião dos bairros
with open('data/bairros_unique.csv', 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()[1:]
    microrregiao_dict = {}
    for linha in linhas:
        partes = linha.strip().split(';')
        bairro = partes[0]
        micro = partes[1]
        microrregiao_dict[bairro] = micro

random.seed(42)

# Agrupar por microrregiões para posicionamento (MESMAS POSIÇÕES DO GRAFO ORIGINAL)
microrregioes_agrupadas = {}
for bairro in grafo.vertices:
    micro = microrregiao_dict.get(bairro, 'N/A')
    for m in micro.split(' / '):
        if m not in microrregioes_agrupadas:
            microrregioes_agrupadas[m] = []
        microrregioes_agrupadas[m].append(bairro)

for micro in microrregioes_agrupadas:
    microrregioes_agrupadas[micro] = list(set(microrregioes_agrupadas[micro]))

# Posições dos clusters (mesmas do grafo original - MANTER LAYOUTS)
posicoes_clusters = {
    '1.1': (1000, 1000), '1.2': (2500, 1000), '1.3': (4000, 1000),
    '2.1': (500, 2500), '2.2': (2000, 2500), '2.3': (3500, 2500),
    '2.2 / 2.3': (2750, 2500),
    '3.1': (5000, 2500), '3.2': (1000, 4000), '3.3': (2500, 4000),
    '4.1': (4000, 4000), '4.2': (5500, 4000), '4.3': (500, 5500),
    '5.1': (2000, 5500), '5.2': (3500, 5500), '5.3': (5000, 5500),
    '6.1': (1500, 7000), '6.2': (3500, 7000), '6.3': (5000, 7000),
    'N/A': (3000, 1000)
}

# Calcular posições dos bairros (MESMA LÓGICA - MANTER LAYOUTS)
posicoes = {}
for micro, bairros_micro in microrregioes_agrupadas.items():
    centro_cluster = posicoes_clusters.get(micro, (3000, 3000))
    n_bairros = len(bairros_micro)

    if n_bairros == 1:
        posicoes[bairros_micro[0]] = {'x': centro_cluster[0], 'y': centro_cluster[1]}
    else:
        raio_cluster = 200 + (n_bairros * 30)
        for i, bairro in enumerate(bairros_micro):
            angulo = (2 * math.pi * i) / n_bairros
            jitter_x = random.uniform(-50, 50)
            jitter_y = random.uniform(-50, 50)
            x = centro_cluster[0] + raio_cluster * math.cos(angulo) + jitter_x
            y = centro_cluster[1] + raio_cluster * math.sin(angulo) + jitter_y
            posicoes[bairro] = {'x': x, 'y': y}

# Criar lista de bairros e mapeamento de IDs
bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

# Cores por cluster de conectividade - SIMPLIFICADO
# Usar apenas algumas cores distintas para os principais clusters
cores_cluster_base = [
    '#3498db',  # Azul
    '#e74c3c',  # Vermelho
    '#2ecc71',  # Verde
    '#f39c12',  # Laranja
    '#9b59b6',  # Roxo
    '#1abc9c',  # Turquesa
    '#e67e22',  # Laranja escuro
    '#16a085',  # Verde escuro
    '#c0392b',  # Vermelho escuro
    '#8e44ad',  # Roxo escuro
]

clusters_unicos = sorted(set(dados_bairro[normalizar_nome(b)]['cluster_conectividade']
                              for b in bairros_lista if normalizar_nome(b) in dados_bairro))

cores_cluster = {}
for i, cluster_id in enumerate(clusters_unicos):
    if cluster_id == -1:
        cores_cluster[cluster_id] = '#95a5a6'  # Cinza para bairros sem cluster
    else:
        cores_cluster[cluster_id] = cores_cluster_base[i % len(cores_cluster_base)]

# Criar nós com informações de conectividade
nodes = []
for i, bairro in enumerate(bairros_lista):
    # Normalizar o nome do bairro para buscar nos dados
    bairro_norm = normalizar_nome(bairro)

    micro = microrregiao_dict.get(bairro, 'N/A')
    # Buscar dados usando nome normalizado
    dados = dados_bairro.get(bairro_norm, {
        'total_empresas': 0,
        'top_3_atividades': [],
        'microrregiao': micro,
        'grau': 0,
        'centralidade_grau': 0,
        'centralidade_closeness': 0,
        'centralidade_betweenness': 0,
        'cluster_conectividade': -1,
        'top_20_percent': False
    })

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': micro,
        'total_empresas': int(dados['total_empresas']),
        'top_3_atividades': dados['top_3_atividades'],
        'grau': int(dados['grau']),
        'centralidade_grau': float(dados['centralidade_grau']),
        'centralidade_closeness': float(dados['centralidade_closeness']),
        'centralidade_betweenness': float(dados['centralidade_betweenness']),
        'cluster_conectividade': int(dados['cluster_conectividade']),
        'top_20_percent': bool(dados['top_20_percent']),
        'cor_cluster': cores_cluster.get(int(dados['cluster_conectividade']), '#cccccc')
    })

# Criar arestas (grafo light já foi criado)
edges = []
pares_vistos = set()

for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    par = tuple(sorted([origem, destino]))

    if par not in pares_vistos:
        pares_vistos.add(par)
        edges.append({
            'from': bairro_to_id[origem],
            'to': bairro_to_id[destino]
        })

print(f"Grafo de Conectividade Econômica criado:")
print(f"  Vértices: {len(nodes)}")
print(f"  Arestas (light): {len(edges)}")
print(f"  Clusters de conectividade: {num_clusters}")

# Estatísticas
empresas_counts = [n['total_empresas'] for n in nodes if n['total_empresas'] > 0]
if empresas_counts:
    print(f"\nEmpresas por bairro:")
    print(f"  Mín: {min(empresas_counts)}")
    print(f"  Máx: {max(empresas_counts)}")
    print(f"  Média: {sum(empresas_counts) / len(empresas_counts):.0f}")

print("\nTop 5 bairros por centralidade de grau:")
top_centralidade = sorted(nodes, key=lambda x: x['centralidade_grau'], reverse=True)[:5]
for b in top_centralidade:
    print(f"  {b['label']}: grau={b['grau']}, centralidade={b['centralidade_grau']:.3f}, empresas={b['total_empresas']}")

print("\nDistribuição de bairros por cluster:")
from collections import Counter
cluster_counts = Counter(n['cluster_conectividade'] for n in nodes)
for cluster_id, count in sorted(cluster_counts.items())[:10]:
    print(f"  Cluster {cluster_id}: {count} bairros")

# Gerar HTML da visualização
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Conectividade Econômica por Bairro – Recife</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            overflow: hidden;
        }}
        #container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        #header {{
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 10;
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 26px;
            font-weight: 600;
        }}
        h1 small {{
            font-size: 14px;
            color: #7f8c8d;
            font-weight: normal;
        }}
        #filtros {{
            margin: 10px 0;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        select, input[type="text"], input[type="checkbox"] {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }}
        select:focus, input[type="text"]:focus {{
            outline: none;
            border-color: #3498db;
        }}
        input[type="text"] {{
            min-width: 250px;
        }}
        label {{
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }}
        button {{
            padding: 8px 16px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
            font-weight: 500;
        }}
        button:hover {{
            background: #2980b9;
        }}
        button.secondary {{
            background: #95a5a6;
        }}
        button.secondary:hover {{
            background: #7f8c8d;
        }}
        #legenda {{
            display: flex;
            gap: 20px;
            margin-top: 12px;
            font-size: 13px;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid #ecf0f1;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legenda-linha {{
            width: 30px;
            height: 3px;
            background: #bdc3c7;
        }}
        .legenda-circulo {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px solid #34495e;
        }}
        .legenda-circulo-hub {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            border: 3px solid #e74c3c;
            background: rgba(231, 76, 60, 0.2);
        }}
        #canvasContainer {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: #fafafa;
        }}
        canvas {{
            display: block;
            cursor: grab;
        }}
        canvas.dragging {{
            cursor: grabbing;
        }}
        #tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.92);
            color: white;
            padding: 14px 16px;
            border-radius: 8px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 100;
            max-width: 340px;
            line-height: 1.6;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .tooltip-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
            padding-bottom: 6px;
            color: #3498db;
        }}
        .tooltip-row {{
            margin: 5px 0;
        }}
        .tooltip-label {{
            color: #bdc3c7;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .tooltip-value {{
            color: white;
            font-weight: 500;
        }}
        .tooltip-atividade {{
            margin: 3px 0;
            padding-left: 12px;
            font-size: 12px;
            color: #ecf0f1;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>Conectividade Econômica por Bairro – Recife <small>Análise de Rede e Clusters</small></h1>
            <div id="filtros">
                <label for="selectMicro"><strong>Filtrar por Microrregião:</strong></label>
                <select id="selectMicro">
                    <option value="todas">Todas as Microrregiões</option>
                </select>

                <label for="selectCluster" style="margin-left: 15px;"><strong>Filtrar por Cluster:</strong></label>
                <select id="selectCluster">
                    <option value="todos">Todos os Clusters</option>
                </select>

                <label style="margin-left: 15px;">
                    <input type="checkbox" id="checkboxHubs">
                    <strong>Destacar Hubs de Conectividade (Top 20%)</strong>
                </label>

                <label for="inputBusca" style="margin-left: 15px;"><strong>Buscar:</strong></label>
                <input type="text" id="inputBusca" placeholder="Digite o nome do bairro...">

                <button id="btnResetFiltro" class="secondary">🔄 Resetar</button>
            </div>
            <div id="legenda">
                <span style="font-weight: 600; color: #34495e;">Legenda:</span>
                <div class="legenda-item">
                    <div class="legenda-linha"></div>
                    <span>Conexões entre bairros</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-circulo"></div>
                    <span>Bairro (tamanho = nº empresas)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-circulo-hub"></div>
                    <span>Hub de conectividade</span>
                </div>
                <div class="legenda-item" style="margin-left: 10px;">
                    <span style="background: linear-gradient(90deg, {', '.join([cores_cluster[c] for c in list(cores_cluster.keys())[:5]])}); width: 100px; height: 16px; border-radius: 3px; display: inline-block;"></span>
                    <span>Cores = Clusters de conectividade</span>
                </div>
                <span style="margin-left: auto; color: #7f8c8d; font-weight: 500;">
                    Total: {sum(n['total_empresas'] for n in nodes):,} empresas | {len(edges)} conexões
                </span>
            </div>
        </div>
        <div id="canvasContainer">
            <canvas id="canvas"></canvas>
            <div id="tooltip"></div>
        </div>
    </div>
    <script>
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        const selectMicro = document.getElementById('selectMicro');
        const selectCluster = document.getElementById('selectCluster');
        const checkboxHubs = document.getElementById('checkboxHubs');
        const btnResetFiltro = document.getElementById('btnResetFiltro');
        const inputBusca = document.getElementById('inputBusca');

        // Configuração da visualização
        const canvasContainer = document.getElementById('canvasContainer');
        let viewportX = 0;
        let viewportY = 0;
        let scale = 1;
        let dragging = false;
        let dragStart = {{ x: 0, y: 0 }};

        // Estado dos filtros
        let microregioAtiva = 'todas';
        let clusterAtivo = 'todos';
        let mostrarApenasHubs = false;
        let bairroDestacado = null;

        // Redimensionar canvas
        function resizeCanvas() {{
            canvas.width = canvasContainer.clientWidth;
            canvas.height = canvasContainer.clientHeight;
            desenhar();
        }}
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // Popular select de microrregiões
        const micros = [...new Set(nodes.map(n => n.microrregiao))].sort();
        micros.forEach(micro => {{
            const option = document.createElement('option');
            option.value = micro;
            option.textContent = `Microrregião ${{micro}}`;
            selectMicro.appendChild(option);
        }});

        // Popular select de clusters
        const clusters = [...new Set(nodes.map(n => n.cluster_conectividade))].sort((a, b) => a - b);
        clusters.forEach(cluster => {{
            const option = document.createElement('option');
            option.value = cluster;
            option.textContent = cluster === -1 ? 'Sem cluster' : `Cluster ${{cluster}}`;
            selectCluster.appendChild(option);
        }});

        // Event listeners
        selectMicro.addEventListener('change', (e) => {{
            microregioAtiva = e.target.value;
            desenhar();
        }});

        selectCluster.addEventListener('change', (e) => {{
            clusterAtivo = e.target.value;
            desenhar();
        }});

        checkboxHubs.addEventListener('change', (e) => {{
            mostrarApenasHubs = e.target.checked;
            desenhar();
        }});

        btnResetFiltro.addEventListener('click', () => {{
            viewportX = 0;
            viewportY = 0;
            scale = 1;
            microregioAtiva = 'todas';
            clusterAtivo = 'todos';
            mostrarApenasHubs = false;
            bairroDestacado = null;
            selectMicro.value = 'todas';
            selectCluster.value = 'todos';
            checkboxHubs.checked = false;
            inputBusca.value = '';
            desenhar();
        }});

        inputBusca.addEventListener('input', (e) => {{
            const busca = e.target.value.toLowerCase().trim();
            if (busca === '') {{
                bairroDestacado = null;
            }} else {{
                const encontrado = nodes.find(n => n.label.toLowerCase().includes(busca));
                if (encontrado) {{
                    bairroDestacado = encontrado.id;
                    // Centralizar no bairro
                    viewportX = canvas.width / 2 - encontrado.x * scale;
                    viewportY = canvas.height / 2 - encontrado.y * scale;
                }}
            }}
            desenhar();
        }});

        // Função para verificar se nó deve ser exibido
        function nodeVisivel(node) {{
            // Filtro de microrregião
            if (microregioAtiva !== 'todas') {{
                const micros = node.microrregiao.split(' / ');
                if (!micros.includes(microregioAtiva)) {{
                    return false;
                }}
            }}

            // Filtro de cluster
            if (clusterAtivo !== 'todos') {{
                if (node.cluster_conectividade !== parseInt(clusterAtivo)) {{
                    return false;
                }}
            }}

            // Filtro de hubs
            if (mostrarApenasHubs && !node.top_20_percent) {{
                return false;
            }}

            // Bairro destacado
            if (bairroDestacado !== null && node.id !== bairroDestacado) {{
                return false;
            }}

            return true;
        }}

        // Função de desenho
        function desenhar() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Fundo
            ctx.fillStyle = '#fafafa';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(viewportX, viewportY);
            ctx.scale(scale, scale);

            // Desenhar arestas (leves para não distrair)
            ctx.strokeStyle = 'rgba(189, 195, 199, 0.3)';
            ctx.lineWidth = 1 / scale;

            edges.forEach(edge => {{
                const from = nodes[edge.from];
                const to = nodes[edge.to];

                // Mostrar aresta apenas se ambos os nós estão visíveis
                if (!nodeVisivel(from) || !nodeVisivel(to)) return;

                ctx.beginPath();
                ctx.moveTo(from.x, from.y);
                ctx.lineTo(to.x, to.y);
                ctx.stroke();
            }});

            // Desenhar nós
            nodes.forEach(node => {{
                if (!nodeVisivel(node)) return;

                // Tamanho do nó baseado em log(empresas) para melhor escala visual
                const raioBase = node.total_empresas > 0
                    ? 5 + Math.log(node.total_empresas + 1) * 3
                    : 4;

                // Cor baseada no cluster de conectividade
                ctx.fillStyle = node.cor_cluster;

                // Desenhar círculo do nó
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioBase, 0, 2 * Math.PI);
                ctx.fill();

                // Borda para top 20% (hubs de conectividade)
                if (node.top_20_percent) {{
                    ctx.strokeStyle = '#e74c3c';
                    ctx.lineWidth = 3 / scale;
                    ctx.stroke();
                }}

                // Borda padrão
                ctx.strokeStyle = '#34495e';
                ctx.lineWidth = 1.5 / scale;
                ctx.stroke();

                // Label (apenas para bairros destacados ou top hubs)
                if (bairroDestacado === node.id || (scale > 1.5 && node.top_20_percent)) {{
                    ctx.fillStyle = '#2c3e50';
                    ctx.font = `${{12 / scale}}px 'Segoe UI', sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y - raioBase - 10 / scale);
                }}
            }});

            ctx.restore();
        }}

        // Interatividade - Pan e Zoom
        canvas.addEventListener('mousedown', (e) => {{
            dragging = true;
            dragStart = {{ x: e.clientX - viewportX, y: e.clientY - viewportY }};
            canvas.classList.add('dragging');
        }});

        canvas.addEventListener('mousemove', (e) => {{
            if (dragging) {{
                viewportX = e.clientX - dragStart.x;
                viewportY = e.clientY - dragStart.y;
                desenhar();
            }} else {{
                // Tooltip
                const rect = canvas.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left - viewportX) / scale;
                const mouseY = (e.clientY - rect.top - viewportY) / scale;

                let nodeEncontrado = null;
                for (let node of nodes) {{
                    if (!nodeVisivel(node)) continue;

                    const raioBase = node.total_empresas > 0
                        ? 5 + Math.log(node.total_empresas + 1) * 3
                        : 4;

                    const dist = Math.sqrt((mouseX - node.x) ** 2 + (mouseY - node.y) ** 2);
                    if (dist <= raioBase) {{
                        nodeEncontrado = node;
                        break;
                    }}
                }}

                if (nodeEncontrado) {{
                    tooltip.style.display = 'block';
                    tooltip.style.left = e.clientX + 15 + 'px';
                    tooltip.style.top = e.clientY + 15 + 'px';

                    let atividadesHTML = '';
                    if (nodeEncontrado.top_3_atividades && nodeEncontrado.top_3_atividades.length > 0) {{
                        atividadesHTML = '<div style="margin-top: 8px;"><div class="tooltip-label">Top 3 Atividades:</div>';
                        nodeEncontrado.top_3_atividades.forEach((ativ, i) => {{
                            atividadesHTML += `<div class="tooltip-atividade">${{i + 1}}. ${{ativ.atividade}}: ${{ativ.quantidade}}</div>`;
                        }});
                        atividadesHTML += '</div>';
                    }}

                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{nodeEncontrado.label}}</div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Microrregião:</span>
                            <span class="tooltip-value">${{nodeEncontrado.microrregiao}}</span>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Cluster de Conectividade:</span>
                            <span class="tooltip-value">${{nodeEncontrado.cluster_conectividade === -1 ? 'N/A' : nodeEncontrado.cluster_conectividade}}</span>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Total de Empresas:</span>
                            <span class="tooltip-value">${{nodeEncontrado.total_empresas.toLocaleString()}}</span>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Grau (conexões):</span>
                            <span class="tooltip-value">${{nodeEncontrado.grau}}</span>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Centralidade de Grau:</span>
                            <span class="tooltip-value">${{nodeEncontrado.centralidade_grau.toFixed(3)}}</span>
                        </div>
                        ${{nodeEncontrado.top_20_percent ? '<div class="tooltip-row" style="color: #e74c3c; font-weight: 600;">⭐ Hub de Conectividade (Top 20%)</div>' : ''}}
                        ${{atividadesHTML}}
                    `;
                }} else {{
                    tooltip.style.display = 'none';
                }}
            }}
        }});

        canvas.addEventListener('mouseup', () => {{
            dragging = false;
            canvas.classList.remove('dragging');
        }});

        canvas.addEventListener('mouseleave', () => {{
            dragging = false;
            canvas.classList.remove('dragging');
            tooltip.style.display = 'none';
        }});

        canvas.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            const newScale = scale * delta;

            if (newScale >= 0.3 && newScale <= 5) {{
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                viewportX = mouseX - (mouseX - viewportX) * delta;
                viewportY = mouseY - (mouseY - viewportY) * delta;
                scale = newScale;

                desenhar();
            }}
        }});

        // Desenho inicial
        desenhar();

        // Auto-zoom para caber na tela inicialmente
        setTimeout(() => {{
            const minX = Math.min(...nodes.map(n => n.x));
            const maxX = Math.max(...nodes.map(n => n.x));
            const minY = Math.min(...nodes.map(n => n.y));
            const maxY = Math.max(...nodes.map(n => n.y));

            const graphWidth = maxX - minX;
            const graphHeight = maxY - minY;

            const scaleX = canvas.width / (graphWidth + 400);
            const scaleY = canvas.height / (graphHeight + 400);

            scale = Math.min(scaleX, scaleY, 1);

            viewportX = (canvas.width - (minX + maxX) * scale) / 2;
            viewportY = (canvas.height - (minY + maxY) * scale) / 2;

            desenhar();
        }}, 100);
    </script>
</body>
</html>
'''

# Salvar arquivo HTML
output_file = 'Visualizacao_Empresas/grafo_conectividade.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização salva: {output_file}")
print(f"\nAbra o arquivo no navegador para visualizar o grafo de conectividade econômica!")
