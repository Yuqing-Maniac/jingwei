import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'build')); import brand
ORG = brand.load()['org']   # 机构标识：brand.local.json（不入库）> brand.example.json
from playwright.sync_api import sync_playwright
f,w,h,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':w,'height':h},device_scale_factor=2)
  pg.goto('file:///home/claude/poster/'+f); pg.wait_for_timeout(1500)
  pg.evaluate("o=>document.querySelectorAll('[data-brand=credit]').forEach(e=>e.textContent=o+'\u3000出品')", ORG)
  pg.locator('#poster').screenshot(path=out,type='jpeg',quality=93); b.close()
