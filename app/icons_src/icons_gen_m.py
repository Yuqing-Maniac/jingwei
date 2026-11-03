import math

VERT = ('0.3', '0', '0.7', '1')
DIAG = ('0', '0', '1', '1')
HORZ = ('0', '0', '1', '0')

def L(d, *stops):
    return ('l', d, stops)

GR = {
    'air': L(DIAG, (0, '#F4F7FA'), (.5, '#C8D1DB'), (1, '#8D9BAC')),
    'airV': L(VERT, (0, '#F4F7FA'), (.5, '#C8D1DB'), (1, '#8D9BAC')),
    'airdk': L(VERT, (0, '#C2CCD7'), (1, '#7C8A9B')),
    'sea': L(VERT, (0, '#E3E8EE'), (.55, '#B2BDC9'), (1, '#6F7E8E')),
    'seadk': L(VERT, (0, '#A9B4C1'), (1, '#5D6B7A')),
    'deck': L(VERT, (0, '#8C98A6'), (1, '#4F5B68')),
    'boot': L(VERT, (0, '#8E3129'), (1, '#4A1612')),
    'subm': L(VERT, (0, '#7A8693'), (.5, '#414C58'), (1, '#1C232A')),
    'water': ('l', ('0', '0', '0', '1'), ((0, '#8EC3EC', .55), (1, '#3D7FC0', 0))),
    'land': L(VERT, (0, '#B6C78B'), (.5, '#81955A'), (1, '#4E5F35')),
    'landdk': L(VERT, (0, '#86995D'), (1, '#3E4C29')),
    'track': L(VERT, (0, '#454B53'), (1, '#15181C')),
    'canvas': L(VERT, (0, '#A9B97F'), (.6, '#7A8C50'), (1, '#55663A')),
    'white': L(VERT, (0, '#FFFFFF'), (.55, '#E1E6EC'), (1, '#A3AEBB')),
    'whitedk': L(VERT, (0, '#D3DAE2'), (1, '#8F9BA9')),
    'cylW': L(HORZ, (0, '#BCC5D0'), (.3, '#FFFFFF'), (.65, '#DCE2E8'), (1, '#97A3B1')),
    'red': L(VERT, (0, '#D9614F'), (1, '#9B3125')),
    'orange': L(VERT, (0, '#F0B060'), (1, '#B8691F')),
    'metal': L(VERT, (0, '#FBFCFD'), (.55, '#D6DCE3'), (1, '#98A4B1')),
    'metal2': L(VERT, (0, '#C9D1DA'), (1, '#8794A3')),
    'metal3': L(VERT, (0, '#A5B0BD'), (1, '#6A7685')),
    'cylM': L(HORZ, (0, '#AEB8C4'), (.3, '#F6F8FA'), (.7, '#CDD4DC'), (1, '#8794A3')),
    'dkm': L(VERT, (0, '#6A7480'), (.5, '#434B55'), (1, '#262C33')),
    'dkm2': L(VERT, (0, '#4A525C'), (1, '#1E2328')),
    'glass': L(VERT, (0, '#BFE3FF'), (.5, '#78B6EE'), (1, '#3D86D6')),
    'canopy': L(VERT, (0, '#86B7E0'), (.45, '#2E5D8B'), (1, '#0F2339')),
    'scr': L(VERT, (0, '#2F6FB0'), (1, '#0E2A4A')),
    'array': L(DIAG, (0, '#7FA3C8'), (.5, '#3F6690'), (1, '#1E3550')),
    'solar': L(DIAG, (0, '#6E9BD0'), (.5, '#2F5D96'), (1, '#18365C')),
    'gold': L(VERT, (0, '#F1D893'), (.5, '#C9A145'), (1, '#8A6A20')),
    'skin': L(VERT, (0, '#E6C49C'), (1, '#A98560')),
    'uniform': L(VERT, (0, '#8BA3BE'), (.5, '#56708F'), (1, '#33495F')),
    'cloud': L(DIAG, (0, '#FFFFFF'), (.5, '#D3E2F1'), (1, '#86A7CB')),
    'appbg': L(DIAG, (0, '#8FC6F5'), (.5, '#4C8FD6'), (1, '#24599A')),
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
from collections import namedtuple

Mark = namedtuple('Mark', 'x y s')
Ray = namedtuple('Ray', 'x y s a')
Row = namedtuple('Row', 'key name cat platform role')

PLATFORMS = {}
ROLES = {}

def platform(pid):
    def deco(fn):
        if pid in PLATFORMS:
            raise KeyError(pid)
        PLATFORMS[pid] = fn
        return fn
    return deco

def role(rid):
    def deco(fn):
        if rid in ROLES:
            raise KeyError(rid)
        ROLES[rid] = fn
        return fn
    return deco

def ray_end(ray):
    a = math.radians(ray.a)
    return ray.x + ray.s * math.cos(a), ray.y + ray.s * math.sin(a)

def ray_to(x1, y1, x2, y2):
    return Ray(x1, y1, round(math.hypot(x2 - x1, y2 - y1), 1), round(math.degrees(math.atan2(y2 - y1, x2 - x1)), 1))

def bounds(v):
    if isinstance(v, Mark):
        return (v.x - v.s / 2.0, v.y - v.s / 2.0, v.x + v.s / 2.0, v.y + v.s / 2.0)
    if isinstance(v, Ray):
        x2, y2 = ray_end(v)
        return (min(v.x, x2), min(v.y, y2), max(v.x, x2), max(v.y, y2))
    if isinstance(v, tuple) and v:
        bs = [bounds(i) for i in v]
        return (min(t[0] for t in bs), min(t[1] for t in bs), max(t[2] for t in bs), max(t[3] for t in bs))
    raise TypeError(type(v).__name__)

ARC = '#3D86D6'
ARC2 = '#8FD0FF'

def draw_boom(b, ray):
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    fat = ray.s >= 48
    bl = 22.0 if fat else min(16.0, ray.s * .36)
    thick = 14.0 if fat else 9.0
    a = math.radians(ray.a)
    ux, uy = math.cos(a), math.sin(a)
    bx, by = x2 - ux * bl, y2 - uy * bl
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{bx:.1f} {by:.1f}', '#5E6A78', 4.4 if fat else 3.2)
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{bx:.1f} {by:.1f}', '#E8EDF2', 1.35 if fat else 1.05)
    if abs(ux) >= abs(uy):
        x0, x1 = (bx, x2) if bx <= x2 else (x2, bx)
        cy = (by + y2) / 2.0
        r = thick / 2.0
        b.p(
            f'M{x0 + r:.1f} {cy - r:.1f} L{x1 - r:.1f} {cy - r:.1f} '
            f'A{r:.1f} {r:.1f} 0 0 1 {x1 - r:.1f} {cy + r:.1f} '
            f'L{x0 + r:.1f} {cy + r:.1f} A{r:.1f} {r:.1f} 0 0 1 {x0 + r:.1f} {cy - r:.1f} Z',
            'metal', MS, 1.05,
        )
        b.hl(f'M{x0 + r + 1:.1f} {cy - r + 1.8:.1f} L{x1 - r - 1:.1f} {cy - r + 1.8:.1f}', 1.05, .75)
        b.r((x0 + x1) / 2.0 - 1.5, cy - r + 1.2, 3, thick - 2.4, 'dkm')
    else:
        y0, y1 = (by, y2) if by <= y2 else (y2, by)
        cx = (bx + x2) / 2.0
        cyl(b, cx, y0, thick / 2.0, y1 - y0, ry=min(3.2, thick / 3.0), fill='cylM', top='metal', st=MS, sw=1.05)
        b.r(cx - thick / 2.0, (y0 + y1) / 2.0 - 1.3, thick, 2.6, 'dkm')

def draw_dip(b, mark):
    if not isinstance(mark, Mark):
        raise TypeError(type(mark).__name__)
    r = mark.s / 2.0
    b.c(mark.x, mark.y, r, 'sphere', MS, 1.1)
    b.e(mark.x, mark.y + r * .15, r * .72, r * .28, '#7FB4E0', op=.28)
    b.c(mark.x, mark.y, r * .4, 'lens', '#05101C', .8)
    b.e(mark.x, mark.y - r * .55, r * .55, r * .16, 'metal3', MS, .7)
    glint(b, mark.x - r * .28, mark.y - r * .32, max(r * .3, 1.2), max(r * .14, .6))

def draw_crate(b, mark):
    if not isinstance(mark, Mark):
        raise TypeError(type(mark).__name__)
    s = mark.s
    w, h = s * .70, s * .62
    dx, dy = s * .22, s * .16
    x = mark.x - (w + dx) / 2.0
    y = mark.y - (h - dy) / 2.0
    box(b, round(x, 1), round(y, 1), round(w, 1), round(h, 1), round(dx, 1), round(dy, 1), 'metal2', 'metal', 'metal3', MS, 1.05)
    b.ln(f'M{x + 3:.1f} {y + h * .5:.1f} L{x + w - 3:.1f} {y + h * .5:.1f}', '#6A7685', .9, .85)
    b.ln(f'M{x + w * .5:.1f} {y + 2.4:.1f} L{x + w * .5:.1f} {y + h - 2.4:.1f}', '#6A7685', .9, .85)
    b.hl(f'M{x + 1.4:.1f} {y + 1.6:.1f} L{x + 1.4:.1f} {y + h - 2:.1f}', .8, .6)

PLATFORM_KEYS = {
    'fw': ('marks', 'boom', 'drop'),
    'ruav': ('ball', 'stubs', 'pods', 'masts', 'hook', 'skin', 'marks'),
    'loiter': ('ball', 'pods', 'masts', 'marks'),
    'usv': ('ball', 'pods', 'masts', 'crate', 'stern', 'skin', 'marks'),
    'uuv': ('nose', 'shot', 'buoy', 'crate', 'tow', 'skin'),
    'ugv': ('pods', 'masts', 'skin', 'marks'),
    'patrol': ('boom', 'drop'),
    'heli': ('cable', 'masttop'),
    'sat': ('nadir', 'zenith', 'look'),
    'msl': ('nose', 'mid', 'tail'),
    'fold': (),
    'attack': (),
    'elint_air': (),
    'ssbn': (),
    'elint_ship': (),
    'lsd': (),
    'depth_rl': (),
    'vls': (),
    'aaa': (),
    'atgm': (),
    'coastal': (),
    'mad': (),
    'dipset': (),
    'iff': (),
    'rwr': (),
    'atc': (),
    'hangar': (),
    'bunker': (),
}

ROLE_KEYS = {
    'corner': ('marks',),
    'asw': ('boom', 'drop'),
    'eo': ('ball',),
    'stores': ('stubs',),
    'jam': ('pods',),
    'relay': ('masts',),
    'sling': ('hook',),
    'bands': ('skin',),
    'mines': ('stern',),
    'torp': ('shot',),
    'jam_acoustic': ('nose',),
    'relay_buoy': ('buoy',),
    'crate': ('crate',),
    'acoustic': ('tow',),
    'dip': ('cable',),
    'dome': ('masttop',),
    'scope': ('nadir',),
    'dish': ('zenith',),
    'navclock': ('nadir',),
    'limb': ('look',),
    'sea_skim': ('nose', 'mid'),
    'dart': ('nose', 'tail'),
    'spiral': ('nose',),
}

BODY = {
    'fw': (32, 28, 36, 48),
    'ruav': (24, 14, 56, 48),
    'loiter': (18, 36, 56, 22),
    'usv': (22, 48, 58, 32),
    'uuv': (22, 34, 56, 36),
    'ugv': (18, 46, 60, 36),
    'patrol': (26, 30, 54, 40),
    'heli': (22, 26, 58, 46),
    'sat': (30, 22, 36, 40),
    'msl': (28, 40, 44, 24),
}

def _piece_long(v):
    if isinstance(v, (Mark, Ray)):
        return v.s
    return max(_piece_long(i) for i in v)

def _mark_breaks(row, slots):
    parts = [slots[k] for k in ROLE_KEYS[row.role]]
    bs = [bounds(p) for p in parts]
    x0 = min(t[0] for t in bs)
    y0 = min(t[1] for t in bs)
    x1 = max(t[2] for t in bs)
    y1 = max(t[3] for t in bs)
    long = max([_piece_long(p) for p in parts] + [x1 - x0, y1 - y0])
    if long < 26:
        raise AssertionError((row.key, 'mark', round(long, 1)))
    bx, by, bw, bh = BODY[row.platform]
    if x0 >= bx and y0 >= by and x1 <= bx + bw and y1 <= by + bh:
        raise AssertionError((row.key, 'inside body'))

def draw(row, b):
    slots = PLATFORMS[row.platform](b)
    need = PLATFORM_KEYS[row.platform]
    missing = [k for k in need if k not in slots]
    if missing:
        raise KeyError((row.key, missing))
    extra = [k for k in slots if k not in need]
    if extra or len(slots) != len(need):
        raise KeyError((row.key, 'slots', tuple(slots), need))
    if row.role is None:
        return slots
    for k in ROLE_KEYS[row.role]:
        if k not in slots or slots[k] is None:
            raise KeyError((row.key, k))
    _mark_breaks(row, slots)
    ROLES[row.role](b, slots)
    return slots

@platform('fw')
def fw(b):
    b.sh(48, 80, 26, 2.6)
    b.p('M40 62 L30 78 L42 70 Z', 'airdk', AS, 1)
    b.p('M56 62 L66 78 L54 70 Z', 'airdk', AS, 1)
    b.p('M18 42 L78 42 L78 56 L18 56 Z', 'air', AS, 1.15)
    b.hl('M20 44.2 L76 44.2', 1.15, .8)
    b.p('M41 16 L55 16 L57 66 L48 76 L39 66 Z', 'airV', AS, 1.2)
    b.hl('M43.4 20 L43.4 64', 1.05, .75)
    b.e(48, 24, 4.2, 5, 'canopy', '#1B2D40', .85)
    glint(b, 46, 21, 1.6, 1.1)
    b.e(48, 68, 7, 2.2, 'prop')
    b.ln('M41 68 L55 68', '#2E3640', 1.5)
    b.c(48, 68, 1.6, 'hub')
    return {
        'marks': (Mark(10, 49, 22), Mark(86, 49, 22), Mark(48, 12, 18)),
        'boom': Ray(48, 64, 28, 90),
        'drop': Mark(62, 84, 16),
    }

@platform('ruav')
def ruav(b):
    b.sh(58, 59, 16, 2)
    b.p('M40 36 L26 24 L30 24 L42 38 Z', 'airdk', AS, 1)
    b.e(32, 40, 2.2, 5, 'prop')
    b.ln('M32 35 L32 45', '#2E3640', 1.3)
    b.c(32, 40, 1.2, 'hub')
    b.p('M36 40 L56 42 L56 48 L36 46 Z', 'airdk', AS, 1)
    b.p('M50 38 C62 34 76 36 78 44 C78 52 66 56 52 54 L46 48 Z', 'airV', AS, 1.2)
    b.hl('M54 39.4 C62 36.6 72 37.2 76 42', 1, .75)
    b.ln('M50 54 L48 60 M72 54 L74 60', '#3A434E', 1.6)
    b.ln('M44 60 L78 60', '#3A434E', 2.2)
    b.ln('M46 60 L76 60', '#8592A2', .7)
    b.r(58, 20, 3.2, 12, '#3A434E')
    rotor(b, 60, 28, 14, 16)
    return {
        'ball': Ray(62, 46, 40, 90),
        'stubs': (Mark(76, 42, 32), Mark(74, 56, 30)),
        'pods': (Mark(38, 26, 28), Mark(66, 72, 28)),
        'masts': (ray_to(48, 36, 42, 8), ray_to(60, 32, 60, 5), ray_to(70, 38, 76, 8)),
        'hook': Mark(62, 76, 40),
        'skin': Mark(50, 46, 42),
        'marks': (Mark(36, 10, 18), Mark(22, 70, 26), Mark(84, 64, 20)),
    }

@platform('loiter')
def loiter(b):
    b.sh(48, 86, 24, 2.6)
    b.p('M14 20 L62 64 L50 76 L4 32 Z', 'white', WS, 1.1)
    b.p('M14 72 L50 20 L62 32 L24 82 Z', 'whitedk', WS, 1.1)
    b.hl('M18 28 L54 62', 1.05, .7)
    b.p('M22 42 L58 38 L72 46 L58 54 L22 50 Z', 'white', WS, 1.15)
    b.hl('M26 44.2 L60 40.4', .95, .75)
    b.e(12, 46, 3.2, 8, 'prop')
    b.ln('M12 38 L12 54', '#2E3640', 1.6)
    b.c(12, 46, 1.6, 'hub')
    return {
        'ball': Ray(68, 46, 26, 0),
        'pods': (Mark(34, 30, 26), Mark(52, 30, 26)),
        'masts': (ray_to(36, 40, 24, 14), ray_to(48, 38, 46, 8), ray_to(60, 40, 70, 14)),
        'marks': (Mark(18, 22, 22), Mark(64, 22, 22), Mark(16, 74, 22), Mark(66, 74, 22)),
    }

@platform('usv')
def usv(b):
    b.e(50, 70, 26, 8, 'uwater')
    b.ln('M28 66 Q36 64 44 66 T60 66', '#FFFFFF', .9, .5)
    b.p('M28 64 L26 60 L64 54 L78 60 L74 70 L30 70 Z', 'sea', SS, 1.15)
    b.p('M32 65 L74 65 L72 70 L30 70 Z', 'boot', '#4A1612', 1)
    b.hl('M30 61.2 L66 56', 1, .75)
    b.ln('M40 59 L60 56.4', '#5D6B7A', .8, .55)
    return {
        'ball': Ray(56, 56, 34, 270),
        'pods': (Mark(40, 38, 28), Mark(62, 36, 28)),
        'masts': (ray_to(40, 58, 36, 28), ray_to(52, 58, 52, 20), ray_to(66, 58, 68, 28)),
        'crate': Mark(52, 46, 32),
        'stern': (Mark(16, 58, 22), Mark(16, 74, 20)),
        'skin': Mark(52, 62, 46),
        'marks': (Mark(86, 58, 18), Mark(14, 50, 26), Mark(16, 74, 22)),
    }

@platform('uuv')
def uuv(b):
    b.e(50, 52, 26, 16, '#7FB4E0', op=.28)
    b.e(50, 52, 22, 12, 'uwater')
    b.e(28, 52, 2, 6, 'prop')
    b.ln('M28 46 L28 58', '#2E3640', 1.3)
    b.p('M32 52 C32 45 44 42 56 42 L68 43 C74 45 76 48 76 52 C76 56 74 59 68 61 L56 62 C44 62 32 59 32 52 Z', 'subm', '#11161B', 1.15)
    b.hl('M38 46.2 L70 44.6', 1, .6)
    b.ln('M44 42 L44 62 M58 43 L58 61', '#2A323B', .6, .45)
    return {
        'nose': Mark(80, 52, 26),
        'shot': Ray(62, 50, 30, 0),
        'buoy': Ray(50, 44, 26, 270),
        'crate': Mark(50, 28, 38),
        'tow': Ray(42, 52, 26, 180),
        'skin': Mark(52, 52, 44),
    }

@platform('ugv')
def ugv(b):
    b.sh(48, 79, 24, 2)
    b.p('M24 62 L68 58 L76 64 L72 70 L22 70 Z', 'land', LS, 1.15)
    b.r(26, 64, 46, 5, 'landdk', LS, rx=1, sw=.8)
    for x in (32, 46, 58, 70):
        wheel(b, x, 72, 6.2)
    b.hl('M26 62.6 L68 59', 1, .7)
    return {
        'pods': (Mark(36, 36, 28), Mark(58, 34, 30)),
        'masts': (ray_to(40, 58, 34, 14), ray_to(52, 58, 52, 8), ray_to(64, 58, 70, 14)),
        'skin': Mark(48, 64, 50),
        'marks': (Mark(48, 34, 26), Mark(84, 64, 18), Mark(12, 66, 18)),
    }

@platform('patrol')
def patrol(b):
    b.sh(52, 66, 20, 2.2)
    b.p('M36 40 L26 32 L30 32 L40 42 Z', 'airdk', AS, 1)
    b.p('M36 54 L26 64 L30 64 L40 52 Z', 'airdk', AS, 1)
    b.p('M30 34 L74 32 L76 40 L32 42 Z', 'air', AS, 1.1)
    b.hl('M32 35.2 L72 33.4', 1, .7)
    b.e(46, 43, 5, 3.2, 'airdk', AS, 1)
    b.e(62, 42.4, 5, 3.2, 'airdk', AS, 1)
    b.e(46, 40.4, 2.2, 1, '#3A4552')
    b.e(62, 39.8, 2.2, 1, '#3A4552')
    b.p('M32 44 L66 40 L78 46 L66 52 L32 50 Z', 'airV', AS, 1.2)
    b.p('M60 40 C66 34 74 35 76 42 L68 43 Z', 'canopy', '#1B2D40', .85)
    glint(b, 68, 37, 2, .8)
    b.hl('M34 45.2 L74 41.4', 1, .75)
    return {
        'boom': Ray(36, 48, 28, 180),
        'drop': Mark(58, 82, 16),
    }

@platform('heli')
def heli(b):
    b.sh(54, 68, 18, 2)
    b.p('M40 40 L24 30 L28 30 L42 42 Z', 'airdk', AS, 1)
    b.e(30, 44, 2.2, 5, 'prop')
    b.ln('M30 39 L30 49', '#2E3640', 1.2)
    b.c(30, 44, 1.2, 'hub')
    b.p('M34 42 L54 44 L54 50 L34 48 Z', 'airdk', AS, 1)
    b.p('M48 40 C60 36 74 38 78 46 C76 56 62 58 50 56 L44 48 Z', 'airV', AS, 1.2)
    b.p('M62 38 C70 32 78 34 78 42 L70 44 Z', 'canopy', '#1B2D40', .85)
    glint(b, 70, 35, 2, .8)
    b.hl('M52 41.2 C60 38.2 70 38.6 76 43', 1, .7)
    b.ln('M48 56 L46 64 M70 56 L72 64', '#3A434E', 1.6)
    b.ln('M42 64 L76 64', '#3A434E', 2.2)
    b.r(56, 34, 3.2, 10, '#3A434E')
    rotor(b, 58, 42, 15, 18)
    return {
        'cable': Ray(58, 60, 26, 90),
        'masttop': Mark(58, 16, 34),
    }

@platform('sat')
def sat(b):
    b.p('M30 38 L42 36 L42 48 L30 46 Z', 'metal2', MS, 1)
    b.p('M54 36 L66 38 L66 46 L54 48 Z', 'metal2', MS, 1)
    b.hl('M32 39 L40 37.4', .8, .7)
    b.r(42, 26, 12, 32, 'metal', MS, rx=1.4, sw=1.1)
    b.hl('M44 28 L44 54', 1, .75)
    b.ln('M42 40 L54 40 M42 48 L54 48', '#8F9BA9', .6, .55)
    return {
        'nadir': Ray(48, 58, 34, 90),
        'zenith': Ray(64, 40, 34, 0),
        'look': ray_to(52, 34, 78, 28),
    }

@platform('msl')
def msl(b):
    b.sh(48, 64, 28, 2.4)
    b.p('M18 38 L62 38 C70 38 74 42 74 48 C74 54 70 58 62 58 L18 58 C12 58 8 54 8 48 C8 42 12 38 18 38 Z', 'white', WS, 1.2)
    b.p('M62 38 L86 48 L62 58 Z', 'whitedk', WS, 1.05)
    b.hl('M16 42 L70 42', 1.15, .8)
    b.hl('M34 47.4 L64 47.4', 1, .8)
    b.ln('M40 46 L40 54 M52 46 L52 54', '#8F9BA9', .55, .5)
    return {
        'nose': Mark(78, 48, 26),
        'mid': Mark(44, 52, 26),
        'tail': Mark(20, 48, 24),
    }
@platform('fold')
def fold(b):
    b.sh(48, 88, 26, 3)
    b.p('M40 68 L28 86 L36 88 L48 74 L60 88 L68 86 L56 68 Z', 'airdk', AS, 1)
    b.p('M20 40 L42 36 L44 50 L22 52 Z', 'air', AS, 1.1)
    b.p('M76 40 L54 36 L52 50 L74 52 Z', 'air', AS, 1.1)
    b.hl('M24 41.2 L40 37.6', .95, .75)
    b.hl('M56 37.6 L72 41.2', .95, .55)
    b.p('M12 18 L22 14 L24 50 L14 52 Z', 'airdk', AS, 1.05)
    b.p('M84 18 L74 14 L72 50 L82 52 Z', 'airdk', AS, 1.05)
    b.hl('M14 22 L20 17', .85, .7)
    b.p('M42 10 C44 6 52 6 54 10 L56 72 L48 84 L40 72 Z', 'airV', AS, 1.2)
    b.e(48, 22, 3.6, 6.2, 'canopy', '#1B2D40', .8)
    glint(b, 47, 18, 1.3, 1.6)
    b.hl('M44.4 12 L44.4 40', 1, .75)
    return {}

@platform('attack')
def attack(b):
    b.sh(48, 84, 30, 3)
    b.p('M42 66 L26 80 L32 84 L46 72 L50 72 L64 84 L70 80 L54 66 Z', 'airdk', AS, 1)
    b.p('M6 42 L40 40 L56 40 L90 42 L90 56 L56 54 L40 54 L6 56 Z', 'air', AS, 1.15)
    b.hl('M8 43.6 L38 41.4', 1.05, .75)
    b.p('M38 22 C40 16 56 16 58 22 L60 68 L52 80 L44 80 L36 68 Z', 'airV', AS, 1.2)
    b.p('M40 18 L56 18 L58 28 L38 28 Z', 'airdk', AS, 1)
    b.r(45, 8, 6, 12, 'dkm', DS, rx=1.2, sw=.9)
    b.hl('M46.2 10 L46.2 18', .8, .6)
    b.e(48, 26, 4.2, 4.6, 'canopy', '#1B2D40', .75)
    glint(b, 47, 23.4, 1.1, 1.4)
    b.hl('M42 20 C41.4 28 41.2 36 41.2 46', 1, .7)
    return {}

@platform('elint_air')
def elint_air(b):
    b.sh(50, 78, 34, 3)
    b.p('M30 38 L12 24 L18 24 L34 42 Z', 'airdk', AS, 1.05)
    b.p('M30 56 L12 70 L18 70 L34 52 Z', 'airdk', AS, 1.05)
    b.p('M20 44 L8 44 L10 52 L20 52 Z', 'airdk', AS, .9)
    b.p('M26 58 L34 74 L78 74 L86 56 L76 58 L36 58 Z', 'metal3', MS, 1.1)
    b.hl('M38 60.4 L76 60.4', .9, .6)
    b.ln('M42 66 L74 66', '#6A7685', .7, .5)
    b.p('M38 46 L16 26 L28 24 L50 46 Z', 'air', AS, 1.05)
    b.hl('M22 28 L46 44', .9, .65)
    b.p('M22 44 L72 38 L90 46 L74 56 L22 54 Z', 'airV', AS, 1.2)
    b.p('M58 38 L82 34 L86 42 L62 44 Z', 'array', '#C5DCF6', 1)
    b.p('M56 50 L84 52 L80 58 L54 54 Z', 'metal2', MS, 1)
    plate_dots(b, 62, 36, 18, 6, 3, 2, 1.15)
    b.p('M66 38 C74 30 86 32 88 42 L78 44 Z', 'canopy', '#1B2D40', .85)
    glint(b, 76, 34, 2.4, 1)
    b.hl('M26 46.2 L80 40.6', 1.1, .75)
    return {}

@platform('ssbn')
def ssbn(b):
    b.p('M18 50 L10 40 L16 40 L24 50 Z', 'subm', '#11161B', 1)
    b.p('M18 58 L10 68 L16 68 L24 58 Z', 'subm', '#11161B', 1)
    b.e(8, 54, 2.2, 7, 'prop')
    b.ln('M8 48 L8 60', '#2E3640', 1.2)
    b.p('M20 48 C30 42 42 42 54 42 L82 44 C90 46 94 50 94 54 C94 58 90 62 82 62 L54 62 C42 62 30 62 20 60 Z', 'subm', '#11161B', 1.15)
    b.p('M70 42 L72 30 L80 30 L82 42 Z', 'subm', '#11161B', 1)
    b.hl('M73 31.4 L79 31.4', .8, .65)
    for x in (28, 36, 44, 52, 60):
        b.c(x, 52, 3.3, 'metal2', '#1C232A', .85)
        b.c(x, 52, 1.3, 'dkm')
    b.hl('M26 46.4 L86 45', 1, .55)
    b.r(0, 56, 96, 32, 'water')
    b.ln('M2 56 Q8 54 14 56 T26 56 T38 56 T50 56 T62 56 T74 56 T86 56', '#FFFFFF', 1, .6)
    return {}

@platform('elint_ship')
def elint_ship(b):
    b.p('M4 56 L74 50 L94 58 L86 74 L12 74 L6 64 Z', 'sea', SS, 1.2)
    b.p('M10 68 L86 68 L84 74 L14 74 Z', 'boot', '#4A1612', 1)
    b.p('M30 50 L34 38 L72 38 L78 50 Z', 'seadk', SS, 1.05)
    b.p('M36 40 L50 40 L50 48 L36 46 Z', 'array', '#C5DCF6', 1)
    b.p('M54 40 L68 40 L68 48 L54 46 Z', 'array', '#C5DCF6', 1)
    plate_dots(b, 37, 41, 12, 6, 3, 2, 1.15)
    plate_dots(b, 55, 41, 12, 6, 3, 2, 1.15)
    for x, top in ((34, 16), (46, 10), (58, 18), (66, 14)):
        b.r(x, top, 2.6, 38 - top, 'metal2', MS, rx=.6, sw=.7)
        b.hl(f'M{x + .6:.1f} {top + 2:.0f} L{x + .6:.1f} 36', .7, .65)
    b.e(40, 18, 5, 2.2, 'metal', MS, .8)
    b.e(62, 16, 4.2, 2, 'metal', MS, .8)
    b.c(46, 10, 1.6, 'dkm')
    b.hl('M8 57.4 L74 51.6 L92 58.4', 1, .7)
    water(b, 66)
    return {}

@platform('lsd')
def lsd(b):
    b.p('M20 54 L78 48 L94 58 L86 74 L22 74 Z', 'sea', SS, 1.2)
    b.p('M24 68 L86 68 L84 74 L24 74 Z', 'boot', '#4A1612', 1)
    b.p('M60 48 L64 34 L80 34 L84 48 Z', 'seadk', SS, 1)
    b.r(68, 36, 8, 6, 'canopy', '#1B2D40', rx=.6, sw=.6)
    glint(b, 70, 37.4, 2, .7)
    b.p('M24 56 L54 54 L54 66 L26 68 Z', 'dkm', DS, .9)
    b.p('M30 58 L46 57 L48 63 L32 64 Z', 'metal', MS, .85)
    b.hl('M32 58.6 L44 57.8', .7, .7)
    b.p('M20 56 L8 70 L14 74 L24 62 Z', 'metal3', MS, 1.05)
    b.hl('M12 68 L20 60', .8, .6)
    b.hl('M24 55.4 L76 49.6', 1, .7)
    water(b, 66)
    return {}

@platform('depth_rl')
def depth_rl(b):
    water(b, 58)
    b.p('M8 58 L42 50 L50 58 L46 68 L10 68 Z', 'sea', SS, 1.1)
    b.p('M14 62 L44 62 L42 68 L14 68 Z', 'boot', '#4A1612', .9)
    b.hl('M12 56 L40 51.2', .9, .65)
    for x, h in ((16, 14), (24, 18), (32, 16), (22, 12)):
        b.r(x, 50 - h, 7, h, 'metal2', MS, rx=1.2, sw=.9)
        b.e(x + 3.5, 50 - h, 3.5, 1.6, 'metal', MS, .75)
        b.hl(f'M{x + 1.4:.1f} {52 - h:.0f} L{x + 1.4:.1f} 48', .7, .6)
    b.c(72, 72, 8, 'none', '#FFFFFF', 1.8, op=.85)
    b.c(72, 72, 3.6, '#FFFFFF', op=.4)
    b.c(82, 78, 3.2, 'none', '#FFFFFF', 1.3, op=.6)
    return {}

@platform('vls')
def vls(b):
    b.sh(48, 88, 36, 3)
    b.r(8, 14, 80, 68, 'metal3', MS, rx=2, sw=1.15)
    b.hl('M10 16 L86 16', 1, .6)
    for j in range(4):
        for i in range(4):
            x = 14 + i * 18
            y = 20 + j * 15
            if i == 2 and j == 1:
                b.r(x, y, 15, 12, 'dkm', DS, rx=.7, sw=.8)
                b.p(f'M{x + 4} {y + 11} L{x + 7.5} {y + 2} L{x + 11} {y + 11} Z', 'white', WS, .85)
                b.hl(f'M{x + 6.2} {y + 4} L{x + 6.2} {y + 8}', .7, .7)
            else:
                b.r(x, y, 15, 12, 'metal', MS, rx=.7, sw=.8)
                b.ln(f'M{x + 1.4} {y + 6} L{x + 13.6} {y + 6}', '#8F9BA9', .55, .65)
    return {}

@platform('aaa')
def aaa(b):
    b.sh(48, 86, 20, 3)
    b.e(48, 80, 18, 5, 'metal3', MS, 1)
    b.e(48, 78, 10, 2.6, 'metal2', MS, .8)
    b.r(44, 58, 8, 20, 'metal2', MS, rx=1, sw=1)
    b.p('M26 56 L70 48 L72 62 L28 68 Z', 'metal', MS, 1.1)
    b.hl('M30 55 L66 49', .95, .7)
    b.ln('M46 54 L76 14', '#2E3640', 4.4)
    b.ln('M54 56 L84 16', '#2E3640', 4.4)
    b.ln('M46 54 L76 14', '#C5CED8', 1.35)
    b.ln('M54 56 L84 16', '#C5CED8', 1.35)
    b.c(76, 14, 2.2, 'dkm')
    b.c(84, 16, 2.2, 'dkm')
    return {}

@platform('atgm')
def atgm(b):
    b.sh(48, 82, 32, 3)
    b.p('M12 62 L74 58 L88 66 L84 72 L14 72 Z', 'land', LS, 1.15)
    b.r(18, 66, 64, 5, 'landdk', LS, rx=1, sw=.8)
    for x in (24, 42, 60, 76):
        wheel(b, x, 74, 6.4)
    b.r(22, 40, 52, 18, 'metal2', MS, rx=1.4, sw=1.05)
    b.hl('M24 41.4 L72 41.4', .95, .7)
    for i in range(4):
        y = 43.2 + i * 3.6
        b.r(26, y, 42, 2.8, 'white', WS, rx=1.3, sw=.6)
        b.c(68, y + 1.4, 1.5, 'dkm')
    b.hl('M16 62.6 L74 59', .9, .6)
    return {}

@platform('coastal')
def coastal(b):
    water(b, 56)
    b.p('M0 52 L48 52 L42 78 L0 86 Z', 'land', LS, 1.05)
    b.p('M0 64 L36 64 L32 84 L0 88 Z', 'landdk', LS, .9)
    b.r(8, 40, 30, 24, 'metal3', MS, rx=1, sw=1.05)
    b.hl('M10 41.4 L36 41.4', .85, .65)
    b.p('M22 56 L64 30 L74 42 L32 68 Z', 'landdk', LS, 1.1)
    b.p('M28 52 L60 34 L64 39 L32 57 Z', 'white', WS, .85)
    b.p('M30 60 L62 42 L66 47 L34 65 Z', 'white', WS, .85)
    b.hl('M26 50 L58 32', .9, .7)
    b.ln('M48 58 Q70 62 88 70', '#FFFFFF', 1, .45)
    return {}

@platform('mad')
def mad(b):
    b.sh(48, 64, 30, 2.4)
    draw_boom(b, Ray(12, 46, 74, 0))
    b.r(6, 40, 8, 12, 'metal3', MS, rx=1, sw=.9)
    b.hl('M7.2 41.4 L12 41.4', .7, .6)
    return {}

@platform('dipset')
def dipset(b):
    b.sh(48, 36, 16, 2.2)
    b.r(30, 10, 36, 18, 'metal2', MS, rx=2, sw=1.05)
    b.e(48, 19, 10, 6, 'metal', MS, 1)
    b.c(48, 19, 2.2, 'dkm')
    b.hl('M32 11.6 L64 11.6', .95, .7)
    b.ln('M48 25 L48 58', '#2A323B', 1.6)
    water(b, 54)
    draw_dip(b, Mark(48, 72, 28))
    return {}

@platform('iff')
def iff(b):
    b.sh(48, 84, 18, 2.4)
    b.r(28, 56, 40, 22, 'metal', MS, rx=2, sw=1.1)
    b.r(34, 60, 14, 8, 'canopy', '#1B2D40', rx=1, sw=.6)
    glint(b, 38, 62, 2.2, .7)
    b.hl('M30 57.4 L66 57.4', .9, .7)
    b.r(46, 22, 4, 34, 'metal2', MS, rx=1, sw=.9)
    b.hl('M47.2 24 L47.2 52', .8, .75)
    def chev(x, y):
        b.ln(f'M{x} {y} L{x + 9} {y - 5} L{x} {y - 10}', ARC, 2.3)
        b.ln(f'M{x + 6} {y} L{x + 15} {y - 5} L{x + 6} {y - 10}', ARC2, 2.1)
    chev(62, 34)
    chev(62, 52)
    return {}

@platform('rwr')
def rwr(b):
    b.sh(48, 84, 22, 2.6)
    b.p('M36 72 L46 36 L50 36 L60 72 Z', 'metal2', MS, 1.1)
    b.e(48, 34, 16, 12, 'metal', MS, 1.15)
    b.hl('M36 30 Q48 22 60 30', 1, .7)
    b.c(48, 34, 8, 'dkm', DS, .9)
    b.ln('M48 27 C54 29 54 39 48 41 C42 39 42 29 48 27', ARC2, 1.7)
    b.ln('M48 30 C52 31 52 37 48 38 C44 37 44 31 48 30', '#8FD0FF', 1.15)
    glint(b, 42, 28, 3, 1.2)
    for x1, y1, x2, y2 in ((18, 18, 34, 26), (78, 18, 62, 26), (14, 48, 32, 40), (82, 48, 64, 40)):
        b.ln(f'M{x1} {y1} L{x2} {y2}', REDL, 2.6)
    return {}

@platform('atc')
def atc(b):
    b.sh(48, 88, 18, 2.6)
    b.r(40, 86, 16, 4, 'metal3', MS, rx=.6, sw=.7)
    b.r(44, 40, 8, 46, 'metal2', MS, rx=.8, sw=1)
    b.hl('M45.4 42 L45.4 82', .8, .65)
    b.r(24, 16, 48, 24, 'metal', MS, rx=2, sw=1.1)
    b.r(28, 20, 40, 14, 'canopy', '#1B2D40', rx=1.4, sw=.8)
    glint(b, 36, 23, 8, 1.5)
    b.hl('M26 17.4 L70 17.4', 1, .75)
    b.r(22, 12, 52, 5, 'metal3', MS, rx=1, sw=.8)
    b.ln('M48 12 L48 6', '#5E6A78', 1.4)
    b.c(48, 5.5, 1.5, 'dkm')
    return {}

@platform('hangar')
def hangar(b):
    b.sh(48, 88, 36, 3)
    b.r(10, 42, 76, 40, 'metal2', MS, rx=1, sw=1.1)
    b.p('M10 42 Q48 10 86 42 Z', 'metal', MS, 1.15)
    b.hl('M18 36 Q48 16 78 34', 1.15, .75)
    b.r(16, 50, 30, 32, 'metal3', MS, rx=.8, sw=.9)
    b.r(48, 50, 32, 32, 'dkm', DS, rx=.8, sw=.9)
    b.ln('M46 50 L46 82', '#1E2328', 1.3)
    b.hl('M18 51.2 L44 51.2', .7, .45)
    b.hl('M12 43.2 L84 43.2', .8, .5)
    return {}

@platform('bunker')
def bunker(b):
    b.sh(48, 86, 36, 3)
    b.p('M4 80 L20 56 Q48 44 76 56 L92 80 Z', 'land', LS, 1.15)
    b.p('M14 80 L28 62 Q48 52 68 62 L82 80 Z', 'landdk', LS, 1)
    b.hl('M30 58 Q48 50 66 58', .9, .5)
    b.r(44, 34, 8, 12, 'metal2', MS, rx=1, sw=.8)
    b.e(48, 36, 6, 2.2, 'metal', MS, .7)
    b.c(48, 68, 15, 'metal', MS, 1.15)
    b.c(48, 68, 11, 'dkm', DS, .95)
    b.r(35, 65, 26, 5.5, 'gold', '#6E5418', sw=.85)
    b.c(48, 68, 2.2, 'metal3')
    b.hl('M38 58 A12 12 0 0 1 58 58', 1, .65)
    return {}

def _cube(b, m):
    s = m.s
    w, h = s * .64, s * .56
    dx, dy = s * .26, s * .18
    x = m.x - (w + dx) / 2.0
    y = m.y - (h - dy) / 2.0
    box(b, round(x, 1), round(y, 1), round(w, 1), round(h, 1), round(dx, 1), round(dy, 1), 'white', 'metal', 'whitedk', WS, 1.05)
    b.ln(f'M{x + w * .2:.1f} {y + h * .25:.1f} L{x + w * .62:.1f} {y + h * .62:.1f} L{x + w * .22:.1f} {y + h * .78:.1f}', '#FFFFFF', 1.15, .85)

@role('corner')
def corner(b, slots):
    marks = slots['marks']
    if not isinstance(marks, tuple) or len(marks) < 3:
        raise KeyError('marks')
    for m in marks:
        if not isinstance(m, Mark):
            raise TypeError(type(m).__name__)
        _cube(b, m)

def _buoy(b, m):
    x, y, s = m.x, m.y, m.s
    w = max(3.2, s * .22)
    b.p(
        f'M{x - w:.1f} {y - s * .15:.1f} L{x - w:.1f} {y + s * .32:.1f} '
        f'A{w:.1f} {w * .7:.1f} 0 0 0 {x + w:.1f} {y + s * .32:.1f} L{x + w:.1f} {y - s * .15:.1f} Z',
        'cylM', MS, 1,
    )
    b.e(x, y - s * .15, w, w * .5, 'orange', '#8A4E17', .9)
    b.ln(f'M{x:.1f} {y - s * .15:.1f} L{x:.1f} {y - s * .5:.1f}', '#5E6A78', 1.2)
    b.c(x, y - s * .5, 1.3, REDL)

@role('asw')
def asw(b, slots):
    boom, drop = slots['boom'], slots['drop']
    draw_boom(b, boom)
    if not isinstance(drop, Mark):
        raise TypeError(type(drop).__name__)
    _buoy(b, drop)

@role('eo')
def eo(b, slots):
    ray = slots['ball']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    dia = ray.s * .68
    r = dia / 2.0
    a = math.radians(ray.a)
    ux, uy = math.cos(a), math.sin(a)
    cx, cy = x2 - ux * r, y2 - uy * r
    sx, sy = cx - ux * r, cy - uy * r
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{sx:.1f} {sy:.1f}', '#5E6A78', 2.8)
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{sx:.1f} {sy:.1f}', '#E4EAF0', 1)
    b.c(cx, cy, r, 'sphere', MS, 1.1)
    b.c(cx, cy, r * .55, 'lens', '#05101C', .9)
    glint(b, cx - r * .28, cy - r * .32, max(r * .28, 1.2), max(r * .14, .6))

@role('stores')
def stores(b, slots):
    stubs = slots['stubs']
    if not isinstance(stubs, tuple) or len(stubs) != 2:
        raise KeyError('stubs')
    for m in stubs:
        if not isinstance(m, Mark):
            raise TypeError(type(m).__name__)
        x0 = m.x - m.s / 2.0
        x1 = m.x + m.s / 2.0
        y = m.y
        wing = m.s * .36
        b.p(f'M{x0:.1f} {y - 1.5:.1f} L{x0 + wing:.1f} {y - 6:.1f} L{x0 + wing:.1f} {y + 1:.1f} L{x0:.1f} {y + 2:.1f} Z', 'airdk', AS, .9)
        nose = x1 - 1
        tail = x0 + 4
        b.p(
            f'M{tail:.1f} {y - 3.4:.1f} L{nose - 6:.1f} {y - 3.4:.1f} L{nose:.1f} {y:.1f} '
            f'L{nose - 6:.1f} {y + 3.4:.1f} L{tail:.1f} {y + 3.4:.1f} Z',
            'white', WS, 1,
        )
        b.r(tail + 7, y - 3.4, 3.4, 6.8, 'red')
        b.p(f'M{tail:.1f} {y - 3:.1f} L{tail - 1:.1f} {y - 7:.1f} L{tail + 5:.1f} {y - 3:.1f} Z', 'whitedk', WS, .8)
        b.hl(f'M{tail + 1:.1f} {y - 2.2:.1f} L{nose - 8:.1f} {y - 2.2:.1f}', .9, .7)

def _pod(b, m):
    rx, ry = 5.2, 3.6
    top = m.y - m.s / 2.0
    cyl(b, m.x, top, rx, m.s, ry=ry, fill=JAM, top='#FFD7B0', st='#A85A12', sw=1.05)

@role('jam')
def jam(b, slots):
    pods = slots['pods']
    if not isinstance(pods, tuple) or len(pods) != 2:
        raise KeyError('pods')
    for m in pods:
        if not isinstance(m, Mark):
            raise TypeError(type(m).__name__)
        _pod(b, m)
    a, c = pods
    length = min(a.s, c.s) * .62
    x0 = (a.x + c.x) / 2.0 - length / 2.0
    y = (a.y + c.y) / 2.0
    pts = [f'M{x0:.1f} {y:.1f}']
    steps = 4
    for i in range(steps):
        yy = y + (4.5 if i % 2 == 0 else -4.5)
        pts.append(f'L{x0 + (i + 1) * length / steps:.1f} {yy:.1f}')
    b.ln(' '.join(pts), JAM, 2.6)

@role('relay')
def relay(b, slots):
    masts = slots['masts']
    if not isinstance(masts, tuple) or len(masts) != 3:
        raise KeyError('masts')
    tips = []
    for ray in masts:
        if not isinstance(ray, Ray):
            raise TypeError(type(ray).__name__)
        x2, y2 = ray_end(ray)
        b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{x2:.1f} {y2:.1f}', '#5E6A78', 2.8)
        b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{x2:.1f} {y2:.1f}', '#E4EAF0', 1)
        tips.append((x2, y2))
    trio(b, tips, 4.4)

@role('sling')
def sling(b, slots):
    m = slots['hook']
    if not isinstance(m, Mark):
        raise TypeError(type(m).__name__)
    top = m.y - m.s * .42
    b.ln(f'M{m.x:.1f} {top - 14:.1f} L{m.x:.1f} {top:.1f}', '#2E3640', 1.6)
    b.c(m.x, top - 14, 1.7, 'dkm')
    draw_crate(b, m)

@role('bands')
def bands(b, slots):
    m = slots['skin']
    if not isinstance(m, Mark):
        raise TypeError(type(m).__name__)
    rx = m.s * .42
    ry = max(6.5, m.s * .16)
    for i, col in enumerate((JAM, '#FFFFFF', JAM)):
        b.e(m.x, m.y, max(8, rx - i * 3.4), max(4.5, ry - i * 1.6), 'none', col, 2.6)
    cx = m.x + m.s * .28
    b.c(cx, m.y, 5.2, 'none', JAM, 1.8)
    b.c(cx, m.y, 2.1, JAM)

def _mine(b, m):
    r = m.s / 2.0
    b.c(m.x, m.y, r, 'sphere', MS, 1.05)
    b.c(m.x, m.y, r * .28, 'dkm')
    for k in range(6):
        ang = math.radians(k * 60 - 12)
        x1 = m.x + math.cos(ang) * r * .72
        y1 = m.y + math.sin(ang) * r * .72
        x2 = m.x + math.cos(ang) * r * 1.18
        y2 = m.y + math.sin(ang) * r * 1.18
        b.ln(f'M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}', '#5E6A78', 1.7)
        b.c(x2, y2, 1.15, 'metal3')
    glint(b, m.x - r * .28, m.y - r * .32, r * .28, r * .14)

@role('mines')
def mines(b, slots):
    stern = slots['stern']
    if not isinstance(stern, tuple) or len(stern) != 2:
        raise KeyError('stern')
    for m in stern:
        if not isinstance(m, Mark):
            raise TypeError(type(m).__name__)
        _mine(b, m)

@role('torp')
def torp(b, slots):
    ray = slots['shot']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    x0, y = ray.x, ray.y
    b.p(f'M{x0:.1f} {y - 4:.1f} L{x2 - 8:.1f} {y - 4:.1f} L{x2:.1f} {y:.1f} L{x2 - 8:.1f} {y + 4:.1f} L{x0:.1f} {y + 4:.1f} Z', 'metal', MS, 1)
    b.r(x0 + 8, y - 4, 4, 8, 'red')
    b.p(f'M{x0:.1f} {y - 4:.1f} L{x0 - 4:.1f} {y - 8:.1f} L{x0 + 3:.1f} {y - 4:.1f} Z', 'metal3', MS, .8)
    b.p(f'M{x0:.1f} {y + 4:.1f} L{x0 - 4:.1f} {y + 8:.1f} L{x0 + 3:.1f} {y + 4:.1f} Z', 'metal3', MS, .8)
    b.hl(f'M{x0 + 2:.1f} {y - 2.6:.1f} L{x2 - 10:.1f} {y - 2.6:.1f}', 1, .7)

def _waves(b, x, y, r):
    for i, col in enumerate((ARC, ARC2, '#BFE3FF')):
        rad = 14 + i * 4
        x0 = x - r - 2 - i * 4.2
        span = 8 + i * 3.4
        b.ln(
            f'M{x0:.1f} {y - span:.1f} A{rad:.1f} {rad:.1f} 0 0 0 {x0:.1f} {y + span:.1f}',
            col, 1.7, .9 - i * .15,
        )

@role('jam_acoustic')
def jam_acoustic(b, slots):
    m = slots['nose']
    if not isinstance(m, Mark):
        raise TypeError(type(m).__name__)
    r = m.s / 2.0
    b.c(m.x, m.y, r, 'orange', '#8A4E17', 1.1)
    b.c(m.x, m.y, r * .42, JAM)
    glint(b, m.x - r * .28, m.y - r * .32, r * .3, r * .14)
    _waves(b, m.x + r * .2, m.y, r * .55)

@role('relay_buoy')
def relay_buoy(b, slots):
    ray = slots['buoy']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    by = 34
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{x2:.1f} {by - 4:.1f}', '#5E6A78', 1.5)
    b.ln(f'M{x2:.1f} {by - 5:.1f} L{x2:.1f} {y2 + 4.4:.1f}', '#5E6A78', 1.3)
    b.e(x2, by, 9, 5.2, 'orange', '#8A4E17', 1)
    b.e(x2, by - 1.8, 4.6, 1.6, '#FFFFFF', op=.55)
    b.c(x2, y2, 4.6, 'node', '#1F4F8C', 1)
    glint(b, x2 - 1.5, y2 - 1.6, 1.5, .7)
    b.ln(f'M{x2 - 12:.1f} {by + 4.2:.1f} Q{x2:.1f} {by + 1.4:.1f} {x2 + 12:.1f} {by + 4.2:.1f}', '#FFFFFF', 1, .65)

@role('crate')
def crate(b, slots):
    m = slots['crate']
    draw_crate(b, m)

@role('acoustic')
def acoustic(b, slots):
    ray = slots['tow']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    r = 13
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{x2 + r * .4:.1f} {y2:.1f}', '#5E6A78', 1.5)
    b.c(x2, y2, r, 'sphere', MS, 1.1)
    b.c(x2, y2, r * .38, 'glass', BL, .8)
    b.c(x2, y2, r * .72, 'none', ARC, 1.4)
    b.c(x2, y2, r, 'none', ARC2, 1.15, op=.8)
    glint(b, x2 - 4, y2 - 4, 3, 1.3)

@role('dip')
def dip(b, slots):
    ray = slots['cable']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    b.ln(f'M{ray.x:.1f} {ray.y:.1f} L{x2:.1f} {y2:.1f}', '#2A323B', 1.6)
    draw_dip(b, Mark(x2, y2, 18))

@role('dome')
def dome(b, slots):
    m = slots['masttop']
    if not isinstance(m, Mark):
        raise TypeError(type(m).__name__)
    r = m.s / 2.0
    b.ln(f'M{m.x - 4:.1f} {m.y + 4:.1f} L{m.x - 4:.1f} {m.y + 16:.1f}', '#5F6D7E', 1.8)
    b.ln(f'M{m.x + 4:.1f} {m.y + 4:.1f} L{m.x + 4:.1f} {m.y + 16:.1f}', '#5F6D7E', 1.8)
    b.e(m.x, m.y, r, r * .32, 'air', AS, 1.15)
    b.e(m.x, m.y, r * .62, r * .16, 'none', '#7C8A9B', .9)
    b.p(f'M{m.x - r:.1f} {m.y:.1f} L{m.x + r:.1f} {m.y:.1f} L{m.x + r * .72:.1f} {m.y + r * .18:.1f} L{m.x - r * .72:.1f} {m.y + r * .18:.1f} Z', '#4A5868', op=.4)
    b.hl(f'M{m.x - r * .55:.1f} {m.y - r * .1:.1f} A{r * .6:.1f} {r * .18:.1f} 0 0 1 {m.x + r * .15:.1f} {m.y - r * .18:.1f}', 1.15, .8)

@role('scope')
def scope(b, slots):
    ray = slots['nadir']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    cyl(b, ray.x, ray.y, 5, ray.s, ry=3.2, fill='cylM', top='metal', st=MS, sw=1.05)
    b.e(ray.x, y2, 4, 2.2, 'lens', '#05101C', .9)
    glint(b, ray.x - 1.5, ray.y + 8, 1, 2.2)

@role('dish')
def dish(b, slots):
    ray = slots['zenith']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    cx, cy, s = ray.x, ray.y, ray.s
    h = s
    w = s * .42
    b.p(
        f'M{cx:.1f} {cy - h / 2:.1f} Q{cx - w:.1f} {cy:.1f} {cx:.1f} {cy + h / 2:.1f} '
        f'L{cx + w * .35:.1f} {cy + h * .16:.1f} L{cx + w * .35:.1f} {cy - h * .16:.1f} Z',
        'metal', MS, 1.1,
    )
    b.hl(f'M{cx - w * .15:.1f} {cy - h * .32:.1f} Q{cx - w * .55:.1f} {cy:.1f} {cx - w * .15:.1f} {cy + h * .28:.1f}', 1.05, .75)
    b.ln(f'M{cx - w * .2:.1f} {cy:.1f} L{cx + w * .55:.1f} {cy:.1f}', '#5E6A78', 1.4)
    b.c(cx + w * .5, cy, 2.4, 'dkm')
    b.e(cx + w * .15, cy, 1.6, h * .12, 'metal3', MS, .6)

@role('navclock')
def navclock(b, slots):
    ray = slots['nadir']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    cx, cy, r = ray.x, ray.y + 16, 12
    clock(b, cx, cy, r)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        x1 = cx + math.cos(a) * (r + 1.2)
        y1 = cy + math.sin(a) * (r + 1.2)
        x2 = cx + math.cos(a) * (r + 8)
        y2 = cy + math.sin(a) * (r + 8)
        b.ln(f'M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}', ARC2, 1.7)
        b.c(x2, y2, 1.5, 'node')

@role('limb')
def limb(b, slots):
    ray = slots['look']
    if not isinstance(ray, Ray):
        raise TypeError(type(ray).__name__)
    x2, y2 = ray_end(ray)
    a = math.radians(ray.a)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    w = 30
    x, y = ray.x, ray.y
    b.p(
        f'M{x - px * w * .5:.1f} {y - py * w * .5:.1f} L{x + px * w * .5:.1f} {y + py * w * .5:.1f} '
        f'L{x + ux * 14 + px * w * .22:.1f} {y + uy * 14 + py * w * .22:.1f} '
        f'L{x + ux * 14 - px * w * .22:.1f} {y + uy * 14 - py * w * .22:.1f} Z',
        'metal', MS, 1.1,
    )
    b.hl(f'M{x - px * w * .3:.1f} {y - py * w * .3:.1f} L{x + ux * 8 - px * w * .08:.1f} {y + uy * 8 - py * w * .08:.1f}', 1, .7)
    cx, cy, pr = 80, 32, 14
    b.c(cx, cy, pr, 'glass', BL, 1.1)
    b.p(f'M{cx:.1f} {cy - pr:.1f} A{pr} {pr} 0 0 1 {cx:.1f} {cy + pr:.1f} Z', '#1E3550', op=.35)
    b.hl(f'M{cx - pr + 2:.1f} {cy - 10:.1f} A12 12 0 0 0 {cx - pr + 2:.1f} {cy + 10:.1f}', 2.4, .92)
    glint(b, cx - 6, cy - 5, 3.2, 1.6)

@role('sea_skim')
def sea_skim(b, slots):
    water(b, 74)
    nose, mid = slots['nose'], slots['mid']
    b.p(
        f'M{nose.x - 16:.1f} {nose.y + 6:.1f} L{nose.x - 4:.1f} {nose.y + 6:.1f} '
        f'L{nose.x - 6:.1f} {nose.y + 12:.1f} L{nose.x - 18:.1f} {nose.y + 11:.1f} Z',
        'dkm', DS, .9,
    )
    x, y, s = mid.x, mid.y, mid.s
    b.p(
        f'M{x - 4:.1f} {y + 4:.1f} L{x + s * .7:.1f} {y + 8:.1f} '
        f'L{x + s * .45:.1f} {y + 16:.1f} L{x:.1f} {y + 12:.1f} Z',
        'whitedk', WS, 1.05,
    )
    b.hl(f'M{x:.1f} {y + 6:.1f} L{x + s * .4:.1f} {y + 10:.1f}', 1, .7)

@role('dart')
def dart(b, slots):
    nose, tail = slots['nose'], slots['tail']
    b.p(f'M{nose.x - 10:.1f} {nose.y - 2.2:.1f} L{nose.x + 16:.1f} {nose.y:.1f} L{nose.x - 10:.1f} {nose.y + 2.2:.1f} Z', 'white', WS, .9)
    x, y, s = tail.x, tail.y, tail.s
    h = s / 2.0
    b.p(f'M{x:.1f} {y:.1f} L{x - 10:.1f} {y - h:.1f} L{x - 2:.1f} {y - h + 4:.1f} Z', 'whitedk', WS, .95)
    b.p(f'M{x:.1f} {y:.1f} L{x - 10:.1f} {y + h:.1f} L{x - 2:.1f} {y + h - 4:.1f} Z', 'whitedk', WS, .95)
    b.p(f'M{x:.1f} {y:.1f} L{x + 7:.1f} {y - h * .72:.1f} L{x + 2:.1f} {y - h * .72 + 4:.1f} Z', 'white', WS, .9)
    b.p(f'M{x:.1f} {y:.1f} L{x + 7:.1f} {y + h * .72:.1f} L{x + 2:.1f} {y + h * .72 - 4:.1f} Z', 'white', WS, .9)

@role('spiral')
def spiral(b, slots):
    m = slots['nose']
    if not isinstance(m, Mark):
        raise TypeError(type(m).__name__)
    r = m.s / 2.0
    b.c(m.x, m.y, r, 'white', WS, 1.1)
    b.c(m.x + r * .12, m.y, r * .42, 'lens', '#05101C', .85)
    b.ln(
        f'M{m.x - r * .15:.1f} {m.y - r * .72:.1f} C{m.x + r * .55:.1f} {m.y - r * .2:.1f} '
        f'{m.x - r * .55:.1f} {m.y + r * .15:.1f} {m.x + r * .1:.1f} {m.y + r * .7:.1f}',
        '#5E6A78', 1.7,
    )
    b.p(f'M{m.x - r:.1f} {m.y - 2:.1f} L{m.x - r - 6:.1f} {m.y - 8:.1f} L{m.x - r + 2:.1f} {m.y + 1:.1f} Z', 'whitedk', WS, .8)
    b.p(f'M{m.x - r:.1f} {m.y + 2:.1f} L{m.x - r - 6:.1f} {m.y + 8:.1f} L{m.x - r + 2:.1f} {m.y - 1:.1f} Z', 'whitedk', WS, .8)
    glint(b, m.x - r * .2, m.y - r * .35, r * .22, r * .1)

CATALOG = (
    Row('uav_decoy', '诱饵无人机', '无人', 'fw', 'corner'),
    Row('uav_asw', '反潜无人机', '无人', 'fw', 'asw'),
    Row('ruav_recon', '侦察无人直升机', '无人', 'ruav', 'eo'),
    Row('ruav_strike', '打击无人直升机', '无人', 'ruav', 'stores'),
    Row('ruav_ew', '电子战无人直升机', '无人', 'ruav', 'jam'),
    Row('ruav_relay', '中继无人直升机', '无人', 'ruav', 'relay'),
    Row('ruav_cargo', '运输无人直升机', '无人', 'ruav', 'sling'),
    Row('ruav_decoy', '诱饵无人直升机', '无人', 'ruav', 'corner'),
    Row('ruav_target', '靶标无人直升机', '无人', 'ruav', 'bands'),
    Row('loiter_recon', '侦察巡飞弹', '无人', 'loiter', 'eo'),
    Row('loiter_ew', '干扰巡飞弹', '无人', 'loiter', 'jam'),
    Row('loiter_relay', '中继巡飞弹', '无人', 'loiter', 'relay'),
    Row('loiter_decoy', '诱饵巡飞弹', '无人', 'loiter', 'corner'),
    Row('usv_recon', '侦察无人艇', '无人', 'usv', 'eo'),
    Row('usv_ew', '干扰无人艇', '无人', 'usv', 'jam'),
    Row('usv_relay', '中继无人艇', '无人', 'usv', 'relay'),
    Row('usv_cargo', '运输无人艇', '无人', 'usv', 'crate'),
    Row('usv_decoy', '诱饵无人艇', '无人', 'usv', 'corner'),
    Row('usv_target', '靶标无人艇', '无人', 'usv', 'bands'),
    Row('usv_minelayer', '布雷无人艇', '无人', 'usv', 'mines'),
    Row('uuv_strike', '打击无人潜航器', '无人', 'uuv', 'torp'),
    Row('uuv_ew', '水声干扰潜航器', '无人', 'uuv', 'jam_acoustic'),
    Row('uuv_relay', '水下中继潜航器', '无人', 'uuv', 'relay_buoy'),
    Row('uuv_cargo', '运输无人潜航器', '无人', 'uuv', 'crate'),
    Row('uuv_decoy', '声学诱饵潜航器', '无人', 'uuv', 'acoustic'),
    Row('uuv_target', '靶标潜航器', '无人', 'uuv', 'bands'),
    Row('ugv_ew', '干扰无人车', '无人', 'ugv', 'jam'),
    Row('ugv_relay', '中继无人车', '无人', 'ugv', 'relay'),
    Row('ugv_decoy', '诱饵无人车', '无人', 'ugv', 'corner'),
    Row('ugv_target', '靶标无人车', '无人', 'ugv', 'bands'),
    Row('asw_patrol', '反潜巡逻机', '空中', 'patrol', 'asw'),
    Row('carrier_fighter', '舰载战斗机', '空中', 'fold', None),
    Row('attack_aircraft', '强击机', '空中', 'attack', None),
    Row('asw_heli', '反潜直升机', '空中', 'heli', 'dip'),
    Row('aew_heli', '预警直升机', '空中', 'heli', 'dome'),
    Row('elint_aircraft', '电子侦察机', '空中', 'elint_air', None),
    Row('ssbn', '战略导弹潜艇', '海上', 'ssbn', None),
    Row('elint_ship', '电子侦察船', '海上', 'elint_ship', None),
    Row('lsd', '船坞登陆舰', '海上', 'lsd', None),
    Row('depth_charge_rl', '火箭深弹', '海上', 'depth_rl', None),
    Row('vls', '垂发装置', '陆地', 'vls', None),
    Row('aaa_gun', '高射炮', '陆地', 'aaa', None),
    Row('atgm_vehicle', '反坦克导弹车', '陆地', 'atgm', None),
    Row('coastal_battery', '岸舰导弹', '陆地', 'coastal', None),
    Row('mad_sensor', '磁探仪', '感知通信', 'mad', None),
    Row('dipping_sonar', '吊放声呐', '感知通信', 'dipset', None),
    Row('iff_transponder', '敌我识别', '感知通信', 'iff', None),
    Row('rwr', '雷达告警', '感知通信', 'rwr', None),
    Row('sat_recon', '侦察卫星', '感知通信', 'sat', 'scope'),
    Row('sat_relay', '通信中继卫星', '感知通信', 'sat', 'dish'),
    Row('sat_nav', '导航卫星', '感知通信', 'sat', 'navclock'),
    Row('sat_ewarn', '导弹预警卫星', '感知通信', 'sat', 'limb'),
    Row('ashm', '反舰导弹', '空中', 'msl', 'sea_skim'),
    Row('aam', '空空导弹', '空中', 'msl', 'dart'),
    Row('arm', '反辐射导弹', '空中', 'msl', 'spiral'),
    Row('atc_tower', '塔台', '设施', 'atc', None),
    Row('hangar', '机库', '设施', 'hangar', None),
    Row('ammo_bunker', '弹药库', '设施', 'bunker', None),
)

CATS = ('空中', '海上', '陆地', '设施', '人员', '感知通信', '指控信息', '反无人', '无人', '信息技术')

def main():
    import os, re as _re
    import xml.etree.ElementTree as ET
    from pathlib import Path

    assert len(CATALOG) == 58
    keys = [r.key for r in CATALOG]
    names = [r.name for r in CATALOG]
    assert len(keys) == len(set(keys))
    assert len(names) == len(set(names))
    pairs = [(r.platform, r.role) for r in CATALOG]
    assert len(pairs) == len(set(pairs))
    for r in CATALOG:
        assert r.platform in PLATFORMS, r
        assert r.role is None or r.role in ROLES, r
        assert r.cat in CATS, r
        whole = not PLATFORM_KEYS[r.platform]
        assert (r.role is None) is whole, r
        if r.role is not None:
            assert r.platform in BODY, r
    assert set(PLATFORMS) == set(PLATFORM_KEYS)
    assert set(ROLES) == set(ROLE_KEYS)
    for pid, box in BODY.items():
        assert box[2] <= 60 and box[3] <= 52, (pid, box)

    app = Path(__file__).resolve().parents[2] / 'app'
    out = app / 'icons_m.js'
    seen_keys, seen_names = set(), set()
    files = [app / 'icons.js'] + sorted(app.glob('icons_*.js'))
    for f in files:
        if f.name == 'icons_m.js':
            continue
        text = f.read_text(encoding='utf-8')
        seen_keys.update(_re.findall(r"key: '([^']+)'", text))
        seen_names.update(_re.findall(r"name: '([^']+)'", text))
    clash_k = seen_keys & set(keys)
    clash_n = seen_names & set(names)
    assert not clash_k, clash_k
    assert not clash_n, clash_n

    forbid = ('<text', '<image', 'href', '<style', 'class=', 'filter')
    lines = ['ICON_LIB.push(...[']
    for row in CATALOG:
        k, n, c = row.key, row.name, row.cat
        b = B(k)
        draw(row, b)
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
        if len(s.encode('utf-8')) > 4500:
            print('over', k, len(s.encode('utf-8')))
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

if __name__ == '__main__':
    main()
