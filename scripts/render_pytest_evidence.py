"""Render a compact HTML evidence page from a pytest JUnit XML report."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import platform
import xml.etree.ElementTree as ET


def parse_report(report_path: Path) -> tuple[dict[str, int | float], list[tuple[str, int]]]:
    root = ET.parse(report_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    totals: dict[str, int | float] = {
        "tests": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "time": 0.0,
    }
    modules: Counter[str] = Counter()

    for suite in suites:
        for key in ("tests", "failures", "errors", "skipped"):
            totals[key] += int(suite.attrib.get(key, 0))
        totals["time"] += float(suite.attrib.get("time", 0.0))
        for case in suite.findall("testcase"):
            module = case.attrib.get("classname", "tests").split(".")[-1]
            modules[module] += 1

    return totals, sorted(modules.items())


def render(report_path: Path, output_path: Path) -> None:
    totals, modules = parse_report(report_path)
    passed = int(totals["tests"]) - int(totals["failures"]) - int(totals["errors"]) - int(totals["skipped"])
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    module_rows = "".join(
        f"<div class='module'><span>{escape(name)}</span><strong>{count}</strong></div>"
        for name, count in modules
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Career Assistant Platform — Test Evidence</title>
  <style>
    :root {{ color-scheme: dark; --ink:#07111f; --panel:#0d1b2e; --line:#284260; --green:#64e6a7; --muted:#9bb0c7; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; min-height:100vh; background:var(--ink); color:#f5f8fb; font-family:"Segoe UI",sans-serif; }}
    main {{ width:min(1180px,calc(100% - 72px)); margin:0 auto; padding:64px 0; }}
    .eyebrow {{ color:var(--green); font:600 13px/1.2 Consolas,monospace; letter-spacing:.16em; text-transform:uppercase; }}
    h1 {{ margin:16px 0 10px; font:700 48px/1.05 Bahnschrift,"Segoe UI",sans-serif; }}
    .sub {{ color:var(--muted); font-size:18px; }}
    .hero {{ margin:48px 0 32px; display:grid; grid-template-columns:2fr repeat(3,1fr); gap:16px; }}
    .card {{ min-height:152px; padding:24px; border:1px solid var(--line); background:var(--panel); }}
    .card.primary {{ border-top:4px solid var(--green); }}
    .label {{ color:var(--muted); font:600 12px/1.2 Consolas,monospace; letter-spacing:.12em; text-transform:uppercase; }}
    .value {{ margin-top:18px; font:700 50px/1 Bahnschrift,"Segoe UI",sans-serif; }}
    .value.green {{ color:var(--green); }}
    .modules {{ border:1px solid var(--line); background:var(--panel); padding:28px; }}
    .modules h2 {{ margin:0 0 22px; font:600 22px Bahnschrift,"Segoe UI",sans-serif; }}
    .module {{ display:flex; justify-content:space-between; padding:13px 0; border-top:1px solid #1d334d; font-family:Consolas,monospace; }}
    .module span {{ color:#c8d5e3; }}
    footer {{ display:flex; justify-content:space-between; gap:24px; margin-top:26px; color:var(--muted); font:13px Consolas,monospace; }}
  </style>
</head>
<body><main>
  <div class="eyebrow">Verified build evidence</div>
  <h1>Automated API test suite</h1>
  <div class="sub">Career Assistant Platform · pytest · isolated temporary SQLite databases</div>
  <section class="hero">
    <div class="card primary"><div class="label">Result</div><div class="value green">{passed} passed</div></div>
    <div class="card"><div class="label">Failed</div><div class="value">{int(totals['failures'])}</div></div>
    <div class="card"><div class="label">Errors</div><div class="value">{int(totals['errors'])}</div></div>
    <div class="card"><div class="label">Duration</div><div class="value">{float(totals['time']):.2f}s</div></div>
  </section>
  <section class="modules"><h2>Coverage by test module</h2>{module_rows}</section>
  <footer><span>Python {escape(platform.python_version())} · {escape(platform.system())}</span><span>Generated from pytest JUnit XML · {generated}</span></footer>
</main></body></html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.report, args.output)
