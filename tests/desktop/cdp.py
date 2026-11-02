"""Minimal CDP client for testing the Electron app."""
import json, time, urllib.request, base64, websocket, os, itertools
os.environ['NO_PROXY'] = '127.0.0.1,localhost'
class Page:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60, http_no_proxy=['127.0.0.1'], suppress_origin=True); self.n = itertools.count(1); self.events = []
    def call(self, method, **params):
        i = next(self.n); self.ws.send(json.dumps({'id': i, 'method': method, 'params': params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == i:
                if 'error' in m: raise RuntimeError(m['error'])
                return m.get('result', {})
            self.events.append(m)
    def js(self, expr, await_=True):
        r = self.call('Runtime.evaluate', expression=expr, awaitPromise=await_, returnByValue=True)
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'].get('exception', {}).get('description') or r['exceptionDetails'])
        return r['result'].get('value')
    def shot(self, path):
        open(path, 'wb').write(base64.b64decode(self.call('Page.captureScreenshot', format='png')['data']))
    def key(self, key, code, vk, mods=0):
        for t in ('rawKeyDown', 'keyUp'):
            self.call('Input.dispatchKeyEvent', type=t, key=key, code=code, windowsVirtualKeyCode=vk, modifiers=mods)
    def click(self, x, y):
        for t in ('mousePressed', 'mouseReleased'):
            self.call('Input.dispatchMouseEvent', type=t, x=x, y=y, button='left', clickCount=1)
    def wait(self, expr, timeout=20):
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                if self.js(expr): return True
            except Exception: pass
            time.sleep(0.2)
        raise TimeoutError(expr)
def targets(port=9333):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return json.loads(op.open(f'http://127.0.0.1:{port}/json').read())
def page(match, port=9333, timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            for t in targets(port):
                if t.get('type') == 'page' and match in t.get('url', ''): return Page(t['webSocketDebuggerUrl'])
        except Exception: pass
        time.sleep(0.2)
    raise TimeoutError(match)
