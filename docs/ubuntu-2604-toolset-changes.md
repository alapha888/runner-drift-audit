# Ubuntu 26.04 toolset changes — every difference in tables

GitHub starts moving the `ubuntu-latest` label from Ubuntu 24.04 to Ubuntu 26.04 on **October 19, 2026**, with the rollout running through November 19. Your workflow files do not change — the machine underneath them does.

This page is the human-readable, per-tool version of the diff between GitHub's two official runner-image toolsets (`toolset-2404.json` vs `toolset-2604.json`) — the companion to the process checklist in the [README](https://github.com/alapha888/runner-drift-audit#migration-checklist). The machine-readable version ships in this repository as `toolset-differences-2404-2604.csv`, and [RunnerDriftAudit](https://github.com/alapha888/runner-drift-audit) scans your workflows against it automatically.

## Removed outright — calls to these will fail

| Tool | Ubuntu 24.04 | Ubuntu 26.04 | What to do |
|---|---|---|---|
| mercurial (`hg`) | preinstalled | removed | Install mercurial explicitly, or migrate to git |
| mediainfo | preinstalled | removed | Install mediainfo explicitly in a setup step |
| sphinxsearch (`searchd`) | preinstalled | removed | Install sphinxsearch explicitly, or replace the search step |
| haveged | preinstalled | removed | Remove the haveged step, or install it explicitly |
| Java 8 | available | removed | Move to a supported Java version and pin with `actions/setup-java` |
| gcc-12 / gfortran-12 | available | removed (13/14/15 remain) | Move to gcc/gfortran 13–15, or install 12 explicitly |
| clang-16 / clang-17 | available | removed (20/21/22 remain) | Move to clang 20–22, or install the old version explicitly |

## No longer installed globally — local calls will fail

On Ubuntu 26.04 the only globally installed Node tools left are `n` and `yarn`. Workflows that call any of these without a local install will fail:

- `webpack`, `gulp`, `grunt`, `parcel`, `lerna`, `newman`, `tsc` (TypeScript) — add a local `devDependency`, or call via `npx`.
- `fastlane` (Ruby gem) — no longer bundled with RubyGems; install it explicitly in a setup step.

## Renamed

| Tool | Ubuntu 24.04 | Ubuntu 26.04 | What to do |
|---|---|---|---|
| p7zip | `p7zip-full` | `7zip` | Check `7z` invocations and package names against `7zip` |

## Default versions that jump when nothing pins them

These do not fail loudly — they silently build on a new major version:

| Tool | Ubuntu 24.04 default | Ubuntu 26.04 default | What to do |
|---|---|---|---|
| Java | 17 | 25 | Pin with `actions/setup-java` |
| Node | 22 | 24 | Pin with `actions/setup-node` |
| PHP | 8.3 | 8.5 only | Pin with `shivammathur/setup-php` |
| PostgreSQL | 16 | 18 | Pin a PostgreSQL version explicitly |
| clang | 18 | 21 | Pin a clang version explicitly |
| Go | 1.24 | 1.26 | Pin with `actions/setup-go` |
| Docker / Docker Compose | 28 / 2.38.2 | 29.4.2 / 5.1.3 | Test compose files against Compose v5 and pin where needed |
| CMake | 3.31.6 (held back to avoid CMake 4.0 issues) | latest | Pin a CMake version explicitly if CMake 4 is not yet adopted |

## Check your workflows in one command

```bash
python3 runner_drift_audit.py path/to/your-repo
```

RunnerDriftAudit reports each risk at the exact line — floating `ubuntu-latest` labels (including labels supplied through matrix axes or referenced `env` keys), removed tools invoked in `run` steps, default-version drift where no setup action pins a version, and actions referenced by mutable tags instead of full commit SHAs. Findings are graded HIGH and WARN, and the exit code is 1 whenever a HIGH exists, so it can gate a CI job.

Free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home. It is a line scanner with shell-aware heuristics, not a full YAML or shell parser — treat the findings as a review checklist, not as proof that a build is safe.

Maintaining many repositories? [RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra) ($29 one-time) scans a whole workspace of repositories and merges everything into a single HTML report. The free single-repo tool above stays free and open source either way.
