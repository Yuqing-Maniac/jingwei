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


def _truck_base(b, wheels, cab_x=68, cab_top=44, chassis=(6, 60, 84)):
    x, y, w = chassis
    b.sh(48, 82, 43, 4.2)
    b.r(x, y, w, 6, 'landdk', LS, sw=1)
    cx = cab_x
    b.p(f"M{cx} 66 L{cx} {cab_top} L{cx+14} {cab_top} L{cx+20} {cab_top+10} L{cx+22} {cab_top+12} L{cx+22} 66 Z", 'land', LS)
    b.p(f"M{cx+13.5} {cab_top+2} L{cx+15.5} {cab_top+2} L{cx+19.6} {cab_top+10} L{cx+13.5} {cab_top+10} Z", 'canopy', '#1B2D40', .6)
    b.r(cx + 4, cab_top + 2.5, 7, 7, 'canopy', rx=.8)
    glint(b, cx + 15.5, cab_top + 4.5, .8, 1.6)
    b.r(cx + 19, 60, 4.5, 3.5, '#F2E6B0', rx=.8, op=.9)
    b.hl(f"M{cx+1} {cab_top+1.2} L{cx+13.6} {cab_top+1.2}")
    for wx in wheels: wheel(b, wx, 71, 7.5)

# =====================================================================
#  icons_gen_e.py — batch E : 反无人 detection / C2 family
#  (helpers above copied from icons_gen_b.py / icons_gen_a.py)
# =====================================================================
GR.update({
    'fenceG': ('l', ('0', '0', '0', '1'), ((0, '#27C6B4', .62), (1, '#27C6B4', .14))),
    'detG': ('r', None, ((0, '#CFFBF3'), (.5, '#27C6B4', .7), (1, '#27C6B4', 0))),
    'wedge': ('l', ('0', '0', '1', '0'), ((0, '#27C6B4', .6), (1, '#27C6B4', .08))),
    'mic': ('r', ('0.35', '0.3', '0.75'), ((0, '#8A939D'), (.55, '#3B424B'), (1, '#171B20'))),
    'conS': L(V, (0, '#A9BACB'), (1, '#4A5B6E')),
})
DET = '#1FB8A6'     # detection accent (teal-cyan)
DETL = '#7FE9D8'

def dwav(b, cx, cy, rs, a0, a1, w=1.6, op=.9):
    wav(b, cx, cy, rs, a0, a1, DET, w, op)

def wav(b, cx, cy, rs, a0, a1, col, w=1.6, op=.85):
    for i, r in enumerate(rs):
        x1, y1 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x2, y2 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        b.ln(f"M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}", col, w, round(op * (1 - i * .22), 2))

def bil(P, u, v):
    """P = (p00,p10,p11,p01) quad; u along p00->p10, v along p00->p01"""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = P
    x = (1-u)*(1-v)*x0 + u*(1-v)*x1 + u*v*x2 + (1-u)*v*x3
    y = (1-u)*(1-v)*y0 + u*(1-v)*y1 + u*v*y2 + (1-u)*v*y3
    return x, y

def qpath(pts):
    return 'M' + ' L'.join(f"{x:.1f} {y:.1f}" for x, y in pts) + ' Z'

def array_face(b, P, nu, nv, u0=.1, u1=.9, v0=.1, v1=.9, dark=0):
    sub = [bil(P, u0, v0), bil(P, u1, v0), bil(P, u1, v1), bil(P, u0, v1)]
    b.p(qpath(sub), 'array', '#1E3550', .8)
    d = ''
    for i in range(1, nu):
        u = u0 + (u1 - u0) * i / nu
        a, c = bil(P, u, v0), bil(P, u, v1)
        d += f"M{a[0]:.1f} {a[1]:.1f} L{c[0]:.1f} {c[1]:.1f} "
    for j in range(1, nv):
        v = v0 + (v1 - v0) * j / nv
        a, c = bil(P, u0, v), bil(P, u1, v)
        d += f"M{a[0]:.1f} {a[1]:.1f} L{c[0]:.1f} {c[1]:.1f} "
    b.ln(d, '#9CC2EA', .5, .6)
    if dark: b.p(qpath(sub), '#000000', op=dark)

def dot_face(b, P, rows, u0=.1, u1=.9, v0=.1, v1=.9, dark=0, pitch=3.3):
    sub = [bil(P, u0, v0), bil(P, u1, v0), bil(P, u1, v1), bil(P, u0, v1)]
    b.p(qpath(sub), 'array', '#1E3550', .8)
    d = ''
    for j in range(rows):
        v = v0 + (v1 - v0) * (j + .5) / rows
        a, c = bil(P, u0 + .05, v), bil(P, u1 - .05, v)
        d += f"M{a[0]:.1f} {a[1]:.1f} L{c[0]:.1f} {c[1]:.1f} "
    b.ln(d, '#B8D8F4', 1.7, .85, extra=f"stroke-dasharray='.1 {pitch}'")
    if dark: b.p(qpath(sub), '#000000', op=dark)

def mini_drone(b, cx, cy, s=1.0, col='#2E3640', ring=None):
    if ring:
        b.c(cx, cy, 9 * s, 'none', ring, 1, op=.9, extra="stroke-dasharray='2 1.6'")
    d = 6 * s
    b.ln(f"M{cx-d:.1f} {cy-d*.6:.1f} L{cx+d:.1f} {cy+d*.6:.1f} M{cx-d:.1f} {cy+d*.6:.1f} L{cx+d:.1f} {cy-d*.6:.1f}", col, 1.6 * s)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.e(round(cx + sx * d, 1), round(cy + sy * d * .6 - 1 * s, 1), round(3.2 * s, 1), round(1.1 * s, 1), 'prop', '#8D9BAC' if s > .8 else None, .5)
    b.e(cx, cy, 3 * s, 2 * s, col)
    b.c(cx, round(cy + 1.4 * s, 1), .7 * s, DETL)

