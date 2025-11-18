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

# Construir grafo
def construir_grafo():
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

grafo = construir_grafo()

# Criar mapa de bairro original -> normalizado
bairro_original_para_normalizado = {b: normalizar_nome(b) for b in grafo.vertices}

# Carregar dados de empresas dos bairros
df_empresas = pd.read_csv('Visualizacao_Empresas/empresas_bairros.csv', encoding='utf-8-sig')

# Converter string de top_3_atividades para lista
df_empresas['top_3_atividades'] = df_empresas['top_3_atividades'].apply(ast.literal_eval)

# Criar dicionário de dados por bairro NORMALIZADO
dados_bairro = {}
for _, row in df_empresas.iterrows():
    bairro_norm = row['bairro_normalizado']
    dados_bairro[bairro_norm] = {
        'total_empresas': row['total_empresas'],
        'top_3_atividades': row['top_3_atividades'],
        'microrregiao': row['microrregiao']
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

# Agrupar por microrregiões para posicionamento
microrregioes_agrupadas = {}
for bairro in grafo.vertices:
    micro = microrregiao_dict.get(bairro, 'N/A')
    for m in micro.split(' / '):
        if m not in microrregioes_agrupadas:
            microrregioes_agrupadas[m] = []
        microrregioes_agrupadas[m].append(bairro)

for micro in microrregioes_agrupadas:
    microrregioes_agrupadas[micro] = list(set(microrregioes_agrupadas[micro]))

# Posições dos clusters (mesmas do grafo original)
posicoes_clusters = {
    '1.1': (1000, 1000), '1.2': (2500, 1000), '1.3': (4000, 1000),
    '2.1': (500, 2500), '2.2': (2000, 2500), '2.3': (3500, 2500),
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
bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

# Criar nós com informações de empresas
nodes = []
for i, bairro in enumerate(bairros_lista):
    # Normalizar o nome do bairro para buscar nos dados
    bairro_norm = normalizar_nome(bairro)

    micro = microrregiao_dict.get(bairro, 'N/A')
    # IMPORTANTE: Buscar usando nome normalizado
    dados = dados_bairro.get(bairro_norm, {'total_empresas': 0, 'top_3_atividades': [], 'microrregiao': micro})

    # Obter dados da microrregião
    micro_principal = micro.split(' / ')[0].strip() if ' / ' in micro else micro
    dados_m = dados_micro.get(micro_principal, {'total_empresas': 0, 'top_3_atividades': []})

    # Determinar atividade principal
    atividade_principal = 'SEM_DADOS'
    if dados['top_3_atividades'] and len(dados['top_3_atividades']) > 0:
        atividade_principal = dados['top_3_atividades'][0]['atividade']

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': micro,
        'total_empresas': int(dados['total_empresas']),
        'top_3_atividades': dados['top_3_atividades'],
        'total_empresas_micro': int(dados_m['total_empresas']),
        'top_3_atividades_micro': dados_m['top_3_atividades'],
        'atividade_principal': atividade_principal
    })

# Remover arestas paralelas
pares_vistos = {}
edges = []

for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    par = tuple(sorted([origem, destino]))

    if par not in pares_vistos:
        pares_vistos[par] = True
        edges.append({
            'from': bairro_to_id[origem],
            'to': bairro_to_id[destino],
            'label': aresta['logradouro'],
            'peso': aresta['peso']
        })

# Calcular centros e raios das microrregiões para os halos
micro_info = {}
for micro, bairros in microrregioes_agrupadas.items():
    if len(bairros) == 0:
        continue

    centro_x = sum(posicoes[b]['x'] for b in bairros) / len(bairros)
    centro_y = sum(posicoes[b]['y'] for b in bairros) / len(bairros)

    raio_max = 0
    for b in bairros:
        dist = math.sqrt((posicoes[b]['x'] - centro_x)**2 + (posicoes[b]['y'] - centro_y)**2)
        raio_max = max(raio_max, dist)

    raio_halo = raio_max + 100

    dados_m = dados_micro.get(str(micro), {'total_empresas': 0, 'top_3_atividades': []})

    micro_info[micro] = {
        'centro_x': centro_x,
        'centro_y': centro_y,
        'raio': raio_halo,
        'total_empresas': int(dados_m['total_empresas']),
        'top_3_atividades': dados_m['top_3_atividades'],
        'bairros': bairros
    }

