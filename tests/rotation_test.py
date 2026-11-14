"""Rotate ordinary nodes and preserve geometry through the real export writers."""
import math
import os
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
import zipfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_work' / 'rotation-test'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri()), timeout=90000)
        page.wait_for_function('typeof canRotate === "function" && typeof DrawIO !== "undefined"')
        assert page.evaluate('!!window.Coverage'), 'Coverage must be included in the production build'
        node_id = page.evaluate('''() => {
          doc.pages = {root:{id:'root',name:'Rotation',nodes:[],links:[],noLegend:true}}; cur='root';
          const n=mkNode({type:'rect',x:100,y:100,w:160,h:40,text:'',fill:'#f08020'});
          P().nodes.push(n); selectNodes([n.id]); render(); return n.id;
        }''')
        page.fill('#p-rot', '90')
        assert page.evaluate('rotOf(selectedNodes()[0])') == 90
        page.evaluate('undo()')
        assert page.evaluate('(id)=>rotOf(nodeById(id))', node_id) == 0
        page.evaluate('redo()')
        assert page.evaluate('(id)=>rotOf(nodeById(id))', node_id) == 90
        geometry = page.evaluate('''(id) => {
          const n=nodeById(id); selectNodes([id]); render(); fit(); render();
          const b=contentBBox(), point=rotPoint(n,180,60), r=svg.getBoundingClientRect();
          return {b,handle:!!document.querySelector('[data-h="rot"]'),
            hitX:r.left+(180-view.x)*view.k,hitY:r.top+(60-view.y)*view.k,
            transform:document.querySelector('[data-id="'+id+'"]').getAttribute('transform')};
        }''', node_id)
        assert geometry['handle'] and 'rotate(90' in geometry['transform'], geometry
        assert abs(geometry['b']['w'] - 40) < .001 and abs(geometry['b']['h'] - 160) < .001, geometry
        page.mouse.click(geometry['hitX'], geometry['hitY'])
        assert page.evaluate('selectedNodes()[0].id') == node_id
        page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
        assert page.evaluate('(id)=>rotOf(nodeById(id))', node_id) == 90
        page.evaluate('(id)=>{selectNodes([id]);render()}', node_id)
        grip = page.locator('[data-h="rot"]').bounding_box()
        target = page.evaluate('''(id)=>{const n=nodeById(id),r=svg.getBoundingClientRect();
          return {x:r.left+(n.x+n.w/2-view.x)*view.k,y:r.top+(n.y+n.h/2-80-view.y)*view.k};}''', node_id)
        page.mouse.move(grip['x'] + grip['width'] / 2, grip['y'] + grip['height'] / 2)
        page.mouse.down()
        page.mouse.move(target['x'], target['y'], steps=5)
        page.mouse.up()
        assert page.evaluate('(id)=>rotOf(nodeById(id))', node_id) == 0
        page.evaluate('undo()')
        page.evaluate('(id)=>{selectNodes([id]);render()}', node_id)
        old = page.evaluate('(id)=>{const n=nodeById(id);return {w:n.w,h:n.h,k:view.k,anchor:rotPoint(n,n.x,n.y)}}', node_id)
        corner = page.locator('[data-h="se"]').bounding_box()
        x, y = corner['x'] + corner['width'] / 2, corner['y'] + corner['height'] / 2
        page.mouse.move(x, y)
        page.mouse.down()
        page.mouse.move(x - 20 * old['k'], y + 40 * old['k'], steps=5)
        page.mouse.up()
        resized = page.evaluate('(id)=>{const n=nodeById(id);return {w:n.w,h:n.h,anchor:rotPoint(n,n.x,n.y)}}', node_id)
        assert resized['w'] > old['w'] and resized['h'] > old['h'], (old, resized)
        assert abs(resized['anchor']['x'] - old['anchor']['x']) < .01 and abs(resized['anchor']['y'] - old['anchor']['y']) < .01, (old, resized)
        page.evaluate('undo()')
        with page.expect_download(timeout=90000) as dl:
            page.evaluate('exportPNG(1,false)')
        png = OUT / 'rotation.png'
        dl.value.save_as(png)
        width, height = struct.unpack('>II', png.read_bytes()[16:24])
        assert height > width * 1.7, (width, height)
        routing = page.evaluate('''() => {
          doc.avoid=true;
          const a=mkNode({type:'rect',x:100,y:200,w:100,h:60,rot:45}),
            b=mkNode({type:'rect',x:600,y:200,w:100,h:60}),
            obstacle=mkNode({type:'rect',x:300,y:100,w:150,h:260});
          const link={id:uid(),from:a.id,to:b.id,route:'ortho',kind:'data'};
          const pts=computeRoutes({nodes:[a,obstacle,b],links:[link]}).get(link.id).pts;
          const local=unrotPoint(a,pts[0].x,pts[0].y);
          return {pts,avoid:!pathHits(pts,[obstacle]),
            orthogonal:pts.slice(1).every((q,i)=>Math.abs(q.x-pts[i].x)<.01||Math.abs(q.y-pts[i].y)<.01),
            onEdge:Math.min(Math.abs(local.x-a.x),Math.abs(local.x-a.x-a.w),Math.abs(local.y-a.y),Math.abs(local.y-a.y-a.h))<.01};
        }''')
        assert len(routing['pts']) >= 4 and routing['avoid'] and routing['orthogonal'] and routing['onEdge'], routing
        result = page.evaluate('''async () => {
          const types=['rect','ellipse','sector','equip','text','note','diamond'];
          P().nodes=[]; P().links=[];
          types.forEach((type,i)=>P().nodes.push(mkNode({type,x:80+i*175,y:100,w:130,h:80,
            text:'rotate-'+type,rot:30+i*15,icon:type==='equip'?'lib:'+ICONS[0].key:null,sweep:100})));
          const c=P().nodes.find(n=>n.type==='sector'); c.coverageKind='radar'; c.coverageAlpha=25;
          c.coverageDash='6 4'; c.sw=3; c.w=c.h=120;
          const gradient=P().nodes.find(n=>n.type==='ellipse'); gradient.coverageKind='radar';
          gradient.coverageAlpha=40; gradient.h=gradient.w; gradient.grad='h'; gradient.gradTo='#204080'; gradient.gradA=.5;
          const moved=P().nodes.find(n=>n.type==='equip'); moved.iconLabelDx=25; moved.iconLabelDy=-10; moved.iconLabelGap=0;
          render();
          if (window.JwIconLabels) await JwIconLabels.ready(P());
          const fragment=nodeSVG(c,P(),true), svgOut=exportSVGString(P(),false).str;
          const equipment=P().nodes.find(n=>n.type==='equip'), icon=nodeLayout(equipment).icon;
          const iconCenter=rotPoint(equipment,icon.x+icon.w/2,icon.y+icon.h/2), bounds=contentBBox();
          const expectedIconPin={x:(iconCenter.x-bounds.x+20)/96,y:(bounds.y+bounds.h+20-iconCenter.y)/96};
          const xml=DrawIO.exportString([P()]); const imported=await DrawIO.importText(xml);
          const native=new DOMParser().parseFromString(xml,'text/xml'), nativeLabel=native.querySelector('[id="n'+equipment.id+'_label"]');
          const nativeGeo=nativeLabel.querySelector('mxGeometry'), label=nodeLayout(equipment).text;
          const labelWidth=Math.max(1,...label.lines.map(line=>measure(line,label.size,label.bold,label.family)))+2;
          const labelHeight=label.lines.length*Math.round(label.size*1.38);
          const expectedLabel=rotatedBox(equipment,{x:label.x-labelWidth/2,y:label.cy-labelHeight/2,w:labelWidth,h:labelHeight});
          const coverageLabel=native.querySelector('[id="n'+c.id+'_label"]').getAttribute('label');
          const back=imported.pages[0].nodes;
          const group=mkNode({type:'group',x:0,y:0,w:400,h:300,text:'container'});
          const allowed=types.every(type=>canRotate(P().nodes.find(n=>n.type===type)));
          selectNodes([group.id]);
          return {allowed,container:canRotate(group),xml,fragment,svgOut,expectedIconPin,expectedLabel,coverageLabel,
            nativeLabel:{x:+nativeGeo.getAttribute('x'),y:+nativeGeo.getAttribute('y'),w:+nativeGeo.getAttribute('width'),h:+nativeGeo.getAttribute('height')},
            back:back.map(n=>({type:n.type,rot:rotOf(n),coverageKind:n.coverageKind,coverageAlpha:n.coverageAlpha,coverageDash:n.coverageDash,sw:n.sw})),
            coverage:!!window.Coverage};
        }''')
        assert result['allowed'] and not result['container'], result
        expected = {name: 30 + i * 15 for i, name in enumerate(['rect', 'ellipse', 'sector', 'equip', 'text', 'note', 'diamond'])}
        for node in result['back']:
            assert node['rot'] == expected[node['type']], node
        assert len(result['back']) == len(expected), result['back']
        assert 'rotation=60' in result['xml'] and 'rotate(60' in result['svgOut']
        for axis in ['x', 'y', 'w', 'h']:
            assert abs(result['nativeLabel'][axis] - result['expectedLabel'][axis]) < .11, result['nativeLabel']
        assert '半径' in result['coverageLabel'] and '开角' in result['coverageLabel'], result['coverageLabel']
        if result['coverage']:
            sector = next(n for n in result['back'] if n['type'] == 'sector')
            assert sector['coverageKind'] == 'radar' and sector['coverageAlpha'] == 25 and sector['coverageDash'] == '6 4' and sector['sw'] == 3, sector
            assert 'stroke-dasharray="6 4"' in result['fragment'] and 'fill-opacity="0.25"' in result['fragment'], result['fragment']
        (OUT / 'rotation.drawio').write_text(result['xml'], encoding='utf-8')
        # Existing arrows keep their own world-space rotation and upright ruler labels.
        arrows = page.evaluate('''() => {
          const a=mkNode({type:'dimArrow',x:20,y:350,w:200,h:50,rot:90,text:''});
          const s=nodeSVG(a,P(),true); return s.includes('rotate(90)') && s.includes('rotate(-90');
        }''')
        assert arrows
        for ext, call in [('pptx', 'exportPPTX()'), ('vsdx', 'exportVSDX()')]:
            with page.expect_download(timeout=90000) as dl:
                page.evaluate('async () => {await ' + call + ';}')
            dl.value.save_as(OUT / ('rotation.' + ext))
        a_ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        with zipfile.ZipFile(OUT / 'rotation.pptx') as archive:
            tree = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
            rotations = {round(int(n.get('rot', '0')) / 60000, 3) for n in tree.findall('.//a:xfrm', a_ns)}
            assert set(expected.values()) <= rotations, rotations
            if result['coverage']:
                assert any(n.get('val') == '25000' for n in tree.findall('.//a:alpha', a_ns))
                assert any(n.get('val') == '40000' for n in tree.findall('.//a:alpha', a_ns))
                assert any(n.get('val') == '20000' for n in tree.findall('.//a:alpha', a_ns))
                assert any(n.get('val') == 'dash' for n in tree.findall('.//a:prstDash', a_ns))
        with zipfile.ZipFile(OUT / 'rotation.vsdx') as archive:
            tree = ET.fromstring(archive.read('visio/pages/page1.xml'))
            ns = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}
            angles = [float(n.get('V')) for n in tree.findall('.//v:Cell[@N="Angle"]', ns)]
            for angle in expected.values():
                assert any(abs(value + math.radians(angle)) < .000002 for value in angles), (angle, angles)
            image = tree.find('.//v:Shape[@Type="Foreign"]', ns)
            assert image is not None
            pin = {node.get('N'): float(node.get('V')) for node in image.findall('v:Cell', ns) if node.get('N') in ['PinX', 'PinY']}
            assert abs(pin['PinX'] - result['expectedIconPin']['x']) < .000002 and abs(pin['PinY'] - result['expectedIconPin']['y']) < .000002, (pin, result['expectedIconPin'])
            if result['coverage']:
                assert any(n.get('V') == '0.750000' for n in tree.findall('.//v:Cell[@N="FillForegndTrans"]', ns))
                assert any(n.get('V') == '0.600000' for n in tree.findall('.//v:Cell[@N="GradientStopColorTrans"]', ns))
                assert any(n.get('V') == '0.800000' for n in tree.findall('.//v:Cell[@N="GradientStopColorTrans"]', ns))
                assert any(n.get('V') == '2' for n in tree.findall('.//v:Cell[@N="LinePattern"]', ns))
        assert not errors, errors
        browser.close()
    print('rotation_test ok: UI/undo, hit, bounds, save/load, SVG/PNG/PPTX/VSDX/drawio, coverage styles, legacy arrows')


if __name__ == '__main__':
    main()
