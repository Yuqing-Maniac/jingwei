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


def cyl(b, cx, y, rx, h, ry=5, fill='cylM', top='metal', st=MS, sw=1.2, hl=True):
    b.p(f"M{cx-rx} {y} L{cx-rx} {y+h} A{rx} {ry} 0 0 0 {cx+rx} {y+h} L{cx+rx} {y} Z", fill, st, sw)
    b.e(cx, y, rx, ry, top, st, sw)
    if hl: b.hl(f"M{cx-rx+3} {y+ry+2} L{cx-rx+3} {y+h-1}", 1.2, .7)


BL = '#25578F'
JAM = '#F08A2A'

def plate_dots(b, x, y, w, h, nx, ny, r=2.2):
    for i in range(nx):
        for j in range(ny):
            b.c(round(x + (i + .5) * w / nx, 1), round(y + (j + .5) * h / ny, 1), r, '#D7E8FA')

def trio(b, pts, r=5.6):
    path = 'M' + ' L'.join(f'{x} {y}' for x, y in list(pts) + [pts[0]])
    b.ln(path, '#14365F', 5.4)
    b.ln(path, '#8FD0FF', 3.4)
    for x, y in pts:
        b.c(x, y, r, 'node', '#1F4F8C', 1.1)
        b.e(round(x - r * .28, 1), round(y - r * .36, 1), round(r * .4, 1), round(r * .2, 1), '#FFFFFF', op=.82)

def hcyl(b, x, y, w, ry, fill='cylM', lens='lens', lst='#05101C'):
    rw = max(ry * .42, 1.5)
    b.p(
        f'M{x} {y - ry} L{x + w} {y - ry} A{rw:.1f} {ry} 0 0 1 {x + w} {y + ry} '
        f'L{x} {y + ry} A{rw:.1f} {ry} 0 0 1 {x} {y - ry} Z',
        fill, MS, 1.05,
    )
    b.e(x + w, y, round(rw, 1), ry, lens, lst, 1.05)
    b.hl(f'M{x + 2} {y - ry + 2.2} L{x + w - 1} {y - ry + 2.2}', 1.05, .8)
    glint(b, x + w - rw * .2, y - ry * .32, max(rw * .4, 1.1), max(ry * .18, .7))

def band(b, x0, y0, x1, y1, half, fill, st, sw=1.1):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    px, py = -dy / length * half, dx / length * half
    b.p(
        f'M{x0 + px:.1f} {y0 + py:.1f} L{x1 + px:.1f} {y1 + py:.1f} '
        f'L{x1 - px:.1f} {y1 - py:.1f} L{x0 - px:.1f} {y0 - py:.1f} Z',
        fill, st, sw,
    )


@icon('air_phased_radar', '机载相控阵雷达', '感知通信')
def _(b):
    b.p('M46 58 L78 68 L90 80 L54 68 Z', 'airdk', AS, 1.05)
    b.hl('M52 62 L84 74', .9, .55)
    b.p('M24 46 L62 30 L92 34 L92 62 L62 66 Z', 'air', AS, 1.2)
    b.p('M64 32 C76 18 88 20 92 32 L90 42 C78 36 70 36 62 42 Z', 'canopy', '#1B2D40', .9)
    glint(b, 78, 22, 3.6, 1.3)
    b.p('M8 38 L28 26 L32 66 L12 56 Z', 'array', '#E7F3FF', 1.4)
    plate_dots(b, 12, 34, 14, 24, 2, 3, 1.7)
    b.hl('M28 34 L88 38', 1.15, .75)
    b.ln('M2 26 Q0 48 4 70', '#0E2A4A', 4.8)
    b.ln('M2 26 Q0 48 4 70', '#EAF6FF', 2.5)
    b.ln('M8 34 Q6 48 10 62', '#0E2A4A', 3.6)
    b.ln('M8 34 Q6 48 10 62', '#8FD0FF', 1.9)


@icon('ship_mesh_datalink', '舰载自组网数据链', '感知通信')
def _(b):
    water(b, 58)
    b.p('M4 48 L78 42 L94 56 L88 72 L6 72 L4 60 Z', 'sea', SS, 1.2)
    b.p('M6 61 L90 61 L88 72 L6 72 Z', 'boot', '#4A1612', 1.1)
    b.ln('M8 62 L88 62', '#D27A72', 1.7)
    b.p('M32 48 L35 32 L64 32 L68 48 Z', 'seadk', SS, 1)
    b.r(40, 34, 20, 7, 'canopy', '#1B2D40', rx=.8, sw=.55)
    glint(b, 45, 36, 3.2, .9)
    b.hl('M8 50 L76 44.6', 1.2, .8)
    masts = ((24, 16), (48, 9), (72, 17))
    for x, tip in masts:
        b.r(x - 2.4, tip + 6.2, 4.8, 44 - (tip + 6.2), 'cylM', MS, rx=1.15, sw=.9)
        b.hl(f'M{x - 1.4} {tip + 8} L{x - 1.4} 42', .9, .7)
    trio(b, masts, 6)


