#!/usr/bin/env python3
"""runner-drift-audit: scan GitHub Actions workflows for breakage risks in the
ubuntu-latest 24.04 -> 26.04 runner migration (Oct 19 - Nov 19, 2026).

Rules are grounded in the official actions/runner-images toolsets
(toolset-2404.json vs toolset-2604.json, compared 2026-10-10):

  - Java default 17 -> 25, Java 8 removed
  - Node default 22 -> 24; preinstalled global tools shrink to n + yarn
    (webpack, gulp, grunt, parcel, lerna, newman, typescript/tsc removed)
  - PHP 8.3 -> 8.5 only; PostgreSQL 16 -> 18
  - clang default 18 -> 21 (16/17 removed); gcc/gfortran 12 removed
  - CMake was pinned to 3.31.6 (to avoid CMake 4.0 issues), now "latest"
  - Docker 28.0.4 -> 29.4.2, compose 2.38.2 -> 5.1.3
  - apt packages removed: haveged, mediainfo, sphinxsearch, mercurial
    (p7zip-full replaced by 7zip); ruby gem fastlane no longer preinstalled
  - Go default 1.24 -> 1.26

A second rule source is GitHub's own changelog: the macOS 14 runner
image (labels macos-14, macos-14-large, macos-14-xlarge) is retired on
November 2, 2026, after scheduled brownouts through October 2026
(GitHub Changelog, 2026-10-01). A pinned label does not drift — it
stops working — so those labels are reported as RETIRED_LABEL (HIGH)
wherever a runner label can appear.

Usage: python3 runner_drift_audit.py [path-to-repo-or-workflows-dir]
           [--sarif FILE] [--json FILE] [--summary-file FILE]
Exit code: 1 if any HIGH finding, else 0. Stdlib only.

With --sarif FILE, findings are also written as SARIF 2.1.0 JSON, so
they can be uploaded to GitHub Code Scanning (for example with
github/codeql-action/upload-sarif) and appear in the Security tab.

With --json FILE, findings are also written as plain machine-readable
JSON (schema_version 1): a summary with HIGH/WARN counts plus, for
every scanned file, its findings with severity, line, rule and
message. Use it to feed dashboards, PR comments or your own gates
without scraping the text report. Exit code is unchanged.

With --summary-file FILE, findings are also written as a Markdown
summary (counts plus a per-file findings table). Point it at
$GITHUB_STEP_SUMMARY inside GitHub Actions to see the results on the
job summary page without opening the logs; the Action does this
automatically unless its step-summary input is set to "false".
"""
import json
import os
import re
import sys

# Commands whose backing package/tool disappeared from the 26.04 image.
REMOVED_COMMANDS = {
    "hg": "mercurial was removed from the Ubuntu 26.04 runner image",
    "mediainfo": "mediainfo was removed from the Ubuntu 26.04 runner image",
    "sphinxsearch": "sphinxsearch was removed from the Ubuntu 26.04 runner image",
    "searchd": "sphinxsearch (searchd) was removed from the Ubuntu 26.04 runner image",
    "haveged": "haveged was removed from the Ubuntu 26.04 runner image",
    "fastlane": "the fastlane ruby gem is no longer preinstalled in the Ubuntu 26.04 runner image",
    "webpack": "webpack is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "gulp": "gulp is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "grunt": "grunt is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "parcel": "parcel is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "lerna": "lerna is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "newman": "newman is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "tsc": "typescript (tsc) is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain)",
    "gcc-12": "gcc 12 was removed from the Ubuntu 26.04 runner image (13/14/15 remain)",
    "g++-12": "g++ 12 was removed from the Ubuntu 26.04 runner image (13/14/15 remain)",
    "gfortran-12": "gfortran 12 was removed from the Ubuntu 26.04 runner image (13/14/15 remain)",
    "clang-16": "clang 16 was removed from the Ubuntu 26.04 runner image (20/21/22 remain)",
    "clang-17": "clang 17 was removed from the Ubuntu 26.04 runner image (20/21/22 remain)",
    "p7zip": "p7zip-full was replaced by 7zip in the Ubuntu 26.04 runner image; check 7z invocations and package names",
}

