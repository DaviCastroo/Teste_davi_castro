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
*   **Valores Zerados (R$ 0,00):** Diversas operadoras, especialmente da modalidade "Administradora de Benefícios", apresentaram despesas assistenciais zeradas na conta "411". Esses registros foram **mantidos**, pois empresas atuam na gestão administrativa de planos, repassando o risco assistencial (pagamento de sinistros) para operadoras parceiras. Remover esses dados ocultaria a realidade contábil dessas entidades. [2]
*   **Valores Negativos (R$ -192580,57):** Foram detectados lançamentos negativos (ex: `-3.290.938,14`) em contas de despesa. Estes registro foram **mantidos**, pois representam estornos, glosas ou reversão de provisões técnicas de trimestres anteriores (Reversão de Provisão de Eventos Ocorridos e Não Avisados - PEONA). Ignorá-los causaria inconsistência no saldo anual consolidado.[3]
*   **Tratamento de CNPJs Inválidos:** CNPJs inválidos são **removidos** dos dados. A justificativa é que dados inconsistentes podem comprometer a integridade das análises e a identificação correta das operadoras. 
*   ** Para validar os CNPJs, foi utilizado a biblioteca **validate_docbr**, visando manter a simplicidade do código e utilizar das ferramentas que a linguágem oferece.** [4]
*   **Inconsistências de Cadastro:** Operadoras presentes no arquivo de despesas mas ausentes no CADOP foram importadas mantendo o vínculo financeiro, porém sinalizadas no banco de dados para auditoria futura. [5]
*   **Estratégia de Join:** Para o enriquecimento de dados, foi utilizado um `merge` do Pandas, que é eficiente para operações de join em memória. A escolha se baseia na premissa de que os arquivos de dados cadastrais das operadoras, embora possam ser grandes, são gerenciáveis em memória para essa operação específica. [6]
*   **Estratégia de Agregação/Ordenação:** A agregação e ordenação são realizadas diretamente com as funcionalidades do Pandas (`groupby`, `agg`, `sort_values`), que são otimizadas para performance em conjuntos de dados tabulares. [7]

### 2. Banco de Dados

*   **Normalização:** Optou-se por **tabelas normalizadas separadas** (`despesas` e `operadoras`). Isso reduz a redundância de dados, melhora a integridade e facilita a manutenção, sendo mais adequado para sistemas onde a consistência e a flexibilidade de consulta são importantes, mesmo com um volume de dados crescente. [8]
*   **Abordagem SQL (Query 3 - Operadoras Acima da Média):** Utilização de **CTEs (Common Table Expressions)** em vez de Subqueries aninhadas. Embora ambas tenham performance similar no PostgreSQL moderno, a CTE separa a lógica de cálculo da média trimestral da lógica de filtragem das operadoras. Isso aumenta drasticamente a **legibilidade** e **manutenibilidade** do código, facilitando futuras alterações nas regras de negócio. [9]
*   **Tipos de Dados:**
    *   **Valores Monetários:** Utilização de `DECIMAL` para valores monetários para garantir precisão, evitando problemas de arredondamento inerentes a `FLOAT`. [10]
    *   **Datas:** Utilização de `DATETIME` para datas, para garantir a facilidade durante manipulação. [11]
*   **Tratamento de Inconsistências na Importação:** Durante a importação, valores `NULL` em campos obrigatórios são tratados com valores padrão ou os registros são rejeitados, dependendo da criticidade. Strings em campos numéricos são convertidas ou os registros são marcados como inválidos. Datas inconsistentes são padronizadas ou os registros são sinalizados. A abordagem visa manter a qualidade dos dados no banco. [12]

### 3. API Backend

    ## Como Testar a API (Postman)

    Uma coleção completa com todas as rotas configuradas e exemplos de requisição foi incluída na raiz deste projeto para facilitar a avaliação.

    * **Arquivo:** `postman_collection.json`

    ### Passo a Passo para Importar:

    1.  Certifique-se de que a API Backend está rodando (`http://localhost:8000`).
    2.  Abra o **Postman**.
    3.  Clique no botão **Import** (canto superior esquerdo).
    4.  Arraste o arquivo `Teste Intuitive Care - API.json` (localizado na pasta principal do projeto) para a janela de importação ou selecione-o manualmente.
    5.  A coleção **"Teste Intuitive Care - API"** aparecerá na sua barra lateral contendo:
        * Listagem paginada.
        * Busca por filtros.
        * Detalhamento de operadora.
        * Estatísticas e dados para gráficos.
*   **Escolha do Framework (FastAPI):** FastAPI foi escolhido por sua performance assíncrona, validação de dados automática com Pydantic, e geração de documentação interativa (Swagger UI/ReDoc) out-of-the-box, o que acelera o desenvolvimento e melhora a manutenibilidade. [13]
*   **Estratégia de Paginação (Offset-based):** Implementada paginação baseada em `offset` e `limit` (`page`, `limit` parâmetros). Embora `cursor-based` seja mais escalável para grandes volumes, `offset-based` é mais simples de implementar e suficiente para a maioria dos casos, especialmente neste projeto. [14]
*   **Cache vs. Queries Diretas para Estatísticas:** Para a rota `/api/estatisticas`, a opção de **calcular sempre na hora** foi adotada. Em um cenário de teste ou com volume de dados moderado, a complexidade de implementar cache pode não justificar o ganho de performance. Para um ambiente de produção com alta demanda, o cache ou pré-cálculo seria considerado. [15]
*   **Estrutura de Resposta da API (Dados + Metadados):** As respostas da API para listagens incluem **dados e metadados** (`{data: [...], total: 100, page: 1, limit: 10}`). Isso fornece ao frontend informações essenciais para construir componentes de paginação e exibir o total de registros, melhorando a experiência do desenvolvedor frontend. [16]

