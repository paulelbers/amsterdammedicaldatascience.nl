"""Draws the opening picture: one line that is a heartbeat on the left and
becomes a row of Amsterdam canal houses. Prints an inline SVG."""
Q = 252  # the quay, and the baseline of the heartbeat
X0 = 330

# width, wall height up to the eaves, kind of gable, height of the gable
HOUSES = [
    (70, 124, "step", 44), (58, 152, "neck", 50), (80, 112, "spout", 46), (66, 160, "bell", 40),
    (84, 134, "step", 50), (56, 170, "neck", 46), (74, 126, "bell", 44), (66, 146, "spout", 40),
    (78, 118, "step", 44), (60, 158, "neck", 48),
]

def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")

def gable(kind, x, ye, w, gh):
    """Path from the left eave (x, ye) to the right eave (x+w, ye). Returns (path, top y)."""
    cx = x + w / 2
    if kind == "spout":
        return f"L{f(cx-5)} {f(ye-gh)} H{f(cx+5)} L{f(x+w)} {f(ye)}", ye - gh
    if kind == "step":
        n, cap = 4, 16
        dx, dy = (w / 2 - cap / 2) / n, gh / n
        up = "".join(f"v{f(-dy)} h{f(dx)} " for _ in range(n))
        down = "".join(f"h{f(dx)} v{f(dy)} " for _ in range(n))
        return f"{up}h{f(cap)} {down}".strip(), ye - gh
    if kind == "neck":
        xl, xr, sh = x + w * 0.27, x + w * 0.73, 22
        return (f"Q{f(xl)} {f(ye)} {f(xl)} {f(ye-sh)} V{f(ye-gh)} h-4 L{f(cx)} {f(ye-gh-15)} L{f(xr+4)} {f(ye-gh)} h-4 "
                f"V{f(ye-sh)} Q{f(xr)} {f(ye)} {f(x+w)} {f(ye)}"), ye - gh - 15
    if kind == "bell":
        return (f"C{f(x+w*.04)} {f(ye-gh*.5)} {f(x+w*.3)} {f(ye-gh*.3)} {f(x+w*.31)} {f(ye-gh*.78)} "
                f"Q{f(cx)} {f(ye-gh*1.2)} {f(x+w*.69)} {f(ye-gh*.78)} "
                f"C{f(x+w*.7)} {f(ye-gh*.3)} {f(x+w*.96)} {f(ye-gh*.5)} {f(x+w)} {f(ye)}"), ye - gh * 0.98
    raise ValueError(kind)

def build():
    # The heartbeat: a small wave, the spike, a rounder wave, then the flat line that becomes the quay.
    line = [f"M0 {Q} H92 q11 -16 22 0 h14 l7 10 l13 -150 l14 186 l9 -46 h18 q17 -30 34 0 H{X0}"]
    detail, x = [], X0
    eaves = [Q - h for _, h, _, _ in HOUSES]
    for i, (w, h, kind, gh) in enumerate(HOUSES):
        ye = Q - h
        if i == 0:
            line.append(f"V{f(ye)}")
        path, top = gable(kind, x, ye, w, gh)
        line.append(path)
        nxt = eaves[i + 1] if i + 1 < len(HOUSES) else Q
        line.append(f"V{f(nxt)}")
        cx = x + w / 2
        # the wall between this house and the next, below the lower eave
        if i + 1 < len(HOUSES):
            detail.append(f"M{f(x+w)} {f(max(ye, nxt))} V{Q}")
        # windows: two or three across, a floor every 30
        cols = 3 if w >= 76 else 2
        gap = w / (cols + 1)
        y = ye + 12
        while y + 18 <= Q - 40:
            for c in range(cols):
                detail.append(f"M{f(x+gap*(c+1)-5)} {f(y)} h10 v18 h-10 z")
            y += 30
        # ground floor: a door and tall windows
        detail.append(f"M{f(x+gap-6)} {Q} v-27 h12 v27")
        for c in range(1, cols):
            detail.append(f"M{f(x+gap*(c+1)-5)} {Q-10} v-22 h10 v22 z")
        # the attic window and the hoisting beam every Amsterdam gable has
        detail.append(f"M{f(cx-4)} {f(ye-gh*.42)} h8 v12 h-8 z")
        detail.append(f"M{f(cx)} {f(top+7)} v7")
        x += w
    bx = x + 34
    line.append(f"H{f(bx)} c22 -15 34 -19 50 -19 s28 4 50 19 H1200")
    detail.append(f"M{f(bx+20)} {Q} c6 -12 16 -18 30 -18 s24 6 30 18")
    water = [f"M{a} {Q+12} h{b}" for a, b in ((352, 70), (470, 120), (640, 60), (760, 150), (950, 80), (1068, 70))]
    water += [f"M{a} {Q+23} h{b}" for a, b in ((400, 90), (560, 50), (700, 110), (880, 70), (1000, 40), (1080, 60))]
    water += [f"M{a} {Q+34} h{b}" for a, b in ((450, 60), (610, 100), (820, 60), (940, 80))]
    return " ".join(line), " ".join(detail), " ".join(water)

if __name__ == "__main__":
    line, detail, water = build()
    print(f'''<svg viewBox="0 0 1200 304" role="img" aria-labelledby="sky-t" xmlns="http://www.w3.org/2000/svg">
  <title id="sky-t">A single line: a heartbeat on the left that becomes a row of Amsterdam canal houses.</title>
  <defs><linearGradient id="sky-g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0"><stop offset="0" stop-color="var(--brand)"/><stop offset=".235" stop-color="var(--brand)"/><stop offset=".29" stop-color="var(--ink)"/><stop offset="1" stop-color="var(--ink)"/></linearGradient></defs>
  <g fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path class="sky-water" d="{water}" stroke="var(--ink)" stroke-width="1.4"/>
    <path class="sky-detail" d="{detail}" stroke="var(--ink)" stroke-width="1.15"/>
    <path class="sky-line" pathLength="1" d="{line}" stroke="url(#sky-g)" stroke-width="2.6"/>
  </g>
</svg>''')
