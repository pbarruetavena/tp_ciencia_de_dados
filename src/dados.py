"""Leitura da base. Use estas funções nos notebooks em vez de ler o CSV direto."""

import pandas as pd

from src.config import DATA_RAW


def carregar_csv(nome: str) -> pd.DataFrame:
    """Lê data/raw/<nome>.csv.
    Gera um parquet para utilizar em proximas leituras.
    """
    parquet = DATA_RAW / f"{nome}.parquet"
    if parquet.exists():
        return pd.read_parquet(parquet)

    csv = DATA_RAW / f"{nome}.csv"
    if not csv.exists():
        raise FileNotFoundError(
            f"{csv} não encontrado. Rode antes: python -m src.download_data"
        )
    df = pd.read_csv(csv, low_memory=False)
    df.to_parquet(parquet, index=False)
    return df


def carregar_jogos() -> pd.DataFrame:
    return carregar_csv("steam_games")


def carregar_reviews() -> pd.DataFrame:
    return carregar_csv("steam_games_reviews")
