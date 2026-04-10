# =============================================================================
# pages/produtos.py — Página: Produtos
# =============================================================================

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.config import COR_PRIMARIA, COR_HOVER, PALETA, layout_base


def show(df_f):
    """
    Exibe a página de performance de produtos.

    Parâmetro:
      df_f → DataFrame filtrado de vendas
    """

    st.markdown("## Produtos")
    st.caption("Performance por produto e categoria")
    st.markdown("---")

    # ── Top 10 Produtos ───────────────────────────────────────────────────────
    top10 = (
        df_f.groupby("Nome_Produto")["Valor_Total"]
        .sum()
        .sort_values(ascending=True)
        .tail(10)
        .reset_index()
    )
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

    # ── Treemap: Categoria → Produto ──────────────────────────────────────────
    with col_a:
        fat_cat = (
            df_f.groupby(["Categoria_Produto", "Nome_Produto"])["Valor_Total"]
            .sum()
            .reset_index()
        )
        fig2 = px.treemap(
            fat_cat,
            path=["Categoria_Produto", "Nome_Produto"],
            values="Valor_Total",
            color="Valor_Total",
            color_continuous_scale=["#FFEEEE", COR_PRIMARIA, COR_HOVER],
        )
        fig2.update_layout(
            **layout_base(),
            title="Receita: Categoria → Produto",
            height=380,
            coloraxis_showscale=False,
        )
        fig2.update_traces(hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>")
        st.plotly_chart(fig2, width="stretch")

    # ── Dispersão: Desconto × Valor Total ─────────────────────────────────────
    with col_b:
        # Amostra para não travar o navegador com muitos pontos
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
