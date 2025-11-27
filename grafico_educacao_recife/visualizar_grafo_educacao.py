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


df_educacao = pd.read_csv('grafico_educacao_recife/educacao_bairros.csv', encoding='utf-8-sig')

dados_bairro = {}
for _, row in df_educacao.iterrows():
    bairro = row['bairro']
    if bairro in grafo.vertices:
        dados_bairro[bairro] = {
            'taxa_analf': row['Taxa_Analfabetismo_%'],
            'taxa_alfab': row['Taxa_Alfabetizacao_%'],
            'faixa_analf': row['faixa_analfabetismo'],
            'unidades': row['n_unidades'],
            'matriculas': row['n_matriculas'],
            'populacao': row['Pop_Total'],
            'unidades_10k': row['unidades_por_10k_hab'],
            'matriculas_10k': row['matriculas_por_10k_hab'],
            'microrregiao': row['microrregião']
        }

df_micro = pd.read_csv('grafico_educacao_recife/educacao_microrregioes.csv')
dados_micro = {}
for _, row in df_micro.iterrows():
    micro = str(row['microrregião'])
    dados_micro[micro] = {
        'taxa_analf': row['Taxa_Analfabetismo_%'],
        'faixa_analf': row['faixa_analfabetismo']
    }

def mapear_categoria(faixa):
    if faixa == 'Quase perfeito (<2%)':
        return 'excelente'
    elif faixa == 'Melhor que a média nacional (2% a <6%)':
        return 'bom'
    elif faixa == 'Na média nacional (6% a 8%)':
        return 'regular'
        return 'critico'

random.seed(42)
microrregioes_agrupadas = {}
for bairro in grafo.vertices:
    if bairro in dados_bairro:
        micro = dados_bairro[bairro]['microrregiao']
        if micro not in microrregioes_agrupadas:
            microrregioes_agrupadas[micro] = []
        microrregioes_agrupadas[micro].append(bairro)

posicoes_clusters = {
    '1.1': (1000, 1000), '1.2': (2500, 1000), '1.3': (4000, 1000),
    '2.1': (500, 2500), '2.2': (2000, 2500), '2.3': (3500, 2500),
    '3.1': (5000, 2500), '3.2': (1000, 4000), '3.3': (2500, 4000),
    '4.1': (4000, 4000), '4.2': (5500, 4000), '4.3': (500, 5500),
    '5.1': (2000, 5500), '5.2': (3500, 5500), '5.3': (5000, 5500),
    '6.1': (1500, 7000), '6.2': (3500, 7000), '6.3': (5000, 7000)
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

bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

nodes = []
for i, bairro in enumerate(bairros_lista):
    dados = dados_bairro.get(bairro, {})
    micro = dados.get('microrregiao', 'N/A')

    taxa_analf = dados.get('taxa_analf', 0.0)
    taxa_alfab = dados.get('taxa_alfab', 0.0)
    faixa_analf = dados.get('faixa_analf', 'N/A')
    unidades = dados.get('unidades', 0)
    matriculas = dados.get('matriculas', 0)
    populacao = dados.get('populacao', 0)
    unidades_10k = dados.get('unidades_10k', 0.0)
    matriculas_10k = dados.get('matriculas_10k', 0.0)

    dados_m = dados_micro.get(str(micro), {})
    taxa_analf_micro = dados_m.get('taxa_analf', 0.0)
    faixa_analf_micro = dados_m.get('faixa_analf', 'N/A')


    categoria = mapear_categoria(faixa_analf)
    categoria_micro = mapear_categoria(faixa_analf_micro)

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': str(micro),
        'taxa_analfabetismo': round(taxa_analf, 2),
        'taxa_alfabetizacao': round(taxa_alfab, 2),
        'faixa_analfabetismo': faixa_analf,
        'taxa_analfabetismo_micro': round(taxa_analf_micro, 2),
        'faixa_analfabetismo_micro': faixa_analf_micro,
        'populacao': int(populacao),
        'unidades': int(unidades),
        'matriculas': int(matriculas),
        'unidades_por_10k': round(unidades_10k, 2),
        'matriculas_por_10k': round(matriculas_10k, 2),
        'categoria': categoria,
        'categoria_micro': categoria_micro
    })

