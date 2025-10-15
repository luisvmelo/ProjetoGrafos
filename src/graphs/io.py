# -*- coding: utf-8 -*-
"""
Processamento e normalizacao de dados de bairros do Recife por microrregiao.

Entrada: CSV com colunas numeradas (1.1, 1.2, etc.) contendo nomes de bairros.
Saida: Dois arquivos CSV com dados normalizados e deduplicados.

Requisitos: Python 3.11+, pandas
Autor: Luis Melo
Data: 2024
"""

import pandas as pd
import re
import unicodedata
import argparse
from pathlib import Path
from typing import Tuple, Dict, List
from dataclasses import dataclass


def carregar_csv(caminho: str) -> pd.DataFrame:
    """Carrega o CSV de entrada tratando encoding e erros."""
    path = Path(caminho)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    try:
        df = pd.read_csv(caminho, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, encoding='latin1')

    return df


def selecionar_colunas_microrregiao(df: pd.DataFrame) -> List[str]:
    """Retorna lista de colunas que seguem o padrao X.Y (microrregiao)."""
    pattern = re.compile(r'^\d+\.\d+$')
    return [col for col in df.columns if pattern.match(str(col).strip())]


def criar_aliases() -> Dict[str, str]:
    """Dicionario de substituicoes para normalizacao de nomes."""
    return {
        'sto.': 'Santo',
        'sto ': 'Santo ',
        'sta.': 'Santa',
        'sta ': 'Santa ',
        'vl.': 'Vila',
        'vl ': 'Vila ',
        'sr.': 'Senhor',
        'sra.': 'Senhora',
        'n.': 'Nossa',
        's.': 'Sao',
    }


def normalizar_bairro(nome: str, aliases: Dict[str, str]) -> str:
    """
    Aplica pipeline completo de normalizacao em um nome de bairro.

    Pipeline:
    1. Strip e limpeza de espacos
    2. Normalizacao de hifens
    3. Remocao de pontuacao final
    4. Remocao de parenteses informativos
    5. Aplicacao de aliases
    6. Normalizacao Unicode (NFC)
    7. Title Case inteligente
    8. Remocao de caracteres invisiveis
    """
    if pd.isna(nome) or not isinstance(nome, str):
        return ''

    # 1. Strip e colapsar espacos multiplos
    texto = nome.strip()
    texto = re.sub(r'\s+', ' ', texto)

    # 2. Padronizar hifens
    texto = texto.replace('–', '-').replace('—', '-')

    # 3. Remover pontuacao final nao informativa
    texto = re.sub(r'[.,;]+$', '', texto)

    # 4. Remover parenteses e conteudo (ex: "Bairro (Area 2)" -> "Bairro")
    texto = re.sub(r'\s*\([^)]*\)\s*', ' ', texto)
    texto = texto.strip()

    # 5. Aplicar aliases (antes do title case)
    texto_lower = texto.lower()
    for alias, substituicao in aliases.items():
        texto_lower = texto_lower.replace(alias, substituicao.lower())

    # 6. Normalizacao Unicode NFC
    texto_lower = unicodedata.normalize('NFC', texto_lower)

    # 7. Title Case inteligente (preposicoes em minusculas, exceto no inicio)
    preposicoes = {'de', 'da', 'do', 'dos', 'das', 'e', 'a', 'o'}
    palavras = texto_lower.split()

    resultado = []
    for i, palavra in enumerate(palavras):
        if i == 0 or palavra not in preposicoes:
            resultado.append(palavra.capitalize())
        else:
            resultado.append(palavra)

    texto_final = ' '.join(resultado)

    # 8. Remover caracteres invisiveis (NBSP, ZWSP, etc)
    texto_final = texto_final.replace('\u00A0', ' ')  # NBSP
    texto_final = texto_final.replace('\u200B', '')   # ZWSP
    texto_final = texto_final.replace('\ufeff', '')   # BOM

    # Limpeza final de espacos
    texto_final = re.sub(r'\s+', ' ', texto_final).strip()

    return texto_final


