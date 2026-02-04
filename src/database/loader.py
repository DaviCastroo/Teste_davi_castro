import os
import zipfile

import pandas as pd
from sqlalchemy import create_engine

from src.config import DB_CONNECTION, PROCESSED_DIR, RAW_DIR

string_conexao = DB_CONNECTION

get_engine = create_engine(string_conexao)

# TABELA OPERADORAS
df_operadoras = pd.read_csv(os.path.join(RAW_DIR, "Relatorio_cadop.csv"), sep=";", encoding="utf-8-sig")

df_operadoras_db = df_operadoras[["REGISTRO_OPERADORA", "CNPJ", "Razao_Social", "Modalidade", "UF"]].copy()

df_operadoras_db.columns = ["registro_ans", "cnpj", "razao_social", "modalidade", "uf"]

# Remover duplicatas, se houver (garante integridade, principio de normalização)
df_operadoras_db = df_operadoras_db.drop_duplicates(subset=["registro_ans"])

# Garantir que CNPJ seja texto (evita ser salvo como número)
df_operadoras_db['cnpj'] = df_operadoras_db['cnpj'].astype(str)

df_operadoras_db.to_sql('operadoras', con=get_engine, if_exists='replace', index=False)

# TABELA DESPESAS
with zipfile.ZipFile(os.path.join(PROCESSED_DIR, "Teste_davi_castro.zip")) as z:
    with z.open("despesas_agregadas_enriquecidas.csv") as f:
        df_despesas = pd.read_csv(f, sep=";")

df_despesas_db = df_despesas[["REGISTRO_OPERADORA", "Ano", "Trimestre", "ValorDespesas"]].copy()

df_despesas_db.columns = ["registro_ans", "ano", "trimestre", "valor_despesas"]

# Só podemos inserir despesas se o registro_ans existir na tabela operadoras.
# Filtra apenas os registros com registro_ans válido (evita erro de chave estrangeira)
ids_validos = set(df_operadoras_db["registro_ans"].unique())
df_despesas_db = df_despesas_db[df_despesas_db["registro_ans"].isin(ids_validos)]

# Mesmo principio de chunksize para evitar estouro de memória
df_despesas_db.to_sql('despesas', con=get_engine, if_exists='replace', index=False, chunksize=1000)