K = '反无人'

# ---------------------------------------------------------------- 1
@icon('cuas_radar_lowalt', '低空监视雷达', K)
def _(b):
    b.sh(48, 89, 30, 3.2)
    b.ln("M48 60 L22 88 M48 60 L74 88 M48 60 L48 89", '#3A4048', 2.8)
    for x in (22, 74, 48): b.e(x, 89, 3.2, 1.2, '#1E2328')
    b.r(45, 44, 6, 18, 'cylM', MS)
    b.r(37, 54, 22, 9, 'metal3', MS, rx=2)
    b.r(40, 55.4, 6, 1.4, '#FFFFFF', op=.5)
    leds(b, [(54, 59, GREEN)])
    b.ln("M20 62 A28 6 0 0 0 76 62", DET, 1.6, .95)
    arrowhead(b, 76, 62, -75, DET, 3.6)
    # lattice reflector slab
    b.p("M22 17 L60 11 L60 47 L22 53 Z", 'metal', MS)
    b.p("M60 11 L68 15 L68 51 L60 47 Z", 'metal3', MS)
    b.p("M22 17 L60 11 L68 15 L30 21 Z", 'metal2', MS)
    d = ''
    for i in range(1, 6):
        t = i / 6
        d += f"M{22+38*t:.1f} {17-6*t:.1f} L{22+38*t:.1f} {53-6*t:.1f} "
    for j in range(1, 6):
        t = j / 6
        d += f"M22 {17+36*t:.1f} L60 {11+36*t:.1f} "
    b.ln(d, '#7D8996', .8, .9)
    b.r(36, 3, 18, 6, 'dkm', DS, rx=1.5, sw=.8)
    b.ln("M45 9 L44 14 M52 8 L51 13", '#5E6A78', 1.1)
    b.hl("M22 16.4 L60 10.4 L67.4 14", .9, .9)
    dwav(b, 70, 30, [8, 15, 22], -42, 42)

# ---------------------------------------------------------------- 2
@icon('cuas_radar_4face', '四面阵相控阵雷达', K)
def _(b):
    L_, N_, R_, F_ = (24, 30), (46, 38), (68, 30), (46, 22)
    Lb, Nb, Rb = (8, 66), (46, 80), (84, 66)
    b.sh(46, 88, 42, 4)
    b.p("M6 68 L46 84 L86 68 L86 74 L46 90 L6 74 Z", 'metal3', MS, .9)
    b.p("M6 68 L46 52 L86 68 L46 84 Z", 'metal2', MS, .9)
    b.p(qpath([F_, R_, N_, L_]), 'dkm', DS)
    b.p(qpath([L_, N_, Nb, Lb]), 'metal2', MS)
    b.p(qpath([N_, R_, Rb, Nb]), 'metal3', MS)
    Pl, Pr = (L_, N_, Nb, Lb), (N_, R_, Rb, Nb)
    dot_face(b, Pl, 8, .1, .9, .08, .92)
    dot_face(b, Pr, 8, .1, .9, .08, .92, dark=.22)
    b.p(qpath([bil(Pl, .1, .08), bil(Pl, .45, .08), bil(Pl, .28, .92), bil(Pl, .1, .92)]), '#FFFFFF', op=.14)
    b.ln("M46 39 L46 79", '#E4EAF0', 1, .8)
    b.hl("M25 29.4 L46 21.4 L67 29.4", .9, .8)
    b.c(46, 30, 2.2, DET, '#0E6D62', .6); b.c(45.4, 29.4, .6, '#FFFFFF')
    dwav(b, 14, 44, [7, 13], 150, 210, 1.5)
    dwav(b, 78, 44, [7, 13], -30, 30, 1.5)

# ---------------------------------------------------------------- 3
@icon('cuas_radar_vehicle', '车载探测雷达', K)
def _(b):
    _truck_base(b, (18, 33, 77), cab_x=66, cab_top=46)
    b.r(6, 56, 56, 4, 'landdk', LS, sw=.8)
    b.r(34, 40, 8, 17, 'landdk', LS, sw=.8)
    b.p("M14 44 L58 44 L58 50 L14 50 Z", 'landdk', LS, .9)
    # elevated panel
    b.r(36.5, 30, 3.5, 12, 'cylM', MS, sw=.7)
    b.p("M20 9 L52 5 L52 33 L20 37 Z", 'metal2', MS)
    b.p("M52 5 L59 9 L59 37 L52 33 Z", 'metal3', MS)
    array_face(b, ((20, 9), (52, 5), (52, 33), (20, 37)), 6, 4, .06, .94, .1, .9)
    b.p("M21 10 L34 8 L34 36 L21 37 Z", '#FFFFFF', op=.14)
    b.hl("M20 8.4 L52 4.4 L58.6 8.2", .9, .9)
    leds(b, [(56, 42, GREEN), (60, 42, AMBER)])
    dwav(b, 66, 24, [9, 16, 23], -45, 40)

