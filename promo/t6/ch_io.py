"""互通与转换（035a–035c）：打开 Visio、格式转换原样还原、报告版心"""
import time, base64
IDS = ['035a', '035b', '035c']
SH = '/tmp/claude-0/t6io_'
V = '/home/claude/vfx/cn/'

def zoomto(r, wx, wy, k, dur=1.0):
    r.page.evaluate("""([wx,wy,k,dur])=>new Promise(res=>{
      const s=document.getElementById('svg').getBoundingClientRect();
      const x0=view.x,y0=view.y,k0=view.k;
      const t0=performance.now();
      (function f(){const t=Math.min(1,(performance.now()-t0)/(dur*1000)),e=t*t*(3-2*t);
        view.k=k0+(k-k0)*e;
        const cx0=x0+s.width/2/k0,cy0=y0+s.height/2/k0,cx=cx0+(wx-cx0)*e,cy=cy0+(wy-cy0)*e;
        view.x=cx-s.width/2/view.k;view.y=cy-s.height/2/view.k;applyView();
        if(t<1)requestAnimationFrame(f);else res();})()})""", [wx, wy, k, dur])

def install(r):
    pg = r.page
    def move(x, y, dur=0.6):
        x0, y0 = r.mx, r.my; t0 = time.time()
        while True:
            t = min(1.0, (time.time() - t0) / max(dur, 0.01)); e = t * t * (3 - 2 * t)
            pg.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            if t >= 1: break
        r.mx, r.my = x, y
    r.move = move

def center_of(r, sel):
    b = r.page.locator(sel).first.bounding_box(); return (b['x'] + b['width'] / 2, b['y'] + b['height'] / 2)

def setup(r):
    install(r)
    r.page.evaluate("()=>{fit();clearSel();render()}")
    r.page.mouse.move(960, 600); r.mx, r.my = 960, 600
    u = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    r.page.evaluate("""([a,b])=>{window.__cmp=[a,b];
      const st=document.createElement('style');st.textContent=`
      #cmpov{position:fixed;inset:0;z-index:99990;background:rgba(6,14,30,.86);display:flex;align-items:center;justify-content:center;gap:34px;opacity:0;transition:opacity .35s}
      #cmpov.on{opacity:1}
      #cmpov figure{margin:0;background:#fff;border-radius:14px;padding:12px;box-shadow:0 18px 60px rgba(0,0,0,.5);transform:translateY(40px) scale(.94);transition:transform .45s cubic-bezier(.2,1.2,.4,1)}
      #cmpov.on figure{transform:none}
      #cmpov img{width:820px;display:block;border-radius:6px}
      #cmpov figcaption{font:700 30px 'Noto Sans CJK SC',sans-serif;color:#13305e;text-align:center;padding:10px 0 2px}
      #cmpov figcaption b{color:#E07B00}`;document.head.appendChild(st)}""", [u('/home/claude/video/t6/hi_src.png'), u('/home/claude/video/t6/hi_ppt.png')])

def a035a(r):
    pg = r.page
    r.keys('Ctrl + O　打开 Visio／PPT／draw.io', 1.4)
    pg.set_input_files('#f-open', V + 'cn_arch.vsdx'); r.wait(0.9)
    pg.evaluate("()=>{fit()}"); r.wait(0.4)
    c = pg.evaluate("()=>{const b=P().nodes.find(n=>n.type==='band');return b?[b.x+b.w/2,b.y+b.h/2]:null}")
    if c:
        zoomto(r, c[0], c[1], pg.evaluate('()=>view.k') * 1.3, 0.9)
        for nm in ['光电侦察吊舱', '合成孔径雷达', '电子侦察']:
            try: r.move(*r.node_xy(nm), 0.35); r.wait(0.15)
            except Exception as e: print('nx', e)
    r.wait(0.3)
    pg.screenshot(path=SH + '035a.png')
    for nm in ['任务规划', '态势融合', '协同分配', '人在回路确认']:
        try: r.move(*r.node_xy(nm), 0.35); r.wait(0.12)
        except Exception as e: print('nx', e)
    pg.evaluate("()=>{const v={...view};fit();window.__fv={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView()}")
    f = pg.evaluate("()=>window.__fv"); s = pg.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [s.width,s.height]}")
    zoomto(r, f['x'] + s[0] / 2 / f['k'], f['y'] + s[1] / 2 / f['k'], f['k'], 0.9)

def a035b(r):
    pg = r.page
    r.press('Control+Shift+O', 'Ctrl + Shift + O　格式转换')
    r.wait(0.3)
    pg.set_input_files('#cv-f', [V + 'cn_arch.vsdx', V + 'flow.vsdx', V + 'flow_frame.vsdx']); r.wait(0.35)
    r.click('#cv-tg input[value=pptx]', dur=0.35, after=0.1)
    r.click('#cv .cv-opt input[value=keep]', dur=0.3, after=0.1)
    r.click('#cv-go', dur=0.35, after=0.1)
    try: pg.wait_for_function("document.querySelector('#cv-msg').textContent.includes('已完成')", timeout=15000)
    except Exception as e: print('conv wait', e)
    r.wait(0.6)
    pg.screenshot(path=SH + '035b1.png')
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='cmpov';
      d.innerHTML=`<figure><img src="${window.__cmp[0]}"><figcaption>Visio 原图</figcaption></figure><figure><img src="${window.__cmp[1]}"><figcaption>转出的 PPT　<b>字号一致</b></figcaption></figure>`;
      document.body.appendChild(d);requestAnimationFrame(()=>requestAnimationFrame(()=>d.classList.add('on')))}""")
    r.wait(2.4)
    pg.screenshot(path=SH + '035b2.png')

def a035c(r):
    pg = r.page
    pg.evaluate("()=>{const d=document.getElementById('cmpov');if(d){d.classList.remove('on');setTimeout(()=>d.remove(),400)}}")
    pg.evaluate("()=>{Convert.close()}"); r.wait(0.35)
    pg.evaluate("()=>{loadDoc(buildDemo());clearSel();render();fit()}"); r.wait(0.3)
    r.keys('报告版心　插进 Word 即为版心宽', 1.6)
    try:
        r.click('#d-lay [data-v=report]', dur=0.4, after=0.6)
    except Exception as e: print('lay', e)
    pg.screenshot(path=SH + '035c1.png')
    r.click('#b-export', dur=0.35, after=0.25)
    try:
        r.click('[data-exp=pngrep]', dur=0.35, after=0.5)
    except Exception as e: print('exp', e)
    pg.screenshot(path=SH + '035c2.png')
    r.wait(0.4)

ACTIONS = {i: globals()['a' + i] for i in IDS}
