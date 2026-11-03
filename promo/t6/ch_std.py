"""体系规范 chapter (ids 028–035): view type → checker → 一键修复 → codes + title block → link attrs → pass → xlsx."""
import time

IDS = ['028', '029', '030', '031', '032', '033', '034', '035']
SHOT = '/tmp/claude-0/std'
XLSX = '/home/claude/video/t6/seg/std_demo.xlsx'
import os
DEBUG = bool(os.environ.get('STD_DEBUG'))


def shot(r, name):
    if DEBUG:
        r.page.screenshot(path=f'{SHOT}/{name}.png')


def zoomto(r, wx, wy, k, dur=0.8, wait=True):
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


def tscreen(r, wx, wy, cx, cy, k):
    """screen point of world (wx,wy) once the camera is centred on (cx,cy) at zoom k"""
    s = r.page.evaluate("()=>{const s=document.getElementById('svg').getBoundingClientRect();return [s.left,s.top,s.width,s.height]}")
    return s[0] + s[2] / 2 + (wx - cx) * k, s[1] + s[3] / 2 + (wy - cy) * k


def fitview(r):
    f = r.page.evaluate("()=>{const v={...view};fit();const f={...view};view.x=v.x;view.y=v.y;view.k=v.k;applyView();"
                        "const s=document.getElementById('svg').getBoundingClientRect();return [f.x+s.width/2/f.k,f.y+s.height/2/f.k,f.k]}")
    return f


def refit(r, dur=0.8):
    x, y, k = fitview(r)
    zoomto(r, x, y, k, dur)


def wc(r, text):
    return r.page.evaluate("(t)=>{const n=P().nodes.find(n=>(n.text||'').split('\\n')[0]===t);return [n.x+n.w/2,n.y+n.h/2]}", text)


def tb_center(r):
    return r.page.evaluate("()=>{const n=P().nodes.find(n=>n.type==='tblock');return [n.x+n.w/2,n.y+n.h/2]}")


def hover(r, sel, dur=0.35):
    bb = r.page.locator(sel).first.bounding_box()
    r.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2, dur)


def until(t0, T, r):
    left = T - (time.time() - t0)
    if left > 0: r.wait(left)


def setview(r, v):
    r.page.evaluate("(v)=>{const e=document.getElementById('std-view');e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}))}", v)


def keys_low(r, low):
    r.page.evaluate("(low)=>{const k=window.__keys;k.style.top=low?'auto':'84px';k.style.bottom=low?'44px':'auto'}", low)


def mark(r, tag):
    print('MARK', tag, round(r.now(), 2), flush=True)


def ring(r):
    r.page.evaluate("([x,y])=>{const g=window.__ring;g.style.left=x+'px';g.style.top=y+'px';g.animate([{opacity:.9,transform:'scale(.4)'},{opacity:0,transform:'scale(1.5)'}],{duration:500})}", [r.mx, r.my])


def _tmove(r, x, y, dur=0.4):
    x0, y0 = r.mx, r.my; t0 = time.time()
    while True:
        t = min(1.0, (time.time() - t0) / max(dur, 0.01)); e = t * t * (3 - 2 * t)
        r.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
        if t >= 1: break
        r.page.wait_for_timeout(16)
    r.mx, r.my = x, y


def _ttype(r, text, cps=18):
    t0 = time.time()
    for i, ch in enumerate(text):
        r.page.keyboard.insert_text(ch)
        left = (i + 1) / cps - (time.time() - t0)
        if left > 0: r.page.wait_for_timeout(int(left * 1000))


