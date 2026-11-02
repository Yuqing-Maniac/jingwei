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

# ================= 空中 =================
@icon('fighter', '战斗机', '空中')
def _(b):
    d = ("M48 5 C50.5 10 52.5 17 53 26 L54 36 L60 40 L60 44 L55 43 L56 50 L86 66 L86 71 L57 70 L58 76 "
         "L66 82 L66 88 L56 86 L54 90 L42 90 L40 86 L30 88 L30 82 L38 76 L39 70 L10 71 L10 66 L40 50 L41 43 "
         "L36 44 L36 40 L42 36 L43 26 C43.5 17 45.5 10 48 5 Z")
    b.drop(d)
    b.p(d, 'air', AS)
    b.p("M44 40 C45 52 45 66 44 78 L52 78 C51 66 51 52 52 40 Z", '#FFFFFF', op=.25)
    b.p("M42.6 34 L40.2 46 L42.6 45 Z", '#2B3440')
    b.p("M53.4 34 L55.8 46 L53.4 45 Z", '#2B3440')
    b.ln("M43 72 L38 84", '#5F6D7E', 2.6); b.ln("M53 72 L58 84", '#5F6D7E', 2.6)
    b.ln("M43 72 L38.6 83", '#E8EDF2', .8); b.ln("M53 72 L57.4 83", '#E8EDF2', .8)
    b.r(43.4, 86, 4, 4, '#2B3138', rx=1); b.r(48.6, 86, 4, 4, '#2B3138', rx=1)
    b.e(48, 22, 3.4, 8, 'canopy', '#1B2D40', .8)
    glint(b, 47, 18.5, .9, 2.2)
    b.hl("M46.6 9.5 C45.4 15 44.8 22 44.8 30"); b.hl("M40 51.5 L12 67", 1, .7); b.hl("M36.6 40.5 L41.5 37", .9, .6)

@icon('bomber', '轰炸机', '空中')
def _(b):
    d = ("M48 23 C52 24 55 27 58 31 L92 65 L86 71 L74 67 L66 73 L58 68 L48 74 L38 68 L30 73 L22 67 "
         "L10 71 L4 65 L38 31 C41 27 44 24 48 23 Z")
    b.drop(d)
    b.p(d, 'air', AS)
    b.e(48, 46, 10, 20, '#FFFFFF', op=.22)
    b.p("M39 36 L44 33 L44 36.5 L40 39 Z", '#2B3440'); b.p("M57 36 L52 33 L52 36.5 L56 39 Z", '#2B3440')
    b.p("M36 64 L40 60 L46 64 L48 62 L50 64 L56 60 L60 64 L58 66.5 L50 62.8 L48 64.6 L46 62.8 L38 66.5 Z", '#6E7C8C', op=.6)
    b.p("M44.5 29.5 C46 27.5 50 27.5 51.5 29.5 L50.5 31.5 C49 30.8 47 30.8 45.5 31.5 Z", 'canopy', '#1B2D40', .6)
    b.hl("M46 25 L6 65", 1.1, .8); b.hl("M50 25 L60 34", .9, .5)

def _transport(b, awacs=False):
    fus = "M48 4 C52 4 54 8 54 14 L54 74 C54 80 51 88 48 90 C45 88 42 80 42 74 L42 14 C42 8 44 4 48 4 Z"
    wing = "M6 44 L42 32 L54 32 L90 44 L90 50 L54 45 L42 45 L6 50 Z"
    tail = "M48 75 L68 81 L68 86 L48 84 L28 86 L28 81 Z"
    for d in (wing, fus, tail): b.drop(d)
    b.p(fus, 'air', AS)
    b.p(tail, 'airdk', AS)
    for x, cy in ((18, 40), (30, 36.5), (66, 36.5), (78, 40)):
        b.e(x, cy, 2.8, 6.5, 'airdk', AS, 1)
        b.e(x, cy - 5, 2, 1.1, '#3A4552')
    b.p(wing, 'air', AS)
    b.ln("M48 72 L48 88", '#6E7C8C', 2)
    b.p("M44.6 9.5 L51.4 9.5 L50.8 12.8 L45.2 12.8 Z", 'canopy', '#1B2D40', .6)
    b.hl("M45 8 C44 12 43.8 18 43.8 30"); b.hl("M7 44.5 L41 33.3", 1, .75)
    if awacs:
        b.ln("M44 56 L44 64 M52 56 L52 64", '#5F6D7E', 2)
        b.drop("M48 47 A13 13 0 1 0 48.01 47 Z", 2, 3, .2)
        b.c(48, 60, 13, 'airV', AS)
        b.c(48, 60, 8.5, 'none', '#7C8A9B', 1)
        b.p("M37 57 L59 57 L59 63 L37 63 Z", '#4A5868', op=.55)
        b.hl("M38 53 A12 12 0 0 1 52 48.6", 1.2, .8)

@icon('transport', '运输机', '空中')
def _(b): _transport(b)

@icon('awacs', '预警机', '空中')
def _(b): _transport(b, True)

@icon('helicopter', '武装直升机', '空中')
def _(b):
    b.sh(50, 82, 36, 4)
    b.c(88, 32, 8, 'prop', '#8D9BAC', .6)
    b.ln("M88 24.5 L88 39.5", '#2E3640', 1.8)
    body = ("M8 54 C8 48 12 44 18 43 L28 40 C32 36 40 34 48 35 L60 37 C66 38 70 42 70 46 L86 45 L88 50 "
            "L70 52 C68 58 62 61 54 61 L20 61 C12 61 8 59 8 54 Z")
    b.p("M80 46 L85 29 L91 29 L89 50 L84 50 Z", 'airdk', AS)
    b.p(body, 'airV', AS)
    b.p("M76 52 L86 51 L86 54 L76 55 Z", 'airdk', AS, 1)
    b.p("M42 35.5 C44 30 52 29 58 30 C63 31 66 34 66 39 L60 37.5 Z", 'airdk', AS, 1)
    b.e(63.5, 37, 1.6, 2, '#2B3440')
    b.p("M14 46 C16 42 20 40 25 39 L27 44.5 L15 47 Z", 'canopy', '#1B2D40', .8)
    b.p("M28 40 C31 35 36 33 41 33.5 L42 40 L29 41.5 Z", 'canopy', '#1B2D40', .8)
    glint(b, 19.5, 42, 2, .8); glint(b, 34, 35.5, 2.2, .8)
    b.r(49, 22, 4, 12, '#3A434E')
    b.e(50, 22.5, 45, 3.2, 'prop')
    b.r(5, 20.6, 90, 2.6, '#2E3640', rx=1.3)
    b.ln("M7 21.4 L93 21.4", '#8592A2', .7)
    b.e(51, 22, 5, 2.6, 'hub', '#1D2228', .8)
    b.p("M38 50 L62 49 L62 52.5 L38 53.5 Z", 'airdk', AS, 1)
    b.r(40, 53, 14, 6.5, 'metal3', AS, rx=3.2, sw=1)
    b.e(54, 56.2, 1.6, 3, '#2B3138')
    b.r(56, 54, 11, 2.6, 'white', WS, rx=1.3, sw=.8)
    b.c(15, 61, 3.2, '#3A434E'); b.ln("M14 62 L5 63.5", '#2E3640', 1.6)
    b.ln("M22 61 L21 67 M56 61 L57 67", '#3A434E', 1.6)
    wheel(b, 21, 69, 3.6); wheel(b, 57, 69, 3.6)
    b.hl("M12 47 C14 45 16 44 18 43.5"); b.hl("M44 36 L60 38", 1, .7); b.hl("M70 46.6 L85 45.8", .9, .7)

@icon('uav_fixed', '固定翼无人机', '空中')
def _(b):
    b.g('translate(0 3)')
    pod = "M48 14 C52 14 54 18 54 26 L54 50 C54 54 52 58 48 58 C44 58 42 54 42 50 L42 26 C42 18 44 14 48 14 Z"
    wing = "M9 38 L87 38 C89 38 90 39 90 41 L90 44 C90 46 89 47 87 47 L9 47 C7 47 6 46 6 44 L6 41 C6 39 7 38 9 38 Z"
    for d in (wing, pod, "M30 78 L66 78 L66 84 L30 84 Z"): b.drop(d)
    b.r(32.5, 36, 3.6, 46, 'airdk', AS, rx=1.8, sw=1); b.r(59.9, 36, 3.6, 46, 'airdk', AS, rx=1.8, sw=1)
    b.r(29, 78, 38, 6, 'air', AS, rx=2)
    b.ln("M34.3 76 L34.3 86 M61.7 76 L61.7 86", '#4C5967', 2.2)
    b.e(48, 61, 11, 2, 'prop'); b.ln("M38 61 L58 61", '#2E3640', 1.8)
    b.p(pod, 'air', AS)
    b.p(wing, 'air', AS)
    b.e(48, 21, 3.2, 3.6, 'canopy', '#1B2D40', .8); glint(b, 47, 19.8, 1, .7)
    b.c(48, 60, 1.8, 'hub')
    b.hl("M8 39.5 L88 39.5", 1, .8); b.hl("M44.5 18 C43.6 22 43.4 26 43.4 30", 1, .7)
    b.eg()