# ---------------------------------------------------------------- 4
@icon('cuas_passive', '无源频谱侦测站', K)
def _(b):
    b.sh(48, 89, 38, 3.4)
    b.ln("M48 30 L88 86 M48 30 L58 90", '#7D8996', .9, .9)
    b.e(88, 86.5, 2.6, 1, '#3A4048'); b.e(58, 90, 2.6, 1, '#3A4048')
    b.e(48, 85, 12, 3.4, 'metal3', MS, .9)
    b.r(45.5, 14, 5, 71, 'cylM', MS, sw=.9)
    # discone on top
    b.p("M48 8 L58 22 L38 22 Z", 'metal', MS, .9)
    b.e(48, 8, 6, 1.8, 'metal2', MS, .8)
    b.ln("M48 3 L48 8", '#5E6A78', 1.4); b.c(48, 3, 1.2, '#5E6A78')
    b.e(48, 22, 10, 2.2, 'dkm2', DS, .8)
    # tier 2 crossarm with tall dipoles
    b.ln("M26 36 L70 36", '#5E6A78', 2.2)
    for x, h in ((28, 18), (68, 18), (38, 11), (58, 11)):
        b.ln(f"M{x} 36 L{x} {36-h}", '#2A2E33', 1.9); b.ln(f"M{x-.4} 36 L{x-.4} {36-h}", '#C9D1DA', .6)
        b.c(x, 36 - h - 1, 1.3, '#5E6A78')
    # tier 3 wide crossarm, short whips
    b.ln("M20 54 L76 54", '#5E6A78', 2.4)
    for x in (22, 34, 62, 74):
        b.ln(f"M{x} 54 L{x} 44", '#2A2E33', 1.8)
        b.c(x, 44, 1.1, '#5E6A78')
    b.ln("M20 54 L28 62 M76 54 L68 62", '#7D8996', 1.1)
    # equipment case
    box3d(b, 8, 68, 28, 14, 7, 5, 'dkm', 'metal2', 'dkm2', DS, 1.6)
    b.r(11, 71, 12, 8, 'scr', '#0B1A2C', rx=.8, sw=.5)
    b.ln("M12 77 L15 75 L17 77 L19 72.6 L22 76.6", '#7FE0A0', .8)
    leds(b, [(27, 73, GREEN), (27, 77, AMBER)])
    b.ln("M36 74 C42 72 44 78 46 78", '#2A2E33', 1.4)
    dwav(b, 6, 18, [8, 15, 22], -28, 28, 1.5)
    dwav(b, 92, 28, [8, 15, 22], 152, 208, 1.5)

# ---------------------------------------------------------------- 5
@icon('cuas_df', '无线电测向站', K)
def _(b):
    cx, cy, rx, ry = 48, 74, 38, 11
    b.sh(48, 86, 40, 4)
    b.e(cx, cy + 3, rx + 2, ry + 2, 'metal3', MS, 1)
    b.e(cx, cy, rx + 2, ry + 2, 'metal2', MS, 1)
    b.e(cx, cy, rx - 3, ry - 2, 'metal', '#8794A3', .6)
    rods = []
    for k in range(8):
        a = math.radians(22.5 + k * 45)
        rods.append((cx + (rx - 6) * math.cos(a), cy + (ry - 3) * math.sin(a), math.sin(a)))
    def rod(x, y):
        b.ln(f"M{x:.1f} {y:.1f} L{x:.1f} {y-30:.1f}", '#2A2E33', 2.2)
        b.ln(f"M{x-.5:.1f} {y-.5:.1f} L{x-.5:.1f} {y-29:.1f}", '#C9D1DA', .7)
        b.c(round(x, 1), round(y - 31, 1), 1.5, '#8D9BAC', '#3A4048', .5)
        b.e(round(x, 1), round(y, 1), 2.2, .9, '#1E2328')
    for x, y, s in rods:
        if s < 0: rod(x, y)
    b.r(45, 18, 6, 56, 'cylM', MS, sw=.9)
    b.e(48, 18, 6, 2, 'metal', MS, .8)
    b.ln("M48 18 L48 8", '#5E6A78', 1.6); b.c(48, 7, 1.6, '#8D9BAC', '#3A4048', .5)
    b.ln("M36 22 L60 22", '#5E6A78', 1.6)
    # bearing wedge on plate
    a0, a1 = math.radians(-45), math.radians(18)
    p0 = (cx + 42 * math.cos(a0), cy + 12 * math.sin(a0)); p1 = (cx + 42 * math.cos(a1), cy + 12 * math.sin(a1))
    b.p(f"M{cx} {cy} L{p0[0]:.1f} {p0[1]:.1f} A42 12 0 0 1 {p1[0]:.1f} {p1[1]:.1f} Z", 'wedge', DET, .8)
    b.ln(f"M{cx} {cy} L{(p0[0]+p1[0])/2+2:.1f} {(p0[1]+p1[1])/2:.1f}", DET, 1.4, .95)
    arrowhead(b, (p0[0] + p1[0]) / 2 + 3, (p0[1] + p1[1]) / 2, -12, DET, 3.8)
    for x, y, s in rods:
        if s >= 0: rod(x, y)
    b.hl("M12 70 Q20 62 34 62", .9, .7)

