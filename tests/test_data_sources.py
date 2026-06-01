import tempfile
import unittest
import zipfile
from pathlib import Path

from ev_pipeline.data_sources import (
    build_dataset_bundle,
    find_dataset_file,
    prepare_favicon_asset,
    resolve_favicon_source,
)
from ev_pipeline.models import DatasetSources


class TestDataSources(unittest.TestCase):
    def test_resolve_and_prepare_favicon_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "public" / "assets"
            assets.mkdir(parents=True)
            (assets / "logo.png").write_bytes(b"png-bytes")

            output_dir = root / "docs" / "site"
            output_dir.mkdir(parents=True)

            source = resolve_favicon_source(root)
            self.assertEqual(source, assets / "logo.png")

            href, mime = prepare_favicon_asset(root, output_dir)
            self.assertEqual(href, "./favicon.png")
            self.assertEqual(mime, "image/png")
            self.assertTrue((output_dir / "favicon.png").exists())

    def test_find_dataset_file_uses_docs_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_dir = root / "docs"
            docs_dir.mkdir(parents=True)
            expected = docs_dir / "carros_eletricos.csv"
            expected.write_text("x", encoding="utf-8")

            found = find_dataset_file("carros_eletricos.csv", root, downloaded_dir=None)
            self.assertEqual(found, expected)

    def test_build_dataset_bundle_creates_zip_with_all_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_dir = root / "out"
            output_dir.mkdir(parents=True)

            carros = root / "carros_eletricos.csv"
            vendas = root / "monitoramento_vendas.csv"
            estacoes = root / "charging_stations_2025_world.csv"

            carros.write_text("a", encoding="utf-8")
            vendas.write_text("b", encoding="utf-8")
            estacoes.write_text("c", encoding="utf-8")

            sources = DatasetSources(carros=carros, vendas=vendas, estacoes=estacoes)
            bundle = build_dataset_bundle(sources, output_dir)

            self.assertTrue(bundle.exists())
            with zipfile.ZipFile(bundle, "r") as zf:
                names = set(zf.namelist())
            self.assertEqual(
                names,
                {
                    "carros_eletricos.csv",
                    "monitoramento_vendas.csv",
                    "charging_stations_2025_world.csv",
                },
            )


if __name__ == "__main__":
    unittest.main()
