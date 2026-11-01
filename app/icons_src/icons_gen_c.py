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


def small_uav(b, x, y, s=1.0, rot=0):
    d = "M0 -9 C1.6 -9 2.4 -7 2.6 -4 L11 4 L11 6.5 L2.4 4 L2 7 L4.8 9 L4.8 10.4 L0 9.6 L-4.8 10.4 L-4.8 9 L-2 7 L-2.4 4 L-11 6.5 L-11 4 L-2.6 -4 C-2.4 -7 -1.6 -9 0 -9 Z"
    b.g(f'translate({x} {y}) rotate({rot}) scale({s})')
    b.p(d, 'air', AS, 1.2)
    b.e(0, -4.5, 1.2, 2.2, 'canopy')
    b.eg()

CAT = '无人'

@icon('uav_flying_wing', '飞翼无人机', CAT)
def _(b):
    w = "M48 11 C50 11 51 12 52 14 L89 60 L88 67 L70 61 L58 68 L48 64 L38 68 L26 61 L8 67 L7 60 L44 14 C45 12 46 11 48 11 Z"
    pod = "M44.5 52 L51.5 52 L51.5 72 L44.5 72 Z"
    b.drop(w); b.drop(pod)
    b.p(pod, 'airdk', AS, 1)
    b.e(48, 77, 11, 2.4, 'prop'); b.ln("M37.5 77 L58.5 77", '#2E3640', 1.8)
    b.p(w, 'air', AS)
    b.p("M48 56 L26 61 L38 68 L48 64 L58 68 L70 61 Z", '#8D9BAC', op=.18)
    b.p("M44 52 C44 46 46 44 48 44 C50 44 52 46 52 52 L52 66 L44 66 Z", 'airV', AS, 1)
    b.e(48, 21, 3, 4, 'canopy', '#1B2D40', .8); glint(b, 47.2, 19.6, .9, .7)
    b.c(48, 33, 2.4, 'lens', '#1B2D40', .6)
    b.ln("M12 63.5 L30 58.5 M84 63.5 L66 58.5", '#6F7C8B', .8, .8)
    b.p("M7 60 L5 54 L9 55 L10 61 Z", 'airdk', AS, .8); b.p("M89 60 L91 54 L87 55 L86 61 Z", 'airdk', AS, .8)
    b.c(48, 77, 1.8, 'hub')
    b.hl("M46 15 L11 58.5", 1, .8); b.hl("M47 12.6 L44 16", 1, .6)
    leds(b, [(10, 62, REDL), (86, 62, GREEN)])

@icon('uav_ucav', '无人作战飞机', CAT)
def _(b):
    fus = "M48 5 C50.6 8 52 14 52.4 22 L53 60 L52 76 L50.5 86 L45.5 86 L44 76 L43 60 L43.6 22 C44 14 45.4 8 48 5 Z"
    wl = "M43.5 36 L9 62 L10 68 L43.5 60 Z"
    tl = "M44 68 L27 82 L28 87 L45 80 Z"
    wr, tr = mirror(wl), mirror(tl)
    for d in (wl, wr, tl, tr, fus): b.drop(d)
    b.p(tl, 'airdk', AS); b.p(tr, 'airdk', AS)
    b.p(wl, 'air', AS); b.p(wr, 'air', AS)
    b.p(fus, 'air', AS)
    b.p("M43.4 40 L40 44 L40 56 L43.2 54 Z", 'dkm2', AS, .8); b.p("M52.6 40 L56 44 L56 56 L52.8 54 Z", 'dkm2', AS, .8)
    b.e(48, 22, 3, 6, 'canopy', '#1B2D40', .8); glint(b, 47, 19.6, .9, 1.4)
    b.p("M45.5 86 L50.5 86 L51 89 L45 89 Z", '#2A3038')
    b.e(48, 88.6, 2.6, 1.3, '#F08A3C', op=.9)
    b.ln("M44 60 L11 66.4 M52 60 L85 66.4", '#8D9BAC', .8, .6)
    b.hl("M42.6 38 L10.8 62.2", 1, .85); b.hl("M45.4 10 C44.6 14 44.4 18 44.4 24", 1, .8)
    b.c(10, 66, 1.1, REDL); b.c(86, 66, 1.1, GREEN)

@icon('uav_tiltrotor', '倾转旋翼无人机', CAT)
def _(b):
    fus = "M48 9 C51.5 9 53 13 53 20 L52.4 66 L50.6 78 L45.4 78 L43.6 66 L43 20 C43 13 44.5 9 48 9 Z"
    wing = "M9 40 L87 40 L87 49 L9 49 Z"
    tail = "M44 66 L28 82 L31 85 L46 76 Z"; tail2 = mirror(tail)
    nl = "M9 36 L17 36 L17 58 C17 61 9 61 9 58 Z"; nr = mirror(nl)
    for d in (wing, fus, tail, tail2): b.drop(d)
    b.p(tail, 'airdk', AS); b.p(tail2, 'airdk', AS)
    b.p(fus, 'air', AS)
    b.p(wing, 'air', AS)
    for d in (nl, nr): b.p(d, 'airdk', AS, 1)
    b.e(48, 17, 3, 4, 'canopy', '#1B2D40', .8); glint(b, 47.2, 15.6, .9, .7)
    b.ln("M44 25 L44 56", '#FFFFFF', 1, .5)
    for cx in (13, 83):
        b.c(cx, 33, 13.5, 'prop', '#8D9BAC', .7)
        b.c(cx, 33, 13.5, 'none', '#FFFFFF', .6, .6)
    rotor(b, 13, 33, 13, 28); rotor(b, 83, 33, 13, -28)
    b.hl("M11 41.2 L40 41.2", 1, .8); b.hl("M56 41.2 L85 41.2", 1, .6)

