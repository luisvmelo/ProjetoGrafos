import pandas as pd


xls = pd.ExcelFile('educacao_bairros_microrregioes.xlsx')


print("Processando dados de educação por bairro...")
df_bairros = pd.read_excel(xls, sheet_name='bairros')


print(f"Total de bairros: {len(df_bairros)}")


df_bairros.to_csv('educacao_bairros.csv', index=False, encoding='utf-8-sig')
print(f"\n✓ Arquivo CSV de bairros criado: educacao_bairros.csv")


print("\nProcessando dados de educação por microrregião...")
df_micro = pd.read_excel(xls, sheet_name='microrregioes')

print(f"Total de microrregiões: {len(df_micro)}")


df_micro.to_csv('educacao_microrregioes.csv', index=False, encoding='utf-8-sig')
print(f"✓ Arquivo CSV de microrregiões criado: educacao_microrregioes.csv")


print("\n" + "="*80)
print("ANÁLISE DOS DADOS DE EDUCAÇÃO")
print("="*80)
print(f"\nBairros por categoria de analfabetismo:")
print(df_bairros['faixa_analfabetismo'].value_counts().to_string())

print(f"\nMicrorregiões por categoria de analfabetismo:")
print(df_micro['faixa_analfabetismo'].value_counts().to_string())

print(f"\nTaxa de analfabetismo (bairros):")
print(f"  Média: {df_bairros['Taxa_Analfabetismo_%'].mean():.2f}%")
print(f"  Mínima: {df_bairros['Taxa_Analfabetismo_%'].min():.2f}% - {df_bairros.loc[df_bairros['Taxa_Analfabetismo_%'].idxmin(), 'bairro']}")
print(f"  Máxima: {df_bairros['Taxa_Analfabetismo_%'].max():.2f}% - {df_bairros.loc[df_bairros['Taxa_Analfabetismo_%'].idxmax(), 'bairro']}")
