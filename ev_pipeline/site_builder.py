"""Geracao dos artefatos web (HTML, CSS, JS/TS, JSON)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def _render_favicon_links(favicon_href: str | None, favicon_type: str | None) -> str:
    if not favicon_href:
        return ""

    resolved_type = favicon_type or "image/png"
    return (
        f'<link rel="icon" type="{resolved_type}" href="{favicon_href}" />\n'
        f'    <link rel="shortcut icon" type="{resolved_type}" href="{favicon_href}" />'
    )


def render_index_html(
    template_html: str,
    embedded_analysis_json: str,
    favicon_href: str | None,
    favicon_type: str | None,
    include_chart_script: bool,
) -> str:
    favicon_links = _render_favicon_links(favicon_href, favicon_type)
    chart_script_tag = (
        '<script src="./chart.umd.min.js" defer></script>' if include_chart_script else ""
    )

    rendered = template_html.replace("{{FAVICON_LINKS}}", favicon_links)
    rendered = rendered.replace("{{EMBEDDED_ANALYSIS_JSON}}", embedded_analysis_json)
    rendered = rendered.replace("{{CHART_SCRIPT_TAG}}", chart_script_tag)
    return rendered


def write_site_assets(
    project_root: Path,
    output_dir: Path,
    payload: dict,
    favicon_href: str | None,
    favicon_type: str | None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Remove legacy typo directory from older builds.
    legacy_dir = output_dir / "publc"
    if legacy_dir.exists() and legacy_dir.is_dir():
        shutil.rmtree(legacy_dir, ignore_errors=True)

    source_dir = project_root / "web_src"
    template_path = source_dir / "index.template.html"
    css_path = source_dir / "styles.css"
    dashboard_ts_path = source_dir / "dashboard.ts"
    dashboard_js_path = source_dir / "dashboard.js"
    chart_path = source_dir / "chart.umd.min.js"

    if not template_path.exists():
        raise FileNotFoundError(f"Template HTML nao encontrado: {template_path}")
    if not css_path.exists():
        raise FileNotFoundError(f"CSS de origem nao encontrado: {css_path}")
    if not dashboard_ts_path.exists() and not dashboard_js_path.exists():
        raise FileNotFoundError(
            f"Dashboard source nao encontrado: {dashboard_ts_path} ou {dashboard_js_path}"
        )

    template_html = template_path.read_text(encoding="utf-8")
    styles_css = css_path.read_text(encoding="utf-8")

    dashboard_ts = dashboard_ts_path.read_text(encoding="utf-8") if dashboard_ts_path.exists() else ""
    if (output_dir / "dashboard.js").exists():
        dashboard_js = (output_dir / "dashboard.js").read_text(encoding="utf-8")
    elif dashboard_js_path.exists():
        dashboard_js = dashboard_js_path.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError(
            "Nenhum dashboard.js compilado encontrado. Execute 'npm run build:dashboard' "
            "ou garanta que dashboard.js exista em web_src."
        )

    embedded_json = json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")
    include_chart_script = chart_path.exists()

    index_html = render_index_html(
        template_html,
        embedded_analysis_json=embedded_json,
        favicon_href=favicon_href,
        favicon_type=favicon_type,
        include_chart_script=include_chart_script,
    )

    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    (output_dir / "styles.css").write_text(styles_css, encoding="utf-8")
    # Sempre preservar o .ts fonte quando houver, e garantir um .js funcional
    if dashboard_ts_path.exists():
        (output_dir / "dashboard.ts").write_text(dashboard_ts, encoding="utf-8")

    (output_dir / "dashboard.js").write_text(dashboard_js, encoding="utf-8")
    (output_dir / "analysis.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if include_chart_script:
        shutil.copy2(chart_path, output_dir / "chart.umd.min.js")
    else:
        print("Aviso: chart.umd.min.js nao encontrado em web_src. Graficos podem nao carregar.")
