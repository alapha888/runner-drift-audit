# Resolving indirect runner labels: working through the INDIRECT_RUNS_ON warnings

RunnerDriftAudit reports a `runs-on:` value that is fed by a single
`env` / `vars` / `inputs` expression — and that it cannot resolve from
the file it is reading — as a WARN with the rule ID
`INDIRECT_RUNS_ON`:

```text
[WARN] INDIRECT_RUNS_ON: runner label is fed by the expression '${{ vars.RUNNER_LABEL }}' and this scanner cannot resolve it; check where that value is set (env defaults in this file, repository variables, or caller inputs) and pin it there if it floats.
```

This page is the remediation guide for that one rule: exactly which
`runs-on:` forms trigger it, the one in-file case the scanner *can*
resolve (and therefore does not warn about), where each kind of value
is actually set, how to pin it there, and what a re-scan should — and
should not — show afterwards. With this page, all six of the scanner's
rule IDs have a dedicated remediation guide.

## What the warning means — and what it does not

This warning is not a verdict that your runner label floats or is
retired. It is the opposite of a verdict: the scanner is saying the
label is not written in the file, so it cannot judge it at all.

That matters because the risk is the same shape as a floating label,
one hop further away. If the value behind the expression is
`ubuntu-latest`, the job still moves from 24.04 to 26.04 on the
provider's schedule (October 19 – November 19, 2026). If it is
`macos-14`, the job still fails in the October brownouts and stops
working on November 2, 2026. The scanner just cannot see which — if
either — is true, because the value lives somewhere else.

It is graded WARN, not HIGH, for exactly that reason: an unresolved
value might already be pinned correctly at its source. The work this
warning asks for is a lookup and, if needed, a pin at the source —
not an automatic edit to the `runs-on:` line.

## Exactly what triggers it

The match is deliberately narrow. All of these must hold:

- The `runs-on:` value is **exactly one** expression of the form
  `${{ env.<name> }}`, `${{ vars.<name> }}`, or
  `${{ inputs.<name> }}` — nothing else in the value. Optional quotes
  around the whole expression are allowed.
- That value is **not resolved in the same file** (next section).

Forms that do **not** produce this warning:

- **Compound expressions** — a ternary, `fromJSON(...)`, or any
  expression with operators or function calls, such as
  `${{ inputs.arch == 'arm' && 'ubuntu-22.04' || 'ubuntu-24.04' }}`.
  The scanner does not match them at all, on the grounds that every
  branch can be pinned in the same line. It also gives them no
  verdict from that line: read compound expressions yourself.
- **Matrix references** — `runs-on: ${{ matrix.os }}` is not
  indirect in this sense. Matrix values written in the same file are
  judged directly at the matrix lines (floating and retired labels
  there are HIGH findings, not this WARN).
- **A plain literal label** — `runs-on: ubuntu-24.04` is judged
  directly: clean if supported, HIGH if floating or retired.

## The one case the scanner can resolve: `env` set in the same file

If the expression is `${{ env.<name> }}` and the same file contains a
plain scalar assignment of a runner label to that name — for example
`MY_RUNNER: ubuntu-latest` under an `env:` block — the scanner
resolves it instead of warning:

- A floating label (`*-latest`) is reported as HIGH `FLOATING_LABEL`.
- A retired label (`macos-14` family) is reported as HIGH
  `RETIRED_LABEL`.
- A supported pinned label (such as `ubuntu-24.04`) resolves clean:
  no `INDIRECT_RUNS_ON`, no other finding for that job's label.

Where the HIGH is reported depends on the key name. A `*RUNNER*`-named
key, or a key referenced as a matrix key, is flagged at the
**assignment line**. Any other key name is judged at the **`runs-on:`
line**, with the message noting it was set by `env.<name>` in this
file. Either way there is no additional `INDIRECT_RUNS_ON` line for
the same job — one finding, not two.

This resolution only applies to `env`, and only to a plain label
assignment in the same file. It does not apply when:

- the `env` value is itself built from an expression, set in another
  file, or supplied by the runner environment — there is no plain
  assignment in this file to resolve, so the warning fires;
- the source is `vars` or `inputs` — see below. Even a default that
  happens to be visible in this file does not resolve those, because
  the effective value can be overridden where the variable is set or
  by the caller who passes the input.

