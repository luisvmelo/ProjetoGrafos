import json
import math
import random
import pandas as pd
import os
import sys

# Mudar para o diretório raiz do projeto
os.chdir('/home/luisevmelo/ProjetoGrafos-1')

# Importar classes necessárias
sys.path.append('src/graphs')
from graph import Grafo

def construir_grafo_base():
    df = pd.read_csv('data/adjacencias_bairros.csv')
    grafo = Grafo()
    for _, row in df.iterrows():
        grafo.adicionar_aresta(
            row['bairro_origem'],
            row['bairro_destino'],
            row['logradouro'],
            row['peso']
        )
    return grafo

grafo_base = construir_grafo_base()

# Carregar dados de transporte público (ônibus, metro, VLT)
df_transporte = pd.read_csv('Visualizacao_Transporte/arestas_bairros_transporte.csv', encoding='utf-8-sig')

print(f"Total de conexões: {len(df_transporte)}")
print(f"  Ônibus: {len(df_transporte[df_transporte['mode'] == 'onibus'])}")
print(f"  Metro: {len(df_transporte[df_transporte['mode'] == 'metro'])}")
print(f"  VLT: {len(df_transporte[df_transporte['mode'] == 'vlt'])}")

# Carregar microrregiões
df_bairros = pd.read_csv('data/bairros_unique.csv', encoding='utf-8-sig', sep=';')
microrregiao_dict = {row['bairro']: row['microrregião'] for _, row in df_bairros.iterrows()}

# Carregar dados socioeconômicos
df_socio = pd.read_csv('Visualizacao_Transporte/bairros_socioeconomico_transporte.csv', encoding='utf-8-sig')

# Criar dicionário de dados socioeconômicos por bairro (usando nome original do grafo)
import unicodedata

def normalizar_nome(texto):
    if pd.isna(texto):
        return ''
    texto = str(texto).strip()
    mapeamentos_especiais = {
        'Sitio dos Pintos   Sao Bras': 'Sítio dos Pintos',
        'Cohab   Ibura de Cima': 'Cohab',
        'Alto do Mandu   Sitio Grande': 'Alto do Mandu',
        'BAIRRO DO RECIFE': 'Recife',
        'Bairro do Recife': 'Recife',
        'POCO DA PANELA': 'Poço'
    }
    if texto in mapeamentos_especiais:
        texto = mapeamentos_especiais[texto]
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    normalizado = ' '.join(sem_acento.split())
    normalizado = normalizado.replace('Terezinha', 'Teresinha')
    return normalizado.title()

# Criar dicionário de dados socioeconômicos
dados_socio = {}
for _, row in df_socio.iterrows():
    dados_socio[row['bairro_normalizado']] = {
        'populacao': row['populacao'],
        'renda_mensal': row['renda_mensal'],
        'grau_transporte': row['grau_transporte'],
        'renda_norm': row['renda_norm'],
        'populacao_norm': row['populacao_norm'],
        'grau_norm': row['grau_norm'],
        'indice_acesso': row['indice_acesso'],
        'indice_acesso_norm': row['indice_acesso_norm'],
        'taxa_alfabetizacao': row['taxa_alfabetizacao'],
        'rpa': row['rpa']
    }

# Criar dicionários de bairros conectados por cada tipo de transporte
bairros_com_transporte = set()
conexoes_onibus = set()
conexoes_metro = set()
conexoes_vlt = set()

for _, row in df_transporte.iterrows():
    bairro_a = row['bairro_a']
    bairro_b = row['bairro_b']
    mode = row['mode']

    bairros_com_transporte.add(bairro_a)
    bairros_com_transporte.add(bairro_b)

    # Adicionar conexão por modo de transporte (ambas direções)
    if mode == 'onibus':
        conexoes_onibus.add((bairro_a, bairro_b))
        conexoes_onibus.add((bairro_b, bairro_a))
    elif mode == 'metro':
        conexoes_metro.add((bairro_a, bairro_b))
        conexoes_metro.add((bairro_b, bairro_a))
    elif mode == 'vlt':
        conexoes_vlt.add((bairro_a, bairro_b))
        conexoes_vlt.add((bairro_b, bairro_a))

print(f"Bairros com transporte público: {len(bairros_com_transporte)}")

