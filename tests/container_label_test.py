#!/usr/bin/env python3
"""Container title slab. Positions are checked against the frame, the SVG, and Office output."""
import os
import pathlib
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
fails = []


def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))


def launch(pw):
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox']}
    if exe:
        kw['executable_path'] = exe
    return pw.chromium.launch(**kw)


def main():
    with sync_playwright() as pw:
        browser = launch(pw)
        pg = browser.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:500]))
        pg.goto(HTML)
        pg.wait_for_selector('#svg')
        pg.wait_for_timeout(200)
        check('page loads', not errs, ' '.join(errs)[:400])

        geo = pg.evaluate("""() => {
          const band = mkNode({ type: 'band', text: '分组', x: 0, y: 0, w: 1000, h: 180 });
          const child = mkNode({ type: 'rect', text: '子', parent: band.id, x: 34, y: 0, w: 80, h: 40 });
          const lane = mkNode({ type: 'lane', text: '新的一层', x: 40, y: 6, w: 900, h: 56 });
          const group = mkNode({ type: 'group', text: '子系统', x: 0, y: 0, w: 360, h: 110 });
          const laneTop = mkNode({ type: 'lane', text: '顶层', x: 40, y: 80, w: 900, h: 56, labelSide: 't' });
          const rect = mkNode({ type: 'rect', text: '矩形', x: 20, y: 200, w: 120, h: 40 });
          loadDoc({
            name: '标题位置', theme: 'report', custom: {},
            statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' },
            pages: { root: { id: 'root', name: '总图', nodes: [band, child, lane, group, laneTop, rect], links: [] } }
          });
          const pick = t => P().nodes.find(n => n.text === t);
          const b = pick('分组'), c = pick('子'), l = pick('新的一层'), g = pick('子系统'), lt = pick('顶层');
          const fb = contFrame(b), fl = contFrame(l), fg = contFrame(g), ft = contFrame(lt);
          const sb = nodeSVG(b, P(), true), sl = nodeSVG(l, P(), true), sg = nodeSVG(g, P(), true);
          const path = (sg.match(/<path d="([^"]+)"/) || [])[1] || '';
          const glyphs = [...sb.matchAll(/<tspan x="([^"]+)"/g)].map(m => m[1]);
          const line = sl.match(/<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"/);
          const before = { x: c.x, y: c.y };
          setLabelSide(b, 't');
          const moved = { x: c.x, y: c.y, dx: c.x - before.x, dy: c.y - before.y };
          const top = contFrame(b);
          setLabelSide(b, 't');
          const again = { x: c.x, y: c.y };
          const dom = document.querySelector('#svg').innerHTML;
          return {
            band: fb.title, bandContent: fb.content, glyphs,
            bandRect: /<rect x="0" y="0" width="34" height="180" fill="/.test(sb),
            lane: fl.title, laneContent: fl.content,
            line: line ? line.slice(1).map(Number) : null,
            groupH: fg.title.h, groupContent: fg.content, path,
            laneTopH: ft.title.h, laneTopW: ft.title.w,
            moved, again, top: top.title, topContent: top.content,
            domPath: dom.indexOf(path) >= 0,
            sideStored: b.labelSide
          };
        }""")
        bt, bc = geo['band'], geo['bandContent']
        check('band slab', bt['x'] == 0 and bt['w'] == 34 and bt['h'] == 180, str(bt))
        check('band content', bc['x'] == 34 and bc['y'] == 0 and bc['w'] == 966 and bc['h'] == 180, str(bc))
        check('band glyphs', geo['glyphs'] and all(x == '17' for x in geo['glyphs']), str(geo['glyphs']))
        check('band title rect', geo['bandRect'] is True, '')
        lt, lc = geo['lane'], geo['laneContent']
        check('lane slab', lt['x'] == 40 and lt['w'] == 96 and lt['h'] == 56, str(lt))
        check('lane content', lc['x'] == 136 and lc['y'] == 6 and lc['w'] == 804 and lc['h'] == 56, str(lc))
        check('lane separator', geo['line'] == [136, 12, 136, 56], str(geo['line']))
        check('group slab height', geo['groupH'] == 26, str(geo['groupH']))
        gc = geo['groupContent']
        check('group content', gc['x'] == 0 and gc['y'] == 26 and gc['w'] == 360 and gc['h'] == 84, str(gc))
        expect_path = 'M0.65,26 V6 Q0.65,0.65 6,0.65 H354 Q359.35,0.65 359.35,6 V26 Z'
        check('group path', geo['path'] == expect_path, geo['path'])
        check('group path on canvas', geo['domPath'] is True, '')
        mv = geo['moved']
        check('child delta', mv['dx'] == -34 and mv['dy'] == 34 and mv['x'] == 0 and mv['y'] == 34, str(mv))
        check('second side is still', geo['again']['x'] == 0 and geo['again']['y'] == 34, str(geo['again']))
        top = geo['top']
        check('band top slab', top['x'] == 0 and top['y'] == 0 and top['w'] == 1000 and top['h'] == 34, str(top))
        tc = geo['topContent']
        check('band top content', tc['x'] == 0 and tc['y'] == 34, str(tc))
        check('lane top bar', geo['laneTopH'] == 28 and geo['laneTopW'] == 900, 'h=%s w=%s' % (geo['laneTopH'], geo['laneTopW']))

        panel = pg.evaluate("""() => {
          const b = P().nodes.find(n => n.text === '分组');
          const l = P().nodes.find(n => n.text === '新的一层');
          const r = P().nodes.find(n => n.text === '矩形');
          const lt = P().nodes.find(n => n.text === '顶层');
          selectNodes([b.id]); render();
          const bandProps = document.getElementById('props').innerText;
          const fresh = mkNode({ type: 'band', text: '缺省带', x: 1200, y: 0, w: 400, h: 120 });
          P().nodes.push(fresh);
          selectNodes([fresh.id]); render();
          const leftOn = !!document.querySelector('#p-labelSide button[data-v="l"].on');
          selectNodes([r.id]); render();
          const rectProps = document.getElementById('props').innerText;
          selectNodes([l.id]); render();
          const laneProps = document.getElementById('props').innerText;
          selectNodes([lt.id]); render();
          const topProps = document.getElementById('props').innerText;
          const leg = mkNode({ type: 'legend', x: 400, y: 200, w: 200, h: 60 });
          P().nodes.push(leg);
          selectNodes([leg.id]); render();
          const legProps = document.getElementById('props').innerText;
          return { bandProps, leftOn, rectProps, laneProps, topProps, legProps };
        }""")
        check('panel side on band', '标题位置' in panel['bandProps'] and panel['leftOn'] is True, panel['bandProps'][:160])
        check('panel hidden on rect', '标题位置' not in panel['rectProps'], panel['rectProps'][:120])
        check('panel hidden on legend', '标题位置' not in panel['legProps'], panel['legProps'][:120])
        check('lane width control', '标题栏宽' in panel['laneProps'], panel['laneProps'][:160])
        check('lane top hides width', '标题栏宽' not in panel['topProps'] and '标题位置' in panel['topProps'], panel['topProps'][:160])

        pg.evaluate("""() => { const b = P().nodes.find(n => n.text === '分组'); selectNodes([b.id]); render(); }""")
        pg.click('#p-labelSide button[data-v="b"]')
        clicked = pg.evaluate("""() => {
          const b = P().nodes.find(n => n.text === '分组');
          const c = P().nodes.find(n => n.text === '子');
          return { side: b.labelSide, title: contFrame(b).title, child: { x: c.x, y: c.y } };
        }""")
        check('click bottom writes side', clicked['side'] == 'b' and clicked['title']['h'] == 34 and clicked['title']['y'] == 180 - 34, str(clicked))

        saved = pg.evaluate("""() => {
          const b = P().nodes.find(n => n.text === '分组');
          setLabelSide(b, 'r');
          const raw = projectJSON();
          const wrapped = JSON.parse(raw);
          const kept = wrapped.doc.pages.root.nodes.find(n => n.text === '分组').labelSide;
          loadDoc(JSON.parse(JSON.stringify(wrapped.doc)));
          const n = P().nodes.find(x => x.text === '分组');
          const child = P().nodes.find(x => x.text === '子');
          const loaded = n.labelSide;
          const atSide = contFrame(n).title.x;
          delete n.labelSide;
          const back = contFrame(n).title;
          return {
            format: wrapped.format, kept, loaded, atSide,
            back: { x: back.x, w: back.w, h: back.h },
            child: { x: child.x, y: child.y },
            absent: !Object.prototype.hasOwnProperty.call(n, 'labelSide')
          };
        }""")
        check('json keeps side', saved['format'] == 'hongtu' and saved['kept'] == 'r' and saved['loaded'] == 'r', str(saved))
        check('delete restores left slab', saved['absent'] is True and saved['back']['x'] == 0 and saved['back']['w'] == 34 and saved['back']['h'] == 180, str(saved['back']))

        office = pg.evaluate("""async () => {
          window.__saved = [];
          window.saveFile = saveFile = async (name, data) => { window.__saved.push({ name, data }); };
          const labels = { base: '延续', new: '本步新增／重构', key: '重点关注' };
          const docOf = nodes => ({ name: '导出', theme: 'report', custom: {}, statusLabels: labels, pages: { root: { id: 'root', name: '总图', nodes, links: [] } } });
          const band = mkNode({ type: 'band', text: '分组', x: 0, y: 0, w: 1000, h: 180, labelSide: 't' });
          loadDoc(docOf([band]));
          await exportPPTX();
          const zp = await JSZip.loadAsync(await window.__saved[0].data.arrayBuffer());
          const slide = await zp.file('ppt/slides/slide1.xml').async('string');
          window.__saved = [];
          await exportVSDX();
          const zv = await JSZip.loadAsync(await window.__saved[0].data.arrayBuffer());
          const vband = await zv.file('visio/pages/page1.xml').async('string');
          const lane = mkNode({ type: 'lane', text: '新的一层', x: 40, y: 6, w: 900, h: 56 });
          loadDoc(docOf([lane]));
          window.__saved = [];
          await exportVSDX();
          const zl = await JSZip.loadAsync(await window.__saved[0].data.arrayBuffer());
          const vlane = await zl.file('visio/pages/page1.xml').async('string');
          window.__saved = [];
          await exportPPTX();
          const zpl = await JSZip.loadAsync(await window.__saved[0].data.arrayBuffer());
          const slideLane = await zpl.file('ppt/slides/slide1.xml').async('string');
          const pptShapes = xml => {
            const out = [];
            const re = /<p:sp\\b[\\s\\S]*?<\\/p:sp>/g;
            let m;
            while ((m = re.exec(xml))) {
              const sp = m[0];
              const off = sp.match(/<a:off x="(-?\\d+)" y="(-?\\d+)"/);
              const ext = sp.match(/<a:ext cx="(-?\\d+)" cy="(-?\\d+)"/);
              const text = [...sp.matchAll(/<a:t>([^<]*)<\\/a:t>/g)].map(x => x[1]).join('');
              if (off && ext) out.push({ x: +off[1], y: +off[2], cx: +ext[1], cy: +ext[2], text });
            }
            return out;
          };
          const vsdShapes = xml => {
            const out = [];
            const re = /<Shape ID='\\d+'[\\s\\S]*?<\\/Shape>/g;
            let m;
            while ((m = re.exec(xml))) {
              const sp = m[0];
              const cell = name => { const c = sp.match(new RegExp("<Cell N='" + name + "' V='([^']+)'")); return c ? +c[1] : null; };
              const text = (sp.match(/<Text>([\\s\\S]*?)<\\/Text>/) || [])[1] || '';
              out.push({ pinX: cell('PinX'), pinY: cell('PinY'), w: cell('Width'), h: cell('Height'), text });
            }
            return out;
          };
          const near = (a, b) => Math.abs(a - b) < 1e-4;
          const pb = pptShapes(slide);
          const body = pb.slice().sort((a, b) => b.cx * b.cy - a.cx * a.cy)[0];
          const title = pb.find(s => s.text.indexOf('分组') >= 0);
          const pl = pptShapes(slideLane);
          const lbody = pl.slice().sort((a, b) => b.cx * b.cy - a.cx * a.cy)[0];
          const ltitle = pl.find(s => s.text.indexOf('新的一层') >= 0);
          const vb = vsdShapes(vband);
          const vbody = vb.slice().sort((a, b) => b.w * b.h - a.w * a.h)[0];
          const vtitle = vb.find(s => s.text.indexOf('分组') >= 0);
          const vl = vsdShapes(vlane);
          const vlBody = vl.slice().sort((a, b) => b.w * b.h - a.w * a.h)[0];
          const vlTitle = vl.find(s => s.text.indexOf('新的一层') >= 0);
          return {
            pptBand: title && body ? { rx: title.cx / body.cx, ry: title.cy / body.cy, sameX: title.x === body.x } : null,
            pptLane: ltitle && lbody ? { rx: ltitle.cx / lbody.cx, ry: ltitle.cy / lbody.cy, sameX: ltitle.x === lbody.x, sameY: ltitle.y === lbody.y } : null,
            vsdBand: vtitle && vbody ? { rx: vtitle.w / vbody.w, ry: vtitle.h / vbody.h, sameX: near(vtitle.pinX, vbody.pinX), n: vb.length } : null,
            vsdLane: { n: vl.length, rx: vlTitle && vlBody ? vlTitle.w / vlBody.w : null, ry: vlTitle && vlBody ? vlTitle.h / vlBody.h : null, sameY: vlTitle && vlBody ? near(vlTitle.pinY, vlBody.pinY) : false }
          };
        }""")
        pb = office['pptBand']
        check('pptx band title on top slab', pb and abs(pb['rx'] - 1) < 1e-3 and abs(pb['ry'] - 34 / 180) < 1e-3 and pb['sameX'] is True, str(pb))
        pln = office['pptLane']
        check('pptx lane title on left slab', pln and abs(pln['rx'] - 96 / 900) < 1e-3 and abs(pln['ry'] - 1) < 1e-3 and pln['sameX'] is True and pln['sameY'] is True, str(pln))
        vb = office['vsdBand']
        check('vsdx band title on top slab', vb and abs(vb['rx'] - 1) < 1e-4 and abs(vb['ry'] - 34 / 180) < 1e-4 and vb['sameX'] is True, str(vb))
        vl = office['vsdLane']
        check('vsdx lane title on left slab', vl['n'] == 2 and abs(vl['rx'] - 96 / 900) < 1e-4 and abs(vl['ry'] - 1) < 1e-4 and vl['sameY'] is True, str(vl))
        check('no page errors', not errs, ' '.join(errs)[:400])
        browser.close()
    if fails:
        print('FAILED', len(fails))
        for f in fails:
            print(' -', f)
        sys.exit(1)
    print('PASS')


if __name__ == '__main__':
    main()
