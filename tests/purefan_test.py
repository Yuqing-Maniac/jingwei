"""Pure fan real UI and export regression. Build production HTML before default use.

--source-debug explicitly swaps the app script in the HTTP response for current
sources for pre-build debugging; it never writes dist and is not the CI default.
"""
import argparse
import ast
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import threading
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_work/purefan-test'


def application_html(source_debug):
    html=(ROOT/'dist/offline.html').read_text()
    if not source_debug:return html
    tree=ast.parse((ROOT/'build/build_web.py').read_text())
    mods=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODS' for t in n.targets))
    code='\n'.join((ROOT/'app'/f).read_text() for f in mods+['demo.js'])+'\nloadDoc(buildDemo());'
    count=0
    def replace(m):
        nonlocal count
        if 'const SHP_DEF' not in m.group(1):return m.group(0)
        count+=1
        return '<script>'+code.replace('</script','<\\/script')+'</script>'
    html=re.sub(r'<script[^>]*>([\s\S]*?)</script>',replace,html)
    assert count==1,'Expected exactly one production app bundle'
    return html


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-debug',action='store_true');args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    html=application_html(args.source_debug)
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
        def do_GET(self):
            if self.path=='/purefan-test.html':
                data=html.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            else:super().do_GET()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    errors=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1500,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:%d/purefan-test.html'%server.server_port,timeout=90000,wait_until='domcontentloaded')
        page.wait_for_function('typeof shapeGeom === "function"')
        assert page.evaluate("!!SHP_DEF.fan && !!GEO.fan"),'Production bundle lacks pure fan; rebuild first (no implicit test injection)'
        page.evaluate("""()=>{document.querySelectorAll('#jw-webhist,#jw-home').forEach(e=>e.hidden=true);doc.pages={root:{id:'root',name:'Pure fan',nodes:[],links:[],noLegend:true}};cur='root';clearSel();view={x:0,y:0,k:1};render();}""")
        search=page.locator('#pal-q');search.fill('纯扇形')
        item=page.locator('.pitem[data-add]').filter(has_text='纯扇形').first
        item.wait_for(state='visible')
        stage=page.locator('#stage').bounding_box()
        item.drag_to(page.locator('#stage'),target_position={'x':stage['width']*.5,'y':stage['height']*.45})
        page.wait_for_function("P().nodes.some(n=>n.type==='fan')")
        assert page.evaluate("P().nodes[0].text===''"),'Default pure fan should have no caption'
        def tight():
            return page.evaluate("""()=>{const n=P().nodes.find(n=>n.type==='fan'),e=world.querySelector('[data-id="'+n.id+'"] path'),b=e.getBBox(),s=selectionBox(n);return Math.max(Math.abs(b.x-n.x),Math.abs(b.y-n.y),Math.abs(b.width-n.w),Math.abs(b.height-n.h),Math.abs(s.x-n.x),Math.abs(s.y-n.y),Math.abs(s.w-n.w),Math.abs(s.h-n.h));}""")<.12
        assert tight(),'Visible fan must own its real path bbox'
        def edit(field,value):
            control=page.locator('input[data-shared="'+field+'"]');control.fill(str(value));control.press('Tab')
        edit('sweep',45);assert page.evaluate('P().nodes[0].sweep')==45;assert tight()
        edit('sweep',135);assert tight()
        page.evaluate('undo();selectNodes([P().nodes[0].id]);render();');assert page.evaluate('sectorSweep(P().nodes[0])')==45;assert tight()
        edit('rot',37)
        # Resize by dragging a rotated real handle; opposite visible corner stays.
        before=page.evaluate("""()=>{const n=P().nodes[0];return{fixed:rotPoint(n,n.x,n.y),moving:rotPoint(n,n.x+n.w,n.y+n.h),w:n.w,h:n.h};}""")
        grip=page.locator('[data-h=se]');gb=grip.bounding_box();page.mouse.move(gb['x']+gb['width']/2,gb['y']+gb['height']/2);page.mouse.down();page.mouse.move(gb['x']+gb['width']/2+45,gb['y']+gb['height']/2+30,steps=8);page.mouse.up()
        after=page.evaluate("""()=>{const n=P().nodes[0];return{fixed:rotPoint(n,n.x,n.y),w:n.w,h:n.h};}""")
        assert abs(after['fixed']['x']-before['fixed']['x'])<.15 and abs(after['fixed']['y']-before['fixed']['y'])<.15,'Rotated resize moved the fixed corner'
        assert after['w']!=before['w'] and tight()
        page.screenshot(path=str(OUT/'purefan-rotated-resized.png'))
        # Sweep extrema across all quadrants, no hidden full-circle padding.
        assert page.evaluate("""()=>[10,35,90,135,180,225,270,315,360].every(sweep=>{const u=fanUnit(sweep),w=137*u.w,h=137*u.h,p=shapeGeom('fan',w,h,sweep).fill[0],x=p.map(p=>p[0]),y=p.map(p=>p[1]);return Math.abs(Math.min(...x))<1e-8&&Math.abs(Math.min(...y))<1e-8&&Math.abs(Math.max(...x)-w)<1e-8&&Math.abs(Math.max(...y)-h)<1e-8;})""")
        assert page.evaluate("""()=>[10,30,45,60,90,135,180,225,270,315].every(sweep=>{const u=fanUnit(sweep),p=fanGeom(137*u.w,137*u.h,sweep).fill[0],c=p[0],arc=p.slice(1),r=arc.map(q=>Math.hypot(q[0]-c[0],q[1]-c[1])),a=arc[0],b=arc[arc.length-1],dot=(a[0]-c[0])*(b[0]-c[0])+(a[1]-c[1])*(b[1]-c[1]);let angle=Math.acos(Math.max(-1,Math.min(1,dot/(r[0]*r[r.length-1]))))*180/Math.PI;if(sweep>180)angle=360-angle;return Math.abs(angle-sweep)<1e-6&&Math.max(...r)-Math.min(...r)<1e-6;})"""),'Visible opening/radii must preserve a true circle sector'
        # Serialization and load preserve the explicit new type and dimensions.
        saved=page.evaluate('projectJSON()');page.evaluate('s=>loadDoc(JSON.parse(s).doc)',saved);assert tight()
        assert page.evaluate('JSON.parse(projectJSON()).doc.pages.root.nodes[0].type')=='fan'
        # Old sector still has its old full circle frame and its original points.
        assert page.evaluate("""()=>{const old=mkNode({type:'sector',x:20,y:30,w:100,h:80,sweep:90}),before=JSON.stringify(old),g=shapeGeom('sector',100,80,90);return g.fill[0][0][0]===50&&g.fill[0][0][1]===40&&JSON.stringify(old)===before;}""")
        # Capture real package exports; inspect the produced vector geometry.
        exports=page.evaluate("""async()=>{
          doc.pages.root.nodes[0].x=200;doc.pages.root.nodes[0].y=200;doc.pages.root.nodes[0].w=140;doc.pages.root.nodes[0].h=100;
          const n=P().nodes[0];n.rot=37;n.sweep=135;fitFan(n);n.text='扇形参考';n.grad='h';n.gradTo='#75aaff';render();
          const files={};saveFile=(name,data)=>{files[name.split('.').pop()]=data;return Promise.resolve();};
          const svg=exportSVGString(P(),false).str;await exportPNG(1,false);await exportPPTX();await exportVSDX();
          const dio=DrawIO.exportString(),back=(await DrawIO.importText(dio)).pages[0].nodes.find(n=>n.type==='fan');
          const result={svg,dio,back,node:n,points:shapeGeom('fan',n.w,n.h,n.sweep).fill[0]};
          for(const key of ['png','pptx','vsdx']){const bytes=new Uint8Array(await files[key].arrayBuffer());let str='';for(const b of bytes)str+=String.fromCharCode(b);result[key]=btoa(str);}return result;
        }""")
        (OUT/'purefan.svg').write_text(exports['svg']);(OUT/'purefan.drawio').write_text(exports['dio'])
        for ext in ['png','pptx','vsdx']:(OUT/('purefan.'+ext)).write_bytes(base64.b64decode(exports[ext]))
        for k in ['x','y','w','h','rot','sweep','type','text','grad','gradTo']:assert (abs(exports['node'][k]-exports['back'][k])<.12 if isinstance(exports['node'][k],(float,int)) else exports['node'][k]==exports['back'][k]),('DrawIO round trip',k,exports['back'])
        ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
        with ZipFile(BytesIO(base64.b64decode(exports['pptx']))) as z:
            tree=ET.fromstring(z.read('ppt/slides/slide1.xml'));geoms=tree.findall('.//a:custGeom',ns);assert len(geoms)==1,'Pure fan must use PPT freeform, not native pie'
            assert not tree.findall('.//a:prstGeom[@prst="pie"]',ns)
            assert len(geoms[0].findall('.//a:pt',ns))==len(exports['points'])
            assert geoms[0].find('.//a:close',ns) is not None
            path=geoms[0].find('.//a:path',ns); pts=path.findall('.//a:pt',ns)
            for axis,size in [('x','w'),('y','h')]:
                values=[int(p.attrib[axis]) for p in pts];assert min(values)==0 and max(values)==int(path.attrib[size]), 'PPT fan has hidden geometry padding'
            assert tree.find('.//a:gradFill',ns) is not None, 'Fan gradient lost in PPT'
        with ZipFile(BytesIO(base64.b64decode(exports['vsdx']))) as z:
            text=z.read('visio/pages/page1.xml').decode();assert text.count("T='LineTo'")>=len(exports['points'])-1;assert "N='Angle'" in text
        assert '<path' in exports['svg'] and 'shape=image' in exports['dio'] and 'ht_type="fan"' in exports['dio']
        outside=page.evaluate("""async()=>{
          const n=P().nodes[0];doc.custom.fanLabelTest={name:'Fan label fixture',uri:svgUri('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect x="10" y="10" width="80" height="80" fill="#556677"/></svg>'),aspect:1};
          n.icon='cu:fanLabelTest';n.text='outside label';n.iconLabelDx=300;n.rot=0;render();
          const xml=DrawIO.exportString(),back=await DrawIO.importText(xml),d=new DOMParser().parseFromString(xml,'text/xml'),main=d.querySelector('UserObject[ht_type="fan"]'),labels=[...d.querySelectorAll('UserObject[ht_part="label"]')];
          const l=labels.find(e=>e.getAttribute('label').replace(/<br>/g,' ').includes('outside label')),box=l&&l.querySelector('mxGeometry');
          return {labelOutside:box&&+box.getAttribute('x')>n.x+n.w,count:labels.length,pad:+main.getAttribute('ht_fanPad'),back:back.pages[0].nodes[0],hasCustom:Object.keys(back.custom).length>0};
        }""")
        assert outside['labelOutside'] and outside['count']>=2,'Drawio must keep external caption and icon outside the shape snapshot: '+repr(outside)
        assert outside['pad']>=1 and outside['back']['text']=='outside label' and outside['back']['icon'] and outside['hasCustom'],'Drawio lost stroke padding or custom icon/caption roundtrip'
        page.evaluate('fit();render();')
        page.screenshot(path=str(OUT/'purefan-external-label.png'))
        assert not errors,errors
        (OUT/'report.json').write_text(json.dumps({'passed':True,'sourceDebug':args.source_debug,'pageErrors':errors,'checks':['palette real drag','tight path and selection bbox','sweep edit and undo','rotated fixed-corner resize','save/load','SVG/PNG/PPTX freeform/VSDX/drawio export','legacy sector unchanged']},ensure_ascii=False,indent=2)+'\n')
        browser.close();print('PASS purefan', 'source debug' if args.source_debug else 'production')
    except Exception as exc:
        (OUT/'report.json').write_text(json.dumps({'passed':False,'sourceDebug':args.source_debug,'error':str(exc),'pageErrors':errors},ensure_ascii=False,indent=2)+'\n')
        raise
    finally:server.shutdown()


if __name__=='__main__':main()
