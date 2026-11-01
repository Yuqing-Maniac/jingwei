import sys
from playwright.sync_api import sync_playwright
tid,lay,out=sys.argv[1],sys.argv[2],sys.argv[3]
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  import os; pg.goto(os.environ.get('APP','file:///home/claude/drawtool/offline.html')); pg.wait_for_timeout(1200)
  pg.evaluate("(i)=>{const t=TEMPLATES.find(x=>x.id===i);loadDoc(t.build());fit();render()}", tid)
  pg.evaluate("(l)=>{const b=document.querySelector('#d-lay [data-v='+l+']'); if(b) b.click();}", lay)
  pg.keyboard.press('Control+Shift+F'); pg.wait_for_timeout(300); pg.keyboard.press('Control+0'); pg.wait_for_timeout(300)
  pg.locator('#svg').screenshot(path=out)
  b.close()
