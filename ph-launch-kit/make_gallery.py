#!/usr/bin/env python3
"""Generate Product Hunt gallery assets for RunnerDriftAudit.

Reproducible: python3 make_gallery.py
Outputs (1270x760 PH gallery size, logo 512x512):
  gallery-1-terminal.png     - terminal-style render of the REAL captured output
                               of `python3 runner_drift_audit.py samples/bad`
  gallery-2-differences.png  - the 22 toolset differences, grouped
  gallery-3-timeline.png     - Oct 19 -> Nov 19, 2026 migration timeline
  thumbnail-512.png          - logo redrawn from icons/runner-drift-audit.svg
All text is factual, taken from README.md / runner_drift_audit.py / real run output.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1270, 760
BG = (13, 17, 23)          # #0d1117 GitHub dark
PANEL = (22, 27, 34)       # #161b22
BORDER = (48, 54, 61)      # #30363d
FG = (230, 237, 243)       # #e6edf3
DIM = (139, 148, 158)      # #8b949e
BLUE = (88, 166, 255)      # #58a6ff
GREEN = (63, 185, 80)      # #3fb950
ORANGE = (240, 136, 62)    # #f0883e
RED = (248, 81, 73)        # #f85149
YELLOW = (210, 153, 34)    # #d29922

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- terminal ---
def terminal():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # window chrome
    d.rounded_rectangle([24, 24, W - 24, H - 24], radius=14, fill=PANEL, outline=BORDER, width=2)
    for i, c in enumerate([(248, 81, 73), (210, 153, 34), (63, 185, 80)]):
        d.ellipse([52 + i * 32, 46, 72 + i * 32, 66], fill=c)
    d.text((160, 44), "runner-drift-audit — samples/bad", font=f(MONO, 22), fill=DIM)

    body = f(MONO, 21)
    bold = f(MONO_B, 21)
    x, y = 52, 98
    lh = 30

    def line(segments):
        nonlocal x, y
        cx = x
        for text, font, color in segments:
            d.text((cx, y), text, font=font, fill=color)
            cx += d.textlength(text, font=font)
        y += lh

    line([("$ ", bold, GREEN), ("python3 runner_drift_audit.py samples/bad", body, FG)])
    y += 4
    line([("samples/bad/.github/workflows/ci.yml", bold, BLUE)])
    findings = [
        ("HIGH", RED, "line 5  FLOATING_LABEL", "runs-on 'ubuntu-latest' moves 24.04 -> 26.04"),
        ("WARN", YELLOW, "line 7  UNPINNED_ACTION", "actions/checkout referenced by tag 'v4', not a SHA"),
        ("WARN", YELLOW, "line 10 DEFAULT_DRIFT", "Java default changes 17 -> 25 (Java 8 removed)"),
        ("HIGH", RED, "line 12 REMOVED_TOOL", "mercurial was removed from the 26.04 image"),
        ("HIGH", RED, "line 13 REMOVED_TOOL", "webpack no longer preinstalled globally"),
        ("WARN", YELLOW, "line 14 DEFAULT_DRIFT", "CMake no longer pinned: 3.31.6 -> latest (4.x)"),
    ]
    for sev, col, head, msg in findings:
        line([("  [" + sev + "] ", bold, col), (head, body, FG)])
        line([("           " + msg, body, DIM)])
    y += 4
    line([("Scanned 1 workflow file(s);  HIGH findings: 3.", body, FG)])
    line([("$ ", bold, GREEN), ("echo $?", body, FG)])
    line([("1", body, ORANGE), ("   <- exit code 1 on any HIGH: usable as a CI gate", body, DIM)])
    y += 6
    line([("$ ", bold, GREEN), ("python3 runner_drift_audit.py samples/clean", body, FG)])
    line([("Scanned 1 workflow file(s);  HIGH findings: 0.  (exit 0)", body, GREEN)])
    img.save("gallery-1-terminal.png")


# ------------------------------------------------------------- differences ---
def differences():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((48, 36), "ubuntu-latest: 24.04 -> 26.04", font=f(SANS_B, 44), fill=FG)
    d.text((48, 96), "22 differences in GitHub's official runner toolsets (toolset-2404.json vs toolset-2604.json)",
           font=f(SANS, 24), fill=DIM)

    cols = [
        ("REMOVED FROM THE IMAGE", RED, [
            "mercurial (hg), mediainfo",
            "sphinxsearch, haveged",
            "fastlane gem",
            "webpack, gulp, grunt, parcel,",
            "lerna, newman, tsc",
            "  (global npm installs)",
            "gcc-12, g++-12, gfortran-12",
            "clang-16, clang-17",
            "p7zip (replaced by 7zip)",
        ]),
        ("DEFAULT VERSIONS JUMP", YELLOW, [
            "Java 17 -> 25 (8 removed)",
            "Node 22 -> 24",
            "PHP 8.3 -> 8.5 (only version)",
            "PostgreSQL 16 -> 18",
            "clang 18 -> 21",
            "Go 1.24 -> 1.26",
            "Docker 28 -> 29",
            "Compose 2.38 -> 5.1",
        ]),
        ("ALSO FLAGGED", BLUE, [
            "runs-on: ubuntu-latest",
            "  floating label (HIGH)",
            "actions pinned by tag,",
            "  not full commit SHA (WARN)",
            "CMake unpinned: was held at",
            "  3.31.6 to avoid CMake 4.0;",
            "  26.04 ships latest",
            "",
            "Nothing in your repo changes.",
            "The machine under CI does.",
        ]),
    ]
    cw, gap, top = 378, 21, 160
    for i, (title, col, items) in enumerate(cols):
        x0 = 48 + i * (cw + gap)
        d.rounded_rectangle([x0, top, x0 + cw, H - 120], radius=12, fill=PANEL, outline=BORDER, width=2)
        d.text((x0 + 22, top + 22), title, font=f(SANS_B, 22), fill=col)
        yy = top + 66
        for it in items:
            w_it = d.textlength(it, font=f(MONO, 19))
            assert w_it <= cw - 36, (title, it, w_it)
            d.text((x0 + 22, yy), it, font=f(MONO, 19), fill=FG)
            yy += 35
    cap = "Each difference is a scan rule in RunnerDriftAudit, reported at the exact line in your workflow files."
    capf = f(SANS, 23)
    assert d.textlength(cap, font=capf) <= W - 96, d.textlength(cap, font=capf)
    d.text((48, H - 84), cap, font=capf, fill=DIM)
    img.save("gallery-2-differences.png")


# ---------------------------------------------------------------- timeline ---
def timeline():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((48, 40), "The ubuntu-latest migration window", font=f(SANS_B, 44), fill=FG)
    d.text((48, 100), "GitHub moves the label from Ubuntu 24.04 to 26.04 between Oct 19 and Nov 19, 2026.",
           font=f(SANS, 25), fill=DIM)

    # launch chip
    chip = "Launching Oct 17-18 - audit before the window opens."
    chipf = f(SANS_B, 26)
    chip_w = d.textlength(chip, font=chipf)
    d.rounded_rectangle([48, 168, 72 + chip_w + 26, 232], radius=12, outline=BLUE, width=2)
    d.text((72, 186), chip, font=chipf, fill=BLUE)

    y = 430
    x0, x1 = 90, W - 90
    d.line([x0, y, x1, y], fill=BORDER, width=6)
    pts = [
        (0.03, "OCT 19", "Rollout begins", "ubuntu-latest starts\npointing to 26.04 images.", ORANGE),
        (0.52, "OCT 19 - NOV 19", "Gradual rollout", "Repos migrate at different\ntimes - breakage is silent.", YELLOW),
        (0.97, "NOV 19", "Window closes", "ubuntu-latest is 26.04\nfor everyone.", RED),
    ]
    for frac, date, title, body, col in pts:
        cx = x0 + frac * (x1 - x0)
        d.ellipse([cx - 13, y - 13, cx + 13, y + 13], fill=col)
        tx = min(max(cx - 130, 30), W - 290)
        d.text((tx, y - 120), date, font=f(MONO_B, 24), fill=col)
        d.text((tx, y - 84), title, font=f(SANS_B, 27), fill=FG)
        for j, bl in enumerate(body.split("\n")):
            d.text((tx, y + 44 + j * 32), bl, font=f(SANS, 22), fill=DIM)
    d.rounded_rectangle([48, H - 130, W - 48, H - 48], radius=12, fill=PANEL, outline=BORDER, width=2)
    d.text((72, H - 106), "Exit code 1 on any HIGH finding - run it locally today, or gate a CI job with it before Oct 19.",
           font=f(SANS, 25), fill=FG)
    img.save("gallery-3-timeline.png")


# --------------------------------------------------------------- thumbnail ---
def thumbnail():
    S = 512
    img = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S, S], radius=96, fill=BG)
    # prompt chevron ">" in blue (from the SVG)
    d.line([120, 150, 226, 256], fill=BLUE, width=44)
    d.line([226, 256, 120, 362], fill=BLUE, width=44)
    for (cx, cy) in [(120, 150), (226, 256), (120, 362)]:
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=BLUE)
    # underscore in green
    d.line([252, 362, 392, 362], fill=GREEN, width=44)
    d.ellipse([230, 340, 274, 384], fill=GREEN)
    d.ellipse([370, 340, 414, 384], fill=GREEN)
    # check mark in orange (SVG path offset applied)
    pts = [(260, 168), (316, 224), (412, 128)]
    d.line([pts[0], pts[1]], fill=ORANGE, width=36)
    d.line([pts[1], pts[2]], fill=ORANGE, width=36)
    for (cx, cy) in pts:
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=ORANGE)
    img.save("thumbnail-512.png")


if __name__ == "__main__":
    terminal()
    differences()
    timeline()
    thumbnail()
    print("done")