def setup(r):
    pg = r.page
    r.move = lambda x, y, dur=0.4: _tmove(r, x, y, dur)
    # screencast frame timestamps arrive slightly out of order (~36 per 30 s); Rec.encode clamps the negative
    # gaps to 0.001 s which stretches the video ~5 % and drifts it out of sync. Sort by capture time first.
    _enc = r.encode
    def _encode(path, end_time=None, fps=30):
        r.frames.sort(key=lambda f: f[0])
        return _enc(path, end_time, fps)
    r.encode = _encode
    r.type = lambda text, cps=18: _ttype(r, text, cps)
    pg.evaluate("""()=>{
      const p=P(), g=t=>p.nodes.find(n=>(n.text||'').split('\\n')[0]===t);
      // complete the sample so every element is connected (short in-row links)
      [['联合值班席','一线管控站','值班协同'],['巡逻指挥员','联合值班席','席位调度'],['高速无人拦截艇','波浪滑翔器','水下探测'],
       ['能源补给','运维监控','能源状态'],['维修保障','能源补给','保障工单']].forEach(([a,b,lab])=>
        p.links.push({id:uid(),from:g(a).id,to:g(b).id,dir:'one',kind:'data',route:'ortho',label:lab}));
      // unlabeled links get an exchange content (invisible attribute)
      for(const l of p.links) if(!(l.label||'').trim()) l.attrs=Object.assign({},l.attrs,{content:'状态数据'});
      doc.showCodes=true;
      Object.assign(Std.ensureMeta(),{project:'边海防无人化巡逻体系',drawingNo:'BHF-SV1-001',version:'V1.0',classification:'内部',
        author:'总体设计组',reviewer:'体系总师',approver:'技术负责人',date:'2026-10-15',org:'[单位名称]'});
      clearSel();fit();render();
      // start slightly zoomed in for the zoom-out overview of 028
      const s=document.getElementById('svg').getBoundingClientRect();
      const cx=view.x+s.width/2/view.k, cy=view.y+s.height/2/view.k; view.k*=1.6;
      view.x=cx-s.width/2/view.k+60; view.y=cy-s.height/2/view.k-120; applyView();
    }""")
    pg.mouse.move(1180, 640); r.mx, r.my = 1180, 640


# 028 第三招，也是最关键的一招：画出来的图，要经得起评审。 (4.4 s)
def a028(r):
    pg = r.page
    pg.evaluate("""()=>{
      const d=document.createElement('div'); d.id='__punch';
      d.style.cssText='position:fixed;left:50%;top:46%;transform:translate(-50%,-50%);z-index:2147483640;pointer-events:none;'+
        'background:rgba(20,28,40,.90);color:#fff;font:800 76px "Noto Sans CJK SC",sans-serif;letter-spacing:.12em;padding:22px 54px 26px 66px;border-radius:20px;'+
        'box-shadow:0 18px 60px rgba(0,0,0,.28);opacity:0';
      d.innerHTML='经得起评审<div style="height:6px;margin:12px auto 0;width:0;background:#2F80ED;border-radius:3px;transition:width .5s ease-out" id="__punchbar"></div>';
      document.body.appendChild(d); window.__punch=d;}""")
    x, y, k = fitview(r)
    zoomto(r, x, y, k, 1.2, wait=False)
    r.move(1040, 560, 0.5)
    r.wait(0.25)
    pg.evaluate("""()=>{const d=window.__punch;
      d.animate([{opacity:0,transform:'translate(-50%,-50%) scale(.82)'},{opacity:1,transform:'translate(-50%,-50%) scale(1.04)',offset:.7},{opacity:1,transform:'translate(-50%,-50%) scale(1)'}],{duration:380,fill:'forwards',easing:'ease-out'});
      setTimeout(()=>document.getElementById('__punchbar').style.width='100%',250);}""")
    r.wait(0.5); shot(r, 's028')
    r.wait(1.4)
    pg.evaluate("""()=>{const d=window.__punch;d.animate([{opacity:1,transform:'translate(-50%,-50%) scale(1)'},{opacity:0,transform:'translate(-50%,-50%) scale(1.06)'}],{duration:300,fill:'forwards'}).onfinish=()=>d.remove();}""")
    r.wait(0.3)


# 029 在图面设置里选择视图类型，OV-1 到 SV-4，DoDAF 和 UAF 的常用视图都有。 (7.65 s)
OPTS = [('', '自由绘图'), ('OV-1', 'OV-1　高层作战概念图'), ('OV-2', 'OV-2　作战资源流描述'), ('OV-5b', 'OV-5b　作战活动模型'),
        ('SV-1', 'SV-1　系统接口描述'), ('SV-4', 'SV-4　系统功能描述')]


