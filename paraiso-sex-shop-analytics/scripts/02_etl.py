# =============================================================================
# PARAISO SEX SHOP — ETL (LIMPEZA E CARGA DOS DADOS)
# Sprint 1 | Script 2 de 5
# =============================================================================
# O que esse script faz:
#   1. Lê o arquivo bruto data/ecom_data.csv
#   2. Remove duplicatas e valores inconsistentes
#   3. Padroniza formatos (datas, moeda)
#   4. Cria a coluna Valor_Total (receita real por transação)
#   5. Salva o dataset limpo em data/ecom_data_clean.csv
#   6. Cria o banco de dados SQLite em database/paraiso_db.sqlite
#      com duas tabelas: vendas e vendas_canceladas
#
# Como rodar:
#   Após rodar o script 01, execute: python scripts/02_etl.py
# =============================================================================

import pandas as pd    # para trabalhar com a tabela de dados
import sqlite3         # para criar e manipular o banco de dados SQLite
import os              # para criar pastas

print("=" * 60)
print("  PARAISO SEX SHOP — ETL (Limpeza de Dados)")
print("=" * 60)

# ── PASSO 1: Leitura do arquivo bruto ────────────────────────────────────────

print("\n[1/7] Lendo o arquivo bruto...")

caminho_bruto = "data/ecom_data.csv"

# Verifica se o arquivo existe antes de tentar abrir
if not os.path.exists(caminho_bruto):
    print(f"\n  ERRO: Arquivo '{caminho_bruto}' não encontrado!")
    print("  Rode primeiro: python scripts/01_gerar_dados.py")
    exit(1)

df = pd.read_csv(caminho_bruto, encoding="utf-8-sig")

print(f"  ✔ Arquivo lido: {len(df):,} linhas, {len(df.columns)} colunas")
print(f"  Colunas: {list(df.columns)}")

# ── PASSO 2: Diagnóstico inicial ─────────────────────────────────────────────

print("\n[2/7] Diagnóstico dos dados brutos...")

# Conta duplicatas (linhas completamente iguais)
n_duplicatas = df.duplicated().sum()
print(f"  Duplicatas encontradas: {n_duplicatas}")

# Conta valores nulos por coluna (mostra apenas as colunas com nulos)
nulos = df.isnull().sum()
nulos_com_valor = nulos[nulos > 0]
if len(nulos_com_valor) > 0:
    print("  Valores nulos por coluna:")
    for col, qtd in nulos_com_valor.items():
        print(f"    {col:<25} {qtd} nulos")
else:
    print("  Nenhum valor nulo encontrado.")

# ── PASSO 3: Remoção de duplicatas ───────────────────────────────────────────

print("\n[3/7] Removendo duplicatas...")

linhas_antes = len(df)
# Mantém apenas a primeira ocorrência de cada ID_Transacao
df = df.drop_duplicates(subset=["ID_Transacao"], keep="first")
linhas_depois = len(df)

print(f"  ✔ {linhas_antes - linhas_depois} duplicatas removidas")
print(f"  Total após limpeza: {linhas_depois:,} linhas")

# ── PASSO 4: Tratamento de valores nulos ─────────────────────────────────────

print("\n[4/7] Tratando valores nulos...")

# Metodo_Pagamento nulo → preenche com "Não informado"
n_mp = df["Metodo_Pagamento"].isnull().sum()
df["Metodo_Pagamento"] = df["Metodo_Pagamento"].fillna("Não informado")
print(f"  ✔ Metodo_Pagamento: {n_mp} nulos → preenchidos com 'Não informado'")

# Canal_Venda nulo → preenche com "Não informado"
n_cv = df["Canal_Venda"].isnull().sum()
df["Canal_Venda"] = df["Canal_Venda"].fillna("Não informado")
print(f"  ✔ Canal_Venda: {n_cv} nulos → preenchidos com 'Não informado'")

# Desconto_Pct nulo → preenche com 0.0 (sem desconto)
n_desc = df["Desconto_Pct"].isnull().sum()
df["Desconto_Pct"] = df["Desconto_Pct"].fillna(0.0)
print(f"  ✔ Desconto_Pct: {n_desc} nulos → preenchidos com 0.0")

# ── PASSO 5: Padronização de formatos ────────────────────────────────────────

print("\n[5/7] Padronizando formatos...")

# Converte Data_Venda para o tipo datetime (data real, não texto)
df["Data_Venda"] = pd.to_datetime(df["Data_Venda"], format="%Y-%m-%d")

# Garante que os valores numéricos têm 2 casas decimais
df["Valor_Unitario"] = df["Valor_Unitario"].round(2)
df["Desconto_Pct"]   = df["Desconto_Pct"].round(2)

# Garante que Quantidade é sempre inteiro
df["Quantidade"] = df["Quantidade"].astype(int)

