import os
import zipfile
from decimal import Decimal
from io import StringIO

import pandas as pd
from validate_docbr import CNPJ

from config import PROCESSED_DIR, RAW_DIR

cnpj = CNPJ()

def salvar_zip_com_dados(df1, df2, df3, caminho_zip):
    # Salvar diretamente no zip, sem criar arquivos no disco
    with zipfile.ZipFile(
        os.path.join(PROCESSED_DIR, "Teste_davi_castro.zip"), "w", zipfile.ZIP_DEFLATED
    ) as zipf:
        # Escrever arquivo 1 no zip
        buffer1 = StringIO()
        df1.to_csv(buffer1, index=False, sep=";", encoding="latin1", quoting=1)
        zipf.writestr("despesas_consolidadas.csv", buffer1.getvalue())

        # Escrever arquivo 2 no zip
        buffer2 = StringIO()
        df2.to_csv(buffer2, index=False, sep=";", encoding="latin1", quoting=1,)
        zipf.writestr("despesas_consolidadas_enriquecidas.csv", buffer2.getvalue())

        buffer3 = StringIO()
        df3.to_csv(buffer3, index=False, sep=";", encoding="utf-8", quoting=1)
        zipf.writestr("despesas_agregadas.csv", buffer3.getvalue())


# Obter o diretório do script para resolver caminhos de forma absoluta e evitar problemas de leitura de arquivos

# Preparação dos Mapas (Lookup Tables)
arquivo_operadoras_df = pd.read_csv(
    os.path.join(RAW_DIR, "Relatorio_cadop.csv"),
    sep=",",
    encoding="utf-8-sig",
    dtype={"CNPJ": str},
)
arquivo_operadoras = arquivo_operadoras_df.set_index("REGISTRO_OPERADORA").to_dict(
    "index"
)

mapa_mes_tri = {
    1: "1T", 2: "1T", 3: "1T",
    4: "2T", 5: "2T", 6: "2T",
    7: "3T", 8: "3T", 9: "3T",
    10: "4T", 11: "4T", 12: "4T",
}

# Lista de arquivos trimestrais; 1.2
arquivos = [
    os.path.join(RAW_DIR, "1T2025.csv"),
    os.path.join(RAW_DIR, "2T2025.csv"),
    os.path.join(RAW_DIR, "3T2025.csv"),
]

mapa_cnpj = {ans: dados["CNPJ"] for ans, dados in arquivo_operadoras.items()}
mapa_razao = {ans: dados["Razao_Social"] for ans, dados in arquivo_operadoras.items()}


def consolidar_dados_despesas(lista_arquivos_trimestrais):
    lista_despesas = []

    for arquivo in lista_arquivos_trimestrais:
        # Processamento incremental (Chunking) para eficiência de memória
        for bloco in pd.read_csv(arquivo, chunksize=100000, sep=";", encoding="UTF-8"):
            resumo_bloco = []
            
            # Conversão de data e extração de Ano/Trimestre
            datas = pd.to_datetime(bloco["DATA"], errors="coerce")
            bloco["ANO"] = datas.dt.year
            bloco["TRIMESTRE"] = datas.dt.month.map(mapa_mes_tri)

            # Filtro resiliente: apenas despesas com sinistros (prefixo 411)
            bloco["CD_CONTA_CONTABIL"] = bloco["CD_CONTA_CONTABIL"].astype(str)
            bloco = bloco[bloco["CD_CONTA_CONTABIL"].str.startswith("411")].copy()

            # Mapeamento de CNPJ e Razão Social através do Join, utilizando o REG_ANS
            bloco["CNPJ"] = bloco["REG_ANS"].map(mapa_cnpj)

            bloco = bloco[bloco["CNPJ"].notna()].copy()  # Copia os regisos com CNPJ mapeado
            
            # Valida os cnpjs
            cnpjs_validos = bloco["CNPJ"].apply(cnpj.validate)
            bloco = bloco[cnpjs_validos].copy()  # Remove CNPJs inválidos

            bloco["RAZAO_SOCIAL"] = bloco["REG_ANS"].map(mapa_razao)

            # Tratamento de CNPJs não encontrados (Inconsistências)
            bloco["RAZAO_SOCIAL"] = bloco["RAZAO_SOCIAL"].fillna(
                "RAZAO NAO IDENTIFICADA"
            )

            # Conversão numérica (Troca a vírgula por ponto, devido ao formato que a linguagem entende, que é utilizando o ponto)
            if bloco["VL_SALDO_FINAL"].dtype == object:
                bloco["VL_SALDO_FINAL"] = (bloco["VL_SALDO_FINAL"].str.replace(",", ".").apply(Decimal)
            )  

            #AGREGAÇÃO LOCAL DOS DADOS (DENTRO DO LOOP DE CHUNKS)
            resumo_bloco = bloco.groupby(["CNPJ", "RAZAO_SOCIAL", "ANO", "TRIMESTRE"])["VL_SALDO_FINAL"].sum().reset_index() # Agrupamento e soma das despesas no bloco atual, evita manter dados desnecessários na memória
            # Agregação local (reduz o tamanho da lista_despesas)
            lista_despesas.append(resumo_bloco)

    # Consolidação Global dos dados
    df_despesas_consolidadas = pd.concat(lista_despesas, ignore_index=True)
    
    resultado_final = df_despesas_consolidadas.groupby(["CNPJ", "RAZAO_SOCIAL", "ANO", "TRIMESTRE"])["VL_SALDO_FINAL"].sum().reset_index()

    # Renomeação das colunas conforme exigência do item 1.3
    resultado_final.columns = ["CNPJ","RazaoSocial","Ano","Trimestre","ValorDespesas"]

    return resultado_final

# Chamada da função de consolidação
df_final = consolidar_dados_despesas(arquivos)

# Enriquecimento dos dados
df_final_enriquecido = pd.merge(df_final, arquivo_operadoras_df[["CNPJ", "REGISTRO_OPERADORA", "Modalidade", "UF"]], on="CNPJ", how="left")

df_final_enriquecido["Modalidade"] = df_final_enriquecido["Modalidade"].fillna("NAO IDENTIFICADA")
df_final_enriquecido["UF"] = df_final_enriquecido["UF"].fillna("NAO IDENTIFICADA")

df_agregado = df_final_enriquecido.groupby(["RazaoSocial", "UF"])["ValorDespesas"].agg(Total_Despesas='sum', Media_Trimestral='mean', Desvio_Padrao='std').reset_index()
df_agregado = df_agregado.sort_values(by="Total_Despesas", ascending=False)

salvar_zip_com_dados(df_final, df_final_enriquecido,df_agregado, PROCESSED_DIR)
