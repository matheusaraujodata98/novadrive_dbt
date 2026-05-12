import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide", page_title="NovaDrive Motors", page_icon="🚗")

# ── Estilos CSS Personalizados ────────────────────────────────────────────────
st.markdown("""<style>
.stApp{background:#0a0a0f}
.mc{background:linear-gradient(135deg,#1C1C1E,#252530);border-radius:16px;padding:22px 26px;color:#fff;
    box-shadow:0 8px 32px rgba(0,0,0,.4);border:1px solid #2a2a3a;min-height:120px;transition:transform .2s}
.mc:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.5)}
.mc .lb{margin:0;font-size:11px;color:#8E8E93;font-weight:600;letter-spacing:1px;text-transform:uppercase}
.mc .vl{margin:10px 0 0;font-size:28px;font-weight:800;color:#fff;line-height:1.1}
.mc .sb{margin:6px 0 0;font-size:11px;color:#636366}
.mc .bar{height:3px;border-radius:2px;margin-top:14px;opacity:.7}
.stitle{font-size:15px;font-weight:700;color:#E5E5EA;padding:8px 0 6px;border-bottom:2px solid #2a2a3a;
    display:inline-block;margin-bottom:12px;letter-spacing:.3px}
.dv{height:1px;background:linear-gradient(90deg,transparent,#2a2a3a,transparent);margin:24px 0}
.ins{border-radius:10px;padding:12px 16px;margin-bottom:8px;font-size:13px;display:flex;align-items:flex-start;gap:10px}
.ins span{font-weight:700}
h1,h2,h3,h4,h5,h6,p,span,label,.stMarkdown{color:#E5E5EA !important}
[data-testid="stDataFrame"]{border:1px solid #2a2a3a;border-radius:10px}
.hero{background:linear-gradient(135deg,#0f0f1a,#1a1a2e);border:1px solid #2a2a4a;
    border-radius:16px;padding:24px 30px;margin-bottom:20px}
</style>""", unsafe_allow_html=True)

# ── Geração de Dados ──────────────────────────────────────────────────────────
import snowflake.connector

@st.cache_resource
def init_connection():
    try:
        return snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            account=st.secrets["snowflake"]["account"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"]
        )
    except Exception as e:
        st.error("⚠️ Segredos do Snowflake não encontrados no Streamlit Cloud. Por favor, configure a aba 'Secrets' nas configurações do seu App.")
        st.stop()

conn = init_connection()

@st.cache_data(ttl=600)
def load_data():
    query = "SELECT * FROM ANALISE_VENDAS_CONCESSIONARIA"
    return pd.read_sql(query, conn)

df = load_data()

# Padronizando e garantindo o nome das colunas
df.columns = [c.upper() for c in df.columns]

# Traduzindo das colunas do banco para o padrão que o layout já usa
df = df.rename(columns={
    "CONCESSIONARIA": "Concessionaria",
    "CIDADE": "Cidade",
    "ESTADO": "Estado",
    "QUANTIDADE": "Qtd_Pedidos",     # De acordo com analise_vendas_concessionaria.sql
    "TOTAL": "Total_Vendas",         # De acordo com analise_vendas_concessionaria.sql
    "VALOR_MEDIO": "Ticket_Medio"    # De acordo com analise_vendas_concessionaria.sql
})

if "Ticket_Medio" not in df.columns and "Total_Vendas" in df.columns and "Qtd_Pedidos" in df.columns:
    df["Ticket_Medio"]=(df["Total_Vendas"]/df["Qtd_Pedidos"]).round(2)

# ── Cabeçalho e Filtros (Layout Superior) ─────────────────────────────────────
st.markdown(f"""<div class="hero">
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px">
  <span style="font-size:32px">🚗</span>
  <div>
    <span style="font-size:26px;font-weight:800;color:#fff">NovaDrive Motors</span>
    <span style="background:#3b82f6;color:#fff;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:600;margin-left:10px">SISTEMA DE GESTÃO DE VENDAS</span>
  </div>
</div>
<p style="color:#636366;margin:0;font-size:12px">{df.Estado.nunique()} estados monitorizados &bull; Período Fiscal: 2024 &bull; Atualizado agora</p>
</div>""", unsafe_allow_html=True)

sel = st.multiselect("🗺️ Selecionar Estados para Análise", sorted(df.Estado.unique()), default=df.Estado.unique())

