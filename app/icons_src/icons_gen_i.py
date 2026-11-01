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


# ======================================================================
# icons_gen_i.py — batch i: 感知通信 (sensing & communication) additions
# Helpers above are copied verbatim from icons_gen_f.py (runs standalone).
# ======================================================================
CAT = '感知通信'
GR.update({
    'earth': ('r', ('0.35', '0.3', '0.8'), ((0, '#A6D8F7'), (.5, '#3F86D0'), (1, '#173F78'))),
    'deepw': L(('0', '0', '0', '1'), (0, '#8EC3EC', .6), (1, '#2E6AAA', .9)),
    'dishin': L(H, (0, '#8B97A6'), (.55, '#D9DFE6'), (1, '#F7F9FB')),
    'dishR': ('r', ('0.4', '0.35', '0.7'), ((0, '#F7F9FB'), (.6, '#C3CCD6'), (1, '#8794A3'))),
    'landT': L(D, (0, '#CBD9A6'), (1, '#9CB070')),
    'cylL': L(H, (0, '#6E8247'), (.3, '#B6C78B'), (.7, '#7F9559'), (1, '#3E4C29')),
    'seabed': L(V, (0, '#D3C293'), (1, '#8A7650')),
    'signal': ('r', None, ((0, '#E8F6FF', .9), (1, '#5FA2E4', 0))),
})
SIG = '#3D86D6'

def pad(b, cx, cy, rx, ry):
    b.e(cx, cy + 2, rx + 2, ry, 'shadow')
    b.e(cx, cy, rx, ry, 'grass', '#5E7440', .9)
    b.hl(f"M{cx-rx*.8:.1f} {cy-ry*.35:.1f} Q{cx-rx*.5:.1f} {cy-ry*.9:.1f} {cx-rx*.1:.1f} {cy-ry*.9:.1f}", .9, .6)

def sat(b, cx, cy, s=1.0, rot=0):
    b.o.append(f"<g transform='translate({cx} {cy}) rotate({rot}) scale({s})'>")
    b.r(-27, -5, 19, 10, 'solar', '#18365C', sw=.9); b.r(8, -5, 19, 10, 'solar', '#18365C', sw=.9)
    b.ln("M-21 -5 L-21 5 M-15 -5 L-15 5 M-27 0 L-8 0 M15 -5 L15 5 M21 -5 L21 5 M8 0 L27 0", '#9CC2EA', .5, .7)
    b.ln("M-8 0 L-5 0 M5 0 L8 0", '#5A6370', 1.6)
    b.ln("M0 -6 L0 -10", '#5A6370', 1.1)
    b.e(0, -11, 4, 1.7, 'metal', MS, .7)
    b.r(-5, -6.5, 10, 13, 'gold', '#6E5418', rx=1.6, sw=.9)
    b.hl("M-3.6 -5 L3.6 -5", .8, .9)
    b.eg()

def dish(b, cx, cy, r, ang=0, k=.32, feed=1.0):
    """parabolic dish seen obliquely, facing +x before rotation"""
    b.g(f'rotate({ang} {cx} {cy})')
    b.ln(f"M{cx-r*k:.1f} {cy} L{cx-r*k-6:.1f} {cy}", '#4B5867', 3.2)
    b.e(cx, cy, r * k, r, 'metal', MS, 1)
    b.e(cx + r * k * .1, cy, r * k * .8, r * .9, 'dishin', '#8794A3', .6)
    fx = cx + r * feed
    b.ln(f"M{cx+r*k*.4:.1f} {cy-r*.85:.1f} L{fx:.1f} {cy} M{cx+r*k*.4:.1f} {cy+r*.85:.1f} L{fx:.1f} {cy}", '#5A6370', 1.1)
    b.ln(f"M{cx} {cy} L{fx:.1f} {cy}", '#7A8795', 1.6)
    b.e(fx, cy, 2, 3.2, 'metal3', MS, .6)
    b.ln(f"M{cx-r*k*.7:.1f} {cy-r*.72:.1f} Q{cx} {cy-r*1.0:.1f} {cx+r*k*.7:.1f} {cy-r*.74:.1f}", '#FFFFFF', 1, .85)
    b.eg()

def drum(b, fx, cy, r, L_, d):
    """horizontal shrouded microwave dish; face at x=fx; d=-1 faces left, +1 right"""
    x0 = fx if d < 0 else fx - L_
    b.r(x0, cy - r, L_, 2 * r, 'cylM', MS, sw=1)
    b.e(fx, cy, r * .33, r, 'metal', MS, 1)
    b.e(fx, cy, r * .24, r * .84, 'dishin', '#8794A3', .6)
    b.c(fx + d * 1.2, cy, 1.6, 'metal3', MS, .5)
    b.ln(f"M{x0+2:.1f} {cy-r*.78:.1f} L{x0+L_-2:.1f} {cy-r*.78:.1f}", '#FFFFFF', .9, .8)

def lattice(b, x1, x2, ytop, ybot, wt, nseg, col='#56636F', w=1.2):
    """tapered lattice tower: half-width at top wt/2, bottom (x2-x1)/2, centred"""
    cx = (x1 + x2) / 2
    d = ''
    ys = [ytop + (ybot - ytop) * i / nseg for i in range(nseg + 1)]
    def hw(y): return wt / 2 + ((x2 - x1) / 2 - wt / 2) * (y - ytop) / (ybot - ytop)
    for i, y in enumerate(ys):
        d += f"M{cx-hw(y):.1f} {y:.1f} L{cx+hw(y):.1f} {y:.1f} "
        if i < nseg:
            y2 = ys[i + 1]
            if i % 2 == 0: d += f"M{cx-hw(y):.1f} {y:.1f} L{cx+hw(y2):.1f} {y2:.1f} "
            else: d += f"M{cx+hw(y):.1f} {y:.1f} L{cx-hw(y2):.1f} {y2:.1f} "
    b.ln(d, col, w * .8)
    b.ln(f"M{cx-wt/2:.1f} {ytop} L{x1} {ybot} M{cx+wt/2:.1f} {ytop} L{x2} {ybot}", '#3A4552', w * 1.9)
    b.ln(f"M{cx-wt/2:.1f} {ytop} L{x1} {ybot}", '#D6DCE3', .6, .8)

