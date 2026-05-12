import streamlit as st
import pandas as pd
import random

st.set_page_config(layout="wide", page_title="NovaDrive Motors", page_icon="🚗")
st.markdown("""<style>
.stApp{background:#111}
.mc{background:#1C1C1E;border-radius:12px;padding:20px 24px;color:#fff;box-shadow:0 4px 16px rgba(0,0,0,.3);border:1px solid #2a2a2c;min-height:110px}
.mc .lb{margin:0;font-size:11px;color:#8E8E93;font-weight:600;letter-spacing:.8px;text-transform:uppercase}
.mc .vl{margin:8px 0 0;font-size:26px;font-weight:800;color:#fff;line-height:1.1}
.mc .sb{margin:6px 0 0;font-size:11px;color:#636366}
.st{font-size:14px;font-weight:700;color:#E5E5EA;padding:8px 0;border-bottom:2px solid #3A3A3C;display:inline-block;margin-bottom:8px}
.dv{height:1px;background:linear-gradient(90deg,transparent,#3A3A3C,transparent);margin:18px 0}
.ins{background:#1a2744;border:1px solid #2d4a7a;border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:12px;color:#c8d6f0}
.ins span{font-weight:700;color:#60a5fa}
div[data-testid="stSidebar"]{background:#1C1C1E}
div[data-testid="stSidebar"] *{color:#E5E5EA !important}
h1,h2,h3,h4,h5,h6,p,span,label,.stMarkdown{color:#E5E5EA !important}
[data-testid="stDataFrame"]{border:1px solid #2a2a2c;border-radius:8px}
</style>""", unsafe_allow_html=True)

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

st.sidebar.markdown("### 🚗 NovaDrive Motors\n---")
sel=st.sidebar.multiselect("Filtrar por Estado",sorted(df.Estado.unique()),default=df.Estado.unique())
d=df[df.Estado.isin(sel)]

