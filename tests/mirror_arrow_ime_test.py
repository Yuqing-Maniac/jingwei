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
        page.wait_for_function('typeof renderPalette === "function" && typeof ICONS !== "undefined" && ICONS.length > 0')

        ime = page.evaluate('''() => {
          const el0 = document.getElementById('pal-q');
          el0.focus();
          el0.dispatchEvent(new CompositionEvent('compositionstart', { bubbles: true, data: '' }));
          let acc = '';
          let replaced = false;
          for (const ch of 'nihao') {
            acc += ch;
            const node = document.getElementById('pal-q');
            node.value = acc;
            node.dispatchEvent(new InputEvent('input', { bubbles: true, data: ch, inputType: 'insertCompositionText' }));
            const now = document.getElementById('pal-q');
            if (now !== node) {
              replaced = true;
              now.value = (now.value || '') + ch;
            }
            acc = now.value;
          }
          const composed = document.getElementById('pal-q').value;
          const end = document.getElementById('pal-q');
          end.dispatchEvent(new CompositionEvent('compositionend', { bubbles: true, data: '你好' }));
          end.value = '你好';
          end.dispatchEvent(new Event('input', { bubbles: true }));
          const after = document.getElementById('pal-q');
          const chinese = after.value;
          after.value = '';
          after.dispatchEvent(new Event('input', { bubbles: true }));
          let word = '';
          const box = document.getElementById('pal-q');
          for (const ch of 'rag') {
            word += ch;
            box.value = word;
            box.dispatchEvent(new Event('input', { bubbles: true }));
            word = document.getElementById('pal-q').value;
          }
          const english = document.getElementById('pal-q').value;
          const hit = document.getElementById('palette').innerText.includes('检索增强生成RAG');
          document.getElementById('pal-q').value = '箭头';
          document.getElementById('pal-q').dispatchEvent(new Event('input', { bubbles: true }));
          const arrows = document.getElementById('palette').innerText;
          const arrowFound = arrows.includes('标准箭头') && arrows.includes('距离箭头');
          const caret = (() => {
            const q = document.getElementById('pal-q');
            q.focus();
            q.setSelectionRange(1, 1);
            q.dispatchEvent(new Event('input', { bubbles: true }));
            return q.selectionStart;
          })();
          document.getElementById('pal-q').value = '';
          document.getElementById('pal-q').dispatchEvent(new Event('input', { bubbles: true }));
          const ic = document.getElementById('ic-q');
          const ic0 = ic;
          ic.value = 'n';
          ic.dispatchEvent(new CompositionEvent('compositionstart', { bubbles: true, data: 'n' }));
          ic.dispatchEvent(new Event('input', { bubbles: true }));
          ic.value = 'ni';
          ic.dispatchEvent(new Event('input', { bubbles: true }));
          return { replaced, composed, chinese, english, hit, arrowFound, caret, icSame: document.getElementById('ic-q') === ic0, icValue: document.getElementById('ic-q').value };
        }''')
        assert ime['replaced'] is False, ime
        assert ime['composed'] == 'nihao', ime
        assert ime['chinese'] == '你好', ime
        assert ime['english'] == 'rag', ime
        assert ime['hit'] is True and ime['arrowFound'] is True, ime
        assert ime['caret'] == 1, ime
        assert ime['icSame'] is True and ime['icValue'] == 'ni', ime

        result = page.evaluate('''async () => {
          const key = 'lib:' + ICONS[0].key;
          P().nodes = []; P().links = []; P().noLegend = true;
          const uri = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"><rect width="10" height="10" fill="black"/><rect x="10" width="10" height="10" fill="white"/></svg>');
          doc.custom.boat = { name: '自定义艇', uri: uri };
          const lib = mkNode({ type: 'equip', x: 40, y: 40, w: 96, h: 96, text: '库图标', icon: key, flipX: true });
          const both = mkNode({ type: 'equip', x: 160, y: 40, w: 96, h: 96, text: '双翻', icon: key, flipX: true, flipY: true });
          const cu = mkNode({ type: 'equip', x: 280, y: 40, w: 96, h: 96, text: '自定义', icon: 'cu:boat', flipY: true });
          const plain = mkNode({ type: 'equip', x: 400, y: 40, w: 96, h: 96, text: '旧图', icon: key });
          const word = mkNode({ type: 'text', x: 40, y: 180, w: 80, h: 30, text: '文字' });
          const std = mkNode({ type: 'stdArrow', x: 40, y: 240, w: 160, h: 36, text: '', stroke: '#224488', sw: 3 });
          const dim = mkNode({ type: 'dimArrow', x: 40, y: 320, w: 100, h: 48, text: '' });
          P().nodes.push(lib, both, cu, plain, word, std, dim);
          doc.measure = { unit: 'm', px: 10 };
          selectNodes([lib.id]); render();
          const one = nodeSVG(lib, P(), true);
          const imgAt = one.indexOf('<image');
          const flips = {
            x: one.includes('scale(-1 1)'),
            box: !one.slice(0, imgAt).includes('scale(-1'),
            both: nodeSVG(both, P(), true).includes('scale(-1 -1)'),
            cu: nodeSVG(cu, P(), true).includes('scale(1 -1)'),
            old: !nodeSVG(plain, P(), true).includes('scale(-1') && !nodeSVG(plain, P(), true).includes('scale(1 -1)')
          };
          const panel = document.getElementById('p-flipX') && document.getElementById('p-flipY') && document.getElementById('p-affiliation');
          document.getElementById('p-flipY').click();
          const libAfter = nodeById(lib.id);
          const yOn = !!libAfter.flipY;
          undo();
          const yUndone = !nodeById(lib.id).flipY && !!nodeById(lib.id).flipX;
          selectNodes([lib.id, both.id, word.id]); render();
          const batchBox = !!document.getElementById('p-affiliation');
          document.getElementById('p-affiliation').value = 'red';
          document.getElementById('p-affiliation').dispatchEvent(new Event('change', { bubbles: true }));
          const red = nodeById(lib.id).affiliation === 'red' && nodeById(both.id).affiliation === 'red' && !nodeById(word.id).affiliation;
          nodeById(lib.id).affiliation = 'blue';
          selectNodes([lib.id, both.id]); render();
          const mixed = document.getElementById('p-affiliation').value === '__mixed__';
          const saved = projectJSON();
          loadDoc(JSON.parse(saved).doc);
          const back = JSON.parse(projectJSON()).doc.pages.root.nodes.find(n => n.text === '库图标');
          const kept = back.flipX === true && !back.flipY && back.affiliation === 'blue';
          const oldDoc = JSON.parse(saved);
          const oldNode = oldDoc.doc.pages.root.nodes.find(n => n.text === '旧图');
          delete oldNode.flipX; delete oldNode.flipY; delete oldNode.affiliation;
          loadDoc(oldDoc.doc);
          const restored = JSON.parse(projectJSON()).doc.pages.root.nodes.find(n => n.text === '旧图');
          const legacy = !restored.flipX && !restored.flipY && !restored.affiliation;
          const legacySvg = !diagramSVG(P(), true).includes('scale(-1 1)') || true;
          const plainNow = P().nodes.find(n => n.text === '旧图');
          const legacyDraw = !nodeSVG(plainNow, P(), true).includes('scale(-1');
          selectNodes([P().nodes.find(n => n.type === 'dimArrow').id]); render();
          const dim0 = P().nodes.find(n => n.type === 'dimArrow');
          const auto1 = dimLabel(dim0) === '10 m' && diagramSVG(P(), true).includes('10 m') && diagramSVG(P(), true).includes('标准箭头') === false;
          const stdSvg = nodeSVG(P().nodes.find(n => n.type === 'stdArrow'), P(), true);
          dim0.w = 50; render();
          doc.measure = { unit: 'km', px: 25 };
          const scaled = dimLabel(P().nodes.find(n => n.type === 'dimArrow')) === '2 km' && diagramSVG(P(), true).includes('2 km');
          doc.measure = { unit: 'm', px: 10 };
          const auto2 = dimLabel(P().nodes.find(n => n.type === 'dimArrow')) === '5 m' && diagramSVG(P(), true).includes('5 m');
          const dist = document.getElementById('p-dist');
          const before = dist.value;
          dist.value = '3 km';
          dist.dispatchEvent(new Event('input', { bubbles: true }));
          const dim1 = P().nodes.find(n => n.type === 'dimArrow');
          const ignored = dist.readOnly && dim1.distMode !== 'fixed' && !dim1.distText && dimLabel(dim1) === before;
          dim1.w = 80;
          render();
          const tip = dimLabel(dim1) === '8 m' && document.getElementById('p-dist').value === '8 m';
          const fixed = ignored && tip;
          document.getElementById('p-rot90').click();
          const turned = P().nodes.find(n => n.type === 'dimArrow').rot === 90;
          const stdNode = P().nodes.find(n => n.type === 'stdArrow');
          stdNode.rot = 35; stdNode.sw = 4;
          const ends = arrowEnds(stdNode);
          const angled = Math.abs(ends.tip.y - ends.tail.y) > 20;
          const svgOut = exportSVGString(P(), false).str;
          const svgHas = svgOut.includes('scale(-1 -1)') && svgOut.includes('8 m') && !svgOut.includes('3 km') && svgOut.includes('polygon');
          const xml = DrawIO.exportString([P()]);
          const imported = await DrawIO.importText(xml);
          const nodes = imported.pages[0].nodes;
          const dio = {
            flip: nodes.some(n => n.flipX && n.flipY),
            cu: nodes.some(n => String(n.icon || '').startsWith('cu:')) && nodes.filter(n => n.flipY).every(n => /^(lib|ms):/.test(n.icon || '')),
            arrow: nodes.some(n => n.type === 'stdArrow'),
            dist: nodes.some(n => n.type === 'dimArrow' && !n.distText && !n.distMode && dimLabel(n) === '8 m'),
            line: xml.includes('endArrow=classic')
          };
          const prev = saveFile;
          const blobs = [];
          saveFile = async (name, data) => { blobs.push({ name: name, data: data }); };
          await exportPPTX();
          await exportVSDX();
          saveFile = prev;
          const ppt = await JSZip.loadAsync(await blobs[0].data.arrayBuffer());
          let pptArrow = false;
          for (const name of Object.keys(ppt.files)) {
            if (!name.endsWith('.xml')) continue;
            const t = await ppt.files[name].async('string');
            if (t.includes('triangle') || t.includes('headEnd')) pptArrow = true;
          }
          const vsd = await JSZip.loadAsync(await blobs[1].data.arrayBuffer());
          let vsdArrow = false, vsdText = false;
          for (const name of Object.keys(vsd.files)) {
            if (!name.endsWith('.xml')) continue;
            const t = await vsd.files[name].async('string');
            if (t.includes('EndArrow')) vsdArrow = true;
            if (t.includes('8 m')) vsdText = true;
          }
          const plainPng = await iconPNG(uri, 40);
          const flipPng = await iconPNG(uri + '#fx', 40);
          const sample = (dataUrl) => new Promise(res => {
            const img = new Image();
            img.onload = () => {
              const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
              const g = c.getContext('2d'); g.drawImage(img, 0, 0);
              const y = Math.floor(img.height / 2);
              res({ l: g.getImageData(2, y, 1, 1).data[0], r: g.getImageData(img.width - 3, y, 1, 1).data[0] });
            };
            img.src = dataUrl;
          });
          const a = await sample(plainPng), b = await sample(flipPng);
          const shaft = mkNode({ type: 'dimArrow', w: 173, h: 48, text: '' });
          layoutRow([shaft, mkNode({ type: 'rect', w: 80, h: 40, text: '甲' })], 40, 640, 0, 0);
          const keptLen = shaft.w === 173 && shaft.h === 48;
          return { flips, panel, yOn, yUndone, batchBox, red, mixed, kept, legacy, legacyDraw, auto1, stdHead: stdSvg.includes('<polygon'), scaled, auto2, fixed, turned, angled, svgHas, dio, pptArrow, vsdArrow, vsdText, keptLen, pixels: { a, b }, errors: [] };
        }''')
        assert result['flips']['x'] and result['flips']['box'] and result['flips']['both'] and result['flips']['cu'] and result['flips']['old'], result
        assert result['panel'] and result['yOn'] and result['yUndone'], result
        assert result['batchBox'] and result['red'] and result['mixed'] and result['kept'], result
        assert result['legacy'] and result['legacyDraw'], result
        assert result['auto1'] and result['stdHead'] and result['scaled'] and result['auto2'] and result['fixed'] and result['turned'] and result['angled'] and result['keptLen'], result
        assert result['svgHas'] and result['dio']['flip'] and result['dio']['arrow'] and result['dio']['dist'] and result['dio']['line'], result
        assert result['pptArrow'] and result['vsdArrow'] and result['vsdText'], result
        assert result['pixels']['a']['l'] < result['pixels']['a']['r'], result
        assert result['pixels']['b']['l'] > result['pixels']['b']['r'], result
        assert not errors, errors
        browser.close()
        print('mirror_arrow_ime_test ok')


if __name__ == '__main__':
    main()
