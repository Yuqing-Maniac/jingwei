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


# ---- extra palette (batch d) ----
GR.update({
    'yellow': L(V, (0, '#FCE892'), (.5, '#F2C232'), (1, '#B88A10')),
    'cylT': L(H, (0, '#3A424B'), (.3, '#7E8892'), (.7, '#4A535D'), (1, '#1E2328')),
    'crate': L(V, (0, '#D9B57A'), (1, '#94703C')),
    'sand': L(D, (0, '#F6E8C0'), (.6, '#DCC08A'), (1, '#B8975C')),
    'mineS': ('r', ('0.35', '0.3', '0.75'), ((0, '#9AA3AC'), (.5, '#46505A'), (1, '#1A2026'))),
    'flame': ('r', ('0.5', '0.25', '0.75'), ((0, '#FFFFFF'), (.3, '#FFE59A'), (.7, '#F49A2C', .9), (1, '#E0461C', 0))),
    'deep': L(('0', '0', '0', '1'), (0, '#BFE0F7', .7), (.3, '#6FA9DB', .6), (1, '#173E6B', .75)),
    'beam': L(('0', '0', '0', '1'), (0, '#8FE0FF', .65), (1, '#8FE0FF', 0)),
    'spray': ('r', None, ((0, '#FFFFFF', .95), (1, '#DDEBF7', .0))),
    'stealth': L(V, (0, '#8E9A7A'), (.5, '#5E6B48'), (1, '#343E24')),
})
RS = '#7A261D'
YS = '#8A6A10'

def gear(b, cx, cy, r, n=12, fill='mineS', st='#0E1013'):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        rr = r if i % 2 == 0 else r * .66
        pts.append(f"{cx + rr * math.cos(a):.1f} {cy + rr * math.sin(a):.1f}")
    b.p("M" + " L".join(pts) + " Z", fill, st, .9)
    b.c(cx, cy, r * .3, 'hub', '#0E1013', .7)

# ================= 无人（水面/水下/地面/特种）=================
@icon('usv_armed', '武装无人艇（遥控武器站）', '无人')
def _(b):
    b.p("M12 62 L84 62 L82 70 L18 70 Z", 'sea', SS)
    b.p("M14 67.6 L83 67.6 L82 70 L18 70 Z", 'boot')
    b.p("M5 59 C5 55 10 53 16 53 L72 53 C82 53 90 54 93 57 C91 62 86 64 80 64 L16 64 C9 64 5 62 5 59 Z", 'dkm', DS)
    b.ln("M12 55.4 L72 55.4 C80 55.4 87 56 90 57.6", '#9AA5B1', 1.1, .8)
    b.r(2, 52, 8, 14, 'dkm2', DS, rx=2, sw=.8); b.r(0.5, 56, 4, 4, '#2A2E33')
    b.ln("M6 52 L6 40", '#4B5867', 1.2); b.c(6, 39, 1.2, AMBER)
    b.p("M26 53 L29 43 L43 43 L47 53 Z", 'sea', SS)
    b.p("M31 44.6 L42 44.6 L44 51 L30 51 Z", 'canopy', '#1B2D40', .6); glint(b, 36, 46, 2.4, .7)
    b.r(62, 45, 6, 8, 'seadk', SS, sw=.8)
    b.r(56, 36, 22, 10, 'sea', SS, rx=2)
    b.r(58, 38, 5, 5, 'lens', '#0B141F', rx=2.4, sw=.7); glint(b, 59.8, 39.4, 1, .6)
    b.ln("M77 40 L93 40", '#2E3640', 3); b.ln("M77 39.4 L93 39.4", '#7B8896', .8)
    b.r(91, 38, 4, 4, '#2E3640', rx=.8)
    b.r(66, 33, 8, 3, 'seadk', SS, rx=1, sw=.8)
    b.hl("M58 37.2 L76 37.2", .9, .8); b.hl("M12 54.4 L70 54.4", .9, .5)
    water(b, 66)

@icon('usv_interceptor', '高速无人拦截艇', '无人')
def _(b):
    b.g('rotate(-6 50 66)')
    b.p("M4 62 L58 59 L94 56 L82 71 L12 71 Z", 'sea', SS)
    b.p("M9 67.5 L86 67.5 L82 71 L12 71 Z", 'red')
    b.p("M40 59 L48 50 L64 48 L74 57.5 Z", 'seadk', SS)
    b.p("M51 51 L63 49.4 L69.4 56.2 L47 57 Z", 'canopy', '#1B2D40', .6); glint(b, 58, 51.5, 3, .7)
    b.ln("M44 50 L44 40 M44 40 L52 40", '#4B5867', 1.4); b.r(46, 36, 8, 4, 'metal', SS, rx=1, sw=.7)
    b.r(1, 52, 7, 14, 'dkm2', DS, rx=2, sw=.8); b.r(9.5, 52, 7, 14, 'dkm2', DS, rx=2, sw=.8)
    b.c(30, 53, 1.3, '#E2574C'); b.c(34, 53, 1.3, '#3D86D6')
    b.ln("M14 61 L88 57", '#FFFFFF', 1, .55)
    b.hl("M6 62.8 L58 60 L92 57", .9, .85)
    b.eg()
    b.p("M0 68 C-2 56 6 52 10 56 C6 58 8 62 12 66 Z", 'spray', op=.95)
    b.p("M80 71 C84 66 92 66 96 68 C92 71 86 72 82 74 Z", 'spray')
    b.ln("M0 60 L12 59.5 M1 56 L8 56", '#FFFFFF', 1.2, .8)
    water(b, 67)