if not d.empty:
    ve=d.groupby("Estado",as_index=False).agg(Total_Vendas=("Total_Vendas","sum"),Qtd_Pedidos=("Qtd_Pedidos","sum"))
    ve["Ticket_Medio"]=ve["Total_Vendas"]/ve["Qtd_Pedidos"]
    ve["Total_Mi"]=ve["Total_Vendas"]/1e6
    tv=d.Total_Vendas.sum(); tq=d.Qtd_Pedidos.sum()
    tk=tv/max(tq,1); top=ve.loc[ve.Total_Vendas.idxmax(),"Estado"] if len(ve) else "-"
    topv=ve.Total_Vendas.max() if len(ve) else 0

    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
    <span style="font-size:28px;font-weight:800;color:#fff">🚗 NovaDrive Motors</span>
    <span style="background:#3A3A3C;color:#E5E5EA;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600">DASHBOARD DE VENDAS</span>
    </div>
    <p style="color:#636366!important;margin:0 0 16px;font-size:12px">{d.Estado.nunique()} estados &bull; {d.Concessionaria.nunique()} concessionárias</p>""",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    for col,lb,vl,sb in[(c1,"Faturamento Total",f"R$ {tv/1e6:,.1f}M",f"{d.Estado.nunique()} estados"),
        (c2,"Pedidos Realizados",f"{tq:,}",f"{d.Concessionaria.nunique()} unidades"),
        (c3,"Ticket Médio",f"R$ {tk:,.0f}","por venda"),
        (c4,"Melhor Estado",top,f"R$ {topv/1e6:,.1f}M")]:
        col.markdown(f'<div class="mc"><p class="lb">{lb}</p><p class="vl">{vl}</p><p class="sb">{sb}</p></div>',unsafe_allow_html=True)

    st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
    top3=ve.nlargest(3,"Total_Vendas"); pct=top3.Total_Vendas.sum()/tv*100
    mxtk=ve.loc[ve.Ticket_Medio.idxmax()]
    i1,i2=st.columns(2)
    i1.markdown(f'<div class="ins">🥇 <span>{top}</span> lidera com <span>R$ {topv/1e6:.1f}M</span> em faturamento</div>',unsafe_allow_html=True)
    i1.markdown(f'<div class="ins">📈 Top 3 concentram <span>{pct:.0f}%</span> das vendas: <span>{", ".join(top3.Estado)}</span></div>',unsafe_allow_html=True)
    i2.markdown(f'<div class="ins">💎 Maior ticket médio: <span>{mxtk.Estado}</span> — <span>R$ {mxtk.Ticket_Medio:,.0f}</span>/pedido</div>',unsafe_allow_html=True)
    i2.markdown(f'<div class="ins">⚡ Maior volume: <span>{ve.loc[ve.Qtd_Pedidos.idxmax(),"Estado"]}</span> com <span>{int(ve.Qtd_Pedidos.max()):,}</span> pedidos</div>',unsafe_allow_html=True)

    st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
    g1,g2=st.columns(2)

    with g1:
        st.markdown('<p class="st">💰 Faturamento por Estado (R$ Mi)</p>',unsafe_allow_html=True)
        fat=ve.sort_values("Total_Vendas",ascending=False).copy()
        fat["R$ Mi"]=fat["Total_Mi"].round(1)
        fat=fat.set_index("Estado")[["R$ Mi"]]
        st.bar_chart(fat,color="#3b82f6",height=380)

    with g2:
        st.markdown('<p class="st">📦 Pedidos por Estado</p>',unsafe_allow_html=True)
        ped=ve.sort_values("Qtd_Pedidos",ascending=False).set_index("Estado")[["Qtd_Pedidos"]]
        ped.columns=["Pedidos"]
        st.bar_chart(ped,color="#10b981",height=380)

    st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
    g3,g4=st.columns([1.3,0.7])

    with g3:
        st.markdown('<p class="st">🎯 Ticket Médio por Estado (R$ mil)</p>',unsafe_allow_html=True)
        tkt=ve.sort_values("Ticket_Medio",ascending=False).copy()
        tkt["R$ Mil"]=(tkt["Ticket_Medio"]/1000).round(1)
        tkt=tkt.set_index("Estado")[["R$ Mil"]]
        st.bar_chart(tkt,color="#f59e0b",height=360)
        st.caption("Valores em R$ mil por pedido")

    with g4:
        st.markdown('<p class="st">🏆 Ranking por Estado</p>',unsafe_allow_html=True)
        rk=ve.sort_values("Total_Vendas",ascending=False).copy()
        rk["R$ Mi"]=(rk.Total_Vendas/1e6).round(1)
        rk["%"]=(rk.Total_Vendas/tv*100).round(1)
        rk.insert(0,"#",range(1,len(rk)+1))
        st.dataframe(rk[["#","Estado","R$ Mi","%"]].style.format({"R$ Mi":"R$ {:,.1f}M","%":"{:.1f}%"}),
            use_container_width=True,height=360,hide_index=True)

    st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
    st.markdown('<p class="st">🏢 Top 10 Concessionárias (R$ Mi)</p>',unsafe_allow_html=True)
    t10=d.nlargest(10,"Total_Vendas").copy()
    t10["Concessionaria"]=t10.Concessionaria.str.replace("NovaDrive ","",regex=False)
    t10["R$ Mi"]=(t10["Total_Vendas"]/1e6).round(1)
    t10=t10.sort_values("Total_Vendas",ascending=False).set_index("Concessionaria")[["R$ Mi"]]
    st.bar_chart(t10,color="#8b5cf6",height=300)
    st.caption("Valores em R$ milhões")

    st.markdown('<div class="dv"></div>',unsafe_allow_html=True)
    st.markdown('<p class="st">📋 Detalhes por Concessionária</p>',unsafe_allow_html=True)
    dt=d[["Concessionaria","Cidade","Estado","Qtd_Pedidos","Total_Vendas","Ticket_Medio"]].sort_values("Total_Vendas",ascending=False).copy()
    
    dt["Total_Vendas"]=dt["Total_Vendas"].apply(lambda v:f"R$ {v:,.0f}")
    dt["Ticket_Medio"]=dt["Ticket_Medio"].apply(lambda v:f"R$ {v:,.0f}")
    dt.columns=["Concessionaria","Cidade","Estado","Pedidos","Total Vendas","Ticket Médio"]
    st.dataframe(dt,use_container_width=True,height=400,hide_index=True)

else:
    st.warning("Selecione pelo menos um estado para visualizar os dados.")

st.markdown('<div style="text-align:center;padding:16px 0 8px;color:#636366;font-size:11px">© 2025 NovaDrive Motors · Dashboard de Vendas</div>',unsafe_allow_html=True)
