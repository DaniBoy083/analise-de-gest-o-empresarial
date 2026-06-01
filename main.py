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
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_pipeline(arguments.output_dir)
