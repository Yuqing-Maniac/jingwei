"""ImgImport.read on three canvases drawn in the page."""
import os
import sys
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
fails = []


def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))


def iou(a, b):
    x0 = max(a['x'], b['x'])
    y0 = max(a['y'], b['y'])
    x1 = min(a['x'] + a['w'], b['x'] + b['w'])
    y1 = min(a['y'] + a['h'], b['y'] + b['h'])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    union = a['w'] * a['h'] + b['w'] * b['h'] - inter
    return inter / union if union else 0


def box_of(nodes, expect):
    best, score = None, 0
    for n in nodes:
        if n['type'] != expect['type']:
            continue
        s = iou(n, expect)
        if s > score:
            best, score = n, s
    return best, score


DRAW = r"""() => {
  function canvas(w, h, draw) {
    const c = document.createElement('canvas');
    c.width = w;
    c.height = h;
    const g = c.getContext('2d');
    g.fillStyle = '#ffffff';
    g.fillRect(0, 0, w, h);
    g.strokeStyle = '#243044';
    g.fillStyle = '#243044';
    g.lineWidth = 3;
    g.lineJoin = 'miter';
    g.lineCap = 'butt';
    draw(g);
    const draft = ImgImport.read(g.getImageData(0, 0, w, h));
    return {
      nodes: draft.page.nodes.map(n => ({
        id: n.id, type: n.type, x: n.x, y: n.y, w: n.w, h: n.h, text: n.text || ''
      })),
      links: draft.page.links.map(l => ({
        id: l.id, from: l.from, to: l.to, dir: l.dir, route: l.route || ''
      }))
    };
  }
  const rect = canvas(220, 140, g => { g.strokeRect(40, 30, 140, 80); });
  const diamond = canvas(240, 160, g => {
    g.beginPath();
    g.moveTo(120, 20);
    g.lineTo(200, 80);
    g.lineTo(120, 140);
    g.lineTo(40, 80);
    g.closePath();
    g.stroke();
  });
  const arrow = canvas(320, 140, g => {
    g.strokeRect(20, 40, 80, 50);
    g.strokeRect(210, 40, 80, 50);
    g.beginPath();
    g.moveTo(100, 65);
    g.lineTo(210, 65);
    g.stroke();
    g.beginPath();
    g.moveTo(210, 65);
    g.lineTo(196, 56);
    g.lineTo(196, 74);
    g.closePath();
    g.fill();
  });
  return { rect, diamond, arrow };
}"""

with sync_playwright() as pw:
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox']}
    if exe:
        kw['executable_path'] = exe
    browser = pw.chromium.launch(**kw)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:300]))
    page.goto(HTML)
    page.wait_for_timeout(400)
    got = page.evaluate(DRAW)
    browser.close()

check('no page errors', not errs, str(errs[:2]))

rect_n, rect_iou = box_of(got['rect']['nodes'], {'type': 'rect', 'x': 40, 'y': 30, 'w': 140, 'h': 80})
check('stroked rectangle is one rect', len(got['rect']['nodes']) == 1 and rect_n and rect_n['type'] == 'rect', str(got['rect']['nodes']))
check('stroked rectangle iou at least 0.5', rect_iou >= 0.5, 'iou %.3f' % rect_iou)
check('stroked rectangle has no link', got['rect']['links'] == [], str(got['rect']['links']))

dia_n, dia_iou = box_of(got['diamond']['nodes'], {'type': 'diamond', 'x': 40, 'y': 20, 'w': 160, 'h': 120})
check('stroked diamond is one diamond', len(got['diamond']['nodes']) == 1 and dia_n and dia_n['type'] == 'diamond', str(got['diamond']['nodes']))
check('stroked diamond iou at least 0.5', dia_iou >= 0.5, 'iou %.3f' % dia_iou)

left, left_iou = box_of(got['arrow']['nodes'], {'type': 'rect', 'x': 20, 'y': 40, 'w': 80, 'h': 50})
right, right_iou = box_of(got['arrow']['nodes'], {'type': 'rect', 'x': 210, 'y': 40, 'w': 80, 'h': 50})
check('arrow joins two rects', len(got['arrow']['nodes']) == 2 and left and right and left['id'] != right['id'], str(got['arrow']['nodes']))
check('arrow source rect iou at least 0.5', left_iou >= 0.5, 'iou %.3f' % left_iou)
check('arrow target rect iou at least 0.5', right_iou >= 0.5, 'iou %.3f' % right_iou)
links = got['arrow']['links']
one = links[0] if len(links) == 1 else None
check('arrow is one link with dir one', bool(one) and one['dir'] == 'one', str(links))
if one and left and right:
    check('arrow points from the left rect to the right rect', one['from'] == left['id'] and one['to'] == right['id'], str(one))

if fails:
    print('FAILED', len(fails))
    for item in fails:
        print(' -', item)
    sys.exit(1)
print('imgimport_synth ok')
