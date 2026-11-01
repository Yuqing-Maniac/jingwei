"""导入测试：offline.html + importers.js，逐个夹具导入、渲染、截图并统计。
用法：python3 harness.py [文件…]   （缺省：fx/*.pptx、out/demo.pptx、out/demo.vsdx、vsdx 仓库测试文件）
截图：imp_test/shots/<夹具>_<页序>.png 以及 _beauty.png（beautify 之后）"""
import sys, os, glob, json, base64
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
SHOTS = os.path.join(H, 'shots'); os.makedirs(SHOTS, exist_ok=True)
VREPO = '/tmp/claude-0/-home-claude/4a98c7fc-ad86-519e-b225-277215eac05a/scratchpad/vsdxrepo/tests'
files = sys.argv[1:] or (sorted(glob.glob(os.path.join(H, 'fx', '*.pptx'))) + sorted(glob.glob(os.path.join(H, 'fx', '*.vsdx'))) +
        [os.path.join(ROOT, 'out', 'demo.pptx'), os.path.join(ROOT, 'out', 'demo.vsdx')] +
        [os.path.join(VREPO, f) for f in ['test1.vsdx', 'test2.vsdx', 'test4_connectors.vsdx', 'test5_master.vsdx', 'test7_with_connector.vsdx', 'test8_simple_connector.vsdx', 'test9_rect_and_line.vsdx', 'test10_nested_shapes.vsdx', 'test12_colors.vsdx', 'test_master_multiple_child_shapes.vsdx']])
IMPORT = r"""
async ([b64, name]) => {
  const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  const f = new File([u], name);
  const r = await Importer.fromFile(f);
  if (r.pages.length) r.pages[0].id = 'root';
  window.__imp = r;
  const d = { name: r.name, theme: 'report', statusLabels: { base: '已建', new: '本期新增', key: '重点建设' }, custom: r.custom, pages: {} };
  for (const p of r.pages) d.pages[p.id] = p;
  loadDoc(d);
  const cnt = p => { const c = {}; for (const n of p.nodes) c[n.type] = (c[n.type] || 0) + 1; return c; };
  return { warnings: r.warnings, pages: r.pages.map(p => ({ id: p.id, name: p.name, links: p.links.length, labels: p.links.filter(l => l.label).length,
      dirs: p.links.map(l => l.dir).join(''), types: cnt(p), title: (p.nodes.find(n => n.role === 'title') || {}).text || '',
      bands: p.nodes.filter(n => n.type === 'band').map(n => n.text), lanes: p.nodes.filter(n => n.type === 'lane').map(n => n.text), groups: p.nodes.filter(n => n.type === 'group').map(n => n.text) })) };
}"""
summary = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1500, 'height': 950}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto('file://' + os.path.join(ROOT, 'offline.html')); pg.wait_for_timeout(1500)
    pg.add_script_tag(path=os.path.join(ROOT, 'importers.js'))
    for f in files:
        if not os.path.exists(f): print('missing', f); continue
        tag = os.path.splitext(os.path.basename(f))[0] + ('_v' if f.endswith('.vsdx') and 'demo' in f else '')
        try:
            res = pg.evaluate(IMPORT, [base64.b64encode(open(f, 'rb').read()).decode(), os.path.basename(f)])
        except Exception as e:
            print('FAIL', tag, str(e)[:400]); summary[tag] = {'error': str(e)[:300]}; continue
        summary[tag] = res
        for i, p in enumerate(res['pages']):
            pg.evaluate("id => { cur = id; stack = [id]; render(); fit(); }", p['id']); pg.wait_for_timeout(150)
            pg.locator('#svg').screenshot(path=os.path.join(SHOTS, f'{tag}_{i+1}.png'))
        if res['pages']:
            pg.evaluate("id => { cur = id; beautify(P()); render(); fit(); }", res['pages'][0]['id']); pg.wait_for_timeout(150)
            pg.locator('#svg').screenshot(path=os.path.join(SHOTS, f'{tag}_beauty.png'))
        print(tag, json.dumps(res, ensure_ascii=False))
    print('ERR', errs[:10]); b.close()
json.dump(summary, open(os.path.join(H, 'summary.json'), 'w'), ensure_ascii=False, indent=1)
