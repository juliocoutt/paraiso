# =============================================================================
# PARAISO SEX SHOP — GERAÇÃO DO DATASET SIMULADO
# Sprint 1 | Script 1 de 5
# =============================================================================
# O que esse script faz:
#   Gera um arquivo CSV com 5.500 transações simuladas do e-commerce
#   "Paraiso Sex Shop", com dados realistas do mercado brasileiro.
#   Inclui sazonalidade (Carnaval, Dia dos Namorados, Natal) e
#   comportamento de compra variado por categoria e região.
#
# Como rodar:
#   1. Abra o terminal no VS Code (Ctrl + `)
#   2. Ative o ambiente virtual:
#        Windows: venv\Scripts\activate
#   3. Execute: python scripts/01_gerar_dados.py
#   4. O arquivo data/ecom_data.csv será criado automaticamente.
# =============================================================================

import pandas as pd           # biblioteca para trabalhar com tabelas de dados
import numpy as np            # biblioteca para cálculos matemáticos
from faker import Faker       # biblioteca para gerar nomes e dados fictícios
import random                 # biblioteca para sortear valores aleatórios
from datetime import date, timedelta  # para trabalhar com datas
import os                     # para criar pastas no computador

# ── Configurações iniciais ───────────────────────────────────────────────────

# Define uma semente aleatória para que os dados gerados sejam sempre iguais
# (se rodar o script de novo, os dados serão idênticos)
random.seed(42)
np.random.seed(42)

# Cria um gerador de dados fictícios em português do Brasil
fake = Faker('pt_BR')
Faker.seed(42)

# Define o total de linhas que queremos gerar
TOTAL_LINHAS = 30000

print("=" * 60)
print("  PARAISO SEX SHOP — Geração de Dados")
print("=" * 60)
print(f"\n▶ Iniciando geração de {TOTAL_LINHAS} transações...\n")

# ── Listas de produtos por categoria ────────────────────────────────────────

# Cada categoria tem uma lista de produtos com seu preço unitário
catalogo = {
    "Vibradores": {
        "produtos": [
            "Vibrador Clássico Silicone",
            "Vibrador Rabbit Premium",
            "Massageador Corporal Wave",
            "Vibrador Ponto G Flex",
            "Mini Vibrador Discreto",
            "Vibrador Duplo Prazer",
            "Wand Massager Pro",
        ],
        "preco_min": 89.90,
        "preco_max": 499.90,
        "peso_vendas": 0.22,   # chance de uma venda ser desta categoria (22%)
    },
    "Lubrificantes": {
        "produtos": [
            "Lubrificante Íntimo Aquoso 100ml",
            "Lubrificante Íntimo Aquoso 250ml",
            "Lubrificante Base Silicone",
            "Gel Excitante Feminino",
            "Gel Excitante Masculino",
            "Lubrificante Sabores Morango",
            "Lubrificante Sabores Baunilha",
            "Óleo de Massagem Relaxante",
        ],
        "preco_min": 29.90,
        "preco_max": 89.90,
        "peso_vendas": 0.28,   # categoria com maior volume (28%)
    },
    "Lingerie": {
        "produtos": [
            "Body Rendado Vermelho",
            "Conjunto Lingerie Boudoir",
            "Camisola Sensual Preta",
            "Body Coelhinha Plus Size",
            "Fantasia Enfermeira",
            "Fantasia Policial",
            "Lingerie Cropped com Bojo",
            "Meia-Calça Rendada",
        ],
        "preco_min": 59.90,
        "preco_max": 199.90,
        "peso_vendas": 0.25,   # segunda maior categoria (25%)
    },
    "Acessórios BDSM": {
        "produtos": [
            "Kit Algemas Veludo",
            "Venda para Olhos Satin",
            "Chicote de Couro Soft",
            "Colar e Guia BDSM",
            "Kit Iniciante BDSM 5 Peças",
            "Mordaça Silicone",
            "Corda de Shibari 5m",
        ],
        "preco_min": 49.90,
        "preco_max": 299.90,
        "peso_vendas": 0.10,   # nicho específico (10%)
    },
    "Jogos Adultos": {
        "produtos": [
            "Jogo de Cartas Sexo Quiz",
            "Dado do Prazer",
            "Kit Roleplay Surpresa",
            "Jogo Tabuleiro Casais",
            "Cartas Posições Kamasutra",
            "Dominó Erótico",
        ],
        "preco_min": 39.90,
        "preco_max": 129.90,
        "peso_vendas": 0.08,   # impulso / presente (8%)
    },
    "Cosméticos Íntimos": {
        "produtos": [
            "Creme Retardante Masculino",
            "Creme Excitante Feminino",
            "Spray Prolongador",
            "Gel Térmico Sensação Quente",
            "Perfume Íntimo Floral",
            "Sabonete Íntimo pH Neutro",
            "Kit Cuidados Íntimos",
        ],
        "preco_min": 34.90,
        "preco_max": 149.90,
        "peso_vendas": 0.07,   # cuidados pessoais (7%)
    },
}

