"""ImgImport.read returns 巡逻 drawn in Noto Sans CJK SC."""
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
    page.on('pageerror', lambda e: errs.append(str(e)[:400]))
    page.goto(HTML)
    page.wait_for_timeout(400)
    got = page.evaluate(r"""async () => {
      if (document.fonts && document.fonts.load) {
        await document.fonts.load('64px "Noto Sans CJK SC"');
      }
      const c = document.createElement('canvas');
      c.width = 320;
      c.height = 160;
      const g = c.getContext('2d');
      g.fillStyle = '#ffffff';
      g.fillRect(0, 0, c.width, c.height);
      g.fillStyle = '#243044';
      g.font = '64px "Noto Sans CJK SC"';
      g.textBaseline = 'top';
      g.fillText('巡逻', 36, 40);
      const draft = ImgImport.read(g.getImageData(0, 0, c.width, c.height));
      const texts = draft.page.nodes.map(n => n.text || '');
      return {
        book: window.__imgBook === undefined,
        font: !!(document.fonts && document.fonts.check && document.fonts.check('64px "Noto Sans CJK SC"')),
        texts: texts,
        nodes: draft.page.nodes.map(n => ({ type: n.type, text: n.text || '', font: n.font || '', bold: !!n.bold })),
        notes: draft.notes
      };
    }""")
    browser.close()

check('no page errors', not errs, str(errs[:2]))
check('glyph book leaves the global', got['book'], str(got['book']))
joined = ''.join(got['texts'])
check('canvas 巡逻 comes back as 巡逻', joined == '巡逻', str(got))

if fails:
    print('FAILED', len(fails))
    for item in fails:
        print(' -', item)
    sys.exit(1)
print('imgimport_glyph ok')
