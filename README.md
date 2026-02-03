# Teste de Entrada para Estagiários - Intuitive Care

Este repositório contém a resolução do desafio técnico proposto pela Intuitive Care para a vaga de estágio. O projeto abrange desde o processamento de dados de APIs públicas até a construção de um backend com API RESTful e um frontend web interativo.

## Visão Geral do Projeto

O projeto está dividido nas seguintes etapas, conforme as seções do teste:

1.  **Processamento de Dados (ETL):** Módulos Python para acesso, extração, transformação e carregamento de dados da API de Dados Abertos da ANS.
2.  **Banco de Dados:** Scripts SQL para criação da estrutura do banco de dados e importação dos dados processados.
3.  **API Backend:** Uma API RESTful desenvolvida em Python (FastAPI) para expor os dados processados.
4.  **Frontend Web:** Uma aplicação web construída com Vue.js para interagir com a API e visualizar os dados.

## Estrutura do Repositório

```
Teste_davi_castro/
├── data/                         # Arquivos de dados brutos e processados
├── sql/                          # Scripts SQL para o banco de dados
│   └── ddl.sql                   # Definição da estrutura do banco de dados
├── src/                          # Código fonte da aplicação
│   ├── api/                      # Backend da API (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py               # Ponto de entrada da API
│   │   └── schemas.py            # Definições de schemas Pydantic
│   ├── database/                 # Módulos de interação com o banco de dados
│   ├── frontend/                 # Aplicação frontend (Vue.js)
│   │   ├── css/
│   │   ├── js/
│   │   ├── index.html
│   │   └── logo.svg
│   ├── __init__.py
│   ├── config.py                 # Configurações do projeto
│   └── processador_dados.py      # Script principal de ETL
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md                     
└── requirements.txt              # Dependências Python
```

## Requisitos de Sistema

Para rodar este projeto, você precisará ter instalado:

*   **Python 3.x**
*   **PostgreSQL 10.0+** (para a parte de banco de dados)
*   **Vue.js**

## Configuração do Ambiente

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/DaviCastroo/Teste_davi_castro.git
    cd Teste_davi_castro
    ```

2.  **Crie e ative um ambiente virtual Python:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências Python:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuração do Banco de Dados:**

    *   Crie um banco de dados vazio (ex: `intuitive_care_db`).
    *   Atualize as configurações de conexão com o banco de dados no arquivo `src/config.py`.
    *   Execute o script DDL para criar as tabelas:

        ```bash
        psql -U seu_usuario -d seu_banco_de_dados -f sql/ddl.sql
        ```

## Como Rodar o Projeto

### 1. Processamento de Dados (ETL)

Este passo irá processar os arquívos da ANS, consolidá-los e gerar os arquivos CSV finais (`consolidado_despesas.csv`, `despesas_agregadas_enriquecidas.csv` e `despesas_agregadas.csv`).

!ATENÇÃO!: PARA RODAR O ARQUIVO DE PROCESSAMENTO DE DADOS, É NECESSÁRIO COLOCAR  OS ARQUIVOS `1T2025.csv`, `2T2025.csv`, `3T2025.csv` e `Relatorio_cadop.csv` dentro do diretório `data/raw`.

```bash
python src/processador_dados.py
```

**Explicação:**

*   O script `processador_dados.py` é responsável por:
    *   Identificar os dados de despesas com eventos/sinistros.
    *   Normalizar os dados, tratando variações de encoding (`UTF-8`, `LATIN-1`) estrutura de colunas e tipos de dados (`String`, `Decimal`, `Int`).
    *   Consolidar os dados em `consolidado_despesas.csv` com as colunas `CNPJ`, `RazaoSocial`, `Trimestre`, `Ano`, `ValorDespesas`.
    *   Realizar validações de CNPJ, valores numéricos e razão social.
    *   Enriquecer os dados com informações de operadoras ativas da ANS.
    *   Agregar os dados por `RazaoSocial` e `UF`, calculando total, média e desvio padrão de despesas, salvando em `despesas_agregadas.csv`.
    *   Os arquivos CSV gerados são compactados em um ZIP, sendo salvos no diretório `data/processed`.

### 2. Importação de Dados para o Banco de Dados

Após o processamento, os dados precisam ser importados para o banco de dados. Para isso, existe um arquivo `loader.py`, que se encontra no diretório `database`, que cuida da população do banco de dados.

Vale lembrar que, para o `loader.py` funcionar, é necessário colocar as informações na string de conexão, no arquivo `src/config.py`. Nesse arquivo, coloque as informações na variável `DB_CONNECTION`

**Execução do Script:**

```bash
python -m src.database.loader
```

### 3. Execução da API Backend

Navegue até o diretório `src/api` e inicie a aplicação FastAPI.

```bash
python -m uvicorn src.api.main:app --reload
```

Pronto, a aplicação foi inicializada, agora basta abrir em seu navegado, pela url `http://localhost:8000`

**Explicação:**

*   A API é construída com **FastAPI**, escolhido pela sua alta performance e facilidade de desenvolvimento com tipagem de dados (Pydantic).
*   As rotas implementadas incluem:
    *   `GET /api/operadoras`: Lista todas as operadoras com paginação.
    *   `GET /api/operadoras/{cnpj}`: Retorna detalhes de uma operadora específica.
    *   `GET /api/operadoras/{cnpj}/despesas`: Retorna histórico de despesas da operadora.
    *   `GET /api/estatisticas`: Retorna estatísticas agregadas (total de despesas, média, top 5 operadoras).
*   A documentação interativa da API estará disponível em `http://localhost:8000/docs` (Swagger UI) e `http://localhost:8000/redoc` (ReDoc).

