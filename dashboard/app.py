import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import snowflake.connector

st.set_page_config(layout="wide", page_title="NovaDrive Motors", page_icon="🚗")
st.markdown("""<style>
.stApp{background:#07070f}
.mc{background:linear-gradient(145deg,#12121e,#1a1a2e);border-radius:14px;padding:20px 24px;
    box-shadow:0 8px 24px rgba(0,0,0,.5);border:1px solid #1e1e3a;min-height:115px;transition:all .25s}
.mc:hover{transform:translateY(-3px);border-color:#3b82f6}
.mc .lb{font-size:10px;color:#6b7280;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;margin:0}
.mc .vl{font-size:27px;font-weight:900;color:#f9fafb;margin:8px 0 0;line-height:1}
.mc .sb{font-size:11px;color:#4b5563;margin:6px 0 0}
.mc .accent{height:2px;border-radius:1px;margin-top:12px}
.kpi-delta-up{color:#34d399;font-size:11px;font-weight:600}
.kpi-delta-dn{color:#f87171;font-size:11px;font-weight:600}
.chip{display:inline-block;padding:2px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.5px}
.stitle{font-size:13px;font-weight:700;color:#9ca3af;padding:6px 0;border-bottom:1px solid #1e1e3a;
    display:block;margin-bottom:14px;letter-spacing:.8px;text-transform:uppercase}
.dv{height:1px;background:linear-gradient(90deg,transparent,#1e1e3a,transparent);margin:28px 0}
.card-insight{border-radius:12px;padding:14px 18px;margin-bottom:10px;border-left:3px solid}
.ci-title{font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin:0 0 4px}
.ci-body{font-size:13px;color:#d1d5db;margin:0;line-height:1.5}
.ci-body strong{color:#f9fafb}
.hero-badge{display:inline-block;padding:4px 14px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.8px}
div[data-testid="stSidebar"]{background:#0d0d1a;border-right:1px solid #1e1e3a}
div[data-testid="stSidebar"] *{color:#e5e7eb !important}
h1,h2,h3,p,span,label,.stMarkdown{color:#e5e7eb !important}
[data-testid="stDataFrame"]{border:1px solid #1e1e3a!important;border-radius:10px}
.plotly-graph-div{border-radius:12px}
</style>""", unsafe_allow_html=True)

# ── Conexão Snowflake ─────────────────────────────────────────────────────────
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
    except:
        st.error("⚠️ Configure os Secrets do Snowflake nas configurações do app.")
        st.stop()

@st.cache_data(ttl=600)
def load_data():
    df=pd.read_sql("SELECT * FROM ANALISE_VENDAS_CONCESSIONARIA", init_connection())
    df.columns=[c.upper() for c in df.columns]
    df=df.rename(columns={"CONCESSIONARIA":"Concessionaria","CIDADE":"Cidade","ESTADO":"Estado",
        "QUANTIDADE":"Qtd_Pedidos","TOTAL":"Total_Vendas","VALOR_MEDIO":"Ticket_Medio"})
    if "Ticket_Medio" not in df.columns:
        df["Ticket_Medio"]=(df["Total_Vendas"]/df["Qtd_Pedidos"]).round(2)
    return df