## Where each kind of value is actually set

| Source | Where the effective value lives | Who can change it |
|---|---|---|
| `env.<name>` | An `env:` block in this workflow (workflow, job, or step level), another file, or the runner environment — the scanner only resolves a plain assignment in this same file | Anyone who can edit the workflow, or whatever sets the environment |
| `vars.<name>` | Repository, organisation, or environment variables under Settings → Secrets and variables → Actions → Variables — never in the workflow file | Repository / organisation administrators |
| `inputs.<name>` | The caller: a `workflow_call` caller in another workflow or repository, or the person dispatching a `workflow_dispatch` run. A `default:` under `on:` in this file applies only when the caller passes nothing | The caller's maintainers, per run |

## Fix paths, by source

Start with the lookup: find the current effective value first. Do not
pin blind. If the value is already a supported pinned label, the fix
is documentation, not an edit (see re-scan expectations below).

**`env` — pin at the assignment, in the file.** Find the assignment
and change the label there to a pinned one (`ubuntu-24.04` to stay,
`ubuntu-26.04` to migrate deliberately, `macos-15` in place of
`macos-14`). If there is no assignment in this file — the value comes
from elsewhere — either add an explicit assignment here or replace
the expression with the literal pinned label.

**`vars` — pin in Settings, and note the blast radius.** Open
Settings → Secrets and variables → Actions → Variables, find the
variable, and set it to a pinned label. Changing a repository
variable changes every workflow that reads it, in the same moment —
check the other readers before you change a shared variable, or give
this workflow its own variable / literal label instead.

**`inputs` — pin the default *and* check the callers.** Set the
`default:` for the input under `on.workflow_call.inputs` /
`on.workflow_dispatch.inputs` to a pinned label, then search for
callers that pass the input explicitly — a pinned default does
nothing for a caller that overrides it with a floating or retired
label. Scan caller workflows separately; their `runs-on:` and input
values are outside the files this run reads.

**Any source — inlining is the blunt, reliable option.** Replacing
the expression with the literal label (`runs-on: ubuntu-24.04`)
removes the indirection entirely and lets every future scan judge the
job directly. Prefer it when the variability was not buying anything.
Keep the expression when different callers or environments genuinely
need different runners — and accept the standing warning as the price
(see below).

## What a re-scan should show

This rule's re-scan expectations are different from the other five,
and reading them wrong creates false alarms in both directions:

- **Inlined a pinned literal:** the `INDIRECT_RUNS_ON` line is gone
  and nothing replaces it. Done.
- **Inlined or resolved to a floating / retired label:** the WARN is
  replaced by a HIGH `FLOATING_LABEL` / `RETIRED_LABEL`. That is
  progress, not a regression — an unjudged risk became a judged one.
  Now follow that rule's guide.
- **Pinned an in-file `env` assignment:** the warning is gone; a
  supported pinned label resolves clean, as above.
- **Pinned a `vars` value in Settings, or an `inputs` default /
  caller value:** the `INDIRECT_RUNS_ON` line **stays**. The scanner
  cannot read repository settings or caller repositories, so it
  cannot confirm your fix. This is by design, in the same way some
  `DEFAULT_DRIFT` warnings stay visible after pinning. Closure here
  is a written record — "checked `vars.RUNNER_LABEL` on <date>: set
  to `ubuntu-24.04`" kept with the migration PR — not a zero count.
  Treat a *new* `INDIRECT_RUNS_ON` line (a name or file you had not
  seen before) as a real new item to look up, not noise.

## What this page does not do

- It does not follow indirection further. Composite actions and
  reusable workflows in other files or repositories are not followed
  into — scan those targets separately.
- It does not judge compound expressions. A ternary that selects
  between two pinned labels and a ternary that selects a floating
  label look identical to this rule: neither is flagged. That review
  is manual.
- It does not argue for removing all indirection. Parameterised
  runners are a legitimate pattern for reusable workflows and test
  matrices. The warning only asks that somebody has looked at what
  the parameter actually resolves to — and can show when they did.

---

RunnerDriftAudit is a free, single-file scanner (MIT) for GitHub
Actions workflow drift — floating and retired runner labels, removed
tools, default-version drift, unpinned action refs, and indirect
runner labels. The multi-repo edition with one combined HTML report is
[RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra)
($29 one-time).