@icon('uav_hexa', '六旋翼无人机', CAT)
def _(b):
    b.e(49, 52, 33, 33, 'shadow', op=.5)
    ang = (270, 330, 30, 90, 150, 210)
    pts = [(48 + 29 * math.cos(math.radians(a)), 50 + 29 * math.sin(math.radians(a))) for a in ang]
    for i, (x, y) in enumerate(pts):
        b.ln(f"M48 50 L{x:.1f} {y:.1f}", '#4A5664', 5.6)
        b.ln(f"M48 50 L{x:.1f} {y:.1f}", '#AEB9C5', 3.2)
        b.ln(f"M48 50 L{x:.1f} {y:.1f}", '#E9EEF3', .9)
    for i, (x, y) in enumerate(pts):
        b.c(round(x, 1), round(y, 1), 4.6, 'hub', '#1D2228', 1)
        rotor(b, round(x, 1), round(y, 1), 12.2, (30, -30, 30, -30, 30, -30)[i])
    hexd = "M48 36 L60 43 L60 57 L48 64 L36 57 L36 43 Z"
    b.p(hexd, 'dkm', '#1E2328', 1.2)
    b.p("M48 39 L57.5 44.5 L57.5 55.5 L48 61 L38.5 55.5 L38.5 44.5 Z", 'dkm2', op=.9)
    b.c(48, 50, 5.5, 'orange', '#8A4E17', .8)
    b.c(48, 50, 2.4, 'lens', '#1B2D40', .6); glint(b, 47.2, 49.2, .8, .5)
    b.hl("M37.4 44 L47 38.4", 1, .7)
    leds(b, [(48, 12.6, GREEN), (72, 36, GREEN), (72, 64, REDL), (48, 87, REDL), (24, 64, REDL), (24, 36, GREEN)][:0])
    leds(b, [(48, 35.6, GREEN), (48, 64.4, REDL)])

@icon('uav_fpv', 'FPV穿越机', CAT)
def _(b):
    b.sh(48, 86, 30, 3.2)
    # rear props (far)
    for x in (26, 70):
        b.ln(f"M48 48 L{x} 38", '#2A3038', 3)
    for x in (26, 70):
        b.e(x, 33.5, 11.5, 3.4, 'prop', '#8D9BAC', .6)
        b.ln(f"M{x-10} 33.5 L{x+10} 33.5", '#2E3640', 1.4)
        b.r(x - 2, 35.5, 4, 4.5, 'dkm', '#1E2328', sw=.8)
    # payload
    b.ln("M48 62 L48 66", '#2A3038', 2)
    b.p("M42 74 L38 80 L42 79 Z M54 74 L58 80 L54 79 Z", '#8E3129', '#4A1612', .6)
    b.p("M42.4 68 C42.4 65.6 44 64.6 48 64.6 C52 64.6 53.6 65.6 53.6 68 L53.6 76 C53.6 79 51 82 48 83 C45 82 42.4 79 42.4 76 Z", 'red', '#4A1612', 1)
    b.r(42.4, 69.5, 11.2, 2.4, '#F3E3C6')
    b.hl("M44.4 67 L44.4 76", .9, .6)
    # near arms and props
    for x, y in ((14, 55), (82, 55)):
        b.ln(f"M48 50 L{x} {y}", '#2A3038', 4.2)
        b.ln(f"M48 50 L{x} {y}", '#5B6672', 2)
    # frame
    b.r(33, 46, 30, 8, 'dkm2', '#0B0D10', rx=2.4, sw=1)
    b.r(36, 38.4, 24, 8, 'orange', '#8A4E17', rx=1.8, sw=.9)
    b.ln("M42 38.6 L42 46 M54 38.6 L54 46", '#2A3038', 1.8)
    b.hl("M37 40 L59 40", .9, .6)
    b.ln("M58 38.5 L63 25", '#2A3038', 1.1); b.c(63, 24.6, 1.3, GREEN)
    b.r(42.5, 52, 11, 8, 'dkm', '#0B0D10', rx=1.5, sw=.8)
    b.c(48, 56, 2.8, 'lens', '#05101C', .6); glint(b, 47.2, 55.2, .8, .5)
    for x, y in ((14, 55), (82, 55)):
        b.r(x - 2.6, y - 2, 5.2, 6.5, 'dkm', '#1E2328', rx=1, sw=.8)
        b.e(x, y - 3.5, 13, 3.9, 'prop', '#8D9BAC', .6)
        b.ln(f"M{x-12} {y-3.5} L{x+12} {y-3.5}", '#2E3640', 1.6)
        b.c(x, y - 3.5, 1.6, 'hub')
    for x in (26, 70): b.c(x, 33.5, 1.4, 'hub')

