import asyncio
from playwright.async_api import async_playwright
from jw_paths import VFX, OFFLINE_URL
INIT="""delete Blob.prototype.arrayBuffer;delete Blob.prototype.text;delete Object.fromEntries;delete window.DecompressionStream;"""
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':950})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.add_init_script(INIT)
    await pg.goto(OFFLINE_URL); await pg.wait_for_timeout(1500)
    print('poly', await pg.evaluate("()=>[typeof Blob.prototype.arrayBuffer,typeof Object.fromEntries,typeof DecompressionStream]"))
    for f in [str(VFX/'cn'/'cn_arch.vsdx'),str(VFX/'cn'/'flow.vsdx')]:
      await pg.set_input_files('#f-open',f); await pg.wait_for_timeout(1500)
      print(f.split('/')[-1], await pg.evaluate("()=>P().nodes.length"))
    await pg.keyboard.press('Control+Shift+O'); await pg.wait_for_timeout(400)
    await pg.click('#cv-tg input[value=pptx]'); await pg.wait_for_timeout(200)
    print('on', await pg.evaluate("()=>[...document.querySelectorAll('#cv-tg label.on input')].map(i=>i.value)"))
    await pg.set_input_files('#cv-f',[str(VFX/'cn'/'cn_arch.vsdx')])
    async with pg.expect_download() as d:
      await pg.click('#cv-go')
    dl=await d.value; print('dl',dl.suggested_filename)
    print('warn', await pg.evaluate("()=>!!document.getElementById('compat-warn')"))
    print('errs',errs); await b.close()
asyncio.run(m())
