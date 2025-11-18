import json
import math
import random
import pandas as pd
import os

# Mudar para o diretório raiz do projeto para carregar os dados
os.chdir('/home/luisevmelo/ProjetoGrafos-1')

# Importar classes necessárias
import sys
sys.path.append('src/graphs')
from graph import Grafo

# Construir grafo manualmente
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

# Construir grafo primeiro para ter os nomes corretos
grafo = construir_grafo()

# Criar mapeamento de MAIÚSCULAS (sem acentos) para os nomes corretos do grafo
import unicodedata
def normalizar_nome(texto):
    # Remove acentos
    sem_acento = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    # Remove hífens, espaços extras e converte para maiúsculas
    sem_hifen = sem_acento.replace('-', ' ').replace('  ', ' ').strip().upper()
    # Normalizar variações de escrita comuns
    sem_hifen = sem_hifen.replace('TEREZINHA', 'TERESINHA')
    sem_hifen = sem_hifen.replace('HEMETERIO', 'HEMETERIO')
    return sem_hifen

bairro_mapping = {}
for bairro_grafo in grafo.vertices:
    bairro_norm = normalizar_nome(bairro_grafo)
    bairro_mapping[bairro_norm] = bairro_grafo

# Carregar dados do índice OCDE
df_saude = pd.read_csv('Visualizaçao_Saude/medicos_por_bairro_com_indices.csv', encoding='utf-8-sig')
indice_ocde_dict = {}
medicos_por_unidade_dict = {}
proporcao_dict = {}
medicos_totais_dict = {}
unidades_dict = {}

# Usar o mapeamento correto
for _, row in df_saude.iterrows():
    bairro_csv = row['Bairro']
    bairro_norm = normalizar_nome(bairro_csv)

    # Buscar o nome correto no grafo
    bairro_correto = bairro_mapping.get(bairro_norm, None)

    if bairro_correto:
        indice_ocde_dict[bairro_correto] = row['Índice OCDE']
        medicos_por_unidade_dict[bairro_correto] = row['Médicos por Unidade de Saúde']
        proporcao_dict[bairro_correto] = row['Proporção Médico por População']
        medicos_totais_dict[bairro_correto] = row['medicos totais']
        unidades_dict[bairro_correto] = row['unidades']

# Carregar dados das microrregiões
df_micro = pd.read_csv('Visualizaçao_Saude/microregioes_saude.csv')
indice_micro_dict = {}
for _, row in df_micro.iterrows():
    micro = str(row['microrregiao'])  # Converter para string!
    indice_micro_dict[micro] = row['Indice OCDE']

# Carregar dados de microrregião
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

# Criar nós com informações de saúde
nodes = []
for i, bairro in enumerate(bairros_lista):
    micro = microrregiao_dict.get(bairro, 'N/A')
    indice_ocde = indice_ocde_dict.get(bairro, 0.0)
    medicos_unidade = medicos_por_unidade_dict.get(bairro, 0.0)
    proporcao = proporcao_dict.get(bairro, 0.0)
    medicos_totais = medicos_totais_dict.get(bairro, 0)
    unidades = unidades_dict.get(bairro, 0)

    # Obter índice OCDE da microrregião (para bairros com múltiplas, pega a primeira)
    micro_principal = micro.split(' / ')[0].strip() if ' / ' in micro else micro
    indice_micro = indice_micro_dict.get(micro_principal, 0.0)

    # Determinar categoria de saúde do bairro
    if indice_ocde >= 2.0:
        categoria = 'excelente'
    elif indice_ocde >= 1.0:
        categoria = 'bom'
    elif indice_ocde >= 0.5:
        categoria = 'regular'
    else:
        categoria = 'critico'

    # Determinar categoria da microrregião
    if indice_micro >= 2.0:
        categoria_micro = 'excelente'
    elif indice_micro >= 1.0:
        categoria_micro = 'bom'
    elif indice_micro >= 0.5:
        categoria_micro = 'regular'
    else:
        categoria_micro = 'critico'

    nodes.append({
        'id': i,
        'label': bairro,
        'x': posicoes[bairro]['x'],
        'y': posicoes[bairro]['y'],
        'microrregiao': micro,
        'indice_ocde': round(indice_ocde, 4),
        'indice_micro': round(indice_micro, 4),
        'medicos_por_unidade': round(medicos_unidade, 2),
        'proporcao_medico_pop': round(proporcao, 6),
        'medicos_totais': int(medicos_totais),
        'unidades': int(unidades),
        'categoria': categoria,
        'categoria_micro': categoria_micro
    })

