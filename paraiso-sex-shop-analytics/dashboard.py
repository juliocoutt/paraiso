# =============================================================================
# PARAISO SEX SHOP — DASHBOARD PROFISSIONAL
# Como rodar: venv\Scripts\streamlit run dashboard.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64, pathlib

# ── Configuração ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Paraiso Sex Shop · Analytics",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS limpo e profissional ──────────────────────────────────────────────────

st.markdown("""
<style>
    /* Remove padding padrão */
    .block-container { padding: 2rem 2.5rem 2rem 2.5rem; }

    /* Tipografia */
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

    /* Cards de métrica */
    [data-testid="stMetric"] {
        background-color: #F9F9F9;
        border-left: 3px solid #C0392B;
        border-radius: 4px;
        padding: 20px 24px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: #111111 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #666666 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F5F5F5;
        border-right: 1px solid #E0E0E0;
    }

    /* Divisor */
    hr { border-color: #E0E0E0; }

    /* Título de seção */
    .section-title {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #666666;
        margin-bottom: 1rem;
        margin-top: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Paleta profissional: vermelho escuro + neutros
COR_PRIMARIA  = "#C0392B"
COR_HOVER     = "#E74C3C"
PAPEL         = "#FFFFFF"
PLOT_BG       = "#FAFAFA"
GRADE         = "#EEEEEE"
TEXTO         = "#111111"

PALETA = [COR_PRIMARIA, "#E74C3C", "#922B21", "#7B241C", "#F1948A", "#FADBD8"]

def layout_base():
    return dict(
        template="plotly_white",
        paper_bgcolor=PAPEL,
        plot_bgcolor=PLOT_BG,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXTO, size=12),
        margin=dict(l=16, r=16, t=40, b=16),
        xaxis=dict(showgrid=True, gridcolor=GRADE, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRADE, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(size=11)),
    )

# ── Dados ─────────────────────────────────────────────────────────────────────

@st.cache_data
def carregar():
    df  = pd.read_csv("data/ecom_data_clean.csv", encoding="utf-8-sig", parse_dates=["Data_Venda"])
    rfm = pd.read_csv("data/rfm_clientes.csv", encoding="utf-8-sig")
    return df, rfm

df, rfm = carregar()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    # Logo centralizada
    logo_path = pathlib.Path("dashboard/logo.png")
    if logo_path.exists():
        b64 = base64.b64encode(logo_path.read_bytes()).decode()
        st.markdown(
            f"<div style='text-align:center;padding:24px 0 8px'>"
            f"<img src='data:image/png;base64,{b64}' width='100'/></div>",
            unsafe_allow_html=True
        )
    st.markdown(
        "<div style='text-align:center'>"
        "<span style='font-size:1.1rem;font-weight:700;color:#C0392B'>Paraiso Sex Shop</span><br>"
        "<span style='font-size:0.72rem;color:#999;letter-spacing:0.1em;text-transform:uppercase'>Analytics</span>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)

    # Filtros
    st.markdown("<p class='section-title'>Filtros</p>", unsafe_allow_html=True)
    anos     = sorted(df["Ano"].unique(), reverse=True)
    regioes  = sorted(df["Regiao"].unique())
    cats     = sorted(df["Categoria_Produto"].unique())

    meses_nomes = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",
                   7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
    meses_nums  = sorted(df["Mes"].unique())
    meses_opts  = [meses_nomes[m] for m in meses_nums]

    ano_sel    = st.multiselect("Ano",       anos,       default=None, placeholder="Todos os anos")
    mes_sel    = st.multiselect("Mês",       meses_opts, default=None, placeholder="Todos os meses")
    regiao_sel = st.multiselect("Região",    regioes,    default=None, placeholder="Todas as regiões")
    cat_sel    = st.multiselect("Categoria", cats,       default=None, placeholder="Todas as categorias")

    # Se nada selecionado → mostra tudo
    if not ano_sel:    ano_sel    = anos
    if not mes_sel:    mes_nums_sel = meses_nums
    else:              mes_nums_sel = [k for k,v in meses_nomes.items() if v in mes_sel]
    if not regiao_sel: regiao_sel = regioes
    if not cat_sel:    cat_sel    = cats

    st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)

    # Navegação
    st.markdown("<p class='section-title'>Navegação</p>", unsafe_allow_html=True)
    pagina = st.radio("", ["Visão Geral", "Clientes", "Produtos", "Previsão"],
                      label_visibility="collapsed")

    st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)
    mask   = (df["Ano"].isin(ano_sel) & df["Mes"].isin(mes_nums_sel) &
              df["Regiao"].isin(regiao_sel) & df["Categoria_Produto"].isin(cat_sel))
    df_f   = df[mask]
    st.caption(f"{len(df_f):,} registros · {df_f['ID_Cliente'].nunique()} clientes")

# ══════════════════════════════════════════════════════════════════════════════
# VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "Visão Geral":

    data_ini = df["Data_Venda"].min().strftime("%b/%Y")
    data_fim = df["Data_Venda"].max().strftime("%b/%Y")
    st.markdown(f"""
<div style='text-align:center; padding: 32px 0 24px 0'>
    <h1 style='font-size:2.4rem; font-weight:800; margin-bottom:8px; color:#111'>
        Paraiso Sex Shop
    </h1>
    <p style='font-size:1rem; color:#C0392B; font-weight:600; margin:0; letter-spacing:0.05em'>
        DASHBOARD ANALÍTICO DE VENDAS
    </p>
    <p style='font-size:0.85rem; color:#888; margin-top:8px'>
        Análise completa do período <strong>{data_ini}</strong> a <strong>{data_fim}</strong>
        &nbsp;·&nbsp; {len(df_f):,} transações &nbsp;·&nbsp; {df_f["ID_Cliente"].nunique():,} clientes únicos
    </p>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento",     f"R$ {df_f['Valor_Total'].sum():,.0f}")
    c2.metric("Ticket Médio",    f"R$ {df_f['Valor_Total'].mean():,.2f}")
    c3.metric("Pedidos",         f"{len(df_f):,}")
    c4.metric("Clientes Únicos", f"{df_f['ID_Cliente'].nunique():,}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        cat = df_f.groupby("Categoria_Produto")["Valor_Total"].sum().reset_index().sort_values("Valor_Total")
        fig2 = go.Figure(go.Bar(
            x=cat["Valor_Total"], y=cat["Categoria_Produto"],
            orientation="h",
            marker=dict(color=COR_PRIMARIA, opacity=0.85),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        ))
        fig2.update_layout(**layout_base(), title="Receita por Categoria", height=300)
        st.plotly_chart(fig2, width="stretch")

    with col_b:
        pag = df_f.groupby("Metodo_Pagamento")["Valor_Total"].sum().reset_index()
        fig3 = go.Figure(go.Pie(
            labels=pag["Metodo_Pagamento"], values=pag["Valor_Total"],
            hole=0.6,
            marker=dict(colors=PALETA),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
        ))
        lo = layout_base()
        lo["legend"].update(orientation="v", x=1, y=0.5)
        fig3.update_layout(**lo, title="Método de Pagamento", height=300, showlegend=True)
        st.plotly_chart(fig3, width="stretch")

    # Receita por Região
    st.markdown("<br>", unsafe_allow_html=True)
    reg = df_f.groupby("Regiao")["Valor_Total"].sum().reset_index().sort_values("Valor_Total", ascending=True)
    fig_reg = go.Figure(go.Bar(
        x=reg["Valor_Total"], y=reg["Regiao"],
        orientation="h",
        marker=dict(color=COR_PRIMARIA, opacity=0.85),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    fig_reg.update_layout(**layout_base(), title="Receita por Região", height=280)
    fig_reg.update_xaxes(showticklabels=False)
    st.plotly_chart(fig_reg, width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "Clientes":

    st.markdown("## Clientes")
    st.caption("Perfil, segmentação RFM e análise regional")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Únicos",    f"{df_f['ID_Cliente'].nunique():,}")
    c2.metric("Pedidos / Cliente",  f"{len(df_f)/max(df_f['ID_Cliente'].nunique(),1):.1f}")
    c3.metric("LTV Médio",          f"R$ {df_f.groupby('ID_Cliente')['Valor_Total'].sum().mean():,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        fe = df_f.groupby("Faixa_Etaria")["Valor_Total"].sum().reset_index().sort_values("Valor_Total", ascending=True)
        fig = go.Figure(go.Bar(
            x=fe["Valor_Total"], y=fe["Faixa_Etaria"],
            orientation="h",
            marker=dict(color=COR_PRIMARIA, opacity=0.85),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**layout_base(), title="Receita por Faixa Etária", height=280)
        st.plotly_chart(fig, width="stretch")

    with col_b:
        ge = df_f.groupby("Genero_Cliente")["Valor_Total"].sum().reset_index()
        fig2 = go.Figure(go.Pie(
            labels=ge["Genero_Cliente"], values=ge["Valor_Total"],
            hole=0.6, marker=dict(colors=PALETA),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
        ))
        fig2.update_layout(**layout_base(), title="Receita por Gênero", height=280)
        st.plotly_chart(fig2, width="stretch")

    # Região
    reg = df_f.groupby("Regiao")["Valor_Total"].sum().reset_index().sort_values("Valor_Total", ascending=True)
    fig3 = go.Figure(go.Bar(
        x=reg["Valor_Total"], y=reg["Regiao"],
        orientation="h",
        marker=dict(
            color=reg["Valor_Total"],
            colorscale=[[0, "#FFE0E0"], [1, COR_PRIMARIA]],
            showscale=False,
        ),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    fig3.update_layout(**layout_base(), title="Receita por Região", height=260)
    st.plotly_chart(fig3, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Segmentação RFM")
    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        sc = rfm["Segmento"].value_counts().reset_index()
        sc.columns = ["Segmento", "Clientes"]
        fig4 = go.Figure(go.Bar(
            x=sc["Segmento"], y=sc["Clientes"],
            marker=dict(color=PALETA[:len(sc)]),
            hovertemplate="<b>%{x}</b><br>%{y} clientes<extra></extra>",
        ))
        fig4.update_layout(**layout_base(), title="Clientes por Segmento", height=280, showlegend=False)
        st.plotly_chart(fig4, width="stretch")

    with col_r2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        info = {
            "Champion":  ("🔴", "Recente, frequente, alto valor — fidelizar com VIP"),
            "Loyal":     ("🟠", "Fiel — estimular cross-sell entre categorias"),
            "Promising": ("🟡", "Recente, pouca frequência — nutrir com ofertas"),
            "At Risk":   ("⚪", "Sumiu — campanha de reativação urgente"),
            "Lost":      ("⬛", "Inativo — oferta agressiva ou aceitar churn"),
        }
        for seg, (ico, desc) in info.items():
            n = len(rfm[rfm["Segmento"] == seg])
            st.markdown(f"{ico} &nbsp; **{seg}** &nbsp; <span style='color:#666'>({n})</span> &nbsp; {desc}",
                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PRODUTOS
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "Produtos":

    st.markdown("## Produtos")
    st.caption("Performance por produto e categoria")
    st.markdown("---")

    top10 = (df_f.groupby("Nome_Produto")["Valor_Total"].sum()
               .sort_values(ascending=True).tail(10).reset_index())
    fig = go.Figure(go.Bar(
        x=top10["Valor_Total"], y=top10["Nome_Produto"],
        orientation="h",
        marker=dict(
            color=top10["Valor_Total"],
            colorscale=[[0, "#4a0a07"], [1, COR_PRIMARIA]],
            showscale=False,
        ),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**layout_base(), title="Top 10 Produtos por Receita", height=360)
    st.plotly_chart(fig, width="stretch")

    col_a, col_b = st.columns(2)

    with col_a:
        fat_cat = (df_f.groupby(["Categoria_Produto", "Nome_Produto"])["Valor_Total"]
                   .sum().reset_index())
        fig2 = px.treemap(
            fat_cat,
            path=["Categoria_Produto", "Nome_Produto"],
            values="Valor_Total",
            color="Valor_Total",
            color_continuous_scale=["#FFEEEE", COR_PRIMARIA, COR_HOVER],
        )
        fig2.update_layout(**layout_base(), title="Receita: Categoria → Produto", height=380,
                           coloraxis_showscale=False)
        fig2.update_traces(hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>")
        st.plotly_chart(fig2, width="stretch")

    with col_b:
        am = df_f.sample(min(500, len(df_f)), random_state=42)
        fig3 = go.Figure()
        for i, cat in enumerate(df_f["Categoria_Produto"].unique()):
            d = am[am["Categoria_Produto"] == cat]
            fig3.add_trace(go.Scatter(
                x=d["Desconto_Pct"], y=d["Valor_Total"],
                mode="markers",
                name=cat,
                marker=dict(size=5, opacity=0.6, color=PALETA[i % len(PALETA)]),
                hovertemplate=f"<b>{cat}</b><br>Desconto: %{{x}}%<br>Valor: R$ %{{y:,.0f}}<extra></extra>",
            ))
        fig3.update_layout(**layout_base(), title="Desconto × Valor Total", height=380)
        st.plotly_chart(fig3, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# PREVISÃO
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "Previsão":

    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    # Calcula os 3 meses seguintes ao último mês do dataset
    ultimo_mes  = pd.Period(df["AnoMes"].max(), freq="M")
    prox_meses  = [(ultimo_mes + i) for i in range(1, 4)]
    prox_labels = [str(p) for p in prox_meses]
    prox_label_fmt = f"{prox_meses[0].strftime('%b/%Y')} – {prox_meses[2].strftime('%b/%Y')}"

    st.markdown("## Previsão de Faturamento")
    st.caption(f"Regressão Linear com variáveis de sazonalidade · {prox_label_fmt}")
    st.markdown("---")

    fat_s = (df.groupby("AnoMes")["Valor_Total"].sum().reset_index().sort_values("AnoMes"))
    fat_s["T"]       = range(1, len(fat_s) + 1)
    fat_s["Mes_Num"] = fat_s["AnoMes"].str[-2:].astype(int)
    fat_s["Mes_Fev"] = (fat_s["Mes_Num"] == 2).astype(int)
    fat_s["Mes_Jun"] = (fat_s["Mes_Num"] == 6).astype(int)
    fat_s["Mes_Nov"] = (fat_s["Mes_Num"] == 11).astype(int)
    fat_s["Mes_Dez"] = (fat_s["Mes_Num"] == 12).astype(int)

    feats = ["T", "Mes_Fev", "Mes_Jun", "Mes_Nov", "Mes_Dez"]
    X, y  = fat_s[feats].values, fat_s["Valor_Total"].values
    m     = LinearRegression().fit(X, y)
    yp    = m.predict(X)

    r2   = r2_score(y, yp)
    mae  = mean_absolute_error(y, yp)
    rmse = np.sqrt(mean_squared_error(y, yp))
    mape = np.mean(np.abs((y - yp) / y)) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R²",    f"{r2:.3f}",        help="Quanto mais próximo de 1, melhor")
    c2.metric("MAE",   f"R$ {mae:,.0f}",   help="Erro médio absoluto")
    c3.metric("RMSE",  f"R$ {rmse:,.0f}",  help="Penaliza erros grandes")
    c4.metric("MAPE",  f"{mape:.1f}%",     help="Erro percentual médio")

    st.markdown("<br>", unsafe_allow_html=True)

    n_hist = len(fat_s)
    prox = pd.DataFrame({
        "AnoMes":  prox_labels,
        "T":       [n_hist + 1, n_hist + 2, n_hist + 3],
        "Mes_Fev": [1 if p.month == 2 else 0 for p in prox_meses],
        "Mes_Jun": [1 if p.month == 6 else 0 for p in prox_meses],
        "Mes_Nov": [1 if p.month == 11 else 0 for p in prox_meses],
        "Mes_Dez": [1 if p.month == 12 else 0 for p in prox_meses],
    })
    yf = m.predict(prox[feats].values)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fat_s["AnoMes"], y=fat_s["Valor_Total"],
        mode="lines+markers", name="Histórico",
        line=dict(color="#AAAAAA", width=1.5),
        marker=dict(size=3, color="#AAAAAA"),
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=fat_s["AnoMes"], y=yp,
        mode="lines", name="Modelo",
        line=dict(color=COR_PRIMARIA, width=1.5, dash="dot"),
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    x_prev = [fat_s["AnoMes"].iloc[-1]] + list(prox["AnoMes"])
    y_prev = [yp[-1]] + list(yf)
    fig.add_trace(go.Scatter(
        x=x_prev, y=y_prev,
        mode="lines+markers", name="Previsão 2025",
        line=dict(color=COR_HOVER, width=2.5),
        marker=dict(size=7, symbol="circle", color=COR_HOVER),
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=list(prox["AnoMes"]) + list(prox["AnoMes"])[::-1],
        y=list(yf + rmse) + list(yf - rmse)[::-1],
        fill="toself", fillcolor="rgba(192,57,43,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name=f"Intervalo ±R$ {rmse:,.0f}",
        hoverinfo="skip",
    ))
    fig.update_layout(**layout_base(), title="Faturamento Histórico + Previsão",
                      height=380, xaxis_tickangle=-40)
    st.plotly_chart(fig, width="stretch")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Previsão detalhada")
    df_pv = pd.DataFrame({
        "Mês":              prox["AnoMes"],
        "Previsão":         [f"R$ {v:,.2f}" for v in yf],
        "Mínimo (−RMSE)":   [f"R$ {v:,.2f}" for v in yf - rmse],
        "Máximo (+RMSE)":   [f"R$ {v:,.2f}" for v in yf + rmse],
    })
    st.dataframe(df_pv, hide_index=True, width="stretch")
    st.caption(f"R² = {r2:.3f} · O modelo explica {r2*100:.1f}% da variação · MAPE {mape:.1f}%")
