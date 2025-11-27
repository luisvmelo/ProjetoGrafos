import json
import random
import math


def gerar_visualizacao_amostra_grafo(grafo, num_vertices=50, output_path='out/parte2/amostra_grafo.html'):

    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    random.seed(42)
    vertices_lista = list(grafo.vertices)
    vertices_amostra = random.sample(vertices_lista, min(num_vertices, len(vertices_lista)))
    vertices_set = set(vertices_amostra)
    
    arestas_filtradas = []
    
    for aresta in grafo.arestas:
        origem = aresta['origem']
        destino = aresta['destino']
        peso = aresta['peso']
        
        if origem in vertices_set and destino in vertices_set:
            arestas_filtradas.append({
                'origem': origem,
                'destino': destino,
                'peso': peso
            })
    
    vertices_conectados = set()
    for aresta in arestas_filtradas:
        vertices_conectados.add(aresta['origem'])
        vertices_conectados.add(aresta['destino'])
    
    vertices_final = sorted(list(vertices_conectados))
    
    vertex_to_idx = {v: i for i, v in enumerate(vertices_final)}
    
    n = len(vertices_final)
    nodes = []
    for i, v in enumerate(vertices_final):
        angle = 2 * math.pi * i / n
        x = 400 + 300 * math.cos(angle)
        y = 400 + 300 * math.sin(angle)
        nodes.append({
            'id': i,
            'label': v,
            'x': x,
            'y': y
        })
    
    edges = []
    for aresta in arestas_filtradas:
        origem_idx = vertex_to_idx[aresta['origem']]
        destino_idx = vertex_to_idx[aresta['destino']]
        peso = aresta['peso']
        
        edges.append({
            'from': origem_idx,
            'to': destino_idx,
            'peso': peso,
            'cor': 'red' if peso < 0 else 'green'
        })
    
    num_arestas_positivas = sum(1 for e in edges if e['peso'] >= 0)
    num_arestas_negativas = sum(1 for e in edges if e['peso'] < 0)
    num_vertices_removidos = len(vertices_amostra) - len(vertices_final)
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Amostra do Grafo - Parte 2</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: 
            overflow: hidden;
        }}
        
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 10;
        }}
        h1 {{
            margin: 0 0 5px 0;
            color: 
            font-size: 22px;
        }}
        .info {{
            font-size: 13px;
            color: 
            line-height: 1.6;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-top: 8px;
        }}
        .stat {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .color-box {{
            width: 16px;
            height: 16px;
            border-radius: 2px;
        }}
        .green {{ background: green; }}
        .red {{ background: red; }}
        
            flex: 1;
            position: relative;
            overflow: hidden;
            background: white;
        }}
        
            display: block;
            cursor: grab;
        }}
        
            cursor: grabbing;
        }}
        
            position: absolute;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            display: none;
            z-index: 100;
        }}
        .controls {{
            margin-top: 10px;
        }}
        button {{
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            background: 
            color: white;
            font-size: 13px;
            cursor: pointer;
            margin-right: 8px;
        }}
        button:hover {{
            background: 
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>Amostra do Grafo - Parte 2</h1>
            <div class="info">
                <div>
                    <strong>Grafo completo:</strong> {len(grafo.vertices)} vértices, {len(grafo.arestas)} arestas
                </div>
                <div>
                    <strong>Amostra selecionada:</strong> {len(vertices_amostra)} vértices aleatórios
                </div>
                <div>
                    <strong>Amostra exibida:</strong> {len(vertices_final)} vértices conectados, {len(edges)} arestas
                    ({num_vertices_removidos} vértices isolados removidos)
                </div>
                <div class="stats">
                    <div class="stat">
                        <div class="color-box green"></div>
                        <span>Arestas positivas: {num_arestas_positivas}</span>
                    </div>
                    <div class="stat">
                        <div class="color-box red"></div>
                        <span>Arestas negativas: {num_arestas_negativas}</span>
                    </div>
                </div>
            </div>
            <div class="controls">
                <button onclick="resetView()">Resetar Visualização</button>
                <button onclick="zoomIn()">Zoom +</button>
                <button onclick="zoomOut()">Zoom -</button>
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
        const container = document.getElementById('canvasContainer');
        
        let scale = 1;
        let offsetX = 0;
        let offsetY = 0;
        let isDragging = false;
        let dragStartX = 0;
        let dragStartY = 0;
        let hoveredNode = null;
        
        function resizeCanvas() {{
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            offsetX = canvas.width / 2 - 400;
            offsetY = canvas.height / 2 - 400;
            draw();
        }}
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        
        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            ctx.save();
            ctx.translate(offsetX, offsetY);
            ctx.scale(scale, scale);
            
            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];
                
                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.strokeStyle = edge.cor;
                ctx.lineWidth = edge.peso < 0 ? 2 : 1.5;
                ctx.globalAlpha = edge.peso < 0 ? 0.8 : 0.6;
                
                if (edge.peso < 0) {{
                    ctx.setLineDash([5, 5]);
                }}
                ctx.stroke();
                ctx.setLineDash([]);
                ctx.globalAlpha = 1;
                
                const dx = toNode.x - fromNode.x;
                const dy = toNode.y - fromNode.y;
                const angle = Math.atan2(dy, dx);
                const arrowSize = 10;
                
                const endX = toNode.x - 20 * Math.cos(angle);
                const endY = toNode.y - 20 * Math.sin(angle);
                
                ctx.beginPath();
                ctx.moveTo(endX, endY);
                ctx.lineTo(
                    endX - arrowSize * Math.cos(angle - Math.PI / 6),
                    endY - arrowSize * Math.sin(angle - Math.PI / 6)
                );
                ctx.lineTo(
                    endX - arrowSize * Math.cos(angle + Math.PI / 6),
                    endY - arrowSize * Math.sin(angle + Math.PI / 6)
                );
                ctx.closePath();
                ctx.fillStyle = edge.cor;
                ctx.fill();
            }});
            
            nodes.forEach(node => {{
                const isHovered = hoveredNode === node.id;
                
                ctx.beginPath();
                ctx.arc(node.x, node.y, 15, 0, 2 * Math.PI);
                ctx.fillStyle = isHovered ? '
                ctx.fill();
                ctx.strokeStyle = isHovered ? '
                ctx.lineWidth = isHovered ? 3 : 2;
                ctx.stroke();
                
                ctx.fillStyle = '
                ctx.font = 'bold 11px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                const label = node.label.replace('estacao_', '');
                ctx.fillText(label, node.x, node.y);
            }});
            
            ctx.restore();
        }}
        
        canvas.addEventListener('mousedown', (e) => {{
            isDragging = true;
            dragStartX = e.clientX - offsetX;
            dragStartY = e.clientY - offsetY;
            canvas.classList.add('dragging');
        }});
        
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;
            
            if (isDragging) {{
                offsetX = e.clientX - dragStartX;
                offsetY = e.clientY - dragStartY;
                draw();
            }} else {{
                let found = null;
                for (let node of nodes) {{
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    if (Math.sqrt(dx*dx + dy*dy) < 15) {{
                        found = node.id;
                        break;
                    }}
                }}
                
                if (found !== hoveredNode) {{
                    hoveredNode = found;
                    draw();
                }}
                
                if (hoveredNode !== null) {{
                    const node = nodes[hoveredNode];
                    const nodeEdges = edges.filter(e => e.from === node.id || e.to === node.id);
                    
                    tooltip.innerHTML = `
                        <strong>${{node.label}}</strong><br>
                        Grau: ${{nodeEdges.length}} arestas
                    `;
                    tooltip.style.display = 'block';
                    tooltip.style.left = e.clientX + 15 + 'px';
                    tooltip.style.top = e.clientY + 15 + 'px';
                }} else {{
                    tooltip.style.display = 'none';
                }}
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
            hoveredNode = null;
            draw();
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
        
        function resetView() {{
            scale = 1;
            offsetX = canvas.width / 2 - 400;
            offsetY = canvas.height / 2 - 400;
            draw();
        }}
        
        function zoomIn() {{
            scale = Math.min(5, scale * 1.2);
            draw();
        }}
        
        function zoomOut() {{
            scale = Math.max(0.1, scale / 1.2);
            draw();
        }}
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Visualização HTML gerada: {output_path}")