# Tools whose *default* version changes when no setup-* action pins it.
DEFAULT_DRIFT = [
    (re.compile(r"\b(java|javac|mvn|gradle)\b"), "java",
     "Java default changes 17 -> 25 in the Ubuntu 26.04 image (and Java 8 is removed); pin with actions/setup-java"),
    (re.compile(r"\b(node|npm|npx)\b"), "node",
     "Node default changes 22 -> 24 in the Ubuntu 26.04 image; pin with actions/setup-node"),
    (re.compile(r"\bphp\b"), "php",
     "PHP changes 8.3 -> 8.5 (only version shipped) in the Ubuntu 26.04 image; pin with shivammathur/setup-php"),
    (re.compile(r"\b(psql|pg_ctl|postgres)\b"), "postgres",
     "PostgreSQL default changes 16 -> 18 in the Ubuntu 26.04 image; pin a version explicitly"),
    (re.compile(r"\bcmake\b"), "cmake",
     "CMake was pinned to 3.31.6 on 24.04 to avoid CMake 4.0 compatibility issues; the 26.04 image ships latest, so CMake 4 behavior may apply"),
    (re.compile(r"\bclang\b"), "clang",
     "clang default changes 18 -> 21 in the Ubuntu 26.04 image; pin a version explicitly"),
    (re.compile(r"\bgo\b(?=\s+(build|test|run|vet))"), "go",
     "Go default changes 1.24 -> 1.26 in the Ubuntu 26.04 image; pin with actions/setup-go"),
    (re.compile(r"docker\s+compose\b"), "docker",
     "Docker Compose changes 2.38.2 -> 5.1.3 (and Docker 28 -> 29) in the Ubuntu 26.04 image; test compose files against v5"),
]

SETUP_FOR = {
    "java": "setup-java", "node": "setup-node", "php": "setup-php",
    "postgres": None, "cmake": None, "clang": None, "go": "setup-go",
    "docker": None,
}

USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
RUNSON_RE = re.compile(r"^\s*-?\s*runs-on:\s*(.+)$")
# A floating label can also hide in a bracket list on another key (the usual
# case: a matrix axis such as `os: [ubuntu-latest, windows-latest]`) or as a
# bare list item (a block matrix axis, or a multi-line `runs-on:` list).
# Outside a `runs-on:` line the context is ambiguous, so list detection is
# deliberately narrow: bracket lists only on the `os` axis or on a key the
# file actually references as `matrix.<key>`, and bare items / list entries
# only when they carry a GitHub-hosted runner prefix (ubuntu-/windows-/
# macos-). A `- docker-latest` argument or a `browser: [chrome-latest]`
# axis is not a runner label and must not be flagged.
LIST_KEY_RE = re.compile(r"^\s*-?\s*([\w.-]+):\s*\[([^\]]*)\]")
LIST_ITEM_LABEL_RE = re.compile(
    r"^\s*-\s*['\"]?((?:ubuntu|windows|macos)-[A-Za-z0-9._-]*latest)"
    r"['\"]?\s*(#.*)?$")
# Bare list items carrying a retired label (block matrix axis or a
# multi-line `runs-on:` list). The label set is exact — see
# RETIRED_LABELS — so this cannot drift into flagging pinned labels
# that are still supported.
LIST_ITEM_RETIRED_RE = re.compile(
    r"^\s*-\s*['\"]?(macos-14(?:-large|-xlarge)?)['\"]?\s*(#.*)?$")