@icon('uav_cargo', '物流运输无人机', CAT)
def _(b):
    b.sh(48, 86, 32, 3.2)
    for x, y in ((30, 17), (66, 17)):
        b.ln(f"M48 34 L{x} {y+4}", '#4A5664', 3); b.ln(f"M48 34 L{x} {y+4}", '#AEB9C5', 1.4)
    for x, y, rx in ((30, 17, 9), (66, 17, 9)):
        b.e(x, y, rx, 2.6, 'prop', '#8D9BAC', .5)
        b.ln(f"M{x-rx+1} {y} L{x+rx-1} {y}", '#2E3640', 1.2)
        b.r(x - 1.5, y, 3, 4, 'dkm', '#1E2328', sw=.6)
    for x, y in ((14, 26), (82, 26)):
        b.ln(f"M48 36 L{x} {y+4}", '#4A5664', 4); b.ln(f"M48 36 L{x} {y+4}", '#AEB9C5', 2)
    for x, y in ((14, 26), (82, 26)):
        b.r(x - 2, y, 4, 5, 'dkm', '#1E2328', sw=.6)
        b.e(x, y, 13, 3.6, 'prop', '#8D9BAC', .6)
        b.ln(f"M{x-12} {y} L{x+12} {y}", '#2E3640', 1.6); b.c(x, y, 1.5, 'hub')
    b.ln("M30 42 L26 72 M66 42 L70 72", '#4A5664', 2); b.ln("M22 73 L34 73 M62 73 L74 73", '#2A3038', 2.4)
    b.r(30, 30, 36, 13, 'air', AS, rx=5)
    b.r(34, 32.4, 14, 6, 'canopy', '#1B2D40', rx=2.4, sw=.7); glint(b, 38, 34, 2, .7)
    leds(b, [(58, 36.5, GREEN), (62, 36.5, AMBER)])
    b.hl("M33 32 C36 30.6 42 30.4 46 30.6", .9, .7)
    b.ln("M40 43 L40 48 M56 43 L56 48", '#2A3038', 2)
    b.p("M33 48 L63 48 L63 70 L33 70 Z", 'gold', '#6E521A', 1.1)
    b.p("M33 48 L63 48 L63 53 L33 53 Z", '#FFFFFF', op=.22)
    b.r(46, 48, 4, 22, '#F3E3C6', op=.8)
    b.r(36, 58, 9, 8, '#FFFFFF', '#8A6A20', rx=.8, sw=.7)
    b.ln("M37.6 61 L43.4 61 M37.6 63.4 L42 63.4", '#6E521A', .8)
    b.hl("M34 49.5 L62 49.5", .9, .6)

@icon('uav_tethered', '系留无人机', CAT)
def _(b):
    b.sh(48, 86, 40, 3.6)
    # cable
    cab = "M46 60 C44 50 54 44 49 33 C48 30 48 28 48 26"
    b.ln(cab, '#1E2328', 3); b.ln(cab, '#F2A93B', 1.6); b.ln(cab, '#FFFFFF', .6, .6, extra="stroke-dasharray='2 3'")
    # drone
    b.ln("M48 22 L30 13 M48 22 L66 13", '#4A5664', 3); b.ln("M48 22 L30 13 M48 22 L66 13", '#AEB9C5', 1.4)
    for x in (30, 66):
        b.r(x - 1.5, 12, 3, 4.5, 'dkm', '#1E2328', sw=.6)
        b.e(x, 11.5, 12, 3.2, 'prop', '#8D9BAC', .6)
        b.ln(f"M{x-11} 11.5 L{x+11} 11.5", '#2E3640', 1.4); b.c(x, 11.5, 1.4, 'hub')
    b.r(40, 15, 16, 11, 'air', AS, rx=4.4)
    b.r(43, 17.4, 8, 4.6, 'canopy', '#1B2D40', rx=1.8, sw=.6)
    b.c(48, 27, 2.2, 'lens', '#1B2D40', .5)
    b.hl("M42 16.6 C44 15.6 47 15.4 50 15.6", .8, .7)
    # ground vehicle
    b.r(10, 62, 56, 14, 'land', LS, rx=1.5)
    b.p("M66 66 L66 62 L76 62 L83 70 L84 76 L66 76 Z", 'land', LS)
    b.p("M72 64 L76 64 L80 70 L72 70 Z", 'canopy', '#1B2D40', .6)
    b.e(36, 55, 15, 6, 'cylM', MS, 1)
    b.r(21, 55, 30, 8, 'cylM', MS, rx=0)
    b.e(36, 63, 15, 3.4, 'metal3', MS, .8)
    b.e(36, 55, 15, 5.4, 'metal', MS, 1)
    b.e(36, 55, 9, 3.2, 'dkm2', op=.9)
    b.ln("M24 57 C28 59.5 44 59.5 48 57", '#F2A93B', 1.6)
    b.ln("M23 60.4 C28 62.6 44 62.6 49 60.4", '#F2A93B', 1.3)
    b.c(46, 55.4, 1.7, '#2A2E33'); b.ln("M45 55.4 L46 60", '#F2A93B', 1.8)
    for x in (22, 36, 52): b.ln(f"M{x} 65 L{x} 73", '#3E4C29', 1, .7)
    b.hl("M12 63.2 L64 63.2")
    for wx in (23, 55, 76): wheel(b, wx, 77, 6.2)
    leds(b, [(60, 68, GREEN), (60, 72, AMBER)])

