import os, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
fails = []

def check(name, cond, detail=''):
    print(('ok' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name + (' ' + detail if detail else ''))

def node_by(g, nid):
    for n in g['nodes']:
        if n['id'] == nid:
            return n
    return None

def named(g, text):
    return [n for n in g['nodes'] if n['text'] == text]

with sync_playwright() as pw:
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox']}
    if exe:
        kw['executable_path'] = exe
    b = pw.chromium.launch(**kw)
    pg = b.new_page(viewport={'width': 1600, 'height': 1000})
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
      window.__cutArm = () => {
        const bak = document.getElementById('jw-bak');
        if (bak && bak.parentNode) bak.parentNode.removeChild(bak);
        const hist = document.getElementById('jw-webhist');
        if (hist) hist.hidden = true;
        const ae = document.activeElement;
        if (ae && ae !== document.body && ae.blur) ae.blur();
      };
      window.__cutLoad = (spec) => {
        const made = {};
        const nodes = [];
        (spec.nodes || []).forEach(o => {
          const n = mkNode(Object.assign({}, o, { parent: null }));
          if (o.parent) n.parent = made[o.parent].id;
          made[o.text] = n;
          nodes.push(n);
        });
        const links = (spec.links || []).map(l => ({
          id: l.id, from: made[l.from].id, to: made[l.to].id,
          dir: 'one', kind: 'data', route: 'ortho', label: l.label || ''
        }));
        loadDoc({
          name: '剪切试验', theme: 'report',
          statusLabels: { base: '延续', new: '本步新增／重构', key: '重点关注' },
          custom: {}, lastKind: 'data',
          pages: { root: { id: 'root', name: '总图', nodes: nodes, links: links } }
        });
        if (spec.nodesSel) selectNodes(spec.nodesSel.map(t => made[t].id));
        if (spec.linkSel) selectLinks(spec.linkSel);
        render();
        window.__toasts.length = 0;
        const out = {};
        Object.keys(made).forEach(k => {
          const n = made[k];
          out[k] = { id: n.id, x: n.x, y: n.y, parent: n.parent || null };
        });
        return out;
      };
      window.__cutGraph = () => ({
        nodes: P().nodes.map(n => ({ id: n.id, text: String(n.text || ''), x: n.x, y: n.y, parent: n.parent || null })),
        links: P().links.map(l => ({ id: l.id, from: l.from, to: l.to })),
        toasts: window.__toasts.slice()
      });
    }""")

    def load(spec):
        return pg.evaluate("(spec) => window.__cutLoad(spec)", spec)

    def graph():
        return pg.evaluate("() => window.__cutGraph()")

    def chord(key):
        pg.evaluate("() => window.__cutArm()")
        pg.keyboard.press(key)
        pg.wait_for_timeout(200)

    info = load({
        'nodes': [
            {'type': 'lane', 'text': '岸台区', 'x': 40, 'y': 40, 'w': 480, 'h': 280},
            {'type': 'round', 'text': '岸台', 'parent': '岸台区', 'x': 80, 'y': 90, 'w': 140, 'h': 48},
            {'type': 'rect', 'text': '值守', 'parent': '岸台', 'x': 110, 'y': 170, 'w': 120, 'h': 40},
            {'type': 'round', 'text': '外站', 'x': 560, 'y': 90, 'w': 120, 'h': 48},
        ],
        'links': [
            {'id': 'in1', 'from': '岸台', 'to': '值守', 'label': '值守链路'},
            {'id': 'ex1', 'from': '岸台', 'to': '外站', 'label': '外联'},
        ],
        'nodesSel': ['岸台'],
    })
    chord('Control+x')
    g = graph()
    check('1 cut removes parent and child', node_by(g, info['岸台']['id']) is None and node_by(g, info['值守']['id']) is None, str(g['nodes']))
    check('1 cut keeps container and outside', node_by(g, info['岸台区']['id']) is not None and node_by(g, info['外站']['id']) is not None, str(g['nodes']))
    check('1 cut drops touching links', g['links'] == [], str(g['links']))
    check('1 toast', '已剪切 2 个元素' in g['toasts'], str(g['toasts']))
    chord('Control+v')
    g = graph()
    shore = named(g, '岸台')
    watch = named(g, '值守')
    pair = []
    if len(shore) == 1 and len(watch) == 1:
        pair = [l for l in g['links'] if {l['from'], l['to']} == {shore[0]['id'], watch[0]['id']}]
    ext = [l for l in g['links'] if l['id'] == 'ex1' or l['from'] == info['外站']['id'] or l['to'] == info['外站']['id']]
    check('1 paste returns the texts', len(shore) == 1 and len(watch) == 1, str(g['nodes']))
    check('1 paste uses new ids', len(shore) == 1 and shore[0]['id'] != info['岸台']['id'] and watch[0]['id'] != info['值守']['id'], str(shore + watch))
    check('1 paste shifts by 24', len(shore) == 1 and shore[0]['x'] == info['岸台']['x'] + 24 and shore[0]['y'] == info['岸台']['y'] + 24 and watch[0]['x'] == info['值守']['x'] + 24 and watch[0]['y'] == info['值守']['y'] + 24, str(shore + watch))
    check('1 child parents to pasted parent', len(shore) == 1 and watch and watch[0]['parent'] == shore[0]['id'], str(watch))
    check('1 pasted parent stays in the container', len(shore) == 1 and shore[0]['parent'] == info['岸台区']['id'], str(shore))
    check('1 outside and container remain', node_by(g, info['外站']['id']) is not None and node_by(g, info['岸台区']['id']) is not None, str(g['nodes']))
    check('1 external link absent after paste', ext == [], str(g['links']))
    check('1 internal link follows the pasted pair', len(pair) == 1, str(g['links']))
    chord('Control+z')
    g = graph()
    check('1 undo removes the paste', named(g, '岸台') == [] and named(g, '值守') == [], str(g['nodes']))
    check('1 undo keeps container and outside', node_by(g, info['岸台区']['id']) is not None and node_by(g, info['外站']['id']) is not None, str(g['nodes']))
    check('1 undo still has no external link', all(l['id'] != 'ex1' for l in g['links']), str(g['links']))
    chord('Control+z')
    g = graph()
    parent = node_by(g, info['岸台']['id'])
    child = node_by(g, info['值守']['id'])
    ex = next((l for l in g['links'] if l['id'] == 'ex1'), None)
    inn = next((l for l in g['links'] if l['id'] == 'in1'), None)
    check('1 second undo restores original nodes', parent is not None and child is not None and parent['x'] == info['岸台']['x'] and parent['y'] == info['岸台']['y'] and child['x'] == info['值守']['x'] and child['parent'] == info['岸台']['id'], str(g['nodes']))
    check('1 second undo restores the external link', ex is not None and ex['from'] == info['岸台']['id'] and ex['to'] == info['外站']['id'] and inn is not None and inn['from'] == info['岸台']['id'] and inn['to'] == info['值守']['id'], str(g['links']))

    info = load({
        'nodes': [
            {'type': 'round', 'text': '艇组', 'x': 80, 'y': 80, 'w': 120, 'h': 48},
            {'type': 'rect', 'text': '值守', 'x': 280, 'y': 80, 'w': 120, 'h': 40},
            {'type': 'round', 'text': '外站', 'x': 520, 'y': 80, 'w': 120, 'h': 48},
        ],
        'links': [
            {'id': 'mid', 'from': '艇组', 'to': '值守', 'label': '内部'},
            {'id': 'out', 'from': '艇组', 'to': '外站', 'label': '外联'},
        ],
        'nodesSel': ['艇组', '值守'],
    })
    chord('Control+x')
    chord('Control+v')
    g = graph()
    boats = named(g, '艇组')
    watch = named(g, '值守')
    outside = node_by(g, info['外站']['id'])
    pair = []
    if len(boats) == 1 and len(watch) == 1:
        pair = [l for l in g['links'] if l['from'] == boats[0]['id'] and l['to'] == watch[0]['id']]
    touched = []
    if outside:
        touched = [l for l in g['links'] if l['from'] == outside['id'] or l['to'] == outside['id'] or l['id'] == 'out']
    check('2 paste places the pair', len(boats) == 1 and len(watch) == 1 and boats[0]['id'] != info['艇组']['id'] and watch[0]['id'] != info['值守']['id'], str(g['nodes']))
    check('2 paste shifts the pair by 24', len(boats) == 1 and boats[0]['x'] == info['艇组']['x'] + 24 and boats[0]['y'] == info['艇组']['y'] + 24 and watch[0]['x'] == info['值守']['x'] + 24 and watch[0]['y'] == info['值守']['y'] + 24, str(boats + watch))
    check('2 internal link connects the pasted pair', len(pair) == 1 and pair[0]['id'] != 'mid', str(g['links']))
    check('2 link to the unselected node stays gone', outside is not None and touched == [], str(g['links']))

    info = load({
        'nodes': [
            {'type': 'round', 'text': '岸台', 'x': 80, 'y': 120, 'w': 120, 'h': 48},
            {'type': 'round', 'text': '外站', 'x': 360, 'y': 120, 'w': 120, 'h': 48},
        ],
        'links': [{'id': 'keep', 'from': '岸台', 'to': '外站', 'label': '外联'}],
        'linkSel': ['keep'],
    })
    before = graph()
    chord('Control+x')
    g = graph()
    kept = next((l for l in g['links'] if l['id'] == 'keep'), None)
    check('3 link selection stays on the page', kept is not None and kept['from'] == info['岸台']['id'] and kept['to'] == info['外站']['id'] and node_by(g, info['岸台']['id']) is not None and node_by(g, info['外站']['id']) is not None, str(g))
    check('3 link selection does not toast cut', not any('已剪切' in t for t in g['toasts']), str(g['toasts']))
    check('3 link selection does not move nodes', node_by(g, info['岸台']['id'])['x'] == before['nodes'][0]['x'] and len(g['nodes']) == len(before['nodes']), str(g['nodes']))

    info = load({
        'nodes': [
            {'type': 'round', 'text': '岸台', 'x': 90, 'y': 140, 'w': 120, 'h': 48},
            {'type': 'round', 'text': '外站', 'x': 360, 'y': 140, 'w': 120, 'h': 48},
        ],
        'links': [],
        'nodesSel': ['岸台'],
    })
    focused = pg.evaluate("""() => {
      window.__cutArm();
      const el = document.getElementById('p-text');
      if (!el) return false;
      el.focus();
      return document.activeElement === el;
    }""")
    pg.keyboard.press('Control+x')
    pg.wait_for_timeout(200)
    g = graph()
    stayed = node_by(g, info['岸台']['id'])
    check('4 input had focus', focused, '')
    check('4 focused input leaves the node', stayed is not None and stayed['x'] == info['岸台']['x'] and stayed['y'] == info['岸台']['y'] and node_by(g, info['外站']['id']) is not None, str(g['nodes']))
    check('4 focused input does not toast cut', not any('已剪切' in t for t in g['toasts']), str(g['toasts']))

    info = load({
        'nodes': [
            {'type': 'round', 'text': '岸台', 'x': 100, 'y': 160, 'w': 120, 'h': 48},
            {'type': 'round', 'text': '艇组', 'x': 320, 'y': 160, 'w': 120, 'h': 48},
        ],
        'links': [{'id': 'ab', 'from': '岸台', 'to': '艇组', 'label': '协同'}],
        'nodesSel': ['岸台'],
    })
    chord('Control+Shift+X')
    pg.wait_for_timeout(400)
    g = graph()
    shore = node_by(g, info['岸台']['id'])
    boat = node_by(g, info['艇组']['id'])
    check('5 shift x keeps the selected node', shore is not None and boat is not None and shore['text'] == '岸台', str(g['nodes']))

    info = load({
        'nodes': [
            {'type': 'lane', 'text': '岸台区', 'x': 40, 'y': 40, 'w': 480, 'h': 280},
            {'type': 'round', 'text': '岸台', 'parent': '岸台区', 'x': 80, 'y': 90, 'w': 140, 'h': 48},
            {'type': 'rect', 'text': '值守', 'parent': '岸台', 'x': 110, 'y': 170, 'w': 120, 'h': 40},
            {'type': 'round', 'text': '外站', 'x': 560, 'y': 90, 'w': 120, 'h': 48},
        ],
        'links': [
            {'id': 'in6', 'from': '岸台', 'to': '值守', 'label': '值守链路'},
            {'id': 'ex6', 'from': '岸台', 'to': '外站', 'label': '外联'},
        ],
        'nodesSel': ['岸台'],
    })
    chord('Control+x')
    g = graph()
    check('6 first cut removes the selection', node_by(g, info['岸台']['id']) is None and node_by(g, info['值守']['id']) is None and '已剪切 2 个元素' in g['toasts'], str(g['toasts']) + str(g['nodes']))
    pg.evaluate("() => { window.__toasts.length = 0 }")
    chord('Control+x')
    g = graph()
    check('6 second cut adds no removal and no toast', node_by(g, info['岸台']['id']) is None and node_by(g, info['外站']['id']) is not None and not any('已剪切' in t for t in g['toasts']), str(g['toasts']) + str(g['nodes']))
    chord('Control+z')
    g = graph()
    parent = node_by(g, info['岸台']['id'])
    child = node_by(g, info['值守']['id'])
    ex = next((l for l in g['links'] if l['id'] == 'ex6'), None)
    check('6 one undo restores the cut', parent is not None and child is not None and parent['x'] == info['岸台']['x'] and child['parent'] == info['岸台']['id'] and ex is not None and ex['from'] == info['岸台']['id'] and ex['to'] == info['外站']['id'], str(g))

    info = load({
        'nodes': [
            {'type': 'round', 'text': '岸台', 'x': 70, 'y': 200, 'w': 120, 'h': 48},
            {'type': 'round', 'text': '艇组', 'x': 300, 'y': 200, 'w': 120, 'h': 48},
        ],
        'links': [{'id': 'copy1', 'from': '岸台', 'to': '艇组', 'label': '协同'}],
        'nodesSel': ['岸台', '艇组'],
    })
    chord('Control+c')
    g = graph()
    shore = node_by(g, info['岸台']['id'])
    boat = node_by(g, info['艇组']['id'])
    check('7 copy toasts and leaves the nodes', '已复制 2 个元素' in g['toasts'] and shore is not None and boat is not None and shore['x'] == info['岸台']['x'] and boat['y'] == info['艇组']['y'] and len(g['nodes']) == 2, str(g['toasts']) + str(g['nodes']))
    chord('Control+v')
    g = graph()
    shores = named(g, '岸台')
    boats = named(g, '艇组')
    orig_s = node_by(g, info['岸台']['id'])
    orig_b = node_by(g, info['艇组']['id'])
    news = [n for n in shores if n['id'] != info['岸台']['id']]
    newb = [n for n in boats if n['id'] != info['艇组']['id']]
    copied = []
    if len(news) == 1 and len(newb) == 1:
        copied = [l for l in g['links'] if l['from'] == news[0]['id'] and l['to'] == newb[0]['id']]
    orig_link = next((l for l in g['links'] if l['id'] == 'copy1'), None)
    check('7 paste duplicates onto new ids', orig_s is not None and orig_b is not None and orig_s['x'] == info['岸台']['x'] and orig_b['y'] == info['艇组']['y'] and len(news) == 1 and len(newb) == 1 and news[0]['x'] == info['岸台']['x'] + 24 and news[0]['y'] == info['岸台']['y'] + 24 and newb[0]['x'] == info['艇组']['x'] + 24 and newb[0]['y'] == info['艇组']['y'] + 24, str(g['nodes']))
    check('7 paste duplicates the link', len(copied) == 1 and orig_link is not None and orig_link['from'] == info['岸台']['id'] and orig_link['to'] == info['艇组']['id'], str(g['links']))

    info = load({
        'nodes': [
            {'type': 'lane', 'text': '岸台区', 'x': 40, 'y': 40, 'w': 480, 'h': 280},
            {'type': 'round', 'text': '岸台', 'parent': '岸台区', 'x': 80, 'y': 90, 'w': 140, 'h': 48},
            {'type': 'rect', 'text': '值守', 'parent': '岸台', 'x': 110, 'y': 170, 'w': 120, 'h': 40},
            {'type': 'round', 'text': '外站', 'x': 560, 'y': 90, 'w': 120, 'h': 48},
        ],
        'links': [
            {'id': 'in8', 'from': '岸台', 'to': '值守', 'label': '值守链路'},
            {'id': 'ex8', 'from': '岸台', 'to': '外站', 'label': '外联'},
        ],
        'nodesSel': ['岸台'],
    })
    chord('Delete')
    g = graph()
    check('8 delete removes parent and child', node_by(g, info['岸台']['id']) is None and node_by(g, info['值守']['id']) is None and node_by(g, info['岸台区']['id']) is not None and node_by(g, info['外站']['id']) is not None, str(g['nodes']))
    check('8 delete drops touching links', g['links'] == [], str(g['links']))
    chord('Control+z')
    g = graph()
    parent = node_by(g, info['岸台']['id'])
    ex = next((l for l in g['links'] if l['id'] == 'ex8'), None)
    check('8 undo restores the delete', parent is not None and parent['x'] == info['岸台']['x'] and node_by(g, info['值守']['id']) is not None and ex is not None and ex['to'] == info['外站']['id'], str(g))

    pg.click('#b-help')
    pg.wait_for_timeout(150)
    help_txt = ''.join(pg.inner_text('#help-body').split())
    check('help names cut', 'Ctrl+X／Ctrl+C／Ctrl+V' in help_txt and '剪切／复制／粘贴' in help_txt, help_txt)
    pg.keyboard.press('Escape')

    check('no page errors', not errs, str(errs[:3]))
    b.close()

if fails:
    print('FAILED', len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('cut_paste ok')