# ---------------------------------------------------------------- 6
@icon('cuas_eo', '光电搜索跟踪转塔', K)
def _(b):
    b.sh(48, 89, 34, 3.6)
    b.e(48, 85, 32, 5, 'metal3', MS)
    b.r(30, 70, 36, 14, 'cylM', MS, rx=2)
    b.ln("M32 76 L64 76", '#7D8996', .8, .7)
    leds(b, [(60, 80, GREEN)])
    # yoke
    b.p("M12 34 L25 34 L25 62 L71 62 L71 34 L84 34 L84 66 Q84 72 78 72 L18 72 Q12 72 12 66 Z", 'metal3', MS)
    b.p("M13.5 35.5 L23.5 35.5 L23.5 62 L13.5 64 Z", '#FFFFFF', op=.18)
    b.c(18.5, 46, 4, 'hub', '#1D2228', .8); b.c(77.5, 46, 4, 'hub', '#1D2228', .8)
    # sensor head
    b.r(24, 24, 48, 38, 'metal', MS, rx=7)
    b.p("M24 31 Q24 24 31 24 L65 24 Q72 24 72 31 L72 33 L24 33 Z", 'metal3', MS, .8)
    b.r(28, 36, 40, 22, 'dkm2', DS, rx=4, sw=.8)
    b.c(40, 47, 9.8, 'lens', '#05101C', 1)
    b.c(40, 47, 6.4, 'none', '#4E86BD', .8, op=.9)
    b.c(60, 47, 8, 'dkm', '#05101C', 1)
    b.c(60, 47, 5.6, 'thermal', '#2A1A3A', .6, op=.85)
    b.c(60, 47, 8, 'none', '#F2A93B', .8, op=.9)
    b.c(50, 55.4, 2, '#05101C', '#4A525C', .5); b.c(50, 55.4, .7, REDL)
    glint(b, 37, 43.4, 2.6, 1.3); glint(b, 57.4, 43.6, 1.8, .9)
    b.hl("M26 26 L60 25.2", 1, .85)
    # tracking reticle accent
    b.c(84, 14, 6, 'none', DET, 1.3, op=.95)
    b.ln("M84 5 L84 10 M84 18 L84 23 M75 14 L80 14 M88 14 L93 14", DET, 1.3)
    b.c(84, 14, 1, DET)

# ---------------------------------------------------------------- 7
@icon('cuas_irst', '红外全景搜索系统', K)
def _(b):
    cx = 48
    b.sh(48, 89, 28, 3.4)
    b.e(48, 85, 24, 4, 'metal3', MS)
    b.r(43, 62, 10, 23, 'cylM', MS)
    # back half of scan ring
    b.ln("M8 46 A40 11 0 0 1 88 46", DET, 1.6, .55)
    # drum
    b.p("M26 30 L26 60 A22 7 0 0 0 70 60 L70 30 Z", 'cylM', MS)
    b.p("M26 38 L26 54 A22 7 0 0 0 70 54 L70 38 A22 7 0 0 1 26 38 Z", 'canopy', '#0F2339', 1)
    for i in range(1, 8):
        t = -1 + 2 * i / 8
        x = 48 + 22 * t; s = math.sqrt(1 - t * t)
        b.ln(f"M{x:.1f} {38+7*s:.1f} L{x:.1f} {54+7*s:.1f}", '#AEB8C4', 1.3)
    for i in range(8):
        t = -1 + 2 * (i + .5) / 8
        x = 48 + 22 * t; s = math.sqrt(1 - t * t)
        b.e(round(x - .6, 1), round(41.4 + 7 * s, 1), 1.4, .8, '#FFFFFF', op=.75)
        b.e(round(x, 1), round(49.5 + 7 * s, 1), 2.2, 1.7, 'thermal', op=.5)
    b.e(48, 30, 22, 7, 'metal', MS)
    b.e(48, 29, 15, 4.4, 'metal2', MS, .7)
    b.e(48, 26.8, 6, 2.2, 'dkm', DS, .8)
    b.hl("M27.6 33 L27.6 56", .9, .6)
    # front half of scan ring + arrow
    b.ln("M8 46 A40 11 0 0 0 88 46", DET, 1.8, .95)
    arrowhead(b, 88, 46, -80, DET, 4)

# ---------------------------------------------------------------- 8
@icon('cuas_acoustic_array', '声学阵列', K)
def _(b):
    b.sh(48, 86, 42, 5)
    b.e(48, 78, 41, 11, 'metal2', MS, .9, op=.55)
    poles = [(20, 72, 38), (48, 66, 34), (76, 72, 38), (32, 86, 46), (64, 86, 46)]
    hub = (48, 77)
    # cables
    for x, y, h in poles:
        b.ln(f"M{x} {y} Q{(x+hub[0])/2:.0f} {y+5} {hub[0]} {hub[1]}", '#2A2E33', 1.2, .85)
    b.r(39, 74, 18, 8, 'dkm', DS, rx=1.6, sw=.8)
    leds(b, [(43, 78, GREEN), (48, 78, AMBER)])
    b.r(51, 76, 3.6, 3.6, 'metal3')
    for x, y, h in sorted(poles, key=lambda p: p[1]):
        b.ln(f"M{x-4} {y+2.5} L{x} {y} L{x+4} {y+2.5}", '#3A4048', 1.4)
        b.e(x, y + 1, 3.4, 1.3, '#1E2328')
        b.ln(f"M{x} {y} L{x} {y-h+4}", '#5E6A78', 2.4)
        b.ln(f"M{x-.5} {y} L{x-.5} {y-h+4}", '#C9D1DA', .7)
        b.c(x, y - h, 5.4, 'mic', '#0E1114', .8)
        b.e(x - 1.8, y - h - 2, 1.8, 1, '#FFFFFF', op=.55)
        b.ln(f"M{x-4.4} {y-h+3.2} L{x+4.4} {y-h+3.2}", '#5E6A78', 1.2)
    dwav(b, 8, 24, [8, 15], -35, 35, 1.5)
    dwav(b, 90, 22, [8, 15], 145, 215, 1.5)
    dwav(b, 48, 4, [6, 11], 40, 140, 1.4, .8)

