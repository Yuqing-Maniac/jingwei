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


# ======================================================================
# icons_gen_f.py — batch f: 反无人 defeat / interception devices
# ======================================================================
CAT = '反无人'
NETC = '#6F86A3'
GR.update({
    'fea': L(V, (0, '#B59468'), (.5, '#7A5634'), (1, '#432C18')),
    'feaL': L(V, (0, '#F4EBDA'), (1, '#C2A47A')),
    'beam': ('r', None, ((0, '#FFFFFF'), (.35, '#FFB1A6', .9), (1, '#FF4A3A', 0))),
})

def drone(b, cx, cy, s=1.0, op=None, ghost=False):
    o = f" opacity='{op}'" if op is not None else ''
    b.o.append(f"<g transform='translate({cx} {cy}) scale({s})'{o}>")
    b.ln("M-8 -3 L-3 0 M8 -3 L3 0 M-7 3 L-3 1 M7 3 L3 1", '#2E3640', 1.3)
    for x, y in ((-8, -3.6), (8, -3.6), (-7.2, 3.6), (7.2, 3.6)):
        b.e(x, y, 4.3, 1.2, 'prop', '#8D9BAC', .4)
    b.r(-3.6, -2.2, 7.2, 4.4, 'dkm', DS, rx=1.7, sw=.6)
    b.c(0, 2.6, 1.2, 'lens')
    b.e(-1.2, -1, 1.6, .6, '#FFFFFF', op=.6)
    b.eg()

def zig(b, pts, col=WAVE, w=1.5, op=None):
    b.ln('M' + ' L'.join(f"{x} {y}" for x, y in pts), col, w, op)

def mesh(b, P, nu, nv, col=NETC, w=.8, op=.95, fill=True):
    p00, p10, p11, p01 = P
    def f(u, v):
        x = (1-u)*(1-v)*p00[0] + u*(1-v)*p10[0] + u*v*p11[0] + (1-u)*v*p01[0]
        y = (1-u)*(1-v)*p00[1] + u*(1-v)*p10[1] + u*v*p11[1] + (1-u)*v*p01[1]
        return f"{x:.1f} {y:.1f}"
    if fill:
        poly(b, [p00, p10, p11, p01], '#FFFFFF', None, 1, .28)
    d = ''
    for i in range(nu + 1): d += f"M{f(i/nu,0)} L{f(i/nu,1)} "
    for j in range(nv + 1): d += f"M{f(0,j/nv)} L{f(1,j/nv)} "
    b.ln(d, col, w, op)
    b.ln(f"M{f(0,0)} L{f(1,0)} L{f(1,1)} L{f(0,1)} Z", col, w + .5, op)

def whip(b, x1, y1, x2, y2, col='#2A2E33', w=1.6):
    b.ln(f"M{x1} {y1} L{x2} {y2}", col, w)
    b.c(x2, y2, 1.7, 'metal3', '#2A2E33', .6)

def burst(b, x, y, r=6):
    b.c(x, y, r, 'spark')
    b.ln(f"M{x-r*.9:.1f} {y-r*.9:.1f} L{x+r*.9:.1f} {y+r*.9:.1f} M{x+r*.9:.1f} {y-r*.9:.1f} L{x-r*.9:.1f} {y+r*.9:.1f}", '#FFFFFF', 1, .85)

def brackets(b, x, y, r, col=REDL, w=1.2):
    k = r * .45
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.ln(f"M{x+sx*r:.1f} {y+sy*(r-k):.1f} L{x+sx*r:.1f} {y+sy*r:.1f} L{x+sx*(r-k):.1f} {y+sy*r:.1f}", col, w)