@icon('usv_kamikaze', '自杀式无人艇', '无人')
def _(b):
    b.p("M6 67 L60 64 L90 61 L84 71 L12 71 Z", 'seadk', SS)
    b.p("M12 63 L28 59 L56 59 L68 64 L12 66 Z", 'sea', SS)
    b.r(36, 54, 10, 5, 'dkm2', DS, rx=1.2)
    b.r(38, 55.4, 6, 2.2, 'lens', rx=1)
    b.ln("M16 60 L10 38", '#2E3238', 1)
    b.r(60, 52, 32, 12, 'red', RS, rx=6)
    for x in (70, 76, 82): b.r(x, 52, 2.8, 12, 'yellow', None, sw=0)
    b.r(60, 52, 32, 12, 'none', RS, rx=6, sw=1)
    b.hl("M65 55.4 L86 55.4", 1, .8)
    b.p("M90 40 L92.6 45 L97 44.2 L94 48.4 L96 53 L91.4 51 L88 54.6 L88.4 49.4 L84.4 46.4 L89 45.6 Z", 'flame')
    b.hl("M10 65.4 L56 61", .9, .7)
    water(b, 66)

@icon('usv_large', '大型无人水面舰（三体船）', '无人')
def _(b):
    b.p("M6 70 C5 63 9 58 13 58 C17 58 21 63 20 70 Z", 'sea', SS)
    b.p("M76 70 C75 63 79 58 83 58 C87 58 91 63 90 70 Z", 'sea', SS)
    b.p("M6.4 66.6 L19.6 66.6 L20 70 L6 70 Z", 'boot'); b.p("M76.4 66.6 L89.6 66.6 L90 70 L76 70 Z", 'boot')
    b.p("M13 59 L40 52 L40 58 L15 64 Z", 'seadk', SS); b.p("M83 59 L56 52 L56 58 L81 64 Z", 'seadk', SS)
    b.p("M35 70 L37 50 L59 50 L61 70 Z", 'sea', SS)
    b.p("M35.6 66.6 L60.4 66.6 L61 70 L35 70 Z", 'boot')
    b.p("M39 50 L41 33 L55 33 L57 50 Z", 'sea', SS)
    b.p("M42 36.4 L54 36.4 L55 41 L41 41 Z", 'canopy', '#1B2D40', .6); glint(b, 47, 38, 3, .7)
    b.ln("M42 44.4 L54 44.4", '#5D6B7A', 1)
    b.ln("M48 33 L48 20", '#4B5867', 1.5)
    b.e(48, 14, 8, 3.6, 'metal', SS); b.c(48, 12, 3, 'sphere', SS, .6)
    b.ln("M43 24 L53 24", '#4B5867', 1.2)
    for x in (20, 27, 33): b.r(x, 54.4 - (x - 20) * .15, 4, 3, '#27303A', rx=.5, sw=0)
    for x in (63, 69, 75): b.r(x, 52.6 + (x - 63) * .15, 4, 3, '#27303A', rx=.5, sw=0)
    b.hl("M41 34.4 L55 34.4", .9, .75); b.hl("M36.6 51.4 L58 51.4", .9, .6)
    water(b, 68)

@icon('usv_survey', '测量无人船（双体）', '无人')
def _(b):
    for x in (13, 63):
        b.p(f"M{x} 70 L{x+2} 52 L{x+18} 52 L{x+20} 70 Z", 'sea', SS)
        b.p(f"M{x+.4} 66.6 L{x+19.6} 66.6 L{x+20} 70 L{x} 70 Z", 'orange')
        b.hl(f"M{x+3} 53.4 L{x+17} 53.4", .9, .7)
    b.p("M8 52 L88 52 L88 45 L8 45 Z", 'metal2', SS)
    b.p("M8 45 L14 40 L82 40 L88 45 Z", 'metal', SS)
    b.p("M32 40 L35 24 L61 24 L64 40 Z", 'sea', SS)
    b.p("M37 27 L59 27 L60.6 34 L35.4 34 Z", 'canopy', '#1B2D40', .6); glint(b, 48, 29, 4, .8)
    b.r(32, 36.6, 32, 2.6, 'orange', '#8A4E17', rx=.8, sw=.6)
    b.ln("M48 24 L48 11", '#4B5867', 1.5); b.r(42, 8, 12, 4, 'metal', SS, rx=1.4, sw=.7)
    b.ln("M20 40 L20 30 M76 40 L76 30", '#4B5867', 1.4); b.c(20, 29, 1.5, AMBER); b.c(76, 29, 1.5, GREEN)
    b.p("M48 72 L26 95 L70 95 Z", 'beam')
    b.ln("M34 86 Q48 92 62 86 M30 91 Q48 97 66 91", '#FFFFFF', 1, .6)
    b.r(40, 66, 16, 5, 'dkm', DS, rx=2, sw=.8)
    b.hl("M10 46.6 L86 46.6", .9, .6)
    water(b, 60)

