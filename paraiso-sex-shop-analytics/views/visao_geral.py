# =============================================================================
# pages/visao_geral.py — Página: Visão Geral
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
from utils.config import COR_PRIMARIA, PALETA, layout_base


def show(df, df_f):
    """
    Exibe a página de Visão Geral.

    Parâmetros:
      df   → DataFrame completo (usado para datas mín/máx)
      df_f → DataFrame filtrado (usado nos KPIs e gráficos)
    """

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
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

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento",     f"R$ {df_f['Valor_Total'].sum():,.0f}")
    c2.metric("Ticket Médio",    f"R$ {df_f['Valor_Total'].mean():,.2f}")
    c3.metric("Pedidos",         f"{len(df_f):,}")
    c4.metric("Clientes Únicos", f"{df_f['ID_Cliente'].nunique():,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Receita por Categoria + Método de Pagamento ───────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        cat = (df_f.groupby("Categoria_Produto")["Valor_Total"]
               .sum().reset_index().sort_values("Valor_Total"))
        fig = go.Figure(go.Bar(
            x=cat["Valor_Total"], y=cat["Categoria_Produto"],
            orientation="h",
            marker=dict(color=COR_PRIMARIA, opacity=0.85),
            hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(**layout_base(), title="Receita por Categoria", height=300)
        st.plotly_chart(fig, width="stretch")

    with col_b:
        pag = df_f.groupby("Metodo_Pagamento")["Valor_Total"].sum().reset_index()
        fig2 = go.Figure(go.Pie(
            labels=pag["Metodo_Pagamento"], values=pag["Valor_Total"],
            hole=0.6,
            marker=dict(colors=PALETA),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
        ))
        lo = layout_base()
        lo["legend"].update(orientation="v", x=1, y=0.5)
        fig2.update_layout(**lo, title="Método de Pagamento", height=300, showlegend=True)
        st.plotly_chart(fig2, width="stretch")

    # ── Receita por Região ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    reg = (df_f.groupby("Regiao")["Valor_Total"]
           .sum().reset_index().sort_values("Valor_Total", ascending=True))
    fig3 = go.Figure(go.Bar(
        x=reg["Valor_Total"], y=reg["Regiao"],
        orientation="h",
        marker=dict(color=COR_PRIMARIA, opacity=0.85),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    fig3.update_layout(**layout_base(), title="Receita por Região", height=280)
    fig3.update_xaxes(showticklabels=False)
    st.plotly_chart(fig3, width="stretch")
