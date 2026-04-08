# =============================================================================
# PARAISO SEX SHOP — ANÁLISE EXPLORATÓRIA DE DADOS (EDA)
# Sprint 2 | Script 3 de 5
# =============================================================================
# O que esse script faz:
#   Realiza uma análise completa dos dados limpos, gerando:
#   - Estatísticas descritivas no terminal
#   - 8 gráficos salvos na pasta data/graficos/
#   - Segmentação RFM dos clientes (Champion, Loyal, At Risk, Lost)
#
# Como rodar:
#   Após rodar os scripts 01 e 02, execute: python scripts/03_eda.py
#   Os gráficos serão salvos em data/graficos/
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt    # para criar gráficos
import matplotlib.ticker as mticker
import seaborn as sns              # gráficos mais bonitos
import os

# ── Configurações visuais ────────────────────────────────────────────────────

# Paleta de cores roxo/lilás que combina com o branding "Paraiso Sex Shop"
CORES_MARCA = ["#9B59B6", "#E91E8C", "#F39C12", "#1ABC9C", "#3498DB", "#E74C3C"]

# Configura o estilo padrão de todos os gráficos
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",   # fundo escuro
    "axes.facecolor":   "#16213e",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "axes.titlecolor":  "white",
    "axes.edgecolor":   "#444444",
    "grid.color":       "#333333",
    "font.family":      "DejaVu Sans",
})

print("=" * 60)
print("  PARAISO SEX SHOP — Análise Exploratória (EDA)")
print("=" * 60)

# ── Carrega os dados limpos ───────────────────────────────────────────────────

caminho = "data/ecom_data_clean.csv"
if not os.path.exists(caminho):
    print(f"\n  ERRO: Arquivo '{caminho}' não encontrado!")
    print("  Rode primeiro: python scripts/02_etl.py")
    exit(1)

df = pd.read_csv(caminho, encoding="utf-8-sig", parse_dates=["Data_Venda"])
os.makedirs("data/graficos", exist_ok=True)

print(f"\n  ✔ Dataset carregado: {len(df):,} linhas\n")

# ── ANÁLISE 1: Estatísticas Descritivas ──────────────────────────────────────

print("─" * 60)
print("  [1] ESTATÍSTICAS DESCRITIVAS — Valor_Total")
print("─" * 60)

stats = df["Valor_Total"].describe()
print(f"  Média:         R$ {stats['mean']:>10,.2f}")
print(f"  Mediana:       R$ {df['Valor_Total'].median():>10,.2f}")
print(f"  Desvio Padrão: R$ {stats['std']:>10,.2f}")
print(f"  Mínimo:        R$ {stats['min']:>10,.2f}")
print(f"  Máximo:        R$ {stats['max']:>10,.2f}")
print(f"  Total Receita: R$ {df['Valor_Total'].sum():>10,.2f}")
print()

print("─" * 60)
print("  [1b] MÉTRICAS GERAIS DO NEGÓCIO")
print("─" * 60)
print(f"  Total de pedidos:         {len(df):,}")
print(f"  Clientes únicos:          {df['ID_Cliente'].nunique():,}")
print(f"  Ticket médio por pedido:  R$ {df['Valor_Total'].mean():,.2f}")
print(f"  Pedidos por cliente (avg): {len(df) / df['ID_Cliente'].nunique():.1f}")
print()

# ── ANÁLISE 2: Receita por Categoria ─────────────────────────────────────────

print("─" * 60)
print("  [2] RECEITA POR CATEGORIA")
print("─" * 60)

receita_cat = (
    df.groupby("Categoria_Produto")["Valor_Total"]
    .sum()
    .sort_values(ascending=False)
)
receita_total = receita_cat.sum()

for cat, val in receita_cat.items():
    pct = val / receita_total * 100
    print(f"  {cat:<25} R$ {val:>12,.2f}  ({pct:.1f}%)")
print()

