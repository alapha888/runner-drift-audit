#!/usr/bin/env python3
"""generate_report.py: turn a runner-drift-audit scan into a standalone
migration-readiness report (Markdown + HTML).

Usage:
    python3 generate_report.py [path-to-repo] [--out DIR]

Exit code mirrors the scanner: 1 if any HIGH finding exists, else 0.
Stdlib only. The report is a review aid, not a proof of migration safety.
"""
import csv
import datetime
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runner_drift_audit import audit_file, find_workflows  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DIFFS_CSV = os.path.join(HERE, "toolset-differences-2404-2604.csv")
MIGRATION_WINDOW = "October 19 - November 19, 2026"
SEVERITIES = ("HIGH", "WARN")

FIX_BY_RULE = {
    "FLOATING_LABEL": "Pin the runner label: use ubuntu-24.04 to stay on the current image, or ubuntu-26.04 to migrate deliberately.",
    "RETIRED_LABEL": "Move the job to a supported label: macos-15 for the smallest change, or macos-latest (macos-26) if a floating label is acceptable. The macos-14 image is removed on November 2, 2026.",
    "REMOVED_TOOL": "Replace or drop this step, or install the tool explicitly in a setup step before use.",
    "DEFAULT_DRIFT": "Pin the version explicitly (setup action, service/image pin, or version file) instead of relying on the image default.",
    "UNPINNED_ACTION": "Pin the action to a full commit SHA if your policy requires immutable refs.",
}


def collect_results(root):
    """Audit every workflow under root; return a results dict."""
    files = find_workflows(root)
    per_file = []
    totals = {sev: 0 for sev in SEVERITIES}
    for path in files:
        findings = audit_file(path)
        for sev, _ln, _rule, _msg in findings:
            totals[sev] = totals.get(sev, 0) + 1
        per_file.append({
            "path": path,
            "display": os.path.relpath(path, root) if root not in ("", ".") else path,
            "findings": findings,
        })
    return {
        "root": root,
        "generated": datetime.date.today().isoformat(),
        "files": per_file,
        "totals": totals,
        "total_files": len(files),
        "total_findings": sum(totals.values()),
    }


def load_differences(csv_path=DIFFS_CSV):
    """Load the toolset differences table; [] when the CSV is absent.

    Lines starting with # are schema/comment rows and are skipped before
    parsing, so the CSV header row stays the first non-comment line.
    """
    if not os.path.isfile(csv_path):
        return []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        rows = (line for line in fh if not line.lstrip().startswith("#"))
        return list(csv.DictReader(rows))


def build_checklist(results):
    """Ordered, de-duplicated fix list derived from the findings."""
    items = ["Inventory: list every file in .github/workflows and confirm each one is expected before changing anything."]
    seen = set()
    for entry in results["files"]:
        for sev, ln, rule, msg in entry["findings"]:
            action = FIX_BY_RULE.get(rule, "Review this finding and decide on a fix.")
            key = (entry["display"], ln, rule)
            if key in seen:
                continue
            seen.add(key)
            items.append(f"[{sev}] {entry['display']} line {ln} ({rule}): {action} Finding: {msg}")
    items.append("Re-run the scanner (or this report) until no HIGH findings remain.")
    items.append("Attach the final report to the migration PR so reviewers can see what was checked.")
    return items


def render_markdown(results, differences):
    t = results["totals"]
    lines = [
        "# Migration readiness report — ubuntu-latest 24.04 → 26.04",
        "",
        f"- Scanned root: `{results['root']}`",
        f"- Generated: {results['generated']}",
        f"- Migration window for the `ubuntu-latest` label: {MIGRATION_WINDOW}",
        f"- Workflow files scanned: {results['total_files']}",
        f"- Findings: **{results['total_findings']}** total — HIGH: {t.get('HIGH', 0)}, WARN: {t.get('WARN', 0)}",
        "",
        "## Findings by workflow",
        "",
    ]
    if not results["files"]:
        lines.append("No workflow files found.")
    for entry in results["files"]:
        lines.append(f"### {entry['display']}")
        lines.append("")
        if not entry["findings"]:
            lines.append("No findings.")
        else:
            lines.append("| Severity | Line | Rule | Finding |")
            lines.append("|---|---|---|---|")
            for sev, ln, rule, msg in entry["findings"]:
                cell = msg.replace("|", "\\|")
                lines.append(f"| {sev} | {ln} | {rule} | {cell} |")
        lines.append("")
    lines += ["## Toolset differences (Ubuntu 24.04 → 26.04)", ""]
    if differences:
        cols = ["category", "tool", "change_type", "ubuntu_2404", "ubuntu_2604", "ci_impact", "mitigation"]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("|" + "---|" * len(cols))
        for row in differences:
            lines.append("| " + " | ".join((row.get(c, "") or "").replace("|", "\\|") for c in cols) + " |")
    else:
        lines.append("Differences table source (toolset-differences-2404-2604.csv) not found next to the report generator.")
    lines += ["", "## Fix checklist", ""]
    for i, item in enumerate(build_checklist(results), 1):
        lines.append(f"{i}. {item}")
    lines += [
        "",
        "---",
        "Generated by runner-drift-audit. Line scanner with heuristics, not a full YAML/shell parser; treat findings as a review checklist, not a proof.",
        "Rule sources: actions/runner-images toolset-2404.json vs toolset-2604.json; GitHub Changelog 2026-10-01 (macOS 14 runner image retirement, November 2, 2026).",
        "",
    ]
    return "\n".join(lines)