@icon('uav_micro', '微型扑翼无人机', CAT)
def _(b):
    wl = "M45 47 C38 30 20 18 8 22 C3 36 16 52 45 54 Z"
    wl2 = "M45 56 C34 56 20 62 15 74 C26 80 40 70 46 59 Z"
    wr, wr2 = mirror(wl), mirror(wl2)
    b.e(48, 54, 36, 30, 'shadow', op=.35)
    for d in (wl2, wr2):
        b.p(d, '#CFE6FA', '#6F95BB', 1, op=.8)
    for d in (wl, wr):
        b.p(d, '#D9ECFB', '#6F95BB', 1.1, op=.85)
    for v in ("M45 49 L10 24", "M45 50 L7 33", "M45 51.5 L9 42", "M45 53 L20 49", "M45 58 L18 73", "M46 58 L28 76"):
        b.ln(v, '#5F85AD', .8, .85)
        b.ln(re_mirror(v), '#5F85AD', .8, .85)
    b.hl("M44 47 C38 31 22 21 10 23.4", 1.1, .9); b.hl("M52 47 C58 31 74 21 86 23.4", 1.1, .5)
    b.p("M44 46 C44 40 45.6 38 48 38 C50.4 38 52 40 52 46 L51 70 C50.6 74 49.4 76 48 76 C46.6 76 45.4 74 45 70 Z", 'dkm', '#1E2328', 1)
    b.c(48, 31, 5.6, 'airV', AS, 1)
    b.c(45.6, 30.4, 1.9, 'lens', '#05101C', .5); b.c(50.4, 30.4, 1.9, 'lens', '#05101C', .5)
    b.ln("M46 24 L43 17 M50 24 L53 17", '#2A3038', 1)
    b.p("M48 74 L43 90 L48 86 L53 90 Z", 'orange', '#8A4E17', .9)
    b.hl("M46.2 41 L46.2 62", .9, .5)
    b.c(48, 46, 1.2, GREEN)

def re_mirror(d):
    return mirror(d.replace('M', 'M ').replace('L', ' L '))

@icon('uav_solar', '太阳能长航时无人机', CAT)
def _(b):
    wing = "M2 42 L94 42 L94 56 L2 56 Z"
    b.circle = None
    b.drop(wing)
    b.ln("M48 56 L48 84", '#4C5967', 2.4)
    b.p("M34 80 L62 80 L62 86 L34 86 Z", 'air', AS, 1)
    b.p("M44 50 L52 50 L52 68 C52 70 50 71 48 71 C46 71 44 70 44 68 Z", 'air', AS, 1)
    b.p(wing, 'solar', '#10243F', 1.2)
    for i in range(1, 15):
        x = 2 + i * 92 / 15
        b.ln(f"M{x:.1f} 42.6 L{x:.1f} 55.4", '#9CC2EE', .7, .55)
    b.ln("M2.6 49 L93.4 49", '#9CC2EE', .7, .55)
    b.p("M2 42 L94 42 L94 45 L2 45 Z", '#FFFFFF', op=.18)
    b.p("M41 42 L55 42 L55 56 L41 56 Z", 'air', AS, 1)
    b.e(48, 48, 3, 4, 'canopy', '#1B2D40', .7)
    for x in (16, 33, 63, 80):
        b.r(x - 1.6, 33, 3.2, 10, 'airdk', AS, rx=1.2, sw=.8)
        b.c(x, 31.5, 5.6, 'prop', '#8D9BAC', .5)
        b.ln(f"M{x-4.8} {31.5-1.6} L{x+4.8} {31.5+1.6}", '#2E3640', 1.4); b.c(x, 31.5, 1.2, 'hub')
    b.hl("M3 43.2 L93 43.2", 1, .7)
    # sun
    for a in range(0, 360, 45):
        r = math.radians(a)
        b.ln(f"M{80+7.4*math.cos(r):.1f} {16+7.4*math.sin(r):.1f} L{80+11*math.cos(r):.1f} {16+11*math.sin(r):.1f}", '#E7A92B', 1.8)
    b.c(80, 16, 5.6, 'gold', '#8A6A20', 1)
    b.c(78.4, 14.4, 1.8, '#FFFFFF', op=.6)

@icon('uav_catapult', '弹射起飞无人机', CAT)
def _(b):
    b.sh(48, 87, 40, 3.4)
    # supports
    b.p("M13 86 L20 70 L27 70 L25 86 Z", 'dkm', '#1E2328', 1)
    b.p("M54 86 L60 56 L69 54 L72 86 Z", 'dkm', '#1E2328', 1)
    b.ln("M30 85 L58 64", '#4A5664', 2)
    b.r(8, 84, 70, 4, 'metal3', MS, rx=1.6, sw=.8)
    b.g('rotate(-16 48 61)')
    b.r(6, 58, 86, 6, 'metal3', MS, rx=2)
    b.r(8, 59.4, 82, 1.6, '#DDE3E9', rx=.8, op=.7)
    b.r(10, 64, 34, 5, 'cylM', MS, rx=2.2, sw=.9)
    b.r(44, 64, 3, 5, '#2A3038', rx=.6)
    b.ln("M12 71 L30 71", '#F2A93B', 1.2, .0)
    # shuttle
    b.r(36, 55.4, 12, 3.4, 'orange', '#8A4E17', rx=1, sw=.8)
    # uav on rail (side)
    b.ln("M10 44 L10 53", '#4A5664', 0)
    b.p("M30 53 L32 44 L35.6 44 L40 52 Z", 'airdk', AS, 1)
    b.p("M31 49 L22 45 L24 52 Z", 'airdk', AS, .8) if False else None
    b.p("M38 53 C40 49.6 46 48 56 48 L74 48.4 C80 49 84 51 84 53 C84 55.4 80 56.6 72 56.8 L46 56.4 C40 56 38 55 38 53 Z", 'white', WS, 1.1)
    b.p("M52 49 L63 49 L70 41 L58 41 Z", 'whitedk', WS, 1)
    b.p("M50 50 L62 50 L54 58 L42 58 Z", '#8F9BA9', op=0)
    b.p("M62 49.6 C66 47 71 47.6 72 49.6 Z", 'canopy', '#1B2D40', .6)
    b.e(86, 53, 1.6, 7, 'prop'); b.ln("M86 46.4 L86 59.6", '#2E3640', 1.6)
    b.hl("M40 51 L76 50", .9, .8)
    b.eg()
    # motion lines
    b.ln("M70 80 L88 72", '#3D86D6', 1.4, .0)
    b.ln("M12 40 L26 34 M8 47 L20 42", '#3D86D6', 1.6, .55, extra="stroke-dasharray='4 3'")