# Remover arestas paralelas - manter apenas uma aresta entre cada par
pares_vistos = {}
edges = []

for aresta in grafo.arestas:
    origem = aresta['origem']
    destino = aresta['destino']
    par = tuple(sorted([origem, destino]))

    # Se já vimos esse par, pular (remove duplicatas)
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

    # Calcular centro da microrregião (média das posições)
    centro_x = sum(posicoes[b]['x'] for b in bairros) / len(bairros)
    centro_y = sum(posicoes[b]['y'] for b in bairros) / len(bairros)

    # Calcular raio (distância máxima do centro a qualquer bairro + margem)
    raio_max = 0
    for b in bairros:
        dist = math.sqrt((posicoes[b]['x'] - centro_x)**2 + (posicoes[b]['y'] - centro_y)**2)
        raio_max = max(raio_max, dist)

    raio_halo = raio_max + 100  # Adicionar margem

    indice_micro = indice_micro_dict.get(micro, 0.0)
    if indice_micro >= 2.0:
        categoria_micro = 'excelente'
    elif indice_micro >= 1.0:
        categoria_micro = 'bom'
    elif indice_micro >= 0.5:
        categoria_micro = 'regular'
    else:
        categoria_micro = 'critico'

    micro_info[micro] = {
        'centro_x': centro_x,
        'centro_y': centro_y,
        'raio': raio_halo,
        'indice': round(indice_micro, 4),
        'categoria': categoria_micro,
        'bairros': bairros
    }

print(f"Grafo de Saúde criado:")
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

