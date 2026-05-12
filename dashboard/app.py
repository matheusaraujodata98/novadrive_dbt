import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide", page_title="NovaDrive Motors", page_icon="🚗")

# ── Estilos CSS de Alta Performance ──────────────────────────────────────────
st.markdown("""<style>
.stApp{background:#0a0a0f}
.mc{background:linear-gradient(135deg,#1C1C1E,#252530);border-radius:16px;padding:22px 26px;color:#fff;
    box-shadow:0 8px 32px rgba(0,0,0,.4);border:1px solid #2a2a3a;min-height:120px;transition:transform .2s}
.mc:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.5)}
.mc .lb{margin:0;font-size:11px;color:#8E8E93;font-weight:600;letter-spacing:1px;text-transform:uppercase}
.mc .vl{margin:10px 0 0;font-size:28px;font-weight:800;color:#fff;line-height:1.1}
.mc .sb{margin:6px 0 0;font-size:11px;color:#636366}
.mc .bar{height:3px;border-radius:2px;margin-top:14px;opacity:.7}
.stitle{font-size:16px;font-weight:700;color:#E5E5EA;padding:8px 0 6px;border-bottom:2px solid #3b82f6;
    display:inline-block;margin-bottom:15px;letter-spacing:.5px}
.dv{height:1px;background:linear-gradient(90deg,transparent,#2a2a3a,transparent);margin:24px 0}
.ins{border-radius:10px;padding:12px 16px;margin-bottom:8px;font-size:13px;display:flex;align-items:flex-start;gap:10px}
h1,h2,h3,h4,h5,h6,p,span,label,.stMarkdown{color:#E5E5EA !important}
.hero{background:linear-gradient(135deg,#0f0f1a,#1a1a2e);border:1px solid #2a2a4a;
    border-radius:16px;padding:24px 30px;margin-bottom:20px}
</style>""", unsafe_allow_html=True)

# ── Gerador de Dados ──────────────────────────────────────────────────────────
random.seed(42)
raw=[("Belo Horizonte","MINAS GERAIS"),("Uberlandia","MINAS GERAIS"),("Juiz de Fora","MINAS GERAIS"),
    ("Sao Paulo Centro","SAO PAULO"),("Sao Paulo Zona Sul","SAO PAULO"),("Campinas","SAO PAULO"),("Santos","SAO PAULO"),
    ("Rio de Janeiro Centro","RIO DE JANEIRO"),("Rio de Janeiro Barra","RIO DE JANEIRO"),("Niteroi","RIO DE JANEIRO"),
    ("Curitiba","PARANA"),("Londrina","PARANA"),("Maringa","PARANA"),
    ("Porto Alegre","RIO GRANDE DO SUL"),("Caxias do Sul","RIO GRANDE DO SUL"),
    ("Salvador","BAHIA"),("Feira de Santana","BAHIA"),("Vitoria da Conquista","BAHIA"),
    ("Recife","PERNAMBUCO"),("Caruaru","PERNAMBUCO"),("Goiania","GOIAS"),("Anapolis","GOIAS"),
    ("Brasilia Asa Norte","DISTRITO FEDERAL"),("Brasilia Asa Sul","DISTRITO FEDERAL"),
    ("Florianopolis","SANTA CATARINA"),("Joinville","SANTA CATARINA"),
    ("Fortaleza","CEARA"),("Juazeiro do Norte","CEARA"),("Manaus","AMAZONAS"),
    ("Belem","PARA"),("Vitoria","ESPIRITO SANTO"),("Campo Grande","MATO GROSSO DO SUL")]

data=[{"Concessionaria":f"NovaDrive {c}","Cidade":c,"Estado":e,
    "Qtd_Pedidos":random.randint(20,350),"Total_Vendas":round(random.uniform(800_000,12_000_000),2)}
    for c,e in raw]
df=pd.DataFrame(data)
df["Ticket_Medio"]=(df["Total_Vendas"]/df["Qtd_Pedidos"]).round(2)

# ── Cabeçalho e Filtro ────────────────────────────────────────────────────────
st.markdown(f"""<div class="hero">
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px">
  <span style="font-size:32px">🚗</span>
  <div>
    <span style="font-size:26px;font-weight:800;color:#fff">NovaDrive Motors</span>
    <span style="background:#3b82f6;color:#fff;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:600;margin-left:10px">ANÁLISE DE PERFORMANCE</span>
  </div>
</div>
<p style="color:#636366;margin:0;font-size:12px">Painel Gerencial &bull; {df.Estado.nunique()} estados &bull; Dados em Tempo Real</p>
</div>""", unsafe_allow_html=True)

sel = st.multiselect("🗺️ Filtro de Região", sorted(df.Estado.unique()), default=df.Estado.unique())
d=df[df.Estado.isin(sel)] if sel else df.iloc[0:0]

if d.empty:
    st.warning("Selecione um estado para carregar.")
    st.stop()

