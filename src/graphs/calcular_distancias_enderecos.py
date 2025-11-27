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

enderecos = [
    {'X': 'Nova Descoberta', 'Y': 'Boa Viagem', 'bairro_X': 'Nova Descoberta', 'bairro_Y': 'Boa Viagem'},
    {'X': 'Aflitos', 'Y': 'Pina', 'bairro_X': 'Aflitos', 'bairro_Y': 'Pina'},
    {'X': 'Casa Amarela', 'Y': 'Espinheiro', 'bairro_X': 'Casa Amarela', 'bairro_Y': 'Espinheiro'},
    {'X': 'Afogados', 'Y': 'Brasília Teimosa', 'bairro_X': 'Afogados', 'bairro_Y': 'Brasília Teimosa'},
    {'X': 'Santo Amaro', 'Y': 'Ilha do Leite', 'bairro_X': 'Santo Amaro', 'bairro_Y': 'Ilha do Leite'},
    {'X': 'Casa Forte', 'Y': 'Boa Vista', 'bairro_X': 'Casa Forte', 'bairro_Y': 'Boa Vista'}
]

resultados = []

for endereco in enderecos:
    origem = endereco['bairro_X']
    destino = endereco['bairro_Y']
    x = endereco['X']
    y = endereco['Y']

    caminho, custo, vias = dijkstra(grafo, origem, destino)

    if caminho is None:
        caminho_str = ''
        caminho_detalhado = ''
        custo_final = None
    else:
        caminho_str = ' -> '.join(caminho)
        custo_final = round(custo, 2)

        partes = []
        for i in range(len(caminho) - 1):
            partes.append(f"{caminho[i]} --[{vias[i]}]--> {caminho[i+1]}")
        caminho_detalhado = ' | '.join(partes)

    label_destino = y
    if origem == 'Nova Descoberta' and destino == 'Boa Viagem':
        label_destino = 'Boa Viagem (Setúbal)'

    resultados.append({
        'X': x,
        'Y': label_destino,
        'bairro_X': origem,
        'bairro_Y': destino,
        'custo': custo_final,
        'caminho': caminho_str,
        'caminho_detalhado': caminho_detalhado
    })

    if origem == 'Nova Descoberta' and destino == 'Boa Viagem':
        percurso_detalhes = []
        for i in range(len(caminho) - 1):
            percurso_detalhes.append({
                'de': caminho[i],
                'para': caminho[i+1],
                'via': vias[i]
            })

        percurso_json = {
            'origem': origem,
            'destino': 'Boa Viagem (Setúbal)',
            'custo': custo_final,
            'caminho': caminho,
            'vias': vias,
            'percurso_detalhado': percurso_detalhes
        }
        with open(os.path.join(out_dir, 'percurso_nova_descoberta_setubal.json'), 'w', encoding='utf-8') as f:
            json.dump(percurso_json, f, indent=2, ensure_ascii=False)

with open(os.path.join(out_dir, 'distancias_enderecos.csv'), 'w', encoding='utf-8') as f:
    f.write('X,Y,bairro_X,bairro_Y,custo,caminho,caminho_detalhado\n')
    for r in resultados:
        custo_str = str(r['custo']) if r['custo'] is not None else ''
        f.write(f"{r['X']},{r['Y']},{r['bairro_X']},{r['bairro_Y']},{custo_str},{r['caminho']},{r['caminho_detalhado']}\n")

print(f'Total de pares calculados: {len(resultados)}')
print('\nResultados:')
for r in resultados:
    print(f"  {r['X']} -> {r['Y']}: {r['custo']}m")
    print(f"    Caminho: {r['caminho']}")
    print(f"    Detalhado: {r['caminho_detalhado']}")
