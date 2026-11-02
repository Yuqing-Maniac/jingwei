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

# =====================================================================
#  icons_gen_b.py — extension set B (人员 / 感知通信 / 指控信息)
#  Helpers above are copied verbatim from icons_gen.py (that module
#  writes icons.js at import time, so it is not imported here).
# =====================================================================
import re

GR.update({
    'olive': GR['land'], 'olivedk': GR['landdk'],
    'navyB': L(V, (0, '#4A6688'), (.5, '#26405F'), (1, '#132238')),
    'af': L(V, (0, '#A9BACB'), (.5, '#7489A0'), (1, '#4A5B6E')),
    'shirt': L(V, (0, '#F2F7FC'), (.5, '#C4D8EC'), (1, '#86A3C2')),
    'suit': L(V, (0, '#6E7783'), (.5, '#454C57'), (1, '#252A31')),
    'tac': L(V, (0, '#D9C7A4'), (.5, '#AE9670'), (1, '#76623F')),
    'yellow': L(V, (0, '#FFE88F'), (.5, '#F5C23A'), (1, '#BE860F')),
    'overall': L(V, (0, '#6C97CC'), (.5, '#33639C'), (1, '#1B3A63')),
    'hair': L(V, (0, '#5E524A'), (1, '#2A2420')),
    'hairG': L(V, (0, '#ECEEF0'), (1, '#A2A8AE')),
    'paper': L(V, (0, '#FFFFFF'), (1, '#DDE4EB')),
    'flame': L(('0', '1', '0', '0'), (0, '#D23C26'), (.5, '#F28C28'), (1, '#FFD75E')),
    'brick': L(V, (0, '#D88466'), (1, '#9B4632')),
    'brickT': L(V, (0, '#E8B8A2'), (1, '#C27A60')),
    'terrain': L(D, (0, '#C9DC9A'), (.5, '#97B263'), (1, '#6A8840')),
    'soil': L(V, (0, '#B8936A'), (1, '#6E5236')),
    'pcb': L(V, (0, '#4C9A68'), (1, '#1E4A30')),
    'teal': L(V, (0, '#A6E8D8'), (.5, '#4DB89F'), (1, '#24806C')),
    'amber': L(V, (0, '#FBDB9A'), (.5, '#F0AE4A'), (1, '#B8691F')),
    'green': L(V, (0, '#A6E6B6'), (.5, '#4DBE70'), (1, '#24803F')),
    'nodeG': ('r', ('0.35', '0.3', '0.75'), ((0, '#E2FBE8'), (.5, '#55C878'), (1, '#1F7A3E'))),
    'nodeA': ('r', ('0.35', '0.3', '0.75'), ((0, '#FFF2D6'), (.5, '#F2A93B'), (1, '#A8611A'))),
    'nodeP': ('r', ('0.35', '0.3', '0.75'), ((0, '#F1E6FF'), (.5, '#9A79D8'), (1, '#4E3590'))),
    'thermal': ('r', ('0.45', '0.45', '0.6'), ((0, '#FFF6C0'), (.3, '#FFC13B'), (.6, '#E2574C'), (1, '#4B2C7E'))),
    'beamR': ('l', ('1', '0', '0', '1'), ((0, '#8FD0FF', .6), (1, '#8FD0FF', 0))),
})

_f0 = B.f
def _fchk(s, v):
    if v not in GR and not (v.startswith('#') or v == 'none'):
        raise ValueError('unknown paint ' + v)
    return _f0(s, v)
B.f = _fchk

SKIN_ST = '#7A5D3E'
OS = '#3E4C29'         # olive outline
NS = '#0F1E33'         # navy outline

def star(cx, cy, r):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * .42
        pts.append(f"{cx + rr*math.cos(a):.1f} {cy + rr*math.sin(a):.1f}")
    return 'M' + ' L'.join(pts) + ' Z'

def arrowhead(b, x, y, ang, col, s=3.2):
    a = math.radians(ang)
    p1 = (x - s*math.cos(a) + s*.6*math.sin(a), y - s*math.sin(a) - s*.6*math.cos(a))
    p2 = (x - s*math.cos(a) - s*.6*math.sin(a), y - s*math.sin(a) + s*.6*math.cos(a))
    b.p(f"M{x:.1f} {y:.1f} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} Z", col)

def box3d(b, x, y, w, h, dx, dy, front='metal2', top='metal', side='metal3', st=MS, rx=1.5):
    """front rect at (x,y,w,h); top/side receding up-right by (dx,dy)."""
    b.p(f"M{x} {y} L{x+dx} {y-dy} L{x+w+dx} {y-dy} L{x+w} {y} Z", top, st)
    b.p(f"M{x+w} {y} L{x+w+dx} {y-dy} L{x+w+dx} {y+h-dy} L{x+w} {y+h} Z", side, st)
    b.r(x, y, w, h, front, st, rx=rx)
    b.hl(f"M{x+1.5} {y-.6} L{x+dx+.6} {y-dy+1.3} L{x+w+dx-1} {y-dy+1.3}", .9, .8)

# ---------------- people ----------------
def torso(b, fill, st, bottom=92):
    b.p(f"M12 {bottom} L12 92 C12 74 26 64 48 64 C70 64 84 74 84 92 L84 {bottom} Z", fill, st)

def head(b, ears=True):
    b.r(41, 52, 14, 14, 'skin')
    b.p("M41 58 C44 61 52 61 55 58 L55 63 L41 63 Z", '#7A5D3E', op=.25)
    if ears:
        b.e(32, 40, 2.8, 4.4, 'skin', SKIN_ST, .8); b.e(64, 40, 2.8, 4.4, 'skin', SKIN_ST, .8)
    b.e(48, 38, 16, 19, 'skin', SKIN_ST, 1)
    b.p("M58 26 C63 32 64 42 60 50 C57 54 53 56.5 48 57 C55 52 58 44 58 26 Z", '#7A5D3E', op=.16)

def hair(b, fill='hair', st='#211D1A'):
    b.p("M32 36 C31 22 38 16 48 16 C58 16 65 22 64 36 C62 30 60 27 56 25.5 C50 28 40 28 33.5 30 Z", fill, st, .8)
    b.hl("M37 23 C40 19.4 44 18 49 17.8", 1, .45)

def collar_tie(b, shirt='#E7EBDA', tie='#3E4C29', lapel='olivedk', st=OS):
    b.p("M38 64 L48 80 L58 64 Z", shirt, '#9AA38A', .6)
    b.p("M46 67 L50 67 L51.4 79 L48 83 L44.6 79 Z", tie)
    b.p("M45.6 64 L50.4 64 L50 67.4 L46 67.4 Z", tie)
    b.p("M37 64.5 L48 84 L43 71 L33 68.5 Z", lapel, st, .7)
    b.p("M59 64.5 L48 84 L53 71 L63 68.5 Z", lapel, st, .7)

def boards(b):
    b.p("M17 74 L30 68 L32.4 71.6 L19.4 77.6 Z", 'gold', '#7A5C18', .6)
    b.p("M79 74 L66 68 L63.6 71.6 L76.6 77.6 Z", 'gold', '#7A5C18', .6)
    b.c(24, 72.6, .9, '#FFF6D0'); b.c(72, 72.6, .9, '#FFF6D0')

def fig(b, x, y, s, fn):
    b.g(f"translate({x} {y}) scale({s})"); fn(b); b.eg()

def arm(b, d, col, dark, w=7.2):
    b.ln(d, dark, w); b.ln(d, col, w - 2.6)

def hand(b, x, y, r=3.4):
    b.c(x, y, r, 'skin', SKIN_ST, .7)

# ================= 人员 =================
@icon('commander', '指挥员', '人员')
def _(b):
    torso(b, 'olive', OS)
    collar_tie(b)
    boards(b)
    for i, c_ in enumerate(('#D9473A', '#F2C84B', '#3D86D6', '#43C46B', '#D9473A', '#F2C84B')):
        b.r(56.5 + (i % 3) * 4.4, 77 + (i // 3) * 3.2, 4, 2.6, c_, '#2A2E33', sw=.4)
    b.c(36, 82, 2.4, 'gold', '#7A5C18', .5)
    head(b, ears=True)
    # peaked cap
    b.p("M22 22 C22 12 35 6 48 6 C61 6 74 12 74 22 C68 24.5 58 26 48 26 C38 26 28 24.5 22 22 Z", 'olive', OS)
    b.p("M30 23 C38 25.4 58 25.4 66 23 L65.4 30 C58 32 38 32 30.6 30 Z", 'olivedk', OS, .8)
    b.ln("M31 27 C40 29 56 29 65 27", '#D8B45A', 1.2)
    b.p("M30.4 29.6 C38 32 58 32 65.6 29.6 C64.6 34.6 58 37 48 37 C38 37 31.4 34.6 30.4 29.6 Z", '#1E2328', '#0E1013', .7)
    b.hl("M35 32.8 C42 34.4 54 34.4 61 32.8", .9, .5)
    b.c(48, 17, 4.6, 'gold', '#7A5C18', .7)
    b.p(star(48, 17.3, 3), '#D9473A')
    b.hl("M26 15 C30 10 38 7.6 46 7.4", 1.2, .8)
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)

@icon('staff_officer', '参谋', '人员')
def _(b):
    torso(b, 'olive', OS)
    collar_tie(b)
    boards(b)
    head(b); hair(b)
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)
    # folder held at chest
    b.g('rotate(-10 60 78)')
    b.r(44, 62, 32, 30, '#FFFFFF', '#97A3B1', rx=1, sw=.8)
    for i in range(4): b.ln(f"M48 {68 + i*4.4} L{70 - (i % 2)*6} {68 + i*4.4}", '#97A3B1', 1)
    b.p("M42 66 L74 66 L76 94 L42 94 Z", 'navyB', NS, 1)
    b.r(52, 74, 16, 10, '#FFFFFF', op=.18, rx=1)
    b.p(star(60, 79, 3.2), 'gold')
    b.hl("M43.6 67.4 L73 67.4", .9, .55)
    b.eg()
    hand(b, 44, 86)
    hand(b, 75, 77)

