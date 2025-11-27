import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.graphs.graph import construir_grafo_bairros
from src.graphs.algorithms import dijkstra

project_root = os.path.join(os.path.dirname(__file__), '../..')
out_dir = os.path.join(project_root, 'out/parte1')
os.makedirs(out_dir, exist_ok=True)

grafo = construir_grafo_bairros()

origem = 'Nova Descoberta'
destino = 'Boa Viagem'

caminho, custo, vias = dijkstra(grafo, origem, destino)

caminho_set = set(caminho)
arestas_caminho = set()
for i in range(len(caminho) - 1):
    par = tuple(sorted([caminho[i], caminho[i+1]]))
    arestas_caminho.add(par)

nodes = []
edges = []

posicoes = {}
for i, bairro in enumerate(caminho):
    posicoes[bairro] = {
        'x': i * 150,
        'y': 200
    }

node_id = 0
bairro_to_id = {}

for bairro in caminho:
    nodes.append({
        'id': node_id,
        'label': bairro,
        'x': posicoes[bairro]['x'],
        'y': posicoes[bairro]['y'],
        'color': '#ff6b6b' if bairro == origem or bairro == destino else '#4ecdc4'
    })
    bairro_to_id[bairro] = node_id
    node_id += 1

for i in range(len(caminho) - 1):
    edges.append({
        'from': bairro_to_id[caminho[i]],
        'to': bairro_to_id[caminho[i+1]],
        'label': vias[i],
        'color': '#ff6b6b',
        'width': 4
    })

html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Percurso: Nova Descoberta → Boa Viagem (Setúbal)</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .info {{
            text-align: center;
            margin: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        #canvas {{
            display: block;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: move;
        }}
        .legend {{
            text-align: center;
            margin: 20px;
        }}
        .legend-item {{
            display: inline-block;
            margin: 0 15px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            vertical-align: middle;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <h1>Percurso: Nova Descoberta → Boa Viagem (Setúbal)</h1>
    <div class="info">
        <strong>Distância Total:</strong> {custo:.2f}m ({custo/1000:.2f}km) |
        <strong>Bairros:</strong> {len(caminho)} |
        <strong>Vias:</strong> {len(vias)}
    </div>
    <canvas id="canvas"></canvas>
    <div class="legend">
        <div class="legend-item">
            <span class="legend-color" style="background: #ff6b6b;"></span>
            <span>Origem/Destino</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #4ecdc4;"></span>
            <span>Caminho</span>
        </div>
    </div>
    <script>
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = 1800;
        canvas.height = 600;

        let offsetX = 50;
        let offsetY = 150;
        let isDragging = false;
        let startX, startY;

        canvas.addEventListener('mousedown', (e) => {{
            isDragging = true;
            startX = e.clientX - offsetX;
            startY = e.clientY - offsetY;
        }});

        canvas.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                offsetX = e.clientX - startX;
                offsetY = e.clientY - startY;
                draw();
            }}
        }});

        canvas.addEventListener('mouseup', () => {{
            isDragging = false;
        }});

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            edges.forEach(edge => {{
                const fromNode = nodes.find(n => n.id === edge.from);
                const toNode = nodes.find(n => n.id === edge.to);

                ctx.strokeStyle = edge.color;
                ctx.lineWidth = edge.width;
                ctx.beginPath();
                ctx.moveTo(fromNode.x + offsetX, fromNode.y + offsetY);
                ctx.lineTo(toNode.x + offsetX, toNode.y + offsetY);
                ctx.stroke();

                const midX = (fromNode.x + toNode.x) / 2 + offsetX;
                const midY = (fromNode.y + toNode.y) / 2 + offsetY - 10;

                ctx.fillStyle = '#666';
                ctx.font = '11px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(edge.label, midX, midY);
            }});

            nodes.forEach(node => {{
                ctx.fillStyle = node.color;
                ctx.beginPath();
                ctx.arc(node.x + offsetX, node.y + offsetY, 25, 0, Math.PI * 2);
                ctx.fill();

                ctx.strokeStyle = '#333';
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.fillStyle = 'white';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(node.label, node.x + offsetX, node.y + offsetY + 40);
            }});
        }}

        draw();
    </script>
</body>
</html>'''

with open(os.path.join(out_dir, 'arvore_percurso.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'Visualizacao gerada: out/parte1/arvore_percurso.html')
print(f'Caminho: {" -> ".join(caminho)}')
print(f'Distancia: {custo:.2f}m')
