"""
Desktop UI — AI Test Case Generator + Selenium Execution

Run in VS Code terminal:
  python ui_app.py
"""

from __future__ import annotations

import json
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import BASE_URL, GENERATED_TESTS_DIR, REPORTS_DIR
from src.pipeline import MODULE_PRESETS, build_requirement, execute_plan, generate_plan

APP_TITLE = "AI Test Automation — SE4343"
BG = "#f0f4f8"
ACCENT = "#0f3460"


class TestAutomationApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x700")
        self.configure(bg=BG)
        self.test_plan: dict | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg=ACCENT, pady=12)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="AI Test Case Generator + Auto Execution",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg=ACCENT,
        ).pack()
        tk.Label(
            header,
            text=f"Target: Sauce Demo — {BASE_URL}",
            font=("Segoe UI", 9),
            fg="#cce3ff",
            bg=ACCENT,
        ).pack()

        body = tk.Frame(self, bg=BG, padx=16, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # Row: module + AI provider
        row1 = tk.Frame(body, bg=BG)
        row1.pack(fill=tk.X, pady=(0, 8))

        tk.Label(row1, text="Module:", font=("Segoe UI", 10, "bold"), bg=BG).pack(side=tk.LEFT)
        self.module_var = tk.StringVar(value="All Modules")
        module_combo = ttk.Combobox(
            row1,
            textvariable=self.module_var,
            values=list(MODULE_PRESETS.keys()),
            state="readonly",
            width=14,
        )
        module_combo.pack(side=tk.LEFT, padx=8)
        module_combo.bind("<<ComboboxSelected>>", self._on_module_change)

        tk.Label(row1, text="AI provider:", font=("Segoe UI", 10, "bold"), bg=BG).pack(side=tk.LEFT, padx=(20, 0))
        self.provider_var = tk.StringVar(value="mock")
        ttk.Combobox(
            row1,
            textvariable=self.provider_var,
            values=["mock", "gemini", "groq", "ollama", "openai"],
            state="readonly",
            width=12,
        ).pack(side=tk.LEFT, padx=8)

        self.headless_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            row1,
            text="Headless browser",
            variable=self.headless_var,
            bg=BG,
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT)

        # Requirement
        tk.Label(body, text="Requirement / test focus:", font=("Segoe UI", 10, "bold"), bg=BG, anchor="w").pack(
            fill=tk.X
        )
        self.requirement_text = scrolledtext.ScrolledText(body, height=5, font=("Consolas", 10))
        self.requirement_text.pack(fill=tk.X, pady=4)

        self.status_var = tk.StringVar(value="Ready")

        # Buttons
        btn_frame = tk.Frame(body, bg=BG)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Generate test cases", command=self._on_generate).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Execute tests", command=self._on_execute).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="Generate & Execute", command=self._on_both).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text="Open reports folder", command=self._open_reports).pack(side=tk.RIGHT)

        tk.Label(body, textvariable=self.status_var, font=("Segoe UI", 9), fg="#555", bg=BG, anchor="w").pack(
            fill=tk.X
        )

        self._on_module_change()

        # Output
        tk.Label(body, text="Output:", font=("Segoe UI", 10, "bold"), bg=BG, anchor="w").pack(fill=tk.X, pady=(8, 0))
        self.output = scrolledtext.ScrolledText(body, height=22, font=("Consolas", 9), state=tk.DISABLED)
        self.output.pack(fill=tk.BOTH, expand=True, pady=4)

    def _on_module_change(self, _event=None) -> None:
        module = self.module_var.get()
        preset = MODULE_PRESETS.get(module, "")
        self.requirement_text.delete("1.0", tk.END)
        if preset:
            self.requirement_text.insert("1.0", preset)
        hints = {
            "All Modules": "17 tests — ~5–8 min. Tip: run one module (Login) for a quick demo (~1 min).",
            "Login": "5 tests — ~1–2 min",
            "Inventory": "4 tests — ~1–2 min",
            "Cart": "4 tests — ~2–3 min",
            "Checkout": "4 tests — ~2–3 min",
        }
        if module in hints:
            self._log_hint(hints[module])

    def _log_hint(self, text: str) -> None:
        if hasattr(self, "status_var"):
            self.status_var.set(text)

    def _log(self, text: str, clear: bool = False) -> None:
        self.output.configure(state=tk.NORMAL)
        if clear:
            self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)
        self.update_idletasks()

    def _get_requirement(self) -> str:
        custom = self.requirement_text.get("1.0", tk.END).strip()
        return build_requirement(self.module_var.get(), custom)

    def _on_generate(self) -> None:
        self._run_async(self._generate_only)

    def _on_execute(self) -> None:
        self._run_async(self._execute_only)

    def _on_both(self) -> None:
        self._run_async(self._generate_and_execute)

    def _run_async(self, func) -> None:
        threading.Thread(target=func, daemon=True).start()

    def _generate_only(self) -> None:
        req = self._get_requirement()
        provider = self.provider_var.get()
        self.status_var.set("Generating test cases...")
        self._log(f"=== Generating ({provider}) ===\nRequirement: {req}\n", clear=True)
        try:
            self.test_plan = generate_plan(
                req,
                ai_provider=provider,
                module_filter=self.module_var.get(),
            )
            self._print_plan(self.test_plan)
            self.status_var.set(f"Generated {len(self.test_plan.get('test_cases', []))} test case(s)")
            messagebox.showinfo("Success", "Test cases generated and saved.")
        except Exception as exc:
            self.status_var.set("Generation failed")
            self._log(f"ERROR: {exc}")
            messagebox.showerror("Error", str(exc))

    def _execute_only(self) -> None:
        if not self.test_plan:
            messagebox.showwarning("No plan", "Generate test cases first.")
            return
        self._run_execution()

    def _generate_and_execute(self) -> None:
        self._generate_only()
        if self.test_plan:
            self._run_execution()

    def _run_execution(self) -> None:
        total = len(self.test_plan.get("test_cases", [])) if self.test_plan else 0
        est_min = max(1, total // 3)  # ~3 cases/min after browser reuse optimization
        self.status_var.set(f"Running {total} tests (~{est_min}–{est_min + 2} min)...")
        self._log("\n=== Executing in browser (one Chrome session) ===\n")
        self._log(f"Running {total} test case(s). Please wait...\n")

        def on_progress(current: int, count: int, test_id: str) -> None:
            self.status_var.set(f"Running test {current}/{count}: {test_id}...")
            self._log(f"  >> [{current}/{count}] {test_id}")

        try:
            results, payload, json_path, html_path = execute_plan(
                self.test_plan,
                headless=self.headless_var.get(),
                on_progress=on_progress,
            )
            summary = payload["summary"]
            self._log(f"Total:  {summary['total']}")
            self._log(f"Passed: {summary['passed']}")
            self._log(f"Failed: {summary['failed']}")
            self._log(f"Pass rate: {summary['pass_rate']}%")
            self._log(f"\nHTML report: {html_path}")
            self._log(f"JSON report: {json_path}")
            for row in payload.get("results", []):
                icon = "PASS" if row["status"] == "PASS" else "FAIL"
                self._log(f"  [{icon}] {row['test_id']}: {row['title']}")
            self.status_var.set(
                f"Done — {summary['passed']}/{summary['total']} passed"
            )
            if summary["failed"] == 0:
                messagebox.showinfo("Execution complete", "All tests passed!")
            else:
                messagebox.showwarning("Execution complete", "Some tests failed. See output.")
        except Exception as exc:
            self.status_var.set("Execution failed")
            self._log(f"ERROR: {exc}")
            messagebox.showerror("Error", str(exc))

    def _print_plan(self, plan: dict) -> None:
        self._log(f"Provider: {plan.get('_ai_provider', 'unknown')}\n")
        summary = plan.get("summary", {})
        if summary:
            self._log(
                f"Planned: {summary.get('total_cases')} cases | "
                f"expected ~{summary.get('expected_pass')} PASS / ~{summary.get('expected_fail')} FAIL\n"
            )
        self._log(f"Modules: {', '.join(plan.get('modules_tested', []))}\n")
        self._log("--- Scenarios ---")
        for s in plan.get("scenarios", []):
            self._log(f"  [{s.get('id')}] {s.get('title')}")
        self._log("\n--- Test cases ---")
        for c in plan.get("test_cases", []):
            self._log(f"\n  [{c.get('id')}] {c.get('title')}")
            self._log(f"  Expected: {c.get('expected_output', '')}")
            for i, step in enumerate(c.get("steps", []), 1):
                self._log(f"    {i}. {step.get('description', step.get('action'))}")
        path = GENERATED_TESTS_DIR / "latest_test_plan.json"
        self._log(f"\nSaved: {path}")

    def _open_reports(self) -> None:
        REPORTS_DIR.mkdir(exist_ok=True)
        import os
        os.startfile(str(REPORTS_DIR))


def main() -> None:
    app = TestAutomationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
