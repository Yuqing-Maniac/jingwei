"""画布背景：锁定层、导出和点选都走真实页面。"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get('JW_TEST_URL', (ROOT / 'dist' / 'offline.html').as_uri())


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(URL)
        page.wait_for_function('typeof CanvasBg === "function" || (window.CanvasBg && typeof CanvasBg.markup === "function")')
        page.wait_for_selector('#b-bg')
        result = page.evaluate('''async () => {
          const fail = [];
          const check = (ok, msg) => { if (!ok) fail.push(msg); };
          check(!document.querySelector('#world g.cbg'), 'demo has no background layer');
          const btn = document.getElementById('b-bg');
          const theme = document.getElementById('b-theme');
          check(btn && btn.textContent === '背景', 'toolbar button label');
          check(!!(btn && theme && (btn.compareDocumentPosition(theme) & Node.DOCUMENT_POSITION_FOLLOWING)), 'button sits before theme');
          btn.click();
          const dlg = document.getElementById('cbg-dlg');
          check(dlg && dlg.style.display === 'flex', 'dialog opens');
          const apply = [...dlg.querySelectorAll('button')].find(b => b.textContent === '应用并锁定');
          apply.click();
          check(P().canvasBg && P().canvasBg.locked === true, 'apply writes a locked background');
          check(document.getElementById('toast').textContent === '背景已锁定，点选图元时不会碰到它', 'lock toast');
          undo();
          check(!P().canvasBg, 'undo drops the background');
          const clear = [...dlg.querySelectorAll('button')].find(b => b.textContent === '清除背景');
          apply.click();
          clear.click();
          check(!P().canvasBg, 'clear removes the background');
          [...dlg.querySelectorAll('button')].find(b => b.textContent === '关闭').click();
          check(dlg.style.display === 'none', 'dialog closes');
          P().canvasBg = {
            locked: false,
            grad: { kind: 'linear', angle: 90, stops: [{ at: 0, color: '#112233', opacity: 1 }, { at: 1, color: '#88AADD', opacity: 0.4 }] },
            grid: { show: true, color: '#556677', opacity: 0.6, gap: 36, persp: 40 }
          };
          render();
          const g = document.querySelector('#world g.cbg');
          check(!!g, 'render paints g.cbg');
          check(g && /pointer-events\\s*[:=]\\s*["']?none/i.test(g.outerHTML), 'layer pointer-events none');
          check(g && !g.querySelector('[data-id]') && !g.hasAttribute('data-id'), 'layer has no data-id');
          const nodes = [...document.querySelectorAll('#world [data-id]')];
          let aimed = null;
          for (const node of nodes) {
            const bb = node.getBoundingClientRect();
            if (bb.width < 8 || bb.height < 8) continue;
            const hit = document.elementFromPoint(bb.x + bb.width / 2, bb.y + bb.height / 2);
            const owner = hit && hit.closest ? hit.closest('[data-id]') : null;
            if (owner && owner.getAttribute('data-id') === node.getAttribute('data-id') && !(hit.closest && hit.closest('g.cbg'))) {
              aimed = node.getAttribute('data-id');
              break;
            }
          }
          check(!!aimed, 'hit stays on the diagram node');
          const svg = exportSVGString(P(), false).str;
          check(svg.indexOf('linearGradient') >= 0 || svg.indexOf('#112233') >= 0, 'svg export contains the gradient');
          const raw = projectJSON();
          check(raw.indexOf('canvasBg') >= 0, 'project json stores canvasBg');
          const parsed = JSON.parse(raw);
          parsed.doc.pages[cur].canvasBg.locked = false;
          loadDoc(parsed.doc);
          check(P().canvasBg && P().canvasBg.locked === true, 'loadDoc keeps the background locked');
          check(P().canvasBg.grad.stops[0].color === '#112233', 'loadDoc keeps the color');
          const stage = document.getElementById('svg').getBoundingClientRect();
          let spot = null;
          for (let y = stage.top + 4; y < stage.bottom && !spot; y += 18) {
            for (let x = stage.left + 4; x < stage.right; x += 18) {
              const el = document.elementFromPoint(x, y);
              if (!el || (el.closest && (el.closest('[data-id]') || el.closest('[data-link]') || el.closest('#crumb') || el.closest('#zoombox')))) continue;
              spot = { x: x, y: y };
              break;
            }
          }
          return { fail, spot, errors: [] };
        }''')
        if result['fail']:
            raise SystemExit('ui checks failed: ' + '; '.join(result['fail']))
        if not result['spot']:
            raise SystemExit('no empty sheet point to click')
        page.mouse.click(result['spot']['x'], result['spot']['y'])
        clicked = page.evaluate('''() => ({ size: sel.size, ids: [...sel] })''')
        if clicked['size'] != 0:
            raise SystemExit('empty sheet click selected ' + str(clicked))
        heavy = page.evaluate('''async () => {
          const fail = [];
          const check = (ok, msg) => { if (!ok) fail.push(msg); };
          P().canvasBg = {
            grad: { kind: 'linear', angle: 0, stops: [
              { at: 0, color: '#101820', opacity: 1 },
              { at: 0.5, color: '#335577', opacity: 0.6 },
              { at: 1, color: '#88AADD', opacity: 1 }
            ] },
            grid: { show: true, color: '#223344', opacity: 0.7, gap: 40, persp: 100 }
          };
          render();
          const dio = DrawIO.exportString([P()]);
          check(dio.indexOf('data:image/png,') >= 0 && dio.indexOf('data:image/png;base64') < 0, 'draw.io png style has no semicolon');
          check(dio.indexOf('ht_canvasBg') >= 0, 'draw.io stores the background model');
          check(dio.indexOf('ht_part=&quot;canvasbg&quot;') >= 0 || dio.indexOf('ht_part="canvasbg"') >= 0, 'draw.io marks sheet cells');
          const n0 = P().nodes.length;
          const back = await DrawIO.importText(dio);
          check(back.pages[0].canvasBg && back.pages[0].canvasBg.grad.stops.length === 3, 'import restores the gradient');
          check(back.pages[0].nodes.length === n0, 'sheet cells do not become nodes');
          const cell = (n, v, u) => `<Cell N='${n}' V='${v}'${u ? ` U='${u}'` : ''}/>`;
          const num = v => (+v).toFixed(6);
          let seq = 1;
          const b = contentBBox(P());
          const pad = 20, f = 1 / 96, PH = (b.h + pad * 2) * f;
          const X = v => (v - b.x + pad) * f, Y = v => PH - (v - b.y + pad) * f;
          const vsdx = CanvasBg.vsdxShapes(P(), {
            box: { x: b.x - pad, y: b.y - pad, w: b.w + pad * 2, h: b.h + pad * 2 },
            f, X, Y, cell, num, id: () => seq++, zip: {}, rels: []
          }).join('');
          check(vsdx.indexOf('FillGradient') >= 0, 'vsdx gradient section');
          check(vsdx.indexOf('GradientStopColorTrans') >= 0, 'vsdx stop transparency');
          check((vsdx.match(/LineTo/g) || []).length > 1, 'perspective grid has more than one line');
          const shapes = { n: 0, image: 0 };
          const slide = {
            addShape() { shapes.n += 1; },
            addImage() { shapes.image += 1; }
          };
          const pptx = { ShapeType: { rect: 'rect', line: 'line' } };
          const box = { x: 0, y: 0, w: 180, h: 120 };
          const map = { X: v => v, Y: v => v, S: v => v, box };
          P().canvasBg = { grad: { kind: 'linear', angle: 0, stops: [{ at: 0, color: '#112233', opacity: 0.5 }, { at: 1, color: '#AABBCC', opacity: 0.5 }] }, grid: { show: true, color: '#667788', opacity: 0.4, gap: 30, persp: 0 } };
          check(CanvasBg.plan(P().canvasBg, 'pptx') === 'raster', 'pptx sheet is raster');
          await CanvasBg.paintPptx(slide, pptx, P(), map);
          check(shapes.n === 0 && shapes.image === 1, 'pptx uses one image');
          const linksBefore = P().links.length;
          const nodesBefore = P().nodes.length;
          P().canvasBg = { grad: { kind: 'linear', angle: 90, stops: [{ at: 0, color: '#112233', opacity: 1 }, { at: 1, color: '#AABBCC', opacity: 1 }] }, grid: { show: true, color: '#334455', opacity: 0.8, gap: 48, persp: 100 } };
          const dioN = DrawIO.exportString([P()]);
          check(dioN.indexOf('edge="1"') >= 0 && dioN.indexOf('sourcePoint') >= 0, 'perspective grid is a floating edge');
          const backN = await DrawIO.importText(dioN);
          check(backN.pages[0].links.length === linksBefore, 'grid edges are not links');
          check(backN.pages[0].nodes.length === nodesBefore, 'grid edges are not nodes');
          let hooked = false;
          if (typeof JSZip !== 'undefined') {
            P().nodes = P().nodes.filter(n => n.type === 'text').slice(0, 1);
            P().links = [];
            if (!P().nodes.length) P().nodes.push(mkNode({ type: 'rect', x: 40, y: 40, w: 120, h: 60, text: '块' }));
            P().canvasBg.grad.kind = 'linear';
            const got = await captureExport(() => exportVSDX([P()]));
            if (got[0]) {
              const zip = await JSZip.loadAsync(await got[0].data.arrayBuffer());
              const xml = await zip.file('visio/pages/page1.xml').async('string');
              hooked = xml.indexOf('FillGradient') >= 0;
            }
          }
          check(hooked, 'exportVSDX writes FillGradient');
          return fail;
        }''')
        if errors:
            raise SystemExit('page errors: ' + '; '.join(errors))
        if heavy:
            raise SystemExit('export checks failed: ' + '; '.join(heavy))
        browser.close()
    print('canvasbg_ui ok')


if __name__ == '__main__':
    main()