@icon('uav_male', '察打一体无人机', '空中')
def _(b):
    fus = "M48 6 C53 6 56 10 56 18 L55 30 L53 70 L51 80 L45 80 L43 70 L41 30 L40 18 C40 10 43 6 48 6 Z"
    wing = "M4 40 L42 36 L54 36 L92 40 L92 45 L54 44 L42 44 L4 45 Z"
    vt1 = "M46 72 L31 85 L32.5 88.5 L47.5 79 Z"
    vt2 = mirror(vt1)
    for d in (wing, fus, vt1, vt2): b.drop(d)
    b.p(vt1, 'airdk', AS); b.p(vt2, 'airdk', AS)
    b.e(48, 83, 10, 1.8, 'prop'); b.ln("M39 83 L57 83", '#2E3640', 1.8)
    b.p(fus, 'air', AS)
    b.p(wing, 'air', AS)
    for x in (20, 28, 68, 76):
        b.r(x - 1.7, 31, 3.4, 16, 'white', WS, rx=1.7, sw=.8)
        b.r(x - 1.7, 33.5, 3.4, 1.8, 'red')
        b.p(f"M{x-1.7} 46 L{x-3.5} 48.5 L{x+3.5} 48.5 L{x+1.7} 46 Z", '#8F9BA9')
    b.e(48, 15, 5.5, 6.5, '#FFFFFF', op=.35)
    b.c(48, 26, 2.6, 'lens', '#1B2D40', .6)
    b.hl("M5 40.8 L41 37"); b.hl("M55 37 L91 40.8", .9, .5); b.hl("M44 9.5 C42.5 12 42 15 42 19", 1, .8)

@icon('uav_vtol', '垂起固定翼无人机', '空中')
def _(b):
    fus = "M48 10 C52 10 54 14 54 22 L53 72 C53 78 51 82 48 82 C45 82 43 78 43 72 L42 22 C42 14 44 10 48 10 Z"
    wing = "M9 39 L87 39 C89 39 90 40 90 42 L90 46 C90 48 89 49 87 49 L9 49 C7 49 6 48 6 46 L6 42 C6 40 7 39 9 39 Z"
    for d in (wing, fus): b.drop(d)
    b.r(26.2, 18, 3.8, 66, 'airdk', AS, rx=1.9, sw=1); b.r(66, 18, 3.8, 66, 'airdk', AS, rx=1.9, sw=1)
    b.p("M24 80 L72 80 L72 85 L24 85 Z", 'air', AS)
    b.e(48, 85, 9, 1.8, 'prop'); b.ln("M40 85 L56 85", '#2E3640', 1.6)
    b.p(fus, 'air', AS)
    b.p(wing, 'air', AS)
    b.e(48, 18, 3, 3.6, 'canopy', '#1B2D40', .8)
    for cx, cy, a in ((28.1, 20, 25), (67.9, 20, -25), (28.1, 70, -25), (67.9, 70, 25)):
        rotor(b, cx, cy, 12, a)
    b.hl("M8 40.5 L88 40.5")

@icon('uav_quad', '四旋翼无人机', '空中')
def _(b):
    b.e(51, 54, 26, 26, 'shadow', op=.6)
    for x, y in ((21, 21), (75, 21), (21, 75), (75, 75)):
        b.ln(f"M48 48 L{x} {y}", '#4A5664', 6.4)
        b.ln(f"M48 48 L{x} {y}", '#AEB9C5', 3.6)
        b.ln(f"M48 48 L{x} {y}", '#E9EEF3', 1)
    for x, y, a in ((21, 21, 30), (75, 21, -30), (21, 75, -30), (75, 75, 30)):
        b.c(x, y, 5, 'hub', '#1D2228', 1)
        rotor(b, x, y, 15.5, a)
    b.r(35, 33, 26, 30, 'air', AS, rx=8)
    b.r(39.5, 37, 17, 10, 'canopy', '#1B2D40', rx=4, sw=.8)
    glint(b, 44, 39.5, 2.5, .9)
    b.r(40, 51, 16, 8, '#FFFFFF', rx=3, op=.25)
    b.c(48, 31, 3.2, 'lens', '#1B2D40', .7)
    leds(b, [(25, 25, GREEN), (71, 25, GREEN), (25, 71, REDL), (71, 71, REDL)])
    b.hl("M38 39 C38 36 39 35 41 34.6")

@icon('loitering', '巡飞弹', '空中')
def _(b):
    body = "M12 44 L76 44 C84 44 89 46 92 48 C89 50 84 52 76 52 L12 52 C10 52 9 50 9 48 C9 46 10 44 12 44 Z"
    w1 = "M38 44 L33 12 L39.5 11 L46 44 Z"
    w2 = "M38 52 L33 84 L39.5 85 L46 52 Z"
    t1 = "M14 44 L11 31 L16.5 31 L22 44 Z"; t2 = "M14 52 L11 65 L16.5 65 L22 52 Z"
    c1 = "M64 44 L62.5 36 L65.5 36 L69 44 Z"; c2 = "M64 52 L62.5 60 L65.5 60 L69 52 Z"
    for d in (w1, w2, t1, t2, body): b.drop(d)
    for d in (w1, w2): b.p(d, 'whitedk', WS)
    for d in (t1, t2, c1, c2): b.p(d, 'whitedk', WS, 1)
    b.e(6, 48, 1.8, 13, 'prop'); b.ln("M6 37 L6 59", '#2E3640', 1.6)
    b.p(body, 'white', WS)
    b.r(70, 44, 3, 8, 'red')
    b.p("M83 45.2 C87.5 46 90.5 47.2 92 48 C90.5 48.8 87.5 50 83 50.8 Z", 'canopy', '#1B2D40', .6)
    b.c(8.2, 48, 2, 'hub')
    b.hl("M13 45.6 L78 45.6"); b.hl("M34.4 14 L38.6 43", .9, .7)

@icon('cruise_missile', '巡航导弹', '空中')
def _(b):
    b.sh(50, 74, 40, 3.6)
    body = "M12 43 L74 43 C84 43 90 46 93 48 C90 50 84 53 74 53 L12 53 C9 53 8 51 8 48 C8 45 9 43 12 43 Z"
    b.p("M12 43 L7 31 L12.5 31 L21 43 Z", 'whitedk', WS)
    b.p("M38 51 L57 51 L49 62 L44 62 Z", 'whitedk', WS)
    b.p(body, 'white', WS)
    b.p("M12 53 L7 65 L12.5 65 L21 53 Z", 'whitedk', WS)
    b.p("M22 53 L34 53 L32 57.5 L25 57.5 Z", '#3A4552', WS, .8)
    b.r(66, 43, 3, 10, 'red')
    b.r(4.5, 45.5, 3.5, 5, '#3A4048', rx=1)
    b.p("M86 45.5 C89 46.5 91.5 47.4 93 48 C91.5 48.6 89 49.5 86 50.5 Z", '#4A5664', op=.8)
    b.ln("M30 43 L30 53 M56 43 L56 53", '#8F9BA9', .6)
    b.hl("M12 44.8 L76 44.8")

@icon('ballistic_missile', '弹道导弹', '空中')
def _(b):
    b.sh(48, 89, 22, 3.2)
    b.p("M40 68 L31 82 L31 88 L41 85 Z", 'whitedk', WS)
    b.p("M56 68 L65 82 L65 88 L55 85 Z", 'whitedk', WS)
    b.p("M42 81 L54 81 L56.5 89 L39.5 89 Z", '#3A4048', DS, 1)
    b.p("M48 4 C53 10 56 18 56 27 L56 82 L40 82 L40 27 C40 18 43 10 48 4 Z", 'cylW', WS)
    b.r(40, 27, 16, 4, 'red')
    b.r(40, 56, 16, 2.2, '#3E4650')
    b.ln("M40 44 L56 44", '#8F9BA9', .7)
    b.p("M46.5 72 L49.5 72 L49.5 89 L46.5 89 Z", 'whitedk', WS, .8)
    b.hl("M44 12 C42.5 16 42 21 42 26 M42 33 L42 54 M42 60 L42 80", 1, .85)

# ================= 海上 =================
@icon('carrier', '航空母舰', '海上')
def _(b):
    b.p("M6 53 L91 50 L86 70 L14 70 L8 63 Z", 'sea', SS)
    b.p("M10 66 L87 66 L86 70 L14 70 Z", 'boot')
    b.r(28, 55.5, 10, 4, '#3D4854', rx=.6); b.r(46, 55.5, 10, 4, '#3D4854', rx=.6)
    b.p("M4 47 L78 47 Q88 47 93 41 L93 46 Q89 52 80 53 L4 53 Z", 'deck', SS)
    b.p("M59 47 L60 31 L72 31 L74 47 Z", 'sea', SS)
    b.p("M60.5 34 L71.5 34 L71.7 36.6 L60.4 36.6 Z", 'canopy')
    b.p("M64 31 L65 16 L67 16 L68 31 Z", 'seadk', SS, 1)
    b.ln("M62 21 L70 21 M63 25 L69 25", '#4B5867', 1.2)
    b.p("M61.5 39 L65 39 L65 44 L61.5 44 Z", '#5E7C9C')
    for x in (12, 22, 32, 42):
        b.p(f"M{x} 47 L{x+1.5} 44.5 L{x+5} 44 L{x+6.5} 42.6 L{x+7.2} 44 L{x+8} 47 Z", '#9AA6B3', '#4B5867', .6)
    b.hl("M5 48.2 L78 48.2 Q87 48 91.5 43"); b.hl("M8 54.5 L88 52", 1, .55); b.hl("M60 32.2 L71.4 32.2", .8, .7)
    water(b, 66)