### 4. Frontend Web

*   **Estratégia de Busca/Filtro (Busca no Servidor):** A busca e filtragem são realizadas no backend (`Busca no servidor`). Isso garante que o frontend sempre trabalhe com um conjunto de dados filtrado e paginado, evitando o carregamento de grandes volumes de dados no cliente e otimizando a performance para grandes bases de dados. [17]
*   **Gerenciamento de Estado (Props/Events simples):** Para este projeto, a utilização de `Props/Events` simples do Vue.js é suficiente para gerenciar o estado entre componentes. Para aplicações maiores, Vuex/Pinia seriam considerados. [18]
*   **Performance da Tabela:** A tabela é renderizada com paginação e carregamento sob demanda (lazy loading) para garantir boa performance mesmo com muitas operadoras. [19]
*   **Tratamento de Erros e Loading:** O frontend exibe **mensagens de loading** durante as requisições à API e **mensagens de erro genéricas** em caso de falha. Para uma aplicação de produção, mensagens de erro mais específicas e amigáveis seriam implementadas. [20]


### 5. Decisões Técnicas SQL (Queries Analíticas)

1.  **Cálculo de Crescimento (Query 1):**
    * **Desafio:** Como tratar operadoras que não possuem dados em todos os trimestres?
    * **Solução:** Utiliza-se `INNER JOIN` entre o 1º e o 3º trimestre.
    * **Justificativa:** Para calcular uma taxa de crescimento percentual, é matematicamente obrigatório ter o ponto de partida e o de chegada. Operadoras que entraram ou saíram do mercado durante o ano não são comparáveis neste indicador específico. Também apliquei um filtro (`> 1000`) para evitar distorções de operadoras com despesas iniciais próximas a zero. [21]

2.  **Média por UF (Query 2):**
    * **Solução:** Cálculo manual `SUM(valor) / COUNT(DISTINCT operadora)`.
    * **Justificativa:** A função `AVG()` padrão calcularia a média por *lançamento contábil*. O requisito pedia a média *por operadora*. Como uma operadora pode ter múltiplos lançamentos (ou apenas um consolidado), dividir o montante total pela contagem distinta de CNPJs/Registros fornece o indicador de negócio correto ("Ticket Médio da Operadora no Estado"). [22]

3.  **Performance e Legibilidade (Query 3):**
    * **Trade-off:** Subqueries no `WHERE` vs. CTEs (Common Table Expressions).
    * **Escolha:** **CTEs**.
    * **Justificativa:** A abordagem com CTEs permitiu quebrar o problema complexo em 3 etapas lógicas (calcular médias -> comparar -> agrupar). No PostgreSQL, isso facilita a leitura do código e a manutenção futura (ex: alterar a regra da média) sem sacrificar performance, já que o planejador de queries otimiza CTEs de forma eficiente. [23]

4.  **Visualização de Dados (Gráfico de Despesas por UF):**

Foi implementada uma seção de inteligência de mercado no Dashboard, exibindo a distribuição geográfica das despesas.

* **Biblioteca:** [Chart.js](https://www.chartjs.org/) (via CDN).
* **Componente:** Gráfico de Barras Verticais (`Bar Chart`) responsivo.
* **Funcionalidades:**
    * Exibição do volume total de despesas por Estado (UF).
    * Listagem lateral com ranking completo e scroll infinito.
    * Formatação monetária nativa (BRL) nos tooltips e legendas.
    * Atualização dinâmica sem recarregar a página (SPA).[24]

#### Decisões Técnicas (Trade-offs)

1.  **Renderização no Cliente vs. Servidor (Chart.js):**
    * **Escolha:** Renderização no cliente via `Canvas` (Chart.js).
    * **Justificativa:** O Chart.js é extremamente performático para desenhar milhares de pontos de dados usando HTML5 Canvas (aceleração de GPU), sendo mais leve que bibliotecas baseadas em SVG (DOM) para este volume de dados. A integração via CDN manteve o projeto leve, sem necessidade de *build steps* complexos (Webpack/Vite).[25]

2.  **Agregação de Dados (Backend First):**
    * **Problema:** Calcular o total por UF no Frontend exigiria baixar todas as despesas (milhões de linhas) para o navegador, travando o dispositivo do usuário.
    * **Solução:** Implementação do endpoint `/api/estatisticas/uf` que já retorna os dados agrupados (`GROUP BY uf`).
    * **Benefício:** O tráfego de rede foi reduzido de ~50MB (dados brutos) para ~1KB (JSON sumarizado), garantindo carregamento instantâneo do gráfico.[26]

3.  **UX do Gráfico (Top 10 vs. Completo):**
    * **Decisão:** O gráfico exibe visualmente todas as UFs, mas a lista lateral permite detalhamento.
    * **Justificativa:** Permite identificar rapidamente os *outliers* (estados com maiores gastos) visualmente, enquanto a lista lateral rolável oferece acesso preciso aos dados de estados com menor volume, mantendo a interface limpa.[27]
