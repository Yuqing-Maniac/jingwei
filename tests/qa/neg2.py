from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  pg.click('#b-new'); pg.wait_for_timeout(300)
  items=pg.evaluate("()=>[...document.querySelectorAll('.pitem[data-add]')].map(e=>e.dataset.add)")
  pg.evaluate("(items)=>{for(const a of items){const el=[...document.querySelectorAll('.pitem[data-add]')].find(e=>e.dataset.add===a); if(el) el.click();}}", items[:80])
  print(pg.evaluate("()=>{const ps=new Set(P().nodes.map(n=>n.parent).filter(Boolean));return [...ps].map(id=>{const q=nodeById(id);return q?[id,q.type,q.text,q.x,q.y,q.w,q.h,q.parent]:[id,'MISSING']})}"))
  pg.keyboard.press('Control+Shift+F'); pg.wait_for_timeout(300)
  print(pg.evaluate("()=>{const ps=new Set(P().nodes.map(n=>n.parent).filter(Boolean));return [...ps].map(id=>{const q=nodeById(id);return q?[id,q.type,q.text,q.x,q.y,q.w,q.h,q.parent, kids(id).length]:[id,'MISSING']})}"))
  pg.keyboard.press('Control+0'); pg.wait_for_timeout(300); pg.locator('#svg').screenshot(path='/tmp/claude-0/bh/mixed.png')
  b.close()
