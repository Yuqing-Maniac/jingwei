"""调试：导入单个文件，打印每页节点（类型、文字、父）与连线（端点文字、方向、标注）。python3 inspect.py file [page]"""
import sys, os, base64, json
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
f = sys.argv[1]; pi = int(sys.argv[2]) if len(sys.argv) > 2 else None
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(); pg.goto('file://' + os.path.join(ROOT, 'offline.html')); pg.wait_for_timeout(1200)
    pg.add_script_tag(path=os.path.join(ROOT, 'importers.js'))
    r = pg.evaluate("""async ([b64,name]) => { const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
      const r = await Importer.fromFile(new File([u],name));
      return r.pages.map(p => { const T = id => { const n = p.nodes.find(n=>n.id===id); return n ? (n.type+':'+(n.text||'').slice(0,12)) : '?'; };
        return { name: p.name, nodes: p.nodes.map(n => [n.type, (n.text||'').replace(/\\n/g,'/').slice(0,16), n.parent ? T(n.parent) : '-', n.x, n.y, n.w, n.h, n.status, n.fill||'', n.stroke||'']),
                 links: p.links.map(l => [T(l.from), T(l.to), l.dir, l.kind, l.label]) }; }); }""", [base64.b64encode(open(f,'rb').read()).decode(), os.path.basename(f)])
    for i, p in enumerate(r):
        if pi and i + 1 != pi: continue
        print('==', p['name'])
        for n in p['nodes']: print('  N', n)
        for l in p['links']: print('  L', l)
    b.close()