# Padroniza campos de texto (remove espaços extras, corrige capitalização)
df["Categoria_Produto"] = df["Categoria_Produto"].str.strip()
df["Status_Pedido"]     = df["Status_Pedido"].str.strip()
df["Regiao"]            = df["Regiao"].str.strip()

# ── PASSO 5b: Criação de colunas derivadas ───────────────────────────────────

# Valor_Total = preço * quantidade * (1 - desconto%)
# Exemplo: R$100,00 × 2 itens × (1 - 10%) = R$180,00
df["Valor_Total"] = (
    df["Valor_Unitario"] * df["Quantidade"] * (1 - df["Desconto_Pct"] / 100)
).round(2)

# Extrai campos de data para facilitar análises no Power BI
df["Ano"]       = df["Data_Venda"].dt.year
df["Mes"]       = df["Data_Venda"].dt.month
df["AnoMes"]    = df["Data_Venda"].dt.to_period("M").astype(str)  # ex: "2023-01"
df["DiaSemana"] = df["Data_Venda"].dt.day_name()                   # ex: "Monday"

print(f"  ✔ Data_Venda → convertida para datetime")
print(f"  ✔ Valor_Total calculado (Unitario × Quantidade × (1 - Desconto))")
print(f"  ✔ Colunas Ano, Mes, AnoMes, DiaSemana criadas")

# ── PASSO 6: Separação por status e salvamento dos CSVs ──────────────────────

print("\n[6/7] Separando dados por status e salvando CSVs...")

# Separa vendas canceladas (serão carregadas em tabela separada no banco)
df_cancelados = df[df["Status_Pedido"] == "Cancelado"].copy()

# Dataset principal = apenas Entregue e Devolvido (receita realizada)
df_clean = df[df["Status_Pedido"] != "Cancelado"].copy()

# Garante que a pasta data/ existe
os.makedirs("data", exist_ok=True)

# Salva o dataset limpo (para usar no Power BI também)
df_clean.to_csv("data/ecom_data_clean.csv", index=False, encoding="utf-8-sig")
df.to_csv("data/ecom_data_completo.csv", index=False, encoding="utf-8-sig")

print(f"  ✔ data/ecom_data_clean.csv salvo — {len(df_clean):,} linhas (Entregue + Devolvido)")
print(f"  ✔ data/ecom_data_completo.csv salvo — {len(df):,} linhas (todos os status)")
print(f"  ✔ Pedidos cancelados separados: {len(df_cancelados):,} linhas")

# ── PASSO 7: Carga no banco SQLite ───────────────────────────────────────────

print("\n[7/7] Criando banco de dados SQLite...")

os.makedirs("database", exist_ok=True)

caminho_db = "database/paraiso_db.sqlite"

# Conecta (ou cria) o banco de dados SQLite
# sqlite3 é uma biblioteca nativa do Python, não precisa instalar nada
conn = sqlite3.connect(caminho_db)

# ── Tabela principal: vendas ──
# if_exists="replace" → recria a tabela se ela já existir
# index=False → não salva o índice do pandas como coluna

# Prepara o dataframe para o SQLite (converte datas para string)
df_sql = df_clean.copy()
df_sql["Data_Venda"] = df_sql["Data_Venda"].dt.strftime("%Y-%m-%d")
df_sql.to_sql("vendas", conn, if_exists="replace", index=False)
print(f"  ✔ Tabela 'vendas' criada com {len(df_sql):,} registros")

# ── Tabela de cancelados: vendas_canceladas ──
df_canc_sql = df_cancelados.copy()
df_canc_sql["Data_Venda"] = df_canc_sql["Data_Venda"].dt.strftime("%Y-%m-%d")
df_canc_sql.to_sql("vendas_canceladas", conn, if_exists="replace", index=False)
print(f"  ✔ Tabela 'vendas_canceladas' criada com {len(df_canc_sql):,} registros")

# Verifica se as tabelas foram criadas corretamente
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [t[0] for t in cursor.fetchall()]
print(f"  ✔ Tabelas no banco: {tabelas}")

conn.close()

# ── Resumo final ─────────────────────────────────────────────────────────────

receita_total = df_clean["Valor_Total"].sum()

print(f"\n{'=' * 60}")
print(f"  ETL CONCLUÍDO COM SUCESSO!")
print(f"{'=' * 60}")
print(f"  Banco de dados: {caminho_db}")
print(f"  Período dos dados: {df_clean['Data_Venda'].min().date()} a {df_clean['Data_Venda'].max().date()}")
print(f"  Total de vendas (limpas): {len(df_clean):,}")
print(f"  Receita total do período: R$ {receita_total:,.2f}")
print(f"  Ticket médio: R$ {df_clean['Valor_Total'].mean():,.2f}")
print(f"\n  Próximo passo: rodar python scripts/03_eda.py")
print(f"{'=' * 60}\n")
