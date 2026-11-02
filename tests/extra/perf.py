import asyncio,time
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':950})
    c=await pg.context.new_cdp_session(pg); await c.send('Emulation.setCPUThrottlingRate',{'rate':4})
    t=time.time(); await pg.goto('file:///home/claude/drawtool/offline.html',wait_until='load'); print('load s',round(time.time()-t,2))
    print('render ms',await pg.evaluate("()=>{const t=performance.now();for(let i=0;i<5;i++)render();return (performance.now()-t)/5}"))
    print('beautify ms',await pg.evaluate("()=>{const t=performance.now();try{(window.beautify||window.tidyAll||(()=>{}))()}catch(e){};render();return performance.now()-t}"))
    print('heap MB',await pg.evaluate("()=>performance.memory.usedJSHeapSize/1e6"))
    await pg.set_input_files('#f-open','/home/claude/vfx/cn/cn_arch.vsdx'); t=time.time(); await pg.wait_for_timeout(100)
    await pg.wait_for_function("P().nodes.length>20"); print('open vsdx s',round(time.time()-t,2))
    await b.close()
asyncio.run(m())
