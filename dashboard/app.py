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
LAYOUT=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af",size=11),margin=dict(l=10,r=80,t=10,b=10),
    xaxis=dict(showgrid=True,gridcolor="#1f2937",zeroline=False),
    yaxis=dict(showgrid=False,tickfont=dict(size=10)))

def hbar(df_,x,y,txt,cor,height=400):
    cor_rgba = f"rgba({int(cor[1:3],16)}, {int(cor[3:5],16)}, {int(cor[5:7],16)}, 0.33)"
    fig=go.Figure(go.Bar(x=df_[x],y=df_[y],orientation="h",
        marker=dict(color=df_[x],colorscale=[[0,cor_rgba],[1,cor]],showscale=False),
        text=txt,textposition="outside",textfont=dict(size=10,color="#e5e5ea"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"))
    fig.update_layout(**LAYOUT,height=height)
    fig.update_xaxes(showgrid=True,gridcolor="#1f2937")
    return fig

# ── Gráficos de Faturamento e Volume ──────────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
g1,g2=st.columns(2)

with g1:
    st.markdown('<p class="stitle">💰 Volume Financeiro por Estado</p>', unsafe_allow_html=True)
    fat=ve.sort_values("Total_Vendas",ascending=True)
    fig=hbar(fat,"Total_Mi","Estado",[f"R$ {v:.1f}M" for v in fat.Total_Mi],"#3b82f6",420)
    fig.update_xaxes(title="R$ Milhões") 
    st.plotly_chart(fig,use_container_width=True)

with g2:
    st.markdown('<p class="stitle">📦 Volume de Pedidos por Estado</p>', unsafe_allow_html=True)
    ped=ve.sort_values("Qtd_Pedidos",ascending=True)
    fig=hbar(ped,"Qtd_Pedidos","Estado",[f"{int(v):,}" for v in ped.Qtd_Pedidos],"#10b981",420)
    fig.update_xaxes(title="Total de Pedidos") 
    st.plotly_chart(fig,use_container_width=True)

# ── Gráfico de Ticket Médio ───────────────────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">🎯 Eficiência de Venda (Ticket Médio)</p>', unsafe_allow_html=True)
tkt=ve.sort_values("Ticket_Medio",ascending=True)
fig3=go.Figure(go.Bar(x=tkt["Ticket_Medio"],y=tkt["Estado"],orientation="h",
    marker=dict(color=tkt["Ticket_Medio"],
        colorscale=[[0,"#064e3b"],[0.4,"#f59e0b"],[1,"#ef4444"]],
        showscale=True,colorbar=dict(title="R$",tickformat=",.0f",len=0.8)),
    text=[f"R$ {v:,.0f}" for v in tkt["Ticket_Medio"]],
    textposition="outside",textfont=dict(size=10,color="#e5e5ea"),
    hovertemplate="<b>%{y}</b><br>Ticket: R$ %{x:,.0f}<extra></extra>"))
fig3.update_layout(**LAYOUT,height=420)
fig3.update_xaxes(title="R$ por Unidade",tickformat=",.0f") 
st.plotly_chart(fig3,use_container_width=True)

# ── Top 10 e Ranking Auxiliar ─────────────────────────────────────────────────
st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
g3,g4=st.columns([1.4,0.6])

with g3:
    st.markdown('<p class="stitle">🏢 Performance Individual: Top 10 Concessionárias</p>', unsafe_allow_html=True)
    t10=d.nlargest(10,"Total_Vendas").copy()
    t10["Nome"]=t10.Concessionaria.str.replace("NovaDrive ","",regex=False)
    t10["Mi"]=(t10.Total_Vendas/1e6).round(1)
    t10=t10.sort_values("Total_Vendas",ascending=True)
    fig4=hbar(t10,"Mi","Nome",[f"R$ {v:.1f}M" for v in t10.Mi],"#8b5cf6",380)
    fig4.update_xaxes(title="R$ Milhões") 
    st.plotly_chart(fig4,use_container_width=True)

with g4:
    st.markdown('<p class="stitle">🏆 Ranking de Estados</p>', unsafe_allow_html=True)
    rk=ve.sort_values("Total_Vendas",ascending=False).copy()
    rk["R$ Mi"]=(rk.Total_Vendas/1e6).round(1)
    rk["%"]=(rk.Total_Vendas/tv*100).round(1)
    rk.insert(0,"#",range(1,len(rk)+1))
    st.dataframe(rk[["#","Estado","R$ Mi","%"]].style.format({"R$ Mi":"R$ {:,.1f}M","%":"{:.1f}%"}),
        use_container_width=True,height=380,hide_index=True)

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