RUNNER_PREFIXES = ("ubuntu-", "windows-", "macos-")
# A `runs-on:` value that is exactly one env/vars/inputs expression, e.g.
# `runs-on: ${{ env.RUNNER_LABEL }}`. The label then lives wherever that
# variable is set, which may be outside this file. Deliberately narrow:
# compound expressions (ternaries, fromJSON, function calls) are not
# matched, because they can pin every branch in the same line.
SINGLE_EXPR_RE = re.compile(
    r"^['\"]?\$\{\{\s*(env|vars|inputs)\.([\w-]+)\s*\}\}['\"]?$")
# A plain scalar assignment of a runner label to a named key, e.g.
# `RUNNER_LABEL: ubuntu-latest` under an `env:` block.
ASSIGN_LABEL_RE = re.compile(
    r"^\s*-?\s*([\w.-]+):\s*['\"]?((?:ubuntu|windows|macos)-[A-Za-z0-9._-]*)"
    r"['\"]?\s*(#.*)?$")


def is_runner_label(lab):
    return lab.startswith(RUNNER_PREFIXES)


def floating_label_message(lab, via=""):
    if lab == "ubuntu-latest":
        return (f"runner label '{lab}' is a floating label{via}; it moves "
                "24.04 -> 26.04 between Oct 19 and Nov 19, 2026. Pin "
                "ubuntu-24.04 to stay, or ubuntu-26.04 to migrate deliberately.")
    return (f"runner label '{lab}' is a floating label{via}; it moves to a "
            "new image generation on the provider's schedule, outside this "
            "scanner's Ubuntu migration window. Pin a versioned label if "
            "this job needs to stay stable.")


# Labels retired outright on a published date (GitHub Changelog,
# 2026-10-01, "GitHub Actions: macOS 14 runner image retirement").
# Only labels with a published retirement date are listed; a versioned
# label not listed here is not assumed retired. Jobs on these labels
# fail during scheduled brownouts in October 2026 and stop working
# entirely on the retirement date.
RETIRED_LABELS = {
    "macos-14": "November 2, 2026",
    "macos-14-large": "November 2, 2026",
    "macos-14-xlarge": "November 2, 2026",
}


def retired_label_message(lab, via=""):
    return (f"runner label '{lab}' is retired{via}; the macOS 14 runner "
            f"image is removed on {RETIRED_LABELS[lab]} and jobs using it "
            "fail during scheduled brownouts before that date (GitHub "
            "Changelog, 2026-10-01). Move to macos-15, or to macos-latest "
            "(macos-26) if a floating label is acceptable.")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SEG_SPLIT = re.compile(r"&&|\|\||;|\|")
QUOTE_RE = re.compile(r"\"[^\"\n]*\"|'[^'\n]*'")
PREFIX_WORDS = {"sudo", "env", "command", "time", "xargs"}
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def command_heads(text):
    """First command word of each shell segment, honouring quotes and
    common prefixes (sudo, env, VAR=val, subshell parens)."""
    text = QUOTE_RE.sub(" ", text)
    heads = []
    for seg in SEG_SPLIT.split(text):
        toks = seg.strip().lstrip("({ ").split()
        i = 0
        while i < len(toks) and (toks[i] in PREFIX_WORDS or ASSIGN_RE.match(toks[i])):
            i += 1
        if i < len(toks):
            heads.append(toks[i].strip("()"))
    return heads


def find_workflows(root):
    cands = []
    wf_dir = os.path.join(root, ".github", "workflows")
    if os.path.isdir(wf_dir):
        cands = [os.path.join(wf_dir, f) for f in sorted(os.listdir(wf_dir))]
    elif os.path.isdir(root):
        cands = [os.path.join(root, f) for f in sorted(os.listdir(root))]
    return [p for p in cands if p.endswith((".yml", ".yaml")) and os.path.isfile(p)]


