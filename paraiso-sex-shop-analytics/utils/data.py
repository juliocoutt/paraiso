# =============================================================================
# utils/data.py — Carregamento e cache dos dados
# =============================================================================

import streamlit as st
import pandas as pd


@st.cache_data   # guarda os dados em memória para não recarregar a cada interação
def carregar():
    """
    Lê os dois CSVs principais e retorna como DataFrames.
    Retorna: (df, rfm)
      - df  → dados de vendas completos
      - rfm → tabela de segmentação RFM dos clientes
    """
    df = pd.read_csv(
        "data/ecom_data_clean.csv",
        encoding="utf-8-sig",
        parse_dates=["Data_Venda"],   # converte a coluna de data automaticamente
    )
    rfm = pd.read_csv("data/rfm_clientes.csv", encoding="utf-8-sig")
    return df, rfm
