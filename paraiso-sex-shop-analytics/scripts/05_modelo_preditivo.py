# =============================================================================
# PARAISO SEX SHOP — MODELO PREDITIVO (REGRESSÃO LINEAR)
# Sprint 4 | Script 5 de 5
# =============================================================================
# O que esse script faz:
#   1. Agrega o faturamento mensal dos 24 meses de histórico
#   2. Cria variáveis de sazonalidade (meses com alta demanda)
#   3. Treina um modelo de Regressão Linear com scikit-learn
#   4. Avalia o modelo com R², MAE e RMSE
#   5. Prevê o faturamento dos próximos 3 meses (Jan, Fev, Mar/2025)
#   6. Gera um gráfico com histórico + previsão e intervalo de confiança
#
# Como rodar:
#   python scripts/05_modelo_preditivo.py
#
# Conceitos explicados:
#   - Regressão Linear: tenta encontrar a linha que melhor explica
#     a relação entre o tempo (X) e o faturamento (Y)
#   - R²: mede o quanto o modelo explica a variação dos dados (0 a 1)
#   - MAE: erro médio absoluto em R$ — quanto o modelo erra em média
#   - RMSE: raiz do erro quadrático médio — penaliza erros grandes
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# Funções de Machine Learning da biblioteca scikit-learn
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score

print("=" * 65)
print("  PARAISO SEX SHOP — Modelo Preditivo de Faturamento")
print("=" * 65)

# ── Configurações visuais (mesmo estilo do script de EDA) ─────────────────

CORES_MARCA = ["#9B59B6", "#E91E8C", "#F39C12", "#1ABC9C"]
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor":   "#16213e",
    "axes.labelcolor":  "white",
    "xtick.color":      "white",
    "ytick.color":      "white",
    "text.color":       "white",
    "axes.titlecolor":  "white",
    "axes.edgecolor":   "#444444",
    "grid.color":       "#333333",
})

# ── PASSO 1: Carrega e agrega os dados ───────────────────────────────────────

print("\n[1/5] Carregando e agregando faturamento mensal...")

caminho = "data/ecom_data_clean.csv"
if not os.path.exists(caminho):
    print(f"\n  ERRO: '{caminho}' não encontrado!")
    print("  Rode primeiro: python scripts/02_etl.py")
    exit(1)

df = pd.read_csv(caminho, encoding="utf-8-sig", parse_dates=["Data_Venda"])

# Agrega o faturamento total por mês
fat_mensal = (
    df.groupby("AnoMes")["Valor_Total"]
    .sum()
    .reset_index()
    .sort_values("AnoMes")
    .rename(columns={"Valor_Total": "Faturamento"})
)

# Adiciona uma coluna numérica de tempo (1, 2, 3, ..., 24)
# Isso é necessário porque a Regressão Linear precisa de número, não de data
fat_mensal["T"] = range(1, len(fat_mensal) + 1)

# Extrai o número do mês (1 a 12) para criar variáveis sazonais
fat_mensal["Mes_Num"] = fat_mensal["AnoMes"].str[-2:].astype(int)

print(f"  ✔ {len(fat_mensal)} meses de histórico carregados")
print(f"  Período: {fat_mensal['AnoMes'].min()} a {fat_mensal['AnoMes'].max()}")

# ── PASSO 2: Feature Engineering (criação de variáveis explicativas) ─────────

print("\n[2/5] Criando variáveis de sazonalidade...")

# Cria variáveis binárias (0 ou 1) para meses com alta demanda
# A Regressão Linear vai aprender que esses meses têm impacto positivo
fat_mensal["Mes_Fev"]   = (fat_mensal["Mes_Num"] == 2).astype(int)   # Carnaval + Dia dos Nam.
fat_mensal["Mes_Jun"]   = (fat_mensal["Mes_Num"] == 6).astype(int)   # Dia dos Namorados
fat_mensal["Mes_Nov"]   = (fat_mensal["Mes_Num"] == 11).astype(int)  # Black Friday
fat_mensal["Mes_Dez"]   = (fat_mensal["Mes_Num"] == 12).astype(int)  # Natal

