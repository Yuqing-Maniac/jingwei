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


# ================= 信息技术 (batch k) =================
CAT = '信息技术'
BL = '#25578F'
GOLD = '#8A6A20'

def cyl(b, cx, y, rx, h, ry=5, fill='cylM', top='metal', st=MS, sw=1.2, hl=True):
    b.p(f"M{cx-rx} {y} L{cx-rx} {y+h} A{rx} {ry} 0 0 0 {cx+rx} {y+h} L{cx+rx} {y} Z", fill, st, sw)
    b.e(cx, y, rx, ry, top, st, sw)
    if hl: b.hl(f"M{cx-rx+3} {y+ry+2} L{cx-rx+3} {y+h-1}", 1.2, .7)

def arr(b, x1, y1, x2, y2, col, w=2.2, s=4.2):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - s * math.cos(a), y2 - s * math.sin(a)
    b.ln(f"M{x1:.1f} {y1:.1f} L{bx:.1f} {by:.1f}", col, w)
    px, py = -math.sin(a), math.cos(a)
    b.p(f"M{x2:.1f} {y2:.1f} L{bx+px*s*.8:.1f} {by+py*s*.8:.1f} L{bx-px*s*.8:.1f} {by-py*s*.8:.1f} Z", col)

def container(b, x, y, w, h, dx, dy, fr, tp, sd, ribs=True, st=BL):
    box(b, x, y, w, h, dx, dy, fr, tp, sd, st, sw=.9)
    if ribs:
        n = int(w // 3.6)
        b.ln(''.join(f"M{x+i*w/n:.1f} {y+1.5} L{x+i*w/n:.1f} {y+h-1.5}" for i in range(1, n)), '#FFFFFF', .6, .45)
    b.ln(f"M{x+1.5} {y+1.2} L{x+w-1.5} {y+1.2}", '#FFFFFF', .8, .7)

def vents(b, x, y, w, n, gap=2.2, col='#5E6A78'):
    for i in range(n):
        b.ln(f"M{x} {y+i*gap:.1f} L{x+w} {y+i*gap:.1f}", col, .8, .8)

def port(b, x, y, w=3, h=2.6):
    b.r(x, y, w, h, '#2B3440', rx=.4)

def shield(b, cx, cy, w, h, fill='glass', st=BL):
    hw = w / 2
    b.p(f"M{cx-hw} {cy-h/2} Q{cx} {cy-h/2-3} {cx+hw} {cy-h/2} L{cx+hw} {cy+h*.05} Q{cx+hw*.9} {cy+h*.35} {cx} {cy+h/2} Q{cx-hw*.9} {cy+h*.35} {cx-hw} {cy+h*.05} Z", fill, st, 1.1)
    b.hl(f"M{cx-hw+2.5} {cy-h/2+2.5} L{cx-hw+2.5} {cy} ", 1, .8)

def gear(b, cx, cy, r, fill='metal2', st=MS, n=8):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        rr = r if i % 2 == 0 else r * .72
        for da in (-.12, .12):
            pts.append((cx + rr * math.cos(a + da), cy + rr * math.sin(a + da)))
    b.p('M' + ' L'.join(f"{x:.1f} {y:.1f}" for x, y in pts) + ' Z', fill, st, .9)
    b.c(cx, cy, r * .38, '#EEF2F6', st, .8)

def check(b, cx, cy, r):
    b.c(cx, cy, r, '#43C46B', '#23813F', 1)
    b.ln(f"M{cx-r*.5:.1f} {cy} L{cx-r*.1:.1f} {cy+r*.4:.1f} L{cx+r*.55:.1f} {cy-r*.4:.1f}", '#FFFFFF', 1.8)

def doc(b, x, y, w, h, n=3, fill='white'):
    b.r(x, y, w, h, fill, MS, rx=1.5, sw=.9)
    for i in range(n):
        b.ln(f"M{x+2.5} {y+3.5+i*3.2:.1f} L{x+w-2.5-(i%2)*3:.1f} {y+3.5+i*3.2:.1f}", '#8794A3', 1)

def win(b, x, y, w, h, bar=5, body='white', tint='appbg'):
    b.r(x, y, w, h, body, MS, rx=2.5, sw=1)
    b.p(f"M{x+2.5} {y} L{x+w-2.5} {y} Q{x+w} {y} {x+w} {y+2.5} L{x+w} {y+bar} L{x} {y+bar} L{x} {y+2.5} Q{x} {y} {x+2.5} {y} Z", tint, BL, 1)
    for i, c in enumerate(('#E2574C', '#F2A93B', '#43C46B')):
        b.c(x + 3.2 + i * 3.2, y + bar / 2, .9, c)

# ---------------------------------------------------------------- 1
@icon('it_k8s', '容器集群', CAT)
def _(b):
    b.sh(48, 92, 42, 2.6)
    # helm-wheel ring
    cx, cy, R = 48, 23, 15
    for i in range(7):
        a = 2 * math.pi * i / 7 - math.pi / 2
        b.ln(f"M{cx} {cy} L{cx+(R+4)*math.cos(a):.1f} {cy+(R+4)*math.sin(a):.1f}", '#A5B0BD', 2.4)
        b.c(round(cx + (R + 4) * math.cos(a), 1), round(cy + (R + 4) * math.sin(a), 1), 2.2, 'metal', MS, .8)
    b.c(cx, cy, R, 'none', '#5E6A78', 4.2)
    b.c(cx, cy, R, 'none', '#BFE3FF', 2.6)
    b.hl(f"M{cx-R+2} {cy-4} A{R-2} {R-2} 0 0 1 {cx-3} {cy-R+2}", 1, .9)
    b.c(cx, cy, 6, 'node', BL, 1.1)
    b.c(cx - 1.6, cy - 1.8, 1.4, '#FFFFFF', op=.8)
    # links down
    b.ln("M48 40 L48 60", '#5E6A78', 3)
    b.ln("M48 40 L48 60", '#8FD0FF', 1.2)
    col = [('appbg', 'glass', 'scr'), ('orange', '#F6D08A', '#B8691F'), ('land', '#CFDCA9', 'landdk')]
    row2 = [(8, 0), (35, 1), (62, 2)]
    for x, ci in row2:
        f, t, s = col[ci]
        container(b, x, 76, 20, 11, 7, 4, f, t, s)
    for x, ci in ((21, 1), (48, 0)):
        f, t, s = col[ci]
        container(b, x, 62, 20, 11, 7, 4, f, t, s)
    leds(b, [(12, 81.5, GREEN), (39, 81.5, GREEN), (66, 81.5, AMBER)])

# ---------------------------------------------------------------- 2
@icon('it_container', '容器', CAT)
def _(b):
    b.sh(48, 90, 40, 2.8)
    x, y, w, h, dx, dy = 10, 34, 54, 40, 22, 14
    box(b, x, y, w, h, dx, dy, 'appbg', 'glass', 'scr', BL, 1.2)
    n = 14
    b.ln(''.join(f"M{x+i*w/n:.1f} {y+3} L{x+i*w/n:.1f} {y+h-3}" for i in range(1, n)), '#FFFFFF', .7, .35)
    b.ln(''.join(f"M{x+w+i*dx/6:.1f} {y-i*dy/6+2:.1f} L{x+w+i*dx/6:.1f} {y+h-i*dy/6-2:.1f}" for i in range(1, 6)), '#0E2A4A', .6, .35)
    b.r(x, y, w, 4, 'metal', BL, sw=.8)
    b.r(x, y + h - 4, w, 4, 'metal2', BL, sw=.8)
    b.p(f"M{x} {y+4} L{x} {y+h-4} L{x+4} {y+h-4} L{x+4} {y+4} Z", 'metal2', BL, .8)
    b.p(f"M{x+w-4} {y+4} L{x+w-4} {y+h-4} L{x+w} {y+h-4} L{x+w} {y+4} Z", 'metal2', BL, .8)
    b.hl(f"M{x+6} {y+6} L{x+w-8} {y+6}", 1.1, .75)
    # lock rods on door side
    b.ln(f"M{x+w-10} {y+6} L{x+w-10} {y+h-6} M{x+w-14} {y+6} L{x+w-14} {y+h-6}", '#D6DCE3', 1.4)
    b.r(x + w - 15.5, y + h / 2 - 3, 7, 6, 'gold', GOLD, rx=1, sw=.7)
    # plate / led
    b.r(x + 8, y + h - 14, 14, 6, 'white', MS, rx=1, sw=.6)
    leds(b, [(x + 11, y + h - 11, GREEN), (x + 15, y + h - 11, GREEN), (x + 19, y + h - 11, AMBER)])
    # corner castings
    for cxp, cyp in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        b.r(cxp - 1.5, cyp - 1.5, 3.4, 3.4, 'dkm', DS, sw=.5)

# ---------------------------------------------------------------- 3
@icon('it_vm', '虚拟机', CAT)
def _(b):
    b.sh(48, 91, 40, 2.6)
    # ghost windows (dashed)
    b.r(52, 14, 36, 28, 'none', '#6FA7DA', rx=3, sw=1.2, extra="stroke-dasharray='3 2'")
    b.r(52, 14, 36, 28, '#BFE3FF', None, rx=3, op=.25)
    # virtual machine windows
    b.r(26, 20, 38, 30, 'dkm2', DS, rx=3, sw=1)
    b.r(28.5, 24, 33, 23.5, 'scr', None, rx=1.5)
    b.r(28.5, 24, 33, 4, 'glass', None, rx=1.5, op=.9)
    b.ln("M32 33 L52 33 M32 37 L46 37 M32 41 L50 41", '#BFE3FF', 1.2, .8)
    b.p("M30 47 L44 28 L58 28 L48 47 Z", '#FFFFFF', op=.12)
    b.r(8, 28, 32, 26, 'metal', MS, rx=3, sw=1)
    b.r(10.5, 31.5, 27, 18.5, 'glass', BL, rx=1.5, sw=.6)
    b.hl("M13 34 L26 34", 1.3, .9)
    b.ln("M14 40 L34 40 M14 44 L28 44", '#2E5D8B', 1.2, .6)
    # host base
    box(b, 8, 66, 62, 12, 16, 7, 'metal2', 'metal', 'metal3', MS, 1.1)
    for i in range(4): port(b, 13 + i * 7.5, 71)
    vents(b, 46, 69.5, 18, 4, 2.2)
    leds(b, [(66, 72, GREEN)])
    # supports / link
    b.ln("M24 54 L24 66 M45 50 L45 66", '#8794A3', 2.4, .8)
    b.ln("M24 54 L24 66 M45 50 L45 66", '#3D86D6', 1, .9, extra="stroke-dasharray='2 2'")

# ---------------------------------------------------------------- 4
@icon('it_xc_server', '信创服务器', CAT)
def _(b):
    b.sh(46, 92, 42, 2.6)
    # CPU chip floating above
    b.drop("M28 6 L66 6 L66 40 L28 40 Z", 2, 3, .18)
    for i in range(7):
        xx = 31 + i * 5
        b.ln(f"M{xx} 3 L{xx} 6 M{xx} 40 L{xx} 43", '#C9A145', 1.4)
    for i in range(6):
        yy = 10 + i * 5.2
        b.ln(f"M25 {yy:.1f} L28 {yy:.1f} M66 {yy:.1f} L69 {yy:.1f}", '#C9A145', 1.4)
    b.r(28, 6, 38, 34, 'metal2', MS, rx=3, sw=1.2)
    b.r(32, 10, 30, 26, 'dkm', DS, rx=2, sw=.8)
    b.r(34, 12, 26, 22, 'glass', BL, rx=1.5, sw=.8)
    b.ln("M38 16 L56 16 L56 30 L38 30 Z M44 16 L44 30 M50 16 L50 30 M38 23 L56 23", '#2E5D8B', .8, .55)
    star(b, 47, 23, 5.5, .95)
    b.hl("M30 8 L50 8", 1, .8)
    # 2U server body
    box(b, 8, 54, 62, 26, 20, 10, 'metal', 'metal', 'metal3', MS, 1.2)
    b.r(8, 54, 62, 26, 'metal', MS)
    for r_ in range(2):
        for c in range(4):
            b.r(12 + c * 9.5, 58 + r_ * 10, 8, 8, 'dkm2', DS, rx=1, sw=.6)
            b.ln(f"M{13+c*9.5} {61.5+r_*10} L{19+c*9.5} {61.5+r_*10}", '#6FA7DA', .8, .8)
    b.r(52, 58, 15, 18, 'dkm2', DS, rx=1.5, sw=.7)
    for i in range(5): b.ln(f"M54 {61+i*3} L65 {61+i*3}", '#5A616A', .8)
    leds(b, [(10, 56, GREEN), (13.5, 56, AMBER)])
    # shield badge
    shield(b, 66, 78, 15, 17, 'gold', GOLD)
    star(b, 66, 78, 4, .95)

# ---------------------------------------------------------------- 5
@icon('it_rack', '服务器机柜', CAT)
def _(b):
    b.sh(46, 92, 38, 2.6)
    x, y, w, h, dx, dy = 14, 14, 44, 74, 22, 10
    box(b, x, y, w, h, dx, dy, 'dkm', 'metal2', 'dkm2', DS, 1.2)
    b.r(x + 3, y + 3, w - 6, h - 6, '#161C24', None, rx=1)
    for i in range(7):
        yy = y + 5 + i * 9.6
        b.r(x + 5, yy, w - 10, 7.6, 'metal2', MS, rx=1, sw=.7)
        b.r(x + 6.5, yy + 1.5, 14, 4.6, 'dkm2', None, rx=.8)
        vents(b, x + 8, yy + 2.4, 10, 2, 1.8, '#5A616A')
        for k in range(3): port(b, x + 24 + k * 3.6, yy + 2.2, 2.6, 2.4)
        b.c(x + w - 9.5, yy + 3.8, 1.2, GREEN if i % 3 else AMBER)
    # glass door reflection
    b.p(f"M{x+3} {y+3} L{x+w-3} {y+3} L{x+w-3} {y+10} L{x+3} {y+h*.5} Z", '#BFE3FF', op=.16)
    b.p(f"M{x+3} {y+h*.55} L{x+w-3} {y+10} L{x+w-3} {y+30} L{x+3} {y+h-3} Z", '#FFFFFF', op=.07)
    b.hl(f"M{x+4} {y+4} L{x+4} {y+40}", 1.2, .5)
    # side vents / handle
    b.r(x + w - 4.5, y + 30, 2.6, 14, 'gold', GOLD, rx=1, sw=.5)
    b.ln(f"M{x+w+5} {y-4} L{x+w+5} {y+h-14}", '#FFFFFF', .7, .2)
    b.r(x - 1, y + h, w + 2, 4, 'dkm', DS, sw=.8)

# ---------------------------------------------------------------- 6
@icon('it_lb', '负载均衡', CAT)
def _(b):
    b.sh(48, 92, 42, 2.4)
    # three backend servers
    for i, yy in enumerate((8, 34, 60)):
        b.p(f"M64 {yy+16} L68 {yy+12} L92 {yy+12} L88 {yy+16} Z", 'metal')
        box(b, 62, yy + 2, 26, 14, 6, 4, 'metal2', 'metal', 'metal3', MS, 1)
        b.r(64, yy + 4, 12, 4, 'dkm2', None, rx=.8); b.r(64, yy + 9.5, 12, 4, 'dkm2', None, rx=.8)
        leds(b, [(81, yy + 6, GREEN), (81, yy + 11.5, GREEN if i != 1 else AMBER)])
    # balancer device
    b.drop("M6 30 L36 30 L36 62 L6 62 Z", 2, 3, .18)
    box(b, 6, 34, 30, 28, 8, 5, 'metal2', 'metal', 'metal3', MS, 1.2)
    b.r(9, 37.5, 24, 17, 'scr', BL, rx=1.5, sw=.8)
    b.ln("M12 46 L18 46 M18 46 L27 41 M18 46 L27 46 M18 46 L27 51", '#BFE3FF', 1.3, .95)
    for yy in (41, 46, 51): b.c(28.5, yy, 1.4, '#8FD0FF')
    b.hl("M10 39 L22 39", 1, .6)
    for i in range(4): port(b, 10 + i * 5.5, 57, 3.6, 2.8)
    leds(b, [(30, 58.4, GREEN)])
    # fan out arrows
    for ty in (20, 46, 72):
        b.ln(f"M44 48 C52 48 52 {ty} 55 {ty}", '#3D86D6', 2.6)
        b.ln(f"M44 48 C52 48 52 {ty} 55 {ty}", '#BFE3FF', .9, .8)
        arr(b, 54, ty, 61, ty, '#3D86D6', 2.2, 4)
    arr(b, 36, 48, 45, 48, '#3D86D6', 2.6, 4.5)
    b.c(45, 48, 2, 'node', BL, .8)

# ---------------------------------------------------------------- 7
@icon('it_core_switch', '核心交换机', CAT)
def _(b):
    b.sh(46, 92, 42, 2.6)
    x, y, w, h, dx, dy = 8, 24, 62, 58, 18, 10
    box(b, x, y, w, h, dx, dy, 'metal', 'metal', 'metal3', MS, 1.3)
    # top fan tray
    b.r(x + 2, y + 2, w - 4, 11, 'dkm2', DS, rx=1.5, sw=.7)
    for i in range(3):
        cx = x + 13 + i * 18
        b.c(cx, y + 7.5, 4.3, 'dkm', '#0B0D10', .7)
        for a in (0, 60, 120):
            ra = math.radians(a)
            b.ln(f"M{cx-3.3*math.cos(ra):.1f} {y+7.5-3.3*math.sin(ra):.1f} L{cx+3.3*math.cos(ra):.1f} {y+7.5+3.3*math.sin(ra):.1f}", '#8794A3', 1)
        b.c(cx, y + 7.5, 1, '#C9D1DA')
    # line cards
    for r_ in range(3):
        yy = y + 16 + r_ * 12
        b.r(x + 2, yy, w - 4, 10, 'metal2', MS, rx=1, sw=.6)
        for c in range(2):
            b.ln(f"M{x+5+c*28} {yy+2.7} L{x+29+c*28} {yy+2.7} M{x+5+c*28} {yy+6.5} L{x+29+c*28} {yy+6.5}", '#2B3440', 2.6, extra="stroke-dasharray='3.2 .8'", cap='butt')
        leds(b, [(x + w - 5, yy + 3, GREEN), (x + w - 5, yy + 7, GREEN if r_ else AMBER)])
    b.hl(f"M{x+3} {y+14.5} L{x+w-3} {y+14.5}", .7, .6)
    # glow cross arrows plate
    b.r(x + 16, y + h - 7, 30, 5, 'glass', BL, rx=1.5, sw=.6)
    b.ln(f"M{x+20} {y+h-5.7} L{x+40} {y+h-5.7}", '#FFFFFF', 1, .8)
    # switch arrows floating
    arr(b, 56, 12, 82, 12, '#3D86D6', 2.6, 4.5)
    arr(b, 82, 20, 56, 20, '#F2A93B', 2.6, 4.5)

# ---------------------------------------------------------------- 8
@icon('it_gap', '网闸（隔离装置）', CAT)
def _(b):
    b.sh(48, 91, 44, 2.4)
    # left unit
    box(b, 4, 30, 28, 44, 8, 5, 'metal2', 'metal', 'metal3', MS, 1.2)
    b.r(7, 34, 22, 12, 'dkm2', DS, rx=1.5, sw=.7); b.r(7, 49, 22, 6, 'dkm2', DS, rx=1.5, sw=.7)
    b.ln("M10 38 L24 38 M10 42 L20 42", '#6FA7DA', 1, .8)
    for i in range(4): port(b, 8 + i * 5, 59, 3.4, 2.8)
    leds(b, [(10, 52, GREEN), (14, 52, GREEN)])
    b.r(7, 65, 22, 5, 'glass', BL, rx=1, sw=.6)
    # right unit
    box(b, 62, 30, 28, 44, 6, 4, 'metal2', 'metal', 'metal3', MS, 1.2)
    b.r(65, 34, 22, 12, 'dkm2', DS, rx=1.5, sw=.7); b.r(65, 49, 22, 6, 'dkm2', DS, rx=1.5, sw=.7)
    b.ln("M68 38 L82 38 M68 42 L78 42", '#6FA7DA', 1, .8)
    for i in range(4): port(b, 66 + i * 5, 59, 3.4, 2.8)
    leds(b, [(68, 52, AMBER), (72, 52, GREEN)])
    b.r(65, 65, 22, 5, 'glass', BL, rx=1, sw=.6)
    # the gap: two rails with air in between
    b.r(40, 18, 4, 62, 'dkm', DS, sw=.7); b.r(50, 18, 4, 62, 'dkm', DS, sw=.7)
    b.p("M44 18 L50 18 L50 80 L44 80 Z", '#FFFFFF', op=.12)
    for yy in (24, 36, 48, 60, 72):
        b.ln(f"M44.5 {yy} L49.5 {yy}", '#E2574C', 1, .0)
    # crossing arrow (energy/data) one-way
    b.ln("M32 50 L62 50", '#F2A93B', 3.4)
    arr(b, 56, 50, 63, 50, '#F2A93B', 3.4, 6)
    b.ln("M32 50 L44 50", '#FFE2A8', 1, .8)
    # gap marks
    b.ln("M42 14 L42 20 M52 14 L52 20", '#E2574C', 1.6)
    b.ln("M38 23 L36 23 M58 23 L60 23", '#E2574C', 0)
    # left-flow blocked marker
    b.c(47, 66, 3.2, '#E2574C', '#8E3129', .8)
    b.ln("M45.3 64.3 L48.7 67.7 M48.7 64.3 L45.3 67.7", '#FFFFFF', 1.1)

# ---------------------------------------------------------------- 9
@icon('it_bastion', '堡垒机', CAT)
def _(b):
    b.sh(48, 92, 38, 2.6)
    x, w = 22, 52
    # tower body
    b.drop(f"M{x} 28 L{x+w} 28 L{x+w} 88 L{x} 88 Z", 2.5, 3, .16)
    b.r(x, 26, w, 62, 'metal2', MS, sw=1.3)
    b.p(f"M{x} 26 L{x} 12 L{x+9} 12 L{x+9} 18 L{x+16} 18 L{x+16} 12 L{x+27} 12 L{x+27} 18 L{x+34} 18 L{x+34} 12 L{x+w} 12 L{x+w} 26 Z", 'metal', MS, 1.3)
    b.p(f"M{x+w} 26 L{x+w} 88 L{x+w-7} 88 L{x+w-7} 26 Z", 'metal3', None)
    b.ln(f"M{x+2} 27.5 L{x+w-2} 27.5", '#FFFFFF', 1, .7)
    b.hl(f"M{x+2.5} 14 L{x+7} 14", 1, .8)
    # brick lines
    for yy in (36, 44, 52):
        b.ln(f"M{x} {yy} L{x+w-7} {yy}", '#8794A3', .7, .6)
    # arrow slit window (glass)
    b.r(x + 9, 17, 5, 7, 'dkm2', None, rx=2.2); b.r(x + 38, 17, 5, 7, 'dkm2', None, rx=2.2) if False else None
    # server slots lower
    for i in range(3):
        yy = 66 + i * 7
        b.r(x + 4, yy, w - 14, 5, 'dkm2', DS, rx=1, sw=.6)
        b.ln(f"M{x+7} {yy+2.5} L{x+17} {yy+2.5}", '#6FA7DA', 1, .8)
        b.c(x + w - 15, yy + 2.5, 1.2, GREEN if i != 1 else AMBER)
    # shield with keyhole
    b.drop("M48 28 L48 60 Z", 0, 0, 0)
    shield(b, 48, 46, 28, 32, 'glass', BL)
    b.p("M48 33 Q60 33 62 36 L62 47 Q60 56 48 62 Q36 56 34 47 L34 36 Q36 33 48 33 Z", '#FFFFFF', op=.18)
    b.c(48, 44, 4, '#1B2A3C', '#0F2339', .8)
    b.p("M46.2 46 L49.8 46 L51 54 L45 54 Z", '#1B2A3C')
    b.hl("M38 38 L38 46", 1.2, .85)

# ---------------------------------------------------------------- 10
@icon('it_ids', '入侵检测', CAT)
def _(b):
    b.sh(48, 91, 40, 2.4)
    # sensor base
    box(b, 14, 70, 52, 12, 14, 6, 'metal2', 'metal', 'metal3', MS, 1.1)
    for i in range(5): port(b, 18 + i * 6, 74.5)
    leds(b, [(54, 76, GREEN), (58, 76, GREEN)])
    # eye
    b.drop("M10 46 Q48 12 86 46 Q48 78 10 46 Z", 2, 3, .18)
    b.p("M10 44 Q48 10 86 44 Q48 78 10 44 Z", 'white', MS, 1.4)
    b.p("M14 44 Q48 16 82 44 Q48 72 14 44 Z", 'scr', BL, 1)
    b.c(48, 44, 17, 'lens', '#0F2339', 1.2)
    b.c(48, 44, 11, 'node', BL, 1)
    b.c(48, 44, 5, '#0B1B2E')
    b.e(43, 38, 4, 2.4, '#FFFFFF', op=.85)
    b.ln("M20 42 Q34 26 46 26", '#FFFFFF', 1.2, .5)
    # packets coming in
    for i, (yy, col) in enumerate(((30, '#8FD0FF'), (46, '#8FD0FF'), (62, '#8FD0FF'))):
        pass
    # alert triangle
    b.drop("M80 8 L92 30 L68 30 Z", 1.5, 2, .2)
    b.p("M80 6 L92 28 L68 28 Z", '#E2574C', '#8E3129', 1.3)
    b.p("M80 10 L88 25 L72 25 Z", '#F7897F', op=.5)
    b.ln("M80 13 L80 21", '#FFFFFF', 2.2); b.c(80, 24.4, 1.3, '#FFFFFF')
    # radar scan arcs left
    b.ln("M4 36 Q0 46 4 56", '#3D86D6', 1.6, .8); b.ln("M8 40 Q5 46 8 52", '#3D86D6', 1.6, .9)

# ---------------------------------------------------------------- 11
@icon('it_vpn', 'VPN 网关', CAT)
def _(b):
    b.sh(48, 91, 42, 2.4)
    # cloud (public network) above, faint
    b.p("M22 30 Q16 30 16 24 Q16 18 23 18 Q25 10 34 11 Q40 4 49 10 Q58 6 62 14 Q72 13 72 22 Q72 30 64 30 Z", 'cloud', '#86A7CB', 1)
    b.hl("M24 17 Q28 13 34 14", 1, .9)
    # tunnel tube
    b.r(24, 50, 48, 18, 'cylM', MS, rx=9, sw=1.3) if False else None
    b.p("M22 48 L74 48 L74 70 L22 70 Z", 'glass', BL, 1.3)
    b.r(22, 48, 52, 22, 'glass', BL, rx=3, sw=1.3)
    b.p("M23 49 L73 49 L73 54 L23 54 Z", '#FFFFFF', op=.4)
    b.ln("M26 62 L70 62", '#2E5D8B', 1, .5)
    for i in range(4):
        arr(b, 30 + i * 11, 60, 38 + i * 11, 60, '#FFFFFF', 1.6, 3)
    # flanges
    b.r(18, 44, 6, 30, 'metal', MS, rx=2, sw=1); b.r(72, 44, 6, 30, 'metal', MS, rx=2, sw=1)
    # end gateways
    box(b, 2, 52, 14, 22, 5, 3, 'metal2', 'metal', 'metal3', MS, 1)
    box(b, 80, 52, 12, 22, 4, 3, 'metal2', 'metal', 'metal3', MS, 1)
    leds(b, [(6, 56, GREEN), (86, 56, GREEN)])
    for yy in (62, 66, 70): b.ln(f"M4 {yy} L12 {yy}", '#5E6A78', .8); b.ln(f"M82 {yy} L89 {yy}", '#5E6A78', .8)
    # padlock
    b.p("M42 56 L42 52 Q42 44 48 44 Q54 44 54 52 L54 56", 'none', '#6A7685', 3) if False else None
    b.ln("M43 50 L43 47 Q43 40 48 40 Q53 40 53 47 L53 50", '#6A7685', 3.2)
    b.ln("M43 50 L43 47 Q43 40 48 40 Q53 40 53 47 L53 50", '#E1E6EC', 1.3)
    b.r(38, 49, 20, 17, 'gold', GOLD, rx=3, sw=1.1)
    b.c(48, 56, 2.6, '#3A2D0E'); b.p("M46.9 57 L49.1 57 L49.8 62 L46.2 62 Z", '#3A2D0E')
    b.hl("M40.5 51.5 L52 51.5", 1.1, .7)
    b.ln("M24 30 L24 46 M72 30 L72 46", '#3D86D6', 1.4, .8, extra="stroke-dasharray='2 2'")

# ---------------------------------------------------------------- 12
@icon('it_waf', 'Web 应用防火墙', CAT)
def _(b):
    b.sh(48, 92, 42, 2.4)
    # browser behind
    b.drop("M8 8 L80 8 L80 56 L8 56 Z", 2, 3, .16)
    win(b, 8, 8, 72, 48, 7, 'white', 'appbg')
    b.r(24, 10, 40, 3.2, '#E3EEF9', None, rx=1.6)
    b.r(12, 17, 64, 14, 'scr', BL, rx=1.5, sw=.7)
    b.ln("M16 22 L40 22 M16 26 L32 26", '#BFE3FF', 1.4, .85)
    for i in range(3):
        b.r(12 + i * 22, 35, 19, 16, 'glass', BL, rx=1.5, sw=.6)
    b.hl("M14 19 L36 19", 1, .5)
    # brick wall bottom
    b.r(4, 64, 88, 26, 'red', '#6E241B', rx=2, sw=1.2)
    for r_ in range(4):
        yy = 64 + r_ * 6.5
        b.ln(f"M4 {yy+6.5:.1f} L92 {yy+6.5:.1f}", '#E9B9AF', 1, .7)
        off = 0 if r_ % 2 == 0 else 8
        for k in range(-1, 6):
            xx = 4 + off + k * 16
            if 4 < xx < 92: b.ln(f"M{xx} {yy:.1f} L{xx} {yy+6.5:.1f}", '#E9B9AF', 1, .7)
    b.hl("M6 65.5 L90 65.5", 1, .6)
    # shield overlapping
    b.drop("M70 30 L70 80 Z", 0, 0, 0)
    shield(b, 66, 52, 32, 38, 'metal', MS)
    shield(b, 66, 52, 25, 30, 'glass', BL)
    b.p("M66 40 L76 43 L76 52 Q74 58 66 64 Q58 58 56 52 L56 43 Z", '#FFFFFF', op=.18)
    # globe on shield
    b.c(66, 52, 8, 'none', '#FFFFFF', 1.2, .9)
    b.e(66, 52, 3.4, 8, 'none', '#FFFFFF', 1, .8)
    b.ln("M58 52 L74 52 M59.5 47 L72.5 47 M59.5 57 L72.5 57", '#FFFFFF', 1, .8)

# ---------------------------------------------------------------- 13
@icon('it_ca', 'CA 证书', CAT)
def _(b):
    b.sh(48, 91, 40, 2.4)
    b.drop("M8 12 L88 12 L88 74 L8 74 Z", 2.5, 3.5, .18)
    b.r(8, 12, 80, 62, 'white', MS, rx=3, sw=1.3)
    b.r(12, 16, 72, 54, 'none', '#3D86D6', rx=2, sw=1.4)
    b.r(15, 19, 66, 48, 'none', '#BFE3FF', rx=1.5, sw=.8)
    # header ribbon
    b.p("M28 12 L68 12 L72 20 L68 28 L28 28 L24 20 Z", 'appbg', BL, 1.2)
    b.hl("M31 15 L62 15", 1.2, .7)
    check(b, 48, 20.5, 5.2)
    # text lines
    b.ln("M22 36 L74 36 M22 42 L74 42 M22 48 L58 48", '#8794A3', 1.6)
    b.ln("M22 36 L50 36", '#5E6A78', 1.6)
    # signature
    b.ln("M22 60 Q26 54 29 60 T36 58 T44 60", '#25578F', 1.4)
    # seal ribbons + rosette
    b.p("M66 66 L58 90 L65 86 L69 92 L74 70 Z", '#3D86D6', BL, 1)
    b.p("M76 66 L82 90 L76 86 L72 92 L68 70 Z", '#2F6FB0', BL, 1)
    pts = []
    for i in range(24):
        a = math.pi * 2 * i / 24
        r_ = 12 if i % 2 == 0 else 10
        pts.append(f"{72+r_*math.cos(a):.1f} {62+r_*math.sin(a):.1f}")
    b.p('M' + ' L'.join(pts) + ' Z', 'gold', GOLD, 1)
    b.c(72, 62, 7.4, 'none', '#FFF2C4', 1, .9)
    b.c(72, 62, 5, 'gold', GOLD, .7)
    star(b, 72, 62, 3.6, .95)
    b.hl("M64 56 Q67 52 72 51", 1, .9)

# ---------------------------------------------------------------- 14
@icon('it_mq', '消息队列', CAT)
def _(b):
    b.sh(48, 90, 42, 2.4)
    # queue pipe
    b.r(12, 30, 72, 38, 'dkm', DS, rx=5, sw=1.3)
    b.r(15, 33, 66, 32, '#1B2A3C', None, rx=3)
    b.ln("M15 36 L81 36", '#FFFFFF', 1, .35)
    cols = [('#F6D08A', '#F0B060'), ('#CFE9FF', '#78B6EE'), ('#CFDCA9', '#81955A'), ('#F6D08A', '#F0B060')]
    for i, (t, f) in enumerate(cols):
        x = 17 + i * 16
        b.r(x, 38, 13, 22, f, '#25578F' if i == 1 else '#5E6A78', rx=1.5, sw=.8)
        b.p(f"M{x} 39.5 L{x+6.5} 48 L{x+13} 39.5 Z", t, '#5E6A78', .7)
        b.ln(f"M{x+2.5} 54 L{x+10.5} 54 M{x+2.5} 57 L{x+8} 57", '#FFFFFF', 1.1, .85)
    # ends
    arr(b, 2, 49, 12, 49, '#3D86D6', 3, 5)
    arr(b, 84, 49, 94, 49, '#43C46B', 3, 5)
    b.r(80, 32, 4, 34, 'metal', MS, rx=1.5, sw=.8); b.r(12, 32, 4, 34, 'metal', MS, rx=1.5, sw=.8)
    leds(b, [(26, 74, GREEN), (32, 74, GREEN), (38, 74, AMBER)])
    b.ln("M54 74 L82 74", '#3D86D6', 1.6, .8, extra="stroke-dasharray='3 3'")
    # top FIFO-ish order markers
    b.ln("M20 24 L76 24", '#5E6A78', 1, .0)
    b.p("M80 20 L88 24 L80 28 Z", '#8794A3', op=0)

# ---------------------------------------------------------------- 15
@icon('it_cache', '缓存', CAT)
def _(b):
    b.sh(48, 90, 42, 2.4)
    # memory module
    b.drop("M6 30 L90 30 L90 70 L6 70 Z", 2.5, 3.5, .18)
    b.r(6, 28, 84, 42, 'land', LS, rx=2.5, sw=1.3)
    b.r(6, 28, 84, 42, 'canvas', None, rx=2.5, op=.4)
    b.r(6, 70, 84, 7, 'gold', GOLD, sw=.9)
    for i in range(21):
        b.ln(f"M{9+i*3.9:.1f} 71.5 L{9+i*3.9:.1f} 76", '#8A6A20', 1)
    b.p("M44 70 L44 77 L50 77 L50 70 Z", '#262C33')
    for i in range(4):
        x = 12 + i * 18.5
        b.r(x, 33, 15, 28, 'dkm2', DS, rx=1.5, sw=.8)
        b.r(x + 2, 35, 11, 6, 'dkm', None, rx=1)
        b.ln(f"M{x+3} 46 L{x+12} 46 M{x+3} 50 L{x+9} 50", '#6A7480', .9)
        b.c(x + 3, 57, 1, '#9FB1C6')
    b.hl("M10 30 L84 30", 1, .5)
    # lightning bolt
    b.drop("M60 2 L40 26 L50 26 L44 44 L66 18 L55 18 Z", 1.5, 2, .25)
    b.p("M60 1 L40 25 L50 25 L44 43 L66 17 L55 17 Z", 'orange', '#8A4A10', 1.2)
    b.p("M59 4 L45 23 L52 23 L48 36 L60 19 Z", '#FFE2A8', op=.55)
    b.ln("M72 12 L80 8 M74 20 L84 20 M30 10 L24 6", '#F2A93B', 1.6, .8)

# ---------------------------------------------------------------- 16
@icon('it_middleware', '应用中间件', CAT)
def _(b):
    b.sh(48, 92, 42, 2.4)
    # bottom OS/infra slab
    box(b, 8, 74, 66, 9, 14, 6, 'metal2', 'metal', 'metal3', MS, 1)
    for i in range(6): port(b, 13 + i * 6, 76.8, 3.6, 2.8)
    # middle middleware slab (glass + gear)
    box(b, 8, 50, 66, 16, 14, 6, 'glass', '#DCEFFF', 'scr', BL, 1.2)
    b.hl("M10 52 L70 52", 1.1, .75)
    gear(b, 41, 58, 9.5, 'metal', MS, 8)
    gear(b, 23, 58, 5, 'metal2', MS, 6)
    gear(b, 59, 58, 5, 'metal2', MS, 6)
    # plugs (connectors)
    for x in (22, 41, 60):
        b.r(x - 2, 66, 4, 8, 'metal3', MS, sw=.6)
        b.r(x - 2, 43, 4, 7, 'metal3', MS, sw=.6)
        b.ln(f"M{x-.8} 43 L{x-.8} 40 M{x+.8} 43 L{x+.8} 40", '#C9A145', 1)
    # apps on top
    for x, f, t in ((8, 'appbg', 'glass'), (30, 'orange', '#F6D08A'), (52, 'land', '#CFDCA9')):
        b.r(x, 18, 20, 22, f, '#5E6A78', rx=3.5, sw=1)
        b.p(f"M{x+3} 18.5 L{x+17} 18.5 Q{x+20} 18.5 {x+20} 22 L{x+20} 25 L{x} 25 L{x} 22 Q{x} 18.5 {x+3} 18.5 Z", t, None, 1, .6)
        b.ln(f"M{x+4} 30 L{x+16} 30 M{x+4} 34 L{x+12} 34", '#FFFFFF', 1.4, .9)
    # arrows vertical
    arr(b, 86, 72, 86, 14, '#3D86D6', 0, 0) if False else None

# ---------------------------------------------------------------- 17
@icon('it_microservice', '微服务', CAT)
def _(b):
    b.sh(48, 92, 42, 2.4)
    nodes = [(8, 14, 'appbg', 'glass', 'scr'), (58, 10, 'orange', '#F6D08A', '#B8691F'), (32, 38, 'metal2', 'metal', 'metal3'),
             (6, 60, 'land', '#CFDCA9', 'landdk'), (60, 56, 'appbg', 'glass', 'scr')]
    centers = [(x + 11, y + 8) for x, y, *_ in nodes]
    for i, j in ((0, 2), (1, 2), (2, 3), (2, 4), (0, 3), (1, 4)):
        (x1, y1), (x2, y2) = centers[i], centers[j]
        b.ln(f"M{x1} {y1} L{x2} {y2}", '#5E6A78', 3.4, .9)
        b.ln(f"M{x1} {y1} L{x2} {y2}", '#8FD0FF', 1.4, .9)
    for (x, y, f, t, s), (cx, cy) in zip(nodes, centers):
        box(b, x, y, 22, 16, 8, 5, f, t, s, BL if f in ('appbg',) else MS, 1.1)
        b.ln(f"M{x+4} {y+5} L{x+16} {y+5} M{x+4} {y+9} L{x+11} {y+9}", '#FFFFFF', 1.3, .85)
        b.c(x + 17.5, y + 11.5, 1.2, GREEN)
    gear(b, 78, 38, 5.5, 'metal', MS, 6)
    gear(b, 20, 50, 0.1, 'metal', MS, 6) if False else None

# ---------------------------------------------------------------- 18
@icon('it_registry', '镜像仓库', CAT)
def _(b):
    b.sh(48, 91, 42, 2.4)
    # arrows push / pull
    arr(b, 14, 36, 14, 8, '#43C46B', 3.2, 6)
    arr(b, 82, 8, 82, 36, '#3D86D6', 3.2, 6)
    # little containers sticking out
    container(b, 22, 22, 18, 11, 6, 4, 'appbg', 'glass', 'scr')
    container(b, 44, 18, 18, 11, 6, 4, 'orange', '#F6D08A', '#B8691F')
    container(b, 34, 36, 18, 11, 6, 4, 'land', '#CFDCA9', 'landdk')
    # bin
    b.p("M6 46 L90 46 L82 86 L14 86 Z", 'dkm', DS, 1.4)
    b.p("M6 46 L90 46 L88 52 L8 52 Z", 'metal', MS, 1)
    b.p("M14 58 L82 58 L80 66 L16 66 Z", 'dkm2', None, 1, .5)
    b.r(30, 62, 36, 14, 'white', MS, rx=2, sw=.9)
    b.ln("M35 67 L61 67 M35 71 L52 71", '#8794A3', 1.4)
    b.hl("M10 49 L84 49", 1, .8)
    b.p("M8 47 L88 47", 'none')
    # tag
    b.p("M72 60 L84 60 L88 66 L84 72 L72 72 Z", 'gold', GOLD, .8)
    b.c(76, 66, 1.4, '#3A2D0E')

# ---------------------------------------------------------------- 19
@icon('it_cicd', '持续集成', CAT)
def _(b):
    b.sh(48, 90, 42, 2.4)
    inf = "M48 48 C40 34 18 30 14 48 C18 66 40 62 48 48 C56 34 78 30 82 48 C78 66 56 62 48 48 Z"
    b.drop(inf, 2, 3, .15)
    b.p(inf, 'none', '#25578F', 10)
    b.p("M48 48 C40 34 18 30 14 48 C18 66 40 62 48 48", 'none', '#3D86D6', 7)
    b.p("M48 48 C56 34 78 30 82 48 C78 66 56 62 48 48", 'none', '#43C46B', 7)
    b.ln("M48 48 C40 34 18 30 14 48", '#BFE3FF', 1.4, .8)
    b.ln("M48 48 C56 34 78 30 82 48", '#C9F2D3', 1.4, .8)
    # arrowheads
    b.p("M30 28.5 L22 30.5 L28 36 Z", '#25578F')
    b.p("M66 67.5 L74 65.5 L68 60 Z", '#23813F')
    # stages
    for x, y in ((18, 40), (26, 31), (68, 31), (78, 40)):
        pass
    for (x, y, c) in ((20, 38, '#FFFFFF'), (30, 33, '#FFFFFF'), (66, 63, '#FFFFFF'), (76, 56, '#FFFFFF')):
        b.c(x, y, 3.4, 'metal', MS, .9); b.c(x, y, 1.4, GREEN if y > 50 else '#3D86D6')
    # center play node
    b.c(48, 48, 9, 'metal', MS, 1.2)
    b.p("M45.5 43.5 L53.5 48 L45.5 52.5 Z", '#3D86D6')
    # check badge + gear
    check(b, 82, 80, 7)
    gear(b, 12, 80, 8, 'metal', MS, 8)
    b.ln("M24 84 L38 84", '#3D86D6', 0)

# ---------------------------------------------------------------- 20
@icon('it_os', '国产操作系统', CAT)
def _(b):
    b.sh(48, 91, 38, 2.4)
    b.drop("M8 10 L88 10 L88 66 L8 66 Z", 2.5, 3.5, .18)
    b.r(8, 10, 80, 56, 'dkm', DS, rx=4, sw=1.4)
    b.r(12, 14, 72, 46, '#0E2A4A', None, rx=2)
    b.r(12, 14, 72, 46, 'scr', None, rx=2, op=.8)
    # boot emblem: layered hex-ring spinner (generic)
    cx, cy = 48, 32
    b.c(cx, cy, 11, 'none', '#1F4F8C', 3.2)
    b.ln(f"M{cx-11} {cy} A11 11 0 0 1 {cx} {cy-11}", '#8FD0FF', 3.2)
    b.ln(f"M{cx+11} {cy} A11 11 0 0 1 {cx} {cy+11}", '#BFE3FF', 3.2, .7)
    b.p(f"M{cx} {cy-5} L{cx+5} {cy-2.5} L{cx+5} {cy+2.5} L{cx} {cy+5} L{cx-5} {cy+2.5} L{cx-5} {cy-2.5} Z", 'glow', '#E8F6FF', .8)
    # progress bar
    b.r(30, 50, 36, 4, '#0B1B2E', '#3D86D6', rx=2, sw=.8)
    b.r(31, 51, 22, 2, '#8FD0FF', None, rx=1)
    b.p("M14 15 L50 15 L38 60 L14 60 Z", '#FFFFFF', op=.1)
    b.hl("M11 12 L60 12", 1, .35)
    # stand
    b.p("M40 66 L56 66 L58 78 L38 78 Z", 'metal2', MS, 1.1)
    b.r(28, 78, 40, 7, 'metal', MS, rx=3, sw=1.2)
    b.hl("M32 80 L60 80", 1, .8)
    leds(b, [(78, 62.3, GREEN)])
    # small keyboard/os window hint
    b.r(72, 28, 0.1, 0.1, 'none') if False else None

# ---------------------------------------------------------------- 21
@icon('it_web', '门户网站', CAT)
def _(b):
    b.sh(48, 92, 42, 2.4)
    b.drop("M6 12 L84 12 L84 82 L6 82 Z", 2.5, 3.5, .18)
    win(b, 6, 12, 78, 70, 8, 'white', 'appbg')
    b.r(22, 13.5, 44, 5, '#E3EEF9', None, rx=2.5)
    # nav
    b.r(8, 23, 74, 6, 'metal2', None, rx=1)
    for i in range(5): b.r(11 + i * 14, 24.8, 10, 2.4, '#FFFFFF', None, rx=1.2, op=.9)
    # banner
    b.r(8, 32, 74, 20, 'scr', BL, rx=1.5, sw=.7)
    b.p("M8 52 L24 42 L36 48 L52 36 L70 46 L82 40 L82 52 Z", '#3D86D6', op=.7)
    b.c(70, 40, 4, '#F2A93B')
    b.ln("M13 38 L36 38 M13 43 L28 43", '#FFFFFF', 1.8, .9)
    # cards
    for i, c in enumerate(('glass', 'orange', 'land')):
        b.r(8 + i * 25, 56, 22, 22, c, MS, rx=2, sw=.7)
        b.ln(f"M{11+i*25} 70 L{25+i*25} 70 M{11+i*25} 74 L{21+i*25} 74", '#FFFFFF', 1.3, .85)
        b.r(11 + i * 25, 59, 16, 7, '#FFFFFF', None, rx=1, op=.5)
    # globe
    b.drop("M76 54 A15 15 0 1 0 76.01 54 Z", 2, 3, .2)
    b.c(76, 66, 15, 'node', BL, 1.3)
    b.p("M66 58 Q70 54 76 57 Q74 62 70 63 Q66 64 64 62 Z", 'land', LS, .5, .9)
    b.p("M78 66 Q84 64 88 70 Q86 78 80 79 Q77 74 78 66 Z", 'land', LS, .5, .9)
    b.e(76, 66, 15, 4.5, 'none', '#FFFFFF', .7, .5); b.e(76, 66, 5.5, 15, 'none', '#FFFFFF', .7, .5)
    b.hl("M66 58 Q70 53 76 52", 1.1, .8)

# ---------------------------------------------------------------- 22
@icon('it_mobile', '移动应用', CAT)
def _(b):
    b.sh(46, 92, 34, 2.4)
    # back tablet-ish ghost phone
    b.drop("M44 10 L80 10 L80 84 L44 84 Z", 2.5, 3.5, .18)
    b.r(44, 8, 38, 76, 'dkm2', DS, rx=7, sw=1.3)
    b.r(46, 10, 34, 72, 'dkm', None, rx=6)
    b.r(48.5, 14, 29, 64, '#0E2A4A', None, rx=3)
    b.r(48.5, 14, 29, 64, 'appbg', None, rx=3, op=.9)
    b.r(57, 11, 12, 2.6, 'dkm2', None, rx=1.3)
    # app grid
    cols = ['glass', 'orange', 'land', 'red', 'glass', 'metal', 'orange', 'land', 'appbg']
    for i, c in enumerate(cols):
        gx, gy = i % 3, i // 3
        x, y = 51 + gx * 9.2, 22 + gy * 11
        b.r(x, y, 7.4, 7.4, c, '#FFFFFF', rx=2, sw=.5)
        b.hl(f"M{x+1.5} {y+1.8} L{x+5.5} {y+1.8}", .9, .8)
    b.r(51, 62, 25, 9, '#FFFFFF', None, rx=2.5, op=.35)
    b.ln("M54 66.5 L66 66.5", '#25578F', 1.4)
    b.hl("M50 16 L56 76", 1, .0)
    b.p("M48.5 14 L64 14 L50 78 L48.5 78 Z", '#FFFFFF', op=.1)
    b.c(62, 80, 1.6, '#6A7480')
    # side tablet in front (left)
    b.drop("M8 40 L40 40 L40 84 L8 84 Z", 2.5, 3.5, .2)
    b.r(8, 38, 34, 46, 'metal', MS, rx=4, sw=1.2)
    b.r(11, 41, 28, 38, 'scr', BL, rx=2, sw=.7)
    b.r(11, 41, 28, 5, 'glass', None, rx=1.5, op=.9)
    b.ln("M14 52 L34 52 M14 57 L30 57", '#BFE3FF', 1.4, .85)
    b.r(14, 61, 10, 13, 'orange', None, rx=1.5); b.r(26, 61, 10, 13, 'glass', None, rx=1.5)
    b.c(25, 81.4, 1.2, '#8794A3')
    # notification badge
    b.c(80, 14, 6, '#E2574C', '#8E3129', 1)
    b.ln("M80 11 L80 15.4", '#FFFFFF', 1.8); b.c(80, 17.5, .9, '#FFFFFF')

# ---------------------------------------------------------------- 23
@icon('it_object_store', '对象存储', CAT)
def _(b):
    b.sh(48, 91, 38, 2.6)
    # objects popping out
    container(b, 24, 16, 16, 12, 6, 4, 'orange', '#F6D08A', '#B8691F', False)
    box(b, 46, 8, 16, 14, 6, 4, 'glass', '#DCEFFF', 'scr', BL, 1)
    doc(b, 64, 12, 16, 20, 3)
    b.r(30, 30, 20, 12, 'land', LS, rx=1.5, sw=.9)
    b.p("M32 40 L38 33 L42 37 L45 34 L48 40 Z", '#CFDCA9', op=.9)
    b.c(35, 33.5, 1.4, '#F6D08A')
    # bucket
    b.drop("M12 38 L84 38 L74 86 L22 86 Z", 2.5, 3.5, .18)
    b.p("M12 36 L84 36 L75 86 Q48 92 21 86 Z", 'cylM', MS, 1.4)
    b.p("M12 36 A36 8 0 0 0 84 36 A36 8 0 0 0 12 36 Z", '#1B2A3C', MS, 1.3)
    b.e(48, 36, 35, 6.5, '#0E2A4A', None)
    # blocks visible inside (poking)
    b.p("M18 46 L24 80 M30 46 L33 83 M66 46 L63 83 M78 46 L72 80", 'none', '#8794A3', .7, .0)
    b.p("M13 41 Q48 49 83 41 L81 50 Q48 58 15 50 Z", 'glass', BL, 1)
    b.ln("M16 44 Q48 52 80 44", '#FFFFFF', 1.1, .7)
    # bands
    b.ln("M17 66 Q48 72 79 66", '#6A7685', 1.2, .6)
    b.ln("M19 76 Q48 82 77 76", '#6A7685', 1.2, .6)
    b.hl("M17 52 L23 78", 1.4, .75)
    # handle ring
    b.c(48, 66, 6, 'white', MS, 1); b.c(48, 66, 2.4, '#6FA7DA')
    leds(b, [(48, 79, GREEN)])

# ---------------------------------------------------------------- 24
@icon('it_dw', '数据仓库', CAT)
def _(b):
    b.sh(48, 92, 44, 2.6)
    # warehouse
    b.drop("M6 44 L48 18 L90 44 L90 86 L6 86 Z", 2.5, 3.5, .18)
    b.p("M6 44 L48 16 L90 44 L90 86 L6 86 Z", 'metal', MS, 1.4)
    b.p("M4 46 L48 14 L92 46 L92 52 L48 22 L4 52 Z", 'red', '#6E241B', 1.3)
    b.hl("M8 46 L48 17", 1.2, .6)
    # louvres
    for i in range(3): b.ln(f"M12 {58+i*5} L28 {58+i*5} M68 {58+i*5} L84 {58+i*5}", '#98A4B1', 1.2)
    # door opening
    b.r(30, 54, 36, 32, '#161C24', DS, sw=1.2)
    b.r(30, 54, 36, 8, 'metal2', MS, sw=.9)
    for i in range(3): b.ln(f"M31 {56+i*2.4:.1f} L65 {56+i*2.4:.1f}", '#8794A3', .7)
    # shelves with disks
    b.r(32, 76, 32, 2, 'metal3', None); b.r(32, 66, 32, 2, 'metal3', None)
    for xi, yb in ((38, 76), (48, 76), (58, 76), (43, 66), (53, 66)):
        cyl(b, xi, yb - 7, 4.4, 6, 1.6, 'glass', '#DCEFFF', BL, .7, False)
    b.r(30, 84, 36, 2, 'dkm', None)
    # roof vent / table icon
    b.r(40, 28, 16, 12, 'white', MS, rx=1.5, sw=.8)
    b.ln("M40 32 L56 32 M40 36 L56 36 M46 28 L46 40 M51 28 L51 40", '#6FA7DA', .8)
    b.r(40, 28, 16, 3.5, 'glass', None, rx=1, op=.8)

# ---------------------------------------------------------------- 25
@icon('it_lakehouse', '湖仓一体', CAT)
def _(b):
    b.sh(48, 92, 42, 2.4)
    # water block (lake) front
    b.drop("M6 60 L90 60 L90 86 L6 86 Z", 2, 3, .15)
    b.r(6, 56, 84, 30, 'node', BL, rx=4, sw=1.3)
    b.r(6, 56, 84, 30, 'water', None, rx=4)
    b.p("M6 62 Q16 57 26 62 T46 62 T66 62 T86 62 L90 62 L90 56 L6 56 Z", '#DCEFFF', op=.5)
    for yy, xo in ((66, 0), (74, 8), (81, 3)):
        b.ln(f"M{12+xo} {yy} Q{18+xo} {yy-3} {24+xo} {yy} T{36+xo} {yy} T{48+xo} {yy} T{60+xo} {yy} T{72+xo} {yy}", '#FFFFFF', 1.2, .6)
    # house
    b.drop("M18 34 L48 8 L78 34 L78 58 L18 58 Z", 2.5, 3.5, .2)
    b.p("M20 32 L48 10 L76 32 L76 58 L20 58 Z", 'white', MS, 1.4)
    b.p("M14 36 L48 6 L82 36 L76 38 L48 14 L20 38 Z", 'orange', '#8A4A10', 1.3)
    b.hl("M18 35 L47 9", 1.2, .7)
    b.r(60, 12, 6, 12, 'metal3', MS, sw=.8)
    # table-grid window
    b.r(30, 36, 36, 22, 'scr', BL, rx=2, sw=1)
    b.ln("M30 43 L66 43 M30 50 L66 50 M42 36 L42 58 M54 36 L54 58", '#8FD0FF', .9, .8)
    b.r(30, 36, 36, 6, 'glass', None, rx=1.5, op=.9)
    b.p("M31 37 L45 37 L36 57 L31 57 Z", '#FFFFFF', op=.15)
    b.c(48, 8, 0, 'none')

# ---------------------------------------------------------------- 26
@icon('it_etl', '数据集成', CAT)
def _(b):
    b.sh(48, 90, 44, 2.4)
    # source tables left
    for i, yy in enumerate((10, 34, 58)):
        cyl(b, 14, yy, 10, 14, 3.6, 'cylM', 'metal', MS, 1, True)
        b.ln(f"M8 {yy+8} L20 {yy+8}", '#6FA7DA', 1, .8)
        arr(b, 26, yy + 8, 36, 44 + (i - 1) * 4, '#8794A3', 1.4, 3)
    # funnel + gear center
    b.p("M34 24 L62 24 L62 30 L54 48 L54 66 L42 66 L42 48 L34 30 Z", 'glass', BL, 1.3)
    b.e(48, 24, 14, 3.6, '#DCEFFF', BL, 1.1)
    b.e(48, 24, 11, 2.4, '#0E2A4A', None)
    b.hl("M37 30 L44 46", 1.3, .8)
    gear(b, 48, 52, 5, 'gold', GOLD, 8)
    b.p("M42 66 L54 66 L50 74 L46 74 Z", 'metal3', MS, 1)
    # target warehouse cylinder right
    cyl(b, 80, 28, 11, 36, 4, 'cylM', 'metal', MS, 1.2, True)
    for yy in (40, 52): b.p(f"M69 {yy} A11 4 0 0 0 91 {yy}", 'none', '#6A7685', .9)
    b.ln("M72 34 L88 34", '#6FA7DA', 0)
    leds(b, [(80, 58, GREEN)])
    arr(b, 62, 62, 68, 52, '#3D86D6', 2.2, 4) if False else None
    arr(b, 56, 76, 78, 76, '#3D86D6', 2.6, 5)
    b.ln("M80 66 L80 74", '#3D86D6', 2.2)
    b.ln("M24 76 L40 76", '#3D86D6', 0)

# ---------------------------------------------------------------- 27
@icon('it_stream', '流计算', CAT)
def _(b):
    b.sh(48, 90, 44, 2.4)
    waves = [(22, '#25578F', '#8FD0FF'), (46, '#2F6FB0', '#BFE3FF'), (70, '#25578F', '#8FD0FF')]
    for y, dk, lt in waves:
        d = f"M2 {y} Q14 {y-12} 26 {y} T50 {y} T74 {y} T98 {y}"
        b.ln(d, dk, 9)
        b.ln(d, '#3D86D6', 6.4)
        b.ln(d, lt, 1.4, .8)
    # flowing packets
    for (x, y, c) in ((12, 17, '#F2A93B'), (36, 27, '#FFFFFF'), (62, 17, '#43C46B'),
                      (6, 41, '#FFFFFF'), (30, 51, '#F2A93B'), (56, 41, '#FFFFFF'), (82, 51, '#43C46B'),
                      (14, 65, '#43C46B'), (40, 75, '#FFFFFF'), (66, 65, '#F2A93B')):
        b.r(x - 3, y - 3, 6, 6, c, '#25578F', rx=1.5, sw=.7)
    # processing gate ring
    b.p("M72 6 Q92 6 92 48 Q92 90 72 90 L64 90 Q82 90 82 48 Q82 6 64 6 Z", 'metal', MS, 1.3)
    b.e(76, 48, 6, 42, 'glass', BL, 1.2, .35)
    b.ln("M70 20 Q76 14 82 20", '#FFFFFF', 1.1, .8)
    b.p("M80 38 L72 50 L77 50 L74 60 L84 46 L78 46 Z", 'orange', '#8A4A10', .8)

# ---------------------------------------------------------------- 28
@icon('it_batch', '批处理', CAT)
def _(b):
    b.sh(48, 90, 44, 2.4)
    # conveyor
    b.drop("M4 66 L92 66 L92 82 L4 82 Z", 2, 3, .18)
    b.r(4, 64, 88, 16, 'dkm', DS, rx=8, sw=1.3)
    b.r(7, 67, 82, 10, 'dkm2', None, rx=5)
    for i in range(10):
        cx = 12 + i * 8.2
        b.c(cx, 72, 3.2, 'hub', '#1A1D21', .7)
    b.ln("M8 66 L88 66", '#FFFFFF', 1, .3)
    # batch of crates (3 stacked + more)
    def crate(x, y, w=16, h=13, f='orange', t='#F6D08A', s='#B8691F'):
        box(b, x, y, w, h, 6, 4, f, t, s, MS, .9)
        b.ln(f"M{x+w/2} {y} L{x+w/2} {y+h}", '#FFFFFF', .7, .5)
    crate(8, 50, 16, 14, 'orange', '#F6D08A', '#B8691F')
    crate(8, 36, 16, 14, 'appbg', 'glass', 'scr')
    crate(32, 50, 16, 14, 'land', '#CFDCA9', 'landdk')
    crate(32, 36, 16, 14, 'orange', '#F6D08A', '#B8691F')
    crate(20, 22, 16, 14, 'appbg', 'glass', 'scr')
    # arrows
    arr(b, 54, 56, 66, 56, '#3D86D6', 2.6, 5)
    # processing gear machine
    box(b, 66, 30, 20, 34, 6, 4, 'metal2', 'metal', 'metal3', MS, 1.1)
    b.r(69, 34, 14, 12, 'scr', BL, rx=1.5, sw=.7)
    gear(b, 76, 40, 4.4, 'gold', GOLD, 8)
    port(b, 69, 50); port(b, 74, 50); port(b, 79, 50)
    leds(b, [(70, 56, GREEN), (74, 56, GREEN)])
    # clock badge
    clock(b, 80, 14, 11)

# ---------------------------------------------------------------- 29
@icon('it_tsdb', '时序数据库', CAT)
def _(b):
    b.sh(46, 91, 36, 2.6)
    cyl(b, 40, 14, 30, 68, 8, 'cylM', 'metal', MS, 1.4, True)
    b.p("M10 40 A30 8 0 0 0 70 40 L70 64 A30 8 0 0 1 10 64 Z", '#FFFFFF', op=0)
    # screen band showing waveform
    b.p("M10.5 36 A29.5 8 0 0 0 69.5 36 L69.5 68 A29.5 8 0 0 1 10.5 68 Z", 'scr', BL, 1)
    b.p("M12 38 A28 7 0 0 0 68 38 L68 46 A28 7 0 0 1 12 46 Z", '#FFFFFF', op=.12)
    b.ln("M12 58 Q18 56 22 50 T30 56 T38 44 T46 60 T54 48 T62 54 L68 52", '#8FD0FF', 3.2, .4)
    b.ln("M12 58 Q18 56 22 50 T30 56 T38 44 T46 60 T54 48 T62 54 L68 52", '#E8F6FF', 1.5)
    b.ln("M14 48 L66 48 M14 64 L66 64", '#3D86D6', .6, .6)
    # top disk bands
    b.p("M10 22 A30 8 0 0 0 70 22", 'none', '#6A7685', .9)
    leds(b, [(64, 29, GREEN)])
    b.hl("M13 18 L13 33", 1.4, .8)
    # axes/time badge
    clock(b, 76, 74, 14)
    b.ln("M78 8 L78 42 L92 42", '#5E6A78', 1.6)
    b.ln("M80 36 L84 26 L87 32 L91 18", '#F2A93B', 1.8)
    b.c(91, 18, 1.8, '#F2A93B')

# ---------------------------------------------------------------- 30
@icon('it_graphdb', '图数据库', CAT)
def _(b):
    b.sh(46, 91, 36, 2.6)
    cyl(b, 40, 14, 30, 68, 8, 'cylM', 'metal', MS, 1.4, True)
    b.p("M10.5 34 A29.5 8 0 0 0 69.5 34 L69.5 72 A29.5 8 0 0 1 10.5 72 Z", '#12304F', BL, 1)
    b.p("M12 36 A28 7 0 0 0 68 36 L68 44 A28 7 0 0 1 12 44 Z", '#FFFFFF', op=.1)
    P = [(22, 56), (36, 46), (50, 58), (60, 46), (42, 70), (24, 70)]
    for i, j in ((0, 1), (1, 2), (2, 3), (1, 4), (2, 4), (0, 5), (5, 4), (1, 3)):
        b.ln(f"M{P[i][0]} {P[i][1]} L{P[j][0]} {P[j][1]}", '#8FD0FF', 1.3, .95)
    cols = ['node', 'orange', 'node', 'node', 'node', 'node']
    for k, ((x, y), c) in enumerate(zip(P, cols)):
        b.c(x, y, 4.2, 'orange' if k == 1 else 'node', '#E8F6FF', .8)
    b.hl("M13 18 L13 33", 1.4, .8)
    leds(b, [(64, 29, GREEN)])
    # satellite nodes outside
    for (x, y) in ((82, 20), (86, 46), (80, 74)):
        b.ln(f"M70 {y+ (48-y)*0.0+ (0)} L{x} {y}", '#8794A3', 0)
    b.ln("M70 40 L82 22 M70 52 L86 48 M68 68 L80 74", '#5E6A78', 1.6)
    for (x, y) in ((82, 20), (86, 46), (80, 74)):
        b.c(x, y, 5, 'node', BL, 1); b.c(x - 1.4, y - 1.6, 1.2, '#FFFFFF', op=.8)

# ---------------------------------------------------------------- 31
@icon('it_search', '搜索引擎', CAT)
def _(b):
    b.sh(48, 91, 42, 2.4)
    # search bar
    b.r(6, 8, 84, 22, 'white', MS, rx=11, sw=1.4)
    b.r(9, 11, 78, 16, 'scr', BL, rx=8, sw=.7)
    b.ln("M18 19 L48 19", '#BFE3FF', 2, .9)
    b.ln("M18 19 L34 19", '#FFFFFF', 2, .9)
    b.hl("M16 13.5 L60 13.5", 1, .4)
    # results
    for i, c in enumerate(('glass', 'orange', 'land')):
        y = 36 + i * 17
        b.r(8, y, 56, 14, 'white', MS, rx=2, sw=.8)
        b.r(11, y + 2.5, 9, 9, c, MS, rx=1.5, sw=.6)
        b.ln(f"M24 {y+5} L52 {y+5}", '#25578F', 1.6)
        b.ln(f"M24 {y+9.5} L58 {y+9.5}", '#8794A3', 1.2)
    # magnifier
    b.drop("M74 52 A15 15 0 1 0 74.01 52 Z", 2, 3, .2)
    b.ln("M76 66 L90 86", '#262C33', 8)
    b.ln("M76 66 L90 86", '#6A7480', 5)
    b.ln("M77 65.5 L89 82", '#A5B0BD', 1.2)
    b.c(66, 52, 17, 'metal', MS, 1.4)
    b.c(66, 52, 13, 'glass', BL, 1)
    b.c(66, 52, 13, '#FFFFFF', op=.22)
    b.p("M56 46 Q60 40 68 40 L62 46 Z", '#FFFFFF', op=.7)
    b.ln("M58 55 L74 55 M58 60 L68 60", '#2E5D8B', 1.3, .7)

# ---------------------------------------------------------------- 32
@icon('it_file_server', '文件服务器', CAT)
def _(b):
    b.sh(48, 91, 42, 2.4)
    # NAS in back
    box(b, 46, 14, 34, 54, 10, 6, 'metal2', 'metal', 'metal3', MS, 1.3)
    for i in range(4):
        yy = 18 + i * 11
        b.r(49, yy, 28, 9, 'dkm2', DS, rx=1.2, sw=.7)
        b.r(51, yy + 1.8, 18, 5.4, 'metal3', None, rx=.8)
        b.ln(f"M53 {yy+4.5} L66 {yy+4.5}", '#C9D1DA', .8, .7)
        b.c(73, yy + 4.5, 1.1, GREEN if i != 2 else AMBER)
    # folder front
    b.p("M6 36 Q6 32 10 32 L26 32 L32 38 L52 38 Q56 38 56 42 L56 84 Q56 88 52 88 L10 88 Q6 88 6 84 Z", 'gold', GOLD, 1.3)
    b.p("M6 48 Q6 44 10 44 L74 44 Q78 44 77 48 L72 84 Q71 88 67 88 L10 88 Q6 88 6 84 Z", '#F1D893', GOLD, 1.3) if False else None
    b.p("M6 46 Q6 43 10 43 L72 43 Q76 43 75.5 47 L71 84 Q70 88 66 88 L10 88 Q6 88 6 84 Z", 'gold', GOLD, 1.3)
    b.p("M8 45 L72 45 L72 52 L8 52 Z", '#FFF2C4', op=.4)
    b.hl("M10 46.4 L68 46.4", 1.3, .85)
    # docs in folder
    doc(b, 14, 58, 22, 22, 3)
    b.p("M44 62 L64 62 M44 68 L60 68", 'none', '#8A6A20', 1.4, .7)
    b.r(40, 60, 24, 18, '#FFF2C4', GOLD, rx=1.5, sw=.6, op=.9)
    b.ln("M44 65 L60 65 M44 69 L56 69 M44 73 L58 73", '#A9863A', 1.1)

# ---------------------------------------------------------------- 33
@icon('it_backup', '备份', CAT)
def _(b):
    b.sh(48, 91, 38, 2.6)
    cyl(b, 48, 28, 24, 44, 7, 'cylM', 'metal', MS, 1.3, True)
    for yy in (44, 58): b.p(f"M24 {yy} A24 7 0 0 0 72 {yy}", 'none', '#6A7685', .9)
    b.e(48, 28, 20, 4.8, '#12304F', None, op=.5)
    leds(b, [(64, 52, GREEN), (64, 66, GREEN)])
    b.ln("M32 50 L50 50 M32 64 L46 64", '#6FA7DA', 1.2, .9)
    # circular restore arrow around
    b.ln("M80 40 A36 36 0 1 0 74 68", '#25578F', 8.5, 1) if False else None
    b.ln("M84 52 A38 34 0 1 0 74 74", '#25578F', 7)
    b.ln("M84 52 A38 34 0 1 0 74 74", '#3D86D6', 4.6)
    b.ln("M84 52 A38 34 0 0 0 48 12", '#BFE3FF', 1.2, .8) if False else None
    b.p("M92 46 L78 50 L88 60 Z", '#3D86D6', '#25578F', 1)
    # clock inside arrow
    clock(b, 16, 22, 12)
    b.ln("M4 40 L4 20", '#3D86D6', 0)
    # shield check
    shield(b, 78, 80, 18, 20, 'glass', BL)
    b.ln("M72.5 80 L76.5 84 L84 75.5", '#FFFFFF', 2.2)

# ---------------------------------------------------------------- 34
@icon('it_dr', '灾备中心', CAT)
def _(b):
    def dc(x, y, w, h, dx, dy, ghost=False, main=True):
        box(b, x, y, w, h, dx, dy, 'metal2', 'metal', 'metal3', MS, 1.2)
        b.r(x + 2, y + 2, w - 4, 4, 'dkm2', None, rx=1)
        for i in range(3):
            b.r(x + 3, y + 9 + i * 8, w - 6, 6, 'dkm2', DS, rx=1, sw=.5)
            b.ln(f"M{x+5} {y+12+i*8} L{x+13} {y+12+i*8}", '#6FA7DA', 1, .8)
            b.c(x + w - 6, y + 12 + i * 8, 1.1, GREEN if main or i else AMBER)
    # main center left (solid)
    dc(6, 42, 32, 44, 10, 6)
    star(b, 22, 46, 0.1) if False else None
    # backup right
    dc(58, 38, 28, 48, 8, 5, False, False)
    # sky: cloud / globe link arc
    b.ln("M24 34 Q48 4 74 30", '#3D86D6', 3)
    arr(b, 71, 28, 76, 33, '#3D86D6', 3, 5)
    b.ln("M72 94 L72 94", '#fff', 0)
    # return arrow (below), reversed
    b.ln("M78 62 Q62 62 50 62", '#F2A93B', 0)
    # sync double arrows between
    arr(b, 52, 58, 58, 58, '#F2A93B', 2, 3.5)
    arr(b, 58, 70, 52, 70, '#43C46B', 2, 3.5)
    # return curved arrow (restore) from backup to main
    b.ln("M82 91 Q52 97 26 91", '#43C46B', 2.6)
    arr(b, 26, 91, 16, 86, '#43C46B', 2.6, 5)
    # badge shield on backup
    shield(b, 90, 26, 14, 16, 'gold', GOLD)
    star(b, 90, 26, 3.4, .95)
    # lightning/flame hint of failure on main (small)
    b.p("M30 6 L22 20 L27 20 L24 30 L34 15 L28 15 Z", 'orange', '#8A4A10', .8)
    b.ln("M12 34 L12 38", '#F2A93B', 0)

# ---------------------------------------------------------------- 35
@icon('it_metadata', '数据目录', CAT)
def _(b):
    b.sh(48, 91, 40, 2.4)
    x, y, w, h, dx, dy = 12, 16, 54, 70, 20, 10
    box(b, x, y, w, h, dx, dy, 'metal2', 'metal', 'metal3', MS, 1.3)
    cols = 3
    for r_ in range(4):
        yy = y + 3 + r_ * 16.5
        b.r(x + 3, yy, w - 6, 14, 'metal', MS, rx=1.5, sw=.8)
        b.hl(f"M{x+5} {yy+1.6} L{x+w-5} {yy+1.6}", .9, .8)
        # label slot
        b.r(x + w / 2 - 10, yy + 3.2, 20, 5.6, 'white', '#6A7685', rx=1, sw=.6)
        b.ln(f"M{x+w/2-7} {yy+6} L{x+w/2+7} {yy+6}", '#25578F', 1.2)
        # handle
        b.r(x + w / 2 - 6, yy + 9.6, 12, 2.6, 'gold', GOLD, rx=1.3, sw=.5)
    # pulled-out index card + tag
    b.r(62, 6, 30, 26, 'white', MS, rx=2, sw=1)
    b.r(62, 6, 30, 7, 'appbg', BL, rx=2, sw=.8)
    b.ln("M66 19 L88 19 M66 23 L84 23 M66 27 L80 27", '#8794A3', 1.3)
    b.ln("M66 19 L76 19", '#25578F', 1.3)
    # tag
    b.p("M68 50 L88 50 L94 58 L88 66 L68 66 Z", 'orange', '#8A4A10', 1)
    b.c(73, 58, 2, '#FFFFFF', '#8A4A10', .7)
    b.ln("M78 56 L87 56 M78 61 L85 61", '#FFFFFF', 1.3, .9)
    b.ln("M73 58 L60 62", '#8A4A10', 0)

# ---------------------------------------------------------------- 36
@icon('it_master_data', '主数据', CAT)
def _(b):
    b.sh(48, 91, 40, 2.4)
    # satellites
    S = [(6, 8), (66, 8), (6, 62), (66, 62)]
    for (x, y) in S:
        b.ln(f"M{x+12} {y+9} L48 48", '#5E6A78', 3)
        b.ln(f"M{x+12} {y+9} L48 48", '#8FD0FF', 1.2)
    for k, (x, y) in enumerate(S):
        b.r(x, y, 24, 20, 'white', MS, rx=2.5, sw=1)
        b.r(x, y, 24, 6, ['appbg', 'orange', 'land', 'red'][k], MS, rx=2, sw=.8)
        b.ln(f"M{x+3} {y+10} L{x+21} {y+10} M{x+3} {y+14} L{x+21} {y+14} M{x+10} {y+7} L{x+10} {y+19}", '#8794A3', .9)
    # golden record cylinder
    cyl(b, 48, 32, 17, 30, 5.6, 'gold', '#F1D893', GOLD, 1.3, True)
    for yy in (44, 54): b.p(f"M31 {yy} A17 5.6 0 0 0 65 {yy}", 'none', GOLD, .9, .8)
    b.e(48, 32, 12, 3.4, '#C9A145', None, op=.6)
    # crown / star above
    star(b, 48, 23, 9, 1)
    b.p("M48 14 L50.8 20 L57 21 L52.5 25.4 L53.6 31.6 L48 28.6 L42.4 31.6 L43.5 25.4 L39 21 L45.2 20 Z", '#FFE08A', '#8A6A20', .9)
    leds(b, [(48, 66, GREEN)])

# ---------------------------------------------------------------- 37
@icon('it_data_service', '数据服务', CAT)
def _(b):
    b.sh(48, 91, 42, 2.4)
    # database source
    cyl(b, 22, 12, 16, 50, 5, 'cylM', 'metal', MS, 1.3, True)
    for yy in (26, 40): b.p(f"M6 {yy} A16 5 0 0 0 38 {yy}", 'none', '#6A7685', .9)
    leds(b, [(32, 22, GREEN), (32, 36, GREEN)])
    # pipe to valve
    b.r(36, 52, 36, 7, 'cylM', MS, rx=2, sw=1)
    b.r(36, 50, 4, 11, 'metal', MS, rx=1.5, sw=.8)
    # valve body
    b.p("M60 50 L70 50 L70 64 L60 64 Z", 'metal2', MS, 1)
    b.r(58, 50, 6, 14, 'metal2', MS, rx=1.5, sw=.9)
    b.ln("M64 50 L64 40", '#6A7685', 3)
    b.e(64, 38, 9, 3.2, 'red', '#6E241B', 1)
    b.ln("M56 38 L72 38", '#E9B9AF', 0)
    b.hl("M57 37 L66 37", 1, .8)
    # spout
    b.p("M68 56 L76 56 L76 62 L72 66 L68 66 Z", 'metal2', MS, 1)
    # falling data blocks
    for i, (x, y, c) in enumerate(((66, 67, 'glass'), (76, 70, 'orange'))):
        b.r(x, y, 8, 6, c, BL, rx=1, sw=.6)
        b.ln(f"M{x+1.5} {y+2} L{x+6.5} {y+2}", '#FFFFFF', .9, .8)
    # receiving dashboard
    b.r(46, 66, 0.1, 0.1, 'none') if False else None
    b.r(52, 78, 38, 12, 'dkm', DS, rx=2, sw=1)
    b.r(54, 80, 34, 8, 'scr', None, rx=1)
    for i, hh in enumerate((3, 5, 4, 6)):
        b.r(57 + i * 7, 87 - hh, 4, hh, '#8FD0FF', None, rx=.6)

# ---------------------------------------------------------------- 38
@icon('it_business_obj', '业务对象', CAT)
def _(b):
    b.sh(48, 91, 40, 2.4)
    # small linked cubes
    b.ln("M60 30 L76 18 M36 62 L22 74", '#5E6A78', 3)
    b.ln("M60 30 L76 18 M36 62 L22 74", '#8FD0FF', 1.2)
    box(b, 72, 6, 14, 14, 6, 4, 'orange', '#F6D08A', '#B8691F', MS, 1)
    box(b, 8, 70, 14, 14, 6, 4, 'land', '#CFDCA9', 'landdk', MS, 1)
    box(b, 70, 70, 14, 14, 6, 4, 'metal2', 'metal', 'metal3', MS, 1)
    b.ln("M60 52 L74 70", '#5E6A78', 3); b.ln("M60 52 L74 70", '#8FD0FF', 1.2)
    # main object cube
    box(b, 14, 26, 44, 44, 16, 10, 'glass', '#DCEFFF', 'scr', BL, 1.3)
    b.p("M14 26 L58 26 L58 70 L14 70 Z", '#FFFFFF', op=.12)
    # order sheet on front
    b.r(19, 33, 34, 32, 'white', MS, rx=2, sw=.9)
    b.r(19, 33, 34, 7, 'appbg', BL, rx=2, sw=.8)
    b.c(24, 36.5, 1.5, '#FFFFFF')
    b.ln("M28 36.5 L46 36.5", '#FFFFFF', 1.4, .9)
    for i in range(3):
        yy = 45 + i * 6.4
        b.r(22, yy - 1.4, 8, 2.8, '#BFE3FF', None, rx=1)
        b.ln(f"M33 {yy} L{49-(i%2)*4} {yy}", '#8794A3', 1.4)
    b.hl("M16 28 L52 28", 1, .0)
    b.hl("M16 28.4 L55 28.4", 1.1, .8)

if __name__ == '__main__':
    import re as _re, os, glob
    HERE = os.path.dirname(os.path.abspath(__file__))
    KEYS = [k for k, n, c, fn in ICONS]
    assert len(KEYS) == len(set(KEYS)) == 38, len(KEYS)
    old = set()
    for f in glob.glob(os.path.join(HERE, 'icons*.js')):
        if os.path.basename(f) == 'icons_k.js': continue
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
    open(os.path.join(HERE, 'icons_k.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), 'largest', sorted(SZ)[-8:])
