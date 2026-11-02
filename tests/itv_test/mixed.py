"""Mixed document: DEPLOY page + SV-1 page → xlsx with union columns; validated with openpyxl."""
import os, base64, openpyxl
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(H, 'itv_test', 'out')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(H, 'offline.html')); pg.wait_for_timeout(1200)
    s = pg.evaluate("""async()=>{const d=TEMPLATES.find(t=>t.id==='it-deploy').build(); const s=TEMPLATES.find(t=>t.id==='std-sv1').build().pages.root;
      s.id='p2'; d.pages.p2=s; const r=d.pages.root; r.nodes.push(mkNode({type:'round',text:'SV-1 页',x:0,y:-200,w:120,h:40,sub:'p2'}));
      loadDoc(d); const blob=await StdXlsx.build(doc); const u=new Uint8Array(await blob.arrayBuffer()); let x=''; for(let i=0;i<u.length;i+=32768) x+=String.fromCharCode.apply(null,u.subarray(i,i+32768)); return btoa(x);}""")
    open(f'{OUT}/mixed.xlsx', 'wb').write(base64.b64decode(s))
    wb = openpyxl.load_workbook(f'{OUT}/mixed.xlsx')
    for ws in wb.worksheets: print(ws.title, ws.max_row, [c.value for c in ws[1]][:14] if ws.title != '说明' else '')
    print('errs', errs); b.close()
for f in ['out/std/sv1.xlsx']:
    wb = openpyxl.load_workbook(os.path.join(H, f)); print(f, [ (ws.title, ws.max_row, ws.max_column) for ws in wb.worksheets])
