-- Tabela de Dados Cadastrais
CREATE TABLE operadoras (
    registro_ans INT PRIMARY KEY,
    cnpj VARCHAR(14) UNIQUE NOT NULL, -- CNPJ é texto (evita perder zeros à esquerda)
    razao_social VARCHAR(255),
    modalidade VARCHAR(100),
    uf CHAR(2)
);

-- Tabela de Despesas Financeiras
CREATE TABLE despesas (
    id SERIAL PRIMARY KEY,
    registro_ans INT,
    ano INT,
    trimestre VARCHAR(2), -- 1T, 2T...
    valor_despesas DECIMAL(15, 2), 
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);