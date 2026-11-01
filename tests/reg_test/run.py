import asyncio, os
from playwright.async_api import async_playwright
from PIL import Image
OLD='file:///home/claude/pkg/HongTu_v2.7/HongTu_v2.7.html'; NEW='file:///home/claude/drawtool/offline.html'
async def shots(url,tag,b):
    pg=await b.new_page(viewport={'width':1400,'height':900}); await pg.goto(url); await pg.wait_for_timeout(700)
    n=await pg.evaluate('(window.TEMPLATES||[]).length')
    out=[]
    for i in range(-1,n):
        await pg.evaluate('''(i)=>{const d=i<0?buildDemo():(()=>{const t=TEMPLATES[i];const r=t.build();return r.pages?r:{name:t.name,theme:doc.theme,statusLabels:doc.statusLabels,custom:doc.custom,pages:{root:r}}})();loadDoc(JSON.parse(JSON.stringify(d)));beautify();render();fit();}''',i)
        await pg.wait_for_timeout(200)
        f=f'{tag}_{i+1}.png'; await pg.locator('#stage').screenshot(path=f); out.append(f)
    await pg.close(); return out
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    a=await shots(OLD,'old',b); c=await shots(NEW,'new',b)
    for x,y in zip(a,c):
        A=Image.open(x); B=Image.open(y); C=Image.new('RGB',(A.width*2+10,A.height),'red'); C.paste(A,(0,0)); C.paste(B,(A.width+10,0)); C.thumbnail((1400,500)); C.save('cmp_'+x[4:])
    print(len(a)); await b.close()
asyncio.run(main())
