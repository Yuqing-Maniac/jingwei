"""互通 chapter (p10, p11): open pptx/vsdx/drawio -> export menu sweep."""
import time, os
IDS = ['p12', 'p13']
SH = '/tmp/claude-0/t7s/'
FX = '/home/claude/drawtool/imp_test/fx/a_layered.pptx'
VS = '/home/claude/drawtool/out/cb/tpl.vsdx'
DIO = '/home/claude/drawtool/dio_test/foreign.drawio'
OUT = '/home/claude/video/t7/seg/'


def shot(r, n):
    if os.environ.get('DBG'):
        try: r.page.screenshot(path=SH + n + '.png')
        except Exception: pass


def _tmove(r, x, y, dur=0.4):
    x0, y0 = r.mx, r.my; t0 = time.time()
    while True:
        t = min(1.0, (time.time() - t0) / max(dur, 0.01)); e = t * t * (3 - 2 * t)
        r.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
        if t >= 1: break
        r.page.wait_for_timeout(16)
    r.mx, r.my = x, y


def hover(r, sel, dur=0.3):
    bb = r.page.locator(sel).first.bounding_box()
    r.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2, dur)


def ring(r):
    r.page.evaluate("([x,y])=>{const g=window.__ring;g.style.left=x+'px';g.style.top=y+'px';g.animate([{opacity:.9,transform:'scale(.4)'},{opacity:0,transform:'scale(1.5)'}],{duration:500})}", [r.mx, r.my])


def clickat(r):
    ring(r); r.page.mouse.click(r.mx, r.my)


def zoomto(r, wx, wy, k, dur=0.6, wait=True):
    r.page.evaluate("""([wx,wy,k,dur,wait])=>{const pr=new Promise(res=>{
      const s=document.getElementById('svg').getBoundingClientRect();
      const x0=view.x,y0=view.y,k0=view.k,k1=k;
      const cx0=x0+s.width/2/k0,cy0=y0+s.height/2/k0;
      const t0=performance.now();
      (function f(){const t=Math.min(1,(performance.now()-t0)/(dur*1000)),e=t*t*(3-2*t);
        view.k=k0+(k1-k0)*e;
        const cx=cx0+(wx-cx0)*e,cy=cy0+(wy-cy0)*e;
        view.x=cx-s.width/2/view.k;view.y=cy-s.height/2/view.k;applyView();
        if(t<1)requestAnimationFrame(f);else res();})()}); if(wait) return pr;}""", [wx, wy, k, dur, wait])


def setup(r):
    pg = r.page
    r.move = lambda x, y, dur=0.4: _tmove(r, x, y, dur)
    _enc = r.encode
    def _encode(path, end_time=None, fps=30):
        r.frames.sort(key=lambda f: f[0]); return _enc(path, end_time, fps)
    r.encode = _encode
    pg.on('download', lambda d: None)
    pg.evaluate("()=>{sel.clear();selLink=null;fit();render()}")
    pg.mouse.move(960, 600); r.mx, r.my = 960, 600
    import base64
    u = lambda f: 'data:image/png;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
    pg.evaluate("""([a,b])=>{window.__cmp=[a,b];
      const st=document.createElement('style');st.textContent=`
      #cmpov{position:fixed;top:0;left:0;right:0;bottom:0;z-index:99990;background:rgba(6,14,30,.86);display:flex;align-items:center;justify-content:center;gap:34px;opacity:0;transition:opacity .35s}
      #cmpov.on{opacity:1}
      #cmpov figure{margin:0;background:#fff;border-radius:14px;padding:12px;box-shadow:0 18px 60px rgba(0,0,0,.5);transform:translateY(40px) scale(.94);transition:transform .45s cubic-bezier(.2,1.2,.4,1)}
      #cmpov.on figure{transform:none}
      #cmpov img{width:820px;display:block;border-radius:6px}
      #cmpov figcaption{font:700 30px 'Noto Sans CJK SC',sans-serif;color:#13305e;text-align:center;padding:10px 0 2px}
      #cmpov figcaption b{color:#E07B00}`;document.head.appendChild(st)}""", [u('/home/claude/video/t7/hi_src.png'), u('/home/claude/video/t7/hi_ppt.png')])