def render_html(results, differences):
    t = results["totals"]
    e = html.escape
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Migration readiness report — ubuntu-latest 24.04 → 26.04</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;line-height:1.5}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}td,th{border:1px solid #ccc;padding:.35rem .5rem;text-align:left;vertical-align:top}"
        ".high{color:#b00020;font-weight:700}.warn{color:#9a6a00;font-weight:700}"
        "code{background:#f2f2f2;padding:.1rem .3rem;border-radius:3px}</style>",
        "</head><body>",
        "<h1>Migration readiness report — ubuntu-latest 24.04 → 26.04</h1>",
        "<ul>",
        f"<li>Scanned root: <code>{e(str(results['root']))}</code></li>",
        f"<li>Generated: {e(results['generated'])}</li>",
        f"<li>Migration window for the <code>ubuntu-latest</code> label: {MIGRATION_WINDOW}</li>",
        f"<li>Workflow files scanned: {results['total_files']}</li>",
        f"<li>Findings: <strong>{results['total_findings']}</strong> total — "
        f'<span class="high">HIGH: {t.get("HIGH", 0)}</span>, <span class="warn">WARN: {t.get("WARN", 0)}</span></li>',
        "</ul>",
        "<h2>Findings by workflow</h2>",
    ]
    if not results["files"]:
        parts.append("<p>No workflow files found.</p>")
    for entry in results["files"]:
        parts.append(f"<h3><code>{e(entry['display'])}</code></h3>")
        if not entry["findings"]:
            parts.append("<p>No findings.</p>")
            continue
        parts.append("<table><tr><th>Severity</th><th>Line</th><th>Rule</th><th>Finding</th></tr>")
        for sev, ln, rule, msg in entry["findings"]:
            cls = "high" if sev == "HIGH" else "warn"
            parts.append(f'<tr><td class="{cls}">{e(sev)}</td><td>{ln}</td><td>{e(rule)}</td><td>{e(msg)}</td></tr>')
        parts.append("</table>")
    parts.append("<h2>Toolset differences (Ubuntu 24.04 → 26.04)</h2>")
    if differences:
        cols = ["category", "tool", "change_type", "ubuntu_2404", "ubuntu_2604", "ci_impact", "mitigation"]
        parts.append("<table><tr>" + "".join(f"<th>{e(c)}</th>" for c in cols) + "</tr>")
        for row in differences:
            parts.append("<tr>" + "".join(f"<td>{e(row.get(c, '') or '')}</td>" for c in cols) + "</tr>")
        parts.append("</table>")
    else:
        parts.append("<p>Differences table source (toolset-differences-2404-2604.csv) not found next to the report generator.</p>")
    parts.append("<h2>Fix checklist</h2><ol>")
    for item in build_checklist(results):
        parts.append(f"<li>{e(item)}</li>")
    parts.append("</ol>")
    parts.append("<hr><p>Generated by runner-drift-audit. Line scanner with heuristics, not a full YAML/shell parser; "
                 "treat findings as a review checklist, not a proof.<br>"
                 "Rule sources: actions/runner-images toolset-2404.json vs toolset-2604.json; GitHub Changelog 2026-10-01 (macOS 14 runner image retirement, November 2, 2026).</p>")
    parts.append("</body></html>")
    return "\n".join(parts) + "\n"


def main(argv):
    import argparse
    parser = argparse.ArgumentParser(
        prog="generate_report.py",
        description="Generate a Markdown + HTML migration-readiness report from a runner-drift scan.")
    parser.add_argument("path", nargs="?", default=".",
                        help="repository or workflows directory to scan (default: current directory)")
    parser.add_argument("--out", default="runner-drift-report",
                        help="output directory for the two report files")
    ns = parser.parse_args(argv[1:])
    root = ns.path
    out_dir = ns.out
    results = collect_results(root)
    differences = load_differences()
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "migration-readiness-report.md")
    html_path = os.path.join(out_dir, "migration-readiness-report.html")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(results, differences))
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(render_html(results, differences))
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")
    print(f"Findings: {results['total_findings']} (HIGH {results['totals'].get('HIGH', 0)}, "
          f"WARN {results['totals'].get('WARN', 0)}) across {results['total_files']} workflow file(s).")
    return 1 if results["totals"].get("HIGH", 0) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
