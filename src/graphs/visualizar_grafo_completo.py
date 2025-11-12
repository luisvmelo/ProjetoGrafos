import json
from graph import construir_grafo_bairros

grafo = construir_grafo_bairros()

with open('out/ego_bairro.csv', 'r', encoding='utf-8') as f:
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

with open('data/bairros_unique.csv', 'r', encoding='utf-8-sig') as f:
    linhas = f.readlines()[1:]
    microrregiao_dict = {}
    for linha in linhas:
        partes = linha.strip().split(';')
        bairro = partes[0]
        micro = partes[1]
        microrregiao_dict[bairro] = micro

with open('out/percurso_nova_descoberta_setubal.json', 'r', encoding='utf-8') as f:
    percurso = json.load(f)
    caminho_destaque = set(percurso['caminho'])
    arestas_destaque = set()
    for i in range(len(percurso['caminho']) - 1):
        par = tuple(sorted([percurso['caminho'][i], percurso['caminho'][i+1]]))
        arestas_destaque.add(par)

import math
import random

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
    '1.1': (1000, 1000),
    '1.2': (2500, 1000),
    '1.3': (4000, 1000),
    '2.1': (500, 2500),
    '2.2': (2000, 2500),
    '2.3': (3500, 2500),
    '3.1': (5000, 2500),
    '3.2': (1000, 4000),
    '3.3': (2500, 4000),
    '4.1': (4000, 4000),
    '4.2': (5500, 4000),
    '4.3': (500, 5500),
    '5.1': (2000, 5500),
    '5.2': (3500, 5500),
    '5.3': (5000, 5500),
    '6.1': (1500, 7000),
    '6.2': (3500, 7000),
    '6.3': (5000, 7000),
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

bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

nodes = []
for i, bairro in enumerate(bairros_lista):
    grau = graus_dict.get(bairro, 0)
    densidade_ego = densidade_ego_dict.get(bairro, 0.0)
    micro = microrregiao_dict.get(bairro, 'N/A')

    eh_destaque = bairro in caminho_destaque

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes[bairro]['x'],
        'y': posicoes[bairro]['y'],
        'grau': grau,
        'microrregiao': micro,
        'densidade_ego': round(densidade_ego, 4),
        'destaque': eh_destaque
    })

edges = []
for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    logradouro = aresta['logradouro']
    peso = aresta['peso']

    par = tuple(sorted([origem, destino]))
    eh_destaque = par in arestas_destaque

    edges.append({
        'from': bairro_to_id[origem],
        'to': bairro_to_id[destino],
        'label': logradouro,
        'peso': peso,
        'destaque': eh_destaque
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
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        #searchBox {{
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            width: 300px;
        }}
        #searchBox:focus {{
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
        button:active {{
            background: #2da39a;
        }}
        #info {{
            font-size: 12px;
            color: #666;
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
        #legend {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            font-size: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid #333;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>Grafo Interativo - Bairros de Recife</h1>
            <div id="controls">
                <input type="text" id="searchBox" placeholder="Digite o nome de um bairro...">
                <button id="btnDestaque">Realçar Nova Descoberta → Boa Viagem</button>
                <button id="btnReset">Resetar Visualização</button>
                <span id="info">94 bairros, 944 vias</span>
            </div>
        </div>
        <div id="canvasContainer">
            <canvas id="canvas"></canvas>
            <div id="tooltip"></div>
            <div id="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #4ecdc4;"></div>
                    <span>Bairro normal</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ff6b6b;"></div>
                    <span>Caminho destacado</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffd93d;"></div>
                    <span>Busca ativa</span>
                </div>
            </div>
        </div>
    </div>
    <script>
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        const searchBox = document.getElementById('searchBox');
        const btnDestaque = document.getElementById('btnDestaque');
        const btnReset = document.getElementById('btnReset');

        let offsetX = 0;
        let offsetY = 0;
        let scale = 1.0;
        let isDragging = false;
        let startX, startY;
        let destaqueAtivo = false;
        let buscaAtiva = null;

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
            }} else {{
                handleMouseMove(e);
            }}
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

                if (dist < 30) {{
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

        searchBox.addEventListener('input', (e) => {{
            const termo = e.target.value.toLowerCase().trim();
            if (termo === '') {{
                buscaAtiva = null;
            }} else {{
                const encontrado = nodes.find(n => n.label.toLowerCase().includes(termo));
                if (encontrado) {{
                    buscaAtiva = encontrado.id;
                    const targetX = canvas.width / 2 - encontrado.x * scale;
                    const targetY = canvas.height / 2 - encontrado.y * scale;
                    offsetX = targetX;
                    offsetY = targetY;
                }} else {{
                    buscaAtiva = null;
                }}
            }}
            draw();
        }});

        btnDestaque.addEventListener('click', () => {{
            destaqueAtivo = !destaqueAtivo;
            btnDestaque.textContent = destaqueAtivo ?
                'Ocultar Caminho Destacado' :
                'Realçar Nova Descoberta → Boa Viagem';
            draw();
        }});

        btnReset.addEventListener('click', () => {{
            scale = 1.0;
            offsetX = canvas.width / 2 - 3000;
            offsetY = canvas.height / 2 - 4000;
            destaqueAtivo = false;
            buscaAtiva = null;
            searchBox.value = '';
            btnDestaque.textContent = 'Realçar Nova Descoberta → Boa Viagem';
            draw();
        }});

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.save();
            ctx.translate(offsetX, offsetY);
            ctx.scale(scale, scale);

            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (destaqueAtivo && !edge.destaque) {{
                    ctx.strokeStyle = '#e0e0e0';
                    ctx.lineWidth = 0.5;
                }} else if (edge.destaque && destaqueAtivo) {{
                    ctx.strokeStyle = '#ff6b6b';
                    ctx.lineWidth = 3;
                }} else {{
                    ctx.strokeStyle = '#ccc';
                    ctx.lineWidth = 1;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            nodes.forEach(node => {{
                let cor = '#4ecdc4';
                let raio = 12;

                if (node.id === buscaAtiva) {{
                    cor = '#ffd93d';
                    raio = 18;
                }} else if (destaqueAtivo && node.destaque) {{
                    cor = '#ff6b6b';
                    raio = 15;
                }} else if (destaqueAtivo && !node.destaque) {{
                    cor = '#d0d0d0';
                    raio = 10;
                }}

                ctx.fillStyle = cor;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raio, 0, Math.PI * 2);
                ctx.fill();

                ctx.strokeStyle = '#333';
                ctx.lineWidth = 2;
                ctx.stroke();

                if (scale > 0.4) {{
                    ctx.fillStyle = '#333';
                    ctx.font = 'bold 14px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y + raio + 18);
                }}
            }});

            ctx.restore();
        }}

        draw();
    </script>
</body>
</html>'''

with open('out/grafo_interativo.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Visualizacao interativa gerada: out/grafo_interativo.html')
print(f'Vertices: {len(nodes)}')
print(f'Arestas: {len(edges)}')
