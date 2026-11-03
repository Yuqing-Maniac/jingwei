"""Opening a PNG loads a diagram, and a blank picture does not."""
import os
import sys
import pathlib
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
TMP = pathlib.Path('/tmp/imgimport-open')
fails = []


def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))


def write_images():
    TMP.mkdir(parents=True, exist_ok=True)
    blank = Image.new('RGB', (220, 140), 'white')
    blank.save(TMP / 'blank.png')
    rect = Image.new('RGB', (220, 140), 'white')
    draw = ImageDraw.Draw(rect)
    draw.rectangle((40, 30, 180, 110), outline=(36, 48, 68), width=3)
    rect.save(TMP / 'shore.png')


write_images()

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
    page.wait_for_timeout(500)
    before = page.evaluate("""() => ({
      name: doc.name,
      n: P().nodes.length,
      undo: (typeof undoS !== 'undefined') ? undoS.length : -1
    })""")
    page.set_input_files('#f-open', str(TMP / 'blank.png'))
    page.wait_for_function("() => (document.getElementById('toast').textContent || '').indexOf('没有识别到') >= 0", timeout=8000)
    after_blank = page.evaluate("""() => ({
      name: doc.name,
      n: P().nodes.length,
      undo: (typeof undoS !== 'undefined') ? undoS.length : -1,
      toast: document.getElementById('toast').textContent
    })""")
    page.set_input_files('#f-open', str(TMP / 'shore.png'))
    page.wait_for_function("() => (document.getElementById('toast').textContent || '').indexOf('已导入') === 0", timeout=8000)
    after = page.evaluate("""() => ({
      name: doc.name,
      n: P().nodes.length,
      types: P().nodes.map(n => n.type),
      toast: document.getElementById('toast').textContent,
      accept: document.getElementById('f-open').accept
    })""")
    browser.close()

check('no page errors', not errs, str(errs[:2]))
check('blank picture does not replace the document', after_blank['name'] == before['name'] and after_blank['n'] == before['n'], str(after_blank))
check('blank picture does not checkpoint', after_blank['undo'] == before['undo'], 'undo %s -> %s' % (before['undo'], after_blank['undo']))
check('blank picture says nothing was found', '没有识别到可编辑的框图' in after_blank['toast'], after_blank['toast'])
check('imported toast starts with 已导入', after['toast'].startswith('已导入'), after['toast'])
check('imported picture becomes the document', after['name'] == 'shore' and after['n'] >= 1 and 'rect' in after['types'], str(after))
check('open dialog accepts png and jpeg', '.png' in after['accept'] and '.jpg' in after['accept'] and '.jpeg' in after['accept'], after['accept'])

if fails:
    print('FAILED', len(fails))
    for item in fails:
        print(' -', item)
    sys.exit(1)
print('imgimport_open ok')