def a029(r):
    pg = r.page
    t0 = time.time()
    hover(r, '.hint >> text=规范', 0.45)            # 规范 section header
    hover(r, '#std-view', 0.35); r.wait(0.15)
    bb = pg.locator('#std-view').bounding_box()
    ring(r)
    pg.evaluate("""([bb,opts])=>{
      const d=document.createElement('div'); d.id='__dd'; const H=30;
      d.style.cssText=`position:fixed;left:${bb.x}px;top:${bb.y-opts.length*H-6}px;width:${bb.width}px;background:#fff;border:1px solid #9AA6B5;border-radius:6px;`+
        'box-shadow:0 10px 30px rgba(0,0,0,.18);z-index:2147483600;padding:3px 0;font:13.5px "Noto Sans CJK SC",sans-serif;color:#18202B;pointer-events:none';
      d.innerHTML=opts.map((o,i)=>`<div data-i="${i}" style="height:${H}px;line-height:${H}px;padding:0 10px;white-space:nowrap;overflow:hidden">${o[1]}</div>`).join('');
      document.body.appendChild(d);
      window.__ddHi=i=>d.querySelectorAll('[data-i]').forEach((e,j)=>{e.style.background=j===i?'#2F80ED':'';e.style.color=j===i?'#fff':''});
      window.__ddHi(0);
    }""", [bb, OPTS])
    rows = pg.evaluate("()=>[...document.querySelectorAll('#__dd [data-i]')].map(e=>{const b=e.getBoundingClientRect();return [b.x+b.width*0.45,b.y+b.height/2]})")
    shot(r, 's029a')
    ts = time.time() - t0
    for j, i in enumerate([1, 2, 3, 4, 5]):
        r.move(*rows[i], 0.2)
        pg.evaluate(f"()=>window.__ddHi({i})")
        setview(r, OPTS[i][0])
        if i == 3: shot(r, 's029b')
        until(t0, ts + 0.6 * (j + 1), r)
    r.move(*rows[4], 0.25); pg.evaluate("()=>window.__ddHi(4)"); r.wait(0.2)
    ring(r); r.wait(0.08)
    pg.evaluate("()=>document.getElementById('__dd').remove()")
    setview(r, 'SV-1')
    pg.evaluate("()=>document.activeElement&&document.activeElement.blur()")
    r.wait(0.2)
    hb = pg.locator('#props .hint >> text=元素：').first.bounding_box()
    r.move(hb['x'] + 60, hb['y'] + hb['height'] / 2, 0.35)
    shot(r, 's029c')
    left = 6.7 - (time.time() - t0)
    if left > 0: r.wait(left)


# 030 按 Ctrl 加 Shift 加 K，规范检查逐条列出不合规的地方，点一下直接定位。 (6.58 s)
def a030(r):
    pg = r.page
    r.move(1100, 560, 0.3)
    mark(r, 'K030'); keys_low(r, True); r.press('Control+Shift+K', 'Ctrl + Shift + K　规范检查')
    r.wait(0.9); shot(r, 's030a')
    r.move(960, 640, 0.3)
    for _ in range(6):
        pg.mouse.wheel(0, 110); r.wait(0.11)
    r.wait(0.3)
    # pick a visible 定位 for a concrete interface
    loc = pg.locator('#std-body .it', has_text='巡逻无人艇 → 高速无人拦截艇').locator('button').first
    if not loc.is_visible():
        loc = pg.locator('#std-body .it button >> visible=true').nth(6)
    loc.scroll_into_view_if_needed()
    bb = loc.bounding_box()
    r.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2, 0.4); r.wait(0.15)
    shot(r, 's030b')
    # animate the camera move that 定位 performs
    pg.evaluate("""()=>{window.__pv={...view}; const orig=window.applyView; window.__origAV=orig;
      window.applyView=function(){const tgt={...view}, pv=window.__pv; if(Math.abs(tgt.k-pv.k)<1e-6&&Math.abs(tgt.x-pv.x)<1e-6&&Math.abs(tgt.y-pv.y)<1e-6){orig();return} window.applyView=orig;
        view.x=pv.x;view.y=pv.y;view.k=pv.k;orig();
        const s=document.getElementById('svg').getBoundingClientRect(), W=s.width,H=s.height;
        const c0=[pv.x+W/2/pv.k,pv.y+H/2/pv.k], c1=[tgt.x+W/2/tgt.k,tgt.y+H/2/tgt.k], t0=performance.now();
        (function f(){const t=Math.min(1,(performance.now()-t0)/750),e=t*t*(3-2*t);view.k=pv.k+(tgt.k-pv.k)*e;
          view.x=c0[0]+(c1[0]-c0[0])*e-W/2/view.k; view.y=c0[1]+(c1[1]-c0[1])*e-H/2/view.k; orig(); if(t<1)requestAnimationFrame(f)})();
      };}""")
    pg.mouse.down(); pg.wait_for_timeout(60); pg.mouse.up()
    r.wait(0.3)
    r.move(1250, 700, 0.35)
    r.wait(0.4); shot(r, 's030c')
    pg.evaluate("()=>{if(window.__origAV)window.applyView=window.__origAV}")


