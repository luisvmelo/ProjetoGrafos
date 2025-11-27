#!/usr/bin/env python3
"""CLI para execucao dos algoritmos do projeto de grafos"""

import argparse
import sys
from src.solve import executar_algoritmo_individual


def main():
    parser = argparse.ArgumentParser(
        description='Projeto de Grafos - Parte 1 e Parte 2'
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        help='Caminho para o dataset'
    )
    
    parser.add_argument(
        '--alg',
        choices=['BFS', 'DFS', 'DIJKSTRA', 'BELLMAN_FORD'],
        help='Algoritmo a ser executado'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Vertice de origem'
    )
    
    parser.add_argument(
        '--target',
        type=str,
        help='Vertice de destino'
    )
    
    parser.add_argument(
        '--out',
        type=str,
        default='./out/',
        help='Diretorio de saida'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Modo interativo'
    )
    
    parser.add_argument(
        '--visualizar',
        action='store_true',
        help='Gerar visualizacao da amostra do grafo'
    )
    
    parser.add_argument(
        '--comparar',
        action='store_true',
        help='Executar analise completa da Parte 2 (comparacao dos 4 algoritmos)'
    )
    
    args = parser.parse_args()
    
    if args.comparar:
        if not args.dataset or 'parte2' not in args.dataset:
            print("ERRO: --dataset ./data/dataset_parte2/ obrigatorio para comparacao")
            sys.exit(1)
        
        from src.solve import executar_analise_completa
        executar_analise_completa()
        return
    
    if args.visualizar:
        if not args.dataset or 'parte2' not in args.dataset:
            print("ERRO: --dataset ./data/dataset_parte2/ e obrigatorio para visualizacao")
            sys.exit(1)
        
        from src.graphs.io import carregar_dataset_parte2
        from src.viz import gerar_visualizacao_amostra_grafo
        
        grafo = carregar_dataset_parte2(args.dataset)
        gerar_visualizacao_amostra_grafo(grafo, num_vertices=50)
        print("out/parte2/amostra_grafo.html")
        return
    
    if args.dataset and 'parte2' in args.dataset:
        if not args.alg:
            print("ERRO: --alg e obrigatorio para Parte 2")
            print("Exemplo: python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source estacao_0 --target estacao_100")
            sys.exit(1)
        
        if not args.source:
            print("ERRO: --source e obrigatorio")
            print("Exemplo: python -m src.cli --dataset ./data/dataset_parte2/ --alg BFS --source estacao_0")
            sys.exit(1)
        
        if args.alg in ['DIJKSTRA', 'BELLMAN_FORD'] and not args.target:
            print(f"ERRO: --target e obrigatorio para {args.alg}")
            print(f"Exemplo: python -m src.cli --dataset ./data/dataset_parte2/ --alg {args.alg} --source estacao_0 --target estacao_100")
            sys.exit(1)
        
        out_dir = args.out if args.out != './out/' else './out/parte2'
        
        executar_algoritmo_individual(
            dataset_path=args.dataset,
            algoritmo=args.alg,
            source=args.source,
            target=args.target,
            out_dir=out_dir
        )
        return
    
    if args.interactive:
        print("Modo interativo ainda nao implementado")
        return
    
    if args.alg:
        print(f"Algoritmo {args.alg} selecionado")
        if args.source:
            print(f"  Origem: {args.source}")
        if args.target:
            print(f"  Destino: {args.target}")
        print("Implementacao pendente para Parte 1")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