def pin(b, x, y, s=1.0):
    b.o.append(f"<g transform='translate({x} {y}) scale({s})'>")
    b.p("M0 0 C-7 -8 -7 -15 0 -15 C7 -15 7 -8 0 0 Z", 'red', '#7A2219', .8)
    b.c(0, -10.5, 2.4, '#FFFFFF')
    b.eg()

def ripple(b, cx, cy, rx, ry, col=WAVE, n=3, op=.8):
    for i in range(n):
        f = (i + 1) / n
        b.e(cx, cy, round(rx * f, 1), round(ry * f, 1), 'none', col, 1.4, op=round(op * (1 - i * .25), 2))

# ============ 1 合成孔径雷达 ============
@icon('sar_radar', '合成孔径雷达', CAT)
def _(b):
    G = lambda u, v: (6 + 60 * u + 24 * v, 88 - 22 * v)
    gp = [G(0, 0), G(1, 0), G(1, 1), G(0, 1)]
    b.e(50, 90, 44, 5, 'shadow')
    poly(b, gp, 'grass', '#5E7440', 1)
    b.ln("M7 87 L66 87", '#FFFFFF', .9, .6)
    # swath strip
    st = [G(.08, .25), G(.96, .25), G(.96, .85), G(.08, .85)]
    poly(b, st, 'orange', '#8A4E17', .9, .6)
    for i in range(1, 8):
        u = .08 + .88 * i / 8
        b.ln(f"M{G(u,.25)[0]:.1f} {G(u,.25)[1]:.1f} L{G(u,.85)[0]:.1f} {G(u,.85)[1]:.1f}", '#FFFFFF', .6, .55)
    # beam wedge
    ax, ay = 34, 31
    a, c2 = G(.38, .25), G(.38, .85)
    b.p(f"M{ax} {ay} L{a[0]:.1f} {a[1]:.1f} L{c2[0]:.1f} {c2[1]:.1f} Z", WAVE, None, op=.28)
    b.ln(f"M{ax} {ay} L{a[0]:.1f} {a[1]:.1f} M{ax} {ay} L{c2[0]:.1f} {c2[1]:.1f}", WAVE, 1.2, .9, extra="stroke-dasharray='3 2'")
    # aircraft (side view, heading right)
    b.p("M10 22 L6 8 L15 8 L24 18 Z", 'airdk', AS, 1)
    b.p("M34 22 L46 21 L40 31 L33 31 Z", 'airdk', AS, 1)
    b.p("M8 21 C10 16 22 14 40 15 L58 18 C64 19 64 24 58 25 L22 26 C13 26 8 25 8 21 Z", 'air', AS)
    b.p("M52 17.4 L58 18.6 C60 19.4 60 21 58 21.8 L52 21.6 Z", 'canopy', '#1B2D40', .6)
    b.r(26, 26, 18, 5, 'dkm', DS, rx=1.6, sw=.8)
    b.ln("M29 28.5 L41 28.5", '#43C46B', .9)
    b.hl("M14 18.5 C22 16.5 36 16 50 17.6", .9, .8)
    b.ln("M2 14 L8 14 M0 19 L6 19", '#FFFFFF', 1.2, .8)
    sat(b, 80, 14, .5, -12)
    b.ln("M80 20 Q74 31 56 40", SIG, 1.1, .8, extra="stroke-dasharray='2.4 2.2'")

# ============ 2 超视距雷达 ============
@icon('otH_radar', '超视距雷达', CAT)
def _(b):
    pad(b, 48, 80, 46, 10)
    # back pylons + curtain
    for x in (10, 76):
        b.ln(f"M{x} 14 L{x} 70", '#3A4552', 3)
        b.ln(f"M{x} 14 L{x} 70", '#D6DCE3', 1)
        b.ln(f"M{x-3} 26 L{x+3} 26 M{x-3} 40 L{x+3} 40 M{x-3} 54 L{x+3} 54", '#56636F', 1.2)
    b.p("M12 22 L74 18 L74 62 L12 66 Z", '#FFFFFF', None, op=.35)
    mesh(b, [(12, 22), (74, 18), (74, 62), (12, 66)], 14, 7, '#7F8C9B', .8, .95, fill=False)
    b.ln("M12 22 L74 18", '#FFFFFF', 1.2, .8)
    # reflector row
    for i in range(10):
        x = 8 + i * 7.6; y = 82 - i * .5
        b.ln(f"M{x:.1f} {y} L{x:.1f} {y-17:.1f}", '#3A4552', 2.4)
        b.ln(f"M{x:.1f} {y} L{x:.1f} {y-17:.1f}", '#E4E9EE', .9)
        b.ln(f"M{x-3:.1f} {y-9:.1f} L{x+3:.1f} {y-9:.1f}", '#56636F', 1.1)
        b.c(round(x, 1), y - 17, 1.4, 'metal3', MS, .5)
    wav(b, 78, 42, (7, 12, 17), -55, 55, WAVE, 1.8, .9)

