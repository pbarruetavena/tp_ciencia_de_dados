# tp_ciencia_de_dados

Trabalho de Introdução à Ciência de Dados com a base
[Steam Games Dataset (daily updates)](https://www.kaggle.com/datasets/hubertsidorowicz/steam-games-dataset-daily-updates),
com dados de ~144 mil jogos da Steam.

- **GitHub** (este repositório): onde o grupo desenvolve e versiona o código.
- **Kaggle/Colab**: vitrine, onde publicamos o notebook final.

## Versão da base

A base é atualizada **todo dia** no Kaggle. Para que todos analisem os mesmos
dados, usamos uma versão fixa, definida em [`src/config.py`](src/config.py)
(`DATASET_VERSION`, atualmente **83**).

Arquivos da base:

| Arquivo | Tamanho | Conteúdo |
|---|---|---|
| `steam_games.csv` | ~1 GB | metadados, preço, gêneros, avaliações, tempo de jogo... (42 colunas) |
| `steam_games_reviews.csv` | ~5 MB | até 100 reviews em inglês por jogo (JSON); junta pelo `app_id` |

## Estrutura

```
├── data/                  
│   ├── raw/               #   CSVs originais + cópia em Parquet
│   └── processed/         #   bases limpas geradas pelo grupo
├── notebooks/
│   ├── exploracao/        # rascunhos
│   └── final/             # notebooks apresentáveis
├── reports/figures/       # gráficos salvos 
├── src/
│   ├── config.py          # versão da base e caminhos
│   ├── dados.py           # carregar_jogos(), carregar_reviews()
│   ├── limpeza.py         # limpar(), filtrar_iqr(), com_reviews_minimas()
│   ├── download_data.py   # baixa a base do Kaggle
│   └── configurar_git.py  # configura o nbstripout
└── requirements.txt
```

## Primeira configuração

Precisa de Python 3.11 ou mais novo. Rode na raiz do projeto:

```bash
# 1. Ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 2. Dependências
pip install -r requirements.txt

# 3. Filtro que limpa os outputs dos rascunhos no commit 
python -m src.configurar_git

# 4. Baixar a base (~1 GB, não precisa de conta no Kaggle)
python -m src.download_data
```

No VS Code/Jupyter, selecione o kernel do `.venv`.

## Usando os dados nos notebooks

Comece copiando `notebooks/exploracao/00_modelo.ipynb`. O essencial é:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parents[1]))   # permite importar src/

from src.dados import carregar_jogos, carregar_reviews
jogos = carregar_jogos()
```

A primeira leitura demora um pouco porque salva uma cópia em Parquet. As
seguintes levam poucos segundos.

Código que mais de uma pessoa usa (limpeza, novas colunas) vai para `src/`,
não fica copiado entre notebooks.

## Abrindo no Google Colab

Qualquer notebook do repositório abre no Colab trocando o começo do link:

```
https://github.com/pbarruetavena/tp_ciencia_de_dados/blob/main/<caminho>.ipynb
→ https://colab.research.google.com/github/pbarruetavena/tp_ciencia_de_dados/blob/main/<caminho>.ipynb
```

O Colab abre só o notebook, sem `src/` e sem os dados. Coloque esta célula no
início (ela só roda no Colab; localmente é ignorada):

```python
import os, sys
if "google.colab" in sys.modules:
    # Caminho absoluto: rodar a célula de novo não cria clones aninhados
    REPO = "/content/tp_ciencia_de_dados"
    if not os.path.exists(REPO):
        !git clone -q https://github.com/pbarruetavena/tp_ciencia_de_dados.git {REPO}
    else:
        !git -C {REPO} pull -q --ff-only
    %cd {REPO}
    !pip install -q kagglehub
    !python -m src.download_data
    sys.path.insert(0, REPO)
```

- O download (~1 GB) precisa ser refeito a cada sessão nova do Colab.
- Não instale o `requirements.txt` inteiro no Colab: ele já tem pandas,
  matplotlib, seaborn, scipy e statsmodels, e trocar as versões costuma exigir
  reiniciar a sessão.
