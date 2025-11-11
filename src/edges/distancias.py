import pandas as pd
import json
import math

def calcular_distancia_euclidiana(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def ponto_dentro_poligono(x, y, poligono):
    n = len(poligono)
    dentro = False
    j = n - 1
    for i in range(n):
        xi, yi = poligono[i][0], poligono[i][1]
        xj, yj = poligono[j][0], poligono[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 0.0001) + xi):
            dentro = not dentro
        j = i
    return dentro

def ponto_dentro_bairro(ponto, bairro_geom):
    x, y = ponto[0], ponto[1]
    if bairro_geom['type'] == 'Polygon':
        return ponto_dentro_poligono(x, y, bairro_geom['coordinates'][0])
    elif bairro_geom['type'] == 'MultiPolygon':
        for poligono in bairro_geom['coordinates']:
            if ponto_dentro_poligono(x, y, poligono[0]):
                return True
    return False

def distancia_minima_ponto_poligono(ponto, bairro_geom):
    x, y = ponto[0], ponto[1]
    min_dist = float('inf')

    poligonos = []
    if bairro_geom['type'] == 'Polygon':
        poligonos = [bairro_geom['coordinates'][0]]
    elif bairro_geom['type'] == 'MultiPolygon':
        poligonos = [poly[0] for poly in bairro_geom['coordinates']]

    for poligono in poligonos:
        for i in range(len(poligono)):
            p = poligono[i]
            dist = calcular_distancia_euclidiana((x, y), (p[0], p[1]))
            min_dist = min(min_dist, dist)

    return min_dist

def calcular_comprimento_linha(coords):
    comprimento = 0.0
    for i in range(len(coords) - 1):
        p1 = coords[i]
        p2 = coords[i + 1]
        comprimento += calcular_distancia_euclidiana(p1, p2)
    return comprimento

def classificar_trecho(coords, geom_origem, geom_destino):
    pontos_origem = 0
    pontos_destino = 0

    for ponto in coords:
        if ponto_dentro_bairro(ponto, geom_origem):
            pontos_origem += 1
        elif ponto_dentro_bairro(ponto, geom_destino):
            pontos_destino += 1

    if pontos_origem > 0 and pontos_destino > 0:
        return True

    total_pontos = len(coords)
    proporcao_origem = pontos_origem / total_pontos if total_pontos > 0 else 0
    proporcao_destino = pontos_destino / total_pontos if total_pontos > 0 else 0

    if proporcao_origem > 0.05 and proporcao_destino > 0.05:
        return True

    if (pontos_origem > 0 or pontos_destino > 0) and total_pontos > 0:
        if (pontos_origem + pontos_destino) / total_pontos > 0.3:
            return True

    return False

with open('data/bairros.geojson', 'r', encoding='utf-8') as f:
    bairros_geojson = json.load(f)

with open('data/bvisualizacao_fctrechologradouro.geojson', 'r', encoding='utf-8') as f:
    trechos_geojson = json.load(f)

df_vias = pd.read_csv('data/vias_conectam_bairros_SELECIONADOS.csv')

bairros_geom = {}
for feature in bairros_geojson['features']:
    nome = feature['properties']['EBAIRRNOMEOF']
    bairros_geom[nome] = feature['geometry']

resultados = []
total = len(df_vias)
for idx, row in df_vias.iterrows():
    if idx % 100 == 0:
        print(f"Processando {idx}/{total}...")

    bairro_origem = row['bairro_origem']
    bairro_destino = row['bairro_destino']
    nome_via = row['nome_logradouro']

    if bairro_origem not in bairros_geom or bairro_destino not in bairros_geom:
        resultados.append({
            'bairro_origem': bairro_origem,
            'bairro_destino': bairro_destino,
            'nome_logradouro': nome_via,
            'distancia': None
        })
        continue

    geom_origem = bairros_geom[bairro_origem]
    geom_destino = bairros_geom[bairro_destino]

    distancia_total = 0.0
    trechos_encontrados = 0

    for trecho in trechos_geojson['features']:
        nome_trecho = trecho['properties']['NLOGRACONC']
        if nome_trecho != nome_via:
            continue

        comprimento = trecho['properties']['SdeLength_']
        if comprimento is None or comprimento == 0:
            continue

        geom_type = trecho['geometry']['type']
        if geom_type == 'MultiLineString':
            linhas = trecho['geometry']['coordinates']
        elif geom_type == 'LineString':
            linhas = [trecho['geometry']['coordinates']]
        else:
            continue

        for linha in linhas:
            if len(linha) < 2:
                continue

            if classificar_trecho(linha, geom_origem, geom_destino):
                distancia_total += comprimento
                trechos_encontrados += 1
                break

    if distancia_total > 0:
        resultados.append({
            'bairro_origem': bairro_origem,
            'bairro_destino': bairro_destino,
            'nome_logradouro': nome_via,
            'distancia': round(distancia_total, 2)
        })
    else:
        resultados.append({
            'bairro_origem': bairro_origem,
            'bairro_destino': bairro_destino,
            'nome_logradouro': nome_via,
            'distancia': None
        })

df_resultado = pd.DataFrame(resultados)
df_resultado.to_csv('data/distancias_vias.csv', index=False, encoding='utf-8')
print(f"\nProcessamento concluído! Total: {len(df_resultado)} linhas")
print(f"Com distância: {df_resultado['distancia'].notna().sum()}")
print(f"Sem distância: {df_resultado['distancia'].isna().sum()}")
