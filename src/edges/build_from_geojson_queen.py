# -*- coding: utf-8 -*-
"""
Gera grafo de adjacencias entre bairros do Recife a partir de GeoJSON.

Criterio QUEEN: dois bairros sao adjacentes se compartilham pelo menos um vertice.
Usa apenas biblioteca padrao Python (sem shapely/geopandas/networkx).

Autor: Luis Melo
Data: 2024
"""

import json
import argparse
import unicodedata
from pathlib import Path
from typing import Set, Tuple, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Estatisticas:
    """Estatisticas do processamento."""
    total_nodes_csv: int
    total_mapeados: int
    nao_mapeados: List[str]
    total_arestas: int


def normalizar_nome(nome: str) -> str:
    """
    Normaliza nome para comparacao (lowercase, sem acento, trim, colapsar espacos).
    """
    if not nome:
        return ""

    # Trim e colapsar espacos
    texto = " ".join(nome.split())

    # Lowercase
    texto = texto.lower()

    # Remover acentos (NFD decompose + filtrar)
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    return texto


def criar_aliases() -> Dict[str, str]:
    """
    Aliases para matching de nomes.
    Retorna dict: nome_normalizado_csv -> nome_normalizado_geojson
    """
    return {
        normalizar_nome("Alto Santa Teresinha"): normalizar_nome("Alto Santa Terezinha"),
        normalizar_nome("Pau-Ferro"): normalizar_nome("Pau Ferro"),
        normalizar_nome("Sitio Dos Pintos"): normalizar_nome("Sítio Dos Pintos - São Brás"),
        normalizar_nome("Cohab"): normalizar_nome("Cohab - Ibura De Cima"),
    }


def extrair_vertices_geometria(geom: dict, ndigits: int = 6) -> Set[Tuple[float, float]]:
    """
    Extrai todos os vertices de uma geometria (Polygon ou MultiPolygon).
    Arredonda coordenadas para ndigits casas decimais.
    """
    vertices = set()

    geom_type = geom.get("type", "")
    coords = geom.get("coordinates", [])

    if geom_type == "Polygon":
        # Polygon: lista de aneis (cada anel = lista de [lon, lat])
        for anel in coords:
            for ponto in anel:
                if len(ponto) >= 2:
                    lon = round(float(ponto[0]), ndigits)
                    lat = round(float(ponto[1]), ndigits)
                    vertices.add((lon, lat))

    elif geom_type == "MultiPolygon":
        # MultiPolygon: lista de poligonos
        for poligono in coords:
            for anel in poligono:
                for ponto in anel:
                    if len(ponto) >= 2:
                        lon = round(float(ponto[0]), ndigits)
                        lat = round(float(ponto[1]), ndigits)
                        vertices.add((lon, lat))

    return vertices


def carregar_geojson(caminho: str, ndigits: int) -> Dict[str, Set[Tuple[float, float]]]:
    """
    Carrega GeoJSON e retorna dict: nome_normalizado -> set de vertices.
    Prioriza EBAIRRNOMEOF, fallback EBAIRRNOME.
    """
    with open(caminho, 'r', encoding='utf-8') as f:
        data = json.load(f)

    bairros_geo = {}

    features = data.get("features", [])
    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})

        # Priorizar EBAIRRNOMEOF
        nome = props.get("EBAIRRNOMEOF") or props.get("EBAIRRNOME") or ""
        if not nome:
            continue

        nome_norm = normalizar_nome(nome)
        vertices = extrair_vertices_geometria(geom, ndigits)

        if nome_norm in bairros_geo:
            # Merge vertices se mesmo bairro aparece multiplas vezes
            bairros_geo[nome_norm].update(vertices)
        else:
            bairros_geo[nome_norm] = vertices

    return bairros_geo


def carregar_nodes_csv(caminho: str) -> List[str]:
    """
    Carrega bairros_unique.csv e retorna lista de nomes ORIGINAIS unicos.
    """
    bairros = set()

    with open(caminho, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Pular header
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # CSV: bairro,microrregiao
        parts = line.split(',', 1)
        if parts:
            bairro = parts[0].strip()
            if bairro:
                bairros.add(bairro)

    return sorted(bairros)


def mapear_bairros(
    bairros_csv: List[str],
    bairros_geo: Dict[str, Set[Tuple[float, float]]],
    aliases: Dict[str, str]
) -> Tuple[Dict[str, str], List[str]]:
    """
    Mapeia bairros do CSV para nomes normalizados no GeoJSON.

    Returns:
        (mapa: nome_csv -> nome_normalizado_geo, lista de nao mapeados)
    """
    mapa = {}
    nao_mapeados = []

    for bairro in bairros_csv:
        nome_norm = normalizar_nome(bairro)

        # Tentar match direto
        if nome_norm in bairros_geo:
            mapa[bairro] = nome_norm
            continue

        # Tentar via alias
        if nome_norm in aliases:
            nome_alias = aliases[nome_norm]
            if nome_alias in bairros_geo:
                mapa[bairro] = nome_alias
                continue

        # Nao encontrado
        nao_mapeados.append(bairro)

    return mapa, nao_mapeados


def calcular_adjacencias(
    bairros_csv: List[str],
    mapa: Dict[str, str],
    bairros_geo: Dict[str, Set[Tuple[float, float]]]
) -> List[Tuple[str, str]]:
    """
    Calcula adjacencias (criterio QUEEN: vertices compartilhados).
    Retorna lista de arestas (bairro_origem, bairro_destino) ordenadas.
    """
    arestas = set()

    # Filtrar apenas bairros mapeados
    bairros_validos = [b for b in bairros_csv if b in mapa]

    # Comparar todos os pares
    for i, bairro_a in enumerate(bairros_validos):
        nome_geo_a = mapa[bairro_a]
        vertices_a = bairros_geo[nome_geo_a]

        for bairro_b in bairros_validos[i+1:]:
            nome_geo_b = mapa[bairro_b]
            vertices_b = bairros_geo[nome_geo_b]

            # QUEEN: intersecao de vertices nao vazia
            if vertices_a & vertices_b:
                # Ordenar para evitar duplicatas (A,B) e (B,A)
                origem, destino = sorted([bairro_a, bairro_b])
                arestas.add((origem, destino))

    return sorted(arestas)


def salvar_csv_adjacencias(arestas: List[Tuple[str, str]], caminho: str) -> None:
    """
    Salva CSV de adjacencias (UTF-8-SIG).
    """
    # Criar diretorio se nao existir
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, 'w', encoding='utf-8-sig', newline='') as f:
        # Header
        f.write("bairro_origem,bairro_destino,logradouro,observacao,peso\n")

        # Dados
        for origem, destino in arestas:
            f.write(f'{origem},{destino},"","contato por vértice (queen) — fronteira compartilhada",1.0\n')