@icon('uav_coaxial', '共轴双旋翼无人直升机', CAT)
def _(b):
    b.sh(48, 86, 30, 3.2)
    b.ln("M30 77 L30 82 L66 82 L66 77", '#3A434E', 0)
    b.ln("M33 66 L30 80 M63 66 L66 80", '#3A434E', 1.8)
    b.ln("M22 80.4 L72 80.4 Q75 80.4 76 78.4", '#3A434E', 2.4); b.ln("M23 80 L70 80", '#8592A2', .6)
    # tail stub + fins
    b.p("M64 58 L84 56 L86 50 L90 50 L88 62 L64 66 Z", 'airdk', AS, 1)
    b.p("M80 56 L83 44 L88 44 L88 58 Z", 'airdk', AS, 1)
    body = "M18 58 C18 48 28 44 40 44 L56 44 C66 44 74 50 74 58 C74 68 66 72 56 72 L34 72 C24 72 18 68 18 58 Z"
    b.p(body, 'airV', AS)
    b.p("M20 55 C22 49 28 46 36 45.4 L40 45 L36 58 L20 60 Z", 'canopy', '#1B2D40', .8)
    glint(b, 27, 49, 2.6, .9)
    b.p("M22 52 C24 49 28 47.4 33 46.6", '#FFFFFF', 0)
    b.r(44, 50, 14, 8, 'airdk', AS, rx=2, sw=.8)
    leds(b, [(66, 62, GREEN)])
    b.c(24, 70, 4.2, 'sphere', MS, .9); b.c(22.8, 70.6, 2.2, 'lens', '#05101C', .5)
    # mast + rotors
    b.r(44, 26, 4.4, 20, 'metal3', AS, rx=1)
    b.r(40, 41, 12.4, 4, 'metal2', AS, rx=1.2, sw=.8)
    b.e(46, 36, 40, 3.4, 'prop')
    b.r(6, 35, 80, 2.2, '#2E3640', rx=1.1); b.ln("M8 35.6 L84 35.6", '#8592A2', .5)
    b.e(46, 24, 40, 3.4, 'prop')
    b.r(6, 23, 80, 2.2, '#2E3640', rx=1.1); b.ln("M8 23.6 L84 23.6", '#8592A2', .5)
    b.e(46, 23.2, 4.6, 2.4, 'hub', '#1D2228', .8)
    b.hl("M22 49 C26 46 32 45.4 38 45.2", .9, .7)

@icon('uav_ducted', '涵道风扇无人机', CAT)
def _(b):
    b.sh(48, 88, 32, 3.4)
    b.ln("M24 60 L20 85 M72 60 L76 85", '#3A434E', 2.2)
    b.ln("M15 85.6 L25 85.6 M71 85.6 L81 85.6", '#2A3038', 2.6)
    # pod
    b.r(38, 56, 20, 22, 'air', AS, rx=6)
    b.c(48, 78, 5.2, 'sphere', MS, .9); b.c(48, 78.6, 2.8, 'lens', '#05101C', .5); glint(b, 47, 77.6, .9, .6)
    b.r(41, 60, 14, 6, 'canopy', '#1B2D40', rx=2.4, sw=.7)
    # duct
    b.p("M13 38 L13 49 C13 57 28 63 48 63 C68 63 83 57 83 49 L83 38 Z", 'metal2', MS, 1.2)
    b.p("M13 43 L13 49 C13 57 28 63 48 63 C68 63 83 57 83 49 L83 43 C80 51 66 56 48 56 C30 56 16 51 13 43 Z", '#FFFFFF', op=.14)
    b.e(48, 38, 35, 15.5, 'metal', MS, 1.2)
    b.e(48, 38, 30, 12, 'dkm2', '#1E2328', 1)
    for a in range(0, 360, 45):
        r = math.radians(a + 15)
        x, y = 48 + 28.4 * math.cos(r), 38 + 11 * math.sin(r)
        b.ln(f"M48 38 L{x:.1f} {y:.1f}", '#7A8795', 3.2)
        b.ln(f"M48 38 L{x:.1f} {y:.1f}", '#C9D1DA', 1.3)
    b.e(48, 38, 8, 3.6, '#8FA0B3', '#1E2328', .8, op=.35)
    b.e(48, 37.4, 4.4, 2.8, 'hub', '#1D2228', .8)
    b.ln("M48 50 L48 56", '#3A434E', 0)
    b.hl("M14 36 C18 28 32 24 48 24", 1.2, .85)
    leds(b, [(15, 45, REDL), (81, 45, GREEN)])

