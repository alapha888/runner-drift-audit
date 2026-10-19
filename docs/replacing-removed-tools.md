# Replacing removed tools: working through the REMOVED_TOOL findings

RunnerDriftAudit reports a `run:` step that invokes a tool removed
from the Ubuntu 26.04 runner image as a HIGH with the rule ID
`REMOVED_TOOL`:

```text
[HIGH] REMOVED_TOOL: mercurial was removed from the Ubuntu 26.04 runner image.
```

This page is the remediation guide for that one rule: the 19 command
names it covers and how they group, how the scanner decides to fire
(and what it cannot see), the fix path for each group, and what a
re-scan should show afterwards.

Unlike a default-version drift, a removal is not a silent change.
The tool is not there at a different version — it is not there at
all, so the step that calls it fails. That is why the scanner grades
this rule HIGH, not WARN, and why the exit code is 1 while any
`REMOVED_TOOL` finding remains.

## The 19 commands, in four groups plus one rename

All entries come from the scanner's own `REMOVED_COMMANDS` table,
which is grounded in the official `actions/runner-images` toolset
diff (`toolset-2404.json` vs `toolset-2604.json`, compared
2026-10-10). The wording after each group is the scanner's own
finding text.

### Removed outright

| Command | Finding text says |
|---|---|
| `hg` | mercurial was removed |
| `mediainfo` | mediainfo was removed |
| `sphinxsearch` | sphinxsearch was removed |
| `searchd` | sphinxsearch (searchd) was removed |
| `haveged` | haveged was removed |

`sphinxsearch` and `searchd` are two command names for the same
package; the scanner lists both because a workflow can call either.

### No longer preinstalled — a gem and the global Node tools

| Command | Finding text says |
|---|---|
| `fastlane` | the fastlane ruby gem is no longer preinstalled |
| `webpack` | no longer preinstalled globally (only `n` and `yarn` remain) |
| `gulp` | no longer preinstalled globally (only `n` and `yarn` remain) |
| `grunt` | no longer preinstalled globally (only `n` and `yarn` remain) |
| `parcel` | no longer preinstalled globally (only `n` and `yarn` remain) |
| `lerna` | no longer preinstalled globally (only `n` and `yarn` remain) |
| `newman` | no longer preinstalled globally (only `n` and `yarn` remain) |
| `tsc` | typescript (tsc) is no longer preinstalled globally (only `n` and `yarn` remain) |

These tools still exist as projects. What changed is that the image
no longer supplies them for free: a workflow that relied on the
global install has to supply the tool itself.

### Versioned compilers that were removed

| Command | What remains in the 26.04 image |
|---|---|
| `gcc-12` | gcc 13/14/15 remain |
| `g++-12` | g++ 13/14/15 remain (same wording as gcc) |
| `gfortran-12` | gfortran 13/14/15 remain |
| `clang-16` | clang 20/21/22 remain |
| `clang-17` | clang 20/21/22 remain |

Note the boundary with the drift rule: an unversioned `clang` call
is a `DEFAULT_DRIFT` WARN (the default moves 18 → 21). Only the
versioned `clang-16` / `clang-17` commands are removals, and only
those are HIGH here.

### One rename, reported in the same rule

| Command | Finding text says |
|---|---|
| `p7zip` | p7zip-full was replaced by 7zip; check 7z invocations and package names |

This one is not a disappearance: the package changed name from
`p7zip-full` to `7zip`. The scanner flags the `p7zip` command head;
it does not flag `7z` itself. What needs checking is any place your
workflow names the old package or assumes the old package's
contents.

### What is not in this rule

- Java 8 is also removed in 26.04, but there is no `java8` command
  in the table. Java appears in this scanner as a `DEFAULT_DRIFT`
  WARN (default 17 → 25, with Java 8 removed noted in the message);
  see the [pinning guide](pinning-default-versions.md).
- A tool that is merely at a new default version — Node, PHP,
  PostgreSQL, Go, CMake, Docker — is drift, not removal, and is
  covered by the same pinning guide.

## How the scanner decides

The check is narrower than a full reading of your workflow, and the
edges matter when a finding is missing — or unexpected:

- It only fires in files that mention `ubuntu-latest`,
  `ubuntu-24.04`, or `ubuntu-26.04` anywhere in the file, and only
  inside `run:` steps (including multi-line `run: |` blocks). The
  same command in a workflow that runs only on Windows or macOS
  runners is not flagged, because the removal is specific to the
  Ubuntu 26.04 image.
