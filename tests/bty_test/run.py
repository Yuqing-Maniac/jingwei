import asyncio, base64, sys, os
from playwright.async_api import async_playwright
OUT='/home/claude/drawtool/bty_test/out'; os.makedirs(OUT,exist_ok=True)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1500,'height':950})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file:///home/claude/drawtool/offline.html'); await pg.wait_for_timeout(700)
    for f in sys.argv[1:]:
      name=os.path.splitext(os.path.basename(f))[0]
      data=base64.b64encode(open(f,'rb').read()).decode()
      await pg.evaluate('''async ([d,n])=>{const bin=Uint8Array.from(atob(d),c=>c.charCodeAt(0));await openForeign(new File([bin],n));}''',[data,os.path.basename(f)])
      await pg.wait_for_timeout(400)
      await pg.locator('#stage').screenshot(path=f'{OUT}/{name}_0.png')
      info=await pg.evaluate('''()=>P().nodes.map(n=>n.type+':'+(n.text||'').slice(0,8)+':'+n.w+'x'+n.h+':s'+n.size).join(' | ')''')
      print(name,'BEFORE',info[:1500])
      await pg.click('#b-beauty'); await pg.wait_for_timeout(400)
      await pg.evaluate('fit()')
      await pg.locator('#stage').screenshot(path=f'{OUT}/{name}_1.png')
      info=await pg.evaluate('''()=>P().nodes.map(n=>n.type+':'+(n.text||'').slice(0,8)+':'+n.w+'x'+n.h+':s'+n.size).join(' | ')''')
      print(name,'AFTER',info[:1500])
    print('errs',errs); await b.close()
asyncio.run(main())
