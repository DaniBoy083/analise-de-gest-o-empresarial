import csv
import tempfile
import unittest
from pathlib import Path

from ev_pipeline.analysis import build_analysis_payload, parse_market_share
from ev_pipeline.models import DatasetSources


class TestAnalysis(unittest.TestCase):
    def test_parse_market_share(self) -> None:
        import pandas as pd

        values = pd.Series(["10,5%", "2", "x"])
        parsed = parse_market_share(values)

        self.assertEqual(float(parsed.iloc[0]), 10.5)
        self.assertEqual(float(parsed.iloc[1]), 2.0)
        self.assertTrue(pd.isna(parsed.iloc[2]))

    def test_build_analysis_payload_with_synthetic_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            carros = root / "carros_eletricos.csv"
            vendas = root / "monitoramento_vendas.csv"
            estacoes = root / "charging_stations_2025_world.csv"

            with carros.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.writer(fp)
                writer.writerow(["Modelo", "Fabricante", "Quantidade", "MarketShare"])
                writer.writerow(["A", "BrandX", "100", "10,0"])
                writer.writerow(["B", "BrandY", "200", "20,0"])
                writer.writerow(["C", "BrandX", "300", "30,0"])

            with vendas.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.writer(fp)
                writer.writerow(["ano", "janeiro", "fevereiro", "Total"])
                writer.writerow(["2023", "10", "20", "30"])
                writer.writerow(["2024", "30", "30", "60"])

            with estacoes.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.writer(fp)
                writer.writerow(
                    [
                        "id",
                        "city",
                        "country_code",
                        "state_province",
                        "power_kw",
                        "is_fast_dc",
                    ]
                )
                writer.writerow(["1", "Sao Paulo", "BR", "SP", "100", "True"])
                writer.writerow(["2", "Campinas", "BR", "Sao Paulo", "50", "false"])
                writer.writerow(["3", "Rio", "BR", "RJ", "150", "1"])
                writer.writerow(["4", "Boston", "US", "MA", "200", "true"])

            sources = DatasetSources(carros=carros, vendas=vendas, estacoes=estacoes)
            payload = build_analysis_payload(sources, dataset_origin="synthetic")

            self.assertEqual(payload["meta"]["dataset_origin"], "synthetic")
            self.assertEqual(payload["kpis"]["total_units"], 600)
            self.assertEqual(payload["kpis"]["top_manufacturer"], "BrandX")
            self.assertEqual(payload["kpis"]["recommended_state"], "Sao Paulo")
            self.assertEqual(payload["charts"]["yearly_sales"]["labels"], ["2023", "2024"])
            self.assertEqual(payload["charts"]["yearly_sales"]["values"], [30, 60])
            self.assertIn("Sao Paulo", payload["charts"]["state_stations"]["labels"])


if __name__ == "__main__":
    unittest.main()
