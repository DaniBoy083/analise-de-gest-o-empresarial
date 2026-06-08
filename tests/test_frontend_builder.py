import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ev_pipeline.frontend_builder import build_frontend_assets


class TestFrontendBuilder(unittest.TestCase):
    def test_build_frontend_assets_uses_esbuild_when_package_json_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "package.json").write_text("{}", encoding="utf-8")
            web_src = root / "web_src"
            web_src.mkdir(parents=True)
            (web_src / "dashboard.ts").write_text("console.log('ok');", encoding="utf-8")

            output_dir = root / "docs" / "site"
            output_dir.mkdir(parents=True)

            def fake_run(command, cwd, check):
                (output_dir / "dashboard.js").write_text("console.log('compiled');", encoding="utf-8")
                return subprocess.CompletedProcess(command, 0)

            with patch("ev_pipeline.frontend_builder.subprocess.run", side_effect=fake_run) as run_mock:
                result = build_frontend_assets(root, output_dir)

            self.assertTrue(result)
            run_mock.assert_called_once()
            self.assertTrue((output_dir / "dashboard.js").exists())

    def test_build_frontend_assets_returns_false_without_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            web_src = root / "web_src"
            web_src.mkdir(parents=True)
            (web_src / "dashboard.ts").write_text("console.log('ok');", encoding="utf-8")
            output_dir = root / "docs" / "site"
            output_dir.mkdir(parents=True)

            self.assertFalse(build_frontend_assets(root, output_dir))


if __name__ == "__main__":
    unittest.main()
