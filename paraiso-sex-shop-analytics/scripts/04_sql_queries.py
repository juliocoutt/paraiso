# =============================================================================
# PARAISO SEX SHOP — CONSULTAS SQL COMPLEXAS
# Sprint 2 | Script 4 de 5
# =============================================================================
# O que esse script faz:
#   Executa 6 consultas SQL de diferentes níveis de complexidade
#   diretamente no banco SQLite, exibindo os resultados formatados
#   no terminal. Demonstra uso de:
#   - GROUP BY, ORDER BY, HAVING
#   - Window Functions (SUM OVER, AVG OVER, RANK OVER)
#   - CTEs (Common Table Expressions — WITH ...)
#   - Cálculo de taxa de retenção e churn
#
# Como rodar:
#   Após rodar os scripts 01, 02 e 03: python scripts/04_sql_queries.py
# =============================================================================

import sqlite3      # biblioteca nativa do Python para SQLite
import pandas as pd # para exibir os resultados como tabela
import os

print("=" * 70)
print("  PARAISO SEX SHOP — Queries SQL Complexas")
print("=" * 70)

# ── Conecta ao banco ──────────────────────────────────────────────────────────

caminho_db = "database/paraiso_db.sqlite"
if not os.path.exists(caminho_db):
    print(f"\n  ERRO: Banco '{caminho_db}' não encontrado!")
    print("  Rode primeiro: python scripts/02_etl.py")
    exit(1)

conn = sqlite3.connect(caminho_db)