@icon('usv_jetski', '摩托艇式无人艇', '无人')
def _(b):
    b.g('rotate(-7 50 64)')
    b.p("M8 60 C10 55 26 55 44 55 L66 53 C78 51 90 55 93 59 L86 68 L14 68 Z", 'orange', '#8A4E17')
    b.p("M12 64 L88 64 L86 68 L14 68 Z", 'dkm', DS, .8)
    b.p("M16 55 C22 49 40 49 52 53 L46 56 C36 56 24 56 16 57 Z", 'dkm2', DS, .9)
    b.p("M56 50 L64 40 L66.4 41 L63 53 Z", 'canopy', '#1B2D40', .7)
    b.ln("M60 49 L63 43", '#2E3640', 2.2); b.ln("M56.5 44.6 L67 41.4", '#2E3640', 2.4)
    b.c(30, 46, 3.4, 'lens', '#0B141F', .8); b.ln("M30 49 L30 53", '#3D4854', 1.6); glint(b, 29, 45, 1, .6)
    b.ln("M12 52 L10 36", '#2E3238', 1); b.c(10, 35.4, 1.3, AMBER)
    b.r(3, 55, 7, 6, '#2A2E33', DS, rx=1.5, sw=.8)
    b.ln("M12 56.4 L62 53.4 L88 56", '#FFFFFF', 1.1, .8)
    b.eg()
    b.p("M2 62 C-1 56 4 52 8 56 C5 58 6 62 10 65 Z", 'spray')
    b.p("M80 68 C84 63 91 62 95 65 C91 68 86 69 82 72 Z", 'spray')
    water(b, 67)

@icon('uuv_xl', '超大型无人潜航器', '无人')
def _(b):
    b.e(50, 50, 46, 30, 'uwater')
    b.p("M18 46 L8 28 L16 28 L28 44 Z", 'seadk', SS, 1); b.p("M18 56 L8 74 L16 74 L28 58 Z", 'seadk', SS, 1)
    b.e(7, 51, 2.4, 11, 'prop'); b.ellipse = None
    b.p("M12 45 C12 42 22 38 30 38 L78 38 C88 38 94 43 94 51 C94 59 88 64 78 64 L30 64 C22 64 12 60 12 57 Z", 'subm', '#11161B')
    b.p("M58 38 L60 31 C61 30 69 30 70 31 L72 38 Z", 'subm', '#11161B', 1)
    b.r(32, 41, 22, 8, '#0E1318', None, rx=1.5)
    for x in (35, 42.4, 49.8): b.r(x, 43, 5.4, 4, 'orange', '#8A4E17', rx=2, sw=.5)
    b.ln("M30 38 L30 64 M56 38 L56 64 M74 38 L74 64", '#2A323B', 1)
    b.r(30, 55, 26, 2.6, '#E59A45', rx=.8, op=.9)
    b.p("M78 38 C88 38 94 43 94 51 C94 59 88 64 78 64 C82 58 82 44 78 38 Z", 'lens', '#0B141F', .8)
    b.c(61, 47, 1.4, GREEN)
    b.hl("M16 44.6 C22 41.4 28 40 34 39.6 L78 39.6 C85 39.6 90 41.6 92 44.4", 1.1, .6)
    for x, y, r in ((6, 38, 1.6), (3, 32, 1.1), (6, 66, 1.4), (88, 28, 1.2), (84, 24, .8)):
        b.c(x + 2, y, r, 'none', '#FFFFFF', .7, op=.7)

