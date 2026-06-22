#!/usr/bin/env python3
"""
AI-Powered Test Case Generator + Auto Execution

Usage:
  python main.py "Test login page"
  python main.py "Test login page" --visible
  python main.py "Test login page" --generate-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.ai_generator import provider_label
from src.config import GENERATED_TESTS_DIR
from src.pipeline import MODULE_PRESETS, build_requirement, execute_plan, execute_plan_parallel, generate_plan


def print_plan_summary(plan: dict) -> None:
    print("\n=== Generated Test Scenarios ===")
    for scenario in plan.get("scenarios", []):
        print(f"  [{scenario.get('id')}] {scenario.get('title')}")
        print(f"      {scenario.get('description', '')}")

    print("\n=== Generated Test Cases ===")
    for case in plan.get("test_cases", []):
        print(f"  [{case.get('id')}] {case.get('title')} (Priority: {case.get('priority', 'N/A')})")
        print(f"      Expected: {case.get('expected_output', '')}")
        print("      Steps:")
        for i, step in enumerate(case.get("steps", []), 1):
            print(f"        {i}. {step.get('description', step.get('action'))}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Test Case Generator with Selenium auto-execution"
    )
    parser.add_argument("requirement", help='e.g. "Test login page"')
    parser.add_argument(
        "--module",
        choices=list(MODULE_PRESETS.keys()),
        default="All Modules",
        help="Select a module preset or Custom requirement",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Show browser window during execution",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate test cases; do not run Selenium",
    )
    parser.add_argument(
        "--grid-url",
        help="Run tests against a Selenium Grid or remote WebDriver hub",
    )
    parser.add_argument(
        "--grid-browsers",
        default="chrome,firefox",
        help="Comma-separated browsers to run in parallel against the remote grid",
    )
    parser.add_argument(
        "--grid-platform",
        default="ANY",
        help="Platform name to request from Selenium Grid (default: ANY)",
    )
    args = parser.parse_args()

    full_requirement = build_requirement(args.module, args.requirement)
    print(f"Module: {args.module}")
    print(f"Requirement: {full_requirement}")
    print(f"AI provider: {provider_label()}")
    print("Generating test cases...")

    plan = generate_plan(full_requirement, module_filter=args.module)
    plan_path = GENERATED_TESTS_DIR / "latest_test_plan.json"
    print(f"Saved test plan: {plan_path}")

    print_plan_summary(plan)

    if args.generate_only:
        print("\nGenerate-only mode — skipping browser execution.")
        return 0

    print("\nRunning tests in browser (Selenium)...")
    if args.grid_url:
        browser_names = [name.strip() for name in args.grid_browsers.split(",") if name.strip()]
        browser_configs = [
            {
                "grid_url": args.grid_url,
                "browser_name": browser_name,
                "platform_name": args.grid_platform,
                "headless": not args.visible,
                "environment": f"{browser_name}@{args.grid_platform}",
            }
            for browser_name in browser_names
        ]
        results, payload, json_path, html_path = execute_plan_parallel(
            plan,
            browser_configs,
            headless=not args.visible,
        )
    else:
        results, payload, json_path, html_path = execute_plan(plan, headless=not args.visible)

    for result in results:
        icon = "PASS" if result.status == "PASS" else "FAIL"
        print(f"  [{icon}] {result.test_id}: {result.title} ({result.duration_seconds}s)")
        if result.error:
            print(f"         Error: {result.error}")

    summary = payload["summary"]
    print("\n=== Execution Summary ===")
    print(f"  Total:  {summary['total']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Pass rate: {summary['pass_rate']}%")
    print(f"\nReports saved:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}")

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
