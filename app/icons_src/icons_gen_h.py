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

GR.update({
    'airU': L(V, (0, '#9DB3CE'), (.5, '#6F88A8'), (1, '#41566F')),
    'airUdk': L(V, (0, '#7E94B0'), (1, '#33475E')),
    'rockG': L(V, (0, '#8C9A63'), (.5, '#5F6E3E'), (1, '#364222')),
    'rockGdk': L(V, (0, '#667545'), (1, '#2C3818')),
    'jointG': L(V, (0, '#5F8068'), (.5, '#3C5C47'), (1, '#1F3527')),
    'jointGdk': L(V, (0, '#46674F'), (1, '#18281D')),
    'infoU': L(V, (0, '#6C9AA6'), (.5, '#427280'), (1, '#24444F')),
    'infoUdk': L(V, (0, '#4F7C89'), (1, '#1C3943')),
    'spaceU': L(V, (0, '#6A7AA6'), (.5, '#3F4E7A'), (1, '#1F2848')),
    'spaceUdk': L(V, (0, '#4B5A86'), (1, '#171E38')),
    'slate': L(V, (0, '#7C8CA3'), (.5, '#55637A'), (1, '#303B4D')),
    'slatedk': L(V, (0, '#5E6D85'), (1, '#252E3D')),
    'navyDk': L(V, (0, '#35507A'), (.5, '#1F3556'), (1, '#0E1A2E')),
    'vest': L(V, (0, '#FFE066'), (.5, '#F2B630'), (1, '#C48512')),
    'map': L(D, (0, '#E7EFC8'), (.5, '#B9D08C'), (1, '#8FAE62')),
    'sky': L(V, (0, '#D8EEFF'), (.6, '#8FC6F2'), (1, '#4C93D8')),
    'chart': L(V, (0, '#F4F8FA'), (1, '#CFE0EA')),
    'cardboard': L(V, (0, '#D7B27E'), (.5, '#B58B55'), (1, '#80602F')),
    'globe': ('r', ('0.35', '0.3', '0.75'), ((0, '#9FD6FF'), (.5, '#2F7BC8'), (1, '#0E2F5E'))),
    'radar': ('r', ('0.5', '0.5', '0.55'), ((0, '#2E7A4A'), (1, '#0B2415'))),
    'whiteB': L(V, (0, '#FFFFFF'), (.5, '#F1F4F7'), (1, '#C5CDD6')),
    'wine': L(V, (0, '#8F3A40'), (1, '#4E1A1E')),
})
AUS, RKS, JTS, INS, SPS, SLS = '#2C3F57', '#2C3818', '#14261B', '#1C3943', '#171E38', '#252E3D'
GOLDS = '#7A5C18'
RED, BLUE = '#D9473A', '#3D86D6'

def bust(b, uni, st, shirt='#E7EBDA', tie='#3E4C29', lapel=None, stripe=None, board='gold', collar=True):
    torso(b, uni, st)
    if collar:
        collar_tie(b, shirt, tie, lapel or uni, st)
    # shoulder boards
    b.p("M17 74 L30 68 L32.4 71.6 L19.4 77.6 Z", board, GOLDS, .6)
    b.p("M79 74 L66 68 L63.6 71.6 L76.6 77.6 Z", board, GOLDS, .6)
    if stripe:
        b.ln("M19 76 L31 70.5 M77 76 L65 70.5", stripe, 1.3)
    b.c(24, 72.6, .9, '#FFF6D0'); b.c(72, 72.6, .9, '#FFF6D0')
    b.hl("M20 80 C24 72 32 68 38 67", 1.2, .5)

def peaked(b, crown, cst, band, brim='#1E2328', badge='gold', trim='#D8B45A', flat=False, red=False):
    if flat:   # navy white top
        b.p("M20 24 C18 12 32 6 48 6 C64 6 78 12 76 24 C68 26.5 58 28 48 28 C38 28 28 26.5 20 24 Z", crown, cst)
        b.e(48, 10.5, 25, 4.6, '#FFFFFF', None, op=.55)
    else:
        b.p("M22 22 C22 12 35 6 48 6 C61 6 74 12 74 22 C68 24.5 58 26 48 26 C38 26 28 24.5 22 22 Z", crown, cst)
    b.p("M30 23 C38 25.4 58 25.4 66 23 L65.4 30 C58 32 38 32 30.6 30 Z", band, cst, .8)
    b.ln("M31 27 C40 29 56 29 65 27", trim, 1.2)
    b.p("M30.4 29.6 C38 32 58 32 65.6 29.6 C64.6 34.6 58 37 48 37 C38 37 31.4 34.6 30.4 29.6 Z", brim, '#0E1013', .7)
    b.hl("M35 32.8 C42 34.4 54 34.4 61 32.8", .9, .5)
    b.hl("M26 15 C30 10 38 7.6 46 7.4", 1.2, .8)