@icon('auv_portable', '便携式自主潜航器', '无人')
def _(b):
    b.e(48, 54, 42, 22, 'uwater')
    b.p("M24 50 L16 40 L22 40 L31 50 Z", 'seadk', SS, 1); b.p("M24 58 L16 68 L22 68 L31 58 Z", 'seadk', SS, 1)
    b.e(14, 54, 2.2, 8, 'dkm2', DS, .8); b.e(15.5, 54, 1.4, 6.6, 'prop')
    b.p("M20 49 L66 46 C74 46 80 50 80 54 C80 58 74 62 66 62 L20 59 Z", 'yellow', YS)
    b.p("M66 46 C74 46 80 50 80 54 C80 58 74 62 66 62 C70 58 70 50 66 46 Z", 'dkm', DS, .8)
    b.r(36, 47, 3, 14, '#2E3640', op=.85)
    b.p("M42 61 L48 69 L53 69 L52 61 Z", 'seadk', SS, .8)
    b.p("M42 47 L48 40 L53 40 L52 47 Z", 'seadk', SS, .8) if False else None
    b.p("M30 48.6 C30 40 40 38 52 38 C58 38 60 42 60 47 Z", 'none')
    b.ln("M32 47.4 C34 38 52 36 56 47", '#2E3640', 2.4); b.ln("M32 47.4 C34 38 52 36 56 47", '#9AA5B1', 1)
    b.ln("M24 49 L22 34", '#4B5867', 1); b.c(22, 33, 1.5, REDL)
    b.c(75, 54, 2.4, 'lens', '#0B141F', .6)
    b.hl("M22 50.6 L66 47.8 C71 47.8 75 49.6 77 51.4", 1, .8)
    b.ln("M42 54.6 L62 54.6", '#7A5A0C', 1.4, .8)
    for x, y, r in ((86, 44, 1.5), (90, 38, 1), (10, 66, 1.2)):
        b.c(x, y, r, 'none', '#FFFFFF', .7, op=.7)

@icon('rov', '遥控潜水器ROV', '无人')
def _(b):
    b.e(50, 56, 44, 34, 'uwater')
    b.ln("M30 4 C22 10 40 14 32 22 C28 26 30 30 34 34", '#20252B', 3.2); b.ln("M30 4 C22 10 40 14 32 22 C28 26 30 30 34 34", '#5A626C', 1)
    b.r(20, 32, 4.4, 40, 'metal2', MS, rx=1.5, sw=.9); b.r(72, 32, 4.4, 40, 'metal2', MS, rx=1.5, sw=.9)
    b.r(20, 66, 56, 5, 'metal3', MS, rx=1.6, sw=.9)
    b.r(18, 26, 60, 14, 'yellow', YS, rx=5)
    b.ln("M24 29.4 L72 29.4", '#FFFFFF', 1, .8); b.ln("M26 36 L70 36", YS, .8, .5)
    for cx in (11, 85):
        b.c(cx, 52, 8, 'dkm2', DS, 1); b.c(cx, 52, 5.6, 'prop', '#8D9BAC', .5)
        b.ln(f"M{cx-5} {52-2} L{cx+5} {52+2} M{cx-4} {52+4} L{cx+4} {52-4}", '#2E3640', 1.6); b.c(cx, 52, 1.6, 'hub', '#1D2228', .5)
    b.r(36, 44, 24, 18, 'dkm', DS, rx=3)
    b.c(48, 53, 6.4, 'lens', '#0B141F', 1); glint(b, 46, 50.6, 1.8, .9)
    b.c(39.6, 47.6, 2, '#FFF3B8', '#B8891A', .6); b.c(56.4, 47.6, 2, '#FFF3B8', '#B8891A', .6)
    b.ln("M60 62 L72 76", '#4B5867', 3.6); b.ln("M60 62 L72 76", '#B6C0CC', 1.6)
    b.c(60, 62, 2.6, 'hub', '#1D2228', .6)
    b.ln("M72 76 L84 74", '#4B5867', 3.2); b.ln("M72 76 L84 74", '#B6C0CC', 1.4); b.c(72, 76, 2.4, 'hub', '#1D2228', .6)
    b.ln("M84 74 L92 69 M84 74 L92 79", '#2E3640', 2.2)
    b.hl("M20 33 L20 66", .9, .5)
    for x, y, r in ((26, 80, 1.5), (30, 86, 1), (68, 18, 1.4), (84, 28, 1)):
        b.c(x, y, r, 'none', '#FFFFFF', .7, op=.7)

@icon('wave_glider', '波浪滑翔器', '无人')
def _(b):
    b.r(0, 46, 96, 46, 'water')
    b.p("M6 46 L12 40 L82 40 L91 44 L88 47 L10 47 Z", 'yellow', YS)
    b.p("M20 40 L74 40 L72 36 L22 36 Z", 'solar', '#18365C', .8)
    b.ln("M33 36.4 L32 40 M47 36.4 L47 40 M61 36.4 L62 40", '#7FA3C8', .6, .8)
    b.ln("M80 40 L80 24", '#4B5867', 1.4); b.c(80, 23, 1.6, REDL); b.ln("M80 26 L88 26 L80 31 Z", '#E2574C', .8)
    b.hl("M13 41.6 L22 38 L72 38", .9, .8)
    b.ln("M2 47 Q8 44 14 47 T26 47 T38 47 T50 47 T62 47 T74 47 T86 47 T98 47", '#FFFFFF', 1.2, .85)
    b.ln("M48 48 L48 68", '#2A2E33', 1.6); b.ln("M48 48 L48 68", '#8D9BAC', .5)
    b.r(28, 68, 44, 3.6, 'dkm', DS, rx=1.5, sw=.8)
    for x in (29, 44, 59):
        b.p(f"M{x} 71 L{x+11} 71 L{x+14} 79 L{x+3} 79 Z", 'yellow', YS, .9)
    b.p("M70 67 L84 65 L86 73 L72 72 Z", 'dkm', DS, .8); b.p("M84 64 L90 61 L90 72 L86 73 Z", 'yellow', YS, .8)
    b.p("M28 72 L20 76 L20 82 L29 78 Z", 'dkm2', DS, .8)
    b.ln("M6 58 Q14 55 22 58 M60 86 Q70 83 80 86", '#FFFFFF', .8, .35)

