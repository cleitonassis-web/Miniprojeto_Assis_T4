"""
Mini-Projeto Avaliativo - Manipulacao de Dados com Python e SQL
Modulo 1 - Semana 07 | Turma: T4
Aluno: Assis

Analise Exploratoria de Dados (AED) da base "Varejo" (varejo/supermercado),
disponivel em: https://www.kaggle.com/datasets/namespaiva/base-varejo

Como executar:
    python3 analise_varejo.py
(o CSV original deve estar em data/Varejo.csv, na mesma pasta deste script)

O script segue os 6 sprints do desafio proposto no enunciado e imprime,
em cada etapa, as evidencias pedidas pela rubrica de avaliacao.
"""

import csv
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "Varejo.csv"
CSV_LIMPO_PATH = BASE_DIR / "data" / "Varejo_limpo.csv"

# Dicionario de dados da base "Varejo" (documentado a partir do material do curso)
DICIONARIO_CAMPOS = {
    "DATA": "Data da compra",
    "CO_ID": "Identificacao do numero de compra (numero da nota fiscal)",
    "CL_ID": "Identificacao do cliente (numero do cliente)",
    "CL_GENERO": "Sexo biologico informado pelo cliente (M/F)",
    "CL_EC": "Estado civil do cliente (1-Casado/uniao estavel, 2-Divorciado, "
             "3-Separado, 4-Solteiro, 5-Viuvo)",
    "CL_FHL": "Numero de filhos do cliente",
    "CL_SEG": "Segmentacao economica do cliente (classe A, B ou C)",
    "PR_ID": "Codigo do produto (SKU) adquirido",
    "PR_CAT": "Categoria do produto adquirido",
    "PR_NOME": "Nome do produto adquirido",
}

# Colunas de dados reais (o CSV exportado do Kaggle traz 4 colunas extras
# vazias no final, sem cabecalho e sem nenhum valor preenchido em nenhuma
# linha - foram checadas e descartadas na importacao)
COLUNAS_VALIDAS = list(DICIONARIO_CAMPOS.keys())


def linha(titulo: str) -> None:
    print("\n" + "=" * 78)
    print(titulo)
    print("=" * 78)


def fmt_num(valor) -> str:
    """Formata um numero com separador de milhar no padrao brasileiro (ponto),
    sem afetar virgulas de pontuacao do texto ao redor."""
    return f"{valor:,}".replace(",", ".")


# ---------------------------------------------------------------------------
# SPRINT 1 - IMPORTACAO DE DADOS
# ---------------------------------------------------------------------------
def sprint1_importacao() -> pd.DataFrame:
    linha("SPRINT 1 - IMPORTACAO DE DADOS")

    df = pd.read_csv(
        CSV_PATH,
        sep=";",
        usecols=range(len(COLUNAS_VALIDAS)),
        dtype=str,
        encoding="utf-8",
    )
    df.columns = COLUNAS_VALIDAS

    print(f"Total de registros importados: {fmt_num(len(df))}")
    print(f"Total de colunas: {df.shape[1]}")
    print("\nColunas e tipos de dados (bruto, tudo lido como texto nesta etapa):")
    print(df.dtypes)

    print("\nAmostra das 5 primeiras linhas:")
    print(df.head(5).to_string())

    return df


def sprint1b_leitura_nativa_csv(n_amostra: int = 5) -> None:
    """Leitura estruturada e nativa do arquivo usando csv.DictReader,
    sem depender do pandas - atende ao criterio 3 da rubrica
    (Manipulacao de Arquivos CSV)."""
    linha("SPRINT 1b - LEITURA NATIVA COM csv.DictReader")

    total = 0
    amostra = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f, delimiter=";")
        # Mantem so os 10 campos validos, descartando as 4 colunas vazias
        campos_originais = leitor.fieldnames[: len(COLUNAS_VALIDAS)]
        for i, linha_dict in enumerate(leitor):
            total += 1
            if i < n_amostra:
                registro = {
                    campo: linha_dict[campo] for campo in campos_originais
                }
                amostra.append(registro)

    print(f"Registros lidos via csv.DictReader: {fmt_num(total)}")
    print(f"Campos identificados: {campos_originais}")
    print("\nAmostra (primeiros registros como dicionario):")
    for registro in amostra:
        print(registro)


# ---------------------------------------------------------------------------
# SPRINT 2 - TRANSFORMACAO DE TIPOS DE DADOS
# ---------------------------------------------------------------------------
def limpar_texto(valor: str) -> str:
    """Remove espacos extras nas bordas e colapsa espacos internos
    duplicados usando expressao regular."""
    if pd.isna(valor):
        return valor
    valor = re.sub(r"\s+", " ", str(valor)).strip()
    return valor.upper()


