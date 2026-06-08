"""Build do frontend TypeScript usando esbuild."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _find_esbuild_executable(project_root: Path) -> Path | None:
    candidate_dir = project_root / "node_modules" / ".bin"
    for executable in ["esbuild.cmd", "esbuild.exe", "esbuild"]:
        path = candidate_dir / executable
        if path.exists():
            return path
    return None


def build_frontend_assets(project_root: Path, output_dir: Path) -> bool:
    source_ts = project_root / "web_src" / "dashboard.ts"
    if not source_ts.exists():
        return False
    if not (project_root / "package.json").exists():
        return False

    output_dashboard_js = output_dir / "dashboard.js"
    esbuild_path = _find_esbuild_executable(project_root)
    command = []

    if esbuild_path is not None:
        command = [
            str(esbuild_path),
            str(source_ts),
            "--bundle",
            "--platform=browser",
            f"--outfile={output_dashboard_js}",
            "--sourcemap",
            "--minify",
        ]
    else:
        command = [
            "npm",
            "exec",
            "--no-install",
            "esbuild",
            str(source_ts),
            "--bundle",
            "--platform=browser",
            f"--outfile={output_dashboard_js}",
            "--sourcemap",
            "--minify",
        ]

    try:
        subprocess.run(command, cwd=project_root, check=True)
    except FileNotFoundError:
        print("Aviso: npm nao encontrado. Compilacao do dashboard.ts sera ignorada.")
        return False
    except subprocess.CalledProcessError:
        print("Aviso: falha ao compilar dashboard.ts com esbuild. Continuando sem compilacao.")
        return False

    if output_dashboard_js.exists():
        return True

    print("Aviso: dashboard.js compilado nao encontrado apos esbuild.")
    return False
