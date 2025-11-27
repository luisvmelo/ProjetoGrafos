import json
import math
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.graphs.graph import construir_grafo_bairros
from src.graphs.algorithms import dijkstra

project_root = os.path.join(os.path.dirname(__file__), '../..')
data_dir = os.path.join(project_root, 'data')
out_dir = os.path.join(project_root, 'out/parte1')

grafo = construir_grafo_bairros()

with open(os.path.join(out_dir, 'ego_bairro.csv'), 'r', encoding='utf-8') as f:
    linhas = f.readlines()[1:]
    graus_dict = {}
    densidade_ego_dict = {}
    for linha in linhas:
        partes = linha.strip().split(',')
        bairro = partes[0]
        grau = int(partes[1])
        densidade_ego = float(partes[4])
        graus_dict[bairro] = grau
        densidade_ego_dict[bairro] = densidade_ego

with open(os.path.join(data_dir, 'bairros_unique.csv'), 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()[1:]
    microrregiao_dict = {}
    for linha in linhas:
        partes = linha.strip().split(';')
        bairro = partes[0]
        micro = partes[1]
        microrregiao_dict[bairro] = micro

with open(os.path.join(out_dir, 'percurso_nova_descoberta_setubal.json'), 'r', encoding='utf-8') as f:
    percurso = json.load(f)
    caminho_destaque = set(percurso['caminho'])
    arestas_destaque = set()
    for i in range(len(percurso['caminho']) - 1):
        par = tuple(sorted([percurso['caminho'][i], percurso['caminho'][i+1]]))
        arestas_destaque.add(par)

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

cores_microrregioes = {
    '1.1': '#e74c3c', '1.2': '#e67e22', '1.3': '#f39c12',
    '2.1': '#f1c40f', '2.2': '#2ecc71', '2.3': '#27ae60',
    '3.1': '#16a085', '3.2': '#1abc9c', '3.3': '#3498db',
    '4.1': '#2980b9', '4.2': '#9b59b6', '4.3': '#8e44ad',
    '5.1': '#e91e63', '5.2': '#ff5722', '5.3': '#795548',
    '6.1': '#607d8b', '6.2': '#34495e', '6.3': '#95a5a6',
    'N/A': '#bdc3c7'
}

bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

nodes = []
for i, bairro in enumerate(bairros_lista):
    grau = graus_dict.get(bairro, 0)
    densidade_ego = densidade_ego_dict.get(bairro, 0.0)
    micro = microrregiao_dict.get(bairro, 'N/A')
    eh_destaque = bairro in caminho_destaque
    micros_lista = [m.strip() for m in micro.split('/')]
    cores = [cores_microrregioes.get(m, '#bdc3c7') for m in micros_lista]

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes[bairro]['x'],
        'y': posicoes[bairro]['y'],
        'grau': grau,
        'microrregiao': micro,
        'densidade_ego': round(densidade_ego, 4),
        'destaque': eh_destaque,
        'cores': cores
    })

pares_contador = {}
for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    par = tuple(sorted([origem, destino]))
    if par not in pares_contador:
        pares_contador[par] = 0
    else:
        pares_contador[par] += 1

edges = []
pares_atual = {}
for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    logradouro = aresta['logradouro']
    peso = aresta['peso']
    par = tuple(sorted([origem, destino]))
    eh_destaque = par in arestas_destaque

    if par not in pares_atual:
        pares_atual[par] = 0

    total_arestas_par = pares_contador[par] + 1
    indice_aresta = pares_atual[par]
    pares_atual[par] += 1

    edges.append({
        'from': bairro_to_id[origem],
        'to': bairro_to_id[destino],
        'label': logradouro,
        'peso': peso,
        'destaque': eh_destaque,
        'curva_indice': indice_aresta,
        'curva_total': total_arestas_par
    })