# Agrupar bairros por microrregião (usar apenas a PRIMEIRA microrregião para posicionamento)
random.seed(42)
microrregioes_agrupadas = {}
for bairro in grafo_base.vertices:
    micro = microrregiao_dict.get(bairro, 'N/A')
    # Pegar apenas a PRIMEIRA microrregião para evitar sobrescrever posições
    micro_principal = micro.split(' / ')[0]
    if micro_principal not in microrregioes_agrupadas:
        microrregioes_agrupadas[micro_principal] = []
    microrregioes_agrupadas[micro_principal].append(bairro)

for micro in microrregioes_agrupadas:
    microrregioes_agrupadas[micro] = list(set(microrregioes_agrupadas[micro]))

# Posições dos clusters (mesmas do projeto)
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

# Calcular posições dos bairros
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
bairros_lista = sorted(grafo_base.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

# Criar nós com dados socioeconômicos
nodes = []
for i, bairro in enumerate(bairros_lista):
    tem_transporte = bairro in bairros_com_transporte
    micro = microrregiao_dict.get(bairro, 'N/A')

    # Buscar dados socioeconômicos
    bairro_norm = normalizar_nome(bairro)
    socio = dados_socio.get(bairro_norm, {
        'populacao': 0,
        'renda_mensal': 0,
        'grau_transporte': 0,
        'renda_norm': 0,
        'populacao_norm': 0,
        'grau_norm': 0,
        'indice_acesso': 0,
        'indice_acesso_norm': 0,
        'taxa_alfabetizacao': 0,
        'rpa': 'N/A'
    })

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': micro,
        'tem_transporte': tem_transporte,
        'populacao': int(socio['populacao']),
        'renda_mensal': float(socio['renda_mensal']),
        'grau_transporte': int(socio['grau_transporte']),
        'renda_norm': float(socio['renda_norm']),
        'populacao_norm': float(socio['populacao_norm']),
        'grau_norm': float(socio['grau_norm']),
        'indice_acesso': float(socio['indice_acesso']),
        'indice_acesso_norm': float(socio['indice_acesso_norm']),
        'taxa_alfabetizacao': float(socio['taxa_alfabetizacao']),
        'rpa': str(socio['rpa'])
    })

# Criar arestas do grafo base (ruas)
edges_ruas = []
pares_vistos = {}

for aresta in grafo_base.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    par = tuple(sorted([origem, destino]))
    if par not in pares_vistos:
        pares_vistos[par] = True
        edges_ruas.append({
            'from': bairro_to_id[origem],
            'to': bairro_to_id[destino],
            'label': aresta['logradouro'],
            'tipo': 'rua'
        })

# Criar arestas de transporte público separadas por modo
edges_onibus = []
edges_metro = []
edges_vlt = []

pares_onibus_vistos = {}
pares_metro_vistos = {}
pares_vlt_vistos = {}

for (bairro_a, bairro_b) in conexoes_onibus:
    par = tuple(sorted([bairro_a, bairro_b]))
    if par not in pares_onibus_vistos and bairro_a in bairro_to_id and bairro_b in bairro_to_id:
        pares_onibus_vistos[par] = True
        edges_onibus.append({
            'from': bairro_to_id[bairro_a],
            'to': bairro_to_id[bairro_b],
            'tipo': 'onibus'
        })

for (bairro_a, bairro_b) in conexoes_metro:
    par = tuple(sorted([bairro_a, bairro_b]))
    if par not in pares_metro_vistos and bairro_a in bairro_to_id and bairro_b in bairro_to_id:
        pares_metro_vistos[par] = True
        edges_metro.append({
            'from': bairro_to_id[bairro_a],
            'to': bairro_to_id[bairro_b],
            'tipo': 'metro'
        })

for (bairro_a, bairro_b) in conexoes_vlt:
    par = tuple(sorted([bairro_a, bairro_b]))
    if par not in pares_vlt_vistos and bairro_a in bairro_to_id and bairro_b in bairro_to_id:
        pares_vlt_vistos[par] = True
        edges_vlt.append({
            'from': bairro_to_id[bairro_a],
            'to': bairro_to_id[bairro_b],
            'tipo': 'vlt'
        })

