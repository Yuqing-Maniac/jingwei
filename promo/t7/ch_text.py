"""文字成图 + 一键美化 (p05–p06)"""
import time, os
IDS = ['p05', 'p06']
SH = os.environ.get('SHOT')

MD1 = "# 海上无人巡逻体系\n## 指控段\n### 指挥层\n- 岸基指挥所、卫通站\n"
MD2 = ("## 平台段\n### 空中层\n- 察打一体无人机、中继无人机 [新增]\n### 水面层\n- 巡逻无人艇、无人机机巢\n"
       "- 岸基指挥所 -> 察打一体无人机 : 任务指令\n- 中继无人机 <-> 卫通站 : 数据回传\n- 无人机机巢 -> 巡逻无人艇 : 协同")


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


def refit(r, dur=0.6):
    r.page.evaluate("()=>{const v={...view};fit();window.__fv={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView()}")
    f = r.page.evaluate("()=>window.__fv"); s = r.page.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [s.width,s.height]}")
    zoomto(r, f['x'] + s[0] / 2 / f['k'], f['y'] + s[1] / 2 / f['k'], f['k'], dur)


def ttype(r, text, secs):
    """time-budgeted fast typing: chunk size adapts to the real cost of each insert call"""
    import math
    t_end = r.now() + secs; n = len(text); i = 0; cost = 0.04
    while i < n:
        left = n - i; rem = t_end - r.now()
        calls = max(1.0, rem / max(cost, 0.03))
        k = max(1, math.ceil(left / calls))
        t1 = r.now()
        r.page.keyboard.insert_text(text[i:i + k]); i += k
        dt = r.now() - t1; cost = 0.6 * cost + 0.4 * dt
        slack = (t_end - r.now()) / max(1, math.ceil((n - i) / k)) - cost
        if slack > 0.005 and i < n: r.page.wait_for_timeout(int(slack * 1000))


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


def shot(r, n):
    if SH: r.page.screenshot(path=f'{SH}_{n}.png')


def setup(r):
    install(r)
    r.page.evaluate("()=>{fit(); window.SpeechRecognition=undefined; window.webkitSpeechRecognition=undefined;}")
    # open once off-camera so first-use tips are dismissed, then close
    r.page.keyboard.press('Control+Shift+G'); r.page.wait_for_timeout(400)
    r.page.evaluate("()=>{const b=document.getElementById('tg-tipx'); if(b&&b.offsetParent) b.click(); const t=document.getElementById('tg-in'); t.value=''; t.dispatchEvent(new Event('input',{bubbles:true}))}")
    r.page.keyboard.press('Escape'); r.page.wait_for_timeout(300)
    r.page.mouse.move(960, 600); r.mx, r.my = 960, 600


def a05(r):
    pg = r.page; T0 = r.now()
    r.press('Control+Shift+G', 'Ctrl + Shift + G　文字成图')
    pg.focus('#tg-in')
    pg.keyboard.press('Control+a'); pg.keyboard.press('Delete')
    ttype(r, MD1, max(0.2, T0 + 1.2 - r.now()))
    ttype(r, MD2, max(0.3, T0 + 2.45 - r.now()))
    r.move(*r.box('#tg-prev'), 0.25); r.wait(0.1)
    shot(r, 'p05a')
    r.click('#tg-go', dur=0.25, after=0.02)
    r.wait(max(0.1, T0 + 4.1 - r.now())); shot(r, 'p05b')


def a06(r):
    pg = r.page; T0 = r.now(); END = T0 + 6.1
    # scramble a little (off-grid) so the beautify snap is visible
    pg.evaluate("""()=>{const ns=P().nodes.filter(n=>!n.band&&!n.lane&&n.w<400);let i=0;
      for(const n of ns){const d=[[72,-30],[-78,38],[55,40],[-62,-36],[85,28],[-45,-44]][i++%6];n.x+=d[0];n.y+=d[1]}
      render()}""")
    r.wait(0.75); shot(r, 'p06a')
    r.keys('Ctrl + Shift + F　一键美化', 1.5); pg.keyboard.press('Control+Shift+F'); r.wait(0.45)
    shot(r, 'p06b')
    c = pg.evaluate("()=>{const ns=P().nodes;let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const n of ns){x0=Math.min(x0,n.x);y0=Math.min(y0,n.y);x1=Math.max(x1,n.x+n.w);y1=Math.max(y1,n.y+n.h)}return [(x0+x1)/2,(y0+y1)/2,view.k]}")
    if END - r.now() > 2.4:
        zoomto(r, c[0], c[1] - 60, c[2] * 1.25, 0.55)
        r.wait(0.15)
    if END - r.now() > 1.2:
        r.keys('Ctrl + Shift + X　减少交叉', 1.0); pg.keyboard.press('Control+Shift+X')
        r.wait(max(0.3, min(0.7, END - r.now() - 0.8)))
    shot(r, 'p06c')
    refit(r, max(0.25, min(0.8, END - r.now() - 0.05)))
    shot(r, 'p06d')


ACTIONS = {'p05': a05, 'p06': a06}
