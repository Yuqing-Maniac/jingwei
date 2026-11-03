import time
IDS = ['036','037','038','039','040','041','042']
SH = '/tmp/claude-0/s/'

def zoomto(r, wx, wy, k, dur=1.0):
    r.page.evaluate("""([wx,wy,k,dur])=>new Promise(res=>{
      const s=document.getElementById('svg').getBoundingClientRect();
      const x0=view.x,y0=view.y,k0=view.k,k1=k;
      const t0=performance.now();
      (function f(){const t=Math.min(1,(performance.now()-t0)/(dur*1000)),e=t*t*(3-2*t);
        view.k=k0+(k1-k0)*e;
        const cx0=x0+s.width/2/k0,cy0=y0+s.height/2/k0,cx=cx0+(wx-cx0)*e,cy=cy0+(wy-cy0)*e;
        view.x=cx-s.width/2/view.k;view.y=cy-s.height/2/view.k;applyView();
        if(t<1)requestAnimationFrame(f);else res();})()})""", [wx, wy, k, dur])

def center(r):
    return r.page.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [view.x+s.width/2/view.k,view.y+s.height/2/view.k,view.k]}")

def shot(r, n):
    return
    try: r.page.screenshot(path=SH + 'fin_' + n + '.png')
    except Exception: pass

def hover(r, loc, dur=0.3):
    bb = loc.bounding_box(); r.move(bb['x']+bb['width']/2, bb['y']+bb['height']/2, dur)

def settheme(r, k):
    r.page.select_option('#b-theme', k)
    r.page.evaluate("()=>document.getElementById('b-theme').dispatchEvent(new Event('change'))")

def _tmove(self, x, y, dur=0.6):
    x0, y0 = self.mx, self.my; t0 = time.time()
    while True:
        t = (time.time() - t0) / dur
        if t >= 1: break
        e = t * t * (3 - 2 * t)
        self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
    self.page.mouse.move(x, y); self.mx, self.my = x, y

D = {}
def begin(i):
    import subprocess
    D['t'] = time.time(); D['b'] = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','/home/claude/video/t6/audio/%s.mp3'%i],capture_output=True,text=True).stdout) + 0.1
def left(): return D['b'] - (time.time() - D['t'])

def setup(r):
    import types
    r.move = types.MethodType(_tmove, r)
    import os; os.makedirs(SH, exist_ok=True)
    r.page.evaluate("()=>{fit();clearSel();render()}")
    r.mx, r.my = 960, 600

def a036(r):
    begin('036')
    t0 = time.time()
    r.press('Control+Shift+M', 'Ctrl + Shift + M　版式模板')
    r.wait(0.25)
    cards = r.page.locator('.tpl-card')
    n = cards.count()
    # fast sweep over regular cards
    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        if i < n and left() > 3.6:
            hover(r, cards.nth(i), 0.16)
    shot(r, '036a')
    # scroll to standard views
    r.page.evaluate("()=>{const b=document.querySelector('.tpl-b');window.__tb=b}")
    for _ in range(3):
        r.page.mouse.wheel(0, 330); r.wait(0.15)
    shot(r, '036b')
    for i in range(9, n):
        c = cards.nth(i)
        if c.is_visible() and left() > 0.2: hover(r, c, 0.2)
    shot(r, '036c')
    print('036 used', time.time() - t0)

def a037(r):
    begin('037')
    T=time.time()
    cards = r.page.locator('.tpl-card')
    r.page.evaluate("()=>{const b=document.querySelector('.tpl-b');b.scrollTop=0}")
    c = r.page.locator('.tpl-card', has_text='装备组网').first
    hover(r, c, 0.15)
    r.click(xy=(r.mx, r.my), dur=0.05, after=0.02)
    hover(r, r.page.locator('#tpl-use'), 0.15)
    r.click(xy=(r.mx, r.my), dur=0.05, after=0.05)
    print('037 tpl',time.time()-T); r.page.evaluate("()=>{fit()}")
    # rename an element
    try:
        x, y = r.page.evaluate("""()=>{const n=P().nodes.find(n=>(n.text||'').includes('地面控制'))||P().nodes[3];const s=document.getElementById('svg').getBoundingClientRect();return [(n.x+n.w/2-view.x)*view.k+s.left,(n.y+n.h/2-view.y)*view.k+s.top]}""")
        r.move(x, y, 0.15); r.page.mouse.dblclick(x, y); r.wait(0.08)
        r.page.keyboard.press('Control+a'); r.type('指控中心', cps=60)
        print('037 t',time.time()-T)
        r.page.keyboard.press('Control+Enter'); r.page.keyboard.press('Escape')
    except Exception as e:
        print('rename fail', e)

def a038(r):
    begin('038')
    hover(r, r.page.locator('#b-theme'), 0.25)
    for k in ['command', 'report', 'ink']:
        settheme(r, k); r.wait(0.45)
        shot(r, '038_' + k)
    settheme(r, 'command'); r.wait(0.2)
    r.press('F1', 'F1　快捷键一览'); r.wait(1.0)
    shot(r, '038f1')
    r.page.keyboard.press('Escape'); r.wait(0.2)

