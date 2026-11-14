"""Stack overlapping icons without changing containers or multi-selection order."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_work' / 'layer-order-test'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri()), timeout=90000)
        page.wait_for_function('typeof layerSelection === "function"')
        setup = page.evaluate('''() => {
          doc.pages={root:{id:'root',name:'Layers',nodes:[],links:[],noLegend:true}}; cur='root';
          const nodes=['A','B','C','D'].map((name,i)=>{
            const key='layer'+name;
            doc.custom[key]={name,aspect:1,uri:svgUri('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect x="10" y="10" width="80" height="80" fill="'+['#ee4411','#22aa44','#2266ee','#aa33cc'][i]+'"/></svg>')};
            return mkNode({type:'equip',icon:'cu:'+key,x:100,y:100,w:140,h:140,text:name,noBox:true});
          });
          const container=mkNode({type:'group',x:40,y:40,w:450,h:330,text:'container'});
          const arrow=mkNode({type:'stdArrow',x:280,y:270,w:160,h:24,stroke:'#010203',text:''});
          nodes[1].parent=container.id;
          P().nodes=[nodes[0],container,nodes[1],nodes[2],nodes[3],arrow];
          window.layerFixture=JSON.stringify(P().nodes);
          window.layerIds=Object.fromEntries(nodes.map(n=>[n.text,n.id])); layerIds.container=container.id;
          window.layerNames=()=>P().nodes.filter(n=>!isCont(n)).map(n=>n.text||'arrow');
          window.layerReset=()=>{P().nodes=JSON.parse(layerFixture);selectNodes([layerIds.D,layerIds.B,layerIds.container]);render()};
          render(); fit(); render(); return {ids:layerIds,containerIndex:1};
        }''')
        for action, expected in [
            ('up', ['A', 'C', 'B', 'arrow', 'D']),
            ('down', ['B', 'A', 'D', 'C', 'arrow']),
            ('front', ['A', 'C', 'arrow', 'B', 'D']),
            ('back', ['B', 'D', 'A', 'C', 'arrow']),
        ]:
            result = page.evaluate('''action=>{
              layerReset(); const history=undoS.length, parents=P().nodes.map(n=>[n.id,n.parent||null]);
              const changed=layerSelection(action), names=layerNames(), delta=undoS.length-history;
              const containerIndex=P().nodes.findIndex(n=>isCont(n));
              const parentsSame=parents.every(([id,parent])=>(nodeById(id).parent||null)===parent);
              undo(); const undone=layerNames(); redo(); const redone=layerNames();
              loadDoc(JSON.parse(projectJSON()).doc); return {changed,names,delta,containerIndex,parentsSame,undone,redone,saved:layerNames()};
            }''', action)
            assert result['changed'] and result['delta'] == 1 and result['parentsSame'], result
            assert result['containerIndex'] == setup['containerIndex'], result
            assert result['names'] == result['redone'] == result['saved'] == expected, (action, result)
            assert result['undone'] == ['A', 'B', 'C', 'D', 'arrow'], result
        page.evaluate('layerReset();selectNodes([layerIds.A]);render()')
        assert page.locator('#props [data-layer]').count() == 4
        page.click('#props [data-layer="front"]')
        assert page.evaluate('layerNames()')[-1] == 'A'
        hit = page.evaluate('''()=>{const n=nodeById(layerIds.A),L=nodeLayout(n),r=svg.getBoundingClientRect();
          return {x:r.left+(L.icon.x+L.icon.w/2-view.x)*view.k,y:r.top+(L.icon.y+L.icon.h/2-view.y)*view.k};}''')
        assert page.evaluate('''p=>document.elementFromPoint(p.x,p.y).closest('[data-id]').dataset.id''', hit) == setup['ids']['A']
        page.mouse.click(hit['x'], hit['y'], button='right')
        assert page.locator('#ctx [data-layer]:visible').count() == 4
        page.click('#ctx [data-layer="back"]')
        assert page.evaluate('layerNames()')[0] == 'A'
        assert page.evaluate('''p=>document.elementFromPoint(p.x,p.y).closest('[data-id]').dataset.id''', hit) == setup['ids']['D']
        page.evaluate('selectNodes([layerIds.container]);render()')
        assert page.locator('#props [data-layer]').count() == 0
        assert page.evaluate('layerSelection("front")') is False
        # Put the arrow between two icons to catch exporters that defer all arrows to the end.
        exports = page.evaluate('''async()=>{
          layerReset(); selectNodes([layerIds.D,layerIds.B]); layerSelection('front');
          if(window.JwIconLabels) await JwIconLabels.ready(P());
          const svgOut=exportSVGString(P(),false).str, xml=DrawIO.exportString([P()]);
          const imported=await DrawIO.importText(xml);
          return {names:layerNames(),svg:svgOut,xml,
            svgIds:drawOrder(P()).map(n=>n.id),
            roundtrip:imported.pages[0].nodes.filter(n=>!isCont(n)).map(n=>n.text||'arrow')};
        }''')
        assert exports['names'] == exports['roundtrip'] == ['A', 'C', 'arrow', 'B', 'D'], exports['roundtrip']
        svg_tree = ET.fromstring(exports['svg'])
        svg_ids = [node.get('data-id') for node in svg_tree.iter() if node.get('data-id')]
        assert svg_ids == exports['svgIds'], svg_ids
        (OUT / 'layers.drawio').write_text(exports['xml'], encoding='utf-8')
        for ext, call in [('pptx', 'exportPPTX()'), ('vsdx', 'exportVSDX()')]:
            with page.expect_download(timeout=90000) as dl:
                page.evaluate('async()=>{await ' + call + ';}')
            dl.value.save_as(OUT / ('layers.' + ext))
        with zipfile.ZipFile(OUT / 'layers.pptx') as archive:
            tree = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
            ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main', 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
            order = []
            for shape in tree.find('.//p:spTree', ns):
                text = ''.join(node.text or '' for node in shape.findall('.//a:t', ns))
                if text in ['A', 'B', 'C', 'D']:
                    order.append(text)
                elif any(node.get('val') == '010203' for node in shape.findall('.//a:srgbClr', ns)):
                    order.append('arrow')
            assert order == exports['names'], order
        with zipfile.ZipFile(OUT / 'layers.vsdx') as archive:
            tree = ET.fromstring(archive.read('visio/pages/page1.xml'))
            ns = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}
            order = []
            for shape in tree.find('v:Shapes', ns):
                text = shape.find('v:Text', ns)
                if text is not None and text.text in ['A', 'B', 'C', 'D']:
                    order.append(text.text)
                elif any(node.get('V') == '#010203' for node in shape.findall('v:Cell[@N="LineColor"]', ns)):
                    order.append('arrow')
            assert order == exports['names'], order
        assert not errors, errors
        browser.close()
    print('layer_order_test ok: four actions, multi-selection, container invariants, undo/save, UI/hit, SVG/PPTX/VSDX/drawio order')


if __name__ == '__main__':
    main()
