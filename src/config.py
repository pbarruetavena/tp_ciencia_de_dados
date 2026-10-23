"""Configurações compartilhadas pelo grupo: versão da base e caminhos."""

from pathlib import Path

DATASET = "hubertsidorowicz/steam-games-dataset-daily-updates"
DATASET_VERSION = 83

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw"
DATA_PROCESSED = RAIZ / "data" / "processed"
FIGURAS = RAIZ / "reports" / "figures"