@icon('destroyer', '驱逐舰', '海上')
def _(b):
    b.p("M4 55 L70 55 L93 49 L86 70 L13 70 L6 62 Z", 'sea', SS)
    b.p("M9 66 L87 66 L86 70 L13 70 Z", 'boot')
    b.r(10, 47, 13, 8, 'sea', SS, sw=1)
    b.p("M23 55 L24 43 L30 43 L31 55 Z", 'sea', SS, 1); b.r(23.6, 41.5, 6.8, 2.4, '#3D4854', rx=.8)
    b.p("M31 55 L33 40 L57 40 L60 55 Z", 'sea', SS)
    b.p("M38 40 L40 23 L50 23 L52 40 Z", 'sea', SS)
    b.r(43.5, 12, 3, 11, 'seadk', SS, sw=.8); b.ln("M41 15 L49 15 M42 18.5 L48 18.5", '#4B5867', 1.1)
    b.p("M40 43 L48 43 L48.8 51.5 L39.2 51.5 Z", 'array', '#2C3E52', .7)
    b.p("M42.2 26.5 L47.8 26.5 L48.3 33 L41.7 33 Z", 'array', '#2C3E52', .7)
    b.p("M53.5 42.6 L57.5 42.6 L58.2 46 L53.6 46 Z", 'canopy')
    b.r(62, 52.4, 9, 2.6, '#3D4854', rx=.4); b.ln("M65 52.4 L65 55 M68 52.4 L68 55", '#8C98A6', .5)
    b.ln("M82 51 L93 48.2", '#3D4854', 1.8)
    b.p("M74.5 53.4 L76.5 49.6 L82.5 49.6 L84 53 Z", 'seadk', SS, 1)
    b.hl("M6 56.4 L70 56.4 L91 51"); b.hl("M33.6 41.3 L56.5 41.3", .9, .75); b.hl("M40.6 24.3 L49.6 24.3", .8, .7)
    water(b, 66)

@icon('frigate', '护卫舰', '海上')
def _(b):
    b.p("M8 58 L70 58 L90 53 L84 70 L15 70 L10 64 Z", 'sea', SS)
    b.p("M11 66 L85 66 L84 70 L15 70 Z", 'boot')
    b.r(14, 50, 12, 8, 'sea', SS, sw=1)
    b.p("M27 58 L28 48 L33 48 L34 58 Z", 'sea', SS, 1); b.r(27.6, 46.6, 5.8, 2.2, '#3D4854', rx=.8)
    b.p("M34 58 L35.5 47 L56 47 L58.5 58 Z", 'sea', SS)
    b.ln("M42 47 L44.5 28 M50 47 L47.5 28 M42.8 41 L49.2 41 M43.6 35 L48.4 35", '#56636F', 1.4)
    b.r(43.5, 26, 5, 3, 'seadk', SS, sw=.8)
    b.e(46, 24, 7, 1.8, 'metal2', SS, .8)
    b.p("M52.4 49.2 L56 49.2 L56.6 52 L52.4 52 Z", 'canopy')
    b.ln("M79 52.6 L88 50.6", '#3D4854', 1.5)
    b.p("M72 56.6 L73.6 53 L79 53 L80.4 56 Z", 'seadk', SS, 1)
    b.hl("M10 59.3 L70 59.3 L88 54.7"); b.hl("M36.5 48.2 L55.4 48.2", .9, .75)
    water(b, 66)

@icon('patrol_boat', '巡逻作战艇', '海上')
def _(b):
    b.p("M8 60 L66 60 L91 52 L84 70 L16 70 L10 66 Z", 'sea', SS)
    b.p("M12 66.5 L85.5 66.5 L84 70 L16 70 Z", 'boot')
    b.p("M28 60 L30 47 L54 47 L61 53 L61 60 Z", 'sea', SS)
    b.p("M38 49 L53.5 49 L58.6 53.4 L38 53.4 Z", 'canopy', '#1B2D40', .6)
    glint(b, 45, 50.3, 3, .7)
    b.r(31, 50, 5, 3.4, 'canopy', rx=.6)
    b.r(41.2, 30, 2.6, 17, 'seadk', SS, sw=.8)
    b.r(34, 31, 17, 2.6, 'seadk', SS, rx=1.3, sw=.8)
    b.e(42.5, 28.5, 3, 1.6, 'metal', SS, .6)
    b.r(70.5, 53, 6, 5, 'seadk', SS, sw=.8)
    b.ln("M77 48.4 L92 44", '#2E3640', 2.4)
    b.p("M68 54 L70.5 46 L78 46 L80 50 L80 54 Z", 'sea', SS)
    b.ln("M18 60 L18 54 L24 52", '#3D4854', 1.4)
    b.hl("M10 61.3 L66 61.3 L89 54"); b.hl("M30.6 48.2 L53.5 48.2", .9, .75)
    water(b, 66)

@icon('missile_boat', '导弹快艇', '海上')
def _(b):
    b.p("M5 60 L70 58.5 L93 55 L85 68 L12 68 L7 64 Z", 'sea', SS)
    b.p("M9 65 L86.5 65 L85 68 L12 68 Z", 'boot')
    b.p("M46 58.6 L50 49 L67 49 L74 57.8 Z", 'sea', SS)
    b.p("M57 50.5 L66.4 50.5 L70.6 55.4 L58 55.4 Z", 'canopy', '#1B2D40', .6)
    b.ln("M56 49 L57 37 M53 41 L61 41", '#4B5867', 1.4)
    b.g('rotate(-13 12 57)')
    b.ln("M18 57 L18 52 M34 57 L34 52", '#4B5867', 1.6)
    b.r(12, 46, 30, 6, 'sea', SS, rx=1.2)
    b.r(12, 40, 30, 6, 'sea', SS, rx=1.2)
    b.r(40, 46, 2.6, 6, '#3D4854'); b.r(40, 40, 2.6, 6, '#3D4854')
    b.hl("M13 41.3 L40 41.3", .9, .7)
    b.eg()
    b.p("M80 66 Q88 62 93 63 Q89 66 84 68 Z", '#FFFFFF', op=.7)
    b.ln("M2 66 L12 65.5 M3 63.5 L9 63.2", '#FFFFFF', 1.2, .7)
    b.hl("M7 61.2 L70 59.8 L91 56.5")
    water(b, 65)

@icon('usv', '无人艇', '海上')
def _(b):
    b.p("M10 62 L68 62 L91 55 L84 70 L16 70 L12 66 Z", 'sea', SS)
    b.p("M13 67 L85.6 67 L84 70 L16 70 Z", 'boot')
    b.p("M32 62 L37 52 L58 52 L66 60 L66 62 Z", 'sea', SS)
    b.p("M57 54.2 L64 60 L60 60 L55 54.2 Z", 'canopy')
    b.r(45.6, 34, 2.8, 18, 'seadk', SS, sw=.8)
    b.e(47, 32, 7, 3.8, 'metal', SS)
    b.c(53, 45, 3.8, 'metal2', SS, .8); b.c(54, 45, 2.2, 'lens')
    b.ln("M40 52 L39 36 M36 52 L35 42", '#3D4854', 1)
    b.ln("M10 63 L56 63", '#D58A3A', 1.6, .9)
    b.p("M2 67 L12 64 L13 68 Z", '#FFFFFF', op=.6)
    b.ln("M1 64.5 L8 63", '#FFFFFF', 1, .6)
    b.hl("M12 63.2 L68 63.2 L89 56.6"); b.hl("M38 53.2 L57.5 53.2", .9, .7); b.hl("M42 30.5 C44 29.2 48 29 51 29.8", .9, .9)
    water(b, 66)

@icon('submarine', '潜艇', '海上')
def _(b):
    b.p("M14 51 L6 39 L11 39 L20 50 Z", 'subm', '#11161B', 1)
    b.p("M14 57 L6 69 L11 69 L20 58 Z", 'subm', '#11161B', 1)
    b.e(4.5, 54, 1.8, 8, 'prop')
    b.p("M8 52 C20 46 30 45 40 45 L80 45 C88 45 93 49 93 54 C93 59 88 63 80 63 L40 63 C28 63 18 61 8 57 Z", 'subm', '#11161B')
    b.p("M57 45 L59 30 C59.5 28.5 72 28.5 73 30 L75 45 Z", 'subm', '#11161B')
    b.r(54, 35, 24, 2.4, '#2A323B', rx=1.2)
    b.ln("M62 29 L62 22 M66 29 L66 19 M69 29 L69 24", '#2A323B', 1.4)
    b.hl("M59.5 30.5 C62 29.6 69 29.6 72 30.3", .9, .7); b.hl("M24 47.8 C30 46.6 36 46.4 42 46.4 L82 46.4 C86 46.5 89 48 90.5 50", 1, .6)
    b.r(0, 54, 96, 36, 'water')
    b.ln("M2 54 Q8 52 14 54 T26 54 T38 54 T50 54 T62 54 T74 54 T86 54 T98 54", '#FFFFFF', 1.1, .7)
    b.ln("M10 64 Q16 62 22 64 T34 64 M60 66 Q66 64 72 66 T84 66", '#FFFFFF', .8, .3)
    b.p("M90 54 Q94 51 95 53 Q93 55 90 56 Z", '#FFFFFF', op=.6)

@icon('uuv', '无人潜航器', '海上')
def _(b):
    b.e(50, 50, 46, 22, 'uwater')
    b.p("M12 43 L7 32 L11.5 32 L18 43 Z", 'seadk', SS, 1)
    b.r(1.5, 43, 4.5, 10, '#3A4048', DS, rx=1.2, sw=.8)
    b.ln("M3.8 40 L3.8 56", '#2E3640', 1.4)
    b.p("M14 42 L76 42 C86 42 92 45 93 48 C92 51 86 54 76 54 L14 54 C10 54 6 52 6 48 C6 44 10 42 14 42 Z", 'sea', SS)
    b.p("M76 42 C86 42 92 45 93 48 C92 51 86 54 76 54 Z", 'orange', '#8A4E17', .8)
    b.p("M12 53 L7 64 L11.5 64 L18 53 Z", 'seadk', SS, 1)
    b.r(56, 44.5, 9, 3.2, 'canopy', rx=1.2)
    b.ln("M30 42 L30 54 M48 42 L48 54", '#5D6B7A', .7)
    b.c(40, 46, 1.2, GREEN)
    b.hl("M14 43.6 L76 43.6 C83 43.8 88 45 91 46.8")
    for x, y, r in ((-2, 34, 1.6), (2, 28, 1.1), (5, 62, 1.3), (9, 68, .9), (88, 34, 1.1), (80, 30, .8)):
        b.c(x + 4, y, r, 'none', '#FFFFFF', .7, op=.7)