# ============ 1 手持干扰枪 ============
@icon('cuas_jammer_gun', '手持干扰枪', CAT)
def _(b):
    b.g('translate(-3 9) rotate(-14 48 50)')
    b.drop("M5 40 L86 33 L86 59 L60 59 L38 70 L20 54 Z", 2, 3, .14)
    b.p("M22 44 L8 40 Q4 40 5 45 L7 56 Q8 60 12 58 L22 53 Z", 'dkm2', DS)
    b.r(5, 41, 3.6, 17, 'dkm', DS, rx=1.5, sw=.7)
    b.p("M30 53 L39 53 L36 71 L28 71 Q26 71 27 68 Z", 'dkm2', DS)
    b.ln("M40 54 Q42 60 46 60 L50 54", '#262C33', 1.2)
    b.r(18, 41, 42, 13, 'dkm', DS, rx=3)
    b.r(22, 37.5, 28, 4, 'metal3', MS, rx=1.2, sw=.9)
    b.r(34, 54, 11, 8, 'landdk', LS, rx=1.5, sw=.9)
    b.r(24, 44, 11, 6, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.ln("M25.5 47.5 L27.5 45.5 L29 48.5 L31 45 L33 47", AMBER, .8)
    leds(b, [(40, 47, GREEN), (45, 47, AMBER)])
    # antenna head
    b.r(58, 31, 18, 29, 'metal2', MS, rx=2)
    for i in range(4): b.ln(f"M{60.5+i*4} 33 L{60.5+i*4} 58", '#6A7685', 1)
    b.r(61, 35, 12, 21, 'array', '#1E3550', rx=1, sw=.7, op=.9)
    b.p("M76 36 L88 29 L88 62 L76 55 Z", 'metal3', MS)
    b.p("M78 38 L86 33.5 L86 57.5 L78 53 Z", 'dkm2', None)
    b.hl("M59 32.4 L75 32.4", .9, .8)
    for x, t, dx in ((26, 16, -3), (37, 10, 0), (48, 15, 3)):
        b.r(x - 2, 37, 4, 3, 'metal3', rx=.8, sw=.5)
        whip(b, x, 37, x + dx, t)
    b.eg()
    zig(b, [(86, 34), (88, 27), (86.5, 31), (91, 22), (89.5, 27)], WAVE, 1.6)
    b.ln("M83 22 Q93 22 93 34", WAVE, 1.2, .6)
    drone(b, 80, 11, .8)

# ============ 2 背负式干扰器 ============
@icon('cuas_jammer_backpack', '背负式干扰器', CAT)
def _(b):
    b.sh(40, 86, 24, 3.2)
    b.drop("M26 28 L56 28 Q62 28 62 34 L62 72 Q62 78 56 78 L32 78 Q26 78 26 72 Z", 2, 3, .16)
    b.r(26, 26, 36, 14, 'land', LS, rx=6)
    b.r(26, 34, 36, 44, 'canvas', LS, rx=6)
    b.ln("M28 40 L60 40", '#3E4C29', 1, .7)
    b.ln("M27 70 L61 70", '#3E4C29', 1, .6)
    b.r(36, 52, 22, 20, 'dkm', DS, rx=2)
    b.r(38.5, 54.5, 11, 7, 'scr', '#0B1A2C', rx=1, sw=.6)
    zig(b, [(40, 59), (42, 56.4), (44, 60.5), (46, 56), (48, 59)], AMBER, .8)
    leds(b, [(53, 56, GREEN), (53, 60, AMBER), (53, 64, REDL)])
    b.c(43, 67, 2, 'hub', '#1D2228', .6); b.c(51, 67, 2, 'hub', '#1D2228', .6)
    b.r(28, 56, 5, 14, 'landdk', LS, rx=1.5, sw=.8)
    b.ln("M30 28 Q14 34 16 56 Q17 70 30 76", '#262C33', 4.4)
    b.ln("M30 28 Q14 34 16 56 Q17 70 30 76", '#5A6370', 1.6)
    b.ln("M24 56 L36 56", '#262C33', 2.4)
    b.r(44, 22, 5, 5, 'metal3', MS, rx=1, sw=.6)
    b.r(32, 22, 5, 5, 'metal3', MS, rx=1, sw=.6)
    whip(b, 46.5, 22, 49, 3, w=1.8)
    whip(b, 34.5, 22, 30, 9, w=1.6)
    b.hl("M30 27.6 L58 27.6", .9, .8)
    wav(b, 56, 40, (14, 22, 30), -72, -8, WAVE, 1.8)
    drone(b, 84, 13, .85)

# ============ 3 全向干扰站 ============
@icon('cuas_jammer_omni', '全向干扰站', CAT)
def _(b):
    b.sh(48, 86, 34, 3.4)
    b.e(48, 38, 36, 9, 'none', WAVE, 1.4, op=.45)
    b.e(48, 38, 24, 6, 'none', WAVE, 1.8, op=.8)
    b.e(48, 38, 13, 3.2, 'none', WAVE, 2, op=.95)
    # tripod + cabinet
    b.ln("M48 62 L26 86 M48 62 L70 86 M48 62 L48 88", '#3A424B', 3.2)
    b.ln("M48 62 L26 86 M48 62 L70 86", '#8794A3', 1)
    b.r(34, 60, 28, 14, 'metal', MS, rx=2)
    for i in range(4): b.ln(f"M{38+i*5} 63.5 L{38+i*5} 70.5", '#8794A3', 1.1)
    leds(b, [(58, 64, GREEN), (58, 69, AMBER)])
    # mast
    b.r(46.2, 22, 3.6, 40, 'cylM', MS, sw=.8)
    b.ln("M40 50 L48 44 L56 50", '#5A6370', 1)
    for y in (32, 46):
        b.ln(f"M32 {y} L64 {y}", '#2A2E33', 1.6)
        b.c(32, y, 1.7, 'metal3', '#2A2E33', .6); b.c(64, y, 1.7, 'metal3', '#2A2E33', .6)
    b.r(41, 20, 14, 5, 'metal3', MS, rx=1.6)
    for x, y2, x2 in ((43, 12, 34), (46, 8, 41), (50, 8, 55), (53, 12, 62)):
        whip(b, x, 21, x2, y2, w=1.6) if False else None
    b.ln("M43 21 L33 9 M46 21 L41 4 M50 21 L55 4 M53 21 L63 9", '#2A2E33', 1.6)
    for x, y in ((33, 9), (41, 4), (55, 4), (63, 9)): b.c(x, y, 1.7, 'metal3', '#2A2E33', .6)
    b.hl("M47.2 24 L47.2 58", .8, .7)
    drone(b, 84, 20, .75); drone(b, 12, 18, .6)

# ============ 4 定向干扰器 ============
@icon('cuas_jammer_directional', '定向干扰器', CAT)
def _(b):
    b.sh(46, 88, 28, 3)
    b.ln("M44 62 L22 86 M44 62 L68 86 M44 62 L44 88", '#3A424B', 3.4)
    b.ln("M44 62 L22 86 M44 62 L68 86", '#8794A3', 1)
    b.r(37, 54, 14, 10, 'dkm', DS, rx=2)
    leds(b, [(41, 59, GREEN), (46, 59, AMBER)])
    b.p("M31 36 L35 36 L38 52 L50 52 L53 36 L57 36 L54 56 L34 56 Z", 'metal3', MS, .9)
    b.g('rotate(-33 44 42)')
    b.r(8, 40.4, 74, 3.6, 'metal3', MS, rx=1.2, sw=.8)
    for x, ln_ in ((13, 28), (23, 22), (35, 19), (47, 16.5), (59, 14), (71, 11)):
        y1, y2 = 42.2 - ln_ / 2, 42.2 + ln_ / 2
        b.ln(f"M{x} {y1} L{x} {y2}", '#3E4752', 3.2)
        b.ln(f"M{x} {y1} L{x} {y2}", '#F1F4F7', 1.5)
    b.r(30, 37.5, 18, 9, 'dkm', DS, rx=2, sw=.8)
    b.c(39, 42, 2, 'lens', None)
    b.hl("M9 41.2 L81 41.2", .8, .8)
    b.eg()
    wav(b, 80, 25, (7, 14, 21), -72, -8, WAVE, 2.2, .95)
    drone(b, 87, 7, .7)

# ============ 5 导航诱骗设备 ============
@icon('cuas_spoofer', '导航诱骗设备', CAT)
def _(b):
    b.sh(32, 86, 30, 3.2)
    # satellite
    b.g('rotate(-22 20 20)')
    b.r(5, 15, 12, 9, 'solar', '#18365C', sw=.8); b.r(25, 15, 12, 9, 'solar', '#18365C', sw=.8)
    b.ln("M5 19.5 L17 19.5 M25 19.5 L37 19.5 M9 15 L9 24 M13 15 L13 24 M29 15 L29 24 M33 15 L33 24", '#9CC2EA', .5, .7)
    b.r(17, 14, 8, 11, 'gold', '#6E5418', rx=1.2, sw=.8)
    b.p("M19.5 25 L22.5 25 L21 30 Z", 'metal3', MS, .6)
    b.hl("M18 15.3 L24 15.3", .8, .9)
    b.eg()
    b.ln("M24 31 L72 46", '#5FA2E4', 1.1, .8, extra="stroke-dasharray='2.6 2.4'")
    # device
    b.r(10, 60, 48, 20, 'dkm', DS, rx=3)
    b.r(14, 63, 20, 12, 'scr', '#0B1A2C', rx=1.2, sw=.6)
    b.p("M16 72 L21 66 L25 70 L31 65 L31 73 L16 73 Z", '#2F8F5A', op=.7)
    b.c(26, 68, 1.8, REDL, '#FFFFFF', .5)
    leds(b, [(41, 66, GREEN), (46, 66, AMBER), (51, 66, REDL)])
    b.ln("M39 72 L52 72", '#262C33', 1.4)
    b.r(32, 56, 3, 5, 'metal3', MS, sw=.5)
    b.e(33.5, 55.5, 10, 3, 'metal', MS, .9)
    b.e(33.5, 54.8, 5.6, 1.4, 'array', None, op=.9)
    b.hl("M12 61.2 L56 61.2", .8, .7)
    wav(b, 40, 52, (12, 20, 28), -68, -22, WAVE, 2.2, .95)
    # drone true / spoofed
    drone(b, 80, 40, 1.15)
    b.ln("M84 48 Q92 56 86 64", WAVE, 1.3, .9, extra="stroke-dasharray='2.2 2'")
    b.p("M83.6 62 L87 66.6 L88.6 61 Z", WAVE)
    drone(b, 74, 72, .95, op=.4)
    b.p("M71 80 Q74 76 77 80 L74 86 Z", REDL, '#7A2219', .6)

# ============ 6 协议破解接管设备 ============
@icon('cuas_takeover', '协议破解接管设备', CAT)
def _(b):
    b.sh(32, 86, 28, 3)
    # laptop
    b.p("M8 76 L16 68 L52 68 L46 76 Z", 'metal', MS)
    b.ln("M18 70.5 L48 70.5 M16 73 L44 73", '#8794A3', 1, .7)
    b.p("M6 76 L46 76 L46 79.5 L6 79.5 Z", 'metal2', MS, .9)
    b.p("M12 42 L50 42 L52 68 L16 68 Z", 'dkm', DS)
    b.p("M15 44.5 L48 44.5 L49.6 65.5 L18 65.5 Z", 'scr', '#0B1A2C', .6)
    b.ln("M19 49 L30 49 M19 53 L38 53 M19 57 L27 57 M19 61 L34 61", '#43C46B', 1.1, .9)
    b.p("M38 56 L46 56 L46 62 L38 62 Z", '#243F5E', op=.6)
    b.c(42, 59, 2.2, 'none', AMBER, .9)
    b.ln("M42 56.8 L42 61.2 M39.8 59 L44.2 59", AMBER, .7)
    b.hl("M13 43 L49 43", .8, .6)
    # link + padlock
    b.ln("M50 48 Q58 40 64 30", WAVE, 1.6, .95, extra="stroke-dasharray='3 2.4'")
    b.r(52, 40, 12, 10, 'gold', '#6E5418', rx=1.8, sw=.8)
    b.ln("M54.4 40 L54.4 36 Q54.4 32 58.2 32 Q62 32 62 35", '#8A6A20', 2)
    b.ln("M54.4 40 L54.4 36 Q54.4 32 58.2 32 Q62 32 62 35", '#E9D08A', .8)
    b.c(58, 44, 1.5, '#5A4210'); b.ln("M58 44 L58 47", '#5A4210', 1.2)
    b.hl("M53.4 41.4 L62.6 41.4", .8, .8)
    # drone under control
    drone(b, 76, 20, 1.6)
    brackets(b, 76, 21, 17, WAVE, 1.4)
    b.ln("M62 10 L90 10", WAVE, .0)
    for x, y in ((90, 38), (64, 6)):
        pass

# ============ 7 激光拦截车 ============
@icon('cuas_laser_vehicle', '激光拦截车', CAT)
def _(b):
    _truck_base(b, (14, 28, 42, 77), cab_x=66, cab_top=44, chassis=(6, 60, 84))
    b.r(8, 40, 54, 21, 'land', LS, rx=2)
    for x in (18, 30, 42, 54): b.ln(f"M{x} 41.5 L{x} 59.5", '#3E4C29', .9, .6)
    b.r(12, 46, 12, 10, 'landdk', LS, rx=1, sw=.7)
    b.ln("M6 62 L2 70 M62 62 L66 70", '#3A424B', 2.4)
    b.hl("M9 41.4 L60 41.4", .9, .7)
    # turret
    b.r(24, 34, 22, 6, 'dkm', DS, rx=2)
    b.c(35, 27, 10, 'sphere', MS, 1)
    b.p("M26 22 Q35 14 44 22 Q35 20 26 22 Z", '#FFFFFF', op=.35)
    b.g('rotate(-20 40 24)')
    b.ln("M44 24 L96 24", LASER, 7, .18)
    b.ln("M44 24 L96 24", LASER, 3, .75)
    b.ln("M44 24 L96 24", '#FFFFFF', 1.1, .95)
    b.r(36, 18, 8, 12, 'dkm2', DS, rx=2, sw=.8)
    b.e(44.6, 24, 2, 4.6, 'lens', '#05101C', .5)
    b.eg()
    drone(b, 84, 9, .8)
    burst(b, 84, 9, 5)

# ============ 8 高功率微波车 ============
@icon('cuas_hpm_vehicle', '高功率微波车', CAT)
def _(b):
    _truck_base(b, (14, 28, 42, 77), cab_x=66, cab_top=44, chassis=(6, 60, 84))
    b.r(8, 44, 54, 17, 'land', LS, rx=2)
    for x in (16, 26, 36): b.r(x, 47, 6, 11, 'cylT', DS, rx=2, sw=.7)
    b.r(46, 47, 12, 11, 'landdk', LS, rx=1, sw=.7)
    for i in range(4): b.ln(f"M{48+i*2.6} 49 L{48+i*2.6} 56", '#2E3A1C', .9)
    b.ln("M6 62 L2 70 M62 62 L66 70", '#3A424B', 2.4)
    b.hl("M9 45.4 L60 45.4", .9, .7)
    b.p("M28 44 L34 44 L38 36 L26 36 Z", 'metal3', MS, .9)
    b.g('rotate(-42 33 36)')
    b.p("M14 30 L46 19 L46 53 L14 42 Z", 'metal', MS)
    b.p("M46 19 L52 21 L52 51 L46 53 Z", 'dkm2', DS)
    b.p("M47.4 21.4 L50.4 22.4 L50.4 49.6 L47.4 50.6 Z", 'gold', None, op=.9)
    b.ln("M48.8 22 L48.8 50", '#6E5418', .6)
    b.ln("M14 36 L46 36", '#98A4B1', .8)
    b.hl("M15 30.8 L45 20.6", 1, .8)
    b.p("M14 30 L8 33 L8 39 L14 42 Z", 'metal3', MS, .9)
    b.eg()
    wav(b, 52, 28, (10, 18, 26, 34), -74, -8, WAVE, 2.2, .95)
    drone(b, 86, 10, .8)

# ============ 9 捕网枪 ============
@icon('cuas_net_gun', '捕网发射器', CAT)
def _(b):
    b.g('translate(-2 8)')
    b.drop("M4 42 L62 38 L66 58 L40 60 L36 72 L24 72 L24 58 L8 62 Z", 2, 3, .14)
    # tethers + net
    P = [(74, 24), (94, 30), (92, 62), (72, 66)]
    for x, y in P: b.ln(f"M66 49 L{x} {y}", NETC, .9, .8)
    mesh(b, P, 5, 5)
    drone(b, 83, 46, 1.0, op=.95)
    mesh(b, [(76, 38), (90, 40), (89, 54), (75, 55)], 2, 2, fill=False, op=.5)
    for x, y in P: b.c(x, y, 2.3, 'dkm', DS, .7)
    # gun
    b.p("M24 42 L8 39 Q4 39 5 44 L8 58 Q9 61 13 59 L24 54 Z", 'dkm2', DS)
    b.r(5, 40, 3.6, 17, 'dkm', DS, rx=1.5, sw=.7)
    b.r(20, 40, 24, 15, 'dkm', DS, rx=3)
    b.p("M32 55 L42 55 L39 72 L30 72 Q28 72 29 69 Z", 'dkm2', DS)
    b.ln("M44 56 Q46 62 50 62 L53 56", '#262C33', 1.2)
    b.r(42, 36, 22, 24, 'metal2', MS, rx=3)
    b.r(44, 38, 16, 20, 'metal', None, rx=2, op=.6)
    b.r(55, 33, 5, 28, 'metal3', MS, rx=2, sw=.8)
    b.e(63.5, 48, 3.8, 10.5, 'dkm2', DS, .9)
    b.e(63.5, 48, 2, 7, '#05080B')
    b.r(28, 33, 12, 4, 'metal3', MS, rx=1.2, sw=.8)
    b.r(24, 43, 10, 5, 'landdk', LS, rx=1, sw=.7)
    leds(b, [(38, 45.5, GREEN)])
    b.hl("M22 40.8 L42 40.8", .9, .8); b.hl("M44 37.4 L58 37.4", .9, .8)
    b.eg()

# ============ 10 网捕无人机 ============
@icon('cuas_net_drone', '网捕无人机', CAT)
def _(b):
    b.ln("M34 20 L16 12 M62 20 L80 12", '#4A5664', 5)
    b.ln("M34 20 L16 12 M62 20 L80 12", '#AEB9C5', 2.6)
    for x, y, rx in ((14, 8, 11), (82, 8, 11), (24, 20, 9), (72, 20, 9)):
        pass
    b.e(14, 9, 11, 3, 'prop', '#8D9BAC', .5); b.e(82, 9, 11, 3, 'prop', '#8D9BAC', .5)
    b.c(14, 11, 2, 'hub', '#1D2228', .6); b.c(82, 11, 2, 'hub', '#1D2228', .6)
    # tethers + net
    P = [(8, 78), (88, 78), (68, 34), (28, 34)]
    for (x, y), (x2, y2) in zip(((28, 34), (68, 34), (14, 12), (82, 12)), ((8, 78), (88, 78), (28, 34), (68, 34))):
        pass
    b.ln("M30 24 L22 40 M66 24 L74 40", NETC, .9, .9)
    mesh(b, P, 8, 6)
    # body
    b.r(32, 14, 32, 14, 'air', AS, rx=5)
    b.r(38, 17, 20, 6, 'canopy', '#1B2D40', rx=2.6, sw=.7)
    glint(b, 43, 18.6, 2.4, .8)
    b.c(48, 28, 2.4, 'lens', '#1B2D40', .6)
    b.e(22, 21, 9, 2.6, 'prop', '#8D9BAC', .5); b.e(74, 21, 9, 2.6, 'prop', '#8D9BAC', .5)
    b.ln("M34 20 L24 20.5 M62 20 L72 20.5", '#4A5664', 3)
    # caught drone
    drone(b, 49, 56, 1.8)
    mesh(b, [(30, 44), (68, 44), (64, 66), (34, 66)], 4, 3, fill=False, op=.55)
    for x, y in P[:2]: b.c(x, y, 3, 'dkm', DS, .7)
    b.c(28, 34, 1.8, 'metal3', MS, .6); b.c(68, 34, 1.8, 'metal3', MS, .6)

# ============ 11 拦截无人机 ============
@icon('cuas_interceptor_drone', '拦截无人机', CAT)
def _(b):
    b.ln("M2 86 L24 76 M0 76 L20 68 M8 92 L28 84", WAVE, 1.6, .75)
    b.g('rotate(-32 44 54)')
    b.drop("M26 44 L66 44 L66 56 L26 56 Z", 2, 3, .12)
    # rear rotors (far side, lighter)
    b.ln("M32 46 L26 36 M62 46 L56 36", '#4A5664', 3)
    b.e(26, 33, 13, 3.4, 'prop', '#8D9BAC', .5, op=.75); b.e(56, 33, 13, 3.4, 'prop', '#8D9BAC', .5, op=.75)
    b.c(26, 34.5, 1.6, 'hub', '#1D2228', .5); b.c(56, 34.5, 1.6, 'hub', '#1D2228', .5)
    # body
    b.r(24, 42, 42, 12, 'dkm', DS, rx=4)
    b.r(32, 38, 22, 5, 'airdk', AS, rx=2)
    b.hl("M27 43.4 L62 43.4", .9, .7)
    b.ln("M30 56 L24 64 M60 56 L54 64", '#4A5664', 3)
    b.e(24, 66, 12, 3, 'prop', '#8D9BAC', .5); b.e(54, 66, 12, 3, 'prop', '#8D9BAC', .5)
    b.c(24, 65, 1.6, 'hub', '#1D2228', .5); b.c(54, 65, 1.6, 'hub', '#1D2228', .5)
    # warhead nose
    b.p("M66 43 L82 48 L66 53 Z", 'white', WS, .8)
    b.p("M76 45.6 L84 48 L76 50.4 Z", 'red')
    b.p("M66 43 L70 44.2 L70 51.8 L66 53 Z", 'gold', '#6E5418', .5)
    b.c(60, 48, 2.2, 'lens', '#05101C', .5)
    b.eg()
    burst(b, 78, 22, 6)
    drone(b, 86, 14, .8)

# ============ 12 小口径近防炮 ============
@icon('cuas_gun', '小口径近防炮', CAT)
def _(b):
    b.sh(40, 86, 30, 3.6)
    b.p("M20 84 L26 70 L58 70 L64 84 Z", 'landdk', LS)
    b.r(18, 82, 48, 4, 'dkm', DS, rx=1.5, sw=.8)
    b.r(24, 66, 36, 6, 'dkm', DS, rx=2)
    # ammo drum
    b.r(12, 48, 14, 16, 'landdk', LS, rx=3)
    b.ln("M14 52 L24 52 M14 56 L24 56 M14 60 L24 60", '#2E3A1C', .8, .8)
    # housing
    b.r(24, 40, 34, 26, 'land', LS, rx=4)
    b.p("M30 40 L34 33 L52 33 L56 40 Z", 'landdk', LS)
    b.hl("M27 41.4 L55 41.4", .9, .7)
    b.r(30, 48, 10, 8, 'landdk', LS, rx=1, sw=.7)
    # radome + eo
    b.c(38, 27, 8, 'sphere', MS, .9)
    b.e(35, 23.5, 3, 1.5, '#FFFFFF', op=.8)
    b.r(47, 28, 8, 7, 'dkm', DS, rx=1.5, sw=.8); b.c(52, 31.5, 2.3, 'lens', None)
    # barrels
    b.g('rotate(-22 52 52)')
    b.r(54, 44, 12, 15, 'dkm', DS, rx=2)
    b.r(66, 45, 20, 13, 'metal3', MS, rx=2, sw=.9)
    b.ln("M66 48.5 L86 48.5 M66 51.5 L86 51.5 M66 54.5 L86 54.5", '#2A2E33', 1.2)
    b.hl("M67 46 L85 46", .9, .8)
    b.r(83, 43.5, 5, 16, 'dkm2', DS, rx=1.5, sw=.8)
    for y in (46.5, 51.5, 56.5): b.c(88.2, y, 1.1, '#05080B')
    b.eg()
    b.ln("M80 36 L86 29 M84 40 L91 32", AMBER, 1.6, .95, extra="stroke-dasharray='3 2.4'")
    b.ln("M80 36 L86 29", '#FFFFFF', .6, .8)
    drone(b, 86, 14, .75)

# ============ 13 可编程空爆弹 ============
@icon('cuas_programmable_ammo', '可编程空爆弹', CAT)
def _(b):
    b.g('rotate(-22 34 70)')
    b.r(6, 61, 30, 17, 'yellow', '#8A6A20', rx=2)
    b.ln("M12 62.4 L12 76.6 M30 62.4 L30 76.6", '#B88A10', 1, .8)
    b.r(3, 60, 4.4, 19, 'gold', '#6E5418', rx=1.4, sw=.8)
    b.c(4.6, 69.5, 1.5, '#8A6A20')
    b.hl("M8 63 L34 63", .9, .85)
    b.p("M36 62 L56 62 C66 62 72 65.5 78 69.5 C72 73.5 66 77 56 77 L36 77 Z", 'metal', MS)
    b.r(35, 60.5, 3.4, 18, 'gold', '#6E5418', rx=1, sw=.7)
    b.p("M40 64.4 L58 64.4 L58 74.6 L40 74.6 Z", '#23303E', '#0B1A2C', .5)
    for i in range(4):
        for j in range(3): b.c(43 + i * 4.2, 67 + j * 3.2, 1.3, 'metal3', None)
    b.r(60.4, 66, 7, 7, 'node', '#1F4F8C', rx=1.2, sw=.6)
    b.ln("M62 67.5 L66 67.5 M62 70 L66 70", '#FFFFFF', .6, .8)
    b.p("M68 64 C72 65 75 67 78 69.5 C75 72 72 74 68 75 Z", 'glass', '#25578F', .7)
    b.hl("M38 63.2 L60 63.2", .9, .8)
    b.eg()
    # airburst
    b.c(66, 33, 12, 'heat')
    b.c(66, 33, 4, 'spark')
    for a in range(0, 360, 45):
        r = math.radians(a)
        b.ln(f"M{66+5*math.cos(r):.1f} {33+5*math.sin(r):.1f} L{66+10*math.cos(r):.1f} {33+10*math.sin(r):.1f}", WAVE, 1.4, .9)
    for x, y in ((74, 24), (78, 30), (79, 18), (72, 15), (82, 25), (76, 11)):
        b.c(x, y, 1.5, 'dkm', DS, .4)
    b.ln("M70 27 L82 16", WAVE, 1, .6, extra="stroke-dasharray='2 2'")
    b.ln("M42 56 Q52 50 58 42", WAVE, 1.2, .8, extra="stroke-dasharray='2.4 2.4'")
    drone(b, 85, 14, .85)

# ============ 14 便携式防空导弹 ============
@icon('cuas_manpads', '便携式防空导弹', CAT)
def _(b):
    b.g('translate(4 2) rotate(-26 50 58)')
    b.drop("M4 48 L74 48 L74 62 L4 62 Z", 2, 3, .14)
    b.p("M10 47 L2 43 L2 66 L10 62 Z", 'landdk', LS)
    b.r(9, 47, 64, 15, 'land', LS, rx=5)
    b.ln("M24 48 L24 61 M58 48 L58 61", '#3E4C29', 1, .7)
    b.r(70, 45.5, 5, 18, 'landdk', LS, rx=1.5, sw=.8)
    b.p("M75 50 C84 51 88 54 92 55 C88 56 84 59 75 60 Z", 'white', WS, .8)
    b.p("M86 53.4 L93 55 L86 56.6 Z", 'red')
    b.p("M78 50.6 L80 50.8 L80 59.2 L78 59.4 Z", '#8F9BA9')
    b.p("M30 47 L33 39 L46 39 L48 47 Z", 'dkm', DS)
    b.r(35, 40.4, 7, 4, 'glass', '#25578F', rx=.8, sw=.5)
    b.p("M34 62 L42 62 L41 75 L33 75 Q31 75 32 72 Z", 'dkm2', DS)
    b.r(50, 62, 10, 8, 'metal', MS, rx=2, sw=.8)
    b.r(4, 45, 5, 18, 'dkm2', DS, rx=2, sw=.8)
    b.hl("M12 48.6 L70 48.6", 1, .75)
    b.eg()
    brackets(b, 84, 14, 11, REDL, 1.5)
    drone(b, 84, 14, .75)
    b.ln("M58 32 L74 20", REDL, 1, .7, extra="stroke-dasharray='2 2'")

# ============ 15 小型拦截弹发射架 ============
@icon('cuas_missile_launcher', '小型拦截弹发射架', CAT)
def _(b):
    b.sh(40, 88, 28, 3.2)
    b.ln("M34 62 L12 86 M34 62 L60 86 M34 62 L34 88", '#3A424B', 3.4)
    b.ln("M34 62 L12 86 M34 62 L60 86", '#8794A3', 1)
    b.r(26, 56, 16, 10, 'dkm', DS, rx=2)
    b.g('rotate(-48 34 54)')
    b.drop("M12 42 L66 42 L66 66 L12 66 Z", 2, 3, .12)
    b.r(12, 42, 54, 24, 'land', LS, rx=3)
    b.ln("M12 54 L66 54", '#3E4C29', 1)
    for x in (24, 40, 54): b.ln(f"M{x} 43 L{x} 65", '#3E4C29', .9, .6)
    b.hl("M14 43.4 L64 43.4", .9, .7)
    b.p("M66 40.5 L71 42.5 L71 65.5 L66 67.5 Z", 'metal3', MS, .9)
    b.p("M64 46 L76 48 L64 50 Z", 'white', WS, .6)
    b.p("M64 58 L76 60 L64 62 Z", 'white', WS, .6)
    b.eg()
    # missile in flight
    b.ln("M44 46 Q58 40 66 30", '#FFFFFF', 4.4, .55)
    b.ln("M44 46 Q58 40 66 30", '#C9D3DE', 2, .55)
    b.g('rotate(-46 70 26)')
    b.p("M60 23 L78 23 L84 26 L78 29 L60 29 Z", 'white', WS, .8)
    b.p("M78 23 L84 26 L78 29 Z", 'red')
    b.p("M60 23 L55 20 L60 26 Z M60 29 L55 32 L60 26 Z", 'red')
    b.p("M60 23.6 L53 26 L60 28.4 Z", 'flame')
    b.eg()
    drone(b, 86, 8, .7)

# ============ 16 遥控武器站 ============
@icon('cuas_rws', '遥控武器站', CAT)
def _(b):
    b.sh(44, 88, 38, 3.4)
    b.p("M4 84 L12 74 L78 74 L88 84 Z", 'landdk', LS)
    b.r(4, 82, 84, 3.4, 'land', LS, rx=1, sw=.8)
    b.e(40, 72, 18, 4.6, 'dkm', DS, .9)
    b.r(14, 52, 12, 14, 'landdk', LS, rx=2, sw=.9)
    b.ln("M15 56 L25 56 M15 60 L25 60", '#2E3A1C', .8)
    b.p("M26 70 L24 44 L48 44 L54 52 L56 70 Z", 'land', LS)
    b.p("M30 66 L29 50 L42 50 L46 56 L48 66 Z", 'landdk', LS, .8)
    b.hl("M25.6 45 L47 45", .9, .75)
    # gun
    b.r(54, 47, 14, 12, 'dkm', DS, rx=2)
    b.r(66, 51.2, 24, 4.2, 'dkm2', DS, rx=1.4, sw=.8)
    b.ln("M70 52 L88 52", '#6A7480', .7)
    b.r(87, 49.6, 6, 7.4, 'metal3', MS, rx=1.3, sw=.8)
    b.r(60, 59, 8, 6, 'landdk', LS, rx=1, sw=.7)
    # EO ball
    b.r(30, 34, 16, 11, 'dkm', DS, rx=3)
    b.c(38, 29, 8.4, 'dkm', DS, 1)
    b.c(40.4, 28.6, 5, 'lens', '#05101C', .7)
    b.e(38.6, 26.8, 1.7, .9, '#FFFFFF', op=.85)
    b.c(33, 33, 1.5, REDL)
    b.ln("M46 24 L74 12", '#5FA2E4', 1.1, .85, extra="stroke-dasharray='2.6 2.4'")
    brackets(b, 82, 9, 9, REDL, 1.2)
    drone(b, 82, 9, .62)

# ============ 17 防护网/拦阻网 ============
@icon('cuas_shield_net', '防护网', CAT)
def _(b):
    plate(b, 8, 72, 60, 20, 'grass', 5, 'soil')
    # back poles
    b.ln("M30 60 L30 22 M88 60 L88 22", '#5E6A78', 2.2)
    box(b, 30, 74, 24, 13, 9)
    wins(b, [(34 + i * 6.4, 63.5) for i in range(3)], 4, 4)
    b.r(46, 68, 5, 6, 'dkm', DS, rx=.5, sw=.5)
    gable_v  # keep helpers referenced
    mesh(b, [(14, 36), (70, 36), (88, 24), (32, 24)], 9, 4)
    b.ln("M14 36 L14 74 M70 36 L70 74", '#5E6A78', 2.4)
    for x, y in ((14, 36), (70, 36), (30, 22), (88, 22)): b.c(x, y, 2.2, 'metal', MS, .8)
    drone(b, 52, 10, .85)
    b.ln("M46 17 Q52 22 58 17", WAVE, 1.4, .9)
    b.ln("M42 15 Q52 25 62 15", WAVE, 1.1, .5)

# ============ 18 猛禽驯化拦截 ============
@icon('cuas_raptor', '猛禽驯化拦截', CAT)
def _(b):
    b.sh(48, 90, 26, 3)
    wing = ("M41 26 C31 17 18 11 3 14 L7 19 L3 23 L9 27 L5 32 L13 34 L11 40 C23 40 32 42 41 47 Z")
    for d in (wing, mirror(wing)): b.drop(d, 2, 3, .14)
    tail = "M42 54 L38 70 L44 67 L48 72 L52 67 L58 70 L54 54 Z"
    drone(b, 48, 79, 1.7)
    b.p(tail, 'fea', '#2A1A0E', .9)
    b.p(wing, 'fea', '#2A1A0E', 1)
    b.p(mirror(wing), 'fea', '#2A1A0E', 1)
    b.ln("M40 28 C30 24 20 22 8 21 M40 34 C30 31 22 30 11 31 M40 40 C32 38 24 38 13 37", '#2A1A0E', .8, .7)
    b.ln(mirror("M40 28 C30 24 20 22 8 21 M40 34 C30 31 22 30 11 31 M40 40 C32 38 24 38 13 37"), '#2A1A0E', .8, .7)
    b.hl("M40 26 C30 18 18 12 5 15", 1, .5)
    b.e(48, 42, 9.5, 17, 'fea', '#2A1A0E', 1)
    b.e(48, 46, 5.5, 11, 'feaL', None, op=.7)
    b.c(48, 20, 7.4, 'white', '#9A8A70', .9)
    b.p("M44.4 21.6 L51.6 21.6 L50.6 27.6 L48 30 L45.4 27.6 Z", 'yellow', '#8A6A20', .7)
    b.p("M46.2 26.6 L49.8 26.6 L48 30.4 Z", '#8A6A20')
    b.c(45, 18.6, 1.3, '#1A1208'); b.c(51, 18.6, 1.3, '#1A1208')
    b.ln("M43 16.4 L46.6 17.4 M53 16.4 L49.4 17.4", '#7A5634', 1)
    b.ln("M43 54 L41 66 M54 54 L56 66", '#E3B53A', 3.2)
    b.ln("M43 54 L41 66 M54 54 L56 66", '#FCE892', 1)
    b.ln("M38 67 Q41 72 44 67 M53 67 Q56 72 59 67", '#2A1A0E', 1.6)
    b.ln("M36 70 L40 70 M56 70 L60 70", '#2A1A0E', 1.4)

# ============ 19 诱饵/假目标 ============
def _decoy(b, cx, cy, s, ghost=False):
    st = "stroke='#8A97A8' stroke-width='1.6' stroke-dasharray='3 2.4' fill='#FFFFFF' fill-opacity='.3'"
    b.o.append(f"<g transform='translate({cx} {cy}) scale({s})'{" opacity='.55'" if ghost else ''}>")
    if ghost:
        b.o.append(f"<path d='M0 -22 C3 -22 4 -16 4 -8 L4 16 L8 22 L-8 22 L-4 16 L-4 -8 C-4 -16 -3 -22 0 -22 Z M-36 4 L-8 -8 L8 -8 L36 4 L36 8 L-36 8 Z' {st}/>")
    else:
        b.o.append("<path d='M-36 3 L-8 -8 L8 -8 L36 3 L36 8 L-36 8 Z' fill='#E59A45' stroke='#9A5414' stroke-width='1.2'/>")
        for x in (-32, -22, 14, 24):
            b.p(f"M{x} 8 L{x+4} 2.6 L{x+9} 2.6 L{x+6} 8 Z", 'white', None, op=.95)
        b.p("M0 -24 C4 -24 5 -17 5 -8 L5 18 L10 25 L-10 25 L-5 18 L-5 -8 C-5 -17 -4 -24 0 -24 Z", 'white', WS, 1)
        b.r(-5, 6, 10, 4, 'orange', None, op=.95)
        b.p("M-3 -22 C0 -25 3 -22 3 -22 L3 -16 L-3 -16 Z", 'orange', None)
        b.hl("M-33 4 L-8 -7 L8 -7 L33 4", .9, .8)
    b.eg()

@icon('cuas_decoy', '诱饵假目标', CAT)
def _(b):
    _decoy(b, 24, 26, .52, True)
    _decoy(b, 76, 22, .46, True)
    b.sh(48, 86, 28, 3)
    _decoy(b, 48, 52, 1.0)
    # corner reflector
    poly(b, [(48, 35), (58, 46), (48, 57), (38, 46)], 'metal', MS, 1)
    b.ln("M38 46 L58 46 M48 35 L48 57", '#6A7685', 1)
    b.p("M48 35 L58 46 L48 46 Z", '#FFFFFF', op=.45)
    wav(b, 48, 46, (24, 32, 40), 200, 340, WAVE, 1.8, .85)
    wav(b, 48, 46, (24, 32, 40), 20, 160, WAVE, 1.4, .5)

KEYS = """cuas_jammer_gun cuas_jammer_backpack cuas_jammer_omni cuas_jammer_directional cuas_spoofer cuas_takeover
cuas_laser_vehicle cuas_hpm_vehicle cuas_net_gun cuas_net_drone cuas_interceptor_drone cuas_gun cuas_programmable_ammo
cuas_manpads cuas_missile_launcher cuas_rws cuas_shield_net cuas_raptor cuas_decoy""".split()

if __name__ == '__main__':
    import re as _re, os
    HERE = os.path.dirname(os.path.abspath(__file__))
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    assert set(byk) == set(KEYS), set(KEYS) ^ set(byk)
    assert len(KEYS) == len(set(KEYS))
    old = set()
    import glob
    for f in glob.glob(os.path.join(HERE, 'icons*.js')):
        if os.path.basename(f) == 'icons_f.js': continue
        old |= set(_re.findall(r"key: '([^']+)'", open(f, encoding='utf-8').read()))
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
    open(os.path.join(HERE, 'icons_f.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(KEYS), 'largest', sorted(SZ)[-6:])
