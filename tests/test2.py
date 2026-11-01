from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1500,'height':900})
  pg.goto('file://'+os.path.abspath('offline.html')); pg.wait_for_timeout(1200)
  pg.select_option('#b-theme','command'); pg.wait_for_timeout(300); pg.screenshot(path='out/dark.png')
  pg.click('[data-enter]'); pg.wait_for_timeout(400); pg.screenshot(path='out/s2.png')
  m=b.new_page(viewport={'width':400,'height':800}); m.goto('file://'+os.path.abspath('offline.html')); m.wait_for_timeout(1200); m.screenshot(path='out/mob.png')
  print(m.evaluate('document.documentElement.scrollWidth'))
  b.close()
