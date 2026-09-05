# README_Assis_T4

Mini-Projeto Avaliativo — Análise de Dados com Python T4 — Módulo 1, Semana 07
Aluno: Assis | Turma: T4

## Instruções de execução

1. Abra a pasta do projeto no VS Code (ou envie `analise_varejo.py` para o Google Colab).
2. Garanta que o arquivo `data/Varejo.csv` existe (baixe em [kaggle.com/datasets/namespaiva/base-varejo](https://www.kaggle.com/datasets/namespaiva/base-varejo) caso ainda não tenha — é necessário login no Kaggle).
3. Instale a dependência, se necessário: `pip install pandas`.
4. Execute todo o script de uma vez: `python3 analise_varejo.py` (no VS Code) ou "Executar tudo" (no Colab).
5. A saída é impressa no terminal/console, sprint por sprint, e a base tratada é exportada automaticamente para `data/Varejo_limpo.csv`.

## Reflexão teórica: ETL e qualidade de dados

ETL é a sigla para **Extract, Transform, Load** (Extração, Transformação e Carga), o processo pelo qual dados brutos, geralmente espalhados, incompletos ou em formatos inadequados, são convertidos em uma base confiável e pronta para análise. Neste projeto, a etapa de **Extração** consistiu em ler o arquivo `Varejo.csv` (830 mil linhas, separador `;`) tanto com `pandas.read_csv` quanto de forma nativa com `csv.DictReader`, validando que os 10 campos documentados no dicionário de dados realmente correspondem às colunas presentes no arquivo.

A etapa de **Transformação** foi a mais extensa: colunas que chegaram como texto (`CO_ID`, `CL_ID`, `CL_EC`, `CL_FHL`, `PR_ID`) precisaram ser convertidas para inteiro, com uma expressão regular garantindo que sobrassem apenas dígitos antes da conversão; o campo `DATA` foi convertido de string (`dd/mm/aaaa`) para `datetime`, o que é o que torna possível agrupar por ano/mês depois; e colunas de texto livre (`CL_GENERO`, `CL_SEG`, `PR_CAT`, `PR_NOME`) passaram por uma limpeza de espaços e padronização de caixa alta. Essa etapa é onde mais se manifestam os problemas de **qualidade de dados**: aqui, o principal problema encontrado foi o marcador `#N/D` usado no lugar de valores ausentes nas colunas `PR_CAT` e `PR_NOME` (3.650 registros) — um lembrete de que "ausência de dado" nem sempre aparece como `NaN`/nulo técnico; muitas vezes vem disfarçada de um código ou string específica da fonte, e só é detectada olhando os valores únicos de cada coluna com atenção.

Por fim, a etapa de **Carga** consistiu em consolidar a base já tratada (sem duplicatas, com tipos corretos e categorias preenchidas) e exportá-la para `Varejo_limpo.csv`, pronta para alimentar análises mais avançadas ou dashboards de BI. Um ponto de atenção documentado no código: nem todo requisito genérico de um roteiro de limpeza se aplica a toda base — por exemplo, o item sobre "tratamento de nulos em dimensões físicas" não fazia sentido aqui, já que a base Varejo não tem nenhuma coluna de peso/dimensão de produto. Reconhecer isso (em vez de forçar um tratamento que não existe) também faz parte de um bom processo de qualidade de dados: entender a base antes de aplicar receitas prontas.

## Insights obtidos da análise

1. **Alimentos domina o mix de vendas**: a categoria "ALIMENTOS" é disparada a mais vendida, com 384.197 itens (mais que o triplo da segunda colocada, "HIGIENE", com 137.702), o que indica que a operação é fortemente puxada por compras de reposição/consumo básico.
2. **Público feminino compra um pouco mais**: clientes do gênero F respondem por 382.427 dos 733.447 itens vendidos (~52%) após a limpeza, contra 351.020 do gênero M — uma diferença relevante, mas não avassaladora, sugerindo uma base de clientes relativamente equilibrada entre os dois gêneros.
3. **Volume por compra é estável**: com 1.000 clientes únicos e 18.471 compras (notas fiscais) distintas, a média é de ~39,7 itens por compra — um "carrinho" tipicamente grande, típico de compra mensal/quinzenal de supermercado, e não de reposição pontual.
4. **A maioria dos clientes tem poucos ou nenhum filho**: a média de filhos por cliente (CL_FHL) é 1,14, mas a mediana é 0 e a moda também é 0 (527 dos 1.000 clientes não têm filhos) — a distribuição é assimétrica à direita, então a média sozinha esconde que mais da metade da base não tem filhos.
5. **2021 foi o ano de pico de vendas**: com 216.813 itens vendidos, 2021 supera os demais anos da série (2019 a 2022), o que vale a pena cruzar futuramente com fatores externos (por exemplo, mudanças de comportamento de consumo no período).
6. **Qualidade da base exigiu tratamento ativo**: 96.553 registros (11,6% do total) eram duplicatas exatas dentro da mesma nota fiscal e foram removidos, e 3.650 registros (0,44%) tinham categoria de produto não informada (`#N/D`), preenchida como "SEM CATEGORIA" — sem esse tratamento, qualquer contagem por categoria ou por compra estaria inflada ou distorcida.

## Problemas remanescentes na base

- 3.650 registros continuam sem nome de produto (`PR_NOME = '#N/D'`), pois não há como recuperar essa informação a partir dos dados disponíveis — ficam sinalizados, não removidos, para não perder o registro da venda.
- A base não tem coluna de valor monetário (preço) nem de quantidade por item, o que impede calcular ticket médio ou faturamento sem cruzar com uma tabela de preços externa.
- O item do enunciado sobre tratamento de nulos em "dimensões físicas" não se aplica a esta base específica, que não possui esse tipo de campo (detalhado no código, Sprint 3).
