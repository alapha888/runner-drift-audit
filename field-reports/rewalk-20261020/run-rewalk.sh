#!/bin/bash
# Oct-20 post-cutover re-walk runner — implements the protocol pinned in
# field-reports/2026-10-13-pre-cutover-self-audit.md (Addendum, late evening).
# Usage: bash run-rewalk.sh [output_dir]
# Baseline is frozen at scanner v0.3.2 / the 2026-10-13 report. This script
# records the scanner version actually used, so scanner-growth rows can be
# separated from migration rows in the delta report.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
OUT="${1:-$HERE/output}"
mkdir -p "$OUT"
SCANNER="$REPO/runner_drift_audit.py"

{
  echo "# Re-walk run metadata"
  echo "- Date: $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC)"
  echo "- Scanner file: $SCANNER"
  echo "- Scanner SHA256: $(shasum -a 256 "$SCANNER" | awk '{print $1}')"
  if [ -d "$REPO/.git" ]; then
    echo "- Scanner repo HEAD: $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo unknown)"
    echo "- Latest release tag (gh): $(gh release list --repo alapha888/runner-drift-audit --limit 1 2>/dev/null || echo 'gh unavailable — fill in manually')"
  fi
  echo "- Baseline: v0.3.2, field-reports/2026-10-13-pre-cutover-self-audit.md (frozen, do not edit)"
  echo "- Protocol: same inventory, same order; rows that moved inert->flagged and rows that did not move are both reported."
} > "$OUT/metadata.md"

run_one () {
  name="$1"; target="$2"
  echo "=== $name :: $target ==="
  python3 "$SCANNER" "$target" 2>&1 | tee "$OUT/scan-$name.txt"
  echo
}
{
  run_one "cn-ai-coding-workflow" "$HOME/workspace/independent/cn-ai-coding-workflow"
  run_one "cn-ai-coding-workflow-lite" "$HOME/workspace/independent/cn-ai-coding-workflow-lite"
  # Baseline target 3 was pending-workflow-scope/self-test.yml (unpushed on
  # Oct 13, token lacked workflow scope). The file has since been pushed as
  # .github/workflows/self-test.yml (workflow scope granted; commit 662c3bd),
  # so the pending directory no longer exists. Scanning the repo root finds
  # exactly that file and reproduces the baseline (0 HIGH / 2 WARN) — verified
  # on the Oct 19 day-1 snapshot. This is a path move, not a migration delta.
  run_one "self-test" "$REPO"
} > "$OUT/scans-all.txt"

echo "Outputs in $OUT : metadata.md, scans-all.txt, scan-*.txt"
echo "Next: fill 2026-10-20-post-cutover-self-audit-SKELETON.md row by row from scans-all.txt."
