"""Regenerate HTML report from an existing JSON report file.

Usage:
  python tools/regenerate_report.py reports/report_20260620_131952.json

If no path is provided, the script picks the newest `reports/*.json` file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jinja2 import Template

from src.report_generator import HTML_TEMPLATE


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    reports_dir = root / "reports"
    if len(argv) > 1:
        json_path = Path(argv[1])
        if not json_path.is_absolute():
            json_path = root / json_path
    else:
        files = sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            print("No JSON reports found in", reports_dir)
            return 2
        json_path = files[0]

    print("Using JSON report:", json_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    html = Template(HTML_TEMPLATE).render(
        generated_at=payload.get("generated_at", ""),
        requirement=payload.get("requirement", ""),
        total=payload.get("summary", {}).get("total", 0),
        passed=payload.get("summary", {}).get("passed", 0),
        failed=payload.get("summary", {}).get("failed", 0),
        pass_rate=payload.get("summary", {}).get("pass_rate", 0.0),
        results=payload.get("results", []),
    )

    out = reports_dir / (json_path.stem + "_regenerated.html")
    out.write_text(html, encoding="utf-8")
    print("Wrote HTML report:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
