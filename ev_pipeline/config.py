"""Constantes de configuracao da pipeline."""

from pathlib import Path

DATASET_SLUG = "nathanrocha/recarga-de-veculos-eltricos-brasil"
KAGGLE_URL = "https://www.kaggle.com/datasets/nathanrocha/recarga-de-veculos-eltricos-brasil"
KAGGLE_DOWNLOAD_URL = (
    "https://www.kaggle.com/datasets/nathanrocha/recarga-de-veculos-eltricos-brasil"
    "?resource=download"
)

DEFAULT_OUTPUT_DIR = Path("docs") / "site"
FAVICON_EXTENSIONS = {".png", ".ico", ".svg", ".jpg", ".jpeg", ".webp"}
