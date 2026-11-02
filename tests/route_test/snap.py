import asyncio
from playwright.async_api import async_playwright
from jw_paths import OFFLINE_URL
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':900})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(OFFLINE_URL); await pg.wait_for_timeout(600)
    await pg.evaluate('''()=>{
      const N=(id,x,y,t,w=120,h=44)=>mkNode({id,type:'rect',x,y,w,h,text:t});
      const nodes=[N('a',0,0,'甲'),N('b',200,0,'乙'),N('c',400,0,'丙'),N('d',100,160,'拖我'),N('e',520,300,'戊',160,60)];
      loadDoc({name:'t',theme:doc.theme,statusLabels:doc.statusLabels,custom:{},pages:{root:{id:'root',name:'吸附测试',nodes,links:[]}}});render();fit();}''')
    C=lambda id: pg.evaluate('''(id)=>{const n=nodeById(id),r=svg.getBoundingClientRect();return [(n.x+n.w/2-view.x)*view.k+r.left,(n.y+n.h/2-view.y)*view.k+r.top,view.k]}''',id)
    x,y,k=await C('d')
    await pg.mouse.move(x,y); await pg.mouse.down()
    # 目标：中心 x 对齐“乙”中心（260），往右移 ~97 世界单位（d 中心 160→257）
    for i in range(1,11): await pg.mouse.move(x+97*k*i/10, y+20*k*i/10)
    await pg.wait_for_timeout(100)
    g=await pg.evaluate('JSON.stringify(ui.guides)'); print('guides',g)
    await pg.screenshot(path='snap1.png')
    await pg.mouse.up()
    print('d after', await pg.evaluate('(()=>{const n=nodeById("d");return [n.x,n.y]})()'))
    # 等间距：把 c 挪到 b 右侧，间距等于 a-b 间距（80）
    x,y,k=await C('c')
    await pg.mouse.move(x,y); await pg.mouse.down()
    for i in range(1,11): await pg.mouse.move(x+(-3)*k*i/10, y+(150)*k*i/10)
    await pg.wait_for_timeout(100); print('guides2',await pg.evaluate('JSON.stringify(ui.guides)'))
    await pg.screenshot(path='snap2.png'); await pg.mouse.up()
    print('errs',errs); await b.close()
asyncio.run(main())
