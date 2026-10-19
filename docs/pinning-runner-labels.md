# Pinning floating runner labels: working through the FLOATING_LABEL findings

RunnerDriftAudit reports a runner label that ends in `-latest` as a
HIGH finding with the rule ID `FLOATING_LABEL`:

```text
[HIGH] line 5 FLOATING_LABEL: runner label 'ubuntu-latest' is a floating label; it moves 24.04 -> 26.04 between Oct 19 and Nov 19, 2026. Pin ubuntu-24.04 to stay, or ubuntu-26.04 to migrate deliberately.
```

This page is the remediation guide for that one rule: which labels it
covers, how the scanner finds them (including the forms that hide in a
matrix or behind an `env` key), the two deliberate choices for the
Ubuntu label, what to do with the other `-latest` labels, and what a
re-scan should show afterwards.

## Why a floating label is HIGH, not WARN

A floating label is not a version. It is a promise by the provider to
point the name at a newer image on the provider's schedule. For
`ubuntu-latest` that schedule is published and already running: the
label moves from Ubuntu 24.04 to Ubuntu 26.04 between **October 19 and
November 19, 2026**. Nothing in your repository changes — the machine
underneath your CI does — and during the window the same workflow can
land on either image from one run to the next.

That is why the scanner grades it HIGH. A pinned label states the
image you tested against. A floating label states that you accept
whichever image is current on the day the job happens to run,
including the day the image changes underneath a release.

## The two messages

The scanner writes a different message depending on the label, and
the difference matters:

- **`ubuntu-latest`** gets the dated message above: the move, the
  window (October 19 – November 19, 2026), and the two pins. This is
  the only label whose move this scanner tracks, because it is the
  only one grounded in the `actions/runner-images` toolset diff the
  rules are built from.
- **Any other `-latest` label** (`windows-latest`, `macos-latest`,
  and the rest) gets a generic message: the label "moves to a new
  image generation on the provider's schedule, outside this scanner's
  Ubuntu migration window", with the advice to pin a versioned label
  if the job needs to stay stable. The scanner does not claim a date
  or a toolset change for these labels — it does not have one. Treat
  the finding as "this job's image is not under your control", not as
  a migration warning with a deadline.

## How the scanner finds floating labels

The check is a line scanner, and it looks in more places than the
`runs-on:` line itself — because that is where floating labels hide:

- **Directly on `runs-on:`** — scalar (`runs-on: ubuntu-latest`),
  quoted, and inline-list (`runs-on: [ubuntu-latest]`) forms.
- **In a bracket list on an `os` axis, or on a key the file actually
  references as `matrix.<key>`** — the usual matrix case,
  `os: [ubuntu-latest, windows-latest]`. Bracket lists on other keys
  are deliberately not flagged: a `- docker-latest` argument or a
  `browser: [chrome-latest]` axis is not a runner label.
- **As a bare list item** carrying an `ubuntu-` / `windows-` /
  `macos-` prefix — a block matrix axis, or a multi-line `runs-on:`
  list.
- **Assigned to a key one hop away** — a floating label assigned to a
  `*RUNNER*`-named key that the file references through an expression
  (for example an `env:` value read as `${{ env.MY_RUNNER }}`), or to
  a key referenced as `matrix.<key>` (for example a `matrix.include:`
  entry), is flagged at the assignment line. The same label assigned
  to a key nothing references — a report baseline, a test fixture —
  is not flagged.
- **Set by an `env` key in the same file** — when `runs-on:` is a
  single `${{ env.<key> }}` expression and the key is assigned a
  floating label in the file, the finding is reported at the
  `runs-on:` line with the source named.

One boundary to know: a `runs-on:` fed by a single `vars.*` /
`inputs.*` / unresolved `env.*` expression the scanner cannot resolve
from the file is **not** a `FLOATING_LABEL` finding. It is an
`INDIRECT_RUNS_ON` warning instead — see
[Resolving indirect runner labels](resolving-indirect-runs-on.md)
for that rule's fix paths.

## Fixing `ubuntu-latest`: the two deliberate choices

There is no third option that keeps the label floating and removes
the finding. The choice is which image you pin, and when:

1. **Pin `ubuntu-24.04` to stay.** The right choice when the
   repository is not ready to migrate. The job keeps running on the
   image it was tested against, the HIGH finding clears, and the
   migration becomes a separate, reviewed change you make on your
   own schedule — during the window, or after it. Staying is not
   free forever: 24.04 is the older image, and pinning is a decision
   to migrate later, not a decision to never migrate. Write the
   intended migration date in the PR that adds the pin.
2. **Pin `ubuntu-26.04` to migrate deliberately.** The right choice
   when you are ready — ideally after one branch run on
   `ubuntu-26.04` has exercised the new image on purpose, while
   `ubuntu-latest` may still resolve to 24.04. Work through the rest
   of the scan first: the
   [removed-tools guide](replacing-removed-tools.md) and the
   [default-drift guide](pinning-default-versions.md) cover the
   findings that decide whether a 26.04 run passes. The
   [rollout-week playbook](rollout-week-playbook.md) covers the
   window itself.

The one choice to avoid is the passive one: leaving `ubuntu-latest`
in place and letting the rollout pick the day your CI changes. That
is the outcome the HIGH grade exists to prevent.

Apply the same pin everywhere the label appears — the `runs-on:`
line, each matrix entry, and the assignment line if the label is set
through a key. A partial fix leaves a HIGH finding behind, which is
the scanner telling you a form was missed, not a false positive to
suppress.

## Fixing the other `-latest` labels

For `windows-latest`, `macos-latest`, and similar labels, pin the
current versioned label for that family (for example `macos-15`
instead of `macos-latest`) when the job needs a stable image. Two
honest qualifications:

- The scanner cannot tell you what changed between image generations
  for these families — its toolset diff covers Ubuntu only. Pinning
  buys you control over *when* the image changes; checking *what*
  changed is a manual pass over the provider's image release notes
  before you move the pin.
- A floating label is sometimes a deliberate choice — a job whose
  whole purpose is to test against the newest image, for example. If
  you keep one, write that reason down where the next reader will
  find it (a comment on the `runs-on:` line is enough). The finding
  will keep appearing in scans; a recorded "checked and kept, on
  <date>, because <reason>" is the difference between a decision and
  an oversight. Note the related trap in the
  [macOS 14 retirement guide](macos-14-retirement.md): moving a
  retired `macos-14` job to `macos-latest` resolves the retirement by
  accepting a floating label — that trade should be made knowingly,
  not by default.

## What a re-scan should show

- Every pinned label clears its `FLOATING_LABEL` finding. There is
  no "checked-and-pinned" residue for this rule — unlike
  `DEFAULT_DRIFT`, a correct fix makes the finding go away entirely.
- If a HIGH finding remains, a form was missed: a matrix axis, a
  bare list item, or the assignment behind an `env` key. The line
  number in the remaining finding names the form.
- A workflow that used a floating label only through a
  `vars.*` / `inputs.*` expression still shows its
  `INDIRECT_RUNS_ON` warning after you pin the value at its source.
  That warning's re-scan behaviour is documented in the
  [indirect-labels guide](resolving-indirect-runs-on.md); it is not
  a failed fix for this rule.
