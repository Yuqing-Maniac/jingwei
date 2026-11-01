import asyncio, base64, sys, os, json
from playwright.async_api import async_playwright
from jw_paths import DRAWTOOL, OFFLINE_URL
files=sys.argv[1:]
OUT=str(DRAWTOOL/'raw_test'/'out')
os.makedirs(OUT,exist_ok=True)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and errs.append(m.text))
    await pg.goto(OFFLINE_URL); await pg.wait_for_timeout(600)
    for f in files:
      data=base64.b64encode(open(f,'rb').read()).decode()
      try:
        r=await pg.evaluate('''async (d)=>{const bin=Uint8Array.from(atob(d),c=>c.charCodeAt(0));
          const parsed=await VsdxRaw.parse(bin.buffer);const blob=await VsdxRaw.toPPTX(parsed,{});
          const u=new Uint8Array(await blob.arrayBuffer());let s='';for(let i=0;i<u.length;i+=8192)s+=String.fromCharCode.apply(null,u.subarray(i,i+8192));
          return {b:btoa(s),w:parsed.warnings,n:parsed.pages.length}}''',data)
        name=os.path.splitext(os.path.basename(f))[0]
        open(f'{OUT}/{name}.pptx','wb').write(base64.b64decode(r['b'])); print(name,'pages',r['n'],'warn',r['w'])
      except Exception as e: print('FAIL',f,str(e)[:300])
    print('errs',errs[:5]); await b.close()
asyncio.run(main())
