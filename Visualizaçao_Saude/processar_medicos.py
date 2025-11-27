import pandas as pd


df = pd.read_excel('medicos_por_bairro.xlsx')

print("Processando dados de médicos por bairro...")
print(f"Total de bairros: {len(df)}")


df['Médicos por Unidade de Saúde'] = df['Médico por U.S.'].round(2)
df['Proporção Médico por População'] = df['Proporção médico população'].round(6)
df['Índice OCDE'] = df['Indice OCDE'].round(4)


output_file = 'medicos_por_bairro_com_indices.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✓ Arquivo CSV criado: {output_file}")
print("\nPrimeiras linhas do resultado:")
print(df.head(10))


print("\n" + "="*80)
print("ANÁLISE DO ÍNDICE OCDE (valor >= 1.0 significa que atende ao padrão OCDE)")
print("="*80)
print(f"\nBairros que atendem ao padrão OCDE (≥ 3.5 médicos/1000 hab): {(df['Índice OCDE'] >= 1.0).sum()}")
print(f"Bairros abaixo do padrão OCDE: {(df['Índice OCDE'] < 1.0).sum()}")
print(f"\nÍndice OCDE médio: {df['Índice OCDE'].mean():.4f}")
print(f"Índice OCDE mediano: {df['Índice OCDE'].median():.4f}")
print(f"\nMelhor índice: {df['Índice OCDE'].max():.4f} - {df.loc[df['Índice OCDE'].idxmax(), 'Bairro']}")
print(f"Pior índice: {df['Índice OCDE'].min():.4f} - {df.loc[df['Índice OCDE'].idxmin(), 'Bairro']}")
