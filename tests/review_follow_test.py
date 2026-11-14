"""扇形命中、同色渐变只改填充、半透明回读，以及组合图标和阵列的红蓝阵营。"""
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
        page.wait_for_function('typeof outlineHit === "function" && typeof Combo !== "undefined"')
        result = page.evaluate('''async () => {
          const p = P();
          p.nodes = p.nodes.filter(n => n.type === 'legend' || n.type === 'tblock');
          p.links = [];
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
          const dio = DrawIO.exportString([P()]);
          const prev = saveFile;
          const blobs = [];
          saveFile = async (name, data) => { blobs.push(data); };
          await exportPPTX();
          const ppt2 = await paintPptGradients(blobs[0]);
          await exportVSDX();
          saveFile = prev;
          const ppt = await JSZip.loadAsync(await ppt2.arrayBuffer());
          let gradN = 0, lineGrad = 0, noFill = 0;
          for (const name of Object.keys(ppt.files)) {
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
          let vsdOk = false;
          for (const name of Object.keys(vsd.files)) {
            if (!name.endsWith('.xml')) continue;
            const t = await vsd.files[name].async('string');
            if (t.indexOf('六边') >= 0 || t.indexOf('宽扇') >= 0) vsdOk = true;
          }
          let fadeSeen = false;
          const ire = /image=data:image\\/svg\\+xml,([A-Za-z0-9+/=]+)/g;
          let im;
          while ((im = ire.exec(dio))) {
            try { if (atob(im[1]).indexOf('stop-opacity="0.4"') >= 0) fadeSeen = true; } catch (e) {}
          }
          return {
            hit: hit && { x: Math.round(hit.x), y: Math.round(hit.y) },
            differ: redUri !== neutral && blueUri !== doc.custom[grp.slice(3)].uri,
            plainSame: iconURI(form) === neutral,
            show: NODE_FIELDS.affiliation.show([plain, one]),
            svgHas: svg.indexOf('红阵列') >= 0,
            gradN, lineGrad, noFill, vsdOk, fadeSeen,
            fade: dio.indexOf('ht_gradA="0.4"') >= 0,
            pie: dio.indexOf('endAngle=0.7500') >= 0,
            noDefaults: typeof readDefaults !== 'function' && typeof scenePack !== 'function',
            ops: TEMPLATES.filter(t => t.group === '作战场景').map(t => t.id).sort().join(',')
          };
        }''')
        browser.close()
    print(result)
    assert not errors, errors
    assert result['hit'] and result['hit']['x'] < 198 and result['hit']['y'] < 90, result['hit']
    assert result['differ'] and result['plainSame'] and result['show'] and result['svgHas']
    assert result['gradN'] >= 2 and result['lineGrad'] == 0 and result['noFill'] >= 1 and result['vsdOk']
    assert result['fade'] and result['fadeSeen'] and result['pie']
    assert result['noDefaults']
    assert result['ops'] == 'scn-assault,scn-contact,scn-patrol'
    print('review_follow_test ok')


if __name__ == '__main__':
    main()
