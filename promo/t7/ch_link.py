"""智能连线 (p07 避障, p08 吸附)"""
import time
IDS = ['p07', 'p08']
SH = '/tmp/claude-0/t7link_'

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

def wc(r, text):
    return r.page.evaluate("(t)=>{const n=P().nodes.find(n=>(n.text||'').split('\\n')[0]===t);return [n.x+n.w/2,n.y+n.h/2]}", text)

def refit(r, dur=0.8):
    r.page.evaluate("()=>{const v={...view};fit();window.__fv={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView()}")
    f = r.page.evaluate("()=>window.__fv"); s = r.page.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [s.width,s.height]}")
    zoomto(r, f['x'] + s[0] / 2 / f['k'], f['y'] + s[1] / 2 / f['k'], f['k'], dur)

def fdrag(r, a, b, dur=0.3):
    pg = r.page
    r.move(a[0], a[1], 0.15); pg.mouse.down(); r.wait(0.04)
    t0 = time.time()
    while True:
        t = min(1.0, (time.time() - t0) / dur); e = t * t * (3 - 2 * t)
        pg.mouse.move(a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e)
        if t >= 1: break
    r.mx, r.my = b; pg.mouse.up(); r.wait(0.08)

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

def setup(r):
    install(r)
    r.page.evaluate("()=>{fit();sel.clear();selLink=null;render()}")
    r.page.mouse.move(960, 600); r.mx, r.my = 960, 600


def a07(r):
    """连线避障：同一行隔着中间框的两个框之间依次连两条线，自动从上下两侧绕开"""
    pg = r.page
    info = pg.evaluate("""()=>{const L=P().nodes.filter(n=>!isCont(n)&&!['text','note','legend','tblock'].includes(n.type));
      const rows={};for(const n of L){const k=Math.round((n.y+n.h/2)/10);(rows[k]=rows[k]||[]).push(n)}
      let pick=null,bs=-1;for(const r of Object.values(rows)){if(r.length<3)continue;if(r.some(n=>n.parent&&P().nodes.find(q=>q.id===n.parent)?.type==='group'))continue;r.sort((a,b)=>a.x-b.x);const g=Math.min(r[1].x-(r[0].x+r[0].w),r[2].x-(r[1].x+r[1].w));if(g>bs){bs=g;pick=r}}
      if(!pick)return null;const a=pick[0],c=pick[2];window.__av=[a.id,c.id];return {cx:(a.x+c.x+c.w)/2,cy:a.y+a.h/2}}""")
    print('avoid', info)
    zoomto(r, info['cx'], info['cy'], 1.2, 0.8)
    r.keys('连线避障　自动绕开中间的框', 2.4)
    pg.evaluate("()=>{const [a,c]=window.__av;P().links.push({id:uid(),from:a,to:c,dir:'one',kind:'data',route:'ortho',label:'跨框直达'});render()}")
    r.wait(1.3)
    pg.evaluate("()=>{const [a,c]=window.__av;P().links.push({id:uid(),from:c,to:a,dir:'one',kind:'ctrl',route:'ortho',label:'回传'});render()}")
    r.wait(1.4)
    pg.screenshot(path=SH + 'p07.png')

def a08(r):
    """拖动吸附：拖偏一个框再拖回，参考线出现、吸住"""
    pg = r.page
    pg.keyboard.press('Escape'); pg.evaluate('()=>{sel.clear();selLink=null;render()}')
    info = pg.evaluate("""()=>{const L=P().nodes.filter(n=>!isCont(n)&&!['text','note','legend','tblock'].includes(n.type)&&n.w<260);
      let best=null;for(const a of L)for(const b of L){if(a===b)continue;const dy=Math.abs((a.y+a.h/2)-(b.y+b.h/2)),dx=b.x-(a.x+a.w);if(dy<2&&dx>40&&dx<260&&(!best||dx<best.dx))best={a:a.text.split('\\n')[0],b:b.text.split('\\n')[0],dx,cx:(a.x+b.x+b.w)/2,cy:a.y+a.h/2}}return best}""")
    print('snap pair', info)
    zoomto(r, info['cx'], info['cy'], 1.6, 0.5)
    r.keys('拖动吸附　对齐边／中线／等间距', 2.6)
    x, y = r.node_xy(info['b'])
    k = pg.evaluate('()=>view.k')
    r.move(x, y, 0.25); pg.mouse.down(); r.wait(0.05)
    path = [(x + 6 * k, y + 46 * k), (x + 12 * k, y + 18 * k), (x + 8 * k, y + 4 * k)]
    for (px, py) in path:
        x0, y0 = r.mx, r.my; t0 = time.time(); dur = 0.55
        while True:
            t = min(1.0, (time.time() - t0) / dur); e = t * t * (3 - 2 * t)
            pg.mouse.move(x0 + (px - x0) * e, y0 + (py - y0) * e)
            if t >= 1: break
        r.mx, r.my = px, py
    r.wait(1.2)
    pg.screenshot(path=SH + 'p08.png')
    pg.mouse.up(); r.wait(0.2)
    refit(r, 0.6)

ACTIONS = {'p07': a07, 'p08': a08}
