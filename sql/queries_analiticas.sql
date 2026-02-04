-- ----------------------------------------------------------------------------
-- QUERY 1: Top 5 operadoras com maior crescimento de despesas (1T -> 3T)
-- ----------------------------------------------------------------------------
-- Utilizamos INNER JOIN para considerar apenas operadoras que reportaram dados
-- em AMBOS os períodos (1T e 3T), garantindo a comparabilidade.
-- Filtro de despesas do 1T > 1000 para evitar distorções matemáticas de 
-- "crescimento infinito" em operadoras que saíram de R$ 0 ou valores irrisórios.

WITH despesas_1t AS (
    SELECT registro_ans, valor_despesas 
    FROM despesas 
    WHERE ano = 2025 AND trimestre = '1T' 
      AND valor_despesas > 1000 -- Filtro de consistência
),
despesas_3t AS (
    SELECT registro_ans, valor_despesas 
    FROM despesas 
    WHERE ano = 2025 AND trimestre = '3T'
)
SELECT 
    o.razao_social,
    d1.valor_despesas AS despesas_1t,
    d3.valor_despesas AS despesas_3t,
    -- Cálculo: (Valor Final - Valor Inicial) / Valor Inicial * 100
    ROUND(
        ((d3.valor_despesas - d1.valor_despesas) / d1.valor_despesas * 100)::NUMERIC, 
        2
    ) AS crescimento_percentual
FROM despesas_1t d1
JOIN despesas_3t d3 ON d1.registro_ans = d3.registro_ans
JOIN operadoras o ON d1.registro_ans = o.registro_ans
ORDER BY crescimento_percentual DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- QUERY 2: Top 5 UFs com maiores despesas totais
-- ----------------------------------------------------------------------------
-- DESAFIO ADICIONAL: Calcular a média por operadora (não a média aritmética simples).
-- A média real é a Soma Total da UF dividida pelo número de Operadoras Distintas naquela UF.

SELECT 
    o.uf,
    SUM(d.valor_despesas) AS total_despesas_estado,
    COUNT(DISTINCT d.registro_ans) AS qtd_operadoras_ativas,
    -- Ticket Médio: Quanto cada operadora gasta em média nesse estado
    ROUND(
        (SUM(d.valor_despesas) / COUNT(DISTINCT d.registro_ans))::NUMERIC, 
        2
    ) AS media_por_operadora
FROM operadoras o
JOIN despesas d ON o.registro_ans = d.registro_ans
WHERE d.ano = 2025
GROUP BY o.uf
ORDER BY total_despesas_estado DESC
LIMIT 5;


-- ----------------------------------------------------------------------------
-- QUERY 3: Operadoras com despesas acima da média em >= 2 trimestres
-- ----------------------------------------------------------------------------
-- TRADE-OFF TÉCNICO:
-- Optou-se por CTEs (Common Table Expressions) em vez de Subqueries aninhadas.
-- Motivo: Separa a lógica de "calcular a média do mercado" da lógica de 
-- "comparar a operadora", facilitando a leitura e manutenção sem perda de performance.

WITH medias_trimestrais AS (
    -- Passo 1: Calcular a "Régua" (Média do Mercado) para cada trimestre
    SELECT 
        trimestre,
        AVG(valor_despesas) AS media_mercado
    FROM despesas
    WHERE ano = 2025
    GROUP BY trimestre
),
performance_operadora AS (
    -- Passo 2: Comparar cada operadora com a régua do seu trimestre
    SELECT 
        d.registro_ans,
        d.trimestre,
        CASE 
            WHEN d.valor_despesas > m.media_mercado THEN 1 
            ELSE 0 
        END AS superou_media
    FROM despesas d
    JOIN medias_trimestrais m ON d.trimestre = m.trimestre
    WHERE d.ano = 2025
)
-- Passo 3: Somar quantas vezes cada operadora superou a média
SELECT 
    o.razao_social,
    SUM(p.superou_media) AS qtd_trimestres_acima
FROM performance_operadora p
JOIN operadoras o ON p.registro_ans = o.registro_ans
GROUP BY o.registro_ans, o.razao_social
HAVING SUM(p.superou_media) >= 2 -- Filtro final
ORDER BY qtd_trimestres_acima DESC, o.razao_social ASC;