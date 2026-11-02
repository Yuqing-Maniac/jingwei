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


# =====================================================================
#  icons_gen_g.py — batch G: 单兵·按兵种 (cat 人员)
#  Header above (palette, builder B, helpers, people helpers) is copied
#  from icons_gen_b.py; everything below is new.
# =====================================================================
GR.update({
    'camoB': L(V, (0, '#A3B47A'), (.5, '#74874B'), (1, '#46562F')),
    'ocB': L(V, (0, '#9DB6C8'), (.5, '#6283A0'), (1, '#37506A')),
    'sof': L(V, (0, '#667061'), (.5, '#3E473B'), (1, '#1F251E')),
    'sofh': L(V, (0, '#59625A'), (.5, '#363D38'), (1, '#181C1A')),
    'ghil': L(V, (0, '#A5A465'), (.5, '#737A42'), (1, '#444C28')),
    'tankG': L(V, (0, '#6E7B53'), (.5, '#4A5638'), (1, '#2B3520')),
    'tankH': L(V, (0, '#5B6350'), (.5, '#363E30'), (1, '#181D15')),
    'cbrn': L(V, (0, '#DDE2B2'), (.5, '#B3BC82'), (1, '#7D8758')),
    'rubber': L(V, (0, '#59605A'), (.5, '#30363A'), (1, '#14181B')),
    'hivis': L(V, (0, '#F2FF84'), (.5, '#CBF228'), (1, '#86A80C')),
    'orV': L(V, (0, '#FFB468'), (.5, '#F27020'), (1, '#AE4208')),
    'brass': L(V, (0, '#FAE8AE'), (.5, '#D6AB4E'), (1, '#8E6822')),
    'crate': L(V, (0, '#A3AE76'), (.5, '#73804A'), (1, '#444F2C')),
    'wood': L(V, (0, '#D2B27C'), (.5, '#A68451'), (1, '#6E5230')),
    'hood': L(V, (0, '#434F63'), (.5, '#272F3E'), (1, '#10151D')),
    'adT': L(V, (0, '#A9B58C'), (.5, '#78855A'), (1, '#445030')),
    'nvg': ('r', ('0.4', '0.35', '0.65'), ((0, '#E4FFE4'), (.4, '#4CE070'), (1, '#0B4A1E'))),
    'shell': L(V, (0, '#BBC584'), (.5, '#869256'), (1, '#4E5A30')),
    'canW': L(V, (0, '#FFFFFF'), (1, '#CFD6DE')),
    'canR': L(V, (0, '#F28A3C'), (1, '#BE4D14')),
})

GS = '#1C2420'      # dark green outline
BS = '#2A2218'

def rot(cx, cy, a, x, y):
    t = math.radians(a)
    return (round(cx + x * math.cos(t) - y * math.sin(t), 1), round(cy + x * math.sin(t) + y * math.cos(t), 1))

def patch(b, col, x=17, y=73, w=8, h=6):
    b.r(x, y, w, h, col, '#1E2328', rx=1, sw=.5)
    b.ln(f"M{x+1.2} {y+1.5} L{x+w-1.2} {y+1.5}", '#FFFFFF', .7, .5)

def vcollar(b, fill='olivedk', st=OS):
    b.p("M38 64 L48 74 L58 64 Z", fill, st, .7)

def helm(b, fill='olive', dk='olivedk', st=OS, net=True, strap=True):
    if strap:
        b.ln("M33 40 C34 52 40 56 48 57 C56 56 62 52 63 40", '#2E3238', 1.6)
    b.p("M27 38 C25 20 35 9 48 9 C61 9 71 20 69 38 C64 32.6 57 30.4 48 30.4 C39 30.4 32 32.6 27 38 Z", fill, st, 1.1)
    b.p("M25.6 38.4 C31 31 38 29 48 29 C58 29 65 31 70.4 38.4 C65 34.6 57 33 48 33 C39 33 31 34.6 25.6 38.4 Z", dk, st, .8)
    if net:
        b.ln("M36 22 L40 17 M52 14 L57 18 M60 26 L64 23 M31 30 L35 26 M45 20 L49 16", '#4E5F35', 1.5, .7)
    b.hl("M31 24 C34 15 40 11.4 47 11", 1.3, .8)

def drawrifle(b, cx, cy, ang, sc=1.0, scope=False, supp=False, camo=False):
    b.g(f"translate({cx} {cy}) rotate({ang}) scale({sc})")
    b.p("M-32 -2 L-21 -3.6 L-19 3.2 L-24 7 L-33 5 Z", 'dkm2', KS, .7)
    b.r(-21, -4, 20, 7, 'dkm', KS, rx=1.2, sw=.8)
    b.p("M-12 3 L-6.5 3 L-5 12 L-11 13 Z", '#2A2E33', KS, .6)
    b.r(-1, -3, 18, 5.6, 'dkm2', KS, rx=1.4, sw=.8)
    if supp:
        b.r(16, -2.8, 15, 5.2, 'dkm2', KS, rx=2, sw=.8)
        b.ln("M18 -1.4 L30 -1.4", '#7D8590', .7, .6)
    else:
        b.ln("M17 -.2 L33 -.2", '#15181C', 2.2)
        b.r(31, -1.8, 3.4, 3.6, '#0B0D10', rx=.8, sw=.2)
        b.p("M24 -1 L24 -4.4 L26 -4.4 L26 -1 Z", '#15181C')
    if scope:
        b.r(-17, -10.6, 15, 4.6, 'dkm2', KS, rx=2.2, sw=.8)
        b.e(-1.2, -8.3, 1.5, 2.6, 'lens', KS, .5)
        b.e(-17.6, -8.3, 1.3, 2.4, 'lens', KS, .5)
        b.ln("M-14 -10 L-4 -10", '#FFFFFF', .7, .6)
        b.ln("M-12 -6 L-12 -4 M-5 -6 L-5 -4", KS, 1.2)
    else:
        b.r(-18, -6.6, 6, 2.6, 'dkm', KS, rx=.8, sw=.6)
    b.ln("M-20 -3.3 L15 -3.3", '#FFFFFF', .6, .45)
    b.eg()

# ================= 人员·单兵·按兵种 =================
@icon('inf_rifleman', '步兵（步枪手）', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#D9473A')
    b.ln("M30 68 L58 92", '#3E4C29', 3.4)
    head(b, ears=False)
    helm(b)
    drawrifle(b, 49, 71, -33, 1.0)
    p1 = rot(49, 71, -33, 12, 0); p2 = rot(49, 71, -33, -8, 2)
    arm(b, f"M72 92 L{p1[0]} {p1[1]+2}", '#7E9157', OS, 6.6); hand(b, p1[0], p1[1], 3.2)
    arm(b, f"M20 92 L{p2[0]} {p2[1]+2}", '#7E9157', OS, 6.6); hand(b, p2[0], p2[1], 3.2)
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)