pares_vistos = {}
edges = []

for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']

    if origem in bairro_to_id and destino in bairro_to_id:
        par = tuple(sorted([origem, destino]))
        if par not in pares_vistos:
            pares_vistos[par] = True
            edges.append({
                'from': bairro_to_id[origem],
                'to': bairro_to_id[destino],
                'label': aresta['logradouro'],
                'peso': aresta['peso']
            })

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

    dados_m = dados_micro.get(str(micro), {})
    taxa_analf_micro = dados_m.get('taxa_analf', 0.0)
    faixa_analf_micro = dados_m.get('faixa_analf', 'N/A')
    categoria_micro = mapear_categoria(faixa_analf_micro)

    micro_info[micro] = {
        'centro_x': centro_x,
        'centro_y': centro_y,
        'raio': raio_halo,
        'taxa_analfabetismo': round(taxa_analf_micro, 2),
        'categoria': categoria_micro,
        'bairros': bairros
    }

print(f"Grafo de Educação criado:")
print(f"  Vértices: {len(nodes)}")
print(f"  Arestas originais: {len(grafo.arestas)}")
print(f"  Arestas únicas: {len(edges)}")
print(f"  Microrregiões: {len(micro_info)}")
print(f"\nDistribuição por categoria (bairros):")
for cat in ['excelente', 'bom', 'regular', 'critico']:
    count = sum(1 for n in nodes if n['categoria'] == cat)
    print(f"  {cat.capitalize()}: {count}")
print(f"\nDistribuição por categoria (microrregiões):")
for cat in ['excelente', 'bom', 'regular', 'critico']:
    count = sum(1 for m in micro_info.values() if m['categoria'] == cat)
    print(f"  {cat.capitalize()}: {count}")