# 031 一键修复：补类型、补编号、补图例，再加上标准的工程标题栏。 (5.88 s)
def a031(r):
    pg = r.page
    t0 = time.time()
    pg.evaluate("()=>{clearSel();render()}")
    mark(r, 'K031'); keys_low(r, True); r.press('Control+Shift+K', 'Ctrl + Shift + K　规范检查')
    r.wait(0.1)
    r.click('#std-fix', dur=0.3, after=0.5)
    shot(r, 's031a')
    r.click('#std-close', dur=0.25, after=0.0)
    x, y, k = fitview(r)
    zoomto(r, x, y, k, 0.6, wait=False)     # overview: codes everywhere + new title block
    r.move(1250, 640, 0.35); r.wait(0.45)
    shot(r, 's031b')
    tx, ty = tb_center(r)
    tw = pg.evaluate("()=>{const n=P().nodes.find(n=>n.type==='tblock');return [n.x+n.w*0.3,n.y+n.h*0.5]}")
    cx, cy, kk = tx - 80, ty - 40, 1.45
    zoomto(r, cx, cy, kk, 0.75, wait=False)
    r.move(*tscreen(r, tw[0], tw[1], cx, cy, kk), 0.75)
    shot(r, 's031c')
    left = 5.3 - (time.time() - t0)
    if left > 0: r.wait(left)


# 032 编号和标题栏同步显示在图上，也同步带进 PPT 和 Visio。 (5.77 s)
def a032(r):
    pg = r.page
    t0 = time.time()
    x, y = wc(r, '四旋翼巡查无人机')
    cx, cy, kk = x - 120, y - 10, 1.6
    zoomto(r, cx, cy, kk, 0.65, wait=False)
    tag = pg.evaluate("()=>{const n=P().nodes.find(n=>(n.text||'').split('\\n')[0]==='垂起固定翼无人机');return [n.x+16,n.y-7]}")
    r.move(*tscreen(r, tag[0], tag[1], cx, cy, kk), 0.65)
    until(t0, 1.1, r)
    shot(r, 's032a')
    x, y, k = fitview(r)
    tx, ty = tb_center(r)
    zoomto(r, (x + tx) / 2 + 120, (y + ty) / 2 + 80, k * 1.15, 0.6, wait=False)
    hover(r, '#b-export', 0.5)
    ring(r); pg.evaluate("()=>document.getElementById('b-export').click()"); r.wait(0.1)
    bp = r.box('[data-exp=pptx]'); bv = r.box('[data-exp=vsdx]')
    r.move(*bp, 0.25); until(t0, 3.3, r)
    shot(r, 's032b')
    r.move(*bv, 0.22); until(t0, 4.3, r)
    pg.keyboard.press('Escape')
    pg.evaluate("()=>document.querySelectorAll('.menu.open').forEach(m=>m.classList.remove('open'))")
    left = 5.0 - (time.time() - t0)
    if left > 0: r.wait(left)


