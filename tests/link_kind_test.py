#!/usr/bin/env python3
"""选中连线按 S 循环类型、告警／时统、图例生命周期、撤销与导出。"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = Path(os.environ.get("JW_PAGE", ROOT / "dist" / "offline.html")).resolve()
SHOT = Path(os.environ.get("JW_SHOT", "/opt/cursor/artifacts"))
URL = PAGE.as_uri()

FAILS = []


def check(name, ok, detail=""):
    print(("ok " if ok else "FAIL ") + name + ((" " + detail) if detail else ""))
    if not ok:
        FAILS.append(name + ((" " + detail) if detail else ""))


def main():
    if not PAGE.is_file():
        print("missing", PAGE)
        return 2
    SHOT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", args=["--no-sandbox", "--disable-gpu"])
        ctx = browser.new_context(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL)
        page.wait_for_function("() => typeof LINK_KINDS === 'object' && typeof render === 'function'")

        page.evaluate(
            """() => {
              saveFile = async () => true;
              const a = mkNode({ type: 'rect', text: '甲', x: 80, y: 80, w: 140, h: 56 });
              const b = mkNode({ type: 'rect', text: '乙', x: 420, y: 80, w: 140, h: 56 });
              const c = mkNode({ type: 'rect', text: '丙', x: 80, y: 220, w: 140, h: 56, status: 'new' });
              doc.statusLabels.new = '本步新增／重构且名称很长需要留白';
              doc.pages = { root: { id: 'root', name: '总图', nodes: [a, b, c], links: [
                { id: 'L1', from: a.id, to: b.id, dir: 'one', kind: 'data', route: 'ortho', label: '' }
              ] } };
              cur = 'root'; stack = ['root'];
              clearSel(); render();
            }"""
        )
        info = page.evaluate(
            """() => {
              const p = P();
              const lg = p.nodes.find(n => n.type === 'legend');
              const labels = legendEntries(p).map(it => it.label);
              const hit = p.nodes.filter(n => n !== lg && n.x < lg.x + lg.w && n.x + n.w > lg.x && n.y < lg.y + lg.h && n.y + n.h > lg.y);
              return { has: !!lg, labels, overlap: hit.length, w: lg && lg.w, noLegend: !!p.noLegend };
            }"""
        )
        check("auto legend", info["has"] and "数据流" in info["labels"] and "本步新增／重构且名称很长需要留白" in info["labels"], str(info))
        check("legend clear of nodes", info["overlap"] == 0, str(info))
        check("long label widens legend", info["w"] >= 240, str(info["w"]))

        page.evaluate("() => { selectLinks(['L1']); render(); }")
        page.keyboard.press("s")
        kind = page.evaluate("() => P().links.find(l => l.id === 'L1').kind")
        check("S from data to ctrl", kind == "ctrl", kind)
        for expect in ("wired", "radio", "sat", "alarm", "sync", "plain"):
            page.keyboard.press("s")
            kind = page.evaluate("() => P().links.find(l => l.id === 'L1').kind")
            check("S to " + expect, kind == expect, kind)
        labels = page.evaluate("() => legendEntries(P()).filter(it => it.kind === 'ln').map(it => it.k)")
        check("legend follows current kind only", labels == ["plain"], str(labels))

        page.keyboard.press("1")
        kind = page.evaluate("() => P().links.find(l => l.id === 'L1').kind")
        check("digit 1 still plain", kind == "plain", kind)
        page.keyboard.press("6")
        kind = page.evaluate("() => P().links.find(l => l.id === 'L1').kind")
        check("digit 6 still sat", kind == "sat", kind)

        page.evaluate(
            """() => {
              const p = P();
              const c = p.nodes.find(n => n.text === '丙');
              const b = p.nodes.find(n => n.text === '乙');
              p.links.push({ id: 'L2', from: c.id, to: b.id, dir: 'one', kind: 'ctrl', route: 'ortho', label: '' });
              p.links.find(l => l.id === 'L1').kind = 'data';
              selectLinks(['L1', 'L2']);
              render();
            }"""
        )
        page.keyboard.press("s")
        kinds = page.evaluate("() => P().links.map(l => l.kind).sort()")
        check("mixed selection unifies to next of first", kinds == ["ctrl", "ctrl"], str(kinds))
        page.keyboard.press("Control+z")
        kinds = page.evaluate("() => P().links.map(l => l.id + ':' + l.kind).sort()")
        check("undo restores both kinds", kinds == ["L1:data", "L2:ctrl"], str(kinds))
        page.keyboard.press("Control+y")
        kinds = page.evaluate("() => P().links.map(l => l.kind).sort()")
        check("redo reapplies unified kind", kinds == ["ctrl", "ctrl"], str(kinds))

        page.evaluate("() => { P().links.forEach(l => l.kind = l.id === 'L1' ? 'alarm' : 'sync'); render(); }")
        raw = page.evaluate("() => projectJSON()")
        page.evaluate("(raw) => { const o = JSON.parse(raw); loadDoc(o.doc); }", raw)
        back = page.evaluate(
            """() => {
              const p = P();
              return {
                kinds: p.links.map(l => l.kind).sort(),
                labels: legendEntries(p).filter(it => it.kind === 'ln').map(it => it.label).sort(),
                noLegend: !!p.noLegend
              };
            }"""
        )
        check("reload keeps kinds", back["kinds"] == ["alarm", "sync"], str(back))
        check("reload keeps legend rows", back["labels"] == ["告警", "时统"], str(back))
        parsed = page.evaluate(
            """() => {
              const alarm = TextGen.parseDialect('甲 -> 乙 [告警]')[0].links[0].kind;
              const sync = TextGen.parseDialect('甲 -> 乙 [时统]')[0].links[0].kind;
              return { alarm, sync };
            }"""
        )
        check("text import maps alarm and sync", parsed == {"alarm": "alarm", "sync": "sync"}, str(parsed))
        page.evaluate("() => selectLinks(['L2'])")
        page.keyboard.press("Delete")
        labels = page.evaluate("() => legendEntries(P()).filter(it => it.kind === 'ln').map(it => it.label)")
        check("last sync link drops that legend row", labels == ["告警"], str(labels))
        page.keyboard.press("Control+z")

        page.evaluate("() => { const lg = P().nodes.find(n => n.type === 'legend'); selectNodes([lg.id]); }")
        page.keyboard.press("Delete")
        dismissed = page.evaluate(
            """() => {
              const p = P();
              p.links.push({ id: 'L3', from: p.links[0].from, to: p.links[0].to, dir: 'one', kind: 'wired', route: 'ortho', label: '' });
              render();
              return { n: p.nodes.filter(n => n.type === 'legend').length, off: p.noLegend === true };
            }"""
        )
        check("delete legend stays dismissed", dismissed["n"] == 0 and dismissed["off"], str(dismissed))
        page.keyboard.press("Control+z")
        restored = page.evaluate("() => ({ n: P().nodes.filter(n => n.type === 'legend').length, off: !!P().noLegend })")
        check("undo delete brings legend back", restored["n"] == 1 and not restored["off"], str(restored))
        page.keyboard.press("Control+y")
        dismissed = page.evaluate("() => ({ n: P().nodes.filter(n => n.type === 'legend').length, off: P().noLegend === true })")
        check("redo delete dismisses again", dismissed["n"] == 0 and dismissed["off"], str(dismissed))

        manual = page.evaluate(
            """() => {
              addNode({ type: 'legend', role: 'legend', w: 200, h: 60 }, 240, 420);
              return { n: P().nodes.filter(n => n.type === 'legend').length, off: !!P().noLegend };
            }"""
        )
        check("manual legend returns", manual["n"] == 1 and not manual["off"], str(manual))

        page.evaluate("() => { selectLinks(['L1']); render(); document.body.focus(); }")
        kept = page.evaluate("() => P().links.find(l => l.id === 'L1').kind")
        page.keyboard.press("Shift+s")
        check("Shift+S does not cycle", page.evaluate("() => P().links.find(l => l.id === 'L1').kind") == kept)
        page.evaluate("() => { const i = document.querySelector('#p-label'); if (!i) throw new Error('no label field'); i.focus(); }")
        page.keyboard.press("s")
        check("S in a field does not cycle", page.evaluate("() => P().links.find(l => l.id === 'L1').kind") == kept, kept)
        page.evaluate(
            """() => {
              const d = document.createElement('div');
              d.id = 'ime-box';
              d.contentEditable = 'true';
              d.textContent = '组合';
              document.body.appendChild(d);
              d.focus();
            }"""
        )
        page.keyboard.press("s")
        check("S in contenteditable does not cycle", page.evaluate("() => P().links.find(l => l.id === 'L1').kind") == kept)
        page.evaluate("() => document.getElementById('ime-box').remove()")
        page.evaluate("() => document.body.focus()")
        page.evaluate(
            """() => {
              document.dispatchEvent(new KeyboardEvent('keydown', { key: 's', bubbles: true, cancelable: true, isComposing: true }));
            }"""
        )
        check("composing S does not cycle", page.evaluate("() => P().links.find(l => l.id === 'L1').kind") == kept)
        page.keyboard.press("Control+s")
        check("Ctrl+S does not cycle", page.evaluate("() => P().links.find(l => l.id === 'L1').kind") == kept)
        page.keyboard.press("Meta+s")
        check("Cmd+S does not cycle", page.evaluate("() => P().links.find(l => l.id === 'L1').kind") == kept)

        exported = page.evaluate(
            """async () => {
              const caught = [];
              const orig = saveFile;
              saveFile = async (name, data) => { caught.push({ name, data }); return true; };
              const svg = exportSVGString(P(), true).str;
              const dio = DrawIO.exportString([P()]);
              await exportPPTX();
              await exportVSDX([P()]);
              saveFile = orig;
              const ppt = caught.find(x => /pptx$/i.test(x.name));
              const vsd = caught.find(x => /vsdx$/i.test(x.name));
              const read = async (blob) => new TextDecoder('utf-8', { fatal: false }).decode(await blob.arrayBuffer());
              let pats = '';
              if (vsd) {
                const zip = await JSZip.loadAsync(vsd.data);
                const page = Object.keys(zip.files).find(n => n.endsWith('visio/pages/page1.xml'));
                pats = page ? (await zip.file(page).async('string')).match(/N='LinePattern' V='[0-9]+'/g).join(' ') : '';
              }
              return {
                svgAlarm: svg.includes('告警') && svg.includes('stroke-dasharray="4 2"'),
                svgSync: svg.includes('时统') && svg.includes('stroke-dasharray="12 4"'),
                dio: dio.includes('dashPattern=4 2') && dio.includes('dashPattern=12 4') && dio.includes('ht_kind="alarm"') && dio.includes('ht_kind="sync"'),
                ppt: ppt ? (await read(ppt.data)).includes('sysDash') && (await read(ppt.data)).includes('lgDash') : false,
                vsd: pats.includes("V='2'") && pats.includes("V='6'")
              };
            }"""
        )
        check("svg export has new dashes", exported["svgAlarm"] and exported["svgSync"], str(exported))
        check("drawio export has new dashes", exported["dio"], str(exported["dio"]))
        check("pptx export has dash names", exported["ppt"], str(exported["ppt"]))
        check("vsdx export has line pattern", exported["vsd"], str(exported["vsd"]))

        page.evaluate(
            """() => {
              selectLinks(['L1']);
              P().links.find(l => l.id === 'L1').kind = 'alarm';
              const lg = P().nodes.find(n => n.type === 'legend');
              const r = svg.getBoundingClientRect();
              view.k = 2;
              view.x = Math.min(lg.x, 60) - 24;
              view.y = (lg.y + lg.h) - (r.height - 120) / view.k;
              applyView();
              render();
              const toast = document.getElementById('toast');
              if (toast) toast.classList.remove('show');
            }"""
        )
        page.screenshot(path=str(SHOT / "link-kind-200.png"))
        for scale, name in ((1, "link-kind-100.png"), (1.5, "link-kind-150.png")):
            page.evaluate(
                """(k) => {
                  const lg = P().nodes.find(n => n.type === 'legend');
                  const r = svg.getBoundingClientRect();
                  view.k = k;
                  view.x = lg.x - 36;
                  view.y = lg.y - 80;
                  applyView();
                  render();
                }""",
                scale,
            )
            page.screenshot(path=str(SHOT / name))
        check("screenshot written", (SHOT / "link-kind-200.png").is_file())
        check("no page errors", not errors, "; ".join(errors[:3]))
        browser.close()
    if FAILS:
        print("FAILED", len(FAILS))
        for f in FAILS:
            print(" -", f)
        return 1
    print("link_kind_test ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
