"""Baixa a versão fixada da base do Kaggle para data/raw/.

Uso (na raiz do projeto):
    python -m src.download_data
"""

from pathlib import Path

import kagglehub

from src.config import DATA_RAW, DATASET, DATASET_VERSION


def ligar_em_data_raw(origem: Path) -> None:
    """Cria em data/raw/ atalhos para os CSVs que estão em outra pasta.
    """
    for csv in origem.glob("*.csv"):
        destino = DATA_RAW / csv.name
        if destino.is_symlink():
            destino.unlink()
        if not destino.exists():
            destino.symlink_to(csv)


def main() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    caminho = Path(
        kagglehub.dataset_download(
            f"{DATASET}/versions/{DATASET_VERSION}",
            output_dir=str(DATA_RAW),
        )
    )
    if caminho.resolve() != DATA_RAW.resolve():
        ligar_em_data_raw(caminho)
    print(f"Versão {DATASET_VERSION} disponível em: {caminho}")


if __name__ == "__main__":
    main()
