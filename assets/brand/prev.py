import asyncio, base64
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1100,'height':560})
    u=lambda f:'data:image/svg+xml;base64,'+base64.b64encode(open(f,'rb').read()).decode()
    html=f'<body style="margin:0;background:#E9EDF2;display:flex;gap:30px;align-items:center;padding:20px"><img src="{u("icon.svg")}" width=512><div style="display:flex;flex-direction:column;gap:16px">'+''.join(f'<div style="display:flex;gap:16px;align-items:center"><img src="{u("icon_small.svg")}" width={z}><span>{z}px</span></div>' for z in (128,64,32,16))+f'</div><div style="background:#1d1f24;padding:20px"><img src="{u("icon.svg")}" width=256></div></body>'
    await pg.set_content(html); await pg.wait_for_timeout(300); await pg.screenshot(path='preview.png'); await b.close()
asyncio.run(m())
