import sys,time
from playwright.sync_api import sync_playwright
files=[l.strip() for l in open('/tmp/claude-0/bh/samples.txt') if l.strip()]
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200])); pg.on('console',lambda m: errs.append('console:'+m.text[:200]) if m.type=='error' else None)
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  for f in files:
    errs.clear(); t=time.time()
    pg.evaluate("()=>{loadDoc(buildDemo());window.__tst='';}")
    pg.set_input_files('#f-open',f)
    try: pg.wait_for_function("()=>/已导入|失败|无法|不是|错误|仅支持|没有/.test(document.querySelector('#toast').textContent)",timeout=30000)
    except Exception: pass
    pg.wait_for_timeout(300)
    toast=pg.evaluate("()=>document.querySelector('#toast').textContent")
    info=pg.evaluate("()=>{const ps=Object.values(doc.pages);let bad=0;for(const p of ps)for(const n of p.nodes)if(![n.x,n.y,n.w,n.h].every(isFinite))bad++;return {pages:ps.length,nodes:ps.reduce((a,p)=>a+p.nodes.length,0),links:ps.reduce((a,p)=>a+p.links.length,0),bad}}")
    # beautify each page
    e2=[]
    try:
      pg.keyboard.press('Control+Shift+F'); pg.wait_for_timeout(200)
      bad2=pg.evaluate("()=>P().nodes.filter(n=>![n.x,n.y,n.w,n.h].every(isFinite)).length")
    except Exception as e: bad2=str(e)[:80]
    flag='!!' if (errs or info['bad'] or bad2) else '  '
    print(flag, f.split('/')[-1][:40], info, 'bty_bad',bad2, round(time.time()-t,1),'s |', toast[:70], errs[:2])
  b.close()
