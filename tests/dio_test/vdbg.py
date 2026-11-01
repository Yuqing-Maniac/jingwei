import json, re, sys
from playwright.sync_api import sync_playwright
V='/tmp/claude-0/-home-claude/4a98c7fc-ad86-519e-b225-277215eac05a/scratchpad/drawio/src/main/webapp/js/viewer-static.min.js'
def render(x, out):
    html=f"<html><body style='margin:0;background:#fff'><div class='mxgraph' data-mxgraph='{json.dumps({'xml':x,'highlight':'none','nav':False}).replace('&','&amp;').replace(chr(39),'&#39;')}'></div><script src='file://{V}'></script></body></html>"
    open('vd.html','w',encoding='utf-8').write(html)
    with sync_playwright() as p:
        b=p.chromium.launch(); vp=b.new_page(viewport={'width':1500,'height':1100})
        vp.on('pageerror',lambda e: print('E',str(e)[:300]))
        vp.goto('file:///home/claude/drawtool/dio_test/vd.html'); vp.wait_for_timeout(7000)
        print(out, vp.evaluate("document.querySelectorAll('svg g g').length"), vp.evaluate("document.querySelector('.mxgraph svg') ? document.querySelector('.mxgraph svg').getAttribute('style') : 'nosvg'"))
        vp.screenshot(path=out, full_page=True); b.close()
x=open('layered.drawio',encoding='utf-8').read()

x2=re.sub(r'<UserObject label="[^"]*" id="n[a-z0-9]+_t".*?</UserObject>','',x)

for name,pat in [('a','movable=0;resizable=0;deletable=0;connectable=0;spacing=0'),('b','spacing=0')]:
    pass
x3=x.replace('movable=0;resizable=0;deletable=0;connectable=0;spacing=0','spacing=0'); render(x3,'d2.png')
x4=re.sub(r'(id="n[a-z0-9]+)_t"',r'\1t"',x); render(x4,'d3.png')
