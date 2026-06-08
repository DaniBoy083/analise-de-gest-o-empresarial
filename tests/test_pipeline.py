import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ev_pipeline.models import DatasetSources
from ev_pipeline.pipeline import run_pipeline


class TestPipeline(unittest.TestCase):
    def test_run_pipeline_orchestrates_layers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "docs" / "site"
            fake_sources = DatasetSources(
                carros=Path(temp_dir) / "carros_eletricos.csv",
                vendas=Path(temp_dir) / "monitoramento_vendas.csv",
                estacoes=Path(temp_dir) / "charging_stations_2025_world.csv",
            )

            with (
                patch("ev_pipeline.pipeline.try_download_dataset", return_value=None),
                patch("ev_pipeline.pipeline.resolve_sources", return_value=fake_sources) as resolve_sources_mock,
                patch("ev_pipeline.pipeline.build_analysis_payload", return_value={"meta": {}}) as build_payload_mock,
                patch("ev_pipeline.pipeline.build_dataset_bundle") as build_bundle_mock,
                patch("ev_pipeline.pipeline.build_frontend_assets", return_value=False) as frontend_build_mock,
                patch("ev_pipeline.pipeline.prepare_favicon_asset", return_value=("./favicon.png", "image/png")) as favicon_mock,
                patch("ev_pipeline.pipeline.write_site_assets") as write_site_mock,
            ):
                run_pipeline(output_dir)

            resolve_sources_mock.assert_called_once()
            build_payload_mock.assert_called_once_with(fake_sources, dataset_origin="arquivos_locais/docs")
            build_bundle_mock.assert_called_once_with(fake_sources, output_dir)
            favicon_mock.assert_called_once()
            write_site_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
