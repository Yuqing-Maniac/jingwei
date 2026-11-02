"""图标库 + 编队与复合图标 (013–021)"""
import sys, time
sys.path.insert(0, '/home/claude/video/t2')
import ch_palette as P0
from ch_palette import pscroll, goto_sec, toggle, hv, item_xy_exact, scroll_item, silent_close, hbox
IDS = [f'{i:03d}' for i in range(13, 22)]
MS = P0.MS

def zoomto(r, wx, wy, k, dur=0.8):
    r.page.evaluate("""([wx,wy,k,dur])=>new Promise(res=>{
      const s=document.getElementById('svg').getBoundingClientRect();
      const x0=view.x,y0=view.y,k0=view.k,k1=k;
      const t0=performance.now();
      (function f(){const t=Math.min(1,(performance.now()-t0)/(dur*1000)),e=t*t*(3-2*t);
        view.k=k0+(k1-k0)*e;
        const cx0=x0+s.width/2/k0,cy0=y0+s.height/2/k0,cx=cx0+(wx-cx0)*e,cy=cy0+(wy-cy0)*e;
        view.x=cx-s.width/2/view.k;view.y=cy-s.height/2/view.k;applyView();
        if(t<1)requestAnimationFrame(f);else res();})()})""", [wx, wy, k, dur])

def refit(r, dur=0.8):
    r.page.evaluate("()=>{const v={...view};fit();window.__fv={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView()}")
    f = r.page.evaluate("()=>window.__fv"); s = r.page.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [s.width,s.height]}")
    zoomto(r, f['x'] + s[0] / 2 / f['k'], f['y'] + s[1] / 2 / f['k'], f['k'], dur)

def wc(r, text):
    return r.page.evaluate("(t)=>{const n=P().nodes.find(n=>(n.text||'').split('\\n')[0]===t);return [n.x+n.w/2,n.y+n.h/2]}", text)

import os
def sh(r,n):
    if os.environ.get('SHOTS'): r.page.screenshot(path=f'/tmp/ic_{n}.png')

def setup(r):
    pg = r.page
    pg.evaluate("()=>{openSecs.clear();openSecs.add('基础形状');sel.clear();selLink=null;renderPalette();render();fit()}")
    pg.evaluate("()=>{document.getElementById('palette').scrollTop=0}")
    pg.mouse.move(1000, 700); r.mx, r.my = 1000, 700
    P0.install(r)

def a013(r):
    pg = r.page
    r.move(120, 420, 0.3)
    # open many sections quickly while scrolling
    pg.evaluate("()=>{openSecs.clear();renderPalette()}")
    for k, s in enumerate(['基础形状', '无人', '反无人', '空中', '海上', '陆地']):
        pg.evaluate("(s)=>{openSecs.add(s);renderPalette()}", s)
        goto_sec(r, s, 0.35, 30); r.wait(0.45)
    sh(r,'013');pscroll(r, 0, 0.9)
    pg.evaluate("()=>{openSecs.clear();openSecs.add('基础形状');openSecs.add('无人');renderPalette()}")

def a014(r):
    goto_sec(r, '无人', 0.3, 40)
    hv(r, '无人艇', 0.25, 0.05)
    toggle(r, '无人', 0.25, 0.05); toggle(r, '反无人', 0.25, 0.05)
    goto_sec(r, '反无人', 0.15, 40)
    toggle(r, '反无人', 0.25, 0.05)
    toggle(r, '人员', 0.25, 0.05)
    goto_sec(r, '人员', 0.15, 40); hv(r, '海军参谋', 0.25, 0.05); sh(r,'014')

def a015(r):
    pg = r.page
    silent_close(r, '人员'); pscroll(r, 0, 0.2)
    r.click('#pal-q', dur=0.35, after=0.1)
    for q in ['机巢', '系留', '激光', '微波']:
        pg.fill('#pal-q', ''); pg.dispatch_event('#pal-q', 'input')
        r.type(q, cps=7); r.wait(0.55)
        pg.evaluate("()=>{document.getElementById('palette').scrollTop=0}")
        pg.mouse.move(r.mx, r.my)
    r.wait(0.2); sh(r,'015')

def a016(r):
    pg = r.page
    pg.fill('#pal-q', ''); pg.dispatch_event('#pal-q', 'input'); r.wait(0.1)
    goto_sec(r, MS, 0.2, 40)
    if not P0.is_open(r, MS): toggle(r, MS, 0.35, 0.15)
    goto_sec(r, MS, 0.2, 40)
    r.click('#d-ms [data-v="cn"]', dur=0.3, after=0.6)
    sh(r,'016')
    r.click('#d-ms [data-v="nato"]', dur=0.35, after=0.2)

def a017(r):
    pg = r.page
    silent_close(r, MS); pscroll(r, 0, 0.1)
    r.click('#pal-q', dur=0.3, after=0.05); r.type('拦截无人机', cps=14); r.wait(0.2)
    src = item_xy_exact(r, '拦截无人机')
    dst = pg.evaluate("""()=>{const r=document.getElementById('svg').getBoundingClientRect();
      return [(750-view.x)*view.k+r.left,(458-view.y)*view.k+r.top]}""")
    r.drag(src, tuple(dst), 0.7); r.wait(0.2)
    sh(r,'017')
    pg.fill('#pal-q', ''); pg.dispatch_event('#pal-q', 'input')

def a018(r):
    r.page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
    r.move(1000, 600, 0.3)
    r.keys('Ctrl + Shift + B　编队生成器'); r.page.keyboard.press('Control+Shift+B'); r.wait(1.2); sh(r,'018')

def a019(r):
    pg = r.page
    r.click('#cb-q', dur=0.3, after=0.05); r.type('察', cps=16); pg.fill('#cb-q','察打'); pg.dispatch_event('#cb-q','input')
    r.click('#cb-icons [data-k]', dur=0.3, after=0.1)
    for p in ['wedge', 'diamond', 'circle', 'swarm']:
        r.click(f'#cb-pats [data-p="{p}"]', dur=0.2, after=0.15)
    sh(r,'019a')
    r.click('#cb-ok', dur=0.25, after=0.2)

def a020(r):
    pg = r.page
    pg.evaluate("()=>{P().nodes=P().nodes.filter(n=>!/编队/.test(n.text||''));sel.clear();render()}")
    cx, cy = wc(r, '光电监控塔'); ox, oy = wc(r, '无人值守传感器')
    zoomto(r, (cx + ox) / 2 + 50, cy - 30, 1.5, 0.6)
    r.click(xy=r.node_xy('无人值守传感器'), dur=0.35, after=0.1)
    pg.keyboard.down('Shift'); r.click(xy=r.node_xy('光电监控塔'), dur=0.35, after=0.1); pg.keyboard.up('Shift')
    r.keys('Ctrl + G　组合为复合图标'); pg.keyboard.press('Control+g'); r.wait(1.0); sh(r,'020')

def a021(r):
    pg = r.page
    r.click('#b-export', dur=0.4, after=0.2)
    items = pg.evaluate("()=>[...document.querySelectorAll('#m-export button')].filter(e=>/PowerPoint|Visio/.test(e.textContent)).map(e=>{const b=e.getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2]})")
    print('ITEMS', items)
    for it in items: r.move(it[0], it[1], 0.35); r.wait(0.5); sh(r,'021')

ACTIONS = {f'{i:03d}': globals()[f'a{i:03d}'] for i in range(13, 22)}
