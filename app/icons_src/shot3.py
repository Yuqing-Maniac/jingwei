from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
  pg.goto('file://'+os.path.abspath('offline.html')); pg.wait_for_timeout(1500)
  pg.screenshot(path='out/v2_main.png')
  pg.keyboard.press('Control+Shift+M'); pg.wait_for_timeout(2500); pg.screenshot(path='out/v2_tpl.png'); pg.keyboard.press('Escape')
  pg.keyboard.press('Control+Shift+G'); pg.wait_for_timeout(800); pg.screenshot(path='out/v2_text.png'); pg.keyboard.press('Escape')
  pg.keyboard.press('F1'); pg.wait_for_timeout(500); pg.screenshot(path='out/v2_keys.png')
  print(errs); b.close()
