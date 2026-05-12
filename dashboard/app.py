import streamlit as st
import snowflake.connector
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Nova Drive Dashboard", page_icon="🚗", layout="wide")

st.title("🚗 Dashboard Analítico - Nova Drive")
st.markdown("Visualização das métricas da concessionária diretamente do Snowflake.")

# Inicializa a conexão em cache para otimização
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        **st.secrets["snowflake"]
    )

try:
    conn = init_connection()
    st.success("Conectado ao Snowflake com sucesso!")
except Exception as e:
    st.error(f"Erro de conexão com Snowflake: {e}")
    st.stop()

# Função para fazer query com cache de dados
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        # Retorna num DataFrame do Pandas para facilitar criação de gráficos
        return cur.fetch_pandas_all()

# Exemplo de Dashboard usando as tabelas do seu banco (Marts do dbt)
st.subheader("📊 Faturamento por Concessionária")
try:
    # Ajuste o schema e database para o nome exato que está no seu Snowflake 
    df_concessionaria = run_query("SELECT CONCESSIONARIA, TOTAL, QUANTIDADE FROM ANALISE_VENDAS_CONCESSIONARIA ORDER BY TOTAL DESC;")
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df_concessionaria)
    with col2:
        st.bar_chart(df_concessionaria, x="CONCESSIONARIA", y="TOTAL")

except Exception as e:
    st.warning("Não foi possível carregar os dados. Verifique a query ou se as tabelas já foram geradas lá pelo dbt.")