def garrison(b, fill, st, pipe, badge=True):
    b.p("M29 28 C27 20 29 13 34 8 C40 13 56 13 62 8 C67 13 69 20 67 28 C58 31.5 38 31.5 29 28 Z", fill, st, 1)
    b.ln("M34 8 C40 13 56 13 62 8", pipe, 1.4)
    b.ln("M28.6 25.6 C38 29.4 58 29.4 67.4 25.6", pipe, 1)
    if badge:
        b.c(48, 20, 3.2, 'gold', GOLDS, .6); b.p(star(48, 20.2, 2.1), RED)
    b.hl("M36 13.5 C40 16 46 16.6 52 16", 1, .5)

def headset(b, mic=True):
    b.ln("M30 38 C30 12 66 12 66 38", '#22272D', 4.2)
    b.ln("M31.5 30 C33 16 63 16 64.5 30", '#5E6A78', 1.2)
    b.e(31, 41, 5.4, 7.5, 'dkm', '#15191E', .8)
    b.e(65, 41, 5.4, 7.5, 'dkm', '#15191E', .8)
    if mic:
        b.ln("M30 46 C30 54 36 58 44 56.5", '#22272D', 2)
        b.e(45, 56.4, 2.4, 1.8, '#22272D')
    b.c(67.5, 38, 1.2, GREEN)

def monitor(b, x=14, y=64, w=68, h=30):
    b.r(x, y, w, h, 'dkm2', DS, rx=3, sw=1)
    b.r(x + 3, y + 3, w - 6, h - 3, 'scr', '#0B1A2C', rx=1, sw=.6)
    return (x + 3, y + 3, w - 6, h - 3)

def screen_glint(b, x, y, w, h):
    b.p(f"M{x+3} {y+.5} L{x+14} {y+.5} L{x+6} {y+h-1} L{x+3} {y+h-1} Z", '#FFFFFF', op=.1)

def ophead(b, hairc='hair'):
    b.r(41, 54, 14, 12, 'skin')
    b.e(48, 38, 16, 19, 'skin', SKIN_ST, 1)
    b.p("M32 36 C31 22 38 16 48 16 C58 16 65 22 64 36 C61 29 56 26 48 26 C40 26 35 29 32 36 Z", hairc, '#211D1A', .8)

def clip(b, x, y, w, h, paper='paper', rot=0, cx=0, cy=0):
    b.r(x, y, w, h, 'dkm2', DS, rx=2, sw=1)
    b.r(x + 2.5, y + 5, w - 5, h - 7.5, paper, '#97A3B1', sw=.6)
    b.r(x + w / 2 - 6, y - 2, 12, 6, 'metal3', MS, rx=1.5, sw=.8)
    b.c(x + w / 2, y + 1, 1.2, '#E7EBEF')

# ================= 人员（按军种） =================
@icon('cmd_army', '陆军指挥员', '人员')
def _(b):
    bust(b, 'olive', OS, stripe='#D9473A')
    head(b)
    peaked(b, 'olive', OS, 'olivedk', badge='gold')
    b.c(48, 16.5, 4.4, 'gold', GOLDS, .7); b.p(star(48, 16.8, 2.9), RED)
    # map table
    b.p("M8 94 L18 79 L78 79 L88 94 Z", 'map', '#5E7A3C', 1)
    b.ln("M24 85 L72 85 M20 90 L76 90 M40 79 L36 94 M56 79 L60 94", '#FFFFFF', .7, .55)
    b.p("M26 90 C34 84 44 86 52 82 L50 79.6 L60 82.6 L50 86 L51 84.2 C44 88 34 88 28 92 Z", RED)
    b.c(66, 86, 2.4, BLUE, '#25578F', .6)
    arm(b, "M80 70 C76 74 68 78 60 80", 'olive', OS)
    hand(b, 58, 81, 3.2)
    b.ln("M56.6 82.4 L50 85.4", '#E6C49C', 2); 

@icon('cmd_navy', '海军指挥员', '人员')
def _(b):
    bust(b, 'navyB', NS, shirt='#F2F7FC', tie='#0F1E33', lapel='navyDk', stripe='#F2F7FC')
    head(b)
    peaked(b, 'whiteB', '#97A3B1', 'navyDk', flat=True, trim='#D8B45A')
    # anchor badge
    b.c(48, 17, 4.6, 'gold', GOLDS, .7)
    b.ln("M48 13.8 L48 20.6 M45.4 17.4 L50.6 17.4 M45.6 18.8 C46 20.6 50 20.6 50.4 18.8", '#7A2A20', 1)
    # binoculars
    b.ln("M38 64 C38 72 42 74 44 74 M58 64 C58 72 54 74 52 74", '#1E2328', 1.2)
    for x in (33, 53):
        b.r(x, 70, 11, 19, 'dkm', DS, rx=3, sw=.9)
        b.e(x + 5.5, 71, 5.8, 2.6, 'lens', DS, .6)
        b.r(x + 1.5, 78, 8, 2.6, '#8794A3', rx=1)
    b.r(43, 78, 10, 4, 'dkm2', DS, rx=1.5, sw=.8)
    b.hl("M35 74 L35 85 M55 74 L55 85", .9, .5)
    hand(b, 30, 84, 3.2); hand(b, 66, 84, 3.2)

