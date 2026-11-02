"""连线与美化 (022–027)"""
import time
IDS = ['022', '023', '023b', '024', '025', '025b', '026', '027']
SH = '/tmp/claude-0/t6lay_'

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

def a022(r):
    pg = r.page
    ax, ay = wc(r, '光电监控塔'); bx, by = wc(r, '巡逻无人车')
    zoomto(r, (ax + bx) / 2 + 40, (ay + by) / 2, 1.7, 0.5)
    n = r.node_xy('光电监控塔'); a = r.node_xy('光电监控塔', 'r'); b = r.node_xy('巡逻无人车')
    r.move(*n, 0.3)
    HIT = "([x,y])=>{const e=document.elementFromPoint(x,y);return !!(e&&e.dataset&&e.dataset.port)}"
    for k in range(5):
        pg.mouse.move(*a); r.mx, r.my = a; r.wait(0.2)
        if pg.evaluate(HIT, list(a)): break
        pg.mouse.move(*n); r.mx, r.my = n; r.wait(0.2)
    r.wait(0.35)
    pg.mouse.down(); r.wait(0.05)
    t0 = time.time(); dur = 0.7
    while True:
        t = min(1.0, (time.time() - t0) / dur); e = t * t * (3 - 2 * t)
        pg.mouse.move(a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e)
        if t >= 1: break
    r.mx, r.my = b; r.wait(0.1); pg.mouse.up(); r.wait(0.3)
    print('selLink', pg.evaluate("()=>!!selLink"))

def a023(r):
    pg = r.page
    for k, lb in [('2', '2　数据流'), ('3', '3　指令流'), ('4', '4　有线／光纤'), ('5', '5　无线数据链')]:
        r.press(k, lb); r.wait(0.17)
    r.press('d', 'D　单向 → 双向'); r.wait(0.35)
    r.press('d', 'D　双向 → 无箭头'); r.wait(0.3)

def a024(r):
    pg = r.page
    pg.keyboard.press('Escape'); pg.evaluate('()=>{sel.clear();selLink=null;render()}')
    refit(r, 0.4)
    pg.evaluate("""()=>{const g=t=>P().nodes.find(n=>(n.text||'').split('\\n')[0]===t);
      const a=g('无人值守传感器'),b=g('高速无人拦截艇'),c=g('巡逻无人车');a.x+=160;a.y-=70;b.x-=200;b.y+=90;c.x+=80;c.y-=90;render()}""")
    for name, dx, dy in [('四旋翼巡查无人机', 90, 70), ('垂起固定翼无人机', -110, 60)]:
        x, y = r.node_xy(name); fdrag(r, (x, y), (x + dx, y + dy), 0.22)
    pg.mouse.click(1590, 1000); r.wait(0.1)
    r.keys('Ctrl + Shift + F　一键美化'); pg.keyboard.press('Control+Shift+F'); r.wait(0.8)

def a025(r):
    pg = r.page
    info = pg.evaluate("""()=>{const c={};for(const l of P().links){c[l.from]=(c[l.from]||0)+1;c[l.to]=(c[l.to]||0)+1}
      let best=null;for(const n of P().nodes){const k=c[n.id]||0;if(!best||k>best.k)best={k,t:n.text.split('\\n')[0],x:n.x+n.w/2,y:n.y+n.h/2}}return best}""")
    print('busiest', info)
    zoomto(r, info['x'], info['y'], 1.8, 0.8)
    r.move(*r.node_xy(info['t']), 0.4); r.wait(0.6)
    r.move(1400, 700, 0.5); r.wait(1.2)
    refit(r, 0.8)

def a026(r):
    pg = r.page
    pg.evaluate("""()=>{const g=t=>P().nodes.find(n=>(n.text||'').split('\\n')[0]===t);
      [['无人值守传感器','巡逻无人艇'],['高空长航时无人机','高速无人拦截艇'],['四足巡逻机器人','卫通站'],['垂起固定翼无人机','光电监控塔'],['无人机机巢','巡逻无人艇']].forEach(([x,y])=>{if(g(x)&&g(y))P().links.push({id:uid(),from:g(x).id,to:g(y).id,dir:'one',kind:'ctrl',route:'ortho',label:''})});render()}""")
    r.wait(0.7)
    r.keys('Ctrl + Shift + X　自动重排　减少交叉', 1.6); pg.keyboard.press('Control+Shift+X'); r.wait(0.4)
    allj = pg.evaluate("()=>{const o=[];for(const l of P().links){const r=routesFor(P()).get(l.id);for(const j of r.jumps)if(Math.abs(r.pts[j.seg].y-r.pts[j.seg+1].y)<1)o.push([j.list[0].c,r.pts[j.seg].y])}return o}")
    print('JUMPS', allj)
    if allj:
        zoomto(r, allj[0][0], allj[0][1], 3.0, 0.9); r.wait(0.3)
    r.wait(0.5)