# ---------------------------------------------------------------- 9
@icon('cuas_remote_id', '远程识别接收器', K)
def _(b):
    b.sh(50, 88, 36, 3.2)
    # ID badge
    b.r(60, 6, 30, 20, 'paper', '#8794A3', rx=3, sw=1)
    b.r(60, 6, 30, 5, 'scr', '#0F2339', rx=2.4, sw=.8)
    b.c(69, 18, 3.2, 'skin', '#7A5D3E', .6)
    b.p("M63.4 25 Q63.4 21.4 69 21.4 Q74.6 21.4 74.6 25 Z", 'uniform', '#33495F', .6)
    b.ln("M77 15 L87 15 M77 19 L85 19 M77 23 L86 23", '#5E6A78', 1.2)
    # drone
    mini_drone(b, 24, 24, 1.5)
    dwav(b, 24, 24, [16, 23, 30], 8, 58, 1.7)
    # receiver
    b.ln("M70 52 L70 46", '#2A2E33', 3.4); b.ln("M70 52 L70 46", '#5E6A78', 1.2)
    b.r(67.6, 40, 4.8, 7, 'dkm2', DS, rx=2, sw=.7)
    box3d(b, 18, 56, 52, 26, 10, 7, 'dkm', 'metal2', 'dkm2', DS, 2.5)
    b.r(23, 60.5, 33, 17, 'scr', '#0B1A2C', rx=1.5, sw=.6)
    for i, c in enumerate((GREEN, AMBER, GREEN)):
        y = 63 + i * 5
        b.c(27, y, 1.3, c)
        b.ln(f"M31 {y} L{44 - i*3} {y} M47 {y} L{53 - i} {y}", '#9CC2EA', 1.3, .9)
    b.p("M24 61 L38 61 L30 77 L24 77 Z", '#FFFFFF', op=.12)
    b.c(62, 64, 3.2, 'sphere', '#1E2328', .7); b.c(62, 73, 2.2, 'sphere', '#1E2328', .7)
    b.c(78, 55, 1.2, DET)

# ---------------------------------------------------------------- 10
@icon('cuas_mast', '一体化探测塔', K)
def _(b):
    b.sh(48, 90, 34, 3.4)
    b.e(48, 86, 26, 4, 'metal3', MS)
    def xl(y): return 38 + 8 * (84 - y) / 58
    def xr(y): return 58 - 8 * (84 - y) / 58
    ys = [84, 72, 60, 48, 36, 26]
    d = ''
    for i in range(len(ys) - 1):
        ya, yb = ys[i], ys[i + 1]
        d += f"M{xl(ya):.1f} {ya} L{xr(yb):.1f} {yb} M{xr(ya):.1f} {ya} L{xl(yb):.1f} {yb} "
    for y in ys: d += f"M{xl(y):.1f} {y} L{xr(y):.1f} {y} "
    b.ln(d, '#8794A3', 1.1)
    b.ln(f"M{xl(84)} 84 L{xl(26):.1f} 26 M{xr(84)} 84 L{xr(26):.1f} 26", '#5E6A78', 2.4)
    b.ln(f"M{xl(84)-.6} 84 L{xl(26)-.6:.1f} 26", '#E4EAF0', .7)
    # antenna crossarm
    b.ln("M30 50 L66 50", '#5E6A78', 2)
    for x in (32, 64):
        b.ln(f"M{x} 50 L{x} 38", '#2A2E33', 1.8); b.c(x, 38, 1.1, '#5E6A78')
    b.ln("M40 50 L40 42 M56 50 L56 42", '#2A2E33', 1.5)
    # EO ball on arm
    b.ln("M51 38 L58 38", '#5E6A78', 2)
    b.c(63, 38, 6, 'sphere', MS, .9)
    b.e(65.6, 38, 3, 3.6, 'canopy', '#0F2339', .6); b.c(66, 38, 1.8, 'lens', '#05101C', .4)
    b.hl("M59 35 Q61 32.4 64 32", .8, .9)
    # radar on top
    b.r(43.5, 20, 9, 7, 'metal3', MS, rx=1.2, sw=.8)
    b.r(32, 4, 28, 16, 'metal', MS, rx=1.5)
    b.p("M60 4 L65 7 L65 17 L60 20 Z", 'metal3', MS, .9)
    array_face(b, ((34, 6), (58, 6), (58, 18), (34, 18)), 6, 2, 0, 1, 0, 1)
    b.hl("M33 5 L59 5", .8, .9)
    # cabinet
    box3d(b, 60, 74, 20, 12, 6, 4, 'dkm', 'metal2', 'dkm2', DS, 1.4)
    leds(b, [(64, 79, GREEN), (68, 79, AMBER)])
    b.ln("M58 82 C54 82 52 84 50 84", '#2A2E33', 1.4)
    dwav(b, 66, 12, [9, 15], -48, 40, 1.5)
    dwav(b, 28, 12, [9, 15], 140, 228, 1.5)

# ---------------------------------------------------------------- 11
@icon('cuas_detector_handheld', '手持式无人机侦测仪', K)
def _(b):
    b.sh(40, 90, 22, 3)
    # rubber-duck antenna
    b.ln("M18 38 L12 8", '#1E2328', 4.4); b.ln("M17.4 37 L11.4 9", '#5E6A78', 1)
    b.r(14, 33, 8, 6, 'dkm2', DS, rx=1.6, sw=.7)
    # grip
    b.p("M20 56 L40 56 L38.5 85 Q38 90 33 90 L27 90 Q22 90 21.6 85 Z", 'dkm2', DS)
    b.ln("M25 64 L36 64 M25 69 L36.4 69 M25 74 L36.6 74 M25 79 L36.8 79", '#6A7480', 1, .9)
    # body
    b.r(5, 36, 56, 22, 'dkm', DS, rx=7)
    b.hl("M10 38 L54 38", 1, .6)
    b.r(9, 39.6, 32, 15, 'scr', '#0B1A2C', rx=2, sw=.7)
    b.c(21, 47, 6, 'none', DETL, .6, op=.8); b.c(21, 47, 2.6, 'none', DETL, .6, op=.8)
    b.ln("M21 47 L26 42.4", DETL, .8)
    mini_drone(b, 28, 45, .62, '#E8F0F8', REDL)
    b.ln("M35 42 L39 42 M35 46 L39 46 M35 50 L38 50", '#7FE0A0', 1.1)
    b.p("M10 40.4 L22 40.4 L15 53.6 L10 53.6 Z", '#FFFFFF', op=.12)
    leds(b, [(47, 43, GREEN), (53, 43, AMBER)])
    b.c(48, 51, 2.3, 'sphere', '#1E2328', .6); b.c(55, 51, 2.3, 'sphere', '#1E2328', .6)
    # directional patch panel
    b.p("M60 24 L72 20 L72 70 L60 74 Z", 'metal', MS)
    b.p("M72 20 L77 23 L77 73 L72 70 Z", 'metal3', MS)
    array_face(b, ((60, 24), (72, 20), (72, 70), (60, 74)), 2, 5, .15, .85, .06, .94)
    b.ln("M61 24 L72.6 20", '#FFFFFF', .9, .9)
    b.r(56, 44, 5, 8, 'metal3', MS, rx=1, sw=.8)
    dwav(b, 79, 46, [8, 14], -48, 48, 1.6)