@icon('uuv_seabed', '海底驻留无人平台', '无人')
def _(b):
    b.r(4, 6, 88, 84, 'deep', None, rx=10)
    b.ln("M6 17 Q14 14 22 17 T38 17 T54 17 T70 17 T86 17", '#FFFFFF', 1.1, .8)
    b.p("M4 78 C20 72 36 76 54 74 C70 72 84 74 92 78 L92 86 Q92 90 86 90 L10 90 Q4 90 4 84 Z", 'sand', '#9A7B45', .9)
    b.ln("M54 36 C58 28 46 24 50 16", '#20252B', 1.4)
    b.c(50, 14, 4, 'orange', '#8A4E17', .9); b.hl("M48 12 L50 11", 1, .9)
    b.r(18, 70, 66, 4, 'metal3', MS, rx=1.4, sw=.9)
    b.r(24, 66, 4, 6, 'metal3', MS, sw=.8); b.r(70, 66, 4, 6, 'metal3', MS, sw=.8)
    b.p("M28 46 L62 46 C66 46 68 50 68 54 L68 62 C68 66 66 68 62 68 L28 68 C24 68 22 66 22 62 L22 54 C22 50 24 46 28 46 Z", 'metal', MS)
    b.p("M62 46 L80 40 L80 74 L62 68 Z", 'dkm', DS)
    b.e(80, 57, 5.6, 17, '#0E1318', '#3D4854', .9); b.e(80, 57, 3.2, 10, 'glow')
    b.ln("M80 41 L80 73", GREEN, 1.2, .0)
    b.c(80, 44, 1.4, GREEN); b.c(80, 70, 1.4, GREEN)
    b.p("M34 46 C34 38 44 38 44 46 Z", 'metal2', MS, .9)
    b.ln("M39 38 L39 33 L48 33", '#4B5867', 1.4)
    b.r(28, 54, 28, 6, 'glass', '#25578F', rx=1.5, sw=.6)
    b.ln("M30 50 L56 50", '#FFFFFF', 1, .8)
    b.c(30, 63.6, 1.4, GREEN); b.c(35, 63.6, 1.4, AMBER)
    for x, y, r in ((12, 54, 1.5), (14, 44, 1), (88, 34, 1.2)):
        b.c(x, y, r, 'none', '#FFFFFF', .7, op=.7)

@icon('ugv_armed', '武装轮式无人车', '无人')
def _(b):
    b.sh(48, 83, 44, 4.5)
    b.p("M6 66 L6 54 L16 47 L62 47 L86 55 L90 66 Z", 'land', LS)
    b.p("M16 47 L62 47 L86 55 L6 55 Z", 'landdk', LS, .8)
    b.r(10, 60, 78, 5, 'landdk', LS, rx=1, sw=.9)
    b.r(78, 54, 7, 3.4, 'canopy', rx=.6)
    for x in (18, 38, 60, 78): wheel(b, x, 72, 8.4)
    b.r(32, 37, 24, 11, 'land', LS, rx=2)
    b.r(44, 40, 7, 5, 'canopy', rx=1); glint(b, 46, 41.3, 1.2, .6)
    b.ln("M56 41 L90 41", '#2E3640', 3); b.ln("M56 40.4 L90 40.4", '#7B8896', .7); b.r(88, 39, 4, 4, '#2E3640', rx=.8)
    b.r(24, 40, 8, 4, 'landdk', LS, rx=.8, sw=.8); b.r(24, 44, 8, 3.4, 'landdk', LS, rx=.8, sw=.8)
    b.c(38, 34, 3.6, 'lens', '#0B141F', .8); b.ln("M38 37 L38 38", '#2E3238', 1.6); glint(b, 37, 33, 1, .6)
    b.ln("M28 37 L24 22", '#2E3238', 1); b.c(24, 21, 1.2, AMBER)
    b.ln("M33 37.6 L30 34 M33 36 L30 32.4", '#3A3F46', 1.2)
    leds(b, [(12, 52, GREEN)])
    b.hl("M8 54 L16.6 48.2 L62 48.2", .9, .85); b.hl("M34 38.4 L54 38.4", .9, .7)

