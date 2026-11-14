import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOT = Path(os.environ.get('JW_SHOT', '/opt/cursor/artifacts'))


def main():
    SHOT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri()))
        page.wait_for_function('typeof rulerGeom === "function" && typeof renderPalette === "function"')
        result = page.evaluate('''async () => {
          const textsOf = (svg) => {
            const out = [], re = /<text\\b[^>]*>([^<]*)<\\/text>/g;
            let m;
            while ((m = re.exec(svg))) out.push(m[1]);
            return out;
          };
          P().nodes = []; P().links = []; P().noLegend = true;
          doc.measure = { unit: 'm', px: 10 };
          const n = mkNode({ type: 'dimArrow', x: 80, y: 160, w: 160, h: 64, text: '', stroke: '#1F5FBF', sw: 2, rulerStart: 0, rulerStep: 10, rulerGap: 40, rulerMinor: 1, rulerUnit: 'm', rulerText: '0,10,25' });
          P().nodes.push(n);
          selectNodes([n.id]); render();
          const g0 = rulerGeom(n);
          const xs0 = g0.majors.map(t => t.x);
          const labels0 = g0.majors.map(t => t.text);
          const gap0 = xs0.length > 1 ? xs0[1] - xs0[0] : 0;
          const svg0 = nodeSVG(n, P(), true);
          const shown0 = textsOf(svg0);
          n.w = 240; render();
          const g1 = rulerGeom(n);
          const xs1 = g1.majors.map(t => t.x);
          const gap1 = xs1.length > 1 ? xs1[1] - xs1[0] : 0;
          const labels1 = g1.majors.map(t => t.text);
          const customDist = dimLabel(n) === labels1[labels1.length - 1];
          const probe = mkNode({ type: 'dimArrow', w: 200, h: 48, rulerStart: 0, rulerStep: 10, rulerGap: 48, rulerUnit: 'm', rulerMinor: 0 });
          const partial = dimLabel(probe) === '41.667 m';
          probe.w = 192;
          const exact = dimLabel(probe) === '40 m';
          const svg1 = diagramSVG(P(), true);
          const shown1 = textsOf(svg1);
          const tickLines = (svg1.match(/<line /g) || []).length;
          n.rot = 90; render();
          const turned = nodeSVG(n, P(), true);
          const upright = turned.indexOf('rotate(-90') >= 0 && turned.indexOf('font-size="12"') >= 0;
          delete n.rot; render();
          const panel = ['p-rulerStart', 'p-rulerGap', 'p-rulerStep', 'p-rulerMinor', 'p-rulerUnit', 'p-rulerSide', 'p-rulerText', 'p-sw', 'p-rot', 'p-stroke', 'p-headColor', 'p-dist'].every(id => document.getElementById(id));
          document.getElementById('p-rulerText').value = '0,10,20';
          document.getElementById('p-rulerText').dispatchEvent(new Event('input', { bubbles: true }));
          const edited = rulerGeom(P().nodes[0]).majors.map(t => t.text);
          const distEl = document.getElementById('p-dist');
          const distance = !!distEl && distEl.readOnly && distEl.value === '60 m' && dimLabel(P().nodes[0]) === '60 m' && !P().nodes[0].distMode && !P().nodes[0].distText;
          const svgOut = exportSVGString(P(), false).str;
          const svgTicks = textsOf(svgOut);
          const xml = DrawIO.exportString([P()]);
          const imported = await DrawIO.importText(xml);
          const back = imported.pages[0].nodes.find(it => it.type === 'dimArrow');
          const dio = {
            type: back && back.type,
            step: back && back.rulerStep,
            gap: back && back.rulerGap,
            text: back && back.rulerText,
            ticks: (xml.match(/ht_part="ruler"/g) || []).length,
            nums: xml.indexOf('>0<') >= 0 || xml.indexOf('label="0"') >= 0,
            line: xml.indexOf('endArrow=classic') >= 0
          };
          const prev = saveFile;
          const blobs = [];
          saveFile = async (name, data) => { blobs.push({ name: name, data: data }); };
          await exportPPTX();
          await exportVSDX();
          const png = await rasterize(svgOut, 400, 240, 2);
          saveFile = prev;
          const ppt = await JSZip.loadAsync(await blobs[0].data.arrayBuffer());
          let pptText = '';
          for (const name of Object.keys(ppt.files)) {
            if (name.indexOf('slide') < 0 || name.indexOf('.xml') < 0) continue;
            pptText += await ppt.files[name].async('string');
          }
          const vsd = await JSZip.loadAsync(await blobs[1].data.arrayBuffer());
          let vsdText = '';
          for (const name of Object.keys(vsd.files)) {
            if (name.indexOf('page') < 0 || name.indexOf('.xml') < 0) continue;
            vsdText += await vsd.files[name].async('string');
          }
          document.getElementById('p-stroke').value = '#112233';
          document.getElementById('p-stroke').dispatchEvent(new Event('input', { bubbles: true }));
          document.getElementById('p-headColor').value = '#aa0044';
          document.getElementById('p-headColor').dispatchEvent(new Event('input', { bubbles: true }));
          const colored = P().nodes[0];
          const colorSvg = nodeSVG(colored, P(), true);
          const colorNode = colored.stroke === '#112233' && colored.headColor === '#aa0044' && colorSvg.indexOf('stroke="#112233"') >= 0 && colorSvg.indexOf('fill="#aa0044"') >= 0 && colorSvg.indexOf('fill="#112233"') >= 0;
          const colorXml = DrawIO.exportString([P()]);
          const colorBack = (await DrawIO.importText(colorXml)).pages[0].nodes.find(it => it.type === 'dimArrow');
          const colorDio = !!(colorBack && colorBack.headColor === '#aa0044' && colorBack.stroke === '#112233' && !colorBack.distText && colorXml.indexOf('#aa0044') >= 0 && colorXml.indexOf('endArrow=none') >= 0);
          const blobs2 = [];
          saveFile = async (name, data) => { blobs2.push({ name: name, data: data }); };
          await exportPPTX();
          await exportVSDX();
          const colorOut = exportSVGString(P(), false).str;
          const colorPng = await rasterize(colorOut, 400, 240, 2);
          saveFile = prev;
          const ppt2z = await JSZip.loadAsync(await blobs2[0].data.arrayBuffer());
          let ppt2 = '';
          for (const name of Object.keys(ppt2z.files)) {
            if (name.indexOf('slide') < 0 || name.indexOf('.xml') < 0) continue;
            ppt2 += await ppt2z.files[name].async('string');
          }
          const vsd2z = await JSZip.loadAsync(await blobs2[1].data.arrayBuffer());
          let vsd2 = '';
          for (const name of Object.keys(vsd2z.files)) {
            if (name.indexOf('page') < 0 || name.indexOf('.xml') < 0) continue;
            vsd2 += await vsd2z.files[name].async('string');
          }
          const colorFile = ppt2.indexOf('AA0044') >= 0 && ppt2.indexOf('112233') >= 0 && vsd2.indexOf('#aa0044') >= 0 && vsd2.indexOf('#112233') >= 0 && colorPng && colorPng.size > 1000 && colorOut.indexOf('#aa0044') >= 0 && colorOut.indexOf('#112233') >= 0;
          document.getElementById('p-stroke').value = '#445566';
          document.getElementById('p-stroke').dispatchEvent(new Event('input', { bubbles: true }));
          const keptHead = P().nodes[0].stroke === '#445566' && P().nodes[0].headColor === '#aa0044' && nodeSVG(P().nodes[0], P(), true).indexOf('stroke="#445566"') >= 0 && nodeSVG(P().nodes[0], P(), true).indexOf('fill="#aa0044"') >= 0;
          document.querySelector('#props [data-shared="headColor"] [data-clear]').click();
          const cleared = !P().nodes[0].headColor && nodeSVG(P().nodes[0], P(), true).indexOf('fill="#445566"') >= 0;
          P().nodes[0].headColor = '#aa0044';
          const saved = JSON.parse(projectJSON());
          const old = saved.doc.pages.root.nodes.find(it => it.type === 'dimArrow');
          delete old.rulerGap; delete old.rulerStep; delete old.rulerStart; delete old.rulerMinor; delete old.rulerUnit; delete old.rulerText; delete old.rulerSide;
          old.w = 100; old.h = 48; old.distMode = 'fixed'; old.distText = '12 m';
          loadDoc(saved.doc);
          const legacy = P().nodes.find(it => it.type === 'dimArrow');
          const gL = rulerGeom(legacy);
          const legacySvg = diagramSVG(P(), true);
          document.getElementById('pal-q').value = '箭头';
          document.getElementById('pal-q').dispatchEvent(new Event('input', { bubbles: true }));
          const thumb = document.getElementById('palette').innerHTML;
          P().nodes = [mkNode({ type: 'dimArrow', x: 160, y: 220, w: 240, h: 72, text: '', stroke: '#1F5FBF', sw: 2.4, headColor: '#C4552A', rulerStart: 0, rulerStep: 10, rulerGap: 48, rulerMinor: 4, rulerUnit: 'm', rulerText: '0,10,25' })];
          P().links = []; P().noLegend = true;
          selectNodes([P().nodes[0].id]); render(); fit();
          const anchor = document.getElementById('p-dist').closest('.row');
          document.getElementById('props').scrollTop = Math.max(0, anchor.offsetTop - 120);
          const thumbItem = [].slice.call(document.querySelectorAll('#palette .pitem')).filter(el => el.textContent.indexOf('距离箭头') >= 0)[0];
          if (thumbItem) thumbItem.scrollIntoView({ block: 'center' });
          const toast = document.getElementById('toast');
          if (toast) { toast.style.transition = 'none'; toast.style.opacity = '0'; toast.classList.remove('show'); toast.textContent = ''; }
          document.body.style.zoom = '1.5';
          const rows = [].slice.call(document.querySelectorAll('#props .row'));
          let overlap = false;
          for (let i = 0; i < rows.length; i++) {
            const a = rows[i].getBoundingClientRect();
            if (a.height < 2) continue;
            const fs = parseFloat(getComputedStyle(rows[i].querySelector('label') || rows[i]).fontSize);
            if (!(fs >= 12)) overlap = true;
            for (let j = i + 1; j < rows.length; j++) {
              const b = rows[j].getBoundingClientRect();
              const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
              const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
              if (ox > 1 && oy > 1) overlap = true;
            }
          }
          document.body.style.zoom = '';
          return {
            xs0, labels0, gap0, shown0, count0: xs0.length,
            xs1, labels1, gap1, shown1, count1: xs1.length, tickLines, upright, panel, edited,
            customDist, partial, exact, distance, colorNode, colorDio, colorFile, keptHead, cleared,
            svgTicks, dio,
            pptHas: pptText.indexOf('>20<') >= 0 && pptText.indexOf('60 m') >= 0,
            vsdHas: vsdText.indexOf('>20<') >= 0 && vsdText.indexOf('60 m') >= 0,
            png: png && png.size > 1000,
            legacy: { gone: !legacy.distMode && !legacy.distText, label: dimLabel(legacy), head: legacy.headColor, count: gL.majors.length, gap: gL.majors.length > 1 ? gL.majors[1].x - gL.majors[0].x : 0, svg: legacySvg.indexOf('10 m') >= 0 && legacySvg.indexOf('12 m') < 0, minors: gL.minors.length > 0 },
            thumb: thumb.indexOf('>0<') >= 0 && thumb.indexOf('>10<') >= 0 && thumb.indexOf('>20<') >= 0 && thumb.indexOf('距离箭头') >= 0,
            overlap
          };
        }''')
        assert result['count0'] == 5 and result['gap0'] == 40, result
        assert result['labels0'] == ['0', '10', '25', '40', '55 m'], result
        assert result['shown0'] == result['labels0'], result
        assert result['count1'] == 7 and result['gap1'] == 40, result
        assert result['xs1'][:5] == result['xs0'], result
        assert result['labels1'][0] == '0' and result['labels1'][-1].endswith(' m'), result
        assert result['shown1'] == result['labels1'], result
        assert result['tickLines'] > result['count1'], result
        assert result['upright'] and result['panel'], result
        assert result['edited'][:3] == ['0', '10', '20'], result
        assert '20' in result['svgTicks'] and '60 m' in result['svgTicks'], result
        assert result['dio']['type'] == 'dimArrow' and result['dio']['step'] == 10 and result['dio']['gap'] == 40, result
        assert result['dio']['text'] == '0,10,20' and result['dio']['ticks'] > 4 and result['dio']['nums'] and result['dio']['line'], result
        assert result['customDist'] and result['partial'] and result['exact'] and result['distance'], result
        assert result['colorNode'] and result['colorDio'] and result['colorFile'] and result['keptHead'] and result['cleared'], result
        assert result['pptHas'] and result['vsdHas'] and result['png'], result
        assert result['legacy']['gone'] and result['legacy']['label'] == '10 m' and result['legacy']['head'] == '#aa0044' and result['legacy']['count'] >= 2 and result['legacy']['svg'] and result['legacy']['minors'], result
        assert result['thumb'] and result['overlap'] is False, result
        assert not errors, errors
        page.wait_for_timeout(250)
        page.screenshot(path=str(SHOT / 'ruler-arrow.png'))
        browser.close()
        print('ruler_arrow_test ok')


if __name__ == '__main__':
    main()