@icon('cmd_air', '空军指挥员', '人员')
def _(b):
    bust(b, 'airU', AUS, shirt='#EEF4FA', tie='#2C3F57', lapel='airUdk', stripe='#EEF4FA', board='metal')
    head(b)
    peaked(b, 'airU', AUS, 'airUdk', trim='#EEF4FA')
    # wings badge
    b.p("M30 18 C36 14 41 15 44 17.6 C40 18.6 35 19.2 30 18 Z M66 18 C60 14 55 15 52 17.6 C56 18.6 61 19.2 66 18 Z", 'gold', GOLDS, .6)
    b.c(48, 17, 3.6, 'gold', GOLDS, .7)
    # radar-plot map table
    b.p("M8 94 L18 79 L78 79 L88 94 Z", 'sky', '#2D6AA8', 1)
    b.ln("M22 92 C36 80 60 80 74 92 M32 92 C40 84 56 84 64 92", '#FFFFFF', .8, .7)
    b.ln("M24 90 C34 86 46 88 56 83 L68 81", '#F2A93B', 1.2, extra="stroke-dasharray='2.4 1.6'")
    b.p("M68 81 L61 79.6 L63 83 Z", '#F2A93B')
    b.p("M45 85.6 L48 82 L51 85.6 L48.6 85 L48.8 88 L47.2 88 L47.4 85 Z", '#FFFFFF', '#6B7785', .5)
    arm(b, "M80 70 C76 74 68 78 60 80", 'airU', AUS)
    hand(b, 58, 81, 3.2)
    b.ln("M56.6 82.4 L50 85.4", '#E6C49C', 2)

@icon('cmd_rocket', '火箭军指挥员', '人员')
def _(b):
    bust(b, 'rockG', RKS, shirt='#E7EBDA', tie='#9B3125', lapel='rockGdk', stripe=RED)
    head(b)
    peaked(b, 'rockG', RKS, '#B33A2C', trim='#F2C84B')
    b.c(48, 16.5, 4.4, 'gold', GOLDS, .7); b.p("M48 12.6 L50 17 L48 20.4 L46 17 Z", RED)
    # missile model held upright
    b.p("M70 58 C74 62 75 68 75 74 L75 92 L65 92 L65 74 C65 68 66 62 70 58 Z", 'cylW', '#8F9BA9', .9)
    b.p("M70 58 C72.4 60.4 74 63 74.6 66 L65.4 66 C66 63 67.6 60.4 70 58 Z", 'red', '#7A2A20', .6)
    b.p("M65 82 L59 94 L65 91 Z M75 82 L81 94 L75 91 Z", 'red', '#7A2A20', .6)
    b.ln("M65 72 L75 72", RED, 1.3)
    b.hl("M67 68 L67 88", .9, .7)
    hand(b, 70, 83, 3.4); hand(b, 28, 86, 3.4)
    b.ln("M30 86 L36 84", '#E6C49C', 2)

@icon('cmd_joint', '联合作战指挥员', '人员')
def _(b):
    # screens behind
    for x, flip in ((3, 0), (67, 1)):
        b.p(f"M{x} 12 L{x+26} 16 L{x+26} 52 L{x} 56 Z" if not flip else f"M{x+26} 12 L{x} 16 L{x} 52 L{x+26} 56 Z", 'dkm2', DS, 1)
    b.p("M6 16 L26 19.4 L26 49 L6 52.6 Z", 'scr')
    b.p("M90 16 L70 19.4 L70 49 L90 52.6 Z", 'scr')
    b.ln("M9 44 L13 38 L17 41 L23 30", '#7FE0A0', 1.1)
    b.c(15, 28, 4.4, 'globe'); b.ln("M10.6 28 L19.4 28", '#BFE3FF', .6, .7)
    b.r(8, 22.4, 6, 1.2, '#F2A93B', op=.8)
    b.c(80, 30, 5, 'none', '#7FE0A0', .9); b.ln("M80 30 L84.4 27", '#7FE0A0', 1)
    b.ln("M74 42 L88 40 M74 45.6 L84 44.4", '#8FD0FF', 1, .7)
    bust(b, 'jointG', JTS, shirt='#E7EBDA', tie='#B8912E', lapel='jointGdk', stripe='#F4DC92')
    head(b)
    peaked(b, 'jointG', JTS, 'jointGdk', trim='#F1D893')
    b.ln("M30.4 31 C38 33.2 58 33.2 65.6 31", '#D8B45A', 1)
    b.c(48, 16.5, 5, 'gold', GOLDS, .7); b.p(star(48, 16.8, 3.4), '#F4DC92')
    # desk
    b.p("M6 94 L12 83 L84 83 L90 94 Z", 'dkm', DS, 1)
    b.r(30, 86, 36, 3.4, 'scr', '#0B1A2C', rx=1)
    leds(b, [(22, 88, GREEN), (28, 88, AMBER), (70, 88, GREEN), (76, 88, REDL)])
    hand(b, 36, 82, 3.2); hand(b, 60, 82, 3.2)