html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grafo Interativo - Bairros de Recife</title>
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
        #controls {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .search-group {{
            display: flex;
            gap: 5px;
            align-items: center;
        }}
        input[type="text"] {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            width: 200px;
        }}
        input[type="text"]:focus {{
            outline: none;
            border-color: #4ecdc4;
        }}
        button {{
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background: #4ecdc4;
            color: white;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        button:hover {{
            background: #3db8af;
        }}
        #pathResult {{
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 13px;
            display: none;
        }}
        #pathResult h3 {{
            margin: 0 0 8px 0;
            font-size: 14px;
        }}
        #pathResult ul {{
            margin: 5px 0;
            padding-left: 20px;
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
            position: absolute;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 100;
            max-width: 250px;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>Grafo Interativo - Bairros de Recife</h1>
            <div id="controls">
                <div class="search-group">
                    <input type="text" id="origemBox" placeholder="Bairro origem">
                    <span>→</span>
                    <input type="text" id="destinoBox" placeholder="Bairro destino">
                    <button id="btnCalcular">Calcular Caminho</button>
                </div>
                <button id="btnDestaque">Realçar Nova Descoberta → Boa Viagem</button>
                <button id="btnReset">Resetar</button>
            </div>
            <div id="pathResult"></div>
        </div>
        <div id="canvasContainer">
            <canvas id="canvas"></canvas>
            <div id="tooltip"></div>
        </div>
    </div>
    <script>
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};
        const bairros = {json.dumps(bairros_lista)};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        const origemBox = document.getElementById('origemBox');
        const destinoBox = document.getElementById('destinoBox');
        const btnCalcular = document.getElementById('btnCalcular');
        const btnDestaque = document.getElementById('btnDestaque');
        const btnReset = document.getElementById('btnReset');
        const pathResult = document.getElementById('pathResult');

        let offsetX = 0;
        let offsetY = 0;
        let scale = 1.0;
        let isDragging = false;
        let startX, startY;
        let destaqueAtivo = false;
        let caminhoCalculado = null;
        let bairroSelecionado = null;

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
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 40) {{
                        if (bairroSelecionado === node.label) {{
                            bairroSelecionado = null;
                        }} else {{
                            bairroSelecionado = node.label;
                            caminhoCalculado = null;
                            destaqueAtivo = false;
                            pathResult.style.display = 'none';
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

        function handleMouseMove(e) {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;

            let found = false;
            for (const node of nodes) {{
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 40) {{
                    tooltip.innerHTML = `<strong>${{node.label}}</strong><br>
                        Grau: ${{node.grau}}<br>
                        Microrregião: ${{node.microrregiao}}<br>
                        Densidade Ego: ${{node.densidade_ego}}`;
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

        btnCalcular.addEventListener('click', () => {{
            const origem = origemBox.value.trim();
            const destino = destinoBox.value.trim();

            if (!origem || !destino) {{
                alert('Digite ambos os bairros');
                return;
            }}

            const origemEncontrada = bairros.find(b => b.toLowerCase() === origem.toLowerCase());
            const destinoEncontrado = bairros.find(b => b.toLowerCase() === destino.toLowerCase());

            if (!origemEncontrada || !destinoEncontrado) {{
                alert('Bairro não encontrado');
                return;
            }}

            const resultado = calcularCaminhoLocal(origemEncontrada, destinoEncontrado);
            if (resultado) {{
                caminhoCalculado = resultado;
                destaqueAtivo = false;
                mostrarCaminho(resultado);
                draw();
            }} else {{
                alert('Caminho não encontrado');
            }}
        }});

        function calcularCaminhoLocal(origem, destino) {{
            const grafo = {{}};
            nodes.forEach(n => grafo[n.label] = []);
            edges.forEach(e => {{
                const from = nodes[e.from].label;
                const to = nodes[e.to].label;
                grafo[from].push({{destino: to, via: e.label, peso: e.peso}});
                grafo[to].push({{destino: from, via: e.label, peso: e.peso}});
            }});

            const distancias = {{}};
            const anteriores = {{}};
            const visitados = new Set();

            bairros.forEach(b => {{
                distancias[b] = Infinity;
                anteriores[b] = null;
            }});
            distancias[origem] = 0;

            while (visitados.size < bairros.length) {{
                let atual = null;
                let menorDist = Infinity;

                for (const v of bairros) {{
                    if (!visitados.has(v) && distancias[v] < menorDist) {{
                        menorDist = distancias[v];
                        atual = v;
                    }}
                }}

                if (!atual || distancias[atual] === Infinity) break;
                visitados.add(atual);
                if (atual === destino) break;

                for (const viz of grafo[atual]) {{
                    if (!visitados.has(viz.destino)) {{
                        const novaDist = distancias[atual] + viz.peso;
                        if (novaDist < distancias[viz.destino]) {{
                            distancias[viz.destino] = novaDist;
                            anteriores[viz.destino] = {{bairro: atual, via: viz.via}};
                        }}
                    }}
                }}
            }}

            if (distancias[destino] === Infinity) return null;

            const caminho = [];
            const vias = [];
            let atual = destino;

            while (atual) {{
                caminho.unshift(atual);
                const ant = anteriores[atual];
                if (ant) {{
                    vias.unshift(ant.via);
                    atual = ant.bairro;
                }} else {{
                    atual = null;
                }}
            }}

            return {{
                caminho: caminho,
                vias: vias,
                custo: distancias[destino].toFixed(2)
            }};
        }}

        function mostrarCaminho(data) {{
            let html = `<h3>Caminho encontrado (custo: ${{data.custo}}m)</h3><ul>`;
            for (let i = 0; i < data.caminho.length - 1; i++) {{
                html += `<li>${{data.caminho[i]}} --[${{data.vias[i]}}]--> ${{data.caminho[i+1]}}</li>`;
            }}
            html += '</ul>';
            pathResult.innerHTML = html;
            pathResult.style.display = 'block';
        }}

        btnDestaque.addEventListener('click', () => {{
            destaqueAtivo = !destaqueAtivo;
            caminhoCalculado = null;

            if (destaqueAtivo) {{
                const caminhoND = {json.dumps(percurso['caminho'])};
                const viasND = {json.dumps(percurso['vias'])};
                const custoND = {json.dumps(percurso['custo'])};

                const grafo = {{}};
                nodes.forEach(n => grafo[n.label] = []);
                edges.forEach(e => {{
                    const from = nodes[e.from].label;
                    const to = nodes[e.to].label;
                    grafo[from].push({{destino: to, via: e.label, peso: e.peso}});
                    grafo[to].push({{destino: from, via: e.label, peso: e.peso}});
                }});

                let html = `<h3>Caminho Nova Descoberta → Boa Viagem (Setúbal)</h3>`;
                html += `<p><strong>Distância total: ${{custoND}}m</strong></p>`;
                html += `<ul>`;

                for (let i = 0; i < caminhoND.length - 1; i++) {{
                    const bairroAtual = caminhoND[i];
                    const proximoBairro = caminhoND[i + 1];
                    const via = viasND[i];

                    let pesoVia = 0;
                    const vizinhos = grafo[bairroAtual];
                    for (const viz of vizinhos) {{
                        if (viz.destino === proximoBairro && viz.via === via) {{
                            pesoVia = viz.peso;
                            break;
                        }}
                    }}

                    html += `<li>${{bairroAtual}} --[${{via}}]--> ${{proximoBairro}} (${{pesoVia.toFixed(2)}}m)</li>`;
                }}

                html += '</ul>';
                pathResult.innerHTML = html;
                pathResult.style.display = 'block';
            }} else {{
                pathResult.style.display = 'none';
            }}

            btnDestaque.textContent = destaqueAtivo ? 'Ocultar Caminho' : 'Realçar Nova Descoberta → Boa Viagem';
            draw();
        }});

        btnReset.addEventListener('click', () => {{
            scale = 1.0;
            offsetX = canvas.width / 2 - 3000;
            offsetY = canvas.height / 2 - 4000;
            destaqueAtivo = false;
            caminhoCalculado = null;
            bairroSelecionado = null;
            origemBox.value = '';
            destinoBox.value = '';
            pathResult.style.display = 'none';
            draw();
        }});

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            ctx.translate(offsetX, offsetY);
            ctx.scale(scale, scale);

            const caminhoAtivo = caminhoCalculado || (destaqueAtivo ? {{caminho: {json.dumps(percurso['caminho'])}, vias: {json.dumps(percurso['vias'])}}} : null);
            const caminhoSet = caminhoAtivo ? new Set(caminhoAtivo.caminho) : null;
            const viasSet = new Set();

            if (caminhoAtivo && caminhoAtivo.vias) {{
                for (let i = 0; i < caminhoAtivo.vias.length; i++) {{
                    const bairro1 = caminhoAtivo.caminho[i];
                    const bairro2 = caminhoAtivo.caminho[i + 1];
                    const via = caminhoAtivo.vias[i];
                    const chave = [bairro1, bairro2].sort().join('|') + '::' + via;
                    viasSet.add(chave);
                }}
            }}

            let vizinhosSet = null;
            let arestasVizinhos = new Set();

            if (bairroSelecionado && !caminhoSet) {{
                vizinhosSet = new Set();
                vizinhosSet.add(bairroSelecionado);

                edges.forEach(edge => {{
                    const fromNode = nodes[edge.from];
                    const toNode = nodes[edge.to];

                    if (fromNode.label === bairroSelecionado) {{
                        vizinhosSet.add(toNode.label);
                        const chave = [fromNode.label, toNode.label].sort().join('|') + '::' + edge.label;
                        arestasVizinhos.add(chave);
                    }} else if (toNode.label === bairroSelecionado) {{
                        vizinhosSet.add(fromNode.label);
                        const chave = [fromNode.label, toNode.label].sort().join('|') + '::' + edge.label;
                        arestasVizinhos.add(chave);
                    }}
                }});
            }}

            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];
                const par = [fromNode.label, toNode.label].sort().join('|');
                const chaveCompleta = par + '::' + edge.label;

                if (caminhoSet && viasSet.has(chaveCompleta)) {{
                    ctx.strokeStyle = '#ff6b6b';
                    ctx.lineWidth = 4;
                }} else if (caminhoSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else if (vizinhosSet && arestasVizinhos.has(chaveCompleta)) {{
                    ctx.strokeStyle = '#4ecdc4';
                    ctx.lineWidth = 3;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    ctx.strokeStyle = '#000';
                    ctx.lineWidth = 1;
                }}

                ctx.beginPath();

                if (edge.curva_total === 1) {{
                    ctx.moveTo(fromNode.x, fromNode.y);
                    ctx.lineTo(toNode.x, toNode.y);
                }} else {{
                    const dx = toNode.x - fromNode.x;
                    const dy = toNode.y - fromNode.y;
                    const distancia = Math.sqrt(dx * dx + dy * dy);

                    const offsetMax = Math.min(distancia * 0.3, 150);
                    const step = offsetMax / (edge.curva_total - 1);
                    const offset = (edge.curva_indice - (edge.curva_total - 1) / 2) * step;

                    const perpX = -dy / distancia;
                    const perpY = dx / distancia;

                    const midX = (fromNode.x + toNode.x) / 2 + perpX * offset;
                    const midY = (fromNode.y + toNode.y) / 2 + perpY * offset;

                    ctx.moveTo(fromNode.x, fromNode.y);
                    ctx.quadraticCurveTo(midX, midY, toNode.x, toNode.y);
                }}

                ctx.stroke();
            }});

            nodes.forEach(node => {{
                let raio = 18;
                let shouldDim = false;

                if (caminhoSet && !caminhoSet.has(node.label)) {{
                    shouldDim = true;
                }} else if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                if (vizinhosSet && node.label === bairroSelecionado) {{
                    raio = 24;
                }}

                if (node.cores.length === 1) {{
                    ctx.fillStyle = shouldDim ? '#d0d0d0' : node.cores[0];
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, raio, 0, Math.PI * 2);
                    ctx.fill();
                }} else {{
                    for (let i = 0; i < node.cores.length; i++) {{
                        const startAngle = (i * 2 * Math.PI) / node.cores.length;
                        const endAngle = ((i + 1) * 2 * Math.PI) / node.cores.length;
                        ctx.fillStyle = shouldDim ? '#d0d0d0' : node.cores[i];
                        ctx.beginPath();
                        ctx.arc(node.x, node.y, raio, startAngle, endAngle);
                        ctx.lineTo(node.x, node.y);
                        ctx.fill();
                    }}
                }}

                ctx.strokeStyle = (vizinhosSet && node.label === bairroSelecionado) ? '#4ecdc4' : '#333';
                ctx.lineWidth = (vizinhosSet && node.label === bairroSelecionado) ? 4 : 2.5;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raio, 0, Math.PI * 2);
                ctx.stroke();

                if (scale > 0.4) {{
                    ctx.fillStyle = '#333';
                    ctx.font = 'bold 16px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y + raio + 20);
                }}
            }});

            ctx.restore();
        }}

        draw();
    </script>
</body>
</html>'''

with open(os.path.join(out_dir, 'grafo_interativo.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Visualizacao interativa gerada: out/parte1/grafo_interativo.html')
print(f'Vertices: {len(nodes)}')
print(f'Arestas: {len(edges)}')
