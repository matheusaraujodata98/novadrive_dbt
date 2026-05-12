import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide", page_title="NovaDrive Motors", page_icon="🚗")

# ── Estilos CSS ───────────────────────────────────────────────────────────────
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

# ── Métricas Iniciais ─────────────────────────────────────────────────────────
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

# ── Helpers Plotly Otimizados ─────────────────────────────────────────────────
LAYOUT=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af",size=12),margin=dict(l=10,r=10,t=30,b=10))

def plot_bar(df_, x, y, orient='h', cor="#3b82f6", text_col=None):
    df_top = df_.nlargest(12, x if orient=='v' else x).copy()
    df_sorted = df_top.sort_values(by=x if orient=='v' else x, ascending=(orient=='h'))
    
    fig = go.Figure(go.Bar(
        x=df_sorted[x] if orient=='v' else df_sorted[x],
        y=df_sorted[y] if orient=='v' else df_sorted[y],
        orientation=orient,
        marker=dict(color=cor),
        text=df_sorted[text_col] if text_col else None,
        textposition="outside",
        textfont=dict(color="#fff", size=11)
    ))
    
    fig.update_layout(**LAYOUT, height=400)
    if orient == 'h':
        fig.update_xaxes(showgrid=True, gridcolor="#1f2937", title="")
        fig.update_yaxes(showgrid=False)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#1f2937", title="")
    return fig

# ── Seção 1: O "Onde" e o "Quanto" (Top 12) ───────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown('<p class="stitle">💰 Top 12: Faturamento (Horizontal)</p>', unsafe_allow_html=True)
    ve["Format_Mi"] = ve["Total_Mi"].apply(lambda x: f"R$ {x:.1f}M")
    fig_fat = plot_bar(ve, "Total_Mi", "Estado", orient='h', cor="#3b82f6", text_col="Format_Mi")
    st.plotly_chart(fig_fat, use_container_width=True)

with c2:
    st.markdown('<p class="stitle">📦 Top 12: Volume de Pedidos (Vertical)</p>', unsafe_allow_html=True)
    ve["Format_Ped"] = ve["Qtd_Pedidos"].apply(lambda x: f"{int(x):,}")
    fig_ped = plot_bar(ve, "Qtd_Pedidos", "Estado", orient='v', cor="#10b981", text_col="Format_Ped")
    st.plotly_chart(fig_ped, use_container_width=True)

# ── Seção 2: Matriz de Performance (Scatter Plot) ─────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">🔍 Matriz de Eficiência: Volume vs Faturamento</p>', unsafe_allow_html=True)
st.caption("Bolhas maiores indicam um Ticket Médio mais alto. Quadrante superior direito = Alta Performance.")

fig_scatter = px.scatter(
    ve, x="Qtd_Pedidos", y="Total_Mi", size="Ticket_Medio", color="Ticket_Medio",
    text="Estado", color_continuous_scale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#f59e0b"]],
    labels={"Qtd_Pedidos": "Quantidade de Pedidos", "Total_Mi": "Faturamento (R$ Mi)", "Ticket_Medio": "Ticket Médio"}
)

fig_scatter.update_traces(
    textposition="top center", textfont=dict(size=11, color="#e5e5ea"),
    marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.3)"))
)

fig_scatter.update_layout(
    **LAYOUT, height=450, coloraxis_colorbar=dict(title="Ticket (R$)", tickformat=",.0f")
)
fig_scatter.update_xaxes(showgrid=True, gridcolor="#1f2937")
fig_scatter.update_yaxes(showgrid=True, gridcolor="#1f2937")

st.plotly_chart(fig_scatter, use_container_width=True)

# ── Seção 3: Market Share e Tabela Geral ──────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
c3, c4 = st.columns([1.0, 1.0])

with c3:
    st.markdown('<p class="stitle">🍩 Concentração de Receita (Top 5 vs Outros)</p>', unsafe_allow_html=True)
    
    # Lógica para separar os 5 maiores e agrupar o resto em "Outros"
    top5_df = ve.nlargest(5, "Total_Vendas")
    outros_val = ve[~ve["Estado"].isin(top5_df["Estado"])]["Total_Vendas"].sum()
    
    donut_data = pd.DataFrame({
        "Categoria": top5_df["Estado"].tolist() + ["Outros Estados"],
        "Valor": top5_df["Total_Vendas"].tolist() + [outros_val]
    })
    # Remove "Outros" se for 0
    donut_data = donut_data[donut_data["Valor"] > 0]
    
    fig_donut = px.pie(
        donut_data, names="Categoria", values="Valor", hole=0.6,
        color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#374151"]
    )
    fig_donut.update_traces(
        textposition='inside', textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
        marker=dict(line=dict(color='#0a0a0f', width=2))
    )
    fig_donut.update_layout(
        margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=400, showlegend=False
    )
    # Colocando o total no meio da rosca
    fig_donut.add_annotation(
        text=f"<b>R$ {tv/1e6:.1f}M</b><br><span style='font-size:12px;color:#9ca3af'>Total</span>", 
        x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="#fff")
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with c4:
    st.markdown('<p class="stitle">🏆 Base de Dados (Todos os Estados)</p>', unsafe_allow_html=True)
    rk = ve.sort_values("Total_Vendas", ascending=False).copy()
    rk["Faturamento"] = rk["Total_Mi"].map("R$ {:,.1f}M".format)
    rk["Ticket"] = rk["Ticket_Medio"].map("R$ {:,.0f}".format)
    st.dataframe(rk[["Estado", "Faturamento", "Qtd_Pedidos", "Ticket"]], use_container_width=True, hide_index=True, height=400)

st.markdown('<div style="text-align:center;padding:20px;color:#636366;font-size:11px">© 2026 NovaDrive Motors</div>', unsafe_allow_html=True)