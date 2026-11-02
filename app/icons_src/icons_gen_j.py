import json, math

V = ('0.3', '0', '0.7', '1')    # top-left lit, mostly vertical
D = ('0', '0', '1', '1')        # diagonal (planforms)
H = ('0', '0', '1', '0')        # horizontal (vertical cylinders)

def L(d, *stops):
    return ('l', d, stops)

GR = {
    # air
    'air': L(D, (0, '#F4F7FA'), (.5, '#C8D1DB'), (1, '#8D9BAC')),
    'airV': L(V, (0, '#F4F7FA'), (.5, '#C8D1DB'), (1, '#8D9BAC')),
    'airdk': L(V, (0, '#C2CCD7'), (1, '#7C8A9B')),
    # sea
    'sea': L(V, (0, '#E3E8EE'), (.55, '#B2BDC9'), (1, '#6F7E8E')),
    'seadk': L(V, (0, '#A9B4C1'), (1, '#5D6B7A')),
    'deck': L(V, (0, '#8C98A6'), (1, '#4F5B68')),
    'boot': L(V, (0, '#8E3129'), (1, '#4A1612')),
    'subm': L(V, (0, '#7A8693'), (.5, '#414C58'), (1, '#1C232A')),
    'water': ('l', ('0', '0', '0', '1'), ((0, '#8EC3EC', .55), (1, '#3D7FC0', 0))),
    # land
    'land': L(V, (0, '#B6C78B'), (.5, '#81955A'), (1, '#4E5F35')),
    'landdk': L(V, (0, '#86995D'), (1, '#3E4C29')),
    'track': L(V, (0, '#454B53'), (1, '#15181C')),
    'canvas': L(V, (0, '#A9B97F'), (.6, '#7A8C50'), (1, '#55663A')),
    # missile / white
    'white': L(V, (0, '#FFFFFF'), (.55, '#E1E6EC'), (1, '#A3AEBB')),
    'whitedk': L(V, (0, '#D3DAE2'), (1, '#8F9BA9')),
    'cylW': L(H, (0, '#BCC5D0'), (.3, '#FFFFFF'), (.65, '#DCE2E8'), (1, '#97A3B1')),
    'red': L(V, (0, '#D9614F'), (1, '#9B3125')),
    'orange': L(V, (0, '#F0B060'), (1, '#B8691F')),
    # tech
    'metal': L(V, (0, '#FBFCFD'), (.55, '#D6DCE3'), (1, '#98A4B1')),
    'metal2': L(V, (0, '#C9D1DA'), (1, '#8794A3')),
    'metal3': L(V, (0, '#A5B0BD'), (1, '#6A7685')),
    'cylM': L(H, (0, '#AEB8C4'), (.3, '#F6F8FA'), (.7, '#CDD4DC'), (1, '#8794A3')),
    'dkm': L(V, (0, '#6A7480'), (.5, '#434B55'), (1, '#262C33')),
    'dkm2': L(V, (0, '#4A525C'), (1, '#1E2328')),
    'glass': L(V, (0, '#BFE3FF'), (.5, '#78B6EE'), (1, '#3D86D6')),
    'canopy': L(V, (0, '#86B7E0'), (.45, '#2E5D8B'), (1, '#0F2339')),
    'scr': L(V, (0, '#2F6FB0'), (1, '#0E2A4A')),
    'array': L(D, (0, '#7FA3C8'), (.5, '#3F6690'), (1, '#1E3550')),
    'solar': L(D, (0, '#6E9BD0'), (.5, '#2F5D96'), (1, '#18365C')),
    'gold': L(V, (0, '#F1D893'), (.5, '#C9A145'), (1, '#8A6A20')),
    'skin': L(V, (0, '#E6C49C'), (1, '#A98560')),
    'uniform': L(V, (0, '#8BA3BE'), (.5, '#56708F'), (1, '#33495F')),
    'cloud': L(D, (0, '#FFFFFF'), (.5, '#D3E2F1'), (1, '#86A7CB')),
    'appbg': L(D, (0, '#8FC6F5'), (.5, '#4C8FD6'), (1, '#24599A')),
    # radials
    'shadow': ('r', None, ((0, '#000000', .38), (1, '#000000', 0))),
    'prop': ('r', None, ((0, '#FFFFFF', .55), (.8, '#B9C6D3', .28), (1, '#8D9BAC', .1))),
    'hub': ('r', ('0.35', '0.3', '0.7'), ((0, '#A9AFB7'), (.6, '#5C636C'), (1, '#2C3136'))),
    'tyre': ('r', ('0.4', '0.35', '0.65'), ((0, '#4D535B'), (.7, '#24282D'), (1, '#121417'))),
    'sphere': ('r', ('0.35', '0.3', '0.75'), ((0, '#FFFFFF'), (.55, '#D3DAE2'), (1, '#8A97A6'))),
    'lens': ('r', ('0.4', '0.35', '0.6'), ((0, '#6FA7DA'), (.5, '#1F4470'), (1, '#070F1A'))),
    'node': ('r', ('0.35', '0.3', '0.75'), ((0, '#DDF0FF'), (.5, '#5FA2E4'), (1, '#1F4F8C'))),
    'glow': ('r', None, ((0, '#E8F6FF'), (.4, '#8FD0FF'), (1, '#3D86D6', 0))),
    'uwater': ('r', None, ((0, '#7FB4E0', .35), (1, '#7FB4E0', 0))),
}


class B:
    def __init__(s, key):
        s.k = key; s.used = []; s.o = []

    def f(s, v):
        if v in GR:
            if v not in s.used: s.used.append(v)
            return f"url(#{s.k}-{v})"
        return v

    def _st(s, fill, st, sw, op, extra):
        a = f" fill='{s.f(fill)}'"
        if st: a += f" stroke='{st}' stroke-width='{sw}'"
        if op is not None: a += f" opacity='{op}'"
        return a + (' ' + extra if extra else '')

    def p(s, d, fill, st=None, sw=1.2, op=None, extra=''):
        s.o.append(f"<path d='{d}'{s._st(fill, st, sw, op, extra)}/>")

    def r(s, x, y, w, h, fill, st=None, rx=0, sw=1.2, op=None, extra=''):
        rr = f" rx='{rx}'" if rx else ''
        s.o.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}'{rr}{s._st(fill, st, sw, op, extra)}/>")

    def c(s, cx, cy, r, fill, st=None, sw=1.2, op=None, extra=''):
        s.o.append(f"<circle cx='{cx}' cy='{cy}' r='{r}'{s._st(fill, st, sw, op, extra)}/>")

    def e(s, cx, cy, rx, ry, fill, st=None, sw=1.2, op=None, extra=''):
        s.o.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}'{s._st(fill, st, sw, op, extra)}/>")

    def ln(s, d, col, w=1.2, op=None, cap='round', extra=''):
        o = f" opacity='{op}'" if op is not None else ''
        s.o.append(f"<path d='{d}' fill='none' stroke='{col}' stroke-width='{w}'{"" if cap=="round" else " stroke-linecap='"+cap+"'"}{o}{' '+extra if extra else ''}/>")

    def hl(s, d, w=1.1, op=.8):
        s.ln(d, '#FFFFFF', w, op)

    def sh(s, cx, cy, rx, ry):
        s.e(cx, cy, rx, ry, 'shadow')

    def drop(s, d, dx=2.5, dy=3.5, op=.16):
        s.o.append(f"<path d='{d}' fill='#0A1420' opacity='{op}' transform='translate({dx} {dy})'/>")

    def g(s, tr):
        s.o.append(f"<g transform='{tr}'>")

    def eg(s):
        s.o.append('</g>')

    def raw(s, x):
        s.o.append(x)

    def svg(s):
        defs = []
        for n in s.used:
            t, d, stops = GR[n]
            st = ''
            for stp in stops:
                o = f" stop-opacity='{stp[2]}'" if len(stp) > 2 else ''
                st += f"<stop offset='{stp[0]:g}' stop-color='{stp[1]}'{o}/>"
            if t == 'l':
                defs.append(f"<linearGradient id='{s.k}-{n}' x1='{d[0]}' y1='{d[1]}' x2='{d[2]}' y2='{d[3]}'>{st}</linearGradient>")
            else:
                a = f" cx='{d[0]}' cy='{d[1]}' r='{d[2]}'" if d else ''
                defs.append(f"<radialGradient id='{s.k}-{n}'{a}>{st}</radialGradient>")
        return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96'><defs>" + ''.join(defs) +
                "</defs><g stroke-linejoin='round' stroke-linecap='round'>" + ''.join(s.o) + "</g></svg>")


