"""Real photo insertion UI, native exports and desktop canvas-drop regression."""
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
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
OUT = ROOT / '_work' / 'image-insert-test'


def image_size(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return struct.unpack('>II', data[16:24])
    assert data[:2] == b'\xff\xd8', 'Exported photo is not PNG/JPEG'
    i = 2
    while i < len(data):
        if data[i] != 255:
            i += 1
            continue
        while data[i] == 255:
            i += 1
        marker = data[i]
        i += 1
        if marker in [0xD8, 0xD9] or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[i:i + 2], 'big')
        if marker in [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF]:
            return (int.from_bytes(data[i + 5:i + 7], 'big'), int.from_bytes(data[i + 3:i + 5], 'big'))
        i += length
    raise AssertionError('JPEG has no frame dimensions')


def drop_file(page, fixture, *, desktop=False):
    return page.evaluate('''arg=>{
      const r=svg.getBoundingClientRect(),x=r.left+r.width*.60,y=r.top+r.height*.48;
      const bytes=Uint8Array.from(atob(arg.data),c=>c.charCodeAt(0));
      const file=new File([bytes],arg.name,{type:arg.mime});
      if(arg.desktop)Object.defineProperty(file,'path',{value:'/fixture/'+arg.name});
      const transfer=new DataTransfer();transfer.items.add(file);
      const event=new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:transfer,clientX:x,clientY:y});
      const point=clientToWorld(event.clientX,event.clientY);
      svg.dispatchEvent(event);
      return point;
    }''', {'name': fixture['path'].name, 'mime': fixture['mime'], 'data': fixture['data'], 'desktop': desktop})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = os.environ.get('JW_TEST_URL') or f'http://127.0.0.1:{server.server_port}/dist/offline.html'
    errors = []
    checks = []
    page = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or shutil.which('chromium'), args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1500, 'height': 1100}, accept_downloads=True)
            page.on('pageerror', lambda e: errors.append(e.stack or str(e)))
            # Technical fixtures: four color quadrants and fine grid lines, with no Pillow dependency.
            fixtures = []
            for name, width, height, mime in [('wide.jpg', 960, 480, 'image/jpeg'), ('tall.JPEG', 400, 800, 'image/jpeg'), ('square.jpg', 600, 600, 'image/jpeg'), ('wide.png', 720, 360, 'image/png')]:
                encoded = page.evaluate('''({w,h,mime})=>{const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
                  ['#ee3311','#22aa66','#2255dd','#e6bd22'].forEach((color,i)=>{x.fillStyle=color;x.fillRect(i%2*w/2,Math.floor(i/2)*h/2,w/2,h/2)});
                  x.strokeStyle='#ffffff';x.lineWidth=1;for(let i=8;i<w;i+=16){x.beginPath();x.moveTo(i,0);x.lineTo(i,h);x.stroke();}
                  return c.toDataURL(mime,.96).split(',')[1];}''', {'w': width, 'h': height, 'mime': mime})
                path = OUT / name
                path.write_bytes(base64.b64decode(encoded))
                assert image_size(path.read_bytes()) == (width, height)
                fixtures.append({'path': path, 'w': width, 'h': height, 'mime': mime, 'data': encoded})
            response = page.goto(url, wait_until='domcontentloaded', timeout=90000)
            assert response and response.ok
            page.wait_for_selector('#b-insert-image', timeout=90000)
            assert page.locator('#f-insert-image').count(), 'Build production with photo insertion first'
            baseline = page.evaluate('''()=>{
              document.querySelectorAll('#jw-home,#jw-webhist').forEach(e=>e.hidden=true);
              doc.name='图片插入回归';doc.custom={};doc.pages={root:{id:'root',name:'照片',noLegend:true,links:[],nodes:[
                mkNode({id:'keep-a',type:'rect',x:30,y:30,w:140,h:60,text:'保留图元A'}),mkNode({id:'keep-b',type:'rect',x:220,y:30,w:140,h:60,text:'保留图元B'})]}};
              cur='root';clearSel();Object.assign(view,{x:0,y:0,k:1});render();return JSON.stringify(P().nodes);
            }''')
            photos = []
            for index, fixture in enumerate(fixtures):
                with page.expect_file_chooser() as chooser:
                    page.click('#b-insert-image')
                chooser.value.set_files(str(fixture['path']))
                page.wait_for_function('count=>P().nodes.filter(n=>n.imageOnly).length===count', arg=index + 1)
                node = page.evaluate('''()=>{const n=selectedNodes()[0],L=nodeLayout(n),a=doc.custom[n.icon.slice(3)];return {id:n.id,w:n.w,h:n.h,text:n.text,noBox:n.noBox,imageOnly:n.imageOnly,icon:L.icon,label:L.text,asset:a};}''')
                assert node['imageOnly'] and node['noBox'] and node['text'] == '' and node['label'] is None, node
                assert min(node['w'], node['h']) > 140 and abs(node['w'] / node['h'] - fixture['w'] / fixture['h']) < 1e-6
                assert abs(node['icon']['w'] - node['w']) < .01 and abs(node['icon']['h'] - node['h']) < .01, node
                assert [node['asset']['width'], node['asset']['height']] == [fixture['w'], fixture['h']]
                assert base64.b64decode(node['asset']['uri'].split(',', 1)[1]) == fixture['path'].read_bytes()
                photos.append(node['id'])
                assert page.locator('#props h3').inner_text() == '图片'
                assert page.locator('#p-text,#p-type').count() == 0
                if index == 0:
                    page.click('#b-undo')
                    assert page.evaluate('P().nodes.filter(n=>n.imageOnly).length') == 0
                    assert page.evaluate('Object.keys(doc.custom).length') == 0
                    page.click('#b-redo')
                    page.locator('#world [data-id="' + node['id'] + '"] image').click()
                    page.fill('#p-rot', '30')
                    page.locator('[data-geo="w"]').fill('600')
                    page.locator('[data-geo="w"]').press('Enter')
                    assert float(page.locator('[data-geo="h"]').input_value()) == 300, 'Linked height field did not refresh'
                    before = page.evaluate('''id=>{const n=nodeById(id);return {w:n.w,h:n.h,anchor:rotPoint(n,n.x,n.y)}}''', node['id'])
                    corner = page.locator('[data-h="se"]').bounding_box()
                    assert corner
                    x, y = corner['x'] + corner['width'] / 2, corner['y'] + corner['height'] / 2
                    page.mouse.move(x, y);page.mouse.down();page.mouse.move(x + 45, y + 35, steps=6);page.mouse.up()
                    resized = page.evaluate('''id=>{const n=nodeById(id),L=nodeLayout(n);return {w:n.w,h:n.h,rot:n.rot,iw:L.icon.w,ih:L.icon.h,anchor:rotPoint(n,n.x,n.y)}}''', node['id'])
                    assert resized['w'] > before['w'] and abs(resized['w'] / resized['h'] - 2) < .001, (before, resized)
                    assert abs(resized['iw'] - resized['w']) < .01 and abs(resized['ih'] - resized['h']) < .01
                    assert math.hypot(resized['anchor']['x'] - before['anchor']['x'], resized['anchor']['y'] - before['anchor']['y']) < .1
                    assert resized['rot'] == 30
                    page.click('#props [data-layer="back"]')
                    assert page.evaluate('P().nodes[0].id') == node['id']
                    page.click('#props [data-layer="front"]')
                for key, value in [('x', [100, 650, 100, 500][index]), ('y', [150, 150, 500, 600][index]), ('w', [400, 200, 240, 320][index])]:
                    page.locator('[data-geo="' + key + '"]').fill(str(value))
                    page.locator('[data-geo="' + key + '"]').press('Enter')
                actual = page.evaluate('''id=>{const n=nodeById(id);return {w:n.w,h:n.h}}''', node['id'])
                assert abs(float(page.locator('[data-geo="w"]').input_value()) - actual['w']) < 1
                assert abs(float(page.locator('[data-geo="h"]').input_value()) - actual['h']) < 1
            assert page.evaluate('JSON.stringify(P().nodes.filter(n=>!n.imageOnly))') == baseline
            checks.append('JPG/JPEG/PNG actual picker, full uncapped photo layout, original bytes, rotation, proportional resize, layers, insertion undo/redo')
            sizes = page.evaluate('P().nodes.filter(n=>n.imageOnly).map(n=>[n.id,n.w,n.h])')
            page.click('#b-beauty')
            assert sorted(page.evaluate('P().nodes.filter(n=>n.imageOnly).map(n=>[n.id,n.w,n.h])')) == sorted(sizes), 'Beautification resized or distorted a photo'
            page.click('#b-undo')
            with page.expect_download(timeout=90000) as download:
                page.click('#b-save')
            project = OUT / 'photos.jingwei.json';download.value.save_as(project)
            saved = json.loads(project.read_text())
            assert len(saved['doc']['custom']) == 4 and all(a['uri'].startswith('data:image/') for a in saved['doc']['custom'].values())
            page.evaluate("doc.name='重开前';P().nodes=[];doc.custom={};clearSel();render()")
            page.locator('#f-open').set_input_files(str(project))
            page.wait_for_function("doc.name==='图片插入回归'&&P().nodes.filter(n=>n.imageOnly).length===4")
            assert page.evaluate('doc.name') == '图片插入回归'
            assert page.evaluate('JSON.stringify(P().nodes.filter(n=>!n.imageOnly))') == baseline
            assert page.evaluate('P().nodes.filter(n=>n.imageOnly).map(n=>[n.id,n.w,n.h])') == sizes
            checks.append('beautify keeps size/aspect; actual downloaded project reopens with embedded full-resolution resources')
            exports = {}
            for kind in ['svg', 'png', 'pptx', 'vsdx', 'drawio']:
                with page.expect_download(timeout=90000) as download:
                    page.click('#b-export');page.locator('#m-export [data-exp="' + kind + '"]').click()
                path = OUT / ('photos.' + kind);download.value.save_as(path);assert path.stat().st_size > 500
                exports[kind] = path
            svg = ET.fromstring(exports['svg'].read_text());ns = {'s': 'http://www.w3.org/2000/svg', 'p': 'http://schemas.openxmlformats.org/presentationml/2006/main', 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
            assert len(svg.findall('.//s:image', ns)) == 4
            assert any('rotate(30' in e.get('transform', '') for e in svg.iter())
            expected_sizes = {(f['w'], f['h']) for f in fixtures}
            for kind, folder in [('pptx', 'ppt/media/'), ('vsdx', 'visio/media/')]:
                with zipfile.ZipFile(exports[kind]) as archive:
                    media = [archive.read(name) for name in archive.namelist() if name.startswith(folder) and not name.endswith('/')]
                    assert expected_sizes <= {image_size(data) for data in media}, (kind, [image_size(data) for data in media])
                    if kind == 'pptx':
                        slide = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
                        assert len(slide.findall('.//p:pic', ns)) == 4
                        assert any(int(e.get('rot', '0')) == 30 * 60000 for e in slide.findall('.//p:pic/p:spPr/a:xfrm', ns))
            assert min(image_size(exports['png'].read_bytes())) > 500
            back = page.evaluate('''async xml=>{const d=await DrawIO.importText(xml);return {nodes:d.pages[0].nodes.filter(n=>n.imageOnly).map(n=>({w:n.w,h:n.h,rot:n.rot||0,text:n.text,noBox:n.noBox})),custom:d.custom}}''', exports['drawio'].read_text())
            assert len(back['nodes']) == 4 and all(n['noBox'] and n['text'] == '' for n in back['nodes'])
            assert any(n['rot'] == 30 for n in back['nodes'])
            assert {(round(n['w'], 3), round(n['h'], 3)) for n in back['nodes']} == {(round(n[1], 3), round(n[2], 3)) for n in sizes}
            checks.append('real SVG/PNG/PPTX/VSDX/drawio downloads, full-resolution native media, drawio imageOnly roundtrip')
            # Actual browser file drop, with a scaled/panned viewport and a nonempty project.
            page.evaluate('Object.assign(view,{x:-220,y:35,k:.65});render()')
            drop_point = drop_file(page, fixtures[0])
            page.wait_for_function('P().nodes.filter(n=>n.imageOnly).length===5')
            center = page.evaluate('''()=>{const n=selectedNodes()[0];return {x:n.x+n.w/2,y:n.y+n.h/2}}''')
            assert math.hypot(center['x'] - drop_point['x'], center['y'] - drop_point['y']) < .01, (drop_point, center)
            assert page.evaluate('doc.name') == '图片插入回归' and page.evaluate('JSON.stringify(P().nodes.filter(n=>!n.imageOnly))') == baseline
            page.screenshot(path=str(OUT / 'photo-canvas.png'))
            # Run the actual built desktop shell with a bridge fixture, including window capture drop.
            desk = browser.new_page(viewport={'width': 1500, 'height': 1100})
            desk.on('pageerror', lambda e: errors.append(e.stack or str(e)))
            desk.add_init_script('''window.__deskReads=0;window.__deskConfirms=0;window.jwDesk={
              on(){},title(){},win(){},winState:async()=>({max:false,full:false}),info:async()=>({version:'test',platform:'linux',arch:'x64'}),
              pending:async()=>[],recent:async()=>[],backupList:async()=>[],backupWrite:async()=>null,backupDrop:async()=>true,
              confirmClose:async()=>{window.__deskConfirms++;return 'discard'},read:async()=>{window.__deskReads++;throw new Error('Canvas drop must not open a file')},save:async()=>'/fixture/project.json'};''')
            desk_url = os.environ.get('JW_DESK_TEST_URL') or url.rsplit('/', 1)[0] + '/desk.html'
            response = desk.goto(desk_url, wait_until='domcontentloaded', timeout=90000);assert response and response.ok
            desk.wait_for_selector('#jw-go', timeout=90000);desk.click('#jw-go')
            desk.evaluate("doc.name='桌面保留工程';doc.pages={root:{id:'root',name:'保留',noLegend:true,links:[],nodes:[mkNode({id:'desk-keep',type:'rect',x:40,y:40,w:160,h:80,text:'保留'})]}};cur='root';checkpoint();Object.assign(view,{x:-80,y:-40,k:.8});render()")
            point = drop_file(desk, fixtures[1], desktop=True)
            desk.wait_for_function('P().nodes.some(n=>n.imageOnly)')
            result = desk.evaluate('''()=>{const n=P().nodes.find(n=>n.imageOnly);return {name:doc.name,count:P().nodes.length,keep:!!nodeById('desk-keep'),reads:__deskReads,confirms:__deskConfirms,x:n.x+n.w/2,y:n.y+n.h/2}}''')
            assert result['name'] == '桌面保留工程' and result['count'] == 2 and result['keep'] and result['reads'] == result['confirms'] == 0, result
            assert math.hypot(result['x'] - point['x'], result['y'] - point['y']) < .01, (point,result)
            desk.screenshot(path=str(OUT / 'desktop-photo-drop.png'));desk.close()
            checks.append('web and desktop captured file drops insert at transformed canvas position without replacing a dirty project')
            assert not errors, errors
            browser.close()
            (OUT / 'report.json').write_text(json.dumps({'passed': True, 'pageErrors': errors, 'checks': checks}, ensure_ascii=False, indent=2))
            print('PASS image insertion production')
    except Exception as error:
        (OUT / 'report.json').write_text(json.dumps({'passed': False, 'error': str(error), 'pageErrors': errors, 'completed': checks}, ensure_ascii=False, indent=2))
        raise
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