@icon('air_mesh_datalink', '机载自组网数据链', '感知通信')
def _(b):
    fus = 'M4 50 L28 44 L70 44 L88 48 L86 58 L66 62 L24 62 L6 56 Z'
    wing = 'M26 56 L52 50 L74 62 L34 66 Z'
    tail = 'M72 46 L86 18 L94 22 L84 48 Z'
    stab = 'M74 54 L94 50 L92 58 L76 60 Z'
    b.drop(wing, 2, 3, .16)
    b.drop(fus, 2, 3, .16)
    b.p(tail, 'airdk', AS, 1.1)
    b.p(stab, 'airdk', AS, 1)
    b.p(wing, 'air', AS, 1.15)
    b.p(fus, 'airV', AS, 1.25)
    b.p('M16 46 C28 40 42 42 48 48 L46 54 C34 50 22 50 14 54 Z', 'canopy', '#1B2D40', .85)
    glint(b, 28, 44, 2.6, 1)
    b.hl('M10 49 L70 46', 1.15, .8)
    b.r(40, 62, 4.2, 14, 'metal3', MS, rx=1, sw=.9)
    pts = ((30, 24), (46, 10), (62, 24))
    for x, y in pts:
        b.ln(f'M{x} {y + 6} L{x} 42', '#5E6A78', 2.5)
        b.ln(f'M{x} {y + 6} L{x} 42', '#E4EAF0', .95)
    trio(b, pts, 5.5)


@icon('uav_ttc', '无人机测控站', '指控信息')
def _(b):
    b.sh(46, 90, 40, 3.2)
    hubs = ((18, 12), (70, 12), (18, 28), (70, 28))
    for x, y in hubs:
        b.ln(f'M48 20 L{x} {y}', '#3E4854', 4.6)
        b.ln(f'M48 20 L{x} {y}', '#E4EAF0', 1.7)
    b.r(40, 14, 16, 12, 'air', AS, rx=3.2, sw=1)
    for x, y, ang in ((18, 12, 30), (70, 12, -24), (18, 28, -18), (70, 28, 26)):
        rotor(b, x, y, 8.4, ang)
    b.p('M8 68 L16 60 L58 60 L50 68 Z', 'canvas', LS, 1)
    b.r(8, 68, 42, 16, 'land', LS, rx=1.6, sw=1.1)
    b.r(14, 73, 7, 11, 'landdk', LS, rx=.8, sw=.7)
    b.r(28, 72, 8, 5, 'canopy', '#1B2D40', rx=.5, sw=.45)
    b.hl('M10 69.2 L48 69.2', .8, .55)
    b.r(76, 58, 3.4, 20, 'metal3', MS, rx=.6, sw=.75)
    b.p('M62 54 Q76 38 90 54 L88 58 Q76 46 64 58 Z', 'metal', MS, 1.05)
    b.hl('M66 52 Q72 44 80 48', 1, .75)
    b.c(76, 50, 1.7, 'dkm')
    b.ln("M48 26 L76 48", '#3D86D6', 2.1, .95, extra="stroke-dasharray='3.2 2.2'")


@icon('loiter_ttc', '巡飞弹测控站', '指控信息')
def _(b):
    b.sh(44, 90, 40, 3)
    b.p('M6 64 L14 56 L60 56 L52 64 Z', 'canvas', LS, 1)
    b.r(6, 64, 46, 16, 'land', LS, rx=1.6, sw=1.1)
    b.hl('M8 65.4 L50 65.4', .8, .5)
    wheel(b, 16, 84, 6)
    wheel(b, 40, 84, 6)
    band(b, 16, 68, 88, 22, 7.2, 'metal2', MS, 1.15)
    band(b, 32, 58, 64, 38, 6.4, 'whitedk', WS, .85)
    band(b, 24, 64, 80, 28, 3.3, 'white', WS, 1.05)
    b.p('M76 30 L90 20 L82 34 Z', 'white', WS, 1)
    dx, dy = 80 - 24, 28 - 64
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    tx, ty = 27, 62
    for sign in (1, -1):
        b.p(
            f'M{tx:.1f} {ty:.1f} L{tx + sign * px * 8 + ux * 2:.1f} {ty + sign * py * 8 + uy * 2:.1f} '
            f'L{tx + sign * px * 8 - ux * 2:.1f} {ty + sign * py * 8 - uy * 2:.1f} Z',
            'whitedk', WS, .8,
        )
    b.hl('M22 62 L82 26', 1.15, .7)
    b.r(66, 70, 18, 12, 'landdk', LS, rx=1.3, sw=.95)
    b.ln('M75 70 L75 58', '#2A2E33', 2.4)
    b.c(75, 57, 1.8, 'metal3', MS, .6)