def rodar_query(titulo, descricao, sql):
    """
    Função auxiliar: recebe o título, a descrição e o SQL da query,
    executa no banco e exibe o resultado formatado.
    """
    print(f"\n{'─' * 70}")
    print(f"  QUERY: {titulo}")
    print(f"  {descricao}")
    print(f"{'─' * 70}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    print()
    return df

# ══════════════════════════════════════════════════════════════════════════════
# QUERY 1 — Faturamento Total e Ticket Médio por Mês
# Conceitos: GROUP BY, ORDER BY, funções de agregação (SUM, AVG, COUNT)
# ══════════════════════════════════════════════════════════════════════════════

df_q1 = rodar_query(
    titulo="Faturamento Mensal com Ticket Médio",
    descricao="GROUP BY mês | Agregações: SUM, AVG, COUNT",
    sql="""
    SELECT
        AnoMes                                AS Mes,
        COUNT(ID_Transacao)                   AS Qtd_Pedidos,
        ROUND(SUM(Valor_Total), 2)            AS Faturamento_Total,
        ROUND(AVG(Valor_Total), 2)            AS Ticket_Medio,
        ROUND(MAX(Valor_Total), 2)            AS Maior_Venda,
        ROUND(MIN(Valor_Total), 2)            AS Menor_Venda
    FROM vendas
    GROUP BY AnoMes
    ORDER BY AnoMes ASC
    """
)

# ══════════════════════════════════════════════════════════════════════════════
# QUERY 2 — Top 5 Clientes por Valor Total Gasto
# Conceitos: GROUP BY, ORDER BY DESC, LIMIT
# ══════════════════════════════════════════════════════════════════════════════

df_q2 = rodar_query(
    titulo="Top 5 Clientes por Receita Gerada",
    descricao="GROUP BY cliente | ORDER BY receita DESC | LIMIT 5",
    sql="""
    SELECT
        ID_Cliente,
        Nome_Cliente,
        Genero_Cliente,
        Regiao,
        COUNT(ID_Transacao)          AS Total_Pedidos,
        ROUND(SUM(Valor_Total), 2)   AS Receita_Total,
        ROUND(AVG(Valor_Total), 2)   AS Ticket_Medio
    FROM vendas
    GROUP BY ID_Cliente, Nome_Cliente, Genero_Cliente, Regiao
    ORDER BY Receita_Total DESC
    LIMIT 5
    """
)

# ══════════════════════════════════════════════════════════════════════════════
# QUERY 3 — Ranking de Categorias com Participação % na Receita
# Conceitos: Window Function — SUM() OVER (), RANK() OVER (ORDER BY)
# ══════════════════════════════════════════════════════════════════════════════

df_q3 = rodar_query(
    titulo="Ranking de Categorias — Receita e Participação %",
    descricao="Window Function: SUM() OVER () para calcular % do total | RANK() OVER ()",
    sql="""
    WITH receita_cat AS (
        SELECT
            Categoria_Produto,
            ROUND(SUM(Valor_Total), 2)   AS Receita_Total,
            COUNT(ID_Transacao)          AS Qtd_Pedidos
        FROM vendas
        GROUP BY Categoria_Produto
    )
    SELECT
        RANK() OVER (ORDER BY Receita_Total DESC)            AS Ranking,
        Categoria_Produto,
        Receita_Total,
        Qtd_Pedidos,
        ROUND(
            100.0 * Receita_Total / SUM(Receita_Total) OVER (),
            2
        )                                                    AS Participacao_Pct
    FROM receita_cat
    ORDER BY Ranking
    """
)

# ══════════════════════════════════════════════════════════════════════════════
# QUERY 4 — Taxa de Retenção Mensal
# Clientes que compraram no mês N E também no mês N+1
# Conceitos: CTE com self-join, comparação de períodos
# ══════════════════════════════════════════════════════════════════════════════

df_q4 = rodar_query(
    titulo="Taxa de Retenção Mensal de Clientes",
    descricao="CTE + Self-JOIN: clientes ativos em mês N que voltaram em N+1",
    sql="""
    WITH clientes_por_mes AS (
        -- Obtém lista de clientes únicos por mês
        SELECT DISTINCT
            AnoMes,
            ID_Cliente
        FROM vendas
    ),
    retencao AS (
        -- Para cada mês, conta quantos clientes voltaram no mês seguinte
        SELECT
            a.AnoMes                         AS Mes_Referencia,
            COUNT(DISTINCT a.ID_Cliente)     AS Clientes_Mes_Atual,
            COUNT(DISTINCT b.ID_Cliente)     AS Clientes_Retidos,
            ROUND(
                100.0 * COUNT(DISTINCT b.ID_Cliente)
                      / NULLIF(COUNT(DISTINCT a.ID_Cliente), 0),
                1
            )                                AS Taxa_Retencao_Pct
        FROM clientes_por_mes a
        LEFT JOIN clientes_por_mes b
            ON  a.ID_Cliente = b.ID_Cliente
            AND b.AnoMes = (
                -- Mês seguinte: adiciona 1 mês usando manipulação de string
                SUBSTR(a.AnoMes, 1, 4) || '-' ||
                CASE
                    WHEN CAST(SUBSTR(a.AnoMes, 6, 2) AS INT) = 12 THEN '01'
                    ELSE PRINTF('%02d', CAST(SUBSTR(a.AnoMes, 6, 2) AS INT) + 1)
                END
            )
        GROUP BY a.AnoMes
    )
    SELECT *
    FROM retencao
    ORDER BY Mes_Referencia
    """
)

# ══════════════════════════════════════════════════════════════════════════════
# QUERY 5 — Clientes em Churn (sem compra nos últimos 90 dias do dataset)
# Conceitos: subquery com MAX, HAVING, DATEDIFF via julianday
# ══════════════════════════════════════════════════════════════════════════════

df_q5 = rodar_query(
    titulo="Clientes em Risco de Churn (inativos há 90+ dias)",
    descricao="Subquery: última compra por cliente | filtra quem ficou 90 dias sem comprar",
    sql="""
    WITH ultima_compra AS (
        SELECT
            ID_Cliente,
            Nome_Cliente,
            MAX(Data_Venda)                          AS Ultima_Compra,
            COUNT(ID_Transacao)                      AS Total_Pedidos,
            ROUND(SUM(Valor_Total), 2)               AS Valor_Total_Gasto
        FROM vendas
        GROUP BY ID_Cliente, Nome_Cliente
    ),
    data_max AS (
        SELECT MAX(Data_Venda) AS Data_Ref FROM vendas
    )
    SELECT
        u.ID_Cliente,
        u.Nome_Cliente,
        u.Ultima_Compra,
        u.Total_Pedidos,
        u.Valor_Total_Gasto,
        CAST(julianday(d.Data_Ref) - julianday(u.Ultima_Compra) AS INT)
                                                     AS Dias_Sem_Comprar
    FROM ultima_compra u, data_max d
    WHERE CAST(julianday(d.Data_Ref) - julianday(u.Ultima_Compra) AS INT) >= 90
    ORDER BY Dias_Sem_Comprar DESC
    LIMIT 15
    """
)

# ══════════════════════════════════════════════════════════════════════════════
# QUERY 6 — Média Móvel de 3 Meses do Faturamento
# Conceitos: Window Function — AVG() OVER (ORDER BY ROWS BETWEEN)
# ══════════════════════════════════════════════════════════════════════════════

df_q6 = rodar_query(
    titulo="Média Móvel de 3 Meses do Faturamento",
    descricao="Window Function: AVG() OVER (ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)",
    sql="""
    WITH fat_mensal AS (
        SELECT
            AnoMes,
            ROUND(SUM(Valor_Total), 2) AS Faturamento
        FROM vendas
        GROUP BY AnoMes
        ORDER BY AnoMes
    )
    SELECT
        AnoMes,
        Faturamento,
        ROUND(
            AVG(Faturamento) OVER (
                ORDER BY AnoMes
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ),
            2
        )                              AS Media_Movel_3M,
        ROUND(
            SUM(Faturamento) OVER (
                ORDER BY AnoMes
                ROWS UNBOUNDED PRECEDING
            ),
            2
        )                              AS Faturamento_Acumulado
    FROM fat_mensal
    """
)

# ── Fecha a conexão ───────────────────────────────────────────────────────────

conn.close()

# ── Salva os resultados das queries em CSV ───────────────────────────────────

os.makedirs("data", exist_ok=True)
df_q1.to_csv("data/query1_faturamento_mensal.csv",    index=False, encoding="utf-8-sig")
df_q3.to_csv("data/query3_ranking_categorias.csv",    index=False, encoding="utf-8-sig")
df_q4.to_csv("data/query4_retencao_mensal.csv",       index=False, encoding="utf-8-sig")
df_q6.to_csv("data/query6_media_movel.csv",           index=False, encoding="utf-8-sig")

print(f"{'=' * 70}")
print(f"  QUERIES SQL CONCLUÍDAS!")
print(f"{'=' * 70}")
print(f"  Resultados das queries principais salvos em data/")
print(f"\n  Próximo passo: rodar python scripts/05_modelo_preditivo.py")
print(f"{'=' * 70}\n")