@icon('ugv_logistics', '无人运输车（物资）', '无人')
def _(b):
    b.sh(48, 83, 44, 4.2)
    b.r(8, 58, 74, 7, 'landdk', LS, rx=1.5, sw=1)
    b.p("M82 64 L82 52 L90 52 L92 64 Z", 'land', LS)
    b.r(83.4, 54, 6, 4, 'canopy', rx=.8); glint(b, 86, 55, 1.4, .6)
    b.ln("M87 52 L87 44", '#2E3238', 1); b.c(87, 43, 1.8, 'lens', '#0B141F', .6)
    for x in (18, 36, 54, 72): wheel(b, x, 71, 6.8)
    b.r(12, 42, 28, 16, 'crate', '#6E4F23', rx=1)
    b.r(42, 46, 22, 12, 'crate', '#6E4F23', rx=1)
    b.r(66, 48, 14, 10, 'canvas', LS, rx=1)
    b.r(18, 29, 20, 13, 'crate', '#6E4F23', rx=1)
    for x in (18, 32): b.r(x, 42, 2.4, 16, '#3A3F46', sw=0, op=.8)
    b.r(46, 46, 2.4, 12, '#3A3F46', sw=0, op=.8)
    b.ln("M12 50 L40 50 M18 35.4 L38 35.4", '#6E4F23', .7, .7)
    b.ln("M42 49.4 L64 49.4", '#6E4F23', .7, .7)
    b.ln("M70 50 L77 50 M70 54 L77 54", '#36421F', .8, .8)
    b.hl("M13 43 L39 43", .9, .6); b.hl("M19 30 L37 30", .9, .6)
    leds(b, [(14, 61.5, GREEN)])

@icon('ugv_mineclear', '无人扫雷车', '无人')
def _(b):
    b.sh(40, 83, 38, 4.2)
    b.p("M5 66 L5 54 L12 47 L50 47 L62 56 L62 66 Z", 'land', LS)
    b.r(8, 60, 52, 4.6, 'landdk', LS, rx=1, sw=.9)
    for x in (16, 33, 50): wheel(b, x, 72, 8)
    b.r(44, 50, 10, 4, 'canopy', rx=.6)
    b.r(18, 40, 16, 7, 'landdk', LS, rx=1.5, sw=.9)
    b.ln("M24 40 L22 24", '#2E3238', 1); b.c(22, 23.4, 1.3, AMBER)
    b.ln("M60 60 L76 70", '#4B5867', 4); b.ln("M60 60 L76 70", '#B6C0CC', 1.6)
    b.ln("M60 66 L70 74", '#4B5867', 3)
    b.c(60, 60, 2.6, 'hub', '#1D2228', .6)
    gear(b, 82, 71, 11.4, 12)
    gear(b, 67, 77, 8.6, 10)
    b.p("M5 56 L12 56 L12 59 L5 59 Z", '#F2C232', op=.9)
    b.ln("M6 62 L9 56 M10 62 L13 56", '#2E3238', 1.2, .0)
    b.p("M90 80 L92.4 84.4 L95.6 82.4 L94 87 L90 86 Z", 'flame', op=.9)
    b.hl("M7 54 L12.6 48.2 L50 48.2", .9, .85)
    b.ln("M0 80 Q4 78 8 80", '#FFFFFF', 0.1, 0)

@icon('ugv_recon_small', '小型侦察机器人（可抛投）', '无人')
def _(b):
    b.sh(48, 80, 40, 3.8)
    b.ln("M70 54 L92 36", '#2E3238', 1.4); b.c(92, 35.4, 1.4, AMBER)
    b.e(76, 56, 8, 18.6, 'tyre', KS, 1); b.e(76, 56, 3.2, 8.4, 'hub', '#0E1013', .7)
    b.r(22, 46, 54, 20, 'landdk', LS, rx=9)
    b.r(24, 48, 50, 7, 'land', None, rx=3.4, op=.9)
    b.c(48, 55, 4.6, 'lens', '#0B141F', .9); glint(b, 46.4, 53.4, 1.4, .8)
    b.ln("M30 60.6 L42 60.6 M56 60.6 L68 60.6", '#4E5F35', 1, .8)
    b.e(22, 56, 10, 22, 'tyre', KS, 1)
    b.e(22, 56, 5, 11.4, 'hub', '#0E1013', .8); b.e(22, 56, 1.8, 4, '#23272C')
    for a in range(0, 360, 40):
        r = math.radians(a)
        b.ln(f"M{22 + 8.2 * math.cos(r):.1f} {56 + 18.2 * math.sin(r):.1f} L{22 + 10 * math.cos(r):.1f} {56 + 21.8 * math.sin(r):.1f}", '#5A616A', 1.2, .8)
    b.c(66, 50, 1.2, GREEN)
    b.ln("M6 26 Q14 12 30 12", '#E08A2E', 1.6, .9, extra="stroke-dasharray='3 2.4'")
    b.p("M30 8 L37 12 L30 16 Z", '#E08A2E', None, op=.95)
    b.hl("M24 48 L68 48", .9, .6)