@icon('cuas_detect_jam', '侦测干扰一体反无人设备', '反无人')
def _(b):
    b.sh(46, 88, 40, 3.2)
    box(b, 8, 48, 66, 26, 12, 7, 'land', 'canvas', 'landdk', LS, 1.15)
    b.ln('M41 50 L41 72', '#3E4C29', 1.6)
    b.r(12, 52, 26, 18, 'array', '#C5DCF6', rx=1.8, sw=1.15)
    plate_dots(b, 14, 54, 22, 14, 3, 2, 2.15)
    for x, top in ((52, 20), (66, 14)):
        b.r(x - 1.7, top, 3.4, 48 - top, 'metal2', MS, rx=.9, sw=.75)
        b.c(x, top, 2.2, 'metal', MS, .7)
    b.ln(f'M46 64 L54 50 L62 72 L70 50 L78 64', JAM, 4.8)
    wheel(b, 22, 80, 6)
    wheel(b, 54, 80, 6)
    b.hl('M10 49.4 L18 42.2 L76 42.2', .95, .72)


@icon('beidou_timing', '北斗授时系统', '指控信息')
def _(b):
    b.sh(48, 90, 42, 3)
    for x0 in (4, 68):
        b.r(x0, 10, 24, 12, 'solar', '#14294A', sw=.8)
        b.ln(f'M{x0 + 8} 10.6 L{x0 + 8} 21.4 M{x0 + 16} 10.6 L{x0 + 16} 21.4 M{x0 + 1} 16 L{x0 + 23} 16', '#C5D9F2', .75, .8)
        b.p(f'M{x0 + 1.2} 11 L{x0 + 9} 11 L{x0 + 5} 21 L{x0 + 1.2} 21 Z', '#FFFFFF', op=.16)
    b.r(28, 6, 40, 20, 'gold', '#6E5418', rx=2, sw=1.05)
    b.ln('M32 11 L64 11 M32 16 L64 16 M32 21 L64 21', '#8A6A20', .8, .85)
    b.hl('M30 7.4 L62 7.4', 1.1, .85)
    b.r(46, 26, 4, 10, 'metal3', MS, sw=.7)
    box(b, 6, 52, 74, 26, 10, 6, 'metal', 'metal', 'metal3', MS, 1.15)
    b.e(48, 48, 15, 4, 'metal2', MS, .8)
    b.p('M33 46 Q48 30 63 46 Z', 'white', '#8794A3', 1.1)
    b.hl('M37 42 Q45 34 50 32', 1.05, .85)
    clock(b, 27, 65, 12)
    for i in range(4):
        x = 48 + i * 7.6
        b.r(x, 57.5, 6, 14.5, '#101814', '#1A2420', rx=.7, sw=.55)
        for k in range(3):
            b.r(x + .9, 59 + k * 4.2, 4.2, 2.5, GREEN)
    b.hl('M8 53.2 L16 47.2 L86 47.2', .9, .65)


@icon('eo_composite', '复合光电系统', '感知通信')
def _(b):
    b.sh(40, 90, 28, 3.2)
    b.e(34, 88, 16, 4.6, 'metal3', MS, 1)
    b.e(34, 84, 11, 3.2, 'metal', MS, .9)
    b.r(30, 70, 8, 14, 'cylM', MS, 1)
    hcyl(b, 28, 20, 52, 11, 'cylM', 'lens', '#05101C')
    hcyl(b, 28, 46, 40, 8, 'cylM', '#E2B04A', '#8A5A14')
    hcyl(b, 28, 68, 30, 5.5, 'dkm', '#14181C', '#0B0D10')


