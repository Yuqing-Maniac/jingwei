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


# ======================================================================
# icons_gen_a.py — extension set A (空中/海上/陆地 additions + 设施)
# Helpers above are copied verbatim from icons_gen.py (lines 1-192 and
# _truck_base) so this file runs standalone without regenerating icons.js.
# ======================================================================

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

# ---- extra palette for this set ----
GR.update({
    'airblk': L(D, (0, '#A9B5C2'), (.5, '#6B7785'), (1, '#3E4752')),
    'yellow': L(V, (0, '#FCE892'), (.5, '#F2C232'), (1, '#B88A10')),
    'cylY': L(H, (0, '#D9A81E'), (.3, '#FCE892'), (.7, '#F0C030'), (1, '#A97E0E')),
    'cylT': L(H, (0, '#3A424B'), (.3, '#7E8892'), (.7, '#4A535D'), (1, '#1E2328')),
    'cylO': L(H, (0, '#B8691F'), (.3, '#F6C27C'), (.7, '#E59A45'), (1, '#9A5414')),
    'heat': ('r', None, ((0, '#FFF6D8'), (.35, '#FFC25A', .9), (1, '#F0581C', 0))),
    'flame': ('r', ('0.5', '0.25', '0.75'), ((0, '#FFFFFF'), (.3, '#FFE59A'), (.7, '#F49A2C', .9), (1, '#E0461C', 0))),
    'smoke': ('r', ('0.4', '0.35', '0.65'), ((0, '#FFFFFF', .9), (.7, '#D5DCE4', .7), (1, '#AEB8C4', 0))),
    'spark': ('r', None, ((0, '#FFFFFF'), (.3, '#FFD0C8'), (1, '#FF4A3A', 0))),
    'mineS': ('r', ('0.35', '0.3', '0.75'), ((0, '#9AA3AC'), (.5, '#46505A'), (1, '#1A2026'))),
    'tree': ('r', ('0.35', '0.3', '0.75'), ((0, '#C8DE96'), (.55, '#6F9447'), (1, '#3C5A25'))),
    # facilities
    'conc': L(V, (0, '#E4E7EB'), (1, '#8C96A2')),
    'concT': L(D, (0, '#F7F8FA'), (1, '#C3CAD2')),
    'concS': L(V, (0, '#B3BBC5'), (1, '#737E8B')),
    'roof': L(D, (0, '#B4C4D6'), (.5, '#7F96AF'), (1, '#55708E')),
    'roofS': L(V, (0, '#7C92AA'), (1, '#46596E')),
    'grass': L(D, (0, '#C9DBA2'), (.5, '#A2BC76'), (1, '#7A9752')),
    'soil': L(V, (0, '#9C8A68'), (1, '#5E5038')),
    'tarmac': L(D, (0, '#717A86'), (1, '#3A414B')),
    'sand': L(D, (0, '#F6E8C0'), (.6, '#DCC08A'), (1, '#B8975C')),
    'crate': L(V, (0, '#D9B57A'), (1, '#94703C')),
    'contR': L(V, (0, '#D9614F'), (1, '#8E2E22')),
    'contB': L(V, (0, '#6E9BD0'), (1, '#2D5486')),
    'contG': L(V, (0, '#8FB59A'), (1, '#45705A')),
})
CS = '#6B7581'   # concrete outline
RF = '#3F5268'   # roof outline
LASER = '#FF4A3A'
WAVE = '#E08A2E'

R = .58
def poly(b, pts, fill, st=None, sw=1, op=None):
    b.p('M' + ' L'.join(f"{x:.1f} {y:.1f}" for x, y in pts) + ' Z', fill, st, sw, op)

def box(b, x, y, w, h, d, ft='conc', tp='concT', sd='concS', st=CS, sw=1, hl=True):
    """(x,y) = front-left-bottom corner; depth d along (1,-R)."""
    dx, dy = d, d * R
    poly(b, [(x, y - h), (x + dx, y - h - dy), (x + w + dx, y - h - dy), (x + w, y - h)], tp, st, sw)
    poly(b, [(x + w, y - h), (x + w + dx, y - h - dy), (x + w + dx, y - dy), (x + w, y)], sd, st, sw)
    b.r(x, y - h, w, h, ft, st, sw=sw)
    if hl: b.hl(f"M{x+.8:.1f} {y-h+.9:.1f} L{x+w-.6:.1f} {y-h+.9:.1f}", .8, .75)

def gable_v(b, x, y, w, h, d, rise, ft='conc', st=CS):
    """ridge runs in depth; gable faces viewer"""
    dx, dy = d, d * R
    poly(b, [(x, y - h), (x + w / 2, y - h - rise), (x + w / 2 + dx, y - h - rise - dy), (x + dx, y - h - dy)], 'roof', RF)
    poly(b, [(x + w, y - h), (x + w + dx, y - h - dy), (x + w + dx, y - dy), (x + w, y)], 'concS', st)
    poly(b, [(x + w / 2, y - h - rise), (x + w / 2 + dx, y - h - rise - dy), (x + w + dx, y - h - dy), (x + w, y - h)], 'roofS', RF)
    poly(b, [(x, y), (x, y - h), (x + w / 2, y - h - rise), (x + w, y - h), (x + w, y)], ft, st)
    b.hl(f"M{x+.6:.1f} {y-h-.4:.1f} L{x+w/2:.1f} {y-h-rise+.6:.1f}", .9, .8)

def gable_u(b, x, y, w, h, d, rise, ft='conc', st=CS):
    """ridge runs along width; long side faces viewer"""
    dx, dy = d, d * R
    rx_, ry_ = x + dx / 2, y - h - dy / 2 - rise
    poly(b, [(x + w, y), (x + w, y - h), (rx_ + w, ry_), (x + w + dx, y - h - dy), (x + w + dx, y - dy)], 'concS', st)
    poly(b, [(x, y - h), (x + w, y - h), (rx_ + w, ry_), (rx_, ry_)], 'roof', RF)
    b.r(x, y - h, w, h, ft, st, sw=1)
    b.hl(f"M{rx_+.8:.1f} {ry_+.8:.1f} L{rx_+w-.8:.1f} {ry_+.8:.1f}", .9, .8)

def plate(b, x0, y0, w, d, top='grass', t=4, edge='soil', shadow=True):
    dx, dy = d, d * R
    if shadow: b.e(x0 + w / 2 + dx / 2 + 2, y0 + t + 1.5 - dy * .15, (w + dx) / 2 + 2, 3.6, 'shadow')
    poly(b, [(x0 + w, y0), (x0 + w + dx, y0 - dy), (x0 + w + dx, y0 - dy + t), (x0 + w, y0 + t)], edge, '#4A3F2C' if edge == 'soil' else CS, .9)
    b.r(x0, y0, w, t, edge, '#4A3F2C' if edge == 'soil' else CS, sw=.9)
    poly(b, [(x0, y0), (x0 + dx, y0 - dy), (x0 + w + dx, y0 - dy), (x0 + w, y0)], top, '#5E7440' if top == 'grass' else CS, 1)
    b.hl(f"M{x0+1:.1f} {y0-.6:.1f} L{x0+dx-.4:.1f} {y0-dy+.4:.1f} L{x0+w+dx-1:.1f} {y0-dy+.4:.1f}", .9, .7)

def wins(b, pts, w, h, fill='glass', st='#25578F', sw=.45):
    b.p(''.join(f"M{x:.1f} {y:.1f}h{w}v{h}h-{w}Z" for x, y in pts), fill, st, sw)

def PP(x0, y0):
    return lambda u, v: (x0 + u + v, y0 - v * R)

def tree(b, x, y, r=4.5):
    b.e(x + 1.2, y + .6, r * .9, r * .35, 'shadow')
    b.ln(f"M{x} {y} L{x} {y-r*.8:.1f}", '#5A4630', 1.4)
    b.c(x, round(y - r * 1.3, 1), r, 'tree', '#2F4A1C', .8)
    b.e(round(x - r * .35, 1), round(y - r * 1.65, 1), round(r * .4, 1), round(r * .25, 1), '#FFFFFF', op=.35)

def vcyl(b, cx, yb, r, h, fill='cylW', top='concT', st=CS):
    k = r * .36
    b.p(f"M{cx-r} {yb-h} L{cx-r} {yb} A{r} {k:.1f} 0 0 0 {cx+r} {yb} L{cx+r} {yb-h} Z", fill, st, 1)
    b.e(cx, yb - h, r, round(k, 1), top, st, 1)

def flag(b, x, y, h=20):
    b.ln(f"M{x} {y} L{x} {y-h}", '#5E6A78', 1.3)
    b.p(f"M{x+.5} {y-h} Q{x+5} {y-h-1.6} {x+8.5} {y-h+.6} Q{x+11} {y-h+2} {x+13} {y-h+1} L{x+13} {y-h+8} Q{x+11} {y-h+9} {x+8.5} {y-h+7.6} Q{x+5} {y-h+5.4} {x+.5} {y-h+7} Z", 'red', '#7A2219', .7)

def wav(b, cx, cy, rs, a0, a1, col, w=1.6, op=.85):
    """concentric arcs centred (cx,cy), angles in degrees (0 = right, clockwise positive y)"""
    for i, r in enumerate(rs):
        x1, y1 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x2, y2 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        b.ln(f"M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}", col, w, round(op * (1 - i * .22), 2))

# ================= 空中 =================
@icon('tanker', '空中加油机', '空中')
def _(b):
    fus = "M48 4 C51.5 4 53 8 53 14 L53 64 C53 69 50.5 73 48 75 C45.5 73 43 69 43 64 L43 14 C43 8 44.5 4 48 4 Z"
    wing = "M43 27 L6 47 L6 52 L43 40 L53 40 L90 52 L90 47 L53 27 Z"
    tail = "M48 60 L65 68 L65 72 L48 69 L31 72 L31 68 Z"
    for d in (wing, fus, tail): b.drop(d)
    # hoses + drogues
    for x in (11, 85):
        b.ln(f"M{x} 51 Q{x+(2 if x < 48 else -2)} 62 {x} 72", '#3A4552', 1.2)
        b.p(f"M{x-1.6} 71 L{x+1.6} 71 L{x+4} 77 L{x-4} 77 Z", 'whitedk', WS, .8)
        b.e(x, 77, 4, 1.2, 'red', '#7A2219', .6)
    b.ln("M48 72 L48 90", '#5F6D7E', 2.8); b.ln("M47.4 73 L47.4 89", '#E8EDF2', .8)
    b.p("M43.5 83 L48 79.5 L52.5 83 L52 84.5 L48 82 L44 84.5 Z", '#6E7C8C')
    b.r(46.6, 89, 2.8, 3, '#2B3138', rx=.8)
    b.p(fus, 'air', AS)
    b.p(tail, 'airdk', AS)
    for x, cy in ((20, 39.5), (31.5, 33.3), (64.5, 33.3), (76, 39.5)):
        b.e(x, cy, 2.7, 6.2, 'airdk', AS, 1); b.e(x, cy - 4.8, 1.9, 1, '#3A4552')
    b.p(wing, 'air', AS)
    for x in (8.5, 87.5): b.r(x - 2, 46, 4, 7, 'white', WS, rx=2, sw=.8)
    b.p("M44.6 9.5 L51.4 9.5 L50.8 12.6 L45.2 12.6 Z", 'canopy', '#1B2D40', .6)
    b.hl("M45 8 C44 12 43.8 18 43.8 28"); b.hl("M7 47.5 L42 28.6", 1, .75)