@icon('uav_seaplane', '水上起降无人机', CAT)
def _(b):
    b.sh(48, 84, 30, 2.4) if False else None
    # high wing slab (3/4)
    wing = "M30 31 L72 31 L84 22 L42 22 Z"
    fus = "M10 50 L26 46 L68 42 C79 42 85 46 85 50 C85 54 79 57 68 57 L28 55 Z"
    fin = "M11 50 L8 34 L16 34 L30 47 Z"
    b.drop(wing, 2, 3, .14)
    b.p(fin, 'airdk', AS)
    b.p("M12 48 L4 44 L6 50 Z", 'airdk', AS, .8)
    b.ln("M44 32 L50 44 M66 32 L62 43", '#4A5664', 1.6)
    # floats
    for fx, fy, sh_ in ((26, 63, 'seadk'), (30, 66, 'sea')):
        pass
    b.ln("M34 55 L36 64 M62 56 L60 64", '#4A5664', 2)
    b.p("M24 62 L74 62 C80 62 82 64.6 80 67 L28 67 C21 67 19 63.6 24 62 Z", 'seadk', MS, 1)
    b.ln("M30 63.6 L70 63.6", '#FFFFFF', .8, .7)
    b.p(fus, 'air', AS)
    b.p("M66 43 C73 42.6 79 44 82 48 L66 48 Z", 'canopy', '#1B2D40', .8)
    b.ln("M14 50 L66 48", '#8D9BAC', .7, .7)
    b.p(wing, 'air', AS)
    b.p("M30 31 L72 31 L74.5 29 L33 29 Z", '#FFFFFF', op=.3)
    b.e(86.5, 49, 1.6, 8, 'prop'); b.ln("M86.5 41 L86.5 57", '#2E3640', 1.6)
    b.hl("M38 23.4 L80 23.4", 1, .7)
    water(b, 62)
    b.p("M24 66.4 L80 66.4 L80 68 L24 68 Z", '#FFFFFF', op=.0)
    b.ln("M18 70 Q24 67.6 30 70 T42 70 M54 70 Q60 67.6 66 70 T78 70", '#FFFFFF', 1.2, .7)

@icon('uav_ew', '电子战无人机', CAT)
def _(b):
    fus = "M48 32 C51.5 32 53 36 53 42 L52.6 72 L51 86 L45 86 L43.4 72 L43 42 C43 36 44.5 32 48 32 Z"
    wl = "M43 48 L8 68 L8 74 L43 64 Z"; wr = mirror(wl)
    tl = "M44 76 L33 86 L34 89 L45 83 Z"; tr = mirror(tl)
    for d in (wl, wr, fus): b.drop(d)
    for d in (tl, tr): b.p(d, 'airdk', AS, 1)
    b.p(fus, 'air', AS)
    b.p(wl, 'air', AS); b.p(wr, 'air', AS)
    # pods
    for x in (22, 74):
        b.r(x - 3, 58, 6, 18, 'white', WS, rx=3, sw=.9)
        b.r(x - 3, 61, 6, 2.2, 'red'); b.r(x - 3, 68.5, 6, 2.2, 'red')
        b.ln(f"M{x} 58 L{x} 52", '#3A434E', 1); b.c(x, 51.6, 1.1, REDL)
    b.e(48, 41, 2.6, 4.6, 'canopy', '#1B2D40', .8); glint(b, 47.2, 39.4, .8, 1.2)
    b.ln("M48 55 L48 46", '#3A434E', 0)
    b.p("M46.4 56 L49.6 56 L49 64 L47 64 Z", '#3A434E')
    b.hl("M42 49 L10 68", 1, .85); b.hl("M45.6 36 C44.8 39 44.6 42 44.6 46", .9, .8)
    # jamming arcs
    for i, r in enumerate((11, 20, 29)):
        a1, a2 = math.radians(-135), math.radians(-45)
        x1, y1 = 48 + r * math.cos(a1), 32 + r * math.sin(a1)
        x2, y2 = 48 + r * math.cos(a2), 32 + r * math.sin(a2)
        b.ln(f"M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}", '#E8742F', 2.6 - i * .3, 1 - i * .18)
    b.c(48, 32, 1.4, '#E8742F', op=.0)
    for sgn in (-1, 1):
        b.ln(f"M{48+sgn*19} 46 L{48+sgn*14} 42 L{48+sgn*17} 39 L{48+sgn*12} 35", '#F08A3C', 1.3, .8)

