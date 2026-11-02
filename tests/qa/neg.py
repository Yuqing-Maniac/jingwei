from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  pg.click('#b-new'); pg.wait_for_timeout(300)
  items=pg.evaluate("()=>[...document.querySelectorAll('.pitem[data-add]')].map(e=>e.dataset.add)")
  pg.evaluate("(items)=>{for(const a of items){const el=[...document.querySelectorAll('.pitem[data-add]')].find(e=>e.dataset.add===a); if(el) el.click();}}", items[:80])
  print(pg.evaluate("()=>{const q=P().nodes.find(n=>P().nodes.some(m=>m.parent===n.id)&&!isCont(n));return q?[q.type,q.text,q.w,q.h]:null}"))
  pg.keyboard.press('Control+Shift+F'); pg.wait_for_timeout(300)
  print(pg.evaluate("()=>P().nodes.filter(n=>n.w<24||n.h<24||isCont(n)).map(n=>[n.type,n.text,n.x,n.y,n.w,n.h,n.parent])"))
  b.close()