# 033 接口的协议、链路、频度、时延，直接在属性里填写。 (4.73 s)
def a033(r):
    pg = r.page
    T0 = time.time()
    # the interface 巡逻无人艇 → 高速无人拦截艇 (编队协同)
    info = pg.evaluate("""()=>{const p=P(),g=t=>p.nodes.find(n=>(n.text||'').split('\\n')[0]===t);
      const l=p.links.find(l=>l.from===g('巡逻无人艇').id&&l.to===g('高速无人拦截艇').id);
      const pts=linkPoints(l,p); const a=pts[0],b=pts[pts.length-1];
      return {id:l.id,wx:a.x+(b.x-a.x)*0.3,wy:a.y+(b.y-a.y)*0.3}}""")
    cx, cy, kk = info['wx'] + 60, info['wy'] - 20, 1.5
    zoomto(r, cx, cy, kk, 0.35, wait=False)
    r.move(*tscreen(r, info['wx'], info['wy'], cx, cy, kk), 0.35)
    pg.mouse.down(); pg.wait_for_timeout(50); pg.mouse.up()
    pg.evaluate("(id)=>{selectLinks([id]);render()}", info['id'])
    r.wait(0.05)
    if DEBUG: print('T sel', round(time.time() - T0, 2))
    boxes = pg.evaluate("()=>Object.fromEntries(['protocol','medium','freq','latency'].map(k=>{const b=document.getElementById('std-a-'+k).getBoundingClientRect();return [k,[b.x+b.width*0.45,b.y+b.height/2]]}))")
    for sid, val in [('protocol', 'TCP/IP'), ('medium', '超短波数据链'), ('freq', '10 Hz'), ('latency', '≤50 ms')]:
        tt = time.time(); r.move(*boxes[sid], 0.15); pg.mouse.down(); pg.mouse.up(); t1 = time.time()
        r.type(val, cps=20)
        if DEBUG: print('T', sid, round(t1 - tt, 2), round(time.time() - t1, 2))
    shot(r, 's033')
    # complete every other interface invisibly so the re-check passes
    pg.evaluate("""()=>{for(const l of P().links){const a=l.attrs||{};l.attrs=Object.assign({},a,{protocol:a.protocol||'TCP/IP',medium:a.medium||'超短波数据链',
       content:a.content||(l.label||'').trim()||'状态数据'})}; document.activeElement&&document.activeElement.blur();}""")


# 034 复查一遍，全部通过。 (1.99 s)
def a034(r):
    pg = r.page
    mark(r, 'K034'); keys_low(r, True); r.press('Control+Shift+K', 'Ctrl + Shift + K　规范检查')
    r.click('#std-re', dur=0.25, after=0.0)
    pg.evaluate("""()=>{const ps=[...document.querySelectorAll('#std-dlg .pill')];
      ps.forEach((e,i)=>{e.style.transformOrigin='left center';e.style.display='inline-flex';
        e.animate([{transform:'scale(1)'},{transform:'scale(1.45)',offset:.45},{transform:'scale(1)'}],{duration:650,delay:i*60,easing:'ease-out'})});
      const ok=ps.find(e=>e.textContent.trim()==='通过'); if(ok){ok.style.background='#0E9F8E';ok.style.color='#fff';ok.style.borderColor='#0E9F8E';ok.style.fontWeight='700'}}""")
    r.wait(0.35)
    shot(r, 's034')
    print('ISSUES', pg.evaluate("()=>Std.check().length"))


# 035 最后一键导出规范表格：元素清单、接口清单、信息交换矩阵，图和表同源同步。 (7.44 s)
def a035(r):
    pg = r.page
    t0 = time.time()
    r.click('#std-close', dur=0.3, after=0.05)
    pg.evaluate("()=>{clearSel();render()}")
    refit(r, 0.6)
    hover(r, '#std-xlsx', 0.45); r.wait(0.2)
    with pg.expect_download() as d:
        pg.mouse.down(); pg.wait_for_timeout(60); pg.mouse.up()
    d.value.save_as(XLSX)
    keys_low(r, False)
    r.keys('元素清单 · 接口清单 · 信息交换矩阵', hold=2.6)
    shot(r, 's035')
    r.move(1300, 760, 0.6)
    left = 6.8 - (time.time() - t0)
    if left > 0: r.wait(left)


ACTIONS = {'028': a028, '029': a029, '030': a030, '031': a031, '032': a032, '033': a033, '034': a034, '035': a035}
