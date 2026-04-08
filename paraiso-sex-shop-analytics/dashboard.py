# =============================================================================
# PARAISO SEX SHOP — DASHBOARD INTERATIVO (STREAMLIT)
# =============================================================================
# Como rodar:
#   venv\Scripts\streamlit run dashboard.py
# Abrirá automaticamente no navegador em http://localhost:8501
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Configuração da página ────────────────────────────────────────────────────

st.set_page_config(
    page_title="Paraiso Sex Shop — Analytics",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo customizado
st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #9B59B6;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stMetric { background-color: #16213e; border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

CORES = ["#9B59B6", "#E91E8C", "#F39C12", "#1ABC9C", "#3498DB", "#E74C3C"]

# ── Carrega dados ─────────────────────────────────────────────────────────────

@st.cache_data
def carregar_dados():
    df = pd.read_csv("data/ecom_data_clean.csv", encoding="utf-8-sig", parse_dates=["Data_Venda"])
    rfm = pd.read_csv("data/rfm_clientes.csv", encoding="utf-8-sig")
    return df, rfm

df, rfm = carregar_dados()

# ── Sidebar — Filtros ─────────────────────────────────────────────────────────

st.sidebar.image("https://img.icons8.com/color/96/000000/heart-with-pulse.png", width=60)
st.sidebar.title("Paraiso Sex Shop")
st.sidebar.markdown("**Dashboard Analítico**")
st.sidebar.markdown("---")

anos = sorted(df["Ano"].unique())
regioes = sorted(df["Regiao"].unique())
categorias = sorted(df["Categoria_Produto"].unique())

ano_sel = st.sidebar.multiselect("Ano", anos, default=anos)
regiao_sel = st.sidebar.multiselect("Região", regioes, default=regioes)
cat_sel = st.sidebar.multiselect("Categoria", categorias, default=categorias)

# Aplica filtros
mask = (
    df["Ano"].isin(ano_sel) &
    df["Regiao"].isin(regiao_sel) &
    df["Categoria_Produto"].isin(cat_sel)
)
df_f = df[mask]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Registros filtrados:** {len(df_f):,}")

# ── Navegação entre páginas ───────────────────────────────────────────────────

pagina = st.sidebar.radio(
    "Navegar para",
    ["📊 Visão Geral", "👥 Clientes", "🛍️ Produtos", "🔮 Previsão"]
)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — VISÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════

if pagina == "📊 Visão Geral":

    st.title("📊 Visão Geral — Paraiso Sex Shop")
    st.markdown("Período: **Jan/2023 – Dez/2024** | Fonte: Dataset simulado InsightFlow")
    st.markdown("---")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    faturamento = df_f["Valor_Total"].sum()
    ticket_medio = df_f["Valor_Total"].mean()
    total_pedidos = len(df_f)
    clientes_unicos = df_f["ID_Cliente"].nunique()

    col1.metric("💰 Faturamento Total", f"R$ {faturamento:,.0f}")
    col2.metric("🎯 Ticket Médio",       f"R$ {ticket_medio:,.2f}")
    col3.metric("📦 Total de Pedidos",   f"{total_pedidos:,}")
    col4.metric("👤 Clientes Únicos",    f"{clientes_unicos:,}")

    st.markdown("---")

    # Gráfico de linha — Faturamento mensal
    fat_mensal = (
        df_f.groupby("AnoMes")["Valor_Total"]
        .sum()
        .reset_index()
        .sort_values("AnoMes")
    )

    fig_linha = px.line(
        fat_mensal,
        x="AnoMes",
        y="Valor_Total",
        title="Faturamento Mensal",
        markers=True,
        color_discrete_sequence=[CORES[1]],
        labels={"AnoMes": "Mês", "Valor_Total": "Receita (R$)"},
    )
    fig_linha.update_layout(
        template="plotly_dark",
        plot_bgcolor="#16213e",
        paper_bgcolor="#1a1a2e",
        height=380,
        xaxis_tickangle=-45,
    )
    fig_linha.update_traces(fill="tozeroy", fillcolor="rgba(233,30,140,0.1)")
    st.plotly_chart(fig_linha, use_container_width=True)

    # Linha 2 — Categoria + Método de pagamento
    col_a, col_b = st.columns(2)

    with col_a:
        fat_cat = df_f.groupby("Categoria_Produto")["Valor_Total"].sum().reset_index().sort_values("Valor_Total", ascending=False)
        fig_cat = px.bar(
            fat_cat,
            x="Categoria_Produto",
            y="Valor_Total",
            title="Receita por Categoria",
            color="Categoria_Produto",
            color_discrete_sequence=CORES,
            labels={"Valor_Total": "Receita (R$)", "Categoria_Produto": ""},
        )
        fig_cat.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", showlegend=False, height=340)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        pag = df_f.groupby("Metodo_Pagamento")["Valor_Total"].sum().reset_index()
        fig_pag = px.pie(
            pag,
            names="Metodo_Pagamento",
            values="Valor_Total",
            title="Receita por Método de Pagamento",
            color_discrete_sequence=CORES,
            hole=0.4,
        )
        fig_pag.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", height=340)
        st.plotly_chart(fig_pag, use_container_width=True)

    # Canal de venda
    col_c, col_d = st.columns(2)

    with col_c:
        canal = df_f.groupby("Canal_Venda")["Valor_Total"].sum().reset_index()
        fig_canal = px.bar(
            canal,
            x="Canal_Venda",
            y="Valor_Total",
            title="Receita por Canal de Venda",
            color="Canal_Venda",
            color_discrete_sequence=CORES,
            labels={"Valor_Total": "Receita (R$)", "Canal_Venda": ""},
        )
        fig_canal.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", showlegend=False, height=300)
        st.plotly_chart(fig_canal, use_container_width=True)

    with col_d:
        status = df_f.groupby("Status_Pedido")["Valor_Total"].sum().reset_index()
        fig_status = px.pie(
            status,
            names="Status_Pedido",
            values="Valor_Total",
            title="Status dos Pedidos",
            color_discrete_sequence=CORES,
            hole=0.4,
        )
        fig_status.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", height=300)
        st.plotly_chart(fig_status, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — CLIENTES
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "👥 Clientes":

    st.title("👥 Análise de Clientes")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("👤 Clientes Únicos",       f"{df_f['ID_Cliente'].nunique():,}")
    col2.metric("🔁 Pedidos por Cliente",    f"{len(df_f)/max(df_f['ID_Cliente'].nunique(),1):.1f}")
    col3.metric("💰 LTV Médio",              f"R$ {df_f.groupby('ID_Cliente')['Valor_Total'].sum().mean():,.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        fat_faixa = df_f.groupby("Faixa_Etaria")["Valor_Total"].sum().reset_index().sort_values("Valor_Total", ascending=False)
        fig_faixa = px.bar(
            fat_faixa,
            x="Faixa_Etaria",
            y="Valor_Total",
            title="Receita por Faixa Etária",
            color="Faixa_Etaria",
            color_discrete_sequence=CORES,
            labels={"Valor_Total": "Receita (R$)", "Faixa_Etaria": ""},
        )
        fig_faixa.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", showlegend=False, height=340)
        st.plotly_chart(fig_faixa, use_container_width=True)

    with col_b:
        fat_genero = df_f.groupby("Genero_Cliente")["Valor_Total"].sum().reset_index()
        fig_genero = px.pie(
            fat_genero,
            names="Genero_Cliente",
            values="Valor_Total",
            title="Receita por Gênero",
            color_discrete_sequence=CORES,
            hole=0.4,
        )
        fig_genero.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", height=340)
        st.plotly_chart(fig_genero, use_container_width=True)

    # Receita por região
    fat_regiao = df_f.groupby("Regiao")["Valor_Total"].sum().reset_index().sort_values("Valor_Total", ascending=True)
    fig_regiao = px.bar(
        fat_regiao,
        x="Valor_Total",
        y="Regiao",
        title="Receita por Região do Brasil",
        orientation="h",
        color="Valor_Total",
        color_continuous_scale=["#9B59B6", "#E91E8C"],
        labels={"Valor_Total": "Receita (R$)", "Regiao": ""},
    )
    fig_regiao.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", height=320, coloraxis_showscale=False)
    st.plotly_chart(fig_regiao, use_container_width=True)

    # Segmentação RFM
    st.subheader("🎯 Segmentação RFM dos Clientes")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        seg_count = rfm["Segmento"].value_counts().reset_index()
        seg_count.columns = ["Segmento", "Clientes"]
        fig_rfm = px.bar(
            seg_count,
            x="Segmento",
            y="Clientes",
            title="Clientes por Segmento RFM",
            color="Segmento",
            color_discrete_sequence=CORES,
        )
        fig_rfm.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", showlegend=False, height=340)
        st.plotly_chart(fig_rfm, use_container_width=True)

    with col_r2:
        st.markdown("**Descrição dos Segmentos**")
        descricoes = {
            "Champion":  "Comprou recente, frequente e gasta muito. Ofereça acesso VIP.",
            "Loyal":     "Cliente fiel. Estimule cross-sell entre categorias.",
            "Promising": "Recente mas ainda pouco frequente. Nutrir com conteúdo.",
            "At Risk":   "Já foi bom cliente mas sumiu. Campanha de reativação urgente.",
            "Lost":      "Inativo há muito tempo. Oferta agressiva ou aceitar churn.",
        }
        for seg, desc in descricoes.items():
            cor = {"Champion": "🟣", "Loyal": "🟡", "Promising": "🟢", "At Risk": "🟠", "Lost": "🔴"}.get(seg, "⚪")
            qtd = len(rfm[rfm["Segmento"] == seg])
            st.markdown(f"{cor} **{seg}** ({qtd} clientes): {desc}")

    # Top 10 clientes
    st.subheader("🏆 Top 10 Clientes por Receita")
    top10 = (
        df_f.groupby(["ID_Cliente", "Nome_Cliente", "Regiao"])
        .agg(Receita=("Valor_Total", "sum"), Pedidos=("ID_Transacao", "count"))
        .reset_index()
        .sort_values("Receita", ascending=False)
        .head(10)
    )
    top10["Receita"] = top10["Receita"].apply(lambda x: f"R$ {x:,.2f}")
    st.dataframe(top10, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — PRODUTOS
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "🛍️ Produtos":

    st.title("🛍️ Análise de Produtos")
    st.markdown("---")

    # Top 10 produtos
    top10_prod = (
        df_f.groupby("Nome_Produto")["Valor_Total"]
        .sum()
        .sort_values(ascending=True)
        .tail(10)
        .reset_index()
    )
    fig_top10 = px.bar(
        top10_prod,
        x="Valor_Total",
        y="Nome_Produto",
        orientation="h",
        title="Top 10 Produtos por Receita",
        color="Valor_Total",
        color_continuous_scale=["#9B59B6", "#E91E8C"],
        labels={"Valor_Total": "Receita (R$)", "Nome_Produto": ""},
    )
    fig_top10.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", height=420, coloraxis_showscale=False)
    st.plotly_chart(fig_top10, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Treemap por categoria
        fat_cat = df_f.groupby(["Categoria_Produto", "Nome_Produto"])["Valor_Total"].sum().reset_index()
        fig_tree = px.treemap(
            fat_cat,
            path=["Categoria_Produto", "Nome_Produto"],
            values="Valor_Total",
            title="Receita: Categoria → Produto",
            color="Valor_Total",
            color_continuous_scale=["#1a1a2e", "#9B59B6", "#E91E8C"],
        )
        fig_tree.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", height=420)
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_b:
        # Dispersão: Desconto × Valor Total
        amostra = df_f.sample(min(600, len(df_f)), random_state=42)
        fig_disp = px.scatter(
            amostra,
            x="Desconto_Pct",
            y="Valor_Total",
            color="Categoria_Produto",
            title="Desconto (%) × Valor Total",
            opacity=0.5,
            color_discrete_sequence=CORES,
            labels={"Desconto_Pct": "Desconto (%)", "Valor_Total": "Valor Total (R$)"},
        )
        fig_disp.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", height=420)
        st.plotly_chart(fig_disp, use_container_width=True)

    # Quantidade média por categoria
    qtd_cat = df_f.groupby("Categoria_Produto")["Quantidade"].mean().reset_index().sort_values("Quantidade", ascending=False)
    fig_qtd = px.bar(
        qtd_cat,
        x="Categoria_Produto",
        y="Quantidade",
        title="Quantidade Média por Pedido (por Categoria)",
        color="Categoria_Produto",
        color_discrete_sequence=CORES,
        labels={"Quantidade": "Qtd Média", "Categoria_Produto": ""},
    )
    fig_qtd.update_layout(template="plotly_dark", paper_bgcolor="#1a1a2e", plot_bgcolor="#16213e", showlegend=False, height=320)
    st.plotly_chart(fig_qtd, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — PREVISÃO
# ══════════════════════════════════════════════════════════════════════════════

elif pagina == "🔮 Previsão":

    st.title("🔮 Modelo Preditivo de Faturamento")
    st.markdown("**Algoritmo:** Regressão Linear com variáveis de sazonalidade")
    st.markdown("---")

    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    # Agrega faturamento mensal (sem filtros de região/categoria para a série completa)
    fat_serie = (
        df.groupby("AnoMes")["Valor_Total"]
        .sum()
        .reset_index()
        .sort_values("AnoMes")
    )
    fat_serie["T"] = range(1, len(fat_serie) + 1)
    fat_serie["Mes_Num"] = fat_serie["AnoMes"].str[-2:].astype(int)
    fat_serie["Mes_Fev"] = (fat_serie["Mes_Num"] == 2).astype(int)
    fat_serie["Mes_Jun"] = (fat_serie["Mes_Num"] == 6).astype(int)
    fat_serie["Mes_Nov"] = (fat_serie["Mes_Num"] == 11).astype(int)
    fat_serie["Mes_Dez"] = (fat_serie["Mes_Num"] == 12).astype(int)

    features = ["T", "Mes_Fev", "Mes_Jun", "Mes_Nov", "Mes_Dez"]
    X = fat_serie[features].values
    y = fat_serie["Valor_Total"].values

    modelo = LinearRegression().fit(X, y)
    y_pred = modelo.predict(X)

    r2   = r2_score(y, y_pred)
    mae  = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mape = np.mean(np.abs((y - y_pred) / y)) * 100

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("R² (Precisão)", f"{r2:.3f}", help="Quanto mais próximo de 1, melhor")
    col2.metric("MAE", f"R$ {mae:,.0f}", help="Erro médio absoluto")
    col3.metric("RMSE", f"R$ {rmse:,.0f}", help="Penaliza erros grandes")
    col4.metric("MAPE", f"{mape:.1f}%", help="Erro percentual médio")

    st.markdown("---")

    # Previsão Jan-Mar 2025
    proximos = pd.DataFrame({
        "AnoMes": ["2025-01", "2025-02", "2025-03"],
        "T": [25, 26, 27],
        "Mes_Fev": [0, 1, 0],
        "Mes_Jun": [0, 0, 0],
        "Mes_Nov": [0, 0, 0],
        "Mes_Dez": [0, 0, 0],
    })
    y_fut = modelo.predict(proximos[features].values)

    # Gráfico histórico + previsão
    fig_prev = go.Figure()

    fig_prev.add_trace(go.Scatter(
        x=fat_serie["AnoMes"], y=fat_serie["Valor_Total"],
        mode="lines+markers", name="Faturamento Real",
        line=dict(color=CORES[0], width=2),
        marker=dict(size=5),
    ))
    fig_prev.add_trace(go.Scatter(
        x=fat_serie["AnoMes"], y=y_pred,
        mode="lines", name="Modelo Ajustado",
        line=dict(color=CORES[2], width=1.5, dash="dash"),
    ))

    # Linha de previsão (conecta último ponto histórico com futuro)
    x_prev = [fat_serie["AnoMes"].iloc[-1]] + list(proximos["AnoMes"])
    y_prev = [y_pred[-1]] + list(y_fut)
    fig_prev.add_trace(go.Scatter(
        x=x_prev, y=y_prev,
        mode="lines+markers", name="Previsão 2025",
        line=dict(color=CORES[1], width=2.5),
        marker=dict(size=8, symbol="square"),
    ))

    # Faixa de incerteza
    fig_prev.add_trace(go.Scatter(
        x=list(proximos["AnoMes"]) + list(proximos["AnoMes"])[::-1],
        y=list(y_fut + rmse) + list(y_fut - rmse)[::-1],
        fill="toself", fillcolor="rgba(233,30,140,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name=f"Intervalo ±R${rmse:,.0f}",
    ))

    fig_prev.add_vline(x=fat_serie["AnoMes"].iloc[-1], line_dash="dot", line_color="gray",
                       annotation_text="  ← Histórico | Previsão →")

    fig_prev.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#16213e",
        title="Faturamento Histórico + Previsão Jan–Mar/2025",
        xaxis_title="Mês",
        yaxis_title="Receita (R$)",
        height=460,
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_prev, use_container_width=True)

    # Tabela de previsão
    st.subheader("📋 Previsão Detalhada")
    df_prev = pd.DataFrame({
        "Mês": proximos["AnoMes"],
        "Previsão": [f"R$ {v:,.2f}" for v in y_fut],
        "Mínimo (−RMSE)": [f"R$ {v:,.2f}" for v in y_fut - rmse],
        "Máximo (+RMSE)": [f"R$ {v:,.2f}" for v in y_fut + rmse],
    })
    st.dataframe(df_prev, use_container_width=True, hide_index=True)

    st.info(f"**Interpretação do R² = {r2:.3f}:** O modelo explica {r2*100:.1f}% da variação do faturamento. MAPE de {mape:.1f}% indica erro médio aceitável para planejamento comercial.")
