"""Configure attached payloads through production UI; preserve world geometry in exports."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import copy
import json
import math
import os
from pathlib import Path
import shutil
import struct
import threading
import xml.etree.ElementTree as ET
import zipfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_work' / 'payloads-test'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = os.environ.get('JW_TEST_URL') or f'http://127.0.0.1:{server.server_port}/dist/offline.html'
    errors, checks = [], []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or shutil.which('chromium'), args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1500, 'height': 1150}, accept_downloads=True)
            page.on('pageerror', lambda e: errors.append(e.stack or str(e)))
            response = page.goto(url, wait_until='domcontentloaded', timeout=90000)
            assert response and response.ok
            page.wait_for_function('!!window.Payloads && !!window.PayloadPresets', timeout=90000)

            def rows(nid):
                return page.evaluate('id=>JSON.parse(JSON.stringify(nodeById(id).payloads||[]))', nid)

            def row(nid, pid):
                return next(p for p in rows(nid) if p['id'] == pid)

            selection_clicks = 0

            def choose(nid):
                nonlocal selection_clicks
                # Camera positioning is test setup; node selection and every payload edit use UI.
                page.evaluate('''id=>{const n=nodeById(id);Object.assign(view,{x:n.x-260,y:n.y-180,k:1});render()}''', nid)
                target = page.locator('#world [data-id="' + nid + '"]')
                box = target.bounding_box()
                fraction = .28 if selection_clicks % 2 else .72
                selection_clicks += 1
                target.click(position={'x': box['width'] * fraction, 'y': box['height'] * .35})

            def open_panel(nid, pid=None):
                if page.locator('#payloads-dialog').count() and page.locator('#payloads-dialog').is_visible():
                    page.click('#payload-close')
                choose(nid)
                page.click('#p-payloads')
                page.wait_for_selector('#payloads-dialog:visible')
                if pid:
                    page.locator('[data-payload-select="' + pid + '"]').click()

            def close_panel():
                page.click('#payload-close')
                page.wait_for_selector('#payloads-dialog', state='hidden')

            def field(name, value):
                locator = page.locator('#payload-' + name)
                if locator.evaluate('(e)=>e.tagName') == 'SELECT':
                    locator.select_option(str(value))
                elif name == 'color':
                    locator.evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("change",{bubbles:true}))}', value)
                else:
                    locator.fill(str(value))
                    locator.press('Tab')

            def preset(nid, kind):
                defs = page.evaluate('id=>PayloadPresets.forNode(nodeById(id)).map(p=>({id:p.presetId||p.presetKey||p.id,kind:p.kind}))', nid)
                key = next(p['id'] for p in defs if p['kind'] == kind)
                page.locator('[data-payload-preset="' + key + '"]').check()
                matches = [p for p in rows(nid) if p.get('presetId', p.get('presetKey')) == key]
                assert len(matches) == 1, (key, matches)
                page.locator('[data-payload-select="' + matches[0]['id'] + '"]').click()
                return key, matches[0]['id']

            def effect(nid, pid):
                return page.locator('#world [data-platform-id="' + nid + '"][data-payload-id="' + pid + '"]')

            def origin(nid, pid):
                return effect(nid, pid).evaluate('(e)=>({x:+e.dataset.originWorldX,y:+e.dataset.originWorldY,direction:+e.dataset.worldDirection})')

            def mode_checks(nid, pid, mode):
                group = effect(nid, pid)
                assert group.count() == 1
                shape = group.locator('[data-fov]')
                assert shape.count() == 1 and group.get_attribute('data-sensor-mode') == mode
                dash = shape.get_attribute('stroke-dasharray') or ''
                arrows = group.locator('[data-flow-arrow]')
                if mode in ['active', 'emitter', 'passive']:
                    assert (dash not in ['', 'none', '0']) == (mode == 'passive')
                    assert arrows.count() == 3
                    for data in arrows.evaluate_all('es=>es.map(e=>({...e.dataset}))'):
                        dot = ((float(data['x2']) - float(data['x1'])) * (float(data['x1']) - float(data['originWorldX'])) +
                               (float(data['y2']) - float(data['y1'])) * (float(data['y1']) - float(data['originWorldY'])))
                        assert dot < 0 if mode == 'passive' else dot > 0
                        assert data['flow'] == ('in' if mode == 'passive' else 'out')
                else:
                    assert arrows.count() == 0

            def download(kind, stem):
                with page.expect_download(timeout=90000) as event:
                    page.click('#b-export')
                    page.locator('#m-export [data-exp="' + kind + '"]').click()
                path = OUT / (stem + '.' + kind)
                event.value.save_as(path)
                assert path.stat().st_size > 100
                return path

            base = page.evaluate('JSON.parse(projectJSON())')
            base['doc']['name'] = '旧载荷兼容示意'
            base['doc']['custom'] = {}
            base['doc']['pages'] = {'root': {'id': 'root', 'name': '总图', 'noLegend': True, 'links': [], 'nodes': [
                {'id': 'old-' + key, 'type': 'equip', 'icon': 'lib:' + key, 'x': 80 + i * 300, 'y': 100, 'w': 180, 'h': 180, 'text': '虚构平台' + str(i)}
                for i, key in enumerate(['uav_recon_eo', 'usv', 'destroyer'])]}}
            page.locator('#f-open').set_input_files({'name': 'legacy.json', 'mimeType': 'application/json', 'buffer': json.dumps(base, ensure_ascii=False).encode()})
            page.wait_for_function("doc.name==='旧载荷兼容示意'")
            before = page.evaluate('({geometry:P().nodes.map(n=>[n.id,n.x,n.y,n.w,n.h]),box:contentBBox(P())})')
            for nid in ['old-uav_recon_eo', 'old-usv', 'old-destroyer']:
                open_panel(nid)
                assert page.locator('#payload-presets [data-payload-preset]').count() >= 2
                assert all(not value for value in page.locator('[data-payload-preset]').evaluate_all('es=>es.map(e=>e.checked)'))
                close_panel()
            assert page.evaluate('({geometry:P().nodes.map(n=>[n.id,n.x,n.y,n.w,n.h]),box:contentBBox(P())})') == before
            assert page.evaluate('Payloads.bounds(P())===null && P().nodes.every(n=>!n.payloads||!n.payloads.length)')
            checks.append('legacy projects and opening configuration do not auto-enable ranges or alter layout')

            base['doc']['name'] = '载荷绘图回归'
            base['doc']['pages']['root']['nodes'] = []
            page.locator('#f-open').set_input_files({'name': 'empty.json', 'mimeType': 'application/json', 'buffer': json.dumps(base, ensure_ascii=False).encode()})
            page.wait_for_function("doc.name==='载荷绘图回归' && P().nodes.length===0")
            nodes = {}
            for key, x, y in [('uav_recon_eo', 100, 120), ('usv', 600, 120), ('destroyer', 350, 650)]:
                page.select_option('#pal-appearance', 'cn')
                page.fill('#pal-q', key)
                page.locator('#palette [data-add*="lib:' + key + '"]').first.click()
                nid = page.evaluate('selectedNodes()[0].id')
                nodes[key] = nid
                for axis, value in [('x', x), ('y', y), ('w', 200), ('h', 200)]:
                    control = page.locator('#props [data-geo="' + axis + '"]')
                    control.fill(str(value));control.press('Tab')
                assert not rows(nid)
            eo, usv, destroyer = nodes['uav_recon_eo'], nodes['usv'], nodes['destroyer']
            open_panel(eo)
            eo_key, a = preset(eo, 'eo')
            for name, value in [('name', '虚构光电A'), ('direction', 45), ('sweep', 75), ('range', 130), ('color', '#d77c25')]:
                field(name, value)
            modified = row(eo, a)
            toggle = page.locator('[data-payload-preset="' + eo_key + '"]')
            toggle.uncheck();assert row(eo, a)['enabled'] is False
            toggle.check();toggle.check();assert row(eo, a) == modified and len(rows(eo)) == 1
            page.click('#payload-add')
            b = next(p['id'] for p in rows(eo) if p['id'] != a)
            for name, value in [('kind', 'eo'), ('name', '虚构光电B'), ('direction', 215), ('sweep', 95), ('range', 170), ('line-style', 'dashDot')]:
                field(name, value)
            assert row(eo, a) == modified and row(eo, b)['name'] != row(eo, a)['name']
            close_panel()
            assert effect(eo, a).locator('[data-fov]').get_attribute('stroke-dasharray') != effect(eo, b).locator('[data-fov]').get_attribute('stroke-dasharray')
            mode_checks(eo, a, 'passive');mode_checks(eo, b, 'passive')
            checks.append('real preset checkbox retains edits on off/on; multiple same-kind custom payloads have separate names, IDs and styles')

            old_origin, independent = origin(eo, a), rows(eo)
            choose(eo)
            page.fill('#p-rot', '90');page.locator('#p-rot').press('Tab')
            new_origin = origin(eo, a)
            assert rows(eo) == independent and math.hypot(new_origin['x'] - old_origin['x'], new_origin['y'] - old_origin['y']) > 5
            assert new_origin['direction'] == old_origin['direction'] == 45
            origins = {p['id']: origin(eo, p['id']) for p in rows(eo)}
            old_node = page.evaluate('id=>({x:nodeById(id).x,y:nodeById(id).y})', eo)
            position = page.evaluate('''id=>{const n=nodeById(id),r=svg.getBoundingClientRect(),p=rotPoint(n,n.x+n.w*.35,n.y+n.h*.42);return {x:r.left+(p.x-view.x)*view.k,y:r.top+(p.y-view.y)*view.k}}''', eo)
            page.keyboard.down('Alt');page.mouse.move(position['x'], position['y']);page.mouse.down();page.mouse.move(position['x'] + 36, position['y'] + 28, steps=7);page.mouse.up();page.keyboard.up('Alt')
            moved = page.evaluate('id=>({x:nodeById(id).x,y:nodeById(id).y})', eo)
            dx, dy = moved['x'] - old_node['x'], moved['y'] - old_node['y']
            assert math.hypot(dx, dy) > 10
            for p in rows(eo):
                now, old = origin(eo, p['id']), origins[p['id']]
                assert abs(now['x'] - old['x'] - dx) < 1e-4 and abs(now['y'] - old['y'] - dy) < 1e-4
                assert now['direction'] == old['direction']
            assert rows(eo) == independent
            checks.append('platform rotation moves normalized mounts without changing payload world angles; dragging translates every attached effect equally')

            choose(eo)
            page.keyboard.press('Control+c');page.keyboard.press('Control+v')
            page.wait_for_function('P().nodes.length===4')
            copied = page.evaluate('selectedNodes()[0].id')
            assert copied != eo and rows(copied) == independent
            open_panel(copied, a)
            field('name', '复制平台独立光电');field('range', 155);field('mount-x', 15)
            assert rows(eo) == independent and row(copied, a)['mount']['x'] == .15
            close_panel();page.click('#p-del')
            assert page.evaluate('P().nodes.length') == 3 and rows(eo) == independent
            checks.append('copy/paste platform payload arrays and nested mounts do not cross-edit the source')

            open_panel(usv)
            _, decoy = preset(usv, 'emDecoy')
            field('name', '虚构模拟载荷')
            close_panel()
            ghost = effect(usv, decoy).locator('[data-simulated-target="surfaceShip"]')
            assert ghost.count() == 1 and '模拟' in ghost.text_content()
            assert ghost.locator('image').count() == 1 and float(ghost.locator('image').get_attribute('opacity')) < 1
            assert page.locator('#world [data-id="' + usv + '"]').count() == 1
            mode_checks(usv, decoy, 'emitter')
            original_ghost_width = float(ghost.locator('rect').get_attribute('width'))
            actual_platform = page.evaluate('id=>{const n=nodeById(id);return[n.x,n.y,n.w,n.h,n.rot||0]}', usv)
            original_payload = row(usv, decoy)
            open_panel(usv, decoy);field('overlay-scale', 200);close_panel()
            assert row(usv, decoy)['overlayScale'] == 2
            assert abs(float(effect(usv, decoy).locator('[data-simulated-target] rect').get_attribute('width')) - original_ghost_width * 2) < 1e-5
            page.click('#b-undo');assert row(usv, decoy)['overlayScale'] == 1
            page.click('#b-redo');assert row(usv, decoy)['overlayScale'] == 2
            open_panel(usv, decoy);field('overlay-name', '虚构模拟身份A')
            page.click('#payload-overlay-larger')
            assert row(usv, decoy)['overlayScale'] > 2
            page.click('#payload-overlay-smaller');field('overlay-scale', 200)
            assert page.evaluate('id=>{const n=nodeById(id);return[n.x,n.y,n.w,n.h,n.rot||0]}', usv) == actual_platform
            assert all(row(usv, decoy)[key] == original_payload[key] for key in ['range', 'direction', 'mount'])
            page.click('#payload-add')
            decoy_b = next(p['id'] for p in rows(usv) if p['id'] != decoy)
            for name, value in [('name', '虚构模拟载荷B'), ('overlay-scale', 80), ('overlay-name', '虚构模拟身份B'), ('range', 90), ('direction', 145)]:
                field(name, value)
            assert row(usv, decoy)['overlayScale'] == 2 and row(usv, decoy_b)['overlayScale'] == .8
            close_panel()
            assert '虚构模拟身份A' in effect(usv, decoy).text_content() and '虚构模拟身份B' in effect(usv, decoy_b).text_content()
            # Actual transformed ghost geometry, including its label, must fit export bounds.
            assert page.evaluate('''id=>{const b=Payloads.bounds({nodes:[nodeById(id)]});return Array.from(world.querySelectorAll('[data-platform-id="'+id+'"] [data-simulated-target]')).every(g=>{
              const r=g.getBBox(),m=world.getCTM().inverse().multiply(g.getCTM());return [[r.x,r.y],[r.x+r.width,r.y],[r.x,r.y+r.height],[r.x+r.width,r.y+r.height]].every(([x,y])=>{const p=new DOMPoint(x,y).matrixTransform(m);return p.x>=b.x-.01&&p.y>=b.y-.01&&p.x<=b.x+b.w+.01&&p.y<=b.y+b.h+.01})})}''', usv)
            checks.append('emitter identity name/scale and +/- controls resize only the ghost; undo/redo, two-emitter isolation and ghost fit bounds')
            open_panel(usv, decoy);page.uncheck('#payload-show-overlay');close_panel()
            assert effect(usv, decoy).locator('[data-simulated-target]').count() == 0
            open_panel(usv, decoy);page.check('#payload-show-overlay');page.uncheck('#payload-show-range');close_panel()
            assert effect(usv, decoy).locator('[data-simulated-target]').count() == 1 and effect(usv, decoy).locator('[data-fov]').count() == 0
            open_panel(usv, decoy);page.check('#payload-show-range')
            for kind, mode in [('activeSonar', 'active'), ('passiveSonar', 'passive')]:
                _, pid = preset(usv, kind)
                for sweep in [360, 80]:
                    field('sweep', sweep)
                    if sweep != 360:field('direction', 110)
                    close_panel();mode_checks(usv, pid, mode)
                    assert effect(usv, pid).locator('[data-fov]').evaluate('(e)=>e.tagName') == ('circle' if sweep == 360 else 'path')
                    open_panel(usv, pid)
            close_panel()
            assert rows(eo) == independent
            checks.append('USV emitter ghost is marked simulated and independently switchable; active/passive sonar circle and sector arrows/strokes are correct')

            open_panel(destroyer)
            for index, kind in enumerate(['mainGun', 'secondaryGun', 'hpm', 'laser', 'loiteringMunition']):
                key, pid = preset(destroyer, kind)
                for name, value in [('name', '虚构手段' + str(index + 1)), ('range', 80 + index * 25), ('direction', index * 55), ('sweep', 360 if index == 0 else 95)]:
                    field(name, value)
                others = [p for p in rows(destroyer) if p['id'] != pid]
                page.locator('[data-payload-preset="' + key + '"]').uncheck()
                assert [p for p in rows(destroyer) if p['id'] != pid] == others
                page.locator('[data-payload-preset="' + key + '"]').check()
            close_panel()
            assert len(rows(destroyer)) == 5 and rows(eo) == independent
            for p in rows(destroyer):
                assert effect(destroyer, p['id']).locator('[data-flow-arrow]').count() == 0
            choose(eo)
            page.click('#props [data-layer="back"]');assert page.evaluate('P().nodes[0].id') == eo
            assert rows(eo) == independent and all(effect(eo, p['id']).count() == 1 for p in rows(eo))
            page.click('#props [data-layer="front"]');assert page.evaluate('P().nodes[P().nodes.length-1].id') == eo
            checks.append('five weapon kinds keep separate toggles/angles/radii without detection labels; nodes and layers retain their attached configuration')

            open_panel(eo, a);previous = row(eo, a)['range'];field('range', 333);close_panel()
            page.click('#b-undo');assert row(eo, a)['range'] == previous
            page.click('#b-redo');assert row(eo, a)['range'] == 333
            expected = page.evaluate('P().nodes.map(n=>({id:n.id,payloads:n.payloads||[]}))')
            with page.expect_download(timeout=90000) as event:
                page.click('#b-save')
            project = OUT / 'payloads.jingwei.json';event.value.save_as(project)
            saved = json.loads(project.read_text());assert any(n.get('payloads') for n in saved['doc']['pages']['root']['nodes'])
            page.evaluate("doc.name='重开前';P().nodes=[];clearSel();render()")
            page.locator('#f-open').set_input_files(str(project))
            page.wait_for_function("doc.name==='载荷绘图回归'&&P().nodes.length===3")
            assert page.evaluate('P().nodes.map(n=>({id:n.id,payloads:n.payloads||[]}))') == expected
            checks.append('one-change undo/redo and actual downloaded project reopen preserve all payloads')

            files = {kind: download(kind, 'payloads') for kind in ['svg', 'png', 'pptx', 'vsdx', 'drawio']}
            svg = ET.fromstring(files['svg'].read_text())
            assert len([e for e in svg.iter() if e.get('data-payload-id')]) == sum(len(n['payloads']) for n in expected)
            effect_box = page.evaluate('payloadEffectsSVG(P()).box')
            expected_bitmap = (round(effect_box['w'] * min(1, 4096 / max(effect_box['w'], effect_box['h']))), round(effect_box['h'] * min(1, 4096 / max(effect_box['w'], effect_box['h']))))
            with zipfile.ZipFile(files['pptx']) as archive:
                sizes = [struct.unpack('>II', archive.read(name)[16:24]) for name in archive.namelist() if name.startswith('ppt/media/') and archive.read(name).startswith(b'\x89PNG')]
                assert expected_bitmap in sizes, (expected_bitmap, sizes)
            with zipfile.ZipFile(files['vsdx']) as archive:
                names = [n for n in archive.namelist() if n.startswith('visio/media/payload-effects-')]
                assert names and struct.unpack('>II', archive.read(names[0])[16:24]) == expected_bitmap
            xml = files['drawio'].read_text();tree = ET.fromstring(xml)
            assert tree.find('.//UserObject[@ht_part="payload-effects"]') is not None
            back = page.evaluate('''async xml=>{const d=await DrawIO.importText(xml);return d.pages[0].nodes.map(n=>({icon:n.icon,rot:n.rot||0,payloads:n.payloads||[]}))}''', xml)
            original = page.evaluate('P().nodes.map(n=>({icon:n.icon,rot:n.rot||0,payloads:n.payloads||[]}))')
            assert sorted(back, key=lambda n: n['icon']) == sorted(original, key=lambda n: n['icon'])
            page.screenshot(path=str(OUT / 'payload-canvas.png'))
            checks.append('SVG/PNG/PPTX/VSDX/drawio show effects; native packages contain bounded effect bitmaps; drawio restores attached editable payload arrays')

            # A legacy automatic grid must not multiply world extent into an enormous bitmap/line count.
            page.click('#b-bg');page.select_option('#cbg-scope', 'auto');page.check('#cbg-grid')
            page.locator('#cbg-dlg button').filter(has_text='应用并锁定').click();page.click('#cbg-x')
            open_panel(eo, a);field('sweep', 360);field('range', 100000);page.click('#payload-fit')
            assert row(eo, a)['range'] == 100000 and page.evaluate('!P().canvasBg.region')
            contained = page.evaluate('''()=>{const b=Payloads.bounds({nodes:[nodeById(''' + json.dumps(eo) + ''')]}),r=svg.getBoundingClientRect();return b.x>=view.x-1e-3&&b.y>=view.y-1e-3&&b.x+b.w<=view.x+r.width/view.k+1e-3&&b.y+b.h<=view.y+r.height/view.k+1e-3}''')
            assert contained
            far_svg = download('svg', 'far-range');far_png = download('png', 'far-range');download('pptx', 'far-range');download('vsdx', 'far-range');far_dio = download('drawio', 'far-range')
            width, height = struct.unpack('>II', far_png.read_bytes()[16:24])
            assert 0 < width <= 8192 and 0 < height <= 8192 and width * height <= 32 * 1024 * 1024
            far = ET.fromstring(far_svg.read_text());viewbox = list(map(float, far.get('viewBox').split()))
            mount = page.evaluate('arg=>Payloads.mount(nodeById(arg.n),nodeById(arg.n).payloads.find(p=>p.id===arg.p))', {'n': eo, 'p': a})
            assert viewbox[0] <= mount['x'] - 100000 and viewbox[1] <= mount['y'] - 100000
            assert viewbox[0] + viewbox[2] >= mount['x'] + 100000 and viewbox[1] + viewbox[3] >= mount['y'] + 100000
            assert len([e for e in far.iter() if e.tag.endswith('line')]) < 10000
            assert row(eo, a)['range'] == 100000
            far_back = page.evaluate('''async xml=>{const d=await DrawIO.importText(xml);return d.pages[0].nodes.flatMap(n=>n.payloads||[]).filter(p=>p.range===100000).length}''', far_dio.read_text())
            assert far_back == 1
            open_panel(eo, a);field('range', 1e9);page.click('#payload-fit')
            assert row(eo, a)['range'] == 1e9 and page.evaluate('Payloads.bounds(P()).w>1e9')
            billion = download('png', 'billion-range');bw, bh = struct.unpack('>II', billion.read_bytes()[16:24])
            assert 0 < bw <= 8192 and 0 < bh <= 8192 and bw * bh <= 32 * 1024 * 1024
            assert row(eo, a)['range'] == 1e9
            checks.append('100000 and 1e9 distances fit/export in full world extent with old auto grid; PNG edge/area cap affects pixels only')
            assert not errors, errors
            browser.close()
            (OUT / 'report.json').write_text(json.dumps({'passed': True, 'pageErrors': errors, 'checks': checks}, ensure_ascii=False, indent=2))
            print('PASS payload production UI and exports')
    except Exception as error:
        (OUT / 'report.json').write_text(json.dumps({'passed': False, 'error': str(error), 'pageErrors': errors, 'completed': checks}, ensure_ascii=False, indent=2))
        raise
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
