#!/usr/bin/env python3
"""Generate the playbook's four diagrams (light and dark) as self-contained HTML with inline SVG.

Follows the diagram-design skill's editorial system with its shipped default tokens:
orthogonal connectors, one accent per diagram, Geist / Geist Mono / Instrument Serif,
accessible <title>/<desc>. Run:  python3 assets/src/make-diagrams.py   (writes assets/src/*.html)
Then export PNGs with assets/src/export-png.py.
"""
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))

SKINS = {
    "": dict(paper="#f5f5f5", paper2="#ececec", ink="#2d3142", muted="#4f5d75", soft="#5a6580",
             rule="rgba(45,49,66,0.12)", rule_solid="#bfc0c0", accent="#bf4520", tint="rgba(191,69,32,0.08)",
             link="#2e5aa8", zone_fill="rgba(45,49,66,0.02)", zone_stroke="rgba(45,49,66,0.10)"),
    "-dark": dict(paper="#2d3142", paper2="#393e53", ink="#f5f5f5", muted="#bfc0c0", soft="#949eb2",
                  rule="rgba(245,245,245,0.12)", rule_solid="rgba(191,192,192,0.25)", accent="#f08a59",
                  tint="rgba(240,138,89,0.10)", link="#739fdf", zone_fill="rgba(245,245,245,0.02)",
                  zone_stroke="rgba(245,245,245,0.10)"),
}
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600"
         "&family=Geist+Mono:wght@400;500;600&display=swap")
SANS = "'Geist', system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"


