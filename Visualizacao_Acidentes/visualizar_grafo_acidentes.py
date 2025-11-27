import json
import math
import random
import pandas as pd
import os
import unicodedata
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

df_acidentes = pd.read_csv('Visualizacao_Acidentes/acidentes_bairros.csv', encoding='utf-8-sig')

dados_bairro = {}
for _, row in df_acidentes.iterrows():
    bairro = row['bairro_normalizado']
    dados_bairro[bairro] = {
        'total_acidentes': int(row['total_acidentes']),
        'com_vitima': int(row['com_vitima']),
        'sem_vitima': int(row['sem_vitima']),
        'perc_com_vitima': float(row['perc_com_vitima']),
        'microrregiao': row['microrregiao']
    }

df_micro = pd.read_csv('Visualizacao_Acidentes/acidentes_microrregioes.csv', encoding='utf-8-sig')

dados_micro = {}
for _, row in df_micro.iterrows():
    micro = str(row['microrregiao'])
    dados_micro[micro] = {
        'total_acidentes': int(row['total_acidentes']),
        'com_vitima': int(row['com_vitima']),
        'sem_vitima': int(row['sem_vitima']),
        'perc_com_vitima': float(row['perc_com_vitima'])
    }

with open('data/bairros_unique.csv', 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()[1:]
    microrregiao_dict = {}
    for linha in linhas:
        partes = linha.strip().split(';')
        bairro = partes[0]
        micro = partes[1]
        microrregiao_dict[bairro] = micro

random.seed(42)

microrregioes_agrupadas = {}
for bairro in grafo.vertices:
    micro = microrregiao_dict.get(bairro, 'N/A')
    for m in micro.split(' / '):
        if m not in microrregioes_agrupadas:
            microrregioes_agrupadas[m] = []
        microrregioes_agrupadas[m].append(bairro)

for micro in microrregioes_agrupadas:
    microrregioes_agrupadas[micro] = list(set(microrregioes_agrupadas[micro]))

posicoes_clusters = {
    '1.1': (1000, 1000), '1.2': (2200, 1000), '1.3': (3400, 1000),
    '2.1': (600, 2200), '2.2': (1800, 2200), '2.3': (3000, 2200),
    '3.1': (4200, 2200), '3.2': (1000, 3400), '3.3': (2200, 3400),
    '4.1': (3400, 3400), '4.2': (4600, 3400), '4.3': (600, 4600),
    '5.1': (1800, 4600), '5.2': (3000, 4600), '5.3': (4200, 4600),
    '6.1': (1400, 5800), '6.2': (3000, 5800), '6.3': (4200, 5800),
    'N/A': (2600, 1000)
}

posicoes = {}
for micro, bairros_micro in microrregioes_agrupadas.items():
    centro_cluster = posicoes_clusters.get(micro, (3000, 3000))
    n_bairros = len(bairros_micro)

    if n_bairros == 1:
        posicoes[bairros_micro[0]] = {'x': centro_cluster[0], 'y': centro_cluster[1]}
    else:
        raio_cluster = 120 + (n_bairros * 15)
        for i, bairro in enumerate(bairros_micro):
            angulo = (2 * math.pi * i) / n_bairros
            jitter_x = random.uniform(-30, 30)
            jitter_y = random.uniform(-30, 30)
            x = centro_cluster[0] + raio_cluster * math.cos(angulo) + jitter_x
            y = centro_cluster[1] + raio_cluster * math.sin(angulo) + jitter_y
            posicoes[bairro] = {'x': x, 'y': y}

bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

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
        'POCO DA PANELA': 'Poço'
    }

    if texto in mapeamentos_especiais:
        texto = mapeamentos_especiais[texto]

    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    normalizado = ' '.join(sem_acento.split())
    normalizado = normalizado.replace('Terezinha', 'Teresinha')
    return normalizado.title()


nodes = []
for i, bairro in enumerate(bairros_lista):
    bairro_norm = normalizar_nome(bairro)
    micro = microrregiao_dict.get(bairro, 'N/A')
    dados = dados_bairro.get(bairro_norm, {
        'total_acidentes': 0,
        'com_vitima': 0,
        'sem_vitima': 0,
        'perc_com_vitima': 0,
        'microrregiao': micro
    })

    micro_principal = micro.split(' / ')[0].strip() if ' / ' in micro else micro
    dados_m = dados_micro.get(micro_principal, {
        'total_acidentes': 0,
        'com_vitima': 0,
        'sem_vitima': 0,
        'perc_com_vitima': 0
    })

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': micro,
        'total_acidentes': dados['total_acidentes'],
        'com_vitima': dados['com_vitima'],
        'sem_vitima': dados['sem_vitima'],
        'perc_com_vitima': dados['perc_com_vitima'],
        'total_acidentes_micro': dados_m['total_acidentes'],
        'perc_com_vitima_micro': dados_m['perc_com_vitima']
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

print(f"Grafo de Acidentes criado:")
print(f"  Vértices: {len(nodes)}")
print(f"  Arestas únicas: {len(edges)}")


acidentes_counts = [n['total_acidentes'] for n in nodes if n['total_acidentes'] > 0]
if acidentes_counts:
    print(f"\nAcidentes por bairro:")
    print(f"  Mín: {min(acidentes_counts)}")
    print(f"  Máx: {max(acidentes_counts)}")
    print(f"  Média: {sum(acidentes_counts) / len(acidentes_counts):.0f}")

