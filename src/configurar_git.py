"""Configura o filtro do nbstripout neste clone do repositório.

Precisa ser rodado uma vez por pessoa, com o .venv ativado:
    python -m src.configurar_git
"""

import subprocess
import sys
from pathlib import Path

from src.config import RAIZ


def git_config(chave: str, valor: str) -> None:
    subprocess.run(["git", "config", chave, valor], cwd=RAIZ, check=True)


def main() -> None:
    python = Path(sys.executable).as_posix()
    git_config("filter.nbstripout.clean", f'"{python}" -m nbstripout')
    git_config("filter.nbstripout.smudge", "cat")
    git_config("filter.nbstripout.required", "true")
    print("Filtro nbstripout configurado (regras em .gitattributes).")


if __name__ == "__main__":
    main()
