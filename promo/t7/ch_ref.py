"""参照生成 (p07–p09) — headline feature"""
import time, os
IDS = ['p09', 'p10', 'p11']
SH = os.environ.get('SHOT')

NAME = '海岛无人值守监视系统'
CONTENT = ("感知：对海雷达、光电转塔、AIS 接收机、水声监听浮标、巡逻无人艇；\n"
           "传输：微波接力为主、卫通备份，岛岸光纤环网；\n"
           "处理：边缘计算节点、目标融合与智能分析、海洋态势云平台；\n"
           "应用：岸基监视指挥中心、岛上值守站、无人机机巢自主巡查。")


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


def fitview(r):
    r.page.evaluate("()=>{const v={...view};fit();window.__fv={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView()}")
    f = r.page.evaluate("()=>window.__fv"); s = r.page.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [s.width,s.height]}")
    return f['x'] + s[0] / 2 / f['k'], f['y'] + s[1] / 2 / f['k'], f['k']


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
    r.page.evaluate("()=>{const a=document.activeElement;if(a)a.dispatchEvent(new Event('input',{bubbles:true}))}")


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


def until(r, t, minw=0.0):
    r.wait(max(minw, t - r.now()))


def shot(r, n):
    if SH: r.page.screenshot(path=f'{SH}_{n}.png')


# CSS "camera" on the dialog: scale .rg-box around a point (client coords)
def dzoom(r, sel, k, dur=0.6, cy=540):
    """CSS camera on the dialog: bring element `sel` to screen centre at scale k (sel=None resets)."""
    r.page.evaluate("""([sel,k,dur,cy])=>{const b=document.querySelector('#rg .rg-box');
      b.style.transformOrigin='0 0';
      b.style.transition='transform '+dur+'s cubic-bezier(.45,0,.25,1)';
      if(!sel){b.style.transform='none';return}
      const prev=b.style.transform;b.style.transition='none';b.style.transform='none';
      const bb=b.getBoundingClientRect(),e=document.querySelector(sel).getBoundingClientRect();
      b.style.transform=prev;b.offsetWidth;b.style.transition='transform '+dur+'s cubic-bezier(.45,0,.25,1)';
      const cx=e.left+e.width/2,cyy=e.top+e.height/2;
      const tx=960-bb.left-k*(cx-bb.left),ty=cy-bb.top-k*(cyy-bb.top);
      b.style.transform='translate('+tx+'px,'+ty+'px) scale('+k+')';}""", [sel, k, dur, cy])


POP_JS = """([cards, dur])=>{
  let o=document.getElementById('pz'); if(o) o.remove();
  o=document.createElement('div'); o.id='pz';
  o.style.cssText='position:fixed;inset:0;z-index:2147483000;pointer-events:none;background:rgba(10,15,22,0);transition:background '+dur+'s';
  document.body.appendChild(o);
  const W=1920,H=1080,gap=40,n=cards.length;
  const cw=n===1?(cards[0].w||820):Math.min(860,(W-160-gap*(n-1))/n), ch=n===1?(cards[0].h||860):860;
  let x=(W-(cw*n+gap*(n-1)))/2;
  for(const c of cards){
    const src=document.querySelector(c.src).getBoundingClientRect();
    const d=document.createElement('div');
    d.style.cssText=`position:absolute;left:${x}px;top:${(H-ch)/2+55}px;width:${cw}px;height:${ch}px;background:#fff;border-radius:16px;box-shadow:0 0 0 3px #2F80ED,0 24px 60px rgba(0,0,0,.35);display:flex;flex-direction:column;overflow:hidden;will-change:transform,opacity;transform-origin:0 0`;
    const h=document.createElement('div');
    h.style.cssText='font:600 26px "Noto Sans CJK SC",sans-serif;color:#fff;background:'+(c.color||'#2F80ED')+';padding:12px 22px;letter-spacing:.04em;flex:none';
    h.textContent=c.title; d.appendChild(h);
    const b=document.createElement('div'); b.style.cssText='flex:1;min-height:0;padding:14px 18px;display:flex;align-items:center;justify-content:center';
    const node=document.querySelector(c.src+(c.inner||'')).cloneNode(true);
    if(node.tagName.toLowerCase()==='svg'){node.removeAttribute('width');node.removeAttribute('height');node.style.cssText='width:100%;height:100%;display:block';}
    else{node.style.cssText='font:500 25px/1.75 "Noto Sans CJK SC",sans-serif;color:#1f2a37;white-space:pre-wrap;margin:0;align-self:flex-start';}
    b.appendChild(node); d.appendChild(b); o.appendChild(d);
    const sx=src.width/cw, sy=src.height/ch;
    d.style.transform=`translate(${src.left-x}px,${src.top-((H-ch)/2+55)}px) scale(${sx},${sy})`; d.style.opacity='0.2';
    d.offsetWidth;
    d.style.transition=`transform ${dur}s cubic-bezier(.3,0,.2,1), opacity ${dur*0.6}s`;
    d.style.transform='none'; d.style.opacity='1';
    d.dataset.back=`translate(${src.left-x}px,${src.top-((H-ch)/2+55)}px) scale(${sx},${sy})`;
    x+=cw+gap;
  }
  o.offsetWidth; o.style.background='rgba(10,15,22,.35)';
}"""

