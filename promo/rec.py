"""Screen recorder + helpers for scripted UI videos (CDP screencast → crisp frames)."""
import time, os, base64, subprocess, json, math, random

CURSOR_JS = r"""
(() => {
  if (window.__cur) return;
  const add = () => {
    const c = document.createElement('div'); window.__cur = c;
    c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;z-index:2147483647;pointer-events:none;transform:translate(-3px,-2px);transition:none';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M3 2 L3 21 L8 16.5 L11.5 24 L14.6 22.6 L11.2 15.4 L18 15.4 Z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    const r = document.createElement('div'); window.__ring = r;
    r.style.cssText = 'position:fixed;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;border:3px solid #2F80ED;opacity:0;z-index:2147483646;pointer-events:none';
    document.body.appendChild(r);
    const k = document.createElement('div'); window.__keys = k;
    k.style.cssText = 'position:fixed;left:50%;top:84px;transform:translateX(-50%);background:rgba(20,28,40,.88);color:#fff;font:600 26px "Noto Sans CJK SC",sans-serif;padding:10px 22px;border-radius:12px;z-index:2147483646;pointer-events:none;opacity:0;transition:opacity .2s;letter-spacing:.04em';
    document.body.appendChild(k);
    document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
    document.addEventListener('mousedown', e => { r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; r.animate([{opacity:.9, transform:'scale(.4)'},{opacity:0, transform:'scale(1.5)'}], {duration:500}); }, true);
  };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
})();
"""

class Rec:
    def __init__(self, page, outdir):
        self.page = page; self.out = outdir; os.makedirs(outdir, exist_ok=True)
        self.frames = []; self.cdp = page.context.new_cdp_session(page)
        self.mx, self.my = 960, 540
        self.cdp.on('Page.screencastFrame', self._frame)

    def _frame(self, ev):
        ts = ev['metadata'].get('timestamp') or time.time()
        fn = os.path.join(self.out, f"f{len(self.frames):06d}.jpg")
        with open(fn, 'wb') as f: f.write(base64.b64decode(ev['data']))
        self.frames.append((ts, fn))
        try: self.cdp.send('Page.screencastFrameAck', {'sessionId': ev['sessionId']})
        except Exception: pass

    def start(self):
        self.cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 92, 'maxWidth': 1920, 'maxHeight': 1080, 'everyNthFrame': 1})
        self.t0 = time.time(); self.wait(0.3); return self.t0

    def stop(self):
        self.wait(0.4); self.t1 = time.time()
        self.cdp.send('Page.stopScreencast')

    def now(self): return time.time() - self.t0

    def wait(self, s):
        # keep event loop pumping so frames arrive
        end = time.time() + s
        while time.time() < end:
            self.page.wait_for_timeout(min(50, max(1, int((end - time.time()) * 1000))))

    def keys(self, label, hold=1.1):
        self.page.evaluate("(t)=>{const k=window.__keys;k.textContent=t;k.style.opacity=1;clearTimeout(window.__kh);window.__kh=setTimeout(()=>k.style.opacity=0,%d)}" % int(hold * 1000), label)

    def move(self, x, y, dur=0.6):
        steps = max(6, int(dur * 40))
        x0, y0 = self.mx, self.my
        for i in range(1, steps + 1):
            t = i / steps; e = t * t * (3 - 2 * t)
            self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            self.page.wait_for_timeout(int(dur * 1000 / steps))
        self.mx, self.my = x, y

    def box(self, sel):
        el = self.page.locator(sel).first; el.scroll_into_view_if_needed(); bb = el.bounding_box()
        return bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2

    def click(self, sel=None, xy=None, dur=0.6, after=0.35):
        x, y = xy if xy else self.box(sel)
        self.move(x, y, dur); self.page.mouse.down(); self.page.wait_for_timeout(70); self.page.mouse.up(); self.wait(after)

    def dclick(self, xy, dur=0.5):
        self.move(*xy, dur); self.page.mouse.dblclick(*xy); self.wait(0.3)

    def drag(self, a, b, dur=1.0):
        self.move(*a, 0.5); self.page.mouse.down(); self.wait(0.15)
        steps = max(10, int(dur * 40)); x0, y0 = a
        for i in range(1, steps + 1):
            t = i / steps; e = t * t * (3 - 2 * t)
            self.page.mouse.move(x0 + (b[0] - x0) * e, y0 + (b[1] - y0) * e)
            self.page.wait_for_timeout(int(dur * 1000 / steps))
        self.mx, self.my = b; self.wait(0.12); self.page.mouse.up(); self.wait(0.3)

    def press(self, combo, label=None):
        if label: self.keys(label)
        self.page.keyboard.press(combo); self.wait(0.25)

    def type(self, text, cps=28):
        for ch in text:
            if ch == '\n': self.page.keyboard.press('Enter')
            else: self.page.keyboard.insert_text(ch)
            self.page.wait_for_timeout(int(1000 / cps))

    # world -> client helpers
    def node_xy(self, text, where='c'):
        r = self.page.evaluate("""([t,w])=>{const n=P().nodes.find(n=>(n.text||'').split('\\n')[0]===t)||P().nodes.find(n=>(n.text||'').includes(t)); if(!n) return null;
          const r=document.getElementById('svg').getBoundingClientRect();
          const X=v=>(v-view.x)*view.k+r.left, Y=v=>(v-view.y)*view.k+r.top;
          let x=n.x+n.w/2,y=n.y+n.h/2; if(w==='r'){x=n.x+n.w} if(w==='l'){x=n.x} if(w==='t'){y=n.y} if(w==='b'){y=n.y+n.h} if(w==='tr'){x=n.x+n.w-2;y=n.y+2}
          return [X(x),Y(y)]}""", [text, where])
        if not r: raise RuntimeError('node not found: ' + text)
        return tuple(r)

    def encode(self, path, end_time=None, fps=30):
        lst = os.path.join(self.out, 'list.txt')
        self.frames.sort(key=lambda f: f[0])
        fr = self.frames
        end = end_time if end_time is not None else self.t1
        with open(lst, 'w') as f:
            # pad start to t0
            for i, (ts, fn) in enumerate(fr):
                nxt = fr[i + 1][0] if i + 1 < len(fr) else end
                if i == 0 and ts > self.t0:
                    f.write(f"file '{fn}'\nduration {ts - self.t0:.4f}\n")
                f.write(f"file '{fn}'\nduration {max(0.001, nxt - ts):.4f}\n")
            f.write(f"file '{fr[-1][1]}'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                        '-vf', f'fps={fps},scale=1920:1080:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', path], check=True)
        return end - self.t0