# Gráfico de barras — Receita por Categoria
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(receita_cat.index, receita_cat.values / 1000, color=CORES_MARCA)
ax.set_title("Receita Total por Categoria de Produto", fontsize=14, pad=15)
ax.set_xlabel("Categoria")
ax.set_ylabel("Receita (R$ mil)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}k"))
plt.xticks(rotation=30, ha="right")
# Adiciona o valor em cima de cada barra
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 1,
            f"R$ {h:,.0f}k", ha="center", va="bottom", fontsize=9, color="white")
plt.tight_layout()
plt.savefig("data/graficos/01_receita_por_categoria.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/01_receita_por_categoria.png")

# ── ANÁLISE 3: Top 10 Produtos mais vendidos ──────────────────────────────────

print("\n─" * 61)
print("  [3] TOP 10 PRODUTOS MAIS VENDIDOS (por receita)")
print("─" * 60)

top10 = (
    df.groupby("Nome_Produto")["Valor_Total"]
    .sum()
    .sort_values(ascending=True)
    .tail(10)
)

for prod, val in top10.items():
    print(f"  {prod:<35} R$ {val:>10,.2f}")
print()

# Gráfico horizontal
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(top10.index, top10.values / 1000, color=CORES_MARCA[0])
ax.set_title("Top 10 Produtos — Receita Total (R$ mil)", fontsize=14, pad=15)
ax.set_xlabel("Receita (R$ mil)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}k"))
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.5, bar.get_y() + bar.get_height()/2,
            f"R$ {w:,.0f}k", va="center", fontsize=9, color="white")
plt.tight_layout()
plt.savefig("data/graficos/02_top10_produtos.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/02_top10_produtos.png")

# ── ANÁLISE 4: Faturamento Mensal (série temporal) ───────────────────────────

print("\n─" * 61)
print("  [4] FATURAMENTO MENSAL")
print("─" * 60)

fat_mensal = (
    df.groupby("AnoMes")["Valor_Total"]
    .sum()
    .reset_index()
    .sort_values("AnoMes")
)

print(f"  {'Mês':<10} {'Receita':>15}")
print(f"  {'-'*10} {'-'*15}")
for _, row in fat_mensal.iterrows():
    print(f"  {row['AnoMes']:<10} R$ {row['Valor_Total']:>12,.2f}")
print()

# Gráfico de linha
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(range(len(fat_mensal)), fat_mensal["Valor_Total"] / 1000,
        marker="o", color=CORES_MARCA[1], linewidth=2, markersize=5)
ax.fill_between(range(len(fat_mensal)), fat_mensal["Valor_Total"] / 1000,
                alpha=0.2, color=CORES_MARCA[1])
ax.set_title("Faturamento Mensal — Paraiso Sex Shop (2023–2024)", fontsize=14, pad=15)
ax.set_xlabel("Mês")
ax.set_ylabel("Receita (R$ mil)")
ax.set_xticks(range(len(fat_mensal)))
ax.set_xticklabels(fat_mensal["AnoMes"].tolist(), rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}k"))
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("data/graficos/03_faturamento_mensal.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/03_faturamento_mensal.png")

# ── ANÁLISE 5: Distribuição por Faixa Etária e Gênero ────────────────────────

print("\n─" * 61)
print("  [5] VENDAS POR FAIXA ETÁRIA E GÊNERO")
print("─" * 60)

vendas_faixa = df.groupby(["Faixa_Etaria", "Genero_Cliente"])["Valor_Total"].sum().unstack(fill_value=0)
print(vendas_faixa.to_string())
print()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1 — Receita por Faixa Etária
fat_faixa = df.groupby("Faixa_Etaria")["Valor_Total"].sum().sort_values(ascending=False)
axes[0].bar(fat_faixa.index, fat_faixa.values / 1000, color=CORES_MARCA[:len(fat_faixa)])
axes[0].set_title("Receita por Faixa Etária", fontsize=12)
axes[0].set_ylabel("Receita (R$ mil)")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}k"))

# Gráfico 2 — Receita por Gênero (pizza)
fat_genero = df.groupby("Genero_Cliente")["Valor_Total"].sum()
axes[1].pie(fat_genero.values, labels=fat_genero.index,
            autopct="%1.1f%%", colors=CORES_MARCA[:len(fat_genero)],
            startangle=90, textprops={"color": "white"})
