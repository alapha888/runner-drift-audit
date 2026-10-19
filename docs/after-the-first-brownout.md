# After the first macos-14 brownout: a morning-after checklist

The first scheduled `macos-14` brownout ran **October 19, 14:00 UTC
to October 20, 00:00 UTC** (GitHub Changelog, 2026-10-01). The window
is closed. This page is for the morning after: what the failures in
that window meant, what a green run this morning does not mean, and
the order to work through what is left.

## 1. Sort last night's failures by the clock, not by the job name

A job on `macos-14`, `macos-14-large`, or `macos-14-xlarge` that
failed between 14:00 UTC on October 19 and 00:00 UTC on October 20
failed by design — the brownout, not your code. Do not debug it, and
do not re-run it hoping for a different result inside a future
window.

A failure on those labels *outside* that window is a real failure.
So is a failure on any other label at any time. The brownout explains
one slice of one night; it is not a blanket excuse for a red board.

## 2. Do not close the issue because the job passes again today

The labels still exist after the window ends. A `macos-14` job that
failed at 20:00 UTC last night can pass at 09:00 UTC today, and that
green run proves nothing about next month: the image is retired in
full on **November 2, 2026**, after which the same job fails every
time. Treat a passing run this morning as a reprieve with a date on
it, not as a fix.

## 3. Migrate while the old label still works

This is the one stretch where both labels are usable, which makes it
the cheapest time to move:

- Change `macos-14` / `macos-14-large` / `macos-14-xlarge` to
  `macos-15` for a fixed image, or `macos-latest` if floating is
  acceptable for that job — the two labels GitHub recommends in the
  retirement notice.
- Test the replacement on its own merits. While the old label still
  passes, a side-by-side comparison still means something; during
  the next brownout it will not.
- `macos-latest` is a floating label, so the scanner will flag it as
  `FLOATING_LABEL`. That is the trade-off working as intended:
  choose the pinned label for a stable image, or accept the floating
  finding knowingly and record why.

## 4. Re-scan, and keep the result with the migration

Run the scanner (v0.3.7 or later) after the change:

```bash
python3 runner_drift_audit.py .
```

A workflow clean of `RETIRED_LABEL` findings will not be stopped by
the November 2 retirement. Keep the scan output with the migration
change — it is the record that the label was checked, not just
edited.

## 5. Keep the two October changes separate in your notes

The `ubuntu-latest` rollout is a different change on a different
clock: it opened October 19 and runs through **November 19, 2026**.
A Linux job that behaves differently from one run to the next this
month is the rollout, not fallout from the macOS brownout. The
[rollout-week playbook](rollout-week-playbook.md) covers that case.

## What this page does not cover

- It does not list further brownout dates. The dates here are the
  ones GitHub published in the 2026-10-01 Changelog notice; if
  GitHub schedules more brownouts before November 2, the same
  clock-sorting in step 1 applies to those windows.
- It does not debug failures unrelated to runner labels. If the
  failing step is in your build or test code, the label guides will
  not help with it.
- A clean scan does not prove a workflow will pass on the new image;
  the scanner reads workflow files statically and does not run your
  jobs.
