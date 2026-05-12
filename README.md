# 🚗 Projeto Nova Drive - Data Engineering Pipeline

A **Nova Drive** é uma rede fictícia de concessionárias de veículos. Este repositório contém a **Pipeline de Engenharia de Dados (ELT)** completa, construída para extrair dados do sistema transacional (ERP) da empresa, carregá-los de forma incremental num Data Warehouse na nuvem, e transformá-los num modelo analítico de *Star Schema* capaz de gerar insights de negócio.

## 🎯 Arquitetura da Solução e Stack Tecnológica

O fluxo de dados segue a arquitetura **ELT (Extract, Load, Transform)** utilizando:

* **PostgreSQL (Origem)**: Simula o banco de dados transacional atrelado ao sistema de vendas, gestão de frota, clientes e vendedores da concessionária.
* **Apache Airflow**: Motor de orquestração. Gerencia o agendamento (`schedule=timedelta(days=1)`), controle das DAGs e o fluxo de dados em Python via operadores e decorators.
* **Snowflake (Data Warehouse / Destino)**: Banco de dados colunar na nuvem, altamente escalável, para onde os dados brutos são ingeridos e onde ocorrem as agregações finais.
* **dbt (Data Build Tool)**: Responsável pela fase de Transformação dentro do Snowflake. Padroniza as camadas (`stage`, `dimensions`, `facts` e `analysis`), garantindo qualidade e documentação dos dados.
* **Docker & Docker Compose**: Automatiza a subida local da infraestrutura do Apache Airflow e das dependências.

---

## 🛠️ Como Funciona o Pipeline (ELT)

### 1. Extract & Load (Airflow)
A orquestração está concentrada no script `dags/novadrive.py`. A DAG base (`postgres_to_snowflake_etl`) lê os dados do PostgreSQL usando o `PostgresHook` e carrega no Snowflake usando o `SnowflakeHook`.
* **Carga Incremental Baseada em Watermark**: Para não sobrecarregar o banco com full loads diários, o script captura o `ID` máximo (Primary Key) existente no respectivo destino no Snowflake e busca no PostgreSQL **apenas novas linhas** onde o ID seja maior que o último registrado.
* **Domínios (Tabelas) Ingeridos**: `vendas`, `veiculos`, `clientes`, `vendedores`, `concessionarias`, `estados` e `cidades`. A DAG gera tarefas dinamicamente em loop gerando tarefas `get_max_id_*` e `load_data_*`.

### 2. Transform (dbt)
Com os dados "crus/brutos" replicados no Snowflake, as transformações do dbt (`dbt_transformations/`) são acionadas em três camadas:

* **1. Camada Stage (`models/stage/`)**: Trata e tipa os 7 domínios cruciais (padronizando nomenclaturas como `stg_vendas`, `stg_clientes`, etc).
* **2. Camada Core / Data Warehouse (`models/dimensions/` e `models/facts/`)**:
  * O schema final é um **Star Schema**.
  * A estrela do modelo é a tabela Fatos **`fct_vendas`**, ligada às Dimensões (`dim_cidades`, `dim_clientes`, `dim_concessionarias`, `dim_estados`, `dim_veiculos` e `dim_vendedores`).
* **3. Camada Analysis (`models/analysis/`)**: Datamarts materializados fisicamente como *Tables* no DW com Data Aggregation pronto para serem pludados pelo Painel de BI, sendo eles:
  * `analise_vendas_concessionaria`: Quantidade, Faturamento Total e  Ticket Médio separados por Loja (Cidade e Estado).
  * `analise_vendas_vendedor`: Performance individual dos vendedores com rankings de vendas e volume por filial.
  * `analise_vendas_temporal`: Análise hierárquica truncada por Mês (sazonalidade comercial da Nova Drive).
  * `analise_vendas_veiculo`: Foco no portfólio para ver quais modelos de carros vendem melhor.

---

## 📂 Visão Geral da Estrutura do Repositório

```text
.
├── config/                  # Ajustes como `airflow.cfg`
├── dags/                    # Código fonte do Airflow (`novadrive.py`)
├── dbt_transformations/     # TODO o projeto de modelagem, SQLs e views
├── plugins/                 # Extensões ou hooks custom do Airflow (se houver)
├── scripts/                 # Bash/Python scripts para auxiliar operações DevOps
├── docker-compose.yaml      # Definição e containers necessários do Airflow/Postgres
├── .env.example             # Base p/ preencher `.env` (crentials Airflow, DW e DB)
└── README.md                # Esta documentação
```

---

## 🚀 Step-by-Step para Executar o Projeto Localmente

**Pré-requisitos**: Possuir `Git`, ambiente virtual Python (`python -m venv`), Docker e Docker Compose nativos em sua máquina, conta liberada no Snowflake configurada.

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SeuUsuario/nova-drive.git
   cd nova-drive
   ```

2. **Configure Variáveis de Ambiente de Forma Segura:**
   ```bash
   cp .env.example .env
   # Abra o arquivo .env no seu editor e preencha as senhas de POSTGRES_* e SNOWFLAKE_*
   ```

3. **Inicie os Containers Docker (Ambiente Airflow):**
   ```bash
   docker-compose up -d
   ```
   > Aguarde o término e acesse o Airflow em http://localhost:8080 (se certifique via UI e hooks que seu airflow conectará corretamente com os bancos Postgres e Snowflake).

4. **Trabalhadores e Instalação dbt:**
   Num terminal local da sua máquina, ative o ambiente virtual para baixar a camada de testes:
   ```bash
   cd dbt_transformations
   python3 -m venv .venv
   source .venv/bin/activate
   pip install dbt-snowflake
   dbt deps
   ```

5. **Execute a Compilação do Data Warehouse:**
   Cuidado para ter a DAG `postgres_to_snowflake` já executada com sucesso ao menos uma vez.
   ```bash
   dbt build  # Irá executar seed, run no modelo cronológico e testes no DW
   ```

6. **Acesse as métricas de Linhagem dos Dados:**
   ```bash
   dbt docs generate
   dbt docs serve
   # Navegue até localhost:8080 caso não abra sozinho
   ```
---
*Engenharia implementada por **Matheus** | Projeto voltado para portfolio e aprendizado avançado na Cloud Data Stack.*
