import asyncio
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':900},accept_downloads=True)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file:///home/claude/drawtool/offline.html'); await pg.wait_for_timeout(1200)
    print(await pg.evaluate("()=>[...document.querySelectorAll('.pitem span')].slice(0,10).map(s=>s.textContent)"))
    await pg.evaluate("""()=>{const pg=P();pg.nodes.length=0;pg.links.length=0;
      const a=mkNode({type:'roundL',text:'左圆右方',x:40,y:40,w:160,h:44}),b=mkNode({type:'roundR',text:'右圆左方',x:300,y:40,w:160,h:44}),c=mkNode({type:'round',text:'圆角矩形',x:40,y:140,w:160,h:44}),d=mkNode({type:'roundL',text:'带状态',x:300,y:140,w:160,h:60,status:'key'});
      pg.nodes.push(a,b,c,d);pg.links.push({id:'l1',from:a.id,to:b.id,kind:'plain',dir:'fwd'});fit();render()}""")
    await pg.wait_for_timeout(300)
    await pg.screenshot(path='/tmp/claude-0/rl_canvas.png',clip={'x':200,'y':60,'width':900,'height':500})
    # palette thumbnails
    el=pg.locator('.pitem').nth(0); bb=await el.bounding_box()
    await pg.screenshot(path='/tmp/claude-0/rl_pal.png',clip={'x':0,'y':bb['y']-30,'width':200,'height':160})
    # property select
    await pg.evaluate("()=>{const n=P().nodes[0];sel.clear();sel.add(n.id);render()}")
    print(await pg.evaluate("()=>[...document.querySelectorAll('#p-type option')].slice(0,5).map(o=>o.textContent)"))
    for fn in ['exportPPTX','exportVSDX','exportDrawio']:
      print(fn, await pg.evaluate(f"()=>typeof window.{fn}"))
    print('errs',errs); await b.close()
asyncio.run(m())
