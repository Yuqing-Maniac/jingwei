"""IT-view templates harness: python3 itv_test/run.py [template ids...]
Loads offline.html, for each 信息系统架构 template: check before/after Std.fix, beautify stability,
screenshot (fit), xlsx export validated with openpyxl. Output in itv_test/out/."""
import os, sys, json, base64
from playwright.sync_api import sync_playwright
import openpyxl
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(H, 'itv_test', 'out'); os.makedirs(OUT, exist_ok=True)
IDS = sys.argv[1:] or ['it-biz', 'it-app', 'it-data', 'it-tech', 'it-deploy', 'it-sec']
JS_LOAD = """id=>{const T=TEMPLATES.find(t=>t.id===id); const d=T.build(); loadDoc(d); fit();
 const pre=Std.check(doc).map(i=>i.level+':'+i.rule+':'+i.msg);
 const r=Std.fix(doc); render(); fit();
 const post=Std.check(doc).map(i=>i.level+':'+i.rule+':'+i.msg);
 const p=P(); const before=JSON.stringify(p.nodes.map(n=>[n.id,n.x,n.y,n.w,n.h]));
 return {group:T.group,name:T.name,view:p.view,pre,fix:r,post,nodes:p.nodes.length,links:p.links.length,before,
   etypes:Object.entries(p.nodes.reduce((a,n)=>{if(n.etype)a[n.etype]=(a[n.etype]||0)+1;return a},{}))}}"""
JS_BEAUT = """()=>{const p=P(); const b=new Map(p.nodes.map(n=>[n.id,[n.x,n.y,n.w,n.h]])); beautify(p); render(); fit();
 let mx=0, who=''; for(const n of p.nodes){const o=b.get(n.id); const dd=Math.max(...[n.x,n.y,n.w,n.h].map((v,i)=>Math.abs(v-o[i]))); if(dd>mx){mx=dd; who=n.type+':'+(n.text||'').slice(0,12);}}
 return {maxShift:mx, who, post:Std.check(doc).filter(i=>i.level==='error').map(i=>i.rule+':'+i.msg)}}"""
JS_XLSX = """async()=>{const b=await StdXlsx.build(doc); const buf=new Uint8Array(await b.arrayBuffer()); let s=''; for(let i=0;i<buf.length;i+=32768) s+=String.fromCharCode.apply(null, buf.subarray(i,i+32768)); return btoa(s);}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto('file://' + os.path.join(H, 'offline.html')); pg.wait_for_timeout(1500)
    for tid in IDS:
        r = pg.evaluate(JS_LOAD, tid); pg.wait_for_timeout(300)
        pg.screenshot(path=f'{OUT}/{tid}.png')
        print(f"== {tid} [{r['group']}] {r['name']} view={r['view']} nodes={r['nodes']} links={r['links']}")
        print('   pre :', len(r['pre']), [x for x in r['pre'] if not x.startswith('info')][:8])
        print('   fix :', r['fix'])
        print('   post:', len(r['post']), r['post'][:10])
        print('   etypes:', r['etypes'])
        x = base64.b64decode(pg.evaluate(JS_XLSX)); fn = f'{OUT}/{tid}.xlsx'; open(fn, 'wb').write(x)
        wb = openpyxl.load_workbook(fn)
        for ws in wb.worksheets:
            hdr = [c.value for c in ws[1]] if ws.max_row else []
            print(f'   xlsx[{ws.title}] {ws.max_row}x{ws.max_column}', hdr[:14] if ws.title != '说明' else '')
        bt = pg.evaluate(JS_BEAUT); pg.wait_for_timeout(300)
        print('   beautify maxShift:', bt['maxShift'], bt['who'], 'errors after:', bt['post'])
        if bt['maxShift'] > 0: pg.screenshot(path=f'{OUT}/{tid}-beautified.png')
    # properties panel: view selector with optgroups
    pg.evaluate("()=>{sel=new Set(); selLink=null; render();}"); pg.wait_for_timeout(200)
    og = pg.evaluate("()=>[...document.querySelectorAll('#std-view optgroup')].map(g=>g.label+':'+g.children.length)")
    print('view optgroups:', og)
    pg.screenshot(path=f'{OUT}/props.png', clip={'x': 1650, 'y': 40, 'width': 270, 'height': 600})
    print('errs', errs[:10]); b.close()