- It matches the **command head** of each shell segment — the first
  command word after splitting on `&&`, `||`, `;`, and `|` — and it
  sees through common prefixes (`sudo`, `env`, `command`, `time`,
  `xargs`, and `VAR=value` assignments) and quoted strings. So
  `sudo hg log` and `FOO=1 hg log` are both caught.
- The match is on the exact command name. A longer word that merely
  contains one — a script named `hg-helper`, a path, or an argument
  such as `echo hg` (where `hg` is not a command head) — is not a
  `REMOVED_TOOL` finding.
- Unlike `DEFAULT_DRIFT`, there is no one-per-tool or one-per-line
  cap and no setup-action suppression: every segment whose head is
  in the table is reported, at its own line. Ten calls to removed
  tools are ten findings. That is deliberate — each call site is a
  separate step that will fail.

## Fixing each group

The general shape is the same in every group: replace the call,
drop the step, or install the tool explicitly in a setup step
before the step that uses it. Installing explicitly means the
version becomes your workflow's choice instead of the image's —
pin it where you can, for the same reason as in the pinning guides.

### Removed outright

- **`hg`** — install mercurial explicitly in a setup step, or
  migrate the step to git if the Mercurial use was incidental (for
  example, a version stamp that could come from the git checkout
  instead).
- **`mediainfo`** — install mediainfo explicitly in a setup step
  before the step that reads media metadata.
- **`sphinxsearch` / `searchd`** — install sphinxsearch explicitly,
  or replace the search step with whatever now serves that role.
  Fix both command names if your workflow uses both.
- **`haveged`** — remove the haveged step, or install it
  explicitly. Before reinstalling, check what the step was for:
  entropy workarounds carried forward for years are often no longer
  load-bearing, and a step that can be dropped should be dropped
  rather than re-supplied.

### The gem and the global Node tools

- **`fastlane`** — install the gem explicitly in a setup step
  before the first `fastlane` call.
- **`webpack`, `gulp`, `grunt`, `parcel`, `lerna`, `newman`,
  `tsc`** — add the tool as a local `devDependency` of the project,
  or call it via `npx`. A local dependency is the more durable of
  the two: the version is then recorded in the project, not
  resolved fresh from the registry on each run. Either way, the
  fix is to stop relying on the image supplying a global copy —
  on 26.04 only `n` and `yarn` remain globally installed.

### Versioned compilers

- **`gcc-12` / `g++-12` / `gfortran-12`** — move to gcc/g++/gfortran
  13–15, which remain in the image, or install 12 explicitly if a
  build genuinely depends on it. Moving majors is a compiler
  change, not a rename: expect new warnings and occasionally new
  errors, and give the move its own run rather than bundling it
  with the runner migration.
- **`clang-16` / `clang-17`** — move to clang 20–22, which remain
  in the image, or install the old version explicitly. The same
  caution applies: this is a compiler upgrade with its own fallout,
  separate from the label move.

### The rename

- **`p7zip`** — check `7z` invocations and package names against
  the replacement `7zip` package. If a setup step installs
  `p7zip-full` by name, that name is what changed; the `7z` calls
  themselves may need no change, but confirm against the new
  package rather than assuming.

## What a re-scan should show

- A fixed call site stops reporting. There is no
  checked-and-pinned residue for this rule, unlike PostgreSQL /
  CMake / clang / Docker in the drift guide: once no `run:` step
  invokes a removed command head, the file has no `REMOVED_TOOL`
  findings, and if those were the only HIGH findings, the exit
  code returns to 0.
- If you fixed a finding by installing the tool explicitly, the
  install step itself will usually not be flagged — an
  `apt-get install` line's command head is the installer, not the
  removed tool. That silence is correct behaviour, not proof: read
  the install step yourself and confirm it names the tool and runs
  before the step that uses it.
- If a finding remains after you believed a step was fixed, the
  usual cause is a second call site — another segment, another
  file, or the other command name of a pair (`sphinxsearch` fixed,
  `searchd` still called). Work through the report line by line
  rather than fixing the first hit and re-running once.

## Limits

This is a line scanner with shell-aware heuristics, not a full
YAML or shell parser, and this guide inherits those limits. A
removed tool invoked through a script file, a Makefile, or another
level of indirection the scanner cannot see in the workflow file
will not be reported. Treat a clean scan as "no removed-tool call
heads in the scanned `run:` steps", not as proof that no step can
reach a removed tool.
