"""Limpeza da base de jogos: gera as colunas usadas nas perguntas de pesquisa.

Uso nos notebooks:
    from src.dados import carregar_jogos
    from src.limpeza import limpar
    jogos = limpar(carregar_jogos())

Decisões (conferidas na versão 83 da base):
- `estimated_owners` vem em dois formatos ("0 - 20000" e "0 .. 20,000"), que
  são unificados. "0 - 0" vira NaN: nenhum desses jogos tem review, então
  tratamos como falta de dado do SteamSpy.
- Tempo jogado igual a 0 vira NaN: 93% da base tem 0, inclusive ~70% dos jogos
  com 100+ reviews, então o zero indica falta de dado, não jogo sem jogadores.
- Preço de jogos "unavailable" fica NaN. Outliers de preço não são removidos
  aqui; use `filtrar_iqr` na análise que precisar.
"""

import json
import re

import numpy as np
import pandas as pd

COLUNAS_LISTA = ["genres", "categories", "tags", "developers", "publishers"]
COLUNAS_TEMPO = ["average_playtime_forever", "median_playtime_forever"]
N_GENEROS_DUMMIES = 10


def limpar(df: pd.DataFrame) -> pd.DataFrame:
    """Devolve uma cópia da base com tipos corrigidos e colunas derivadas."""
    df = df.copy()
    _listas(df)
    _owners(df)
    _reviews(df)
    _datas(df)
    _preco(df)
    _tempo_jogado(df)
    _plataformas(df)
    _dummies_generos(df)

    df["log_price"] = np.log1p(df["price"])
    df["log_reviews"] = np.log1p(df["total_reviews"])
    df["log_playtime"] = np.log1p(df["average_playtime_forever"])
    df["log_owners"] = np.log1p(df["owners_mid"])
    return df


def filtrar_iqr(
    df: pd.DataFrame, coluna: str, k: float = 1.5
) -> tuple[pd.DataFrame, int]:
    """Mantém as linhas com `coluna` dentro de [Q1 - k*IQR, Q3 + k*IQR].

    Devolve o df filtrado e quantos outliers foram removidos. Linhas com NaN na
    coluna também saem, mas não entram na contagem de outliers.
    """
    q1, q3 = df[coluna].quantile([0.25, 0.75])
    iqr = q3 - q1
    dentro = df[coluna].between(q1 - k * iqr, q3 + k * iqr)
    outliers = int((df[coluna].notna() & ~dentro).sum())
    return df[dentro], outliers


def com_reviews_minimas(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Jogos com pelo menos `n` reviews, para a taxa positiva não ser ruído."""
    return df[df["total_reviews"] >= n]


def _listas(df: pd.DataFrame) -> None:
    def converter(texto):
        if not isinstance(texto, str):
            return []
        itens = json.loads(texto)
        return [i["description"] if isinstance(i, dict) else i for i in itens]

    for coluna in COLUNAS_LISTA:
        df[coluna] = df[coluna].map(converter)


def _owners(df: pd.DataFrame) -> None:
    limites = (
        df["estimated_owners"]
        .str.replace(",", "")
        .str.extract(r"^(\d+)\s*(?:-|\.\.)\s*(\d+)$")
        .astype(float)
    )
    sem_dado = limites[1] == 0
    df["owners_min"] = limites[0].mask(sem_dado)
    df["owners_max"] = limites[1].mask(sem_dado)
    df["owners_mid"] = (df["owners_min"] + df["owners_max"]) / 2

    faixas = (
        df[["owners_min", "owners_max"]]
        .dropna()
        .drop_duplicates()
        .sort_values("owners_min")
    )
    rotulos = [f"{int(a):,} - {int(b):,}" for a, b in faixas.itertuples(index=False)]
    df["owners_faixa"] = pd.Categorical(
        [
            f"{int(a):,} - {int(b):,}" if pd.notna(a) else None
            for a, b in zip(df["owners_min"], df["owners_max"])
        ],
        categories=rotulos,
        ordered=True,
    )


def _reviews(df: pd.DataFrame) -> None:
    df["total_reviews"] = df["positive"] + df["negative"]
    df["taxa_positiva"] = df["positive"] / df["total_reviews"].replace(0, np.nan)


def _datas(df: pd.DataFrame) -> None:
    df["release_date"] = pd.to_datetime(
        df["release_date"], format="%Y-%m-%d", errors="coerce"
    )
    df["ano"] = df["release_date"].dt.year.astype("Int64")
    df["mes"] = df["release_date"].dt.month.astype("Int64")
    df["trimestre"] = df["release_date"].dt.quarter.astype("Int64")
    referencia = df["release_date"].max()
    df["idade_dias"] = (referencia - df["release_date"]).dt.days.astype("Int64")


def _preco(df: pd.DataFrame) -> None:
    df["gratuito"] = (
        df["price_status"].map({"free": True, "paid": False}).astype("boolean")
    )


def _tempo_jogado(df: pd.DataFrame) -> None:
    for coluna in COLUNAS_TEMPO:
        df[coluna] = df[coluna].replace(0, np.nan)


def _plataformas(df: pd.DataFrame) -> None:
    for coluna in ["windows", "mac", "linux"]:
        df[coluna] = df[coluna].astype("boolean")


def _dummies_generos(df: pd.DataFrame) -> None:
    contagem = df["genres"].explode().value_counts()
    for genero in contagem.index[:N_GENEROS_DUMMIES]:
        nome = re.sub(r"[^a-z0-9]+", "_", genero.lower()).strip("_")
        df[f"genero_{nome}"] = df["genres"].map(lambda gs, g=genero: g in gs)
