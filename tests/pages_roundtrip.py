"""One project file holds a page tree. Old files, siblings, children, and the demo drill."""
import pathlib
import sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
fails = []


def check(name, cond, detail=''):
    line = ('ok' if cond else 'FAIL') + '  ' + name
    if detail:
        line += '  ' + detail
    print(line)
    if not cond:
        fails.append(name + (('  ' + detail) if detail else ''))


OLD = r"""
() => {
  loadDoc({
    name: '边海防无人化巡逻体系', theme: 'report',
    statusLabels: { base: '已建', new: '本期新增', key: '重点建设' },
    custom: {},
    pages: { root: { id: 'root', name: '总图', nodes: [mkNode({ type: 'round', text: '巡逻节点', x: 40, y: 40, w: 160, h: 40 })], links: [] } }
  });
  const canvas = (document.querySelector('#world') || {}).textContent || '';
  const pageName = (document.querySelector('#d-pname') || {}).value || '';
  return {
    cur,
    up: doc.pages.root.up,
    hasUp: Object.prototype.hasOwnProperty.call(doc.pages.root, 'up'),
    sib: siblingPages('root').map(p => p.name),
    kids: childPages('root').map(p => p.name),
    node: doc.pages.root.nodes.map(n => n.text),
    canvas: canvas.indexOf('巡逻节点') >= 0,
    pageName
  };
}
"""

ROUND = r"""
() => {
  loadDoc({
    name: '边海防无人化巡逻体系', theme: 'report',
    statusLabels: { base: '已建', new: '本期新增', key: '重点建设' },
    custom: {},
    pages: { root: { id: 'root', name: '总图', nodes: [mkNode({ type: 'round', text: '巡逻节点', x: 40, y: 40, w: 160, h: 40 })], links: [] } }
  });
  addSibling('通信保障');
  showPage('root');
  const child = addChild('机巢内部');
  P().nodes.push(mkNode({ type: 'round', text: '换电单元', x: 80, y: 80, w: 140, h: 40 }));
  goPage(0);
  const wrap = JSON.parse(projectJSON());
  loadDoc(wrap.doc);
  const sib = siblingPages('root');
  const kids = childPages('root');
  const kid = kids[0];
  showPage(sib[1] ? sib[1].id : '');
  const sibCanvas = (document.querySelector('#world') || {}).textContent || '';
  showPage(kid ? kid.id : '');
  const kidCanvas = (document.querySelector('#world') || {}).textContent || '';
  showPage('root');
  const rootCanvas = (document.querySelector('#world') || {}).textContent || '';
  const doors = doc.pages.root.nodes.map(n => n.sub).filter(Boolean);
  const sibPage = doc.pages[sib[1] ? sib[1].id : ''];
  const sibTitle = sibPage ? sibPage.nodes.filter(n => n.role === 'title').map(n => n.text) : [];
  const kidTitle = kid ? kid.nodes.filter(n => n.role === 'title').map(n => n.text) : [];
  return {
    format: wrap.format,
    version: wrap.version,
    cur,
    rootNode: doc.pages.root.nodes.map(n => n.text),
    sib: sib.map(p => ({ name: p.name, up: p.up })),
    kid: kid ? { id: kid.id, name: kid.name, up: kid.up, nodes: kid.nodes.map(n => n.text) } : null,
    childId: child,
    doors,
    pageOrder: Object.prototype.hasOwnProperty.call(doc, 'pageOrder'),
    sibCanvas: sibCanvas.indexOf('通信保障') >= 0,
    kidCanvas: kidCanvas.indexOf('换电单元') >= 0 && kidCanvas.indexOf('机巢内部') >= 0,
    rootCanvas: rootCanvas.indexOf('巡逻节点') >= 0 && rootCanvas.indexOf('换电单元') < 0,
    sibTitle,
    kidTitle
  };
}
"""