# ── Métricas de Storytelling ──────────────────────────────────────────────────
ve=d.groupby("Estado",as_index=False).agg(Total_Vendas=("Total_Vendas","sum"),Qtd_Pedidos=("Qtd_Pedidos","sum"))
ve["Ticket_Medio"]=ve["Total_Vendas"]/ve["Qtd_Pedidos"]
ve["Total_Mi"]=ve["Total_Vendas"]/1e6
tv=d.Total_Vendas.sum(); tq=d.Qtd_Pedidos.sum(); tk=tv/max(tq,1)
top=ve.loc[ve.Total_Vendas.idxmax(),"Estado"]; topv=ve.Total_Vendas.max()

# ── Linha 1: KPIs ─────────────────────────────────────────────────────────────
k1,k2,k3,k4=st.columns(4)
for col,lb,vl,sb,cor in [
    (k1,"Faturamento Total",f"R$ {tv/1e6:,.1f}M","Total acumulado","#3b82f6"),
    (k2,"Volume de Pedidos",f"{tq:,}","Vendas concluídas","#10b981"),
    (k3,"Ticket Médio",f"R$ {tk:,.0f}","Média por venda","#f59e0b"),
    (k4,"Liderança",top,f"R$ {topv/1e6:,.1f}M","#8b5cf6")
]:
    col.markdown(f"""<div class="mc"><p class="lb">{lb}</p><p class="vl">{vl}</p><p class="sb">{sb}</p>
    <div class="bar" style="background:linear-gradient(90deg,{cor},transparent)"></div></div>""", unsafe_allow_html=True)

# ── Helpers Plotly ────────────────────────────────────────────────────────────
LAYOUT=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af",size=11),margin=dict(l=10,r=10,t=30,b=10))

def plot_bar(df_, x, y, orient='h', cor="#3b82f6", title=""):
    # Para barras horizontais 'h', maior em cima = sort ascending=True (Plotly plota de baixo pra cima)
    # Para barras verticais 'v', maior na esquerda = sort ascending=False
    df_sorted = df_.sort_values(by=x if orient=='v' else x, ascending=(orient=='h'))
    
    fig = go.Figure(go.Bar(
        x=df_sorted[x] if orient=='v' else df_sorted[x],
        y=df_sorted[y] if orient=='v' else df_sorted[y],
        orientation=orient,
        marker=dict(color=cor),
        textposition="auto",
    ))
    fig.update_layout(**LAYOUT, height=350, title=title)
    fig.update_xaxes(showgrid=True, gridcolor="#1f2937")
    fig.update_yaxes(showgrid=False)
    return fig

# ── Seção 1: O "Onde" e o "Quanto" (Horizontal vs Vertical) ─────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown('<p class="stitle">💰 Faturamento por Estado (Horizontal)</p>', unsafe_allow_html=True)
    # Horizontal: Maior no topo
    fig_fat = plot_bar(ve, "Total_Mi", "Estado", orient='h', cor="#3b82f6")
    st.plotly_chart(fig_fat, use_container_width=True)

with c2:
    st.markdown('<p class="stitle">📦 Volume de Pedidos (Vertical)</p>', unsafe_allow_html=True)
    # Vertical: Maior na esquerda
    fig_ped = plot_bar(ve, "Qtd_Pedidos", "Estado", orient='v', cor="#10b981")
    st.plotly_chart(fig_ped, use_container_width=True)

# ── Seção 2: Visão de Árvore (Hierarquia) ─────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">🗺️ Mapa Estrutural de Vendas</p>', unsafe_allow_html=True)
fig_tree = px.treemap(ve, path=[px.Constant("Brasil"), 'Estado'], values='Total_Vendas',
                     color='Ticket_Medio', color_continuous_scale='Viridis')
fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=400, paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_tree, use_container_width=True)

# ── Seção 3: Eficiência e Ranking ─────────────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
c3, c4 = st.columns([1.2, 0.8])

with c3:
    st.markdown('<p class="stitle">🎯 Eficiência de Vendas (Ticket Médio)</p>', unsafe_allow_html=True)
    tkt_sorted = ve.sort_values("Ticket_Medio", ascending=True)
    fig_tkt = go.Figure(go.Bar(x=tkt_sorted["Ticket_Medio"], y=tkt_sorted["Estado"], orientation='h',
                              marker=dict(color=tkt_sorted["Ticket_Medio"], colorscale='Portland')))
    fig_tkt.update_layout(**LAYOUT, height=400)
    st.plotly_chart(fig_tkt, use_container_width=True)

with c4:
    st.markdown('<p class="stitle">🏆 Ranking de Performance</p>', unsafe_allow_html=True)
    rk = ve.sort_values("Total_Vendas", ascending=False).head(10)
    rk["Mi"] = rk["Total_Mi"].map("R$ {:,.1f}M".format)
    st.dataframe(rk[["Estado", "Mi", "Qtd_Pedidos"]], use_container_width=True, hide_index=True, height=400)

st.markdown('<div style="text-align:center;padding:20px;color:#636366;font-size:11px">© 2026 NovaDrive Motors</div>', unsafe_allow_html=True)