def audit_file(path):
    findings = []  # (severity, line_no, rule, message)
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    text = "\n".join(lines)
    matrix_keys = set(re.findall(r"matrix\.([\w-]+)", text))
    # Names referenced through an expression context (env.X / vars.X /
    # inputs.X) anywhere in the file, and plain scalar assignments, used
    # to follow one level of label indirection (see SINGLE_EXPR_RE).
    expr_refs = set(re.findall(r"(?:env|vars|inputs)\.([\w-]+)", text))
    assignments = {}
    for raw in lines:
        ma = ASSIGN_LABEL_RE.match(raw.split("#")[0])
        if ma:
            assignments[ma.group(1)] = ma.group(2)
    # A floating or retired label assigned to a *RUNNER*-named key that
    # the file actually references through an expression is a real
    # label, one hop away from the `runs-on:` line. The same holds for
    # a scalar assignment to a key the file references as `matrix.<key>`
    # (the usual case: a `matrix.include:` entry such as `- os: macos-14`).
    # Unreferenced keys (report baselines, test fixtures) are not flagged.
    for idx, raw in enumerate(lines, 1):
        ma = ASSIGN_LABEL_RE.match(raw.split("#")[0])
        if not ma:
            continue
        key, lab = ma.group(1), ma.group(2)
        if "runner" in key.lower() and key in expr_refs:
            via = (f" (assigned to '{key}' and "
                   "referenced through an expression)")
        elif key in matrix_keys:
            via = (f" (assigned to '{key}', a matrix key "
                   "referenced in this file)")
        else:
            continue
        if lab.endswith("-latest"):
            findings.append(("HIGH", idx, "FLOATING_LABEL",
                             floating_label_message(lab, via)))
        elif lab in RETIRED_LABELS:
            findings.append(("HIGH", idx, "RETIRED_LABEL",
                             retired_label_message(lab, via)))
    on_ubuntu = bool(re.search(r"ubuntu-(latest|24\.04|26\.04)", text))
    setup_present = {k: (v and v in text) for k, v in SETUP_FOR.items()}
    seen_drift = set()
    run_block_indent = None  # indent of a `run: |` key while inside its block

    for i, line in enumerate(lines, 1):
        # Track multi-line run blocks by indentation.
        is_run_line = False
        run_text = line
        if run_block_indent is not None:
            if line.strip() == "":
                is_run_line = True
            elif len(line) - len(line.lstrip()) > run_block_indent:
                is_run_line = True
            else:
                run_block_indent = None
        m_run = re.match(r"^(\s*)-?\s*run:\s*(.*)$", line)
        if m_run:
            rest = m_run.group(2).strip()
            if re.match(r"^[|>][0-9]*[+-]?\s*(#.*)?$", rest):
                run_block_indent = len(m_run.group(1)) + (2 if line.lstrip().startswith("- ") else 0)
                is_run_line = False
            elif rest:
                is_run_line = True
                run_text = rest
        if not is_run_line:
            m = RUNSON_RE.search(line)
            if m:
                me = SINGLE_EXPR_RE.match(m.group(1).split("#")[0].strip())
                if me:
                    kind, name = me.group(1), me.group(2)
                    if (kind == "env" and name in assignments
                            and "runner" not in name.lower()
                            and name not in matrix_keys):
                        # Resolved in this file, but under a key name
                        # the assignment pass does not flag: judge the
                        # label here instead of staying silent. A
                        # supported pinned label resolves clean.
                        lab = assignments[name]
                        via = f" (set by 'env.{name}' in this file)"
                        if lab.endswith("-latest"):
                            findings.append(
                                ("HIGH", i, "FLOATING_LABEL",
                                 floating_label_message(lab, via)))
                        elif lab in RETIRED_LABELS:
                            findings.append(
                                ("HIGH", i, "RETIRED_LABEL",
                                 retired_label_message(lab, via)))
                    elif not (kind == "env" and name in assignments):
                        findings.append(
                            ("WARN", i, "INDIRECT_RUNS_ON",
                             f"runner label is fed by the expression "
                             f"'${{{{ {kind}.{name} }}}}' and this scanner "
                             "cannot resolve it; check where that value is "
                             "set (env defaults in this file, repository "
                             "variables, or caller inputs) and pin it there "
                             "if it floats."))
                else:
                    labels = [t.split("#")[0].strip(" '\"[],")
                              for t in m.group(1).split(",")]
                    for lab in labels:
                        if lab.endswith("-latest"):
                            findings.append(("HIGH", i, "FLOATING_LABEL",
                                             floating_label_message(lab)))
                        elif lab in RETIRED_LABELS:
                            findings.append(("HIGH", i, "RETIRED_LABEL",
                                             retired_label_message(lab)))
            else:
                mb = LIST_KEY_RE.match(line)
                if mb and (mb.group(1) == "os"
                           or mb.group(1) in matrix_keys):
                    for raw in mb.group(2).split(","):
                        lab = raw.split("#")[0].strip(" '\"")
                        if lab.endswith("-latest") and is_runner_label(lab):
                            findings.append(("HIGH", i, "FLOATING_LABEL",
                                             floating_label_message(
                                                 lab, " (referenced in a list, "
                                                 "e.g. a matrix axis)")))
                        elif lab in RETIRED_LABELS:
                            findings.append(("HIGH", i, "RETIRED_LABEL",
                                             retired_label_message(
                                                 lab, " (referenced in a list, "
                                                 "e.g. a matrix axis)")))
                else:
                    mi = LIST_ITEM_LABEL_RE.match(line)
                    if mi:
                        findings.append(("HIGH", i, "FLOATING_LABEL",
                                         floating_label_message(
                                             mi.group(1), " (referenced as a "
                                             "list item, e.g. a matrix axis or "
                                             "a multi-line runs-on list)")))
                    else:
                        mr = LIST_ITEM_RETIRED_RE.match(line)
                        if mr:
                            findings.append(("HIGH", i, "RETIRED_LABEL",
                                             retired_label_message(
                                                 mr.group(1),
                                                 " (referenced as a list "
                                                 "item, e.g. a matrix axis or "
                                                 "a multi-line runs-on list)")))
            m = USES_RE.search(line)
            if m:
                ref = m.group(1).strip("'\"")
                if "@" in ref and not ref.startswith(("./", "docker://")):
                    name, _, version = ref.rpartition("@")
                    if not SHA_RE.match(version):
                        findings.append(("WARN", i, "UNPINNED_ACTION",
                                         f"action '{name}' is referenced by mutable tag '{version}', "
                                         "not a full commit SHA; the tag can move under you."))
        if on_ubuntu and is_run_line:
            for cmd in command_heads(run_text):
                if cmd in REMOVED_COMMANDS:
                    findings.append(("HIGH", i, "REMOVED_TOOL", REMOVED_COMMANDS[cmd] + "."))
            for rx, tool, msg in DEFAULT_DRIFT:
                if setup_present.get(tool) or tool in seen_drift:
                    continue
                if rx.search(QUOTE_RE.sub(" ", run_text)):
                    findings.append(("WARN", i, "DEFAULT_DRIFT", msg + "."))
                    seen_drift.add(tool)
                    break
    return findings


