"""作战场景模板：画廊分组、渲染、保存再打开、导出。"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
IDS = ['scn-seal', 'scn-sea', 'scn-air']
LABELS = {'scn-seal': '巡逻区', 'scn-sea': '巡逻海区', 'scn-air': '集结地域'}


def main():
    fails = []

    def check(name, cond, detail=''):
        print(('ok' if cond else 'FAIL') + '  ' + name + (('  ' + detail) if detail else ''))
        if not cond:
            fails.append(name)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1400, 'height': 900}, accept_downloads=True)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri()))
        page.wait_for_function('Array.isArray(window.TEMPLATES) && TEMPLATES.length > 0')
        found = page.evaluate('''(ids) => ids.map(id => {
          const t = TEMPLATES.find(x => x.id === id);
          return t ? { id: t.id, name: t.name, group: t.group || '' } : null;
        })''', IDS)
        check('three scenario templates', found == [
            {'id': 'scn-seal', 'name': '区域封控场景', 'group': '作战场景'},
            {'id': 'scn-sea', 'name': '海上拦截场景', 'group': '作战场景'},
            {'id': 'scn-air', 'name': '空地协同场景', 'group': '作战场景'},
        ], str(found))
        page.evaluate('openTemplates()')
        page.wait_for_selector('.tpl-gh')
        gallery = page.locator('.tpl-b').inner_text()
        check('gallery lists the group', '作战场景' in gallery and '区域封控场景' in gallery and '海上拦截场景' in gallery and '空地协同场景' in gallery)
        page.keyboard.press('Escape')
        for tid in IDS:
            before = len(errors)
            info = page.evaluate('''(id) => {
              const t = TEMPLATES.find(x => x.id === id);
              const d = t.build();
              loadDoc(d); render(); fit();
              const nodes = P().nodes;
              const icons = nodes.filter(n => n.icon).map(n => n.icon);
              const libBad = icons.filter(k => k.startsWith('lib:') && !ICON_MAP[k.slice(4)]);
              const msBad = icons.filter(k => k.startsWith('ms:') && !MS_LIST.some(m => m[0] === k.slice(3)));
              const sides = nodes.filter(n => n.affiliation === 'red' || n.affiliation === 'blue').map(n => n.affiliation);
              const types = nodes.map(n => n.type);
              const svg = diagramSVG(P(), true);
              let exportStr = '';
              try { exportStr = exportSVGString(P(), true).str; } catch (e) { exportStr = 'ERR ' + e; }
              const saved = JSON.parse(projectJSON());
              loadDoc(saved.doc); render();
              const again = P().nodes.map(n => n.text);
              const sideBack = P().nodes.filter(n => n.affiliation === 'red' || n.affiliation === 'blue').length;
              const bare = nodes.filter(n => (n.affiliation === 'red' || n.affiliation === 'blue') && !(n.icon && n.icon.startsWith('lib:')));
              let beauty = '';
              try { beautify(); render(); } catch (e) { beauty = String(e); }
              return {
                texts: nodes.map(n => n.text),
                again, sideBack, bare: bare.length, beauty,
                libBad, msBad, sides,
                hasMs: icons.some(k => k.startsWith('ms:')),
                hasArrow: types.includes('stdArrow') && types.includes('arrowR'),
                hasZone: types.includes('ellipse') || types.includes('rect'),
                svg: svg.length,
                exportStr: exportStr.slice(0, 12),
                exportLen: exportStr.length
              };
            }''', tid)
            check(tid + ' labels survive save', LABELS[tid] in info['again'] and info['sideBack'] > 0, str(info['again']))
            check(tid + ' military symbol', info['hasMs'] and not info['msBad'])
            check(tid + ' red and blue', 'red' in info['sides'] and 'blue' in info['sides'] and not info['libBad'] and info['bare'] == 0)
            check(tid + ' arrows and zone', info['hasArrow'] and info['hasZone'])
            check(tid + ' svg export', info['svg'] > 500 and not str(info['exportStr']).startswith('ERR') and info['exportLen'] > 500, info['exportStr'])
            check(tid + ' beautify', info['beauty'] == '', info['beauty'])
            check(tid + ' no page error', len(errors) == before, str(errors[before:]))
            page.evaluate('''(id) => { loadDoc(TEMPLATES.find(x => x.id === id).build()); render(); fit(); }''', tid)
            page.click('#b-export')
            with page.expect_download(timeout=30000) as dl:
                page.click('[data-exp="png"]')
            path = dl.value
            check(tid + ' png download', path.suggested_filename.endswith('.png'))
        browser.close()
    if fails:
        raise SystemExit('failed: ' + ', '.join(fails))
    print('scenario templates ok')


if __name__ == '__main__':
    main()