# ============ 3 舰载雷达 ============
@icon('ship_radar', '舰载雷达', CAT)
def _(b):
    # hull + superstructure
    b.p("M2 70 L94 70 L88 78 L8 78 Z", 'sea', SS)
    b.p("M5 74 L91 74 L88 78 L8 78 Z", 'boot')
    b.p("M22 70 L24 56 L72 56 L76 70 Z", 'sea', SS)
    b.r(30, 59, 36, 5, 'canopy', '#1B2D40', rx=.8, sw=.6)
    glint(b, 40, 60.6, 3, .7)
    b.p("M34 56 L36 48 L60 48 L62 56 Z", 'seadk', SS, 1)
    # mast
    b.r(44, 34, 8, 22, 'cylM', MS, sw=1)
    b.ln("M42 44 L54 44 M42 50 L54 50", '#4B5867', 1.3)
    # cube phased array
    b.p("M30 12 L38 6 L68 6 L60 12 Z", 'metal', MS, .9)
    b.p("M60 12 L68 6 L68 30 L60 36 Z", 'array', '#1E3550', .9)
    b.r(30, 12, 30, 24, 'array', '#1E3550', rx=.8, sw=1)
    d = ''
    for i in range(1, 6): d += f"M{30+i*5} 12 L{30+i*5} 36 "
    for j in range(1, 5): d += f"M30 {12+j*4.8:.1f} L60 {12+j*4.8:.1f} "
    b.ln(d, '#9CC2EA', .5, .55)
    b.ln("M62 11 L62 33 M65 9 L65 31", '#9CC2EA', .5, .45)
    b.hl("M31 12.9 L59 12.9", .9, .8)
    b.hl("M39 6.9 L66 6.9", .8, .8)
    # whip + yard
    b.ln("M32 8 L26 1", '#4B5867', 1.2)
    b.ln("M70 50 L86 50", '#4B5867', 1.5); b.e(87, 50, 3, 2, 'metal', SS, .6)
    wav(b, 52, 21, (24, 32), -30, 30, WAVE, 1.6, .85)
    water(b, 74)

# ============ 4 机载预警雷达吊舱 ============
@icon('aew_pod', '机载预警雷达吊舱', CAT)
def _(b):
    b.sh(48, 88, 38, 3)
    b.g('translate(0 7)')
    b.p("M8 50 L4 30 L16 30 L28 47 Z", 'airdk', AS, 1)
    b.p("M12 49 L2 46 L2 51 L16 52 Z", 'airdk', AS, 1)
    # dorsal pod
    b.ln("M36 44 L36 38 M62 44 L62 38", '#6E7C8C', 3)
    b.p("M22 36 C22 30 28 28 38 28 L68 28 C78 28 82 32 82 36 C82 40 78 42 68 42 L36 42 C28 42 22 41 22 36 Z", 'airV', AS)
    b.r(30, 30.5, 42, 9, 'array', '#1E3550', rx=3, sw=.8)
    d = ''
    for i in range(1, 10): d += f"M{30+i*4.2:.1f} 30.8 L{30+i*4.2:.1f} 39.2 "
    b.ln(d, '#9CC2EA', .5, .5)
    b.hl("M26 31.5 C30 29.6 40 29.2 60 29.2", .9, .85)
    # fuselage
    b.p("M8 50 C10 46 22 44 40 44 L76 44 C86 44 92 48 92 53 C92 58 86 60 76 60 L18 60 C11 60 7 56 8 50 Z", 'airV', AS)
    b.p("M80 46 C86 46 89 49 90 52 L78 52 Z", 'canopy', '#1B2D40', .6)
    b.ln("M44 46 L44 58 M52 46 L52 58 M60 46 L60 58 M68 46 L68 58", '#2B3440', 2.6, .8)
    b.ln("M12 55 L86 55", '#8D9BAC', .6)
    # wing + prop engine
    b.p("M40 58 L58 58 L52 66 L42 66 Z", 'airdk', AS, 1)
    b.e(66, 64, 7, 3.4, 'airdk', AS, .9)
    b.e(75, 64, 1.6, 8, 'prop'); b.ln("M75 56 L75 72", '#2E3640', 1.4)
    b.hl("M12 48.4 C20 46.5 30 45.8 40 45.6 L74 45.6", .9, .8)
    wav(b, 52, 36, (26, 32, 38), -62, -30, WAVE, 1.8, .9)
    wav(b, 52, 36, (26, 32, 38), -150, -118, WAVE, 1.8, .9)
    b.eg()

# ============ 5 气象雷达 ============
@icon('weather_radar', '气象雷达', CAT)
def _(b):
    b.sh(36, 88, 24, 3)
    b.p("M28 88 L33 52 L39 52 L44 88 Z", 'conc', CS, 1)
    b.ln("M30 80 L42 80 M31 70 L41 70 M32 60 L40 60", '#8C96A2', .9)
    b.r(24, 49, 24, 4.4, 'metal2', MS, rx=1.4, sw=.9)
    b.c(36, 32, 17.5, 'sphere', '#8A97A6', 1)
    b.ln("M18.6 32 A17.4 5 0 0 0 53.4 32 M36 14.5 A6 17.4 0 0 0 36 49.5 M36 14.5 A6 17.4 0 0 1 36 49.5", '#B6C0CC', .8, .9)
    b.ln("M22 20 L50 44 M50 20 L22 44", '#C3CCD6', .7, .7)
    b.e(29, 22, 5, 2.4, '#FFFFFF', op=.7)
    wav(b, 36, 32, (22, 27), -32, 32, WAVE, 1.6, .9)
    # PPI scope
    b.c(75, 66, 17, '#0A2418', '#3E4752', 1.6)
    b.c(75, 66, 12, 'none', '#2F8F5A', .7, op=.8); b.c(75, 66, 6, 'none', '#2F8F5A', .7, op=.8)
    b.ln("M58 66 L92 66 M75 49 L75 83", '#2F8F5A', .6, .7)
    b.p("M75 66 L75 49 A17 17 0 0 1 87 54 Z", '#43C46B', op=.3)
    b.c(81, 59, 3.4, '#43C46B', op=.9); b.c(70, 72, 3.8, AMBER, op=.9); b.c(71.4, 71, 1.7, REDL)
    b.c(81, 74, 2.2, '#43C46B', op=.8)
    # cloud + rain
    b.p("M60 22 C56 22 54 18 57 16 C57 11 63 10 66 13 C68 8 78 8 80 14 C86 13 88 19 84 22 Z", 'cloud', '#86A7CB', .9)
    b.ln("M65 25 L63 32 M72 25 L70 32 M79 25 L77 32", SIG, 1.3, .85)

