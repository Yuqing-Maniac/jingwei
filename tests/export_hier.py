"""导出文件名跟随工程名；整体导出按层级出文件；嵌套分视图的 PPTX 在时限内完成。"""
import pathlib
import time
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
SHOT = pathlib.Path('/opt/cursor/artifacts/export-menu.png')
BOUND_MS = 8000
fails = []


def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))


SETUP = r"""
() => {
  window.__saved = [];
  window.saveFile = saveFile = async (name, data) => { window.__saved.push({ name, data }); };
  const box = (text, x) => mkNode({ type: 'round', text, x, y: 80, w: 140, h: 48 });
  const rootN = box('MARK-ROOT', 40);
  const midN = box('MARK-MID', 40);
  const leafN = box('MARK-LEAF', 40);
  const back = box('回指', 240);
  rootN.sub = 'pmid';
  midN.sub = 'pleaf';
  back.sub = 'pmid';
  loadDoc({
    name: '巡逻工程', theme: 'report',
    statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' },
    custom: {},
    pages: {
      root: { id: 'root', name: '体系总览', nodes: [rootN], links: [] },
      pmid: { id: 'pmid', name: '一分系统', nodes: [midN], links: [] },
      pleaf: { id: 'pleaf', name: '内部单元', nodes: [leafN, back], links: [] }
    }
  });
  cur = 'pleaf';
  return {
    order: pagesInOrder().map(p => p.name),
    pngRoot: (cur = 'root', fname('png')),
    pngLeaf: (cur = 'pleaf', fname('png')),
    ppt: docExportName('pptx'),
    proj: projectFileDefault(),
    menu: [...document.querySelectorAll('#m-export [data-exp]')].map(b => b.dataset.exp),
    cap: (document.querySelector('#m-export .cap') || {}).textContent || ''
  };
}
"""

PPTX = r"""
async () => {
  window.__saved = [];
  const t0 = performance.now();
  await exportPPTX();
  const ms = Math.round(performance.now() - t0);
  const blob = window.__saved.length ? window.__saved[0].data : null;
  if (!blob) return { ms, name: null, slides: 0, hits: [] };
  const z = await JSZip.loadAsync(await blob.arrayBuffer());
  const names = Object.keys(z.files).filter(n => /^ppt\/slides\/slide\d+\.xml$/.test(n))
    .sort((a, b) => (+a.match(/slide(\d+)/)[1]) - (+b.match(/slide(\d+)/)[1]));
  const hits = [];
  for (const n of names) {
    const xml = await z.files[n].async('string');
    const m = xml.match(/MARK-(ROOT|MID|LEAF)/);
    hits.push(m ? m[0] : '');
  }
  return { ms, name: window.__saved[0].name, slides: names.length, hits };
}
"""

SVG = r"""
async () => {
  const item = window.__saved[0];
  if (!item) return { zip: null, files: [] };
  const z = await JSZip.loadAsync(await item.data.arrayBuffer());
  const files = Object.keys(z.files).filter(n => !z.files[n].dir).sort();
  return { zip: item.name, files };
}
"""

DESK = r"""
async () => {
  window.__written = [];
  window.__saved = [];
  window.jwDesk = {
    pickDir: async () => '/tmp/jw-export',
    writeIn: async (dir, name, data) => {
      const n = data && data.byteLength ? data.byteLength : 0;
      window.__written.push({ dir, name, n });
      return dir + '/' + name;
    }
  };
  await exportHierarchy('svg');
  return { written: window.__written, saved: window.__saved.map(s => s.name) };
}
"""

DEMO = r"""
async () => {
  window.__saved = [];
  window.saveFile = saveFile = async (name, data) => { window.__saved.push({ name, data }); };
  loadDoc(buildDemo());
  const host = doc.pages.pnest.nodes.find(n => String(n.text || '').indexOf('机巢舱体') >= 0);
  const leaf = { id: 'pleaf', name: '舱体分视图', nodes: [], links: [] };
  doc.pages.pleaf = leaf;
  host.sub = 'pleaf';
  leaf.nodes.push(mkNode({ type: 'round', text: 'MARK-CABIN', x: 40, y: 40, w: 140, h: 48 }));
  window.__saved = [];
  const t0 = performance.now();
  await exportPPTX();
  const ms = Math.round(performance.now() - t0);
  const blob = window.__saved[0] && window.__saved[0].data;
  let slides = 0, cabin = -1;
  if (blob) {
    const z = await JSZip.loadAsync(await blob.arrayBuffer());
    const names = Object.keys(z.files).filter(n => /^ppt\/slides\/slide\d+\.xml$/.test(n))
      .sort((a, b) => (+a.match(/slide(\d+)/)[1]) - (+b.match(/slide(\d+)/)[1]));
    slides = names.length;
    for (let i = 0; i < names.length; i++) {
      const xml = await z.files[names[i]].async('string');
      if (xml.indexOf('MARK-CABIN') >= 0) cabin = i;
    }
  }
  return { ms, name: window.__saved[0] && window.__saved[0].name, slides, cabin, order: pagesInOrder().map(p => p.name) };
}
"""