@icon('uav_relay', '通信中继无人机', CAT)
def _(b):
    b.sh(46, 86, 34, 2.8)
    fin = "M12 60 L7 45 L15 45 L30 57 Z"
    fus = "M10 60 L28 57 L66 53 C78 53 85 57 85 61 C85 65 78 67 66 67 L30 65 Z"
    wing = "M36 64 L68 64 L82 76 L48 76 Z"
    b.drop(wing, 2, 3, .12)
    b.p(fin, 'airdk', AS)
    b.p("M12 61 L5 59 L7 65 Z", 'airdk', AS, .8)
    b.p(fus, 'air', AS)
    b.p(wing, 'airdk', AS)
    b.p("M36 64 L68 64 L70 66 L38 66 Z", '#FFFFFF', op=.3)
    b.p("M68 54 C75 53.6 81 55.4 83 59.4 L68 60 Z", 'canopy', '#1B2D40', .8)
    b.e(86.5, 61, 1.6, 8, 'prop'); b.ln("M86.5 53 L86.5 69", '#2E3640', 1.6)
    # dorsal dome + mast
    b.p("M38 56 C38 47 44 44 52 44 C60 44 64 48 64 55 Z", 'sphere', MS, 1.1)
    b.p("M42 50 C44 47 48 46 52 46", '#FFFFFF', 0)
    b.hl("M41 51 C43 47.6 47 46 52 45.6", 1, .9)
    b.ln("M52 44 L52 20", '#4A5664', 2.2); b.ln("M52 44 L52 20", '#C9D1DA', .9)
    for y, hw in ((24, 6), (30, 4.6)):
        b.ln(f"M{52-hw} {y} L{52+hw} {y}", '#2E3640', 1.8); b.ln(f"M{52-hw} {y} L{52+hw} {y}", '#C9D1DA', .7)
    b.c(52, 19, 2, 'node', '#1F4F8C', .6)
    for i, r in enumerate((8, 14, 20)):
        for sgn in (-1, 1):
            a = math.radians(40)
            x1, y1 = 52 + sgn * r * math.cos(a), 19 - r * math.sin(a)
            x2, y2 = 52 + sgn * r * math.cos(a), 19 + r * math.sin(a)
            sw = 1 if sgn > 0 else 0
            b.ln(f"M{x1:.1f} {y1:.1f} A{r} {r} 0 0 {sw} {x2:.1f} {y2:.1f}", '#3D86D6', 2 - i * .3, 1 - i * .2)
    b.hl("M12 58 L60 54.6", .9, .6)
    b.c(15, 46, 0.1, REDL, op=0)

@icon('uav_recon_small', '手抛式侦察无人机', CAT)
def _(b):
    b.g('rotate(14 48 40)')
    fus = "M48 8 C50.6 8 51.8 11 51.8 16 L51.2 54 L49.8 62 L46.2 62 L44.8 54 L44.2 16 C44.2 11 45.4 8 48 8 Z"
    wing = "M14 27 L44.4 24 L51.6 24 L82 27 L82 33 L51.6 31 L44.4 31 L14 33 Z"
    tail = "M38 52 L44.6 50 L51.4 50 L58 52 L58 56 L51.4 56 L44.6 56 L38 56 Z"
    for d in (wing, fus, tail): b.drop(d, 2, 3, .14)
    b.p(tail, 'airdk', AS, 1)
    b.p(fus, 'air', AS)
    b.p(wing, 'air', AS)
    b.e(48, 6.8, 7.2, 1.8, 'prop'); b.ln("M40.8 6.8 L55.2 6.8", '#2E3640', 1.4)
    b.e(48, 19, 2, 3.2, 'canopy', '#1B2D40', .6)
    b.c(48, 32, 1.8, 'lens', '#1B2D40', .5)
    b.p("M14 27 L14 33 L17 32.6 L17 27 Z", 'orange', '#8A4E17', .7); b.p("M82 27 L82 33 L79 32.6 L79 27 Z", 'orange', '#8A4E17', .7)
    b.hl("M16 28 L44 25.4", .9, .8); b.hl("M46.2 12 L46.2 24", .9, .7)
    b.eg()
    # sleeve + hand
    b.p("M30 96 L36 76 L62 76 L66 96 Z", 'uniform', '#26394B', 1.1)
    b.r(34, 72, 30, 6, '#33495F', '#1E2E3E', rx=2, sw=.9)
    b.hl("M38 80 L35 94", 1, .35)
    b.p("M38 72 C34 66 36 56 44 54 L58 54 C64 54 65 62 62 72 Z", 'skin', '#7C5F3F', 1.1)
    for i, x in enumerate((43, 49, 55, 60.5)):
        b.r(x - 2.6, 52 - (1 if i in (1, 2) else 0), 5.2, 9, 'skin', '#7C5F3F', rx=2.6, sw=.9)
    b.ln("M43 60.6 L43 64 M49 60.6 L49 64 M55 60.6 L55 64", '#A98560', .7, .7)
    b.p("M38 66 C32 64 31 57 36 56 C40 55 41 60 41 64 Z", 'skin', '#7C5F3F', 1)
    b.hl("M44 56 C47 54.6 54 54.6 58 56", .8, .5)
    b.ln("M70 30 L84 24 M74 40 L88 35", '#3D86D6', 1.4, .55, extra="stroke-dasharray='4 3'")