# Lista de categorias e seus pesos (probabilidades de aparecer nas vendas)
categorias = list(catalogo.keys())
pesos_categorias = [catalogo[c]["peso_vendas"] for c in categorias]

# ── Configurações de clientes e regiões ─────────────────────────────────────

# 800 clientes únicos → gera recorrência realista
NUM_CLIENTES = 3000

# Informações fictícias de cada cliente (geradas uma vez e reutilizadas)
clientes = []
for i in range(1, NUM_CLIENTES + 1):
    genero = random.choices(["F", "M", "Não informado"], weights=[0.58, 0.38, 0.04])[0]
    faixa_etaria = random.choices(
        ["18-25", "26-35", "36-45", "46+"],
        weights=[0.20, 0.40, 0.28, 0.12]
    )[0]
    if genero == "F":
        nome = fake.name_female()
    elif genero == "M":
        nome = fake.name_male()
    else:
        nome = fake.name()
    regiao = random.choices(
        ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"],
        weights=[0.43, 0.24, 0.20, 0.08, 0.05]   # distribuição pop. brasileira
    )[0]
    clientes.append({
        "ID_Cliente": i,
        "Nome_Cliente": nome,
        "Genero_Cliente": genero,
        "Faixa_Etaria": faixa_etaria,
        "Regiao": regiao,
    })

# Transforma a lista de clientes em uma tabela para facilitar a busca
df_clientes = pd.DataFrame(clientes)

# ── Função que calcula o peso de sazonalidade para cada data ─────────────────

def peso_sazonalidade(data_venda: date) -> float:
    """
    Retorna um multiplicador de volume de vendas com base na data.
    Picos no calendário brasileiro de datas comemorativas:
      - Fevereiro (12): Dia dos Namorados BR / Carnaval → +80%
      - Junho (12): Dia dos Namorados Tradicional → +60%
      - Outubro (31): Halloween → +20%
      - Novembro (25-30): Black Friday → +40%
      - Dezembro: Natal → +50%
    """
    mes = data_venda.month
    dia = data_venda.day

    if mes == 2:
        return 1.80   # Carnaval + Dia dos Namorados BR
    elif mes == 6 and 5 <= dia <= 15:
        return 1.60   # Dia dos Namorados tradicional (12/06)
    elif mes == 10 and dia >= 25:
        return 1.20   # Halloween
    elif mes == 11 and dia >= 25:
        return 1.40   # Black Friday
    elif mes == 12:
        return 1.50   # Natal
    elif mes in [1, 7, 8]:
        return 0.75   # meses fracos (pós-festas, inverno)
    else:
        return 1.00   # meses normais

# ── Geração das transações ───────────────────────────────────────────────────

# Data de início e fim do período de vendas
data_inicio = date(2015, 1, 1)
data_fim    = date(2026, 12, 31)
total_dias  = (data_fim - data_inicio).days

transacoes = []  # lista onde vamos guardar cada transação

