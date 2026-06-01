"""Orquestracao da pipeline de ponta a ponta."""

from __future__ import annotations

from pathlib import Path

from .analysis import build_analysis_payload
from .data_sources import (
    build_dataset_bundle,
    prepare_favicon_asset,
    resolve_sources,
    try_download_dataset,
)
from .site_builder import write_site_assets


def run_pipeline(output_dir: Path) -> None:
    project_root = Path(__file__).resolve().parent.parent

    downloaded_dir = try_download_dataset()
    dataset_origin = str(downloaded_dir) if downloaded_dir else "arquivos_locais/docs"

    sources = resolve_sources(project_root, downloaded_dir)
    payload = build_analysis_payload(sources, dataset_origin=dataset_origin)

    output_dir.mkdir(parents=True, exist_ok=True)

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
