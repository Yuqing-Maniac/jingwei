#!/usr/bin/env python3
"""Coverage UI, geometric edits, undo/save and shared SVG export regression."""
import os
import pathlib
import functools
import http.server
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with sync_playwright() as pw:
        exe = os.environ.get('JW_CHROME')
        for candidate in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'):
            if not exe and os.path.exists(candidate):
                exe = candidate
        browser = pw.chromium.launch(**dict(args=['--no-sandbox'], **({'executable_path': exe} if exe else {})))
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto('http://127.0.0.1:%s/dist/offline.html' % server.server_port)
        page.wait_for_selector('#svg')
        assert page.evaluate('!!window.Coverage'), 'Module must be included in the production build'
        page.evaluate("""() => {
          loadDoc({name:'范围示意测试',theme:'report',custom:{},statusLabels:{base:'延续',new:'新增',key:'重点'},pages:{root:{id:'root',name:'总图',nodes:[],links:[]}}});
          addNode(SHAPES.find(s=>s.k==='coverage-radar').spec, 360, 300);
        }""")
        assert page.locator('#coverage-preview svg').count() == 1
        assert page.locator('#p-coverageRadius').input_value() == '120'
        before = page.evaluate('({x:P().nodes[0].x,y:P().nodes[0].y,w:P().nodes[0].w,h:P().nodes[0].h})')
        page.fill('#p-coverageRadius', '180')
        page.locator('#p-coverageRadius').blur()
        geo = page.evaluate('({x:P().nodes[0].x,y:P().nodes[0].y,w:P().nodes[0].w,h:P().nodes[0].h})')
        assert geo['w'] == geo['h'] == 360
        assert geo['x'] + 180 == before['x'] + 120
        assert geo['y'] + 180 == before['y'] + 120
        page.evaluate('undo()')
        assert page.evaluate('P().nodes[0].w') == 240
        page.evaluate('redo(); selectNodes([P().nodes[0].id]); render()')
        page.fill('#p-coverageHeading', '90')
        page.locator('#p-coverageHeading').blur()
        # Verify the actual transformed arc midpoint, rather than just a UI value.
        def center_vector():
            return page.evaluate('''() => {
              const n=P().nodes[0], a=(-90+n.sweep/2)*Math.PI/180;
              const q=rotPoint(n,n.x+n.w/2+Math.cos(a)*n.w/2,n.y+n.h/2+Math.sin(a)*n.h/2);
              return {dx:q.x-(n.x+n.w/2),dy:q.y-(n.y+n.h/2),heading:Coverage.heading(n)};
            }''')
        center = center_vector()
        assert abs(center['dy']) < 1e-7 and center['dx'] > 0 and center['heading'] == 90
        page.fill('#p-sweep', '75')
        page.locator('#p-sweep').blur()
        changed = center_vector()
        assert abs(changed['dy']) < 1e-7 and changed['dx'] > 0 and changed['heading'] == 90
        assert page.locator('#p-rot').count() == 0
        page.fill('#p-coverageAlpha', '25')
        page.locator('#p-coverageAlpha').blur()
        page.select_option('#p-coverageDash', '6 4')
        result = page.evaluate("""() => {
          const saved=JSON.parse(snapshot()); loadDoc(saved.doc); selectNodes([P().nodes[0].id]); render();
          const n=P().nodes[0];return {n:n,style:Coverage.style(n),caption:Coverage.caption(n),geom:shapeGeom(n.type,n.w,n.h,n.sweep),svg:exportSVGString(P(),false).str};
        }""")
        assert result['n']['rot'] == 52.5
        assert result['n']['sweep'] == 75
        assert result['n']['w'] == result['n']['h'] == 360
        assert result['style']['dash'] == '6 4'
        assert result['style']['fillAlpha'] == .25
        assert '半径 180 画布单位' in result['caption']
        assert '开角 75°' in result['caption']
        assert '75°' in result['svg']
        page.evaluate("doc.measure={px:10,unit:'示意格'}")
        page.check('#p-coverageScaled')
        assert page.locator('#p-coverageRadius').input_value() == '18'
        assert page.evaluate('P().nodes[0].w') == 360
        page.fill('#p-coverageRadius', '20')
        page.locator('#p-coverageRadius').blur()
        assert page.evaluate('P().nodes[0].w===400 && P().nodes[0].h===400')
        assert page.evaluate('Coverage.caption(P().nodes[0])').find('半径 20 示意格') >= 0
        page.uncheck('#p-coverageScaled')
        assert page.locator('#p-coverageRadius').input_value() == '200'
        assert page.evaluate('P().nodes[0].w') == 400
        page.evaluate("""() => { addNode(SHAPES.find(s=>s.k==='coverage-defense-dash').spec,700,300); }""")
        page.fill('[data-geo="w"]', '300')
        page.locator('[data-geo="w"]').blur()
        assert page.evaluate('P().nodes[1].w===300 && P().nodes[1].h===300')
        assert page.locator('#coverage-slide-coverageRadius').count() == 1
        # Palette entries remain ordinary drag/click specs and export geometry is native.
        assert page.evaluate("SHAPES.filter(s=>/^coverage-/.test(s.k)).length") == 4
        assert not errors, errors
        out = ROOT / '_work' / 'coverage-preview.png'
        out.parent.mkdir(exist_ok=True)
        page.evaluate('fit(); render()')
        page.screenshot(path=str(out))
        print('PASS coverage controls, circle radius, shared labels/export, undo/save; preview:', out)
        browser.close()


if __name__ == '__main__':
    main()
