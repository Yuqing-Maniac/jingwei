import asyncio, os
from playwright.async_api import async_playwright
from jw_paths import DRAWTOOL, VFX, OFFLINE_URL
D=str(DRAWTOOL/'conv_ui'/'dl'); os.makedirs(D,exist_ok=True)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); ctx=await b.new_context(accept_downloads=True,viewport={'width':1400,'height':950}); pg=await ctx.new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    got=[]
    async def ondl(d):
        f=os.path.join(D,d.suggested_filename); await d.save_as(f); got.append(d.suggested_filename)
    pg.on('download',lambda d: asyncio.ensure_future(ondl(d)))
    await pg.goto(OFFLINE_URL); await pg.wait_for_timeout(600)
    await pg.click('#b-conv'); await pg.wait_for_timeout(200)
    await pg.set_input_files('#cv-f',[str(VFX/'cn'/'cn_arch.vsdx'),str(VFX/'dh'/'tests'/'test4_connectors.vsdx')])
    await pg.check('input[name=cv-t][value=pptx]'); await pg.check('input[name=cv-lay][value=keep]')
    await pg.screenshot(path='d1.png')
    await pg.click('#cv-go'); await pg.wait_for_function("document.querySelector('#cv-msg').textContent.includes('已完成')",timeout=60000)
    await pg.wait_for_timeout(800); print('batch1', got, await pg.inner_text('#cv-list'))
    await pg.screenshot(path='d2.png')
    # 继续添加新文件
    await pg.set_input_files('#cv-f',[str(DRAWTOOL/'out'/'cb'/'tpl.vsdx')])
    print('after add:', await pg.inner_text('#cv-list'))
    await pg.check('input[name=cv-lay][value=beauty]')
    await pg.screenshot(path='d3.png')
    await pg.click('#cv-go'); await pg.wait_for_function("document.querySelector('#cv-msg').textContent.includes('已完成')",timeout=60000)
    await pg.wait_for_timeout(800); print('batch2', got, await pg.inner_text('#cv-list'))
    # 重复加同一文件，改目标再转
    await pg.set_input_files('#cv-f',[str(DRAWTOOL/'out'/'cb'/'tpl.vsdx')])
    await pg.check('input[name=cv-t][value=png]'); await pg.click('#cv-go'); await pg.wait_for_function("document.querySelector('#cv-msg').textContent.includes('已完成')",timeout=60000)
    await pg.wait_for_timeout(800); print('batch3', got, await pg.inner_text('#cv-list'))
    print('errs',errs); await b.close()
asyncio.run(main())
