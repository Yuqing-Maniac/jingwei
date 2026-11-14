"""Real-browser alpha selection geometry, handle resizing and hit regression.

Build dist/offline.html first. Uses HTTP so Chromium's file URL policy cannot
silently replace the application with an administrator-blocked error document.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_work' / 'selectionbounds-test'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = None
    url = os.environ.get('JW_TEST_URL')
    if not url:
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = 'http://127.0.0.1:%d/dist/offline.html' % server.server_port
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or shutil.which('chromium'),
                                         args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1600, 'height': 1050})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(url, timeout=90000)
            page.wait_for_function('typeof nodeLayout === "function"')
            assert page.evaluate('!!window.JwSelectionBounds && !!window.JwIconLabels'), 'Rebuild offline.html with selectionbounds.js after iconlabels.js'
            auto_before = page.evaluate('''() => {
              doc.pages={root:{id:'root',name:'Automatic alpha',nodes:[],links:[],noLegend:true}};cur='root';
              doc.custom.selectionAutomatic={name:'Automatic alpha',aspect:1,
                uri:svgUri('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect x="25" y="30" width="40" height="35" fill="#db8317"/></svg>')};
              const n=mkNode({type:'equip',icon:'cu:selectionAutomatic',x:200,y:150,w:120,h:140,text:'Auto',noBox:true});
              P().nodes=[n];selectNodes([n.id]);render();return JSON.stringify(n);
            }''')
            # No ready() call and no iconLabelGap opt-in: selection itself must
            # start the alpha scan and its completion must refresh the controls.
            page.wait_for_function('''() => {
              const n=P().nodes[0],b=JwSelectionBounds.box(n),ic=nodeLayout(n).icon;
              const grip=world.querySelector('[data-h="se"]');
              return b.w<ic.w*.5 && grip && Math.abs(+grip.getAttribute('x')+(+grip.getAttribute('width'))/2-b.x-b.w)<.1;
            }''')
            assert page.evaluate('JSON.stringify(P().nodes[0])') == auto_before
            fixtures = page.evaluate('''async () => {
              doc.pages={root:{id:'root',name:'Visible selection',nodes:[],links:[],noLegend:true}};cur='root';
              doc.custom.selectionAlpha={name:'Alpha fixture',aspect:1,
                uri:svgUri('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect x="20" y="20" width="60" height="50" fill="#1759cf"/></svg>')};
              const country=ICONS.find(i=>i.countries&&i.countries.cn&&i.countries.us);
              if(!country)throw Error('Real country asset missing');
              const nodes=[
                mkNode({type:'equip',icon:'cu:selectionAlpha',text:'Caption',x:180,y:160,w:120,h:140,noBox:true}),
                mkNode({type:'equip',icon:'lib:'+country.key,text:'Library',x:370,y:160,w:120,h:140,noBox:true}),
                mkNode({type:'equip',icon:'lib:'+country.key,appearance:'cn',text:'Country CN',x:560,y:160,w:120,h:140,noBox:true}),
                mkNode({type:'equip',icon:'lib:'+country.key,appearance:'us',text:'Country US',x:750,y:160,w:120,h:140,noBox:true}),
                mkNode({type:'equip',icon:'ms:SFGPUCI----K---',text:'Military symbol',x:940,y:160,w:120,h:140,noBox:true})
              ];
              P().nodes=nodes;clearSel();render();
              window.selectionFixtureIds=nodes.map(n=>n.id);
              const before=projectJSON();
              // A normal selection query starts alpha loading without a caption
              // opt-in or manually selecting "tight label".
              nodes.forEach(n=>JwSelectionBounds.box(n));
              await JwSelectionBounds.ready(P());
              await new Promise(r=>setTimeout(r,40));
              const same=before===projectJSON();
              return {same,nodes:nodes.map(n=>{const ic=nodeLayout(n).icon,b=JwSelectionBounds.box(n),v=JwIconLabels.visualBox(ic);
                return {id:n.id,icon:n.icon,country:n.appearance||'',node:{x:n.x,y:n.y,w:n.w,h:n.h},box:b,
                  expected:{x:v.x,y:v.y,w:v.right-v.x,h:v.bottom-v.y},gapOptIn:'iconLabelGap' in n,
                  excludesLabel:b.y+b.h<nodeLayout(n).text.box[1]};})};
            }''')
            assert fixtures['same'], 'Reading/awaiting alpha geometry changed legacy document serialization'
            assert len(fixtures['nodes']) == 5
            for row in fixtures['nodes']:
                assert not row['gapOptIn'] and row['excludesLabel'], row
                for key in ('x', 'y', 'w', 'h'):
                    assert abs(row['box'][key] - row['expected'][key]) < 1e-7, row
                assert row['box']['w'] < row['node']['w'] and row['box']['h'] < row['node']['h'], row
            custom = fixtures['nodes'][0]
            assert abs(custom['box']['w'] / 108 - .6) < .015, custom
            assert abs(custom['box']['h'] / 108 - .5) < .015, custom
            page.evaluate('selectNodes(window.selectionFixtureIds);render()')
            page.screenshot(path=str(OUT / 'real-family-alpha-frames.png'))

            geometry = page.evaluate('''() => {
              const api=JwSelectionBounds, original=nodeById(window.selectionFixtureIds[0]), rows=[];
              const diagonal={nw:'se',ne:'sw',sw:'ne',se:'nw'};
              const before=JSON.stringify(original);
              for(const rot of [0,37,90,180])for(const h of ['nw','ne','sw','se']){
                const n={...original,rot},b=api.box(n),cs=api.corners(n),grip=cs.find(c=>c.h===h),a=cs.find(c=>c.h===diagonal[h]);
                const expected=rotPoint(n,b.x+(h.includes('e')?b.w:0),b.y+(h.includes('s')?b.h:0));
                const session=api.beginResize(n,h,grip),out=api.resize(session,{x:grip.x+.2*(grip.x-a.x),y:grip.y+.2*(grip.y-a.y)});
                const result={...n,...out},fixed=api.corners(result).find(c=>c.h===diagonal[h]);
                const bbox=api.bounds(result),vb=api.box(result),center=rotPoint(result,vb.x+vb.w/2,vb.y+vb.h/2);
                rows.push({rot,h,cornerError:Math.hypot(grip.x-expected.x,grip.y-expected.y),
                  anchorError:Math.hypot(fixed.x-a.x,fixed.y-a.y),scale:vb.w/b.w,
                  hitsCenter:api.hit(result,center),contained:api.contains(result,{x:bbox.x-.1,y:bbox.y-.1,w:bbox.w+.2,h:bbox.h+.2}),
                  missesSmallMarquee:!api.contains(result,{x:bbox.x+1,y:bbox.y+1,w:bbox.w-2,h:bbox.h-2}),
                  resized:out.w!==n.w&&out.h!==n.h,unchanged:JSON.stringify(original)===before});
              }
              const plain=mkNode({x:25,y:30,w:130,h:45}),framed={...original,noBox:false},highlighted={...original,status:'new'};
              const capped={...original,w:240,h:240},cs=api.corners(capped),grip=cs.find(c=>c.h==='se'),a=cs.find(c=>c.h==='nw');
              const cap=api.resize(api.beginResize(capped,'se',grip),{x:grip.x+100,y:grip.y+100});
              const huge={...original,w:800,h:800,rot:37},hc=api.corners(huge),hg=hc.find(c=>c.h==='se'),ha=hc.find(c=>c.h==='nw');
              const shrunk={...huge,...api.resize(api.beginResize(huge,'se',hg),{x:hg.x-.25*(hg.x-ha.x),y:hg.y-.25*(hg.y-ha.y)})};
              const fixed=api.corners(shrunk).find(c=>c.h==='nw');
              return {rows,plain:{box:api.box(plain),session:api.beginResize(plain,'se',{x:155,y:75})},
                framed:{box:api.box(framed),session:api.beginResize(framed,'se',grip)},
                highlighted:{box:api.box(highlighted),session:api.beginResize(highlighted,'se',grip)},
                legacyBox:{x:original.x,y:original.y,w:original.w,h:original.h},cap,capOriginal:{x:capped.x,y:capped.y,w:capped.w,h:capped.h},
                huge:{scale:api.box(shrunk).w/api.box(huge).w,anchorError:Math.hypot(fixed.x-ha.x,fixed.y-ha.y),w:shrunk.w,h:shrunk.h}};
            }''')
            for row in geometry['rows']:
                assert row['cornerError'] < 1e-7 and row['anchorError'] < 1e-6, row
                assert abs(row['scale'] - 1.2) < 1e-5, row
                assert all(row[k] for k in ('hitsCenter', 'contained', 'missesSmallMarquee', 'resized', 'unchanged')), row
            assert geometry['plain'] == {'box': {'x': 25, 'y': 30, 'w': 130, 'h': 45}, 'session': None}, geometry
            for kind in ('framed', 'highlighted'):
                assert geometry[kind]['box'] == geometry['legacyBox'] and geometry[kind]['session'] is None, geometry
            assert geometry['cap'] == geometry['capOriginal'], 'Existing 140px icon cap must not inflate invisible padding'
            assert abs(geometry['huge']['scale'] - .75) < 1e-5 and geometry['huge']['anchorError'] < 1e-6, geometry['huge']
            assert geometry['huge']['w'] < 800 and geometry['huge']['h'] < 800, 'Cannot shrink capped legacy node through surplus padding'

            # Pure API checks above do not substitute for the actual core grips.
            # Use a rotated node so a forgotten legacy n.w/h handler fails here.
            controls = page.evaluate('''() => {
              const n=nodeById(window.selectionFixtureIds[0]);n.rot=37;P().nodes=[n];selectNodes([n.id]);
              view={x:0,y:0,k:1};render();
              const cs=JwSelectionBounds.corners(n),r=svg.getBoundingClientRect();
              return {id:n.id,corners:cs,grips:Array.from(world.querySelectorAll('[data-h]')).filter(e=>e.dataset.h!=='rot').map(e=>({h:e.dataset.h,
                x:+e.getAttribute('x')+(+e.getAttribute('width'))/2,y:+e.getAttribute('y')+(+e.getAttribute('height'))/2})),
                screen:{x:r.left,y:r.top},before:{x:n.x,y:n.y,w:n.w,h:n.h},box:JwSelectionBounds.box(n)};
            }''')
            assert len(controls['grips']) == 4, controls
            for grip in controls['grips']:
                expect = next(c for c in controls['corners'] if c['h'] == grip['h'])
                assert abs(expect['x'] - grip['x']) < .1 and abs(expect['y'] - grip['y']) < .1, 'Core grips still use invisible node gutters: ' + str(controls)
            se = next(c for c in controls['corners'] if c['h'] == 'se')
            nw = next(c for c in controls['corners'] if c['h'] == 'nw')
            sx, sy = controls['screen']['x'], controls['screen']['y']
            page.mouse.move(sx + se['x'], sy + se['y'])
            page.mouse.down()
            page.mouse.move(sx + se['x'] + .2 * (se['x'] - nw['x']), sy + se['y'] + .2 * (se['y'] - nw['y']), steps=8)
            page.mouse.up()
            resized = page.evaluate('''() => {const n=selectedNodes()[0];return {node:{x:n.x,y:n.y,w:n.w,h:n.h},corners:JwSelectionBounds.corners(n),box:JwSelectionBounds.box(n)};}''')
            fixed = next(c for c in resized['corners'] if c['h'] == 'nw')
            assert abs(fixed['x'] - nw['x']) < .2 and abs(fixed['y'] - nw['y']) < .2, resized
            assert resized['node']['w'] > controls['before']['w'] + 5 and resized['node']['h'] > controls['before']['h'] + 5, resized
            assert resized['box']['w'] > controls['box']['w'] * 1.1, resized
            page.screenshot(path=str(OUT / 'rotated-alpha-handles.png'))

            # Caption remains an ordinary selection/move target outside alpha.
            page.evaluate('''() => {const n=selectedNodes()[0];n.rot=0;n.iconLabelDx=170;n.iconLabelDy=0;clearSel();render();}''')
            label = page.locator('[data-icon-label]').bounding_box()
            page.mouse.click(label['x'] + label['width']/2, label['y'] + label['height']/2)
            assert page.evaluate('selectedNodes()[0].id') == controls['id'], 'Caption outside alpha no longer selects its node'

            # A top icon's transparent outer padding must not consume clicks on
            # a real visible object behind it. Use a known rectangular alpha
            # fixture so the test point is deterministic, rather than relying
            # on a particular generated aircraft's internal transparent holes.
            overlap = page.evaluate('''async () => {
              const top=mkNode({type:'equip',icon:'cu:selectionAlpha',x:260,y:210,w:120,h:140,text:'',noBox:true});
              const back=mkNode({type:'rect',x:265,y:222,w:20,h:15,text:'',fill:'#d52525'});
              P().nodes=[back,top];clearSel();await JwSelectionBounds.ready();render();
              const p={x:270,y:225},r=svg.getBoundingClientRect();
              return {top:top.id,back:back.id,point:p,x:r.left+(p.x-view.x)*view.k,y:r.top+(p.y-view.y)*view.k,
                outside:!JwSelectionBounds.hit(top,p),inside:JwSelectionBounds.hit(back,p)};
            }''')
            assert overlap['outside'] and overlap['inside'], overlap
            page.mouse.click(overlap['x'], overlap['y'])
            assert page.evaluate('selectedNodes().map(n=>n.id)') == [overlap['back']], 'Transparent top icon stole the underlying visible node click'
            # Marquee tightly enclosing alpha selects an icon, even though its
            # persisted node rectangle extends well outside that marquee.
            marquee = page.evaluate('''() => {
              P().nodes=P().nodes.filter(n=>n.id===''' + json.dumps(overlap['top']) + ''');clearSel();render();
              const n=P().nodes[0],b=JwSelectionBounds.bounds(n),r=svg.getBoundingClientRect();
              return {id:n.id,x0:r.left+(b.x-3-view.x)*view.k,y0:r.top+(b.y-3-view.y)*view.k,
                x1:r.left+(b.x+b.w+3-view.x)*view.k,y1:r.top+(b.y+b.h+3-view.y)*view.k};
            }''')
            page.mouse.move(marquee['x0'], marquee['y0'])
            page.mouse.down()
            page.mouse.move(marquee['x1'], marquee['y1'], steps=6)
            page.mouse.up()
            assert page.evaluate('selectedNodes().map(n=>n.id)') == [marquee['id']], 'Core marquee still tests padded node rectangles'
            selected_export = page.evaluate('exportSVGString(P(),false).str')
            page.evaluate('clearSel();render()')
            assert page.evaluate('exportSVGString(P(),false).str') == selected_export, 'Selection overlay leaked into export'
            assert 'data-h=' not in selected_export
            page.screenshot(path=str(OUT / 'alpha-overlap-and-marquee.png'))
            assert not errors, errors
            (OUT / 'geometry.json').write_text(json.dumps({'fixtures': fixtures, 'geometry': geometry, 'controls': controls, 'resized': resized}, ensure_ascii=False, indent=2), encoding='utf-8')
            browser.close()
            print('selectionbounds_test PASS: real lib/country/ms/cu alpha, legacy serialization, rotated fixed-corner resize, actual grips, caption/overlap hits, marquee and export')
    finally:
        if server:
            server.shutdown()


if __name__ == '__main__':
    main()