@icon('ew_aircraft', '电子战飞机', '空中')
def _(b):
    fus = "M48 7 C50.5 11 52 17 52.5 25 L53 70 L55 84 L41 84 L43 70 L43.5 25 C44 17 45.5 11 48 7 Z"
    wing = "M43.5 36 L12 55 L12 61 L43.5 57 L52.5 57 L84 61 L84 55 L52.5 36 Z"
    st = "M43 72 L31 80 L31 85 L43 81 L53 81 L65 85 L65 80 L53 72 Z"
    for d in (wing, st, fus): b.drop(d)
    b.p(st, 'airdk', AS)
    b.p(fus, 'air', AS)
    b.p(wing, 'air', AS)
    b.ln("M44.5 66 L42.5 80 M51.5 66 L53.5 80", '#5F6D7E', 2.2)
    for x in (24, 72):
        b.r(x - 2.6, 42, 5.2, 18, 'white', WS, rx=2.6, sw=.9)
        b.r(x - 2.6, 44, 5.2, 3, '#4A5664', rx=1)
        b.p(f"M{x-1} 60 L{x+1} 60 L{x} 63 Z", '#8F9BA9')
    for x in (10, 86):
        b.r(x - 2.2, 50, 4.4, 14, 'white', WS, rx=2.2, sw=.9)
        b.e(x, 51.5, 2.2, 1.4, '#3A4552')
    b.p("M42.6 32 L40.6 40 L42.8 39.4 Z", '#2B3440'); b.p("M53.4 32 L55.4 40 L53.2 39.4 Z", '#2B3440')
    b.e(48, 22, 3.2, 7, 'canopy', '#1B2D40', .8); glint(b, 47, 18.6, .9, 2)
    b.hl("M46.6 11 C45.4 16 44.8 22 44.8 30"); b.hl("M42 38 L13 55.6", 1, .7)
    b.ln("M62 24 L68 20 L66 28 L74 22 L72 30 L80 24", WAVE, 1.6)
    b.ln("M34 24 L28 20 L30 28 L22 22 L24 30 L16 24", WAVE, 1.6)
    b.ln("M70 13 Q80 16 84 26 M75 7 Q88 11 92 26", WAVE, 1.3, .6)
    b.ln("M26 13 Q16 16 12 26 M21 7 Q8 11 4 26", WAVE, 1.3, .6)

@icon('recon_aircraft', '侦察机', '空中')
def _(b):
    fus = "M48 8 C50.5 8 52 12 52 20 L52 76 C52 81 50 85 48 86 C46 85 44 81 44 76 L44 20 C44 12 45.5 8 48 8 Z"
    wing = "M44 38 L4 43 L4 47.5 L44 49 L52 49 L92 47.5 L92 43 L52 38 Z"
    tail = "M48 74 L63 78 L63 82 L48 81 L33 82 L33 78 Z"
    for d in (wing, fus, tail): b.drop(d)
    b.p(tail, 'airblk', '#1D242C')
    b.p(fus, 'airblk', '#1D242C')
    b.p(wing, 'airblk', '#1D242C')
    for x in (24, 72):
        b.e(x, 42, 2.8, 8, 'airblk', '#1D242C', .9)
    b.r(2.6, 42, 3, 7, '#1D242C', rx=1); b.r(90.4, 42, 3, 7, '#1D242C', rx=1)
    b.p("M43.4 32 L41.6 38 L43.6 38 Z", '#151A20'); b.p("M52.6 32 L54.4 38 L52.4 38 Z", '#151A20')
    b.e(48, 22, 2.8, 5.5, 'canopy', '#0B1622', .8); glint(b, 47.2, 19.6, .8, 1.6)
    b.c(48, 12.5, 1.9, 'lens', '#0B1622', .5)
    b.ln("M44.6 54 L51.4 54 M44.6 60 L51.4 60", '#1D242C', .8, .7)
    b.hl("M46 10.5 C44.8 14 44.6 20 44.6 30", 1, .5); b.hl("M5 43.6 L43 38.8", 1, .45); b.hl("M53 38.8 L91 43.6", .8, .3)

@icon('transport_heli', '运输直升机', '空中')
def _(b):
    b.sh(48, 80, 40, 3.6)
    body = ("M8 52 C8 45 12 40 20 40 L76 40 C82 40 86 44 86 50 L86 58 C86 63 83 66 78 66 L16 66 "
            "C11 66 8 62 8 57 Z")
    b.p("M64 40 L67 24 L80 24 L86 44 L86 46 Z", 'airdk', AS)
    b.p(body, 'airV', AS)
    b.p("M14 41 L28 33 L32 33 L32 40 Z", 'airdk', AS, 1)
    b.p("M9 51 C9 46 12 42.5 17 42 L22 42 L22 50.5 Z", 'canopy', '#1B2D40', .8)
    glint(b, 14.5, 45, 1.6, .7)
    wins(b, [(x, 45) for x in (30, 38, 46, 54, 62)], 4.4, 4, 'canopy', None)
    b.r(67, 30, 15, 6, 'metal3', MS, rx=3, sw=.8); b.e(82, 33, 1.2, 2.4, '#2B3138')
    b.r(30, 58, 36, 7, 'airdk', AS, rx=3.5, sw=1)
    b.ln("M84 52 L86 64", '#5F6D7E', .9)
    b.ln("M20 66 L20 70 M74 66 L74 70", '#3A434E', 1.6)
    wheel(b, 20, 72, 3.6); wheel(b, 74, 72, 3.6)
    for cx, cy in ((25, 30), (72, 21)):
        b.r(cx - 1.6, cy, 3.2, 4 if cx < 48 else 4, '#3A434E')
        b.e(cx, cy, 21, 2.6, 'prop')
        b.r(cx - 21, cy - 1.3, 42, 2.4, '#2E3640', rx=1.2)
        b.ln(f"M{cx-19} {cy-.6} L{cx+19} {cy-.6}", '#8592A2', .6)
        b.e(cx, cy, 4, 2.2, 'hub', '#1D2228', .8)
    b.hl("M12 46 C13.5 43.5 16 42 19 41.4"); b.hl("M24 41.3 L76 41.3", 1, .7); b.hl("M67.6 25.3 L79.4 25.3", .9, .7)

@icon('uav_heli', '无人直升机', '空中')
def _(b):
    b.sh(44, 82, 32, 3.4)
    b.p("M60 42 L88 45 L88 48.4 L60 51 Z", 'airdk', AS, 1)
    b.p("M83 45 L86 32 L91 32 L90 48 Z", 'airdk', AS, 1)
    b.c(84, 40, 5.5, 'prop', '#8D9BAC', .5); b.ln("M84 35 L84 45", '#2E3640', 1.4); b.c(84, 40, 1.4, 'hub')
    body = "M14 46 C14 38 22 34 33 34 L52 34 C61 34 66 40 66 46 C66 53 60 57 51 57 L28 57 C19 57 14 53 14 46 Z"
    b.p(body, 'airV', AS)
    b.p("M30 34 C33 29 38 28 46 28 C51 28 54 30 55 34 Z", 'airdk', AS, 1)
    b.e(48, 31, 2.4, 1.4, '#2B3440')
    b.p("M16 42 C18 38 22 36 28 35.6 L26 40 Z", '#FFFFFF', op=.35)
    b.ln("M27 57 L24 66 M52 57 L55 66", '#3A434E', 1.8)
    b.ln("M14 66.5 L64 66.5 Q67 66.5 68 64", '#3A434E', 2.4); b.ln("M15 66 L63 66", '#8592A2', .6)
    b.ln("M22 57 L22 60", '#3A434E', 1.6)
    b.c(22, 62, 4.6, 'sphere', MS, .9); b.c(20.6, 62.6, 2.4, 'lens', '#05101C', .5); glint(b, 19.9, 61.8, .8, .5)
    b.ln("M58 36 L60 26", '#3A434E', 1); b.c(60, 25.6, 1.2, REDL)
    b.r(38, 19, 4, 10, '#3A434E')
    b.e(40, 19.5, 38, 3, 'prop')
    b.r(2, 17.9, 76, 2.4, '#2E3640', rx=1.2); b.ln("M4 18.6 L76 18.6", '#8592A2', .6)
    b.e(40, 19, 4.4, 2.4, 'hub', '#1D2228', .8)
    leds(b, [(34, 50, GREEN)])
    b.hl("M18 41 C21 37 26 35.6 33 35.4"); b.hl("M62 43.6 L86 46", .8, .6)

@icon('hale_uav', '高空长航时无人机', '空中')
def _(b):
    fus = "M48 6 C53.5 6 55.5 11 55.5 19 L54 32 L52 76 L50.5 84 L45.5 84 L44 76 L42 32 L40.5 19 C40.5 11 42.5 6 48 6 Z"
    wing = "M3 43 L43 38 L53 38 L93 43 L93 46.5 L53 45 L43 45 L3 46.5 Z"
    vt1 = "M46 76 L32 87 L34.5 89.5 L48 82 Z"; vt2 = mirror(vt1)
    for d in (wing, fus, vt1, vt2): b.drop(d)
    b.p(vt1, 'airdk', AS); b.p(vt2, 'airdk', AS)
    b.p(fus, 'air', AS)
    b.p(wing, 'air', AS)
    b.e(48, 64, 4.6, 10, 'airdk', AS, 1)
    b.e(48, 55.6, 3, 1.6, '#2B3440')
    b.r(46, 73, 4, 3, '#3A4048', rx=1)
    b.e(48, 14, 5.4, 6, '#FFFFFF', op=.4)
    b.c(48, 29, 2.2, 'lens', '#1B2D40', .5)
    b.hl("M4 43.8 L42 39"); b.hl("M54 39 L92 43.8", .9, .5); b.hl("M44.2 9.5 C42.6 12 42 15 42.2 20", 1, .8)

@icon('swarm', '无人机蜂群', '空中')
def _(b):
    pts = [(48, 14), (28, 33), (68, 33), (48, 51), (10, 52), (86, 52), (28, 71), (68, 71)]
    lk = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 5), (3, 6), (3, 7), (4, 6), (5, 7), (1, 2)]
    for a, c_ in lk:
        (x1, y1), (x2, y2) = pts[a], pts[c_]
        b.ln(f"M{x1} {y1} L{x2} {y2}", '#3D86D6', 1, .55, extra="stroke-dasharray='2 2.4'")
    d = "M0 -9 C1.6 -9 2.4 -7 2.6 -4 L11 4 L11 6.5 L2.4 4 L2 7 L4.8 9 L4.8 10.4 L0 9.6 L-4.8 10.4 L-4.8 9 L-2 7 L-2.4 4 L-11 6.5 L-11 4 L-2.6 -4 C-2.4 -7 -1.6 -9 0 -9 Z"
    for i, (x, y) in enumerate(pts):
        s = 1.15 if i == 0 else .95
        b.g(f'translate({x} {y}) scale({s})')
        if i == 0: b.drop(d, 1.6, 2.4, .16)
        b.p(d, 'air', AS, 1)
        b.e(0, -4.5, 1.2, 2.2, 'canopy')
        b.ln("M-1.6 -6.6 L-1.8 -2", '#FFFFFF', .8, .7)
        b.eg()
    leds(b, [(48, 23.5, GREEN)])

