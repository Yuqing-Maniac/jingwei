"""扇形、实色、渐变、渐变到透明、描边和无描边，并核对导出。"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri()))
        page.wait_for_function('typeof sectorGeom === "function" && typeof paintOf === "function"')
        result = page.evaluate('''async () => {
          const p = P();
          p.nodes = p.nodes.filter(n => n.type === 'legend' || n.type === 'tblock');
          const fan = mkNode({ type: 'sector', w: 120, h: 100, text: '' });
          fan.x = 40; fan.y = 40;
          const box = mkNode({ type: 'rect', w: 140, h: 70, text: '色块', fill: '#112233' });
          box.x = 200; box.y = 40;
          p.nodes.push(fan, box);
          const fanPath = svg => {
            const ds = (svg.match(/<path d="[^"]+"/g) || []).map(s => s.slice(9, -1));
            const hit = ds.filter(d => d.indexOf('M100.0,90.0') === 0 || d.indexOf('M140.0,90.0') === 0);
            hit.sort((a, b) => b.length - a.length);
            return hit[0] || '';
          };
          selectNodes([fan.id]); render();
          const panel = {
            sweep: document.getElementById('p-sweep') && document.getElementById('p-sweep').value,
            fill: !!document.getElementById('p-fill'),
            grad: !!document.getElementById('p-grad'),
            stroke: !!document.getElementById('p-stroke'),
            noLine: !!document.getElementById('p-noLine')
          };
          const d90 = fanPath(diagramSVG(p, true));
          document.getElementById('p-sweep').value = '180';
          document.getElementById('p-sweep').dispatchEvent(new Event('input', { bubbles: true }));
          const d180 = fanPath(diagramSVG(p, true));
          const grown = P().nodes.find(n => n.type === 'sector');
          grown.w = 200; render();
          const dWide = fanPath(diagramSVG(p, true));
          undo();
          const undone = sectorSweep(P().nodes.find(n => n.type === 'sector')) === 90;
          const again = P().nodes.find(n => n.type === 'sector');
          again.sweep = 180; again.w = 120; render();
          selectNodes([box.id]); render();
          document.getElementById('p-grad').value = 'v';
          document.getElementById('p-grad').dispatchEvent(new Event('change', { bubbles: true }));
          document.getElementById('p-gradTo').value = '#abcdef';
          document.getElementById('p-gradTo').dispatchEvent(new Event('input', { bubbles: true }));
          document.getElementById('p-gradA').value = '0';
          document.getElementById('p-gradA').dispatchEvent(new Event('input', { bubbles: true }));
          document.getElementById('p-noLine').checked = true;
          document.getElementById('p-noLine').dispatchEvent(new Event('change', { bubbles: true }));
          const live = P().nodes.find(n => n.text === '色块');
          const svg = diagramSVG(P(), true);
          const solid = mkNode({ type: 'ellipse', w: 80, h: 60, text: '', fill: '#2255aa', stroke: '#101820' });
          solid.x = 40; solid.y = 180;
          P().nodes.push(solid); render();
          const svg2 = diagramSVG(P(), true);
          const exp = exportSVGString(P(), true).str;
          const png = await rasterize('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#112233" stop-opacity="1"/><stop offset="1" stop-color="#112233" stop-opacity="0"/></linearGradient></defs><rect width="40" height="40" fill="url(#g)"/></svg>', 40, 40, 1);
          const alpha = await new Promise((res, rej) => {
            const img = new Image();
            const url = URL.createObjectURL(png);
            img.onload = () => {
              const c = document.createElement('canvas'); c.width = 40; c.height = 40;
              const g = c.getContext('2d'); g.drawImage(img, 0, 0);
              URL.revokeObjectURL(url);
              res({ top: g.getImageData(20, 2, 1, 1).data[3], bot: g.getImageData(20, 37, 1, 1).data[3] });
            };
            img.onerror = () => { URL.revokeObjectURL(url); rej(new Error('png')); };
            img.src = url;
          });
          const prev = saveFile;
          const blobs = [];
          saveFile = async (name, data) => { blobs.push({ name: name, data: data }); };
          await exportPPTX();
          await exportVSDX();
          const xml = DrawIO.exportString([P()]);
          const back = await DrawIO.importText(xml);
          saveFile = prev;
          const ppt = await JSZip.loadAsync(await blobs[0].data.arrayBuffer());
          let pptPie = false, pptGrad = false, pptClear = false, pptNoLine = false;
          for (const name of Object.keys(ppt.files)) {
            if (!/\\.xml$/.test(name)) continue;
            const t = await ppt.files[name].async('string');
            if (t.includes('prst="pie"')) pptPie = true;
            if (t.includes('<a:gradFill')) pptGrad = true;
            if (t.includes('<a:alpha val="0"/>')) pptClear = true;
            if (t.includes('<a:ln><a:noFill/></a:ln>')) pptNoLine = true;
          }
          const vsd = await JSZip.loadAsync(await blobs[1].data.arrayBuffer());
          let vsdGrad = false, vsdClear = false, vsdFan = false;
          for (const name of Object.keys(vsd.files)) {
            if (!name.endsWith('.xml')) continue;
            const t = await vsd.files[name].async('string');
            if (t.includes('FillGradientEnabled')) vsdGrad = true;
            if (t.includes('GradientStopColorTrans') && t.includes("V='1.000000'")) vsdClear = true;
            if (t.includes('扇形') || (t.match(/LineTo/g) || []).length > 20) vsdFan = true;
          }
          let dioFade = false;
          const ire = /image=data:image\\/svg\\+xml,([A-Za-z0-9+/=]+)/g;
          let im;
          while ((im = ire.exec(xml))) {
            try {
              const raw = atob(im[1]);
              if (raw.indexOf('stop-opacity="0"') >= 0 && raw.indexOf('stroke="none"') >= 0) dioFade = true;
            } catch (e) {}
          }
          const imported = back.pages[0].nodes.find(n => n.fill === '#112233');
          return {
            panel, d90: d90.length, d180: d180.length, wider: d180 !== d90 && dWide.includes('240') && d180.includes('160'), undone,
            model: { grad: live.grad, to: live.gradTo, a: live.gradA, noLine: !!live.noLine, sweep: sectorSweep(P().nodes.find(n => n.type === 'sector')) },
            svgGrad: svg.includes('linearGradient') && svg.includes('stop-opacity="0"') && svg.includes('stroke="none"'),
            svgSolid: svg2.includes('#2255aa') && svg2.includes('#101820'),
            exp: exp.includes('stop-opacity="0"') && exp.includes('#2255aa'),
            alpha, pptPie, pptGrad, pptClear, pptNoLine, vsdGrad, vsdClear, vsdFan,
            dio: dioFade && xml.includes('shape=mxgraph.basic.pie;startAngle=0;endAngle=0.5000'),
            back: imported && imported.grad === 'v' && imported.gradA === 0 && imported.noLine === true && back.pages[0].nodes.some(n => n.type === 'sector' && n.sweep === 180)
          };
        }''')
        browser.close()
        assert not errors, errors
        assert result['panel']['sweep'] == '90' and result['panel']['fill'] and result['panel']['grad'] and result['panel']['stroke'] and result['panel']['noLine'], result
        assert result['d90'] > 20 and result['d180'] > result['d90'] and result['wider'] and result['undone'], result
        assert result['model'] == {'grad': 'v', 'to': '#abcdef', 'a': 0, 'noLine': True, 'sweep': 180}, result
        assert result['svgGrad'] and result['svgSolid'] and result['exp'], result
        assert result['alpha']['top'] > 200 and result['alpha']['bot'] < 30, result
        assert result['pptPie'] and result['pptGrad'] and result['pptClear'] and result['pptNoLine'], result
        assert result['vsdGrad'] and result['vsdClear'] and result['vsdFan'], result
        assert result['dio'] and result['back'], result
        print('sector_fill_test ok')


if __name__ == '__main__':
    main()