# ============ 6 火控雷达 ============
@icon('fire_control_radar', '火控雷达', CAT)
def _(b):
    b.sh(44, 86, 36, 4)
    b.r(14, 74, 56, 8, 'landdk', LS, rx=2, sw=1)
    wheel(b, 24, 84, 5); wheel(b, 60, 84, 5)
    b.p("M30 74 L34 56 L54 56 L58 74 Z", 'land', LS)
    b.r(30, 62, 24, 5, 'landdk', LS, rx=1, sw=.7)
    b.ln("M34 74 L28 86 M54 74 L60 86", '#3A424B', 2)
    # yoke arms
    b.ln("M30 52 L30 36 M58 52 L58 36", '#4B5867', 3.4)
    b.ln("M30 52 L30 36 M58 52 L58 36", '#B6C0CC', 1)
    b.r(28, 50, 32, 7, 'land', LS, rx=2, sw=.9)
    dish(b, 44, 34, 24, -36, .3, 1.0)
    # secondary tracker dish
    dish(b, 62, 50, 9, -36, .34, 1.0)
    b.hl("M31 52 L57 52", .8, .7)
    brackets(b, 82, 20, 9, REDL, 1.4)
    drone(b, 82, 20, .6)
    b.ln("M70 30 L77 24", REDL, 1.2, .9, extra="stroke-dasharray='2 2'")

def surf(b, y, x0=0, x1=96, op=.75):
    b.ln(f"M{x0} {y} Q{x0+6} {y-2} {x0+12} {y} T{x0+24} {y} T{x0+36} {y} T{x0+48} {y} T{x0+60} {y} T{x0+72} {y} T{x0+84} {y} T{x0+96} {y}", '#FFFFFF', 1.1, op)

# ============ 7 舰壳声呐 ============
@icon('hull_sonar', '舰壳声呐', CAT)
def _(b):
    b.p("M2 26 L66 26 C74 26 80 24 86 20 L78 36 C74 43 68 46 62 46 L2 46 Z", 'sea', SS)
    b.p("M2 40 L74 40 L68 45 L2 45 Z", 'boot')
    b.p("M12 26 L15 12 L40 12 L45 26 Z", 'sea', SS)
    b.r(19, 15, 17, 5, 'canopy', '#1B2D40', rx=.8, sw=.6)
    b.ln("M27 12 L27 3 M22 7 L32 7", '#4B5867', 1.4)
    b.p("M50 26 L52 20 L60 20 L62 26 Z", 'array', '#2C3E52', .7)
    b.hl("M3 27.4 L66 27.4 C74 27.4 79 25.6 84 22", .9, .7)
    b.r(0, 44, 96, 48, 'deepw')
    surf(b, 44, 0, 96, .8)
    b.ln("M8 54 Q14 52 20 54 T32 54 M46 62 Q52 60 58 62", '#FFFFFF', .8, .3)
    # dome
    b.r(60, 44, 12, 4, 'dkm2', DS, sw=.8)
    b.e(66, 53, 13, 6.5, 'dkm', DS, 1)
    b.ln("M56 53 L76 53 M58.5 50 L73.5 50 M58.5 56 L73.5 56", '#262C33', .7)
    b.e(62, 50.4, 5, 1.6, '#FFFFFF', op=.55)
    wav(b, 68, 53, (16, 23, 30), -48, 44, '#FFFFFF', 1.8, .95)
    # submarine target
    b.e(74, 82, 13, 4.6, 'subm', '#11161B', 1)
    b.p("M70 78 L71.5 74 L77 74 L78 78 Z", 'subm', '#11161B', .8)
    b.p("M60 82 L55 79 L55 85 Z", 'subm', '#11161B', .8)
    b.hl("M64 80 C68 79 74 78.8 82 79.4", .8, .5)

# ============ 8 拖曳阵声呐 ============
@icon('towed_array', '拖曳阵声呐', CAT)
def _(b):
    b.p("M0 20 L34 20 L41 38 L0 38 Z", 'sea', SS)
    b.p("M0 34 L39 34 L41 38 L0 38 Z", 'boot')
    b.p("M4 20 L6 8 L22 8 L26 20 Z", 'sea', SS)
    b.r(9, 11, 11, 4, 'canopy', rx=.6)
    b.ln("M28 20 L34 8 L40 12 L36 22", '#4B5867', 1.6)
    b.r(26, 14, 6, 6, 'seadk', SS, rx=1, sw=.8)
    b.hl("M1 21.4 L33 21.4", .9, .7)
    b.r(0, 36, 96, 56, 'deepw')
    surf(b, 36, 0, 96, .8)
    b.ln("M50 48 Q56 46 62 48 T74 48 M12 62 Q18 60 24 62 T36 62", '#FFFFFF', .8, .3)
    b.ln("M37 11 Q62 20 58 46 T46 70", '#2A323B', 1.8)
    b.ln("M37 11 Q62 20 58 46 T46 70", '#9AA6B3', .6)
    b.p("M44 70 L54 66.4 L54 73.6 Z", 'metal3', MS, .8)
    b.r(54, 66.4, 33, 7.2, 'cylO', '#8A4E17', rx=3.4, sw=.9)
    b.ln("M62 66.6 L62 73.4 M71 66.6 L71 73.4 M80 66.6 L80 73.4", '#8A4E17', .9)
    b.p("M87 66 L91 62.5 L91 77.5 L87 74 Z", 'dkm', DS, .8)
    b.hl("M56 67.8 L85 67.8", .8, .8)
    wav(b, 72, 70, (11, 17), -125, -55, '#FFFFFF', 1.7, .95)
    wav(b, 72, 70, (11, 17), 55, 125, '#FFFFFF', 1.7, .9)

