"""Photograph the review dialog and the canvas after import for each shapes2 image."""
import os
import pathlib
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / 'tests' / 'fixtures' / 'shapes2'
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
OUT = pathlib.Path('/opt/cursor/artifacts/shapes2')
KEYS = ['poly', 'rounds', 'flowmisc', 'arrows', 'sizes', 'extra']
FONT = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 28, index=2)


def chrome():
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox', '--disable-gpu', '--disable-features=Translate']}
    if exe:
        kw['executable_path'] = exe
    return kw


def review_state(page):
    return page.evaluate("""() => ({
      nodes: [...document.querySelectorAll('#ir-svg [data-kind="node"]')].map(n => ({
        id: n.getAttribute('data-id'),
        text: n.querySelector('text') ? n.querySelector('text').textContent : ''
      })),
      links: [...document.querySelectorAll('#ir-svg [data-kind="link"]')].map(n => ({
        id: n.getAttribute('data-id'),
        from: n.getAttribute('data-from'),
        to: n.getAttribute('data-to'),
        dir: n.getAttribute('data-dir')
      }))
    })""")


def nid(nodes, prefix):
    for n in nodes:
        if (n['text'] or '').startswith(prefix):
            return n['id']
    raise RuntimeError('missing ' + prefix + ' ' + str(nodes))


def drag(page, link_id, end, node_id):
    handle = page.locator('#ir-svg [data-kind="handle"][data-end="%s"][data-id="%s"]' % (end, link_id))
    dest = page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % node_id)
    hb = handle.bounding_box()
    db = dest.bounding_box()
    page.mouse.move(hb['x'] + hb['width'] / 2, hb['y'] + hb['height'] / 2)
    page.mouse.down()
    page.mouse.move(db['x'] + db['width'] / 2, db['y'] + db['height'] / 2, steps=14)
    page.mouse.up()
    page.wait_for_timeout(100)


def correct_arrows(page):
    state = review_state(page)
    nodes = state['nodes']
    want = {
        '甲': nid(nodes, '甲'), '乙': nid(nodes, '乙'), '丙': nid(nodes, '丙'), '丁': nid(nodes, '丁'),
        '起': nid(nodes, '起'), '终': nid(nodes, '终'), '折起': nid(nodes, '折起'), '折落': nid(nodes, '折落'),
    }
    merged = None
    for link in state['links']:
        ends = {link['from'], link['to']}
        if ends == {want['乙'], want['丁']}:
            merged = link
    if not merged:
        raise RuntimeError('merged crossing link not found ' + str(state['links']))
    page.locator('#ir-svg [data-kind="link"][data-id="%s"]' % merged['id']).dispatch_event('click')
    end = 'to' if merged['to'] == want['丁'] else 'from'
    drag(page, merged['id'], end, want['丙'])
    page.click('#ir-split')
    page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % want['甲']).click()
    page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % want['丁']).click()
    page.click('#ir-link')
    page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % want['起']).click()
    page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % want['终']).click()
    page.select_option('#ir-dir', 'both')
    page.click('#ir-link')
    page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % want['折起']).click()
    page.locator('#ir-svg [data-kind="node"][data-id="%s"]' % want['折落']).click()


def paste(left, right, left_label, right_label, dest):
    H = 860
    def fit(im):
        r = H / im.height
        return im.resize((max(1, round(im.width * r)), H), Image.Resampling.LANCZOS)
    a, b = fit(Image.open(left).convert('RGB')), fit(Image.open(right).convert('RGB'))
    gap, header = 16, 52
    canvas = Image.new('RGB', (a.width + gap + b.width, H + header), (244, 246, 248))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 12), left_label, fill=(27, 36, 51), font=FONT)
    draw.text((a.width + gap + 12, 12), right_label, fill=(27, 36, 51), font=FONT)
    canvas.paste(a, (0, header))
    canvas.paste(b, (a.width + gap, header))
    canvas.save(dest)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / '_raw'
    raw.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **chrome())
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        page.goto(HTML)
        page.wait_for_timeout(400)
        for key in KEYS:
            page.set_input_files('#f-open', str(FIX / (key + '.png')))
            page.wait_for_function("() => document.getElementById('img-review').style.display === 'flex'", timeout=30000)
            page.wait_for_timeout(250)
            before = raw / (key + '-review.png')
            page.locator('#img-review').screenshot(path=str(before))
            if key == 'arrows':
                correct_arrows(page)
                after = raw / 'arrows-corrected.png'
                page.locator('#img-review').screenshot(path=str(after))
                paste(before, after, '交叉箭头  修正前', '修正后', OUT / 'arrows-fix.png')
            page.click('#ir-ok')
            page.wait_for_function("() => document.getElementById('img-review').style.display === 'none'")
            page.wait_for_timeout(300)
            stage = raw / (key + '-stage.png')
            page.locator('#stage').screenshot(path=str(stage))
            paste(before, stage, key + '  原图与识别', '校对后导入', OUT / (key + '.png'))
            if key == 'arrows':
                canvas = page.evaluate("""() => P().links.map(l => {
                  const name = id => { const n = P().nodes.find(x => x.id === id); return n ? n.text : id; };
                  return name(l.from) + '->' + name(l.to) + ' ' + (l.dir || 'one');
                })""")
                print('arrows canvas', canvas)
        browser.close()
    print('wrote', OUT)


if __name__ == '__main__':
    main()
