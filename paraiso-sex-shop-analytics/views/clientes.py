# =============================================================================
# pages/clientes.py — Página: Clientes
# =============================================================================

import streamlit as st
import plotly.graph_objects as go
from utils.config import COR_PRIMARIA, PALETA, layout_base


def show(df_f, rfm):
    """
    Exibe a página de análise de clientes.

    Parâmetros:
      df_f → DataFrame filtrado de vendas
      rfm  → DataFrame com segmentação RFM dos clientes
    """

    st.markdown("## Clientes")
    st.caption("Perfil, segmentação RFM e análise regional")
    st.markdown("---")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes Únicos",   f"{df_f['ID_Cliente'].nunique():,}")
    c2.metric("Pedidos / Cliente", f"{len(df_f) / max(df_f['ID_Cliente'].nunique(), 1):.1f}")
    c3.metric("LTV Médio",         f"R$ {df_f.groupby('ID_Cliente')['Valor_Total'].sum().mean():,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Faixa Etária + Gênero ─────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        fe = (df_f.groupby("Faixa_Etaria")["Valor_Total"]
              .sum().reset_index().sort_values("Valor_Total", ascending=True))
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
            hole=0.6,
            marker=dict(colors=PALETA),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
        ))
        fig2.update_layout(**layout_base(), title="Receita por Gênero", height=280)
        st.plotly_chart(fig2, width="stretch")

    # ── Receita por Região ────────────────────────────────────────────────────
    reg = (df_f.groupby("Regiao")["Valor_Total"]
           .sum().reset_index().sort_values("Valor_Total", ascending=True))
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

    # ── Segmentação RFM ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Segmentação RFM")
    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        sc = rfm["Segmento"].value_counts().reset_index()
        sc.columns = ["Segmento", "Clientes"]
        fig4 = go.Figure(go.Bar(
            x=sc["Segmento"], y=sc["Clientes"],
            marker=dict(color=PALETA[: len(sc)]),
            hovertemplate="<b>%{x}</b><br>%{y} clientes<extra></extra>",
        ))
        fig4.update_layout(**layout_base(), title="Clientes por Segmento", height=280, showlegend=False)
        st.plotly_chart(fig4, width="stretch")

    with col_r2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Descrição de cada segmento RFM com ação sugerida
        info = {
            "Champion":  ("🔴", "Recente, frequente, alto valor — fidelizar com VIP"),
            "Loyal":     ("🟠", "Fiel — estimular cross-sell entre categorias"),
            "Promising": ("🟡", "Recente, pouca frequência — nutrir com ofertas"),
            "At Risk":   ("⚪", "Sumiu — campanha de reativação urgente"),
            "Lost":      ("⬛", "Inativo — oferta agressiva ou aceitar churn"),
        }
        for seg, (ico, desc) in info.items():
            n = len(rfm[rfm["Segmento"] == seg])
            st.markdown(
                f"{ico} &nbsp; **{seg}** &nbsp; <span style='color:#666'>({n})</span> &nbsp; {desc}",
                unsafe_allow_html=True,
            )