# ============ 9 岸基声呐站／水听器阵 ============
@icon('sonar_station', '岸基声呐站', CAT)
def _(b):
    b.r(0, 46, 96, 46, 'deepw')
    surf(b, 46, 30, 96, .8)
    b.p("M0 34 L22 34 L32 44 L48 58 L66 70 L96 74 L96 92 L0 92 Z", 'seabed', '#6E5E3E', 1)
    b.p("M0 34 L22 34 L31 43 L0 46 Z", 'grass', '#5E7440', 1)
    b.hl("M1 35 L21 35", .9, .7)
    # shed + mast
    b.p("M2 21 L12 13 L22 21 Z", 'roof', RF, .9)
    b.r(4, 21, 16, 13, 'conc', CS, sw=.9)
    b.r(9, 26, 6, 8, 'dkm', DS, rx=.6, sw=.6)
    b.r(5.5, 23, 3, 3, 'glass', '#25578F', sw=.4); b.r(16, 23, 3, 3, 'glass', '#25578F', sw=.4)
    b.ln("M28 34 L28 8", '#3A4552', 2.4); b.ln("M28 34 L28 8", '#D6DCE3', .8)
    b.ln("M24 12 L32 12 M25 17 L31 17", '#56636F', 1.1)
    b.ln("M28 8 L28 2", '#4B5867', 1.2); b.c(28, 2, 1.4, 'metal3', MS, .5)
    b.p("M34 14 L44 16 L42 22 L32 20 Z", 'solar', '#18365C', .8)
    wav(b, 28, 12, (7, 12), -60, 20, WAVE, 1.4, .85)
    # cable
    b.ln("M20 33 L24 36 L31 44 L48 58 L64 69 L78 73 L92 75", '#262C33', 1.8)
    b.ln("M20 33 L24 36 L31 44 L48 58 L64 69 L78 73 L92 75", '#E59A45', .7, .8)
    # hydrophones
    for x, y in ((58, 65.5), (73, 70.5), (88, 73.6)):
        b.p(f"M{x-5} {y+1.5} L{x-3} {y-1} L{x+3} {y-1} L{x+5} {y+1.5} Z", 'dkm', DS, .6)
        b.r(x - 2.4, y - 14, 4.8, 13.5, 'cylM', MS, rx=2, sw=.8)
        b.ln(f"M{x-2.4} {y-9} L{x+2.4} {y-9} M{x-2.4} {y-5} L{x+2.4} {y-5}", SIG, .9)
        b.c(x, y - 14.5, 2.2, 'node', '#1F4F8C', .6)
        wav(b, x, y - 14.5, (6, 10), -150, -30, '#FFFFFF', 1.3, .9)

# ============ 10 无人值守地面传感器 ============
@icon('ugs', '无人值守地面传感器', CAT)
def _(b):
    pad(b, 48, 80, 38, 10)
    # grass blades
    b.ln("M24 80 L22 74 M27 81 L27 75 M70 80 L72 74 M67 82 L68 76", '#5E7440', 1.4)
    # antenna
    b.ln("M54 36 L60 8", '#2A2E33', 1.6); b.c(60, 7.5, 1.8, 'metal3', '#2A2E33', .6)
    wav(b, 60, 8, (6, 11, 16), -150, -30, SIG, 1.6, .9)
    # body
    b.r(38, 36, 22, 40, 'cylL', LS, rx=5, sw=1)
    b.r(36, 33, 26, 8, 'landdk', LS, rx=3.5, sw=1)
    b.ln("M38 52 L60 52 M38 64 L60 64", '#3E4C29', 1, .8)
    b.c(49, 46, 4.4, 'lens', '#0B1A2C', .8); glint(b, 47.6, 44.4, 1.4, .7)
    leds(b, [(44, 58, GREEN), (54, 58, AMBER)])
    b.p("M40 30 L58 30 L61 24 L37 24 Z", 'solar', '#18365C', .8)
    b.ln("M43 24 L42 30 M49 24 L49 30 M55 24 L56 30", '#9CC2EA', .5, .6)
    b.hl("M40 37.4 L58 37.4", .9, .7)
    b.hl("M41 42 L41 74", 1, .6)
    b.e(49, 77, 15, 3.6, 'soil', '#4A3F2C', .8)
    b.e(49, 76, 12, 2.4, 'grass', None, op=.9)
    # buried geophone probe + cable
    b.ln("M38 70 Q24 72 18 76", '#262C33', 1.6)
    b.p("M12 74 L22 74 L20 78 L14 78 Z", 'metal3', MS, .8)
    b.ln("M17 78 L17 84", '#4B5867', 1.8)