@icon('target_drone', '靶机', '空中')
def _(b):
    fus = "M48 5 C51.2 8 52.5 14 52.5 20 L52.5 74 L43.5 74 L43.5 20 C43.5 14 44.8 8 48 5 Z"
    wing = "M43.5 38 L12 51 L12 57 L43.5 53 L52.5 53 L84 57 L84 51 L52.5 38 Z"
    tail = "M43.5 66 L30 76 L30 81 L43.5 77 L52.5 77 L66 81 L66 76 L52.5 66 Z"
    for d in (wing, tail, fus): b.drop(d)
    b.p(tail, 'orange', '#8A4E17')
    b.p(fus, 'white', WS)
    b.p("M48 5 C51.2 8 52.5 14 52.5 20 L43.5 20 C43.5 14 44.8 8 48 5 Z", 'orange', '#8A4E17', .9)
    b.p(wing, 'white', WS)
    b.p("M12 51 L19 48.1 L19 56.1 L12 57 Z", 'orange', '#8A4E17', .8); b.p("M84 51 L77 48.1 L77 56.1 L84 57 Z", 'orange', '#8A4E17', .8)
    for x in (30, 66):
        b.c(x, 50.5, 4.2, 'red', '#7A2219', .6); b.c(x, 50.5, 2.6, '#FFFFFF'); b.c(x, 50.5, 1.2, 'red')
    b.r(43.5, 30, 9, 3, 'orange')
    b.r(44.5, 74, 7, 7, 'dkm', DS, rx=1.5, sw=.8); b.e(48, 81, 3, 1.2, '#1E2328')
    b.ln("M48 60 L48 66", '#8F9BA9', .7)
    b.hl("M45.2 21 L45.2 72"); b.hl("M42 39.5 L13 51.6", 1, .75)

@icon('airship', '浮空器', '空中')
def _(b):
    b.sh(32, 88, 18, 2.6)
    b.p("M68 26 L84 9 L90 11 L83 26 Z", 'whitedk', WS)
    b.e(46, 30, 34, 15.5, 'white', WS, 1.3)
    b.p("M68 34 L84 51 L90 49 L83 34 Z", 'whitedk', WS)
    b.p("M74 30 L93 30 L92 34 L76 34 Z", 'whitedk', WS)
    b.p("M16 22 C24 16 40 14 54 15.5 C40 18 26 22 16 30 Z", '#FFFFFF', op=.8)
    b.e(44, 40, 26, 4.6, '#8F9BA9', op=.25)
    b.ln("M14 30 L78 30", '#A3AEBB', .7, .7)
    b.p("M38 45 L52 45 L50 50 L40 50 Z", 'metal3', MS, .8)
    b.c(45, 50.5, 2.4, 'lens', '#05101C', .5)
    b.ln("M30 43 L40 58 M46 45.5 L40 58 M60 42 L40 58", '#5E6A78', .8)
    b.ln("M40 58 Q34 72 32 84", '#3A4048', 1.2)
    b.p("M22 88 L24 82 L40 82 L42 88 Z", 'metal2', MS, .9)
    b.c(32, 82, 3.4, 'hub', '#1D2228', .7)
    b.hl("M16 24 C22 19 30 16 40 15", 1.2, .8)

@icon('hypersonic', '高超声速飞行器', '空中')
def _(b):
    b.sh(50, 84, 34, 3)
    b.g('rotate(-16 50 50)')
    for y, w_, x0 in ((40, 1.2, 4), (56, 1.2, 8), (47, .9, 0), (61, .8, 18)):
        b.ln(f"M{x0} {y} L{x0+16} {y}", '#9CC2EA', w_, .7)
    b.p("M96 48 C82 38 58 33 30 34 L30 62 C58 63 82 58 96 48 Z", '#FFB25A', op=.18)
    b.p("M14 40 L7 29 L13 29 L23 38 Z", 'metal2', MS, .9)
    b.p("M93 48 L22 37 L10 41 L10 50 L22 52 Z", 'metal3', '#2E3640')
    b.p("M93 48 L22 52 L10 50 L10 56 L24 60 Z", 'dkm', '#15191E')
    b.p("M14 55 L7 66 L13 66 L23 58 Z", 'dkm2', '#15191E', .9)
    b.r(6, 44, 4, 9, '#2A2E33', rx=1)
    b.ln("M92 48.2 L62 51", '#F28C28', 1.3, .9)
    b.ln("M30 41.5 L84 46.2", '#FFFFFF', .9, .55)
    b.c(91, 48, 6, 'heat')
    b.eg()

@icon('interceptor', '拦截弹', '空中')
def _(b):
    b.g('rotate(32 48 50)')
    for y, r, o in ((96, 7.5, .65), (88, 6, .85)):
        b.c(48, y, r, 'smoke', op=o)
    b.e(48, 82, 5, 10, 'flame')
    b.p("M42 60 L35 72 L35 76 L43 72 Z", 'whitedk', WS); b.p("M54 60 L61 72 L61 76 L53 72 Z", 'whitedk', WS)
    b.p("M43 73 L53 73 L54.5 77 L41.5 77 Z", '#3A4048', DS, .8)
    b.p("M42.5 44 L53.5 44 L53.5 73 L42.5 73 Z", 'cylW', WS)
    b.p("M48 4 C51.5 9 52.5 15 52.5 21 L52.5 44 L43.5 44 L43.5 21 C43.5 15 44.5 9 48 4 Z", 'cylW', WS)
    b.p("M48 4 C50.2 7 51.3 10 51.8 13 L44.2 13 C44.7 10 45.8 7 48 4 Z", 'canopy', '#0F2339', .7)
    glint(b, 47, 8.5, .6, 1.5)
    b.p("M43.5 22 L39 30 L43.5 29 Z", 'whitedk', WS, .8); b.p("M52.5 22 L57 30 L52.5 29 Z", 'whitedk', WS, .8)
    b.r(43.5, 33, 9, 3, 'red'); b.r(42.5, 44, 11, 1.8, '#5E6A78')
    b.hl("M45 16 L45 42 M44.2 47 L44.2 71", 1, .85)
    b.eg()

# ================= 海上 =================
@icon('amphibious', '两栖攻击舰', '海上')
def _(b):
    b.p("M4 47 L92 47 L86 70 L12 70 L5 60 Z", 'sea', SS)
    b.p("M8.5 66 L87 66 L86 70 L12 70 Z", 'boot')
    b.r(5.6, 50, 8, 11, '#2A323B', rx=.6)
    b.ln("M6.4 53 L13 53 M6.4 56 L13 56", '#5D6B7A', .6)
    for x in (24, 40): b.r(x, 51, 10, 5, '#3D4854', rx=.6)
    b.p("M3 43.5 L93 43.5 L92.4 47.4 L3.6 47.4 Z", 'deck', SS, 1)
    b.p("M56 43.5 L57 30 L72 30 L73 43.5 Z", 'sea', SS)
    b.p("M58 33 L71 33 L71.2 35.6 L57.8 35.6 Z", 'canopy')
    b.p("M62.5 30 L63.5 17 L66.5 17 L67.5 30 Z", 'seadk', SS, 1)
    b.ln("M60.5 21 L69.5 21 M61.5 25 L68.5 25", '#4B5867', 1.2)
    b.e(65, 15.6, 3, 1.4, 'metal', SS, .6)
    for x in (16, 36):
        b.ln(f"M{x+6} 41 L{x+12} 40", '#5F6D7E', 1)
        b.e(x + 3, 40, 5, 2.4, 'airV', AS, .7)
        b.ln(f"M{x+3} 37.5 L{x+3} 39", '#3A434E', 1); b.ln(f"M{x-4} 37.2 L{x+10} 37.2", '#2E3640', 1.4)
        b.p(f"M{x-1.2} 39 L{x+1.8} 39 L{x+1.4} 41 L{x-1.4} 41 Z", 'canopy')
    b.ln("M80 43.5 L80 40 M84 43.5 L84 40", '#4B5867', 1)
    b.hl("M4.4 44.7 L92 44.7"); b.hl("M7 48.8 L90.6 48.8", 1, .55); b.hl("M57.4 31.2 L71.4 31.2", .8, .7)
    water(b, 66)

@icon('supply_ship', '综合补给舰', '海上')
def _(b):
    b.p("M4 56 L72 56 L93 50 L86 70 L12 70 L6 63 Z", 'sea', SS)
    b.p("M9 66 L87.6 66 L86 70 L12 70 Z", 'boot')
    b.p("M64 56 L65 40 L78 40 L80 56 Z", 'sea', SS)
    b.p("M65.6 43 L77.6 43 L77.8 45.6 L65.4 45.6 Z", 'canopy')
    b.r(69.5, 28, 3, 12, 'seadk', SS, sw=.8); b.ln("M67 31 L75 31 M68 35 L74 35", '#4B5867', 1.1)
    b.p("M7 56 L8 43 L28 43 L29 56 Z", 'sea', SS)
    b.r(10, 47, 9, 9, '#3D4854', rx=.5)
    b.p("M17 43 L18 34 L25 34 L26 43 Z", 'seadk', SS, 1); b.r(17.6, 33, 7.8, 2, '#2A323B', rx=.6)
    for x in (37, 47, 57):
        b.ln(f"M{x-2.4} 56 L{x-1.4} 24 M{x+2.4} 56 L{x+1.4} 24", '#4B5867', 1.8)
        b.ln(f"M{x-1.8} 54 L{x-1} 26", '#C9D1DA', .6)
        b.r(x - 5, 23, 10, 2.6, 'seadk', SS, rx=.8, sw=.8)
        b.ln(f"M{x-4} 25.6 Q{x-9} 36 {x-7} 46 M{x+4} 25.6 Q{x+9} 36 {x+7} 46", '#2A323B', .8)
        b.e(x, 53.5, 3.4, 2.4, 'metal3', SS, .7)
    b.ln("M30 56 L63 56", '#4B5867', .8)
    b.hl("M6 57.3 L72 57.3 L91 52"); b.hl("M8.6 44.2 L27.4 44.2", .8, .7); b.hl("M65.6 41.2 L77.4 41.2", .8, .7)
    water(b, 66)

@icon('landing_craft', '气垫登陆艇', '海上')
def _(b):
    b.r(0, 66, 96, 22, 'water')
    b.p("M5 58 C5 53 9 50 15 50 L84 50 C90 50 94 53 94 58 C94 64 90 69 84 69 L14 69 C8 69 5 64 5 58 Z", 'dkm2', DS)
    for x in range(14, 86, 6): b.ln(f"M{x} 56 L{x} 68", '#4A525C', .8, .7)
    b.hl("M10 53 L88 53", .9, .35)
    b.r(7, 44, 84, 7, 'sea', SS, rx=1.5)
    b.r(12, 37, 26, 7, 'seadk', SS, rx=1, sw=.9)
    b.ln("M15 40 L35 40", '#4B5867', .8, .7)
    b.p("M66 44 L67 33 L80 33 L82 44 Z", 'sea', SS)
    b.p("M67.6 35.6 L79.6 35.6 L80 38.4 L67.4 38.4 Z", 'canopy')
    b.r(72.5, 25, 2.4, 8, 'seadk', SS, sw=.7); b.ln("M70 27 L77 27", '#4B5867', 1)
    for x in (8, 24):
        b.r(x - 1.5, 20, 2, 18, 'seadk', SS, sw=.7)
        b.r(x, 16, 13, 24, 'sea', SS, rx=4)
        b.r(x + 4.5, 18.5, 4, 19, '#2A323B', rx=1.5)
        b.ln(f"M{x+6.5} 19.5 L{x+6.5} 36.5", '#8C98A6', .6)
        b.hl(f"M{x+1.6} 20 L{x+1.6} 36", .9, .7)
    b.e(4, 68, 6, 2.4, '#FFFFFF', op=.7); b.e(92, 68, 6, 2.4, '#FFFFFF', op=.7)
    b.e(48, 70, 30, 2, '#FFFFFF', op=.45)
    b.ln("M2 74 Q8 72 14 74 T26 74 T38 74 T50 74 T62 74 T74 74 T86 74 T98 74", '#FFFFFF', 1, .55)
    b.ln("M10 80 Q16 78 22 80 T34 80 M58 80 Q64 78 70 80 T82 80", '#FFFFFF', .8, .35)
    b.hl("M9 45.3 L89 45.3"); b.hl("M67.4 34.2 L79.6 34.2", .8, .7)