# ---------------------------------------------------------------- 12
@icon('cuas_detector_portable', '便携箱式侦测设备', K)
def _(b):
    b.sh(48, 88, 42, 3.6)
    # lid (open, upright behind)
    b.p("M23 55 L25 12 Q25 9 28 9 L68 9 Q71 9 71 12 L73 55 Z", 'dkm2', DS)
    b.p("M29 16 L67 16 L69 50 L27 50 Z", 'scr', '#0B1A2C', .8)
    for i, (c, o) in enumerate(((DET, .9), ('#7FE0A0', .8), (AMBER, .8), ('#7FE0A0', .7), (DET, .8))):
        y = 21 + i * 6
        b.ln(f"M{31 + (i % 2) * 2} {y} L{44 + i * 3} {y} M{48 + i} {y} L{64 - (i%3)} {y}", c, 1.6, o)
    b.ln("M31 44 L34 40 L37 45 L40 38 L43 44 L47 41 L50 46 L54 39 L58 44 L63 42", '#FFFFFF', 1, .8)
    b.p("M29 16 L42 16 L38 50 L27 50 Z", '#FFFFFF', op=.1)
    leds(b, [(48, 12.4, GREEN)])
    # base
    b.p("M8 66 L22 54 L88 54 L74 66 Z", 'metal3', MS)
    b.p("M74 66 L88 54 L88 70 L74 82 Z", 'dkm2', DS)
    b.r(8, 66, 66, 16, 'dkm', DS, rx=2.4)
    b.hl("M9 67 L21.4 55.2 L87 55.2", .9, .7)
    # controls on top
    for x in (30, 40): b.e(x, 60, 3.2, 1.7, 'sphere', '#1E2328', .6)
    b.r(50, 58.4, 12, 3.4, '#1E2328', rx=.8)
    leds(b, [(53, 60, GREEN), (57, 60, AMBER)])
    # front face details
    b.r(14, 68.6, 8, 4.6, 'amber', '#8A4E12', rx=1.2, sw=.6); b.r(60, 68.6, 8, 4.6, 'amber', '#8A4E12', rx=1.2, sw=.6)
    for x in (30, 38, 46, 54): b.c(x, 74.2, 2, 'sphere', '#1E2328', .6)
    b.ln("M28 78.6 Q41 82.4 54 78.6", '#6A7480', 1.3)
    # antennas
    for (x0, y0, x1, y1) in ((78, 59, 77, 20), (85, 60, 91, 30)):
        b.ln(f"M{x0} {y0} L{x1} {y1}", '#1E2328', 3.6); b.ln(f"M{x0-.8} {y0} L{x1-.8} {y1+1}", '#6A7480', .8)
        b.e(x0, y0 + .6, 3.6, 1.6, 'dkm2', DS, .6)
    dwav(b, 80, 14, [6, 11], -150, -30, 1.5)

# ---------------------------------------------------------------- 13
@icon('cuas_shelter', '方舱式反无人系统', K)
def _(b):
    b.sh(46, 88, 42, 3.8)
    # roof gear
    b.ln("M50 40 L50 22", '#2A2E33', 1.6)
    for y in (24, 28, 32): b.ln(f"M{50-4} {y} L{50+4} {y}", '#5E6A78', 1.1)
    b.ln("M25 42 L25 34", '#5E6A78', 3)
    b.p("M12 20 L36 16 L36 34 L12 38 Z", 'metal2', MS)
    array_face(b, ((12, 20), (36, 16), (36, 34), (12, 38)), 4, 3, .08, .92, .1, .9)
    b.hl("M12 19.4 L36 15.4", .8, .9)
    # container
    b.r(10, 77, 56, 4, 'dkm2', DS, sw=.8)
    box3d(b, 8, 44, 58, 34, 20, 11, 'land', 'canvas', 'landdk', LS, 2)
    d = ''
    for x in range(14, 40, 4): d += f"M{x} 46 L{x} 76 "
    b.ln(d, '#55663A', 1.2, .8)
    b.r(8, 42, 58, 4, 'landdk', LS, rx=1.4, sw=.8)
    b.r(8, 74, 58, 4, 'landdk', LS, rx=1.4, sw=.8)
    # door
    b.r(43, 49, 18, 25, 'land', LS, rx=1.2, sw=1)
    b.ln("M52 49 L52 74", '#3E4C29', .9)
    b.c(49.6, 62, 1.2, '#D6DCE3', '#2E3238', .5); b.c(54.4, 62, 1.2, '#D6DCE3', '#2E3238', .5)
    leds(b, [(15, 50.6, GREEN), (20, 50.6, AMBER)])
    # side vent
    b.p("M70 58 L82 51.6 L82 60 L70 66.4 Z", '#000000', op=.2)
    b.ln("M70 62 L82 55.6 M70 65 L82 58.6", '#3A4048', 1, .7)
    # EO ball on telescopic mast
    b.ln("M68 38 L68 20", '#5E6A78', 2.4); b.ln("M67.4 38 L67.4 21", '#E4EAF0', .6)
    b.c(68, 16, 6, 'sphere', MS, .9)
    b.e(70.6, 16, 3, 3.6, 'canopy', '#0F2339', .6); b.c(71, 16, 1.8, 'lens', '#05101C', .4)
    b.hl("M64 13.4 Q66 10.6 69 10.2", .8, .9)
    b.hl("M9.4 43 L66 43", .8, .6)
    # protective dome (detection accent)
    b.ln("M3 58 A45 54 0 0 1 93 58", DET, 1.3, .8, extra="stroke-dasharray='3.4 2.6'")