# ============ 11 振动／地磁传感器 ============
@icon('seismic_sensor', '振动地磁传感器', CAT)
def _(b):
    b.e(46, 74, 44, 14, 'grass', '#5E7440', .9)
    b.hl("M8 72 Q20 62 40 61", .9, .6)
    ripple(b, 46, 76, 40, 11, WAVE, 4, .85)
    # magnetic field lines
    b.ln("M30 38 C14 20 40 8 48 8 C56 8 82 20 66 38", SIG, 1.3, .8, extra="stroke-dasharray='3 2.4'")
    b.ln("M34 44 C22 28 44 18 48 18 C52 18 74 28 62 44", SIG, 1.3, .65, extra="stroke-dasharray='3 2.4'")
    # spike + puck
    b.p("M45 68 L51 68 L48 84 Z", 'metal3', MS, .8)
    b.e(48, 66, 16, 5, 'dkm2', DS, 1)
    b.p("M32 64 L32 56 C32 52 38 48 48 48 C58 48 64 52 64 56 L64 64 C64 68 56 70 48 70 C40 70 32 68 32 64 Z", 'dkm', DS, 1)
    b.e(48, 56, 15, 5, 'metal2', MS, .8)
    b.e(48, 55.4, 8, 2.6, 'metal', None, op=.9)
    b.c(48, 55.4, 2, 'lens')
    b.hl("M35 60 C35 56 40 53 46 52.4", .9, .8)
    leds(b, [(40, 64, GREEN), (56, 64, AMBER)])
    # cable + box
    b.ln("M62 66 Q74 70 80 66", '#262C33', 1.6)
    b.r(78, 56, 12, 12, 'metal', MS, rx=1.6, sw=.9)
    b.c(84, 62, 2, GREEN, op=.9)
    zig(b, [(6, 40), (12, 40), (14, 34), (17, 46), (20, 36), (22, 42), (26, 42)], AMBER, 1.5)

# ============ 12 动中通卫星终端 ============
@icon('satcom_otm', '动中通卫星终端', CAT)
def _(b):
    b.sh(46, 86, 44, 4)
    b.p("M6 70 L6 40 L56 40 L56 47 L66 47 L78 57 L90 59 C92 60 92 64 92 70 Z", 'land', LS)
    b.p("M67 49.5 L76 58 L63 58 L63 49.5 Z", 'canopy', '#1B2D40', .6)
    b.r(59, 49.5, 7, 7, 'canopy', rx=.8)
    b.r(8, 52, 46, 12, 'landdk', LS, rx=1.5, sw=.8)
    b.ln("M20 52 L20 64 M32 52 L32 64 M44 52 L44 64", '#2E3A1C', .8, .8)
    b.r(86, 60, 6, 3, '#F2E6B0', rx=.8, op=.9)
    b.ln("M10 41.2 L55 41.2", '#FFFFFF', .9, .7)
    # roof dome
    b.r(14, 36.5, 34, 4.4, 'dkm', DS, rx=1.5, sw=.8)
    b.p("M16 37 A15 15 0 0 1 46 37 Z", 'sphere', '#8A97A6', 1)
    b.ln("M19.5 28 Q31 22 42.5 28", '#FFFFFF', 1.1, .8)
    b.ln("M24 24 L38 37 M38 24 L24 37", '#B6C0CC', .6, .6)
    wheel(b, 24, 71, 8); wheel(b, 74, 71, 8)
    # satellite link
    sat(b, 76, 14, .62, 14)
    b.ln("M42 22 Q56 10 66 14", SIG, 1.2, .85, extra="stroke-dasharray='2.6 2.2'")
    wav(b, 31, 28, (21, 26), -75, -35, WAVE, 1.5, .9)

# ============ 13 散射通信设备 ============
@icon('troposcatter', '散射通信设备', CAT)
def _(b):
    _truck_base(b, (16, 30, 58, 78), cab_x=68, cab_top=46, chassis=(6, 60, 84))
    b.r(10, 55, 50, 5, 'landdk', LS, rx=1, sw=.8)
    # struts
    b.ln("M26 52 L20 57 M54 38 L54 56", '#3A424B', 3)
    b.ln("M26 52 L20 57 M54 38 L54 56", '#B6C0CC', 1)
    # panel (thickness, face, ribs)
    b.p("M8 20 L44 4 L56 32 L20 50 Z", 'dkm', DS, .9)
    P = [(12, 18), (48, 6), (58, 36), (22, 49)]
    poly(b, P, 'metal', MS, 1.4)
    mesh(b, P, 8, 6, '#8794A3', .7, .95, fill=False)
    b.ln("M12 18 L48 6", '#FFFFFF', 1.2, .9)
    b.p("M34 24 L41 22 L43 30 L36 32 Z", 'metal3', MS, .7)
    b.c(38, 27, 1.8, 'lens')
    wav(b, 36, 26, (32, 40, 48), -62, -8, WAVE, 1.8, .95)
    # scatter volume
    b.p("M74 14 C70 14 69 9 72 8 C73 3 80 2 82 6 C86 4 91 8 88 12 C92 13 91 17 87 17 L74 17 Z", 'cloud', '#86A7CB', .9)
    b.ln("M72 22 L70 28 M78 22 L76 28 M84 22 L82 28", SIG, 1.2, .8)

