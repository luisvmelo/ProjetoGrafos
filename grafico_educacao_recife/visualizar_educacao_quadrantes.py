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
            'unidades': row['n_unidades'],
            'matriculas': row['n_matriculas'],
            'populacao': row['Pop_Total'],
            'n_criancas_5_14': row['n_criancas_5_14'],
            'unidades_10k': row['unidades_por_10k_hab'],
            'matriculas_10k': row['matriculas_por_10k_hab'],
            'tipo_educacao': row['tipo_educacao_bairro'],
            'microrregiao': row['microrregião']
        }


CORES_TIPO = {
    'SEM_ESCOLA_ALTO_ANALF': '#d32f2f',    # Vermelho forte
    'SEM_ESCOLA_BAIXO_ANALF': '#1976d2',   # Azul
    'COM_ESCOLA_ALTO_ANALF': '#ff6f00',    # Laranja
    'COM_ESCOLA_BAIXO_ANALF': '#388e3c'    # Verde
}


RESUMOS_TIPO = {
    'SEM_ESCOLA_ALTO_ANALF': 'Território crítico — não há escola municipal e o analfabetismo é acima da média nacional.',
    'SEM_ESCOLA_BAIXO_ANALF': 'Bairro bem alfabetizado sem presença de escola municipal — provavelmente atendido pela rede privada.',
    'COM_ESCOLA_ALTO_ANALF': 'Presença de escolas não tem sido suficiente para reverter o analfabetismo.',
    'COM_ESCOLA_BAIXO_ANALF': 'Situação saudável — escola municipal e analfabetismo baixo.'
}


random.seed(42)
microrregioes_agrupadas = {}
for bairro in grafo.vertices:
    if bairro in dados_bairro:
        micro = dados_bairro[bairro]['microrregiao']
        if micro not in microrregioes_agrupadas:
            microrregioes_agrupadas[micro] = []
        microrregioes_agrupadas[micro].append(bairro)


posicoes_clusters = {
    '1.1': (800, 800), '1.2': (2800, 800), '1.3': (4800, 800),
    '2.1': (400, 2400), '2.2': (2000, 2400), '2.3': (3600, 2400),
    '3.1': (5400, 2400), '3.2': (800, 4000), '3.3': (2800, 4000),
    '4.1': (4800, 4000), '4.2': (6000, 4000), '4.3': (400, 5600),
    '5.1': (2000, 5600), '5.2': (3600, 5600), '5.3': (5400, 5600),
    '6.1': (1400, 7200), '6.2': (3600, 7200), '6.3': (5400, 7200)
}


posicoes = {}
for micro, bairros_micro in microrregioes_agrupadas.items():
    centro_cluster = posicoes_clusters.get(micro, (3000, 3000))
    n_bairros = len(bairros_micro)

    if n_bairros == 1:
        posicoes[bairros_micro[0]] = {'x': centro_cluster[0], 'y': centro_cluster[1]}
    else:
        raio_cluster = 250 + (n_bairros * 35) 
        for i, bairro in enumerate(bairros_micro):
            angulo = (2 * math.pi * i) / n_bairros
            jitter_x = random.uniform(-60, 60)
            jitter_y = random.uniform(-60, 60)
            x = centro_cluster[0] + raio_cluster * math.cos(angulo) + jitter_x
            y = centro_cluster[1] + raio_cluster * math.sin(angulo) + jitter_y
            posicoes[bairro] = {'x': x, 'y': y}


criancas_valores = [dados_bairro[b]['n_criancas_5_14'] for b in dados_bairro.keys()]
min_criancas = min(criancas_valores)
max_criancas = max(criancas_valores)

def calcular_tamanho_no(n_criancas):
    if max_criancas == min_criancas:
        return 20
    proporcao = (n_criancas - min_criancas) / (max_criancas - min_criancas)
    return 10 + (proporcao * 25)

bairros_lista = sorted(grafo.vertices)
bairro_to_id = {bairro: i for i, bairro in enumerate(bairros_lista)}

nodes = []
for i, bairro in enumerate(bairros_lista):
    dados = dados_bairro.get(bairro, {})

    taxa_analf = dados.get('taxa_analf', 0.0)
    taxa_alfab = dados.get('taxa_alfab', 0.0)
    unidades = dados.get('unidades', 0)
    matriculas = dados.get('matriculas', 0)
    populacao = dados.get('populacao', 0)
    n_criancas = dados.get('n_criancas_5_14', 0)
    unidades_10k = dados.get('unidades_10k', 0.0)
    matriculas_10k = dados.get('matriculas_10k', 0.0)
    tipo_educacao = dados.get('tipo_educacao', 'COM_ESCOLA_BAIXO_ANALF')
    micro = dados.get('microrregiao', 'N/A')

    tamanho = calcular_tamanho_no(n_criancas)

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes.get(bairro, {'x': 3000, 'y': 3000})['x'],
        'y': posicoes.get(bairro, {'x': 3000, 'y': 3000})['y'],
        'microrregiao': str(micro),
        'taxa_analfabetismo': round(taxa_analf, 2),
        'taxa_alfabetizacao': round(taxa_alfab, 2),
        'populacao': int(populacao),
        'n_criancas_5_14': int(n_criancas),
        'unidades': int(unidades),
        'matriculas': int(matriculas),
        'unidades_por_10k': round(unidades_10k, 2),
        'matriculas_por_10k': round(matriculas_10k, 2),
        'tipo_educacao': tipo_educacao,
        'tamanho': tamanho,
        'cor': CORES_TIPO.get(tipo_educacao, '#999'),
        'resumo': RESUMOS_TIPO.get(tipo_educacao, 'Sem dados')
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
                'to': bairro_to_id[destino]
            })

