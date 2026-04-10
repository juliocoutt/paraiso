# =============================================================================
# utils/config.py — Cores, CSS e layout padrão dos gráficos
# =============================================================================

# ── Paleta de cores ───────────────────────────────────────────────────────────
COR_PRIMARIA = "#C0392B"   # vermelho escuro principal
COR_HOVER    = "#E74C3C"   # vermelho mais claro (hover/destaque)
PAPEL        = "#FFFFFF"   # fundo do gráfico
PLOT_BG      = "#FAFAFA"   # área de plotagem
GRADE        = "#EEEEEE"   # linhas de grade
TEXTO        = "#111111"   # cor do texto

# Lista de cores para usar em gráficos com várias séries
PALETA = [COR_PRIMARIA, "#E74C3C", "#922B21", "#7B241C", "#F1948A", "#FADBD8"]


def layout_base():
    """
    Retorna um dicionário com configurações visuais padrão para todos os gráficos Plotly.
    Basta chamar fig.update_layout(**layout_base()) em qualquer figura.
    """
    return dict(
        template="plotly_white",
        paper_bgcolor=PAPEL,
        plot_bgcolor=PLOT_BG,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXTO, size=12),
        margin=dict(l=16, r=16, t=40, b=16),
        xaxis=dict(showgrid=True, gridcolor=GRADE, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRADE, zeroline=False),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
    )


# ── CSS injetado no Streamlit ─────────────────────────────────────────────────
CSS = """
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
"""