print(f"Grafo de Empresas criado:")
print(f"  Vértices: {len(nodes)}")
print(f"  Arestas originais: {len(grafo.arestas)}")
print(f"  Arestas únicas: {len(edges)}")
print(f"  Microrregiões: {len(micro_info)}")

# Calcular min e max para escala de halos
empresas_counts = [n['total_empresas'] for n in nodes if n['total_empresas'] > 0]
if empresas_counts:
    print(f"\nEmpresas por bairro:")
    print(f"  Mín: {min(empresas_counts)}")
    print(f"  Máx: {max(empresas_counts)}")
    print(f"  Média: {sum(empresas_counts) / len(empresas_counts):.0f}")

print("\nTop 5 bairros com mais empresas:")
top_bairros = sorted(nodes, key=lambda x: x['total_empresas'], reverse=True)[:5]
for b in top_bairros:
    print(f"  {b['label']}: {b['total_empresas']} empresas")

# Gerar HTML da visualização
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grafo de Empresas por Bairro - Recife</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
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
            color: #333;
            font-size: 24px;
        }}
        #filtroMicro {{
            margin: 10px 0;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        select, input[type="text"] {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }}
        select:focus, input[type="text"]:focus {{
            outline: none;
            border-color: #4ecdc4;
        }}
        input[type="text"] {{
            min-width: 250px;
        }}
        button {{
            padding: 8px 16px;
            background: #4ecdc4;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        button:hover {{
            background: #3db5ac;
        }}
        #legenda {{
            display: flex;
            gap: 20px;
            margin-top: 10px;
            font-size: 13px;
            align-items: center;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legenda-cor {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 2px solid #333;
            background: #9b59b6;
        }}
        #canvasContainer {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: white;
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
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 15px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 100;
            max-width: 320px;
            line-height: 1.5;
        }}
        .tooltip-title {{
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
            padding-bottom: 5px;
        }}
        .tooltip-row {{
            margin: 3px 0;
        }}
        .tooltip-label {{
            color: #aaa;
            font-size: 11px;
        }}
        .tooltip-atividade {{
            margin: 2px 0;
            padding-left: 10px;
            font-size: 12px;
        }}
        #painelMicroregioes {{
            position: absolute;
            right: -400px;
            top: 0;
            width: 400px;
            height: 100%;
            background: white;
            box-shadow: -2px 0 10px rgba(0,0,0,0.2);
            transition: right 0.3s ease;
            overflow-y: auto;
            z-index: 50;
            padding: 20px;
        }}
        #painelMicroregioes.aberto {{
            right: 0;
        }}
        .fechar-painel {{
            position: sticky;
            top: 0;
            background: white;
            padding: 10px 0;
            border-bottom: 2px solid #eee;
            margin-bottom: 15px;
        }}
        .micro-item {{
            margin: 15px 0;
            padding: 12px;
            background: #f9f9f9;
            border-radius: 6px;
            border-left: 4px solid #4ecdc4;
        }}
        .micro-titulo {{
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 14px;
            color: #4ecdc4;
        }}
        .micro-total {{
            font-size: 13px;
            color: #555;
            margin-bottom: 8px;
        }}
        .micro-atividade {{
            margin: 4px 0;
            padding: 6px;
            background: white;
            border-radius: 4px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>Empresas por Bairro - Recife</h1>
            <div id="filtroMicro">
                <label for="selectMicro"><strong>Filtrar por Microrregião:</strong></label>
                <select id="selectMicro">
                    <option value="todas">Todas as Microrregiões</option>
                </select>
                <label for="inputBusca"><strong>Buscar Bairro:</strong></label>
                <input type="text" id="inputBusca" placeholder="Digite o nome do bairro...">
                <button id="btnResetFiltro">Resetar Visualização</button>
                <button id="btnTopMicroregioes">📊 Ver Top 3 por Microrregião</button>
            </div>
            <div id="legenda">
                <span style="font-weight: bold; margin-right: 10px;">Cores por Atividade Principal:</span>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #3498db;"></div>
                    <span>Varejo</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #e74c3c;"></div>
                    <span>Saúde</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #f39c12;"></div>
                    <span>Educação</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #9b59b6;"></div>
                    <span>Construção</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #1abc9c;"></div>
                    <span>Informática</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #16a085;"></div>
                    <span>Outros</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #95a5a6;"></div>
                    <span>Sem empresas</span>
                </div>
                <span style="margin-left: 20px; color: #666;">
                    | Total: {sum(n['total_empresas'] for n in nodes):,} empresas
                </span>
            </div>
        </div>
        <div id="canvasContainer">
            <canvas id="canvas"></canvas>
            <div id="tooltip"></div>
            <div id="painelMicroregioes">
                <div class="fechar-painel">
                    <h2 style="margin: 0 0 10px 0;">Top 3 Atividades por Microrregião</h2>
                    <button onclick="fecharPainelMicro()">✕ Fechar</button>
                </div>
                <div id="conteudoPainelMicro"></div>
            </div>
        </div>
    </div>
    <script>
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};
        const microregioes = {json.dumps(list(micro_info.values()))};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        const selectMicro = document.getElementById('selectMicro');
        const btnResetFiltro = document.getElementById('btnResetFiltro');
        const inputBusca = document.getElementById('inputBusca');
        const btnTopMicroregioes = document.getElementById('btnTopMicroregioes');
        const painelMicroregioes = document.getElementById('painelMicroregioes');

        btnTopMicroregioes.addEventListener('click', () => {{
            painelMicroregioes.classList.add('aberto');
            gerarPainelMicroregioes();
        }});

        function fecharPainelMicro() {{
            painelMicroregioes.classList.remove('aberto');
        }}

        function gerarPainelMicroregioes() {{
            // Ordenar microrregiões por total de empresas
            const microsOrdenadas = [...microregioes].sort((a, b) => b.total_empresas - a.total_empresas);

            let html = '';
            microsOrdenadas.forEach(micro => {{
                const microNome = micro.bairros[0] ? nodes.find(n => n.label === micro.bairros[0])?.microrregiao : 'N/A';

                html += `
                    <div class="micro-item">
                        <div class="micro-titulo">Microrregião ${{microNome}}</div>
                        <div class="micro-total">Total: ${{micro.total_empresas.toLocaleString()}} empresas</div>
                        <div><strong>Top 3 Atividades:</strong></div>
                `;

                micro.top_3_atividades.forEach((ativ, idx) => {{
                    html += `
                        <div class="micro-atividade">
                            ${{idx + 1}}. ${{ativ.atividade}} <strong>(${{ativ.quantidade}})</strong>
                        </div>
                    `;
                }});

                html += '</div>';
            }});

            document.getElementById('conteudoPainelMicro').innerHTML = html;
        }}

        let offsetX = 0;
        let offsetY = 0;
        let scale = 1.0;
        let isDragging = false;
        let startX, startY;
        let bairroSelecionado = null;
        let microSelecionada = 'todas';
        let bairroBuscado = null;

        // Popular dropdown de microrregiões
        const microregioesUnicas = [...new Set(nodes.map(n => n.microrregiao))].sort();
        microregioesUnicas.forEach(micro => {{
            const option = document.createElement('option');
            option.value = micro;
            const microInfo = microregioes.find(m => m.bairros && m.bairros.includes(nodes.find(n => n.microrregiao === micro)?.label));
            const total = microInfo ? microInfo.total_empresas : 'N/A';
            option.textContent = `${{micro}} (${{total}} empresas)`;
            selectMicro.appendChild(option);
        }});

        selectMicro.addEventListener('change', (e) => {{
            microSelecionada = e.target.value;
            bairroSelecionado = null;

            if (microSelecionada !== 'todas') {{
                const microInfo = microregioes.find(m => {{
                    const primeiroNo = nodes.find(n => {{
                        const microPrincipal = n.microrregiao.includes(' / ')
                            ? n.microrregiao.split(' / ')[0].trim()
                            : n.microrregiao;
                        return microPrincipal === microSelecionada || n.microrregiao === microSelecionada;
                    }});
                    return primeiroNo && m.bairros && m.bairros.includes(primeiroNo.label);
                }});

                if (microInfo) {{
                    offsetX = canvas.width / 2 - microInfo.centro_x * scale;
                    offsetY = canvas.height / 2 - microInfo.centro_y * scale;
                }}
            }}

            draw();
        }});

        // Busca de bairro
        inputBusca.addEventListener('input', (e) => {{
            const busca = e.target.value.trim().toLowerCase();
            if (busca.length === 0) {{
                bairroBuscado = null;
                draw();
                return;
            }}

            const bairroEncontrado = nodes.find(n =>
                n.label.toLowerCase().includes(busca)
            );

            if (bairroEncontrado) {{
                bairroBuscado = bairroEncontrado.label;
                bairroSelecionado = bairroEncontrado.label;

                offsetX = canvas.width / 2 - bairroEncontrado.x * scale;
                offsetY = canvas.height / 2 - bairroEncontrado.y * scale;

                draw();
            }} else {{
                bairroBuscado = null;
                draw();
            }}
        }});

        btnResetFiltro.addEventListener('click', () => {{
            microSelecionada = 'todas';
            selectMicro.value = 'todas';
            bairroSelecionado = null;
            bairroBuscado = null;
            inputBusca.value = '';
            scale = 1.0;
            offsetX = canvas.width / 2 - 3000;
            offsetY = canvas.height / 2 - 4000;
            draw();
        }});

        function resizeCanvas() {{
            const container = document.getElementById('canvasContainer');
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            offsetX = canvas.width / 2 - 3000;
            offsetY = canvas.height / 2 - 4000;
            draw();
        }}

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        let mouseDownX = 0;
        let mouseDownY = 0;
        let hasMoved = false;

        canvas.addEventListener('mousedown', (e) => {{
            const rect = canvas.getBoundingClientRect();
            mouseDownX = e.clientX - rect.left;
            mouseDownY = e.clientY - rect.top;
            hasMoved = false;
            isDragging = true;
            startX = e.clientX - offsetX;
            startY = e.clientY - offsetY;
        }});

        canvas.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                const rect = canvas.getBoundingClientRect();
                const currentX = e.clientX - rect.left;
                const currentY = e.clientY - rect.top;
                const distMoved = Math.sqrt(Math.pow(currentX - mouseDownX, 2) + Math.pow(currentY - mouseDownY, 2));

                if (distMoved > 5) {{
                    hasMoved = true;
                    canvas.classList.add('dragging');
                    offsetX = e.clientX - startX;
                    offsetY = e.clientY - startY;
                    draw();
                }}
            }} else {{
                handleMouseMove(e);
            }}
        }});

        canvas.addEventListener('mouseup', (e) => {{
            if (!hasMoved) {{
                const rect = canvas.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left - offsetX) / scale;
                const mouseY = (e.clientY - rect.top - offsetY) / scale;

                let clicouEmBairro = false;
                for (const node of nodes) {{
                    const raio = calcularRaioVertice(node.total_empresas);
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < raio) {{
                        if (bairroSelecionado === node.label) {{
                            bairroSelecionado = null;
                        }} else {{
                            bairroSelecionado = node.label;
                        }}
                        clicouEmBairro = true;
                        draw();
                        break;
                    }}
                }}

                if (!clicouEmBairro && bairroSelecionado) {{
                    bairroSelecionado = null;
                    draw();
                }}
            }}

            isDragging = false;
            hasMoved = false;
            canvas.classList.remove('dragging');
        }});

        canvas.addEventListener('mouseleave', () => {{
            isDragging = false;
            canvas.classList.remove('dragging');
            tooltip.style.display = 'none';
        }});

        canvas.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const worldX = (mouseX - offsetX) / scale;
            const worldY = (mouseY - offsetY) / scale;
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            const newScale = Math.max(0.1, Math.min(5, scale * delta));
            scale = newScale;
            offsetX = mouseX - worldX * scale;
            offsetY = mouseY - worldY * scale;
            draw();
        }});

        function getCorAtividade(atividade, totalEmpresas) {{
            // Cinza apenas para bairros sem empresas
            if (!totalEmpresas || totalEmpresas === 0) return '#95a5a6';
            // Se não tem atividade definida mas tem empresas
            if (!atividade || atividade === 'SEM_DADOS') return '#16a085';

            if (atividade.includes('VAREJISTA')) return '#3498db';
            if (atividade === 'SAUDE') return '#e74c3c';
            if (atividade === 'EDUCACAO') return '#f39c12';
            if (atividade === 'CONSTRUCAO CIVIL') return '#9b59b6';
            if (atividade.includes('INFORMATICA')) return '#1abc9c';
            return '#16a085'; // Verde escuro para "Outros"
        }}

        function calcularRaioVertice(totalEmpresas) {{
            // Vértice proporcional ao número de empresas
            // Empresas entre 0-14240, vértices entre 8-35 pixels de raio
            if (totalEmpresas === 0) return 8;
            const proporcao = totalEmpresas / 14240; // Maior valor observado
            return 8 + (proporcao * 27); // 8 a 35 pixels
        }}

        function calcularRaioHalo(totalEmpresas) {{
            // Halo proporcional ao número de empresas
            // Empresas entre 0-14240, halos entre 50-220 pixels
            if (totalEmpresas === 0) return 50;
            const proporcao = totalEmpresas / 14240; // Maior valor observado
            return 50 + (proporcao * 170); // 50 a 220 pixels
        }}

        function handleMouseMove(e) {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;

            let found = false;
            for (const node of nodes) {{
                const raio = calcularRaioVertice(node.total_empresas);
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < raio) {{
                    let top3Html = '';
                    if (node.top_3_atividades && node.top_3_atividades.length > 0) {{
                        top3Html = '<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);"><strong>Top 3 Atividades:</strong></div>';
                        node.top_3_atividades.forEach((ativ, idx) => {{
                            top3Html += `<div class="tooltip-atividade">${{idx + 1}}. ${{ativ.atividade}} (${{ativ.quantidade}})</div>`;
                        }});
                    }}

                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{node.label}}</div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Total de Empresas:</span>
                            <strong>${{node.total_empresas.toLocaleString()}}</strong>
                        </div>
                        ${{top3Html}}
                        <div class="tooltip-row" style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2);">
                            <span class="tooltip-label">Microrregião:</span> ${{node.microrregiao}}
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
            ctx.save();
            ctx.translate(offsetX, offsetY);
            ctx.scale(scale, scale);

            let vizinhosSet = null;
            let arestasVizinhos = new Set();

            if (bairroSelecionado) {{
                vizinhosSet = new Set();
                vizinhosSet.add(bairroSelecionado);

                edges.forEach(edge => {{
                    const fromNode = nodes[edge.from];
                    const toNode = nodes[edge.to];

                    if (fromNode.label === bairroSelecionado) {{
                        vizinhosSet.add(toNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }} else if (toNode.label === bairroSelecionado) {{
                        vizinhosSet.add(fromNode.label);
                        arestasVizinhos.add(`${{edge.from}}-${{edge.to}}`);
                    }}
                }});
            }}

            // Determinar quais nós devem ser exibidos baseado no filtro
            const nodesFiltrados = microSelecionada === 'todas'
                ? nodes
                : nodes.filter(n => {{
                    const microPrincipal = n.microrregiao.split(' / ')[0].trim();
                    return microPrincipal === microSelecionada || n.microrregiao === microSelecionada;
                }});

            const labelsFiltrados = new Set(nodesFiltrados.map(n => n.label));

            // 1. Desenhar arestas
            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#4ecdc4';
                    ctx.lineWidth = 3;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    ctx.strokeStyle = '#999';
                    ctx.lineWidth = 1;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 2. Desenhar nós com halo individual
            nodes.forEach(node => {{
                if (!labelsFiltrados.has(node.label)) return;

                const raioNo = calcularRaioVertice(node.total_empresas);
                const raioHalo = calcularRaioHalo(node.total_empresas);
                let shouldDim = false;

                if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                // Desenhar halo individual
                if (!shouldDim && node.total_empresas > 0) {{
                    const corHalo = getCorAtividade(node.atividade_principal, node.total_empresas);
                    const gradient = ctx.createRadialGradient(node.x, node.y, raioNo, node.x, node.y, raioHalo);
                    gradient.addColorStop(0, corHalo + '00');
                    gradient.addColorStop(0.5, corHalo + '30');
                    gradient.addColorStop(1, corHalo + '60');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, raioHalo, 0, Math.PI * 2);
                    ctx.fill();
                }}

                // Desenhar nó principal
                const corNo = getCorAtividade(node.atividade_principal, node.total_empresas);
                ctx.fillStyle = shouldDim ? '#d0d0d0' : corNo;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.fill();

                // Borda do nó
                ctx.strokeStyle = (vizinhosSet && node.label === bairroSelecionado) ? '#e74c3c' : '#333';
                ctx.lineWidth = (vizinhosSet && node.label === bairroSelecionado) ? 4 : 2;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.stroke();

                // Label do bairro
                if (scale > 0.4) {{
                    ctx.fillStyle = '#333';
                    ctx.font = 'bold 14px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y + raioNo + 18);
                }}
            }});

            ctx.restore();
        }}

        draw();
    </script>
</body>
</html>'''

with open('Visualizacao_Empresas/grafo_empresas.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização gerada: Visualizacao_Empresas/grafo_empresas.html")