SARIF_RULES = {
    "FLOATING_LABEL": (
        "Floating runner label",
        "A runs-on label such as ubuntu-latest moves to a new runner "
        "image on the provider's schedule; pin a versioned label."),
    "RETIRED_LABEL": (
        "Retired runner label",
        "A runs-on label whose runner image is retired on a published "
        "date (macos-14 family, removed November 2, 2026); jobs using "
        "it fail during scheduled brownouts before that date and stop "
        "working entirely afterwards. Move to a supported label."),
    "INDIRECT_RUNS_ON": (
        "Runner label supplied indirectly",
        "A runs-on value fed by an env/vars/inputs expression cannot be "
        "resolved by this scanner; check and pin it where it is set."),
    "UNPINNED_ACTION": (
        "Action referenced by a mutable tag",
        "An action referenced by a tag instead of a full commit SHA can "
        "move under you; pin to a full SHA where policy requires it."),
    "REMOVED_TOOL": (
        "Removed tool invoked",
        "A run step invokes a tool that was removed from the Ubuntu "
        "26.04 runner image."),
    "DEFAULT_DRIFT": (
        "Default tool version drift",
        "A tool's default version changes in the Ubuntu 26.04 runner "
        "image and no setup action pins it."),
}

SARIF_LEVEL = {"HIGH": "error", "WARN": "warning"}


