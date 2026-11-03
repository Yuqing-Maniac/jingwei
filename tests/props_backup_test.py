#!/usr/bin/env python3
import os
import pathlib
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
SHOT = pathlib.Path('/opt/cursor/artifacts/screenshots')
DOC = """{
  name: '试验', theme: 'report', custom: {},
  statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' },
  pages: { root: { id: 'root', name: '总图', nodes: nodes, links: links } }
}"""
fails = []


def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))


def launch(pw):
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox']}
    if exe:
        kw['executable_path'] = exe
    return pw.chromium.launch(**kw)


def new_page(browser):
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
    pg = ctx.new_page()
    pg._errs = []
    pg._downloads = []
    pg.on('pageerror', lambda e: pg._errs.append(str(e)[:400]))
    pg.on('download', lambda d: pg._downloads.append(d.suggested_filename))
    pg.goto(HTML)
    pg.wait_for_selector('#svg')
    pg.wait_for_timeout(200)
    return pg


def main():
    SHOT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = launch(pw)
        pg = new_page(browser)

        border = pg.evaluate("""() => {
          const made = [
            iconPlaceSpec('lib:x', '甲', 96, 96),
            iconPlaceSpec('ms:a', '乙', 96, 92),
            iconPlaceSpec('cu:b', '丙', 96, 96)
          ];
          const q = document.getElementById('pal-q');
          q.value = '机';
          q.dispatchEvent(new Event('input', { bubbles: true }));
          const dom = [...document.querySelectorAll('#palette .pitem[data-add]')]
            .map(el => JSON.parse(el.dataset.add)).filter(s => s.icon);
          const spec = dom[0];
          const before = P().nodes.length;
          addNode(spec, 420, 280);
          const n = P().nodes[P().nodes.length - 1];
          const kept = mkNode({ type: 'equip', text: '老装备', icon: spec.icon, noBox: true, x: 20, y: 20, w: 96, h: 96 });
          const nodes = [kept], links = [];
          loadDoc(%s);
          return {
            fn: made.every(s => !Object.prototype.hasOwnProperty.call(s, 'noBox') && s.noBox !== true),
            domCount: dom.length,
            domClean: dom.every(s => !Object.prototype.hasOwnProperty.call(s, 'noBox') && s.noBox !== true),
            added: P().nodes.length > before || n.noBox === false,
            placed: n.noBox === false,
            kept: P().nodes.some(x => x.text === '老装备' && x.noBox === true)
          };
        }""" % DOC)
        check('palette spec omits noBox', border['fn'] and border['domCount'] > 0 and border['domClean'], str(border))
        check('addNode of that spec has a card', border['placed'] is True, str(border))
        check('stored noBox true stays true', border['kept'] is True, str(border))

        mixed = pg.evaluate("""() => {
          const a = mkNode({ type: 'round', text: '甲', x: 60, y: 70, w: 160, h: 64, size: 12 });
          const b = mkNode({ type: 'round', text: '乙', x: 60, y: 180, w: 160, h: 64, size: 18 });
          const nodes = [a, b], links = [];
          loadDoc(%s);
          checkpoint();
          P().nodes[0].text = '甲改';
          const depth = undoS.length;
          selectNodes(P().nodes.map(n => n.id));
          render();
          return {
            depth: depth,
            props: document.getElementById('props').textContent,
            s0: P().nodes[0].size, s1: P().nodes[1].size,
            text: P().nodes[0].text
          };
        }""" % DOC)
        check('mixed size shows 多值', '多值' in mixed['props'], mixed['props'][:180])
        pg.screenshot(path=str(SHOT / 'multi-select-panel.png'))
        edited = pg.evaluate("""() => {
          const input = document.getElementById('p-size');
          input.focus();
          input.value = '20';
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.blur();
          return { s0: P().nodes[0].size, s1: P().nodes[1].size, depth: undoS.length, text: P().nodes[0].text };
        }""")
        check('size 20 writes both', edited['s0'] == 20 and edited['s1'] == 20, str(edited))
        check('one undo step', edited['depth'] == mixed['depth'] + 1, 'before %s after %s' % (mixed['depth'], edited['depth']))
        pg.keyboard.press('Control+z')
        pg.wait_for_timeout(80)
        undone = pg.evaluate("() => ({ s0: P().nodes[0].size, s1: P().nodes[1].size, text: P().nodes[0].text, depth: undoS.length })")
        check('one undo restores both sizes', undone['s0'] == 12 and undone['s1'] == 18 and undone['text'] == '甲改', str(undone))
        pg.keyboard.press('Control+z')
        pg.wait_for_timeout(80)
        undone2 = pg.evaluate("() => ({ s0: P().nodes[0].size, s1: P().nodes[1].size, text: P().nodes[0].text })")
        check('second undo is the earlier text edit', undone2['text'] == '甲' and undone2['s0'] == 12 and undone2['s1'] == 18, str(undone2))

        same = pg.evaluate("""() => {
          const icon = 'lib:' + ICON_LIB[0].key;
          const other = 'lib:' + (ICON_LIB[1] || ICON_LIB[0]).key;
          const n1 = mkNode({ type: 'equip', text: '同1', icon: icon, x: 40, y: 60, w: 110, h: 96 });
          const n2 = mkNode({ type: 'equip', text: '同2', icon: icon, x: 180, y: 60, w: 110, h: 96 });
          const n3 = mkNode({ type: 'equip', text: '同3', icon: icon, x: 320, y: 60, w: 110, h: 96 });
          const n4 = mkNode({ type: 'equip', text: '异', icon: other, x: 460, y: 60, w: 110, h: 96 });
          const nodes = [n1, n2, n3, n4];
          const links = [
            { id: 'la', from: n1.id, to: n2.id, kind: 'data', route: 'ortho', label: '' },
            { id: 'lb', from: n2.id, to: n3.id, kind: 'data', route: 'ortho', label: '' },
            { id: 'lc', from: n3.id, to: n4.id, kind: 'ctrl', route: 'ortho', label: '' }
          ];
          loadDoc(%s);
          selectNodes([n1.id]);
          render();
          return { button: !!document.getElementById('p-same'), icon: icon, other: other };
        }""" % DOC)
        check('same button on one node', same['button'] is True, str(same))
        pg.click('#p-same')
        pg.wait_for_timeout(80)
        picked = pg.evaluate("""() => {
          const ids = [...sel];
          const nodes = ids.map(id => P().nodes.find(n => n.id === id));
          return { n: ids.length, icons: nodes.map(n => n && n.icon) };
        }""")
        check('选中同类 selects the three', picked['n'] == 3 and len(set(picked['icons'])) == 1, str(picked))
        pg.screenshot(path=str(SHOT / 'select-same.png'))
        pg.evaluate("() => { selectLinks(['la']); render(); }")
        pg.keyboard.press('Control+Shift+A')
        pg.wait_for_timeout(80)
        links = pg.evaluate("""() => {
          const ids = [...linkSel];
          const kinds = ids.map(id => P().links.find(l => l.id === id).kind);
          return { n: ids.length, kinds: kinds, ctrl: P().links.some(l => l.kind === 'ctrl' && !linkSel.has(l.id)) };
        }""")
        check('shortcut selects every link of that kind', links['n'] == 2 and links['kinds'] == ['data', 'data'] and links['ctrl'] is True, str(links))

        check('no page errors on the editor', not pg._errs, str(pg._errs[:2]))
        pg.context.close()

        def backup_case(tag):
            page = new_page(browser)
            page.evaluate("""() => {
              const n = P().nodes.find(x => String(x.text || '').indexOf('边海防无人化巡逻体系') >= 0);
              n.text = '仅存在于备份';
              render();
            }""")
            page.evaluate("() => Backup.commit()")
            stored = page.evaluate("""() => new Promise((res, rej) => {
              const req = indexedDB.open('hongtu.backup');
              req.onerror = () => rej(req.error);
              req.onsuccess = () => {
                const db = req.result;
                const tx = db.transaction('slots', 'readonly');
                const q = tx.objectStore('slots').getAll();
                q.onsuccess = () => {
                  const rows = q.result || [];
                  db.close();
                  res(rows.map(r => JSON.stringify(r)));
                };
                q.onerror = () => rej(q.error);
              };
            })""")
            found = any('仅存在于备份' in row for row in stored)
            check(tag + ' slot holds the edit', found, str(stored)[:240])
            page.reload()
            page.wait_for_selector('#jw-bak')
            label = page.inner_text('#jw-bak')
            check(tag + ' dialog offers restore', '恢复未保存的工程' in label, label[:80])
            return page

        restore = backup_case('restore')
        restore.screenshot(path=str(SHOT / 'restore-prompt.png'))
        check('restore run did not download', not restore._downloads, str(restore._downloads))
        restore.click('#jw-bak-restore')
        restore.wait_for_function("() => [...P().nodes].some(n => String(n.text || '').indexOf('仅存在于备份') >= 0)")
        check('restore brings the edit back', True, '')
        check('restore still did not download', not restore._downloads, str(restore._downloads))
        check('restore page errors', not restore._errs, str(restore._errs[:2]))
        restore.context.close()

        ignore = backup_case('ignore')
        ignore.click('#jw-bak-ignore')
        ignore.wait_for_selector('#jw-bak', state='detached')
        ignore.wait_for_function("""() => new Promise(res => {
          const req = indexedDB.open('hongtu.backup');
          req.onerror = () => res(false);
          req.onsuccess = () => {
            const db = req.result;
            const q = db.transaction('slots', 'readonly').objectStore('slots').getAll();
            q.onsuccess = () => { const n = (q.result || []).length; db.close(); res(n === 0); };
            q.onerror = () => res(false);
          };
        })""")
        left = ignore.evaluate("""() => ({
          demo: [...P().nodes].some(n => String(n.text || '').indexOf('边海防无人化巡逻体系') >= 0),
          edited: [...P().nodes].some(n => String(n.text || '').indexOf('仅存在于备份') >= 0),
          dlg: !!document.getElementById('jw-bak')
        })""")
        check('ignore keeps the demo', left['demo'] is True and left['edited'] is False and left['dlg'] is False, str(left))
        ignore.reload()
        ignore.wait_for_selector('#svg')
        ignore.wait_for_timeout(600)
        again = ignore.evaluate("""() => ({
          demo: [...P().nodes].some(n => String(n.text || '').indexOf('边海防无人化巡逻体系') >= 0),
          dlg: !!document.getElementById('jw-bak')
        })""")
        check('ignore removes the offer', again['demo'] is True and again['dlg'] is False, str(again))
        check('ignore did not download', not ignore._downloads, str(ignore._downloads))
        check('ignore page errors', not ignore._errs, str(ignore._errs[:2]))
        ignore.context.close()
        browser.close()

    for name in ('multi-select-panel.png', 'restore-prompt.png', 'select-same.png'):
        shot = SHOT / name
        check('screenshot ' + name, shot.is_file() and shot.stat().st_size > 1000, str(shot.stat().st_size if shot.is_file() else 0))
    if fails:
        print('FAILED', len(fails))
        for item in fails:
            print(' -', item)
        sys.exit(1)
    print('props_backup_test ok')


if __name__ == '__main__':
    main()