@icon('minesweeper', '扫雷舰艇', '海上')
def _(b):
    b.ln("M22 60 Q14 66 9 68", '#2A323B', 1)
    b.p("M2 67.5 C2 66 5 65 9 65 C13 65 16 66 16 67.5 C16 69 13 70 9 70 C5 70 2 69 2 67.5 Z", 'orange', '#8A4E17', .8)
    b.ln("M9 65 L9 57", '#3A4048', 1); b.p("M9.4 57 L14 58.4 L9.4 60 Z", 'red')
    b.p("M20 58 L68 58 L92 52 L86 70 L26 70 L22 64 Z", 'sea', SS)
    b.p("M24 66 L87.6 66 L86 70 L26 70 Z", 'boot')
    b.p("M46 58 L47 46 L70 46 L72 58 Z", 'sea', SS)
    b.p("M60 48.6 L69.4 48.6 L69.8 51.4 L60 51.4 Z", 'canopy')
    b.ln("M54 46 L56 25 M60 46 L58 25 M54.8 39 L59.2 39 M55.4 32 L58.6 32", '#56636F', 1.4)
    b.e(57, 24, 6, 1.6, 'metal2', SS, .8)
    b.ln("M24 58 L28 42 M36 58 L32 42 M27 43 L33 43", '#4B5867', 2)
    b.ln("M24.6 57 L28.2 43", '#C9D1DA', .6)
    b.c(39, 54.5, 3.6, 'metal3', SS, .8); b.c(39, 54.5, 1.3, '#2A323B')
    b.ln("M30 43 L30 52", '#2A323B', .8)
    b.e(30, 53.5, 3, 1.6, 'orange', '#8A4E17', .6)
    b.ln("M78 54.6 L88 52.4", '#3D4854', 1.5)
    b.p("M74 57 L75.4 53.6 L80 53.6 L81 56.6 Z", 'seadk', SS, 1)
    b.hl("M22 59.3 L68 59.3 L90 53.7"); b.hl("M48.4 47.2 L69.4 47.2", .9, .75)
    water(b, 66)

def _miniboat(b, x, y, s=1, rot=0):
    b.g(f'translate({x} {y}) rotate({rot}) scale({s})')
    b.p("M0 -1 L12 -1 L17 -3.4 L14.4 3 L2 3 Z", 'sea', SS, .8)
    b.p("M1 1.6 L14.9 1.6 L14.4 3 L2 3 Z", 'orange')
    b.p("M4.4 -1 L5.6 -4.6 L10.4 -4.6 L11.6 -1 Z", 'seadk', SS, .7)
    b.r(9, -4, 2, 1.6, 'canopy')
    b.eg()

@icon('usv_mother', '无人艇母船', '海上')
def _(b):
    b.p("M16 56 L66 56 L92 49 L86 70 L22 70 L18 66 Z", 'sea', SS)
    b.p("M19.5 66 L87.6 66 L86 70 L22 70 Z", 'boot')
    b.p("M16 56 L19.5 66 L22 70 L16 70 L18 66 Z", '#2A323B', SS, .8)
    b.ln("M17 57 L20 66", '#8C98A6', .7, .8)
    b.p("M58 56 L59 38 L76 38 L78 56 Z", 'sea', SS)
    b.p("M60 41 L75.6 41 L75.8 43.6 L59.8 43.6 Z", 'canopy')
    b.r(66.5, 24, 3, 14, 'seadk', SS, sw=.8); b.ln("M63.5 28 L72.5 28", '#4B5867', 1.1)
    b.c(68, 21.5, 3.4, 'sphere', SS, .7)
    b.r(60, 47, 8, 6, '#3D4854', rx=.5)
    b.ln("M56 56 L56 34 L44 38", '#4B5867', 1.8); b.ln("M44 38 L44 45", '#2A323B', .8)
    b.ln("M56.6 55 L56.6 35", '#C9D1DA', .6)
    _miniboat(b, 21, 52.6, 1.15); _miniboat(b, 40, 52.6, 1.0)
    _miniboat(b, 0, 64.4, 1.0)
    b.ln("M0 69 L4 68 M2 70.6 L8 69.6", '#FFFFFF', 1, .6)
    b.hl("M18 57.3 L66 57.3 L90 50.6"); b.hl("M59.6 39.2 L75.6 39.2", .8, .7)
    water(b, 66)

@icon('glider', '水下滑翔机', '海上')
def _(b):
    b.e(50, 50, 46, 26, 'uwater')
    b.ln("M2 24 L26 40 L50 26 L74 42 L94 30", '#FFFFFF', 1, .35, extra="stroke-dasharray='3 3'")
    b.g('rotate(14 48 52)')
    b.p("M56 47 L44 33 L39 33 L48 47 Z", 'dkm', DS, .9)
    b.p("M16 47 L4 49 L4 51 L16 53 Z", 'dkm', DS, .9)
    b.p("M12 47 L5 37 L10 37 L17 47 Z", 'dkm', DS, .9)
    b.ln("M7 37.5 L3 22", '#2A2E33', 1.4); b.c(3, 21.5, 1.2, REDL)
    b.p("M16 45 L76 45 C85 45 91 47 92 50 C91 53 85 55 76 55 L16 55 C13 55 12 53 12 50 C12 47 13 45 16 45 Z", 'yellow', '#8A6A10')
    b.ln("M30 45 L30 55 M64 45 L64 55", '#8A6A10', .8, .8)
    b.r(30, 45, 4, 10, 'dkm', DS, sw=.6)
    b.p("M58 53 L44 67 L39 67 L48 53 Z", 'dkm', DS, .9)
    b.hl("M16 46.6 L76 46.6 C83 46.8 88 48 90.5 49.4")
    b.eg()
    for x, y, r in ((6, 66, 1.4), (10, 74, 1), (14, 70, .8), (80, 22, 1.1), (86, 28, .8)):
        b.c(x, y, r, 'none', '#FFFFFF', .7, op=.7)

@icon('torpedo', '鱼雷', '海上')
def _(b):
    b.e(52, 50, 44, 20, 'uwater')
    b.ln("M3 40 L16 40 M2 58 L12 58", '#FFFFFF', 1, .5)
    for x, y, r in ((4, 47, 1.6), (1, 52, 1.2), (8, 53, 1), (2, 44, .8)):
        b.c(x, y, r, 'none', '#FFFFFF', .7, op=.75)
    b.p("M20 42 L15 34 L19 34 L27 42 Z", 'seadk', SS, 1)
    b.p("M20 54 L15 62 L19 62 L27 54 Z", 'seadk', SS, 1)
    b.e(10.6, 48, 1.8, 7.5, 'prop'); b.ln("M10.6 41 L10.6 55", '#2E3640', 1.6)
    b.e(14, 48, 1.8, 6.5, 'prop'); b.ln("M14 42 L14 54", '#2E3640', 1.6)
    b.p("M24 42 L78 42 C87 42 93 45 93 48 C93 51 87 54 78 54 L24 54 L16 51 L16 45 Z", 'subm', '#11161B')
    b.p("M78 42 C87 42 93 45 93 48 C93 51 87 54 78 54 Z", 'seadk', '#11161B', .9)
    b.r(66, 42, 3, 12, 'yellow')
    b.ln("M42 42 L42 54", '#11161B', .7, .7)
    b.c(91, 48, 1.4, '#1A2026')
    b.hl("M24 43.6 L78 43.6 C84 43.8 88.6 45 91.2 46.6", 1, .6)

@icon('mine', '水雷', '海上')
def _(b):
    b.r(0, 12, 96, 76, 'water')
    b.ln("M2 12 Q8 10 14 12 T26 12 T38 12 T50 12 T62 12 T74 12 T86 12 T98 12", '#FFFFFF', 1.1, .7)
    b.ln("M8 22 Q14 20 20 22 T32 22 M60 20 Q66 18 72 20 T84 20", '#FFFFFF', .8, .3)
    b.p("M0 84 Q14 79 30 82 T60 81 T96 80 L96 90 L0 90 Z", 'sand', '#A88A50', .8)
    b.ln("M48 58 L48 78", '#2A323B', 1.6, extra="stroke-dasharray='2 1.2'")
    b.p("M39 78 L57 78 L60 85 L36 85 Z", 'dkm', DS)
    b.hl("M40 79.2 L56 79.2", .8, .5)
    for a in (-90, -40, -140, 5, 175):
        x, y = 48 + 19 * math.cos(math.radians(a)), 40 + 19 * math.sin(math.radians(a))
        x0, y0 = 48 + 14 * math.cos(math.radians(a)), 40 + 14 * math.sin(math.radians(a))
        b.ln(f"M{x0:.1f} {y0:.1f} L{x:.1f} {y:.1f}", '#1A2026', 4)
        b.ln(f"M{x0:.1f} {y0:.1f} L{x:.1f} {y:.1f}", '#7C8791', 2)
        b.c(round(x, 1), round(y, 1), 2.2, 'metal2', '#1A2026', .8)
    b.c(48, 40, 17, 'mineS', '#11161B', 1.2)
    b.p("M31 40 C31 43 39 45.5 48 45.5 C57 45.5 65 43 65 40 C65 42 57 44 48 44 C39 44 31 42 31 40 Z", '#11161B', op=.6)
    b.e(48, 42.6, 17, 3, 'none', '#8C969F', .9, op=.6)
    b.e(42, 32, 6, 3.6, '#FFFFFF', op=.35)
    b.ln("M48 57 L48 59", '#11161B', 2.4)

@icon('research_vessel', '科考船', '海上')
def _(b):
    b.p("M6 56 L64 56 L92 48 L86 70 L12 70 L8 62 Z", 'white', WS)
    b.p("M9.5 66 L87.6 66 L86 70 L12 70 Z", 'boot')
    b.ln("M8 61 L89 61", '#2F6FB0', 1.8, .9)
    b.p("M46 56 L47 42 L76 42 L80 54 L80 56 Z", 'white', WS)
    b.p("M50 42 L51 32 L72 32 L74 42 Z", 'white', WS)
    b.p("M52 35 L71.6 35 L72 38 L51.8 38 Z", 'canopy')
    for x in (50, 56, 62, 68): b.r(x, 46, 3.6, 3, 'canopy', rx=.4)
    b.r(60.5, 18, 3, 14, 'whitedk', WS, sw=.8); b.ln("M57 23 L67 23", '#6E7A88', 1.1)
    b.c(62, 15.6, 4, 'sphere', WS, .8)
    b.r(40, 46, 4, 10, 'whitedk', WS, sw=.8); b.r(39.4, 44, 5.2, 2.4, '#3A4048', rx=.8)
    b.ln("M30 56 L30 50 L40 36", '#B8691F', 2.2); b.ln("M40 36 L40 46", '#2A323B', .8)
    b.ln("M10 56 L14 38 M22 56 L18 38 M13.5 38 L18.5 38", '#B8691F', 2.4)
    b.ln("M10.8 55 L14.3 39.4", '#F6C27C', .7)
    b.ln("M16 38 L16 39 Q6 44 6 76", '#2A323B', .8)
    b.r(3.4, 76, 5.2, 6, 'metal', MS, rx=1.2, sw=.7)
    b.hl("M8 57.3 L64 57.3 L90 50"); b.hl("M48.4 43.2 L75.8 43.2", .9, .75)
    water(b, 66)