def a027(r):
    pg = r.page
    refit(r, 0.3)
    x, y = r.node_xy('无人机机巢', 'tr')
    r.move(x - 40, y + 25, 0.2); r.click(xy=(x, y), dur=0.2, after=0.1)
    print('SUB?', pg.evaluate("()=>document.querySelectorAll('[data-crumb]').length"))
    pg.keyboard.press('Control+0'); r.wait(0.6)
    r.click('[data-crumb="0"]', dur=0.3, after=0.1)
    pg.keyboard.press('Control+0'); r.wait(0.3)


def a023b(r):
    """拖动吸附：把一个框慢慢拖向另一个框的中线对齐位置，粉色参考线出现时停住"""
    pg = r.page
    pg.keyboard.press('Escape'); pg.evaluate('()=>{sel.clear();selLink=null;render()}')
    # 选一对同层的相邻框：拖动右边一个，让它与左边框中线对齐（先拖偏，再拖回吸附）
    info = pg.evaluate("""()=>{const L=P().nodes.filter(n=>!isCont(n)&&n.type!=='text'&&n.type!=='note'&&n.type!=='legend'&&n.type!=='tblock'&&n.w<260);
      let best=null;for(const a of L)for(const b of L){if(a===b)continue;const dy=Math.abs((a.y+a.h/2)-(b.y+b.h/2)),dx=b.x-(a.x+a.w);if(dy<2&&dx>40&&dx<260&&(!best||dx<best.dx))best={a:a.text.split('\\n')[0],b:b.text.split('\\n')[0],dx,cx:(a.x+b.x+b.w)/2,cy:a.y+a.h/2}}return best}""")
    print('snap pair', info)
    zoomto(r, info['cx'], info['cy'], 1.6, 0.45)
    r.keys('拖动吸附　对齐边／中线／等间距', 1.6)
    x, y = r.node_xy(info['b'])
    k = pg.evaluate('()=>view.k')
    r.move(x, y, 0.25); pg.mouse.down(); r.wait(0.05)
    # 先往下拖偏 40 世界单位，再慢慢拖回，经过对齐位置时吸住
    path = [(x + 6 * k, y + 40 * k), (x + 10 * k, y + 16 * k), (x + 8 * k, y + 4 * k)]
    for (px, py) in path:
        x0, y0 = r.mx, r.my; t0 = time.time(); dur = 0.45
        while True:
            t = min(1.0, (time.time() - t0) / dur); e = t * t * (3 - 2 * t)
            pg.mouse.move(x0 + (px - x0) * e, y0 + (py - y0) * e)
            if t >= 1: break
        r.mx, r.my = px, py
    r.wait(0.9)
    print('guides', pg.evaluate('()=>JSON.stringify(ui.guides)'))
    pg.screenshot(path=SH + '023b.png')
    pg.mouse.up(); r.wait(0.2)

def a025b(r):
    """连线避障：同一层隔着中间框的两个框之间连两条线，自动从上下两侧绕开"""
    pg = r.page
    pg.keyboard.press('Escape'); pg.evaluate('()=>{sel.clear();selLink=null;render()}')
    info = pg.evaluate("""()=>{const L=P().nodes.filter(n=>!isCont(n)&&n.type!=='text'&&n.type!=='note'&&n.type!=='legend'&&n.type!=='tblock');
      const rows={};for(const n of L){const k=Math.round((n.y+n.h/2)/10);(rows[k]=rows[k]||[]).push(n)}
      let pick=null,bs=-1;for(const r of Object.values(rows)){if(r.length<3)continue;if(r.some(n=>n.parent&&P().nodes.find(q=>q.id===n.parent)?.type==='group'))continue;r.sort((a,b)=>a.x-b.x);const g=Math.min(r[1].x-(r[0].x+r[0].w),r[2].x-(r[1].x+r[1].w));if(g>bs){bs=g;pick=r}}
      if(!pick)return null;const a=pick[0],c=pick[2];
      P().links.push({id:uid(),from:a.id,to:c.id,dir:'one',kind:'data',route:'ortho',label:'跨框直达'});
      P().links.push({id:uid(),from:c.id,to:a.id,dir:'one',kind:'ctrl',route:'ortho',label:'回传'});
      render();return {cx:(a.x+c.x+c.w)/2,cy:a.y+a.h/2}}""")
    print('avoid', info)
    if info: zoomto(r, info['cx'], info['cy'], 1.15, 0.8)
    r.keys('连线避障　自动绕开中间的框', 1.8)
    r.wait(1.6)
    pg.screenshot(path=SH + '025b.png')
    refit(r, 0.6)

ACTIONS = {i: globals()['a' + i] for i in IDS}