@icon('sonar_buoy', '声呐浮标', '海上')
def _(b):
    b.ln("M48 4 L48 18", '#4B5867', 1.6); b.c(48, 4.5, 1.8, REDL)
    b.ln("M41 8 Q38 11 41 14 M55 8 Q58 11 55 14 M37 5 Q32 11 37 17 M59 5 Q64 11 59 17", '#3D86D6', 1.2, .8)
    b.p("M38 22 L38 52 Q48 57 58 52 L58 22 Z", 'cylM', MS)
    b.p("M38 22 L38 29 Q48 32 58 29 L58 22 Z", 'orange', '#8A4E17', .9)
    b.e(48, 22, 10, 3, 'orange', '#8A4E17', .9)
    b.e(48, 21.6, 6, 1.4, '#FFFFFF', op=.5)
    b.hl("M40.5 31 L40.5 50", 1.1, .8)
    b.r(0, 44, 96, 46, 'water')
    b.ln("M2 44 Q8 42 14 44 T26 44 T38 44 M58 44 Q64 42 70 44 T82 44 T94 44", '#FFFFFF', 1.1, .7)
    b.ln("M48 55 L48 72", '#2A323B', 1.2)
    b.r(44, 72, 8, 13, 'metal3', '#3D4854', rx=2, sw=1)
    b.ln("M44 76 L36 82 M52 76 L60 82", '#3D4854', 1.2)
    b.ln("M34 70 Q28 78 34 86 M62 70 Q68 78 62 86 M27 66 Q19 78 27 90 M69 66 Q77 78 69 90", '#BFE3FF', 1.3, .85)

# ================= 陆地 =================
@icon('tank', '主战坦克', '陆地')
def _(b):
    b.sh(48, 82, 42, 4.5)
    track(b, 10, 84, 64, 80, 6)
    b.p("M6 66 L8 56 L80 54 L90 60 L88 66 Z", 'land', LS)
    b.r(12, 61, 74, 6, 'landdk', LS, rx=1, sw=1)
    b.r(70, 44.8, 20, 3.4, 'landdk', LS, sw=1)
    b.r(78, 44, 5, 5, 'landdk', LS, rx=1, sw=1)
    b.r(88.5, 44.2, 4.5, 4.6, 'landdk', LS, rx=.8, sw=1)
    b.p("M22 53 L28 42 L58 39 L70 43.5 L72 54 L24 55 Z", 'land', LS)
    b.r(36, 35.5, 9, 4.5, 'landdk', LS, rx=1.2, sw=1)
    b.ln("M43 36 L54 33.6", '#2E3238', 1.2)
    b.p("M60 41.5 L66 43 L65.5 46 L60 45 Z", 'canopy')
    b.hl("M29 42.7 L58 40 L68 43.6"); b.hl("M9 56.6 L80 55", 1, .7)

@icon('ifv', '步兵战车', '陆地')
def _(b):
    b.sh(48, 82, 42, 4.5)
    track(b, 10, 84, 65, 80, 6)
    b.p("M6 67 L6 45 L15 40 L70 40 L90 53 L90 67 Z", 'land', LS)
    b.r(10, 61, 76, 6, 'landdk', LS, rx=1, sw=1)
    b.r(60, 33.4, 28, 2.4, '#3A3F46', DS, sw=.6)
    b.r(84, 33, 5, 3.2, '#3A3F46', rx=.6)
    b.p("M38 40 L40 31 L57 31 L62 40 Z", 'land', LS)
    b.r(42, 25.5, 11, 5.5, 'landdk', LS, rx=1, sw=1)
    b.e(52.5, 28.2, 1, 2, '#2E3238')
    for x in (18, 28, 38, 48):
        b.r(x, 46, 5, 3, 'canopy', rx=.5)
    b.ln("M12 44 L12 62", '#3E4C29', 1)
    b.hl("M7 45.4 L15.4 41.2 L70 41.2 L88 53.6"); b.hl("M40.6 32.2 L56.6 32.2", .9, .7)

@icon('sp_howitzer', '自行火炮', '陆地')
def _(b):
    b.sh(48, 82, 42, 4.5)
    track(b, 8, 84, 65, 80, 6)
    b.p("M5 66 L7 56 L80 55 L90 61 L88 66 Z", 'land', LS)
    b.r(10, 61, 76, 6, 'landdk', LS, rx=1, sw=1)
    b.g('rotate(-24 64 41)')
    b.r(62, 39.2, 27, 3.8, 'landdk', LS, sw=1)
    b.r(70, 38.4, 6, 5.4, 'landdk', LS, rx=1.2, sw=1)
    b.r(87, 38.2, 6, 5.8, 'landdk', LS, rx=.8, sw=1)
    b.eg()
    b.p("M12 56 L14 35 L60 33 L68 40 L68 56 Z", 'land', LS)
    b.r(22, 30, 10, 5, 'landdk', LS, rx=1.2, sw=1)
    b.ln("M30 31 L40 29", '#2E3238', 1.2)
    b.r(20, 41, 8, 6, 'none', '#3E4C29', rx=.5, sw=.9)
    b.hl("M15.4 36.2 L60 34.2 L66.8 40.3"); b.hl("M8 57.3 L80 56.4", 1, .7)

@icon('towed_gun', '牵引火炮', '陆地')
def _(b):
    b.sh(46, 84, 42, 4)
    b.p("M42 66 L5 80.5 L5 84 L44 71 Z", 'landdk', LS)
    b.p("M46 68 L14 84 L17 87 L50 71 Z", 'land', LS)
    b.r(3, 79, 4, 7, '#2E3238', rx=.8); b.p("M12 83 L15 88.5 L19 86 Z", '#2E3238')
    b.g('rotate(-30 46 58)')
    b.r(30, 54.5, 30, 7, 'landdk', LS, rx=1.5)
    b.r(36, 55.8, 56, 4.2, 'land', LS)
    b.r(88, 54.8, 7, 6.2, 'landdk', LS, rx=1)
    b.hl("M37 57 L88 57", .9, .75)
    b.eg()
    b.p("M34 64 L54 56 L60 64 L42 70 Z", 'land', LS)
    b.p("M55 42 L63 38 L69 62 L61 66 Z", 'land', LS)
    b.hl("M56 42.8 L62.6 39.5", .9, .8)
    wheel(b, 50, 72, 11)

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

@icon('mlrs', '远程火箭炮', '陆地')
def _(b):
    _truck_base(b, (16, 32, 58, 77))
    b.ln("M26 60 L40 46", '#3E4C29', 2.4)
    b.g('rotate(-18 12 58)')
    b.r(10, 41, 54, 17, 'land', LS)
    for x in (20, 32, 44): b.ln(f"M{x} 41.5 L{x} 57.5", '#3E4C29', 1, .7)
    b.r(60, 41, 5, 17, '#3A3F46', DS, sw=.8)
    for yy in (44.5, 49.5, 54.5):
        b.c(62.5, yy, 1.6, '#C9CFD6')
    b.hl("M11 42.4 L60 42.4")
    b.eg()

@icon('tel', '导弹发射车', '陆地')
def _(b):
    _truck_base(b, (12, 25, 38, 51, 82), cab_x=68, cab_top=40, chassis=(4, 60, 86))
    b.ln("M34 60 L44 44", '#3E4C29', 2.6)
    b.g('rotate(-24 10 57)')
    b.r(8, 57, 58, 3.2, 'landdk', LS, sw=.8)
    b.p("M8 47 L60 47 C68 47 75 49.5 79 52 C75 54.5 68 57 60 57 L8 57 Z", 'white', WS)
    b.r(52, 47, 3, 10, 'red')
    b.r(22, 47, 1.5, 10, '#8F9BA9', op=.8)
    b.p("M8 47 L3 43 L3 61 L8 57 Z", 'whitedk', WS, .8)
    b.hl("M9 48.5 L62 48.5 C68 48.8 72 49.8 75 51")
    b.eg()

@icon('sam', '防空导弹车', '陆地')
def _(b):
    _truck_base(b, (16, 30, 58, 77), cab_x=68, cab_top=44)
    b.r(10, 54, 42, 6, 'landdk', LS, sw=1)
    for i, x in enumerate((12, 23, 34)):
        b.g(f'rotate(-8 {x+5} 56)')
        b.r(x, 14, 10, 42, 'land', LS, rx=1.5)
        b.r(x, 14, 10, 3.5, '#3A3F46', rx=1.2)
        b.ln(f"M{x+2.3} 19 L{x+2.3} 53", '#FFFFFF', 1, .6)
        b.ln(f"M{x} 30 L{x+10} 30 M{x} 44 L{x+10} 44", '#3E4C29', .9, .7)
        b.eg()
    b.r(58, 34, 2.4, 20, 'landdk', LS, sw=.6)
    b.p("M52 22 L66 20 L67 33 L53 34 Z", 'array', '#2C3E52', 1)
    b.ln("M55.5 22 L56.5 33.6 M59.5 21.4 L60.5 33.3 M63.5 20.8 L64.4 33 M52.6 27.7 L66.5 26.4", '#9CC2EA', .5, .7)

