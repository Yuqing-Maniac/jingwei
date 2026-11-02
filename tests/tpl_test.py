from playwright.sync_api import sync_playwright
import os, sys
os.makedirs('out/tpl',exist_ok=True)
only = sys.argv[1:] 
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080},accept_downloads=True)
  errs=[]; pg.on('console',lambda m: errs.append(m.text) if m.type in('error','warning') else None); pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto('file://'+os.path.abspath('tpl_test.html')); pg.wait_for_timeout(1500)
  pg.evaluate('openTemplates()'); pg.wait_for_timeout(800)
  pg.screenshot(path='out/tpl/gallery.png')
  n=pg.evaluate('TEMPLATES.length'); print('n',n)
  # select a card to show confirm bar
  pg.click('.tpl-card >> nth=1'); pg.wait_for_timeout(200); pg.screenshot(path='out/tpl/gallery_sel.png')
  pg.keyboard.press('Escape')
  for i in range(n):
    tid=pg.evaluate(f'TEMPLATES[{i}].id')
    if only and tid not in only: continue
    pg.evaluate('openTemplates()'); pg.click(f'.tpl-card >> nth={i}'); pg.click('#tpl-use'); pg.wait_for_timeout(500)
    pg.screenshot(path=f'out/tpl/{i+1}_{tid}.png', clip={'x':232,'y':44,'width':1920-232-268,'height':1036})
    # export PNG
    pg.click('#b-export')
    with pg.expect_download(timeout=30000) as d: pg.click('[data-exp="png"]')
    d.value.save_as(f'out/tpl/{i+1}_{tid}_export.png')
  print('ERR',errs[:10]); b.close()