# Define quais colunas serão usadas como variáveis de entrada (X)
features = ["T", "Mes_Fev", "Mes_Jun", "Mes_Nov", "Mes_Dez"]

# X = variáveis que o modelo vai usar para fazer a previsão
# y = o que queremos prever (faturamento)
X = fat_mensal[features].values
y = fat_mensal["Faturamento"].values

print(f"  ✔ Features criadas: {features}")

# ── PASSO 3: Treina o modelo de Regressão Linear ─────────────────────────────

print("\n[3/5] Treinando o modelo de Regressão Linear...")

modelo = LinearRegression()

# Validação cruzada com 5 folds (testa o modelo em diferentes partes dos dados)
# Retorna os scores de R² para cada fold
if len(X) >= 5:
    cv_scores = cross_val_score(modelo, X, y, cv=5, scoring="r2")
    print(f"  Validação cruzada R² (5 folds): {cv_scores.round(3)}")
    print(f"  R² médio CV: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Treina o modelo com todos os dados (para gerar previsões)
modelo.fit(X, y)

# Gera as previsões no período histórico
y_pred = modelo.predict(X)

# ── PASSO 4: Avaliação do modelo ─────────────────────────────────────────────

print("\n[4/5] Avaliando o modelo...")

r2   = r2_score(y, y_pred)
mae  = mean_absolute_error(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))
mape = np.mean(np.abs((y - y_pred) / y)) * 100  # Erro percentual médio

print(f"\n  {'─' * 45}")
print(f"  MÉTRICAS DE AVALIAÇÃO DO MODELO")
print(f"  {'─' * 45}")
print(f"  R²  (coeficiente de determinação): {r2:.4f}")
print(f"  MAE (erro médio absoluto):         R$ {mae:,.2f}")
print(f"  RMSE (raiz erro quadrático médio): R$ {rmse:,.2f}")
print(f"  MAPE (erro percentual médio):      {mape:.1f}%")
print(f"  {'─' * 45}")

# Interpretação automática do R²
print(f"\n  Interpretação do R² = {r2:.4f}:")
if r2 >= 0.80:
    print("  → Excelente! O modelo explica mais de 80% da variação do faturamento.")
elif r2 >= 0.60:
    print("  → Bom. O modelo captura a tendência geral com boa precisão.")
elif r2 >= 0.40:
    print("  → Moderado. O modelo identifica tendências mas com limitações.")
else:
    print("  → Fraco. Os dados têm muita variação não explicada pela tendência linear.")

print(f"\n  Coeficientes do modelo:")
print(f"  Intercepto (base):         R$ {modelo.intercept_:,.2f}")
for feat, coef in zip(features, modelo.coef_):
    print(f"  {feat:<20} R$ {coef:>10,.2f} por unidade")

# ── PASSO 5: Previsão dos próximos 3 meses ───────────────────────────────────

print("\n[5/5] Prevendo faturamento para Jan-Mar/2025...")

# Cria os dados dos próximos 3 meses
proximos_meses = pd.DataFrame({
    "AnoMes":   ["2025-01", "2025-02", "2025-03"],
    "T":        [25, 26, 27],                   # continua a sequência 1..24..25..26..27
    "Mes_Num":  [1, 2, 3],
    "Mes_Fev":  [0, 1, 0],
    "Mes_Jun":  [0, 0, 0],
    "Mes_Nov":  [0, 0, 0],
    "Mes_Dez":  [0, 0, 0],
})

X_futuro = proximos_meses[features].values
y_futuro = modelo.predict(X_futuro)

# Calcula intervalo de confiança simplificado (±1 RMSE)
# Na prática, quanto maior o RMSE, maior a incerteza da previsão
intervalo = rmse

print(f"\n  {'Mês':<10} {'Previsão':>15} {'Intervalo (±1 RMSE)':>25}")
print(f"  {'─'*10} {'─'*15} {'─'*25}")
for mes, prev in zip(proximos_meses["AnoMes"], y_futuro):
    print(f"  {mes:<10} R$ {prev:>12,.2f}   ± R$ {intervalo:>10,.2f}")

