import os
from playwright.sync_api import sync_playwright
O='/tmp/claude-0/bh/exp/'
SIG="()=>{const p=P();return p.nodes.filter(n=>n.text&&!isCont(n)&&!['text','note','legend','tblock'].includes(n.type)).map(n=>n.type+':'+String(n.text).replace(/\\s/g,'')).sort()}"
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  for tid in ['demo','t1','std-sv1','it-deploy','std-ov5b','combo']:
    if tid!='demo':
      ok=pg.evaluate("(i)=>{const t=TEMPLATES.find(x=>x.id===i);if(!t)return false;loadDoc(t.build());fit();render();return true}",tid)
      if not ok: print('no tpl',tid); continue
    else: pg.evaluate("()=>{loadDoc(buildDemo());fit();render()}")
    pg.keyboard.press('Control+Shift+F'); pg.wait_for_timeout(200)
    sig=pg.evaluate(SIG)
    for k in ['png','png4','pngbg','pngrep','pptx','vsdx','drawio','svg']:
      errs.clear()
      try:
        pg.click('#b-export')
        with pg.expect_download(timeout=40000) as d: pg.click(f'[data-exp="{k}"]')
        fn=O+f'{tid}.{d.value.suggested_filename.split(".")[-1]}' if k in('pptx','vsdx','drawio','svg') else O+f'{tid}_{k}.png'
        d.value.save_as(fn)
        if errs: print(tid,k,'ERR',errs[:3])
      except Exception as e: print(tid,k,'FAIL',str(e)[:200]); pg.keyboard.press('Escape')
    # xlsx
    try:
      with pg.expect_download(timeout=30000) as d: pg.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(x=>/导出规范表格/.test(x.textContent));b&&b.click()}")
      d.value.save_as(O+tid+'.xlsx')
    except Exception as e: print(tid,'xlsx FAIL',str(e)[:120])
    # roundtrip
    for ext in ['pptx','vsdx','drawio']:
      f=O+f'{tid}.{ext}'
      if not os.path.exists(f): continue
      errs.clear()
      pg.evaluate("()=>{loadDoc(buildDemo())}")
      pg.set_input_files('#f-open',f); pg.wait_for_timeout(1500)
      s2=pg.evaluate(SIG)
      a,bb=set(sig),set(s2)
      miss=sorted(a-bb); extra=sorted(bb-a)
      if miss or extra or errs: print(tid,ext,'roundtrip missing',miss[:6],'extra',extra[:6],errs[:2])
      if tid!='demo': pg.evaluate("(i)=>{loadDoc(TEMPLATES.find(x=>x.id===i).build());fit();render()}",tid); pg.keyboard.press('Control+Shift+F')
      else: pg.evaluate("()=>{loadDoc(buildDemo());fit();render()}"); pg.keyboard.press('Control+Shift+F')
      pg.wait_for_timeout(200)
  print('done'); b.close()
