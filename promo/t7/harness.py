"""Chapter-segment recorder for the long tutorial.

Each chapter module (/home/claude/video/t2/ch_<name>.py) defines:
    IDS     = ['011', '012', ...]          # script.json ids this segment narrates, in order
    def setup(r): ...                      # runs BEFORE recording starts (load doc, fit, set theme…)
    ACTIONS = {'011': fn, '012': fn, ...}  # fn(r) runs at the start of that sentence
and is recorded with:  python3 /home/claude/video/t2/harness.py <name> [--dry]
Output: /home/claude/video/t2/seg/<name>.mp4 + <name>.json  (times relative to segment start)
--dry : run actions without recording/encoding (fast iteration; still waits for audio lengths unless --fast)
--fast: do not wait for audio lengths (just run actions back to back)

Rules for actions: they receive r (rec.Rec) — r.page is the Playwright page.
Useful: r.move(x,y,dur), r.click(sel|xy=), r.dclick(xy), r.drag(a,b,dur), r.press(combo,label),
r.keys(label), r.type(text,cps), r.wait(s), r.node_xy(text, where='c'|'l'|'r'|'t'|'b'|'tr'), r.box(sel).
Only 2 recordings may run at once (2 CPU cores): the harness takes a slot lock automatically.
"""
import sys, os, json, time, importlib.util, subprocess, shutil, fcntl
sys.path.insert(0, '/home/claude/video')
from playwright.sync_api import sync_playwright
from rec import Rec, CURSOR_JS

T2 = '/home/claude/video/t7'
AUD = '/home/claude/video/t7/audio'
APP = 'file:///home/claude/drawtool/offline.html'
GAP = 0.22

def adur(i):
    p = f'{AUD}/{i}.mp3'
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)

def text_of():
    return {s['id']: s['text'] for s in json.load(open('/home/claude/video/t7/script.json', encoding='utf-8'))}

def slot():
    os.makedirs(f'{T2}/locks', exist_ok=True)
    while True:
        for k in range(2):
            f = open(f'{T2}/locks/slot{k}', 'w')
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB); return f
            except BlockingIOError:
                f.close()
        time.sleep(3)

def main():
    name = sys.argv[1]; dry = '--dry' in sys.argv; fast = '--fast' in sys.argv
    spec = importlib.util.spec_from_file_location('ch', f'{T2}/ch_{name}.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    TX = text_of(); lock = None if dry else slot()
    os.makedirs(f'{T2}/seg', exist_ok=True)
    fr = f'{T2}/frames_{name}'; shutil.rmtree(fr, ignore_errors=True)
    tl = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--font-render-hinting=none'])
        ctx = b.new_context(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1, accept_downloads=True)
        ctx.add_init_script(CURSOR_JS)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); pg.mouse.move(960, 600)
        r = Rec(pg, fr); r.mx, r.my = 960, 600
        if hasattr(m, 'setup'): m.setup(r)
        pg.wait_for_timeout(500)
        if dry:
            r.t0 = time.time()
        else:
            r.start()
        for i in m.IDS:
            t = r.now(); d = adur(i)
            fn = m.ACTIONS.get(i)
            if fn: fn(r)
            el = r.now() - t
            if not fast and el < d + GAP: r.wait(d + GAP - el)
            tl.append({'id': i, 'text': TX[i], 'start': t, 'end': r.now(), 'adur': d, 'act': el})
            print(f'{i} start={t:6.1f} act={el:5.1f} audio={d:5.1f} {"OVERRUN" if el > d + GAP else ""}', flush=True)
        r.wait(0.6)
        if not dry:
            r.stop(); dur = r.encode(f'{T2}/seg/{name}.mp4')
            json.dump({'name': name, 'dur': dur, 'tl': tl, 'errors': errs}, open(f'{T2}/seg/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('segment', name, 'duration', round(dur, 1))
        print('page errors:', errs)
        b.close()
    shutil.rmtree(fr, ignore_errors=True)
    if lock: lock.close()

if __name__ == '__main__':
    main()