# ================= 陆地 =================
def _armored4x4(b):
    b.sh(48, 82, 42, 4.4)
    b.p("M7 63 L7 51 L16 44 L64 44 L80 51 L89 53 L89 63 Z", 'land', LS)
    b.r(9, 58, 78, 5, 'landdk', LS, rx=1, sw=.9)
    b.p("M66 46 L77.6 51.4 L71 51.4 L63.4 46 Z", 'canopy', '#1B2D40', .6)
    b.r(22, 48, 6, 4, 'canopy', rx=.5); b.r(44, 48, 6, 4, 'canopy', rx=.5)
    b.ln("M36 47 L36 58", '#3E4C29', .9, .7)
    b.r(85, 55, 4, 3, '#F2E6B0', rx=.8, op=.9)
    for x in (19, 37, 61, 77): wheel(b, x, 69, 7.5)
    b.hl("M8 51.4 L16.4 45.3 L64 45.3 L79 51.8")

@icon('recon_vehicle', '装甲侦察车', '陆地')
def _(b):
    _armored4x4(b)
    b.r(26, 40, 14, 4, 'landdk', LS, rx=1, sw=.9)
    b.r(31.6, 16, 2.8, 25, 'landdk', LS, sw=.7); b.r(31, 28, 4, 2, '#3E4C29')
    b.r(20, 6, 26, 8, 'array', '#1E3550', rx=1, sw=.8)
    b.ln("M24 6.5 L24 13.5 M29 6.5 L29 13.5 M34 6.5 L34 13.5 M39 6.5 L39 13.5 M20.5 10 L45.5 10", '#9CC2EA', .5, .6)
    b.r(31, 14, 4, 3, '#3E4C29')
    b.c(33, 21, 4.6, 'land', LS, 1); b.c(34.4, 21, 2.6, 'lens', '#05101C', .5); glint(b, 33.4, 20, .8, .6)
    b.ln("M14 44 L10 20", '#2E3238', 1.1); b.c(10, 20, 1.1, '#2E3238')
    b.r(54, 39, 10, 5, 'landdk', LS, rx=1, sw=.8); b.r(62, 40.4, 14, 2, '#3A3F46')
    b.hl("M21 7.2 L45 7.2", .8, .8)

def _shelter(b, x=6, y=30, w=60, h=30):
    b.r(x, y, w, h, 'land', LS, rx=1.5)
    b.r(x, y, w, 3.2, 'landdk', LS, rx=1.2, sw=.8)
    b.hl(f"M{x+2} {y+4.4} L{x+w-2} {y+4.4}", 1, .6)

@icon('command_vehicle', '指挥车', '陆地')
def _(b):
    _truck_base(b, (18, 33, 77), cab_x=66, cab_top=42)
    _shelter(b)
    b.r(40, 38, 10, 20, 'none', '#3E4C29', rx=.6, sw=1); b.c(48, 48, .9, '#2E3238')
    b.r(14, 38, 16, 7, 'canopy', rx=.8)
    for i in range(4): b.ln(f"M{15 + i*3.8:.1f} 50 L{15 + i*3.8:.1f} 56", '#3E4C29', 1.2, .7)
    leds(b, [(56, 40, GREEN), (60, 40, AMBER)])
    b.ln("M12 30 L8 4 M20 30 L22 8 M60 30 L64 6", '#2E3238', 1.1)
    for x, y in ((8, 4), (22, 8), (64, 6)): b.c(x, y, 1.2, '#2E3238')
    b.r(39.6, 16, 2.8, 14, 'landdk', LS, sw=.7)
    b.ln("M33 12 L49 12 M35 16 L47 16 M37 20 L45 20", '#3A3F46', 1.2)
    b.ln("M41 20 L41 9", '#3A3F46', 1.2)

@icon('comm_vehicle', '通信车', '陆地')
def _(b):
    _truck_base(b, (18, 33, 77), cab_x=66, cab_top=42)
    _shelter(b, 6, 36, 60, 24)
    b.r(12, 42, 12, 6, 'canopy', rx=.8)
    b.r(46, 42, 9, 16, 'none', '#3E4C29', rx=.6, sw=1)
    leds(b, [(30, 45, GREEN), (34, 45, GREEN)])
    b.r(30, 30, 6, 6, 'landdk', LS, rx=1, sw=.8)
    b.ln("M33 30 L33 26", '#3A3F46', 2)
    b.g('rotate(-35 34 18)')
    b.e(34, 18, 17, 7, 'metal3', MS)
    b.e(34, 16.8, 15.6, 5.6, 'metal', MS, .8)
    b.eg()
    b.ln("M24 25 L45 8 M44 26 L45 8", '#5E6A78', 1)
    b.c(45, 8, 1.8, 'metal2', MS, .7)
    b.ln("M52 12 Q56 16 54 21 M56 7 Q63 14 59 24 M61 3 Q70 14 64 27", '#3D86D6', 1.6, .85)
    b.ln("M62 36 L64 14", '#2E3238', 1.1); b.c(64, 14, 1.1, '#2E3238')
    b.hl("M20 14 Q26 8 36 7", 1, .7)

@icon('engineering', '工程车', '陆地')
def _(b):
    b.sh(48, 84, 44, 4.2)
    track(b, 6, 62, 66, 81, 5)
    b.r(10, 62, 48, 4.6, 'landdk', LS, rx=1, sw=.9)
    b.p("M6 62 L6 50 C6 47 8 46 11 46 L44 46 L48 52 L48 62 Z", 'land', LS)
    b.r(6, 52, 10, 10, 'landdk', LS, rx=1.5, sw=.9)
    for x in (24, 28, 32): b.ln(f"M{x} 50 L{x} 58", '#3E4C29', 1, .6)
    b.p("M30 46 L30 30 L42 30 L46 46 Z", 'land', LS)
    b.p("M32 32.5 L41 32.5 L43.6 44 L32 44 Z", 'canopy', '#1B2D40', .6)
    glint(b, 35, 35, 1.4, .7)
    b.p("M42 54 L46 47 L68 15 L75 18 L51 56 Z", 'land', LS)
    b.ln("M48 50 L64 25", '#E8EDF2', 1.6); b.ln("M48 50 L64 25", '#8F9BA9', .7)
    b.p("M68 15 L75 18 L84 50 L79.5 51.5 Z", 'land', LS)
    b.ln("M74 22 L80 44", '#E8EDF2', 1.4)
    b.c(71.5, 16.6, 2.6, 'hub', '#1D2228', .7); b.c(81.6, 50.8, 2.4, 'hub', '#1D2228', .7)
    b.p("M78 50 L91 53 L90 65 L84 66 L77 59 Z", 'dkm', DS)
    b.ln("M84 66 L83 69 M87 65.5 L86.6 68.6 M90 65 L90 68", '#2A2E33', 1.4)
    b.hl("M7 49 C7.5 47.6 9 47.3 11 47.3 L43.4 47.3"); b.hl("M47 47.6 L67.6 16.6", 1, .7)

@icon('fuel_truck', '油料保障车', '陆地')
def _(b):
    _truck_base(b, (16, 30, 58, 77), cab_x=68, cab_top=44)
    b.r(10, 34, 58, 25, 'land', LS, rx=12)
    b.e(14, 46.5, 4, 11.6, 'landdk', LS, 1)
    b.ln("M14 37 L66 37", '#FFFFFF', 1.4, .6)
    b.ln("M28 35 L28 58 M46 35 L46 58", '#3E4C29', .9, .6)
    for x in (20, 37, 55): b.r(x - 3, 31, 6, 3.4, 'landdk', LS, rx=1, sw=.8)
    b.ln("M14 30 L64 30", '#3A3F46', 1); b.ln("M16 30 L16 34 M34 30 L34 34 M52 30 L52 34", '#3A3F46', .9)
    b.p("M50 42 L55 47 L50 52 L45 47 Z", 'orange', '#8A4E17', .8)
    b.p("M50 44 C51.6 46 52 47 52 48 C52 49.4 51 50.2 50 50.2 C49 50.2 48 49.4 48 48 C48 47 48.6 46 50 44 Z", '#FFFFFF', op=.85)
    b.c(10, 56.5, 3.4, 'metal3', MS, .8); b.c(10, 56.5, 1.4, '#2A2E33')

@icon('ambulance', '救护车', '陆地')
def _(b):
    _truck_base(b, (18, 33, 77), cab_x=66, cab_top=42)
    b.r(6, 28, 60, 32, 'land', LS, rx=2)
    b.hl("M8 29.6 L64 29.6", 1.1, .7)
    b.r(24, 33, 24, 22, '#F6F8FA', '#9AA5B2', rx=2, sw=1)
    b.r(32.5, 36, 7, 16, 'red', '#7A2219', .6); b.r(27, 40.5, 18, 7, 'red', '#7A2219', .6)
    b.r(32.5, 40.5, 7, 7, 'red')
    b.r(10, 34, 8, 9, 'canopy', rx=.8)
    b.r(52, 34, 10, 6, 'canopy', rx=.8)
    b.r(72, 39, 8, 3, '#3D86D6', '#1F4F8C', rx=1.2, sw=.6); b.e(76, 39.4, 2.4, .8, '#FFFFFF', op=.7)

@icon('cuas', '反无人机系统', '陆地')
def _(b):
    _armored4x4(b)
    b.p("M24 44 L26 38 L54 38 L56 44 Z", 'landdk', LS)
    for i, x in enumerate((27, 36, 45)):
        b.g(f'rotate({(i-1)*12} {x+3.5} 38)')
        b.r(x, 20, 7, 17, 'metal', MS, rx=1, sw=.9)
        for k in range(3): b.ln(f"M{x+1.6} {23 + k*4.6} L{x+5.4} {23 + k*4.6}", '#7D8996', 1)
        b.eg()
    b.r(60, 26, 2.6, 18, 'landdk', LS, sw=.6)
    b.p("M53 16 L69 14 L70 25 L54 27 Z", 'array', '#2C3E52', 1)
    b.ln("M57 15.6 L58 26.4 M61.5 15 L62.4 25.9 M66 14.5 L66.8 25.4 M53.6 21.4 L69.4 19.6", '#9CC2EA', .5, .7)
    b.ln("M8 22 L13 18 L11 25 L18 19 L16 26", WAVE, 1.4)
    b.ln("M74 30 L79 26 L77 33 L84 27 L82 34", WAVE, 1.4)
    b.g('translate(84 10)')
    b.ln("M-5 -3 L5 3 M5 -3 L-5 3", '#5E6A78', 1.6)
    for x, y in ((-5, -3), (5, -3), (-5, 3), (5, 3)): b.e(x, y, 3, 1.1, '#8D9BAC', op=.8)
    b.r(-2, -1.6, 4, 3.2, '#5E6A78', rx=1)
    b.ln("M-7 -7 L7 7", REDL, 2)
    b.eg()