# Gerar HTML da visualização
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Grafo de Saúde - Índice OCDE por Bairro</title>
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
            border-radius: 50%;
            border: 2px solid #333;
        }}
        #canvasContainer {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: white;
        }}
        #painelRelatorio {{
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
        #painelRelatorio.aberto {{
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
        .relatorio-item {{
            margin: 15px 0;
            padding: 12px;
            background: #f9f9f9;
            border-radius: 6px;
            border-left: 4px solid #e74c3c;
        }}
        .relatorio-item.positiva {{
            border-left-color: #27ae60;
        }}
        .relatorio-titulo {{
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        .relatorio-descricao {{
            font-size: 13px;
            color: #555;
            line-height: 1.4;
        }}
        .legenda-arestas {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
            font-size: 12px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
        }}
        .legenda-aresta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .legenda-aresta-linha {{
            width: 30px;
            height: 3px;
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
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 15px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            display: none;
            z-index: 100;
            max-width: 280px;
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
            <h1>Índice OCDE de Saúde por Bairro - Recife</h1>
            <div id="filtroMicro">
                <label for="selectMicro"><strong>Filtrar por Microrregião:</strong></label>
                <select id="selectMicro">
                    <option value="todas">Todas as Microrregiões</option>
                </select>
                <label for="inputBusca"><strong>Buscar Bairro:</strong></label>
                <input type="text" id="inputBusca" placeholder="Digite o nome do bairro...">
                <button id="btnResetFiltro">Resetar Visualização</button>
                <button id="btnRelatorio">📊 Ver Relatório de Conexões</button>
            </div>
            <div id="legenda">
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #27ae60;"></div>
                    <span><strong>Excelente</strong> (≥ 2.0 × OCDE)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #3498db;"></div>
                    <span><strong>Bom</strong> (1.0-2.0 × OCDE)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #f39c12;"></div>
                    <span><strong>Regular</strong> (0.5-1.0 × OCDE)</span>
                </div>
                <div class="legenda-item">
                    <div class="legenda-cor" style="background: #e74c3c;"></div>
                    <span><strong>Crítico</strong> (&lt; 0.5 × OCDE)</span>
                </div>
            </div>
            <div class="legenda-arestas">
                <strong>Conexões:</strong>
                <div class="legenda-aresta-item">
                    <div class="legenda-aresta-linha" style="background: #27ae60;"></div>
                    <span>Bom↔Bom</span>
                </div>
                <div class="legenda-aresta-item">
                    <div class="legenda-aresta-linha" style="background: #3498db;"></div>
                    <span>Bom↔Crítico</span>
                </div>
                <div class="legenda-aresta-item">
                    <div class="legenda-aresta-linha" style="background: #f39c12;"></div>
                    <span>Regular↔Regular</span>
                </div>
                <div class="legenda-aresta-item">
                    <div class="legenda-aresta-linha" style="background: #e74c3c;"></div>
                    <span>Crítico↔Crítico</span>
                </div>
            </div>
        </div>
        <div id="canvasContainer">
            <canvas id="canvas"></canvas>
            <div id="tooltip"></div>
            <div id="painelRelatorio">
                <div class="fechar-painel">
                    <h2 style="margin: 0 0 10px 0;">Relatório de Conexões</h2>
                    <button onclick="fecharPainel()">✕ Fechar</button>
                </div>
                <div id="conteudoRelatorio"></div>
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
        const btnRelatorio = document.getElementById('btnRelatorio');
        const painelRelatorio = document.getElementById('painelRelatorio');

        let offsetX = 0;
        let offsetY = 0;
        let scale = 1.0;
        let isDragging = false;
        let startX, startY;
        let bairroSelecionado = null;
        let microSelecionada = 'todas';
        let bairroBuscado = null;

        // Função para calcular score de qualidade da conexão
        function calcularScoreConexao(indice1, indice2) {{
            // Média dos índices - quanto maior, melhor a conexão
            return (indice1 + indice2) / 2;
        }}

        function getCategoriaConexao(fromNode, toNode) {{
            const indice1 = fromNode.indice_ocde;
            const indice2 = toNode.indice_ocde;
            const ambosBonus = (indice1 >= 1.0 && indice2 >= 1.0);
            const ambosCriticos = (indice1 < 0.5 && indice2 < 0.5);
            const umBomUmRuim = (indice1 >= 1.0 && indice2 < 1.0) || (indice2 >= 1.0 && indice1 < 1.0);

            if (ambosBonus) return 'excelente';
            if (umBomUmRuim) return 'compensatoria';
            if (ambosCriticos) return 'critica';
            return 'regular';
        }}

        function getCorConexao(categoria) {{
            switch(categoria) {{
                case 'excelente': return '#27ae60';
                case 'compensatoria': return '#3498db';
                case 'regular': return '#f39c12';
                case 'critica': return '#e74c3c';
                default: return '#999';
            }}
        }}

        btnRelatorio.addEventListener('click', () => {{
            painelRelatorio.classList.add('aberto');
            gerarRelatorio();
        }});

        function fecharPainel() {{
            painelRelatorio.classList.remove('aberto');
        }}

        function gerarRelatorio() {{
            const conexoes = [];

            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];
                const categoria = getCategoriaConexao(fromNode, toNode);
                const score = calcularScoreConexao(fromNode.indice_ocde, toNode.indice_ocde);

                conexoes.push({{
                    de: fromNode.label,
                    para: toNode.label,
                    indice_de: fromNode.indice_ocde,
                    indice_para: toNode.indice_ocde,
                    categoria: categoria,
                    score: score,
                    logradouro: edge.label
                }});
            }});

            // Separar por tipo
            const criticas = conexoes.filter(c => c.categoria === 'critica').sort((a, b) => a.score - b.score);
            const compensatorias = conexoes.filter(c => c.categoria === 'compensatoria').sort((a, b) => b.score - a.score);
            const excelentes = conexoes.filter(c => c.categoria === 'excelente').sort((a, b) => b.score - a.score);

            let html = `
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #e74c3c;">⚠️ Conexões Críticas (${{criticas.length}})</h3>
                    <p style="font-size: 13px; color: #666;">Ambos bairros com índice OCDE abaixo de 0.5</p>
                </div>
            `;

            criticas.slice(0, 10).forEach(c => {{
                html += `
                    <div class="relatorio-item">
                        <div class="relatorio-titulo">${{c.de}} ↔ ${{c.para}}</div>
                        <div class="relatorio-descricao">
                            Índices: ${{c.indice_de.toFixed(2)}} ↔ ${{c.indice_para.toFixed(2)}}<br>
                            Logradouro: ${{c.logradouro}}<br>
                            <strong>Situação:</strong> Ambos abaixo do padrão OCDE - área crítica
                        </div>
                    </div>
                `;
            }});

            html += `
                <div style="margin: 30px 0 20px 0;">
                    <h3 style="color: #3498db;">🔄 Conexões Compensatórias (${{compensatorias.length}})</h3>
                    <p style="font-size: 13px; color: #666;">Um bairro bom conectado a um crítico/regular</p>
                </div>
            `;

            compensatorias.slice(0, 10).forEach(c => {{
                const melhor = c.indice_de > c.indice_para ? c.de : c.para;
                const pior = c.indice_de > c.indice_para ? c.para : c.de;
                html += `
                    <div class="relatorio-item positiva">
                        <div class="relatorio-titulo">${{c.de}} ↔ ${{c.para}}</div>
                        <div class="relatorio-descricao">
                            Índices: ${{c.indice_de.toFixed(2)}} ↔ ${{c.indice_para.toFixed(2)}}<br>
                            Logradouro: ${{c.logradouro}}<br>
                            <strong>Benefício:</strong> ${{melhor}} pode atender ${{pior}}
                        </div>
                    </div>
                `;
            }});

            html += `
                <div style="margin: 30px 0 20px 0;">
                    <h3 style="color: #27ae60;">✅ Conexões Excelentes (${{excelentes.length}})</h3>
                    <p style="font-size: 13px; color: #666;">Ambos bairros atendem ao padrão OCDE</p>
                </div>
            `;

            excelentes.slice(0, 5).forEach(c => {{
                html += `
                    <div class="relatorio-item positiva">
                        <div class="relatorio-titulo">${{c.de}} ↔ ${{c.para}}</div>
                        <div class="relatorio-descricao">
                            Índices: ${{c.indice_de.toFixed(2)}} ↔ ${{c.indice_para.toFixed(2)}}<br>
                            Logradouro: ${{c.logradouro}}<br>
                            <strong>Situação:</strong> Região bem servida de saúde
                        </div>
                    </div>
                `;
            }});

            document.getElementById('conteudoRelatorio').innerHTML = html;
        }}

        // Popul ar dropdown de microrregiões
        const microregioesUnicas = [...new Set(nodes.map(n => n.microrregiao))].sort();
        microregioesUnicas.forEach(micro => {{
            const option = document.createElement('option');
            option.value = micro;
            const microInfo = microregioes.find(m => m.bairros && m.bairros.includes(nodes.find(n => n.microrregiao === micro)?.label));
            const indice = microInfo ? microInfo.indice : 'N/A';
            option.textContent = `${{micro}} (Índice: ${{indice}})`;
            selectMicro.appendChild(option);
        }});

        selectMicro.addEventListener('change', (e) => {{
            microSelecionada = e.target.value;
            bairroSelecionado = null;

            if (microSelecionada !== 'todas') {{
                // Centralizar na microrregião selecionada
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

                // Centralizar no bairro encontrado
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
                    const raio = calcularRaioNo();
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

        function calcularRaioNo() {{
            // Raio fixo para todos os nós
            return 18;
        }}

        function calcularRaioHalo(node) {{
            // Calcular o "índice de criticidade" (inverso do índice OCDE)
            // Quanto menor o índice OCDE, maior o halo (mais crítico)
            // Índice OCDE 1.0 = padrão mínimo aceitável

            if (node.indice_ocde >= 1.0) {{
                // Se atende ao padrão, halo pequeno (proporcional ao quanto excede)
                const excesso = Math.min(node.indice_ocde, 5.0);
                return 25 + (excesso - 1.0) * 3; // De 25 a ~37 pixels
            }} else {{
                // Se não atende, halo grande (inversamente proporcional)
                // Quanto mais próximo de 0, maior o halo
                const criticidade = 1.0 - node.indice_ocde; // 0 a 1
                return 30 + criticidade * 50; // De 30 a 80 pixels
            }}
        }}

        function getCorCategoria(categoria) {{
            switch(categoria) {{
                case 'excelente': return '#27ae60';
                case 'bom': return '#3498db';
                case 'regular': return '#f39c12';
                case 'critico': return '#e74c3c';
                default: return '#95a5a6';
            }}
        }}

        function handleMouseMove(e) {{
            const rect = canvas.getBoundingClientRect();
            const mouseX = (e.clientX - rect.left - offsetX) / scale;
            const mouseY = (e.clientY - rect.top - offsetY) / scale;

            let found = false;
            for (const node of nodes) {{
                const raio = calcularRaioNo();
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < raio) {{
                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{node.label}}</div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Índice OCDE (Bairro):</span>
                            <strong>${{node.indice_ocde}}</strong>
                            (${{node.indice_ocde >= 1.0 ? '✓ Atende' : '✗ Não atende'}})
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Índice OCDE (Microrregião):</span>
                            <strong>${{node.indice_micro}}</strong>
                            (${{node.indice_micro >= 1.0 ? '✓ Atende' : '✗ Não atende'}})
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Médicos:</span> <strong>${{node.medicos_totais}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Unidades:</span> <strong>${{node.unidades}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Médicos/Unidade:</span> <strong>${{node.medicos_por_unidade}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Proporção Médico/Pop:</span> <strong>${{node.proporcao_medico_pop}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Microrregião:</span> ${{node.microrregiao}}
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Categoria Bairro:</span> <strong>${{node.categoria.toUpperCase()}}</strong>
                        </div>
                        <div class="tooltip-row">
                            <span class="tooltip-label">Categoria Micro:</span> <strong>${{node.categoria_micro.toUpperCase()}}</strong>
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

            // 1. DESENHAR HALOS DE MICRORREGIÕES (camada de fundo)
            microregioes.forEach(micro => {{
                // Filtrar: só desenhar halo se a microrregião tem bairros visíveis
                const temBairrosVisiveis = micro.bairros.some(b => labelsFiltrados.has(b));
                if (!temBairrosVisiveis && microSelecionada !== 'todas') return;

                const corMicro = getCorCategoria(micro.categoria);

                // Desenhar halo grande da microrregião com gradiente radial
                const gradient = ctx.createRadialGradient(
                    micro.centro_x, micro.centro_y, micro.raio * 0.3,
                    micro.centro_x, micro.centro_y, micro.raio
                );

                gradient.addColorStop(0, corMicro + '00'); // Centro transparente
                gradient.addColorStop(0.6, corMicro + '15'); // Meio levemente visível
                gradient.addColorStop(1, corMicro + '35'); // Borda mais visível

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(micro.centro_x, micro.centro_y, micro.raio, 0, Math.PI * 2);
                ctx.fill();

                // Borda sutil da microrregião
                ctx.strokeStyle = corMicro + '50';
                ctx.lineWidth = 2;
                ctx.setLineDash([10, 5]); // Linha tracejada
                ctx.beginPath();
                ctx.arc(micro.centro_x, micro.centro_y, micro.raio, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]); // Resetar linha
            }});

            // 2. Desenhar arestas
            edges.forEach(edge => {{
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];

                // Filtrar arestas: só desenhar se ambos os nós estão visíveis
                if (!labelsFiltrados.has(fromNode.label) || !labelsFiltrados.has(toNode.label)) return;

                const chave = `${{edge.from}}-${{edge.to}}`;
                const categoriaConexao = getCategoriaConexao(fromNode, toNode);
                const corConexao = getCorConexao(categoriaConexao);

                if (vizinhosSet && arestasVizinhos.has(chave)) {{
                    ctx.strokeStyle = '#4ecdc4';
                    ctx.lineWidth = 3;
                }} else if (vizinhosSet) {{
                    ctx.strokeStyle = '#ddd';
                    ctx.lineWidth = 0.5;
                }} else {{
                    // Usar cor baseada na qualidade da conexão
                    ctx.strokeStyle = corConexao;
                    ctx.lineWidth = categoriaConexao === 'critica' ? 2 : 1.5;
                    ctx.globalAlpha = categoriaConexao === 'critica' ? 0.8 : 0.6;
                }}

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.stroke();
                ctx.globalAlpha = 1.0;
            }});

            // 3. Desenhar nós com halo individual
            nodes.forEach(node => {{
                // Filtrar nós: só desenhar se está visível
                if (!labelsFiltrados.has(node.label)) return;

                const raioNo = calcularRaioNo();
                const raioHalo = calcularRaioHalo(node);
                let shouldDim = false;

                if (vizinhosSet && !vizinhosSet.has(node.label)) {{
                    shouldDim = true;
                }}

                // 3.1. Desenhar o halo individual do bairro (círculo maior, semitransparente)
                if (!shouldDim) {{
                    const corHalo = getCorCategoria(node.categoria);
                    ctx.fillStyle = corHalo + '40'; // Adiciona transparência (40 em hex = ~25% opacidade)
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, raioHalo, 0, Math.PI * 2);
                    ctx.fill();

                    // Gradiente opcional para efeito de mapa de calor
                    const gradient = ctx.createRadialGradient(node.x, node.y, raioNo, node.x, node.y, raioHalo);
                    gradient.addColorStop(0, corHalo + '00'); // Centro transparente
                    gradient.addColorStop(0.5, corHalo + '30'); // Meio semitransparente
                    gradient.addColorStop(1, corHalo + '60'); // Borda mais opaca
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, raioHalo, 0, Math.PI * 2);
                    ctx.fill();
                }}

                // 3.2. Desenhar o nó principal (tamanho fixo)
                ctx.fillStyle = shouldDim ? '#d0d0d0' : getCorCategoria(node.categoria);
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.fill();

                // 3.3. Borda do nó
                ctx.strokeStyle = (vizinhosSet && node.label === bairroSelecionado) ? '#4ecdc4' : '#333';
                ctx.lineWidth = (vizinhosSet && node.label === bairroSelecionado) ? 4 : 2;
                ctx.beginPath();
                ctx.arc(node.x, node.y, raioNo, 0, Math.PI * 2);
                ctx.stroke();

                // 3.4. Label do bairro
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

with open('Visualizaçao_Saude/grafo_saude_ocde.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Visualização gerada: Visualizaçao_Saude/grafo_saude_ocde.html")