def derreter_dataframe(df: pd.DataFrame, colunas_micro: List[str]) -> pd.DataFrame:
    """
    Transforma colunas de microrregiao em formato longo (unpivot/melt).
    Retorna DataFrame com colunas: microrregiao, bairro
    """
    df_melted = df[colunas_micro].melt(
        var_name='microrregiao',
        value_name='bairro'
    )
    return df_melted


def processar_bairros(df_melted: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Normaliza bairros e gera os dois DataFrames de saida.

    Returns:
        Tuple com (df_unique, df_nos)
    """
    aliases = criar_aliases()

    # Normalizar todos os bairros
    df_melted['bairro_norm'] = df_melted['bairro'].apply(
        lambda x: normalizar_bairro(x, aliases)
    )

    # Remover linhas vazias
    df_limpo = df_melted[df_melted['bairro_norm'] != ''].copy()

    # bairros_unique: pares unicos (bairro, microrregiao)
    df_unique = df_limpo[['bairro_norm', 'microrregiao']].drop_duplicates()
    df_unique.columns = ['bairro', 'microrregiao']
    df_unique = df_unique.sort_values(['bairro', 'microrregiao']).reset_index(drop=True)

    # bairros_nos: apenas bairros unicos
    df_nos = df_limpo[['bairro_norm']].drop_duplicates()
    df_nos.columns = ['bairro']
    df_nos = df_nos.sort_values('bairro').reset_index(drop=True)

    return df_unique, df_nos


@dataclass
class EstatisticasProcessamento:
    """Estatisticas do processamento de bairros."""
    total_original: int
    total_apos_filtro: int
    pares_unicos: int
    bairros_unicos: int
    bairros_multiplas_micro: List[Tuple[str, int, List[str]]]
    top_microrregioes: List[Tuple[str, int]]


def calcular_estatisticas(df_melted: pd.DataFrame, df_unique: pd.DataFrame,
                          df_nos: pd.DataFrame) -> EstatisticasProcessamento:
    """Calcula estatisticas do processamento."""
    # Contagens basicas
    total_original = len(df_melted)
    total_apos_norm = len(df_melted[df_melted['bairro_norm'] != ''])
    total_unique = len(df_unique)
    total_nos = len(df_nos)

    # Bairros em multiplas microrregioes
    df_temp = df_unique.groupby('bairro').size().reset_index(name='count')
    df_multi = df_temp[df_temp['count'] > 1].sort_values('count', ascending=False)

    bairros_multi = []
    for _, row in df_multi.iterrows():
        micros = df_unique[df_unique['bairro'] == row['bairro']]['microrregiao'].tolist()
        bairros_multi.append((row['bairro'], row['count'], micros))

    # Top microrregioes
    df_top_micro = df_unique.groupby('microrregiao').size().reset_index(name='count')
    df_top_micro = df_top_micro.sort_values('count', ascending=False)
    top_micro = [(row['microrregiao'], row['count']) for _, row in df_top_micro.head(10).iterrows()]

    return EstatisticasProcessamento(
        total_original=total_original,
        total_apos_filtro=total_apos_norm,
        pares_unicos=total_unique,
        bairros_unicos=total_nos,
        bairros_multiplas_micro=bairros_multi,
        top_microrregioes=top_micro
    )


def gerar_relatorio(stats: EstatisticasProcessamento) -> None:
    """Imprime relatorio de qualidade no console."""
    print("\n" + "="*70)
    print("RELATORIO DE PROCESSAMENTO - BAIRROS DO RECIFE")
    print("="*70)

    print(f"\nRegistros processados:")
    print(f"  Linhas originais (apos melt): {stats.total_original:,}")
    print(f"  Linhas apos remover vazios:   {stats.total_apos_filtro:,}")
    print(f"  Pares unicos (bairro, micro): {stats.pares_unicos:,}")
    print(f"  Bairros unicos encontrados:   {stats.bairros_unicos:,}")

    if stats.bairros_multiplas_micro:
        print(f"\nBairros presentes em multiplas microrregioes ({len(stats.bairros_multiplas_micro)}):")
        for bairro, count, micros in stats.bairros_multiplas_micro[:10]:
            print(f"  - {bairro}: {count} microrregioes {micros}")
    else:
        print("\nNenhum bairro aparece em multiplas microrregioes")

    print(f"\nTop 10 microrregioes por quantidade de bairros:")
    for micro, count in stats.top_microrregioes:
        print(f"  {micro:>6s}: {count:3d} bairros")

    print("\n" + "="*70)


def salvar_csv(df: pd.DataFrame, caminho: str):
    """Salva DataFrame como CSV com UTF-8 BOM."""
    df.to_csv(caminho, index=False, encoding='utf-8-sig')


def validar_ambiente() -> None:
    """Valida que o ambiente atende aos requisitos minimos."""
    import sys
    if sys.version_info < (3, 11):
        raise RuntimeError(
            f"Python 3.11+ necessario. Versao atual: {sys.version_info.major}.{sys.version_info.minor}"
        )


def processar_arquivo(caminho_entrada: str, silencioso: bool = False) -> Tuple[Path, Path]:
    """
    Processa o arquivo CSV de entrada e gera os arquivos de saida.

    Args:
        caminho_entrada: Caminho para o CSV de entrada
        silencioso: Se True, suprime mensagens de progresso

    Returns:
        Tuple com os caminhos dos arquivos gerados (unique, nos)
    """
    def log(msg: str) -> None:
        if not silencioso:
            print(msg)

    # Configurar caminhos de saida
    dir_saida = Path(caminho_entrada).parent
    caminho_unique = dir_saida / "bairros_unique.csv"
    caminho_nos = dir_saida / "bairros_nos.csv"

    # Processar
    log(f"Carregando arquivo: {caminho_entrada}")
    df = carregar_csv(caminho_entrada)

    log("Identificando colunas de microrregiao...")
    colunas_micro = selecionar_colunas_microrregiao(df)
    log(f"Encontradas {len(colunas_micro)} colunas: {', '.join(colunas_micro[:5])}...")

    log("Transformando dados (unpivot/melt)...")
    df_melted = derreter_dataframe(df, colunas_micro)

    log("Normalizando nomes de bairros...")
    df_unique, df_nos = processar_bairros(df_melted)

    log(f"\nSalvando arquivos:")
    salvar_csv(df_unique, str(caminho_unique))
    log(f"  -> {caminho_unique}")

    salvar_csv(df_nos, str(caminho_nos))
    log(f"  -> {caminho_nos}")

    # Gerar relatorio
    stats = calcular_estatisticas(df_melted, df_unique, df_nos)
    gerar_relatorio(stats)

    log("\nProcessamento concluido com sucesso!")

    return caminho_unique, caminho_nos


def main() -> None:
    """Funcao principal do script."""
    parser = argparse.ArgumentParser(
        description="Processa e normaliza dados de bairros do Recife por microrregiao",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python io.py
  python io.py --input C:\\Users\\luise\\Downloads\\bairros_recife.csv
  python io.py --input dados.csv --quiet

Saidas geradas (no mesmo diretorio da entrada):
  - bairros_unique.csv: pares unicos (bairro, microrregiao)
  - bairros_nos.csv: lista unica de bairros normalizados
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        default="/mnt/c/Users/luise/Downloads/bairros_recife.csv",
        help='Caminho para o arquivo CSV de entrada (padrao: /mnt/c/Users/luise/Downloads/bairros_recife.csv)'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso (suprime mensagens de progresso)'
    )

    args = parser.parse_args()

    try:
        validar_ambiente()
        processar_arquivo(args.input, silencioso=args.quiet)

    except FileNotFoundError as e:
        print(f"\nErro: {e}")
        print("Verifique se o caminho do arquivo esta correto.")
        exit(1)

    except RuntimeError as e:
        print(f"\nErro de ambiente: {e}")
        exit(1)

    except Exception as e:
        print(f"\nErro inesperado durante o processamento:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
