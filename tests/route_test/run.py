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
      const nodes=[N('a',0,0,'指挥中心'),N('m',220,0,'中继站'),N('b',440,0,'无人机'),
        N('c',0,200,'雷达'),N('d',220,170,'融合处理',120,110),N('e',440,200,'显控'),
        N('f',0,420,'起点'),N('g',220,380,'障碍A'),N('h',220,470,'障碍B'),N('i',440,420,'终点'),
        N('j',700,0,'上'),N('k',700,180,'中间框'),N('l',700,360,'下')];
      const L=(f,t,label='',kind='data')=>({id:uid(),from:f,to:t,dir:'one',kind,route:'ortho',label});
      const links=[L('a','b','指令'),L('a','b','遥测','ctrl'),L('b','a','回传','radio'),L('c','e','点迹'),L('c','e','航迹','ctrl'),L('f','i','直达'),L('j','l','穿越'),L('l','j','回路','ctrl')];
      loadDoc({name:'t',theme:doc.theme,statusLabels:doc.statusLabels,custom:{},pages:{root:{id:'root',name:'避障测试',nodes,links}}});
      render();fit();}''')
    await pg.wait_for_timeout(300)
    await pg.locator('#stage').screenshot(path='route.png')
    t=await pg.evaluate('''()=>{const out=[];for(let i=0;i<(window.TEMPLATES||[]).length;i++){const t=TEMPLATES[i];const r=t.build();const d=r.pages?r:{name:t.name,theme:doc.theme,statusLabels:doc.statusLabels,custom:doc.custom,pages:{root:r}};loadDoc(JSON.parse(JSON.stringify(d)));beautify();const t0=performance.now();for(let k=0;k<5;k++){computeRoutes(P());}out.push(((performance.now()-t0)/5).toFixed(1));}return out.join(' ')}''')
    print('route ms per template',t); print('errs',errs); await b.close()
asyncio.run(main())