@icon('staff_army', '陆军参谋', '人员')
def _(b):
    bust(b, 'olive', OS, stripe=None)
    head(b); hair(b)
    garrison(b, 'olive', OS, '#D8B45A')
    # map roll in left hand
    b.g('rotate(14 28 80)')
    b.r(22, 62, 12, 32, 'cylW', '#8F9BA9', rx=5, sw=.9)
    b.e(28, 63.4, 6, 2.2, '#FFFFFF', '#97A3B1', .6)
    b.ln("M24 74 L32 74 M24 80 L32 80", '#C27A60', 1.6, .8)
    b.eg()
    # unrolled map sheet
    b.g('rotate(-8 60 78)')
    b.r(40, 64, 34, 28, 'map', '#5E7A3C', rx=1, sw=.9)
    b.ln("M40 72 L74 72 M40 80 L74 80 M52 64 L52 92 M63 64 L63 92", '#FFFFFF', .6, .5)
    b.p("M44 88 C50 80 58 82 64 74 L62 72 L70 72.6 L66 79 L66 76.4 C60 84 52 84 46 90 Z", RED)
    b.c(70, 87, 2, BLUE, '#25578F', .5)
    b.eg()
    hand(b, 28, 88, 3.4); hand(b, 74, 82, 3.4)

@icon('staff_navy', '海军参谋', '人员')
def _(b):
    bust(b, 'navyB', NS, shirt='#F2F7FC', tie='#0F1E33', lapel='navyDk', stripe='#F2F7FC')
    head(b); hair(b)
    garrison(b, 'navyDk', NS, '#F2F7FC')
    # sea chart
    b.g('rotate(-6 56 78)')
    b.r(30, 62, 44, 30, 'chart', '#97A3B1', rx=1, sw=.9)
    b.p("M30 62 L74 62 L74 74 C66 70 58 76 50 72 C42 68 36 72 30 70 Z", '#9FD0EC', op=.8)
    b.p("M52 92 C54 82 60 80 66 82 C70 84 74 80 74 78 L74 92 Z", '#C9B98A', '#8F7F55', .6)
    b.ln("M34 80 L70 78 M34 86 L56 84 M42 62 L42 92 M58 62 L58 92", '#5E8DB4', .6, .6)
    b.c(40, 72, 5.2, '#FFFFFF', '#2C3F57', .7)
    b.ln("M40 66.4 L40 77.6 M34.4 72 L45.6 72", '#2C3F57', .8)
    b.p("M40 67 L41.6 72 L40 77 L38.4 72 Z", RED)
    b.eg()
    # dividers
    b.ln("M66 94 L72 66 M66 94 L78 70", '#8794A3', 1.6)
    b.c(72, 65.6, 1.6, 'gold', GOLDS, .5)
    hand(b, 32, 86, 3.4)

@icon('staff_air', '空军参谋', '人员')
def _(b):
    bust(b, 'airU', AUS, shirt='#EEF4FA', tie='#2C3F57', lapel='airUdk', board='metal')
    head(b); hair(b)
    garrison(b, 'airU', AUS, '#EEF4FA', badge=False)
    b.p("M42 22 C45 17 51 17 54 22 C51 21 45 21 42 22 Z", 'metal', '#6B7785', .6)
    b.c(48, 22.6, 1.8, 'gold', GOLDS, .5)
    # route clipboard
    b.g('rotate(-7 58 78)')
    clip(b, 38, 60, 40, 34, 'sky')
    b.ln("M44 86 C50 76 58 84 64 74 C67 69 70 68 72 67", '#FFFFFF', 1.3, extra="stroke-dasharray='3 2'")
    b.c(46, 86, 1.8, '#FFFFFF'); b.c(61, 76, 1.5, '#FFFFFF')
    b.p("M72 67 L66.6 66.6 L68.6 70 Z", '#F2A93B')
    b.p("M52 71 L55 66 L58 71 L56 70.4 L56.2 73.6 L53.8 73.6 L54 70.4 Z", '#FFFFFF', '#6B7785', .4)
    b.eg()
    hand(b, 38, 84, 3.4)

@icon('staff_rocket', '火箭军参谋', '人员')
def _(b):
    bust(b, 'rockG', RKS, shirt='#E7EBDA', tie='#9B3125', lapel='rockGdk', stripe=RED)
    head(b); hair(b)
    garrison(b, 'rockG', RKS, '#D9473A', badge=False)
    b.p("M48 15.4 L51 21 L48 25 L45 21 Z", RED, '#7A2A20', .5)
    b.g('rotate(-7 58 78)')
    clip(b, 38, 60, 40, 34, 'paper')
    b.ln("M44 88 C48 68 62 66 70 82", RED, 1.5)
    b.p("M44 88 L46.6 84 L47.8 86.4 Z", RED)
    b.c(70, 84, 3.4, 'none', RED, 1); b.c(70, 84, 1, RED)
    b.ln("M65 84 L75 84 M70 79 L70 89", RED, .8)
    b.ln("M43 90 L77 90", '#97A3B1', .8)
    b.eg()
    hand(b, 38, 84, 3.4)

