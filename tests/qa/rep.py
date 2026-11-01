import sys
from playwright.sync_api import sync_playwright
files=sys.argv[1:]
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  for f in files:
    for page in ['a4p','a4l']:
      pg.set_input_files('#f-open',f); pg.wait_for_timeout(1500)
      pg.evaluate("(pgk)=>{doc.layout={mode:'report',page:pgk,font:10.5};beautify(P());render();fit()}",page)
      r=pg.evaluate("()=>{const p=P(),b=contentBBox(p),c=Compact.cfg();const ns=p.nodes.filter(n=>!isCont(n)&&n.text);return {w:Math.round(b.w),target:Compact.targetW(c),font:Compact.fontAt(b.w,Compact.PAGES[c.page].cm),minSize:Math.min(...ns.map(n=>n.size||13)),overlaps:(()=>{let k=0;const L=ns.filter(n=>!['text','note','legend','tblock'].includes(n.type));for(let i=0;i<L.length;i++)for(let j=i+1;j<L.length;j++){const a=L[i],c=L[j];if(Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x)>3&&Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y)>3)k++;}return k})()}}")
      print(f.split('/')[-1],page,r,errs[:2])
      if len(sys.argv)>1: pg.locator('#svg').screenshot(path=f'/tmp/claude-0/bh/rep_{f.split("/")[-1]}_{page}.png')
  b.close()