### 4. Execução do Frontend Web

Navegue até o diretório `src/frontend`, instale as dependências Node.js e inicie o servidor de desenvolvimento.

```bash
cd src/frontend
npm install  # ou yarn install
npm run serve # ou yarn serve
```

**Explicação:**

*   O frontend é uma aplicação **Vue.js** que consome a API backend.
*   Funcionalidades:
    *   Exibição de tabela paginada com operadoras.
    *   Busca/filtro por razão social ou CNPJ.
    *   Gráfico de distribuição de despesas por UF (utilizando uma biblioteca como Chart.js ou similar).
    *   Página de detalhes da operadora com histórico de despesas.

## Decisões Técnicas (Trade-offs)

Durante o desenvolvimento, diversas decisões técnicas foram tomadas, considerando os requisitos do teste e as boas práticas de engenharia de software. Abaixo estão as principais:

### 1. Processamento de Dados

*   **Processamento de Arquivos (Memória vs. Incremental):** Optou-se por um **processamento incremental (chunking)** para arquivos grandes, utilizando `chunksize` no `pd.read_csv`. Isso evita o esgotamento de memória ao lidar com grandes volumes de dados, processando-os em blocos menores. [1]
*   **Tratamento de CNPJs Inválidos:** CNPJs inválidos são **removidos** dos dados. A justificativa é que dados inconsistentes podem comprometer a integridade das análises e a identificação correta das operadoras. 
*   ** Para validar os CNPJs, foi utilizado a biblioteca **validate_docbr**, visando manter a simplicidade do código e utilizar das ferramentas que a linguágem oferece.** [2] 
*   **Estratégia de Join:** Para o enriquecimento de dados, foi utilizado um `merge` do Pandas, que é eficiente para operações de join em memória. A escolha se baseia na premissa de que os arquivos de dados cadastrais das operadoras, embora possam ser grandes, são gerenciáveis em memória para essa operação específica. [3]
*   **Estratégia de Agregação/Ordenação:** A agregação e ordenação são realizadas diretamente com as funcionalidades do Pandas (`groupby`, `agg`, `sort_values`), que são otimizadas para performance em conjuntos de dados tabulares. [4]

### 2. Banco de Dados

*   **Normalização:** Optou-se por **tabelas normalizadas separadas** (`despesas` e `operadoras`). Isso reduz a redundância de dados, melhora a integridade e facilita a manutenção, sendo mais adequado para sistemas onde a consistência e a flexibilidade de consulta são importantes, mesmo com um volume de dados crescente. [5]
*   **Tipos de Dados:**
    *   **Valores Monetários:** Utilização de `DECIMAL` para valores monetários para garantir precisão, evitando problemas de arredondamento inerentes a `FLOAT`. [6]
    *   **Datas:** Utilização de `DATETIME` para datas, para garantir a facilidade durante manipulação. [7]
*   **Tratamento de Inconsistências na Importação:** Durante a importação, valores `NULL` em campos obrigatórios são tratados com valores padrão ou os registros são rejeitados, dependendo da criticidade. Strings em campos numéricos são convertidas ou os registros são marcados como inválidos. Datas inconsistentes são padronizadas ou os registros são sinalizados. A abordagem visa manter a qualidade dos dados no banco. [8]

### 3. API Backend

*   **Escolha do Framework (FastAPI):** FastAPI foi escolhido por sua performance assíncrona, validação de dados automática com Pydantic, e geração de documentação interativa (Swagger UI/ReDoc) out-of-the-box, o que acelera o desenvolvimento e melhora a manutenibilidade. [9]
*   **Estratégia de Paginação (Offset-based):** Implementada paginação baseada em `offset` e `limit` (`page`, `limit` parâmetros). Embora `cursor-based` seja mais escalável para grandes volumes, `offset-based` é mais simples de implementar e suficiente para a maioria dos casos, especialmente neste projeto. [10]
*   **Cache vs. Queries Diretas para Estatísticas:** Para a rota `/api/estatisticas`, a opção de **calcular sempre na hora** foi adotada. Em um cenário de teste ou com volume de dados moderado, a complexidade de implementar cache pode não justificar o ganho de performance. Para um ambiente de produção com alta demanda, o cache ou pré-cálculo seria considerado. [11]
*   **Estrutura de Resposta da API (Dados + Metadados):** As respostas da API para listagens incluem **dados e metadados** (`{data: [...], total: 100, page: 1, limit: 10}`). Isso fornece ao frontend informações essenciais para construir componentes de paginação e exibir o total de registros, melhorando a experiência do desenvolvedor frontend. [12]

### 4. Frontend Web

*   **Estratégia de Busca/Filtro (Busca no Servidor):** A busca e filtragem são realizadas no backend (`Busca no servidor`). Isso garante que o frontend sempre trabalhe com um conjunto de dados filtrado e paginado, evitando o carregamento de grandes volumes de dados no cliente e otimizando a performance para grandes bases de dados. [13]
*   **Gerenciamento de Estado (Props/Events simples):** Para este projeto, a utilização de `Props/Events` simples do Vue.js é suficiente para gerenciar o estado entre componentes. Para aplicações maiores, Vuex/Pinia seriam considerados. [14]
*   **Performance da Tabela:** A tabela é renderizada com paginação e carregamento sob demanda (lazy loading) para garantir boa performance mesmo com muitas operadoras. [15]
*   **Tratamento de Erros e Loading:** O frontend exibe **mensagens de loading** durante as requisições à API e **mensagens de erro genéricas** em caso de falha. Para uma aplicação de produção, mensagens de erro mais específicas e amigáveis seriam implementadas. [16]