print("\nTop 5 bairros com mais acidentes:")
top_bairros = sorted(nodes, key=lambda x: x['total_acidentes'], reverse=True)[:5]
for b in top_bairros:
    print(f"  {b['label']}: {b['total_acidentes']} acidentes ({b['perc_com_vitima']:.1f}% com vítima)")

html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mapa de Calor - Acidentes de Trânsito - Recife 2024</title>
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
            border-color: #e74c3c;
        }}
        input[type="text"] {{
            min-width: 250px;
        }}
        button {{
            padding: 8px 16px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        button:hover {{
            background: #c0392b;
        }}
        #legenda {{
            display: flex;
            gap: 20px;
            margin-top: 10px;
            font-size: 13px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legenda-gradiente {{
            width: 250px;
            height: 20px;
            background: linear-gradient(to right,
                rgba(200, 220, 255, 0.4),
                rgba(100, 150, 255, 0.5),
                rgba(50, 200, 100, 0.6),
                rgba(255, 255, 0, 0.7),
                rgba(255, 150, 0, 0.8),
                rgba(200, 0, 0, 0.9));
            border-radius: 4px;
            border: 1px solid #999;
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
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>🚗 Mapa de Calor - Acidentes de Trânsito - Recife 2024</h1>
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
                <span style="font-weight: bold; margin-right: 10px;">Intensidade do Mapa de Calor:</span>
                <div class="legenda-gradiente"></div>
                <span style="color: #666;">Menos acidentes → Mais acidentes</span>
                <span style="margin-left: 20px; color: #666;">
                    | Total: {sum(n['total_acidentes'] for n in nodes):,} acidentes em 2024
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
            const microNodes = nodes.filter(n => n.microrregiao === micro);
            const totalAcidentes = microNodes.reduce((sum, n) => sum + n.total_acidentes, 0);
            option.textContent = `${{micro}} (${{totalAcidentes}} acidentes)`;
            selectMicro.appendChild(option);
        }});

        selectMicro.addEventListener('change', (e) => {{
            microSelecionada = e.target.value;
            bairroSelecionado = null;
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

        function getCorIntensidade(totalAcidentes) {{
            // Escala por faixas absolutas de acidentes
            if (totalAcidentes === 0) {{
                return 'rgba(220, 220, 220, 0.1)'; // Cinza bem claro
            }} else if (totalAcidentes <= 9) {{
                // 1-9 acidentes: azul bem claro
                const p = totalAcidentes / 9;
                return `rgba(${{200}}, ${{220}}, ${{255}}, ${{0.3 + p * 0.1}})`;
            }} else if (totalAcidentes <= 20) {{
                // 10-20 acidentes: azul médio
                const p = (totalAcidentes - 10) / 10;
                return `rgba(${{100 + p * 100}}, ${{150 + p * 70}}, ${{255}}, ${{0.4 + p * 0.1}})`;
            }} else if (totalAcidentes <= 40) {{
                // 21-40 acidentes: verde
                const p = (totalAcidentes - 21) / 19;
                return `rgba(${{50 + p * 150}}, ${{200 + p * 55}}, ${{100 - p * 100}}, ${{0.5 + p * 0.1}})`;
            }} else if (totalAcidentes <= 90) {{
                // 41-90 acidentes: amarelo
                const p = (totalAcidentes - 41) / 49;
                return `rgba(${{200 + p * 55}}, ${{255}}, ${{0}}, ${{0.6 + p * 0.1}})`;
            }} else if (totalAcidentes <= 190) {{
                // 91-190 acidentes: laranja
                const p = (totalAcidentes - 91) / 99;
                return `rgba(${{255}}, ${{200 - p * 50}}, ${{0}}, ${{0.7 + p * 0.1}})`;
            }} else {{
                // 191-549 acidentes: vermelho intenso
                const p = Math.min((totalAcidentes - 191) / 358, 1.0);
                return `rgba(${{255 - p * 55}}, ${{Math.floor(150 - p * 150)}}, ${{0}}, ${{0.8 + p * 0.1}})`;
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
                            <span class="tooltip-label">Total de Acidentes:</span>
                            <strong>${{node.total_acidentes}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Com Vítima:</span>
                            <strong>${{node.com_vitima}}</strong> (${{node.perc_com_vitima.toFixed(1)}}%)
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Sem Vítima:</span>
                            <strong>${{node.sem_vitima}}</strong>
                        </div>
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

            // 1. DESENHAR MAPA DE CALOR (atrás de tudo)
            nodesFiltrados.forEach(node => {{
                if (node.total_acidentes === 0) return;

                const corCalor = getCorIntensidade(node.total_acidentes);

                // Raio bem maior para criar mapa de calor contínuo com sobreposição
                const raioCalor = 500 + (node.total_acidentes / 549) * 300;

                const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, raioCalor);
                gradient.addColorStop(0, corCalor);
                gradient.addColorStop(0.5, corCalor.replace(/[\d.]+\)$/, '0.3)'));
                gradient.addColorStop(0.85, corCalor.replace(/[\d.]+\)$/, '0.05)'));
                gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioCalor, 0, Math.PI * 2);
                ctx.fill();
            }});

            // 2. Desenhar arestas
            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#e74c3c';
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
                let shouldDim = false;

                if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                // Desenhar nó principal
                ctx.fillStyle = shouldDim ? '#d0d0d0' : '#333';
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.fill();

                // Borda do nó
                ctx.strokeStyle = (vizinhosSet && node.label === bairroSelecionado) ? '#e74c3c' : '#fff';
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

with open('out/parte1/grafo_acidentes.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização gerada: out/parte1/grafo_acidentes.html")
