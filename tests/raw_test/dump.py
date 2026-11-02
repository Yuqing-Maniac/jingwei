import asyncio, base64, sys, json
from playwright.async_api import async_playwright
from jw_paths import OFFLINE_URL
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page()
    await pg.goto(OFFLINE_URL); await pg.wait_for_timeout(500)
    data=base64.b64encode(open(sys.argv[1],'rb').read()).decode()
    r=await pg.evaluate('''async (d)=>{const bin=Uint8Array.from(atob(d),c=>c.charCodeAt(0));
      const P=await VsdxRaw.parse(bin.buffer);const out=[];
      const f=(it,dep)=>{out.push('  '.repeat(dep)+it.id+' '+it.name+' fill='+JSON.stringify(it.fill)+' line='+JSON.stringify(it.line&&{c:it.line.c,w:it.line.w})+' paths='+it.paths.length+(it.text?' text='+JSON.stringify(it.text.paras.map(p=>p.runs.map(r=>[r.t.slice(0,20),r.sz.toFixed(1),r.c,r.latin,r.ea,r.b]))):''));(it.kids||[]).forEach(k=>f(k,dep+1))};
      P.pages.forEach((pg,i)=>{out.push('PAGE '+pg.name+' '+pg.w.toFixed(2)+'x'+pg.h.toFixed(2));pg.items.forEach(it=>f(it,1))});return out.join('\n')}''',data)
    print(r); await b.close()
asyncio.run(main())
