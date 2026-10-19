# Pinning default tool versions: working through the DEFAULT_DRIFT warnings

RunnerDriftAudit reports a `run:` step that uses a tool whose
image default changes in Ubuntu 26.04 — without a setup action pinning
it — as a WARN with the rule ID `DEFAULT_DRIFT`:

```text
[WARN] DEFAULT_DRIFT: Java default changes 17 -> 25 in the Ubuntu 26.04 image (and Java 8 is removed); pin with actions/setup-java.
```

This page is the remediation guide for that one rule: the eight tools
it covers and their exact version changes, how the scanner decides to
fire (and when it stays silent), how to pin each tool, and what a
re-scan should — and should not — show afterwards.

## The eight drifts

All eight come from the official `actions/runner-images` toolset diff
(`toolset-2404.json` vs `toolset-2604.json`, compared 2026-10-10):

| Tool | Ubuntu 24.04 default | Ubuntu 26.04 default | Scanner looks for |
|---|---|---|---|
| Java | 17 (Java 8 also present) | 25 (Java 8 removed) | `java`, `javac`, `mvn`, `gradle` |
| Node | 22 | 24 | `node`, `npm`, `npx` |
| PHP | 8.3 | 8.5 (only version shipped) | `php` |
| PostgreSQL | 16 | 18 | `psql`, `pg_ctl`, `postgres` |
| CMake | 3.31.6, held back on purpose to avoid CMake 4.0 issues | "latest", so CMake 4 behaviour may apply | `cmake` |
| clang | 18 | 21 | `clang` |
| Go | 1.24 | 1.26 | `go` followed by `build`, `test`, `run`, or `vet` |
| Docker / Compose | Docker 28, Compose 2.38.2 | Docker 29, Compose 5.1.3 | `docker compose` |

A default drift is not a removal. The tool is still there; it is a
different version than the one your last green run used, arriving on a
date the provider chose. That is why the scanner grades it WARN, not
HIGH — and why the fix is to state the version you actually depend on,
not to wait for the image to change under you.

## How the scanner decides

The check is narrower than a full reading of your workflow, and the
edges matter when a warning is missing — or stays:

- It only fires in files that mention `ubuntu-latest`, `ubuntu-24.04`,
  or `ubuntu-26.04` anywhere in the file, and only inside `run:` steps
  (including multi-line `run: |` blocks).
- It reports **at most one drift per `run:` line** — the first matching
  tool in the scanner's order (Java, Node, PHP, PostgreSQL, CMake,
  clang, Go, Docker) — and at most one warning per tool per file. A
  single line such as
  `java -version && node --version && psql --version` surfaces only
  the Java warning on that line. The other tools are not cleared;
  they are hidden behind the first match. Split the commands onto
  separate lines, or work through the table above tool by tool,
  before you treat a clean re-scan as complete.
- For Java, Node, PHP, and Go, the warning is suppressed if the
  matching setup action's name — `setup-java`, `setup-node`,
  `setup-php`, `setup-go` — appears anywhere in the same file. That
  is a substring heuristic, not a version check: the scanner does not
  verify that the setup step pins the version you intended, or that
  it runs before the step that uses the tool. Read the setup step
  yourself.
- For PostgreSQL, CMake, clang, and Docker there is no setup action
  in the scanner's table, so nothing suppresses the warning. Pinning
  them (below) is still the right fix — but the WARN will keep
  appearing in reports afterwards. Record those lines as
  checked-and-pinned rather than chasing a zero count.

## Pinning the four setup-action tools

Pin the version you are on today if you are not ready to move, or the
new version if you are moving deliberately. Either way the version
stops being the image's choice.

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '17'   # stay on 17; '25' to move deliberately.
                         # There is no staying on Java 8: it is removed.
- uses: actions/setup-node@v4
  with:
    node-version: '22'   # stay on 22; '24' to move
- uses: shivammathur/setup-php@v2
  with:
    php-version: '8.3'   # stay on 8.3; '8.5' to move (26.04 ships only 8.5 natively)
- uses: actions/setup-go@v5
  with:
    go-version: '1.24'   # stay on 1.24; '1.26' to move
```

Note the Go detection edge: the scanner only recognises `go` when it
is followed by `build`, `test`, `run`, or `vet`. A workflow that only
runs, for example, `go vet` is covered; one that calls other `go`
subcommands may rely on the default without a warning. If you use Go
at all through the image default, pin it anyway.

## Pinning the four manual tools

These four have no setup action in the scanner's table. The pin is an
explicit version in the place the version is actually decided:

- **PostgreSQL** — pin the service or the install, not the client
  call. If `psql` talks to a service container, state the image:
  `services: postgres: image: postgres:16` to stay on 16, or
  `postgres:18` to move — and test the move, because a major-version
  change is a data-format and behaviour change, not just a client
  bump. If you rely on the image's preinstalled server, install a
  named version explicitly instead.
- **CMake** — the 24.04 image held CMake at 3.31.6 specifically to
  avoid CMake 4.0 compatibility issues; the 26.04 image ships
  "latest", so CMake 4 behaviour may apply to an unpinned build. If
  your build depends on pre-4 behaviour, add an explicit install step
  for the CMake version you tested with, before the first `cmake`
  call. If it does not, test once against the new default and record
  that you did.
- **clang** — the default moves 18 → 21, and the versioned
  `clang-16` / `clang-17` commands are removed outright (those are
  reported separately as HIGH `REMOVED_TOOL` findings, not drift).
  Call a versioned binary that exists in the 26.04 image, or install
  a named `clang-<version>` package, and set `CC` / `CXX` explicitly
  if your build picks the compiler up from the environment.
- **Docker Compose** — Compose jumps 2.38.2 → 5.1.3 alongside Docker
  28 → 29. Test your compose files against Compose v5 before the
  window closes; if a file depends on v2 behaviour, install the
  Compose version you tested with as an explicit step instead of
  relying on the preinstalled one.

In all four cases the scanner will still report the WARN after you
pin, for the reason above. Note the pin next to the baseline report
so a reviewer can see the warning was acted on, not ignored.

## Re-scanning

After pinning, re-run the same scan and compare with the baseline:

```bash
python3 runner_drift_audit.py path/to/your-repo --json after.json --summary-file after-summary.md
```

Expected: the setup-action drifts you pinned are gone, the four
manual-tool warnings may remain (recorded as checked-and-pinned), and
no *new* line appears. A drift that vanishes because you merged two
commands onto one line has not been fixed — see the one-per-line
limit above.

## Limits

This is a line scanner with shell-aware heuristics, not a full YAML
or shell parser. It does not read the version a setup step requests,
does not resolve versions set outside the workflow file, and does
not inspect container images. Treat its findings as a review
checklist, not as proof that a build is safe. It does not execute
workflows.

---

RunnerDriftAudit is a free, single-file scanner (MIT) for GitHub
Actions workflow drift — floating and retired runner labels, removed
tools, default-version drift, and unpinned action refs. The multi-repo
edition with one combined HTML report is
[RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra)
($29 one-time).