def sprint2_transformacao(df: pd.DataFrame) -> pd.DataFrame:
    linha("SPRINT 2 - TRANSFORMACAO DE TIPOS DE DADOS")
    df = df.copy()

    # --- limpeza de strings (texto) ---
    colunas_texto = ["CL_GENERO", "CL_SEG", "PR_CAT", "PR_NOME"]
    for col in colunas_texto:
        df[col] = df[col].map(limpar_texto)

    # --- conversao de inteiros ---
    colunas_inteiras = ["CO_ID", "CL_ID", "CL_EC", "CL_FHL", "PR_ID"]
    for col in colunas_inteiras:
        # regex para garantir que sobrou so digitos antes de converter
        df[col] = df[col].astype(str).str.extract(r"(\d+)")[0]
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # --- conversao de data (string -> datetime) ---
    df["DATA"] = pd.to_datetime(df["DATA"], format="%d/%m/%Y", errors="coerce")

    print("Tipos de dados apos a conversao:")
    print(df.dtypes)

    print(f"\nDatas invalidas apos conversao: {df['DATA'].isna().sum()}")
    print(f"Periodo coberto pela base: {df['DATA'].min().date()} a {df['DATA'].max().date()}")

    print(f"\nValores nao numericos apos conversao das colunas inteiras:")
    for col in colunas_inteiras:
        print(f"  {col}: {df[col].isna().sum()} valor(es) nao numerico(s)")

    return df


