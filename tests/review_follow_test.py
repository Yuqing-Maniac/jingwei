"""审查项与新增行为：扇形命中、同色渐变、半透明、编队阵营、新建默认、场景模板、画布背景。"""
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
        page.wait_for_function('typeof outlineHit === "function" && typeof Combo !== "undefined" && typeof scenePack === "function"')
        result = page.evaluate('''async () => {
          const p = P();
          p.nodes = p.nodes.filter(n => n.type === 'legend' || n.type === 'tblock');
          p.links = [];
          const old = mkNode({ type: 'equip', icon: 'lib:uav_quad', text: '已有', w: 96, h: 96, x: 0, y: 0 });
          p.nodes.push(old);
          const sector = mkNode({ type: 'sector', text: '扇区', w: 200, h: 200, sweep: 60, x: 0, y: 0 });
          const hit = outlineHit(sector, 'r', { x: 200, y: 100 });
          const wide = mkNode({ type: 'sector', text: '宽扇', w: 120, h: 100, sweep: 270, x: 40, y: 40, fill: '#2255aa', stroke: '#101820' });
          const a = mkNode({ type: 'ellipse', text: '甲', w: 80, h: 60, x: 300, y: 40, fill: '#112233', grad: 'v', gradTo: '#abcdef', gradA: 0.4, stroke: '#101820' });
          const b = mkNode({ type: 'ellipse', text: '乙', w: 80, h: 60, x: 420, y: 40, fill: '#112233', grad: 'v', gradTo: '#abcdef', gradA: 0.4, stroke: '#101820', noLine: true });
          const hex = mkNode({ type: 'hexagon', text: '六边', w: 90, h: 70, x: 540, y: 40 });
          p.nodes.push(sector, wide, a, b, hex);
          const key = (ICONS.find(i => i.variants && i.variants.red) || {}).key;
          const form = Combo.formationIcon('lib:' + key, 3, 'grid', { name: '测试阵列' });
          const grp = Combo.groupIcon([{ icon: 'lib:' + key, x: 0, y: 0, s: 1 }, { icon: 'lib:' + key, x: 1.2, y: 0, s: 1 }], '测试组合');
          const plain = mkNode({ type: 'equip', icon: form, text: '未着色阵列', w: 140, h: 80, x: 20, y: 260 });
          const tint = mkNode({ type: 'equip', icon: form, text: '红阵列', w: 140, h: 80, x: 180, y: 260, affiliation: 'red' });
          const mix = mkNode({ type: 'equip', icon: grp, text: '蓝组合', w: 140, h: 80, x: 340, y: 260, affiliation: 'blue' });
          const one = mkNode({ type: 'equip', icon: 'lib:' + key, text: '单图标', w: 80, h: 80, x: 500, y: 260 });
          p.nodes.push(plain, tint, mix, one);
          NODE_FIELDS.affiliation.set(tint, 'red');
          NODE_FIELDS.affiliation.set(mix, 'blue');
          NODE_FIELDS.affiliation.set(one, 'blue');
          const neutral = doc.custom[form.slice(3)].uri;
          const redUri = iconURI(form, 'red');
          const blueUri = iconURI(grp, 'blue');
          const svg = diagramSVG(p, true);
          localStorage.setItem('hongtu.defaults', JSON.stringify({ frame: 'off', affiliation: 'red', fill: '#abcdef', stroke: '', noLine: false, size: 15, sw: 3 }));
          addNode({ type: 'equip', icon: 'lib:' + key, text: '新建', w: 96, h: 96 }, 40, 400);
          addNode({ type: 'stdArrow', w: 120, h: 28, text: '' }, 200, 420);
          const made = P().nodes.filter(n => n.text === '新建' || n.type === 'stdArrow').slice(-2);
          const fresh = made.find(n => n.text === '新建'), arrow = made.find(n => n.type === 'stdArrow');
          const ops = TEMPLATES.filter(t => t.group === '作战场景').map(t => {
            const d = t.build();
            const nodes = d.pages.root.nodes;
            return { id: t.id, n: nodes.length, sides: nodes.filter(n => n.affiliation).map(n => n.affiliation), types: nodes.map(n => n.type), custom: Object.keys(d.custom || {}).length };
          });
          P().scene = { stops: ['#112233', '#445566', '#778899'], opacity: 0.5, dir: 'v', grid: 40, persp: 0.45, gridColor: '#99aabb', gridOpacity: 0.4, locked: true };
          const sceneSvg = diagramSVG(P(), true);
          const exp = exportSVGString(P(), false).str;
          const dio = DrawIO.exportString([P()]);
          const back = await DrawIO.importText(dio);
          const prev = saveFile;
          const blobs = [];
          saveFile = async (name, data) => { blobs.push(data); };
          await exportPPTX();
          const ppt2 = await paintPptGradients(blobs[0]);
          await exportVSDX();
          saveFile = prev;
          const ppt = await JSZip.loadAsync(await ppt2.arrayBuffer());
          let gradN = 0, lineGrad = 0, noFill = 0, pics = 0;
          for (const name of Object.keys(ppt.files)) {
            if (name.indexOf('ppt/media/') === 0) pics++;
            if (!/slide\\d+\\.xml$/.test(name)) continue;
            const t = await ppt.files[name].async('string');
            gradN += (t.match(/<a:gradFill/g) || []).length;
            const sps = t.split('</p:sp>');
            for (const sp of sps) {
              const ln = sp.split('</p:spPr>')[0] || '';
              const line = (ln.match(/<a:ln[\\s\\S]*<\\/a:ln>/) || [''])[0];
              if (line.indexOf('gradFill') >= 0) lineGrad++;
              if (line.indexOf('<a:noFill/>') >= 0) noFill++;
            }
          }
          const vsd = await JSZip.loadAsync(await blobs[1].arrayBuffer());
          let foreign = false, media = 0;
          for (const name of Object.keys(vsd.files)) {
            if (name.indexOf('visio/media/') === 0) media++;
            if (name.endsWith('page1.xml') && (await vsd.files[name].async('string')).indexOf("Type='Foreign'") >= 0) foreign = true;
          }
          let dioScene = false;
          const ire = /image=data:image\\/svg\\+xml,([A-Za-z0-9+/=]+)/g;
          let im;
          while ((im = ire.exec(dio))) {
            try { const raw = atob(im[1]); if (raw.indexOf('jw-scene') >= 0 && raw.indexOf('#778899') >= 0) dioScene = true; } catch (e) {}
          }
          const fade = dio.indexOf('ht_gradA="0.4"') >= 0;
          let fadeSeen = false;
          const ire2 = /image=data:image\\/svg\\+xml,([A-Za-z0-9+/=]+)/g;
          while ((im = ire2.exec(dio))) {
            try { if (atob(im[1]).indexOf('stop-opacity="0.4"') >= 0) fadeSeen = true; } catch (e) {}
          }
          return {
            errors: [],
            hit: hit && { x: Math.round(hit.x), y: Math.round(hit.y) },
            key, differ: redUri !== neutral && blueUri !== doc.custom[grp.slice(3)].uri,
            plainSame: iconURI(form) === neutral,
            show: NODE_FIELDS.affiliation.show([plain, one]),
            svgRed: svg.indexOf(redUri.slice(0, 40)) >= 0,
            oldPlain: !old.affiliation && !old.noBox && old.fill == null,
            fresh: fresh && { noBox: !!fresh.noBox, affiliation: fresh.affiliation, fill: fresh.fill, size: fresh.size },
            arrowSw: arrow && arrow.sw,
            ops,
            scene: sceneSvg.indexOf('linearGradient') >= 0 && (sceneSvg.match(/<stop /g) || []).length >= 3 && sceneSvg.indexOf('pointer-events="none"') >= 0 && (sceneSvg.match(/<line /g) || []).length > 4,
            exp: exp.indexOf('#778899') >= 0,
            dioScene, fade, fadeSeen,
            back: back.pages[0].scene && back.pages[0].scene.stops && back.pages[0].scene.locked === true,
            gradN, lineGrad, noFill, pics, foreign, media,
            pie: dio.indexOf('endAngle=0.7500') >= 0
          };
        }''')
        browser.close()
    print(result)
    assert not errors, errors
    assert result['hit'] and result['hit']['x'] < 198 and result['hit']['y'] < 90, result['hit']
    assert result['differ'] and result['plainSame'] and result['show']
    assert result['fresh']['noBox'] and result['fresh']['affiliation'] == 'red' and result['fresh']['fill'] == '#abcdef' and result['fresh']['size'] == 15
    assert result['oldPlain'] and result['arrowSw'] == 3
    assert len(result['ops']) == 2 and all(o['n'] > 4 and o['custom'] >= 1 and 'blue' in o['sides'] and 'red' in o['sides'] for o in result['ops'])
    assert result['scene'] and result['exp'] and result['dioScene'] and result['back']
    assert result['fade'] and result['fadeSeen'] and result['pie']
    assert result['gradN'] >= 2 and result['lineGrad'] == 0 and result['noFill'] >= 1
    assert result['pics'] >= 1 and result['foreign'] and result['media'] >= 1
    print('review_follow_test ok')


if __name__ == '__main__':
    main()