@icon('pilot', '飞行员', '人员')
def _(b):
    torso(b, 'af', '#3A4A5C')
    b.p("M40 64 L48 72 L56 64 Z", '#5D6E82')
    b.ln("M48 72 L48 92", '#3A4A5C', 1.2)
    b.ln("M26 70 L38 92 M70 70 L58 92", '#2E3640', 3.4)
    b.ln("M26 70 L38 92 M70 70 L58 92", '#5D6670', 1.2)
    b.r(62, 76, 9, 6, '#D9473A', '#7A2219', sw=.5)
    b.p(star(64.6, 78.6, 1.6), '#F2C84B')
    b.r(25, 78, 9, 5, '#2E3640', rx=1)
    head(b, ears=False)
    # helmet
    b.p("M29 46 C26 22 35 10 48 10 C61 10 70 22 67 46 C66 52 63 55 60 56 L61 38 L35 38 L36 56 C33 55 30 52 29 46 Z", 'white', '#7C8A9B', 1.1)
    b.ln("M48 10.5 L48 22", '#3D86D6', 3.2, cap='butt')
    b.p("M33 26 C38 22 58 22 63 26 L62.4 40 C57 43.6 39 43.6 33.6 40 Z", 'canopy', '#0F2339', 1)
    b.p("M35 27 C40 24.4 46 24 52 24 L38 41 C36 40 35 38 34.6 36 Z", '#FFFFFF', op=.18)
    glint(b, 40, 29, 3, 1.2)
    b.p("M40 46 C40 43 56 43 56 46 L54.4 53 C52.4 56 43.6 56 41.6 53 Z", 'dkm', '#15191E', .8)
    b.r(45, 49, 6, 3, '#6A7480', rx=1.2)
    b.ln("M48 55 C48 62 56 64 60 72", '#2E3238', 3)
    b.ln("M48 55 C48 62 56 64 60 72", '#6A7480', 1, extra="stroke-dasharray='1.4 1.4'")
    b.hl("M32 24 C35 15 41 12 47 11.6", 1.3, .9)
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)

@icon('drone_pilot', '无人机飞手', '人员')
def _(b):
    torso(b, '#2E3238', '#15181C')
    b.p("M22 70 C28 66 36 64.5 40 64.5 L44 92 L20 92 Z", 'tac', '#5A4A30', .9)
    b.p("M74 70 C68 66 60 64.5 56 64.5 L52 92 L76 92 Z", 'tac', '#5A4A30', .9)
    head(b); hair(b)
    # baseball cap
    b.p("M31 30 C30 17 38 11 48 11 C58 11 66 17 65 30 C60 28 54 27.4 48 27.4 C42 27.4 36 28 31 30 Z", 'tac', '#5A4A30', 1)
    b.ln("M48 11.4 L48 27", '#8A7550', .8)
    b.p("M30 30 C36 26.4 60 26.4 66 30 C63 34.6 33 34.6 30 30 Z", '#4A3E2A', '#2A2216', .7)
    b.c(48, 12, 1.4, '#8A7550')
    b.hl("M35 19 C38 14.6 43 12.6 47 12.4", 1, .7)
    # controller
    b.ln("M30 66 L22 46", '#22272D', 2.2); b.ln("M66 66 L74 46", '#22272D', 2.2)
    b.c(22, 46, 1.6, '#22272D'); b.c(74, 46, 1.6, '#22272D')
    b.p("M22 72 C22 67 26 65 31 65 L65 65 C70 65 74 67 74 72 L74 82 C74 87 70 89 65 89 L31 89 C26 89 22 87 22 82 Z", 'dkm', '#15191E', 1)
    for x in (34, 62):
        b.c(x, 78, 6, 'dkm2', '#101317', .8)
        b.c(x, 78, 2.8, 'hub', '#0E1013', .6)
    b.r(42, 68, 12, 8, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.ln("M44 73.5 L47 71 L49 72.6 L52 70", '#7FE0A0', .8)
    leds(b, [(44, 82, GREEN), (52, 82, AMBER)])
    b.hl("M27 66.4 L69 66.4", .9, .55)
    arm(b, "M12 92 L20 82", '#2E3238', '#15181C'); hand(b, 22, 80, 3.8)
    arm(b, "M84 92 L76 82", '#2E3238', '#15181C'); hand(b, 74, 80, 3.8)

@icon('engineer', '工程师', '人员')
def _(b):
    torso(b, 'shirt', '#5F7C9C')
    b.p("M38 64 L48 74 L44 78 L35 67 Z", '#FFFFFF', '#8EA5BF', .7)
    b.p("M58 64 L48 74 L52 78 L61 67 Z", '#FFFFFF', '#8EA5BF', .7)
    head(b); hair(b)
    # hard hat
    b.p("M29 31 C29 17 37 9 48 9 C59 9 67 17 67 31 Z", 'yellow', '#9A6E0E', 1)
    b.p("M44.5 9.6 C46 9.2 50 9.2 51.5 9.6 L52.4 31 L43.6 31 Z", '#FFF3C4', op=.55)
    b.r(24, 29, 48, 5, 'yellow', '#9A6E0E', rx=2.5, sw=1)
    b.hl("M33 22 C34 15 38 11.4 43 10.4", 1.2, .85)
    # laptop
    b.p("M27 62 L69 62 L71 84 L25 84 Z", 'metal2', MS, 1)
    b.p("M30 64.6 L66 64.6 L67.6 81.6 L28.4 81.6 Z", 'scr', '#0B1A2C', .6)
    b.ln("M32 69 L44 69 M32 72.4 L52 72.4 M35 75.8 L48 75.8 M32 79 L42 79", '#7FE0A0', 1, .85)
    b.ln("M56 68.6 L63 68.6", '#F2A93B', 1, .8)
    b.p("M31 65.4 L42 65.4 L34 80.8 L30 80.8 Z", '#FFFFFF', op=.12)
    b.p("M23 84 L73 84 L80 92 L16 92 Z", 'metal', MS, 1)
    b.ln("M27 87 L69 87 M25.4 89.4 L70.6 89.4", '#97A3B1', .8, extra="stroke-dasharray='2.4 1'")

@icon('maintainer', '维修保障人员', '人员')
def _(b):
    torso(b, 'overall', '#132A48')
    b.p("M30 92 L32 74 L64 74 L66 92 Z", '#244D80', op=.6)
    b.ln("M32 74 L28 66 M64 74 L68 66", '#132A48', 2.6)
    b.ln("M15 82 C30 79 66 79 81 82", '#F2A93B', 3.2, cap='butt')
    b.ln("M15 82 C30 79 66 79 81 82", '#FFF2C4', .9, .9, cap='butt')
    b.c(33, 75, 1.6, 'metal', MS, .5); b.c(63, 75, 1.6, 'metal', MS, .5)
    b.r(38, 84, 9, 7, '#1B3A63', '#132A48', sw=.6)
    head(b); hair(b)
    # work cap
    b.p("M31 30 C30 17 38 11 48 11 C58 11 66 17 65 30 C60 28 54 27.4 48 27.4 C42 27.4 36 28 31 30 Z", 'overall', '#132A48', 1)
    b.p("M30 30 C36 26.4 60 26.4 66 30 C63 34.6 33 34.6 30 30 Z", '#1B3A63', '#0E1F36', .7)
    b.hl("M35 19 C38 14.6 43 12.6 47 12.4", 1, .7)
    # wrench
    b.g('rotate(28 70 74)')
    b.r(66.5, 58, 7, 32, 'cylM', MS, rx=3.5)
    b.p("M66.5 49 L66.5 55 L72.5 55 L72.5 49 A8.5 8.5 0 1 1 66.5 49 Z", 'metal', MS, 1)
    b.r(67.5, 84, 5, 4, 'metal3', rx=1.5)
    b.hl("M68 60 L68 82", 1, .8)
    b.eg()
    hand(b, 71, 76, 4)
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .45)

@icon('analyst', '情报分析员', '人员')
def _(b):
    b.sh(60, 90, 34, 3)
    # monitor
    b.r(65, 58, 8, 12, 'metal3', MS, sw=.8)
    b.p("M58 74 L80 74 L84 70 L62 70 Z", 'metal2', MS, .8)
    b.p("M48 12 L92 12 L92 58 L48 58 Z", 'dkm2', DS, 1)
    b.r(51, 15, 38, 40, 'scr', '#0B1A2C', sw=.6)
    b.p("M53 18 L66 18 L66 30 L53 30 Z", '#3D86D6', op=.45)
    b.ln("M54 26 C57 22 60 27 64 21", '#7FE0A0', 1)
    b.c(60, 24, 1.3, REDL)
    for i, h in enumerate((8, 12, 6, 14)):
        b.r(70 + i * 4.4, 30 - h, 3, h, '#F2A93B' if i == 3 else '#8FD0FF', op=.9)
    b.ln("M54 36 L86 36 M54 40 L80 40 M54 44 L84 44 M54 48 L74 48", '#9CC2EA', 1, .6)
    b.p("M52 16 L62 16 L54 53 L52 53 Z", '#FFFFFF', op=.1)
    leds(b, [(88, 56.6, GREEN)])
    # desk
    b.p("M30 80 L94 80 L90 74 L36 74 Z", 'metal', MS, 1)
    b.r(30, 80, 64, 5, 'metal3', MS, sw=.8)
    b.p("M48 77.6 L66 77.6 L65 75.6 L49.6 75.6 Z", '#3A4048')
    # person (side view, facing right)
    b.p("M4 92 C4 76 10 66 24 63 C34 61 40 66 42 74 L44 92 Z", 'uniform', '#253A50')
    b.r(20, 52, 12, 13, 'skin')
    b.e(27, 40, 14, 17, 'skin', SKIN_ST, 1)
    b.p("M40 37 L44 44 L39.6 45.4 Z", 'skin', SKIN_ST, .8)
    b.p("M13 42 C10 26 18 21 27 21 C36 21 41 26 40 33 C34 31 30 32 27 34 C26 38 22 41 21 46 C18 46 15 45 13 42 Z", 'hair', '#211D1A', .8)
    b.e(23.5, 42, 2.6, 4, 'skin', SKIN_ST, .8)
    b.ln("M22 70 L34 77 L48 76", '#253A50', 7.2); b.ln("M22 70 L34 77 L48 76", '#56708F', 4.6)
    hand(b, 50, 75.6, 3)
    b.hl("M8 82 C10 74 14 69 20 66.4", 1.2, .5)

def _suit(tie, hairc='hair'):
    def f(b):
        torso(b, 'suit', '#15191E', 128)
        b.p("M38 64 L48 80 L58 64 Z", '#F4F6F8', '#A3AEBB', .6)
        b.p("M46 67 L50 67 L51.4 79 L48 83 L44.6 79 Z", tie)
        b.p("M45.6 64 L50.4 64 L50 67.4 L46 67.4 Z", tie)
        b.p("M37 64.5 L48 86 L43 72 L33 69 Z", '#2E343C', '#15191E', .7)
        b.p("M59 64.5 L48 86 L53 72 L63 69 Z", '#2E343C', '#15191E', .7)
        head(b); hair(b, hairc, '#5C6268' if hairc == 'hairG' else '#211D1A')
        b.hl("M20 80 C24 72 32 68 38 67", 1.4, .4)
    return f