# ── Gráfico: Histórico + Previsão ─────────────────────────────────────────────

print("\n  Gerando gráfico de previsão...")

os.makedirs("data/graficos", exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 6))

# Eixo X: todos os meses (histórico + futuro)
todos_meses  = list(fat_mensal["AnoMes"]) + list(proximos_meses["AnoMes"])
n_historico  = len(fat_mensal)
n_total      = len(todos_meses)
x_hist       = np.arange(n_historico)
x_futuro_idx = np.arange(n_historico, n_total)

# 1. Linha do faturamento real
ax.plot(x_hist, y / 1000, marker="o", color=CORES_MARCA[0],
        linewidth=2, markersize=5, label="Faturamento Real", zorder=3)

# 2. Linha do modelo ajustado (fitted values)
ax.plot(x_hist, y_pred / 1000, linestyle="--", color=CORES_MARCA[2],
        linewidth=1.5, alpha=0.8, label="Modelo Ajustado (Regressão Linear)")

# 3. Linha da previsão (futuro)
x_previsao = np.array([n_historico - 1] + list(x_futuro_idx))
y_previsao = np.array([y_pred[-1]] + list(y_futuro)) / 1000
ax.plot(x_previsao, y_previsao, marker="s", color=CORES_MARCA[1],
        linewidth=2, markersize=7, linestyle="-", label="Previsão 2025", zorder=3)

# 4. Faixa de incerteza (intervalo de confiança ±1 RMSE)
ax.fill_between(x_futuro_idx,
                (y_futuro - intervalo) / 1000,
                (y_futuro + intervalo) / 1000,
                alpha=0.25, color=CORES_MARCA[1], label=f"Intervalo ±R$ {intervalo/1000:.0f}k (±1 RMSE)")

# 5. Linha vertical separando histórico de previsão
ax.axvline(x=n_historico - 0.5, color="gray", linestyle=":", alpha=0.7)
ax.text(n_historico - 0.3, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1,
        " ← Histórico   Previsão →", color="gray", fontsize=9, va="top")

# Formatação
ax.set_title("Previsão de Faturamento Mensal — Paraiso Sex Shop", fontsize=14, pad=15)
ax.set_xlabel("Mês")
ax.set_ylabel("Faturamento (R$ mil)")
ax.set_xticks(range(n_total))
ax.set_xticklabels(todos_meses, rotation=45, ha="right", fontsize=7)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}k"))
ax.legend(loc="upper left", fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("data/graficos/09_previsao_faturamento.png", dpi=150, bbox_inches="tight")
plt.close()

print("  ✔ Gráfico salvo: data/graficos/09_previsao_faturamento.png")

# ── Salva previsão em CSV ─────────────────────────────────────────────────────

df_previsao = proximos_meses[["AnoMes"]].copy()
df_previsao["Previsao_Faturamento"] = y_futuro.round(2)
df_previsao["Intervalo_RMSE"]       = round(intervalo, 2)
df_previsao["Limite_Inferior"]      = (y_futuro - intervalo).round(2)
df_previsao["Limite_Superior"]      = (y_futuro + intervalo).round(2)
df_previsao.to_csv("data/previsao_2025.csv", index=False, encoding="utf-8-sig")
print("  ✔ Previsão salva: data/previsao_2025.csv")

# ── Resumo final ─────────────────────────────────────────────────────────────

print(f"\n{'=' * 65}")
print(f"  MODELO PREDITIVO CONCLUÍDO!")
print(f"{'=' * 65}")
print(f"  R² do modelo: {r2:.4f} | MAE: R$ {mae:,.2f} | RMSE: R$ {rmse:,.2f}")
print(f"\n  Previsão para os próximos 3 meses:")
for mes, prev in zip(proximos_meses["AnoMes"], y_futuro):
    print(f"    {mes}: R$ {prev:,.2f}")
print(f"\n  Todos os scripts foram executados com sucesso!")
print(f"  Agora abra o Power BI Desktop e importe data/ecom_data_clean.csv")
print(f"{'=' * 65}\n")
