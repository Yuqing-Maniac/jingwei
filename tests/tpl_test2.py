from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080})
  errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type in('error','warning') else None); pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto('file://'+os.path.abspath('tpl_test.html')); pg.wait_for_timeout(1200)
  pg.evaluate('openTemplates()'); pg.click('.tpl-card >> nth=2'); pg.click('#tpl-use'); pg.wait_for_timeout(300)
  pg.click('[data-enter]'); pg.wait_for_timeout(400); pg.screenshot(path='out/tpl/sub.png')
  pg.evaluate('goPage(0)')
  pg.evaluate('openTemplates()'); pg.click('.tpl-card >> nth=4'); pg.click('#tpl-add'); pg.wait_for_timeout(300)
  print(pg.evaluate('Object.keys(doc.pages).length'))
  pg.keyboard.press('Control+z'); print(pg.evaluate('Object.keys(doc.pages).length'))
  print('ERR',errs); b.close()
