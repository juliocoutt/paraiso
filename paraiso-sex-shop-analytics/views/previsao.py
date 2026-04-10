# =============================================================================
# pages/previsao.py — Página: Previsão de Faturamento
# =============================================================================

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from utils.config import COR_PRIMARIA, COR_HOVER, layout_base


def show(df):
    """
    Exibe a página de previsão com Regressão Linear.

    Parâmetro:
      df → DataFrame COMPLETO de vendas (sem filtros — a previsão usa o histórico inteiro)
    """

    # ── Descobre os próximos 3 meses após o último mês do dataset ─────────────
    ultimo_mes      = pd.Period(df["AnoMes"].max(), freq="M")
    prox_meses      = [(ultimo_mes + i) for i in range(1, 4)]
    prox_labels     = [str(p) for p in prox_meses]
    prox_label_fmt  = f"{prox_meses[0].strftime('%b/%Y')} – {prox_meses[2].strftime('%b/%Y')}"

    st.markdown("## Previsão de Faturamento")
    st.caption(f"Regressão Linear com variáveis de sazonalidade · {prox_label_fmt}")
    st.markdown("---")

    # ── Prepara dados para o modelo ───────────────────────────────────────────
    # Agrega faturamento por mês e cria variáveis explicativas
    fat_s = (
        df.groupby("AnoMes")["Valor_Total"]
        .sum()
        .reset_index()
        .sort_values("AnoMes")
    )
    fat_s["T"]       = range(1, len(fat_s) + 1)          # tendência linear (1, 2, 3, ...)
    fat_s["Mes_Num"] = fat_s["AnoMes"].str[-2:].astype(int)
    fat_s["Mes_Fev"] = (fat_s["Mes_Num"] == 2).astype(int)   # sazonalidade: Fevereiro
    fat_s["Mes_Jun"] = (fat_s["Mes_Num"] == 6).astype(int)   # sazonalidade: Junho
    fat_s["Mes_Nov"] = (fat_s["Mes_Num"] == 11).astype(int)  # sazonalidade: Novembro
    fat_s["Mes_Dez"] = (fat_s["Mes_Num"] == 12).astype(int)  # sazonalidade: Dezembro

    feats = ["T", "Mes_Fev", "Mes_Jun", "Mes_Nov", "Mes_Dez"]
    X, y  = fat_s[feats].values, fat_s["Valor_Total"].values

    # Treina o modelo
    modelo = LinearRegression().fit(X, y)
    yp     = modelo.predict(X)

    # ── Métricas de qualidade do modelo ──────────────────────────────────────
    r2   = r2_score(y, yp)
    mae  = mean_absolute_error(y, yp)
    rmse = np.sqrt(mean_squared_error(y, yp))
    mape = np.mean(np.abs((y - yp) / y)) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R²",   f"{r2:.3f}",       help="Quanto mais próximo de 1, melhor")
    c2.metric("MAE",  f"R$ {mae:,.0f}",  help="Erro médio absoluto")
    c3.metric("RMSE", f"R$ {rmse:,.0f}", help="Penaliza erros grandes")
    c4.metric("MAPE", f"{mape:.1f}%",    help="Erro percentual médio")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Previsão para os próximos 3 meses ─────────────────────────────────────
    n_hist = len(fat_s)
    prox = pd.DataFrame({
        "AnoMes":  prox_labels,
        "T":       [n_hist + 1, n_hist + 2, n_hist + 3],
        "Mes_Fev": [1 if p.month == 2  else 0 for p in prox_meses],
        "Mes_Jun": [1 if p.month == 6  else 0 for p in prox_meses],
        "Mes_Nov": [1 if p.month == 11 else 0 for p in prox_meses],
        "Mes_Dez": [1 if p.month == 12 else 0 for p in prox_meses],
    })
    yf = modelo.predict(prox[feats].values)

    # ── Gráfico: histórico + modelo + previsão ────────────────────────────────
    fig = go.Figure()

    # Linha cinza = dados reais históricos
    fig.add_trace(go.Scatter(
        x=fat_s["AnoMes"], y=fat_s["Valor_Total"],
        mode="lines+markers", name="Histórico",
        line=dict(color="#AAAAAA", width=1.5),
        marker=dict(size=3, color="#AAAAAA"),
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))

    # Linha pontilhada vermelha = o que o modelo "aprendeu" nos dados históricos
    fig.add_trace(go.Scatter(
        x=fat_s["AnoMes"], y=yp,
        mode="lines", name="Modelo",
        line=dict(color=COR_PRIMARIA, width=1.5, dash="dot"),
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))

    # Linha vermelha sólida = previsão futura
    x_prev = [fat_s["AnoMes"].iloc[-1]] + list(prox["AnoMes"])
    y_prev = [yp[-1]] + list(yf)
    fig.add_trace(go.Scatter(
        x=x_prev, y=y_prev,
        mode="lines+markers", name="Previsão",
        line=dict(color=COR_HOVER, width=2.5),
        marker=dict(size=7, symbol="circle", color=COR_HOVER),
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))

    # Faixa de intervalo de confiança (± 1 RMSE)
    fig.add_trace(go.Scatter(
        x=list(prox["AnoMes"]) + list(prox["AnoMes"])[::-1],
        y=list(yf + rmse) + list(yf - rmse)[::-1],
        fill="toself",
        fillcolor="rgba(192,57,43,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name=f"Intervalo ±R$ {rmse:,.0f}",
        hoverinfo="skip",
    ))

    fig.update_layout(
        **layout_base(),
        title="Faturamento Histórico + Previsão",
        height=380,
        xaxis_tickangle=-40,
    )
    st.plotly_chart(fig, width="stretch")

    # ── Tabela com os valores previstos ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Previsão detalhada")
    df_pv = pd.DataFrame({
        "Mês":            prox["AnoMes"],
        "Previsão":       [f"R$ {v:,.2f}" for v in yf],
        "Mínimo (−RMSE)": [f"R$ {v:,.2f}" for v in yf - rmse],
        "Máximo (+RMSE)": [f"R$ {v:,.2f}" for v in yf + rmse],
    })
    st.dataframe(df_pv, hide_index=True, width="stretch")
    st.caption(f"R² = {r2:.3f} · O modelo explica {r2*100:.1f}% da variação · MAPE {mape:.1f}%")