print(f"\nGrafo de Transporte criado:")
print(f"  Vértices: {len(nodes)}")
print(f"  Arestas de rua: {len(edges_ruas)}")
print(f"  Arestas de ônibus: {len(edges_onibus)}")
print(f"  Arestas de metro: {len(edges_metro)}")
print(f"  Arestas de VLT: {len(edges_vlt)}")
print(f"  Bairros com transporte público: {sum(1 for n in nodes if n['tem_transporte'])}")

# Estatísticas de população
total_pop = sum(n['populacao'] for n in nodes)
print(f"\nPopulação total: {total_pop:,} habitantes")
print(f"População com transporte: {sum(n['populacao'] for n in nodes if n['tem_transporte']):,}")

# Continua com o HTML...

# Gerar HTML da visualização
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Transporte Público e Indicadores Socioeconômicos - Recife</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
            height: 100vh;
            background: #f5f5f5;
        }}
        #app {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        #sidebar {{
            width: 100%;
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow-x: auto;
            overflow-y: visible;
            z-index: 10;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        h1 {{
            font-size: 18px;
            margin: 0;
            color: #333;
            white-space: nowrap;
        }}
        h2 {{
            font-size: 14px;
            margin: 0 0 5px 0;
            color: #555;
        }}
        .subtitle {{
            font-size: 12px;
            color: #666;
            margin: 0;
            line-height: 1.3;
            max-width: 300px;
        }}
        #filtroMicro {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-shrink: 0;
        }}
        #filtroMicro label {{
            margin: 0;
            font-weight: 600;
            font-size: 12px;
            white-space: nowrap;
        }}
        #filtroMicro select, #filtroMicro input {{
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
            min-width: 150px;
        }}
        #filtroMicro button {{
            padding: 6px 12px;
            background: #4ecdc4;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            white-space: nowrap;
        }}
        #filtroMicro button:hover {{
            background: #45b7b0;
        }}
        #legenda {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            flex-grow: 1;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin: 0;
            font-size: 12px;
        }}
        .legenda-cor {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 2px solid #333;
        }}
        .legenda-linha {{
            width: 40px;
            height: 3px;
            border-radius: 2px;
        }}
        .legenda-gradiente {{
            width: 100%;
            height: 20px;
            border-radius: 4px;
            margin: 8px 0;
            border: 1px solid #ddd;
        }}
        #canvasContainer {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: white;
            height: calc(100vh - 80px);
        }}
        #canvas {{
            display: block;
            cursor: grab;
        }}
        #canvas.dragging {{
            cursor: grabbing;
        }}
        #tooltip {{
            position: fixed;
            background: rgba(0, 0, 0, 0.92);
            color: white;
            padding: 14px 18px;
            border-radius: 8px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 1000;
            max-width: 350px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
            line-height: 1.5;
        }}
        .tooltip-title {{
            font-weight: bold;
            font-size: 17px;
            margin-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
            padding-bottom: 8px;
            color: #4ecdc4;
        }}
        .tooltip-row {{
            margin: 6px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }}
        .tooltip-label {{
            color: #ccc;
            font-size: 12px;
        }}
        .tooltip-value {{
            font-weight: 600;
            color: white;
        }}
    </style>
