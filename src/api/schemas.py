from typing import List

from pydantic import BaseModel


# Esquema Operadora 
class OperadoraSchema(BaseModel):
    registro_ans: int
    cnpj: str
    razao_social: str
    modalidade: str
    uf: str

# Esquema Despesas 
class DespesaSchema(BaseModel):
    registro_ans: int
    ano: int
    trimestre: str
    valor_despesas: float

# Esquema de Paginação (Para a lista de operadoras)
# O Front precisa saber não só os dados, mas o total de páginas
class PaginaOperadoras(BaseModel):
    items: List[OperadoraSchema]
    total: int
    pagina_atual: int
    tamanho_pagina: int


class TopOperadorasSchema(BaseModel):
    razao_social: str
    total: float

# Esquema Estatísticas
class EstatisticasSchema(BaseModel):
    total_geral: float
    media_por_lancamento: float
    top_5: list[TopOperadorasSchema]