d=df[df.Estado.isin(sel)] if sel else df.iloc[0:0]

if d.empty:
    st.warning("⚠️ Por favor, selecione pelo menos um estado para carregar os indicadores.")
    st.stop()

# ── Processamento de Métricas ─────────────────────────────────────────────────
ve=d.groupby("Estado",as_index=False).agg(Total_Vendas=("Total_Vendas","sum"),Qtd_Pedidos=("Qtd_Pedidos","sum"))
ve["Ticket_Medio"]=ve["Total_Vendas"]/ve["Qtd_Pedidos"]
ve["Total_Mi"]=ve["Total_Vendas"]/1e6
tv=d.Total_Vendas.sum(); tq=d.Qtd_Pedidos.sum(); tk=tv/max(tq,1)
top=ve.loc[ve.Total_Vendas.idxmax(),"Estado"]; topv=ve.Total_Vendas.max()
top3=ve.nlargest(3,"Total_Vendas"); pct=top3.Total_Vendas.sum()/tv*100
mxtk=ve.loc[ve.Ticket_Medio.idxmax()]; mvol=ve.loc[ve.Qtd_Pedidos.idxmax()]

# ── Painel de KPIs ────────────────────────────────────────────────────────────
k1,k2,k3,k4=st.columns(4)
kpis=[
    (k1,"Faturamento Total",f"R$ {tv/1e6:,.1f}M",f"{d.Estado.nunique()} estados","#3b82f6"),
    (i2 if 'i2' in locals() else k2,"Pedidos Realizados",f"{tq:,}",f"{d.Concessionaria.nunique()} unidades","#10b981"),
    (k3,"Ticket Médio",f"R$ {tk:,.0f}","por venda","#f59e0b"),
    (k4,"Estado Líder",top,f"R$ {topv/1e6:,.1f}M faturados","#8b5cf6"),
]
for col,lb,vl,sb,cor in kpis:
    col.markdown(f"""<div class="mc">
    <p class="lb">{lb}</p><p class="vl">{vl}</p><p class="sb">{sb}</p>
    <div class="bar" style="background:linear-gradient(90deg,{cor},transparent)"></div>
    </div>""", unsafe_allow_html=True)

# ── Storytelling e Insights ───────────────────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">💡 Narrativa de Performance</p>', unsafe_allow_html=True)
i1,i2=st.columns(2)
insights=[
    (i1,"#1a2744","#2d4a7a","#60a5fa","🥇",f"O estado de <span>{top}</span> domina o ranking, representando o maior volume financeiro da rede."),
    (i1,"#1a3a2a","#2d6a4a","#34d399","📈",f"Alta concentração: <span>{', '.join(top3.Estado)}</span> somam <span>{pct:.0f}%</span> do faturamento total."),
    (i2,"#2a1a3a","#4a2d6a","#a78bfa","💎",f"<span>{mxtk.Estado}</span> apresenta a operação mais premium com ticket de <span>R$ {mxtk.Ticket_Medio:,.0f}</span>."),
    (i2,"#2a1a1a","#6a2d2d","#f87171","⚡",f"Maior fluxo operacional em <span>{mvol.Estado}</span> com <span>{int(mvol.Qtd_Pedidos):,}</span> transações concluídas."),
]
for col,bg,border,clr,icon,txt in insights:
    col.markdown(f'<div class="ins" style="background:{bg};border:1px solid {border};color:#c8d6f0">'
        f'<span style="font-size:18px">{icon}</span>'
        f'<span style="color:#c8d6f0">{txt.replace("<span>",f"<span style=color:{clr}>")}</span></div>',
        unsafe_allow_html=True)

# ── Auxiliares Plotly ─────────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af", size=11), margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#1f2937", zeroline=False)
)

# ── 1. Curva ABC: Concentração de Faturamento (Pareto) ────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">📊 Curva ABC: Concentração do Faturamento por Estado</p>', unsafe_allow_html=True)

df_pareto = ve.sort_values("Total_Vendas", ascending=False).copy()
df_pareto["Perc"] = df_pareto["Total_Vendas"] / df_pareto["Total_Vendas"].sum() * 100
df_pareto["Acumulado"] = df_pareto["Perc"].cumsum()