html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grafo de Educação - Analfabetismo por Bairro - Recife</title>
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
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legenda-cor {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 2px solid #333;
        }}
        #canvasContainer {{
            flex: 1;
            position: relative;
            overflow: hidden;
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
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 100;
            max-width: 300px;
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
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>Analfabetismo e Educação por Bairro - Recife</h1>
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
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #27ae60;"></div>
                    <span><strong>Quase perfeito</strong> (&lt;2%)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #3498db;"></div>
                    <span><strong>Bom</strong> (2-6%)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #f39c12;"></div>
                    <span><strong>Regular</strong> (6-8%)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #e74c3c;"></div>
                    <span><strong>Crítico</strong> (≥8%)</span>
                </div>
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
        const microregioes = {json.dumps(list(micro_info.values()))};

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

        // Popular dropdown de microrregiões
        const microregioesUnicas = [...new Set(nodes.map(n => n.microrregiao))].sort();
        microregioesUnicas.forEach(micro => {{
            const option = document.createElement('option');
            option.value = micro;
            const microInfo = microregioes.find(m => m.bairros && m.bairros.includes(nodes.find(n => n.microrregiao === micro)?.label));
            const taxa = microInfo ? microInfo.taxa_analfabetismo : 'N/A';
            option.textContent = `${{micro}} (Analfabetismo: ${{taxa}}%)`;
            selectMicro.appendChild(option);
        }});

        selectMicro.addEventListener('change', (e) => {{
            microSelecionada = e.target.value;
            bairroSelecionado = null;

            if (microSelecionada !== 'todas') {{
                const microInfo = microregioes.find(m => {{
                    const primeiroNo = nodes.find(n => n.microrregiao === microSelecionada);
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

        let hasMoved = false;

        canvas.addEventListener('mousedown', (e) => {{
            isDragging = true;
            hasMoved = false;
            startX = e.clientX - offsetX;
            startY = e.clientY - offsetY;
            canvas.classList.add('dragging');
        }});

        canvas.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                hasMoved = true;
                offsetX = e.clientX - startX;
                offsetY = e.clientY - startY;
                draw();
            }}
            handleMouseMove(e);
        }});

        canvas.addEventListener('mouseup', (e) => {{
            if (!hasMoved) {{
                const rect = canvas.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left - offsetX) / scale;
                const mouseY = (e.clientY - rect.top - offsetY) / scale;

                let clicouEmBairro = false;
                for (const node of nodes) {{
                    const raio = 18;
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

        function getCorCategoria(categoria) {{
            switch(categoria) {{
                case 'excelente': return '#27ae60';
                case 'bom': return '#3498db';
                case 'regular': return '#f39c12';
                case 'critico': return '#e74c3c';
                default: return '#999';
            }}
        }}

        function handleMouseMove(e) {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;

            let found = false;
            for (const node of nodes) {{
                const raio = 18;
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < raio) {{
                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{node.label}}</div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Taxa de Analfabetismo:</span>
                            <strong>${{node.taxa_analfabetismo}}%</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Taxa de Alfabetização:</span>
                            <strong>${{node.taxa_alfabetizacao}}%</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Faixa:</span> ${{node.faixa_analfabetismo}}
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Analfabetismo Micro:</span>
                            <strong>${{node.taxa_analfabetismo_micro}}%</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">População:</span> <strong>${{node.populacao.toLocaleString()}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Unidades Educacionais:</span> <strong>${{node.unidades}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Matrículas:</span> <strong>${{node.matriculas.toLocaleString()}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Unidades/10k hab:</span> <strong>${{node.unidades_por_10k}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Matrículas/10k hab:</span> <strong>${{node.matriculas_por_10k}}</strong>
                        </div>
                        <div class="tooltip-row">
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

            // Determinar vizinhos se há bairro selecionado
            let vizinhosSet = null;
            let arestasVizinhos = new Set();
            if (bairroSelecionado) {{
                vizinhosSet = new Set([bairroSelecionado]);
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
                : nodes.filter(n => n.microrregiao === microSelecionada);

            const labelsFiltrados = new Set(nodesFiltrados.map(n => n.label));

            // 1. Desenhar halos de microrregiões
            microregioes.forEach(micro => {{
                const temBairrosVisiveis = micro.bairros.some(b => labelsFiltrados.has(b));
                if (!temBairrosVisiveis && microSelecionada !== 'todas') return;

                const corMicro = getCorCategoria(micro.categoria);

                const gradient = ctx.createRadialGradient(
                    micro.centro_x, micro.centro_y, micro.raio * 0.3,
                    micro.centro_x, micro.centro_y, micro.raio
                );

                gradient.addColorStop(0, corMicro + '00');
                gradient.addColorStop(0.6, corMicro + '15');
                gradient.addColorStop(1, corMicro + '35');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(micro.centro_x, micro.centro_y, micro.raio, 0, Math.PI * 2);
                ctx.fill();

                ctx.strokeStyle = corMicro + '50';
                ctx.lineWidth = 2;
                ctx.setLineDash([10, 5]);
                ctx.beginPath();
                ctx.arc(micro.centro_x, micro.centro_y, micro.raio, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            }});

            // 2. Desenhar arestas
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

            // 3. Desenhar nós
            nodes.forEach(node => {{
                if (!labelsFiltrados.has(node.label)) return;

                const raioNo = 18;
                const raioHalo = node.taxa_analfabetismo > 8 ? 40 : 25;
                let shouldDim = false;

                if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                // Halo individual
                if (!shouldDim) {{
                    const corHalo = getCorCategoria(node.categoria);
                    const gradient = ctx.createRadialGradient(node.x, node.y, raioNo, node.x, node.y, raioHalo);
                    gradient.addColorStop(0, corHalo + '00');
                    gradient.addColorStop(0.5, corHalo + '30');
                    gradient.addColorStop(1, corHalo + '60');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, raioHalo, 0, Math.PI * 2);
                    ctx.fill();
                }}

                // Nó principal
                ctx.fillStyle = shouldDim ? '#d0d0d0' : getCorCategoria(node.categoria);
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.fill();

                // Borda
                ctx.strokeStyle = (vizinhosSet && node.label === bairroSelecionado) ? '#4ecdc4' : '#333';
                ctx.lineWidth = (vizinhosSet && node.label === bairroSelecionado) ? 4 : 2;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.stroke();

                // Label
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

with open('out/parte1/grafo_educacao.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização gerada: out/parte1/grafo_educacao.html")
