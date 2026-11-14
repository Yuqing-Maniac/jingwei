"""Load each combat-scenario template, edit one label, and export SVG plus PPTX."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
IDS = ['scn-contact', 'scn-patrol', 'scn-assault']
CHROME = os.environ.get('JW_CHROME') or '/opt/google/chrome/chrome'


def main():
    out = Path(os.environ.get('JW_SCENARIO_OUT', '/tmp/scenario-tpl'))
    out.mkdir(parents=True, exist_ok=True)
    url = os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri())
    failures = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1600, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_default_timeout(120000)
        page.goto(url, timeout=120000)
        page.wait_for_function('typeof TEMPLATES !== "undefined" && typeof exportSVGString === "function"')
        gallery = page.evaluate('''() => {
          openTemplates();
          const titles = [...document.querySelectorAll('.tpl-t b')].map(b => b.textContent);
          const bad = [...document.querySelectorAll('.tpl-err')].length;
          document.getElementById('tpl-close').click();
          return { titles: titles, bad: bad };
        }''')
        for tid in IDS:
            errors.clear()
            info = page.evaluate('''(id) => {
              const t = TEMPLATES.find(x => x.id === id);
              if (!t) return { missing: true };
              const d = t.build();
              loadDoc(d); fit(); render();
              const nodes = P().nodes;
              const lib = nodes.filter(n => n.icon && n.icon.indexOf('lib:') === 0);
              const one = lib[0];
              selectNodes([one.id]); render();
              const box = document.getElementById('p-text');
              box.value = '已改标注';
              box.dispatchEvent(new Event('input', { bubbles: true }));
              const side = document.querySelector('.sh[data-shared="affiliation"] select');
              const before = one.affiliation || 'neutral';
              side.value = before === 'red' ? 'blue' : 'red';
              side.dispatchEvent(new Event('change', { bubbles: true }));
              const dim = nodes.find(n => n.type === 'dimArrow');
              selectNodes([dim.id]); render();
              const shown = dimLabel(dim);
              const dist = document.getElementById('p-dist');
              const panel = dist.value;
              dist.value = '3 km';
              dist.dispatchEvent(new Event('input', { bubbles: true }));
              render();
              const svg = exportSVGString(P(), true).str;
              return {
                name: t.name,
                group: t.group,
                edited: one.text,
                side: one.affiliation || 'neutral',
                dist: shown,
                panel: panel,
                after: document.getElementById('p-dist').value,
                stuck: dim.distText || '',
                svgHas: svg.indexOf(shown) >= 0 && svg.indexOf('3 km') < 0,
                blue: nodes.some(n => n.affiliation === 'blue'),
                red: nodes.some(n => n.affiliation === 'red'),
                ms: nodes.some(n => n.icon && n.icon.indexOf('ms:') === 0),
                lib: lib.length,
                std: nodes.some(n => n.type === 'stdArrow'),
                dim: nodes.some(n => n.type === 'dimArrow'),
                shape: nodes.some(n => ['ellipse', 'sector', 'rect', 'round', 'chevron'].indexOf(n.type) >= 0),
                svg: svg
              };
            }''', tid)
            if info.get('missing'):
                failures.append(tid + ' missing')
                continue
            page.screenshot(path=str(out / (tid + '.png')))
            svg_path = out / (tid + '.svg')
            svg_path.write_text(info['svg'], encoding='utf-8')
            with page.expect_download(timeout=60000) as dl:
                page.evaluate('() => exportPPTX()')
            ppt = out / (tid + '.pptx')
            dl.value.save_as(str(ppt))
            checks = [
                info['group'] == '作战场景' and info['name'] in gallery['titles'] and gallery['bad'] == 0,
                info['edited'] == '已改标注',
                info['side'] in ('red', 'blue'),
                info['dist'] and info['panel'] == info['dist'] and info['after'] == info['dist'] and info['stuck'] == '' and info['svgHas'],
                info['blue'] and info['red'] and info['ms'] and info['lib'] > 0,
                info['std'] and info['dim'] and info['shape'],
                '<polygon' in info['svg'] and '<image' in info['svg'],
                ppt.stat().st_size > 2000,
                not errors,
            ]
            if not all(checks):
                failures.append(tid + ' ' + str({
                    'name': info['name'], 'group': info['group'], 'edited': info['edited'],
                    'side': info['side'], 'dist': info['dist'], 'blue': info['blue'],
                    'red': info['red'], 'ms': info['ms'], 'lib': info['lib'],
                    'std': info['std'], 'dim': info['dim'], 'shape': info['shape'],
                    'svg': len(info['svg']), 'ppt': ppt.stat().st_size,
                    'gallery': gallery, 'errors': errors[:3], 'checks': checks,
                }))
        browser.close()
    if failures:
        raise SystemExit('\n'.join(failures))
    print('ok', ' '.join(IDS))


if __name__ == '__main__':
    main()