@icon('robodog_armed', '武装四足机器人', '无人')
def _(b):
    b.sh(50, 85, 36, 3.8)
    def leg(hip, knee, foot, far):
        o1, i1, o2, i2 = ('#14181C', '#2E353D', '#0B0D10', '#23282E') if far else ('#1E2328', '#58626E', '#0B0D10', '#3A4148')
        b.ln(f"M{hip[0]} {hip[1]} L{knee[0]} {knee[1]}", o1, 7.6)
        b.ln(f"M{hip[0]} {hip[1]} L{knee[0]} {knee[1]}", i1, 5.2)
        b.ln(f"M{knee[0]} {knee[1]} L{foot[0]} {foot[1]}", o2, 5)
        b.ln(f"M{knee[0]} {knee[1]} L{foot[0]} {foot[1]}", i2, 2.6)
        b.c(knee[0], knee[1], 3.4, 'hub', '#0E1013', .8); b.c(knee[0], knee[1], 1.2, '#E08A2E')
        b.e(foot[0], foot[1] + 1, 3, 2, '#0B0D10')
    leg((32, 48), (22, 62), (28, 84), True)
    leg((66, 48), (74, 62), (66, 84), True)
    b.r(20, 34, 52, 17, 'dkm', DS, rx=7)
    b.p("M70 36 L83 36 C86.5 36 88 38 88 41 L88 46 C88 48.5 86.5 49.5 84 49.5 L70 49.5 Z", 'dkm', DS)
    b.r(75, 38.6, 11, 6, 'lens', '#0B141F', rx=2.2, sw=.6); b.c(84, 41.6, 1.2, REDL)
    b.r(26, 28, 30, 6.4, 'dkm2', DS, rx=1.5); b.r(30, 22.6, 12, 5.4, 'dkm2', DS, rx=1.2)
    b.ln("M56 31 L88 31", '#1E2328', 3); b.ln("M56 30.4 L88 30.4", '#7B8896', .7); b.r(86, 29.2, 5, 3.6, '#2E3640', rx=.8)
    b.r(40, 34, 6, 8, 'dkm2', DS, rx=1, sw=.8)
    b.ln("M91 31 L96 31", REDL, 1.2, .9)
    b.ln("M24 43 L66 43", '#E08A2E', 1.4, .8)
    leds(b, [(26, 39, GREEN)])
    leg((30, 48), (20, 64), (30, 84), False)
    leg((64, 48), (72, 64), (64, 84), False)
    b.hl("M24 36.4 L66 36.4", .9, .45); b.hl("M28 29.2 L54 29.2", .8, .45)

@icon('humanoid', '人形机器人', '无人')
def _(b):
    b.sh(48, 90, 20, 2.6)
    def limb(p, q, w=7.6, col='white'):
        b.ln(f"M{p[0]} {p[1]} L{q[0]} {q[1]}", '#5F6D7E', w)
        b.ln(f"M{p[0]} {p[1]} L{q[0]} {q[1]}", '#E4E9EF', w - 2.4)
        b.ln(f"M{p[0]-1} {p[1]} L{q[0]-1} {q[1]}", '#FFFFFF', 1, .8)
    limb((42, 62), (40, 76), 8.6); limb((40, 76), (40, 87), 7)
    limb((54, 62), (56, 76), 8.6); limb((56, 76), (56, 87), 7)
    b.c(40, 76, 3.6, 'hub', '#0E1013', .8); b.c(56, 76, 3.6, 'hub', '#0E1013', .8)
    b.r(33, 86, 14, 5, 'dkm', DS, rx=2.4, sw=.9); b.r(49, 86, 14, 5, 'dkm', DS, rx=2.4, sw=.9)
    limb((29, 29), (22, 45), 6.8); limb((22, 45), (24, 59), 6)
    limb((67, 29), (74, 45), 6.8); limb((74, 45), (72, 59), 6)
    b.c(22, 45, 3, 'hub', '#0E1013', .7); b.c(74, 45, 3, 'hub', '#0E1013', .7)
    b.c(24, 61, 3.6, 'dkm', DS, .8); b.c(72, 61, 3.6, 'dkm', DS, .8)
    b.r(36, 56, 24, 9, 'dkm', DS, rx=3.4)
    b.p("M30 24 C30 22 34 21 40 21 L56 21 C62 21 66 22 66 24 L61 55 L35 55 Z", 'white', '#5F6D7E')
    b.p("M38 25 L58 25 L56 44 L40 44 Z", 'whitedk', '#7C8A9B', .7)
    b.c(48, 33, 5, 'glow'); b.c(48, 33, 2.2, '#FFFFFF')
    b.ln("M40 47 L56 47 M41 50.4 L55 50.4", '#8794A3', .8)
    b.c(29, 27, 4.6, 'hub', '#0E1013', .8); b.c(67, 27, 4.6, 'hub', '#0E1013', .8)
    b.r(44, 16.6, 8, 5.4, 'dkm', DS, rx=1.5, sw=.8)
    b.r(38, 3, 20, 15, 'white', '#5F6D7E', rx=6)
    b.r(40.4, 7, 15.2, 7.2, 'canopy', '#1B2D40', rx=3.2, sw=.7); glint(b, 45, 8.8, 2.6, .8)
    b.c(44.4, 10.8, 1.1, '#8FD0FF'); b.c(51.6, 10.8, 1.1, '#8FD0FF')
    b.hl("M32 25.4 L62 25.4", .9, .8)

