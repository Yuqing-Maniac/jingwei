from playwright.sync_api import sync_playwright
from jw_paths import OFFLINE_URL
O='/tmp/claude-0/rlx/'
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto(OFFLINE_URL); pg.wait_for_timeout(1200)
  pg.evaluate("""()=>{const pg=P();pg.nodes.length=0;pg.links.length=0;
      const a=mkNode({type:'roundL',text:'左圆右方',x:40,y:40,w:160,h:44}),b=mkNode({type:'roundR',text:'右圆左方',x:300,y:40,w:160,h:44}),c=mkNode({type:'round',text:'圆角矩形',x:40,y:140,w:160,h:44}),d=mkNode({type:'roundL',text:'带状态',x:300,y:140,w:160,h:60,status:'key'});
      pg.nodes.push(a,b,c,d);pg.links.push({id:'l1',from:a.id,to:b.id,kind:'plain',dir:'fwd'});fit();render()}""")
  for k in ['pptx','vsdx','drawio','svg']:
    pg.click('#b-export')
    with pg.expect_download(timeout=30000) as d:
      pg.click(f'[data-exp="{k}"]')
    d.value.save_as(O+'rl.'+k); print('saved',k)
  # drawio roundtrip
  pg.set_input_files('#f-open',O+'rl.drawio'); pg.wait_for_timeout(1000)
  print('drawio in', pg.evaluate("()=>P().nodes.map(n=>n.type+':'+n.text)"))
  pg.set_input_files('#f-open',O+'rl.vsdx'); pg.wait_for_timeout(1000)
  print('vsdx in', pg.evaluate("()=>P().nodes.map(n=>n.type+':'+n.text)"))
  pg.screenshot(path=O+'vsdx_in.png',clip={'x':200,'y':60,'width':900,'height':500})
  print('errs',errs); b.close()
