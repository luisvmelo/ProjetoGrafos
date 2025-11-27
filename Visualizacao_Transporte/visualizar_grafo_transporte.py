import json
import math
import random
import pandas as pd
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)


import sys
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


df_transporte = pd.read_csv('Visualizacao_Transporte/arestas_bairros_transporte.csv', encoding='utf-8-sig')

print(f"Total de conexões: {len(df_transporte)}")
print(f"  Ônibus: {len(df_transporte[df_transporte['mode'] == 'onibus'])}")
print(f"  Metro: {len(df_transporte[df_transporte['mode'] == 'metro'])}")
print(f"  VLT: {len(df_transporte[df_transporte['mode'] == 'vlt'])}")


df_bairros = pd.read_csv('data/bairros_unique.csv', encoding='utf-8-sig', sep=';')
microrregiao_dict = {row['bairro']: row['microrregião'] for _, row in df_bairros.iterrows()}


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


microrregioes_agrupadas = {}
for bairro in grafo_base.vertices:
    micro = microrregiao_dict.get(bairro, 'N/A')

    
    for m in micro.split(' / '):
        if m not in microrregioes_agrupadas:
            microrregioes_agrupadas[m] = []
        microrregioes_agrupadas[m].append(bairro)

for micro in microrregioes_agrupadas:
    microrregioes_agrupadas[micro] = list(set(microrregioes_agrupadas[micro]))


posicoes_clusters = {
    '1.1': (1000, 1000), '1.2': (2500, 1000), '1.3': (4000, 1000),
    '2.1': (500, 2500), '2.2': (2000, 2500), '2.3': (3500, 2500),
    '3.1': (5000, 2500), '3.2': (1000, 4000), '3.3': (2500, 4000),
    '4.1': (4000, 4000), '4.2': (5500, 4000), '4.3': (500, 5500),
    '5.1': (2000, 5500), '5.2': (3500, 5500), '5.3': (5000, 5500),
    '6.1': (1500, 7000), '6.2': (3500, 7000), '6.3': (5000, 7000),
    'N/A': (3000, 1000)
}


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


bairros_lista = sorted(grafo_base.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}


nodes = []
for i, bairro in enumerate(bairros_lista):
    tem_transporte = bairro in bairros_com_transporte
    micro = microrregiao_dict.get(bairro, 'N/A')

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': micro,
        'tem_transporte': tem_transporte
    })


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


html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grafo de Transporte Público - Recife</title>
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
            height: 100vh;
        }}
        #sidebar {{
            width: 320px;
            background: white;
            padding: 20px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            overflow-y: auto;
            z-index: 10;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 10px;
            color: #333;
        }}
        h2 {{
            font-size: 18px;
            margin: 20px 0 10px 0;
            color: #555;
        }}
        #filtroMicro {{
            margin-bottom: 20px;
        }}
        #filtroMicro label {{
            display: block;
            margin: 10px 0 5px 0;
            font-weight: 600;
        }}
        #filtroMicro select, #filtroMicro input {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}
        #filtroMicro button {{
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            background: #4ecdc4;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }}
        #filtroMicro button:hover {{
            background: #45b7b0;
        }}
        #legenda {{
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
        }}
        .legenda-cor {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #333;
        }}
        .legenda-linha {{
            width: 40px;
            height: 3px;
            border-radius: 2px;
        }}
        #canvasContainer {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: white;
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
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 14px;
            pointer-events: none;
            display: none;
            z-index: 1000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .tooltip-title {{
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.3);
            padding-bottom: 6px;
        }}
        .tooltip-row {{
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }}
        .tooltip-label {{
            color: #ccc;
        }}
    </style>