@icon('truck', '运输保障车', '陆地')
def _(b):
    _truck_base(b, (18, 33, 77), cab_x=66, cab_top=42)
    b.p("M8 60 L8 38 C8 34 10 32 14 32 L60 32 C64 32 66 34 66 38 L66 60 Z", 'canvas', LS)
    for x in (20, 32, 44, 56): b.ln(f"M{x} 32.6 L{x} 59.5", '#4E5F35', 1.2, .6)
    b.ln("M8 50 L66 50", '#4E5F35', .8, .5)
    b.hl("M10 34.4 L62 34.4", 1.1, .7)

@icon('ugv', '无人车', '陆地')
def _(b):
    b.sh(48, 82, 42, 4.5)
    b.p("M8 63 L8 50 L14 45 L80 45 L90 53 L88 63 Z", 'land', LS)
    b.r(10, 57, 76, 5, 'landdk', LS, rx=1, sw=.9)
    b.r(80, 50, 6, 3, 'canopy', rx=.6)
    for x in (20, 46, 72): wheel(b, x, 69, 9.5)
    b.r(26.5, 27, 3, 18, 'landdk', LS, sw=.8)
    b.c(28, 24, 5.2, 'land', LS)
    b.r(28, 21.5, 5, 5, 'canopy', rx=1.5)
    b.ln("M14 45 L11 15", '#2E3238', 1.2); b.c(11, 15, 1.2, '#2E3238')
    b.r(48, 37, 16, 8, 'land', LS, rx=1.5)
    b.r(62, 39.4, 24, 2.6, '#3A3F46', DS, sw=.6)
    b.r(52, 38.6, 6, 3.6, 'canopy', rx=.6)
    leds(b, [(18, 50, GREEN)])
    b.hl("M9 50.4 L14.6 46.2 L80 46.2 L88 52.6")

@icon('robodog', '无人狗（四足）', '陆地')
def _(b):
    b.sh(50, 84, 36, 3.8)
    def leg(hip, knee, foot, far):
        o1, i1, o2, i2 = ('#2A321B', '#5E6F3E', '#15181C', '#31363C') if far else (LS, '#8EA162', '#15181C', '#4A5058')
        b.ln(f"M{hip[0]} {hip[1]} L{knee[0]} {knee[1]}", o1, 7.4)
        b.ln(f"M{hip[0]} {hip[1]} L{knee[0]} {knee[1]}", i1, 5)
        b.ln(f"M{knee[0]} {knee[1]} L{foot[0]} {foot[1]}", o2, 5)
        b.ln(f"M{knee[0]} {knee[1]} L{foot[0]} {foot[1]}", i2, 2.6)
        b.c(knee[0], knee[1], 3.4, 'hub', '#0E1013', .8)
        b.e(foot[0], foot[1] + 1, 3, 2, '#15181C')
    leg((34, 46), (26, 63), (36, 82), True)
    leg((68, 46), (60, 63), (70, 82), True)
    b.r(36, 27, 18, 7, 'landdk', LS, rx=1.5, sw=1)
    b.ln("M40 27 L37 12", '#2E3238', 1.2); b.c(37, 12, 1.3, AMBER)
    b.r(22, 33, 50, 17, 'land', LS, rx=7)
    b.p("M70 35 L83 35 C86.5 35 88 37 88 40 L88 45 C88 47.5 86.5 48.5 84 48.5 L70 48.5 Z", 'land', LS)
    b.r(77, 37.5, 10, 6.5, 'canopy', '#1B2D40', rx=2.2, sw=.6)
    glint(b, 80, 39.3, 1.6, .7)
    b.ln("M30 41 L62 41", '#4E5F35', .9, .6)
    leds(b, [(28, 38, GREEN)])
    leg((30, 46), (22, 63), (30, 82), False)
    leg((64, 46), (56, 63), (64, 82), False)
    b.hl("M26 34.4 L68 34.4"); b.hl("M71 36.3 L83 36.3", .9, .7)

@icon('soldier', '单兵', '陆地')
def _(b):
    b.sh(48, 90, 20, 3.2)
    b.p("M33 57 L63 57 L62 87 L52 87 L48 66 L44 87 L34 87 Z", 'landdk', LS)
    b.r(32.6, 84, 12, 5, '#2A2E33', rx=1.6); b.r(51.4, 84, 12, 5, '#2A2E33', rx=1.6)
    b.p("M30 34 C33 30 40 29 48 29 C56 29 63 30 66 34 L66 58 L30 58 Z", 'land', LS)
    b.r(35, 42, 26, 15, 'landdk', LS, rx=2, sw=.9)
    b.ln("M43.6 42 L43.6 57 M52.4 42 L52.4 57", '#2E3A1C', .8, .7)
    b.r(44, 26, 8, 5, 'skin')
    b.e(48, 22, 8, 9, 'skin', '#7A5D3E', .9)
    b.p("M38.5 22 C37 13 42 8 48 8 C54 8 59 13 57.5 22 C55 20 52 19.5 48 19.5 C44 19.5 41 20 38.5 22 Z", 'land', LS)
    b.p("M36 21 C35 11 41 5 48 5 C55 5 61 11 60 21 C57 18 53 17 48 17 C43 17 39 18 36 21 Z", 'land', LS)
    b.r(40, 21, 16, 3.2, '#2E3238', rx=1.4, op=.85)
    b.ln("M30 36 L24 52 L38 55", LS, 7.2); b.ln("M30 36 L24 52 L38 55", '#86995D', 4.6)
    b.ln("M22 63 L76 30", '#15181C', 5); b.ln("M22 63 L76 30", '#3A3F46', 2.4)
    b.p("M46 49 L52 45.5 L56 52 L50.5 55 Z", '#2A2E33')
    b.ln("M66 36 L70 44 L60 41", LS, 7.2); b.ln("M66 36 L70 44 L60 41", '#86995D', 4.6)
    b.c(38.5, 55, 3, 'skin', '#7A5D3E', .7); b.c(60, 41, 3, 'skin', '#7A5D3E', .7)
    b.hl("M38 12 C40 8 44 6.4 48 6.4", 1.1, .75); b.hl("M33 32.6 C37 30.6 42 30.2 47 30.2", .9, .6)

# ================= 感知通信 =================
@icon('radar', '雷达', '感知通信')
def _(b):
    b.sh(48, 86, 30, 3.6)
    b.p("M26 86 L70 86 L64 76 L32 76 Z", 'metal2', MS)
    b.r(43, 50, 10, 27, 'cylM', MS)
    b.e(48, 50, 9, 3, 'metal', MS)
    b.ln("M30 80 A22 5 0 0 0 66 80", '#3D86D6', 1.4, .9)
    b.p("M64 80.6 L67.5 78.5 L66 82 Z", '#3D86D6')
    b.r(44, 41, 8, 8, 'metal3', MS, rx=1)
    b.ln("M24 38 L44 45 M72 38 L52 45", '#7D8996', 1.4)
    b.p("M6 26 Q48 8 90 26 L88 42 Q48 26 8 42 Z", 'metal', MS)
    b.p("M8 42 Q48 26 88 42 L88.4 38.6 Q48 22.8 7.6 38.6 Z", 'metal3', op=.8)
    for x in (20, 34, 48, 62, 76):
        b.ln(f"M{x} {28 - (5 if 20 < x < 76 else 1)} L{x} {40 - (5 if 20 < x < 76 else 1)}", '#97A3B1', .7, .7)
    b.r(14, 13.5, 68, 4, 'dkm', DS, rx=1.5, sw=.8)
    b.hl("M8 26.4 Q48 9.4 88 26.4", 1.1, .9)

@icon('phased_radar', '相控阵雷达', '感知通信')
def _(b):
    b.sh(48, 85, 42, 3.6)
    b.r(6, 66, 84, 6, 'metal3', MS, sw=1)
    b.p("M8 66 L8 52 L46 52 L46 66 Z", 'metal', MS)
    b.ln("M14 56 L40 56", '#97A3B1', .8)
    leds(b, [(14, 61, GREEN), (19, 61, AMBER)])
    b.ln("M40 52 L52 40", '#5E6A78', 3)
    b.p("M48 12 L76 6 L88 58 L60 64 Z", 'metal2', MS)
    b.p("M51 15.4 L74.4 10.4 L84.8 55.4 L61.4 60.4 Z", 'array', '#1E3550', .8)
    for t in (0.2, 0.4, 0.6, 0.8):
        b.ln(f"M{51+23.4*t:.1f} {15.4-5*t:.1f} L{61.4+23.4*t:.1f} {60.4-5*t:.1f}", '#9CC2EA', .55, .6)
        b.ln(f"M{51+10.4*t:.1f} {15.4+45*t:.1f} L{74.4+10.4*t:.1f} {10.4+45*t:.1f}", '#9CC2EA', .55, .6)
    b.p("M51.6 16 L60 14.2 L66 59.4 L61.8 60.2 Z", '#FFFFFF', op=.14)
    b.ln("M40 26 Q34 34 38 44 M32 20 Q22 34 30 50 M24 14 Q10 34 22 56", '#3D86D6', 1.6, .8)
    for x in (18, 34, 66, 80): wheel(b, x, 75, 7)
    b.hl("M49 11.4 L75.4 5.8", 1.1, .9); b.hl("M9.4 53.4 L44.6 53.4", .9, .8)

