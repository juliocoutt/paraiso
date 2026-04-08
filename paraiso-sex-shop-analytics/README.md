# Paraiso Sex Shop — Análise de Dados de E-Commerce

> **Desafio InsightFlow** | Ciclo completo de análise de dados: ETL → EDA → Dashboard → Modelo Preditivo

---

## Sobre o Projeto

Este projeto simula a atuação de um analista de dados na empresa fictícia **Paraiso Sex Shop**, um e-commerce adulto do mercado brasileiro. A missão é responder perguntas estratégicas de negócio a partir de um dataset de 5.500 transações cobrindo o período de **janeiro de 2023 a dezembro de 2024**.

**Perguntas de negócio respondidas:**
- Qual o perfil de consumo e segmentação dos clientes?
- Quais categorias e produtos têm maior participação na receita?
- Existe padrão de sazonalidade no faturamento?
- É possível prever o faturamento dos próximos meses?
- Quais clientes estão em risco de churn?

**Por que esse nicho?**  
O mercado de produtos íntimos no Brasil apresenta características analíticas ricas: sazonalidade marcada em datas comemorativas (Carnaval, Dia dos Namorados, Natal), ticket médio elevado, e forte potencial de análise de retenção e LTV — tornando-o ideal para demonstrar habilidades analíticas em um contexto de mercado real.

---

## Stack Utilizada

| Ferramenta | Uso |
|---|---|
| Python 3.11+ | ETL, EDA, modelo preditivo |
| pandas | manipulação e análise de dados |
| scikit-learn | Regressão Linear |
| matplotlib / seaborn | visualizações |
| SQLite | banco de dados relacional |
| Power BI Desktop | dashboard interativo |
| GitHub | versionamento e entrega |

---

## Estrutura do Repositório

```
paraiso-sex-shop-analytics/
├── data/
│   ├── ecom_data.csv              # dataset bruto gerado (5.500+ linhas)
│   ├── ecom_data_clean.csv        # dataset limpo (pós ETL)
│   ├── ecom_data_completo.csv     # dataset completo com todos os status
│   ├── rfm_clientes.csv           # segmentação RFM dos clientes
│   ├── previsao_2025.csv          # previsão Jan-Mar/2025
│   ├── query1_faturamento_mensal.csv
│   ├── query3_ranking_categorias.csv
│   ├── query4_retencao_mensal.csv
│   ├── query6_media_movel.csv
│   └── graficos/                  # 9 gráficos exportados em PNG
│       ├── 01_receita_por_categoria.png
│       ├── 02_top10_produtos.png
│       ├── 03_faturamento_mensal.png
│       ├── 04_perfil_clientes.png
│       ├── 05_outliers_boxplot.png
│       ├── 06_correlacao_desconto.png
│       ├── 07_segmentacao_rfm.png
│       ├── 08_receita_por_regiao.png
│       └── 09_previsao_faturamento.png
├── database/
│   └── paraiso_db.sqlite          # banco SQLite com tabelas vendas e vendas_canceladas
├── scripts/
│   ├── 01_gerar_dados.py          # Sprint 1: gera o CSV simulado
│   ├── 02_etl.py                  # Sprint 1: limpa os dados e carrega no SQLite
│   ├── 03_eda.py                  # Sprint 2: análise exploratória + gráficos
│   ├── 04_sql_queries.py          # Sprint 2: 6 queries SQL complexas
│   └── 05_modelo_preditivo.py     # Sprint 4: regressão linear + previsão
├── dashboard/
│   └── paraiso_dashboard.pbix     # dashboard Power BI (3 páginas)
├── requirements.txt
└── README.md
```

---

## Como Executar

