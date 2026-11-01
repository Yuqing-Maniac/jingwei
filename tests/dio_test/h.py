import json, os
from playwright.sync_api import sync_playwright
V='/tmp/claude-0/-home-claude/4a98c7fc-ad86-519e-b225-277215eac05a/scratchpad/drawio/src/main/webapp/js/viewer-static.min.js'
out={}
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1500,'height':1000})
    errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(800)
    cases={'demo':None,'layered':"TEMPLATES.find(t=>t.id==='layered')", 'swim':"TEMPLATES.find(t=>t.id==='swimlane')", 'sv1':"TEMPLATES.find(t=>t.id==='std-sv1')"}
    for k,expr in cases.items():
        if expr: pg.evaluate(f"(()=>{{const t={expr}; if(t) loadDoc(t.build());}})()"); pg.wait_for_timeout(400)
        pg.evaluate("render(); fit()"); pg.screenshot(path=f'{k}_orig.png')
        s=pg.evaluate("DrawIO.exportString()"); open(f'{k}.drawio','w',encoding='utf-8').write(s)
        # round trip
        r=pg.evaluate("""async (s)=>{const r=await DrawIO.importText(s); const d={name:'rt',theme:doc.theme,statusLabels:doc.statusLabels,custom:Object.assign({},doc.custom,r.custom),pages:{}}; r.pages.forEach(p=>d.pages[p.id]=p); if(r.docSettings) Object.assign(d, r.docSettings); const before=JSON.parse(JSON.stringify(Object.values(doc.pages).map(p=>[p.nodes.length,p.links.length]))); loadDoc(d); return {before, after:r.pages.map(p=>[p.nodes.length,p.links.length]), types:r.pages[0].nodes.reduce((a,n)=>(a[n.type]=(a[n.type]||0)+1,a),{}), warn:r.warnings, view:r.pages[0].view, meta:!!(r.docSettings&&r.docSettings.meta)}}""", s)
        pg.wait_for_timeout(300); pg.evaluate("render(); fit()"); pg.screenshot(path=f'{k}_rt.png')
        print(k, len(s)//1024,'KB', r)
    print('ERR',errs)
    # viewer render
    vp=b.new_page(viewport={'width':1500,'height':1100})
    vp.on('pageerror',lambda e: print('VIEWER ERR',e))
    for k in cases:
        x=open(f'{k}.drawio',encoding='utf-8').read()
        html=f"<html><body style='margin:0;background:#fff'><div class='mxgraph' style='max-width:100%' data-mxgraph='{json.dumps({'xml':x,'highlight':'none','toolbar':'','nav':False,'page':0}).replace('&','&amp;').replace(chr(39),'&#39;')}'></div><script src='file://{V}'></script></body></html>"
        open(f'v_{k}.html','w',encoding='utf-8').write(html)
        vp.goto(f'file:///home/claude/drawtool/dio_test/v_{k}.html'); vp.wait_for_timeout(2500)
        vp.screenshot(path=f'{k}_drawio.png', full_page=True)
    b.close()