@icon('eo_turret', '光电转塔', '感知通信')
def _(b):
    b.r(28, 5, 40, 6, 'metal2', MS, rx=2)
    b.p("M36 11 L60 11 L57 24 L39 24 Z", 'metal3', MS)
    b.c(48, 55, 32, 'sphere', MS)
    b.ln("M17 52 C24 46 72 46 79 52", '#8A97A6', 1, .7)
    b.r(28, 40, 40, 32, 'canopy', '#0F2339', rx=11)
    b.c(40, 56, 9.5, 'lens', '#05101C', 1)
    b.c(59, 49.5, 5, 'lens', '#05101C', .8)
    b.c(59, 63, 4, 'lens', '#05101C', .8)
    b.c(40, 56, 4.2, 'none', '#4E86BD', .8, op=.8)
    glint(b, 37, 52.5, 2.4, 1.3); glint(b, 57.8, 47.8, 1.2, .8); glint(b, 58, 61.6, 1, .6)
    b.p("M30 44 C33 41 40 40.6 46 40.6 L34 70 C30 68 28.6 60 28.6 52 Z", '#FFFFFF', op=.1)
    b.hl("M24 37 C30 28 40 24 48 24", 1.4, .9); b.hl("M30.6 6.4 L65 6.4", .9, .8)

@icon('satellite', '卫星', '感知通信')
def _(b):
    b.g('rotate(-22 48 48)')
    for x0 in (4, 63):
        b.r(x0, 39, 29, 18, 'solar', '#14294A')
        for k in (1, 2, 3): b.ln(f"M{x0 + k*29/4:.1f} 39.5 L{x0 + k*29/4:.1f} 56.5", '#9CC2EA', .6, .6)
        b.ln(f"M{x0} 48 L{x0+29} 48", '#9CC2EA', .6, .6)
        b.p(f"M{x0+1} 40 L{x0+12} 40 L{x0+5} 56 L{x0+1} 56 Z", '#FFFFFF', op=.14)
    b.r(33, 46.6, 5, 2.8, 'metal3'); b.r(58, 46.6, 5, 2.8, 'metal3')
    b.p("M38 36 L44 31 L64 31 L58 36 Z", 'gold', '#6E5418', 1)
    b.p("M58 36 L64 31 L64 58 L58 63 Z", 'gold', '#6E5418', 1, op=None)
    b.p("M58 36 L64 31 L64 58 L58 63 Z", '#000000', op=.25)
    b.r(38, 36, 20, 27, 'gold', '#6E5418')
    b.ln("M41 42 L55 42 M41 48 L55 48 M41 54 L55 54", '#8A6A20', .6, .6)
    b.hl("M39.4 37.4 L56.6 37.4", .9, .8)
    b.ln("M48 31 L48 24", '#7D8996', 1.4)
    b.p("M38 22 Q48 30 58 22 Q48 18 38 22 Z", 'metal', MS)
    b.ln("M48 24 L48 16", '#5E6A78', 1.1); b.c(48, 15.5, 1.4, '#5E6A78')
    b.eg()

@icon('comm_tower', '通信基站', '感知通信')
def _(b):
    b.sh(50, 88, 32, 3)
    b.r(24, 84, 48, 4, 'metal2', MS, rx=1)
    b.ln("M30 84 L44 14 M66 84 L52 14", '#5E6A78', 2.6)
    b.ln("M30 84 L44 14 M66 84 L52 14", '#C9D1DA', .9)
    zz = "M31 80 L64 72 L33 64 L61 56 L36 48 L59 40 L39 32 L56 26 L42 20 L53 16"
    b.ln(zz, '#7D8996', 1)
    b.ln("M33 66 L63 66 M37 48 L59 48 M40.6 32 L55.4 32", '#7D8996', .9)
    b.r(45.5, 9, 5, 16, 'metal3', MS, rx=1)
    b.r(36.5, 12, 5.4, 16, 'metal', MS, rx=1.2)
    b.r(54.1, 12, 5.4, 16, 'metal', MS, rx=1.2)
    b.ln("M48 9 L48 3", '#5E6A78', 1.2); b.c(48, 3.5, 1.6, REDL)
    b.c(62, 42, 7, 'metal', MS); b.c(62, 42, 4.2, 'metal3'); b.c(62, 42, 1.4, '#3A4048')
    b.r(68, 70, 18, 14, 'metal', MS, rx=1.5)
    b.ln("M72 74 L82 74 M72 77 L82 77", '#97A3B1', .8)
    leds(b, [(72, 80.5, GREEN), (76, 80.5, GREEN), (80, 80.5, AMBER)])
    b.ln("M30 16 Q24 22 30 28 M24 11 Q14 22 24 33 M66 16 Q72 22 66 28 M72 11 Q82 22 72 33", '#3D86D6', 1.6, .85)

@icon('datalink', '数据链电台', '感知通信')
def _(b):
    b.sh(50, 86, 38, 3.4)
    b.p("M14 36 L26 27 L86 27 L74 36 Z", 'metal2', MS)
    b.p("M74 36 L86 27 L86 72 L74 82 Z", 'dkm2', DS)
    b.r(14, 36, 60, 46, 'dkm', DS, rx=2.5)
    b.r(20, 42, 26, 12, 'scr', '#0B1A2C', rx=1.5, sw=.8)
    b.ln("M23 50 L28 46 L32 49 L37 45 L43 47", '#7FE0A0', 1, .9)
    b.p("M21 43 L33 43 L25 53 L21 53 Z", '#FFFFFF', op=.15)
    b.c(56, 47, 5, 'sphere', '#1E2328', .8); b.ln("M56 47 L58.5 44", '#3A4048', 1.2)
    b.c(67, 47, 3.4, 'sphere', '#1E2328', .8)
    for i in range(4):
        for j in range(2):
            b.r(20 + i * 7, 60 + j * 7, 5, 4.5, 'metal3', '#1E2328', rx=.8, sw=.6)
    b.c(56, 66, 3.5, '#9AA5B2', '#1E2328', .8); b.c(56, 66, 1.5, '#3A4048')
    b.c(66, 66, 3.5, '#9AA5B2', '#1E2328', .8); b.c(66, 66, 1.5, '#3A4048')
    leds(b, [(54, 75, GREEN), (59, 75, GREEN), (64, 75, AMBER)])
    b.r(77, 26, 6, 4, 'metal3', MS, rx=1)
    b.ln("M80 27 L85 4", '#2A2E33', 2.2)
    b.ln("M86 11 Q90 14 88.5 19 M87.5 6 Q95 12 91.5 22", '#3D86D6', 1.4, .85)
    b.hl("M16 37.4 L72 37.4", .9, .55); b.hl("M17 35.4 L26.5 28.3 L85 28.3", .9, .8)

@icon('sat_station', '卫通站', '感知通信')
def _(b):
    b.sh(48, 87, 36, 3.4)
    b.p("M16 72 L26 66 L80 66 L70 72 Z", 'metal', MS)
    b.p("M70 72 L80 66 L80 80 L70 86 Z", 'metal3', MS)
    b.r(16, 72, 54, 14, 'metal2', MS, rx=1)
    b.r(22, 75, 8, 11, 'metal3', MS, sw=.8)
    leds(b, [(60, 77, GREEN), (64, 77, AMBER)])
    b.r(37, 46, 8, 22, 'cylM', MS)
    b.e(41, 47, 6, 3, 'metal3', MS)
    b.g('rotate(40 46 40)')
    b.e(46, 40, 32, 12.5, 'metal3', MS)
    b.e(46, 38.4, 30.5, 10.5, 'metal', MS, .8)
    b.e(46, 38.4, 30.5, 10.5, '#FFFFFF', op=.0)
    b.eg()
    b.ln("M22 19.5 L60 25 M70 60.5 L60 25", '#7D8996', 1.2)
    b.c(60, 25, 3, 'metal2', MS, .8)
    b.ln("M68 18 Q72 22 70 27 M72 11 Q80 20 76 30 M76 4 Q88 18 82 33", '#3D86D6', 1.6, .85)
    b.hl("M21 21 Q30 18 44 26", 1.1, .8)

@icon('mesh', '自组网', '感知通信')
def _(b):
    nodes = [(48, 14), (16, 38), (80, 36), (28, 78), (70, 78), (48, 48)]
    links = [(0, 1), (0, 2), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (1, 3), (2, 4), (3, 4)]
    for a, c_ in links:
        (x1, y1), (x2, y2) = nodes[a], nodes[c_]
        b.ln(f"M{x1} {y1} L{x2} {y2}", '#5E6A78', 3)
        b.ln(f"M{x1} {y1} L{x2} {y2}", '#C9D1DA', 1.4)
    for i, (x, y) in enumerate(nodes):
        r = 11 if i == 5 else 8.5
        b.e(x + 1.5, y + r + 1.6, r * .9, 2, 'shadow')
        b.c(x, y, r, 'node', '#1F4F8C')
        b.e(x - r * .3, y - r * .42, r * .48, r * .26, '#FFFFFF', op=.75)
    b.ln("M40 37 Q48 31 56 37 M36 33 Q48 24 60 33", '#3D86D6', 1.4, .8)