# ---------------------------------------------------------------------------
# SPRINT 3 - LIMPEZA DE NULOS E DUPLICATAS
# ---------------------------------------------------------------------------
def sprint3_limpeza(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    linha("SPRINT 3 - LIMPEZA DE NULOS, INCONSISTENCIAS E DUPLICATAS")
    df = df.copy()
    relatorio: dict = {}

    # 1) valores nulos reais (NaN) por coluna
    print("1) Valores nulos (NaN) por coluna:")
    nulos = df.isnull().sum()
    print(nulos)
    relatorio["nulos_por_coluna"] = nulos.to_dict()

    # 2) categorias marcadas como ausentes com o codigo "#N/D"
    marcador_ausente = df["PR_CAT"] == "#N/D"
    qtd_ausente = int(marcador_ausente.sum())
    print(f"\n2) Registros com categoria de produto ausente ('#N/D'): {qtd_ausente}")

    # Preenchimento com if/else, conforme pedido no enunciado
    def preencher_categoria(valor: str) -> str:
        if valor == "#N/D" or pd.isna(valor) or valor.strip() == "":
            return "SEM CATEGORIA"
        else:
            return valor

    df["PR_CAT"] = df["PR_CAT"].map(preencher_categoria)
    print("   -> Preenchidas com 'SEM CATEGORIA' via logica if/else.")
    relatorio["categorias_preenchidas"] = qtd_ausente

    # O nome do produto tambem vem como "#N/D" nesses mesmos registros;
    # como nao ha como recuperar o nome real, isso fica documentado como
    # problema remanescente da base (ver Sprint 5 / README).
    qtd_nome_ausente = int((df["PR_NOME"] == "#N/D").sum())
    relatorio["produtos_sem_nome"] = qtd_nome_ausente
    print(f"   Nome do produto tambem ausente nesses casos: {qtd_nome_ausente} "
          f"(mantido como '#N/D' - nao ha forma de inferir o nome real; "
          f"reportado como problema remanescente).")

    # 3) "dimensoes fisicas" (peso/tamanho): a base Varejo NAO possui nenhuma
    # coluna de dimensao fisica/peso de produto (ver dicionario de campos).
    # Verificacao feita e documentada explicitamente, em vez de aplicar um
    # tratamento generico que nao se encaixaria nesta base.
    print("\n3) Verificacao de colunas de dimensao fisica/peso: nao existem "
          "colunas desse tipo na base Varejo (10 campos: DATA, CO_ID, CL_ID, "
          "CL_GENERO, CL_EC, CL_FHL, CL_SEG, PR_ID, PR_CAT, PR_NOME) - "
          "item do enunciado nao aplicavel a este dataset especifico.")
    relatorio["colunas_dimensao_fisica"] = "nao aplicavel - nao existem no dataset"

    # 4) duplicatas - regra de negocio: duas linhas so sao consideradas
    # duplicadas de fato quando TODOS os campos coincidem, incluindo o
    # identificador da compra (CO_ID). Ou seja, a mesma comparacao ja
    # respeita a separacao por numero de compra pedida no enunciado.
    duplicadas = df.duplicated(keep="first")
    qtd_duplicadas = int(duplicadas.sum())
    print(f"\n4) Registros totalmente duplicados (mesma compra CO_ID + mesmo "
          f"produto + mesmos dados de cliente): {qtd_duplicadas}")
    print("   Justificativa: cada linha representa um item comprado; como a "
          "base nao tem coluna de quantidade, duas linhas identicas dentro "
          "da MESMA nota fiscal (CO_ID) sao tratadas como duplicidade de "
          "lancamento e removidas, mantendo a primeira ocorrencia.")

    antes = len(df)
    df = df[~duplicadas].reset_index(drop=True)
    depois = len(df)
    relatorio["duplicadas_removidas"] = qtd_duplicadas
    relatorio["linhas_antes"] = antes
    relatorio["linhas_depois"] = depois
    print(f"   Registros antes: {fmt_num(antes)} | depois: {fmt_num(depois)}")

    return df, relatorio


# ---------------------------------------------------------------------------
# SPRINT 3b - PADROES DE AGRUPAMENTO
# ---------------------------------------------------------------------------
def sprint3b_agrupamentos(df: pd.DataFrame) -> dict:
    linha("SPRINT 3b - PADROES DE AGRUPAMENTO (groupby / pivot_table)")
    resultados = {}

    print("Combinacao 1) Quantidade de itens vendidos por genero do cliente:")
    por_genero = df.groupby("CL_GENERO").size().sort_values(ascending=False)
    print(por_genero)
    resultados["itens_por_genero"] = por_genero

    print("\nCombinacao 2) Quantidade de itens vendidos por categoria de produto:")
    por_categoria = (
        df.groupby("PR_CAT").size().sort_values(ascending=False)
    )
    print(por_categoria)
    resultados["itens_por_categoria"] = por_categoria

    print("\nCombinacao 3) Tabela dinamica: segmento economico (CL_SEG) x "
          "categoria de produto (PR_CAT), contagem de itens:")
    pivot_seg_cat = pd.pivot_table(
        df, index="CL_SEG", columns="PR_CAT", values="PR_ID",
        aggfunc="count", fill_value=0,
    )
    print(pivot_seg_cat)
    resultados["pivot_segmento_categoria"] = pivot_seg_cat

    print("\nCombinacao 4) Analise temporal: itens vendidos por ano:")
    por_ano = df.groupby(df["DATA"].dt.year).size()
    print(por_ano)
    resultados["itens_por_ano"] = por_ano

    return resultados


# ---------------------------------------------------------------------------
# SPRINT 4 - ESTATISTICAS DESCRITIVAS (coluna CL_FHL - numero de filhos)
# ---------------------------------------------------------------------------
def sprint4_estatisticas(df: pd.DataFrame) -> dict:
    linha("SPRINT 4 - ESTATISTICAS DESCRITIVAS: CL_FHL (numero de filhos do cliente)")

    # Estatistica e por cliente, nao por linha de item comprado - cada
    # cliente aparece em varias linhas, entao usamos os valores unicos
    # por cliente (CL_ID) para nao inflar a media com clientes que
    # compraram mais vezes.
    fhl_por_cliente = df.drop_duplicates(subset=["CL_ID"])["CL_FHL"].astype("Int64")

    estatisticas = {
        "media": fhl_por_cliente.mean(),
        "mediana": fhl_por_cliente.median(),
        "desvio_padrao": fhl_por_cliente.std(),
        "moda": fhl_por_cliente.mode().tolist(),
        "maximo": fhl_por_cliente.max(),
        "minimo": fhl_por_cliente.min(),
        "contagem": fhl_por_cliente.count(),
        "q1": fhl_por_cliente.quantile(0.25),
        "q2_mediana": fhl_por_cliente.quantile(0.50),
        "q3": fhl_por_cliente.quantile(0.75),
    }

    print(f"Base de calculo: {estatisticas['contagem']} clientes unicos "
          f"(1 valor de CL_FHL por cliente, para nao repetir o mesmo "
          f"cliente a cada item comprado)")
    print(f"Media:          {estatisticas['media']:.3f}")
    print(f"Mediana:        {estatisticas['mediana']:.3f}")
    print(f"Desvio padrao:  {estatisticas['desvio_padrao']:.3f}")
    print(f"Moda:           {estatisticas['moda']}")
    print(f"Maximo:         {estatisticas['maximo']}")
    print(f"Minimo:         {estatisticas['minimo']}")
    print(f"Q1 (25%):       {estatisticas['q1']}")
    print(f"Q2/Mediana(50%):{estatisticas['q2_mediana']}")
    print(f"Q3 (75%):       {estatisticas['q3']}")

    print("\nResumo via describe():")
    print(fhl_por_cliente.describe())

    print("\nDistribuicao de frequencia (numero de clientes por qtd. de filhos):")
    print(fhl_por_cliente.value_counts().sort_index())

    return estatisticas


# ---------------------------------------------------------------------------
# SPRINT 5 - RELATORIO / INSIGHTS
# ---------------------------------------------------------------------------
def sprint5_insights(df: pd.DataFrame, relatorio_limpeza: dict,
                      agrupamentos: dict, estatisticas: dict) -> str:
    linha("SPRINT 5 - RELATORIO DE CONCLUSOES E INSIGHTS")

    categoria_top = agrupamentos["itens_por_categoria"].idxmax()
    categoria_top_qtd = int(agrupamentos["itens_por_categoria"].max())
    genero_top = agrupamentos["itens_por_genero"].idxmax()
    genero_top_qtd = int(agrupamentos["itens_por_genero"].max())
    total_clientes = df["CL_ID"].nunique()
    total_compras = df["CO_ID"].nunique()
    ano_pico = agrupamentos["itens_por_ano"].idxmax()
    ano_pico_qtd = int(agrupamentos["itens_por_ano"].max())

    insights = [
        f"1. A categoria de produto com mais itens vendidos e '{categoria_top}', "
        f"com {fmt_num(categoria_top_qtd)} itens registrados, o que indica ser o "
        f"carro-chefe do mix de produtos da rede.",

        f"2. O genero '{genero_top}' concentra a maior parte das compras "
        f"({fmt_num(genero_top_qtd)} itens de um total de {fmt_num(len(df))}), sugerindo "
        f"que campanhas de marketing podem priorizar esse publico sem "
        f"deixar de atender o outro.",

        f"3. A base cobre {total_clientes} clientes unicos e {fmt_num(total_compras)} "
        f"compras (notas fiscais) distintas, com media de "
        f"{len(df)/total_compras:.1f} itens por compra.",

        f"4. O numero de filhos por cliente (CL_FHL) tem media de "
        f"{estatisticas['media']:.2f} e mediana de {estatisticas['mediana']:.0f}, "
        f"com moda em {estatisticas['moda']} - a maior parte da base e "
        f"formada por clientes com poucos ou nenhum filho, o que pode "
        f"orientar o mix de produtos infantis.",

        f"5. {ano_pico} foi o ano com mais itens vendidos ({fmt_num(ano_pico_qtd)} "
        f"itens), o que pode ser cruzado futuramente com sazonalidade e "
        f"eventos de venda.",

        f"6. Qualidade dos dados: foram encontrados e tratados "
        f"{fmt_num(relatorio_limpeza['duplicadas_removidas'])} registros duplicados "
        f"e {fmt_num(relatorio_limpeza['categorias_preenchidas'])} categorias de "
        f"produto ausentes ('#N/D'), preenchidas como 'SEM CATEGORIA'.",
    ]

    print("\n".join(insights))

    problemas_remanescentes = [
        f"- {relatorio_limpeza['produtos_sem_nome']} registros continuam sem "
        f"nome de produto (PR_NOME = '#N/D'), pois nao ha forma de recuperar "
        f"essa informacao a partir dos dados disponiveis.",
        "- A base nao possui coluna de valor monetario/preco nem de "
        "quantidade por item, o que limita analises financeiras (ticket "
        "medio, faturamento) sem cruzamento com uma tabela de precos externa.",
        "- O item do enunciado sobre tratamento de nulos em 'dimensoes "
        "fisicas' nao se aplica a esta base, que nao possui esse tipo de "
        "campo (ver Sprint 3).",
    ]
    print("\nProblemas remanescentes na base:")
    print("\n".join(problemas_remanescentes))

    return "\n".join(insights) + "\n\nProblemas remanescentes:\n" + "\n".join(problemas_remanescentes)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    df_bruto = sprint1_importacao()
    sprint1b_leitura_nativa_csv()
    df_tipado = sprint2_transformacao(df_bruto)
    df_limpo, relatorio_limpeza = sprint3_limpeza(df_tipado)
    agrupamentos = sprint3b_agrupamentos(df_limpo)
    estatisticas = sprint4_estatisticas(df_limpo)
    sprint5_insights(df_limpo, relatorio_limpeza, agrupamentos, estatisticas)

    # Exportacao opcional do dataframe limpo
    df_export = df_limpo.copy()
    df_export["DATA"] = df_export["DATA"].dt.strftime("%d/%m/%Y")
    df_export.to_csv(CSV_LIMPO_PATH, sep=";", index=False, encoding="utf-8")
    linha("EXPORTACAO")
    print(f"Dataframe limpo exportado para: {CSV_LIMPO_PATH}")
    print(f"Linhas exportadas: {fmt_num(len(df_export))}")


if __name__ == "__main__":
    main()
