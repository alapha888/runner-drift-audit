**TAGLINE**
Audit GitHub Actions for the Ubuntu 26.04 runner migration

**DESCRIPTION**
GitHub is transitioning the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04 between October 19 and November 19, 2026. Your workflow code does not change, but the underlying runner image does. 

A diff of GitHub's official toolset specifications (toolset-2404.json vs. toolset-2604.json) reveals 22 differences that can break CI builds: removed tools (including mercurial, mediainfo, global webpack/gulp/grunt, p7zip, gcc-12, clang-16/17), default runtime jumps (such as Java 17 to 25 with Java 8 dropped, Node 22 to 24, PHP 8.3 to 8.5, and Docker 28 to 29), and unpinned CMake setups.

RunnerDriftAudit is a free, MIT-licensed command-line tool packaged as a single Python file using only the standard library with zero third-party dependencies. It inspects your `.github/workflows/` files line by line, reporting floating runner labels, calls to removed binaries, unpinned runtime version drift, and mutable action tags. 

Findings are graded HIGH or WARN. The CLI exits with code 1 when any HIGH finding is detected, making it easy to run locally or enforce as a CI gating check.

**TOPICS**
- Developer Tools
- GitHub
- DevOps
- Open Source

**MAKER FIRST COMMENT**
Hey Product Hunt,

I built RunnerDriftAudit because GitHub moves `ubuntu-latest` under running workflows without requiring any commit from you. The official runner-images diff is public, but almost nobody has time to manually cross-reference two multi-thousand-line JSON toolset files against their workflow steps.

I extracted 22 concrete changes between `toolset-2404.json` and `toolset-2604.json`—spanning dropped CLI utilities, removed compiler revisions, and default runtime upgrades—and turned them into audit rules. On our bundled test workflows, the tool flags 3 HIGH and 3 WARN items on the messy sample (catching floating labels, removed mercurial and webpack calls, runtime drift, and mutable tags), while returning 0 HIGH on the clean sample.

To be clear about its limits: this is a static scanner using targeted heuristics, not a full AST shell or YAML evaluator. Its findings are designed as an actionable triage checklist before October 19, not formal proof of build correctness.

If you test your workflows with it, what breaking changes or version surprises did the Ubuntu 26.04 transition uncover in your setup?
