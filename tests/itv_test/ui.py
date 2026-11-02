"""UI screenshots: properties panel (page / DEPLOY node / DEPLOY link / DATA link), check dialog empty state, template gallery."""
import os
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(H, 'itv_test', 'out')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(H, 'offline.html')); pg.wait_for_timeout(1200)
    clip = {'x': 1650, 'y': 40, 'width': 270, 'height': 1040}
    pg.evaluate("()=>{loadDoc(TEMPLATES.find(t=>t.id==='it-deploy').build()); fit(); const n=P().nodes.find(n=>n.text==='容器云集群'); sel=new Set([n.id]); selLink=null; render();}")
    pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/props-deploy-node.png', clip=clip)
    pg.evaluate("()=>{const z=P().nodes.find(n=>n.etype==='zone'); sel=new Set([z.id]); render();}"); pg.wait_for_timeout(200); pg.screenshot(path=f'{OUT}/props-zone.png', clip=clip)
    pg.evaluate("()=>{sel=new Set(); selLink=P().links[5].id; render();}"); pg.wait_for_timeout(200); pg.screenshot(path=f'{OUT}/props-deploy-link.png', clip=clip)
    pg.evaluate("()=>{loadDoc(TEMPLATES.find(t=>t.id==='it-data').build()); fit(); sel=new Set(); selLink=P().links[0].id; render();}"); pg.wait_for_timeout(200); pg.screenshot(path=f'{OUT}/props-data-link.png', clip=clip)
    pg.evaluate("()=>{sel=new Set(); selLink=null; render();}"); pg.wait_for_timeout(200); pg.screenshot(path=f'{OUT}/props-page.png', clip=clip)
    pg.evaluate("()=>{const d=TEMPLATES.find(t=>t.id==='it-sec').build(); d.pages.root.links.push({id:'x1',from:d.pages.root.nodes.find(n=>n.text==='业务数据库').id,to:d.pages.root.nodes.find(n=>n.text==='涉密数据库').id,dir:'one',kind:'data',route:'ortho',label:'违规直连'}); loadDoc(d); fit(); Std.openCheck();}")
    pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/check-sec-violation.png')
    pg.evaluate("()=>{Std.closeCheck(); loadDoc({name:'x',theme:'report',statusLabels:{base:'a',new:'b',key:'c'},custom:{},pages:{root:{id:'root',name:'x',nodes:[],links:[]}}}); Std.openCheck();}")
    pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/check-empty.png')
    pg.evaluate("()=>{Std.closeCheck(); openTemplates();}"); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{const b=document.querySelector('.tpl-b'); b.scrollTop=b.scrollHeight;}"); pg.wait_for_timeout(300)
    pg.screenshot(path=f'{OUT}/gallery.png')
    print('errs', errs); b.close()
