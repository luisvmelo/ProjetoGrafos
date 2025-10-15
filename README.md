# Projeto Grafos - Bairros do Recife

Implementacao de algoritmos de grafos aplicados ao mapeamento de bairros da cidade do Recife.

## Estrutura

```
projeto-grafos/
├── data/               # Dados de entrada e intermediarios
├── out/                # Saidas geradas (visualizacoes, JSONs)
├── src/
│   ├── edges/         # Processamento de arestas/adjacencias
│   ├── graphs/        # Estruturas de dados e algoritmos
│   └── viz.py         # Visualizacoes
└── tests/             # Testes unitarios
```

## Requisitos

- Python 3.11+
- pandas

```bash
pip install pandas
```

## Uso

### 1. Processar bairros (normalizacao)

```bash
python src/graphs/io.py --input bairros_recife.csv
```

### 2. Gerar adjacencias (criterio QUEEN)

```bash
python src/edges/build_from_geojson_queen.py \
  --geojson bvisualizacao_fcbairro.geojson \
  --nodes bairros_unique.csv \
  --out data/adjacencias_bairros.csv
```

## Autor

Luis Melo
