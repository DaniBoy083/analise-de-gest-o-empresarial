from __future__ import annotations

import argparse
from pathlib import Path

from ev_pipeline.config import DEFAULT_OUTPUT_DIR
from ev_pipeline.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Executa pipeline de analise de dados e gera relatorio HTML/CSS/TypeScript "
            "com dashboard interativo."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretorio de saida dos artefatos web (padrao: docs/site).",
    )
    parser.add_argument(
        "--data-url",
        dest="data_url",
        type=str,
        default=None,
        help="URL externa opcional para baixar os dados (zip ou arquivos).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    # Opcional: permitir que o usuario forneca uma URL externa para os dados
    data_url = getattr(arguments, "data_url", None)
    run_pipeline(arguments.output_dir, data_url=data_url)