DEMO = r"""
() => {
  const nestReady = !!(doc.pages.pnest && childPages('root').some(p => p.id === 'pnest'));
  if (!nestReady) loadDoc(buildDemo());
  const host = doc.pages.root.nodes.find(n => n.text && String(n.text).indexOf('无人机机巢') >= 0);
  const before = Object.keys(doc.pages).length;
  const childBefore = childPages('root').map(p => p.id);
  enterSub(host && host.id);
  const canvas = (document.querySelector('#world') || {}).textContent || '';
  const pageName = (document.querySelector('#d-pname') || {}).value || '';
  return {
    loaded: !nestReady,
    host: host && host.id,
    childOfRoot: childBefore.indexOf('pnest') >= 0 && doc.pages.pnest.up === 'root',
    grew: Object.keys(doc.pages).length - before,
    cur,
    pageName,
    nestName: doc.pages.pnest && doc.pages.pnest.name,
    canvas: canvas.indexOf('自动换电单元') >= 0
  };
}
"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.set_default_timeout(60000)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(HTML)
        page.wait_for_selector('#svg')
        page.wait_for_function('() => typeof loadDoc === "function" && doc && doc.pages && doc.pages.root')

        old = page.evaluate(OLD)
        print('predicate 1', old)
        check('old file opens on its only page', old['cur'] == 'root' and old['pageName'] == '总图' and old['canvas'], str(old))
        check('old file siblings are only 总图', old['sib'] == ['总图'], str(old['sib']))
        check('old file has no child pages', old['kids'] == [], str(old['kids']))
        check('old node text is still 巡逻节点', old['node'] == ['巡逻节点'] and old['hasUp'] and old['up'] is None, str(old))

        trip = page.evaluate(ROUND)
        print('predicate 2', trip)
        check('wrapper stays hongtu version 1', trip['format'] == 'hongtu' and trip['version'] == 1, str(trip['format']) + ' ' + str(trip['version']))
        check('reload returns to root and keeps 巡逻节点', trip['cur'] == 'root' and trip['rootNode'] == ['巡逻节点'] and trip['rootCanvas'], str(trip['rootNode']))
        check('siblings are 总图 then 通信保障, both top-level',
              [s['name'] for s in trip['sib']] == ['总图', '通信保障'] and all(s['up'] is None for s in trip['sib']) and trip['sibCanvas'],
              str(trip['sib']))
        check('child is 机巢内部 under root and still has 换电单元',
              trip['kid'] and trip['kid']['name'] == '机巢内部' and trip['kid']['up'] == 'root'
              and '换电单元' in trip['kid']['nodes'] and trip['kidCanvas'] and trip['childId'] == trip['kid']['id'],
              str(trip['kid']))
        check('root has no door to the new pages', trip['doors'] == [] and trip['pageOrder'] is False, str(trip['doors']))
        check('new pages carry their name as a title', trip['sibTitle'] == ['通信保障'] and trip['kidTitle'] == ['机巢内部'], str(trip['sibTitle']) + ' ' + str(trip['kidTitle']))

        demo = page.evaluate(DEMO)
        print('predicate 3', demo)
        check('demo nest is a child of root', demo['childOfRoot'], str(demo))
        check('enterSub opens the nest page', demo['cur'] == 'pnest' and demo['pageName'] == demo['nestName'] and demo['canvas'] and demo['grew'] == 0, str(demo))

        page.evaluate(OLD)
        page.click('#crumb [data-add="sib"]')
        sib = page.evaluate(r"""
() => {
  const row = [...document.querySelectorAll('#crumb .cr')].find(r => ((r.querySelector('.lab') || {}).textContent) === '同级');
  const on = row && row.querySelector('[data-page].on');
  const canvas = (document.querySelector('#world') || {}).textContent || '';
  return {
    name: on ? on.textContent : '',
    chips: row ? [...row.querySelectorAll('[data-page]')].map(b => b.textContent) : [],
    canvas,
    pageName: (document.querySelector('#d-pname') || {}).value || ''
  };
}
""")
        print('predicate 4 sibling', sib)
        check('＋同级 adds a sibling chip and shows that page',
              sib['name'] == '未命名页' and sib['chips'] == ['总图', '未命名页'] and sib['pageName'] == '未命名页' and sib['canvas'].find('未命名页') >= 0,
              str(sib))
        page.click('#crumb [data-page="root"]')
        back = page.evaluate(r"""
() => {
  const canvas = (document.querySelector('#world') || {}).textContent || '';
  const row = [...document.querySelectorAll('#crumb .cr')].find(r => ((r.querySelector('.lab') || {}).textContent) === '同级');
  const on = row && row.querySelector('[data-page].on');
  return {
    canvas,
    pageName: (document.querySelector('#d-pname') || {}).value || '',
    on: on ? on.textContent : '',
    still: row ? [...row.querySelectorAll('[data-page]')].map(b => b.textContent) : []
  };
}
""")
        print('predicate 4 root', back)
        check('root chip brings 巡逻节点 back',
              back['pageName'] == '总图' and back['on'] == '总图' and '巡逻节点' in back['canvas'] and '未命名页' not in back['canvas'] and back['still'] == ['总图', '未命名页'],
              str(back))

        if errors:
            check('page has no script errors', False, ' | '.join(errors))
        else:
            check('page has no script errors', True)
        browser.close()
    if fails:
        print('FAILED', len(fails))
        for f in fails:
            print(' -', f)
        return 1
    print('PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