AS, SS, LS, WS, MS, DS, KS = '#5F6D7E', '#4B5867', '#36421F', '#6E7A88', '#5E6A78', '#15191E', '#0B0D10'

ICONS = []
def icon(key, name, cat):
    def deco(fn):
        ICONS.append((key, name, cat, fn)); return fn
    return deco

def mirror(d):
    """mirror path about x=48 (only absolute M/L/C/Q/Z with numbers)"""
    import re
    toks = re.findall(r'[A-Za-z]|-?[0-9.]+', d)
    out = []; i = 0; xturn = True
    for t in toks:
        if t.isalpha():
            out.append(t); xturn = True
        else:
            v = float(t)
            if xturn: v = 96 - v
            out.append(('%g' % v)); xturn = not xturn
    return ' '.join(out)

# ---------------- helpers ----------------
def glint(b, x, y, w=3, h=1.2):
    b.e(x, y, w, h, '#FFFFFF', op=.85)

def rotor(b, cx, cy, r, ang=20):
    b.c(cx, cy, r, 'prop', '#8D9BAC', .6, op=None)
    a = math.radians(ang)
    dx, dy = (r - 1) * math.cos(a), (r - 1) * math.sin(a)
    b.ln(f"M{cx-dx:.1f} {cy-dy:.1f} L{cx+dx:.1f} {cy+dy:.1f}", '#2E3640', 2.4)
    b.ln(f"M{cx-dx:.1f} {cy-dy:.1f} L{cx+dx:.1f} {cy+dy:.1f}", '#6B7785', .8)
    b.c(cx, cy, 2.6, 'hub', '#1D2228', .8)

def water(b, y=66):
    y += 2
    b.r(0, y, 96, 96 - y - 8, 'water')
    b.ln(f"M4 {y+4} Q10 {y+2} 16 {y+4} T28 {y+4} T40 {y+4} T52 {y+4} T64 {y+4} T76 {y+4} T88 {y+4}", '#FFFFFF', 1, .55)
    b.ln(f"M10 {y+10} Q16 {y+8} 22 {y+10} T34 {y+10} T46 {y+10} M58 {y+10} Q64 {y+8} 70 {y+10} T82 {y+10}", '#FFFFFF', .8, .35)

def track(b, x1, x2, y1, y2, n):
    h = y2 - y1
    b.r(x1, y1, x2 - x1, h, 'track', KS, rx=h / 2)
    b.r(x1 + 1.5, y1 + 1.5, x2 - x1 - 3, h - 3, 'none', '#5A616A', rx=(h - 3) / 2, sw=.9, extra="stroke-dasharray='1.6 1.6'")
    rr = h / 2 - 2.6
    step = (x2 - x1 - h) / (n - 1)
    for i in range(n):
        cx = x1 + h / 2 + i * step
        b.c(round(cx, 1), (y1 + y2) / 2 + .4, round(rr, 1), 'hub', '#0E1013', .8)
        b.c(round(cx, 1), (y1 + y2) / 2 + .4, 1.3, '#23272C')

def wheel(b, cx, cy, r=7.5):
    b.c(cx, cy, r, 'tyre', KS, 1)
    b.c(cx, cy, r * .5, 'hub', '#1A1D21', .8)
    b.c(cx, cy, r * .16, '#2A2E33')

def leds(b, pts):
    for x, y, col in pts:
        b.c(x, y, 1.4, col, op=None)

GREEN, AMBER, REDL = '#43C46B', '#F2A93B', '#E2574C'

# ================= 指控信息 (batch j) =================
CAT = '指控信息'
BL = '#25578F'

def box(b, x, y, w, h, dx=10, dy=6, fr='metal2', tp='metal', sd='metal3', st=MS, sw=1.2):
    b.p(f"M{x+w} {y} L{x+w+dx} {y-dy} L{x+w+dx} {y+h-dy} L{x+w} {y+h} Z", sd, st, sw)
    b.p(f"M{x} {y} L{x+dx} {y-dy} L{x+w+dx} {y-dy} L{x+w} {y} Z", tp, st, sw)
    b.r(x, y, w, h, fr, st, sw=sw)

def star(b, cx, cy, r, op=.95):
    k = r * .28
    b.p(f"M{cx} {cy-r} L{cx+k} {cy-k} L{cx+r} {cy} L{cx+k} {cy+k} L{cx} {cy+r} L{cx-k} {cy+k} L{cx-r} {cy} L{cx-k} {cy-k} Z", '#FFFFFF', op=op)

def clock(b, cx, cy, r):
    b.c(cx, cy, r, 'metal', MS, 1.2)
    b.c(cx, cy, r - 2.6, 'white', '#8794A3', .6)
    for a in range(0, 360, 30):
        x1 = cx + (r - 4.2) * math.sin(math.radians(a)); y1 = cy - (r - 4.2) * math.cos(math.radians(a))
        x2 = cx + (r - 6) * math.sin(math.radians(a)); y2 = cy - (r - 6) * math.cos(math.radians(a))
        b.ln(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}", '#5E6A78', 1)
    b.ln(f"M{cx} {cy} L{cx} {cy-r+6}", '#2B3440', 1.8)
    b.ln(f"M{cx} {cy} L{cx+(r-8)*.8:.1f} {cy+(r-8)*.35:.1f}", '#2B3440', 1.8)
    b.c(cx, cy, 1.5, '#E2574C')

def person(b, cx, cy, s=1.0, col='uniform'):
    b.c(cx, cy, 3.2 * s, 'skin', '#7A5D40', .5)
    b.p(f"M{cx-6*s} {cy+10*s} Q{cx-6*s} {cy+4.5*s} {cx} {cy+4.5*s} Q{cx+6*s} {cy+4.5*s} {cx+6*s} {cy+10*s} Z", col, '#22344A', .5)

DASH = "stroke-dasharray='2.4 1.8'"

@icon('cmd_shelter', '指挥方舱', CAT)
def _(b):
    b.sh(48, 86, 44, 3.4)
    b.r(4, 66, 88, 6, 'dkm2', DS, rx=1)
    b.p("M5 66 L5 46 Q5 42 9 40 L16 32 Q18 30 22 30 L30 30 L30 66 Z", 'land', LS)
    b.p("M10 45 L17 35 L27 35 L27 45 Z", 'canopy', '#1B2D40', .8)
    b.hl("M11 41 L17.5 33.5", 1, .6)
    b.r(30, 22, 62, 44, 'land', LS, rx=1.5)
    b.r(29, 18, 64, 6, 'landdk', LS, rx=2)
    b.r(40, 28, 32, 36, 'dkm2', DS, sw=1)
    b.r(43, 31, 12, 14, 'scr', '#0B1A2C', .6); b.r(57, 31, 12, 14, 'scr', '#0B1A2C', .6)
    b.ln("M45 36 L52 35 M45 40 L50 40 M60 41 L63 36 L67 38", '#9CC2EA', .8, .9)
    b.r(42, 51, 28, 3, 'metal3', MS, sw=.6); b.r(44, 54, 3, 10, '#2B3138'); b.r(65, 54, 3, 10, '#2B3138')
    b.c(51, 49, 2.2, '#56708F'); b.c(61, 49, 2.2, '#56708F')
    b.p("M72 28 L84 24 L84 64 L72 64 Z", 'landdk', LS, 1)
    b.ln("M74 34 L82 32 M74 56 L82 54", '#E1E6EC', .8, .5)
    b.ln("M38 18 L38 4 M33 8 L43 8 M35 13 L41 13", '#5E6A78', 1.4)
    b.ln("M84 19 L84 12", '#5E6A78', 1.6)
    b.g('rotate(-35 84 10)'); b.e(84, 10, 7, 3, 'metal', MS, 1); b.eg()
    b.c(88, 5.5, 1.2, '#E2574C')
    b.r(50, 13, 14, 5, 'metal', MS, rx=1, sw=.8)
    for x in (18, 52, 76):
        wheel(b, x, 72, 7)
    leds(b, [(33, 27, GREEN), (88, 28, AMBER)])
    b.hl("M31 21 L90 21", .9, .6)