def a039(r):
    begin('039')
    r.keys('Ctrl + E　导出')
    r.page.keyboard.press('Control+e'); r.wait(0.3)
    if not r.page.locator('#m-export.open').count(): r.click('#b-export', dur=0.2, after=0.1)
    shot(r, '039a')
    with r.page.expect_download():
        hover(r, r.page.locator('[data-exp=pptx]'), 0.3)
        r.click(xy=(r.mx, r.my), dur=0.05, after=0.2)
    r.click('#b-export', dur=0.2, after=0.05)
    hover(r, r.page.locator('[data-exp=vsdx]'), 0.25); r.wait(max(0,min(0.8,left()-1.2)))
    shot(r, '039b')
    hover(r, r.page.locator('[data-exp=png]'), 0.25); r.wait(max(0,min(0.8,left()-0.1)))
    shot(r, '039c')
    r.page.keyboard.press('Escape')
    r.page.evaluate("()=>document.querySelectorAll('.menu.open').forEach(m=>m.classList.remove('open'))")

def a040(r):
    begin('040')
    pg = r.page
    # 1 text-gen
    r.press('Control+Shift+G', 'Ctrl + Shift + G　文字成图'); r.wait(0.15)
    shot(r, '040a')
    pg.keyboard.press('Escape'); pg.evaluate("()=>{const e=document.getElementById('tg-x')||document.querySelector('#tg-cancel');if(e)e.click()}"); r.wait(0.1)
    # 2 palette drag
    try:
        src = pg.evaluate("""()=>{const it=document.querySelector('#palette .pitem[draggable=true]');const b=it.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2]}""")
        r.drag(tuple(src), (1100, 700), 0.2)
    except Exception as e: print('pal', e)
    shot(r, '040b')
    # 3 beautify
    r.press('Control+Shift+F', 'Ctrl + Shift + F　一键美化'); r.wait(0.15)
    # 4 checker
    r.press('Control+Shift+K', 'Ctrl + Shift + K　规范自检'); r.wait(0.2)
    shot(r, '040d')
    pg.evaluate("()=>{const e=document.getElementById('std-close');if(e)e.click()}"); r.wait(0.1)
    # 5 export
    r.press('Control+Shift+O', 'Ctrl + Shift + O　格式互通'); r.wait(0.25)
    shot(r, '040e')
    pg.evaluate("()=>{try{Convert.close()}catch(e){}}")
    pg.evaluate("()=>{document.querySelectorAll('.menu.open').forEach(m=>m.classList.remove('open'));const n=P().nodes;const i=n.findIndex(x=>x.text==='矩形');if(i>=0)n.splice(i,1);sel.clear();render()}")

def a041(r):
    begin('041')
    pg = r.page
    pg.evaluate("()=>{try{window.__ov&&window.__ov.remove()}catch(e){};clearSel();render();fit()}")
    r.move(1500, 1000, 0.2)
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='chips';d.style.cssText='position:fixed;left:0;right:0;bottom:70px;display:flex;justify-content:center;gap:22px;z-index:99999;pointer-events:none';
      ['绿色','离线','免费','高效','好用','普惠'].forEach(t=>{const c=document.createElement('div');c.textContent=t;c.style.cssText='font:700 44px "Noto Sans CJK SC",sans-serif;color:#eaffef;padding:12px 30px;border-radius:14px;background:rgba(10,40,24,.78);border:2px solid #4cff9a;box-shadow:0 0 28px #28e07a,0 0 6px #7dffbd inset;opacity:0;transform:translateY(24px) scale(.8);transition:all .35s cubic-bezier(.2,1.4,.4,1)';d.appendChild(c)});document.body.appendChild(d)}""")
    c0 = center(r); t0 = time.time()
    zoomto(r, c0[0], c0[1], c0[2] * 1.35, 4.2) if False else None
    import threading
    t0 = time.time()
    def zoom_bg(): pass
    # chips timed; slow zoom via animation started non-blocking
    pg.evaluate("""([cx,cy,k])=>{const s=document.getElementById('svg').getBoundingClientRect();const x0=view.x,y0=view.y,k0=view.k,k1=k*1.14,t0=performance.now(),D=4300;
      (function f(){const t=Math.min(1,(performance.now()-t0)/D),e=t;view.k=k0+(k1-k0)*e;view.x=cx-s.width/2/view.k;view.y=cy-s.height/2/view.k;applyView();if(t<1)requestAnimationFrame(f)})()}""", c0)
    for i in range(6):
        pg.evaluate("(i)=>{const c=document.querySelectorAll('#chips div')[i];c.style.opacity=1;c.style.transform='none'}", i)
        r.wait(max(0, (i + 1) * 0.62 - (time.time() - t0)))
    shot(r, '041')

def a042(r):
    begin('042')
    pg = r.page
    pg.evaluate("()=>{const d=document.getElementById('chips');if(d){d.style.transition='opacity .4s';d.style.opacity=0}}")
    r.wait(0.4)
    pg.evaluate("()=>{document.getElementById('chips')&&document.getElementById('chips').remove();fit()}")
    r.move(1900, 1070, 0.3)
    shot(r, '042')

ACTIONS = {'036': a036, '037': a037, '038': a038, '039': a039, '040': a040, '041': a041, '042': a042}
