import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="NovaDrive Motors")

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

conn = st.connection("snowflake")
session = conn.session()
df = session.sql("SELECT CONCESSIONARIA, CIDADE, ESTADO, QUANTIDADE, TOTAL, VALOR_MEDIO FROM NOVADRIVE.STAGE.ANALISE_VENDAS_CONCESSIONARIA").to_pandas()

st.markdown(f"""<div class="hero">
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px">
  <span style="font-size:32px">&#128663;</span>
  <div>
    <span style="font-size:26px;font-weight:800;color:#fff">NovaDrive Motors</span>
    <span style="background:#3b82f6;color:#fff;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:600;margin-left:10px">SISTEMA DE GESTAO DE VENDAS</span>
  </div>
</div>
<p style="color:#636366;margin:0;font-size:12px">{df.ESTADO.nunique()} estados &bull; Dados reais &bull; Atualizado agora</p>
</div>""", unsafe_allow_html=True)

sel = st.multiselect("Selecionar Estados para Analise", sorted(df.ESTADO.unique()), default=sorted(df.ESTADO.unique()))
d = df[df.ESTADO.isin(sel)] if sel else df.iloc[0:0]

if d.empty:
    st.warning("Selecione pelo menos um estado.")
    st.stop()

ve = d.groupby("ESTADO", as_index=False).agg(TOTAL_VENDAS=("TOTAL", "sum"), QTD_PEDIDOS=("QUANTIDADE", "sum"))
ve["TICKET_MEDIO"] = ve["TOTAL_VENDAS"] / ve["QTD_PEDIDOS"]
ve["TOTAL_MI"] = ve["TOTAL_VENDAS"] / 1e6
tv = d.TOTAL.sum(); tq = d.QUANTIDADE.sum(); tk = tv / max(tq, 1)
top_estado = ve.loc[ve.TOTAL_VENDAS.idxmax(), "ESTADO"]
topv = ve.TOTAL_VENDAS.max()
top3 = ve.nlargest(3, "TOTAL_VENDAS")
pct = top3.TOTAL_VENDAS.sum() / tv * 100
mxtk = ve.loc[ve.TICKET_MEDIO.idxmax()]
mvol = ve.loc[ve.QTD_PEDIDOS.idxmax()]

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "Faturamento Total", f"R$ {tv/1e6:,.1f}M", f"{d.ESTADO.nunique()} estados", "#3b82f6"),
    (k2, "Pedidos Realizados", f"{tq:,}", f"{d.CONCESSIONARIA.nunique()} unidades", "#10b981"),
    (k3, "Ticket Medio", f"R$ {tk:,.0f}", "por venda", "#f59e0b"),
    (k4, "Estado Lider", top_estado, f"R$ {topv/1e6:,.1f}M faturados", "#8b5cf6"),
]
for col, lb, vl, sb, cor in kpis:
    col.markdown(f"""<div class="mc">
    <p class="lb">{lb}</p><p class="vl">{vl}</p><p class="sb">{sb}</p>
    <div class="bar" style="background:linear-gradient(90deg,{cor},transparent)"></div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">Narrativa de Performance</p>', unsafe_allow_html=True)
i1, i2 = st.columns(2)
insights = [
    (i1, "#1a2744", "#2d4a7a", "#60a5fa", "1o", f"<span style='color:#60a5fa'>{top_estado}</span> domina o ranking com <span style='color:#60a5fa'>R$ {topv/1e6:.1f}M</span> em faturamento."),
    (i1, "#1a3a2a", "#2d6a4a", "#34d399", "Top3", f"<span style='color:#34d399'>{', '.join(top3.ESTADO)}</span> somam <span style='color:#34d399'>{pct:.0f}%</span> do faturamento total."),
    (i2, "#2a1a3a", "#4a2d6a", "#a78bfa", "Ticket", f"<span style='color:#a78bfa'>{mxtk.ESTADO}</span> tem operacao mais premium: <span style='color:#a78bfa'>R$ {mxtk.TICKET_MEDIO:,.0f}</span>/pedido."),
    (i2, "#2a1a1a", "#6a2d2d", "#f87171", "Volume", f"<span style='color:#f87171'>{mvol.ESTADO}</span> lidera com <span style='color:#f87171'>{int(mvol.QTD_PEDIDOS):,}</span> pedidos."),
]
for col, bg, border, clr, icon, txt in insights:
    col.markdown(f'<div class="ins" style="background:{bg};border:1px solid {border};color:#c8d6f0">'
        f'<span style="font-size:16px;font-weight:700;color:{clr}">{icon}</span>'
        f'<span style="color:#c8d6f0">{txt}</span></div>', unsafe_allow_html=True)

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af", size=11), margin=dict(l=10, r=80, t=10, b=10),
    xaxis=dict(showgrid=True, gridcolor="#1f2937", zeroline=False),
    yaxis=dict(showgrid=False, tickfont=dict(size=10)))

def hbar(df_, x, y, txt, cor, height=400):
    cor_rgba = f"rgba({int(cor[1:3],16)},{int(cor[3:5],16)},{int(cor[5:7],16)},0.33)"
    fig = go.Figure(go.Bar(x=df_[x], y=df_[y], orientation="h",
        marker=dict(color=df_[x], colorscale=[[0, cor_rgba], [1, cor]], showscale=False),
        text=txt, textposition="outside", textfont=dict(size=10, color="#e5e5ea"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"))
    fig.update_layout(**LAYOUT, height=height)
    return fig

st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
g1, g2 = st.columns(2)

with g1:
    st.markdown('<p class="stitle">Faturamento por Estado</p>', unsafe_allow_html=True)
    fat = ve.sort_values("TOTAL_VENDAS", ascending=True)
    fig = hbar(fat, "TOTAL_MI", "ESTADO", [f"R$ {v:.1f}M" for v in fat.TOTAL_MI], "#3b82f6", 420)
    fig.update_xaxes(title="R$ Milhoes")
    st.plotly_chart(fig, use_container_width=True)

with g2:
    st.markdown('<p class="stitle">Pedidos por Estado</p>', unsafe_allow_html=True)
    ped = ve.sort_values("QTD_PEDIDOS", ascending=True)
    fig = hbar(ped, "QTD_PEDIDOS", "ESTADO", [f"{int(v):,}" for v in ped.QTD_PEDIDOS], "#10b981", 420)
    fig.update_xaxes(title="Total de Pedidos")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">Ticket Medio por Estado</p>', unsafe_allow_html=True)
tkt = ve.sort_values("TICKET_MEDIO", ascending=True)
fig3 = go.Figure(go.Bar(x=tkt["TICKET_MEDIO"], y=tkt["ESTADO"], orientation="h",
    marker=dict(color=tkt["TICKET_MEDIO"],
        colorscale=[[0, "#064e3b"], [0.4, "#f59e0b"], [1, "#ef4444"]],
        showscale=True, colorbar=dict(title="R$", tickformat=",.0f", len=0.8)),
    text=[f"R$ {v:,.0f}" for v in tkt["TICKET_MEDIO"]],
    textposition="outside", textfont=dict(size=10, color="#e5e5ea"),
    hovertemplate="<b>%{y}</b><br>Ticket: R$ %{x:,.0f}<extra></extra>"))
fig3.update_layout(**LAYOUT, height=420)
fig3.update_xaxes(title="R$ por Venda", tickformat=",.0f")
st.plotly_chart(fig3, use_container_width=True)

st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
g3, g4 = st.columns([1.4, 0.6])

with g3:
    st.markdown('<p class="stitle">Top 10 Concessionarias</p>', unsafe_allow_html=True)
    t10 = d.nlargest(10, "TOTAL").copy()
    t10["MI"] = (t10["TOTAL"] / 1e6).round(1)
    t10 = t10.sort_values("TOTAL", ascending=True)
    fig4 = hbar(t10, "MI", "CONCESSIONARIA", [f"R$ {v:.1f}M" for v in t10.MI], "#8b5cf6", 380)
    fig4.update_xaxes(title="R$ Milhoes")
    st.plotly_chart(fig4, use_container_width=True)

with g4:
    st.markdown('<p class="stitle">Ranking de Estados</p>', unsafe_allow_html=True)
    rk = ve.sort_values("TOTAL_VENDAS", ascending=False).copy()
    rk["R$ Mi"] = (rk.TOTAL_VENDAS / 1e6).round(1)
    rk["%"] = (rk.TOTAL_VENDAS / tv * 100).round(1)
    rk.insert(0, "#", range(1, len(rk) + 1))
    st.dataframe(rk[["#", "ESTADO", "R$ Mi", "%"]].style.format({"R$ Mi": "R$ {:,.1f}M", "%": "{:.1f}%"}),
        use_container_width=True, height=380, hide_index=True)

st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
st.markdown('<p class="stitle">Base de Dados Consolidada</p>', unsafe_allow_html=True)
dt = d[["CONCESSIONARIA", "CIDADE", "ESTADO", "QUANTIDADE", "TOTAL", "VALOR_MEDIO"]].sort_values("TOTAL", ascending=False).copy()
dt["TOTAL"] = dt["TOTAL"].apply(lambda v: f"R$ {v:,.0f}")
dt["VALOR_MEDIO"] = dt["VALOR_MEDIO"].apply(lambda v: f"R$ {v:,.0f}")
dt.columns = ["Unidade", "Cidade", "Estado", "Pedidos", "Faturamento", "Ticket Medio"]
st.dataframe(dt, use_container_width=True, height=400, hide_index=True)

st.markdown('<div style="text-align:center;padding:30px 0 10px;color:#636366;font-size:11px">'
    '© 2025 NovaDrive Motors - Inteligencia de Dados</div>', unsafe_allow_html=True)