print(f"Grafo de Educação (Quadrantes) criado:")
print(f"  Vértices: {len(nodes)}")
print(f"  Arestas: {len(edges)}")
print(f"\nDistribuição por tipo educacional:")
for tipo in ['SEM_ESCOLA_ALTO_ANALF', 'SEM_ESCOLA_BAIXO_ANALF', 'COM_ESCOLA_ALTO_ANALF', 'COM_ESCOLA_BAIXO_ANALF']:
    count = sum(1 for n in nodes if n['tipo_educacao'] == tipo)
    print(f"  {tipo}: {count}")

html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Educação por Bairro - Recife (Quadrantes)</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #fafafa;
            overflow: hidden;
        }}
        #container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        #header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10;
        }}
        h1 {{
            margin: 0 0 15px 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .subtitle {{
            margin: 0 0 15px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        #controles {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        select, input[type="text"] {{
            padding: 10px 15px;
            border: 2px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.2);
            color: white;
            border-radius: 6px;
            font-size: 14px;
            backdrop-filter: blur(10px);
        }}
        select option {{
            color: #333;
            background: white;
        }}
        input[type="text"]::placeholder {{
            color: rgba(255,255,255,0.7);
        }}
        select:focus, input[type="text"]:focus {{
            outline: none;
            border-color: rgba(255,255,255,0.6);
            background: rgba(255,255,255,0.3);
        }}
        input[type="text"] {{
            min-width: 250px;
        }}
        button {{
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }}
        button:hover {{
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
        }}
        #legenda {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 15px;
            font-size: 13px;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255,255,255,0.15);
            padding: 8px 12px;
            border-radius: 6px;
            backdrop-filter: blur(10px);
        }}
        .legenda-cor {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            flex-shrink: 0;
        }}
        .legenda-texto {{
            flex: 1;
        }}
        .legenda-tipo {{
            font-weight: 600;
            margin-bottom: 2px;
        }}
        .legenda-desc {{
            font-size: 11px;
            opacity: 0.85;
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
            background: rgba(30, 30, 30, 0.95);
            color: white;
            padding: 16px;
            border-radius: 8px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 100;
            max-width: 350px;
            line-height: 1.6;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        .tooltip-title {{
            font-size: 17px;
            font-weight: bold;
            margin-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            padding-bottom: 8px;
        }}
        .tooltip-row {{
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .tooltip-label {{
            color: #aaa;
            font-size: 12px;
        }}
        .tooltip-resumo {{
            margin-top: 12px;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            font-size: 12px;
            font-style: italic;
            border-left: 3px solid #4ecdc4;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="header">
            <h1>🎓 Educação e Analfabetismo por Bairro - Recife</h1>
            <p class="subtitle">Visualização por Quadrantes: Presença de Escolas × Taxa de Analfabetismo</p>
            <div id="controles">
                <label for="selectMicro"><strong>📍 Microrregião:</strong></label>
                <select id="selectMicro">
                    <option value="todas">Todas</option>
                </select>
                <label for="inputBusca"><strong>🔍 Buscar:</strong></label>
                <input type="text" id="inputBusca" placeholder="Digite o nome do bairro...">
                <button id="btnReset">↻ Resetar</button>
            </div>
            <div id="legenda">
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: {CORES_TIPO['SEM_ESCOLA_ALTO_ANALF']};"></div>
                    <div class="legenda-texto">
                        <div class="legenda-tipo">🔴 Sem escola + Alto analfabetismo</div>
                        <div class="legenda-desc">Território crítico</div>
                    </div>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: {CORES_TIPO['SEM_ESCOLA_BAIXO_ANALF']};"></div>
                    <div class="legenda-texto">
                        <div class="legenda-tipo">🔵 Sem escola + Baixo analfabetismo</div>
                        <div class="legenda-desc">Provável rede privada</div>
                    </div>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: {CORES_TIPO['COM_ESCOLA_ALTO_ANALF']};"></div>
                    <div class="legenda-texto">
                        <div class="legenda-tipo">🟠 Com escola + Alto analfabetismo</div>
                        <div class="legenda-desc">Rede não resolve</div>
                    </div>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: {CORES_TIPO['COM_ESCOLA_BAIXO_ANALF']};"></div>
                    <div class="legenda-texto">
                        <div class="legenda-tipo">🟢 Com escola + Baixo analfabetismo</div>
                        <div class="legenda-desc">Situação saudável</div>
                    </div>
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

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');
        const selectMicro = document.getElementById('selectMicro');
        const btnReset = document.getElementById('btnReset');
        const inputBusca = document.getElementById('inputBusca');

        let offsetX = 0;
        let offsetY = 0;
        let scale = 1.0;
        let isDragging = false;
        let startX, startY;
        let bairroSelecionado = null;
        let microSelecionada = 'todas';

        // Popular dropdown
        const micros = [...new Set(nodes.map(n => n.microrregiao))].sort();
        micros.forEach(micro => {{
            const option = document.createElement('option');
            option.value = micro;
            option.textContent = micro;
            selectMicro.appendChild(option);
        }});

        selectMicro.addEventListener('change', (e) => {{
            microSelecionada = e.target.value;
            bairroSelecionado = null;

            if (microSelecionada !== 'todas') {{
                const nosMicro = nodes.filter(n => n.microrregiao === microSelecionada);
                if (nosMicro.length > 0) {{
                    const centerX = nosMicro.reduce((sum, n) => sum + n.x, 0) / nosMicro.length;
                    const centerY = nosMicro.reduce((sum, n) => sum + n.y, 0) / nosMicro.length;
                    offsetX = canvas.width / 2 - centerX * scale;
                    offsetY = canvas.height / 2 - centerY * scale;
                }}
            }}

            draw();
        }});

        inputBusca.addEventListener('input', (e) => {{
            const busca = e.target.value.trim().toLowerCase();
            if (busca.length === 0) {{
                draw();
                return;
            }}

            const encontrado = nodes.find(n => n.label.toLowerCase().includes(busca));
            if (encontrado) {{
                bairroSelecionado = encontrado.label;
                offsetX = canvas.width / 2 - encontrado.x * scale;
                offsetY = canvas.height / 2 - encontrado.y * scale;
                draw();
            }}
        }});

        btnReset.addEventListener('click', () => {{
            microSelecionada = 'todas';
            selectMicro.value = 'todas';
            bairroSelecionado = null;
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

                let clicked = false;
                for (const node of nodes) {{
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < node.tamanho) {{
                        bairroSelecionado = bairroSelecionado === node.label ? null : node.label;
                        clicked = true;
                        draw();
                        break;
                    }}
                }}

                if (!clicked && bairroSelecionado) {{
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
            scale = Math.max(0.1, Math.min(5, scale * delta));
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

                if (dist < node.tamanho) {{
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
                            <span class="tooltip-label">População Total:</span>
                            <strong>${{node.populacao.toLocaleString()}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Crianças 5-14 anos (est.):</span>
                            <strong>${{node.n_criancas_5_14.toLocaleString()}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Unidades Educacionais:</span>
                            <strong>${{node.unidades}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Matrículas:</span>
                            <strong>${{node.matriculas.toLocaleString()}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Unidades/10k hab:</span>
                            <strong>${{node.unidades_por_10k}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Matrículas/10k hab:</span>
                            <strong>${{node.matriculas_por_10k}}</strong>
                        </div>
                        <div class="tooltip-resumo">
                            <strong>Resumo:</strong> ${{node.resumo}}
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

            // Determinar vizinhos
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

            // Filtrar nós
            const nodesFiltrados = microSelecionada === 'todas'
                ? nodes
                : nodes.filter(n => n.microrregiao === microSelecionada);

            const labelsFiltrados = new Set(nodesFiltrados.map(n => n.label));

            // Desenhar arestas (cinza claro e fino)
            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#4ecdc4';
                    ctx.lineWidth = 2;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#e0e0e0';
                    ctx.lineWidth = 0.3;
                }} else {{
                    ctx.strokeStyle = '#d0d0d0';
                    ctx.lineWidth = 0.5;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
            }});

            // Desenhar nós
            nodes.forEach(node => {{
                if (!labelsFiltrados.has(node.label)) return;

                let shouldDim = vizinhosSet && !vizinhosSet.has(node.label);

                // Nó principal
                ctx.fillStyle = shouldDim ? '#ccc' : node.cor;
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.tamanho, 0, Math.PI * 2);
                ctx.fill();

                // Borda (mais grossa para casos críticos)
                const isCritico = node.tipo_educacao === 'SEM_ESCOLA_ALTO_ANALF';
                ctx.strokeStyle = isCritico ? '#000' : '#333';
                ctx.lineWidth = isCritico ? 3 :
                                (vizinhosSet && node.label === bairroSelecionado) ? 4 : 2;
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.tamanho, 0, Math.PI * 2);
                ctx.stroke();

                // Label
                if (scale > 0.5) {{
                    ctx.fillStyle = '#222';
                    ctx.font = 'bold 13px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText(node.label, node.x, node.y + node.tamanho + 16);
                }}
            }});

            ctx.restore();
        }}

        draw();
    </script>
</body>
</html>'''

with open('out/parte1/grafo_educacao_quadrantes.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização gerada: out/parte1/grafo_educacao_quadrantes.html")
