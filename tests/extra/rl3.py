from playwright.sync_api import sync_playwright
from jw_paths import OFFLINE_URL
O='/tmp/claude-0/rlx/'
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto(OFFLINE_URL); pg.wait_for_timeout(1200)
  ks=pg.evaluate("""()=>{const pg=P();pg.nodes.length=0;pg.links.length=0;const ks=Object.keys(SHP_DEF);
    ks.forEach((k,i)=>pg.nodes.push(mkNode({type:k,text:k,x:40+(i%6)*180,y:40+Math.floor(i/6)*120,w:140,h:k.startsWith('arrowU')||k.startsWith('arrowD')?100:60})));fit();render();return ks}""")
  for k in ['vsdx','pptx']:
    pg.click('#b-export')
    with pg.expect_download(timeout=30000) as d: pg.click(f'[data-exp="{k}"]')
    d.value.save_as(O+'all.'+k)
  for k in ['vsdx','pptx']:
    pg.set_input_files('#f-open',O+'all.'+k); pg.wait_for_timeout(1500)
    got=pg.evaluate("()=>Object.fromEntries(P().nodes.filter(n=>n.text).map(n=>[n.text,n.type]))")
    print(k,'side-round hits:',{t:v for t,v in got.items() if v in('roundL','roundR') or t in('roundL','roundR')})
  print('errs',errs); b.close()