def page(slug, eyebrow, title, desc, width, height, body, skin):
    t = SKINS[skin]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="{FONTS}" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{ --color-paper: {t['paper']}; --color-ink: {t['ink']}; --color-muted: {t['muted']}; --color-accent: {t['accent']};
      --font-sans: {SANS}; --font-serif: 'Instrument Serif', serif; --font-mono: {MONO}; }}
    body {{ font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink); min-height: 100vh;
      display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }}
    .frame {{ max-width: 1200px; width: 100%; }}
    .diagram-container {{ width: 100%; overflow-x: auto; }}
    .eyebrow {{ font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase;
      color: var(--color-muted); margin-bottom: 0.5rem; }}
    h1 {{ font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400; letter-spacing: -0.02em;
      line-height: 1.15; color: var(--color-ink); margin-bottom: 1.5rem; }}
    svg {{ width: 100%; min-width: {width}px; display: block; }}
    @media print {{ .diagram-container {{ overflow-x: visible; }} svg {{ min-width: 0; }} }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    <div class="diagram-container">
      <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
        <title id="{slug}-title">{title}</title>
        <desc id="{slug}-desc">{desc}</desc>
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{t['muted']}"/></marker>
          <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{t['accent']}"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="{t['paper']}"/>
{body}
      </svg>
    </div>
  </div>
</body>
</html>
"""


def node(t, x, y, w, h, tag, name, sub, focal=False, rx=6):
    stroke = t["accent"] if focal else t["ink"]
    fill = t["tint"] if focal else t["paper"]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{t["paper"]}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>']
    if tag:
        tw = 8 + 5.2 * len(tag)
        out.append(f'<rect x="{x + 12}" y="{y + 10}" width="{tw:.0f}" height="12" rx="2" fill="{t["paper2"]}"/>')
        out.append(f'<text x="{x + 12 + tw / 2:.1f}" y="{y + 19}" fill="{t["soft"]}" font-family="{MONO}" font-size="7" font-weight="500" letter-spacing="0.14em" text-anchor="middle">{tag}</text>')
    ny = y + h / 2 + (2 if sub else 4)
    out.append(f'<text x="{x + w / 2}" y="{ny:.0f}" fill="{t["ink"]}" font-family="{SANS}" font-size="13" font-weight="600" text-anchor="middle">{name}</text>')
    if sub:
        out.append(f'<text x="{x + w / 2}" y="{ny + 16:.0f}" fill="{t["muted"]}" font-family="{MONO}" font-size="9" text-anchor="middle">{sub}</text>')
    return "\n".join(out)


def label(t, x, y, text, width=None):
    """Arrow label on an opaque paper mask, centred at (x, y)."""
    w = width or (10 + 5.2 * len(text))
    return (f'<rect x="{x - w / 2:.1f}" y="{y - 7}" width="{w:.0f}" height="12" fill="{t["paper"]}"/>'
            f'<text x="{x}" y="{y + 2}" fill="{t["soft"]}" font-family="{MONO}" font-size="8" letter-spacing="0.06em" text-anchor="middle">{text}</text>')


def legend(t, y, items, x=0, width=960):
    out = [f'<line x1="{x + 40}" y1="{y - 16}" x2="{x + width - 40}" y2="{y - 16}" stroke="{t["rule"]}" stroke-width="1"/>']
    cx = x + 48
    for kind, text in items:
        if kind == "solid":
            out.append(f'<line x1="{cx}" y1="{y}" x2="{cx + 24}" y2="{y}" stroke="{t["muted"]}" stroke-width="1.2" marker-end="url(#arrow)"/>')
        elif kind == "dashed":
            out.append(f'<line x1="{cx}" y1="{y}" x2="{cx + 24}" y2="{y}" stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>')
        elif kind == "focal":
            out.append(f'<rect x="{cx}" y="{y - 7}" width="24" height="14" rx="3" fill="{t["tint"]}" stroke="{t["accent"]}" stroke-width="1.2"/>')
        elif kind == "box":
            out.append(f'<rect x="{cx}" y="{y - 7}" width="24" height="14" rx="3" fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1.2"/>')
        out.append(f'<text x="{cx + 32}" y="{y + 3}" fill="{t["soft"]}" font-family="{MONO}" font-size="8" letter-spacing="0.06em">{text}</text>')
        cx += 40 + 5.2 * len(text) + 40
    return "\n".join(out)


# ---------------------------------------------------------------- 1. model + harness (architecture)
def model_and_harness(skin):
    t = SKINS[skin]
    b = []
    # zone first, then arrows, then nodes
    b.append(f'<rect x="104" y="72" width="752" height="248" rx="8" fill="{t["zone_fill"]}" stroke="{t["zone_stroke"]}" stroke-width="0.8"/>')
    b.append(f'<rect x="392" y="76" width="176" height="12" rx="2" fill="{t["paper"]}"/>')
    b.append(f'<text x="480" y="85" fill="{t["soft"]}" font-size="7" font-family="{MONO}" text-anchor="middle" letter-spacing="0.14em">HARNESS · THE PART YOU ENGINEER</text>')
    # forward flow (accent: the headline path)
    b.append(f'<line x1="336" y1="196" x2="392" y2="196" stroke="{t["accent"]}" stroke-width="1.2" marker-end="url(#arrow-accent)"/>')
    b.append(label(t, 364, 180, "BEFORE"))
    b.append(f'<line x1="592" y1="196" x2="648" y2="196" stroke="{t["accent"]}" stroke-width="1.2" marker-end="url(#arrow-accent)"/>')
    b.append(label(t, 620, 180, "AFTER"))
    # feedback: sensors -> model, dashed, routed under the nodes
    b.append(f'<path d="M 748,240 V 272 Q 748,280 740,280 H 500 Q 492,280 492,272 V 248" fill="none" stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>')
    b.append(label(t, 620, 296, "WHAT WENT WRONG"))
    # nodes
    b.append(node(t, 136, 152, 200, 88, "GUIDES", "Instructions and tools", "map · skills · init.sh · allow list"))
    b.append(node(t, 392, 152, 200, 88, "MODEL", "The model", "decides what code to write", focal=True))
    b.append(node(t, 648, 152, 200, 88, "SENSORS", "Checks", "lint · tests · boot check · review"))
    b.append(legend(t, 368, [("solid", "ACTS BEFORE / AFTER THE MODEL"), ("dashed", "FEEDBACK"), ("focal", "THE ONE PART YOU DO NOT CONTROL")]))
    return page("model-and-harness" + skin, "Architecture · Harness Engineering Playbook", "Agent = model + harness",
                "Guides act before the model and sensors after it; both sit inside the harness, which is everything around the model that a team engineers.",
                960, 392, "\n".join(b), skin)


# ---------------------------------------------------------------- 2. session lifecycle (flowchart)
def session_lifecycle(skin):
    t = SKINS[skin]
    b = []
    cx = 480
    w, h = 304, 52
    x = cx - w // 2
    ys = {"start": 24, "read": 96, "pick": 176, "work": 256, "check": 344, "hand": 448, "end": 536}
    # arrows first (vertical spine)
    spine = [("start", 24 + 36, "read", 96), ("read", 96 + h, "pick", 176), ("pick", 176 + h, "work", 256), ("work", 256 + h, "check", 344),
             ("check", 344 + 72, "hand", 448), ("hand", 448 + h, "end", 536)]
    for _, y1, _, y2 in spine:
        b.append(f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" stroke="{t["muted"]}" stroke-width="1.2" marker-end="url(#arrow)"/>')
    b.append(label(t, cx + 30, 428, "YES"))
    # NO branch: diamond right vertex -> right -> up -> into Work's right edge
    b.append(f'<path d="M {cx + 100},380 H 712 Q 720,380 720,372 V 290 Q 720,282 712,282 H {x + w}" fill="none" stroke="{t["accent"]}" stroke-width="1.2" marker-end="url(#arrow-accent)"/>')
    b.append(label(t, 748, 336, "NO · FIX IT"))
    # nodes
    b.append(node(t, cx - 80, ys["start"], 160, 36, "", "Session starts", "", rx=18))
    b.append(node(t, x, ys["read"], w, h, "", "Read the map and the progress file, run init.sh", ""))
    b.append(node(t, x, ys["pick"], w, h, "", "Pick one failing feature", ""))
    b.append(node(t, x, ys["work"], w, h, "", "Work, with the guard watching", ""))
    # decision diamond (focal)
    b.append(f'<polygon points="{cx},344 {cx + 100},380 {cx},416 {cx - 100},380" fill="{t["tint"]}" stroke="{t["accent"]}" stroke-width="1.2"/>')
    b.append(f'<text x="{cx}" y="{377}" fill="{t["ink"]}" font-family="{SANS}" font-size="12" font-weight="600" text-anchor="middle">Quick check passes?</text>')
    b.append(f'<text x="{cx}" y="{392}" fill="{t["muted"]}" font-family="{MONO}" font-size="8" text-anchor="middle">the Stop hook runs it</text>')
    b.append(node(t, x, ys["hand"], w, h, "", "Hand off: progress file, commit, not verified", ""))
    b.append(node(t, cx - 80, ys["end"], 160, 36, "", "Session ends clean", "", rx=18))
    b.append(legend(t, 612, [("solid", "THE SESSION"), ("focal", "THE GATE THE AGENT CANNOT SKIP")]))
    return page("session-lifecycle" + skin, "Flowchart · Harness Engineering Playbook", "A harnessed session",
                "A session reads its state, works on one feature, cannot stop until the quick check passes, and hands off with a progress file and a commit.",
                960, 636, "\n".join(b), skin)


# ---------------------------------------------------------------- 3. incident to rule (loop)
def incident_loop(skin):
    t = SKINS[skin]
    cx, cy, R = 480, 300, 200
    sw, sh = 160, 64
    hw, hh = 200, 104
    stations = [("Incident", "what went wrong", False), ("Rule", "one line in the map", False),
                ("Guard", "hook, lint rule or test", True), ("Measure", "did it fire? false positives?", False),
                ("Expiry", "review, then remove", False)]
    N = len(stations)
    a, bb, A, B = sw / 2, sh / 2, hw / 2, hh / 2

    def grid(v):
        return int(round(v / 4.0)) * 4

    centers = []
    for k in range(N):
        th = math.radians(-90 + k * 360 / N)
        centers.append((grid(cx + R * math.cos(th)), grid(cy + R * math.sin(th)), th))

    def intersections(x0, y0):
        pts = []
        for xe in (x0 - a, x0 + a):
            d = R * R - (xe - cx) ** 2
            if d >= 0:
                for y in (cy + math.sqrt(d), cy - math.sqrt(d)):
                    if y0 - bb <= y <= y0 + bb:
                        pts.append((xe, y))
        for ye in (y0 - bb, y0 + bb):
            d = R * R - (ye - cy) ** 2
            if d >= 0:
                for x in (cx + math.sqrt(d), cx - math.sqrt(d)):
                    if x0 - a <= x <= x0 + a:
                        pts.append((x, ye))
        return pts

    def ang(p):
        return math.atan2(p[1] - cy, p[0] - cx)

    b = []
    # ring arcs (clockwise), drawn before boxes
    for k in range(N):
        x0, y0, th = centers[k]
        pts = intersections(x0, y0)
        pts.sort(key=lambda p: ((ang(p) - th + math.pi) % (2 * math.pi)))
        q_exit = pts[0] if ((ang(pts[0]) - th) % (2 * math.pi)) < math.pi else pts[-1]
        q_exit = max(pts, key=lambda p: ((ang(p) - th + 2 * math.pi) % (2 * math.pi)) if ((ang(p) - th + 2 * math.pi) % (2 * math.pi)) < math.pi else -1)
        j = (k + 1) % N
        x1, y1, thj = centers[j]
        ptsj = intersections(x1, y1)
        q_entry = min(ptsj, key=lambda p: ((thj - ang(p) + 2 * math.pi) % (2 * math.pi)) if ((thj - ang(p) + 2 * math.pi) % (2 * math.pi)) < math.pi else 9)
        phi_end = ang(q_entry) - 1.2 / R
        q_end = (cx + R * math.cos(phi_end), cy + R * math.sin(phi_end))
        b.append(f'<path d="M {q_exit[0]:.1f},{q_exit[1]:.1f} A {R} {R} 0 0 1 {q_end[0]:.1f},{q_end[1]:.1f}" fill="none" stroke="{t["muted"]}" stroke-width="1.2" marker-end="url(#arrow)"/>')
    # dashed spokes station -> hub
    for k, (x0, y0, th) in enumerate(centers):
        ux, uy = math.cos(th), math.sin(th)
        d_station = min(a / abs(ux) if ux else 1e9, bb / abs(uy) if uy else 1e9)
        d_hub = min(A / abs(ux) if ux else 1e9, B / abs(uy) if uy else 1e9)
        sx, sy = x0 - d_station * ux, y0 - d_station * uy
        ex, ey = cx + (d_hub + 6) * ux, cy + (d_hub + 6) * uy
        b.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>')
    # hub
    b.append(node(t, cx - A, cy - B, hw, hh, "HUB", "The harness", "every pass adds a guard"))
    # stations
    for (x0, y0, th), (name, sub, focal) in zip(centers, stations):
        b.append(node(t, x0 - a, y0 - bb, sw, sh, "", name, sub, focal=focal))
    b.append(legend(t, 596, [("solid", "THE LOOP, CLOCKWISE"), ("dashed", "WRITTEN INTO THE HARNESS"), ("focal", "WHERE A RULE BECOMES ENFORCED")]))
    return page("incident-to-rule" + skin, "Loop · Harness Engineering Playbook", "From incident to guard, with an expiry",
                "Each incident becomes a rule, the rule a guard, the guard is measured and given an expiry, and every pass writes into the harness.",
                960, 620, "\n".join(b), skin)


# ---------------------------------------------------------------- 4. maturity ladder (layer stack)
def maturity_ladder(skin):
    t = SKINS[skin]
    b = []
    layers = [("L4", "Governed", "owners on harness files · CI on pull requests · expiry on rules · a budget rule", False),
              ("L3", "Continuous", "docs in the repo · a debt gate in CI · enforced hard rules · evals or metrics", False),
              ("L2", "Enforced", "hooks · guard · stop-time check · allow list · done means verifying what ships", True),
              ("L1", "Instructed", "a map under 100 lines that names a check that exists · a lockfile", False),
              ("L0", "Unharnessed", "no instruction file, or one nobody maintains", False)]
    x, w, h, top = 136, 760, 64, 40
    for i, (tag, name, sub, focal) in enumerate(layers):
        y = top + i * h
        fill = t["tint"] if focal else (t["paper"] if i % 2 == 0 else t["paper2"])
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
        if focal:
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{t["accent"]}" stroke-width="1.2"/>')
        b.append(f'<text x="{x + 20}" y="{y + 38}" fill="{t["soft"]}" font-family="{MONO}" font-size="9" font-weight="500" letter-spacing="0.18em">{tag}</text>')
        b.append(f'<text x="{x + 72}" y="{y + 38}" fill="{t["ink"]}" font-family="{SANS}" font-size="15" font-weight="600">{name}</text>')
        b.append(f'<text x="{x + w - 20}" y="{y + 38}" fill="{t["muted"]}" font-family="{MONO}" font-size="9" text-anchor="end">{sub}</text>')
        if i:
            b.append(f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{t["rule"]}" stroke-width="1"/>')
    b.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h * len(layers)}" fill="none" stroke="{t["ink"]}" stroke-width="1"/>')
    # direction indicator, left margin
    b.append(f'<line x1="104" y1="{top + h * len(layers) - 8}" x2="104" y2="{top + 8}" stroke="{t["muted"]}" stroke-width="1.2" marker-end="url(#arrow)"/>')
    b.append(f'<text x="96" y="{top + h * len(layers) + 20}" fill="{t["soft"]}" font-family="{MONO}" font-size="7" font-weight="500" letter-spacing="0.14em">ENFORCEMENT</text>')
    b.append(legend(t, top + h * len(layers) + 56, [("focal", "WHERE MOST TEAMS SHOULD BE IN A WEEK"), ("box", "SCORED BY TOOLS/AUDIT-HARNESS.PY")]))
    return page("maturity-ladder" + skin, "Layer stack · Harness Engineering Playbook", "The maturity model",
                "Five levels from an unharnessed repository to a governed one, each scored by the audit on enforcement rather than on file presence.",
                960, top + h * len(layers) + 84, "\n".join(b), skin)


if __name__ == "__main__":
    for skin in SKINS:
        for build in (model_and_harness, session_lifecycle, incident_loop, maturity_ladder):
            html = build(skin)
            slug = html.split('aria-labelledby="')[1].split("-title")[0]
            path = os.path.join(OUT, slug + ".html")
            with open(path, "w") as handle:
                handle.write(html)
            print("wrote", os.path.relpath(path))
