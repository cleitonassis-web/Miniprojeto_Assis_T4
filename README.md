# Miniprojeto_Assis_T4

Mini-Projeto Avaliativo do módulo **Manipulação de Dados com Python e SQL** (Módulo 1, Semana 07) — Análise Exploratória de Dados (AED) sobre a base pública de varejo **"Base Varejo"**, do Kaggle.

- Aluno: Assis
- Turma: T4
- Fonte dos dados: [kaggle.com/datasets/namespaiva/base-varejo](https://www.kaggle.com/datasets/namespaiva/base-varejo)

## Sobre o projeto

O script `analise_varejo.py` percorre o pipeline de ETL (Extract, Transform, Load) completo sobre 830.000 registros de compras de 1.000 clientes em uma rede de supermercados, cobrindo:

1. Importação do CSV (com pandas e também com `csv.DictReader`, nativo do Python);
2. Transformação de tipos de dados (texto, inteiros, datas, com uso de regex);
3. Limpeza de valores ausentes, inconsistências e duplicatas;
4. Agrupamentos (`groupby`/`pivot_table`) explorando diferentes recortes da base;
5. Estatísticas descritivas completas da coluna "número de filhos do cliente" (CL_FHL);
6. Geração de insights a partir dos dados tratados.

## Como executar

1. Baixe o arquivo `Base Varejo.csv` em [kaggle.com/datasets/namespaiva/base-varejo](https://www.kaggle.com/datasets/namespaiva/base-varejo) (requer login no Kaggle) e salve-o como `data/Varejo.csv` dentro desta pasta (o arquivo não está no repositório por ter ~48MB).
2. Instale a dependência: `pip install pandas`
3. Rode: `python3 analise_varejo.py`
4. O script imprime cada etapa no terminal e, ao final, exporta a base tratada em `data/Varejo_limpo.csv`.

## Estrutura do repositório

```
Miniprojeto_Assis_T4/
├── analise_varejo.py          # script principal (todas as etapas comentadas)
├── README.md                  # este arquivo
├── README_Assis_T4.md         # reflexão sobre ETL/qualidade de dados + insights
├── .gitignore
└── data/
    └── (Varejo.csv e Varejo_limpo.csv - não versionados, ver instruções acima)
```

Para a reflexão teórica sobre ETL/qualidade de dados e os insights obtidos, veja [`README_Assis_T4.md`](./README_Assis_T4.md).