@icon('jammer', '干扰设备', '感知通信')
def _(b):
    b.sh(44, 86, 38, 3.4)
    b.p("M8 50 L18 42 L72 42 L62 50 Z", 'metal2', MS)
    b.p("M62 50 L72 42 L72 74 L62 82 Z", 'dkm2', DS)
    b.r(8, 50, 54, 32, 'dkm', DS, rx=2.5)
    for i in range(5): b.ln(f"M14 {56 + i*3.4} L34 {56 + i*3.4}", '#22272D', 1.4)
    b.r(40, 56, 16, 9, 'scr', '#0B1A2C', rx=1, sw=.6)
    b.ln("M42 61 L44 58 L46 63 L48 57.5 L50 62.5 L52 59 L54 61", '#F2A93B', .9)
    leds(b, [(42, 73, REDL), (47, 73, AMBER), (52, 73, GREEN)])
    for x, top in ((22, 18), (32, 12), (42, 18), (52, 12)):
        b.r(x - 2, 42, 4, 3, 'metal3', rx=.8)
        b.ln(f"M{x} 43 L{x} {top}", '#2A2E33', 1.8)
        b.c(x, top, 1.8, 'metal3', '#2A2E33', .6)
    b.ln("M60 22 L66 18 L64 26 L72 20 L70 28 L78 22", '#E08A2E', 1.6)
    b.ln("M62 34 L70 30 L68 38 L76 33 L74 41 L84 35", '#E08A2E', 1.6)
    b.ln("M80 14 Q88 22 84 32 M86 8 Q96 22 90 38", '#E08A2E', 1.3, .6)
    b.hl("M11 48.6 L18.6 43.3 L71 43.3", .9, .8)

# ================= 指控信息 =================
@icon('command_post', '指挥所', '指控信息')
def _(b):
    b.sh(48, 86, 40, 3.4)
    b.p("M10 42 L32 32 L86 32 L64 42 Z", 'metal', MS)
    b.p("M64 42 L86 32 L86 74 L64 84 Z", 'metal3', MS)
    b.r(10, 42, 54, 42, 'metal2', MS)
    for j in range(2):
        for i in range(4):
            b.r(14 + i * 12.5, 47 + j * 13, 9, 8, 'glass', '#25578F', rx=.6, sw=.7)
            b.p(f"M{15 + i*12.5} {48 + j*13} L{19 + i*12.5} {48 + j*13} L{16 + i*12.5} {54 + j*13} L{15 + i*12.5} {54 + j*13} Z", '#FFFFFF', op=.45)
    b.r(32, 73, 10, 11, 'dkm', DS, sw=.8)
    for k in range(2):
        b.p(f"M{68 + k*9} {48 - k*4} L{74 + k*9} {45.3 - k*4} L{74 + k*9} {53.3 - k*4} L{68 + k*9} {56 - k*4} Z", 'glass', '#25578F', .7)
        b.p(f"M{68 + k*9} {62 - k*4} L{74 + k*9} {59.3 - k*4} L{74 + k*9} {67.3 - k*4} L{68 + k*9} {70 - k*4} Z", 'glass', '#25578F', .7)
    b.ln("M48 36 L48 6 M43 12 L53 12 M44.5 18 L51.5 18", '#5E6A78', 1.4)
    b.g('rotate(-30 72 32)'); b.e(72, 30, 7, 3, 'metal', MS, 1); b.eg()
    b.ln("M72 32 L72 36", '#5E6A78', 1.4)
    b.ln("M20 38 L20 10", '#5E6A78', 1.4)
    b.p("M20.6 10 Q27 8 32 11 Q36 13.5 40 12 L40 22 Q36 23.5 32 21.5 Q27 19 20.6 21 Z", 'red', '#7A2219', .8)
    b.hl("M12 41.5 L32.4 33.2 L84 33.2", .9, .85)

@icon('gcs', '地面控制站', '指控信息')
def _(b):
    b.sh(48, 87, 40, 3.4)
    b.p("M16 12 L68 12 L70 56 L14 56 Z", 'dkm', DS)
    b.r(20, 16, 46, 34, 'scr', '#0B1A2C', rx=1.5, sw=.8)
    b.ln("M24 42 C30 34 36 40 42 30 S56 26 60 20", '#7FE0A0', 1.1, .9)
    b.p("M40 31 L44 29 L43 33 Z", '#F2A93B')
    b.ln("M26 22 L36 22 M26 25.5 L33 25.5", '#9CC2EA', .9, .7)
    b.p("M21 17 L36 17 L24 49 L21 49 Z", '#FFFFFF', op=.12)
    b.p("M10 66 L18 54 L80 54 L72 66 Z", 'metal2', MS)
    b.p("M72 66 L80 54 L80 72 L72 84 Z", 'dkm2', DS)
    b.r(10, 66, 62, 18, 'dkm', DS, rx=2)
    b.p("M30 63 L34 57 L58 57 L54 63 Z", '#3A4048', '#1E2328', .6)
    for x in (22, 66):
        b.e(x, 60, 4.4, 1.8, '#2A2E33')
        b.ln(f"M{x} 60 L{x+1} 51", '#2A2E33', 2.4)
        b.c(x + 1, 50, 2.6, 'sphere', '#1E2328', .6)
    b.r(16, 71, 20, 3, '#22272D', rx=1); b.r(16, 76, 20, 3, '#22272D', rx=1)
    leds(b, [(54, 75, GREEN), (59, 75, GREEN), (64, 75, AMBER)])
    b.ln("M78 56 L86 16", '#2A2E33', 1.8)
    b.ln("M88 22 Q92 26 90 31 M90 15 Q97 23 93.5 34", '#3D86D6', 1.4, .85)
    b.hl("M17.4 13.4 L66.6 13.4", .9, .6)

@icon('console', '指控席位', '指控信息')
def _(b):
    b.sh(48, 87, 42, 3.4)
    b.p("M6 62 L20 52 L90 52 L76 62 Z", 'metal', MS)
    b.p("M76 62 L90 52 L90 74 L76 84 Z", 'metal3', MS)
    b.r(6, 62, 70, 22, 'metal2', MS)
    b.ln("M6 66 L76 66", '#97A3B1', .8)
    b.p("M28 60 L32 56 L58 56 L54 60 Z", '#3A4048', '#1E2328', .6)
    leds(b, [(60, 74, GREEN), (65, 74, GREEN), (70, 74, AMBER)])
    b.r(12, 70, 30, 9, 'metal3', MS, rx=1, sw=.8)
    def mon(d, inner, legx):
        b.ln(f"M{legx} 54 L{legx} 46", '#3A4048', 3)
        b.p(d, 'dkm2', DS)
        b.p(inner, 'scr', '#0B1A2C', .6)
    mon("M6 20 L31 23 L31 47 L6 46 Z", "M8.5 22.8 L28.6 25.2 L28.6 44.8 L8.5 44 Z", 19)
    mon("M65 23 L90 20 L90 46 L65 47 Z", "M67.4 25.2 L87.5 22.8 L87.5 44 L67.4 44.8 Z", 77)
    mon("M32 14 L64 14 L64 46 L32 46 Z", "M34.5 16.5 L61.5 16.5 L61.5 43.5 L34.5 43.5 Z", 48)
    b.ln("M37 38 L42 30 L47 34 L53 24 L58 28", '#7FE0A0', 1.1, .9)
    b.c(53, 24, 1.4, '#F2A93B')
    b.ln("M11 30 L24 31.5 M11 34 L20 35 M70 30 L84 28.4 M70 34 L80 33", '#9CC2EA', .9, .7)
    b.r(12, 38, 6, 4, '#7FE0A0', op=.6); b.r(72, 38, 9, 3, '#F2A93B', op=.6)
    b.p("M35 17 L46 17 L37 43 L35 43 Z", '#FFFFFF', op=.12)
    b.hl("M8 61.2 L20.4 53.3 L88 53.3", .9, .85)

@icon('operator', '操作员', '指控信息')
def _(b):
    b.p("M12 92 C12 74 26 64 48 64 C70 64 84 74 84 92 Z", 'uniform', '#253A50')
    b.p("M38 64 L48 76 L58 64 Z", '#DDE5EE', '#7C8A9B', .8)
    b.p("M42 64 L48 72 L54 64 Z", '#33495F')
    b.r(41, 54, 14, 12, 'skin')
    b.e(48, 38, 16, 19, 'skin', '#7A5D3E', 1)
    b.p("M32 36 C31 22 38 16 48 16 C58 16 65 22 64 36 C61 29 56 26 48 26 C40 26 35 29 32 36 Z", '#3A3430', '#211D1A', .8)
    b.ln("M30 38 C30 12 66 12 66 38", '#22272D', 4.2)
    b.ln("M31.5 30 C33 16 63 16 64.5 30", '#5E6A78', 1.2)
    b.e(31, 41, 5.4, 7.5, 'dkm', '#15191E', .8)
    b.e(65, 41, 5.4, 7.5, 'dkm', '#15191E', .8)
    b.ln("M30 46 C30 54 36 58 44 56.5", '#22272D', 2)
    b.e(45, 56.4, 2.4, 1.8, '#22272D')
    b.c(67.5, 38, 1.2, GREEN)
    b.hl("M20 80 C24 72 32 68 40 67", 1.2, .55)

@icon('server', '服务器', '指控信息')
def _(b):
    b.sh(50, 90, 30, 3)
    b.p("M22 12 L34 5 L76 5 L64 12 Z", 'metal2', MS)
    b.p("M64 12 L76 5 L76 82 L64 90 Z", 'dkm2', DS)
    b.r(22, 12, 42, 78, 'dkm', DS, rx=2)
    for i in range(6):
        y = 17 + i * 12
        b.r(26, y, 34, 9, 'metal', MS, rx=1, sw=.8)
        b.ln(f"M29.8 {y+2.2} L29.8 {y+6.8} M32.8 {y+2.2} L32.8 {y+6.8} M35.8 {y+2.2} L35.8 {y+6.8} M38.8 {y+2.2} L38.8 {y+6.8}", '#5E6A78', 1.6)
        b.r(43, y + 3.4, 10, 2.2, '#3A4048', rx=.6)
        leds(b, [(56, y + 3, GREEN), (56, y + 6.4, AMBER if i % 3 == 1 else GREEN)])
    b.hl("M24 13.4 L34.4 6.4 L75 6.4", .9, .8)

