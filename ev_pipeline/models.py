"""Modelos de dominio da pipeline."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetSources:
    carros: Path
    vendas: Path
    estacoes: Path
