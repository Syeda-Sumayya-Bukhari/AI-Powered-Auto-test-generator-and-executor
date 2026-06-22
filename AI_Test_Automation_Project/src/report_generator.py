"""Generate HTML and JSON execution reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Template

from src.config import REPORTS_DIR
from src.selenium_runner import TestCaseResult

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Test Execution Report</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 2rem; background: #f5f7fb; color: #1a1a2e; }
    h1 { color: #0f3460; }
    .summary { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
    .card { background: #fff; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
    .pass { color: #198754; font-weight: bold; }
    .fail { color: #dc3545; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; }
    th, td { padding: 0.75rem 1rem; border-bottom: 1px solid #e9ecef; text-align: left; }
    th { background: #0f3460; color: #fff; }
    tr:hover { background: #f8f9fa; }
    .meta { color: #6c757d; font-size: 0.9rem; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>AI Test Automation — Execution Report</h1>
  <p class="meta">Generated: {{ generated_at }} | Requirement: {{ requirement }}</p>
  <div class="summary">
    <div class="card">Total: <strong>{{ total }}</strong></div>
    <div class="card pass">Passed: <strong>{{ passed }}</strong></div>
    <div class="card fail">Failed: <strong>{{ failed }}</strong></div>
    <div class="card">Pass Rate: <strong>{{ pass_rate }}%</strong></div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Test ID</th>
        <th>Module</th>
        <th>Type</th>
        <th>Title</th>
        <th>Status</th>
        <th>Duration (s)</th>
        <th>Expected Output</th>
        <th>Error</th>
      </tr>
    </thead>
    <tbody>
      {% for r in results %}
      <tr>
        <td>{{ r.test_id }}</td>
        <td>{{ r.module }}</td>
        <td>{{ r.title }}</td>
        <td class="{{ 'pass' if r.status == 'PASS' else 'fail' }}">{{ r.status }}</td>
        <td>{{ r.duration_seconds }}</td>
        <td>{{ r.expected_output }}</td>
        <td>{{ r.error }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""


def results_to_dict(results: list[TestCaseResult]) -> list[dict[str, Any]]:
    return [
        {
            "test_id": r.test_id,
            "module": r.module,
            "test_type": r.test_type,
            "title": r.title,
            "status": r.status,
            "duration_seconds": r.duration_seconds,
            "expected_output": r.expected_output,
            "error": r.error,
            "steps": [
                {
                    "step_index": s.step_index,
                    "action": s.action,
                    "description": s.description,
                    "status": s.status,
                    "message": s.message,
                }
                for s in r.steps
            ],
        }
        for r in results
    ]


def build_report_payload(
    requirement: str,
    results: list[TestCaseResult],
) -> dict[str, Any]:
    passed = sum(1 for r in results if r.status == "PASS")
    failed = len(results) - passed
    total = len(results)
    pass_rate = round((passed / total) * 100, 1) if total else 0.0
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requirement": requirement,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
        },
        "results": results_to_dict(results),
    }


def save_json_report(payload: dict[str, Any], path: Path | None = None) -> Path:
    out = path or REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def save_html_report(
    requirement: str,
    results: list[TestCaseResult],
    path: Path | None = None,
) -> Path:
    payload = build_report_payload(requirement, results)
    summary = payload["summary"]
    html = Template(HTML_TEMPLATE).render(
        generated_at=payload["generated_at"],
        requirement=requirement,
        total=summary["total"],
        passed=summary["passed"],
        failed=summary["failed"],
        pass_rate=summary["pass_rate"],
        results=results,
    )
    out = path or REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    out.write_text(html, encoding="utf-8")
    return out