df=load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="padding:16px 0 20px;border-bottom:1px solid #1e1e3a;margin-bottom:16px">
    <div style="font-size:22px;font-weight:900;color:#f9fafb">🚗 NovaDrive</div>
    <div style="font-size:11px;color:#4b5563;margin-top:2px;letter-spacing:.5px">INTELIGÊNCIA COMERCIAL</div>
    </div>""", unsafe_allow_html=True)
    sel=st.multiselect("Estados",sorted(df.Estado.unique()),default=df.Estado.unique())
    st.markdown(f'<div style="margin-top:12px;font-size:11px;color:#4b5563">{len(sel)} de {df.Estado.nunique()} estados selecionados</div>',unsafe_allow_html=True)
    st.divider()
    st.caption("Fonte: Snowflake · ANALISE_VENDAS_CONCESSIONARIA\nAtualização: a cada 10 min")

d=df[df.Estado.isin(sel)] if sel else df.iloc[0:0]
if d.empty:
    st.warning("Selecione ao menos um estado."); st.stop()

# ── Cálculos ──────────────────────────────────────────────────────────────────
ve=d.groupby("Estado",as_index=False).agg(Total_Vendas=("Total_Vendas","sum"),Qtd_Pedidos=("Qtd_Pedidos","sum"))
ve["Ticket_Medio"]=ve["Total_Vendas"]/ve["Qtd_Pedidos"]
ve["Total_Mi"]=ve["Total_Vendas"]/1e6
tv=d.Total_Vendas.sum(); tq=d.Qtd_Pedidos.sum(); tk=tv/max(tq,1)
top_est=ve.loc[ve.Total_Vendas.idxmax()]; top3=ve.nlargest(3,"Total_Vendas")
pct_top3=top3.Total_Vendas.sum()/tv*100; media_est=ve.Total_Vendas.mean()
mxtk=ve.loc[ve.Ticket_Medio.idxmax()]; mntk=ve.loc[ve.Ticket_Medio.idxmin()]
mvol=ve.loc[ve.Qtd_Pedidos.idxmax()]
acima_media=ve[ve.Total_Vendas>media_est]; abaixo_media=ve[ve.Total_Vendas<=media_est]
pct_lider=top_est.Total_Vendas/tv*100

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="background:linear-gradient(135deg,#0f0f1e,#12122a);border:1px solid #1e1e3a;
    border-radius:16px;padding:22px 28px;margin-bottom:22px">
<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
  <div style="display:flex;align-items:center;gap:14px">
    <span style="font-size:28px">🚗</span>
    <div>
      <div style="font-size:22px;font-weight:900;color:#f9fafb;letter-spacing:-.3px">NovaDrive Motors</div>
      <div style="font-size:11px;color:#4b5563;margin-top:1px">Painel de Inteligência Comercial · Período Fiscal 2024</div>
    </div>
    <span class="hero-badge" style="background:#1e3a5f;color:#60a5fa;border:1px solid #2d4a7a">ANÁLISE DE VENDAS</span>
  </div>
  <div style="text-align:right">
    <div style="font-size:11px;color:#4b5563">{d.Estado.nunique()} estados · {d.Concessionaria.nunique()} unidades</div>
    <div style="font-size:11px;color:#4b5563;margin-top:2px">Snowflake · cache 10min</div>
  </div>
</div>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5=st.columns(5)
kpis=[
    (k1,"Faturamento Total",f"R$ {tv/1e6:,.1f}M",f"{d.Estado.nunique()} estados ativos","#3b82f6"),
    (k2,"Pedidos Realizados",f"{tq:,}",f"média {tq//max(d.Concessionaria.nunique(),1)}/unidade","#10b981"),
    (k3,"Ticket Médio",f"R$ {tk:,.0f}","receita por transação","#f59e0b"),
    (k4,"Estado Líder",top_est.Estado,f"{pct_lider:.1f}% do faturamento total","#8b5cf6"),
    (k5,"Acima da Média",f"{len(acima_media)}/{len(ve)}",f"estados performam acima de R$ {media_est/1e6:.1f}M","#ef4444"),
]
for col,lb,vl,sb,cor in kpis:
    col.markdown(f"""<div class="mc">
    <p class="lb">{lb}</p><p class="vl">{vl}</p><p class="sb">{sb}</p>
    <div class="accent" style="background:linear-gradient(90deg,{cor}aa,transparent)"></div>
    </div>""",unsafe_allow_html=True)

# ── Análise Estratégica ───────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
st.markdown('<span class="stitle">🧠 Análise Estratégica</span>',unsafe_allow_html=True)

col_i1,col_i2=st.columns(2)
gap_ticket=mxtk.Ticket_Medio/mntk.Ticket_Medio
pot_expansao=ve[ve.Qtd_Pedidos<ve.Qtd_Pedidos.median()].nlargest(1,"Ticket_Medio")

insights=[
    (col_i1,"#0f1e0f","#16a34a","CONCENTRAÇÃO DE RECEITA",
     f"Os 3 maiores estados — <strong>{', '.join(top3.Estado)}</strong> — respondem por <strong>{pct_top3:.0f}%</strong> do faturamento total. "
     f"Um risco de concentração relevante: queda de performance nesses mercados impacta diretamente o resultado da rede."),
    (col_i1,"#1a1a0a","#d97706","DISPERSÃO DE TICKET",
     f"O gap entre o maior e menor ticket médio é de <strong>{gap_ticket:.1f}x</strong>. "
     f"<strong>{mxtk.Estado}</strong> opera a <strong>R$ {mxtk.Ticket_Medio:,.0f}</strong>/pedido enquanto "
     f"<strong>{mntk.Estado}</strong> opera a <strong>R$ {mntk.Ticket_Medio:,.0f}</strong> — "
     f"indicando mix de produtos ou perfis de cliente muito distintos entre regiões."),
    (col_i2,"#0f0f1e","#6d28d9","EFICIÊNCIA OPERACIONAL",
     f"<strong>{mvol.Estado}</strong> lidera em volume com <strong>{int(mvol.Qtd_Pedidos):,}</strong> pedidos, "
     f"mas seu ticket médio é <strong>R$ {mvol.Ticket_Medio:,.0f}</strong>. "
     f"Alta frequência com ticket moderado — sugere produto de maior giro. Comparar mix com "
     f"<strong>{mxtk.Estado}</strong> pode revelar oportunidade de upsell."),
    (col_i2,"#1a0f0f","#dc2626","ESTADOS ABAIXO DA MÉDIA",
     f"<strong>{len(abaixo_media)}</strong> estados performam abaixo da média de <strong>R$ {media_est/1e6:.1f}M</strong>: "
     f"<strong>{', '.join(abaixo_media.nsmallest(3,'Total_Vendas').Estado)}</strong> entre os mais críticos. "
     f"Avaliar viabilidade de rede nesses mercados ou realocar recursos para estados de maior retorno."),
]
for col,bg,bor,title,body in insights:
    col.markdown(f"""<div class="card-insight" style="background:{bg};border-color:{bor}">
    <p class="ci-title" style="color:{bor}">{title}</p>
    <p class="ci-body">{body}</p>
    </div>""",unsafe_allow_html=True)

# ── Layout Plotly ─────────────────────────────────────────────────────────────
BG=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af",size=11),margin=dict(l=10,r=90,t=30,b=10),
    xaxis=dict(showgrid=True,gridcolor="#111827",zeroline=False),
    yaxis=dict(showgrid=False,tickfont=dict(size=10)))

def hbar(df_,xcol,ycol,texts,color_hex,height=400,xtitle=""):
    r,g,b=int(color_hex[1:3],16),int(color_hex[3:5],16),int(color_hex[5:7],16)
    vals=df_[xcol].values; mn,mx=vals.min(),vals.max()+1
    clrs=[f"rgba({r},{g},{b},{0.25+0.75*(v-mn)/(mx-mn):.2f})" for v in vals]
    fig=go.Figure(go.Bar(x=df_[xcol],y=df_[ycol],orientation="h",
        marker_color=clrs,text=texts,textposition="outside",
        textfont=dict(size=10,color="#e5e7eb"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"))
    fig.update_layout(**BG,height=height)
    fig.update_xaxes(title=xtitle,showgrid=True,gridcolor="#111827") 
    return fig

# ── Market Share Treemap ──────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
st.markdown('<span class="stitle">🗺️ Distribuição de Market Share por Estado</span>',unsafe_allow_html=True)
st.caption("Área proporcional ao faturamento. Estados maiores dominam o mix de receita — útil para priorização de recursos e metas regionais.")
fig_tree=px.treemap(ve,path=[px.Constant("Rede NovaDrive"),"Estado"],values="Total_Vendas",
    color="Ticket_Medio",color_continuous_scale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#f59e0b"]],
    hover_data={"Total_Mi":":.1f"})
fig_tree.update_traces(textfont=dict(size=13),textinfo="label+percent parent",
    hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.0f}<br>Ticket Médio: R$ %{color:,.0f}<extra></extra>",
    marker=dict(line=dict(color="#07070f",width=2)))
fig_tree.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af",size=11),
    height=420,margin=dict(l=10,r=10,t=10,b=10),
    coloraxis_colorbar=dict(title="Ticket R$",tickformat=",.0f"))
st.plotly_chart(fig_tree,use_container_width=True)

# ── Faturamento vs Média + Pedidos ────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
g1,g2=st.columns(2)

with g1:
    st.markdown('<span class="stitle">💰 Faturamento por Estado vs. Média da Rede</span>',unsafe_allow_html=True)
    st.caption("Linha vermelha = média nacional. Barras acima indicam mercados estratégicos.")
    df_f=ve.sort_values("Total_Vendas",ascending=True)
    fig_f=hbar(df_f,"Total_Mi","Estado",[f"R$ {v:.1f}M" for v in df_f.Total_Mi],"#3b82f6",440,"R$ Milhões")
    fig_f.add_vline(x=media_est/1e6,line=dict(color="#ef4444",width=1.5,dash="dash"))
    fig_f.add_annotation(x=media_est/1e6,y=0,text=f"Média R$ {media_est/1e6:.1f}M",
        showarrow=False,xshift=45,font=dict(color="#ef4444",size=10))
    st.plotly_chart(fig_f,use_container_width=True)

with g2:
    st.markdown('<span class="stitle">📦 Volume de Pedidos por Estado</span>',unsafe_allow_html=True)
    st.caption("Volume operacional. Discrepâncias entre ranking de volume e faturamento revelam diferenças de ticket.")
    df_q=ve.sort_values("Qtd_Pedidos",ascending=True)
    fig_q=hbar(df_q,"Qtd_Pedidos","Estado",[f"{int(v):,}" for v in df_q.Qtd_Pedidos],"#10b981",440,"Pedidos")
    st.plotly_chart(fig_q,use_container_width=True)

# ── Ticket Médio ──────────────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
st.markdown('<span class="stitle">🎯 Ticket Médio por Estado — Análise de Mix e Premiumização</span>',unsafe_allow_html=True)
st.caption(f"Gap de {gap_ticket:.1f}x entre maior e menor ticket sugere perfis de mercado radicalmente diferentes. "
           f"Estados com alto ticket e baixo volume são candidatos a campanhas de geração de demanda.")
df_tk=ve.sort_values("Ticket_Medio",ascending=True)
fig_tk=go.Figure(go.Bar(x=df_tk["Ticket_Medio"],y=df_tk["Estado"],orientation="h",
    marker=dict(color=df_tk["Ticket_Medio"],
        colorscale=[[0,"#064e3b"],[0.35,"#059669"],[0.7,"#d97706"],[1,"#dc2626"]],
        showscale=True,colorbar=dict(title="R$/pedido",tickformat=",.0f",len=0.8,x=1.01)),
    text=[f"R$ {v:,.0f}" for v in df_tk["Ticket_Medio"]],
    textposition="outside",textfont=dict(size=10,color="#e5e7eb"),
    hovertemplate="<b>%{y}</b><br>Ticket Médio: R$ %{x:,.0f}<extra></extra>"))
fig_tk.add_vline(x=tk,line=dict(color="#f9fafb",width=1,dash="dot"))
fig_tk.add_annotation(x=tk,y=0,text=f"Média R$ {tk:,.0f}",showarrow=False,
    xshift=50,font=dict(color="#9ca3af",size=10))
fig_tk.update_layout(**BG,height=440)
fig_tk.update_xaxes(title="Ticket Médio (R$)",tickformat=",.0f") 
st.plotly_chart(fig_tk,use_container_width=True)

# ── Scatter Estratégico ───────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
st.markdown('<span class="stitle">🔍 Matriz Estratégica: Volume × Faturamento</span>',unsafe_allow_html=True)
st.caption("Quadrante superior direito = mercados de alto valor e alta frequência (prioridade máxima). "
           "Superior esquerdo = alto valor, baixo volume (potencial de expansão). "
           "Tamanho da bolha = ticket médio.")
fig_sc=px.scatter(ve,x="Qtd_Pedidos",y="Total_Mi",size="Ticket_Medio",color="Ticket_Medio",
    text="Estado",color_continuous_scale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#f59e0b"]],
    labels={"Qtd_Pedidos":"Volume de Pedidos","Total_Mi":"Faturamento (R$ Mi)","Ticket_Medio":"Ticket Médio"})
fig_sc.update_traces(textposition="top center",textfont=dict(size=9,color="#e5e7eb"),
    marker=dict(line=dict(width=1,color="#ffffff15"),sizemin=8))
fig_sc.add_hline(y=ve.Total_Mi.median(),line=dict(color="#374151",width=1,dash="dot"))
fig_sc.add_vline(x=ve.Qtd_Pedidos.median(),line=dict(color="#374151",width=1,dash="dot"))
fig_sc.update_layout(**BG,height=440,
    xaxis=dict(title="Volume de Pedidos",showgrid=True,gridcolor="#111827"),
    yaxis=dict(title="Faturamento (R$ Mi)",showgrid=True,gridcolor="#111827"),
    coloraxis_colorbar=dict(title="Ticket R$",tickformat=",.0f"),
    margin=dict(l=10,r=80,t=30,b=10))
st.plotly_chart(fig_sc,use_container_width=True)

# ── Top 10 + Ranking ──────────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
g3,g4=st.columns([1.4,0.6])

with g3:
    st.markdown('<span class="stitle">🏢 Top 10 Concessionárias por Faturamento</span>',unsafe_allow_html=True)
    st.caption("As unidades de maior receita. Identificar padrões de localização e gestão para replicar nas demais.")
    t10=d.nlargest(10,"Total_Vendas").copy()
    t10["Nome"]=t10.Concessionaria.str.replace("Concessionaria NovaDrive Motors ","",regex=False).str.replace("NovaDrive ","",regex=False)
    t10["Mi"]=(t10.Total_Vendas/1e6).round(1)
    t10=t10.sort_values("Total_Vendas",ascending=True)
    fig_t10=hbar(t10,"Mi","Nome",[f"R$ {v:.1f}M" for v in t10.Mi],"#8b5cf6",380,"R$ Milhões")
    st.plotly_chart(fig_t10,use_container_width=True)

with g4:
    st.markdown('<span class="stitle">🏆 Ranking por Estado</span>',unsafe_allow_html=True)
    rk=ve.sort_values("Total_Vendas",ascending=False).copy()
    rk["R$ Mi"]=(rk.Total_Vendas/1e6).round(1)
    rk["%"]=(rk.Total_Vendas/tv*100).round(1)
    rk["Ticket"]=rk["Ticket_Medio"].apply(lambda v:f"R$ {v:,.0f}")
    rk.insert(0,"#",range(1,len(rk)+1))
    st.dataframe(rk[["#","Estado","R$ Mi","%","Ticket"]].style.format({"R$ Mi":"R$ {:,.1f}M","%":"{:.1f}%"}),
        use_container_width=True,height=380,hide_index=True)

# ── Tabela ────────────────────────────────────────────────────────────────────
st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
st.markdown('<span class="stitle">📋 Base de Dados Consolidada</span>',unsafe_allow_html=True)
dt=d[["Concessionaria","Cidade","Estado","Qtd_Pedidos","Total_Vendas","Ticket_Medio"]].sort_values("Total_Vendas",ascending=False).copy()
dt["Total_Vendas"]=dt["Total_Vendas"].apply(lambda v:f"R$ {v:,.0f}")
dt["Ticket_Medio"]=dt["Ticket_Medio"].apply(lambda v:f"R$ {v:,.0f}")
dt.columns=["Unidade","Cidade","Estado","Pedidos","Faturamento","Ticket Médio"]
st.dataframe(dt,use_container_width=True,height=420,hide_index=True)

st.markdown('<div style="text-align:center;padding:24px 0 8px;color:#374151;font-size:10px;letter-spacing:.5px">'
    '© 2024 NOVADRIVE MOTORS · INTELIGÊNCIA COMERCIAL · DADOS CONFIDENCIAIS</div>',unsafe_allow_html=True)