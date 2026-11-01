"""Launch packaged Electron under Xvfb with CDP, screenshot and exercise the desktop UI."""
import subprocess, time, os, sys
sys.path.insert(0, '/home/claude/desk/tools'); import cdp
EXE = os.environ.get('EXE', '/home/claude/desk/rt/linux-x64/electron')
OUT = '/tmp/claude-0/etest'; os.makedirs(OUT, exist_ok=True)
W, H = (int(x) for x in os.environ.get('SCR', '1600x1000').split('x'))
env = dict(os.environ, HOME='/tmp/claude-0/ehome'); os.makedirs(env['HOME'], exist_ok=True)
xv = subprocess.Popen(['Xvfb', ':77', '-screen', '0', f'{W}x{H}x24'], stderr=subprocess.DEVNULL); time.sleep(1)
env['DISPLAY'] = ':77'
args = [a for a in sys.argv[1:] if a.startswith('-') or a.endswith(('.json', '.vsdx', '.pptx'))]
el = subprocess.Popen([EXE, '--no-sandbox', '--remote-debugging-port=9333'] + args, env=env, stdout=open(OUT + '/el.log', 'w'), stderr=subprocess.STDOUT)
try:
    try:
        sp = cdp.page('splash.html', timeout=8); time.sleep(0.5); sp.shot(OUT + '/splash.png'); print('splash ok')
    except Exception as e: print('splash', e)
    pg = cdp.page('app/index.html')
    pg.js("window.__errs=[];window.addEventListener('error',e=>__errs.push(String(e.message)));true")
    pg.wait("document.readyState==='complete' && !!document.querySelector('#jw-start')")
    time.sleep(1.2)
    print('start on', pg.js("document.querySelector('#jw-start').classList.contains('on')"))
    pg.shot(OUT + '/start.png')
    exec(open('/home/claude/desk/tools/scenario.py').read()) if os.path.exists('/home/claude/desk/tools/scenario.py') else None
    print('errs', pg.js('window.__errs'))
finally:
    el.terminate(); time.sleep(0.6); el.kill(); xv.kill()