@icon('expert_group', '专家组', '人员')
def _(b):
    fig(b, -6, 6, .64, _suit('#3D86D6'))
    fig(b, 40.5, 6, .64, _suit('#43A06B'))
    fig(b, 7.7, 14.7, .84, _suit('#C2403A', 'hairG'))
    b.r(54, 79, 6, 1.6, 'gold', op=.9)

def _trooper(vest=False):
    def f(b):
        torso(b, 'olive', OS, 128)
        b.p("M38 64 L48 74 L58 64 Z", 'olivedk', OS, .7)
        if vest:
            b.r(30, 74, 36, 30, 'olivedk', OS, rx=3, sw=.9)
            b.ln("M42 74 L42 104 M54 74 L54 104", '#2E3A1C', 1, .7)
        head(b, ears=False)
        b.ln("M33 40 C34 52 40 56 48 57 C56 56 62 52 63 40", '#2E3238', 1.6)
        b.p("M27 38 C25 20 35 9 48 9 C61 9 71 20 69 38 C64 32.6 57 30.4 48 30.4 C39 30.4 32 32.6 27 38 Z", 'olive', OS, 1.1)
        b.p("M25.6 38.4 C31 31 38 29 48 29 C58 29 65 31 70.4 38.4 C65 34.6 57 33 48 33 C39 33 31 34.6 25.6 38.4 Z", 'olivedk', OS, .8)
        b.ln("M36 22 L40 17 M52 14 L57 18 M60 26 L64 23 M31 30 L35 26", '#4E5F35', 1.6, .7)
        b.hl("M31 24 C34 15 40 11.4 47 11", 1.3, .8)
    return f

@icon('squad', '作战小组', '人员')
def _(b):
    fig(b, -6, 6, .64, _trooper())
    fig(b, 40.5, 6, .64, _trooper())
    fig(b, 7.7, 14.7, .84, _trooper(True))
    b.ln("M24 90 L74 62", '#15181C', 4.4); b.ln("M24 90 L74 62", '#3A3F46', 2)
    b.p("M46 77 L52 73.6 L55 79 L50 82 Z", '#2A2E33')
    hand(b, 40, 81, 3.2); hand(b, 58, 71, 3.2)

@icon('sailor', '水兵', '人员')
def _(b):
    # ribbons behind
    b.p("M60 26 L66 50 L63 52 L64.6 46 L58 28 Z", '#1A2638')
    b.p("M63 26 L71 48 L68 50.4 L68.6 44.4 L60.6 27 Z", '#22324A')
    torso(b, 'white', '#7C8A9B')
    b.p("M15 77 C21 69.6 30 65.6 38 64.4 L48 84 L58 64.4 C66 65.6 75 69.6 81 77 L72 80.4 L48 92 L24 80.4 Z", 'navyB', NS, 1)
    b.ln("M22.4 77.6 L48 89.4 L73.6 77.6", '#FFFFFF', 1, .9)
    b.ln("M19.6 75.8 L48 86.6 L76.4 75.8", '#FFFFFF', .8, .7)
    b.p("M38 64.4 L48 84 L58 64.4 Z", '#FFFFFF', '#A3AEBB', .6)
    for y in (67.4, 71.4, 75.4, 79.4):
        w = (84 - y) / 20 * 10
        b.ln(f"M{48 - w:.1f} {y} L{48 + w:.1f} {y}", '#26405F', 1.8, cap='butt')
    b.p("M45 82 L51 82 L49.4 87 L46.6 87 Z", '#15191E')
    head(b); hair(b)
    # sailor cap
    b.p("M27 22 C27 11 37 6 48 6 C59 6 69 11 69 22 C62 25 34 25 27 22 Z", 'white', '#7C8A9B', 1)
    b.p("M30 21.6 C38 24 58 24 66 21.6 L65.6 29 C58 31.4 38 31.4 30.4 29 Z", '#1A2638', '#0B111A', .8)
    b.ln("M32 25.6 C40 27.4 56 27.4 64 25.6", '#D8B45A', .9, .8)
    b.c(48, 26.6, 1.8, 'gold')
    b.hl("M31 15 C35 10 41 8 47 7.8", 1.2, .9)

@icon('driver', '驾驶员', '人员')
def _(b):
    torso(b, 'olive', OS)
    b.p("M38 64 L48 74 L58 64 Z", 'olivedk', OS, .7)
    head(b); hair(b)
    b.p("M31 29 C30 17 38 11 48 11 C58 11 66 17 65 29 C60 27 54 26.4 48 26.4 C42 26.4 36 27 31 29 Z", 'olive', OS, 1)
    b.p("M31 28.6 C38 25.6 58 25.6 65 28.6 L63.4 33 C58 30.6 38 30.6 32.6 33 Z", 'olivedk', OS, .8)
    b.p(star(48, 20, 3), '#D9473A')
    b.hl("M35 19 C38 14.6 43 12.6 47 12.4", 1, .7)
    # steering wheel
    b.e(48, 82, 31, 11, 'none', '#15181C', 7.4)
    b.e(48, 82, 31, 11, 'none', '#3A3F46', 4.6)
    b.ln("M19 80 C24 73.4 36 71 48 71 C60 71 72 73.4 77 80", '#7D8590', 1.1, .9)
    b.ln("M20 83 L38 84 M76 83 L58 84 M48 87 L48 93", '#2A2E33', 4.2)
    b.e(48, 85, 11, 5, 'dkm', '#15191E', .8)
    b.e(48, 84, 4, 1.8, '#6A7480')
    arm(b, "M8 92 L18 80", 'olive', OS); hand(b, 19.6, 78.6, 4)
    arm(b, "M88 92 L78 80", 'olive', OS); hand(b, 76.4, 78.6, 4)

@icon('medic', '卫生员', '人员')
def _(b):
    torso(b, 'olive', OS)
    b.p("M38 64 L48 74 L58 64 Z", 'olivedk', OS, .7)
    b.ln("M24 70 L60 92", '#6E5236', 3.6, cap='butt')
    b.p("M71 69.6 L82.6 75 L84 86 L72 82 Z", 'white', '#8F9BA9', .7)
    b.p("M75.2 74.6 L78.4 76 L78.6 78 L80.6 78.8 L81 82 L78.8 81.4 L79 83.6 L75.8 82.4 L75.6 80.2 L73.4 79.4 L73.2 76.4 L75.4 77 Z", '#D9312A')
    head(b); hair(b)
    b.p("M31 29 C30 17 38 11 48 11 C58 11 66 17 65 29 C60 27 54 26.4 48 26.4 C42 26.4 36 27 31 29 Z", 'white', '#7C8A9B', 1)
    b.p("M31 28.6 C38 25.6 58 25.6 65 28.6 L63.4 33 C58 30.6 38 30.6 32.6 33 Z", 'whitedk', '#7C8A9B', .8)
    b.c(48, 19.4, 6, '#FFFFFF', '#C9D1DA', .6)
    b.p("M46 14.6 L50 14.6 L50 17.4 L52.8 17.4 L52.8 21.4 L50 21.4 L50 24.2 L46 24.2 L46 21.4 L43.2 21.4 L43.2 17.4 L46 17.4 Z", '#D9312A')
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)

@icon('trainee', '学员', '人员')
def _(b):
    torso(b, 'navyB', NS)
    b.p("M38 64 L48 80 L58 64 Z", '#F4F6F8', '#A3AEBB', .6)
    b.p("M46 67 L50 67 L51.4 79 L48 83 L44.6 79 Z", '#26405F')
    b.p("M37 64.5 L48 84 L43 71 L33 68.5 Z", '#1B2E48', NS, .7)
    b.p("M59 64.5 L48 84 L53 71 L63 68.5 Z", '#1B2E48', NS, .7)
    head(b); hair(b)
    # mortarboard
    b.p("M33 30 C33 22 63 22 63 30 C58 28 38 28 33 30 Z", '#22272D', '#0E1013', .8)
    b.p("M48 6 L84 17 L48 28 L12 17 Z", '#2E343C', '#0E1013', 1)
    b.p("M48 7.6 L78 17 L48 12 L18 17 Z", '#FFFFFF', op=.12)
    b.c(48, 17, 1.8, 'gold')
    b.ln("M48 17 L72 22 L72 34", '#E2B54A', 1.4)
    b.p("M70 33 L74 33 L74.6 39 L69.4 39 Z", 'gold')
    # book
    b.p("M24 74 C32 71 42 72 48 76 L48 92 C42 88 32 87.4 24 90 Z", 'paper', '#8F9BA9', .9)
    b.p("M72 74 C64 71 54 72 48 76 L48 92 C54 88 64 87.4 72 90 Z", 'paper', '#8F9BA9', .9)
    b.p("M48 76 L48 92 C46 90.6 45 90 44 89.6 L44 74.4 Z", '#000000', op=.08)
    for i in range(3):
        y = 78 + i * 3.6
        b.ln(f"M28 {y} C34 {y-1.6} 40 {y-1.2} 45 {y+1}", '#97A3B1', .8)
        b.ln(f"M68 {y} C62 {y-1.6} 56 {y-1.2} 51 {y+1}", '#97A3B1', .8)
    hand(b, 23, 84, 3.4); hand(b, 73, 84, 3.4)

def _user(shirt, st, full=True):
    def f(b):
        torso(b, shirt, st, 128)
        b.p("M40 64 C42 69 54 69 56 64 Z", '#FFFFFF', op=.5)
        if full:
            head(b); hair(b)
        else:
            b.r(41, 52, 14, 14, 'skin'); b.e(48, 38, 16, 19, 'skin', SKIN_ST, 1)
            b.p("M32 36 C31 22 38 16 48 16 C58 16 65 22 64 36 C62 30 60 27 56 25.5 C50 28 40 28 33.5 30 Z", 'hair')
        b.hl("M20 80 C24 72 32 68 38 67", 1.6, .55)
    return f

@icon('user_group', '用户群体', '人员')
def _(b):
    fig(b, 44, 2, .5, _user('metal2', MS, False))
    fig(b, 4, 2, .5, _user('metal2', MS, False))
    fig(b, -6, 12, .62, _user('teal', '#1A6656'))
    fig(b, 42.5, 12, .62, _user('amber', '#8A4E14'))
    fig(b, 7.7, 18.8, .8, _user('glass', '#25578F'))

