# =============================================================================
# components/sidebar.py — Sidebar com logo, filtros e navegação
# =============================================================================

import base64
import pathlib
import streamlit as st


def render_sidebar(df):
    """
    Monta a sidebar completa: logo, filtros e menu de navegação.

    Parâmetro:
      df → DataFrame completo de vendas (sem filtros)

    Retorna:
      df_f   → DataFrame já filtrado pelas seleções do usuário
      pagina → nome da página selecionada no menu
    """
    with st.sidebar:

        # ── Logo ──────────────────────────────────────────────────────────────
        logo_path = pathlib.Path("dashboard/logo.png")
        if logo_path.exists():
            b64 = base64.b64encode(logo_path.read_bytes()).decode()
            st.markdown(
                f"<div style='text-align:center;padding:24px 0 8px'>"
                f"<img src='data:image/png;base64,{b64}' width='100'/></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='text-align:center'>"
            "<span style='font-size:1.1rem;font-weight:700;color:#C0392B'>Paraiso Sex Shop</span><br>"
            "<span style='font-size:0.72rem;color:#999;letter-spacing:0.1em;text-transform:uppercase'>Analytics</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)

        # ── Filtros ───────────────────────────────────────────────────────────
        st.markdown("<p class='section-title'>Filtros</p>", unsafe_allow_html=True)

        anos    = sorted(df["Ano"].unique(), reverse=True)
        regioes = sorted(df["Regiao"].unique())
        cats    = sorted(df["Categoria_Produto"].unique())

        # Mapeamento número do mês → nome em português
        meses_nomes = {
            1: "Janeiro",  2: "Fevereiro", 3: "Março",    4: "Abril",
            5: "Maio",     6: "Junho",     7: "Julho",    8: "Agosto",
            9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro",
        }
        meses_nums = sorted(df["Mes"].unique())
        meses_opts = [meses_nomes[m] for m in meses_nums]

        ano_sel    = st.multiselect("Ano",       anos,       default=None, placeholder="Todos os anos")
        mes_sel    = st.multiselect("Mês",       meses_opts, default=None, placeholder="Todos os meses")
        regiao_sel = st.multiselect("Região",    regioes,    default=None, placeholder="Todas as regiões")
        cat_sel    = st.multiselect("Categoria", cats,       default=None, placeholder="Todas as categorias")

        # Se o usuário não selecionou nada → usa tudo
        if not ano_sel:    ano_sel    = anos
        if not mes_sel:    mes_nums_sel = meses_nums
        else:              mes_nums_sel = [k for k, v in meses_nomes.items() if v in mes_sel]
        if not regiao_sel: regiao_sel = regioes
        if not cat_sel:    cat_sel    = cats

        st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)

        # ── Navegação ─────────────────────────────────────────────────────────
        st.markdown("<p class='section-title'>Navegação</p>", unsafe_allow_html=True)
        pagina = st.radio(
            "Navegação",
            ["Visão Geral", "Clientes", "Produtos", "Previsão"],
            label_visibility="collapsed",
        )

        # ── Aplica filtros e mostra contagem ──────────────────────────────────
        st.markdown("<hr style='margin:20px 0'>", unsafe_allow_html=True)
        mask = (
            df["Ano"].isin(ano_sel)
            & df["Mes"].isin(mes_nums_sel)
            & df["Regiao"].isin(regiao_sel)
            & df["Categoria_Produto"].isin(cat_sel)
        )
        df_f = df[mask]
        st.caption(f"{len(df_f):,} registros · {df_f['ID_Cliente'].nunique()} clientes")

    return df_f, pagina
