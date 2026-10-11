"""Draws the opening picture of the C4I page: a row of ones and zeros that
becomes a heartbeat, from bytes to bedside. Prints an inline SVG.

The digits spell MESSAGE in eight-bit ASCII. They use the typeface of the
digits in the emblem and in the windows of the canal houses."""
MESSAGE = "C4I"
FONT = "'Times New Roman', Times, 'Liberation Serif', serif"
Y = 96        # the line the heartbeat runs on
STEP = 23     # distance between two digits
BEAT = "q11 -12 22 0 h14 l7 8 l13 -78 l14 100 l9 -30 h18 q17 -22 34 0"


def build():
    bits = "".join(f"{ord(ch):08b}" for ch in MESSAGE)
    xs = [14 + STEP * k for k in range(len(bits))]
    end = xs[-1] + STEP
    digits = f'<text y="{Y + 10}" x="{" ".join(str(x) for x in xs)}">{bits}</text>'
    line = f"M{end} {Y} H690 {BEAT} H960 {BEAT} H1200"
    return digits, line, end


if __name__ == "__main__":
    digits, line, end = build()
    print(f'''<svg viewBox="0 0 1200 150" role="img" aria-labelledby="pulse-t" xmlns="http://www.w3.org/2000/svg">
  <title id="pulse-t">A row of ones and zeros that becomes a heartbeat: from bytes to bedside.</title>
  <defs><linearGradient id="pulse-g" gradientUnits="userSpaceOnUse" x1="{end}" y1="0" x2="690" y2="0"><stop offset="0" stop-color="var(--ink)"/><stop offset="1" stop-color="var(--brand)"/></linearGradient></defs>
  <g class="sky-detail" fill="var(--ink)" font-family="{FONT}" font-size="30" text-anchor="middle">{digits}</g>
  <path class="sky-line" pathLength="1" fill="none" stroke="url(#pulse-g)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" d="{line}"/>
</svg>''')