# ================= 感知通信 (B) =================
@icon('ir_sensor', '红外探测器', '感知通信')
def _(b):
    b.sh(48, 87, 26, 3.4)
    b.ln("M48 64 L28 86 M48 64 L68 86 M48 64 L48 87", '#3A4048', 2.6)
    b.ln("M48 64 L29 85 M48 64 L48 86", '#9AA5B2', .8)
    b.r(42, 54, 12, 11, 'metal3', MS, rx=1.5)
    b.p("M38 56 L58 56 L56 51 L40 51 Z", 'metal2', MS, .8)
    b.p("M10 26 L20 18 L82 18 L72 26 Z", 'metal', MS)
    b.p("M72 26 L82 18 L82 44 L72 52 Z", 'metal3', MS)
    b.r(10, 26, 62, 26, 'metal2', MS, rx=2)
    b.p("M6 25 L74 25 L74 28.4 L6 28.4 Z", 'dkm', DS, .8)
    b.c(28, 39.6, 11, 'dkm2', DS, 1)
    b.c(28, 39.6, 8.4, 'lens', '#05101C', .8)
    b.c(28, 39.6, 8.4, 'none', '#E08A2E', 1.4, op=.85)
    b.c(28, 39.6, 3.6, 'none', '#B14A8E', .8, op=.7)
    glint(b, 25, 36, 2.4, 1.2)
    b.r(46, 31, 22, 16, 'dkm2', DS, rx=1.2, sw=.8)
    b.r(47.6, 32.6, 18.8, 12.8, 'thermal', rx=.6)
    b.e(55, 38.4, 3.6, 5, '#FFF6C0', op=.6)
    leds(b, [(16, 48, GREEN), (20, 48, AMBER)])
    b.ln("M24 14 Q20 10.5 24 7 Q28 3.5 24 0.5 M34 14 Q30 10.5 34 7 Q38 3.5 34 0.5 M44 14 Q40 10.5 44 7 Q48 3.5 44 0.5", '#E2574C', 1.3, .75)
    b.hl("M12 24.6 L20.4 19.3 L80.6 19.3", .9, .85)

@icon('acoustic', '声学探测阵列', '感知通信')
def _(b):
    b.sh(46, 88, 24, 3.2)
    b.ln("M44 66 L28 88 M44 66 L60 88 M44 66 L44 88", '#3A4048', 2.6)
    b.r(40, 60, 8, 8, 'metal3', MS, rx=1)
    b.c(44, 38, 31, 'dkm', DS, 1.2)
    b.c(44, 38, 28.4, 'metal', MS, .8)
    b.c(44, 38, 18, 'none', '#B5BFCA', .8)
    b.c(44, 38, 9, 'none', '#B5BFCA', .8)
    for k in range(5):
        for i in range(1, 5):
            r_ = 4 + 5.6 * i
            a = math.radians(k * 72 + i * 30 - 90)
            x, y = 44 + r_ * math.cos(a), 38 + r_ * math.sin(a)
            b.c(round(x, 1), round(y, 1), 2.1, 'dkm2', '#101317', .5)
            b.c(round(x - .6, 1), round(y - .7, 1), .6, '#9CC2EA')
    b.c(44, 38, 4, 'hub', '#1D2228', .8)
    b.hl("M20 26 C25 15 34 10 42 9.6", 1.3, .9)
    b.ln("M82 26 Q88 38 82 50 M88 20 Q96 38 88 56", '#3D86D6', 1.6, .85)

@icon('rf_detector', '无线电侦测设备', '感知通信')
def _(b):
    b.sh(46, 87, 40, 3.4)
    b.r(70, 28, 5, 56, 'cylM', MS)
    b.p("M64 86 L81 86 L78 82 L67 82 Z", 'metal3', MS, .8)
    b.ln("M72.5 4 L72.5 30", '#2A2E33', 2)
    for i in range(7):
        y = 6 + i * 3.6; hw = 3 + i * 2.1
        b.ln(f"M{72.5 - hw:.1f} {y:.1f} L{72.5 + hw:.1f} {y:.1f}", '#5E6A78', 1.5)
    b.ln("M72.5 4 L72.5 30", '#C9D1DA', .7)
    b.ln("M40 10 Q46 16 40 22 M32 6 Q42 16 32 26 M24 2 Q38 16 24 30", '#3D86D6', 1.6, .85)
    arrowhead(b, 52, 16, 0, '#3D86D6', 3.6)
    b.ln("M46 16 L50 16", '#3D86D6', 1.6)
    b.ln("M60 66 C64 66 66 72 70 72", '#2A2E33', 1.8)
    box3d(b, 8, 50, 52, 34, 8, 7, 'dkm', 'metal2', 'dkm2', DS, 2.5)
    b.r(13, 55, 32, 18, 'scr', '#0B1A2C', rx=1.2, sw=.6)
    b.ln("M15 70 L19 69.4 L21 60 L23 69 L27 68 L29 63.6 L31 68.4 L35 69 L37 58 L39 69.4 L43 70", '#7FE0A0', 1, .95)
    b.ln("M37 57 L37 71", '#F2A93B', .7, .7)
    b.p("M14 56 L26 56 L18 72 L14 72 Z", '#FFFFFF', op=.12)
    b.c(52, 60, 3.6, 'sphere', '#1E2328', .7); b.c(52, 70, 2.6, 'sphere', '#1E2328', .7)
    leds(b, [(16, 79, GREEN), (21, 79, GREEN), (26, 79, AMBER)])