@icon('staff_info', '信息支援参谋', '人员')
def _(b):
    bust(b, 'infoU', INS, shirt='#E3F1F4', tie='#1C3943', lapel='infoUdk', stripe='#8FE0F0')
    head(b); hair(b)
    # laptop (screen toward viewer)
    b.p("M20 62 L76 62 L78 86 L18 86 Z", 'dkm2', DS, 1)
    b.p("M23 65 L73 65 L74.4 83 L21.6 83 Z", 'scr', '#0B1A2C', .6)
    b.ln("M48 74 L35 70 M48 74 L61 70 M48 74 L40 80 M48 74 L58 80", '#8FD0FF', 1.1)
    b.ln("M35 70 L40 80 M61 70 L58 80", '#8FD0FF', .7, .6)
    for x, y, c_ in ((35, 70, 'node'), (61, 70, 'nodeG'), (40, 80, 'nodeA'), (58, 80, 'node')):
        b.c(x, y, 2.6, c_)
    b.c(48, 74, 3.8, 'glow')
    b.p("M25 65.6 L36 65.6 L28 82 L25 82 Z", '#FFFFFF', op=.1)
    b.p("M16 86 L80 86 L86 93 L10 93 Z", 'metal', MS, 1)
    b.ln("M20 89.4 L76 89.4", '#97A3B1', .8, extra="stroke-dasharray='2.4 1'")

@icon('staff_logistics', '联勤保障参谋', '人员')
def _(b):
    bust(b, 'olive', OS)
    # hi-vis vest
    b.p("M30 66 L40 66 L40 94 L26 94 Z M66 66 L56 66 L56 94 L70 94 Z", 'vest', '#8A5E0A', .8)
    b.ln("M26.5 83 L40 83 M69.5 83 L56 83", '#FFFFFF', 1.8, .9)
    head(b); hair(b)
    garrison(b, 'olive', OS, '#F2B630')
    # crate
    box3d(b, 8, 76, 22, 17, 5, 5, 'cardboard', 'tac', 'cardboard', '#6A4F28')
    b.r(8, 76, 22, 4, '#F4E4C0', op=.35)
    b.r(17, 76, 4, 17, '#E7D3A4', op=.55)
    b.p("M12 84 L16 84 L16 88 L12 88 Z", '#FFFFFF', '#6A4F28', .4)
    # clipboard checklist
    b.g('rotate(6 67 78)')
    clip(b, 52, 62, 30, 32, 'paper')
    for i in range(3):
        y = 72 + i * 6.4
        b.ln(f"M57 {y} L59 {y+1.8} L62.4 {y-2}", '#43A06B', 1.2)
        b.ln(f"M65 {y} L77 {y}", '#97A3B1', 1)
    b.eg()
    hand(b, 50, 90, 3.2)

@icon('staff_intel', '情报参谋', '人员')
def _(b):
    bust(b, 'suit', '#15191E', shirt='#F4F6F8', tie='#6B4BA8', lapel='suit', stripe='#B79CE8', board='metal')
    head(b); hair(b)
    # aerial photo
    b.g('rotate(-9 40 80)')
    b.r(18, 62, 40, 30, '#FFFFFF', '#97A3B1', rx=1, sw=.8)
    b.r(21, 65, 34, 21, 'terrain', '#5E7A3C', sw=.6)
    b.p("M21 78 C30 72 40 76 55 68 L55 72 C42 80 32 77 21 83 Z", '#C9B98A', op=.8)
    b.r(33, 70, 8, 4, '#2E3640', rx=.8, sw=0); b.r(34, 70.6, 6, 1.2, '#8794A3')
    b.c(37, 72, 6, 'none', RED, 1)
    b.eg()
    # magnifier
    b.ln("M72 82 L82 92", '#1E2328', 5.4); b.ln("M72 82 L82 92", '#6A7480', 2.4)
    b.c(64, 74, 11, 'glass', '#6A7480', 3, op=None)
    b.c(64, 74, 9.4, '#FFFFFF', op=.18)
    b.c(64, 74, 11, 'none', '#B9C4D0', 1.2)
    b.hl("M57.4 72 C58 68 61 65.6 65 65.4", 1.4, .9)
    b.p("M60 78 L66 72 L68 74 L62 80 Z", RED, op=.0)
    hand(b, 79, 88, 3.2)

