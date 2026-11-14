"""Real-browser icon caption layout, independent dragging and export regression."""
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
import os
from pathlib import Path
import shutil
import struct
import xml.etree.ElementTree as ET
import zipfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_work' / 'iconlabels-test'


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
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or shutil.which('chromium'),
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(url, timeout=90000)
        page.wait_for_function('typeof nodeLayout === "function"')
        assert page.evaluate('!!window.JwIconLabels'), 'Module must be included in the production build'
        node_id = page.evaluate('''() => {
          doc.pages={root:{id:'root',name:'Icon captions',nodes:[],links:[],noLegend:true}};cur='root';
          doc.custom.captionTest={name:'test',aspect:1,uri:svgUri('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect x="20" y="20" width="60" height="50" fill="#1759cf"/></svg>')};
          const n=mkNode({type:'equip',x:200,y:150,w:120,h:140,text:'caption <test>',icon:'cu:captionTest',noBox:true});
          P().nodes.push(n);selectNodes([n.id]);undoS=[];redoS=[];render();
          window.labelLegacy=JSON.stringify(nodeLayout(n)); return n.id;
        }''')
        assert page.locator('[data-icon-label]').count() == 1, 'Rebuild offline.html with the core label hook'
        # No opt-in: layout is stable, and the ordinary node drag remains available.
        assert page.evaluate('JSON.stringify(nodeLayout(selectedNodes()[0]))===window.labelLegacy')
        assert page.locator('#p-iconLabelPlacement button.on').count() == 0
        page.click('[data-shared="iconLabelPlacement"] button[data-v="tight"]')
        page.evaluate('JwIconLabels.ready(P())')
        layout = page.evaluate('''() => {
          render();const n=selectedNodes()[0],L=nodeLayout(n),v=JwIconLabels.visualBox(L.icon);
          return {gap:L.text.box[1]-v.bottom,legacy:window.labelLegacy,now:JSON.stringify(L),x:n.x,y:n.y};
        }''')
        assert abs(layout['gap']) < .01 and layout['legacy'] != layout['now'], layout
        page.evaluate('(id)=>{undo();selectNodes([id]);render();}', node_id)
        assert page.evaluate('JSON.stringify(nodeLayout(selectedNodes()[0]))===window.labelLegacy')
        page.evaluate('(id)=>{redo();selectNodes([id]);render();}', node_id)
        page.fill('#p-iconLabelGap', '6')
        page.locator('#p-iconLabelGap').blur()
        assert page.evaluate('selectedNodes()[0].iconLabelGap') == 6
        page.check('#p-iconLabelDrag')

        def center():
            return page.evaluate('''() => {
              const n=selectedNodes()[0],t=nodeLayout(n).text,p=rotPoint(n,t.x,t.cy),r=svg.getBoundingClientRect();
              return {x:r.left+(p.x-view.x)*view.k,y:r.top+(p.y-view.y)*view.k};
            }''')

        # Move the caption well outside the original node. The icon itself must stay fixed.
        start = center()
        initial_scale = page.evaluate('view.k')
        page.mouse.move(start['x'], start['y'])
        page.mouse.down()
        page.mouse.move(start['x'] + 260 * initial_scale, start['y'] + 90 * initial_scale, steps=8)
        page.mouse.up()
        moved = page.evaluate('''() => {
          const n=selectedNodes()[0];return {x:n.x,y:n.y,dx:n.iconLabelDx,dy:n.iconLabelDy,b:contentBBox(),
            svg:exportSVGString(P(),false),label:nodeLayout(n).text};
        }''')
        assert (moved['x'], moved['y']) == (layout['x'], layout['y']), moved
        assert abs(moved['dx'] - 260) < 1 and abs(moved['dy'] - 90) < 1, moved
        assert moved['b']['x'] + moved['b']['w'] >= moved['label']['x'], moved
        assert '&lt;test&gt;' in moved['svg']['str'], 'caption is escaped in SVG'
        page.evaluate('(id)=>{undo();selectNodes([id]);render();}', node_id)
        assert page.evaluate('!(selectedNodes()[0].iconLabelDx || selectedNodes()[0].iconLabelDy)')
        page.evaluate('(id)=>{redo();selectNodes([id]);render();}', node_id)
        # Click outside the old node: native g[data-id] hit handling still selects the node.
        page.uncheck('#p-iconLabelDrag')
        page.evaluate('clearSel();render()')
        hit = page.locator('[data-icon-label]').bounding_box()
        page.mouse.click(hit['x'] + hit['width'] / 2, hit['y'] + hit['height'] / 2)
        assert page.evaluate('selectedNodes()[0].id') == node_id
        # Save/open and draw.io round trips preserve the optional fields.
        page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
        assert page.evaluate('(id)=>nodeById(id).iconLabelDx', node_id) == moved['dx']
        back = page.evaluate('''async () => {
          const xml=DrawIO.exportString([P()]),o=await DrawIO.importText(xml);
          return o.pages[0].nodes.map(n=>({gap:n.iconLabelGap,dx:n.iconLabelDx,dy:n.iconLabelDy}));
        }''')
        assert back == [{'gap': 6, 'dx': moved['dx'], 'dy': moved['dy']}], back
        # Rotated dragging uses inverse node rotation, not the screen-space delta.
        page.evaluate('''(id)=>{const n=nodeById(id);n.rot=90;n.iconLabelDx=0;n.iconLabelDy=0;
          selectNodes([id]);render();fit();render();}''', node_id)
        page.check('#p-iconLabelDrag')
        scale = page.evaluate('view.k')
        start = center()
        page.mouse.move(start['x'], start['y'])
        page.mouse.down()
        page.mouse.move(start['x'] + 50 * scale, start['y'] + 20 * scale, steps=6)
        page.mouse.up()
        rotated = page.evaluate('({dx:selectedNodes()[0].iconLabelDx,dy:selectedNodes()[0].iconLabelDy})')
        assert abs(rotated['dx'] - 20) < .2 and abs(rotated['dy'] + 50) < .2, rotated
        start = center()
        before = page.evaluate('snapshot()')
        page.mouse.move(start['x'], start['y'])
        page.mouse.down()
        page.mouse.move(start['x'] + 40, start['y'] + 30, steps=4)
        page.keyboard.press('Escape')
        page.mouse.up()
        assert page.evaluate('snapshot()') == before, 'Escape cancels only the current label drag'
        # Export all actual formats with a caption beyond the node bounds, including rotation.
        page.evaluate('''() => {const n=selectedNodes()[0];n.iconLabelDx=250;n.iconLabelDy=130;render();}''')
        expected = page.evaluate('''async () => {await JwIconLabels.ready();return exportSVGString(P(),false);}''')
        export_geometry = page.evaluate('''() => {const n=selectedNodes()[0],b=nodeLayout(n).text.box;
          return {bounds:contentBBox(),center:rotPoint(n,b[0]+b[2]/2,b[1]+b[3]/2)};}''')
        (OUT / 'iconlabels.svg').write_text(expected['str'], encoding='utf-8')
        for ext, call in [('png', 'exportPNG(1,false)'), ('pptx', 'exportPPTX()'), ('vsdx', 'exportVSDX()')]:
            with page.expect_download(timeout=90000) as download:
                page.evaluate('async () => { await ' + call + '; }')
            download.value.save_as(OUT / ('iconlabels.' + ext))
        width, height = struct.unpack('>II', (OUT / 'iconlabels.png').read_bytes()[16:24])
        assert abs(width - expected['w']) <= 1 and abs(height - expected['h']) <= 1
        with zipfile.ZipFile(OUT / 'iconlabels.pptx') as z:
            xml = z.read('ppt/slides/slide1.xml').decode()
            assert 'caption &lt;test&gt;' in xml and 'rot="5400000"' in xml
            tree = ET.fromstring(xml)
            ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
            shape = next(sp for sp in tree.findall('.//p:sp', ns) if ''.join(t.text or '' for t in sp.findall('.//a:t', ns)) == 'caption <test>')
            transform = shape.find('.//a:xfrm', ns)
            off, size = transform.find('a:off', ns), transform.find('a:ext', ns)
            b, c = export_geometry['bounds'], export_geometry['center']
            factor = min((13.333-.5)/(b['w']+32),(7.5-.4)/(b['h']+32))
            ox, oy = (13.333-(b['w']+32)*factor)/2,(7.5-(b['h']+32)*factor)/2
            for axis, dim, origin in [('x','cx',ox),('y','cy',oy)]:
                actual = (int(off.get(axis))+int(size.get(dim))/2)/914400
                assert abs(actual-(origin+(c[axis]-b[axis]+16)*factor)) < .002
        with zipfile.ZipFile(OUT / 'iconlabels.vsdx') as z:
            xml = z.read('visio/pages/page1.xml').decode()
            assert 'caption &lt;test&gt;' in xml and 'Angle' in xml
            tree = ET.fromstring(xml)
            ns = {'v':'http://schemas.microsoft.com/office/visio/2012/main'}
            shape = next(sp for sp in tree.findall('.//v:Shape', ns) if sp.find('v:Text', ns) is not None and ''.join(sp.find('v:Text', ns).itertext()) == 'caption <test>')
            cells = {e.get('N'):float(e.get('V')) for e in shape.findall('v:Cell', ns) if e.get('N') in ['PinX','PinY']}
            assert abs(cells['PinX']-(c['x']-b['x']+20)/96) < .0001
            assert abs(cells['PinY']-(b['h']+20-c['y']+b['y'])/96) < .0001
        page.evaluate('fit();render()')
        page.screenshot(path=str(OUT / 'iconlabels-dragged-browser.png'))
        # Reset removes all optional placement fields, then original legacy geometry returns.
        page.click('[data-shared="iconLabelPlacement"] button[data-v="reset"]')
        assert page.evaluate('''() => {const n=selectedNodes()[0];return ['iconLabelGap','iconLabelDx','iconLabelDy'].every(k=>!Object.prototype.hasOwnProperty.call(n,k));}''')
        assert page.locator('#p-iconLabelPlacement button.on').count() == 0
        page.uncheck('#p-iconLabelDrag')
        page.evaluate('selectedNodes()[0].rot=0;render();fit();render()')
        start = center()
        original_x = page.evaluate('selectedNodes()[0].x')
        scale = page.evaluate('view.k')
        page.mouse.move(start['x'], start['y'])
        page.mouse.down()
        page.mouse.move(start['x'] + 40 * scale, start['y'], steps=5)
        page.mouse.up()
        assert abs(page.evaluate('selectedNodes()[0].x') - original_x) > 20, 'normal mode keeps node dragging'
        assert page.evaluate("['lib:x','ms:x','cu:x'].every(icon=>JwIconLabels.eligible(mkNode({type:'equip',icon})))")
        page.screenshot(path=str(OUT / 'iconlabels-browser.png'))
        families = page.evaluate('''async () => {
          const key=(ICONS.find(i=>i.key.indexOf('uav_')===0)||ICONS[0]).key;
          P().nodes=['lib:'+key,'ms:SFGPUCI----K---','cu:captionTest'].map((icon,i)=>mkNode({
            type:'equip',icon,text:['装备图标','军标','自定义图标'][i],x:100+i*190,y:100,w:140,h:150,
            iconLabelGap:0,noBox:true}));
          clearSel();await JwIconLabels.ready();render();fit();render();
          return P().nodes.map(n=>{const L=nodeLayout(n);return {icon:n.icon,ok:!!(L.icon&&L.text),
            gap:L.icon&&L.text?L.text.box[1]-JwIconLabels.visualBox(L.icon).bottom:null};});
        }''')
        assert all(row['ok'] and abs(row['gap']) < .01 for row in families), families
        page.screenshot(path=str(OUT / 'iconlabels-three-families.png'))
        assert not errors, errors
        browser.close()
        if server:
            server.shutdown()
        print(json.dumps({'ok': True, 'formats': ['SVG', 'PNG', 'PPTX', 'VSDX', 'draw.io'],
                          'rotatedDrag': rotated, 'png': [width, height], 'evidence': str(OUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