@icon('drone_nest', '无人机机巢', CAT)
def _(b):
    b.sh(48, 84, 42, 4)
    front = "M10 50 L10 78 L76 78 L76 50 Z"
    right = "M76 50 L88 38 L88 66 L76 78 Z"
    top = "M10 50 L22 38 L88 38 L76 50 Z"
    # back lid (open)
    lid = "M24 38 L88 38 L85 14 L27 14 Z"
    b.p(lid, 'metal2', MS, 1.2)
    b.p("M24 38 L88 38 L87 30 L25 30 Z", '#FFFFFF', op=.14)
    b.p("M30 16.4 L83 16.4 L84 22 L29 22 Z", '#FFFFFF', op=.22)
    b.p(right, 'metal3', MS)
    b.p(front, 'metal', MS)
    b.p(top, 'metal2', MS)
    b.p("M20 48 L28 41 L78 41 L70 48 Z", '#1B232B', '#5A666F', 1)
    b.p("M28 41 L78 41 L76 42.6 L26 42.6 Z", '#000000', op=.3)
    # landing mark
    b.e(49, 44.6, 10, 2.4, 'none', '#F2A93B', .9)
    # drone hovering
    b.ln("M49 30 L38 26 M49 30 L60 26 M49 33 L38 38 M49 33 L60 38", '#2A3038', 1.8)
    for x, y, rx in ((38, 25.4, 7), (60, 25.4, 7), (38, 37.4, 8), (60, 37.4, 8)):
        b.e(x, y, rx, 1.9, 'prop', '#8D9BAC', .4)
        b.ln(f"M{x-rx+1} {y} L{x+rx-1} {y}", '#2E3640', 1)
    b.r(43, 28.6, 12, 7, 'air', AS, rx=3, sw=.9)
    b.r(45.6, 30, 6.8, 3.4, 'canopy', rx=1.4)
    b.c(49, 36.6, 1.4, 'lens')
    # front details
    b.r(16, 56, 40, 16, 'metal2', MS, rx=1.2, sw=.9)
    for y in (59, 63, 67):
        b.ln(f"M19 {y} L53 {y}", '#59656F', 1.1)
    b.r(60, 56, 11, 16, 'metal3', MS, rx=1, sw=.9)
    b.c(65.5, 61, 2.2, '#2A3038'); b.c(65.5, 61, 1.2, 'glass')
    leds(b, [(63, 67, GREEN), (68, 67, AMBER)])
    b.r(10, 50, 66, 2.4, 'glass', op=.0)
    b.p("M10 50 L76 50 L76 52.4 L10 52.4 Z", '#3D86D6', op=.75)
    b.hl("M11 53.6 L11 76", .9, .6)
    b.p("M76 78 L88 66 L88 70 L76 82 Z", '#000000', op=0)
    # mast
    b.ln("M83 39 L83 22", '#4A5664', 2); b.ln("M83 39 L83 22", '#C9D1DA', .8)
    b.c(83, 20, 2.2, 'node', '#1F4F8C', .6)
    b.ln("M77 17 A8 8 0 0 1 77 23.8", '#3D86D6', 1.5, .0)
    b.ln("M89 16 Q92 20 89 24 M92.6 14 Q97 20 92.6 26", '#3D86D6', 1.4, .8)
    b.hl("M12 51.2 L22 40", .9, .8)

@icon('drone_launcher', '无人机集群发射车', CAT)
def _(b):
    _truck_base(b, (16, 32, 58, 77))
    b.ln("M24 60 L38 50", '#3E4C29', 2.6)
    b.g('rotate(-20 12 58)')
    b.r(8, 36, 54, 22, 'land', LS)
    for x in (20, 32, 44): b.ln(f"M{x} 36.5 L{x} 57.5", '#3E4C29', 1, .7)
    b.p("M62 36 L72 34 L72 60 L62 58 Z", 'dkm', DS, .9)
    for r_ in range(3):
        for c_ in range(2):
            x, y = 64 + c_ * 3.6, 38.6 + r_ * 6.6
            b.r(x, y, 3, 5, '#0B0F14', rx=.5, sw=0)
    for (x, y) in ((65.5, 40.4), (65.5, 53.4), (69, 46.8)):
        b.ln(f"M{x} {y} L{x-2} {y}", '#E8EDF2', 1.4)
    b.hl("M9 37.6 L60 37.6")
    b.eg()
    for (x, y, s, rot) in ((58, 20, .8, 55), (72, 14, .7, 55), (80, 28, .7, 55)):
        small_uav(b, x, y, s, rot)
    b.ln("M44 30 L54 24 M52 40 L66 30 M60 44 L76 36", '#3D86D6', 1.4, .5, extra="stroke-dasharray='3 3'")

KEYS = """uav_flying_wing uav_ucav uav_tiltrotor uav_hexa uav_fpv uav_cargo uav_tethered uav_micro uav_solar uav_catapult uav_coaxial uav_ducted uav_seaplane uav_ew uav_relay uav_recon_small drone_nest drone_launcher""".split()

if __name__ == '__main__':
    import re as _re, os
    D = '/home/claude/drawtool'
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    assert set(byk) == set(KEYS), set(KEYS) ^ set(byk)
    old = set()
    for f in os.listdir(D):
        if f.startswith('icons') and f.endswith('.js') and f != 'icons_c.js':
            old |= set(_re.findall(r"key: '([^']+)'", open(os.path.join(D, f), encoding='utf-8').read()))
    clash = old & set(KEYS); assert not clash, clash
    SZ = []
    lines = ['ICON_LIB.push(...[']
    for k in KEYS:
        _, n, c, fn = byk[k]
        b = B(k); fn(b)
        s = b.svg()
        s = _re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
        s = _re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
        assert '"' not in s
        SZ.append((len(s), k))
        lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
    lines.append(']);')
    open(os.path.join(D, 'icons_c.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), 'largest', sorted(SZ)[-6:])
