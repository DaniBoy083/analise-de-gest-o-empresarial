"""Camada de entrada/saida para datasets e assets estaticos."""

from __future__ import annotations

import mimetypes
import shutil
import zipfile
from pathlib import Path

import kagglehub

from .config import DATASET_SLUG, FAVICON_EXTENSIONS
from .models import DatasetSources


def try_download_dataset() -> Path | None:
    """Baixa a versao mais recente do dataset via KaggleHub."""
    try:
        downloaded_path = Path(kagglehub.dataset_download(DATASET_SLUG))
        print(f"Dataset baixado/atualizado em: {downloaded_path}")
        return downloaded_path
    except Exception as exc:  # noqa: BLE001 - log de fallback amigavel
        print(
            "Aviso: nao foi possivel baixar do KaggleHub agora. "
            f"Usando arquivos locais. Detalhes: {exc}"
        )
        return None


def find_dataset_file(file_name: str, project_root: Path, downloaded_dir: Path | None) -> Path:
    candidates: list[Path] = []

    if downloaded_dir and downloaded_dir.exists():
        candidates.extend(downloaded_dir.rglob(file_name))

    candidates.extend(
        [
            project_root / "docs" / file_name,
            project_root / file_name,
        ]
    )

    for path in candidates:
        if path.exists():
            return path

    searched = [str(path) for path in candidates]
    raise FileNotFoundError(
        f"Arquivo obrigatorio nao encontrado: {file_name}. Locais verificados: {searched}"
    )


def resolve_sources(project_root: Path, downloaded_dir: Path | None) -> DatasetSources:
    return DatasetSources(
        carros=find_dataset_file("carros_eletricos.csv", project_root, downloaded_dir),
        vendas=find_dataset_file("monitoramento_vendas.csv", project_root, downloaded_dir),
        estacoes=find_dataset_file("charging_stations_2025_world.csv", project_root, downloaded_dir),
    )


def build_dataset_bundle(sources: DatasetSources, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = output_dir / "dataset_consumido.zip"

    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in [sources.carros, sources.vendas, sources.estacoes]:
            archive.write(source, arcname=source.name)

    return bundle_path


def resolve_favicon_source(project_root: Path) -> Path | None:
    """Busca uma imagem de favicon em public/assets e caminhos legados."""
    candidate_dirs = [
        project_root / "public" / "assets",
        project_root / "docs" / "public" / "assets",
        project_root / "docs" / "site" / "public" / "assets",
        project_root / "docs" / "site" / "publc" / "assets",
    ]

    for directory in candidate_dirs:
        if not directory.exists() or not directory.is_dir():
            continue

        files = [
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in FAVICON_EXTENSIONS
        ]
        if not files:
            continue

        files.sort(
            key=lambda path: (
                0 if "favicon" in path.stem.lower() else 1,
                path.name.lower(),
            )
        )
        return files[0]

    return None


def prepare_favicon_asset(project_root: Path, output_dir: Path) -> tuple[str | None, str | None]:
    source = resolve_favicon_source(project_root)
    if source is None:
        print("Aviso: nenhuma imagem encontrada em public/assets para favicon.")
        return None, None

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"favicon{source.suffix.lower()}"
    shutil.copy2(source, target)

    mime_type = mimetypes.guess_type(target.name)[0] or "image/png"
    return f"./{target.name}", mime_type