@icon('inf_mg', '机枪手', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    # crossed bandoliers with brass rounds
    for d in ("M22 66 L74 92", "M74 66 L22 92"):
        b.ln(d, '#2E3A1C', 6.4); b.ln(d, '#5A6B3A', 4.2)
    for i in range(7):
        t = i / 6
        x1 = 28 + t * 40; y1 = 69 + t * 20
        b.r(round(x1 - 1, 1), round(y1 - 1.6, 1), 2.2, 3.4, 'brass', '#6B4E14', sw=.3)
        x2 = 68 - t * 40
        b.r(round(x2 - 1, 1), round(y1 - 1.6, 1), 2.2, 3.4, 'brass', '#6B4E14', sw=.3)
    patch(b, '#F2C84B', 15, 72)
    head(b, ears=False)
    helm(b, net=False)
    b.ln("M36 22 L40 17 M52 14 L57 18 M60 26 L64 23 M45 20 L49 16", '#4E5F35', 1.5, .7)
    # machine gun with box magazine and ammo belt
    b.g('translate(50 80) rotate(-8)')
    b.p("M-34 -2 L-22 -4 L-20 4 L-26 8 L-35 6 Z", 'dkm2', KS, .7)
    b.r(-22, -5, 26, 9, 'dkm', KS, rx=1.5, sw=.8)
    b.r(2, -4, 30, 7, 'metal3', KS, rx=3, sw=.8)
    for i in range(6):
        b.c(7 + i * 4.4, -.5, 1, '#262C33')
    b.ln("M32 -.5 L40 -.5", '#15181C', 2.2)
    b.r(38, -2, 4, 3, '#0B0D10', rx=.8, sw=.2)
    b.ln("M30 3.4 L38 12 M30 3.4 L26 12", '#262C33', 1.8)
    b.r(-20, 4, 15, 12, 'crate', GS, rx=1.5, sw=.8)
    b.ln("M-18 7 L-7 7", '#FFFFFF', .7, .4)
    b.p("M-6 -6 L2 -6 L1 -3 L-6 -3 Z", 'dkm2', KS, .5)
    b.ln("M-12 -9 L-12 -5 M-22 -7 L-14 -7", '#15181C', 1.8)
    b.ln("M-18 -4.6 L2 -4.6", '#FFFFFF', .6, .45)
    b.eg()
    hand(b, 36, 76, 3.2); hand(b, 62, 79, 3.2)
    b.ln("M-2 0", '#000000', 0)
    # belt hanging into box (brass rounds)
    for i in range(5):
        b.r(37 - i * 1.4, 70.6 + i * 2.2, 2, 3, 'brass', '#6B4E14', sw=.3)

@icon('tank_crew', '装甲兵', '人员')
def _(b):
    torso(b, 'tankG', GS)
    vcollar(b, 'tankH', GS)
    patch(b, '#E2574C', 16, 71)
    head(b, ears=False)
    # padded tanker helmet with ridges and goggles
    b.p("M28 42 C25 21 34 9 48 9 C62 9 71 21 68 42 L67 38 C61 33 56 32 48 32 C40 32 35 33 29 38 Z", 'tankH', GS, 1.1)
    b.ln("M48 10 L48 31 M39 11 C37 17 37 25 38 32 M57 11 C59 17 59 25 58 32", '#0E120C', 1.2, .8)
    b.ln("M48 10 L48 31", '#6F7A62', .6, .6)
    b.p("M29 33 C38 30 58 30 67 33 L66.6 37 C58 34 38 34 29.4 37 Z", '#222820', GS, .6)
    b.c(41, 27, 4.6, '#2A2E33', '#0F1214', .8); b.c(55, 27, 4.6, '#2A2E33', '#0F1214', .8)
    b.c(41, 27, 3, 'glass', '#25578F', .5); b.c(55, 27, 3, 'glass', '#25578F', .5)
    b.ln("M38.6 25.6 L40.4 24.6 M52.6 25.6 L54.4 24.6", '#FFFFFF', .8, .85)
    b.ln("M36.4 27 L35 27 M59.6 27 L61 27", '#2A2E33', 2)
    # headset cups + boom mic
    for x in (30, 66):
        b.e(x, 42, 4.2, 7, 'dkm2', '#0C0E10', .8)
        b.e(x - 1, 40, 1.6, 3.2, '#6A7480', op=.7)
    b.ln("M30 49 C32 56 38 58 43 55", '#15181C', 1.6)
    b.c(44, 54.6, 2, '#15181C', '#6A7480', .5)
    # hatch ring and hull
    b.p("M2 86 C20 80 76 80 94 86 L94 96 L2 96 Z", 'land', LS, 1)
    b.ln("M6 85 C22 79 74 79 90 85", '#15181C', 5.6, cap='butt')
    b.ln("M6 85 C22 79 74 79 90 85", '#A5B0BD', 3, cap='butt')
    b.ln("M12 83.4 C26 79.4 52 78.6 60 79", '#FFFFFF', .9, .7)
    for x in (16, 30, 44, 58, 72, 82):
        b.c(x, 90.4 + (3 if False else 0), 1, '#3E4C29', op=.9)
    b.hl("M8 87.4 C24 82 40 81 52 81", 1, .5)

@icon('artillery_crew', '炮兵', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#F29A2E')
    head(b, ears=False)
    helm(b, net=False)
    # ear defenders band
    b.ln("M30 34 C30 28 66 28 66 34", '#15181C', 0)
    for x in (30.5, 65.5):
        b.e(x, 42, 3.8, 6.2, '#C0392B', '#6B1D14', .8)
        b.e(x - .8, 40, 1.3, 2.8, '#FFFFFF', op=.5)
    # 155 mm shell cradled across the chest
    b.g('translate(46 76) rotate(-24)')
    b.p("M-30 -4.6 L-14 -5.2 L-14 5.2 L-30 4.6 Z", 'brass', '#6B4E14', .9)
    b.ln("M-30 -2.4 L-14 -2.8 M-30 2.4 L-14 2.8", '#8E6822', .7, .7)
    b.c(-30, 0, 2.2, '#C9A145', '#6B4E14', .5)
    b.r(-14, -6, 5, 12, '#C9A145', '#6B4E14', sw=.6)
    b.r(-9, -6.6, 26, 13.2, 'shell', GS, rx=1, sw=1)
    b.p("M17 -6.6 C25 -6 31 -3 36 0 C31 3 25 6 17 6.6 Z", 'shell', GS, 1)
    b.r(22, -5, 2.8, 10, '#F2C84B', op=.95)
    b.r(-3, -6.6, 3, 13.2, '#F2C84B', op=.95)
    b.p("M34.5 -1.4 L38 0 L34.5 1.4 Z", '#2A2E33')
    b.ln("M-8 -5 L16 -5", '#FFFFFF', .9, .55)
    b.eg()
    p1 = rot(46, 76, -24, 26, 6); p2 = rot(46, 76, -24, -18, 6)
    arm(b, f"M74 92 L{p1[0]} {p1[1]}", '#7E9157', OS, 6.6); hand(b, p1[0], p1[1] - 1, 3.4)
    arm(b, f"M20 92 L{p2[0]} {p2[1]}", '#7E9157', OS, 6.6); hand(b, p2[0], p2[1] - 1, 3.4)

@icon('ad_soldier', '防空兵', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#4DA3E8')
    head(b, ears=False)
    helm(b, net=False)
    b.ln("M36 22 L40 17 M52 14 L57 18 M60 26 L64 23", '#4E5F35', 1.5, .7)
    # man-portable air-defence missile launcher on the shoulder
    b.g('translate(50 68) rotate(-30)')
    b.p("M-34 -6 L-24 -4.6 L-24 4.6 L-34 6 Z", '#2A2E33', KS, .8)
    b.r(-24, -4.8, 46, 9.6, 'adT', GS, rx=1.6, sw=1)
    b.r(-10, -5.2, 3, 10.4, '#F2C84B', op=.95)
    b.r(14, -5.2, 3, 10.4, '#E2574C', op=.95)
    b.p("M22 -4 L25 -4.6 L25 4.6 L22 4 Z", '#2A2E33', KS, .6)
    b.p("M25 -3.8 C31 -3.4 36 -1.6 40 0 C36 1.6 31 3.4 25 3.8 Z", 'white', '#7C8A9B', .8)
    b.c(40, 0, 1.2, '#2A2E33')
    b.r(-6, -9.4, 9, 4.2, 'dkm', KS, rx=1, sw=.7)
    b.c(.5, -7.4, 1.3, 'lens')
    b.p("M-4 4.6 L2 4.6 L1.6 12 L-4.6 12 Z", 'dkm2', KS, .6)
    b.ln("M-22 -3.6 L20 -3.6", '#FFFFFF', .8, .55)
    b.eg()
    p1 = rot(50, 68, -30, 2, 11); p2 = rot(50, 68, -30, 16, 5)
    arm(b, f"M70 92 L{p1[0]} {p1[1]}", '#7E9157', OS, 6.6); hand(b, p1[0], p1[1], 3.2)
    arm(b, f"M22 92 L{p2[0]-8} {p2[1]+12}", '#7E9157', OS, 6.6); hand(b, p2[0], p2[1] + 2, 3.2)

def camo_blobs(b, cols, pts):
    for (x, y, rx, ry, a), c in zip(pts, cols * 4):
        b.e(x, y, rx, ry, c, op=.92, extra=f"transform='rotate({a} {x} {y})'")

WOOD = ['#3C4A26', '#8A7A4A', '#2A331B', '#586B35']
OCEAN = ['#233B52', '#A9C0D0', '#16283A', '#4A6A86']
TORSO_BLOBS = [(32, 78, 6, 3.2, 20), (46, 86, 7, 3, -15), (60, 76, 6, 3, 25), (70, 86, 5, 3, -10),
               (24, 87, 5, 2.8, 15), (52, 72, 4, 2.4, -25), (38, 70, 3.6, 2, 10), (62, 88, 4.4, 2.4, 20)]

@icon('recon_soldier', '侦察兵', '人员')
def _(b):
    torso(b, 'camoB', OS)
    camo_blobs(b, WOOD, TORSO_BLOBS)
    vcollar(b, '#586B35')
    b.ln("M30 66 L66 92", '#2A2E33', 2.6)
    head(b, ears=True)
    # boonie hat with camo
    b.p("M27 28 C27 14 37 7 48 7 C59 7 69 14 69 28 Z", 'camoB', OS, 1)
    camo_blobs(b, WOOD, [(36, 17, 5, 2.6, 30), (50, 12, 5.4, 2.2, -10), (59, 22, 4.6, 2.6, 25), (42, 24, 4, 2, 0), (30, 24, 3, 2, 40)])
    b.p("M14 31 C18 24 32 26 48 26 C64 26 78 24 82 31 C74 38 58 36 48 36 C38 36 22 38 14 31 Z", 'camoB', OS, 1)
    camo_blobs(b, WOOD, [(24, 31, 5, 2, 10), (38, 33, 5, 1.8, 0), (62, 33, 5, 1.8, 0), (74, 31, 5, 2, -10)])
    b.ln("M30 28 C40 26 56 26 66 28", '#2A331B', 1.4)
    b.hl("M33 15 C37 10 42 8.4 47 8", 1, .6)
    # binoculars at the eyes
    b.r(45, 43, 6, 4, 'dkm2', KS, rx=1, sw=.6)
    for x in (39.5, 56.5):
        b.c(x, 44, 8, 'dkm', KS, 1)
        b.c(x, 44, 6, 'lens', '#0B0D10', .7)
        b.c(x - 2, 42, 1.6, '#FFFFFF', op=.8)
    b.ln("M33 38 C36 36.4 44 36.4 46 38 M50 38 C52 36.4 60 36.4 63 38", '#6A7480', 1, .8)
    hand(b, 28, 50, 3.4); hand(b, 68, 50, 3.4)
    arm(b, "M12 92 L26 58", '#74874B', OS, 6.2); hand(b, 28, 52, 3.6)
    arm(b, "M84 92 L70 58", '#74874B', OS, 6.2); hand(b, 68, 52, 3.6)

@icon('sof_operator', '特战队员', '人员')
def _(b):
    torso(b, 'sof', GS)
    # plate carrier with pouches
    b.p("M30 66 C36 64.5 60 64.5 66 66 L70 92 L26 92 Z", 'dkm', '#0E1210', 1)
    for x in (31, 44, 57):
        b.r(x, 78, 9, 10, 'sof', '#0E1210', rx=1.2, sw=.7)
        b.ln(f"M{x+1} {80} L{x+8} {80}", '#6A7480', .6, .7)
    b.r(40, 68, 16, 6, 'sof', '#0E1210', rx=1, sw=.6)
    b.r(18, 72, 8, 5, '#6A7480', '#0E1210', rx=1, sw=.5)
    b.p("M22 70 C28 66 34 65 38 64.5 L36 74 Z", 'sof', '#0E1210', .7)
    b.ln("M12 92 L18 74 M84 92 L78 74", '#1F251E', 5)
    head(b, ears=False)
    # balaclava covering lower face
    b.p("M31 40 C40 44 56 44 65 40 C65 50 59 58 48 59 C37 58 31 50 31 40 Z", 'sof', '#0E1210', .8)
    b.ln("M40 52 C44 54 52 54 56 52", '#0E1210', .8, .8)
    # tactical high-cut helmet with rails and comms
    b.p("M28 38 C26 20 35 8 48 8 C61 8 70 20 68 38 C63 32 56 30 48 30 C40 30 33 32 28 38 Z", 'sofh', '#0E1210', 1.1)
    b.ln("M29 31 C27 24 29 16 36 12 M67 31 C69 24 67 16 60 12", '#6A7480', 1, .8)
    b.r(44, 14, 8, 6, 'dkm2', '#0E1210', rx=1.2, sw=.6)
    b.r(42, 8.6, 12, 3.6, '#6A7480', '#0E1210', rx=1, sw=.5)
    b.hl("M33 20 C36 13 41 10.4 47 10", 1.2, .6)
    for x in (31, 65):
        b.e(x, 42, 3.6, 5.6, 'dkm2', '#0B0D10', .8)
        b.ln(f"M{x} 47.6 L{x} 54", '#15181C', 1.2)
    # night-vision goggles, lit
    b.r(34, 31.4, 28, 12, 'dkm2', '#0B0D10', rx=3, sw=1)
    b.p("M42 32 L54 32 L52 26 L44 26 Z", 'dkm', '#0B0D10', .8)
    for x in (41.4, 54.6):
        b.c(x, 37.6, 5.4, 'rubber', '#0B0D10', .8)
        b.c(x, 37.6, 4, 'nvg', '#0B4A1E', .5)
        b.c(x - 1.3, 36.2, 1.2, '#FFFFFF', op=.9)
    b.ln("M36 33 L60 33", '#7D8590', .7, .6)
    hand(b, 31, 82, 3.2); hand(b, 65, 82, 3.2)
    b.p("M16 92 L18 80 L36 80 L34 92 Z", 'sof', '#0E1210', .8, op=0)

def ghillie(b, outline, n=70):
    import random
    rnd = random.Random(7)
    cols = ['#8D8A4F', '#56642F', '#B1A56B', '#3C4824', '#7A6A3A', '#6B7D3A']
    for i in range(n):
        t = i / n * 2 * math.pi
        # outline of bust: hood + shoulders as a superellipse-ish
        pass

@icon('sniper', '狙击手', '人员')
def _(b):
    import random
    rnd = random.Random(11)
    cols = ['#8D8A4F', '#56642F', '#B1A56B', '#3C4824', '#7A6A3A', '#6B7D3A']
    torso(b, 'ghil', GS)
    # shaggy suit strands around shoulders
    for i in range(22):
        x = 8 + i * 3.9 + rnd.uniform(-1, 1)
        y = 92 - (0 if 18 < x < 78 else 0)
        top = 64 + 28 * (1 - math.sqrt(max(0, 1 - ((x - 48) / 40) ** 2))) * .9 + rnd.uniform(-3, 3)
        b.ln(f"M{x:.1f} {top + 9:.1f} L{x + rnd.uniform(-4, 4):.1f} {top - 1:.1f}", cols[i % 6], 1.5, .9)
    for i in range(5):
        x = 24 + rnd.uniform(0, 48); y = 74 + rnd.uniform(0, 14)
        b.ln(f"M{x:.1f} {y:.1f} L{x + rnd.uniform(-8, 8):.1f} {y + rnd.uniform(3, 8):.1f}", cols[i % 6], 1.4, .8)
    head(b, ears=False)
    # camo face paint
    b.ln("M35 44 L42 47 M61 44 L54 47 M37 50 L43 52 M59 50 L53 52", '#2E3A1C', 1.8, .9)
    b.p("M34 36 C40 33 56 33 62 36 L62 40 C56 38 40 38 34 40 Z", '#2A331B', op=.55)
    b.c(41, 39.5, 1.1, '#15181C'); b.c(55, 39.5, 1.1, '#15181C')
    # ghillie hood
    b.p("M23 46 C19 22 32 6 48 6 C64 6 77 22 73 46 C71 36 64 29 48 28 C32 29 25 36 23 46 Z", 'ghil', GS, 1)
    for i in range(26):
        a = math.radians(200 + i * 7 + rnd.uniform(-2, 2))
        cx, cy = 48, 36
        r1 = 21 + rnd.uniform(-1, 2); r2 = r1 + rnd.uniform(3, 7)
        rx1, ry1 = 24 * r1 / 21, 30 * r1 / 21
        rx2, ry2 = 24 * r2 / 21, 30 * r2 / 21
        x1, y1 = cx + rx1 * math.cos(a), cy + ry1 * math.sin(a)
        x2, y2 = cx + rx2 * math.cos(a + rnd.uniform(-.2, .2)), cy + ry2 * math.sin(a + rnd.uniform(-.2, .2))
        if y1 < 44:
            b.ln(f"M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}", cols[i % 6], 1.6, .95)
    for i in range(9):
        x = 28 + rnd.uniform(0, 40); y = 10 + rnd.uniform(0, 17)
        b.ln(f"M{x:.1f} {y:.1f} L{x + rnd.uniform(-5, 5):.1f} {y + rnd.uniform(3, 7):.1f}", cols[(i + 2) % 6], 1.5, .9)
    # long scoped rifle wrapped with grass
    drawrifle(b, 48, 76, -20, 1.2, scope=True)
    for i in range(7):
        x, y = rot(48, 76, -20, -30 + i * 7, 4)
        b.ln(f"M{x} {y} L{x + rnd.uniform(-3, 3):.1f} {y + rnd.uniform(2, 5):.1f}", cols[i % 6], 1.5, .9)
    p1 = rot(48, 76, -20, 14, 2); p2 = rot(48, 76, -20, -8, 2)
    hand(b, p1[0], p1[1], 3.4); hand(b, p2[0], p2[1], 3.4)

@icon('engineer_soldier', '工兵', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#F29A2E', 16, 72)
    head(b, ears=False)
    helm(b, net=False)
    # goggles pushed up on the helmet
    b.p("M31 30 C40 27 56 27 65 30 L64.6 34.6 C56 32 40 32 31.4 34.6 Z", '#222820', GS, .6)
    b.c(41, 31, 4.6, '#2A2E33', '#0F1214', .8); b.c(55, 31, 4.6, '#2A2E33', '#0F1214', .8)
    b.c(41, 31, 3, 'orV', '#7A3A0A', .5); b.c(55, 31, 3, 'orV', '#7A3A0A', .5)
    b.ln("M39.6 29.6 L41.2 28.6 M53.6 29.6 L55.2 28.6", '#FFFFFF', .8, .85)
    # headphones round the neck
    b.ln("M33 52 C34 62 62 62 63 52", '#15181C', 2)
    # mine detector: search coil, shaft, control box
    b.ln("M72 70 L26 88", '#15181C', 3.8); b.ln("M72 70 L26 88", '#6A7480', 1.8)
    b.e(22, 89, 15, 5, '#1E2328', '#0B0D10', 1)
    b.e(22, 88.2, 13, 3.8, 'metal2', MS, .8)
    b.e(22, 88, 8, 2.2, 'none', '#6A7480', .8)
    b.e(22, 88, 3, 1.2, '#F2A93B')
    b.r(56, 66, 12, 9, 'dkm', KS, rx=1.8, sw=.8, extra="transform='rotate(-22 62 70)'")
    b.c(60, 71, 2.2, 'amber', '#7A4A10', .5); b.c(65, 69, 1.2, GREEN)
    b.ln("M74 68 C80 66 82 72 78 78", '#15181C', 2.4)
    arm(b, "M84 92 L74 74", '#7E9157', OS, 6.6); hand(b, 73, 71, 3.4)
    arm(b, "M16 92 L36 82", '#7E9157', OS, 6.6); hand(b, 40, 80, 3.2)
    b.p("M40 86 L46 86 L45 92 L41 92 Z", '#E2574C', op=0)

@icon('signal_soldier', '通信兵', '人员')
def _(b):
    # backpack radio and whip antennas behind
    b.ln("M80 40 L82 3", '#15181C', 1.6)
    b.c(82, 3.4, 1.6, '#E2574C')
    b.ln("M74 44 L72 14", '#6A7480', 1.2)
    b.r(66, 38, 24, 36, 'dkm', KS, rx=2.5, sw=1)
    b.r(69, 41, 18, 11, 'scr', '#0B1A2C', rx=1.2, sw=.6)
    b.ln("M71 47 L76 44.6 L80 48 L85 43.6", '#7FE0A0', .9)
    for i in range(3):
        b.c(71 + i * 5, 58, 1.8, 'hub', '#0E1013', .6)
    leds(b, [(83, 58, GREEN), (83, 63, AMBER)])
    b.ln("M70 67 L86 67", '#6A7480', .8, .7)
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#3D86D6', 15, 72)
    b.ln("M70 70 C74 80 70 86 64 90", '#15181C', 2.2)
    head(b, ears=False)
    helm(b, net=False)
    # headset with boom microphone
    for x in (30.5, 65.5):
        b.e(x, 43, 4, 6.6, 'dkm2', '#0C0E10', .8)
        b.e(x - .8, 41, 1.4, 3, '#6A7480', op=.7)
    b.ln("M30 49.4 C32 57 39 59 44 56", '#15181C', 1.7)
    b.c(45, 55.6, 2.2, '#15181C', '#6A7480', .5)
    # handset on coiled cord
    b.g('translate(36 80) rotate(-18)')
    b.r(-4, -9, 8, 18, 'dkm', KS, rx=3, sw=.9)
    b.r(-5.4, -11, 10.8, 5, 'dkm2', KS, rx=2, sw=.7)
    b.r(-5.4, 6, 10.8, 5, 'dkm2', KS, rx=2, sw=.7)
    b.ln("M-2 -6 L-2 6", '#6A7480', .8, .7)
    b.eg()
    b.ln("M36 70 C28 66 22 70 26 74 C30 78 20 80 22 84", '#15181C', 1.4)
    hand(b, 36, 82, 3.2)

@icon('ew_soldier', '电子对抗兵', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#8F6FD8', 15, 72)
    # directional (log-periodic) antenna with signal arcs
    b.ln("M70 62 L84 28", '#6A7480', 2)
    b.p("M80 36 L90 28 L88 24 L78 32 Z", 'metal3', MS, .6, op=0)
    for i, (x, y, l) in enumerate([(74, 52, 8), (76.4, 46, 10), (78.8, 40, 12), (81.2, 34, 10), (83.6, 28, 8)]):
        b.ln(f"M{x - l/2:.1f} {y - 1.6:.1f} L{x + l/2:.1f} {y + 1.6:.1f}", '#C9D1DA', 1.6)
        b.ln(f"M{x - l/2:.1f} {y - 1.6:.1f} L{x + l/2:.1f} {y + 1.6:.1f}", '#6A7480', .6)
    b.ln("M84 24 L84 20", '#6A7480', 2)
    for r_, o in ((6, .9), (11, .6), (16, .35)):
        b.ln(f"M{88 - r_ * .3:.1f} {16 - r_ * .9:.1f} A{r_} {r_} 0 0 1 {88 + r_ * .8:.1f} {16 + r_ * .1:.1f}", '#8F6FD8', 1.4, o)
    head(b, ears=False)
    # beret with badge and headset
    b.p("M25 30 C22 14 38 6 54 8 C69 10 73 21 70 31 C62 26 38 26 25 30 Z", 'olivedk', OS, 1)
    b.p("M29 30 C40 25 58 25 67 29 L66 34.6 C58 30 40 30 30 34.6 Z", '#222820', OS, .8)
    b.c(52, 8.4, 1.6, '#2E3A1C')
    b.hl("M30 16 C35 11 41 9 47 8.6", 1.1, .6)
    b.p("M36 18 L41 13 L44 17 L40 22 Z", '#8F6FD8', '#4A3390', .6, op=0)
    b.c(41, 20, 2.8, 'nodeP', '#3C2A78', .5)
    for x in (30.5, 65.5):
        b.e(x, 43, 3.8, 6.2, 'dkm2', '#0C0E10', .8)
    b.ln("M30 48.6 C32 56 39 58 44 55", '#15181C', 1.6)
    b.c(45, 54.6, 2, '#15181C', '#6A7480', .5)
    # handheld detection terminal with spectrum display
    b.p("M22 92 L26 66 L62 66 L66 92 Z", 'dkm', KS, 1)
    b.r(29, 69, 30, 17, 'scr', '#0B1A2C', rx=1.2, sw=.6)
    b.ln("M31 83 L35 80 L38 82 L42 74 L45 83 L48 78 L51 81 L54 72 L57 84", '#7FE0A0', 1)
    b.ln("M30 77 L58 77", '#2F6FB0', .6, .6)
    b.r(31, 70, 7, 2, '#F2A93B', op=.9)
    leds(b, [(62.4, 71, GREEN), (62.8, 76, AMBER)])
    b.hl("M27 67.4 L60 67.4", .9, .55)
    hand(b, 27, 86, 3.4); hand(b, 62, 86, 3.4)

@icon('cbrn_soldier', '防化兵', '人员')
def _(b):
    torso(b, 'cbrn', '#6A7348', 92)
    # protective suit: seams, pockets, yellow hazard chest tag
    b.ln("M48 64 L48 92", '#6A7348', 1, .8)
    b.r(54, 76, 10, 8, 'cbrn', '#6A7348', rx=1, sw=.7)
    b.r(30, 76, 10, 8, 'cbrn', '#6A7348', rx=1, sw=.7)
    b.p("M16 74 L28 70 L30 76 L18 80 Z", 'hivis', '#6A7A08', .6)
    b.ln("M19 76 L28 73", '#2A2E33', .8, .8)
    b.ln("M20 80 L22 70", '#6A7348', .8, .6)
    # hood
    b.p("M24 56 C18 24 30 6 48 6 C66 6 78 24 72 56 C68 62 28 62 24 56 Z", 'cbrn', '#6A7348', 1.1)
    b.p("M26 56 C30 60 66 60 70 56 L72 64 C60 70 36 70 24 64 Z", 'cbrn', '#6A7348', .8)
    b.ln("M30 58 C40 63 56 63 66 58", '#6A7348', .8, .8)
    # gas mask: lenses, seal, filter canister and hose
    b.p("M31 36 C31 30 38 28 48 28 C58 28 65 30 65 36 C65 48 58 58 48 60 C38 58 31 48 31 36 Z", 'rubber', '#0B0D10', 1)
    for x in (41, 55):
        b.c(x, 38, 6.8, 'dkm2', '#0B0D10', .8)
        b.c(x, 38, 5.2, 'lens', '#0B0D10', .6)
        b.c(x - 1.8, 36, 1.5, '#FFFFFF', op=.85)
    b.p("M42 48 L54 48 L52 57 L44 57 Z", 'dkm', '#0B0D10', .7)
    b.ln("M44 51 L52 51 M45 54 L51 54", '#6A7480', .8, .7)
    b.ln("M33 32 C30 40 34 50 40 56", '#0B0D10', 1.4, .8)
    b.hl("M35 31 C38 29.4 42 28.8 46 28.6", 1, .5)
    b.ln("M32 44 C26 50 24 58 28 66", '#15181C', 4.2); b.ln("M32 44 C26 50 24 58 28 66", '#5A626C', 1.6, extra="stroke-dasharray='1.6 1.2'")
    b.r(22, 64, 10, 12, 'dkm', KS, rx=2.4, sw=.9)
    b.ln("M24 68 L30 68 M24 71 L30 71 M24 74 L30 74", '#6A7480', .7, .8)
    b.c(27, 72, 3.2, 'hivis', '#6A7A08', .5, op=0)
    # rubber gloves
    arm(b, "M12 92 L22 84", '#B3BC82', '#6A7348', 6.6)
    arm(b, "M84 92 L74 84", '#B3BC82', '#6A7348', 6.6)
    b.c(22, 84, 4, 'rubber', '#0B0D10', .8); b.c(74, 84, 4, 'rubber', '#0B0D10', .8)

@icon('drone_operator_army', '陆军无人机操作手', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#43C46B', 15, 72)
    # small quadcopter hovering at upper right
    b.sh(80, 30, 11, 2)
    b.ln("M70 18 L90 34 M90 18 L70 34", '#2A2E33', 2.6)
    b.r(75, 22, 10, 7, 'dkm', KS, rx=2.4, sw=.8)
    b.c(80, 29.4, 1.8, 'lens', '#0B0D10', .5)
    for x, y in ((70, 17), (90, 17), (70, 33), (90, 33)):
        b.e(x, y, 6, 2, 'prop', '#8D9BAC', .5)
        b.c(x, y, 1.2, '#2A2E33')
    b.ln("M80 26 L80 29", '#43C46B', 1.2)
    head(b, ears=False)
    # patrol cap with brim, sunglasses and headset
    b.p("M31 30 C30 17 38 11 48 11 C58 11 66 17 65 30 C60 28 54 27.4 48 27.4 C42 27.4 36 28 31 30 Z", 'olive', OS, 1)
    b.ln("M48 11.4 L48 27", '#4E5F35', .8)
    b.p("M30 30 C36 26.4 60 26.4 66 30 C63 34.6 33 34.6 30 30 Z", 'olivedk', OS, .7)
    b.p(star(48, 19.6, 3), '#D9473A')
    b.hl("M35 19 C38 14.6 43 12.6 47 12.4", 1, .7)
    b.p("M33 38 C40 36.4 56 36.4 63 38 L62 42.6 C56 44 52 42.4 48 42 C44 42.4 40 44 34 42.6 Z", 'dkm2', KS, .7)
    b.hl("M36 38.6 L45 38.2", .8, .6)
    for x in (31, 65):
        b.e(x, 44, 3.4, 5.6, 'dkm2', '#0C0E10', .8)
    b.ln("M31 49 C33 56 40 58 44 55.4", '#15181C', 1.4)
    b.c(45, 55, 1.8, '#15181C', '#6A7480', .5)
    # rugged tablet with orange bumpers, video + crosshair
    b.p("M20 74 C20 70 23 68.6 27 68.6 L69 68.6 C73 68.6 76 70 76 74 L76 88 C76 91 73 92 69 92 L27 92 C23 92 20 91 20 88 Z", 'dkm', '#0B0D10', 1)
    b.r(24, 71, 48, 17, 'scr', '#0B1A2C', rx=1.4, sw=.7)
    b.p("M24 82 L36 76 L46 81 L58 74 L72 80 L72 88 L24 88 Z", '#3F7A4A', op=.85)
    b.c(48, 79, 5, 'none', '#FFFFFF', .8, op=.85)
    b.ln("M48 72 L48 75 M48 83 L48 86 M41 79 L44 79 M52 79 L55 79", '#FFFFFF', .8, .85)
    for x, y in ((20, 68.6), (70, 68.6), (20, 86), (70, 86)):
        b.r(x, y, 6, 5.4, 'orV', '#7A3A0A', rx=1.4, sw=.5)
    b.hl("M25 69.8 L68 69.8", .8, .5)
    hand(b, 21, 80, 3.4); hand(b, 75, 80, 3.4)

@icon('marine', '海军陆战队员', '人员')
def _(b):
    torso(b, 'ocB', '#24384C')
    camo_blobs(b, OCEAN, TORSO_BLOBS)
    b.p("M38 64 L48 74 L58 64 Z", '#2A4058', '#24384C', .7)
    head(b, ears=False)
    b.ln("M33 40 C34 52 40 56 48 57 C56 56 62 52 63 40", '#2E3238', 1.6)
    b.p("M27 38 C25 20 35 9 48 9 C61 9 71 20 69 38 C64 32.6 57 30.4 48 30.4 C39 30.4 32 32.6 27 38 Z", 'ocB', '#24384C', 1.1)
    camo_blobs(b, OCEAN, [(38, 18, 4.6, 2.4, 25), (52, 14, 5, 2.2, -15), (60, 24, 4, 2.4, 20), (44, 26, 4, 2, 5), (32, 27, 3, 1.8, 30)])
    b.p("M25.6 38.4 C31 31 38 29 48 29 C58 29 65 31 70.4 38.4 C65 34.6 57 33 48 33 C39 33 31 34.6 25.6 38.4 Z", '#2A4058', '#24384C', .8)
    # goggles
    b.p("M33 30 C40 27.6 56 27.6 63 30 L62.6 34.6 C56 32.4 40 32.4 33.4 34.6 Z", '#222A33', '#0B0D10', .6)
    b.c(41, 31, 4, '#2A2E33', '#0F1214', .8); b.c(55, 31, 4, '#2A2E33', '#0F1214', .8)
    b.c(41, 31, 2.6, 'glass', '#25578F', .5); b.c(55, 31, 2.6, 'glass', '#25578F', .5)
    b.hl("M31 22 C34 15 40 11.4 47 11", 1.3, .8)
    # inflatable life vest collar with reflective strips and whistle
    b.p("M16 80 C14 70 24 62 36 62 L42 64 L42 74 L30 80 L28 92 L12 92 Z", 'orV', '#7A3A0A', 1)
    b.p("M80 80 C82 70 72 62 60 62 L54 64 L54 74 L66 80 L68 92 L84 92 Z", 'orV', '#7A3A0A', 1)
    b.p("M40 62 L56 62 L56 66 C50 70 46 70 40 66 Z", 'orV', '#7A3A0A', .8)
    for d in ("M20 78 L18 90", "M76 78 L78 90"):
        b.ln(d, '#F2F4F6', 2.2, .9)
    b.ln("M26 70 L40 66 M70 70 L56 66", '#F2F4F6', 1.4, .8)
    b.hl("M20 72 C23 67 29 64 35 63.4", 1.2, .55)
    b.c(60, 78, 2.2, '#C9D1DA', '#6A7480', .5)
    b.ln("M54 66 L60 77", '#C9D1DA', .7)
    patch(b, '#F2C84B', 20, 80, 0, 0) if False else None
    # anchor emblem on chest
    b.ln("M48 80 L48 88 M44 82 L52 82 M43.6 86 C44.4 89.6 51.6 89.6 52.4 86", '#F1D893', 1.2)
    b.c(48, 79, 1.4, 'none', '#F1D893', .8)

@icon('paratrooper', '空降兵', '人员')
def _(b):
    # canopy fragment with suspension lines
    b.p("M2 30 C6 10 28 -1 48 -1 C68 -1 90 10 94 30 C88 24 80 22 72 24 C66 20 58 18 48 18 C38 18 30 20 24 24 C16 22 8 24 2 30 Z", 'canW', '#97A3B1', 1)
    for d in ("M48 -.5 L48 18", "M32 1.4 C30 8 28 15 25 23", "M64 1.4 C66 8 68 15 71 23", "M16 8 C14 14 11 21 6 27", "M80 8 C82 14 85 21 90 27"):
        pass
    b.p("M48 -1 C38 0 30 8 28 20 L24 24 C26 12 34 2 48 -1 Z", 'canR', op=.95)
    b.p("M48 -1 C58 0 66 8 68 20 L72 24 C70 12 62 2 48 -1 Z", 'canR', op=.95)
    b.p("M14 10 C12 16 8 22 4 28 C8 24 8 18 14 10 Z M82 10 C84 16 88 22 92 28 C88 24 88 18 82 10 Z", 'canR', op=.95)
    b.ln("M25 23 L33 66 M71 23 L63 66 M7 28 L24 70 M89 28 L72 70", '#8D9BAC', .9, .9)
    b.hl("M10 20 C16 10 30 3 48 1.6", 1.2, .7)
    # body at slightly reduced scale
    b.g('translate(7.2 11.5) scale(.85)')
    torso(b, 'olive', OS)
    vcollar(b)
    # harness straps, chest buckle, reserve pack
    b.ln("M30 65 L38 92 M66 65 L58 92", '#2E3238', 6.4); b.ln("M30 65 L38 92 M66 65 L58 92", '#5A6B3A', 4.2)
    b.r(38, 76, 20, 14, '#5F6B4A', GS, rx=1.6, sw=.9)
    b.ln("M42 76 L42 90 M54 76 L54 90", '#2E3A1C', .8, .8)
    b.r(44, 71, 8, 4, 'metal2', MS, rx=1, sw=.7)
    b.c(30, 70, 2.6, 'metal', MS, .7); b.c(66, 70, 2.6, 'metal', MS, .7)
    b.p("M12 74 L22 71 L24 78 L14 81 Z", '#4DA3E8', '#24509A', .6)
    head(b, ears=False)
    # round airborne helmet with deep chin cup
    b.ln("M32 44 C34 56 40 60 48 61 C56 60 62 56 64 44", '#15181C', 1.8)
    b.p("M26 40 C24 20 34 8 48 8 C62 8 72 20 70 40 C70 44 67 46 65 46 L64 38 C58 34 38 34 32 38 L31 46 C29 46 26 44 26 40 Z", 'olive', OS, 1.1)
    b.p("M26 36 C32 31 64 31 70 36 L70 41 C64 36.6 32 36.6 26 41 Z", 'olivedk', OS, .8)
    b.hl("M31 22 C34 14 40 10.6 47 10.2", 1.3, .8)
    b.c(48, 20, 3, 'gold', '#7A5C18', .6)
    b.eg()

@icon('af_ground_crew', '空军地勤', '人员')
def _(b):
    torso(b, 'af', '#3A4A5C')
    b.p("M38 64 L48 74 L58 64 Z", '#5D6E82', '#3A4A5C', .7)
    # hi-vis reflective vest
    b.p("M28 66 L38 64 L48 76 L58 64 L68 66 L70 92 L26 92 Z", 'hivis', '#6A7A08', 1)
    b.ln("M32 74 L64 74 M31 84 L65 84", '#E6EAF0', 3)
    b.ln("M32 74 L64 74 M31 84 L65 84", '#9AA4B0', .6, .7)
    b.ln("M38 64.6 L36 92 M58 64.6 L60 92", '#E6EAF0', 2.4)
    b.hl("M31 69 L37 66", 1, .6)
    head(b); hair(b)
    # ear defenders
    b.ln("M31 36 C31 14 65 14 65 36", '#2A2E33', 3.4)
    b.ln("M31 36 C31 14 65 14 65 36", '#6A7480', 1.2)
    for x in (30.4, 65.6):
        b.e(x, 42, 5, 8, 'orV', '#7A3A0A', .9)
        b.e(x - 1, 39.4, 1.6, 3.4, '#FFFFFF', op=.55)
    # marshalling wands
    arm(b, "M12 92 L14 64", '#7489A0', '#3A4A5C', 6.2); hand(b, 14, 61, 3.4)
    arm(b, "M84 92 L82 64", '#7489A0', '#3A4A5C', 6.2); hand(b, 82, 61, 3.4)
    for x, y in ((14, 60), (82, 60)):
        b.ln(f"M{x} {y} L{x + (-4 if x < 48 else 4)} {y - 22}", '#B83A12', 5.6, .5)
        b.ln(f"M{x} {y} L{x + (-4 if x < 48 else 4)} {y - 22}", '#F27020', 3.8)
        b.ln(f"M{x} {y - 2} L{x + (-4 if x < 48 else 4)} {y - 22}", '#FFE2B0', 1.2, .9)
        b.c(x + (-4 if x < 48 else 4), y - 22, 2.4, '#FFF2D6', '#F29A2E', .8)

@icon('rocket_force', '火箭军操作号手', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#D9473A', 15, 72)
    head(b, ears=False)
    # side cap with red piping, headset
    b.p("M29 34 C28 20 34 11 40 9 C44 13 52 13 56 9 C62 11 68 20 67 34 C58 30 38 30 29 34 Z", 'olive', OS, 1)
    b.ln("M30 33 C38 29.4 58 29.4 66 33", '#D9473A', 1.6)
    b.ln("M40 10 C44 18 52 18 56 10", '#2E3A1C', .9, .8)
    b.p(star(48, 24, 3), '#D9473A')
    b.hl("M33 22 C34 17 37 13 41 11", 1.1, .6)
    for x in (30.5, 65.5):
        b.e(x, 42, 3.8, 6.2, 'dkm2', '#0C0E10', .8)
    b.ln("M30 48 C32 56 39 58 44 55", '#15181C', 1.5)
    b.c(45, 54.6, 1.9, '#15181C', '#6A7480', .5)
    # launch console
    b.p("M6 92 L12 70 L84 70 L90 92 Z", 'dkm', '#0B0D10', 1)
    b.p("M12 70 L16 64 L80 64 L84 70 Z", 'metal3', MS, .8)
    b.r(16, 72, 26, 14, 'scr', '#0B1A2C', rx=1.2, sw=.7)
    b.p("M29 74 L31.2 76 L31.2 82 L26.8 82 L26.8 76 Z", '#FFFFFF')
    b.p("M26.8 82 L24.8 84.4 L26.8 83.6 Z M31.2 82 L33.2 84.4 L31.2 83.6 Z", '#E2574C')
    b.ln("M19 84 L22 84 M36 74 L39 74 M36 77 L39 77", '#7FE0A0', .8, .8)
    b.r(46, 72, 20, 14, 'dkm2', '#0B0D10', rx=1.2, sw=.7)
    for i in range(4):
        for j in range(2):
            b.c(50 + i * 4.6, 76 + j * 6, 1.4, [GREEN, AMBER, 'glass', GREEN][i] if j == 0 else ['#6A7480', '#6A7480', REDL, '#6A7480'][i])
    b.r(70, 72, 11, 14, '#8E3129', '#4A1612', rx=1.2, sw=.7)
    b.c(75.5, 78, 3.6, 'red', '#4A1612', .6)
    b.c(75.5, 77.4, 2.2, '#F28A7E', op=.7)
    b.ln("M72 84 L79 84", '#F2C84B', .9)
    b.hl("M14 71 L82 71", .8, .5)
    hand(b, 28, 70, 3.2); hand(b, 68, 70, 3.2)

@icon('logistics_soldier', '后勤保障兵', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    patch(b, '#F29A2E', 15, 72)
    head(b, ears=False)
    # helmet with reflective band
    helm(b, net=False)
    b.ln("M29 33 C38 29.6 58 29.6 67 33", '#E6EAF0', 1.8)
    b.ln("M29 33 C38 29.6 58 29.6 67 33", '#9AA4B0', .5, .6)
    # stacked supply crates
    b.r(18, 80, 28, 12, 'crate', GS, rx=1.6, sw=1)
    b.r(50, 80, 28, 12, 'wood', '#4A361C', rx=1.6, sw=1)
    b.r(30, 62, 36, 18, 'crate', GS, rx=1.8, sw=1)
    b.r(30, 62, 36, 18, 'none', '#F2C84B', rx=1.8, sw=.0)
    b.ln("M30 66 L66 66", '#2E3A1C', 1, .7)
    b.ln("M34 80 L34 62 M62 80 L62 62", '#2E3A1C', 1, .6)
    b.r(37, 69, 22, 8, '#E6EAF0', '#6A7480', rx=1, sw=.6)
    b.p("M45 70.4 L51 70.4 L51 72.4 L53 72.4 L53 75 L51 75 L51 76 L45 76 L45 75 L43 75 L43 72.4 L45 72.4 Z", '#D9473A', op=.9)
    b.hl("M32 63.4 L64 63.4", .9, .55)
    b.ln("M20 83 L44 83", '#2E3A1C', 1, .7)
    b.r(54, 84, 20, 3, '#F2F4F6', '#6A7480', rx=1, sw=.5, op=.9)
    b.ln("M54 90 L74 90", '#4A361C', .9, .6)
    hand(b, 26, 80, 3.4); hand(b, 70, 80, 3.4)
    arm(b, "M14 92 L26 82", '#7E9157', OS, 6.2); arm(b, "M82 92 L70 82", '#7E9157', OS, 6.2)
    hand(b, 26, 80, 3.4); hand(b, 70, 80, 3.4)

@icon('mp_soldier', '警卫兵', '人员')
def _(b):
    torso(b, 'olive', OS)
    vcollar(b)
    # white cross belt and armband
    b.ln("M70 66 L36 92", '#E6EAF0', 5); b.ln("M70 66 L36 92", '#FFFFFF', 1.2, .8)
    b.r(12, 74, 14, 10, '#E6EAF0', '#6A7480', rx=1, sw=.7)
    b.r(12, 76.4, 14, 3.4, '#D9473A')
    b.ln("M13 82 L25 82", '#6A7480', .7)
    b.ln("M10 90 L90 90", '#E6EAF0', 3.4, .0)
    head(b, ears=False)
    b.ln("M33 40 C34 52 40 56 48 57 C56 56 62 52 63 40", '#2E3238', 1.6)
    # white MP helmet with red-white stripe
    b.p("M27 38 C25 20 35 9 48 9 C61 9 71 20 69 38 C64 32.6 57 30.4 48 30.4 C39 30.4 32 32.6 27 38 Z", 'white', '#7C8A9B', 1.1)
    b.p("M25.6 38.4 C31 31 38 29 48 29 C58 29 65 31 70.4 38.4 C65 34.6 57 33 48 33 C39 33 31 34.6 25.6 38.4 Z", 'whitedk', '#7C8A9B', .8)
    b.ln("M48 9.4 L48 29", '#D9473A', 3.4, cap='butt')
    b.ln("M48 9.4 L48 29", '#FFFFFF', .8, .6, cap='butt')
    b.p("M42 17 L54 17 L54 24 C54 27 42 27 42 24 Z", '#D9473A', '#7A2219', .6, op=0)
    b.hl("M31 24 C34 15 40 11.4 47 11", 1.3, .9)
    # baton
    b.g('translate(72 66) rotate(-35)')
    b.r(-3, -22, 6, 44, 'dkm2', KS, rx=2.8, sw=.9)
    b.r(-3, -22, 6, 7, '#FFFFFF', '#8F9BA9', rx=2.8, sw=.7)
    b.ln("M-1 -12 L-1 16", '#6A7480', .8, .7)
    b.eg()
    b.ln("M86 74 L66 80", '#15181C', 0)
    arm(b, "M84 92 L72 70", '#7E9157', OS, 6.4); hand(b, 71, 67, 3.4)
    arm(b, "M16 92 L30 82", '#7E9157', OS, 6.4)
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)

@icon('cyber_operator', '网络空间作战员', '人员')
def _(b):
    # triple monitors with scrolling code
    for x, w, h, y in ((4, 28, 34, 22), (34, 28, 40, 8), (64, 28, 34, 22)):
        b.r(x, y, w, h, 'dkm2', '#0B0D10', rx=2, sw=1)
        b.r(x + 2, y + 2, w - 4, h - 4, 'scr', '#06121F', rx=1, sw=.5)
    cols = ['#7FE0A0', '#8FD0FF', '#F2A93B', '#7FE0A0']
    for i, (x, y) in enumerate(((7, 26), (37, 12), (67, 26))):
        for j in range(5 if i == 1 else 4):
            b.ln(f"M{x} {y + j * 6} L{x + [14, 18, 10, 20, 12][(j + i) % 5]} {y + j * 6}", cols[(i + j) % 4], 1.4, .9)
    b.ln("M4 56 L32 56", '#06121F', 0)
    torso(b, 'hood', '#080B10')
    # hoodie drawstrings, cyan accents
    b.p("M36 64 C40 70 56 70 60 64 L62 74 C54 80 42 80 34 74 Z", '#10151D', '#080B10', .8)
    b.ln("M44 72 L43 84 M52 72 L53 84", '#8FD0FF', 1, .8)
    b.ln("M12 92 C12 74 26 64 48 64", '#8FD0FF', .8, .6)
    b.ln("M84 92 C84 74 70 64 48 64", '#8FD0FF', .8, .6)
    head(b); hair(b)
    # hood back + gaming headset
    b.ln("M31 36 C31 14 65 14 65 36", '#15181C', 3.6)
    b.ln("M31 36 C31 14 65 14 65 36", '#4A525C', 1.2)
    for x in (30.4, 65.6):
        b.e(x, 42, 4.6, 7.4, 'dkm2', '#0B0D10', .8)
        b.e(x, 42, 2.4, 4.6, '#8FD0FF', op=.9)
    b.ln("M30 49 C32 57 40 59 45 56", '#15181C', 1.6)
    b.c(46, 55.6, 2, '#15181C', '#8FD0FF', .6)
    # keyboard with glowing keys
    b.p("M10 92 L18 78 L78 78 L86 92 Z", 'dkm', '#0B0D10', 1)
    for r_ in range(3):
        for c_ in range(8):
            x = 25 + c_ * 6.2 - r_ * 1.2; y = 80 + r_ * 3.8
            b.r(round(x, 1), y, 4.6, 2.4, '#8FD0FF' if (c_ + r_) % 3 else '#3D86D6', rx=.6, op=.9)
    hand(b, 30, 80, 3.6); hand(b, 66, 80, 3.6)
    b.hl("M20 78.6 L76 78.6", .7, .5)


KEYS = """inf_rifleman inf_mg tank_crew artillery_crew ad_soldier recon_soldier sof_operator sniper engineer_soldier signal_soldier
ew_soldier cbrn_soldier drone_operator_army marine paratrooper af_ground_crew rocket_force logistics_soldier mp_soldier cyber_operator""".split()

if __name__ == '__main__':
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    new = [k for k in byk if k in KEYS]
    assert set(KEYS) <= set(byk), set(KEYS) - set(byk)
    import glob
    old = set()
    for f in ['icons.js'] + [x.split('/')[-1] for x in glob.glob('/home/claude/drawtool/icons_[a-f].js')]:
        old |= set(re.findall(r"key: '([a-z_0-9]+)'", open('/home/claude/drawtool/' + f, encoding='utf-8').read()))
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
    open('/home/claude/drawtool/icons_g.js', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), sorted(SZ)[-8:])