UNPOP_JS = """(dur)=>{const o=document.getElementById('pz'); if(!o) return;
  o.style.background='rgba(10,15,22,0)';
  for(const d of o.children){d.style.transition=`transform ${dur}s cubic-bezier(.5,0,.7,1), opacity ${dur}s`;d.style.transform=d.dataset.back;d.style.opacity='0';}
  setTimeout(()=>o.remove(), dur*1000+50);}"""


def pop(r, cards, dur=0.5):
    r.page.evaluate(POP_JS, [cards, dur])


def unpop(r, dur=0.35):
    r.page.evaluate(UNPOP_JS, dur)


def glow(r, sel, on=True):
    r.page.evaluate("""([sel,on])=>{const e=document.querySelector(sel);e.style.transition='box-shadow .3s';
      e.style.boxShadow=on?'0 0 0 3px #2F80ED, 0 0 22px rgba(47,128,237,.55)':'';}""", [sel, on])


def setup(r):
    install(r)
    pg = r.page
    pg.evaluate("()=>localStorage.setItem('hongtu.textgen.v1', JSON.stringify({base:'http://127.0.0.1:8766/v1',model:'deepseek-v4-flash'}))")
    pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("""()=>{doc.meta=Object.assign(doc.meta||{},{project:'边海防无人化巡逻体系',drawingNo:'HT-ZT-01',version:'V2.5',date:'2026-10-15',org:'[单位名称]'});
      Std.placeTblock(P());render();fit();RefGen.open();RefGen.close();}""")
    pg.mouse.move(1100, 620); r.mx, r.my = 1100, 620
    pg.wait_for_timeout(300)


def a07(r):
    pg = r.page; T0 = r.now()
    r.keys('Ctrl + Shift + L　参照生成', 1.4)
    r.click('#b-ref', dur=0.35, after=0.05)
    pg.wait_for_selector('#rg.open #rg-refprev svg', timeout=5000)
    r.wait(0.25)
    r.B = pg.evaluate("""(ks)=>Object.fromEntries(ks.map(k=>{const b=document.querySelector(k).getBoundingClientRect();return [k,[b.left+b.width/2,b.top+b.height/2]]}))""",
                      ['#rg-name', '#rg-content', '#rg-gen', '#rg-apply', '#rg-outprev', '#rg-refprev'])
    shot(r, 'p07a')
    glow(r, '#rg-refprev')
    r.move(*r.B['#rg-refprev'], 0.3)
    pop(r, [{'src': '#rg-refprev', 'inner': ' svg', 'title': '① 参照图　边海防无人化巡逻体系', 'w': 860, 'h': 860}], 0.5)
    until(r, T0 + 2.5, 0.6); shot(r, 'p07b')
    # morph to the extracted skeleton (skipped if running late)
    if r.now() < T0 + 3.1:
        pop(r, [{'src': '#rg-refprev', 'inner': ' svg', 'title': '① 参照图', 'w': 700, 'h': 860},
                {'src': '#rg-sum', 'title': '自动提取骨架', 'color': '#1F6F5C'}], 0.45)
    until(r, T0 + 3.95, 0.3); shot(r, 'p07c')