</head>
<body>
    <div id="app">
        <div id="sidebar">
            <h1>Transporte Público</h1>
            <p style="color: #666; font-size: 14px; margin-bottom: 15px;">
                Conexões de ônibus, metrô e VLT entre bairros de Recife
            </p>
            <div id="filtroMicro">
                <label for="selectMicro"><strong>Filtrar por Microrregião:</strong></label>
                <select id="selectMicro">
                    <option value="todas">Todas as Microrregiões</option>
                </select>
                <label for="inputBusca"><strong>Buscar Bairro:</strong></label>
                <input type="text" id="inputBusca" placeholder="Digite o nome do bairro...">
                <button id="btnResetFiltro">Resetar Visualização</button>
            </div>
            <div id="legenda">
                <h2 style="margin-top: 0;">Legenda - Vértices</h2>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #4ecdc4;"></div>
                    <span>Com transporte público</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #95a5a6;"></div>
                    <span>Sem transporte público</span>
                </div>
                <h2>Legenda - Conexões</h2>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #f39c12;"></div>
                    <span>Ruas (adjacência)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #2ecc71;"></div>
                    <span>Linhas de ônibus</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #e91e63;"></div>
                    <span>Linhas de metrô</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-linha" style="background: #ff9800;"></div>
                    <span>Linhas de VLT</span>
                </div>
                <p style="margin-top: 15px; color: #666; font-size: 13px;">
                    <strong>Total:</strong><br>
                    {sum(1 for n in nodes if n['tem_transporte'])} bairros com transporte<br>
                    {len(edges_onibus)} conexões de ônibus<br>
                    {len(edges_metro)} conexões de metrô<br>
                    {len(edges_vlt)} conexões de VLT
                </p>
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

        // Popul ar dropdown de microrregiões
        const microregioesUnicas = [...new Set(nodes.map(n => n.microrregiao))].sort();
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
            draw();
        }});

        inputBusca.addEventListener('input', (e) => {{
            const termo = e.target.value.toLowerCase();
            if (termo.length >= 2) {{
                const encontrado = nodes.find(n => n.label.toLowerCase().includes(termo));
                if (encontrado) {{
                    bairroBuscado = encontrado.label;
                    bairroSelecionado = encontrado.label;
                }}
            }} else {{
                bairroBuscado = null;
            }}
            draw();
        }});

        function resizeCanvas() {{
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            draw();
        }}

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

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

        canvas.addEventListener('click', (e) => {{
            if (!isDragging) {{
                const rect = canvas.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left - offsetX) / scale;
                const mouseY = (e.clientY - rect.top - offsetY) / scale;

                for (const node of nodes) {{
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 18) {{
                        if (bairroSelecionado === node.label) {{
                            bairroSelecionado = null;
                        }} else {{
                            bairroSelecionado = node.label;
                        }}
                        draw();
                        break;
                    }}
                }}
            }}
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

        function handleMouseMove(e) {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;

            let found = false;
            for (const node of nodes) {{
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 18) {{
                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{node.label}}</div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Microrregião:</span>
                            <strong>${{node.microrregiao}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Transporte Público:</span>
                            <strong>${{node.tem_transporte ? 'Sim' : 'Não'}}</strong>
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

            // Filtrar nós por microrregião
            const nodesFiltrados = microSelecionada === 'todas'
                ? nodes
                : nodes.filter(n => n.microrregiao.includes(microSelecionada));

            const labelsFiltrados = new Set(nodesFiltrados.map(n => n.label));

            // Se há bairro selecionado, pegar vizinhos
            let vizinhosSet = null;
            let arestasVizinhos = new Set();

            if (bairroSelecionado) {{
                vizinhosSet = new Set([bairroSelecionado]);

                // Adicionar vizinhos por ruas
                edgesRuas.forEach(edge => {{
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

            // 1. Desenhar arestas de ruas
            edgesRuas.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#f39c12';
                    ctx.lineWidth = 2;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    ctx.strokeStyle = '#f39c12';
                    ctx.lineWidth = 1;
                    ctx.globalAlpha = 0.3;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
                ctx.globalAlpha = 1.0;
            }});

            // 2. Desenhar arestas de ônibus
            edgesOnibus.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#2ecc71';
                    ctx.lineWidth = 3;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    ctx.strokeStyle = '#2ecc71';
                    ctx.lineWidth = 2;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 3. Desenhar arestas de metrô
            edgesMetro.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#e91e63';
                    ctx.lineWidth = 4;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    ctx.strokeStyle = '#e91e63';
                    ctx.lineWidth = 3;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 4. Desenhar arestas de VLT
            edgesVlt.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#ff9800';
                    ctx.lineWidth = 4;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    ctx.strokeStyle = '#ff9800';
                    ctx.lineWidth = 3;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // 5. Desenhar nós
            nodesFiltrados.forEach(node => {{
                let shouldDim = false;

                if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                // Desenhar nó
                const cor = node.tem_transporte ? '#4ecdc4' : '#95a5a6';
                ctx.fillStyle = shouldDim ? '#d0d0d0' : cor;
                ctx.beginPath();
                ctx.arc(node.x, node.y, 18, 0, Math.PI * 2);
                ctx.fill();

                // Borda do nó
                ctx.strokeStyle = (vizinhosSet && node.label === bairroSelecionado) ? '#e74c3c' : '#333';
                ctx.lineWidth = (vizinhosSet && node.label === bairroSelecionado) ? 4 : 2;
                ctx.beginPath();
                ctx.arc(node.x, node.y, 18, 0, Math.PI * 2);
                ctx.stroke();

                // Labels
                if (!vizinhosSet || vizinhosSet.has(node.label)) {{
                    ctx.fillStyle = '#333';
                    ctx.font = 'bold 14px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y - 25);
                }}
            }});

            ctx.restore();
        }}

        draw();
    </script>
</body>
</html>'''

with open('out/parte1/grafo_transporte.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização gerada: out/parte1/grafo_transporte.html")