def build_sarif(per_file, root):
    """Build a SARIF 2.1.0 log (as a dict) from [(path, findings), ...].

    Artifact URIs are made relative to the scanned root when the file
    lives under it, so Code Scanning can map results back to the repo.
    """
    rules = []
    for rule_id, (short, full) in SARIF_RULES.items():
        rules.append({
            "id": rule_id,
            "name": rule_id,
            "shortDescription": {"text": short},
            "fullDescription": {"text": full},
            "defaultConfiguration": {
                "level": "error" if rule_id in (
                    "FLOATING_LABEL", "RETIRED_LABEL",
                    "REMOVED_TOOL") else "warning",
            },
        })
    results = []
    for path, findings in per_file:
        uri = path
        try:
            rel = os.path.relpath(path, root)
            if not rel.startswith(".."):
                uri = rel
        except ValueError:
            pass
        uri = uri.replace(os.sep, "/")
        for sev, ln, rule, msg in findings:
            results.append({
                "ruleId": rule,
                "level": SARIF_LEVEL.get(sev, "warning"),
                "message": {"text": msg},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": uri},
                        "region": {"startLine": ln},
                    },
                }],
            })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "RunnerDriftAudit",
                "informationUri":
                    "https://github.com/alapha888/runner-drift-audit",
                "rules": rules,
            }},
            "results": results,
        }],
    }


def build_json_report(per_file, root):
    """Build the plain-JSON report (as a dict) from [(path, findings), ...].

    Paths are made relative to the scanned root when the file lives
    under it, matching the SARIF export. Every scanned file is listed,
    including files with no findings, so consumers can distinguish
    "scanned and clean" from "not scanned".
    """
    files = []
    total_high = 0
    total_warn = 0
    for path, findings in per_file:
        rel = path
        try:
            cand = os.path.relpath(path, root)
            if not cand.startswith(".."):
                rel = cand
        except ValueError:
            pass
        rel = rel.replace(os.sep, "/")
        entries = []
        for sev, ln, rule, msg in findings:
            if sev == "HIGH":
                total_high += 1
            elif sev == "WARN":
                total_warn += 1
            entries.append({
                "severity": sev,
                "line": ln,
                "rule": rule,
                "message": msg,
            })
        files.append({"path": rel, "findings": entries})
    return {
        "tool": "RunnerDriftAudit",
        "schema_version": 1,
        "summary": {
            "files_scanned": len(per_file),
            "high": total_high,
            "warn": total_warn,
            "findings": total_high + total_warn,
        },
        "files": files,
    }