def a08(r):
    pg = r.page; T0 = r.now()
    glow(r, '#rg-refprev', False)
    unpop(r, 0.3)
    r.click(xy=r.B['#rg-name'], dur=0.35, after=0.02)
    ttype(r, NAME, max(0.15, T0 + 0.95 - r.now()))
    r.click(xy=r.B['#rg-content'], dur=0.25, after=0.02)
    lines = CONTENT.split('\n')
    ttype(r, '\n'.join(lines[:2]) + '\n', max(0.3, T0 + 2.4 - r.now()))
    pg.keyboard.insert_text('\n'.join(lines[2:])); r.wait(0.08)
    pg.evaluate("()=>document.activeElement.dispatchEvent(new Event('input',{bubbles:true}))")
    print('typed', round(r.now(), 2)); shot(r, 'p08a')
    r.click(xy=r.B['#rg-gen'], dur=0.3, after=0.02)
    print('gen clicked', round(r.now(), 2)); shot(r, 'p08b')
    r.move(*r.B['#rg-outprev'], 0.4)
    pg.wait_for_selector('#rg-outprev svg', timeout=8000)
    glow(r, '#rg-outprev'); glow(r, '#rg-refprev')
    print('out', round(r.now() - T0, 2)); r.wait(0.1)
    until(r, T0 + 6.95, 0.2); shot(r, 'p08c')


def a09(r):
    pg = r.page; T0 = r.now(); END = T0 + 3.85
    # side-by-side: reference vs new — same theme, colours, title block
    pop(r, [{'src': '#rg-refprev', 'inner': ' svg', 'title': '参照图　边海防无人化巡逻体系'},
            {'src': '#rg-outprev', 'inner': ' svg', 'title': '新图　海岛无人值守监视系统', 'color': '#C2692D'}], 0.45)
    r.keys('主题 · 配色 · 标题栏　原样继承', 1.6)
    until(r, T0 + 1.75, 0.6); shot(r, 'p09a')
    unpop(r, 0.25)
    glow(r, '#rg-outprev', False); glow(r, '#rg-refprev', False)
    r.move(*r.B['#rg-apply'], 0.25)
    pg.evaluate("()=>{const o=document.getElementById('pz');if(o)o.remove()}")
    x, y = r.B['#rg-apply']
    pg.evaluate("""([x,y])=>{document.dispatchEvent(new MouseEvent('mousedown',{clientX:x,clientY:y}));
      setTimeout(()=>document.querySelector('#rg-apply').click(),60)}""", [x, y])
    r.wait(0.1); pg.wait_for_function("()=>!document.querySelector('#rg').classList.contains('open')", timeout=8000)
    print('applied', round(r.now() - T0, 2))
    b = pg.evaluate("""()=>{const tb=P().nodes.find(n=>n.type==='tblock');return tb?[tb.x+tb.w/2,tb.y+tb.h/2]:null}""")
    rem = END - r.now()
    if b and rem > 1.0:
        k0 = pg.evaluate("()=>view.k")
        zoomto(r, b[0] - 120, b[1] - 80, k0 * 1.7, min(0.7, rem - 0.25))
    shot(r, 'p09b')
    until(r, END - 0.05)


ACTIONS = {'p09': a07, 'p10': a08, 'p11': a09}