@icon('laser_weapon', '激光武器', '陆地')
def _(b):
    _truck_base(b, (16, 30, 77), cab_x=68, cab_top=44)
    b.r(8, 52, 60, 8, 'land', LS, rx=1)
    b.ln("M24 52 L24 60 M44 52 L44 60", '#3E4C29', .9, .6)
    b.p("M22 52 L24 44 L42 44 L44 52 Z", 'landdk', LS)
    b.g('rotate(-28 33 37)')
    b.ln("M56 37 L95 37", LASER, 7, .18)
    b.ln("M56 37 L95 37", LASER, 3, .7)
    b.ln("M56 37 L95 37", '#FFFFFF', 1.1, .95)
    b.r(18, 29, 36, 16, 'land', LS, rx=5)
    b.r(22, 31, 10, 4, 'landdk', LS, rx=1, sw=.6)
    b.e(53, 37, 3.4, 7, 'dkm2', DS, .9)
    b.e(53.8, 37, 2.2, 5.2, 'lens', '#05101C', .5)
    b.hl("M21 31 L50 31", 1, .7)
    b.c(56, 37, 3.4, 'spark')
    b.eg()
    b.c(33, 37, 3, 'hub', '#1D2228', .7)
    b.c(88.7, 8.9, 7, 'spark')
    b.ln("M83 3 L94 14 M94 3 L83 14", '#FFFFFF', 1, .8)

@icon('hpm', '高能微波武器', '陆地')
def _(b):
    b.sh(48, 82, 42, 4.5)
    track(b, 8, 82, 65, 80, 6)
    b.p("M5 66 L7 56 L78 54 L88 60 L86 66 Z", 'land', LS)
    b.r(10, 61, 74, 6, 'landdk', LS, rx=1, sw=1)
    b.p("M20 55 L22 46 L46 46 L48 55 Z", 'land', LS)
    b.r(30, 36, 4, 10, 'landdk', LS, sw=.8)
    b.p("M40 8 L46 6 L46 50 L40 50 Z", 'metal3', MS, 1)
    b.p("M46 6 L64 12 L64 46 L46 50 Z", 'metal2', MS)
    b.p("M48 9.2 L62 13.8 L62 44.2 L48 47.4 Z", 'array', '#1E3550', .8)
    wins(b, [(49.6 + i * 3.3, 12.4 + j * 7 + i * 1.1 - j * i * .35) for i in range(4) for j in range(5)], 2.2, 3.4, '#C9A145', '#6E5418', .3)
    b.p("M48 9.2 L54 11.2 L54 46 L48 47.4 Z", '#FFFFFF', op=.12)
    b.ln("M32 38 L40 30", '#3E4C29', 2.4)
    wav(b, 64, 29, (8, 15, 22, 29), -55, 55, WAVE, 2.2)
    b.hl("M8 57.3 L78 55.3", 1, .7); b.hl("M47 7.4 L63 12.6", .9, .8)

@icon('mortar', '迫击炮', '陆地')
def _(b):
    b.sh(44, 84, 36, 4)
    b.p("M12 80 L40 73 L54 78 L26 86 Z", 'dkm', DS)
    b.p("M14 80 L40 74 L50 77.6", 'none', '#8A939C', .8)
    b.ln("M56 50 L46 84 M60 50 L68 82", '#3E4C29', 3.2)
    b.ln("M56 50 L46 84 M60 50 L68 82", '#86995D', 1.4)
    b.ln("M44 84 L49 84 M66 82 L71 82", '#2E3238', 2)
    b.g('rotate(-60 34 77)')
    b.r(30, 72, 66, 9, 'land', LS, rx=2.5)
    b.r(90, 71, 6, 11, 'landdk', LS, rx=1.2, sw=1)
    b.r(28, 73, 6, 7, 'landdk', LS, rx=2, sw=.8)
    b.hl("M33 74 L89 74", 1.1, .8)
    b.eg()
    b.r(54, 47, 9, 6, 'landdk', LS, rx=1, sw=.8)
    b.c(66, 53, 3.4, 'none', '#2E3238', 1.2); b.ln("M63 50 L66 53", '#2E3238', 1)
    b.g('rotate(30 80 12)')
    b.p("M80 4 C82.6 6 83.4 9 83.4 12 L83.4 16 L76.6 16 L76.6 12 C76.6 9 77.4 6 80 4 Z", 'metal3', MS, .8)
    b.p("M76.6 16 L74.6 20 L85.4 20 L83.4 16 Z", 'dkm', DS, .6)
    b.eg()
    b.c(70, 18, 3.6, 'smoke', op=.85); b.c(74.5, 13.6, 2.6, 'smoke', op=.6)

@icon('spaa', '弹炮结合防空车', '陆地')
def _(b):
    b.sh(48, 82, 42, 4.5)
    track(b, 8, 84, 65, 80, 6)
    b.p("M5 66 L7 55 L80 54 L90 60 L88 66 Z", 'land', LS)
    b.r(10, 61, 76, 6, 'landdk', LS, rx=1, sw=1)
    for dy_ in (0, 5):
        b.g(f'rotate(-30 60 {41+dy_})')
        b.r(60, 39.6 + dy_, 32, 2.6, '#3A3F46', DS, sw=.6)
        b.r(86, 39 + dy_, 6, 3.8, '#2A2E33', rx=.6)
        b.eg()
    b.p("M22 54 L24 36 L60 36 L68 44 L68 54 Z", 'land', LS)
    b.r(56, 40, 10, 10, 'landdk', LS, rx=1.5, sw=.9)
    b.c(61, 45, 3.2, 'metal2', LS, .8); b.c(61, 45, 1.2, '#2E3238')
    b.g('rotate(-22 30 46)')
    b.r(6, 38, 28, 10, 'landdk', LS, rx=1, sw=1)
    for k in range(2):
        b.c(32, 40.6 + k * 4.8, 2, '#E8EDF2', '#3A3F46', .6)
    b.ln("M8 43 L30 43", '#3E4C29', .8, .7)
    b.eg()
    b.r(38, 30, 4, 6, 'landdk', LS, sw=.6)
    b.p("M28 20 L52 18 L53 29 L29 31 Z", 'array', '#2C3E52', 1)
    b.ln("M34 19.5 L35 30.5 M40 19 L41 30 M46 18.5 L47 29.5 M28.5 25.4 L52.5 23.4", '#9CC2EA', .5, .7)
    b.hl("M25.4 37.3 L59.4 37.3 L66.6 44"); b.hl("M8 56.3 L80 55.3", 1, .7)

@icon('ugv_tracked', '履带无人车', '陆地')
def _(b):
    b.sh(48, 82, 40, 4.2)
    track(b, 8, 86, 63, 80, 5)
    b.p("M6 63 L8 52 L80 52 L90 58 L88 63 Z", 'land', LS)
    b.r(10, 59, 76, 5, 'landdk', LS, rx=1, sw=.9)
    b.r(80, 55, 6, 3, 'canopy', rx=.6)
    b.p("M40 52 L42 44 L58 44 L60 52 Z", 'landdk', LS)
    b.r(56, 46, 26, 2.6, '#3A3F46', DS, sw=.6)
    b.r(44, 38, 10, 6, 'land', LS, rx=1.2, sw=.9); b.r(46, 39.6, 6, 3, 'canopy', rx=.6)
    b.r(18.8, 30, 2.6, 22, 'landdk', LS, sw=.7)
    b.r(14, 23, 12, 8, 'land', LS, rx=2); b.c(23, 27, 2.6, 'lens', '#05101C', .5); glint(b, 22.2, 26, .8, .5)
    b.ln("M72 52 L76 16", '#2E3238', 1.1); b.c(76, 16, 1.2, '#2E3238')
    leds(b, [(32, 56, GREEN), (36, 56, GREEN)])
    b.hl("M8.6 53.3 L80 53.3 L88 58.2")

@icon('eod_robot', '排爆机器人', '陆地')
def _(b):
    b.sh(48, 84, 38, 4)
    b.g('rotate(-18 64 73)')
    track(b, 58, 80, 67, 78, 2)
    b.eg()
    track(b, 12, 66, 66, 81, 4)
    b.r(14, 52, 50, 14, 'land', LS, rx=2.5)
    b.r(18, 56, 14, 6, 'landdk', LS, rx=1, sw=.8)
    leds(b, [(54, 58, GREEN), (58, 58, AMBER)])
    b.ln("M20 52 L18 30", '#2E3238', 1.1); b.c(18, 30, 1.1, '#2E3238')
    arm = "M34 50 L46 22 L72 34"
    b.ln(arm, LS, 8); b.ln(arm, '#86995D', 5.4)
    b.ln("M35.6 46 L46 23.6 L70 34.4", '#C9D59F', 1, .8)
    b.ln("M72 34 L80 56", LS, 6); b.ln("M72 34 L80 56", '#86995D', 3.6)
    for x, y, r in ((34, 50, 4), (46, 22, 3.6), (72, 34, 3.4)): b.c(x, y, r, 'hub', '#1D2228', .8)
    b.r(44, 12, 10, 6, 'landdk', LS, rx=1.5, sw=.8); b.c(52, 15, 2, 'lens', '#05101C', .4)
    b.ln("M78 56 L74 64 M82 56 L86 64", '#2E3238', 2.2)
    b.p("M76 68 L90 68 L90 76 L76 76 Z", '#5A626C', '#2A2E33', .8)
    b.r(81, 68, 3, 8, 'orange'); b.ln("M90 70 Q93 66 92 62", REDL, .9)
    b.hl("M16 53.6 L62 53.6")

