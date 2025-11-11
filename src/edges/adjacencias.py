import pandas as pd
import json

def extrair_pontos(geometria):
    pontos = set()
    if geometria['type'] == 'Polygon':
        for coord in geometria['coordinates'][0]:
            pontos.add((round(coord[0], 6), round(coord[1], 6)))
    elif geometria['type'] == 'MultiPolygon':
        for poligono in geometria['coordinates']:
            for coord in poligono[0]:
                pontos.add((round(coord[0], 6), round(coord[1], 6)))
    return pontos

with open('data/bairros.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

df_bairros = pd.read_csv('data/bairros_unique.csv', sep=';', encoding='utf-8-sig')
lista_bairros = df_bairros['bairro'].tolist()

bairros_pontos = {}
for feature in geojson_data['features']:
    nome = feature['properties']['EBAIRRNOMEOF']
    if nome in lista_bairros:
        pontos = extrair_pontos(feature['geometry'])
        bairros_pontos[nome] = pontos

adjacencias = []
for i, bairro_origem in enumerate(lista_bairros):
    if bairro_origem not in bairros_pontos:
        continue

    pontos_origem = bairros_pontos[bairro_origem]

    for bairro_destino in lista_bairros[i+1:]:
        if bairro_destino not in bairros_pontos:
            continue

        pontos_destino = bairros_pontos[bairro_destino]

        if pontos_origem & pontos_destino:
            adjacencias.append({'bairro origem': bairro_origem, 'bairro match': bairro_destino})

df_adjacencias = pd.DataFrame(adjacencias)
df_adjacencias = df_adjacencias.sort_values(['bairro origem', 'bairro match']).reset_index(drop=True)
df_adjacencias.to_csv('data/adjacencias_provisorio.csv', index=False, sep=',', encoding='utf-8')