# ---------------------------------------------------------------- 14
@icon('cuas_c2', '反无人指控终端', K)
def _(b):
    b.sh(48, 88, 40, 3.4)
    b.r(40, 64, 16, 9, 'metal3', MS, sw=.9)
    b.e(48, 74, 22, 3.6, 'metal2', MS, .9)
    b.r(6, 8, 84, 58, 'dkm', DS, rx=4)
    b.r(10, 12, 76, 50, 'scr', '#0A1B2E', rx=2, sw=.8)
    # PPI
    cx, cy = 34, 38
    b.c(cx, cy, 20, '#0A2238', DET, 1)
    b.c(cx, cy, 13.5, 'none', DET, .6, op=.7); b.c(cx, cy, 7, 'none', DET, .6, op=.7)
    b.ln(f"M{cx-20} {cy} L{cx+20} {cy} M{cx} {cy-20} L{cx} {cy+20}", DET, .5, .55)
    b.p(f"M{cx} {cy} L{cx+15} {cy-13.4} A20 20 0 0 1 {cx+20} {cy} Z", 'wedge', op=.9)
    b.ln(f"M{cx} {cy} L{cx+15} {cy-13.4}", DETL, 1.1, .95)
    mini_drone(b, 24, 28, .46, '#E8F0F8'); mini_drone(b, 28, 50, .46, '#E8F0F8')
    mini_drone(b, 43, 31, .5, '#FFD0C8', REDL)
    # side list
    for i, c in enumerate((REDL, AMBER, GREEN)):
        y = 17 + i * 8
        b.r(58, y, 25, 6, '#10304F', '#2D5C8F', rx=1, sw=.5)
        b.r(59.2, y + 1.2, 3.6, 3.6, c, rx=.8)
        b.ln(f"M65 {y+3} L80 {y+3}", '#9CC2EA', 1, .85)
    # alert banner
    b.r(58, 43, 25, 14, '#8E2E22', '#E2574C', rx=1.5, sw=.8)
    b.p("M64 55 L68 46 L72 55 Z", '#FFE08A', '#E9B44C', .5)
    b.ln("M68 49 L68 52", '#8E2E22', 1.1); b.c(68, 53.8, .5, '#8E2E22')
    b.ln("M74 48 L81 48 M74 52 L79 52", '#FFD0C8', 1.2, .9)
    b.p("M11 13 L34 13 L22 48 L11 48 Z", '#FFFFFF', op=.07)
    b.hl("M8 9.4 L86 9.4", .9, .55)
    # keyboard
    b.p("M12 88 L20 78 L76 78 L84 88 Z", 'dkm2', DS)
    d = ''
    for y in (81, 84.5):
        d += f"M{14 - (y-81)*1.2:.1f} {y} L{82 + (y-81)*1.2:.1f} {y} "
    b.ln(d, '#6A7480', 1.4, .8, extra="stroke-dasharray='3 1.6'")
    b.hl("M13 87.6 L20.4 78.6 L75.6 78.6", .8, .6)

# ---------------------------------------------------------------- 15
@icon('cuas_fence', '电子围栏', K)
def _(b):
    P = [(12, 86, 52), (36, 78, 44), (58, 72, 38), (80, 67, 33)]
    b.sh(48, 88, 44, 3.2)
    b.ln("M12 87 L36 79 L58 73 L80 68", DET, 1.2, .9, extra="stroke-dasharray='2.4 2'")
    for i in range(3):
        x1, y1, h1 = P[i]; x2, y2, h2 = P[i + 1]
        b.p(qpath([(x1, y1 - 3), (x2, y2 - 3), (x2, y2 - h2 + 8), (x1, y1 - h1 + 8)]), 'fenceG', DET, .7)
        for v in (.32, .56, .8):
            ya = y1 - 3 - v * (h1 - 11); yb = y2 - 3 - v * (h2 - 11)
            xm = (x1 + x2) / 2; s = -3 if (int(v * 10) % 2) else 3
            b.ln(f"M{x1} {ya:.1f} Q{(x1+xm)/2:.1f} {ya+s-(ya-yb)*.0:.1f} {xm:.1f} {(ya+yb)/2:.1f} T{x2} {yb:.1f}", '#FFFFFF', .9, .75)
    for x, y, h in P:
        w = 5 * (h / 52) ** .5
        b.e(x, y + .6, w + 2.4, 1.6, '#1E2328')
        b.r(round(x - w / 2, 1), y - h, round(w, 1), h, 'cylM', MS, sw=.8)
        b.r(round(x - w, 1), y - h - 5, round(w * 2, 1), 6, 'dkm', DS, rx=1.2, sw=.8)
        b.c(x, y - h - 2, 1.2, DETL)
    b.ln("M9 82 L9 40", '#FFFFFF', .7, .5)
    # intruding drone
    mini_drone(b, 64, 15, 1.15, '#2E3640', REDL)
    b.ln("M53 5 L57 9 M75 5 L71 9", REDL, 1.3, .9)

