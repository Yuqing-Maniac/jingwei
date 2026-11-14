#!/usr/bin/env python3
"""新建默认：只影响之后新建的图形和连线，套用才改已有对象。"""
import os
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
fails = []


def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))


def launch(pw):
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/opt/pw-browsers/chromium-1097/chrome-linux/chrome'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox']}
    if exe:
        kw['executable_path'] = exe
    return pw.chromium.launch(**kw)


DOC = """{
  name: '试验', theme: 'report', custom: {},
  statusLabels: { base: '延续', new: '本步新增', key: '重点' },
  pages: { root: { id: 'root', name: '总图', nodes: nodes, links: links } }
}"""


def main():
    with sync_playwright() as pw:
        browser = launch(pw)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        pg.goto(HTML)
        pg.wait_for_selector('#svg')
        pg.wait_for_timeout(200)

        seeded = pg.evaluate("""() => {
          const icon = 'lib:' + ICON_LIB[0].key;
          const kept = mkNode({ type: 'equip', text: '旧装备', icon: icon, x: 40, y: 40, w: 96, h: 96 });
          const box = mkNode({ type: 'round', text: '旧框', x: 200, y: 40, w: 120, h: 40, fill: '#112233' });
          const title = mkNode({ type: 'text', role: 'title', text: '标题', size: 22, bold: true, x: 40, y: -40, w: 200, h: 32 });
          const band = mkNode({ type: 'band', text: '分组', x: 40, y: 160, w: 400, h: 120 });
          const nodes = [kept, box, title, band];
          const links = [{ id: 'old', from: kept.id, to: box.id, dir: 'one', route: 'ortho', kind: 'data', label: '' }];
          loadDoc(%s);
          clearSel();
          render();
          return {
            icon: icon,
            panel: document.getElementById('props').textContent,
            selBtn: !!document.getElementById('gd-sel'),
            pageBtn: !!document.getElementById('gd-page'),
            kept: { noBox: kept.noBox, affiliation: kept.affiliation || 'neutral', size: kept.size },
            box: box.fill,
            title: { size: title.size, bold: title.bold }
          };
        }""" % DOC)
        check('empty canvas shows 新建默认', '新建默认' in seeded['panel'] and seeded['pageBtn'] is True, seeded['panel'][:120])
        check('apply-to-selection stays off the empty panel', seeded['selBtn'] is False, str(seeded['selBtn']))

        pg.click('#gd-box button[data-v="1"]')
        pg.click('#gd-side button[data-v="red"]')
        pg.select_option('#gd-size', '14')
        pg.click('#gd-dir button[data-v="both"]')
        pg.click('#gd-route button[data-v="straight"]')
        pg.wait_for_timeout(50)

        made = pg.evaluate("""() => {
          const icon = 'lib:' + ICON_LIB[0].key;
          const before = P().nodes.map(n => n.id);
          addNode(iconPlaceSpec(icon, '新装备', 96, 96), 480, 80);
          const born = P().nodes.find(n => before.indexOf(n.id) < 0);
          const explicit = iconPlaceSpec(icon, '写明带框', 96, 96);
          explicit.noBox = false;
          addNode(explicit, 480, 200);
          const framed = P().nodes[P().nodes.length - 1];
          addNode({ type: 'text', w: 160, h: 30, text: '文字', size: 16 }, 480, 280);
          const label = P().nodes[P().nodes.length - 1];
          addNode({ type: 'rect', w: 100, h: 40, text: '新矩形' }, 640, 80);
          const rect = P().nodes[P().nodes.length - 1];
          const kept = P().nodes.find(n => n.text === '旧装备');
          const box = P().nodes.find(n => n.text === '旧框');
          const link = { id: 'new', from: kept.id, to: box.id, dir: 'one', route: 'ortho', kind: 'data', label: '' };
          JwDefaults.stampLink(link);
          return {
            born: { noBox: born.noBox, affiliation: born.affiliation || '', size: born.size, font: born.font || '' },
            framed: framed.noBox,
            label: label.size,
            rect: { fill: rect.fill || '', stroke: rect.stroke || '' },
            kept: { noBox: kept.noBox, affiliation: kept.affiliation || 'neutral' },
            box: box.fill,
            link: { dir: link.dir, route: link.route },
            pref: localStorage.getItem('hongtu.defaults')
          };
        }""")
        check('new icon uses unframed red and 四号', made['born']['noBox'] is True and made['born']['affiliation'] == 'red' and made['born']['size'] == 14, str(made['born']))
        check('explicit frame on the palette spec wins', made['framed'] is False, str(made['framed']))
        check('text tool keeps its own size', made['label'] == 16, str(made['label']))
        check('existing icon and fill stay put', made['kept']['noBox'] is False and made['kept']['affiliation'] == 'neutral' and made['box'] == '#112233', str(made))
        check('new link uses both and straight', made['link']['dir'] == 'both' and made['link']['route'] == 'straight', str(made['link']))
        check('preference key is hongtu.defaults', made['pref'] and '"noBox":true' in made['pref'].replace(' ', ''), made['pref'])

        pg.evaluate("""() => { clearSel(); render(); }""")
        pg.wait_for_timeout(40)
        pg.evaluate("""() => {
          const el = document.getElementById('gd-fill');
          el.value = '#ff00aa';
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }""")
        pg.wait_for_timeout(40)
        filled = pg.evaluate("""() => {
          const before = P().nodes.map(n => n.id);
          addNode({ type: 'round', w: 80, h: 36, text: '着色' }, 640, 180);
          const n = P().nodes.find(x => before.indexOf(x.id) < 0);
          const old = P().nodes.find(x => x.text === '旧框');
          return { fill: n.fill, old: old.fill };
        }""")
        check('new shape takes the default fill', filled['fill'] == '#ff00aa' and filled['old'] == '#112233', str(filled))

        pg.evaluate("""() => { selectNodes([P().nodes.find(n => n.text === '旧装备').id]); render(); }""")
        pg.wait_for_timeout(40)
        check('selection offers 套用新建默认', pg.locator('#gd-sel').count() == 1)
        depth = pg.evaluate('() => undoS.length')
        pg.click('#gd-sel')
        pg.wait_for_timeout(40)
        applied = pg.evaluate("""() => {
          const kept = P().nodes.find(n => n.text === '旧装备');
          const box = P().nodes.find(n => n.text === '旧框');
          const title = P().nodes.find(n => n.role === 'title');
          const framed = P().nodes.find(n => n.text === '写明带框');
          return {
            kept: { noBox: kept.noBox, affiliation: kept.affiliation },
            box: box.fill,
            framed: framed.noBox,
            title: { size: title.size, bold: title.bold }
          };
        }""")
        check('apply selection rewrites only that icon', applied['kept']['noBox'] is True and applied['kept']['affiliation'] == 'red' and applied['box'] == '#112233' and applied['framed'] is False, str(applied))
        check('title is outside the text default', applied['title']['size'] == 22 and applied['title']['bold'] is True, str(applied['title']))
        check('apply selection is one undo step', pg.evaluate('() => undoS.length') == depth + 1, str(depth))
        pg.keyboard.press('Control+z')
        pg.wait_for_timeout(80)
        undone = pg.evaluate("""() => {
          const kept = P().nodes.find(n => n.text === '旧装备');
          return { noBox: kept.noBox, affiliation: kept.affiliation || 'neutral' };
        }""")
        check('undo restores the icon', undone['noBox'] is False and undone['affiliation'] == 'neutral', str(undone))
        pg.keyboard.press('Control+y')
        pg.wait_for_timeout(80)

        pg.evaluate("""() => {
          clearSel();
          const title = P().nodes.find(n => n.role === 'title');
          title.text = '标题改';
          render();
          undo();
        }""")
        pg.wait_for_timeout(40)
        noop = pg.evaluate("""() => {
          selectNodes([P().nodes.find(n => n.role === 'title').id]);
          render();
          return { redo: redoS.length, text: P().nodes.find(n => n.role === 'title').text };
        }""")
        check('undone title edit is still redoable', noop['redo'] == 1 and noop['text'] == '标题', str(noop))
        pg.click('#gd-sel')
        pg.wait_for_timeout(40)
        kept_redo = pg.evaluate("""() => {
          redo();
          const title = P().nodes.find(n => n.role === 'title');
          return { text: title.text, redo: redoS.length };
        }""")
        check('no-op apply keeps the redo stack', kept_redo['text'] == '标题改', str(kept_redo))
        pg.evaluate('() => { undo(); clearSel(); render(); }')
        pg.wait_for_timeout(40)
        pg.click('#gd-page')
        pg.wait_for_timeout(40)
        page = pg.evaluate("""() => {
          const box = P().nodes.find(n => n.text === '旧框');
          const band = P().nodes.find(n => n.type === 'band');
          const title = P().nodes.find(n => n.role === 'title');
          const link = P().links.find(l => l.id === 'old');
          return { box: box.fill, band: band.fill || '', title: title.size, dir: link.dir, route: link.route };
        }""")
        check('apply page rewrites the old box and the old link', page['box'] == '#ff00aa' and page['dir'] == 'both' and page['route'] == 'straight', str(page))
        check('apply page leaves the band and the title', page['band'] == '' and page['title'] == 22, str(page))

        pg.reload()
        pg.wait_for_selector('#svg')
        pg.wait_for_timeout(150)
        pg.evaluate('() => { clearSel(); render(); }')
        held = pg.evaluate("""() => ({
          on: document.querySelector('#gd-box button.on').textContent,
          side: document.querySelector('#gd-side button.on').textContent,
          size: document.getElementById('gd-size').value
        })""")
        check('defaults survive reload', held['on'] == '不带框' and held['side'] == '红方' and held['size'] == '14', str(held))
        check('no page errors', not errs, str(errs[:2]))
        browser.close()
    if fails:
        print('FAILED', len(fails))
        for f in fails:
            print(' -', f)
        raise SystemExit(1)
    print('all defaults checks passed')


if __name__ == '__main__':
    main()
