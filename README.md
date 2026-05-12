# 🚗 Projeto Nova Drive - Data Engineering Pipeline ELT

[![Status](https://img.shields.io/badge/Status-Concluído-success.svg)]()
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)]()
[![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)]()
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=flat&logo=snowflake&logoColor=white)]()
[![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat&logo=dbt&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)]()

A **Nova Drive** é uma rede fictícia de concessionárias de veículos. Este repositório contém a **Pipeline de Engenharia de Dados (ELT)** completa que **eu desenvolvi** para extrair dados do sistema transacional (ERP) da empresa, carregá-los de forma incremental num Data Warehouse na nuvem, e transformá-los num modelo analítico de *Star Schema* capaz de gerar insights de negócio.

Este projeto foi construído com base em um desafio real (inspirado em curso especializado na área), cujo grande objetivo foi demonstrar na prática como um Data Warehouse bem construído impulsiona a tomada de decisões corporativas baseadas em dados, integrando ferramentas modernas de ponta a ponta.

🔗 **Repositório Oficial e Passo a Passo:** [https://github.com/matheusaraujodata98/novadrive_dbt](https://github.com/matheusaraujodata98/novadrive_dbt)

🔗 **Dashboard:** [nova-drive-dashboard](https://novadrivedashboard.streamlit.app/)

## 🎯 Arquitetura da Solução e Stack Tecnológica

O fluxo de dados segue a arquitetura **ELT (Extract, Load, Transform)**. As ferramentas que utilizei foram:

* **PostgreSQL (Origem)**: Explorei e naveguei profundamente pelo banco de dados da empresa para entender a estrutura transacional (vendas, frota, clientes e vendedores) e planejar de forma correta a migração.
* **Apache Airflow (Orquestração)**: Motor principal de orquestração. Automatizei a criação de *Directed Acyclic Graphs (DAGs)* para monitorar, agendar e orquestrar de forma confiável nossa carga de dados.
* **Snowflake (Data Warehouse / Destino)**: Criei e configurei espaços no Snowflake para escalabilidade na nuvem. É neste ambiente em que ocorre o armazenamento final integrado a todo o ecossistema analítico.
* **dbt (Data Build Tool - Transformação)**: Atua diretamente dentro do DW. Apliquei testes de qualidade, documentações vitais e boas práticas de modelagem *Star Schema* nas tabelas transacionais.
* **Streamlit (Dashboard Frontend)**: Como última camada, com a responsabilidade final de visualização de alto nível para o tomador de decisão. Conectado diretamente aos *marts* gerados pelo dbt.
* **Docker & Docker Compose**: Utilizado para gerenciar eficientemente e isolar meu ambiente local (PostgreSQL nativo e Airflow containers).

---

## 🛠️ Como Funciona o Pipeline (ELT) Detalhado

A orquestração, processamento e modelagem foram cuidadosamente desenhados para serem resilientes e de alta performance.

### 1. Orquestração, Extração e Carga (Apache Airflow ➡️ Snowflake)
A orquestração é o coração pulsante da engenharia de dados. Utilizei o **Airflow** no arquivo `dags/novadrive.py` não apenas para agendar, mas para garantir resiliência, automação e execução isolada das tarefas de extração do PostgreSQL e inserção no DW via hooks parametrizados.
A DAG principal (`postgres_to_snowflake_etl`) foi projetada de forma inteligente:
* **Task Generation Genérica e Paralela:** O código Python da DAG itera sobre um array de tabelas (`veiculos`, `estados`, `vendas`, etc.), criando subgrupos independentes de tasks. Dessa forma, se a carga de `clientes` tiver um problema, as de `vendas` ou `veiculos` continuam sem impacto (isolamento de falhas).
* **Carga Incremental via Watermark:** Ao invés de *Full-Loads* custosos, a arquitetura pega o Snapshot do Destino. A function `get_max_primary_key` faz uma query de "Qual o maior ID inserido no Snowflake?", que serve como parâmetro (*Watermark*) para a function `load_incremental_data`. Esta última consome do Postgres apenas os registros originados após esse ID, otimizando uso de rede e custos de I/O em nuvem.

### 2. O Papel Estratégico do Snowflake como Data Warehouse
O **Snowflake** atua como base de dados de aterrissagem (Landing/Raw) e processamento (Analytics). A escolha pelo Snowflake se deu pela sua arquitetura onde Storage (armazenamento) e Compute (processamento) operam de forma separada. Ele recebe os dados brutos massivos do Airflow e oferece o seu motor elástico e robusto para rodar todas as transformações massivas do DBT sem degradar a performance das consultas do usuário final na ponta.

### 3. Transformação, Modelagem e Preparação Analítica (dbt)
Com os dados "brutos" dentro do Snowflake, o **dbt** (diretório `dbt_transformations/`) assume a modelagem com qualidade, versionamento e testes integrados, utilizando 100% de linguagem SQL.
* **Camada Stage (`models/stage/`)**: Onde aplicamos o *cleansing* básico e normalizações. Ex: padronizando nomenclaturas ou garantindo integridade de IDs na subida transacional para analítica (`stg_vendas`).
* **Camada Core / Star Schema (`models/dimensions/` e `models/facts/`)**: Materialização oficial do *Data Warehouse*. `fct_vendas` atua concentrando os indicadores numéricos (valor, descontos, volume), interligada por chaves-vizinhas com as Dimensões `dim_concessionarias`, `dim_veiculos` e etc., facilitando consultas.
* **Camada Analysis / Marts (`models/analysis/`)**: Este é um dos pontos **mais essenciais da arquitetura para a Visualização**. Ferramentas como Streamlit não devem realizar cálculos pesados de JOIN e GROUP BY no momento em que o usuário acessa o dashboard. Aqui no dbt, criei scripts como `analise_vendas_concessionaria` que pré-agregam faturamento geral, quantidade e ticket médio direto no Banco de Dados. O Streamlit apenas emite um `SELECT *` e já tem o dado "mastigado", resultando num tempo de resposta quase instantâneo.

---

## 📂 Estrutura do Repositório

```text
.
├── config/                  # Ajustes vitais como airflow.cfg
├── dags/                    # Minhas rotinas criadas no Airflow com Tasks dinâmicas
├── dbt_transformations/     # Estrutura modular de modelos de transformacao dbt
├── dashboard/               # Meu código Python (app.py) do Dashboard no Streamlit
├── plugins/                 # Extensões ou operators pro Airflow
├── docker-compose.yaml      # Containers Docker (Postgres, Airflow webserver/scheduler)
├── .env.example             # Base p/ preencher configurações e credenciais
└── README.md                # Esta documentação
```

---

## 🚀 Step-by-Step para Executar o Projeto Localmente

**Pré-requisitos**: Possuir `Git`, gerenciador de Python (como `python -m venv`), e o **Docker & Docker-Compose**. Além disso, é necessária uma conta ativa para conexão em um cluster do **Snowflake**.

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/matheusaraujodata98/novadrive_dbt.git
   cd novadrive_dbt
   ```

2. **Configure Variáveis de Ambiente e Conexões Seguras:**
   ```bash
   cp .env.example .env
   # Edite o .env mapeando suas credenciais de Snowflake e Postgres.
   ```

3. **Inicie a Infraestrutura (Postgres e Airflow via Docker):**
   ```bash
   docker-compose up -d
   ```
   > Aguarde o término e suba aos portais gerenciais, como o UI do Airflow (por padrão rodando em http://localhost:8080).

4. **Dbt - Ambiente e Dependências (Transformação dos Dados):**
   ```bash
   cd dbt_transformations
   python3 -m venv .venv
   source .venv/bin/activate
   pip install dbt-snowflake
   dbt deps
   ```

5. **Executando a Pipeline de Ponta a Ponta:**
   * Via Airflow UI, ative a DAG `postgres_to_snowflake_etl` para realizar a carga transacional na nuvem.
   * Localmente via dbt, processe e transforme essas tabelas para DW e Marts Analíticos:
   ```bash
   dbt build  # Vai aplicar testes de robustez e criar/modelar as tabelas no DW
   ```

6. **Monitorando a Qualidade e Linhagem de Dados (Data Lineage):**
   O dbt oferece uma UI interativa rica sobre como cada tabela é montada nas camadas.
   ```bash
   dbt docs generate
   dbt docs serve
   # Acesse localhost:8080 para ver as interligações
   ```

7. **(Plus) Levantando UI Dashboard:**
   Na pasta base, verifique a pasta `dashboard/` e suas dependências.
   ```bash
   pip install -r dashboard/requirements.txt
   streamlit run dashboard/app.py
   ```

---
*Engenharia arquitetada, desenvolvida e documentada por **Matheus** | Projeto voltado para portfólio contemplando toda a jornada de dados com a Cloud Data Stack moderna.*
