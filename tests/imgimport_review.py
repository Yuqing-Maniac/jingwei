"""Corrections in the import review are what land on the canvas. Cancel writes nothing."""
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


def open_sample(page):
    page.evaluate("""() => {
      const c = document.createElement('canvas');
      c.width = 400; c.height = 240;
      const g = c.getContext('2d');
      g.fillStyle = '#fff';
      g.fillRect(0, 0, 400, 240);
      const url = c.toDataURL('image/png');
      const page0 = {
        id: 'root', name: '总图',
        nodes: [
          mkNode({ id: 'a', type: 'group', text: '□基□', x: 20, y: 20, w: 200, h: 160 }),
          mkNode({ id: 'b', type: 'rect', text: '雷达', parent: 'a', x: 40, y: 60, w: 80, h: 40 }),
          mkNode({ id: 'c', type: 'rect', text: '海上', x: 260, y: 80, w: 80, h: 40 })
        ],
        links: [{ id: 'k0', from: 'b', to: 'a', dir: 'one', route: 'ortho', label: '' }]
      };
      showImageReview({ name: '校对', url: url, width: 400, height: 240, page: page0, notes: [] });
    }""")
    page.wait_for_function("() => document.getElementById('img-review').style.display === 'flex'")


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
    before = page.evaluate("""() => ({ name: doc.name, n: P().nodes.length, undo: undoS.length })""")
    open_sample(page)
    page.locator('#ir-svg [data-kind="node"][data-id="a"]').click(position={'x': 28, 'y': 8})
    seen = page.input_value('#ir-text')
    page.fill('#ir-text', '岸基站')
    preview = page.locator('#ir-svg [data-kind="node"][data-id="a"] text').text_content()
    page.locator('#ir-svg [data-kind="link"][data-id="k0"]').dispatch_event('click')
    page.click('#ir-del')
    page.click('#ir-link')
    page.locator('#ir-svg [data-kind="node"][data-id="b"]').click()
    page.locator('#ir-svg [data-kind="node"][data-id="c"]').click()
    page.click('#ir-add')
    page.locator('#ir-svg').click(position={'x': 16, 'y': 16})
    page.locator('#ir-svg [data-kind="node"][data-id="c"]').click()
    page.select_option('#ir-parent', 'a')
    still = page.evaluate("""() => ({ name: doc.name, n: P().nodes.length, undo: undoS.length })""")
    page.click('#ir-ok')
    page.wait_for_function("() => doc.name === '校对'")
    after = page.evaluate("""() => ({
      name: doc.name,
      nodes: P().nodes.map(n => ({ id: n.id, type: n.type, text: n.text, parent: n.parent || null })),
      links: P().links.map(l => ({ id: l.id, from: l.from, to: l.to, dir: l.dir || 'one' })),
      toast: document.getElementById('toast').textContent
    })""")
    snap = page.evaluate("""() => ({ name: doc.name, n: P().nodes.length, undo: undoS.length })""")
    open_sample(page)
    page.click('#ir-cancel')
    page.wait_for_function("() => document.getElementById('img-review').style.display === 'none'")
    later = page.evaluate("""() => ({
      name: doc.name,
      n: P().nodes.length,
      undo: undoS.length,
      toast: document.getElementById('toast').textContent
    })""")
    browser.close()

nodes = {n['id']: n for n in after['nodes']}
links = after['links']
added = [l for l in links if l['from'] == 'b' and l['to'] == 'c']
check('no page errors', not errs, str(errs[:2]))
check('selected title shows the recognition', seen == '□基□', seen)
check('preview shows the corrected title', preview == '岸基站', preview)
check('canvas stays unchanged until import', still['name'] == before['name'] and still['n'] == before['n'] and still['undo'] == before['undo'], str(still))
check('imported name is the reviewed file', after['name'] == '校对', after['name'])
check('corrected title is on the canvas', nodes.get('a', {}).get('text') == '岸基站' and nodes.get('a', {}).get('type') == 'group', str(nodes.get('a')))
check('deleted link is gone', all(l['id'] != 'k0' for l in links) and len(links) == 1, str(links))
check('new arrow matches the correction', len(added) == 1 and added[0]['dir'] == 'one', str(links))
check('added shape is on the canvas', sum(1 for n in after['nodes'] if n['text'] == '新框' and n['type'] == 'rect') == 1, str(after['nodes']))
check('grouping matches the correction', nodes.get('c', {}).get('parent') == 'a', str(nodes.get('c')))
check('import toast starts with 已导入', after['toast'].startswith('已导入'), after['toast'])
check('cancel keeps the document', later['name'] == snap['name'] and later['n'] == snap['n'], str(later))
check('cancel does not checkpoint', later['undo'] == snap['undo'], 'undo %s -> %s' % (snap['undo'], later['undo']))
check('cancel says it was cancelled', '已取消导入' in later['toast'], later['toast'])

if fails:
    print('FAILED', len(fails))
    for item in fails:
        print(' -', item)
    sys.exit(1)
print('imgimport_review ok')