for id_transacao in range(1, TOTAL_LINHAS + 1):

    # Sorteia uma data aleatória no período, considerando sazonalidade
    # (datas em meses quentes têm mais chance de aparecer)
    tentativas = 0
    while True:
        dia_offset = random.randint(0, total_dias)
        data_venda = data_inicio + timedelta(days=dia_offset)
        peso = peso_sazonalidade(data_venda)
        # Aceita a data com probabilidade proporcional ao peso sazonal
        if random.random() < peso / 2.0:
            break
        tentativas += 1
        if tentativas > 20:
            # Evita loop infinito; usa a data sorteada mesmo assim
            break

    # Sorteia um cliente (alguns clientes compram mais — distribuição não uniforme)
    # Clientes de menor ID têm ligeiramente mais chance (simula top buyers)
    pesos_clientes = np.exp(-np.arange(NUM_CLIENTES) / 300)
    pesos_clientes /= pesos_clientes.sum()
    idx_cliente = np.random.choice(NUM_CLIENTES, p=pesos_clientes)
    cliente = clientes[idx_cliente]

    # Sorteia a categoria e o produto
    categoria = random.choices(categorias, weights=pesos_categorias)[0]
    produto   = random.choice(catalogo[categoria]["produtos"])

    # Gera o preço unitário dentro da faixa da categoria
    preco_min = catalogo[categoria]["preco_min"]
    preco_max = catalogo[categoria]["preco_max"]
    valor_unitario = round(random.uniform(preco_min, preco_max), 2)

    # Quantidade comprada (a maioria compra 1-2 itens)
    quantidade = random.choices([1, 2, 3, 4, 5], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]

    # Desconto (70% das vendas não têm desconto; o resto tem 5% a 30%)
    desconto_pct = 0.0
    if random.random() > 0.70:
        desconto_pct = round(random.choice([5, 10, 15, 20, 25, 30]), 1)

    # Método de pagamento
    metodo_pagamento = random.choices(
        ["Pix", "Cartão Crédito", "Boleto", "Cartão Débito"],
        weights=[0.45, 0.35, 0.12, 0.08]
    )[0]

    # Status do pedido
    status_pedido = random.choices(
        ["Entregue", "Cancelado", "Devolvido"],
        weights=[0.85, 0.10, 0.05]
    )[0]

    # Canal de venda
    canal_venda = random.choices(
        ["Site", "App", "Marketplace"],
        weights=[0.50, 0.30, 0.20]
    )[0]

    # Adiciona a transação à lista
    transacoes.append({
        "ID_Transacao":      id_transacao,
        "Data_Venda":        data_venda.strftime("%Y-%m-%d"),
        "ID_Cliente":        cliente["ID_Cliente"],
        "Nome_Cliente":      cliente["Nome_Cliente"],
        "Genero_Cliente":    cliente["Genero_Cliente"],
        "Faixa_Etaria":      cliente["Faixa_Etaria"],
        "Regiao":            cliente["Regiao"],
        "Nome_Produto":      produto,
        "Categoria_Produto": categoria,
        "Valor_Unitario":    valor_unitario,
        "Quantidade":        quantidade,
        "Desconto_Pct":      desconto_pct,
        "Metodo_Pagamento":  metodo_pagamento,
        "Status_Pedido":     status_pedido,
        "Canal_Venda":       canal_venda,
    })

    # Mostra progresso a cada 1.000 linhas
    if id_transacao % 1000 == 0:
        print(f"  ✔ {id_transacao:,} transações geradas...")

# ── Introduz erros intencionais para o ETL tratar ───────────────────────────
# (simula problemas reais de dados: nulos, duplicatas, inconsistências)

print("\n▶ Introduzindo imperfeições nos dados (para o ETL tratar)...")

df = pd.DataFrame(transacoes)

# 1. Duplicar 50 linhas aleatórias (simula duplicatas de sistema)
indices_dup = random.sample(range(len(df)), 50)
df_dup = df.iloc[indices_dup].copy()
df = pd.concat([df, df_dup], ignore_index=True)

# 2. Inserir 30 valores nulos em colunas importantes
for _ in range(30):
    col = random.choice(["Metodo_Pagamento", "Canal_Venda", "Desconto_Pct"])
    idx = random.randint(0, len(df) - 1)
    df.at[idx, col] = None

# 3. Embaralhar a ordem das linhas (dados raramente chegam ordenados)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ── Salva o CSV ──────────────────────────────────────────────────────────────

# Garante que a pasta data/ existe
os.makedirs("data", exist_ok=True)

caminho_csv = "data/ecom_data.csv"
df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

# ── Resumo final ─────────────────────────────────────────────────────────────

print(f"\n{'=' * 60}")
print(f"  DATASET GERADO COM SUCESSO!")
print(f"{'=' * 60}")
print(f"  Arquivo: {caminho_csv}")
print(f"  Total de linhas: {len(df):,}")
print(f"  Total de colunas: {len(df.columns)}")
print(f"  Período: {df['Data_Venda'].min()} até {df['Data_Venda'].max()}")
print(f"  Clientes únicos: {df['ID_Cliente'].nunique()}")
print(f"\n  Distribuição por categoria:")
for cat, cnt in df["Categoria_Produto"].value_counts().items():
    print(f"    {cat:<25} {cnt:>5} vendas")
print(f"\n  Próximo passo: rodar python scripts/02_etl.py")
print(f"{'=' * 60}\n")