def build_markdown_summary(per_file, root):
    """Build the Markdown job summary from [(path, findings), ...].

    Same relative-path and clean-file conventions as the JSON export:
    every scanned file appears, so "scanned and clean" is visible.
    Messages are escaped for the table cell they land in.
    """
    rep = build_json_report(per_file, root)
    s = rep["summary"]
    lines = [
        "## Runner Drift Audit",
        "",
        f"Scanned {s['files_scanned']} workflow file(s): "
        f"**{s['high']} HIGH**, **{s['warn']} WARN** "
        f"({s['findings']} finding(s) total).",
        "",
    ]
    if not per_file:
        lines.append("No workflow files were found to scan.")
        lines.append("")
        return "\n".join(lines)
    for entry in rep["files"]:
        lines.append(f"### `{entry['path']}`")
        lines.append("")
        if not entry["findings"]:
            lines.append("No findings.")
            lines.append("")
            continue
        lines.append("| Severity | Line | Rule | Finding |")
        lines.append("| --- | ---: | --- | --- |")
        for f in entry["findings"]:
            msg = f["message"].replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {f['severity']} | {f['line']} | {f['rule']} | {msg} |")
        lines.append("")
    lines.append(
        "Rule sources: actions/runner-images toolset-2404.json vs "
        "toolset-2604.json (ubuntu-latest moves 24.04 -> 26.04, "
        "Oct 19 - Nov 19, 2026); GitHub Changelog 2026-10-01 "
        "(macOS 14 runner image retirement, November 2, 2026).")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv):
    root = "."
    sarif_path = None
    json_path = None
    summary_path = None
    args = list(argv[1:])
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--sarif":
            if i + 1 >= len(args):
                raise SystemExit("--sarif requires a file path argument")
            sarif_path = args[i + 1]
            i += 2
        elif a.startswith("--sarif="):
            sarif_path = a.split("=", 1)[1]
            i += 1
        elif a == "--json":
            if i + 1 >= len(args):
                raise SystemExit("--json requires a file path argument")
            json_path = args[i + 1]
            i += 2
        elif a.startswith("--json="):
            json_path = a.split("=", 1)[1]
            i += 1
        elif a == "--summary-file":
            if i + 1 >= len(args):
                raise SystemExit("--summary-file requires a file path argument")
            summary_path = args[i + 1]
            i += 2
        elif a.startswith("--summary-file="):
            summary_path = a.split("=", 1)[1]
            i += 1
        elif a.startswith("--"):
            raise SystemExit(f"unknown option: {a}")
        else:
            root = a
            i += 1
    return root, sarif_path, json_path, summary_path


def main(argv):
    root, sarif_path, json_path, summary_path = parse_args(argv)
    files = find_workflows(root)
    if not files:
        print(f"No workflow files found under {root} (.github/workflows or *.yml/*.yaml).")
        if sarif_path:
            with open(sarif_path, "w", encoding="utf-8") as fh:
                json.dump(build_sarif([], root), fh, indent=2)
                fh.write("\n")
        if json_path:
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump(build_json_report([], root), fh, indent=2)
                fh.write("\n")
        if summary_path:
            with open(summary_path, "w", encoding="utf-8") as fh:
                fh.write(build_markdown_summary([], root))
        return 0
    total_high = 0
    per_file = []
    for path in files:
        findings = audit_file(path)
        per_file.append((path, findings))
        if not findings:
            print(f"OK      {path}")
            continue
        print(f"\n{path}")
        for sev, ln, rule, msg in findings:
            if sev == "HIGH":
                total_high += 1
            print(f"  [{sev}] line {ln} {rule}: {msg}")
    print(f"\nScanned {len(files)} workflow file(s); HIGH findings: {total_high}.")
    print("Rule sources: actions/runner-images toolset-2404.json vs toolset-2604.json; GitHub Changelog 2026-10-01 (macOS 14 retirement).")
    if sarif_path:
        with open(sarif_path, "w", encoding="utf-8") as fh:
            json.dump(build_sarif(per_file, root), fh, indent=2)
            fh.write("\n")
        print(f"SARIF report written to {sarif_path}.")
    if json_path:
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(build_json_report(per_file, root), fh, indent=2)
            fh.write("\n")
        print(f"JSON report written to {json_path}.")
    if summary_path:
        with open(summary_path, "w", encoding="utf-8") as fh:
            fh.write(build_markdown_summary(per_file, root))
        print(f"Markdown summary written to {summary_path}.")
    return 1 if total_high else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
