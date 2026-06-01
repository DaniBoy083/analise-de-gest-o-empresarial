import tempfile
import unittest
from pathlib import Path

from ev_pipeline.site_builder import render_index_html, write_site_assets


class TestSiteBuilder(unittest.TestCase):
    def test_render_index_html_injects_placeholders(self) -> None:
        template = "{{FAVICON_LINKS}}\n{{EMBEDDED_ANALYSIS_JSON}}\n{{CHART_SCRIPT_TAG}}"
        rendered = render_index_html(
            template_html=template,
            embedded_analysis_json='{"ok": true}',
            favicon_href="./favicon.png",
            favicon_type="image/png",
            include_chart_script=True,
        )

        self.assertIn('rel="icon"', rendered)
        self.assertIn('{"ok": true}', rendered)
        self.assertIn('chart.umd.min.js', rendered)

    def test_write_site_assets_writes_files_and_cleans_legacy_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            web_src = root / "web_src"
            web_src.mkdir(parents=True)

            (web_src / "index.template.html").write_text(
                "{{FAVICON_LINKS}}\n{{EMBEDDED_ANALYSIS_JSON}}\n{{CHART_SCRIPT_TAG}}",
                encoding="utf-8",
            )
            (web_src / "styles.css").write_text("body{}", encoding="utf-8")
            (web_src / "dashboard.ts").write_text("console.log('ok');", encoding="utf-8")
            (web_src / "chart.umd.min.js").write_text("/* chart */", encoding="utf-8")

            output = root / "docs" / "site"
            legacy_dir = output / "publc"
            legacy_dir.mkdir(parents=True)
            (legacy_dir / "old.txt").write_text("x", encoding="utf-8")

            write_site_assets(
                project_root=root,
                output_dir=output,
                payload={"hello": "world"},
                favicon_href="./favicon.png",
                favicon_type="image/png",
            )

            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "styles.css").exists())
            self.assertTrue((output / "dashboard.ts").exists())
            self.assertTrue((output / "dashboard.js").exists())
            self.assertTrue((output / "analysis.json").exists())
            self.assertTrue((output / "chart.umd.min.js").exists())
            self.assertFalse(legacy_dir.exists())


if __name__ == "__main__":
    unittest.main()