@icon('staff_plan', '作战计划参谋', '人员')
def _(b):
    bust(b, 'jointG', JTS, shirt='#E7EBDA', tie='#B8912E', lapel='jointGdk', stripe='#F4DC92')
    head(b); hair(b)
    # whiteboard
    b.r(12, 60, 72, 34, 'metal2', MS, rx=2, sw=1)
    b.r(15, 63, 66, 28, 'whiteB', '#B9C4D0', sw=.6)
    b.r(18, 68, 10, 7, 'none', BLUE, sw=1.4); b.r(18, 79, 10, 7, 'none', BLUE, sw=1.4)
    b.r(68, 72, 10, 7, 'none', RED, sw=1.4)
    b.ln("M30 71.5 C42 71.5 48 74 61 75", BLUE, 2.2); b.p("M67 75.5 L60 71.6 L60 79 Z", BLUE)
    b.ln("M30 82.5 C42 82.5 50 80 61 77.6", BLUE, 2.2)
    b.ln("M72 66 C66 66 58 66 52 68", RED, 1.5, extra="stroke-dasharray='2.6 1.6'")
    b.p("M48 69 L54 65.6 L54 71.6 Z", RED)
    b.hl("M16 64 L40 64", .8, .8)
    b.r(36, 91.4, 24, 3, 'metal3', MS, rx=1, sw=.6)
    b.ln("M76 88 L88 78", '#2E3640', 3.2); b.ln("M76 88 L88 78", '#3D86D6', 1.6)
    hand(b, 74, 90, 3.4)

@icon('op_navy_cic', '舰艇作战情报中心操作员', '人员')
def _(b):
    torso(b, 'navyB', NS)
    b.p("M38 64 L48 76 L58 64 Z", '#DDE5EE', '#7C8A9B', .8)
    b.p("M42 64 L48 72 L54 64 Z", '#0F1E33')
    ophead(b)
    headset(b)
    b.hl("M20 80 C24 72 32 68 40 67", 1.2, .5)
    x, y, w, h = monitor(b, 12, 62, 72, 32)
    b.c(36, y + h / 2 + 1, 12.4, 'radar', '#7FE0A0', 1)
    b.c(36, y + h / 2 + 1, 8, 'none', '#3FA865', .6); b.c(36, y + h / 2 + 1, 4, 'none', '#3FA865', .6)
    b.ln(f"M36 {y+h/2+1} L44.8 {y+h/2-6.6}", '#9FFFC0', 1.2)
    b.p(f"M36 {y+h/2+1} L44.8 {y+h/2-6.6} L47 {y+h/2-3} Z", '#7FE0A0', op=.35)
    b.c(30, y + 9, 1.3, AMBER); b.c(41, y + 17, 1.3, REDL)
    b.ln("M56 70 L78 70 M56 74 L74 74 M56 78 L78 78", '#9CC2EA', 1, .7)
    b.r(56, 82, 5, 7, '#7FE0A0', op=.7); b.r(63, 85, 5, 4, '#F2A93B', op=.7); b.r(70, 80, 5, 9, '#8FD0FF', op=.7)
    screen_glint(b, x + 28, y, 30, h)

@icon('op_air_controller', '空中引导员', '人员')
def _(b):
    # tower window behind
    b.r(3, 4, 90, 50, 'sky', '#2D6AA8', rx=3, sw=1.2)
    b.ln("M33 4 L33 54 M63 4 L63 54", '#2D6AA8', 1.6)
    b.p("M8 38 C12 33 18 34 20 38 C24 35 28 38 28 42 L6 42 Z", '#FFFFFF', op=.8)
    b.p("M68 24 C72 20 78 21 80 25 C84 22 88 25 88 29 L66 29 Z", '#FFFFFF', op=.8)
    b.p("M12 18 L24 20 L26 17 L28 17.6 L27 21 L33 22.6 L33 24 L26 23.6 L25 26 L22 26 L23 23 L12 21.6 Z", '#FFFFFF', '#6B7785', .5)
    torso(b, 'airU', AUS)
    b.p("M38 64 L48 76 L58 64 Z", '#EEF4FA', '#7C8A9B', .8)
    b.p("M42 64 L48 72 L54 64 Z", '#2C3F57')
    ophead(b)
    headset(b)
    b.hl("M20 80 C24 72 32 68 40 67", 1.2, .5)
    x, y, w, h = monitor(b, 14, 68, 68, 26)
    b.ln(f"M{x+4} {y+h-4} L{x+w-4} {y+h-4}", '#3FA865', .8, .6)
    for cx, cy in ((26, 82), (46, 76), (64, 84)):
        b.p(f"M{cx} {cy-4} L{cx+3} {cy+3} L{cx} {cy+1.6} L{cx-3} {cy+3} Z", '#F2A93B')
        b.ln(f"M{cx} {cy+3} L{cx-8} {cy+9}", '#F2A93B', .8, .5)
    b.ln("M27 77 L46 79.4 M50 79 L62 80", '#8FD0FF', 1, .6)
    screen_glint(b, x + 30, y, 30, h)