def processar(
    geojson_path: str,
    nodes_path: str,
    output_path: str,
    ndigits: int
) -> Estatisticas:
    """
    Funcao principal de processamento.
    """
    print(f"Carregando GeoJSON: {geojson_path}")
    bairros_geo = carregar_geojson(geojson_path, ndigits)
    print(f"  -> {len(bairros_geo)} bairros encontrados no GeoJSON")

    print(f"\nCarregando nodes CSV: {nodes_path}")
    bairros_csv = carregar_nodes_csv(nodes_path)
    print(f"  -> {len(bairros_csv)} bairros unicos no CSV")

    print(f"\nMapeando nomes (com aliases)...")
    aliases = criar_aliases()
    mapa, nao_mapeados = mapear_bairros(bairros_csv, bairros_geo, aliases)
    print(f"  -> {len(mapa)} bairros mapeados")

    if nao_mapeados:
        print(f"  -> {len(nao_mapeados)} bairros NAO mapeados:")
        for b in nao_mapeados:
            print(f"     - {b}")

    print(f"\nCalculando adjacencias (criterio QUEEN, ndigits={ndigits})...")
    arestas = calcular_adjacencias(bairros_csv, mapa, bairros_geo)
    print(f"  -> {len(arestas)} arestas encontradas")

    print(f"\nSalvando: {output_path}")
    salvar_csv_adjacencias(arestas, output_path)

    return Estatisticas(
        total_nodes_csv=len(bairros_csv),
        total_mapeados=len(mapa),
        nao_mapeados=nao_mapeados,
        total_arestas=len(arestas)
    )


def main() -> None:
    """CLI principal."""
    parser = argparse.ArgumentParser(
        description="Gera grafo de adjacencias entre bairros (criterio QUEEN) a partir de GeoJSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplo de uso (Windows):
  python src/edges/build_from_geojson_queen.py ^
    --geojson "C:\\Users\\luise\\Downloads\\bvisualizacao_fcbairro.geojson" ^
    --nodes "C:\\Users\\luise\\Downloads\\bairros_unique.csv" ^
    --out "data\\adjacencias_bairros.csv"

Exemplo de uso (Linux/WSL):
  python src/edges/build_from_geojson_queen.py \\
    --geojson /mnt/c/Users/luise/Downloads/bvisualizacao_fcbairro.geojson \\
    --nodes /mnt/c/Users/luise/Downloads/bairros_unique.csv \\
    --out data/adjacencias_bairros.csv
        """
    )

    parser.add_argument(
        '--geojson',
        type=str,
        default="/mnt/c/Users/luise/Downloads/bvisualizacao_fcbairro.geojson",
        help='Caminho para o arquivo GeoJSON de entrada'
    )

    parser.add_argument(
        '--nodes',
        type=str,
        default="/mnt/c/Users/luise/Downloads/bairros_unique.csv",
        help='Caminho para o CSV de bairros unicos'
    )

    parser.add_argument(
        '--out',
        type=str,
        default="data/adjacencias_bairros.csv",
        help='Caminho para o CSV de adjacencias de saida'
    )

    parser.add_argument(
        '--ndigits',
        type=int,
        default=6,
        help='Casas decimais para arredondamento de coordenadas (default: 6)'
    )

    args = parser.parse_args()

    try:
        stats = processar(
            geojson_path=args.geojson,
            nodes_path=args.nodes,
            output_path=args.out,
            ndigits=args.ndigits
        )

        print("\n" + "="*70)
        print("RESUMO DO PROCESSAMENTO")
        print("="*70)
        print(f"Total de bairros no CSV:     {stats.total_nodes_csv}")
        print(f"Total mapeados no GeoJSON:   {stats.total_mapeados}")
        print(f"Total nao mapeados:          {len(stats.nao_mapeados)}")
        print(f"Total de arestas geradas:    {stats.total_arestas}")
        print("="*70)

        print("\nProcessamento concluido com sucesso!")

    except FileNotFoundError as e:
        print(f"\nErro: Arquivo nao encontrado - {e}")
        exit(1)

    except Exception as e:
        print(f"\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
