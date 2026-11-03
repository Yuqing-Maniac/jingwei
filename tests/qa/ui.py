import os, json
from playwright.sync_api import sync_playwright
O='/tmp/claude-0/bh/ui/'; os.makedirs(O,exist_ok=True)
log=[]
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000},accept_downloads=True)
  errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300])); pg.on('console',lambda m: errs.append('console:'+m.text[:200]) if m.type=='error' else None)
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  def step(name, fn):
    errs.clear()
    try: r=fn()
    except Exception as e: r='EXC '+str(e)[:200]
    pg.wait_for_timeout(120)
    bad=pg.evaluate("()=>{let k=0;for(const p of Object.values(doc.pages))for(const n of p.nodes)if(![n.x,n.y,n.w,n.h].every(isFinite))k++;return k}")
    if errs or bad or (isinstance(r,str) and r.startswith('EXC')): print('!!',name,r,errs[:3],'NaN' if bad else '')
    else: print('ok',name, r if r is not None else '')
  N=lambda: pg.evaluate("()=>P().nodes.length")
  step('new blank', lambda: (pg.click('#b-new'), pg.wait_for_timeout(300), N())[-1])
  # add every palette item by click
  def addall():
    n=pg.locator('.pitem[data-add]').count(); c0=N()
    # open all sections
    pg.evaluate("()=>document.querySelectorAll('#pal details, .sec').forEach(d=>{if(d.tagName==='DETAILS')d.open=true})")
    items=pg.evaluate("()=>[...document.querySelectorAll('.pitem[data-add]')].map(e=>e.dataset.add)")
    pg.evaluate("""(items)=>{for(const a of items){const s=JSON.parse(a);const el=[...document.querySelectorAll('.pitem[data-add]')].find(e=>e.dataset.add===a); if(el) el.click();}}""", items[:80])
    return (len(items), N()-c0)
  step('click-add palette items (first 80)', addall)
  step('beautify mixed', lambda: (pg.keyboard.press('Control+Shift+F'), N())[-1])
  step('render all shape types', lambda: pg.evaluate("()=>{const p=P();Object.keys(SHP_DEF).forEach((k,i)=>p.nodes.push(mkNode({type:k,text:k,x:i*130,y:2000,w:110,h:56})));render();return p.nodes.length}"))
  step('select all + copy + paste', lambda: (pg.keyboard.press('Control+A'), pg.keyboard.press('Control+C'), pg.keyboard.press('Control+V'), N())[-1])
  step('undo', lambda: (pg.keyboard.press('Control+Z'), N())[-1])
  step('redo', lambda: (pg.keyboard.press('Control+Y'), N())[-1])
  step('delete all', lambda: (pg.keyboard.press('Control+A'), pg.keyboard.press('Delete'), N())[-1])
  step('undo delete', lambda: (pg.keyboard.press('Control+Z'), N())[-1])
  step('load demo', lambda: pg.evaluate("()=>{loadDoc(buildDemo());fit();render();return P().nodes.length}"))
  # drag a node with mouse
  def drag():
    xy=pg.evaluate("()=>{const n=P().nodes.find(n=>n.text==='一线管控站');const r=document.getElementById('svg').getBoundingClientRect();return [r.left+(n.x+n.w/2-view.x)*view.k, r.top+(n.y+n.h/2-view.y)*view.k, n.x]}")
    pg.mouse.move(xy[0],xy[1]); pg.mouse.down(); pg.mouse.move(xy[0]+60,xy[1]+5,steps=8); pg.mouse.up()
    return pg.evaluate("()=>P().nodes.find(n=>n.text==='一线管控站').x")-xy[2]
  step('drag node', drag)
  def resize():
    pg.evaluate("()=>{const n=P().nodes.find(n=>n.text==='一线管控站');sel=new Set([n.id]);render()}")
    h=pg.locator('[data-h]').first
    if not h.count(): return 'no handle'
    bb=h.bounding_box(); pg.mouse.move(bb['x']+3,bb['y']+3); pg.mouse.down(); pg.mouse.move(bb['x']+40,bb['y']+20,steps=6); pg.mouse.up()
    return pg.evaluate("()=>{const n=P().nodes.find(n=>n.text==='一线管控站');return [n.w,n.h]}")
  step('resize via handle', resize)
  step('arrow nudge', lambda: (pg.keyboard.press('ArrowRight'), pg.keyboard.press('Shift+ArrowDown'), 'ok')[-1])
  step('Ctrl+D duplicate', lambda: (pg.keyboard.press('Control+d'), N())[-1])
  # property panel edits
  def props():
    pg.evaluate("()=>{const n=P().nodes.find(n=>n.text==='联合值班席');selectNodes([n.id]);render()}")
    out=[]
    for t in ['roundL','roundR','diamond','ellipse','hexagon','rect']:
      pg.select_option('#p-type', t); pg.wait_for_timeout(60)
      out.append(pg.evaluate("()=>nodeById([...sel][0]).type"))
    return out
  step('property: shape switch', props)
  def status():
    btns=pg.locator('#props [data-st], #props .seg button').count()
    for i in range(min(btns,6)): 
      try: pg.locator('#props [data-st], #props .seg button').nth(i).click(timeout=1000)
      except Exception: pass
    return btns
  step('property: status/seg buttons', status)
  def fsize():
    el=pg.locator('#p-size')
    if not el.count(): return 'no #p-size'
    el.fill('18'); el.dispatch_event('change'); el.dispatch_event('input')
    return pg.evaluate("()=>nodeById([...sel][0]).size")
  step('property: font size', fsize)
  def sub():
    b2=[x for x in ['#p-sub','#p-mksub'] if pg.locator(x).count()]
    btn=pg.locator('button:has-text("创建内部结构")')
    if not btn.count(): return 'no sub button'
    btn.first.click(); pg.wait_for_timeout(300)
    return (len(pg.evaluate("()=>Object.keys(doc.pages)")), pg.evaluate("()=>cur"))
  step('create sub page', sub)
  step('go back root', lambda: pg.evaluate("()=>{const b=[...document.querySelectorAll('#crumbs a,#crumb a,.crumb a,[data-page]')]; if(b[0]) b[0].click(); return cur}"))
  def save_reopen():
    with pg.expect_download() as d: pg.keyboard.press('Control+s')
    f=O+d.value.suggested_filename; d.value.save_as(f)
    n0=pg.evaluate("()=>Object.values(doc.pages).reduce((a,p)=>a+p.nodes.length,0)")
    pg.click('#b-new'); pg.wait_for_timeout(200)
    pg.set_input_files('#f-open',f); pg.wait_for_timeout(800)
    n1=pg.evaluate("()=>Object.values(doc.pages).reduce((a,p)=>a+p.nodes.length,0)")
    return (os.path.basename(f),n0,n1)
  step('save .jingwei.json + reopen', save_reopen)
  # links: select a link and press keys
  def linkkeys():
    pg.evaluate("()=>{selectLinks([P().links[0].id]);render()}")
    for k in ['1','2','3','4','5','6','d','r']: pg.keyboard.press(k)
    return pg.evaluate("()=>{const l=P().links.find(l=>l.id===onlyLinkId());return [l.kind,l.dir]}")
  step('link keys 1-6 d r', linkkeys)
  # textgen
  def textgen(src):
    pg.keyboard.press('Escape'); pg.keyboard.press('Control+Shift+G'); pg.wait_for_timeout(400)
    ta=pg.locator('#tg-src, #tg textarea').first; ta.fill(src); pg.wait_for_timeout(900)
    pg.click('#tg-go'); pg.wait_for_timeout(900)
    return pg.evaluate("()=>[P().nodes.length,P().links.length]")
  step('textgen markdown', lambda: textgen("# 测试体系\n## 指控层\n- 指挥所、数据中心\n## 平台层\n- 无人机 [新增]\n- 无人艇\n- 指挥所 -> 无人机 : 指令"))
  step('textgen prose', lambda: textgen("某海上巡逻体系分为指挥层、通信层和平台层。指挥层包括岸基指挥所和值班席。通信层由卫通站和微波站组成。平台层包括巡逻无人机、无人艇。岸基指挥所通过卫通站向巡逻无人机下达指令。"))
  def refgen():
    pg.keyboard.press('Escape'); pg.keyboard.press('Control+Shift+L'); pg.wait_for_timeout(500)
    r=pg.evaluate("()=>{const e=document.querySelector('input[name=rg-eng][value=rule]'); if(e){e.click();} return !!e}")
    ta=pg.locator('#rg textarea, [id^=rg-] textarea').first
    if ta.count(): ta.fill("# 新项目\n## 指控层\n- 新指挥所\n## 平台层\n- 新无人机")
    btns=pg.evaluate("()=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&/生成/.test(b.textContent)).map(b=>b.id||b.textContent)")
    gb=pg.locator('button:visible:has-text("生成")').last
    if gb.count(): gb.click(); pg.wait_for_timeout(1200)
    return (r,btns,pg.evaluate("()=>P().nodes.length"))
  step('refgen offline', refgen)
  pg.keyboard.press('Escape'); pg.keyboard.press('Escape')
  step('load demo2', lambda: pg.evaluate("()=>{loadDoc(buildDemo());fit();render();return P().nodes.length}"))
  for combo in ['F1','Escape','Control+e','Escape','Control+Shift+K','Escape','Control+Shift+M','Escape','Control+Shift+O','Escape','Control+Shift+B','Escape','Control+0','Control+=','Control+-','Control+Shift+X','Control+Shift+F']:
    step('key '+combo, lambda c=combo: (pg.keyboard.press(c), pg.wait_for_timeout(250), 'ok')[-1])
  def kicon():
    pg.evaluate("()=>{const n=P().nodes.find(n=>n.text==='联合值班席');sel=new Set([n.id]);render()}")
    pg.keyboard.press('Control+k'); pg.wait_for_timeout(300)
    vis=pg.evaluate("()=>[...document.querySelectorAll('.modal,#modal,#ico-pick,#iconpick')].some(e=>e.offsetParent)")
    pg.keyboard.press('Escape'); return vis
  step('Ctrl+K icon picker', kicon)
  def combo_g():
    pg.evaluate("()=>{const ns=P().nodes.filter(n=>n.type==='equip').slice(0,2);sel=new Set(ns.map(n=>n.id));render()}")
    pg.keyboard.press('Control+g'); pg.wait_for_timeout(300)
    pg.keyboard.press('Control+Shift+U'); pg.wait_for_timeout(300); return N()
  step('Ctrl+G group / Ctrl+Shift+U ungroup', combo_g)
  def themes():
    opts=pg.evaluate("()=>[...document.querySelectorAll('#b-theme option')].map(o=>o.value)")
    for o in opts: pg.select_option('#b-theme',o); pg.wait_for_timeout(80)
    return len(opts)
  step('themes switch', themes)
  def snapres():
    pg.evaluate("()=>{const n=P().nodes.find(n=>n.text==='一线管控站');sel=new Set([n.id]);render()}")
    return 'ok'
  step('final render', lambda: pg.evaluate("()=>{render();return document.querySelectorAll('#svg *').length}"))
  b.close()
