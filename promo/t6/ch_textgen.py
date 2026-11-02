IDS = ['007','008','009','010','011','012']

PROSE = ("无人机集群协同侦察体系分为指挥层、中继层和平台层。指挥层包括指挥所和卫通站。"
         "中继层由中继无人机和数据链电台组成。平台层包括察打一体无人机、四旋翼无人机和无人机机巢。"
         "指挥所向察打一体无人机下发任务指令。无人机机巢与四旋翼无人机互联。中继无人机通过数据链向卫通站回传情报。")

BODY = ("## 地面段\n### 指控层\n- 地面控制站、卫通站、无人机机巢 [新增]\n"
        "## 空中段\n### 平台层\n- 察打一体无人机、中继无人机、四旋翼无人机")

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

def ttype(r, text, secs):
    """type text so that it finishes within secs (time-based, catches up under load)"""
    t_end = r.now() + secs; n = len(text); i = 0
    while i < n:
        left = n - i; rem = t_end - r.now()
        per = rem / left if rem > 0 else 0
        k = 1 if per > 0.02 else max(1, min(left, int(0.03 / max(per, 0.001))))
        chunk = text[i:i+k]; i += k
        for ch in chunk:
            if ch == '\n': r.page.keyboard.press('Enter')
            else: r.page.keyboard.insert_text(ch)
        r.page.wait_for_timeout(int(max(0, per * len(chunk)) * 1000))

def _tmove(self, x, y, dur=0.6):
    import time
    x0, y0 = self.mx, self.my; t0 = time.time()
    while True:
        t = (time.time() - t0) / dur
        if t >= 1: break
        e = t * t * (3 - 2 * t)
        self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
    self.page.mouse.move(x, y); self.mx, self.my = x, y

def setup(r):
    import types
    r.move = types.MethodType(_tmove, r)
    r.page.evaluate("()=>{try{fit()}catch(e){}; window.SpeechRecognition=undefined; window.webkitSpeechRecognition=undefined;}")
    r.mx, r.my = 960, 600

def _end(r):
    r.page.evaluate("""()=>{const t=document.getElementById('tg-in');t.focus();t.setSelectionRange(t.value.length,t.value.length)}""")

def a007(r):
    r.press('Control+Shift+G', 'Ctrl + Shift + G　文字成图'); r.wait(0.5)
    r.click('#tg-in', dur=0.4, after=0.1)
    r.page.keyboard.press('Control+a'); r.page.keyboard.press('Delete'); r.wait(0.2)

def a008(r):
    ttype(r, "# 无人机集群协同侦察体系\n> 地面指控、空中侦察与数据回传协同\n", 1.4)
    r.page.evaluate("(b)=>{const t=document.getElementById('tg-in');t.value+=b;t.dispatchEvent(new Event('input',{bubbles:true}))}", BODY + "\n")
    _end(r); r.wait(0.3)
    r.move(*r.box('#tg-prev'), 0.4); r.wait(0.2)
    r.click('#tg-in', dur=0.3, after=0.05); _end(r)

def a009(r):
    ttype(r, "## 连接\n", 0.7); r.wait(0.3)
    ttype(r, "- ", 0.3); ttype(r, "地面控制站 ", 0.6); r.wait(0.1)
    ttype(r, "--> ", 0.4); ttype(r, "察打一体无人机 ", 0.7); r.wait(0.1)
    ttype(r, ": ", 0.3); ttype(r, "任务指令", 0.5); r.wait(0.1)
    ttype(r, "\n- 察打一体无人机 <-> 中继无人机 : 协同侦察\n- 无人机机巢 -> 四旋翼无人机 : 起降保障", 1.0)

def a010(r):
    r.move(*r.box('#tg-prev'), 0.4); r.wait(0.4)
    r.click('#tg-go', dur=0.4, after=0.1); r.wait(0.8)

def a011(r):
    x, y = r.node_xy('无人机机巢')
    r.page.evaluate("()=>{window.__v0={...view}}")
    cx = r.page.evaluate("([x,y])=>{const s=document.getElementById('svg').getBoundingClientRect();return [(x-s.left)/view.k+view.x,(y-s.top)/view.k+view.y]}", [x, y])
    zoomto(r, cx[0], cx[1], r.page.evaluate("()=>view.k") * 1.7, 0.7)
    r.move(*r.node_xy('无人机机巢'), 0.4); r.wait(0.3)
    r.page.evaluate("()=>{const v=window.__v0,s=document.getElementById('svg').getBoundingClientRect();const cx=v.x+s.width/2/v.k,cy=v.y+s.height/2/v.k;window.__z=[cx,cy,v.k]}")
    z = r.page.evaluate("()=>window.__z"); zoomto(r, z[0], z[1], z[2], 0.6)

def a012(r):
    r.press('Control+Shift+G', 'Ctrl + Shift + G　文字成图'); r.wait(0.5)
    r.click('#tg-in', dur=0.3, after=0.05)
    r.page.keyboard.press('Control+a'); r.page.keyboard.press('Delete')
    head, tail = PROSE[:-26], PROSE[-26:]
    r.page.fill('#tg-in', head); _end(r)
    ttype(r, tail, 1.4)
    r.move(*r.box('#tg-prev'), 0.4); r.wait(0.3)
    r.page.keyboard.press('Escape'); r.wait(0.4)

ACTIONS = {'007':a007,'008':a008,'009':a009,'010':a010,'011':a011,'012':a012}
import os
if os.environ.get('SHOT'):
    def _w(i, f):
        def g(r):
            f(r); r.page.screenshot(path=f'/tmp/claude-0/s/tg3_{i}.png')
        return g
    ACTIONS = {k:_w(k,v) for k,v in ACTIONS.items()}
