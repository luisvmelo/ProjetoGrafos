import pandas as pd
import re
from .graph import GrafoDirecionado

def normalizar_nome(nome):
    if pd.isna(nome):
        return None
    texto = str(nome).strip()
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.replace('–', '-').replace('—', '-')
    texto = re.sub(r'[.,;]+$', '', texto)
    texto = re.sub(r'\s*\([^)]*\)\s*', ' ', texto).strip()

    texto_lower = texto.lower()
    aliases = {
        'sto.': 'santo',
        'sto ': 'santo ',
        'sta.': 'santa',
        'sta ': 'santa ',
        'vl.': 'vila',
        'vl ': 'vila ',
        'sr.': 'senhor',
        'sra.': 'senhora',
        'n.': 'nossa',
        's.': 'são',
    }
    for alias, sub in aliases.items():
        texto_lower = texto_lower.replace(alias, sub)

    preposicoes = {'de', 'da', 'do', 'dos', 'das', 'e', 'a', 'o'}
    palavras = texto_lower.split()
    resultado = []
    for i, palavra in enumerate(palavras):
        if i == 0 or palavra not in preposicoes:
            resultado.append(palavra.capitalize())
        else:
            resultado.append(palavra)

    return ' '.join(resultado)


def carregar_dataset_parte2(caminho='data/dataset_parte2/dataset_parte2_grafos.csv'):
    """Carrega o dataset da Parte 2 em um grafo direcionado"""
    import os
    
    if os.path.isdir(caminho):
        caminho = os.path.join(caminho, 'dataset_parte2_grafos.csv')
    
    df = pd.read_csv(caminho)
    
    grafo = GrafoDirecionado()
    
    for _, row in df.iterrows():
        origem = row['origem']
        destino = row['destino']
        peso = row['peso']
        
        info = {
            'tempo': row.get('tempo'),
            'linha': row.get('linha'),
            'tipo_via': row.get('tipo_via'),
            'distancia_m': row.get('distancia_m')
        }
        
        grafo.adicionar_aresta(origem, destino, peso, info)
    
    return grafo


if __name__ == '__main__':
    df = pd.read_excel('data/bairros_recife.xlsx')

    df_melted = df.melt(var_name='microrregiao', value_name='bairro')
    df_melted['bairro'] = df_melted['bairro'].apply(normalizar_nome)
    df_limpo = df_melted.dropna(subset=['bairro'])

    agrupado = df_limpo.groupby('bairro')['microrregiao'].apply(lambda x: ' / '.join(sorted(set(x.astype(str))))).reset_index()
    agrupado.columns = ['bairro', 'microrregião']
    agrupado = agrupado.sort_values('bairro').reset_index(drop=True)

    agrupado.to_csv('data/bairros_unique.csv', index=False, sep=';', encoding='utf-8-sig')