def open_file(r, path, label, fast=False):
    hover(r, '#b-open', 0.02 if fast else 0.15)
    r.page.evaluate("""([ring,t])=>{const g=window.__ring;g.style.left=ring[0]+'px';g.style.top=ring[1]+'px';g.animate([{opacity:.9,transform:'scale(.4)'},{opacity:0,transform:'scale(1.5)'}],{duration:500});
      const k=window.__keys;k.textContent=t;k.style.opacity=1;clearTimeout(window.__kh);window.__kh=setTimeout(()=>k.style.opacity=0,1300)}""", [[r.mx, r.my], label])
    r.page.mouse.click(r.mx, r.my)
    r.page.set_input_files('#f-open', path)


def a_p10(r):
    pg = r.page; t0 = time.time(); D = 4.6
    el = lambda: time.time() - t0
    plan = [(FX, 'PowerPoint　.pptx', 0.0), (VS, 'Visio　.vsdx', 1.5), (DIO, 'draw.io　.drawio', 3.0)]
    for p, lab, at in plan:
        late = el() > at + 0.1
        while el() < at: r.wait(0.03)
        open_file(r, p, lab, fast=late)
        print('  after open', lab, round(el(), 2), flush=True)
    r.wait(0.15)
    if D - el() > 0.9:
        try:
            a, b = pg.evaluate("""()=>{const s=document.getElementById('svg').getBoundingClientRect();
              const n=P().nodes.find(n=>n.type!=='tblock'&&n.w<260&&n.w>60)||P().nodes[0];
              const x=(n.x+n.w/2-view.x)*view.k+s.left,y=(n.y+n.h/2-view.y)*view.k+s.top;return [[x,y],[x+120,y+70]]}""")
            r.move(a[0], a[1], 0.12)
            pg.mouse.down(); r.move(b[0], b[1], 0.22); pg.mouse.up()
        except Exception as e:
            print('drag fail', e)
    shot(r, 'a5')
    print('p10 used', time.time() - t0)


V = '/home/claude/vfx/cn/'


def a_p13(r):
    """Visio 批量转 PPT（保持原排版），再并排对比原图与转出的 PPT"""
    pg = r.page; t0 = time.time()
    r.press('Control+Shift+O', 'Ctrl + Shift + O　格式转换')
    r.wait(0.25)
    pg.set_input_files('#cv-f', [V + 'cn_arch.vsdx', V + 'flow.vsdx', V + 'flow_frame.vsdx']); r.wait(0.3)
    r.click('#cv-tg input[value=pptx]', dur=0.3, after=0.08)
    r.click('#cv .cv-opt input[value=keep]', dur=0.25, after=0.08)
    r.click('#cv-go', dur=0.3, after=0.1)
    try: pg.wait_for_function("document.querySelector('#cv-msg').textContent.includes('已完成')", timeout=15000)
    except Exception as e: print('conv wait', e)
    r.wait(0.5)
    shot(r, 'p13a')
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='cmpov';
      d.innerHTML=`<figure><img src="${window.__cmp[0]}"><figcaption>Visio 原图</figcaption></figure><figure><img src="${window.__cmp[1]}"><figcaption>转出的 PPT　<b>字号一致</b></figcaption></figure>`;
      document.body.appendChild(d);requestAnimationFrame(()=>requestAnimationFrame(()=>d.classList.add('on')))}""")
    r.wait(max(1.8, 6.1 - (time.time() - t0)))
    shot(r, 'p13b')
    print('p13 used', time.time() - t0)


ACTIONS = {'p12': a_p10, 'p13': a_p13}