### Pré-requisitos
- Python 3.10 ou superior ([download](https://python.org))
- VS Code ([download](https://code.visualstudio.com))
- Power BI Desktop ([download gratuito](https://powerbi.microsoft.com/pt-br/desktop/))

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/SEU_USUARIO/paraiso-sex-shop-analytics.git
cd paraiso-sex-shop-analytics
```

**2. Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Você verá (venv) no início do terminal — sinal de que está ativo
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Execute os scripts na ordem**
```bash
python scripts/01_gerar_dados.py     # gera data/ecom_data.csv
python scripts/02_etl.py             # limpa e carrega no SQLite
python scripts/03_eda.py             # análise exploratória + gráficos
python scripts/04_sql_queries.py     # queries SQL no terminal
python scripts/05_modelo_preditivo.py # regressão linear + previsão
```

**5. Abra o Power BI**
- Abra `dashboard/paraiso_dashboard.pbix`
- Se necessário, atualize a fonte de dados para o caminho local de `data/ecom_data_clean.csv`

---

## Sprint 1: ETL — Ingestão e Limpeza de Dados

### Dataset Gerado

O arquivo `data/ecom_data.csv` contém **5.500 transações simuladas** com as seguintes características:

| Coluna | Tipo | Descrição |
|---|---|---|
| ID_Transacao | int | Chave única da transação |
| Data_Venda | date | Jan/2023 – Dez/2024 |
| ID_Cliente | int | 800 clientes únicos (gera recorrência) |
| Nome_Cliente | str | Nome fictício gerado com Faker BR |
| Genero_Cliente | str | F (58%), M (38%), Não informado (4%) |
| Faixa_Etaria | str | 18-25, 26-35, 36-45, 46+ |
| Regiao | str | Sudeste (43%), Sul (24%), Nordeste (20%), CO (8%), N (5%) |
| Nome_Produto | str | Produto do catálogo |
| Categoria_Produto | str | 6 categorias |
| Valor_Unitario | float | R$ 29,90 a R$ 499,90 |
| Quantidade | int | 1 a 5 |
| Desconto_Pct | float | 0% a 30% |
| Metodo_Pagamento | str | Pix (45%), Cartão Crédito (35%), Boleto (12%), Débito (8%) |
| Status_Pedido | str | Entregue (85%), Cancelado (10%), Devolvido (5%) |
| Canal_Venda | str | Site (50%), App (30%), Marketplace (20%) |

### Decisões de Limpeza

| Problema | Decisão | Justificativa |
|---|---|---|
| 50 linhas duplicadas | Removidas (manter 1ª ocorrência) | Duplicatas de sistema sem valor analítico |
| Nulos em `Metodo_Pagamento` e `Canal_Venda` | Preenchidos com "Não informado" | Preserva linha; flag explícita |
| Nulos em `Desconto_Pct` | Preenchidos com 0.0 | Ausência de dado = sem desconto |
| Pedidos cancelados | Movidos para tabela separada | Não contam como receita realizada |
| Coluna `Valor_Total` | Criada: `Unitario × Qtd × (1 - Desc%)` | Representa receita real por transação |

---

## Sprint 2: EDA e SQL — Principais Insights

### Insights do Python (EDA)

**Receita e Performance:**
- A categoria **Vibradores** lidera em receita total, mesmo com menor volume de vendas — reflexo do maior ticket médio (R$ 89–R$ 499).
- **Lubrificantes** é o maior volume de pedidos (28% das transações), motor de frequência de compra.
- Os **meses de fevereiro** (Carnaval + Dia dos Namorados BR) e **dezembro** (Natal) apresentam os picos mais expressivos de faturamento.

**Perfil de Clientes:**
- Público majoritariamente feminino (58% da receita) na faixa de 26–35 anos.
- Região Sudeste domina com ~43% da receita, alinhado com a distribuição populacional do Brasil.
- Ticket médio por pedido: ~R$ 150–R$ 200 (varia conforme categoria).

**Segmentação RFM:**
| Segmento | Perfil | Ação Recomendada |
|---|---|---|
| **Champion** | Comprou recente, frequente, alto valor | Programa de fidelidade, acesso antecipado a lançamentos |
| **Loyal** | Fiel, mas pode aumentar o ticket | Cross-sell entre categorias (ex: Lingerie + Lubrificante) |
| **Promising** | Recente mas ainda pouco frequente | Onboarding com desconto na 2ª compra |
| **At Risk** | Comprava bem, sumiu | Campanha de reativação (e-mail + oferta personalizada) |
| **Lost** | Inativo há muito tempo | Oferta agressiva de reativação ou aceitar o churn |

### Queries SQL Implementadas

| # | Query | Conceitos |
|---|---|---|
| 1 | Faturamento mensal com ticket médio | GROUP BY, SUM, AVG, COUNT |
| 2 | Top 5 clientes por receita | GROUP BY, ORDER BY DESC, LIMIT |
| 3 | Ranking de categorias com % da receita | CTE, Window Function: SUM OVER, RANK OVER |
| 4 | Taxa de retenção mensal | CTE + Self-JOIN por período |
| 5 | Clientes em churn (90+ dias sem comprar) | Subquery, julianday, HAVING |
| 6 | Média móvel de 3 meses | Window Function: AVG OVER ROWS BETWEEN |

---

## Sprint 3: Dashboard Power BI

### Como Reproduzir o Dashboard

1. Abra o Power BI Desktop
2. Clique em **Obter Dados → Texto/CSV**
3. Selecione o arquivo `data/ecom_data_clean.csv`
4. Clique em **Transformar Dados** → revise os tipos de coluna → **Fechar e Aplicar**

### Estrutura do Dashboard (3 páginas)

**Página 1 — Visão Geral**
- 4 Cards: Faturamento Total | Ticket Médio | Total de Pedidos | Clientes Únicos
- Gráfico de linhas: Faturamento por Mês
- Segmentações (filtros): Ano, Região, Categoria

**Página 2 — Clientes**
- Gráfico de barras: Receita por Faixa Etária
- Gráfico de pizza: Split por Gênero
- Gráfico de barras: Receita por Região
- Tabela: Segmentos RFM (importar `data/rfm_clientes.csv`)

**Página 3 — Produtos**
- Gráfico de barras horizontal: Top 10 Produtos
- Treemap: Receita por Categoria
- Gráfico de dispersão: Desconto × Valor Total

---

## Sprint 4: Modelo Preditivo

### Metodologia

**Objetivo:** Prever o faturamento mensal de janeiro a março de 2025.

**Algoritmo:** Regressão Linear Múltipla (`sklearn.linear_model.LinearRegression`)

**Variáveis de entrada (features):**
- `T` — índice temporal (1 a 24), captura a tendência geral de crescimento
- `Mes_Fev` — dummy para Fevereiro (Carnaval + Dia dos Namorados BR)
- `Mes_Jun` — dummy para Junho (Dia dos Namorados tradicional)
- `Mes_Nov` — dummy para Novembro (Black Friday)
- `Mes_Dez` — dummy para Dezembro (Natal)

**Por que Regressão Linear?**  
Com apenas 24 pontos de dados mensais, modelos mais complexos (como ARIMA ou redes neurais) tendem a superajustar. A Regressão Linear oferece:
- Interpretabilidade dos coeficientes
- Robustez com poucos dados
- Facilidade de comunicação para stakeholders

### Métricas de Avaliação

| Métrica | Descrição | Resultado esperado |
|---|---|---|
| **R²** | % da variação explicada pelo modelo | > 0.60 (bom para séries curtas) |
| **MAE** | Erro médio absoluto (em R$) | Referência: < 10% do faturamento médio |
| **RMSE** | Penaliza erros grandes | Usado como intervalo de confiança |
| **MAPE** | Erro percentual médio | < 15% = aceitável para planejamento |

### Previsão Jan–Mar/2025

| Mês | Previsão | Intervalo (±RMSE) |
|---|---|---|
| 2025-01 | *executar o script* | *executar o script* |
| 2025-02 | *executar o script* | *executar o script* |
| 2025-03 | *executar o script* | *executar o script* |

> Execute `python scripts/05_modelo_preditivo.py` para ver os valores reais gerados com os seus dados.

---

## Insights Estratégicos (Storytelling)

Com base nas análises realizadas, as **5 recomendações principais** para o time comercial da Paraiso Sex Shop são:

**1. Concentrar estoque e campanhas em Fevereiro e Junho**  
Os picos de faturamento em Fevereiro (Carnaval + Dia dos Namorados BR) e Junho (Dia dos Namorados tradicional) são consistentes. Antecipar compras de estoque 45 dias antes reduz risco de ruptura nos itens de maior giro (Lubrificantes e Lingerie).

**2. Estratégia de Cross-Sell entre Vibradores e Lubrificantes**  
Vibradores têm o maior ticket médio mas menor volume; Lubrificantes têm o maior volume mas menor ticket. Um kit combinado com desconto progressivo aumenta o ticket médio sem reduzir margem.

**3. Programa de reativação para clientes "At Risk"**  
O segmento RFM "At Risk" representa clientes que já gastaram bem mas estão inativos. Uma campanha de e-mail personalizada com desconto de 15-20% pode recuperar 20-30% desse segmento a custo menor que a aquisição de novos clientes.

**4. Expandir presença no Nordeste**  
Apesar de representar 20% da população brasileira, o Nordeste contribui com cerca de 20% da receita — mesma proporção. Há espaço para crescimento com campanhas regionalizadas e parcerias com marketplaces locais.

**5. Investir no canal App**  
O App representa 30% das vendas e tende a ter maior fidelização que site e marketplace. Melhorias de UX e notificações push em datas comemorativas podem aumentar o share do canal com maior LTV.

---

## Autor

**[SEU NOME]**  
Engenheiro de Produção | Pós-Graduação em Gestão de Projetos  
5 anos de experiência em Marketplaces e E-Commerce

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://linkedin.com/in/SEU_PERFIL)
[![GitHub](https://img.shields.io/badge/GitHub-black)](https://github.com/SEU_USUARIO)

---

*Projeto desenvolvido como parte do programa de formação InsightFlow — Ciclo de Análise de Dados.*
