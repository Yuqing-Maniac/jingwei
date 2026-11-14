"""Production UI: scoped background region, independent grid drag and exports.

Run after root builds dist/offline.html. No source injection or production writes.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import base64
import io
import json
import os
from pathlib import Path
import shutil
import struct
import threading
import xml.etree.ElementTree as ET
import zipfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_work/canvasbg-region-test'


def check_export_geometry(exported):
    """Inspect the actual exported assets, beyond stored roundtrip metadata."""
    r,b=exported['model']['region'],exported['box']
    def close(actual,wanted,label,tolerance=1e-5):
        assert abs(actual-wanted)<tolerance,(label,actual,wanted)
    def png_size(data):
        assert data.startswith(b'\x89PNG\r\n\x1a\n')
        return struct.unpack('>II',data[16:24])
    ns={'s':'http://www.w3.org/2000/svg','p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','v':'http://schemas.microsoft.com/office/visio/2012/main'}
    svg=ET.fromstring(exported['svg']);sheet=svg.find('.//s:g[@class="cbg"]',ns)
    assert sheet is not None
    rect=next(e for e in sheet.findall('.//s:rect',ns) if e.get('fill','').startswith('url('))
    for attr,key in [('x','x'),('y','y'),('width','w'),('height','h')]:close(float(rect.get(attr)),r[key],'SVG '+attr)
    assert sheet.find('.//s:g[@clip-path]',ns) is not None
    for line in sheet.findall('.//s:line',ns):
        for key in ['x1','x2']:assert r['x']<=float(line.get(key))<=r['x']+r['w']
        for key in ['y1','y2']:assert r['y']<=float(line.get(key))<=r['y']+r['h']
    png=base64.b64decode(exported['png'])
    assert png_size(png)==(round(b['w']+48),round(b['h']+48))
    # The first native PPT picture is the scoped background, not a page-sized bitmap.
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(exported['pptx']))) as z:
        slide=ET.fromstring(z.read('ppt/slides/slide1.xml'))
        pic=slide.find('.//p:spTree/p:pic',ns);assert pic is not None
        transform=pic.find('p:spPr/a:xfrm',ns);off=transform.find('a:off',ns);extent=transform.find('a:ext',ns)
        f=min((13.333-.5)/(b['w']+32),(7.5-.4)/(b['h']+32));ox=(13.333-(b['w']+32)*f)/2;oy=(7.5-(b['h']+32)*f)/2
        for actual,wanted,label in [(int(off.get('x'))/914400,ox+(r['x']-b['x']+16)*f,'PPT x'),(int(off.get('y'))/914400,oy+(r['y']-b['y']+16)*f,'PPT y'),(int(extent.get('cx'))/914400,r['w']*f,'PPT width'),(int(extent.get('cy'))/914400,r['h']*f,'PPT height')]:close(actual,wanted,label)
        images=[z.read(name) for name in z.namelist() if name.startswith('ppt/media/') and name.endswith('.png')]
        assert any(png_size(image)==(round(r['w']),round(r['h'])) for image in images)
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(exported['vsdx']))) as z:
        doc=ET.fromstring(z.read('visio/pages/page1.xml'));shapes=doc.findall('v:Shapes/v:Shape',ns);assert len(shapes)>=4
        cells=lambda shape:{e.get('N'):float(e.get('V')) for e in shape.findall('v:Cell',ns) if e.get('N') in ['PinX','PinY','Width','Height','LocPinX','LocPinY']}
        fill=cells(shapes[0]);grid=cells(shapes[1])
        expected={'Width':r['w']/96,'Height':r['h']/96,'PinX':(r['x']-b['x']+20+r['w']/2)/96,'PinY':(b['h']+40-(r['y']-b['y']+20)-r['h']/2)/96}
        for key,value in expected.items():close(fill[key],value,'VSDX '+key)
        for axis,size in [('X','Width'),('Y','Height')]:
            assert grid['Pin'+axis]-grid[size]/2>=fill['Pin'+axis]-fill[size]/2-1e-5
            assert grid['Pin'+axis]+grid[size]/2<=fill['Pin'+axis]+fill[size]/2+1e-5
    dio=ET.fromstring(exported['dio']);background=dio.findall('.//UserObject[@ht_part="canvasbg"]');assert background
    fill=next(e for e in background if e.get('id') in ['cbg-fill','cbg-img'])
    geometry=fill.find('mxCell/mxGeometry')
    for attr,key in [('x','x'),('y','y'),('width','w'),('height','h')]:close(float(geometry.get(attr)),r[key],'drawio '+attr)
    for obj in background:
        for point in obj.findall('.//mxPoint'):
            assert r['x']<=float(point.get('x'))<=r['x']+r['w']
            assert r['y']<=float(point.get('y'))<=r['y']+r['h']


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    errors=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or shutil.which('chromium'),args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1500,'height':1000})
        page.on('pageerror',lambda e:errors.append(e.stack or str(e)))
        response=page.goto(os.environ.get('JW_TEST_URL') or 'http://127.0.0.1:%d/dist/offline.html'%server.server_port,wait_until='domcontentloaded',timeout=90000)
        assert response and response.ok, 'Production test URL did not return a page'
        page.wait_for_function('!!window.CanvasBg')
        assert page.evaluate("typeof CanvasBg.regionBox==='function'"),'Rebuild production with background region support first'
        page.evaluate("""()=>{
          document.querySelectorAll('#jw-home,#jw-webhist').forEach(e=>e.hidden=true);
          doc.pages={root:{id:'root',name:'区域网格',nodes:[mkNode({id:'top',type:'rect',x:100,y:90,w:360,h:100,text:'上层渐变图元',grad:'h',gradTo:'#f4d099'}),mkNode({id:'bottom',type:'rect',x:140,y:400,w:160,h:60,text:'普通图元'})],links:[],noLegend:true}};
          cur='root';clearSel();Object.assign(view,{x:0,y:0,k:1});render();
        }""")
        originals=page.evaluate('JSON.stringify(P().nodes)')
        page.locator('#b-bg').click()
        assert page.locator('#cbg-scope').input_value()=='region','New background should default to fixed region'
        for key,value in [('xpos',100),('ypos',350),('width',480),('height',180),('gap',32),('offset-x',11),('offset-y',17)]:
            page.locator('#cbg-'+key).fill(str(value))
        page.locator('#cbg-grid').check()
        page.locator('#cbg-dlg button').filter(has_text='应用并锁定').click()
        page.locator('#cbg-x').click()
        def model():return page.evaluate('JSON.parse(JSON.stringify(P().canvasBg))')
        def check_bounds():
            return page.evaluate("""()=>{const m=P().canvasBg,b=m.region,g=world.querySelector('g.cbg'),r=g.querySelector('rect[fill^="url"]');if(+r.getAttribute('x')!==b.x||+r.getAttribute('y')!==b.y||+r.getAttribute('width')!==b.w||+r.getAttribute('height')!==b.h)return false;return [...g.querySelectorAll('line')].every(l=>['x1','x2'].every(k=>+l.getAttribute(k)>=b.x-.001&&+l.getAttribute(k)<=b.x+b.w+.001)&&['y1','y2'].every(k=>+l.getAttribute(k)>=b.y-.001&&+l.getAttribute(k)<=b.y+b.h+.001));}""")
        initial=model();assert initial['region']=={'x':100,'y':350,'w':480,'h':180};assert check_bounds()
        # Changing unrelated diagram geometry cannot resize/reanchor this region.
        page.evaluate("P().nodes[0].x+=600;render();")
        assert model()==initial and check_bounds()
        page.evaluate("P().nodes[0].x-=600;render();")
        assert page.evaluate('JSON.stringify(P().nodes)')==originals
        first=page.evaluate("[...world.querySelectorAll('g.cbg line')][0].outerHTML")
        def drag_world(x,y,dx,dy):
            b=page.locator('#svg').bounding_box();v=page.evaluate('({...view})')
            sx=b['x']+(x-v['x'])*v['k'];sy=b['y']+(y-v['y'])*v['k']
            page.mouse.move(sx,sy);page.mouse.down();page.mouse.move(sx+dx*v['k'],sy+dy*v['k'],steps=8);page.mouse.up()
        def check_space_pan():
            before=model();cam=page.evaluate('({...view})');history=page.evaluate('undoS.length')
            page.keyboard.down('Space');drag_world(360,460,24,16);page.keyboard.up('Space')
            after=page.evaluate('({...view})')
            assert model()==before,'Space drag modified the region/grid instead of panning the camera'
            assert abs(after['x']-cam['x']+24)<1e-6 and abs(after['y']-cam['y']+16)<1e-6,(cam,after)
            assert page.evaluate('undoS.length')==history,'Camera pan added a document undo step'
            assert page.evaluate('JSON.stringify(P().nodes)')==originals
        page.locator('#b-bg').click();page.locator('#cbg-drag-region').click()
        check_space_pan()
        drag_world(360,460,70,35)
        moved=model();assert moved['region']=={'x':170,'y':385,'w':480,'h':180};assert moved['grid']==initial['grid'];assert check_bounds()
        assert page.evaluate('JSON.stringify(P().nodes)')==originals,'Background drag moved diagram nodes'
        page.locator('#cbg-done').click()
        # One undo step restores the geometry drag (application itself is separate).
        page.keyboard.press('Control+z');assert model()==initial
        page.locator('#b-bg').click();page.locator('#cbg-drag-grid').click()
        check_space_pan()
        drag_world(360,460,23,-14)
        grid=model();assert grid['region']==initial['region'];assert grid['grid']['offsetX']==34 and grid['grid']['offsetY']==3
        assert check_bounds() and page.evaluate('JSON.stringify(P().nodes)')==originals
        assert page.evaluate("[...world.querySelectorAll('g.cbg line')][0].outerHTML")!=first
        page.keyboard.press('Escape');assert page.locator('#cbg-done').is_hidden()
        page.screenshot(path=str(OUT/'region-grid-dragged.png'))
        page.keyboard.press('Control+z');assert model()==initial
        page.keyboard.press('Control+y');assert model()==grid
        saved=page.evaluate('projectJSON()');page.evaluate('s=>loadDoc(JSON.parse(s).doc)',saved);assert model()==grid and check_bounds()
        # Old documents retain automatic geometry and never gain a fixed region.
        assert page.evaluate("""()=>{const old={canvasBg:{grad:{stops:[{at:0,color:'#ffffff',opacity:1},{at:1,color:'#dddddd',opacity:1}]},grid:{show:true}}};CanvasBg.lockPages({pages:{old}});return !old.canvasBg.region&&CanvasBg.regionBox(old)===null;}""")
        # Perspective offsets also remain strictly within the owner region.
        page.locator('#b-bg').click();page.locator('#cbg-persp').fill('65');page.locator('#cbg-offset-x').fill('125');page.locator('#cbg-offset-y').fill('-45')
        page.locator('#cbg-dlg button').filter(has_text='应用并锁定').click();page.locator('#cbg-x').click();assert check_bounds()
        page.screenshot(path=str(OUT/'region-perspective-clipped.png'))
        exported=page.evaluate("""async()=>{
          const files={};saveFile=(name,data)=>{files[name.split('.').pop()]=data;return Promise.resolve();};
          const svg=exportSVGString(P(),false).str;await exportPNG(1,false);await exportPPTX();await exportVSDX();
          const dio=DrawIO.exportString(),back=await DrawIO.importText(dio);
          const result={svg,dio,background:back.pages[0].canvasBg,model:P().canvasBg,box:contentBBox(P())};
          for(const key of ['png','pptx','vsdx']){const bytes=new Uint8Array(await files[key].arrayBuffer());let str='';for(const b of bytes)str+=String.fromCharCode(b);result[key]=btoa(str);}return result;
        }""")
        assert exported['background']==exported['model'],'Drawio lost background region/offset fields'
        b=exported['box'];r=exported['model']['region'];assert b['x']<=r['x'] and b['y']<=r['y'] and b['x']+b['w']>=r['x']+r['w'] and b['y']+b['h']>=r['y']+r['h']
        assert 'clip-path=' in exported['svg'] and 'ht_canvasBg=' in exported['dio']
        (OUT/'region.svg').write_text(exported['svg']);(OUT/'region.drawio').write_text(exported['dio'])
        for ext in ['png','pptx','vsdx']:(OUT/('region.'+ext)).write_bytes(base64.b64decode(exported[ext]))
        check_export_geometry(exported)
        assert not errors,errors
        (OUT/'report.json').write_text(json.dumps({'passed':True,'pageErrors':errors,'checks':['fixed region','unrelated gradients unchanged','real region drag','independent grid drag','space drag pans only in both edit modes','undo/redo','save/load','legacy auto retained','perspective strict clipping','actual SVG/PNG/PPTX/VSDX/drawio region geometry and roundtrip']},ensure_ascii=False,indent=2)+'\n')
        browser.close();print('PASS canvasbg region production')
    except Exception as e:
        (OUT/'report.json').write_text(json.dumps({'passed':False,'error':str(e),'pageErrors':errors},ensure_ascii=False,indent=2)+'\n');raise
    finally:server.shutdown()


if __name__=='__main__':main()
