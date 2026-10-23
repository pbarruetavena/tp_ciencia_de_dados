"""Baixa a versão fixada da base do Kaggle para data/raw/.

Uso (na raiz do projeto):
    python -m src.download_data
"""

import kagglehub

from src.config import DATA_RAW, DATASET, DATASET_VERSION


def main() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    caminho = kagglehub.dataset_download(
        f"{DATASET}/versions/{DATASET_VERSION}",
        output_dir=str(DATA_RAW),
    )
    print(f"Versão {DATASET_VERSION} disponível em: {caminho}")


if __name__ == "__main__":
    main()