# ================= 设施 =================
@icon('airbase', '机场', '设施')
def _(b):
    x0, y0 = 4, 80
    P = PP(x0, y0)
    plate(b, x0, y0, 60, 28)
    poly(b, [P(2, 2), P(2, 13), P(58, 13), P(58, 2)], 'tarmac', '#2E343C')
    a, c_ = P(7, 7.5), P(55, 7.5)
    b.ln(f"M{a[0]:.1f} {a[1]:.1f} L{c_[0]:.1f} {c_[1]:.1f}", '#FFFFFF', 1, .9, extra="stroke-dasharray='3 2.4'")
    for k in (4, 6, 9, 11):
        p1, p2 = P(3.5, k), P(6, k)
        b.ln(f"M{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f}", '#FFFFFF', .8, .8)
    # hangar (barrel roof)
    hx, hy, hw, hd = P(6, 16)[0], P(6, 16)[1], 26, 10
    for i in range(4, -1, -1):
        t = i / 4
        ox, oy = hx + hd * t, hy - hd * R * t
        b.p(f"M{ox:.1f} {oy:.1f} L{ox:.1f} {oy-5:.1f} A13 12 0 0 1 {ox+hw:.1f} {oy-5:.1f} L{ox+hw:.1f} {oy:.1f} Z",
            'roof', RF, .8)
    b.p(f"M{hx:.1f} {hy:.1f} L{hx:.1f} {hy-5:.1f} A13 12 0 0 1 {hx+hw:.1f} {hy-5:.1f} L{hx+hw:.1f} {hy:.1f} Z", 'conc', CS, 1)
    b.p(f"M{hx+5:.1f} {hy:.1f} L{hx+5:.1f} {hy-6:.1f} A8 7 0 0 1 {hx+hw-5:.1f} {hy-6:.1f} L{hx+hw-5:.1f} {hy:.1f} Z", 'dkm2', DS, .8)
    b.hl(f"M{hx+2:.1f} {hy-8:.1f} A12 11 0 0 1 {hx+10:.1f} {hy-15.4:.1f}", 1, .8)
    # tower
    tx, ty = P(42, 18)
    box(b, tx, ty, 5, 24, 4)
    box(b, tx - 2, ty - 24, 9, 6, 6, ft='glass', tp='concT', sd='canopy', st='#25578F')
    box(b, tx - 2.6, ty - 30, 10, 1.8, 6.4, ft='metal3', tp='metal2', sd='metal3', st=MS, hl=False)
    b.ln(f"M{tx+4} {ty-32.6} L{tx+4} {ty-38}", '#5E6A78', 1); b.c(tx + 4, ty - 38, 1.1, REDL)
    # aircraft on runway
    px, py = P(28, 7.5)
    b.g(f'translate({px:.1f} {py:.1f}) rotate(-30) scale(.62)')
    d = "M14 0 C14 -1.6 12 -2.2 8 -2.2 L4 -2.2 L-4 -13 L-8 -13 L-4 -2.2 L-11 -2 L-14 -6 L-16.4 -6 L-15 0 L-16.4 6 L-14 6 L-11 2 L-4 2.2 L-8 13 L-4 13 L4 2.2 L8 2.2 C12 2.2 14 1.6 14 0 Z"
    b.drop(d, 1.5, 2, .25)
    b.p(d, 'air', AS, 1.2)
    b.eg()
    tree(b, *P(54, 16), 3.4); tree(b, *P(50, 25), 3)

@icon('port', '港口', '设施')
def _(b):
    b.r(0, 56, 96, 34, 'water')
    b.ln("M2 76 Q8 74 14 76 T26 76 T38 76 M20 84 Q26 82 32 84 T44 84 T56 84", '#FFFFFF', .9, .5)
    x0, y0 = 30, 72
    P = PP(x0, y0)
    plate(b, x0, y0, 36, 26, top='concT', edge='conc', shadow=False)
    # containers
    cx, cy = P(14, 18)
    box(b, cx, cy, 12, 5, 6, ft='contB', tp='#8CB2DE', sd='#2D5486', st='#1E3A5E', hl=False)
    box(b, cx + 12, cy, 10, 5, 6, ft='contG', tp='#B5D3BC', sd='#45705A', st='#2E4D3C', hl=False)
    box(b, cx + 3, cy - 5, 12, 5, 6, ft='contR', tp='#EBA095', sd='#8E2E22', st='#6A1F17', hl=False)
    cx, cy = P(18, 7)
    box(b, cx, cy, 12, 5, 6, ft='orange', tp='#F6CB8E', sd='#9A5414', st='#7A4210', hl=False)
    box(b, cx + 12, cy, 6, 5, 6, ft='contB', tp='#8CB2DE', sd='#2D5486', st='#1E3A5E', hl=False)
    # quay crane (rear legs, then front)
    for (x, c1) in ((48, '#9A5414'), (66, '#9A5414')):
        b.p(f"M{x} 64 L{x+1} 22 L{x+3} 22 L{x+3} 64 Z", '#B8691F', '#7A4210', .7)
    b.ln("M14 24 L50 8 L70 22", '#7A4210', 1.2)
    b.p("M4 22 L72 22 L72 27 L8 27 Z", 'orange', '#7A4210', 1)
    for x in range(12, 70, 6): b.ln(f"M{x} 22.6 L{x+3} 26.4", '#9A5414', .7, .8)
    b.p("M47 22 L50 7 L53 7 L54 22 Z", 'orange', '#7A4210', .9)
    b.r(54, 14, 14, 8, 'conc', CS, rx=1, sw=.8); b.r(56, 16, 4, 3, 'canopy', rx=.4)
    for x in (38, 58):
        b.p(f"M{x} 72 L{x+1} 27 L{x+4} 27 L{x+4} 72 Z", 'orange', '#7A4210', .9)
        b.ln(f"M{x+1.4} 70 L{x+2} 29", '#F6CB8E', .8, .9)
    b.ln("M40 46 L60 46", '#9A5414', 2)
    b.r(15, 27, 6, 3, '#3A4048', rx=.6)
    b.ln("M17 30 L17 42 M19 30 L19 42", '#2A2E33', .7)
    b.r(10, 42, 16, 5, 'contR', '#6A1F17', sw=.8)
    b.hl("M5 23.2 L71 23.2", .9, .8)
    # moored ship
    b.p("M2 60 L30 60 L35 56 L32 70 L5 70 Z", 'sea', SS, .9)
    b.p("M3.6 67 L32.7 67 L32 70 L5 70 Z", 'boot')
    b.p("M4 60 L5 52 L13 52 L14 60 Z", 'sea', SS, .8); b.r(6, 53.6, 6, 1.6, 'canopy')
    b.r(16, 56, 12, 4, 'contB', '#1E3A5E', sw=.6)
    b.hl("M3 61.2 L30 61.2 L34 58", .8, .7)

@icon('barracks', '营区', '设施')
def _(b):
    x0, y0 = 4, 80
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30)
    poly(b, [P(4, 2), P(4, 9), P(58, 9), P(58, 2)], 'concT', CS, .7)
    for (u, v) in ((10, 18),):
        x, y = P(u, v)
        gable_u(b, x, y, 40, 10, 8, 5)
        wins(b, [(x + 3 + i * 6.2, y - 7.4) for i in range(6)], 3.6, 4)
    x, y = P(4, 2)
    gable_u(b, x, y, 40, 11, 8, 5.5)
    wins(b, [(x + 3 + i * 6.2, y - 8.4) for i in range(6)], 3.6, 4.4)
    b.r(x + 18, y - 6, 4, 6, 'dkm', DS, sw=.6)
    for (u, v, r) in ((52, 3, 3.4), (54, 13, 3), (52, 24, 3.2), (3, 25, 3)):
        tx, ty = P(u, v); tree(b, round(tx, 1), round(ty, 1), r)
    fx, fy = P(48, 8)
    b.ln(f"M{fx:.1f} {fy:.1f} L{fx:.1f} {fy-30:.1f}", '#5E6A78', 1.3)
    b.p(f"M{fx+.5:.1f} {fy-30:.1f} Q{fx+5:.1f} {fy-31.6:.1f} {fx+9:.1f} {fy-29.4:.1f} Q{fx+11:.1f} {fy-28:.1f} {fx+13:.1f} {fy-29:.1f} L{fx+13:.1f} {fy-22:.1f} Q{fx+11:.1f} {fy-21:.1f} {fx+9:.1f} {fy-22.4:.1f} Q{fx+5:.1f} {fy-24.6:.1f} {fx+.5:.1f} {fy-23:.1f} Z", 'red', '#7A2219', .7)

@icon('depot', '仓库', '设施')
def _(b):
    x0, y0 = 4, 80
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30, top='concT', edge='conc')
    x, y = P(4, 6)
    gable_v(b, x, y, 36, 22, 22, 9)
    for k in (0, 1):
        dx_ = x + 4 + k * 16
        b.r(dx_, y - 16, 12, 16, '#5A626C', '#2A2E33', sw=.8)
        for j in range(1, 8): b.ln(f"M{dx_+.4} {y-16+j*2:.1f} L{dx_+11.6} {y-16+j*2:.1f}", '#8A939C', .6, .8)
    b.c(x + 18, y - 25, 2.6, 'glass', '#25578F', .6)
    for (u, v) in ((48, 2), (54, 2), (48, 8)):
        cx_, cy_ = P(u, v); box(b, round(cx_, 1), round(cy_, 1), 5, 5, 5, ft='crate', tp='#E8CFA0', sd='#8A6634', st='#6B4E26', hl=False)
    cx_, cy_ = P(51, 5); box(b, round(cx_, 1), round(cy_ - 5, 1), 5, 5, 5, ft='crate', tp='#E8CFA0', sd='#8A6634', st='#6B4E26', hl=False)

@icon('launch_site', '发射阵地', '设施')
def _(b):
    x0, y0 = 4, 82
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30, top='concT', edge='conc')
    poly(b, [P(24, 2), P(24, 8), P(40, 8), P(40, 2)], 'dkm2', DS, .7)
    poly(b, [P(16, 10), P(16, 22), P(46, 22), P(46, 10)], 'conc', CS, .8)
    for (u, v) in ((2, 2), (56, 2), (2, 28), (56, 28)):
        lx, ly = P(u, v); b.ln(f"M{lx:.1f} {ly:.1f} L{lx:.1f} {ly-34:.1f}", '#5E6A78', 1.1); b.c(round(lx, 1), round(ly - 34, 1), 1, REDL)
    tx, ty = P(36, 18)
    b.ln(f"M{tx:.1f} {ty:.1f} L{tx:.1f} 6 M{tx+8:.1f} {ty-4.6:.1f} L{tx+8:.1f} 4", '#5E6A78', 2)
    for k in range(7):
        yy = ty - 6 - k * 8
        b.ln(f"M{tx:.1f} {yy:.1f} L{tx+8:.1f} {yy-4.6-8:.1f} M{tx:.1f} {yy-8:.1f} L{tx+8:.1f} {yy-4.6:.1f}", '#7D8996', .7)
    mx, my = P(28, 15)
    b.ln(f"M{tx:.1f} 24 L{mx+4:.1f} 26 M{tx:.1f} 44 L{mx+4:.1f} 46", '#5E6A78', 1.4)
    b.p(f"M{mx:.1f} {my-4:.1f} L{mx-5:.1f} {my+1:.1f} L{mx-5:.1f} {my+3:.1f} L{mx:.1f} {my:.1f} Z", 'whitedk', WS, .8)
    b.p(f"M{mx+8:.1f} {my-4:.1f} L{mx+13:.1f} {my+1:.1f} L{mx+13:.1f} {my+3:.1f} L{mx+8:.1f} {my:.1f} Z", 'whitedk', WS, .8)
    b.p(f"M{mx+4:.1f} 6 C{mx+7:.1f} 10 {mx+8:.1f} 15 {mx+8:.1f} 20 L{mx+8:.1f} {my+1:.1f} L{mx:.1f} {my+1:.1f} L{mx:.1f} 20 C{mx:.1f} 15 {mx+1:.1f} 10 {mx+4:.1f} 6 Z", 'cylW', WS)
    b.r(round(mx, 1), 22, 8, 3, 'red')
    b.ln(f"M{mx+2:.1f} 14 L{mx+2:.1f} 20 M{mx+2:.1f} 27 L{mx+2:.1f} {my-2:.1f}", '#FFFFFF', 1, .85)
    b.r(round(mx - .6, 1), round(my - 2, 1), 9.2, 3, '#3A4048', rx=.6)