# ---------------------------------------------------------------- 16
@icon('cuas_lidar', '激光雷达探测器', K)
def _(b):
    b.sh(32, 90, 26, 3.2)
    b.ln("M32 66 L12 89 M32 66 L52 89 M32 66 L32 90", '#3A4048', 2.8)
    for x in (12, 52, 32): b.e(x, 90, 3, 1.1, '#1E2328')
    b.r(27, 56, 10, 12, 'cylM', MS, rx=2)
    # housing
    b.r(10, 22, 44, 36, 'metal', MS, rx=7)
    b.r(30, 17, 14, 6, 'dkm', DS, rx=2, sw=.8)
    b.ln("M15 30 L15 50 M19 30 L19 50 M23 30 L23 50", '#AEB8C4', 1.4, .9)
    b.hl("M13 26 Q14 24 20 23.6 L44 23.6", 1, .85)
    leds(b, [(15, 53.6, GREEN)])
    # optics plate
    b.r(46, 26, 15, 28, 'dkm', DS, rx=4, sw=1)
    b.c(53.6, 35, 4.4, 'lens', '#05101C', .8)
    b.c(53.6, 46, 5.4, 'lens', '#05101C', .8)
    b.c(53.6, 35, 1.4, REDL); b.c(53.6, 35, 3, 'none', '#F2A93B', .6, op=.9)
    glint(b, 52, 43.8, 1.8, .9)
    # beams + point cloud drone
    for yt in (18, 31, 44, 56):
        b.ln(f"M62 38 L{80} {yt}", DET, .9, .55)
    pts = [(84, 37), (78, 32), (90, 32), (78, 44), (90, 44), (74, 29), (94, 29), (74, 47), (94, 47), (84, 33), (84, 41), (81, 37), (87, 37)]
    for x, y in pts:
        b.c(x, y, 1.35, DET, op=.95); b.c(x - .35, y - .4, .45, '#FFFFFF')
    b.ln("M78 32 L90 44 M90 32 L78 44", DET, .6, .5)
    dwav(b, 62, 38, [7, 13], -30, 30, 1.2, .6)

# ---------------------------------------------------------------- 17
@icon('cuas_ads_b', 'ADS-B／航迹接收站', K)
def _(b):
    b.sh(50, 90, 38, 3.2)
    # track trail
    b.ln("M6 58 Q10 44 22 36", DET, 1.6, .9, extra="stroke-dasharray='2.4 2.4'")
    for (x, y) in ((6, 58), (9.4, 48.4), (15, 41.4)): b.c(x, y, 1.5, DET)
    # airliner (top view)
    b.g('translate(33 24) rotate(42)')
    b.p("M0 -15 C2.4 -15 3.2 -11 3.2 -6 L16 3 L16 6.4 L3 3.6 L2.4 10 L7 13 L7 15.4 L0 14 L-7 15.4 L-7 13 L-2.4 10 L-3 3.6 L-16 6.4 L-16 3 L-3.2 -6 C-3.2 -11 -2.4 -15 0 -15 Z", 'air', AS, 1)
    b.ln("M0 -13 L0 8", '#FFFFFF', .8, .8)
    b.eg()
    dwav(b, 38, 28, [14, 21, 28], 8, 60, 1.6)
    # radome antenna
    b.r(66, 70, 18, 5, 'metal3', MS, rx=1.4, sw=.9)
    b.r(72, 74, 6, 12, 'cylM', MS, sw=.8)
    b.r(69.6, 18, 10.8, 54, 'cylW', '#8794A3', rx=5.4, sw=1)
    b.ln("M70 31 L80 31 M70 45 L80 45 M70 59 L80 59", '#B4BFCB', 1.2, .9)
    b.hl("M72.4 22 L72.4 66", 1, .8)
    b.c(75, 17, 2, 'dkm2', DS, .6)
    dwav(b, 75, 18, [9, 15], -150, -30, 1.4, .8)
    # receiver box
    b.ln("M43 78 C56 76 58 84 72 84", '#2A2E33', 1.5)
    box3d(b, 8, 66, 34, 18, 8, 6, 'dkm', 'metal2', 'dkm2', DS, 2)
    b.r(12, 69.4, 16, 11, 'scr', '#0B1A2C', rx=1, sw=.5)
    b.ln("M14 77 Q18 72 24 73.4", DET, 1, .95); b.c(24.4, 73.4, 1, DETL)
    leds(b, [(33, 71, GREEN), (33, 76, AMBER)])
    b.ln("M38 66 L38 58", '#2A2E33', 2.4); b.c(38, 57, 1.4, '#5E6A78')

KEYS = """cuas_radar_lowalt cuas_radar_4face cuas_radar_vehicle cuas_passive cuas_df cuas_eo cuas_irst cuas_acoustic_array cuas_remote_id cuas_mast cuas_detector_handheld cuas_detector_portable cuas_shelter cuas_c2 cuas_fence cuas_lidar cuas_ads_b""".split()

if __name__ == '__main__':
    import os
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    assert set(byk) == set(KEYS) and len(byk) == len(ICONS), set(KEYS) ^ set(byk)
    D_ = os.path.dirname(os.path.abspath(__file__))
    old = set()
    for f in os.listdir(D_):
        if f.startswith('icons') and f.endswith('.js') and f != 'icons_e.js':
            old |= set(re.findall(r"key: '([a-z_0-9]+)'", open(os.path.join(D_, f), encoding='utf-8').read()))
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
    open(os.path.join(D_, 'icons_e.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), sorted(SZ)[-6:])
