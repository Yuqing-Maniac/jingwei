import os, sys, json, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
SHOT = '/tmp/link-panel-bi.png'
fails = []

def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))

with sync_playwright() as pw:
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox']}
    if exe:
        kw['executable_path'] = exe
    b = pw.chromium.launch(**kw)
    pg = b.new_page(viewport={'width': 1600, 'height': 1000}, accept_downloads=True)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    pg.goto(HTML)
    pg.wait_for_timeout(600)
    pg.evaluate("""() => {
      window.__toasts = [];
      const t = document.getElementById('toast');
      new MutationObserver(() => {
        if (!t.classList.contains('show')) return;
        const msg = t.textContent || '';
        if (!msg || window.__toasts[window.__toasts.length - 1] === msg) return;
        window.__toasts.push(msg);
      }).observe(t, { attributes: true, childList: true, characterData: true, subtree: true });
      const a = mkNode({ type: 'round', text: '岸台', x: 80, y: 180, w: 120, h: 48 });
      const c = mkNode({ type: 'round', text: '艇组', x: 560, y: 180, w: 120, h: 48 });
      loadDoc({
        name: '连线文字', theme: 'report',
        statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' },
        custom: {}, lastKind: 'data',
        pages: { root: { id: 'root', name: '总图', nodes: [a, c], links: [{ id: 'lk1', from: a.id, to: c.id, kind: 'data', route: 'ortho', label: '上报' }] } }
      });
      window.__toasts.length = 0;
      selectLinks(['lk1']); render();
    }""")
    pg.wait_for_timeout(200)
    toasts = pg.evaluate("() => window.__toasts.slice()")
    sel_hits = [t for t in toasts if 'D' in t and 'F2' in t]
    check('select toast once', len(sel_hits) == 1, str(toasts))
    pg.evaluate("() => render()")
    pg.wait_for_timeout(80)
    toasts2 = pg.evaluate("() => window.__toasts.slice()")
    sel_hits2 = [t for t in toasts2 if 'D' in t and 'F2' in t]
    check('second render does not toast again', len(sel_hits2) == 1, str(toasts2))

    def caps():
        return pg.evaluate("""() => {
          const l = P().links.find(x => x.id === 'lk1');
          const name = {};
          P().nodes.forEach(n => { name[n.id] = String(n.text || '').split('\\n')[0]; });
          const items = [...document.querySelectorAll('#world text')].map(t => {
            const b = t.getBoundingClientRect();
            return { text: t.textContent, x: b.x + b.width / 2, y: b.y + b.height / 2 };
          });
          const pills = items.filter(i => i.text === '上报' || i.text === '回执' || i.text === '旧标签');
          const to = items.find(i => i.text === name[l.to]);
          let closer = '', best = Infinity;
          pills.forEach(p => {
            if (!to) return;
            const d = Math.hypot(p.x - to.x, p.y - to.y);
            if (d < best) { best = d; closer = p.text; }
          });
          return {
            dir: l.dir || '', label: l.label || '', labelBack: ('labelBack' in l) ? l.labelBack : null,
            from: name[l.from], to: name[l.to], closer: closer,
            pills: pills.map(p => p.text)
          };
        }""")

    one = caps()
    check('one-way shows one caption', one['pills'] == ['上报'], str(one))
    check('one-way has no labelBack', one['labelBack'] is None, str(one))
    check('back field hidden', pg.locator('#p-back').count() == 0 and pg.locator('#p-label').count() == 1, '')

    pg.keyboard.press('d')
    pg.wait_for_timeout(150)
    check('D reaches both', pg.evaluate("() => P().links.find(x => x.id === 'lk1').dir") == 'both', '')
    check('two caption fields', pg.locator('#p-label').count() == 1 and pg.locator('#p-back').count() == 1, '')
    pg.fill('#p-back', '回执')
    pg.wait_for_timeout(80)
    pg.locator('#props').screenshot(path=SHOT)
    pg.locator('#stage').screenshot(path='/tmp/link-canvas-bi.png')
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(80)
    both = caps()
    check('both strings visible', sorted(both['pills']) == ['上报', '回执'], str(both))
    check('forward sits toward the to end', both['closer'] == '上报' and both['to'] == '艇组', str(both))

    pg.keyboard.press('r')
    pg.wait_for_timeout(120)
    swapped = caps()
    check('R moves the other string toward the to end', swapped['closer'] == '回执' and swapped['to'] == '岸台' and swapped['label'] == '回执', str(swapped))
    pg.keyboard.press('r')
    pg.wait_for_timeout(120)
    restored = caps()
    check('second R restores ends and strings', restored['closer'] == '上报' and restored['from'] == '岸台' and restored['to'] == '艇组' and restored['label'] == '上报' and restored['labelBack'] == '回执', str(restored))

    pg.keyboard.press('r')
    pg.wait_for_timeout(80)
    pg.keyboard.press('Control+z')
    pg.wait_for_timeout(150)
    undone = caps()
    check('undo restores the previous strings', undone['label'] == '上报' and undone['labelBack'] == '回执' and undone['from'] == '岸台' and undone['to'] == '艇组', str(undone))

    with pg.expect_download() as dlinfo:
        pg.click('#b-save')
    dl = dlinfo.value
    saved = '/tmp/link-caps-save.jingwei.json'
    dl.save_as(saved)
    env = json.loads(pathlib.Path(saved).read_text(encoding='utf-8'))
    check('save envelope is hongtu', env.get('format') == 'hongtu' and env.get('version') == 1, dl.suggested_filename)
    link = env['doc']['pages']['root']['links'][0]
    check('saved link keeps labelBack', link.get('labelBack') == '回执' and link.get('label') == '上报', '')
    pg.set_input_files('#f-open', saved)
    pg.wait_for_timeout(300)
    reloaded = pg.evaluate("""() => {
      const l = P().links[0];
      const texts = [...document.querySelectorAll('#world text')].map(t => t.textContent);
      return { label: l.label || '', labelBack: l.labelBack || '', texts: texts.filter(t => t === '上报' || t === '回执') };
    }""")
    check('open path keeps labelBack', reloaded['labelBack'] == '回执' and sorted(reloaded['texts']) == ['上报', '回执'], str(reloaded))

    old = pg.evaluate("""() => {
      const a = mkNode({ type: 'round', text: '岸台', x: 80, y: 180, w: 120, h: 48 });
      const c = mkNode({ type: 'round', text: '艇组', x: 560, y: 180, w: 120, h: 48 });
      loadDoc({
        name: '旧图', theme: 'report',
        statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' },
        custom: {},
        pages: { root: { id: 'root', name: '总图', nodes: [a, c], links: [{ id: 'old', from: a.id, to: c.id, kind: 'data', route: 'ortho', label: '旧标签' }] } }
      });
      const l = P().links[0];
      const texts = [...document.querySelectorAll('#world text')].map(t => t.textContent);
      return { hasBack: Object.prototype.hasOwnProperty.call(l, 'labelBack'), dir: l.dir || '', texts: texts.filter(t => t === '旧标签') };
    }""")
    check('old link draws without labelBack', old['texts'] == ['旧标签'] and old['hasBack'] is False, str(old))

    pg.click('#b-help')
    pg.wait_for_timeout(150)
    help_txt = pg.inner_text('#help-body')
    check('help has Ctrl+Shift+S', 'Ctrl+Shift+S' in ''.join(help_txt.split()), '')
    check('help has D and R lines', '箭头：单向' in help_txt and '调换方向' in help_txt, '')
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(80)

    pg.evaluate("() => { const l = P().links[0]; selectLinks([l.id]); render(); }")
    pg.wait_for_timeout(80)
    before = pg.evaluate("() => P().links[0].label")
    pg.click('#b-saveas')
    pg.wait_for_timeout(80)
    suggested = pg.input_value('#saveas-name')
    check('save-as suggests jingwei name', suggested.endswith('.jingwei.json') and suggested.startswith('旧图'), suggested)
    shown = pg.evaluate("() => document.getElementById('saveas').style.display")
    check('save-as dialog open', shown == 'flex', shown)
    pg.fill('#saveas-name', '   ')
    stray = []
    pg.once('download', lambda d: stray.append(d.suggested_filename))
    pg.click('#saveas-ok')
    pg.wait_for_timeout(250)
    check('empty save-as does nothing', not stray and pg.evaluate("() => document.getElementById('saveas').style.display") == 'flex', str(stray))
    pg.fill('#saveas-name', '另存/测试.json')
    with pg.expect_download() as dl2:
        pg.keyboard.press('Enter')
    got = dl2.value
    check('save-as strips and suffixes', got.suggested_filename == '另存测试.jingwei.json', got.suggested_filename)
    check('save-as does not write the filename into doc.name', pg.evaluate("() => doc.name") == '旧图', '')
    same = pg.evaluate("() => P().links[0].label")
    check('shortcuts stay quiet while save-as was open', same == before, same)
    pg.click('#b-saveas')
    pg.wait_for_timeout(50)
    pg.keyboard.press('Control+z')
    pg.wait_for_timeout(50)
    still = pg.evaluate("() => document.getElementById('saveas').style.display === 'flex' && P().links[0].label")
    check('ctrl+z does not undo through the dialog', still == before, str(still))
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(50)
    check('esc closes save-as', pg.evaluate("() => document.getElementById('saveas').style.display") == 'none', '')

    pg.evaluate("() => { clearSel(); render(); }")
    pg.wait_for_timeout(80)
    pg.fill('#d-dname', '新文档名')
    pg.evaluate("""() => {
      const el = document.getElementById('d-dname');
      el.dispatchEvent(new Event('change', { bubbles: true }));
      el.blur();
    }""")
    pg.wait_for_timeout(80)
    titled = pg.evaluate("() => ({ name: doc.name, title: document.title })")
    check('document name sets the title', titled['name'] == '新文档名' and titled['title'] == '新文档名 - 经纬织图', str(titled))
    pg.keyboard.press('Control+z')
    pg.wait_for_timeout(120)
    back = pg.evaluate("() => ({ name: doc.name, title: document.title })")
    check('undo restores the document name and title', back['name'] == '旧图' and back['title'] == '旧图 - 经纬织图', str(back))
    pg.evaluate("() => { clearSel(); render(); }")
    pg.fill('#d-pname', '首页')
    pg.wait_for_timeout(80)
    page = pg.evaluate("() => ({ page: P().name, title: document.title, crumb: document.getElementById('crumb').textContent })")
    check('page name refresh keeps the document title', page['page'] == '首页' and '首页' in page['crumb'] and page['title'] == '旧图 - 经纬织图', str(page))

    check('no page errors', not errs, str(errs[:3]))
    b.close()

shot = pathlib.Path(SHOT)
check('screenshot written', shot.is_file() and shot.stat().st_size > 1000, str(shot.stat().st_size if shot.is_file() else 0))
if fails:
    print('FAILED', len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('link_caps ok')