</head>
<body>
    <div id="app">
        <div id="sidebar">
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <h1>Transporte Público e Indicadores Socioeconômicos</h1>
                <p class="subtitle">Visualização das conexões de transporte público integrada com dados de população e renda dos bairros de Recife.</p>
            </div>

            <div id="filtroMicro">
                <label for="selectMicro">Microrregião:</label>
                <select id="selectMicro">
                    <option value="todas">Todas</option>
                </select>
                <label for="inputBusca">Bairro:</label>
                <input type="text" id="inputBusca" placeholder="Buscar...">
                <button id="btnResetFiltro">Resetar</button>
            </div>

            <div id="legenda">
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #bdc3c7; width: 25px;"></div>
                    <span>Ruas</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #2ecc71; width: 25px;"></div>
                    <span>Ônibus</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #e91e63; width: 25px;"></div>
                    <span>Metrô</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #ff9800; width: 25px;"></div>
                    <span>VLT</span>
                </div>
                <span style="margin: 0 10px; color: #999;">|</span>
                <span style="font-size: 11px; color: #666;">Tamanho = Vulnerabilidade | Cor = Renda</span>
                <span style="margin-left: auto; color: #7f8c8d; font-weight: 500; font-size: 11px;">
                    {total_pop:,} hab. | {sum(1 for n in nodes if n['tem_transporte'])} bairros
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
        const edgesRuas = {json.dumps(edges_ruas)};
        const edgesOnibus = {json.dumps(edges_onibus)};
        const edgesMetro = {json.dumps(edges_metro)};
        const edgesVlt = {json.dumps(edges_vlt)};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        const selectMicro = document.getElementById('selectMicro');
        const btnResetFiltro = document.getElementById('btnResetFiltro');
        const inputBusca = document.getElementById('inputBusca');

        let offsetX = 0;
        let offsetY = 0;
        let scale = 1.0;
        let isDragging = false;
        let startX, startY;
        let bairroSelecionado = null;
        let microSelecionada = 'todas';
        let bairroBuscado = null;

        // Popular dropdown de microrregiões (substituir . por -)
        const microregioesUnicas = [...new Set(nodes.map(n => n.microrregiao.replace(/\./g, '-')))].sort();
        microregioesUnicas.forEach(micro => {{
            const option = document.createElement('option');
            option.value = micro;
            option.textContent = micro;
            selectMicro.appendChild(option);
        }});

        selectMicro.addEventListener('change', (e) => {{
            microSelecionada = e.target.value;
            bairroSelecionado = null;
            draw();
        }});

        btnResetFiltro.addEventListener('click', () => {{
            microSelecionada = 'todas';
            bairroSelecionado = null;
            bairroBuscado = null;
            selectMicro.value = 'todas';
            inputBusca.value = '';
            offsetX = 0;
            offsetY = 0;
            scale = 1.0;
            draw();
        }});

        inputBusca.addEventListener('input', (e) => {{
            const termo = e.target.value.toLowerCase();
            if (termo.length >= 2) {{
                const encontrado = nodes.find(n => n.label.toLowerCase().includes(termo));
                if (encontrado) {{
                    bairroBuscado = encontrado.label;
                    bairroSelecionado = encontrado.label;
                    // Centralizar no bairro encontrado
                    offsetX = canvas.width / 2 - encontrado.x * scale;
                    offsetY = canvas.height / 2 - encontrado.y * scale;
                }}
            }} else {{
                bairroBuscado = null;
            }}
            draw();
        }});

        // Função para obter cor baseada na renda normalizada
        function getCorRenda(rendaNorm) {{
            // Gradiente: vermelho (baixa) -> amarelo (média) -> verde (alta)
            if (rendaNorm < 0.25) {{
                // Vermelho para laranja
                const t = rendaNorm / 0.25;
                const r = 231;
                const g = Math.floor(76 + (155 - 76) * t);
                const b = 60;
                return `rgb(${{r}}, ${{g}}, ${{b}})`;
            }} else if (rendaNorm < 0.5) {{
                // Laranja para amarelo
                const t = (rendaNorm - 0.25) / 0.25;
                const r = Math.floor(243 - (243 - 241) * t);
                const g = Math.floor(156 + (196 - 156) * t);
                const b = Math.floor(18 + (15 - 18) * t);
                return `rgb(${{r}}, ${{g}}, ${{b}})`;
            }} else if (rendaNorm < 0.75) {{
                // Amarelo para verde claro
                const t = (rendaNorm - 0.5) / 0.25;
                const r = Math.floor(241 - (241 - 46) * t);
                const g = Math.floor(196 + (204 - 196) * t);
                const b = Math.floor(15 + (113 - 15) * t);
                return `rgb(${{r}}, ${{g}}, ${{b}})`;
            }} else {{
                // Verde claro para verde escuro
                const t = (rendaNorm - 0.75) / 0.25;
                const r = Math.floor(46 - (46 - 39) * t);
                const g = Math.floor(204 - (204 - 174) * t);
                const b = Math.floor(113 - (113 - 96) * t);
                return `rgb(${{r}}, ${{g}}, ${{b}})`;
            }}
        }}

        function calcularRaioVulnerabilidade(indiceAcessoNorm) {{
            // Escala MUITO mais agressiva para diferenciar visualmente
            // Top 3 devem ser GIGANTES, resto pequeno

            const raioMin = 6;
            const raioMax = 70;  // Aumentado de 45 para 70

            // Aplicar escala SUPER exponencial para amplificar diferenças
            const exponente = 4.0;  // Aumentado de 2.5 para 4.0
            const valorExponencial = Math.pow(indiceAcessoNorm, exponente);

            return raioMin + (raioMax - raioMin) * valorExponencial;
        }}

        function resizeCanvas() {{
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            draw();
        }}

        // Função de relaxamento: ajusta posições para separar microregiões
        function ajustaPosicoesPorMicrorregiao(nodes) {{
            const iteracoes = 80;  // Número de iterações de relaxamento
            const distanciaMinima = 250;  // Distância mínima desejada entre nós
            const forcaRepulsaoInter = 2.5;  // Multiplicador de repulsão entre microregiões diferentes
            const forcaRepulsaoIntra = 0.3;  // Multiplicador de repulsão dentro da mesma microrregião

            console.log('Iniciando relaxamento de posições...');

            for (let iter = 0; iter < iteracoes; iter++) {{
                // Array para acumular deslocamentos
                const deslocamentos = nodes.map(() => ({{ dx: 0, dy: 0 }}));

                // Para cada par de nós
                for (let i = 0; i < nodes.length; i++) {{
                    for (let j = i + 1; j < nodes.length; j++) {{
                        const nodeA = nodes[i];
                        const nodeB = nodes[j];

                        // Calcular distância entre nós
                        const dx = nodeB.x - nodeA.x;
                        const dy = nodeB.y - nodeA.y;
                        const distancia = Math.sqrt(dx * dx + dy * dy);

                        if (distancia < distanciaMinima && distancia > 0.1) {{
                            // Verificar se são da mesma microrregião
                            const microA = nodeA.microrregiao.split(' / ').map(m => m.replace(/\\./g, '-'));
                            const microB = nodeB.microrregiao.split(' / ').map(m => m.replace(/\\./g, '-'));

                            const mesmaMicro = microA.some(ma => microB.includes(ma));

                            // Escolher força de repulsão
                            const forcaRepulsao = mesmaMicro ? forcaRepulsaoIntra : forcaRepulsaoInter;

                            // Calcular força (inversamente proporcional à distância)
                            const forca = forcaRepulsao * (distanciaMinima - distancia) / distancia;

                            // Vetor unitário da direção de repulsão
                            const fx = (dx / distancia) * forca;
                            const fy = (dy / distancia) * forca;

                            // Acumular deslocamentos (A empurrado para trás, B empurrado para frente)
                            deslocamentos[i].dx -= fx;
                            deslocamentos[i].dy -= fy;
                            deslocamentos[j].dx += fx;
                            deslocamentos[j].dy += fy;
                        }}
                    }}
                }}

                // Aplicar deslocamentos com fator de amortecimento
                const amortecimento = 0.1;  // Movimentos suaves
                for (let i = 0; i < nodes.length; i++) {{
                    nodes[i].x += deslocamentos[i].dx * amortecimento;
                    nodes[i].y += deslocamentos[i].dy * amortecimento;
                }}
            }}

            console.log('Relaxamento concluído!');
        }}

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // Aplicar relaxamento de posições antes do primeiro desenho
        ajustaPosicoesPorMicrorregiao(nodes);

        canvas.addEventListener('mousedown', (e) => {{
            isDragging = true;
            startX = e.clientX - offsetX;
            startY = e.clientY - offsetY;
            canvas.classList.add('dragging');
        }});

        canvas.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                offsetX = e.clientX - startX;
                offsetY = e.clientY - startY;
                draw();
            }}
            handleMouseMove(e);
        }});

        canvas.addEventListener('mouseup', () => {{
            isDragging = false;
            canvas.classList.remove('dragging');
        }});

        canvas.addEventListener('mouseleave', () => {{
            isDragging = false;
            canvas.classList.remove('dragging');
            tooltip.style.display = 'none';
        }});

        canvas.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const worldX = (mouseX - offsetX) / scale;
            const worldY = (mouseY - offsetY) / scale;
            scale = Math.max(0.1, Math.min(5, scale * delta));
            offsetX = mouseX - worldX * scale;
            offsetY = mouseY - worldY * scale;
            draw();
        }});

        function handleMouseMove(e) {{
            if (isDragging) return;

            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;

            let found = false;
            for (const node of nodes) {{
                // Calcular raio baseado em índice de vulnerabilidade (mesmo do desenho)
                const raio = calcularRaioVulnerabilidade(node.indice_acesso_norm);
                const dist = Math.sqrt((mouseX - node.x) ** 2 + (mouseY - node.y) ** 2);

                if (dist <= raio) {{
                    // Determinar status de vulnerabilidade
                    const statusVulnerabilidade = node.indice_acesso_norm > 0.7
                        ? '<span style="color: #e74c3c; font-weight: bold;">⚠ ALTA VULNERABILIDADE</span>'
                        : node.indice_acesso_norm > 0.4
                        ? '<span style="color: #f39c12;">Vulnerabilidade Moderada</span>'
                        : '<span style="color: #27ae60;">Boa Cobertura</span>';

                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{node.label}}</div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Microrregião:</span>
                            <strong class="tooltip-value">${{node.microrregiao}} (RPA ${{node.rpa}})</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">População:</span>
                            <strong class="tooltip-value">${{node.populacao.toLocaleString()}} hab.</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Renda Mensal Média:</span>
                            <strong class="tooltip-value">R$ ${{node.renda_mensal.toFixed(2)}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Grau de Transporte:</span>
                            <strong class="tooltip-value">${{node.grau_transporte}} conexões</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Índice de Vulnerabilidade:</span>
                            <strong class="tooltip-value">${{node.indice_acesso.toFixed(3)}} - ${{statusVulnerabilidade}}</strong>
                        </div>
                    `;
                    tooltip.style.left = (e.clientX + 15) + 'px';
                    tooltip.style.top = (e.clientY + 15) + 'px';
                    tooltip.style.display = 'block';
                    found = true;
                    break;
                }}
            }}

            if (!found) {{
                tooltip.style.display = 'none';
            }}
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#fafafa';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.save();
            ctx.translate(offsetX, offsetY);
            ctx.scale(scale, scale);

            // Filtrar nós visíveis
            const nodesFiltrados = nodes.filter(node => {{
                if (microSelecionada !== 'todas') {{
                    const micros = node.microrregiao.split(' / ').map(m => m.replace(/\./g, '-'));
                    if (!micros.includes(microSelecionada)) return false;
                }}
                if (bairroBuscado && node.label !== bairroBuscado) return false;
                return true;
            }});

            const labelsFiltrados = new Set(nodesFiltrados.map(n => n.label));

            // Identificar vizinhos se houver bairro selecionado
            let vizinhosSet = null;
            let arestasVizinhos = new Set();

            if (bairroSelecionado) {{
                vizinhosSet = new Set([bairroSelecionado]);
                
                // Adicionar vizinhos por ônibus
                edgesOnibus.forEach(edge => {{
                    const fromNode = nodes[edge.from];
                    const toNode = nodes[edge.to];

                    if (fromNode.label === bairroSelecionado) {{
                        vizinhosSet.add(toNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                    if (toNode.label === bairroSelecionado) {{
                        vizinhosSet.add(fromNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                }});

                // Adicionar vizinhos por metrô
                edgesMetro.forEach(edge => {{
                    const fromNode = nodes[edge.from];
                    const toNode = nodes[edge.to];

                    if (fromNode.label === bairroSelecionado) {{
                        vizinhosSet.add(toNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                    if (toNode.label === bairroSelecionado) {{
                        vizinhosSet.add(fromNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                }});

                // Adicionar vizinhos por VLT
                edgesVlt.forEach(edge => {{
                    const fromNode = nodes[edge.from];
                    const toNode = nodes[edge.to];

                    if (fromNode.label === bairroSelecionado) {{
                        vizinhosSet.add(toNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                    if (toNode.label === bairroSelecionado) {{
                        vizinhosSet.add(fromNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                }});
            }}

            // (Halos de microrregiões removidos)

            // 1. Desenhar arestas de ruas (muito leves, quase invisíveis)
            edgesRuas.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                ctx.strokeStyle = 'rgba(189, 195, 199, 0.08)';
                ctx.lineWidth = 0.3 / scale;

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 2. Desenhar arestas de ônibus (mais finas)
            edgesOnibus.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#2ecc71';
                    ctx.lineWidth = 2.5 / scale;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = 'rgba(46, 204, 113, 0.08)';
                    ctx.lineWidth = 0.5 / scale;
                }} else {{
                    ctx.strokeStyle = 'rgba(46, 204, 113, 0.3)';
                    ctx.lineWidth = 1 / scale;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 3. Desenhar arestas de metrô (mais finas)
            edgesMetro.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#e91e63';
                    ctx.lineWidth = 3 / scale;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = 'rgba(233, 30, 99, 0.08)';
                    ctx.lineWidth = 0.5 / scale;
                }} else {{
                    ctx.strokeStyle = 'rgba(233, 30, 99, 0.4)';
                    ctx.lineWidth = 1.5 / scale;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 4. Desenhar arestas de VLT (mais finas)
            edgesVlt.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#ff9800';
                    ctx.lineWidth = 3 / scale;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = 'rgba(255, 152, 0, 0.08)';
                    ctx.lineWidth = 0.5 / scale;
                }} else {{
                    ctx.strokeStyle = 'rgba(255, 152, 0, 0.4)';
                    ctx.lineWidth = 1.5 / scale;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 5. Desenhar nós (com maior destaque)
            nodesFiltrados.forEach(node => {{
                let shouldDim = false;

                if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                // Tamanho baseado em VULNERABILIDADE (não-linear para enfatizar diferenças)
                const raioBase = calcularRaioVulnerabilidade(node.indice_acesso_norm);

                // Cor baseada em renda (normalizada)
                const cor = getCorRenda(node.renda_norm);

                // Desenhar sombra do nó para dar mais destaque
                if (!shouldDim) {{
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
                    ctx.shadowBlur = 6 / scale;
                    ctx.shadowOffsetX = 2 / scale;
                    ctx.shadowOffsetY = 2 / scale;
                }}

                ctx.fillStyle = shouldDim ? '#d0d0d0' : cor;

                // Desenhar círculo do nó
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioBase, 0, Math.PI * 2);
                ctx.fill();

                // Resetar sombra
                ctx.shadowColor = 'transparent';
                ctx.shadowBlur = 0;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 0;

                // Adicionar borda fina ao nó
                ctx.strokeStyle = shouldDim ? '#999' : '#333';
                ctx.lineWidth = 1.5 / scale;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioBase, 0, Math.PI * 2);
                ctx.stroke();

                // Borda destacada para bairro selecionado (por cima da borda normal)
                if (vizinhosSet && node.label === bairroSelecionado) {{
                    ctx.strokeStyle = '#e74c3c';
                    ctx.lineWidth = 4 / scale;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, raioBase + 1, 0, Math.PI * 2);
                    ctx.stroke();
                }}

                // Label para bairros selecionados ou destacados
                if (bairroSelecionado === node.label || (bairroBuscado === node.label)) {{
                    ctx.fillStyle = '#2c3e50';
                    ctx.font = `bold ${{14 / scale}}px 'Segoe UI', sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    ctx.fillText(node.label, node.x, node.y - raioBase - 14 / scale);

                    // Mostrar população
                    ctx.font = `${{12 / scale}}px 'Segoe UI', sans-serif`;
                    ctx.fillStyle = '#7f8c8d';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`${{node.populacao.toLocaleString()}} hab.`, node.x, node.y + raioBase + 14 / scale);
                }}
            }});

            ctx.restore();
        }}

        // Desenho inicial
        draw();

        // Auto-zoom para caber na tela inicialmente
        setTimeout(() => {{
            const minX = Math.min(...nodes.map(n => n.x));
            const maxX = Math.max(...nodes.map(n => n.x));
            const minY = Math.min(...nodes.map(n => n.y));
            const maxY = Math.max(...nodes.map(n => n.y));

            const graphWidth = maxX - minX;
            const graphHeight = maxY - minY;

            const scaleX = canvas.width / (graphWidth + 800);
            const scaleY = canvas.height / (graphHeight + 800);

            scale = Math.min(scaleX, scaleY, 1);

            offsetX = (canvas.width - (minX + maxX) * scale) / 2;
            offsetY = (canvas.height - (minY + maxY) * scale) / 2;

            draw();
        }}, 100);
    </script>
</body>
</html>
'''

# Salvar arquivo HTML
output_file = 'Visualizacao_Transporte/grafo_transporte_socioeconomico.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização salva: {output_file}")
print(f"\nAbra o arquivo no navegador para visualizar o grafo com indicadores socioeconômicos!")
