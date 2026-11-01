from playwright.sync_api import sync_playwright
import os,json
os.makedirs('out/std',exist_ok=True)
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto('file://'+os.path.abspath('offline.html')); pg.wait_for_timeout(1500)
  for tid in ['std-ov1','std-ov2','std-ov5b','std-sv1','std-sv4']:
    r=pg.evaluate("id=>{const T=TEMPLATES.find(t=>t.id===id); loadDoc(T.build()); fit(); const is=Std.check(doc); return is.map(i=>i.level+':'+i.rule)}",tid)
    pg.wait_for_timeout(400); pg.screenshot(path=f'out/std/{tid}.png'); print(tid, len(r), r[:6])
  pg.evaluate("()=>{const T=TEMPLATES.find(t=>t.id==='std-sv1'); loadDoc(T.build()); fit();}")
  pg.click('#b-export')
  with pg.expect_download() as d: pg.click('[data-exp="pptx"]')
  d.value.save_as('out/std/sv1.pptx')
  with pg.expect_download() as d: pg.evaluate("()=>Std.exportXlsx()")
  d.value.save_as('out/std/sv1.xlsx')
  pg.keyboard.press('Control+Shift+K'); pg.wait_for_timeout(500); pg.screenshot(path='out/std/check.png')
  print('errs',errs); b.close()