@icon('op_space', '航天测控员', '人员')
def _(b):
    torso(b, 'spaceU', SPS)
    b.p("M38 64 L48 76 L58 64 Z", '#DDE5EE', '#7C8A9B', .8)
    b.p("M42 64 L48 72 L54 64 Z", '#171E38')
    ophead(b)
    headset(b)
    b.hl("M20 80 C24 72 32 68 40 67", 1.2, .5)
    # satellite icon top-right
    b.g('translate(8 4) scale(.8) rotate(-30 80 18)')
    b.r(74, 14, 12, 8, 'metal', MS, rx=1.5, sw=.8)
    b.r(54, 14.4, 17, 7.2, 'solar', '#12294A', sw=.8); b.r(89, 14.4, 17, 7.2, 'solar', '#12294A', sw=.8)
    b.ln("M60 14.4 L60 21.6 M65.6 14.4 L65.6 21.6 M95 14.4 L95 21.6 M100.6 14.4 L100.6 21.6", '#8FB0DC', .6)
    b.eg()
    x, y, w, h = monitor(b, 12, 62, 72, 32)
    b.r(x, y, w, h, '#050B1A', op=.9)
    for sx, sy in ((20, 70), (30, 88), (68, 68), (76, 90), (58, 90), (40, 66)):
        b.c(sx, sy, .7, '#FFFFFF')
    b.c(48, 79, 11.4, 'globe')
    b.p("M42 74 C46 72 50 74 51 77 C47 79 44 80 41 79 Z M50 82 C53 81 56 82 57 84 C55 87 51 87 49 85 Z", '#6FBF7A', op=.85)
    b.e(48, 79, 21, 7, 'none', '#F2A93B', 1.2, extra="transform='rotate(-18 48 79)'")
    b.c(65, 71.6, 2.2, '#FFFFFF'); b.c(65, 71.6, 3.6, 'none', '#FFFFFF', .6, .6)
    screen_glint(b, x + 28, y, 30, h)

@icon('op_satcom', '卫通值守员', '人员')
def _(b):
    torso(b, 'slate', SLS)
    b.p("M38 64 L48 76 L58 64 Z", '#DDE5EE', '#7C8A9B', .8)
    b.p("M42 64 L48 72 L54 64 Z", '#252E3D')
    ophead(b)
    headset(b)
    b.hl("M20 80 C24 72 32 68 40 67", 1.2, .5)
    # dish pictogram, top-right
    b.ln("M80 40 L80 30", '#6A7480', 3)
    b.p("M64 12 C66 26 80 30 90 26 C86 18 76 10 64 12 Z", 'white', '#8F9BA9', 1)
    b.hl("M67 14.4 C70 22 76 26 84 26", 1, .7)
    b.ln("M77 20 L88 9", '#6A7480', 1.4); b.c(88.6, 8.4, 2, REDL, '#7A2A20', .5)
    x, y, w, h = monitor(b, 12, 62, 72, 32)
    # signal bars + sat link
    for i, hh in enumerate((6, 10, 14, 18)):
        b.r(x + 6 + i * 6, y + h - 6 - hh, 4, hh, '#7FE0A0' if i < 3 else '#3FA865', op=.9)
    b.p("M52 72 C52 80 58 84 66 84 C66 78 60 72 52 72 Z", '#DCE6F0', '#8FD0FF', .6)
    b.ln("M68 80 C70 76 70 72 68 68 M72 82 C75 76 75 70 72 65", '#F2A93B', 1.2)
    b.ln("M40 70 L78 70", '#9CC2EA', .8, .6)
    screen_glint(b, x + 28, y, 30, h)