@icon('radar_station', '雷达站', '设施')
def _(b):
    x0, y0 = 4, 82
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30)
    x, y = P(8, 6)
    box(b, x, y, 30, 16, 18)
    wins(b, [(x + 3 + i * 7, y - 12) for i in range(4)], 4.4, 4)
    b.r(x + 12, y - 7, 5, 7, 'dkm', DS, sw=.6)
    cx = x + 15 + 9; cy = y - 16 - 9 * R
    vcyl(b, round(cx, 1), round(cy + 2, 1), 7, 6, 'cylM', 'metal', MS)
    b.c(round(cx, 1), round(cy - 15, 1), 14, 'sphere', MS, 1.1)
    for dxx in (-7, 0, 7):
        b.ln(f"M{cx+dxx:.1f} {cy-28.4:.1f} Q{cx+dxx*1.7:.1f} {cy-15:.1f} {cx+dxx:.1f} {cy-1.6:.1f}", '#A3AEBB', .6, .7)
    b.ln(f"M{cx-13.4:.1f} {cy-12:.1f} Q{cx:.1f} {cy-8:.1f} {cx+13.4:.1f} {cy-12:.1f} M{cx-11:.1f} {cy-22:.1f} Q{cx:.1f} {cy-19:.1f} {cx+11:.1f} {cy-22:.1f}", '#A3AEBB', .6, .7)
    b.e(round(cx - 5, 1), round(cy - 21, 1), 4.6, 3, '#FFFFFF', op=.8)
    dx_, dy_ = P(52, 16)
    b.ln(f"M{dx_:.1f} {dy_:.1f} L{dx_:.1f} {dy_-12:.1f}", '#5E6A78', 1.8)
    b.g(f'rotate(-35 {dx_:.1f} {dy_-16:.1f})'); b.e(round(dx_, 1), round(dy_ - 16, 1), 7, 2.8, 'metal', MS, .9); b.eg()
    b.ln(f"M{dx_+5:.1f} {dy_-26:.1f} Q{dx_+9:.1f} {dy_-22:.1f} {dx_+7:.1f} {dy_-17:.1f}", '#3D86D6', 1.3, .85)
    tree(b, 12, 78, 3.4)

@icon('command_center', '指挥中心', '设施')
def _(b):
    x0, y0 = 4, 84
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30)
    poly(b, [P(6, 2), P(6, 8), P(56, 8), P(56, 2)], 'concT', CS, .7)
    x, y = P(2, 12); box(b, x, y, 18, 16, 14)
    wins(b, [(x + 2.4 + i * 5.4, y - 13 + j * 6) for i in range(3) for j in range(2)], 3.4, 3.6)
    x, y = P(40, 12); box(b, x, y, 16, 16, 14)
    wins(b, [(x + 2 + i * 4.8, y - 13 + j * 6) for i in range(3) for j in range(2)], 3.2, 3.6)
    x, y = P(20, 10); box(b, x, y, 20, 40, 16)
    wins(b, [(x + 2.4 + i * 5.6, y - 37 + j * 7) for i in range(3) for j in range(5)], 4, 4.6)
    b.r(x + 7, y - 6, 6, 6, 'dkm', DS, sw=.6)
    tx, ty = x + 8 + 8, y - 40 - 8 * R
    b.ln(f"M{tx:.1f} {ty:.1f} L{tx:.1f} {ty-18:.1f} M{tx-4:.1f} {ty-12:.1f} L{tx+4:.1f} {ty-12:.1f} M{tx-3:.1f} {ty-7:.1f} L{tx+3:.1f} {ty-7:.1f}", '#5E6A78', 1.3)
    b.c(round(tx, 1), round(ty - 18, 1), 1.1, REDL)
    b.g(f'rotate(-30 {tx+12:.1f} {ty-2:.1f})'); b.e(round(tx + 12, 1), round(ty - 3, 1), 5, 2, 'metal', MS, .8); b.eg()
    b.ln(f"M{tx+12:.1f} {ty-1:.1f} L{tx+12:.1f} {ty+2:.1f}", '#5E6A78', 1.2)
    fx, fy = P(47, 19)
    flag(b, round(fx, 1), round(fy - 16, 1), 15)

@icon('power_station', '电站', '设施')
def _(b):
    x0, y0 = 4, 82
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30)
    x, y = P(4, 6)
    for (u, h) in ((10, 30), (20, 26)):
        sx, sy = P(4 + u, 6 + 10)
        vcyl(b, round(sx, 1), round(sy - 14, 1), 3.4, h, 'cylM', 'metal3', MS)
        b.r(round(sx - 3.4, 1), round(sy - 14 - h + 3, 1), 6.8, 2, 'red', op=.9)
    box(b, x, y, 32, 20, 16)
    b.ln(f"M{x+2} {y-14} L{x+30} {y-14}", '#97A3B1', .8)
    b.p(f"M{x+19} {y-18} L{x+13} {y-8} L{x+17} {y-8} L{x+14} {y-1} L{x+22} {y-11} L{x+18} {y-11} L{x+21} {y-18} Z", 'yellow', '#8A6A10', .7)
    for i in range(3): b.r(x + 2.4 + i * 3.4, y - 11, 2.4, 9, 'dkm2', rx=.4)
    tx_, ty_ = P(44, 4); box(b, round(tx_, 1), round(ty_, 1), 8, 7, 6, 'metal2', 'metal', 'metal3', MS)
    for k in range(4): b.ln(f"M{tx_+1.4+k*1.8:.1f} {ty_-6:.1f} L{tx_+1.4+k*1.8:.1f} {ty_-1:.1f}", '#5E6A78', .8)
    px, py = P(52, 20)
    b.ln(f"M{px-6:.1f} {py:.1f} L{px:.1f} {py-44:.1f} L{px+6:.1f} {py:.1f}", '#5E6A78', 1.8)
    b.ln(f"M{px-4.6:.1f} {py-10:.1f} L{px+3:.1f} {py-22:.1f} M{px+4.6:.1f} {py-10:.1f} L{px-3:.1f} {py-22:.1f} M{px-2.4:.1f} {py-26:.1f} L{px+1.6:.1f} {py-34:.1f} M{px+2.4:.1f} {py-26:.1f} L{px-1.6:.1f} {py-34:.1f}", '#7D8996', .8)
    for (yy, ww) in ((py - 36, 11), (py - 28, 8)):
        b.ln(f"M{px-ww:.1f} {yy:.1f} L{px+ww:.1f} {yy:.1f}", '#5E6A78', 1.6)
        for s in (-1, 1):
            b.ln(f"M{px+s*ww:.1f} {yy:.1f} L{px+s*ww:.1f} {yy+3:.1f}", '#C9D1DA', 1.6)
    b.ln(f"M{px-11:.1f} {py-33:.1f} Q{px-24:.1f} {py-29:.1f} {x+30:.1f} {y-24:.1f} M{px+11:.1f} {py-33:.1f} Q{px+20:.1f} {py-28:.1f} 92 {py-31:.1f} M{px+8:.1f} {py-25:.1f} Q{px+18:.1f} {py-20:.1f} 92 {py-23:.1f}", '#3A4048', .7)

@icon('fuel_depot', '油库', '设施')
def _(b):
    x0, y0 = 4, 82
    P = PP(x0, y0)
    plate(b, x0, y0, 58, 30)
    poly(b, [P(3, 3), P(3, 27), P(55, 27), P(55, 3)], 'concT', CS, .8)
    tanks = [(16, 21, 11, 18), (41, 21, 11, 18), (14, 7, 10, 15), (39, 7, 10, 15)]
    p1, p2 = P(16, 21), P(39, 7)
    b.ln(f"M{p1[0]:.1f} {p1[1]-2:.1f} L{p2[0]:.1f} {p2[1]-2:.1f}", '#5E6A78', 1.6)
    for (u, v, r, h) in tanks:
        cx, cy = P(u, v)
        vcyl(b, round(cx, 1), round(cy, 1), r, h)
        b.ln(f"M{cx+r-2.6:.1f} {cy-1:.1f} L{cx+r-2.6:.1f} {cy-h+1:.1f} M{cx+r-.8:.1f} {cy-1:.1f} L{cx+r-.8:.1f} {cy-h+1:.1f}", '#7D8996', .7, .9)
        b.ln(f"M{cx-r+2.4:.1f} {cy-h+2:.1f} L{cx-r+2.4:.1f} {cy-2:.1f}", '#FFFFFF', 1.1, .8)
        b.e(round(cx, 1), round(cy - h, 1), round(r * .55, 1), round(r * .2, 1), '#FFFFFF', op=.5)
        b.r(round(cx - r, 1), round(cy - h * .55, 1), r * 2, 2, 'red', op=.85)

@icon('island', '岛礁', '设施')
def _(b):
    b.r(0, 40, 96, 50, 'water')
    b.ln("M2 82 Q8 80 14 82 T26 82 M64 84 Q70 82 76 84 T88 84", '#FFFFFF', .9, .45)
    b.e(48, 64, 44, 16, 'none', '#FFFFFF', 1.2, op=.5)
    b.p("M6 64 C6 54 24 48 46 48 C70 48 90 52 90 62 C90 72 72 78 48 78 C24 78 6 74 6 64 Z", 'sand', '#A88A50', 1)
    b.p("M12 62 C14 55 28 52 46 52 C64 52 82 55 84 61 C80 67 66 71 48 71 C30 71 16 68 12 62 Z", 'grass', '#5E7440', .8)
    b.p("M60 76 L64 76 L66 88 L62 88 Z", 'concT', CS, .8)
    b.e(66, 62, 9, 3.6, 'concT', CS, .8); b.e(66, 62, 6.2, 2.4, 'none', '#FFFFFF', .9)
    b.ln("M63.6 60.6 L63.6 63.4 M68.4 60.6 L68.4 63.4 M63.6 62 L68.4 62", '#3A4048', .9)
    x, y = 26, 64
    box(b, x, y, 18, 12, 10)
    wins(b, [(x + 2.4 + i * 5.2, y - 9) for i in range(3)], 3, 3.4)
    vcyl(b, 40, 52 - 2, 3.4, 4, 'cylM', 'metal', MS)
    b.c(40, 42, 7.2, 'sphere', MS, .9); b.e(37.4, 39.2, 2.6, 1.6, '#FFFFFF', op=.8)
    b.p("M76 60 L77.4 34 L80.6 34 L82 60 Z", 'white', WS, .9)
    b.p("M76.6 50 L81.4 50 L81.6 54 L76.4 54 Z", 'red'); b.p("M77.2 40 L80.8 40 L81 44 L77 44 Z", 'red')
    b.r(76.4, 30, 5.2, 4, 'glass', '#25578F', rx=.6, sw=.6); b.p("M76 30 L79 26 L82 30 Z", 'red', '#7A2219', .6)
    tree(b, 16, 62, 3.2); tree(b, 54, 57, 3); tree(b, 20, 69, 2.6)


KEYS = """tanker ew_aircraft recon_aircraft transport_heli uav_heli hale_uav swarm target_drone airship hypersonic interceptor
amphibious supply_ship landing_craft minesweeper usv_mother glider torpedo mine research_vessel
recon_vehicle command_vehicle comm_vehicle engineering fuel_truck ambulance cuas laser_weapon hpm mortar spaa ugv_tracked eod_robot
airbase port barracks depot launch_site radar_station command_center power_station fuel_depot island""".split()

if __name__ == '__main__':
    import re as _re, os
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    assert set(byk) == set(KEYS), set(KEYS) ^ set(byk)
    assert len(KEYS) == len(set(KEYS))
    base = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons.js'), encoding='utf-8').read()
    old = set(_re.findall(r"key: '([^']+)'", base))
    clash = old & set(KEYS)
    assert not clash, clash
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
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons_a.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), 'largest', sorted(SZ)[-6:])