@icon('unmanned_tank', '无人坦克', '无人')
def _(b):
    b.sh(48, 83, 42, 4.5)
    track(b, 10, 86, 66, 81, 6)
    b.p("M5 68 L11 57 L66 55 L90 62 L87 68 Z", 'stealth', LS)
    b.p("M11 57 L66 55 L90 62 L5 62 Z", 'landdk', LS, .8)
    b.r(12, 62, 74, 5, 'landdk', LS, rx=1, sw=1)
    b.p("M24 56 L30 45 L60 43 L72 52 L72 56 Z", 'stealth', LS)
    b.p("M30 45 L60 43 L72 52 L36 52 Z", 'landdk', LS, .8)
    b.ln("M70 49 L92 47.6", '#2E3640', 3.4); b.ln("M70 48.4 L92 47", '#7B8896', .7); b.r(90, 45.8, 4, 3.6, '#2E3640', rx=.8)
    b.ln("M70 53 L82 52.6", '#2E3640', 2)
    b.r(26, 40, 14, 5, 'landdk', LS, rx=1, sw=.9); b.r(26, 36, 14, 4.4, 'landdk', LS, rx=1, sw=.9)
    b.r(38.4, 36.6, 2.4, 3.6, '#2E3640'); b.r(38.4, 40.6, 2.4, 4, '#2E3640')
    b.ln("M54 43 L54 38", '#3A3F46', 1.8); b.c(54, 35, 4.2, 'lens', '#0B141F', .9); glint(b, 52.6, 33.6, 1.2, .7)
    b.ln("M20 55 L16 32", '#2E3238', 1); b.c(16, 31.4, 1.2, AMBER)
    b.p("M60 51 L66 52 L66 54 L60 54 Z", 'canopy')
    leds(b, [(15, 59, GREEN)])
    b.hl("M13 57.8 L66 56 L88 62.6", .9, .75); b.hl("M32 46 L59 44.2", .9, .6)

@icon('ugv_firefight', '消防救援无人车', '无人')
def _(b):
    b.sh(40, 84, 38, 4.2)
    track(b, 8, 70, 68, 82, 4)
    b.p("M6 70 L6 58 L12 52 L60 52 L72 62 L72 70 Z", 'red', RS)
    b.r(10, 62, 58, 4.6, '#8E2E22', RS, rx=1, sw=.8)
    b.p("M50 54 L58 54 L66 62 L50 62 Z", 'canopy', '#1B2D40', .6); glint(b, 56, 56, 1.4, .6)
    b.c(21, 47, 9, 'metal', MS); b.c(21, 47, 5.4, 'none', '#7C8A9B', 1.2); b.c(21, 47, 2, '#8E2E22')
    b.ln("M12 47 L30 47 M21 38 L21 56", '#98A4B1', .8, .6)
    b.r(40, 40, 8, 13, 'metal3', MS, rx=1.5, sw=.9)
    b.ln("M44 42 L62 28", '#4B5867', 6); b.ln("M44 42 L62 28", '#B6C0CC', 3.4)
    b.r(60, 22, 7, 9, 'metal3', MS, rx=2, sw=.8) if False else None
    b.p("M60 24 L68 28 L66 33 L58 29 Z", 'metal3', MS, .8)
    b.c(30, 51, 1.6, AMBER); b.c(34, 51, 1.6, AMBER)
    b.ln("M68 27 C80 20 90 28 92 42", '#8FD0FF', 3, .9, extra="stroke-dasharray='1 0'"); b.ln("M68 27 C80 20 90 28 92 42", '#FFFFFF', 1, .85)
    b.c(78, 20, 1.2, '#CFE9FF', op=.9); b.c(86, 28, 1.1, '#CFE9FF', op=.9); b.c(93, 34, 1, '#CFE9FF', op=.9)
    b.p("M86 80 C80 76 86 70 86 64 C88 68 92 66 91 60 C96 66 98 74 94 80 Z", 'flame')
    b.hl("M8 58 L12.6 53.2 L58 53.2", .9, .7)


# ---------- build ----------
if __name__ == '__main__':
    import re as _re, os
    KEYS = [k for k, n, c, fn in ICONS]
    want = "usv_armed usv_interceptor usv_kamikaze usv_large usv_survey usv_jetski uuv_xl auv_portable rov wave_glider uuv_seabed ugv_armed ugv_logistics ugv_mineclear ugv_recon_small robodog_armed humanoid unmanned_tank ugv_firefight".split()
    assert KEYS == want, (set(KEYS) ^ set(want))
    lines = ['ICON_LIB.push(...[']
    SZ = []
    for k, n, c, fn in ICONS:
        b = B(k); fn(b)
        s = b.svg()
        s = _re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
        s = _re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
        assert '"' not in s
        SZ.append((len(s), k))
        lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
    lines.append(']);')
    open('/home/claude/drawtool/icons_d.js', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('ok', len(ICONS), sorted(SZ)[-5:])
