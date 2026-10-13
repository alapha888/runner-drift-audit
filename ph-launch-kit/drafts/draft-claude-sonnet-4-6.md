---

**1. TAGLINE**

Audit your CI before ubuntu-latest changes under you.

---

**2. DESCRIPTION**

On October 19, 2026, GitHub begins migrating the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04. Nothing in your repository changes — the machine underneath your CI does.

A diff of GitHub's official runner-images toolsets reveals 22 differences that can break or silently alter builds: removed tools (mercurial, mediainfo, webpack/gulp/grunt global installs, gcc-12, clang-16/17, p7zip), default-version jumps (Java 17→25 with Java 8 removed, Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, Go 1.24→1.26, Docker 28→29), and unpinned CMake.

RunnerDriftAudit scans your GitHub Actions workflow files and reports, line by line: floating `ubuntu-latest` labels, removed tools invoked in run steps, default-version drift where no setup action pins a version, and actions referenced by mutable tags instead of commit SHAs. Findings are graded HIGH or WARN. Exit code 1 on any HIGH finding lets it gate a CI job.

Free, MIT-licensed, single Python file, zero dependencies.

---

**3. TOPICS**

- GitHub Actions
- Developer Tools
- Open Source
- CI/CD
- Command Line

---

**4. MAKER FIRST COMMENT**

I built this because the `ubuntu-latest` label is the problem no linter warns you about. Your YAML stays untouched; the machine underneath just changes. The migration window opens October 19 and runs through November 19 — plenty of time for a quiet breakage to reach production before anyone traces it back to the runner.

The rules aren't invented. GitHub publishes the official toolset JSON files for both runner images. I diffed `toolset-2404.json` against `toolset-2604.json` and encoded what I found: 22 differences covering removed tools, version jumps, and gaps. The tool scans workflow files line by line against those rules.

On the bundled "bad" sample workflow it surfaces 3 HIGH findings (floating label, removed mercurial, removed webpack) and 3 WARN findings (Java default jump, unpinned CMake, mutable action tag). On the "clean" sample it reports 0 HIGH.

Worth being honest about the limits: this is a line scanner with heuristics, not a full YAML parser or shell interpreter. It will miss things a real execution would catch. Treat the output as a structured review checklist, not a proof of safety.

Genuinely curious — what does this migration break in your own CI? Drop a comment; it'll help me know which checks matter most.