@icon('cloud', '云平台', '指控信息')
def _(b):
    for x, y2 in ((30, 82), (48, 86), (66, 82)):
        b.ln(f"M{x} 66 L{x} {y2}", '#5E6A78', 2.6); b.ln(f"M{x} 66 L{x} {y2}", '#C9D1DA', 1)
        b.c(x, y2, 4, 'node', '#1F4F8C', .8)
        b.e(x - 1.2, y2 - 1.6, 1.8, 1, '#FFFFFF', op=.75)
    d = "M24 70 C12 70 6 62 6 53 C6 44 13 37 22 37 C24 25 34 16 46 16 C58 16 67 24 70 35 C82 35 90 43 90 53 C90 62 83 70 72 70 Z"
    b.drop(d, 2, 3, .12)
    b.p(d, 'cloud', '#5D7FA6', 1.4)
    b.p("M14 46 C16 41 20 39 25 39 C27 28 36 20 46 20 C54 20 60 24 64 31 C58 26 50 25 44 27 C36 30 31 37 30 44 C24 42 18 43 14 46 Z", '#FFFFFF', op=.7)
    b.r(30, 46, 36, 6, 'glass', '#25578F', rx=2, sw=.8)
    b.r(30, 55, 36, 6, 'glass', '#25578F', rx=2, sw=.8)
    leds(b, [(34, 49, GREEN), (34, 58, GREEN)])
    b.ln("M40 49 L60 49 M40 58 L60 58", '#FFFFFF', .9, .6)

@icon('database', '数据库', '指控信息')
def _(b):
    b.sh(48, 88, 30, 3)
    for y1, y2 in ((62, 80), (40, 58), (18, 36)):
        b.p(f"M20 {y1} L20 {y2} A28 8 0 0 0 76 {y2} L76 {y1} Z", 'cylM', MS)
        b.p(f"M20 {y2-3} A28 8 0 0 0 76 {y2-3} L76 {y2} A28 8 0 0 1 20 {y2} Z", 'glass', op=.85)
        b.e(48, y1, 28, 8, 'metal', MS)
        leds(b, [(66, y1 + 11.5, GREEN), (71, y1 + 10.5, AMBER if y1 == 40 else GREEN)])
    b.e(48, 18, 18, 4.4, '#FFFFFF', op=.45)
    b.hl("M23.5 23 L23.5 33 M23.5 45 L23.5 55 M23.5 67 L23.5 77", 1.1, .8)

@icon('ai_agent', '智能体', '指控信息')
def _(b):
    b.ln("M48 16 L48 7", '#5E6A78', 2)
    b.c(48, 6, 3.2, 'glow'); b.c(48, 6, 1.8, '#9AD4FF')
    b.p("M20 92 C20 80 31 74 48 74 C65 74 76 80 76 92 Z", 'metal2', MS)
    b.r(41, 66, 14, 9, 'metal3', MS, sw=1)
    b.r(9, 32, 10, 20, 'metal3', MS, rx=3)
    b.r(77, 32, 10, 20, 'metal3', MS, rx=3)
    b.r(17, 15, 62, 54, 'metal', MS, rx=15)
    b.r(25, 29, 46, 26, 'canopy', '#0F2339', rx=11)
    b.e(38, 42, 7, 4.5, 'glow'); b.e(58, 42, 7, 4.5, 'glow')
    b.r(33, 40.4, 10, 3.2, '#D8F0FF', rx=1.6); b.r(53, 40.4, 10, 3.2, '#D8F0FF', rx=1.6)
    b.p("M28 33 C31 30.5 36 30 44 30 L32 53 C28 51 26 46 26 41 Z", '#FFFFFF', op=.12)
    b.r(42, 80, 12, 7, 'glass', '#25578F', rx=1.5, sw=.8)
    b.ln("M54 83.5 L62 83.5 M42 83.5 L34 83.5", '#3D86D6', 1, .8)
    b.hl("M22 28 C23 21 27 17 33 16.4", 1.3, .9)

@icon('security', '安全防护', '指控信息')
def _(b):
    d = "M48 6 L82 18 L80 46 C78 66 66 80 48 90 C30 80 18 66 16 46 L14 18 Z"
    b.drop(d, 2, 3, .14)
    b.p(d, 'metal', MS, 1.4)
    b.p("M48 14 L74 23.5 L72.4 46 C70.6 62 61 73 48 81 C35 73 25.4 62 23.6 46 L22 23.5 Z", 'glass', '#25578F', 1)
    b.p("M48 14 L74 23.5 L73.3 33 C62 30 50 34 22.7 40 L22 23.5 Z", '#FFFFFF', op=.22)
    b.ln("M40 47 L40 40 C40 32 56 32 56 40 L56 47", '#E9EEF3', 4.2, cap='butt')
    b.ln("M40 47 L40 40 C40 32 56 32 56 40 L56 47", '#97A3B1', 1.4, cap='butt', op=.6)
    b.r(35, 46, 26, 20, 'metal', MS, rx=3)
    b.c(48, 54, 3, '#2A3038'); b.p("M46.6 55 L49.4 55 L50.2 61 L45.8 61 Z", '#2A3038')
    b.hl("M17 20 L48 9 M17.5 24 L18.5 46", 1.2, .9)

@icon('app', '应用', '指控信息')
def _(b):
    b.e(50, 86, 34, 3.4, 'shadow')
    b.r(10, 8, 76, 76, 'appbg', '#1E4B82', rx=18, sw=1.4)
    b.p("M28 9.4 L68 9.4 C78 9.4 84.6 16 84.6 26 L84.6 34 C66 30 34 30 11.4 40 L11.4 26 C11.4 16 18 9.4 28 9.4 Z", '#FFFFFF', op=.2)
    for i, (x, y) in enumerate(((22, 20), (52, 20), (22, 50), (52, 50))):
        b.r(x + 1, y + 2, 22, 22, '#0F2A4F', rx=6, op=.35)
        if i == 3:
            b.c(x + 11, y + 11, 11, 'metal', '#C9D1DA', .8)
            b.c(x + 11, y + 11, 4, 'glass')
        else:
            b.r(x, y, 22, 22, 'metal', '#C9D1DA', rx=6, sw=.8)
            b.r(x + 6, y + 6, 10, 10, 'glass' if i != 1 else 'orange', rx=2.5)

@icon('switch', '网络交换机', '指控信息')
def _(b):
    b.sh(48, 70, 42, 3)
    cols = ['#3D86D6', '#43C46B', '#F2A93B', '#3D86D6', '#43C46B']
    for k, (x, c_) in enumerate(zip((16, 27, 38, 49, 60), cols)):
        b.ln(f"M{x+2} 58 C{x+2} 72 {x-6 + k*4} 74 {x-6 + k*4} 90", '#2A2E33', 3.4)
        b.ln(f"M{x+2} 58 C{x+2} 72 {x-6 + k*4} 74 {x-6 + k*4} 90", c_, 2)
    b.p("M5 40 L15 30 L91 30 L81 40 Z", 'metal', MS)
    b.p("M81 40 L91 30 L91 50 L81 60 Z", 'metal3', MS)
    b.r(5, 40, 76, 20, 'metal2', MS, rx=1.5)
    for y in (46.2, 53.2):
        b.ln(f"M9 {y} L64.4 {y}", '#1E2328', 4.4, cap='butt', extra="stroke-dasharray='4.4 1.2'")
        b.ln(f"M9.8 {y-.8} L64.4 {y-.8}", '#5A626C', 1.1, cap='butt', extra="stroke-dasharray='2.8 2.8'")
    leds(b, [(9 + i * 5.6 + 2.2, 42.2, GREEN if i % 4 else AMBER) for i in range(0, 10, 2)])
    b.r(67, 45, 10, 4.5, '#1E2328', rx=.6); b.r(67, 51, 10, 4.5, '#1E2328', rx=.6)
    b.r(68.5, 46.2, 7, 2, '#3D86D6', op=.8); b.r(68.5, 52.2, 7, 2, '#3D86D6', op=.8)
    b.hl("M7 39.3 L15.5 31.2 L89.6 31.2", .9, .85)


KEYS = """fighter bomber transport awacs helicopter uav_fixed uav_male uav_quad uav_vtol loitering cruise_missile ballistic_missile
carrier destroyer frigate patrol_boat missile_boat usv submarine uuv sonar_buoy
tank ifv sp_howitzer towed_gun mlrs tel sam truck ugv robodog soldier
radar phased_radar eo_turret satellite comm_tower datalink sat_station mesh jammer
command_post gcs console operator server cloud database ai_agent security app switch""".split()

byk = {k: (k, n, c, fn) for k, n, c, fn in ICONS}
assert set(byk) == set(KEYS), set(KEYS) ^ set(byk)
SZ=[]
lines = ['const ICON_LIB = [']
for k in KEYS:
    _, n, c, fn = byk[k]
    b = B(k); fn(b)
    s = b.svg()
    import re as _re
    s = _re.sub(r'(\d+\.\d{2,})', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), s)
    s = _re.sub(r"(?<=[ '])0\.(\d)", r'.\1', s)
    assert '"' not in s
    SZ.append((len(s),k))
    lines.append(f"  {{ key: '{k}', name: '{n}', cat: '{c}', svg: \"{s}\" }},")
lines.append('];')
lines.append("if (typeof module !== 'undefined') module.exports = ICON_LIB;")
open('/home/claude/drawtool/icons.js', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('ok', len(KEYS), sorted(SZ)[-5:])