fig_pareto = go.Figure()
fig_pareto.add_trace(go.Bar(
    x=df_pareto["Estado"], y=df_pareto["Total_Vendas"],
    name="Faturamento", marker_color="#3b82f6",
    hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>"
))
fig_pareto.add_trace(go.Scatter(
    x=df_pareto["Estado"], y=df_pareto["Acumulado"],
    name="% Acumulado", mode="lines+markers",
    marker=dict(color="#f59e0b", size=8), line=dict(width=3),
    yaxis="y2", hovertemplate="Acumulado: %{y:.1f}%<extra></extra>"
))

fig_pareto.update_layout(
    **LAYOUT, height=450, showlegend=False,
    yaxis=dict(title="Faturamento (R$)", showgrid=True, gridcolor="#1f2937"),
    yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 110], showgrid=False)
)
st.plotly_chart(fig_pareto, use_container_width=True)

# ── 2. Distribuição de Performance por Unidade (Boxplot) ──────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">📍 Dispersão de Performance: Faturamento por Concessionária</p>', unsafe_allow_html=True)

# Focamos nos 7 maiores estados para o gráfico não ficar esmagado
top_est = df_pareto["Estado"].head(7).tolist()
df_box = d[d["Estado"].isin(top_est)]

fig_box = px.box(
    df_box, x="Estado", y="Total_Vendas", color="Estado",
    points="all", hover_data=["Concessionaria", "Ticket_Medio"],
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_box.update_layout(**LAYOUT, height=450, showlegend=False)
fig_box.update_yaxes(title="Faturamento por Unidade (R$)", showgrid=True, gridcolor="#1f2937")
fig_box.update_xaxes(title="")
fig_box.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Faturamento: R$ %{y:,.2f}<br>Ticket Médio: R$ %{customdata[1]:,.2f}<extra></extra>")
st.plotly_chart(fig_box, use_container_width=True)

# ── 3. Visão Micro: Top 10 Concessionárias (Vertical) & Ranking ───────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
g1, g2 = st.columns([1.5, 1])

with g1:
    st.markdown('<p class="stitle">🏢 Top 10 Concessionárias em Faturamento</p>', unsafe_allow_html=True)
    t10 = d.nlargest(10, "Total_Vendas").copy()
    t10["Nome"] = t10.Concessionaria.str.replace("NovaDrive ", "", regex=False)
    
    fig_bar = px.bar(
        t10, x="Nome", y="Total_Vendas", text=t10["Total_Vendas"].apply(lambda x: f"R$ {x/1e6:.1f}M"),
        color="Total_Vendas", color_continuous_scale="Purples"
    )
    fig_bar.update_traces(textposition="outside", hovertemplate="<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>")
    fig_bar.update_layout(**LAYOUT, height=400, showlegend=False, coloraxis_showscale=False)
    fig_bar.update_xaxes(title="")
    fig_bar.update_yaxes(title="Faturamento (R$)")
    st.plotly_chart(fig_bar, use_container_width=True)

with g2:
    st.markdown('<p class="stitle">🏆 Ranking de Estados</p>', unsafe_allow_html=True)
    rk = ve.sort_values("Total_Vendas", ascending=False).copy()
    rk["R$ Mi"] = (rk.Total_Vendas/1e6).round(1)
    rk["%"] = (rk.Total_Vendas/tv*100).round(1)
    rk.insert(0, "#", range(1, len(rk)+1))
    st.dataframe(rk[["#", "Estado", "R$ Mi", "%"]].style.format({"R$ Mi": "R$ {:,.1f}M", "%": "{:.1f}%"}),
                 use_container_width=True, height=400, hide_index=True)

# ── Tabela de Dados Brutos ────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">📋 Base de Dados Consolidada</p>', unsafe_allow_html=True)
dt=d[["Concessionaria","Cidade","Estado","Qtd_Pedidos","Total_Vendas","Ticket_Medio"]].sort_values("Total_Vendas",ascending=False).copy()
dt["Total_Vendas"]=dt["Total_Vendas"].apply(lambda v:f"R$ {v:,.0f}")
dt["Ticket_Medio"]=dt["Ticket_Medio"].apply(lambda v:f"R$ {v:,.0f}")
dt.columns=["Unidade","Cidade","Estado","Pedidos","Faturamento","Ticket Médio"]
st.dataframe(dt,use_container_width=True,height=400,hide_index=True)

st.markdown('<div style="text-align:center;padding:30px 0 10px;color:#636366;font-size:11px">'
    '© 2026 NovaDrive Motors · Inteligência de Dados · Ambiente Seguro</div>',unsafe_allow_html=True)