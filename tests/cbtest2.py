from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto('file://'+os.path.abspath('offline.html')); pg.wait_for_timeout(1500)
  pg.evaluate("()=>{const T=TEMPLATES.find(t=>t.id==='combo'); loadDoc(T.build()); fit();}"); pg.wait_for_timeout(600)
  pg.screenshot(path='out/cb/tpl.png')
  for k in ['pptx','vsdx','png']:
    pg.click('#b-export')
    with pg.expect_download() as d: pg.click(f'[data-exp="{k}"]')
    d.value.save_as('out/cb/tpl.'+k)
  print(errs); b.close()
