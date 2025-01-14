import pandas as pd
import os

# Pasta onde estão os CSVs
pasta_csvs = "csvs"

# Nome do arquivo de saída
arquivo_saida = "medicos_mg.csv"

# Lista para armazenar os DataFrames
dataframes = []

# Percorrer todos os arquivos na pasta
for arquivo in os.listdir(pasta_csvs):
    if arquivo.endswith(".csv"):  # Verifica se é um arquivo CSV
        caminho_arquivo = os.path.join(pasta_csvs, arquivo)
        print(f"Lendo {arquivo}...")
        df = pd.read_csv(caminho_arquivo)
        dataframes.append(df)

# Concatenar todos os DataFrames em um só
df_unido = pd.concat(dataframes, ignore_index=True)

# Salvar o DataFrame unido em um novo arquivo CSV
df_unido.to_csv(arquivo_saida, index=False)

print(f"Todos os arquivos CSV foram unidos em '{arquivo_saida}'.")