# ============ 14 短波电台 ============
@icon('hf_radio', '短波电台', CAT)
def _(b):
    # ionosphere band + path
    b.ln("M2 24 Q40 0 94 14", '#8FD0FF', 6, .3)
    b.ln("M2 24 Q40 0 94 14", '#D8EFFF', 1.4, .9)
    b.ln("M67 24 L62 10 L90 42", SIG, 1.3, .9, extra="stroke-dasharray='2.8 2.4'")
    b.sh(44, 90, 40, 3.4)
    # antenna
    b.ln("M58 52 L67 22", '#3A4552', 2.2); b.ln("M58 52 L67 22", '#D6DCE3', .8)
    b.c(67.4, 21.4, 1.8, 'metal3', MS, .6)
    for i in range(4):
        b.ln(f"M{54.5+i*.2:.1f} {55-i*2.4:.1f} L{60.6+i*.2:.1f} {53-i*2.4:.1f}", '#5A6370', 1.4)
    box(b, 10, 86, 58, 30, 12, ft='land', tp='landT', sd='landdk', st=LS)
    # front panel
    b.r(14, 60, 24, 12, 'scr', '#0B1A2C', rx=1.4, sw=.7)
    b.ln("M16 66 L18 63 L19.5 68 L21.5 62.5 L23 66 L25 64 M29 63.5 L36 63.5 M29 67 L35 67", '#43C46B', .9, .95)
    b.c(55, 67, 8, 'dkm2', DS, 1)
    b.c(55, 67, 6, 'metal', MS, .8)
    b.ln("M55 62 L55 67", '#262C33', 1.4)
    for i in range(12):
        a = math.radians(i * 30); b.ln(f"M{55+8.8*math.cos(a):.1f} {67+8.8*math.sin(a):.1f} L{55+10.2*math.cos(a):.1f} {67+10.2*math.sin(a):.1f}", '#262C33', .7)
    for x in (17, 25, 33, 41):
        b.c(x, 79, 2.6, 'metal3', MS, .7); b.ln(f"M{x} 77 L{x} 79", '#262C33', .8)
    b.c(53, 80, 2.2, 'gold', '#6E5418', .6); b.c(61, 80, 2.2, 'gold', '#6E5418', .6)
    leds(b, [(42, 63, GREEN), (42, 67, AMBER)])
    # handset on side
    b.p("M70 52 L77 48 L79 62 L72 66 Z", 'dkm', DS, .8)
    b.ln("M68 62 Q64 78 70 82", '#262C33', 1.3)

# ============ 15 超短波电台 ============
@icon('vhf_radio', '超短波电台', CAT)
def _(b):
    b.sh(46, 88, 42, 3.4)
    # backpack set
    b.ln("M14 38 L10 6", '#3A4552', 1.8); b.ln("M14 38 L10 6", '#D6DCE3', .7); b.c(10, 5.6, 1.5, 'metal3', MS, .5)
    b.r(5, 36, 32, 46, 'canvas', LS, rx=5)
    b.r(5, 36, 32, 11, 'land', LS, rx=5)
    b.ln("M7 47 L35 47", '#3E4C29', 1, .7)
    b.r(10, 52, 22, 20, 'dkm', DS, rx=2)
    b.r(12, 54, 11, 6, 'scr', '#0B1A2C', rx=.8, sw=.5)
    b.c(27, 58, 3, 'metal', MS, .7); b.ln("M27 55.8 L27 58", '#262C33', 1)
    b.c(16, 67, 1.8, 'metal3', MS, .5); b.c(23, 67, 1.8, 'metal3', MS, .5)
    leds(b, [(28, 67, GREEN)])
    b.ln("M5 52 Q0 62 6 74", '#262C33', 3); b.ln("M5 52 Q0 62 6 74", '#5A6370', 1)
    b.hl("M9 37.4 L33 37.4", .9, .7)
    # handheld
    b.g('rotate(-7 62 52)')
    b.drop("M48 24 L76 24 L76 80 L48 80 Z", 2, 3, .15)
    b.r(52, 4, 6, 22, 'dkm2', DS, rx=3)
    b.ln("M54 6 L54 24", '#5A6370', 1, .8)
    b.r(60, 16, 7, 9, 'metal', MS, rx=1.6, sw=.8); b.ln("M62 17 L62 24 M65 17 L65 24", '#8794A3', .6)
    b.r(69, 18, 5, 7, 'red', '#7A2219', rx=1.4, sw=.7)
    b.r(48, 24, 28, 56, 'dkm', DS, rx=6)
    b.r(47, 34, 3.2, 12, 'red', '#7A2219', rx=1.4, sw=.6)
    for i in range(5): b.ln(f"M54 {29+i*2.4:.1f} L70 {29+i*2.4:.1f}", '#1E2328', 1.1)
    b.r(52, 41, 20, 10, 'scr', '#0B1A2C', rx=1.4, sw=.7)
    b.ln("M54.5 47 L57 44 L59.5 48.4 L62 43.6 L64.5 47 L67 45", AMBER, 1)
    for i in range(3):
        for j in range(3):
            b.r(52.5 + i * 7, 54 + j * 5.2, 5.4, 3.6, 'metal3', MS, rx=.9, sw=.4)
    b.r(48, 72, 28, 8, 'landdk', LS, rx=4, sw=.8)
    b.hl("M51 25.4 L73 25.4", .9, .7); b.hl("M49.6 30 L49.6 70", .8, .55)
    b.eg()
    wav(b, 55, 8, (8, 14), -155, -25, WAVE, 1.6, .9)

# ============ 16 激光通信终端 ============
@icon('laser_comm', '激光通信终端', CAT)
def _(b):
    b.sh(28, 90, 28, 3.2)
    b.r(6, 80, 40, 8, 'dkm', DS, rx=2, sw=.9)
    b.p("M18 80 L20 64 L32 64 L34 80 Z", 'metal2', MS, .9)
    b.ln("M12 54 L12 66 M44 54 L44 66", '#3A424B', 3.4)
    b.r(10, 62, 36, 6, 'metal3', MS, rx=2, sw=.8)
    b.g('rotate(-32 28 52)')
    b.r(8, 44, 36, 16, 'dkm', DS, rx=4)
    b.ln("M16 44.6 L16 59.4 M26 44.6 L26 59.4", '#262C33', 1)
    b.r(42, 41, 8, 22, 'metal3', MS, rx=2, sw=.9)
    b.e(50, 52, 3, 9.4, 'lens', '#05101C', .6)
    b.e(49.4, 48, 1, 3.4, '#FFFFFF', op=.7)
    b.hl("M10 45.6 L40 45.6", .9, .75)
    b.c(28, 52, 3.4, 'hub', '#1D2228', .7)
    b.eg()
    # beam
    b.ln("M44 40 L76 20", LASER, 8, .16)
    b.ln("M44 40 L76 20", LASER, 3.2, .7)
    b.ln("M44 40 L76 20", '#FFFFFF', 1.2, .95)
    b.c(44, 40, 4, 'beam')
    for t in (.3, .55, .8):
        x = 44 + 32 * t; y = 40 - 20 * t
        b.c(round(x, 1), round(y, 1), 1.1, '#FFFFFF', op=.9)
    sat(b, 80, 17, .62, 12)
    b.c(76, 20, 3.2, 'beam')
    leds(b, [(40, 84, GREEN), (45, 84, AMBER)])

