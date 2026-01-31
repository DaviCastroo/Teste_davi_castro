import os
import zipfile
from decimal import Decimal
from io import StringIO

import pandas as pd


def valida_cnpj(cnpj):
    # Limpa o dado: mantém apenas números, caso algum arquivo venha com formatação de um cnpj (11.222.333/0001-44)
    cnpj = "".join(filter(str.isdigit, str(cnpj)))

    # verifica se o CNPJ tem 14 dígitos.Verifica o conjunto (set) dos numeros, ou seja, se apresentar apenas um conjunto, signifca que todos os digitos sao iguais
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False  # CNPJ inválido

    # Função interna para calcular cada dígito

    def calcular_digito(fatia, pesos):
        soma = sum(int(num) * peso for num, peso in zip(fatia, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Pesos oficiais da Receita Federal
    digito13 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]  # Para o 13º dígito
    digito14 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]  # Para o 14º dígito

    # Verifica o primeiro dígito verificador (13º digito)
    if int(cnpj[12]) != calcular_digito(cnpj[:12], digito13):
        return False

    # Verifica o segundo dígito verificador (14º posição)
    if int(cnpj[13]) != calcular_digito(cnpj[:13], digito14):
        return False

    return True


# Obter o diretório do script para resolver caminhos de forma absoluta e evitar problemas de leitura de arquivos
script_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Preparação dos Mapas (Lookup Tables)
arquivo_operadoras_df = pd.read_csv(
    os.path.join(script_dir, "Relatorio_cadop.csv"),
    sep=",",
    encoding="latin1",
    dtype={"CNPJ": str},
)
arquivo_operadoras = arquivo_operadoras_df.set_index("REGISTRO_OPERADORA").to_dict(
    "index"
)

mapa_mes_tri = {
    1: "1T",
    2: "1T",
    3: "1T",
    4: "2T",
    5: "2T",
    6: "2T",
    7: "3T",
    8: "3T",
    9: "3T",
    10: "4T",
    11: "4T",
    12: "4T",
}

# Lista de arquivos trimestrais; 1.2
arquivos = [
    os.path.join(script_dir, "1T2025.csv"),
    os.path.join(script_dir, "2T2025.csv"),
    os.path.join(script_dir, "3T2025.csv"),
]

mapa_cnpj = {ans: dados["CNPJ"] for ans, dados in arquivo_operadoras.items()}
mapa_razao = {ans: dados["Razao_Social"] for ans, dados in arquivo_operadoras.items()}


def consolidar_dados_despesas(lista_arquivos_trimestrais):
    lista_despesas = []

    for arquivo in lista_arquivos_trimestrais:
        # Processamento incremental (Chunking) para eficiência de memória
        for bloco in pd.read_csv(arquivo, chunksize=100000, sep=";", encoding="UTF-8"):
            # Conversão de data e extração de Ano/Trimestre
            datas = pd.to_datetime(bloco["DATA"], errors="coerce")
            bloco["ANO"] = datas.dt.year
            bloco["TRIMESTRE"] = datas.dt.month.map(mapa_mes_tri)

            # Filtro resiliente: apenas despesas com sinistros (prefixo 411)
            bloco["CD_CONTA_CONTABIL"] = bloco["CD_CONTA_CONTABIL"].astype(str)
            bloco = bloco[bloco["CD_CONTA_CONTABIL"].str.startswith("411")].copy()

            # Mapeamento de CNPJ e Razão Social através do Join, utilizando o REG_ANS
            bloco["CNPJ"] = bloco["REG_ANS"].map(mapa_cnpj)

            # Valida os cnpjs
            cnpjs_validos = bloco["CNPJ"].apply(valida_cnpj)
            bloco = bloco[cnpjs_validos].copy()  # Remove CNPJs inválidos

            bloco["RAZAO_SOCIAL"] = bloco["REG_ANS"].map(mapa_razao)

            # Tratamento de CNPJs não encontrados (Inconsistências)
            bloco["RAZAO_SOCIAL"] = bloco["RAZAO_SOCIAL"].fillna(
                "RAZAO NAO IDENTIFICADA"
            )

            # Conversão numérica (Troca a vírgula por ponto, devido ao formato que a linguagem entende, que é utilizando o ponto)
            if bloco["VL_SALDO_FINAL"].dtype == object:
                bloco["VL_SALDO_FINAL"] = (
                    bloco["VL_SALDO_FINAL"].str.replace(",", ".").apply(Decimal)
                )  # Uso do tipo de dado "decimal" para manter a precisão

            # Agregação local (reduz o tamanho da lista_despesas)
            lista_despesas.append(bloco)

    # Consolidação Global dos dados
    df_despesas_consolidadas = pd.concat(lista_despesas, ignore_index=True)
    resultado_final = (
        df_despesas_consolidadas.groupby(["CNPJ", "RAZAO_SOCIAL", "ANO", "TRIMESTRE"])[
            "VL_SALDO_FINAL"
        ]
        .sum()
        .reset_index()
    )

    # Renomeação das colunas conforme exigência do item 1.3
    resultado_final.columns = [
        "CNPJ",
        "RazaoSocial",
        "Ano",
        "Trimestre",
        "Valor Despesas",
    ]
    return resultado_final


df_final = consolidar_dados_despesas(arquivos)

# Enriquecimento dos dados
df_final_enriquecido = pd.merge(
    df_final, arquivo_operadoras_df[["CNPJ", "Modalidade", "UF"]], on="CNPJ", how="left"
)

df_final_enriquecido["Modalidade"] = df_final_enriquecido["Modalidade"].fillna(
    "NAO IDENTIFICADA"
)
df_final_enriquecido["UF"] = df_final_enriquecido["UF"].fillna("NAO IDENTIFICADA")

# Salvar diretamente no zip, sem criar arquivos no disco
with zipfile.ZipFile(
    os.path.join(script_dir, "Teste_davi_castro.zip"), "w", zipfile.ZIP_DEFLATED
) as zipf:
    # Escrever arquivo 1 no zip
    buffer1 = StringIO()
    df_final.to_csv(buffer1, index=False, sep=";", encoding="utf-8-sig", quoting=1)
    zipf.writestr("despesas_consolidadas.csv", buffer1.getvalue())

    # Escrever arquivo 2 no zip
    buffer2 = StringIO()
    df_final_enriquecido.to_csv(
        buffer2,
        index=False,
        sep=";",
        encoding="utf-8-sig",
        quoting=1,
    )
    zipf.writestr("despesas_consolidadas_enriquecidas.csv", buffer2.getvalue())
