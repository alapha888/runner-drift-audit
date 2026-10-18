# Pinning actions by commit SHA: working through the UNPINNED_ACTION warnings

RunnerDriftAudit reports every `uses:` reference that points at a mutable
tag instead of a full commit SHA as a WARN with the rule ID
`UNPINNED_ACTION`:

```text
action 'actions/checkout' is referenced by mutable tag 'v4', not a full commit SHA; the tag can move under you.
```

This page is the remediation guide for that one rule: what the warning
does and does not claim, how to resolve a tag to the commit it currently
points at, how to write the pin so it stays readable, and how to keep
pins from going stale. It is deliberately not a "pin everything today"
page — the scanner grades this WARN, not HIGH, and the sections below
explain when pinning is worth the maintenance cost and when it is not.

## What the warning means

A tag such as `v4` is a movable pointer. The action's maintainer can
re-point it at a different commit at any time — that is how `v4` receives
minor and patch updates without you changing your workflow — and anyone
who compromises the maintainer's account or the repository can re-point
it too. Your next run then executes different code than your last run,
with no change on your side and nothing in your diff to review.

A full commit SHA is immutable in practice: the same 40-character SHA
always resolves to the same tree. Pinning by SHA turns "whatever the tag
points at today" into "exactly this commit, until I change it".

What the warning does **not** claim:

- It does not claim the tag *has* moved, or that the action is unsafe
  today. It flags the exposure, not an incident.
- It is not a HIGH. Floating runner labels and retired labels break or
  drift your builds on a published schedule; a mutable action tag is a
  supply-chain exposure whose likelihood depends on whose action it is.
  That difference is why the scanner grades it WARN and why the fix
  guidance reads "pin … **if your policy requires immutable refs**".

## What the scanner counts as pinned

The check is exact, and worth knowing before you start editing:

- The ref after `@` must be a **full 40-character, lowercase hex** SHA.
  A short SHA (`@8ade135`), a tag (`@v4.2.2`), and a branch name
  (`@main`) all still report as `UNPINNED_ACTION`.
- References with no `@`, local actions (`uses: ./…`), and Docker
  actions (`uses: docker://…`) are **not flagged** — the scanner skips
  them by design. If your policy covers those too, they are a manual
  check; a clean scan does not say anything about them.
- The rule fires per `uses:` line in the workflow files you give the
  scanner. Actions referenced *inside* a third-party composite action
  do not appear in your report — those are that maintainer's pins to
  manage, and a reason to prefer composite actions whose own internals
  are pinned.

## Resolving a tag to its commit SHA

You need the commit the tag points at **now**, recorded at the moment
you pin. Two reliable ways:

**With git (no clone needed):**

```bash
git ls-remote https://github.com/actions/checkout 'refs/tags/v4*'
```

Annotated tags print two lines: the tag object itself and a peeled
line ending in `^{}`. **Use the `^{}` line** — that is the commit.
Lightweight tags print a single line, which is already the commit.

**With the GitHub API / gh:**

```bash
gh api repos/actions/checkout/git/ref/tags/v4
```

For an annotated tag this returns the tag object; follow its object URL
one step to reach the commit it tags. The `git ls-remote` route above
is usually faster because the peeling is already done.

Whichever route you take, note the tag's version next to the SHA when
you write the pin (next section) — a bare SHA with no version note is
how pins become unreviewable.

## Writing the pin

Keep the human-readable version as a trailing comment:

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

The comment is not decoration. It is what a reviewer reads in a diff,
what Dependabot updates when it bumps the pin, and what you search for
when a CVE names a version range. A SHA pin without the version comment
trades one opacity for another.

Do it in one pass per workflow, then re-run the scanner: the
`UNPINNED_ACTION` lines for the refs you pinned should be gone, and the
ones you deliberately left (see below) should be exactly the ones
remaining. Treat any *new* line as a mistake in your edit, not noise.

## Keeping pins fresh — the real cost

A tag pin updates itself; a SHA pin never does. That is the point, and
also the maintenance bill: security fixes and bug fixes to an action no
longer reach you until someone bumps the SHA. Pinning without an update
mechanism trades a supply-chain risk for a staleness risk.

The standard mechanism is Dependabot for the `github-actions`
ecosystem:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

With that in place, Dependabot opens pull requests that move the SHA
and update the trailing version comment together, so each bump is a
normal, reviewable diff. Renovate offers the same behaviour. If you run
neither, put SHA bumps on a calendar — an unreviewed pile of stale pins
found during an incident is worse than a short, deliberate exception
list.

## Deciding what to pin

Pin where the exposure is real, and write down the exceptions instead
of chasing a zero count:

- **Third-party actions from small or single-maintainer projects** —
  highest value. One compromised account re-points the tag, and there
  is no large organisation's release process behind it.
- **Actions that receive secrets or a write-capable token** — the
  blast radius of a moved tag is set by what the step can reach, not by
  who wrote the action.
- **First-party actions (`actions/*`, `github/*`) referenced by major
  tag** — lower risk, not zero. Many teams still pin them for
  reproducibility; many deliberately accept the major tag so patch
  updates flow. Either is defensible; an undocumented mix is not.
- **Deliberate exceptions** — if a tag stays mutable on purpose, say so
  in the workflow or the repo's notes. The scanner will keep reporting
  it as WARN; that is the agreed cost, visible in every report, rather
  than a surprise later.

## What this page does not do

- It does not argue that every repository must pin every action. The
  scanner's own guidance is conditional — "where policy requires it" —
  and this page keeps that condition.
- It does not cover verifying an action's source before you pin it.
  Pinning freezes the code you have at pin time; reading what that code
  does is a separate review, and a SHA is not a substitute for it.
- It does not pin Docker image digests or local actions — the scanner
  does not flag either (see above), and they have their own mechanisms.

---

RunnerDriftAudit is a free, single-file scanner (MIT) for GitHub
Actions workflow drift — floating and retired runner labels, removed
tools, default-version drift, and unpinned action refs. The multi-repo
edition with one combined HTML report is
[RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra)
($29 one-time).