# ============ 17 微波接力站 ============
@icon('microwave_relay', '微波接力站', CAT)
def _(b):
    pad(b, 48, 86, 42, 6)
    b.ln("M48 12 L48 3", '#4B5867', 1.4); b.c(48, 3, 1.6, REDL, op=None)
    lattice(b, 36, 60, 12, 84, 8, 10)
    b.ln("M40 26 L44 26 M52 48 L56 48", '#3A4552', 3)
    drum(b, 24, 26, 11, 18, -1)
    drum(b, 74, 48, 11, 18, 1)
    b.r(44, 10.4, 8, 3, 'metal3', MS, rx=1, sw=.6)
    wav(b, 22, 26, (7, 13), 140, 220, WAVE, 1.7, .9)
    wav(b, 76, 48, (7, 13), -40, 40, WAVE, 1.7, .9)
    # hut
    b.p("M60 78 L68 72 L82 72 L88 78 Z", 'roof', RF, .9)
    b.r(60, 78, 28, 8, 'conc', CS, sw=.9)
    b.r(75, 80, 6, 6, 'dkm', DS, rx=.6, sw=.5)
    b.ln("M54 80 L60 82", '#262C33', 1.4)

# ============ 18 低轨卫星星座 ============
@icon('leo_constellation', '低轨卫星星座', CAT)
def _(b):
    def opt(cx, cy, rx, ry, rot, t):
        a, r_ = math.radians(t), math.radians(rot)
        x, y = rx * math.cos(a), ry * math.sin(a)
        return (round(cx + x * math.cos(r_) - y * math.sin(r_), 1), round(cy + x * math.sin(r_) + y * math.cos(r_), 1))
    b.c(48, 112, 54, 'none', '#8FD0FF', 3, op=.5)
    b.c(48, 112, 50, 'earth', '#173F78', 1)
    b.p("M26 80 C30 72 40 70 44 74 C46 80 40 84 36 88 C30 90 24 86 26 80 Z", 'tree', None, op=.85)
    b.p("M56 72 C62 68 74 70 76 76 C74 82 66 82 62 86 C56 84 52 76 56 72 Z", 'tree', None, op=.85)
    b.hl("M20 82 Q32 62 56 63", 1.6, .55)
    O = [(48, 38, 44, 12, -18), (48, 38, 40, 11, 24), (48, 40, 46, 8, 3)]
    for o in O:
        b.o.append(f"<ellipse cx='{o[0]}' cy='{o[1]}' rx='{o[2]}' ry='{o[3]}' fill='none' stroke='#5C8FC8' stroke-width='1.1' opacity='.85' transform='rotate({o[4]} {o[0]} {o[1]})'/>")
    S = [opt(*O[0], 205), opt(*O[0], 330), opt(*O[0], 80),
         opt(*O[1], 20), opt(*O[1], 140), opt(*O[1], 250),
         opt(*O[2], 130), opt(*O[2], 290)]
    links = [(0, 6), (6, 4), (4, 2), (1, 7), (7, 3), (2, 6)]
    d = ''.join(f"M{S[i][0]} {S[i][1]} L{S[j][0]} {S[j][1]} " for i, j in links)
    b.ln(d, '#5FA2E4', .9, .8, extra="stroke-dasharray='2.2 2'")
    for k, (x, y) in enumerate(S):
        sat(b, x, y, .36, (-18, 24, 3)[min(k // 3, 2)])
    # ground beam
    b.p(f"M{S[5][0]} {S[5][1]+3} L40 63 L58 63 Z", AMBER, None, op=.3)
    b.ln(f"M{S[5][0]} {S[5][1]+3} L40 63 M{S[5][0]} {S[5][1]+3} L58 63", WAVE, 1, .9, extra="stroke-dasharray='2.4 2'")

KEYS = """sar_radar otH_radar ship_radar aew_pod weather_radar fire_control_radar hull_sonar towed_array sonar_station ugs seismic_sensor satcom_otm troposcatter hf_radio vhf_radio laser_comm microwave_relay leo_constellation nav_satellite gateway_station tactical_terminal antenna_vehicle bs_5g spectrum_monitor""".split()

if __name__ == '__main__':
    import re as _re, os, glob, sys
    HERE = os.path.dirname(os.path.abspath(__file__))
    byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
    only = [k for k in KEYS if k in byk]
    if len(sys.argv) < 2 or sys.argv[1] != 'partial':
        assert set(byk) == set(KEYS), set(byk) ^ set(KEYS)
    assert len(KEYS) == len(set(KEYS))
    old = set()
    for f in glob.glob(os.path.join(HERE, 'icons*.js')):
        if os.path.basename(f) == 'icons_i.js': continue
        old |= set(_re.findall(r"key: '([^']+)'", open(f, encoding='utf-8').read()))
    clash = old & set(only)
    assert not clash, clash
    SZ = []
    lines = ['ICON_LIB.push(...[']
    for k in only:
        _, n, c, fn = byk[k]
        b = B(k); fn(b)
        s = b.svg()
        s = _re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
        s = _re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
        assert '"' not in s
        SZ.append((len(s), k))
        lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
    lines.append(']);')
    open(os.path.join(HERE, 'icons_i.js'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(only), 'largest', sorted(SZ)[-6:])
