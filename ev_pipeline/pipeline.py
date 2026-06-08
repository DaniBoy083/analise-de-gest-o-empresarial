"""Orquestracao da pipeline de ponta a ponta."""

from __future__ import annotations

from pathlib import Path

from .analysis import build_analysis_payload
from .data_sources import (
    build_dataset_bundle,
    prepare_favicon_asset,
    resolve_sources,
    try_download_dataset,
    try_download_from_url,
)
from .frontend_builder import build_frontend_assets
from .site_builder import write_site_assets


def run_pipeline(output_dir: Path, data_url: str | None = None) -> None:
    project_root = Path(__file__).resolve().parent.parent

    downloaded_dir = None
    dataset_origin = "arquivos_locais/docs"

    # Preferir fonte externa se informada via parametro --data-url
    if data_url:
        downloaded_dir = try_download_from_url(data_url)
        dataset_origin = data_url if downloaded_dir is not None else dataset_origin

    if downloaded_dir is None:
        downloaded_dir = try_download_dataset()
        dataset_origin = str(downloaded_dir) if downloaded_dir else dataset_origin

    sources = resolve_sources(project_root, downloaded_dir)
    payload = build_analysis_payload(sources, dataset_origin=dataset_origin)

    output_dir.mkdir(parents=True, exist_ok=True)

    build_frontend_assets(project_root, output_dir)
    bundle_path = build_dataset_bundle(sources, output_dir)
    favicon_href, favicon_type = prepare_favicon_asset(project_root, output_dir)

    write_site_assets(
        project_root=project_root,
        output_dir=output_dir,
        payload=payload,
        favicon_href=favicon_href,
        favicon_type=favicon_type,
    )

    print("\nPipeline concluida com sucesso.")
    print(f"Saida web: {output_dir / 'index.html'}")
    print(f"Arquivo para download local: {bundle_path}")