@icon('officer_female', '女军官', '人员')
def _(b):
    bust(b, 'olive', OS, shirt='#F3F1E6', tie='#B33A2C')
    # back hair
    b.p("M29 36 C26 52 28 64 34 68 L62 68 C68 64 70 52 67 36 Z", 'hair', '#211D1A', .8, extra="transform='translate(0 0)'")
    head(b, ears=False)
    # fringe and side hair
    b.p("M31 38 C28 20 38 14 48 14 C58 14 68 20 65 38 C63 31 60 27 56 25 C50 27 40 27 34 31 Z", 'hair', '#211D1A', .8)
    b.p("M31 36 C30 48 31 58 36 64 C33 56 33 46 35 38 Z M65 36 C66 48 65 58 60 64 C63 56 63 46 61 38 Z", 'hair', None, op=1)
    b.hl("M38 20 C42 17 47 16.4 52 16.6", 1, .4)
    # beret
    b.p("M26 28 C20 16 34 6 52 8 C68 10 74 20 69 28 C60 23 40 25 26 28 Z", 'jointG', JTS, 1)
    b.ln("M27.4 27.2 C40 24 60 22.6 68 27.4", '#D8B45A', 1)
    b.c(50, 5.6, 1.6, 'jointGdk', JTS, .5)
    b.c(36, 21, 3.6, 'gold', GOLDS, .6); b.p(star(36, 21.2, 2.3), RED)
    b.hl("M34 13 C40 9.4 48 8.6 56 10", 1.1, .5)
    # tablet
    b.g('rotate(-8 56 80)')
    b.r(40, 66, 32, 26, 'dkm2', DS, rx=2.4, sw=1)
    b.r(42.6, 68.6, 26.8, 21, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.ln("M45 73 L58 73 M45 77 L63 77", '#9CC2EA', 1, .7)
    for i, hh in enumerate((6, 9, 5)):
        b.r(55 + i * 4.4, 88 - hh, 3, hh, '#F2A93B' if i == 1 else '#8FD0FF', op=.9)
    b.p("M44 69 L52 69 L45 89 L43.6 89 Z", '#FFFFFF', op=.1)
    b.eg()
    hand(b, 40, 86, 3.4); hand(b, 74, 82, 3.4)

@icon('civilian_engineer', '军队文职／工程师', '人员')
def _(b):
    torso(b, 'whiteB', '#97A3B1')
    b.p("M38 64 L48 82 L58 64 Z", 'shirt', '#86A3C2', .6)
    b.p("M46 67 L50 67 L51.4 80 L48 84 L44.6 80 Z", BLUE, '#25578F', .5)
    b.p("M45.6 64 L50.4 64 L50 67.4 L46 67.4 Z", BLUE)
    b.p("M36 64.5 L48 90 L41 72 L31 68 Z", 'white', '#97A3B1', .8)
    b.p("M60 64.5 L48 90 L55 72 L65 68 Z", 'white', '#97A3B1', .8)
    # lanyard + ID
    b.ln("M40 64 L45 86 M56 64 L51 86", '#3D86D6', 1.4)
    b.r(42, 84, 12, 9, '#FFFFFF', '#6A7480', rx=1, sw=.7)
    b.r(42, 84, 12, 2.6, BLUE, rx=1)
    b.c(48, 89, 1.8, '#97A3B1'); b.ln("M45.4 92 C46 90.4 50 90.4 50.6 92", '#97A3B1', .8)
    # pocket pens
    b.ln("M20 80 L20 86 M23 80 L23 86", '#D9473A', 1.4); b.ln("M26 80 L26 86", '#3D86D6', 1.4)
    b.hl("M16 80 C20 72 28 68 35 67", 1.2, .6)
    head(b); hair(b)
    # blueprint roll
    b.g('rotate(-18 70 76)')
    b.r(62, 56, 12, 38, '#3D86D6', '#25578F', rx=5.5, sw=.9)
    b.ln("M64 62 L72 62 M64 66 L72 66 M64 74 L72 74", '#BFE3FF', 1, .8)
    b.r(62, 56, 12, 6, '#BFE3FF', '#25578F', rx=3, sw=.6)
    b.e(68, 57, 5.6, 2, '#FFFFFF', '#8EA5BF', .6)
    b.ln("M64 70 L72 70", '#F2C84B', 1.6)
    b.eg()
    hand(b, 76, 82, 3.4)

@icon('liaison', '联络官', '人员')
def _(b):
    bust(b, 'olive', OS, stripe=None)
    head(b); hair(b)
    garrison(b, 'olive', OS, '#D8B45A')
    # armband (left arm, viewer-left)
    b.p("M13 82 L25 76.4 L27.4 82 L14.4 88.4 Z", '#FFFFFF', '#97A3B1', .6)
    b.p("M14 84.4 L26.2 79 L27.4 82 L14.4 88.4 Z", BLUE, '#25578F', .4)
    b.ln("M18.6 80.4 L20.8 85.4", RED, 1.8)
    # walkie-talkie held at shoulder
    b.r(66, 50, 12, 28, 'dkm', DS, rx=2.6, sw=.9)
    b.ln("M70 50 L70 36", '#22272D', 2.2)
    b.c(70, 35.4, 1.3, '#22272D')
    b.r(68, 54, 8, 5, 'scr', '#0B1A2C', rx=.8, sw=.5)
    b.ln("M69.4 56.6 L74.6 56.6", '#7FE0A0', .8)
    for i in range(3):
        b.c(69.4 + i * 2.8, 64, .9, '#8794A3'); b.c(69.4 + i * 2.8, 67.4, .9, '#8794A3')
    b.c(76, 52.6, 1, REDL)
    b.hl("M67.6 56 L67.6 76", .9, .5)
    hand(b, 72, 80, 3.6)
    b.ln("M79 44 C83 46 83 52 79 54 M82 40 C89 44 89 54 82 58", '#F2A93B', 1.3)

KEYS = """cmd_army cmd_navy cmd_air cmd_rocket cmd_joint staff_army staff_navy staff_air staff_rocket staff_info
staff_logistics staff_intel staff_plan op_navy_cic op_air_controller op_space op_satcom officer_female civilian_engineer liaison""".split()

if __name__ == '__main__':
    import os, glob
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS if k in KEYS}
    assert set(byk) == set(KEYS), set(KEYS) ^ set(byk)
    old = set()
    for f in ['icons.js'] + [x for x in os.listdir('/home/claude/drawtool') if re.match(r'icons_[a-z]\.js$', x) and x != 'icons_h.js']:
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
    open('/home/claude/drawtool/icons_h.js', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), sorted(SZ)[-6:])
