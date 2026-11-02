from playwright.sync_api import sync_playwright
import os
O='out/cb/'
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
  pg.goto('file://'+os.path.abspath('offline.html')); pg.wait_for_timeout(1500)
  pg.click('#b-new'); pg.wait_for_timeout(300)
  pg.keyboard.press('Control+Shift+B'); pg.wait_for_timeout(600); pg.screenshot(path=O+'dlg_wedge.png')
  pg.click('#cb-pats [data-p=swarm]'); pg.fill('#cb-q','战斗机'); pg.dispatch_event('#cb-q','input'); pg.click('#cb-icons [data-k="lib:fighter"]'); pg.wait_for_timeout(300); pg.screenshot(path=O+'dlg_swarm.png')
  pg.click('#cb-pats [data-p=wedge]'); pg.click('#cb-ok'); pg.wait_for_timeout(400)
  # mixed group: add three nodes via evaluate, select, Ctrl+G
  pg.evaluate("""()=>{const mk=(k,t,x,y)=>{const n=mkNode({type:'equip',noBox:true,icon:'lib:'+k,text:t,w:96,h:96,x,y,size:12});P().nodes.push(n);return n};
    const a=mk('uav_quad','四旋翼',-400,300), b=mk('usv_armed','武装无人艇',-300,330), c=mk('ugv_armed','武装无人车',-200,300), d=mk('command_post','指挥所',100,320);
    P().links.push({id:uid(),from:d.id,to:b.id,dir:'one',kind:'ctrl',route:'ortho',label:'任务指令'});
    sel=new Set([a.id,b.id,c.id]); render(); fit();}""")
  pg.wait_for_timeout(300); pg.screenshot(path=O+'before_group.png')
  pg.keyboard.press('Control+g'); pg.wait_for_timeout(500); pg.evaluate("()=>fit()"); pg.wait_for_timeout(300); pg.screenshot(path=O+'after_group.png')
  print(pg.evaluate("()=>[P().nodes.length,P().links.map(l=>l.label)]"))
  for k in ['pptx','png']:
    pg.click('#b-export')
    with pg.expect_download() as d: pg.click(f'[data-exp="{k}"]')
    d.value.save_as(O+'cb.'+k)
  pg.keyboard.press('Control+Shift+U'); pg.wait_for_timeout(400); pg.evaluate("()=>fit()"); pg.screenshot(path=O+'ungroup.png')
  print('errs',errs); b.close()
