#!/usr/bin/env python3
import sys
from playwright.sync_api import sync_playwright

URL = 'file:///agent/repos/jingwei/dist/offline.html'
INSTALL = r"""(layout) => {
  const d = {
    name: '密度试验', theme: 'report', custom: {},
    statusLabels: { base: '延续', new: '本期新增', key: '重点关注' },
    pages: { root: { id: 'root', name: '总图', nodes: [], links: [] } }
  };
  if (layout) d.layout = layout;
  const band = mkNode({ type: 'band', text: '装备带', x: 0, y: 0, w: 1400, h: 160 });
  d.pages.root.nodes.push(band);
  const xs = [];
  for (let i = 0; i < 6; i++) {
    const x = 40 + i * 200;
    xs.push(x);
    d.pages.root.nodes.push(mkNode({
      type: 'equip', text: '装备' + (i + 1), icon: 'lib:uav_quad', noBox: true,
      parent: band.id, x: x, y: 30, w: 104, h: 96, size: 12
    }));
  }
  loadDoc(d);
  return xs;
}"""
MEASURE = r"""() => {
  const p = P();
  const band = p.nodes.find(n => n.type === 'band' && !n.parent);
  const nodes = p.nodes.filter(n => n.type === 'equip');
  const rows = [];
  const sorted = nodes.slice().sort((a, b) => a.y - b.y || a.x - b.x);
  for (const n of sorted) {
    const row = rows[rows.length - 1];
    if (row && Math.abs((n.y + n.h / 2) - (row[0].y + row[0].h / 2)) <= 36) row.push(n);
    else rows.push([n]);
  }
  const raw = [];
  for (const row of rows) {
    row.sort((a, b) => a.x - b.x);
    for (let i = 1; i < row.length; i++) raw.push(row[i].x - (row[i - 1].x + row[i - 1].w));
  }
  return {
    n: nodes.length,
    gaps: raw.map(g => Math.round(g * 10) / 10),
    raw: raw,
    band: band ? band.w : null
  };
}"""

fails = []


def check(name, cond, detail):
    print(('ok  ' if cond else 'FAIL') + ' ' + name + '  ' + detail, flush=True)
    if not cond:
        fails.append(name)


def ready(page):
    page.wait_for_function("() => typeof loadDoc === 'function' && !!document.querySelector('#b-beauty')")
    ignore = page.locator('#jw-bak-ignore')
    if ignore.count():
        ignore.click()


def install(page, layout=None):
    return page.evaluate(INSTALL, layout)


def measure(page):
    m = page.evaluate(MEASURE)
    print('    gaps=%s band=%s n=%s' % (m['gaps'], m['band'], m['n']), flush=True)
    return m


def tight(m):
    return m['n'] == 6 and len(m['raw']) >= 1 and all(0 <= g <= 24 for g in m['raw'])


def wide(m):
    return m['n'] == 6 and any(g >= 80 for g in m['raw'])


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True, args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(URL)
        ready(page)
        page.evaluate("() => localStorage.removeItem('hongtu.layout')")

        install(page, None)
        page.click('#b-beauty')
        m = measure(page)
        check('1 fresh no layout packs', tight(m) and m['band'] is not None and m['band'] < 900,
              'want every gap<=24 and band<900')

        install(page, {'mode': 'standard', 'page': 'a4p', 'font': 10.5})
        page.click('#b-beauty')
        m = measure(page)
        check('2 explicit standard spreads', wide(m), 'want some gap>=80')

        install(page, {'mode': 'compact', 'page': 'a4p', 'font': 10.5})
        page.click('#b-beauty')
        m = measure(page)
        check('3 explicit compact packs', tight(m) and m['band'] is not None and m['band'] < 900,
              'want every gap<=24 and band<900')

        xs = install(page, None)
        back = page.evaluate("() => ({xs: P().nodes.filter(n => n.type==='equip').sort((a,b)=>a.x-b.x).map(n => n.x), layout: doc.layout === undefined ? null : doc.layout})")
        print('    load xs=%s layout=%s' % (back['xs'], back['layout']), flush=True)
        check('4 loadDoc keeps x and omits layout', back['xs'] == xs and back['layout'] is None,
              'want x unchanged and no layout')

        page.click('#d-lay [data-v=standard]')
        page.reload()
        ready(page)
        install(page, None)
        page.click('#b-beauty')
        m = measure(page)
        check('5 remembered standard spreads', wide(m), 'want some gap>=80 after reload')

        page.click('#d-lay [data-v=compact]')
        page.reload()
        ready(page)
        install(page, None)
        page.click('#b-beauty')
        m = measure(page)
        check('5 remembered compact packs', tight(m), 'want every gap<=24 after reload')

        install(page, {'mode': 'report', 'page': 'a4p', 'font': 10.5})
        page.click('#b-beauty')
        m = measure(page)
        check('6 report keeps icon gaps tight', tight(m), 'want every gap<=24')

        if errors:
            print('pageerror', errors[:4], flush=True)
            fails.append('pageerror')
        browser.close()
    if fails:
        print('FAILED', ', '.join(fails), flush=True)
        sys.exit(1)
    print('PASSED', flush=True)


if __name__ == '__main__':
    main()