axes[1].set_title("Receita por Gênero", fontsize=12)

plt.suptitle("Perfil dos Clientes — Paraiso Sex Shop", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig("data/graficos/04_perfil_clientes.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/04_perfil_clientes.png")

# ── ANÁLISE 6: Outliers em Valor_Total ───────────────────────────────────────

print("\n─" * 61)
print("  [6] OUTLIERS — Valor_Total")
print("─" * 60)

Q1 = df["Valor_Total"].quantile(0.25)
Q3 = df["Valor_Total"].quantile(0.75)
IQR = Q3 - Q1
limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR

outliers = df[(df["Valor_Total"] < limite_inferior) | (df["Valor_Total"] > limite_superior)]
print(f"  Q1: R$ {Q1:.2f}  |  Q3: R$ {Q3:.2f}  |  IQR: R$ {IQR:.2f}")
print(f"  Limite inferior: R$ {limite_inferior:.2f}")
print(f"  Limite superior: R$ {limite_superior:.2f}")
print(f"  Outliers detectados: {len(outliers)} ({len(outliers)/len(df)*100:.1f}% do total)")
print()

fig, ax = plt.subplots(figsize=(10, 5))
bp = ax.boxplot(df["Valor_Total"], vert=False, patch_artist=True,
                boxprops=dict(facecolor=CORES_MARCA[0], color="white"),
                medianprops=dict(color=CORES_MARCA[1], linewidth=2),
                whiskerprops=dict(color="white"),
                capprops=dict(color="white"),
                flierprops=dict(marker="o", color=CORES_MARCA[2], alpha=0.5))
ax.set_title("Boxplot — Distribuição do Valor Total por Transação", fontsize=13)
ax.set_xlabel("Valor Total (R$)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
plt.tight_layout()
plt.savefig("data/graficos/05_outliers_boxplot.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/05_outliers_boxplot.png")

# ── ANÁLISE 7: Correlação Desconto × Valor_Total ─────────────────────────────

print("\n─" * 61)
print("  [7] CORRELAÇÃO — Desconto (%) vs Valor Total")
print("─" * 60)

corr = df["Desconto_Pct"].corr(df["Valor_Total"])
print(f"  Coeficiente de correlação: {corr:.4f}")
if abs(corr) < 0.2:
    print("  Interpretação: correlação muito fraca (descontos não impactam muito o ticket)")
elif abs(corr) < 0.5:
    print("  Interpretação: correlação fraca a moderada")
else:
    print("  Interpretação: correlação forte")
print()

fig, ax = plt.subplots(figsize=(8, 5))
# Amostra de 500 pontos para não deixar o gráfico pesado
amostra = df.sample(min(500, len(df)), random_state=42)
ax.scatter(amostra["Desconto_Pct"], amostra["Valor_Total"],
           alpha=0.4, color=CORES_MARCA[0], s=20)
ax.set_title(f"Dispersão: Desconto (%) × Valor Total | Corr={corr:.3f}", fontsize=12)
ax.set_xlabel("Desconto (%)")
ax.set_ylabel("Valor Total (R$)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}"))
plt.tight_layout()
plt.savefig("data/graficos/06_correlacao_desconto.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/06_correlacao_desconto.png")

# ── ANÁLISE 8: Segmentação RFM ───────────────────────────────────────────────

print("\n─" * 61)
print("  [8] SEGMENTAÇÃO RFM DOS CLIENTES")
print("─" * 60)
print("  RFM = Recency (Recência), Frequency (Frequência), Monetary (Monetário)")
print("  Cada cliente recebe um score de 1 a 5 em cada dimensão.")
print()

# Data de referência = último dia do dataset + 1
data_referencia = df["Data_Venda"].max() + pd.Timedelta(days=1)

# Calcula RFM por cliente
rfm = df.groupby("ID_Cliente").agg(
    Recencia    = ("Data_Venda", lambda x: (data_referencia - x.max()).days),
    Frequencia  = ("ID_Transacao", "count"),
    Monetario   = ("Valor_Total", "sum")
).reset_index()

# Score 1-5: para Recência, quanto MENOR o número de dias, melhor (score maior)
rfm["R_Score"] = pd.qcut(rfm["Recencia"],    q=5, labels=[5, 4, 3, 2, 1])
rfm["F_Score"] = pd.qcut(rfm["Frequencia"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
rfm["M_Score"] = pd.qcut(rfm["Monetario"].rank(method="first"),  q=5, labels=[1, 2, 3, 4, 5])

# Converte scores para inteiro
rfm["R_Score"] = rfm["R_Score"].astype(int)
rfm["F_Score"] = rfm["F_Score"].astype(int)
rfm["M_Score"] = rfm["M_Score"].astype(int)

# Score RFM combinado (média ponderada)
rfm["RFM_Score"] = (rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]) / 3

# Classifica em segmentos de negócio
def classificar_rfm(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champion"       # comprou recente, frequente, alto valor
    elif r >= 3 and f >= 3:
        return "Loyal"          # fiel, mas não necessariamente o maior gasto
    elif r >= 3 and f <= 2:
        return "Promising"      # recente mas ainda pouco frequente
    elif r <= 2 and f >= 3:
        return "At Risk"        # comprava bem mas sumiu — risco de churn
    else:
        return "Lost"           # não compra há muito tempo

rfm["Segmento"] = rfm.apply(classificar_rfm, axis=1)

# Exibe resumo
segmentos = rfm["Segmento"].value_counts()
print(f"  {'Segmento':<15} {'Clientes':>10} {'% Base':>10}")
print(f"  {'-'*15} {'-'*10} {'-'*10}")
for seg, cnt in segmentos.items():
    print(f"  {seg:<15} {cnt:>10,} {cnt/len(rfm)*100:>9.1f}%")
print()

# Salva a tabela RFM
rfm.to_csv("data/rfm_clientes.csv", index=False, encoding="utf-8-sig")
print("  ✔ Tabela RFM salva: data/rfm_clientes.csv")

# Gráfico de segmentos RFM
fig, ax = plt.subplots(figsize=(8, 5))
cores_rfm = [CORES_MARCA[i % len(CORES_MARCA)] for i in range(len(segmentos))]
bars = ax.bar(segmentos.index, segmentos.values, color=cores_rfm)
ax.set_title("Segmentação RFM — Clientes Paraiso Sex Shop", fontsize=13)
ax.set_xlabel("Segmento")
ax.set_ylabel("Número de Clientes")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 1,
            f"{int(h)}", ha="center", va="bottom", fontsize=10, color="white")
plt.tight_layout()
plt.savefig("data/graficos/07_segmentacao_rfm.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/07_segmentacao_rfm.png")

# ── ANÁLISE 9: Receita por Região ────────────────────────────────────────────

print("\n─" * 61)
print("  [9] RECEITA POR REGIÃO")
print("─" * 60)

fat_regiao = df.groupby("Regiao")["Valor_Total"].sum().sort_values(ascending=False)
for reg, val in fat_regiao.items():
    print(f"  {reg:<20} R$ {val:>12,.2f}  ({val/receita_total*100:.1f}%)")
print()

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(fat_regiao.index, fat_regiao.values / 1000, color=CORES_MARCA)
ax.set_title("Receita por Região do Brasil", fontsize=13)
ax.set_ylabel("Receita (R$ mil)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}k"))
plt.tight_layout()
plt.savefig("data/graficos/08_receita_por_regiao.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✔ Gráfico salvo: data/graficos/08_receita_por_regiao.png")

# ── Resumo final ─────────────────────────────────────────────────────────────

print(f"\n{'=' * 60}")
print(f"  EDA CONCLUÍDA COM SUCESSO!")
print(f"{'=' * 60}")
print(f"  8 gráficos gerados em: data/graficos/")
print(f"  Tabela RFM salva em:   data/rfm_clientes.csv")
print(f"\n  Próximo passo: rodar python scripts/04_sql_queries.py")
print(f"{'=' * 60}\n")