def main():
    SHOT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/opt/google/chrome/chrome', args=['--no-sandbox', '--disable-dev-shm-usage'])
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        pg.goto(HTML)
        pg.wait_for_timeout(400)
        pg.click('#b-export')
        pg.wait_for_selector('#m-export.open .dd')
        btn = pg.locator('#m-export').bounding_box()
        dd = pg.locator('#m-export .dd').bounding_box()
        x = max(0, min(btn['x'], dd['x']) - 12)
        y = max(0, min(btn['y'], dd['y']) - 12)
        r = max(btn['x'] + btn['width'], dd['x'] + dd['width']) + 12
        btm = max(btn['y'] + btn['height'], dd['y'] + dd['height']) + 12
        pg.screenshot(path=str(SHOT), clip={'x': x, 'y': y, 'width': r - x, 'height': btm - y})
        pg.keyboard.press('Escape')

        wall0 = time.perf_counter()
        try:
            demo = pg.evaluate(DEMO)
        except Exception as e:
            demo = {'error': str(e)[:300]}
        demo_wall = round(time.perf_counter() - wall0, 3)
        print('DEMO', demo_wall, demo)

        try:
            info = pg.evaluate(SETUP)
        except Exception as e:
            info = {'error': str(e)[:300]}
        print('SETUP', info)

        wall1 = time.perf_counter()
        try:
            ppt = pg.evaluate(PPTX)
        except Exception as e:
            ppt = {'error': str(e)[:300]}
        ppt_wall = round(time.perf_counter() - wall1, 3)
        print('PPTX', ppt_wall, ppt)

        wall2 = time.perf_counter()
        try:
            pg.evaluate("() => { window.__saved = []; saveFile = async (name, data) => { window.__saved.push({ name, data }); }; }")
            pg.click('#b-export')
            pg.click('[data-exp="allsvg"]')
            pg.wait_for_function('() => window.__saved.length > 0', timeout=BOUND_MS)
            svg = pg.evaluate(SVG)
            svg['ms'] = round((time.perf_counter() - wall2) * 1000)
        except Exception as e:
            svg = {'error': str(e)[:300]}
        print('SVG', svg)

        try:
            desk = pg.evaluate(DESK)
        except Exception as e:
            desk = {'error': str(e)[:300]}
        print('DESK', desk)
        print('PAGEERR', errs[:5])
        b.close()

    check('demo nested pptx finished', isinstance(demo, dict) and demo.get('ms', 10**9) < BOUND_MS and 'error' not in demo, str(demo))
    check('demo three slides last is cabin', isinstance(demo, dict) and demo.get('slides') == 3 and demo.get('cabin') == 2, str(demo))
    check('demo pptx uses project name', isinstance(demo, dict) and demo.get('name') == '边海防无人化巡逻体系.pptx', str(demo))
    check('setup names', isinstance(info, dict) and info.get('pngRoot') == '巡逻工程.png' and info.get('pngLeaf') == '巡逻工程-内部单元.png' and info.get('ppt') == '巡逻工程.pptx' and info.get('proj') == '巡逻工程.jingwei.json', str(info))
    check('menu has whole export', isinstance(info, dict) and info.get('cap') == '整体导出' and 'allpng' in (info.get('menu') or []) and 'allpptx' in (info.get('menu') or []), str(info))
    check('hierarchy order', isinstance(info, dict) and info.get('order') == ['体系总览', '一分系统', '内部单元'], str(info))
    check('nested pptx within bound', isinstance(ppt, dict) and ppt.get('ms', 10**9) < BOUND_MS and ppt_wall < BOUND_MS / 1000 + 1 and 'error' not in ppt, 'ms=%s wall=%s %s' % (ppt.get('ms') if isinstance(ppt, dict) else None, ppt_wall, ppt))
    check('nested pptx slides in order', isinstance(ppt, dict) and ppt.get('name') == '巡逻工程.pptx' and ppt.get('hits') == ['MARK-ROOT', 'MARK-MID', 'MARK-LEAF'], str(ppt))
    want = [
        '巡逻工程-01-体系总览.svg',
        '巡逻工程-02-体系总览-一分系统.svg',
        '巡逻工程-03-体系总览-一分系统-内部单元.svg',
    ]
    check('svg zip per view', isinstance(svg, dict) and svg.get('zip') == '巡逻工程.zip' and svg.get('files') == want and svg.get('ms', 10**9) < BOUND_MS, str(svg))
    check('desktop folder per view', isinstance(desk, dict) and desk.get('saved') == [] and [w.get('name') for w in desk.get('written') or []] == want and all(w.get('dir') == '/tmp/jw-export' and w.get('n', 0) > 0 for w in desk.get('written') or []), str(desk))
    check('no page error', not errs, str(errs[:3]))
    if fails:
        print('FAILED', len(fails))
        for f in fails:
            print(' -', f)
        raise SystemExit(1)
    print('ALL PASS')


if __name__ == '__main__':
    main()