@icon('compute_platform', '新架构算力平台', '信息技术')
def _(b):
    b.sh(48, 90, 42, 3)
    x, y, w, h, dx, dy = 6, 62, 72, 18, 12, 8
    box(b, x, y, w, h, dx, dy, 'metal2', 'metal', 'metal3', MS, 1.15)
    bw, bh = 14, 26
    centers = []
    for bx in (14, 36, 58):
        b.p(f'M{bx + bw} {y - bh} L{bx + bw + 5} {y - bh - 3} L{bx + bw + 5} {y - 3} L{bx + bw} {y} Z', 'metal3', MS, .85)
        b.r(bx, y - bh, bw, bh, 'metal', MS, rx=1.4, sw=1)
        b.r(bx + 2.4, y - bh + 4, 4.2, bh - 9, 'glass', BL, rx=1, sw=.55)
        b.hl(f'M{bx + 1.3} {y - bh + 2} L{bx + 1.3} {y - 3}', .85, .7)
        centers.append(bx + bw / 2)
    ytop = y - bh
    x0, x1 = centers[0], centers[2]
    b.p(f'M{x0} {ytop} Q48 14 {x1} {ytop} L{x1} {ytop + 6} Q48 22 {x0} {ytop + 6} Z', 'glass', BL, 1.15)
    b.hl(f'M{x0 + 3} {ytop + 1} Q46 16 {x1 - 2} {ytop + 1}', 1.05, .8)
    b.ln(f'M{x0} {y + 7} L{x1} {y + 7}', '#5FA2E4', 2.4)


EXPECT = [
    ('air_phased_radar', '机载相控阵雷达', '感知通信'),
    ('ship_mesh_datalink', '舰载自组网数据链', '感知通信'),
    ('air_mesh_datalink', '机载自组网数据链', '感知通信'),
    ('uav_ttc', '无人机测控站', '指控信息'),
    ('loiter_ttc', '巡飞弹测控站', '指控信息'),
    ('cuas_detect_jam', '侦测干扰一体反无人设备', '反无人'),
    ('beidou_timing', '北斗授时系统', '指控信息'),
    ('eo_composite', '复合光电系统', '感知通信'),
    ('compute_platform', '新架构算力平台', '信息技术'),
]

if __name__ == '__main__':
    import os, re as _re
    import xml.etree.ElementTree as ET
    from pathlib import Path

    got = [(k, n, c) for k, n, c, fn in ICONS]
    assert got == EXPECT, got
    keys = [k for k, n, c, fn in ICONS]
    assert len(keys) == len(set(keys)) == 9

    app = Path(__file__).resolve().parents[2] / 'app'
    out = app / 'icons_l.js'
    seen_keys, seen_names = set(), set()
    files = [app / 'icons.js'] + sorted(app.glob('icons_*.js'))
    for f in files:
        if f.name == 'icons_l.js':
            continue
        text = f.read_text(encoding='utf-8')
        seen_keys.update(_re.findall(r"key: '([^']+)'", text))
        seen_names.update(_re.findall(r"name: '([^']+)'", text))
    clash_k = seen_keys & set(keys)
    clash_n = seen_names & {n for k, n, c in EXPECT}
    assert not clash_k, clash_k
    assert not clash_n, clash_n

    forbid = ('<text', '<image', 'href', '<style', 'class=', 'filter')
    lines = ['ICON_LIB.push(...[']
    for k, n, c, fn in ICONS:
        b = B(k)
        fn(b)
        s = b.svg()
        s = _re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
        s = _re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
        assert '"' not in s, k
        assert s.startswith("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96'>"), k
        low = s.lower()
        for bad in forbid:
            assert bad not in low, (k, bad)
        root = ET.fromstring(s)
        assert root.get('viewBox') == '0 0 96 96', k
        for el in root.iter():
            tag = el.tag.split('}')[-1]
            assert tag not in ('text', 'image', 'style'), (k, tag)
            eid = el.get('id')
            if eid is not None:
                assert eid.startswith(k), (k, eid)
            if tag == 'circle':
                cx, cy, r = float(el.get('cx')), float(el.get('cy')), float(el.get('r'))
                assert -0.6 <= cx - r and cx + r <= 96.6, (k, cx, cy, r)
                assert -0.6 <= cy - r and cy + r <= 96.6, (k, cx, cy, r)
            elif tag == 'ellipse':
                cx, cy = float(el.get('cx')), float(el.get('cy'))
                rx, ry = float(el.get('rx')), float(el.get('ry'))
                assert -0.6 <= cx - rx and cx + rx <= 96.6, (k, 'ex', cx, rx)
                assert -0.6 <= cy - ry and cy + ry <= 96.6, (k, 'ey', cy, ry)
            elif tag == 'rect':
                x, y = float(el.get('x')), float(el.get('y'))
                w, h = float(el.get('width')), float(el.get('height'))
                assert -0.6 <= x and x + w <= 96.6, (k, 'rectx', x, w)
                assert -0.6 <= y and y + h <= 96.6, (k, 'recty', y, h)
        lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
    lines.append(']);')
    data = '\n'.join(lines) + '\n'
    assert data.startswith('ICON_LIB.push')
    assert 'const ICON_LIB' not in data and 'module.exports' not in data
    assert '(?<' not in data and '\u2028' not in data
    tmp = out.with_name(out.name + '.tmp')
    tmp.write_text(data, encoding='utf-8')
    os.replace(tmp, out)
    print('ok', len(keys), out)
