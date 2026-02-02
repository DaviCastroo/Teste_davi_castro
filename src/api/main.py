import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from src.api.schemas import (
    DespesaSchema,
    EstatisticasSchema,
    OperadoraSchema,
    PaginaOperadoras,
)

from ..database.loader import get_engine

app = FastAPI()
 
@app.get("/api/operadoras", response_model=PaginaOperadoras)
def list_operadoras(busca: str = Query("", min_length=0), page: int = Query(1, gt=0), limit: int = Query(10, le=100)):
    engine = get_engine
    offset = (page - 1) * limit

    sql_query = "SELECT * FROM operadoras ORDER BY registro_ans"

    # Obter total de registros
    total_query = "SELECT COUNT(*) as total FROM operadoras"
    if busca:
        total_query += f" WHERE razao_social ILIKE '%{busca}%' OR cnpj ILIKE '%{busca}%'"
    
    total_result = pd.read_sql(total_query, con=engine)
    total_registros = int(total_result['total'].iloc[0])
    
    # Aplicar paginação
    sql_query += f" LIMIT {limit} OFFSET {offset}"
    operadoras = pd.read_sql(sql_query, con=engine)
    
    # Converter CNPJ para string (garante compatibilidade com schema)
    operadoras['cnpj'] = operadoras['cnpj'].astype(str)

    return {
        "items": operadoras.to_dict(orient="records"),
        "total": total_registros,
        "pagina_atual": page,
        "tamanho_pagina": limit,
    }


@app.get("/api/despesas/{cnpj}", response_model=OperadoraSchema)
def list_operadora_cnpj(cnpj: str):
    engine = get_engine

    # Primeiro buscar o registro_ans pelo CNPJ
    sql_query = "SELECT * FROM operadoras WHERE cnpj = %s"
    operadora = pd.read_sql(sql_query, con=engine, params=(cnpj,))
    
    if operadora.empty:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
    operadora['cnpj'] = operadora['cnpj'].astype(str)
    return operadora.iloc[0].to_dict()


@app.get("/api/operadora/{cnpj}/despesas", response_model=list[DespesaSchema])
def list_despesas_operadora(cnpj: str):    
    engine = get_engine

    # Primeiro buscar o registro_ans pelo CNPJ
    sql_operadora = "SELECT * FROM operadoras WHERE cnpj = %s"
    operadora = pd.read_sql(sql_operadora, con=engine, params=(cnpj,))
    
    if operadora.empty:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    
    registro_ans = int(operadora.iloc[0]['registro_ans'])
    
    sql_despesas = f"SELECT * FROM despesas WHERE registro_ans = {registro_ans} ORDER BY ano, trimestre"
    despesas = pd.read_sql(sql_despesas, con=engine, params=(operadora.iloc[0]['registro_ans'],))

    if despesas.empty:
        return []
    
    return despesas.to_dict(orient="records")


@app.get("/api/estatisticas", response_model=EstatisticasSchema)
def get_estatisticas():
    engine = get_engine

    sql_total = """
        SELECT 
            SUM(valor_despesas) as total, 
            AVG(valor_despesas) as media 
        FROM despesas
    """

    df_geral = pd.read_sql(sql_total, con=engine)

    total = df_geral['total'].iloc[0]
    media = df_geral['media'].iloc[0]

    sql_top5 = """SELECT o.razao_social, 
    SUM(d.valor_despesas) as total 
    FROM despesas d JOIN operadoras o
    ON d.registro_ans = o.registro_ans 
    GROUP BY o.razao_social ORDER BY total 
    DESC LIMIT 5""" 
    
    df_top5 = pd.read_sql(sql_top5, con=engine)
    
    lista_top5 = df_top5.to_dict(orient="records")

    return {
        "total_geral": total,    
        "media_por_lancamento": media,
        "top_5": lista_top5
        }