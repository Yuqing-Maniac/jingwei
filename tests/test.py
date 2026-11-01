from playwright.sync_api import sync_playwright
import os
os.makedirs('out',exist_ok=True)
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000},accept_downloads=True)
  errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type in('error','warning') else None); pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto('file://'+os.path.abspath('offline.html')); pg.wait_for_timeout(1500)
  pg.screenshot(path='out/s1.png')
  for k in ['png','pptx','vsdx','svg']:
    pg.click('#b-export')
    with pg.expect_download(timeout=30000) as d:
      pg.click(f'[data-exp="{k}"]')
    d.value.save_as('out/demo.'+k); print('saved',k)
  pg.click('[data-enter]'); pg.wait_for_timeout(500); pg.screenshot(path='out/s2.png')
  print('ERR',errs[:10]); b.close()
