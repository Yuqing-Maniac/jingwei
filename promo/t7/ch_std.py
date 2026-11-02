"""规范 chapter (p12, p13): grouped template gallery -> 部署架构图 -> view selector; violation -> check -> fix -> title block -> xlsx."""
import time, os, sys
sys.path.insert(0, '/home/claude/video/t7')
from ch_io import _tmove, hover, ring, clickat, zoomto
IDS = ['p14', 'p15']
SH = '/tmp/claude-0/t7s/'
XLSX = '/home/claude/video/t7/seg/std_demo.xlsx'


def shot(r, n):
    if os.environ.get('DBG'):
        try: r.page.screenshot(path=SH + n + '.png')
        except Exception: pass


def fitview(r):
    return r.page.evaluate("()=>{const v={...view};fit();const f={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView();"
                           "const s=document.getElementById('svg').getBoundingClientRect();return [f.x+s.width/2/f.k,f.y+s.height/2/f.k,f.k]}")


def setup(r):
    pg = r.page
    r.move = lambda x, y, dur=0.4: _tmove(r, x, y, dur)
    _enc = r.encode
    def _encode(path, end_time=None, fps=30):
        r.frames.sort(key=lambda f: f[0]); return _enc(path, end_time, fps)
    r.encode = _encode
    pg.on('download', lambda d: None)
    pg.evaluate("()=>{sel.clear();selLink=null;fit();render()}")
    pg.keyboard.press('Control+Shift+M'); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{const e=document.getElementById('tpl-ov');if(e)e.remove()}")
    pg.mouse.move(1180, 640); r.mx, r.my = 1180, 640


def scroll_gallery(r, to, dur):
    r.page.evaluate("""([to,dur])=>new Promise(res=>{const b=document.querySelector('.tpl-b');const a=b.scrollTop;const t0=performance.now();
      (function f(){const t=Math.min(1,(performance.now()-t0)/(dur*1000)),e=t*t*(3-2*t);b.scrollTop=a+(to-a)*e;if(t<1)requestAnimationFrame(f);else res()})()})""", [to, dur])


def a_p12(r):
    pg = r.page; t0 = time.time()
    pg.keyboard.press('Control+Shift+M'); r.keys('Ctrl + Shift + M　版式模板', hold=1.0)
    r.wait(0.1); shot(r, 'c1'); print('T1', time.time()-t0)
    # group header positions
    ys = pg.evaluate("()=>{const b=document.querySelector('.tpl-b');return [...b.querySelectorAll('.tpl-gh')].map(e=>[e.textContent,e.offsetTop])}")
    print(ys)
    r.keys('DoDAF 视图族　·　信息系统视图族', hold=2.0)
    # scroll to second group then third
    for nm, y in ys[2:]:
        scroll_gallery(r, max(0, y - 40), 0.65 if time.time()-t0 < 1.6 else 0.3); shot(r, 'c2_' + nm[:2])
    print('T2', time.time()-t0)
    # pick 部署架构图
    c = pg.locator('.tpl-card', has_text='部署架构').first
    c.scroll_into_view_if_needed()
    hover(r, '.tpl-card >> text=部署架构', 0.25)
    print('T3', time.time()-t0); clickat(r); r.wait(0.1)
    hover(r, '#tpl-use', 0.25); clickat(r)
    r.wait(0.15)
    pg.evaluate("()=>{fit()}")
    shot(r, 'c3')
    if time.time()-t0 > 5.0:
        print('p12 used', time.time()-t0); return
    r.move(1180, 700, 0.15)
    pg.evaluate("()=>{sel.clear();selLink=null;render()}")
    hover(r, '#std-view', 0.2)
    shot(r, 'c4')
    ring(r)
    pg.evaluate("""()=>{const e=document.getElementById('std-view');e.style.outline='3px solid #2F80ED';e.style.outlineOffset='2px';
      const o=[...e.querySelectorAll('optgroup')].map(g=>g.label).join('　|　');window.__keys.textContent=o;window.__keys.style.opacity=1;clearTimeout(window.__kh);window.__kh=setTimeout(()=>window.__keys.style.opacity=0,1500)}""")
    r.wait(0.2)
    print('p12 used', time.time() - t0)


def a_p13(r):
    pg = r.page; t0 = time.time()
    pg.evaluate("()=>{const e=document.getElementById('std-view');if(e)e.style.outline='';document.activeElement&&document.activeElement.blur()}")
    pg.evaluate("""()=>{const p=P(),g=t=>p.nodes.find(n=>(n.text||'').split('\\n')[0]===t);p.links.push({id:uid(),from:g('门户前端').id,to:g('涉密数据库').id,dir:'one',kind:'data',route:'ortho',label:'直连'});render()}""")
    r.page.evaluate("()=>{const k=window.__keys;k.style.top='auto';k.style.bottom='44px'}")
    pg.keyboard.press('Control+Shift+K'); r.keys('Ctrl + Shift + K　规范检查', hold=1.0)
    r.wait(0.25); shot(r, 'd1'); print('  T','d1',round(time.time()-t0,2))
    xy = pg.evaluate("()=>{const b=[...document.querySelectorAll('#std-dlg .it')].find(e=>e.textContent.includes('跨区直连')).querySelector('button').getBoundingClientRect();return [b.x+b.width/2,b.y+b.height/2]}")
    r.move(xy[0], xy[1], 0.2); clickat(r)
    r.wait(0.15); shot(r, 'd2'); print('  T d2', round(time.time()-t0,2))
    pg.keyboard.press('Delete'); r.wait(0.2); shot(r, 'd3'); print('  T','d3',round(time.time()-t0,2))
    pg.evaluate("()=>{sel.clear();selLink=null;render()}")
    tb = pg.evaluate("()=>{const n=P().nodes.find(n=>n.type==='tblock');return [n.x+n.w*0.5,n.y+n.h*0.5]}")
    if time.time()-t0 < 3.4: zoomto(r, tb[0] - 150, tb[1] - 60, 1.5, 0.45)
    shot(r, 'd4'); print('  T','d4',round(time.time()-t0,2))
    hover(r, '#std-xlsx', 0.2)
    with pg.expect_download() as d:
        clickat(r)
    r.keys('元素清单 · 接口清单 · 交换矩阵', hold=1.2)
    shot(r, 'd5')
    print('p13 used', time.time() - t0)


ACTIONS = {'p14': a_p12, 'p15': a_p13}
