# 🚗 Projeto Nova Drive - Data Engineering Pipeline

[![Status](https://img.shields.io/badge/Status-Concluído-success.svg)]()
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)]()
[![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)]()
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=flat&logo=snowflake&logoColor=white)]()
[![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat&logo=dbt&logoColor=white)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)]()

A **Nova Drive** é uma rede fictícia de concessionárias de veículos. Este repositório contém a **Pipeline de Engenharia de Dados (ELT)** completa que **eu desenvolvi** para extrair dados do sistema transacional (ERP) da empresa, carregá-los de forma incremental num Data Warehouse na nuvem, e transformá-los num modelo analítico de *Star Schema* capaz de gerar insights de negócio.

Este projeto foi construído com base em um desafio real (inspirado em curso especializado na área), cujo grande objetivo foi demonstrar na prática como um Data Warehouse bem construído impulsiona a tomada de decisões corporativa baseada em dados, integrando ferramentas modernas de ponta a ponta.

## 🎯 Arquitetura da Solução e Stack Tecnológica

O fluxo de dados segue a arquitetura **ELT (Extract, Load, Transform)**. As ferramentas que utilizei foram:

* **PostgreSQL (Origem)**: Explorei e naveguei profundamente pelo banco de dados da empresa para entender a estrutura transacional (vendas, frota, clientes e vendedores) e planejar de forma correta a migração.
* **Apache Airflow**: Configurei o Airflow como motor principal de orquestração. Automatizei a criação de *Directed Acyclic Graphs (DAGs)* para monitorar, agendar e orquestrar de forma confiável nossa migração.
* **Snowflake (Data Warehouse / Destino)**: Criei e configurei espaços no Snowflake para escalabilidade na nuvem. É nesse ambiente em que ocorre o armazenamento final (Data Warehouse) integrado a todo ecossistema.
* **dbt (Data Build Tool)**: Configurei o dbt para atuar nas transformações diretamente dentro do DW. Apliquei testes de qualidade, documentações vitais e boas práticas de modelagem de dados nas tabelas transformadas.
* **Streamlit (Dashboard)**: Como última camada, com a responsabilidade final de visualização para o tomador de decisão, desenvolvi um painel dinâmico em **Streamlit** (em contrapartida a ferramentas padrão como o Looker Studio), conectando aos marts do DW e visualizando KPIs. Você pode acessar o Dashboard ao vivo [clicando aqui](https://novadrivedashboard.streamlit.app/).
* **Docker & Docker Compose**: Utilizado para gerenciar eficientemente e isolar meu ambiente local (subida do Postgres nativo e instâncias de orquestração do Airflow).

---

## 🛠️ Como Funciona o Pipeline (ELT)

### 1. Extract & Load (Airflow)
A orquestração foi condensada por mim no script `dags/novadrive.py`. A DAG base (`postgres_to_snowflake_etl`) extrai do originário PostgreSQL e deposita no Snowflake com resiliência de tasks individuais dinâmicas.
* **Carga Incremental Baseada em Watermark**: Ao criar as rotinas de carregamento, eu criei uma arquitetura inteligente que evita full-loads: o sistema verifica o Snapshot (`ID` máximo) lá do ambiente na nuvem e puxa na query transacional do Postgres **apenas as linhas novas**.
* **Domínios (Tabelas) Ingeridos**: `vendas`, `veiculos`, `clientes`, `vendedores`, `concessionarias`, `estados` e `cidades`.

### 2. Transform & Modeling (dbt)
Com os dados "brutos" alinhados na nuvem do Snowflake, aciono o projeto que elaborei no dbt (`dbt_transformations/`) arquitetado no modelo **Star Schema**:

* **Camada Stage (`models/stage/`)**: Limpeza básica, cast de dados e padronizações (ex: `stg_vendas`, `stg_clientes`).
* **Camada Core / Data Warehouse (`models/dimensions/` e `models/facts/`)**: A *Tabela Fatos* (`fct_vendas`) é materializada e vinculada inteligentemente aos atores *Dimensões* (`dim_cidades`, `dim_clientes` etc).
* **Camada Analysis (`models/analysis/`)**: Meu produto primário pro Streamlit consumir. Agregações específicas:
  * `analise_vendas_concessionaria`: Quantidade de carros vendidos, faturamento geral e ticket médio entre franquias locais.
  * `analise_vendas_vendedor`: Rankeamento de vendedores em performance absoluta.
  * `analise_vendas_temporal`: Análise sazonal mensal baseada na data de fechamento.
  * `analise_vendas_veiculo`: Insights focados na aderência do portfólio de carros no mercado.

---

## 📂 Estrutura do Repositório

```text
.
├── config/                  # Ajustes vitais como airflow.cfg
├── dags/                    # Minhas rotinas criadas no Airflow (extratores)
├── dbt_transformations/     # Estrutura modular de dados usando o dbt
├── plugins/                 # Extensões ou operators pro Airflow
├── docker-compose.yaml      # Containers Docker para orquestrar dependências base
├── .env.example             # Base p/ preencher configurações e credenciais
└── README.md                # A documentação principal do projeto desenvolvido
```

---

## 🚀 Step-by-Step para Executar o Projeto Localmente

**Pré-requisitos**: Possuir `Git`, um gerenciador de python virt/env como o `python -m venv`, e de preferência o Docker/Compose já configurados nativamente. Precisará de Conta/DW no Snowflake.

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SeuUsuario/nova-drive.git
   cd nova-drive
   ```

2. **Configure Variáveis de Ambiente e Conexões Seguras:**
   ```bash
   cp .env.example .env
   # Mapeie no arquivo .env dados de acesso do Postgres e DW Snowflake
   ```

3. **Inicie os Containers e Serviços Locais (Airflow):**
   ```bash
   docker-compose up -d
   ```
   > Aguarde o término e suba aos portais gerenciais, como o do Airflow (por padrão rodando em http://localhost:8080).

4. **Prepare a dependência de Transformação de Dados:**
   ```bash
   cd dbt_transformations
   python3 -m venv .venv
   source .venv/bin/activate
   pip install dbt-snowflake
   dbt deps
   ```

5. **Trabalho do Pipeline Completo:**
   Execute a carga principal via interface/Airflow-scheduler, certificando de que os dados caíram no Data Warehouse. Em seguida, acione o motor de DW.
   ```bash
   dbt build  # Vai aplicar testes de robustez e criar as tabelas transformadas no Snowflake
   ```

6. **Gerador de Documentação Oficial de Dados e Linhagem (Data Lineage):**
   ```bash
   dbt docs generate
   dbt docs serve
   ```