@icon('cmd_hall', '联合指挥大厅', CAT)
def _(b):
    b.p("M3 4 L15 9 L15 46 L3 58 Z", 'metal3', MS)
    b.p("M93 4 L81 9 L81 46 L93 58 Z", 'dkm', DS)
    b.r(15, 9, 66, 37, 'metal2', MS)
    b.p("M15 46 L81 46 L94 88 L2 88 Z", 'metal3', MS)
    b.r(22, 13, 52, 28, 'dkm2', DS, rx=1.5)
    b.r(24.5, 15.5, 47, 23, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.p("M28 24 L36 20 L46 23 L44 31 L33 33 Z", 'land', op=.75)
    b.p("M54 20 L66 19 L68 28 L60 33 L52 28 Z", 'land', op=.75)
    b.ln("M26 28 L70 26 M26 33 L70 31 M40 16 L42 38 M56 16 L58 38", '#9CC2EA', .6, .5)
    b.ln("M31 30 L42 25 L56 29 L64 23", '#F2A93B', 1, .95, extra="stroke-dasharray='2 1.6'")
    b.c(42, 25, 1.5, REDL); b.c(64, 23, 1.5, GREEN); b.c(31, 30, 1.5, GREEN)
    b.p("M26 16 L33 16 L28 38 L26 38 Z", '#FFFFFF', op=.12)
    b.raw("<g stroke='#5E6A78' stroke-width='.7'>")
    for (x, y, w, h, n, s) in ((16, 54, 64, 5, 3, 9), (8, 63, 80, 6, 4, 10), (2, 73, 92, 7, 5, 12)):
        step = w / n
        for i in range(n):
            cx = round(x + step * (i + .5), 1)
            dw = round(step - 6, 1)
            b.raw(f"<rect x='{cx-dw/2:.1f}' y='{y}' width='{dw}' height='{h}' rx='1' fill='#D6DCE3'/>")
            b.raw(f"<rect x='{cx-s*.4:.1f}' y='{y-s*.6:.1f}' width='{s*.8:.1f}' height='{s*.6:.1f}' rx='.6' fill='#2F6FB0' stroke='#0B1A2C'/>")
            b.raw(f"<path d='M{cx-s*.5:.1f} {y+h+s*.8:.1f} Q{cx-s*.5:.1f} {y+h+s*.3:.1f} {cx} {y+h+s*.3:.1f} Q{cx+s*.5:.1f} {y+h+s*.3:.1f} {cx+s*.5:.1f} {y+h+s*.8:.1f} Z' fill='#56708F' stroke='#22344A'/>")
    b.raw("</g>")
    leds(b, [(10, 40, GREEN), (86, 40, AMBER)])
    b.hl("M16 10.4 L80 10.4", .9, .7)

@icon('duty_console', '作战值班席', CAT)
def _(b):
    b.sh(48, 90, 42, 3.2)
    b.ln("M86 58 L86 28", '#5E6A78', 2.4); b.ln("M86 58 L86 28", '#C9D1DA', .9)
    b.r(81.5, 16, 9, 12, 'orange', '#7A4A12', rx=3, sw=.8)
    b.e(86, 16.5, 4.5, 1.8, '#F6D08A', '#7A4A12', .6)
    b.hl("M83.4 19 L83.4 25", 1, .6)
    b.r(44, 46, 8, 14, 'metal3', MS, sw=.8)
    b.p("M8 24 L29 20 L29 48 L8 46 Z", 'dkm2', DS)
    b.p("M67 20 L88 24 L88 46 L67 48 Z", 'dkm2', DS)
    b.r(29, 16, 38, 32, 'dkm2', DS, rx=1.5)
    b.p("M10.5 26.2 L26.6 23 L26.6 44.6 L10.5 43.4 Z", 'scr', '#0B1A2C', .5)
    b.p("M69.4 23 L85.5 26.2 L85.5 43.4 L69.4 44.6 Z", 'scr', '#0B1A2C', .5)
    b.r(31.5, 18.5, 33, 27, 'scr', '#0B1A2C', rx=1, sw=.5)
    b.p("M34 30 L42 24 L50 28 L60 22 L60 40 L34 40 Z", 'land', op=.6)
    b.ln("M36 36 L44 30 L52 34 L60 26", '#F2A93B', 1, .95)
    b.c(44, 30, 1.5, REDL); b.c(60, 26, 1.5, GREEN)
    b.ln("M13 31 L24 29.4 M13 35 L21 34 M13 39 L23 38 M72 29.4 L83 31 M72 34 L80 35 M72 38 L82 39", '#9CC2EA', .9, .8)
    b.p("M33 19 L40 19 L35 44 L33 44 Z", '#FFFFFF', op=.13)
    b.p("M4 64 L14 58 L82 58 L92 64 Z", 'metal', MS)
    b.r(4, 64, 88, 22, 'metal2', MS)
    b.ln("M4 68 L92 68", '#97A3B1', .8)
    b.p("M26 63 L31 59.5 L63 59.5 L68 63 Z", 'dkm', DS, .7)
    b.ln("M32 61 L62 61", '#9AA5B1', .8, .8)
    b.e(77, 61.4, 3.4, 1.5, 'dkm2', DS, .6)
    b.ln("M10 63 Q10 57 16 57 Q22 57 22 62", '#3A4048', 2); b.r(8.5, 61, 3.4, 4.4, 'dkm', DS, rx=1.2, sw=.5)
    b.r(12, 72, 24, 10, 'metal3', MS, rx=1, sw=.8)
    leds(b, [(56, 76, GREEN), (62, 76, GREEN), (68, 76, AMBER), (74, 76, GREEN)])
    b.r(46, 72, 6, 6, 'dkm2', DS, rx=1, sw=.6)
    b.hl("M6 63.2 L15 58.6 L80 58.6", .9, .85)

@icon('sit_3d', '三维态势显示', CAT)
def _(b):
    b.sh(48, 88, 38, 3.2)
    b.p("M12 74 L12 80 A36 10 0 0 0 84 80 L84 74 Z", 'cylM', MS)
    b.e(48, 74, 36, 10, 'metal', MS)
    b.e(48, 74, 30, 7.4, 'dkm2', DS, .8)
    b.e(48, 74, 24, 5.6, 'none', '#8FD0FF', 1, .85)
    b.e(48, 74, 12, 3, 'node', '#1F4F8C', .6)
    for (x1, y1, x2, y2) in ((22, 73, 14, 52), (74, 73, 82, 52), (36, 78, 27, 55), (60, 78, 69, 55)):
        b.ln(f"M{x1} {y1} L{x2} {y2}", '#8FD0FF', 1, .35)
    b.p("M48 30 L84 48 L48 66 L12 48 Z", 'glass', '#3D86D6', 1, .38)
    for i in (.25, .5, .75):
        b.ln(f"M{12+36*i:.1f} {48-18*i:.1f} L{48+36*i:.1f} {66-18*i:.1f}", '#E8F6FF', .7, .55)
        b.ln(f"M{48+36*i:.1f} {30+18*i:.1f} L{12+36*i:.1f} {48+18*i:.1f}", '#E8F6FF', .7, .55)
    b.p("M26 52 L38 30 L50 53 L38 59 Z", 'glass', '#E8F6FF', .8, .8)
    b.p("M46 55 L60 26 L76 51 L60 61 Z", 'glass', '#E8F6FF', .8, .85)
    b.p("M38 30 L50 53 L38 59 Z", '#FFFFFF', op=.28)
    b.p("M60 26 L76 51 L60 61 Z", '#FFFFFF', op=.28)
    b.ln("M38 30 L38 59 M60 26 L60 61", '#E8F6FF', .7, .6)
    b.c(38, 24, 2.4, REDL, '#FFFFFF', .8); b.c(60, 20, 2.4, GREEN, '#FFFFFF', .8)
    b.ln("M38 26 L38 30 M60 22 L60 26", '#FFFFFF', .8, .8)
    b.ln("M44 44 Q52 38 66 42", '#F2A93B', 1.3, .95, extra="stroke-dasharray='2 1.6'")
    b.hl("M16 49 L48 33", .9, .8)

@icon('rugged_pc', '加固计算机', CAT)
def _(b):
    b.sh(50, 88, 40, 3.4)
    b.p("M72 40 L92 30 L92 70 L72 80 Z", 'dkm2', DS)
    b.p("M10 40 L30 30 L92 30 L72 40 Z", 'dkm', DS)
    b.r(10, 40, 62, 40, 'dkm', DS, rx=3)
    b.ln("M32 32 L36 21 L66 21 L72 32", '#3A4048', 3.4); b.ln("M32 32 L36 21 L66 21 L72 32", '#8794A3', 1)
    b.r(14, 44, 54, 32, 'metal2', MS, rx=1.5, sw=1)
    b.r(18, 48, 28, 20, 'dkm2', DS, rx=1, sw=.8)
    b.r(20, 50, 24, 16, 'scr', '#0B1A2C', sw=.5)
    b.ln("M22 62 L28 56 L33 60 L42 52", '#7FE0A0', 1.1)
    b.ln("M22 54 L30 54", '#9CC2EA', .8, .8)
    for (cx, cy) in ((54, 54), (62, 54), (54, 64), (62, 64)):
        b.c(cx, cy, 3.3, 'metal', MS, .9); b.c(cx, cy, 1.5, 'dkm2')
    b.r(18, 71, 10, 3, 'dkm', DS, rx=1, sw=.5)
    leds(b, [(34, 72.5, GREEN), (38, 72.5, AMBER)])
    for (x, y) in ((7, 37), (65, 37), (7, 71), (65, 71)):
        b.r(x, y, 10, 10, 'orange', '#7A4A12', rx=3, sw=.8)
    b.p("M76 34 L90 32 L90 40 L76 46 Z", '#FFFFFF', op=.12)
    b.hl("M16 39.4 L31 31.6 L90 31.6", .9, .65)

@icon('vehicle_terminal', '车载指控终端', CAT)
def _(b):
    b.sh(44, 90, 32, 3)
    b.r(26, 82, 36, 6, 'metal3', MS, rx=1.5)
    b.c(31, 85, 1.2, '#2B3138'); b.c(57, 85, 1.2, '#2B3138')
    b.ln("M44 82 L44 66 Q44 58 40 56", '#3A4048', 5); b.ln("M44 82 L44 66 Q44 58 40 56", '#8794A3', 1.6)
    b.c(44, 70, 3, 'hub', '#1D2228', .8)
    b.r(6, 12, 66, 44, 'dkm', DS, rx=4)
    b.r(10, 16, 58, 36, 'scr', '#0B1A2C', rx=1.5, sw=.7)
    b.p("M14 36 L24 26 L34 30 L36 42 L22 48 Z", 'land', op=.7)
    b.p("M44 22 L58 20 L62 32 L52 38 L44 32 Z", 'land', op=.7)
    b.ln("M12 30 L66 28 M12 42 L66 40 M30 17 L32 51 M50 17 L52 51", '#9CC2EA', .6, .5)
    b.ln("M18 44 L30 36 L44 38 L56 26", '#F2A93B', 1.3, .95, extra=DASH)
    b.c(56, 26, 2, REDL, '#FFFFFF', .6); b.c(18, 44, 2, GREEN, '#FFFFFF', .6)
    b.p("M13 17 L27 17 L17 51 L13 51 Z", '#FFFFFF', op=.12)
    leds(b, [(66, 54, GREEN)])
    b.ln("M72 24 Q78 20 80 26", '#3A4048', 1.6)
    b.ln("M84 60 Q76 64 84 68 Q92 72 82 76 Q74 80 80 84", '#3A4048', 2)
    b.r(78, 30, 12, 30, 'dkm', DS, rx=5)
    b.r(80.5, 24, 7, 8, 'dkm2', DS, rx=2, sw=.8)
    b.c(84, 40, 2, 'orange', '#7A4A12', .6)
    b.r(81.5, 46, 5, 8, 'metal3', MS, rx=1, sw=.6)
    b.hl("M9 15 L50 14", .9, .55)

@icon('ar_glasses', 'AR 眼镜', CAT)
def _(b):
    b.sh(48, 88, 36, 3)
    body = "M8 40 Q8 32 16 32 L80 32 Q88 32 88 40 L86 54 Q84 62 76 62 L62 62 Q56 62 54 56 L52 52 Q48 49 44 52 L42 56 Q40 62 34 62 L20 62 Q12 62 10 54 Z"
    b.ln("M14 32 Q48 8 82 32", '#2B3138', 6); b.ln("M14 32 Q48 8 82 32", '#6A7480', 2)
    b.drop(body, 2, 3, .18)
    b.p(body, 'dkm', DS)
    b.p("M14 40 Q14 36 19 36 L40 36 Q45 36 45 41 L44 50 Q43 57 36 57 L22 57 Q17 57 16 52 Z", 'canopy', '#0B1A2C', .8)
    b.p("M82 40 Q82 36 77 36 L56 36 Q51 36 51 41 L52 50 Q53 57 60 57 L74 57 Q79 57 80 52 Z", 'canopy', '#0B1A2C', .8)
    b.p("M17 38 L28 37 L20 54 L17 52 Z", '#FFFFFF', op=.2); b.p("M54 38 L65 37 L57 54 L54 52 Z", '#FFFFFF', op=.2)
    b.ln("M58 47 L66 47 M62 43 L62 51", '#7FE0A0', 1, .9)
    b.c(62, 47, 4.5, 'none', '#7FE0A0', 1)
    b.ln("M22 44 L36 44 M22 49 L30 49", '#9CC2EA', .9, .8)
    b.c(48, 37, 1.6, '#23272C', '#8794A3', .5)
    leds(b, [(48, 42, GREEN)])
    b.hl("M12 34 L82 34", .9, .55)
    b.p("M64 4 L88 4 L88 18 L64 18 Z", 'glass', '#E8F6FF', .8, .55)
    b.ln("M67 9 L83 9 M67 13 L77 13", '#FFFFFF', 1, .9)

@icon('cmd_software', '指挥软件', CAT)
def _(b):
    b.drop("M6 10 L90 10 L90 86 L6 86 Z", 2.5, 3, .16)
    b.r(6, 10, 84, 76, 'metal', MS, rx=4)
    b.p("M10 10 L86 10 Q90 10 90 14 L90 22 L6 22 L6 14 Q6 10 10 10 Z", 'glass', BL, 1)
    b.c(13, 16, 2, REDL); b.c(19.5, 16, 2, AMBER); b.c(26, 16, 2, GREEN)
    b.r(40, 14, 40, 4, '#FFFFFF', rx=2, op=.55)
    b.r(10, 26, 50, 42, 'scr', '#0B1A2C', rx=1.5, sw=.7)
    b.p("M13 50 L24 34 L36 38 L40 52 L26 62 Z", 'land', op=.75)
    b.p("M42 32 L56 30 L57 44 L48 50 Z", 'land', op=.75)
    b.ln("M12 38 L58 36 M12 52 L58 50 M30 28 L32 66 M46 28 L48 66", '#9CC2EA', .6, .5)
    b.ln("M16 58 L28 46 L44 48 L52 36", '#F2A93B', 1.3, .95, extra=DASH)
    b.c(52, 36, 2.2, REDL, '#FFFFFF', .6); b.c(16, 58, 2.2, GREEN, '#FFFFFF', .6); b.c(44, 48, 1.8, AMBER)
    b.r(64, 26, 22, 42, 'white', MS, rx=1.5, sw=.8)
    for i in range(5):
        y = 29 + i * 7.8
        b.c(68, y + 2.6, 1.5, [GREEN, GREEN, AMBER, REDL, GREEN][i])
        b.r(71.5, y + 1.2, 11, 2.8, '#8794A3', rx=1, op=.8)
    b.r(10, 72, 22, 10, 'glass', BL, rx=2, sw=.8)
    b.r(35, 72, 22, 10, 'orange', '#7A4A12', rx=2, sw=.8)
    b.r(60, 72, 26, 10, 'red', '#6A1D14', rx=2, sw=.8)
    b.ln("M14 77 L28 77 M39 77 L53 77 M64 77 L82 77", '#FFFFFF', 1.4, .85)
    b.p("M12 27 L22 27 L14 66 L12 66 Z", '#FFFFFF', op=.1)
    b.hl("M9 11.4 L86 11.4", .9, .7)

@icon('mission_planning', '任务规划', CAT)
def _(b):
    b.sh(50, 88, 40, 3)
    b.p("M8 60 L66 60 L66 66 L8 66 Z", 'metal3', MS)
    b.p("M66 60 L92 36 L92 42 L66 66 Z", 'dkm', DS)
    b.p("M8 60 L34 36 L92 36 L66 60 Z", 'cloud', '#5D7FA6', 1.2)
    b.p("M16 56 L26 46 L44 46 L36 56 Z", 'land', op=.7)
    b.p("M56 52 L70 40 L84 40 L74 52 Z", 'land', op=.7)
    b.p("M44 54 L56 44 L62 44 L52 54 Z", 'glass', op=.75)
    b.ln("M14 59 L38 38 M24 59 L48 38 M34 59 L58 38 M44 59 L68 38 M54 59 L78 38 M20 52 L72 52 M28 44 L82 44", '#8FA9C8', .6, .55)
    b.ln("ZM30 50 L30 40 M44 52 L44 34 M56 44 L56 28".replace('Z', ''), '#5E6A78', .8, .7, extra="stroke-dasharray='1.4 1.4'")
    b.ln("M16 56 L30 50 L44 52 L56 44 L74 42", '#E8872B', 1.8, .98, extra="stroke-dasharray='3 2'")
    b.c(16, 56, 3, 'node', '#1F4F8C', .8)
    for (x, y, t) in ((30, 50, 38), (44, 52, 32), (56, 44, 26)):
        b.c(x, y, 2, '#FFFFFF', '#E8872B', 1)
        b.c(x, t, 3, 'sphere', '#5E6A78', .8)
    b.ln("M74 42 L74 12", '#5E6A78', 1.6)
    b.p("M74.6 12 L92 16 L74.6 22 Z", 'red', '#7A2219', .8)
    b.c(74, 42, 2, '#2B3440')
    b.hl("M10 58.8 L34.4 37.4 L90 37.4", .9, .8)

@icon('data_lake', '数据湖', CAT)
def _(b):
    b.sh(48, 90, 38, 3.2)
    b.p("M10 52 L10 76 A38 10 0 0 0 86 76 L86 52 Z", 'cylM', MS)
    b.e(48, 52, 38, 10.5, 'metal', MS)
    b.e(48, 53.5, 33, 8.2, 'glass', BL, .8)
    b.e(48, 53.5, 24, 5.8, 'none', '#FFFFFF', 1, .75)
    b.e(48, 53.5, 14, 3.2, 'none', '#FFFFFF', 1, .85)
    b.e(48, 53.5, 5, 1.2, '#FFFFFF', op=.9)
    b.ln("M12 64 Q24 70 36 64 T60 64 T84 64", '#FFFFFF', 1.1, .6)
    b.r(10, 68, 76, 5, 'glass', BL, sw=.6, op=.55)
    b.ln("M14 80 Q26 85 38 80 T62 80 T82 80", '#FFFFFF', 1, .45)
    b.ln("M28 24 L28 44 M50 16 L50 46 M72 26 L72 44", '#8FD0FF', 1, .55, extra="stroke-dasharray='1.8 2'")
    for (x, y, c) in ((24, 14, 'glass'), (46, 6, 'orange'), (68, 16, 'land'), (36, 30, 'orange'), (58, 32, 'glass')):
        b.r(x, y, 9, 8, c, '#5E6A78', rx=1.8, sw=.8)
        b.ln(f"M{x+2} {y+2.5} L{x+7} {y+2.5} M{x+2} {y+5.2} L{x+6} {y+5.2}", '#FFFFFF', .8, .85)
    b.hl("M13 49.6 Q26 43 48 42", .9, .8)

@icon('edge_node', '边缘计算节点', CAT)
def _(b):
    b.sh(50, 88, 38, 3.2)
    for x, y in ((72, 10), (60, 22)):
        b.ln(f"M{x} 40 L{x} {y}", '#2B3138', 3.6); b.ln(f"M{x} 40 L{x} {y}", '#6A7480', 1.2)
    b.ln("M66 8 Q72 3 78 8 M69 11 Q72 8 75 11", '#43C46B', 1.2, .85)
    box(b, 10, 46, 56, 32, 18, 10, 'metal2', 'metal', 'metal3')
    for i in range(5):
        b.ln(f"M{20+i*10} 45 L{30+i*10} 37", '#8794A3', 1.3, .9)
    b.r(15, 51, 28, 22, 'dkm2', DS, rx=2, sw=.8)
    for i in range(4):
        b.ln(f"M{23+i*4.2} 51.6 L{23+i*4.2} 54 M{23+i*4.2} 70 L{23+i*4.2} 72.6", '#C9A145', 1)
    for i in range(3):
        b.ln(f"M16 {58+i*4} L21 {58+i*4} M37 {58+i*4} L42 {58+i*4}", '#C9A145', 1)
    b.r(21, 54.5, 16, 15, 'node', '#0F2F58', rx=1.5, sw=.8)
    b.r(24, 57.5, 10, 9, 'dkm2', '#9CC2EA', rx=1, sw=.5)
    star(b, 29, 62, 3.2, .9)
    b.r(48, 53, 12, 5, 'dkm2', DS, rx=1, sw=.5); b.r(48, 61, 12, 5, 'dkm2', DS, rx=1, sw=.5)
    leds(b, [(50, 70, GREEN), (54, 70, GREEN), (58, 70, AMBER)])
    b.r(14, 78, 8, 4, 'dkm2', DS, rx=1); b.r(54, 78, 8, 4, 'dkm2', DS, rx=1)
    b.hl("M12 47.4 L66 47.4", .9, .8)

@icon('gateway', '安全网关', CAT)
def _(b):
    b.sh(48, 90, 42, 3.2)
    b.r(12, 38, 14, 48, 'metal2', MS, rx=2); b.r(70, 38, 14, 48, 'metal2', MS, rx=2)
    b.r(26, 40, 44, 44, 'glass', BL, sw=.8, op=.32)
    b.ln("M30 44 L30 80 M38 44 L38 80 M58 44 L58 80 M66 44 L66 80", '#E8F6FF', .6, .35)
    b.p("M32 54 L50 54 L50 49 L62 57 L50 65 L50 60 L32 60 Z", '#43C46B', '#1F6B3B', .9, .95)
    b.p("M64 70 L48 70 L48 66 L36 73 L48 80 L48 76 L64 76 Z", 'node', '#1F4F8C', .9, .95)
    b.r(6, 14, 84, 24, 'metal', MS, rx=4)
    b.ln("M8 36 L88 36", '#97A3B1', .8)
    b.p("M48 4 L60 9 L60 22 Q60 31 48 36 Q36 31 36 22 L36 9 Z", 'glass', BL, 1.2)
    b.p("M48 8 L56 11.5 L56 22 Q56 28 48 31.5 Z", '#FFFFFF', op=.22)
    b.ln("M42 20 L47 25 L55 15", '#FFFFFF', 2)
    leds(b, [(18, 22, GREEN), (24, 22, GREEN), (72, 22, AMBER), (78, 22, GREEN)])
    leds(b, [(19, 46, GREEN), (77, 46, GREEN)])
    b.hl("M10 15.4 L34 15.4 M62 15.4 L86 15.4", .9, .8)

@icon('crypto', '密码机', CAT)
def _(b):
    b.sh(50, 88, 40, 3.2)
    box(b, 8, 42, 62, 38, 16, 9, 'dkm', 'dkm2', 'dkm2', DS)
    b.r(12, 46, 54, 30, 'metal2', MS, rx=1.5, sw=1)
    for i in range(3):
        for j in range(3):
            b.c(17 + i * 5.2, 52 + j * 5.2, 1.6, 'dkm2', '#1E2328', .4)
    b.r(52, 50, 10, 6, 'dkm2', DS, rx=1, sw=.6); b.ln("M54 53 L60 53", '#7FE0A0', 1.2)
    leds(b, [(54, 65, GREEN), (58, 65, AMBER), (62, 65, GREEN)])
    b.r(14, 68, 20, 4, 'dkm2', DS, rx=1, sw=.5)
    b.ln("M44 42 L44 30 Q44 20 54 20 Q64 20 64 30 L64 42", '#8A6A20', 6.4)
    b.ln("M44 42 L44 30 Q44 20 54 20 Q64 20 64 30 L64 42", '#E8D08C', 3.2)
    b.hl("M46.4 30 Q46.4 22.6 54 22.6", 1, .8)
    b.r(36, 40, 36, 28, 'gold', '#8A6A20', rx=4, sw=1.2)
    b.c(54, 52, 4, 'dkm2', '#5A4210', .8); b.p("M52.2 54 L55.8 54 L56.6 62 L51.4 62 Z", 'dkm2')
    b.hl("M39 44 L69 44", 1.2, .7)
    b.c(82, 72, 4.5, 'gold', '#8A6A20', 1); b.c(82, 72, 1.6, '#FFFFFF', op=.8)
    b.ln("M86.5 72 L93 72 M91 72 L91 76", '#8A6A20', 2)

@icon('identity', '身份认证', CAT)
def _(b):
    b.sh(48, 91, 36, 2.8)
    b.g('rotate(-8 40 44)')
    b.drop("M8 18 L70 18 L70 64 L8 64 Z", 2.5, 3, .16)
    b.r(8, 18, 62, 46, 'white', MS, rx=4)
    b.p("M12 18 L66 18 Q70 18 70 22 L70 30 L8 30 L8 22 Q8 18 12 18 Z", 'glass', BL, 1)
    b.ln("M14 24 L34 24", '#FFFFFF', 2, .85)
    b.r(13, 35, 20, 24, 'appbg', '#25578F', rx=2, sw=.8)
    person(b, 23, 42, 1.3)
    b.ln("M38 38 L64 38 M38 44 L58 44 M38 50 L50 50", '#8794A3', 1.8, .9)
    b.r(55, 50, 10, 8, 'gold', '#8A6A20', rx=1.5, sw=.8)
    b.ln("M55 54 L65 54 M60 50 L60 58", '#8A6A20', .6)
    b.hl("M10 19.4 L66 19.4", .8, .7)
    b.eg()
    b.c(66, 66, 21, 'node', '#1F4F8C', 1.4)
    b.c(66, 66, 18.5, 'none', '#FFFFFF', .7, .5)
    for r_ in (4, 8, 12, 16):
        b.ln(f"M{66-r_} {70-r_*.1:.1f} Q{66-r_} {66-r_-1} 66 {66-r_-1} Q{66+r_} {66-r_-1} {66+r_} {68}", '#FFFFFF', 1.3, .92)
    b.ln("M56 76 Q54 70 55 66 M66 79 Q66 72 64 68 M76 76 Q78 72 77 66", '#FFFFFF', 1.3, .8)
    b.c(82, 46, 8, '#43C46B', '#1F6B3B', 1.2)
    b.ln("M78 46 L81 49 L86.5 43", '#FFFFFF', 2)

@icon('audit_log', '日志审计', CAT)
def _(b):
    b.drop("M12 8 L68 8 L68 84 L12 84 Z", 2.5, 3.5, .16)
    b.p("M16 8 L56 8 L68 20 L68 80 Q68 84 64 84 L16 84 Q12 84 12 80 L12 12 Q12 8 16 8 Z", 'white', MS)
    b.p("M56 8 L56 17 Q56 20 59 20 L68 20 Z", 'metal2', MS, 1)
    b.ln("M18 16 L40 16", '#5E6A78', 2.2)
    cols = [GREEN, GREEN, AMBER, REDL, GREEN, '#3D86D6']
    for i in range(6):
        y = 26 + i * 9.6
        b.r(18, y, 7, 5, cols[i], '#5E6A78', rx=1.2, sw=.5)
        b.ln(f"M28 {y+2.5} L{50 + (i*7) % 14} {y+2.5}", '#8794A3', 1.8, .9)
    b.ln("M72 76 L90 91", '#3A4048', 6); b.ln("M72 76 L90 91", '#8794A3', 2.4)
    b.c(60, 62, 17, 'glass', None, 0, .38)
    b.c(60, 62, 17, 'none', '#3A4048', 4)
    b.c(60, 62, 17, 'none', '#C9D1DA', 1.4)
    b.ln("M50 54 Q55 49 62 49", '#FFFFFF', 1.8, .85)
    b.ln("M50 62 L68 62", '#E2574C', 2)
    b.ln("M50 67 L62 67", '#5E6A78', 1.6, .8)

@icon('llm', '大模型', CAT)
def _(b):
    b.sh(40, 91, 32, 3)
    for i in range(5):
        x = 17 + i * 8
        b.r(x, 31, 3.4, 5, 'metal3', MS, sw=.5); b.r(x, 82, 3.4, 5, 'metal3', MS, sw=.5)
        b.r(5, 40 + i * 8, 5, 3.4, 'metal3', MS, sw=.5); b.r(60, 40 + i * 8, 5, 3.4, 'metal3', MS, sw=.5)
    b.drop("M10 36 L60 36 L60 82 L10 82 Z", 2, 3, .18)
    b.r(10, 36, 50, 46, 'dkm', DS, rx=5)
    b.r(14, 40, 42, 38, 'dkm2', '#6A7480', rx=3, sw=.8)
    b.r(20, 46, 30, 26, 'node', '#0F2F58', rx=3, sw=1)
    b.ln("M24 52 L32 52 L32 58 M46 52 L40 52 L40 60 M24 66 L34 66 M46 66 L38 66 L38 62", '#E8F6FF', .9, .8)
    star(b, 35, 59, 5.5)
    b.hl("M12 38.4 L56 38.4", .8, .6)
    b.drop("M38 8 Q38 6 40 6 L84 6 Q92 6 92 14 L92 30 Q92 38 84 38 L58 38 L46 48 L48 38 L46 38 Q38 38 38 30 Z", 2, 3, .16)
    b.p("M46 6 L84 6 Q92 6 92 14 L92 30 Q92 38 84 38 L60 38 L47 48 L49 38 L46 38 Q38 38 38 30 L38 14 Q38 6 46 6 Z", 'white', '#5D7FA6', 1.3)
    for i in range(3):
        b.c(52 + i * 10, 22, 3, '#3D86D6', '#25578F', .5)
    b.hl("M44 8.6 L82 8.6", .9, .8)
    b.r(62, 56, 28, 20, 'orange', '#7A4A12', rx=6, sw=1)
    b.ln("M67 63 L85 63 M67 69 L79 69", '#FFFFFF', 1.8, .9)

@icon('agent_platform', '智能体平台', CAT)
def _(b):
    b.sh(48, 91, 42, 3)
    b.p("M6 74 L6 82 A42 9 0 0 0 90 82 L90 74 Z", 'cylM', MS)
    b.e(48, 74, 42, 9, 'metal', MS)
    b.e(48, 74, 30, 6, 'none', '#97A3B1', .9, .8)
    b.e(48, 72, 9, 3.4, 'node', '#1F4F8C', .8)
    b.e(48, 71, 4, 1.4, '#FFFFFF', op=.8)
    for (x, y) in ((20, 48), (76, 48), (48, 46)):
        b.ln(f"M{x} {y} L48 71", '#3D86D6', 1.6, .85, extra=DASH)
        b.c(x, y, 2, 'node', '#1F4F8C', .6)
    def head(cx, cy, s, eye, ant):
        w, h = 24 * s, 20 * s
        x, y = cx - w / 2, cy - h / 2
        b.ln(f"M{cx} {y:.1f} L{cx} {y-5*s:.1f}", '#5E6A78', 1.4)
        b.c(cx, round(y - 6 * s, 1), round(2.2 * s, 1), ant, '#5E6A78', .6)
        b.r(round(x - 3 * s, 1), round(cy - 3 * s, 1), round(3 * s, 1), round(7 * s, 1), 'metal3', MS, rx=1, sw=.6)
        b.r(round(x + w, 1), round(cy - 3 * s, 1), round(3 * s, 1), round(7 * s, 1), 'metal3', MS, rx=1, sw=.6)
        b.r(round(x, 1), round(y, 1), w, h, 'metal', MS, rx=round(6 * s, 1))
        b.r(round(x + 3 * s, 1), round(y + 4 * s, 1), round(w - 6 * s, 1), round(10 * s, 1), 'dkm2', DS, rx=round(4 * s, 1), sw=.7)
        b.c(round(cx - 4.4 * s, 1), round(y + 9 * s, 1), round(1.9 * s, 1), eye); b.c(round(cx + 4.4 * s, 1), round(y + 9 * s, 1), round(1.9 * s, 1), eye)
        b.ln(f"M{x+4*s:.1f} {y+2.2*s:.1f} L{x+w-6*s:.1f} {y+2.2*s:.1f}", '#FFFFFF', 1, .8)
    head(20, 38, .9, '#7FE0A0', GREEN)
    head(76, 38, .9, '#8FD0FF', '#3D86D6')
    head(48, 30, 1.15, '#F2A93B', AMBER)

@icon('video_conf', '视频会议终端', CAT)
def _(b):
    b.sh(48, 91, 38, 3)
    b.r(44, 62, 8, 14, 'metal3', MS, sw=.8)
    b.e(48, 79, 24, 5, 'metal2', MS); b.e(48, 78, 18, 3, 'metal', None)
    b.r(8, 14, 80, 50, 'dkm2', DS, rx=4)
    b.r(12, 18, 72, 42, 'scr', '#0B1A2C', rx=1.5, sw=.6)
    for i, (x, y) in enumerate([(14, 20), (49, 20), (14, 40), (49, 40)]):
        b.r(x, y, 33, 18, 'appbg', '#0B1A2C', rx=1.5, sw=.6, op=.9)
        person(b, x + 16.5, y + 5, .85, ['uniform', 'canopy', 'uniform', 'canopy'][i])
    b.r(49.5, 20.5, 32, 17, 'none', GREEN, rx=1.5, sw=1.3)
    b.r(34, 5, 28, 8, 'dkm', DS, rx=3)
    b.c(48, 9, 2.6, 'lens', '#0B1A2C', .8)
    b.c(47.4, 8.4, .8, '#FFFFFF', op=.9)
    leds(b, [(40, 9, GREEN), (56, 9, AMBER)])
    b.p("M14 19 L26 19 L18 59 L14 59 Z", '#FFFFFF', op=.1)
    b.hl("M11 15.4 L84 15.4", .9, .55)

@icon('digital_twin', '数字孪生', CAT)
def _(b):
    b.sh(48, 91, 40, 3)
    b.e(48, 84, 40, 7, 'metal3', MS)
    b.e(48, 83, 36, 5.4, 'dkm2', DS, .8)
    box(b, 6, 52, 34, 28, 16, 9, 'metal2', 'metal', 'metal3')
    b.r(10, 57, 18, 12, 'scr', '#0B1A2C', rx=1, sw=.5)
    b.ln("M12 65 L17 61 L22 64 L26 59", '#7FE0A0', 1)
    leds(b, [(33, 60, GREEN), (33, 66, AMBER)])
    b.r(10, 73, 14, 3, 'dkm2', DS, rx=1, sw=.5)
    b.hl("M7 53.4 L40 53.4", .9, .8)
    x, y, w, h, dx, dy = 52, 24, 28, 26, 14, 8
    wf = '#3D86D6'
    b.p(f"M{x} {y} L{x+dx} {y-dy} L{x+w+dx} {y-dy} L{x+w} {y} Z", 'glass', wf, 1, .35)
    b.p(f"M{x+w} {y} L{x+w+dx} {y-dy} L{x+w+dx} {y+h-dy} L{x+w} {y+h} Z", 'glass', wf, 1, .45)
    b.r(x, y, w, h, 'glass', wf, sw=1, op=.3)
    b.ln(f"M{x} {y+h} L{x+dx} {y+h-dy} L{x+w+dx} {y+h-dy} M{x+dx} {y-dy} L{x+dx} {y+h-dy}", wf, 1, .6, extra="stroke-dasharray='2 1.6'")
    for (px, py) in ((x, y), (x+w, y), (x, y+h), (x+w, y+h), (x+dx, y-dy), (x+w+dx, y-dy), (x+w+dx, y+h-dy)):
        b.c(px, py, 1.7, '#E8F6FF', wf, .8)
    b.ln("M30 49 Q38 30 48 32", '#F2A93B', 1.8, .95, extra="stroke-dasharray='3 2'")
    b.p("M46 28 L53 32 L46 36 Z", '#F2A93B')
    b.ln("M70 54 Q70 70 48 74", '#43C46B', 1.8, .95, extra="stroke-dasharray='3 2'")
    b.p("M49 70 L42 74 L49 78 Z", '#43C46B')
    b.hl("M54 25.4 L66 18 L92 18", .9, .8)

@icon('dashboard', '数据看板', CAT)
def _(b):
    b.sh(48, 92, 30, 2.6)
    b.r(40, 80, 16, 8, 'metal3', MS, sw=.8); b.r(30, 86, 36, 4, 'metal2', MS, rx=2, sw=.8)
    b.drop("M6 8 L90 8 L90 82 L6 82 Z", 2.5, 3, .16)
    b.r(6, 8, 84, 74, 'dkm', DS, rx=4)
    b.r(10, 12, 28, 30, 'white', MS, rx=2, sw=.8)
    b.c(24, 29, 9.5, 'none', '#D3DAE2', 4.4)
    b.ln("M24 19.5 A9.5 9.5 0 1 1 15.6 33.6", '#43C46B', 4.4)
    b.ln("M15.6 33.6 A9.5 9.5 0 0 1 14.6 25", '#F2A93B', 4.4)
    b.r(18, 27.7, 12, 2.6, '#5E6A78', rx=1)
    b.r(42, 12, 44, 30, 'white', MS, rx=2, sw=.8)
    b.p("M45 36 L52 28 L59 32 L68 21 L76 26 L83 17 L83 39 L45 39 Z", 'glass', op=.45)
    b.ln("M45 36 L52 28 L59 32 L68 21 L76 26 L83 17", '#3D86D6', 1.8)
    b.c(68, 21, 2, '#FFFFFF', '#3D86D6', 1)
    b.r(10, 46, 38, 32, 'white', MS, rx=2, sw=.8)
    for i, hh in enumerate((10, 18, 14, 24, 17)):
        b.r(14 + i * 6.8, 74 - hh, 5, hh, ['glass', 'glass', 'orange', 'glass', 'land'][i], '#5E6A78', sw=.5)
    b.ln("M13 74.5 L45 74.5", '#8794A3', .8)
    b.r(52, 46, 34, 32, 'white', MS, rx=2, sw=.8)
    b.r(56, 51, 14, 5, '#5E6A78', rx=1.5)
    b.r(56, 60, 26, 3.4, '#D3DAE2', rx=1.7); b.r(56, 60, 19, 3.4, '#43C46B', rx=1.7)
    b.r(56, 66, 26, 3.4, '#D3DAE2', rx=1.7); b.r(56, 66, 11, 3.4, '#F2A93B', rx=1.7)
    b.r(56, 72, 26, 3.4, '#D3DAE2', rx=1.7); b.r(56, 72, 23, 3.4, '#3D86D6', rx=1.7)
    b.hl("M9 9.6 L86 9.6", .8, .5)

@icon('ops_monitor', '运维监控', CAT)
def _(b):
    b.sh(48, 92, 38, 3)
    b.drop("M8 6 L88 6 L88 56 L8 56 Z", 2.5, 3, .16)
    b.r(8, 6, 80, 50, 'dkm', DS, rx=4)
    b.r(12, 10, 72, 42, '#0A1A14', '#0B1A2C', rx=1.5, sw=.6)
    b.ln("M12 20 L84 20 M12 30 L84 30 M12 40 L84 40 M24 10 L24 52 M40 10 L40 52 M56 10 L56 52 M72 10 L72 52", '#43C46B', .5, .22)
    b.ln("M14 32 L28 32 L32 26 L37 42 L42 16 L47 36 L51 32 L82 32", '#4DFF8C', 3, .25)
    b.ln("M14 32 L28 32 L32 26 L37 42 L42 16 L47 36 L51 32 L82 32", '#7FFFAF', 1.5, .98)
    b.c(82, 32, 2.2, '#E8FFF0')
    b.p("M14 12 L24 12 L16 50 L14 50 Z", '#FFFFFF', op=.08)
    b.r(44, 56, 8, 6, 'metal3', MS, sw=.6)
    for i in range(2):
        y = 62 + i * 11
        b.r(20, y, 56, 9, 'metal', MS, rx=1.2, sw=.8)
        b.ln(f"M24 {y+2.4} L24 {y+6.6} M27 {y+2.4} L27 {y+6.6} M30 {y+2.4} L30 {y+6.6} M33 {y+2.4} L33 {y+6.6}", '#5E6A78', 1.4)
        b.r(42, y + 3.4, 14, 2.2, '#3A4048', rx=.6)
        leds(b, [(62, y + 4.5, GREEN), (67, y + 4.5, GREEN if i else AMBER), (72, y + 4.5, GREEN)])
    b.hl("M10 7.6 L86 7.6", .8, .5)

@icon('scheduler', '任务调度', CAT)
def _(b):
    b.drop("M6 10 L76 10 L76 72 L6 72 Z", 2.5, 3, .16)
    b.r(6, 10, 70, 62, 'white', MS, rx=4)
    b.p("M10 10 L72 10 Q76 10 76 14 L76 22 L6 22 L6 14 Q6 10 10 10 Z", 'glass', BL, 1)
    b.ln("M12 16 L30 16", '#FFFFFF', 2, .85)
    b.ln("M24 24 L24 70 M36 24 L36 70 M48 24 L48 70 M60 24 L60 70", '#C9D1DA', .7)
    bars = [(10, 20, 'glass'), (20, 24, 'land'), (32, 22, 'orange'), (44, 22, 'glass'), (52, 18, 'red')]
    for i, (x, w, c) in enumerate(bars):
        y = 26 + i * 8.6
        b.r(x, y, w, 5.6, c, '#5E6A78', rx=1.6, sw=.7)
        b.ln(f"M{x+2} {y+1.5} L{x+w-3} {y+1.5}", '#FFFFFF', .8, .6)
    b.ln("M30 31.6 L30 37 L32 37 M54 40.4 L54 46 L44 46", '#5E6A78', .8, .7)
    b.drop("M72 68 A19 19 0 1 0 72.01 68 Z", 2, 3, .2)
    clock(b, 70, 66, 19)
    b.hl("M54 56 A17 17 0 0 1 68 49.4", 1.1, .8)

@icon('spatiotemporal', '时空基准', CAT)
def _(b):
    b.sh(44, 91, 30, 2.8)
    b.c(44, 50, 31, 'node', '#1F4F8C', 1.4)
    b.p("M26 36 Q32 28 42 30 Q44 36 38 40 Q34 46 28 44 Z", 'land', '#3E4C29', .6, .9)
    b.p("M46 46 Q56 42 62 48 Q64 58 56 66 Q50 64 48 56 Z", 'land', '#3E4C29', .6, .9)
    b.p("M38 62 Q42 60 44 66 Q40 72 36 68 Z", 'land', '#3E4C29', .6, .9)
    b.e(44, 50, 31, 8, 'none', '#FFFFFF', .7, .5)
    b.e(44, 50, 12, 31, 'none', '#FFFFFF', .7, .5)
    b.ln("M13 50 L75 50 M44 19 L44 81", '#FFFFFF', .7, .45)
    b.p("M24 30 Q36 20 52 22 Q38 26 30 36 Z", '#FFFFFF', op=.35)
    b.g('rotate(-28 44 50)')
    b.ln("M4 50 A40 12 0 0 1 84 50", '#5E6A78', 1.2, .9, extra="stroke-dasharray='3 2'")
    b.ln("M4 50 A40 12 0 0 0 84 50", '#5E6A78', 1.2, .5, extra="stroke-dasharray='3 2'")
    b.g('translate(80 48)')
    b.r(-3, -2.4, 6, 4.8, 'gold', '#8A6A20', sw=.7); b.r(-11, -1.6, 7, 3.2, 'solar', '#18365C', sw=.5); b.r(5, -1.6, 7, 3.2, 'solar', '#18365C', sw=.5)
    b.eg(); b.eg()
    b.drop("M78 80 A16 16 0 1 0 78.01 80 Z", 2, 3, .2)
    clock(b, 76, 76, 16)
    b.ln("M8 56 L8 78 L26 78", '#F2A93B', 2); b.p("M5 59 L8 52 L11 59 Z", '#F2A93B'); b.p("M24 75 L31 78 L24 81 Z", '#F2A93B')
    b.ln("M8 78 L16 70", '#43C46B', 2); b.p("M14 67 L20 66 L19 72 Z", '#43C46B')

@icon('model_repo', '模型仓库', CAT)
def _(b):
    b.sh(48, 93, 42, 2.6)
    b.r(8, 8, 80, 80, 'dkm2', DS, rx=2)
    b.r(11, 11, 74, 74, '#1B2A3C', None, rx=1)
    b.r(6, 47, 84, 5, 'metal', MS, sw=.9); b.r(6, 85, 84, 5, 'metal', MS, sw=.9)
    b.r(6, 6, 84, 4, 'metal', MS, sw=.9)
    b.raw("<g stroke='#25578F' stroke-width='.6'>")
    def stack(x, base, n, c, tag):
        t, f, sd = c
        for i in range(n):
            y = base - 5 - i * 7.5
            b.p(f"M{x+18} {y} L{x+25} {y-4} L{x+25} {y+1} L{x+18} {y+5} Z", sd)
            b.p(f"M{x} {y} L{x+7} {y-4} L{x+25} {y-4} L{x+18} {y} Z", t)
            b.r(x, y, 18, 5, f)
        top = base - 5 - (n - 1) * 7.5
        b.raw(f"<circle cx='{x+21.5}' cy='{top+1.5}' r='1.2' fill='{tag}' stroke='none'/>")
    BLU = ('#CFE9FF', '#78B6EE', '#3D86D6'); DBL = ('#8FC6F5', '#4C8FD6', '#24599A'); ORA = ('#F6D08A', '#F0B060', '#B8691F')
    stack(14, 47, 3, BLU, GREEN)
    stack(40, 47, 4, DBL, GREEN)
    stack(64, 47, 2, BLU, AMBER)
    stack(14, 85, 2, ORA, GREEN)
    stack(40, 85, 3, BLU, AMBER)
    b.raw("</g>")
    box(b, 66, 70, 14, 14, 8, 5, 'land', 'landdk', 'landdk', LS, sw=.8)
    b.hl("M8 7.4 L86 7.4", .8, .7)

if __name__ == '__main__':
    import re as _re, os, glob
    HERE = os.path.dirname(os.path.abspath(__file__))
    KEYS = [k for k, n, c, fn in ICONS]
    assert len(KEYS) == len(set(KEYS)) == 24
    old = set()
    for f in glob.glob(os.path.join(HERE, 'icons*.js')):
        if os.path.basename(f) == 'icons_j.js': continue
        old |= set(_re.findall(r"key: '([^']+)'", open(f, encoding='utf-8').read()))
    assert not (old & set(KEYS)), old & set(KEYS)
    SZ = []
    lines = ['ICON_LIB.push(...[']
    for k, n, c, fn in ICONS:
        b = B(k); fn(b)
        s = b.svg()
        s = _re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
        s = _re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
        assert '"' not in s
        SZ.append((len(s), k))
        lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
    lines.append(']);')
    open(os.path.join(HERE, 'icons_j.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), 'largest', sorted(SZ)[-8:])
