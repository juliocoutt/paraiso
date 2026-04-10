# =============================================================================
# dashboard.py — Ponto de entrada do dashboard
# Como rodar: venv\Scripts\streamlit run dashboard.py
#
# Estrutura de módulos:
#   utils/config.py        → cores, CSS e layout padrão dos gráficos
#   utils/data.py          → carregamento dos CSVs
#   components/sidebar.py  → sidebar com filtros e navegação
#   views/visao_geral.py   → página Visão Geral
#   views/clientes.py      → página Clientes
#   views/produtos.py      → página Produtos
#   views/previsao.py      → página Previsão
# =============================================================================

import streamlit as st

# Módulos do projeto
from utils.config import CSS
from utils.data import carregar
from components.sidebar import render_sidebar
import views.visao_geral as pg_visao_geral
import views.clientes    as pg_clientes
import views.produtos    as pg_produtos
import views.previsao    as pg_previsao

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Paraiso Sex Shop · Analytics",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injeta o CSS global
st.markdown(CSS, unsafe_allow_html=True)

# ── Carrega dados ─────────────────────────────────────────────────────────────
df, rfm = carregar()

# ── Sidebar: filtros + navegação (retorna dados filtrados e página selecionada)
df_f, pagina = render_sidebar(df)

# ── Roteamento: exibe a página correta ────────────────────────────────────────
if pagina == "Visão Geral":
    pg_visao_geral.show(df, df_f)

elif pagina == "Clientes":
    pg_clientes.show(df_f, rfm)

elif pagina == "Produtos":
    pg_produtos.show(df_f)

elif pagina == "Previsão":
    pg_previsao.show(df)