@icon('laser_rangefinder', '激光测距仪', '感知通信')
def _(b):
    b.sh(40, 88, 26, 3.2)
    b.ln("M36 60 L22 87 M36 60 L50 87 M36 60 L36 88", '#3A4048', 2.6)
    b.r(31, 56, 10, 7, 'metal3', MS, rx=1)
    b.r(4, 36, 10, 12, 'dkm2', DS, rx=2.4, sw=1)
    b.p("M12 34 C12 29 16 27 21 27 L52 27 L60 31 L60 55 L21 55 C16 55 12 53 12 48 Z", 'olive', OS, 1.1)
    b.p("M14 33 C15 30 18 29 22 29 L51 29 L54 31 L18 31 Z", '#FFFFFF', op=.35)
    b.r(20, 40, 18, 9, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.ln("M23 44.5 L25 44.5 M27 44.5 L29 44.5 M31 44.5 L35 44.5", '#F2A93B', 1.8, cap='butt')
    b.r(26, 23, 10, 5, 'olivedk', OS, rx=1.5, sw=.8)
    b.e(60, 36.6, 4.4, 7, 'dkm2', DS, .8); b.e(60.4, 36.6, 3, 5.4, 'lens', '#05101C', .6)
    b.e(60, 49, 3.4, 5, 'dkm2', DS, .8); b.e(60.4, 49, 2.2, 3.6, 'lens', '#05101C', .6)
    glint(b, 59.6, 34.4, .9, 1.4)
    b.ln("M64 49 L84 49", REDL, 4.4, .25)
    b.ln("M64 49 L84 49", '#FF6A5A', 1.4)
    b.c(86, 49, 7, 'none', REDL, 1.4)
    b.c(86, 49, 2.6, 'none', REDL, 1.1)
    b.ln("M86 39.6 L86 44 M86 54 L86 58.4 M76.6 49 L81 49 M91 49 L95 49", REDL, 1.2)
    leds(b, [(16, 51, GREEN)])

@icon('antenna_array', '天线阵', '感知通信')
def _(b):
    b.sh(48, 88, 26, 3.2)
    b.p("M36 88 L60 88 L56 82 L40 82 Z", 'metal3', MS, .8)
    b.r(45, 40, 6, 44, 'cylM', MS)
    b.ln("M22 12 L22 66 M74 12 L74 66 M22 40 L74 40", '#4B5867', 3.6)
    b.ln("M22 12 L22 66 M74 12 L74 66 M22 40 L74 40", '#C9D1DA', 1.2)
    for cx, cy in ((22, 22), (74, 22), (22, 56), (74, 56)):
        b.ln(f"M{cx-15} {cy} L{cx+15} {cy}", '#2E3640', 2.2)
        el = [(cx - 13 + j * 5.2, 8 - j * .9) for j in range(6)]
        b.ln(' '.join(f"M{x:.1f} {cy-h:.1f} L{x:.1f} {cy+h:.1f}" for x, h in el), '#5E6A78', 1.5)
        b.ln(' '.join(f"M{x-.3:.1f} {cy-h+.6:.1f} L{x-.3:.1f} {cy:.1f}" for x, h in el), '#DCE2E8', .5)
        b.r(cx - 2.4, cy - 2.4, 4.8, 4.8, 'metal', MS, rx=1, sw=.7)
    b.ln("M86 30 Q91 37 86 44 M90 24 Q98 37 90 50", '#3D86D6', 1.5, .85)
    b.hl("M46.4 42 L46.4 82", .9, .8)

@icon('relay', '中继站', '感知通信')
def _(b):
    b.p("M2 90 C18 74 32 66 48 66 C64 66 78 74 94 90 Z", 'terrain', '#4E5F35', 1)
    b.hl("M8 86 C20 76 32 70 44 69", 1.1, .5)
    b.ln("M48 70 L38 82 M48 70 L58 82", '#3A4048', 1.6)
    b.r(46, 16, 4, 56, 'cylM', MS)
    b.ln("M48 16 L48 6", '#2A2E33', 1.4); b.c(48, 5.6, 1.6, REDL)
    for s in (-1, 1):
        x0 = 48 + s * 4
        b.ln(f"M48 26 L{x0} 26", '#5E6A78', 2)
        b.p(f"M{x0} 17 L{x0 + s*7} 19 L{x0 + s*7} 37 L{x0} 39 Z", 'metal', MS, 1)
        b.ln(f"M{x0 + s*2} 21 L{x0 + s*2} 35", '#97A3B1', .7)
    b.r(52, 46, 12, 14, 'metal2', MS, rx=1.2)
    leds(b, [(55.6, 50, GREEN), (55.6, 55, AMBER)])
    b.ln("M66 50 L60 50", '#97A3B1', .8)
    b.ln("M30 20 Q24 28 30 36 M24 14 Q14 28 24 42 M66 20 Q72 28 66 36 M72 14 Q82 28 72 42", '#3D86D6', 1.6, .85)
    b.ln("M4 56 L18 50 M78 50 L92 56", '#3D86D6', 1.4, extra="stroke-dasharray='2.4 2.4'")
    arrowhead(b, 4, 56, 157, '#3D86D6', 3.4); arrowhead(b, 92, 56, 23, '#3D86D6', 3.4)

@icon('router', '路由器', '感知通信')
def _(b):
    b.sh(48, 84, 40, 3.4)
    b.ln("M22 50 L14 12 M74 50 L82 12", '#22272D', 3.4)
    b.ln("M21.4 46 L14.6 14 M73.4 46 L80.6 14", '#5E6A78', 1)
    b.p("M8 50 L8 66 A40 12 0 0 0 88 66 L88 50 Z", 'cylM', MS, 1.1)
    b.e(48, 50, 40, 12, 'glass', '#25578F', 1.1)
    b.e(40, 46, 22, 5, '#FFFFFF', op=.25)
    for (x1, y1, x2, y2, a) in ((16, 50, 36, 50, 0), (80, 50, 60, 50, 180), (52, 52.6, 52, 41, -90), (44, 47.4, 44, 59, 90)):
        b.ln(f"M{x1} {y1} L{x2 - 3*math.cos(math.radians(a)):.1f} {y2 - 3*math.sin(math.radians(a)):.1f}", '#FFFFFF', 2.2)
        arrowhead(b, x2, y2, a, '#FFFFFF', 4.2)
    leds(b, [(30, 71, GREEN), (36, 72, GREEN), (42, 72.4, AMBER), (48, 72.6, GREEN)])
    b.hl("M10 54 L10 64", 1, .8)

@icon('firewall', '防火墙', '感知通信')
def _(b):
    b.sh(48, 88, 40, 3.4)
    fl = "M26 42 C18 32 22 22 30 14 C30 22 36 22 38 14 C42 6 48 4 50 0 C52 10 60 14 58 24 C64 20 64 14 64 10 C72 18 74 32 64 42 Z"
    b.p(fl, 'flame', '#B5361F', .8)
    b.p("M36 42 C32 36 36 30 40 26 C40 32 44 32 46 26 C52 30 56 36 52 42 Z", '#FFE48A', op=.9)
    b.p("M8 46 L22 36 L84 36 L70 46 Z", 'brickT', '#7A3524', 1)
    b.p("M70 46 L84 36 L84 76 L70 86 Z", '#8A3A28', '#5A2418', 1)
    b.r(8, 46, 62, 40, 'brick', '#6E2C1E', sw=1.2)
    for i in range(4):
        y = 46 + i * 10
        if i: b.ln(f"M8 {y} L70 {y}", '#F1DDD2', 1.2, cap='butt')
        off = 0 if i % 2 == 0 else 10
        xs = ' '.join(f"M{x} {y} L{x} {y+10}" for x in range(18 + off, 70, 20))
        b.ln(xs, '#F1DDD2', 1.2, cap='butt')
    for i in range(1, 4):
        y = 46 + i * 10
        b.ln(f"M70 {y} L84 {y - 10}", '#C98C78', 1, cap='butt')
    b.hl("M10 47.4 L68 47.4", 1, .45)
    b.hl("M11 45 L22.4 37.3 L82.6 37.3", 1, .8)

@icon('fiber', '光纤／光端机', '感知通信')
def _(b):
    b.sh(40, 86, 36, 3.2)
    cols = ('#F2C84B', '#2FB7C4', '#F28C28')
    ends = ((70, 12), (84, 22), (90, 38))
    for k, ((ex, ey), c_) in enumerate(zip(ends, cols)):
        sx = 34 + k * 9
        d = f"M{sx} 52 C{sx} 32 {ex - 18} {ey + 6} {ex - 5} {ey}"
        b.ln(d, '#2A2E33', 3.6); b.ln(d, c_, 2.2)
        b.g(f"rotate({-25 + k*10} {ex - 3} {ey})")
        b.r(ex - 8, ey - 2.2, 7, 4.4, 'metal', MS, rx=1, sw=.6)
        b.eg()
        b.c(ex + 1.4, ey - .6, 4.6, 'glow')
        b.c(ex + 1.4, ey - .6, 1.6, '#FFFFFF')
    box3d(b, 6, 56, 60, 26, 10, 8, 'metal2', 'metal', 'metal3', MS, 1.5)
    for k in range(3):
        b.r(31 + k * 9, 61, 6, 6, '#1E2328', rx=.8)
        b.r(32.4 + k * 9, 62.4, 3.2, 3.2, cols[k], op=.9)
    b.r(10, 61, 16, 8, 'scr', '#0B1A2C', rx=.8, sw=.6)
    b.ln("M12 65 L24 65", '#7FE0A0', 1, extra="stroke-dasharray='1.6 1'")
    leds(b, [(12, 75, GREEN), (17, 75, GREEN), (22, 75, AMBER)])
    b.ln("M30 75 L62 75", '#97A3B1', .8)

def mini_sat(b, x, y, s=1.0):
    b.g(f"translate({x} {y}) rotate(-20) scale({s})")
    b.r(-14, -3.4, 10, 6.8, 'solar', '#14294A', sw=.6)
    b.r(4, -3.4, 10, 6.8, 'solar', '#14294A', sw=.6)
    b.ln("M-9 -3 L-9 3 M9 -3 L9 3", '#9CC2EA', .5, .7)
    b.r(-4.4, -4.4, 8.8, 8.8, 'gold', '#6E5418', rx=1, sw=.6)
    b.eg()

@icon('beidou', '北斗终端', '感知通信')
def _(b):
    b.sh(44, 87, 36, 3.2)
    mini_sat(b, 18, 13, .9); mini_sat(b, 48, 9, .9); mini_sat(b, 80, 14, .9)
    b.ln("M20 18 L64 40 M48 14 L64 40 M78 19 L64 40", '#3D86D6', 1.1, .75, extra="stroke-dasharray='2.4 2'")
    b.r(61, 40, 6, 8, 'metal3', MS, sw=.8)
    b.p("M54 42 C54 34 74 34 74 42 Z", 'white', '#7C8A9B', 1)
    b.e(64, 42, 10, 2.4, 'metal2', MS, .8)
    b.hl("M57.6 39.6 C59 37 62 36.2 64.4 36.2", 1, .9)
    box3d(b, 10, 52, 58, 32, 8, 7, 'dkm', 'metal2', 'dkm2', DS, 2.5)
    b.r(15, 57, 30, 22, 'scr', '#0B1A2C', rx=1.2, sw=.6)
    b.ln("M17 74 C22 70 26 74 30 68 S38 64 43 60", '#7FE0A0', .9, .8)
    b.ln("M17 62 L43 62 M17 68 L43 68 M23 58 L23 78 M33 58 L33 78", '#3D86D6', .5, .6)
    b.p("M30 60.4 C27.6 60.4 26 62.2 26 64.4 C26 67.4 30 71.6 30 71.6 C30 71.6 34 67.4 34 64.4 C34 62.2 32.4 60.4 30 60.4 Z", REDL, '#8A2A20', .6)
    b.c(30, 64.4, 1.3, '#FFFFFF')
    for i in range(3):
        for j in range(3):
            b.r(49 + i * 5.4, 58 + j * 5.6, 4, 4, 'metal3', '#1E2328', rx=.8, sw=.5)
    leds(b, [(15, 81.6, GREEN)])

@icon('weather', '气象站', '感知通信')
def _(b):
    b.sh(48, 89, 28, 3)
    b.p("M38 89 L58 89 L55 84 L41 84 Z", 'metal3', MS, .8)
    b.r(46, 14, 4, 72, 'cylM', MS)
    b.ln("M30 14 L66 14", '#4B5867', 1.8)
    b.c(48, 8, 3.4, 'sphere', MS, .7); b.ln("M48 11 L48 14", '#4B5867', 1.4)
    for cx in (28, 68):
        b.p(f"M{cx-5} 14 A5 5 0 0 0 {cx+5} 14 Z", 'sphere', MS, .8)
        b.e(cx, 14, 5, 1.4, 'dkm2')
    b.c(48, 14, 2.4, 'hub', '#1D2228', .6)
    b.ln("M22 30 L74 30", '#4B5867', 1.8)
    b.p("M16 30 L24 25.4 L24 34.6 Z", REDL, '#8A2A20', .6)
    b.p("M68 24 L80 22 L80 38 L68 36 Z", 'metal', MS, .9)
    b.c(48, 30, 2.4, 'metal3', MS, .6)
    b.r(56, 50, 26, 22, 'white', '#7C8A9B', rx=1.2)
    b.p("M54 50 L84 50 L82 46 L58 46 Z", 'whitedk', '#7C8A9B', .8)
    for i in range(5): b.ln(f"M59 {54 + i*3.6} L79 {54 + i*3.6}", '#A3AEBB', .9)
    b.ln("M50 60 L56 60", '#4B5867', 2)
    b.g('rotate(-20 28 58)')
    b.r(14, 52, 26, 14, 'solar', '#14294A', sw=.8)
    b.ln("M20.5 52.4 L20.5 65.6 M27 52.4 L27 65.6 M33.5 52.4 L33.5 65.6 M14.4 59 L39.6 59", '#9CC2EA', .5, .6)
    b.p("M15 53 L24 53 L18 65 L15 65 Z", '#FFFFFF', op=.14)
    b.eg()
    b.ln("M40 62 L46 62", '#4B5867', 2)
    b.hl("M47 16 L47 84", .8, .8)

@icon('camera', '监控摄像机', '感知通信')
def _(b):
    b.p("M15 48 L19 62 L4 90 L-2 64 Z", 'beamR')
    b.r(80, 18, 10, 30, 'metal2', MS, rx=2)
    b.c(85, 23, 1.2, '#5E6A78'); b.c(85, 43, 1.2, '#5E6A78')
    b.ln("M82 33 L70 33 L62 42", '#4B5867', 5)
    b.ln("M82 33 L70 33 L62 42", '#C9D1DA', 2)
    b.g('rotate(-22 44 44)')
    b.r(54, 38, 10, 10, 'metal3', MS, rx=2)
    b.r(16, 34, 44, 20, 'white', '#7C8A9B', rx=6)
    b.p("M10 28 L62 28 L62 33.4 L10 33.4 Z", 'metal', MS, .9)
    b.p("M10 28 L16 28 L16 34 L12 34 Z", 'metal3', MS, .6)
    b.e(16, 44, 3.6, 9.6, 'dkm2', DS, .8)
    b.e(14.6, 44, 2.4, 7, 'lens', '#05101C', .6)
    b.ln("M24 51 L56 51", '#A3AEBB', .8)
    b.c(52, 40, 1.4, REDL)
    b.hl("M20 36.4 L56 36.4", 1, .9)
    glint(b, 14, 40.6, .8, 1.6)
    b.eg()

# ================= 指控信息 (B) =================
@icon('big_screen', '指挥大屏', '指控信息')
def _(b):
    b.sh(48, 87, 42, 3.4)
    b.r(18, 70, 6, 14, 'metal3', MS, sw=.8); b.r(72, 70, 6, 14, 'metal3', MS, sw=.8)
    b.r(10, 82, 76, 5, 'metal2', MS, rx=1.5)
    b.r(4, 10, 88, 62, 'dkm2', DS, rx=2.5, sw=1.2)
    tw, th = 27, 27
    for j in range(2):
        for i in range(3):
            x, y = 7.5 + i * (tw + 1.5), 13.5 + j * (th + 1.5)
            b.r(x, y, tw, th, 'scr', '#0B1A2C', sw=.4)
    b.p("M10 18 C14 16 18 20 22 18 C26 16 30 22 32 30 C28 34 22 32 18 36 C14 36 10 34 9 30 Z", '#4E8F5C', op=.75)
    b.ln("M12 34 L20 24 L30 28", REDL, 1, extra="stroke-dasharray='1.6 1.2'")
    b.c(50, 27, 9, 'none', '#7FE0A0', .8, .8); b.c(50, 27, 4.5, 'none', '#7FE0A0', .6, .6)
    b.p("M50 27 L57 21 A9 9 0 0 1 59 27 Z", '#7FE0A0', op=.45)
    b.c(46, 23, 1.2, '#F2A93B')
    for k, h in enumerate((10, 16, 8, 20, 13)):
        b.r(68 + k * 4.6, 37 - h, 3.2, h, '#8FD0FF' if k != 3 else '#F2A93B', op=.85)
    b.ln("M10 60 C16 50 22 58 28 48 S32 52 34 50", '#7FE0A0', 1)
    b.ln("M38 48 L62 48 M38 53 L56 53 M38 58 L60 58 M38 63 L52 63", '#9CC2EA', 1.1, .65)
    b.c(78, 56, 8, 'none', '#3D86D6', 3.4); b.p("M78 56 L78 48 A8 8 0 0 1 85.4 59 Z", '#F2A93B', op=.9)
    b.p("M8 14 L40 14 L14 69 L8 69 Z", '#FFFFFF', op=.08)
    b.hl("M6 11.4 L90 11.4", .9, .6)

@icon('laptop', '便携计算机', '指控信息')
def _(b):
    b.sh(48, 86, 44, 3.2)
    b.r(18, 10, 60, 48, 'dkm2', DS, rx=2.5)
    b.r(22, 14, 52, 40, 'scr', '#0B1A2C', sw=.6)
    b.r(22, 14, 52, 5, '#3D86D6', op=.7)
    b.r(25, 23, 18, 14, '#4E8F5C', op=.55, rx=1)
    b.ln("M27 33 L33 27 L39 30", '#F2A93B', 1)
    b.ln("M47 25 L70 25 M47 29 L66 29 M47 33 L68 33", '#9CC2EA', 1.1, .7)
    b.ln("M26 49 C32 41 38 47 44 40 S56 44 70 38", '#7FE0A0', 1)
    b.p("M23 15 L40 15 L27 53 L23 53 Z", '#FFFFFF', op=.1)
    b.p("M18 58 L78 58 L90 78 L6 78 Z", 'metal', MS, 1.1)
    for k, (y, x0, x1) in enumerate(((61.6, 21, 75), (65.2, 18.6, 77.4), (68.8, 16.4, 79.6))):
        b.ln(f"M{x0} {y} L{x1} {y}", '#5E6A78', 2.4, cap='butt', extra="stroke-dasharray='3.2 1'")
    b.p("M38 71.6 L58 71.6 L59 76 L37 76 Z", 'metal2', '#97A3B1', .6)
    b.r(6, 78, 84, 4, 'metal3', MS, rx=2, sw=1)
    leds(b, [(82, 75, GREEN)])
    b.hl("M20 11.4 L76 11.4", .9, .5)

@icon('tablet', '平板终端', '指控信息')
def _(b):
    b.sh(50, 86, 38, 3.2)
    b.g('rotate(-10 48 48)')
    b.r(10, 18, 76, 56, 'dkm2', DS, rx=7, sw=1.2)
    b.r(16, 24, 64, 44, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.p("M16 24 L42 24 C40 32 44 38 38 46 C32 54 34 62 26 68 L16 68 Z", '#4E8F5C', op=.6)
    b.p("M56 24 L80 24 L80 46 C72 44 66 38 62 32 Z", '#4E8F5C', op=.5)
    b.ln("M24 58 C34 50 44 54 52 42 S66 34 72 30", '#F2A93B', 1.4, extra="stroke-dasharray='2.6 1.6'")
    for x, y, c_ in ((24, 58, '#43C46B'), (72, 30, REDL)):
        b.p(f"M{x} {y} C{x-3} {y-3} {x-3} {y-7} {x} {y-7} C{x+3} {y-7} {x+3} {y-3} {x} {y} Z", c_, '#1E2328', .5)
        b.c(x, y - 4.6, 1.1, '#FFFFFF')
    b.r(64, 52, 12, 12, '#0E2A4A', '#3D86D6', rx=1.5, sw=.6)
    b.ln("M70 54 L70 62 M66 58 L74 58", '#8FD0FF', .8)
    b.c(83, 46, 1.3, '#3A4048')
    b.p("M17 25 L38 25 L22 67 L17 67 Z", '#FFFFFF', op=.1)
    b.hl("M16 19.6 L80 19.6", 1, .5)
    b.eg()

@icon('handheld', '手持终端', '指控信息')
def _(b):
    b.sh(50, 90, 22, 3)
    b.r(30, 4, 7, 14, 'dkm2', DS, rx=2.4)
    b.r(26, 12, 44, 78, 'dkm', DS, rx=8, sw=1.2)
    b.r(24, 26, 4, 14, '#F2A93B', '#8A5A14', rx=1.4, sw=.6)
    b.r(31, 18, 34, 30, 'scr', '#0B1A2C', rx=1.2, sw=.6)
    b.c(48, 33, 10, 'none', '#7FE0A0', .8, .7)
    b.ln("M48 23 L48 43 M38 33 L58 33", '#7FE0A0', .5, .6)
    b.p("M48 25 L51 33 L48 41 L45 33 Z", REDL, op=.9)
    b.p("M48 33 L51 33 L48 41 L45 33 Z", '#FFFFFF', op=.6)
    b.r(33, 20, 9, 3, '#3D86D6', op=.8)
    b.p("M32 19 L42 19 L34 47 L32 47 Z", '#FFFFFF', op=.12)
    b.r(32, 52, 14, 6, 'green', '#1E5A30', rx=2, sw=.6)
    b.r(50, 52, 14, 6, 'red', '#7A2219', rx=2, sw=.6)
    for i in range(3):
        for j in range(4):
            b.r(33 + i * 10.6, 62 + j * 6, 8, 4.2, 'metal3', '#1E2328', rx=1, sw=.5)
    b.hl("M30 15 L66 15", 1, .5)

@icon('data_center', '数据中心', '指控信息')
def _(b):
    b.p("M2 84 L22 70 L94 70 L74 84 Z", 'metal2', MS, .8)
    b.ln("M12 77 L84 77 M26 70 L6 84 M42 70 L22 84 M58 70 L38 84 M74 70 L54 84 M90 70 L70 84", '#8794A3', .6, .7)
    b.p("M8 22 L22 12 L86 12 L72 22 Z", 'metal', MS)
    b.p("M72 22 L86 12 L86 62 L72 72 Z", 'dkm2', DS)
    for k in range(4):
        x = 8 + k * 16
        b.r(x, 22, 16, 50, 'dkm', DS, sw=1)
        b.r(x + 2, 25, 12, 44, 'canopy', '#0F2339', rx=.6, sw=.5, op=.9)
        b.ln(f"M{x+8} 28 L{x+8} 68", '#2A3440', 10, cap='butt', extra="stroke-dasharray='3.4 2.4'")
        b.ln(f"M{x+11} 29.7 L{x+11} 68", GREEN if k % 2 else '#3D9BFF', 1.8, extra="stroke-dasharray='0 5.8'")
        b.p(f"M{x+3} 26 L{x+8} 26 L{x+4} 68 L{x+3} 68 Z", '#FFFFFF', op=.1)
    b.r(6, 6, 80, 3, '#4B5867', rx=1)
    b.ln("M14 9 L14 12 M40 9 L40 12 M66 9 L66 12", '#4B5867', 1.4)
    b.hl("M10 20.6 L22.4 13.3 L85 13.3", .9, .85)

@icon('algorithm', '算法模型', '指控信息')
def _(b):
    b.sh(48, 88, 36, 3.2)
    pins = "M24 14 L76 14 M24 82 L76 82 M14 24 L14 76 M82 24 L82 76"
    b.ln(pins, '#7A5C18', 9, cap='butt', extra="stroke-dasharray='4.6 5'")
    b.ln(pins, '#D9B45A', 7.6, cap='butt', extra="stroke-dasharray='4.6 5'")
    b.ln("M25 10.6 L77 10.6 M25 78.6 L77 78.6", '#FFF1C4', 1, cap='butt', extra="stroke-dasharray='2.6 7'")
    b.r(16, 16, 64, 64, 'dkm', DS, rx=5, sw=1.2)
    b.r(22, 22, 52, 52, 'canopy', '#0F2339', rx=3, sw=.8)
    L1 = [(32, 34), (32, 48), (32, 62)]
    L2 = [(48, 29), (48, 43), (48, 57), (48, 71 - 4)]
    L3 = [(64, 41), (64, 55)]
    segs = ' '.join(f"M{a[0]} {a[1]} L{c_[0]} {c_[1]}" for A, C in ((L1, L2), (L2, L3)) for a in A for c_ in C)
    b.ln(segs, '#8FD0FF', .8, .75)
    for (x, y) in L1 + L2 + L3:
        b.c(x, y, 3.6, 'glow', op=.8)
        b.c(x, y, 2.4, 'node', '#1F4F8C', .5)
    b.p("M23 23 L44 23 L28 73 L23 73 Z", '#FFFFFF', op=.08)
    b.c(22, 22, 1.4, '#97A3B1')
    b.hl("M19 18 L77 18", 1, .5)

@icon('knowledge_graph', '知识图谱', '指控信息')
def _(b):
    nodes = [(48, 46, 11, 'node', '#1F4F8C'), (18, 20, 7, 'nodeG', '#1F7A3E'), (78, 18, 7, 'nodeA', '#A8611A'),
             (84, 58, 6.4, 'nodeP', '#4E3590'), (60, 84, 7, 'nodeG', '#1F7A3E'), (16, 70, 7, 'nodeA', '#A8611A'),
             (40, 12, 4.4, 'nodeP', '#4E3590'), (88, 36, 4.4, 'node', '#1F4F8C'), (34, 88, 4.4, 'node', '#1F4F8C'), (6, 44, 4.4, 'nodeP', '#4E3590')]
    links = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (2, 7), (3, 7), (4, 8), (5, 8), (5, 9), (1, 9), (2, 6)]
    d = ' '.join(f"M{nodes[a][0]} {nodes[a][1]} L{nodes[c_][0]} {nodes[c_][1]}" for a, c_ in links)
    b.ln(d, '#5E6A78', 2.4); b.ln(d, '#C9D1DA', 1)
    for a, c_ in links[:5]:
        x1, y1 = nodes[a][:2]; x2, y2, r_ = nodes[c_][:3]
        ang = math.atan2(y2 - y1, x2 - x1)
        arrowhead(b, x2 - (r_ + .6) * math.cos(ang), y2 - (r_ + .6) * math.sin(ang), math.degrees(ang), '#4B5867', 3.6)
    for x, y, r_, g_, st in nodes:
        b.e(x + 1, y + r_ + 1.2, r_ * .8, 1.4, 'shadow')
        b.c(x, y, r_, g_, st, .9)
        b.e(x - r_ * .3, y - r_ * .42, r_ * .46, r_ * .25, '#FFFFFF', op=.7)

@icon('document', '文档报告', '指控信息')
def _(b):
    b.sh(50, 90, 30, 3)
    b.g('rotate(-8 48 50)')
    b.r(22, 10, 54, 72, 'paper', '#97A3B1', rx=1.5, sw=1)
    b.eg()
    d = "M18 10 L62 10 L78 26 L78 88 L18 88 Z"
    b.drop(d, 2, 2.6, .14)
    b.p(d, 'paper', '#7C8A9B', 1.1)
    b.p("M62 10 L62 26 L78 26 Z", 'metal2', '#7C8A9B', .8)
    b.r(24, 18, 32, 6, '#3D86D6', rx=1)
    b.ln("M24 31 L72 31 M24 36 L72 36 M24 41 L64 41", '#A3AEBB', 1.6, cap='butt')
    b.r(24, 47, 26, 20, '#EEF3F8', '#C9D1DA', sw=.6)
    for k, h in enumerate((8, 13, 6, 16)):
        b.r(27 + k * 5.6, 65 - h, 4, h, '#3D86D6' if k != 3 else '#F2A93B')
    b.ln("M54 50 L72 50 M54 55 L70 55 M54 60 L72 60 M54 65 L66 65", '#A3AEBB', 1.6, cap='butt')
    b.ln("M24 72 L60 72 M24 77 L52 77", '#A3AEBB', 1.6, cap='butt')
    b.c(66, 78, 7, 'none', '#D9312A', 1.4, op=.85)
    b.p(star(66, 78, 3.6), '#D9312A', op=.85)
    b.hl("M19.6 12 L19.6 86", 1, .8)

@icon('video', '视频流', '指控信息')
def _(b):
    b.sh(48, 86, 42, 3.2)
    b.r(6, 14, 84, 64, 'dkm2', DS, rx=3, sw=1.2)
    for i in range(9):
        b.r(10 + i * 9.2, 16.4, 4.6, 3.6, '#D3DAE2', rx=.8, op=.85)
        b.r(10 + i * 9.2, 72, 4.6, 3.6, '#D3DAE2', rx=.8, op=.85)
    b.r(9, 22, 78, 46, 'scr', '#0B1A2C', sw=.6)
    b.p("M9 68 L9 52 L24 40 L36 50 L52 34 L70 50 L87 42 L87 68 Z", '#4E8F5C', op=.6)
    b.p("M9 68 L9 58 L28 50 L44 60 L60 52 L87 60 L87 68 Z", '#2E5D3A', op=.7)
    b.c(76, 30, 4, '#F2C84B', op=.85)
    b.c(48, 45, 12, '#0B1A2C', op=.35)
    b.c(48, 45, 11, 'glass', '#25578F', 1)
    b.p("M44.6 38.6 L55.4 45 L44.6 51.4 Z", '#FFFFFF')
    b.e(45, 39, 5, 2.4, '#FFFFFF', op=.5)
    b.ln("M14 63 L82 63", '#FFFFFF', 1.6, .35)
    b.ln("M14 63 L40 63", REDL, 1.6)
    b.c(40, 63, 2.2, '#FFFFFF')
    b.p("M10 23 L32 23 L16 67 L10 67 Z", '#FFFFFF', op=.08)

@icon('clock', '时统设备', '指控信息')
def _(b):
    b.sh(48, 84, 42, 3.2)
    b.ln("M70 38 L70 44", '#4B5867', 2)
    b.p("M63 38 C63 31 77 31 77 38 Z", 'white', '#7C8A9B', .9)
    b.e(70, 38, 7, 1.8, 'metal2', MS, .6)
    box3d(b, 6, 48, 74, 28, 10, 8, 'metal2', 'metal', 'metal3', MS, 1.5)
    b.c(24, 52, 17, 'dkm', DS, 1.1)
    b.c(24, 52, 14, 'white', '#7C8A9B', .8)
    for i in range(12):
        a = math.radians(i * 30)
        r1 = 10.6 if i % 3 else 9.4
        b.ln(f"M{24 + r1*math.sin(a):.1f} {52 - r1*math.cos(a):.1f} L{24 + 12.4*math.sin(a):.1f} {52 - 12.4*math.cos(a):.1f}", '#3A4048', 1 if i % 3 else 1.6)
    b.ln("M24 52 L24 43.6 M24 52 L30 55.4", '#22272D', 1.8)
    b.ln("M24 52 L16.6 47", REDL, .9)
    b.c(24, 52, 1.6, '#22272D')
    b.e(19.6, 44, 5, 2.4, '#FFFFFF', op=.6)
    b.r(44, 54, 32, 13, '#0B1410', '#1E2328', rx=1.2, sw=.8)
    for k in range(4):
        x = 46.4 + k * 7.4 + (2 if k > 1 else 0)
        b.r(x, 56.4, 4, 8.4, 'none', '#7FE0A0' if True else '', sw=1.1)
        b.ln(f"M{x} 60.6 L{x+4} 60.6", '#7FE0A0', 1)
    b.c(60.8, 58.6, .8, '#7FE0A0'); b.c(60.8, 62.6, .8, '#7FE0A0')
    leds(b, [(48, 71.6, GREEN), (53, 71.6, GREEN), (58, 71.6, AMBER)])

@icon('simulation', '仿真推演', '指控信息')
def _(b):
    b.ln("M14 64 L14 88 M82 64 L82 88 M48 80 L48 94", '#4B5867', 2.6)
    b.p("M6 46 L48 26 L90 46 L48 66 Z", 'terrain', '#4E5F35', 1)
    b.p("M6 46 L48 66 L48 78 L6 58 Z", 'soil', '#5A4026', 1)
    b.p("M48 66 L90 46 L90 58 L48 78 Z", '#8A6A48', '#5A4026', 1)
    b.ln("M6 50 L48 70 L90 50", '#D9BC94', .8, .7)
    b.p("M20 45 C24 36 32 34 38 42 C34 46 26 48 20 45 Z", '#6A8840', '#4E5F35', .7)
    b.p("M24 42 C26 38 30 37.6 33 40", '#FFFFFF', op=.0)
    b.p("M52 36 C56 28 66 28 70 38 C64 42 58 42 52 36 Z", '#6A8840', '#4E5F35', .7)
    b.ln("M24 38.6 C27 35.6 30 35.6 33 38 M56 31.6 C60 28.6 64 29 67 33", '#FFFFFF', .9, .6)
    b.ln("M14 50 C26 50 34 56 46 54 S66 50 80 52", '#3D86D6', 2.4)
    b.ln("M14 50 C26 50 34 56 46 54 S66 50 80 52", '#BFE3FF', .8)
    b.ln("M30 58 C38 50 50 48 60 44", REDL, 1.6, extra="stroke-dasharray='2.6 1.8'")
    arrowhead(b, 62.6, 43, -22, REDL, 4)
    for x, y, c_ in ((28, 56, REDL), (24, 42, REDL), (64, 34, '#3D86D6'), (72, 46, '#3D86D6')):
        b.ln(f"M{x} {y} L{x} {y-12}", '#2A2E33', 1.1)
        b.p(f"M{x} {y-12} L{x+7} {y-9.6} L{x} {y-7.2} Z", c_, '#2A2E33', .4)
        b.e(x, y, 1.6, .7, '#2A2E33')
    b.hl("M9 45.6 L48 27.4 L87 45.6", 1, .7)

@icon('gpu', '算力（GPU）', '指控信息')
def _(b):
    b.sh(50, 86, 42, 3)
    b.r(3, 22, 6, 56, 'metal', MS, rx=1)
    b.c(6, 30, 1.2, '#5E6A78')
    b.r(10, 64, 78, 8, 'pcb', '#143820', sw=.8)
    for i in range(9):
        b.r(38 + i * 4.4, 72, 3, 6, 'gold', '#8A6A20', sw=.3)
    b.p("M9 28 L15 22 L93 22 L87 28 Z", 'metal3', MS, .9)
    b.p("M87 28 L93 22 L93 58 L87 64 Z", 'dkm2', DS)
    b.r(9, 28, 78, 36, 'dkm', DS, rx=3)
    b.ln("M12 31 L84 31", '#3D86D6', 1.6, .9)
    for cx in (30, 64):
        b.c(cx, 46, 14, 'dkm2', '#101317', .8)
        b.c(cx, 46, 12.4, 'prop', '#8D9BAC', .5)
        for k in range(7):
            a = math.radians(k * 360 / 7)
            b.p(f"M{cx + 3*math.cos(a):.1f} {46 + 3*math.sin(a):.1f} Q{cx + 9*math.cos(a+.2):.1f} {46 + 9*math.sin(a+.2):.1f} {cx + 11.6*math.cos(a+.9):.1f} {46 + 11.6*math.sin(a+.9):.1f}", 'none', '#5E6A78', 1.4)
        b.c(cx, 46, 3.4, 'hub', '#1D2228', .6)
    leds(b, [(82, 58, GREEN)])
    b.hl("M11 26.6 L15.6 23.3 L91.6 23.3", .9, .7)

@icon('storage', '存储阵列', '指控信息')
def _(b):
    b.sh(46, 86, 40, 3.2)
    for y0 in (52, 26):
        box3d(b, 8, y0, 66, 24, 12, 9, 'dkm', 'metal2', 'dkm2', DS, 2)
        b.ln(f"M11.4 {y0+12} L72.6 {y0+12}", '#8794A3', 18, cap='butt', extra="stroke-dasharray='4.2 .9'")
        b.ln(f"M11.4 {y0+4} L72.6 {y0+4}", '#C9D1DA', 1.2, cap='butt', extra="stroke-dasharray='4.2 .9'")
        b.ln(f"M13.5 {y0+10} L72 {y0+10}", '#4B5867', 8, cap='butt', extra="stroke-dasharray='.9 4.2'")
        b.ln(f"M13.5 {y0+18} L72 {y0+18}", GREEN, 1.6, extra="stroke-dasharray='0 5.1'")
        b.c(13.5 + 5.1 * (3 if y0 == 52 else 8), y0 + 18, .9, AMBER)

@icon('api', '接口服务', '指控信息')
def _(b):
    b.sh(54, 84, 40, 3.2)
    b.ln("M4 72 C10 72 12 56 20 52", '#22272D', 4.4)
    b.ln("M4 72 C10 72 12 56 20 52", '#5E6A78', 1.4)
    b.r(18, 38, 20, 24, 'dkm', DS, rx=3)
    b.r(36, 42, 4, 16, 'dkm2', DS, rx=1, sw=.6)
    for y in (44.4, 51.6):
        b.r(40, y, 12, 4, 'cylM', MS, rx=1, sw=.6)
    b.hl("M20.6 40 L35.4 40", .9, .5)
    b.c(56, 50, 5, 'glow')
    b.p("M54 22 L64 14 L90 14 L80 22 Z", 'metal', MS)
    b.p("M80 22 L90 14 L90 70 L80 78 Z", 'metal3', MS)
    b.r(54, 22, 26, 56, 'glass', '#25578F', rx=2)
    b.r(60, 38, 14, 24, 'canopy', '#0F2339', rx=2, sw=.8)
    b.r(63, 43.6, 8, 3.2, '#0B111A', rx=1); b.r(63, 52.8, 8, 3.2, '#0B111A', rx=1)
    b.p("M56 24 L66 24 L58 76 L56 76 Z", '#FFFFFF', op=.2)
    leds(b, [(62, 70, GREEN), (67, 70, GREEN), (72, 70, AMBER)])
    b.ln("M62 30 L72 30", '#FFFFFF', 1.4, .7)
    b.hl("M57 21.3 L64.4 15.3 L89 15.3", .9, .85)

@icon('message_bus', '消息总线', '指控信息')
def _(b):
    for x in (16, 44, 72):
        b.ln(f"M{x+4} 30 L{x+4} 46", '#5E6A78', 2.4); b.ln(f"M{x+4} 30 L{x+4} 46", '#C9D1DA', .9)
    for x in (30, 58):
        b.ln(f"M{x+4} 54 L{x+4} 70", '#5E6A78', 2.4); b.ln(f"M{x+4} 54 L{x+4} 70", '#C9D1DA', .9)
    b.drop("M4 43 L92 43 L92 57 L4 57 Z", 2, 2.6, .14)
    b.r(4, 43, 88, 14, 'glass', '#25578F', rx=7, sw=1.1)
    b.r(9, 45, 78, 3.4, '#FFFFFF', rx=1.7, op=.45)
    for x in range(14, 86, 12):
        b.ln(f"M{x} 47 L{x+4} 50 L{x} 53", '#FFFFFF', 1.6, .9)
    for x in (20, 48, 76, 34, 62):
        y = 44 if x in (20, 48, 76) else 56
        b.c(x, y, 2.4, 'metal', MS, .7)
    for x in (16, 44, 72):
        box3d(b, x - 2, 16, 14, 12, 4, 3.6, 'metal2', 'metal', 'metal3', MS, 1)
        leds(b, [(x + 2, 22, GREEN)])
    for x in (30, 58):
        box3d(b, x - 2, 72, 14, 12, 4, 3.6, 'metal2', 'metal', 'metal3', MS, 1)
        leds(b, [(x + 2, 78, AMBER)])

@icon('map', '电子地图', '指控信息')
def _(b):
    xs = [6, 28, 48, 68, 90]
    off = [0, -6, 0, -6, 0]
    b.sh(48, 88, 42, 3)
    for i in range(4):
        x1, x2 = xs[i], xs[i + 1]; o1, o2 = off[i], off[i + 1]
        b.p(f"M{x1} {22+o1} L{x2} {22+o2} L{x2} {80+o2} L{x1} {80+o1} Z", '#E4EEDA', '#7C8A9B', 1)
    def yat(x, y):
        for i in range(4):
            if xs[i] <= x <= xs[i + 1]:
                t = (x - xs[i]) / (xs[i + 1] - xs[i]); return y + off[i] + (off[i + 1] - off[i]) * t
    land = [(6, 30), (16, 34), (28, 30), (38, 40), (48, 36), (56, 46), (68, 40), (80, 48), (90, 44)]
    pts = ' L'.join(f"{x} {yat(x, y):.1f}" for x, y in land)
    b.p(f"M6 {yat(6, 80):.1f} L{pts} L90 {yat(90, 80):.1f} L68 74 L48 80 L28 74 Z", '#B9D08A', op=.85)
    sea = ' L'.join(f"{x} {yat(x, y):.1f}" for x, y in [(6, 22), (6, 30), (16, 34), (28, 30), (38, 40), (48, 36), (56, 46), (68, 40), (80, 48), (90, 44), (90, 22)][:])
    b.p(f"M{sea} L68 16 L48 22 L28 16 Z", '#A9D2F2', op=.85)
    road = ' L'.join(f"{x} {yat(x, y):.1f}" for x, y in [(10, 72), (20, 64), (32, 66), (44, 58), (56, 62), (66, 56)])
    b.ln("M" + road, REDL, 1.6, extra="stroke-dasharray='3 2'")
    for i in (1, 3):
        x1, x2 = xs[i], xs[i + 1]
        b.p(f"M{x1} {22+off[i]} L{x2} {22+off[i+1]} L{x2} {80+off[i+1]} L{x1} {80+off[i]} Z", '#0A1420', op=.1)
    for x, y, c_ in ((20, 64, '#3D86D6'), (68, 56, REDL)):
        y = yat(x, y)
        b.e(x, y + 1, 3, 1.1, '#000000', op=.25)
        b.p(f"M{x} {y} C{x-4} {y-5} {x-6} {y-9} {x-6} {y-12} C{x-6} {y-16} {x-3} {y-18.6} {x} {y-18.6} C{x+3} {y-18.6} {x+6} {y-16} {x+6} {y-12} C{x+6} {y-9} {x+4} {y-5} {x} {y} Z", c_, '#1E2328', .7)
        b.c(x, y - 12, 2.4, '#FFFFFF')
    b.hl("M7.4 23 L27 17 L47 23", .9, .6)

@icon('workflow', '流程编排', '指控信息')
def _(b):
    def blk(x, y, w, h, g_, st, rx):
        b.r(x + 1.5, y + 2, w, h, '#0A1420', rx=rx, op=.16)
        b.r(x, y, w, h, g_, st, rx=rx, sw=1)
        b.r(x + 2, y + 1.4, w - 4, h * .38, '#FFFFFF', rx=rx * .6, op=.35)
    def ar(d, x, y, a):
        b.ln(d, '#4B5867', 1.8); arrowhead(b, x, y, a, '#4B5867', 4)
    ar("M48 21 L48 26", 48, 29.6, 90)
    ar("M34 42 L20 42 L20 52", 20, 55.6, 90)
    ar("M62 42 L76 42 L76 52", 76, 55.6, 90)
    ar("M20 70 L20 80 L30 80", 33.6, 80, 0)
    ar("M76 70 L76 80 L66 80", 62.4, 80, 180)
    blk(34, 6, 28, 14, 'green', '#1E5A30', 7)
    b.drop("M48 30 L62 42 L48 54 L34 42 Z", 1.5, 2, .16)
    b.p("M48 30 L62 42 L48 54 L34 42 Z", 'amber', '#8A4E14', 1)
    b.p("M48 32 L59 41.4 L37 41.4 Z", '#FFFFFF', op=.3)
    blk(6, 56, 28, 14, 'glass', '#25578F', 2.4)
    blk(62, 56, 28, 14, 'glass', '#25578F', 2.4)
    blk(34, 73, 28, 14, 'metal', MS, 2.4)
    b.ln("M12 63 L26 63 M68 63 L82 63 M40 80 L56 80", '#FFFFFF', 1.4, .8)
    b.c(48, 13, 2.4, '#FFFFFF', op=.8)


KEYS = """commander staff_officer pilot drone_pilot engineer maintainer analyst expert_group squad sailor driver medic trainee user_group
ir_sensor acoustic rf_detector laser_rangefinder antenna_array relay router firewall fiber beidou weather camera
big_screen laptop tablet handheld data_center algorithm knowledge_graph document video clock simulation gpu storage api message_bus map workflow""".split()

if __name__ == '__main__':
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    assert set(byk) == set(KEYS) and len(byk) == len(ICONS), set(KEYS) ^ set(byk)
    old = set(re.findall(r"key: '([a-z_0-9]+)'", open('/home/claude/drawtool/icons.js', encoding='utf-8').read()))
    assert not (old & set(KEYS)), old & set(KEYS)
    SZ = []
    lines = ['ICON_LIB.push(...[']
    for k in KEYS:
        _, n, c, fn = byk[k]
        b = B(k); fn(b)
        s = b.svg()
        s = re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
        s = re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
        s = re.sub(r"(?<=[ '-])0\.(\d)", r'.\1', s)
        assert '"' not in s
        SZ.append((len(s), k))
        lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
    lines.append(']);')
    open('/home/claude/drawtool/icons_b.js', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), sorted(SZ)[-6:])
