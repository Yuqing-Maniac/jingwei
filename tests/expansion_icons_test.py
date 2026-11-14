"""Exercise the shipped naval/one-way palette, origin, paint, and file workflows."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_work' / 'expansion-test'
NAVAL = [
    'naval_hhq9b', 'naval_hhq9c', 'naval_hhq16', 'naval_hhq10',
    'naval_yj83j', 'naval_hhq10_launcher', 'naval_yj83j_launcher',
]
ONEWAY = ['oneway_shahed136', 'oneway_shahed131', 'oneway_lucas']
KEYS = ONEWAY + NAVAL
ORIGIN_NAMES = {'ir': '伊朗', 'us': '美国', 'cn': '中国'}
ALIASES = {
    'oneway_shahed136': ['Shahed-136', 'Shahed136', 'Geran-2', 'Geran2', '天竺葵2', '沙赫德136'],
    'oneway_shahed131': ['Shahed-131', 'Shahed131', 'Geran-1', 'Geran1', '天竺葵1', '沙赫德131'],
    'oneway_lucas': ['LUCAS'],
    'naval_hhq9b': ['HHQ-9B', '海红旗9B'],
    'naval_hhq9c': ['HHQ-9C', '海红旗9C'],
    'naval_hhq16': ['HHQ-16', '海红旗16'],
    'naval_hhq10': ['HHQ-10', '海红旗10'],
    'naval_yj83j': ['YJ-83J', '鹰击83J'],
    'naval_hhq10_launcher': ['八联装发射器'],
    'naval_yj83j_launcher': ['舰载发射架'],
}


def expected_origin(key):
    return 'ir' if key.startswith('oneway_shahed') else 'us' if key == 'oneway_lucas' else 'cn'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1640, 'height': 1100}, accept_downloads=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist/offline.html').as_uri()), timeout=90000)
        page.wait_for_selector('#pal-appearance')
        assert page.evaluate('ICONS.length') == 690, 'Run against the complete 690-icon release build'
        metadata = page.evaluate('''keys => keys.map(key => {
          const i=ICON_MAP[key];return i && {key,name:i.name,origin:i.originCountry,
            paint:i.defaultAffiliation,countries:Object.keys(i.countries||{})};
        })''', KEYS)
        assert all(metadata), metadata
        for item in metadata:
            origin = expected_origin(item['key'])
            paint = {'ir': 'neutral', 'us': 'blue', 'cn': 'red'}[origin]
            assert item['origin'] == origin and item['paint'] == paint, item
            assert item['countries'] == ([] if origin == 'ir' else [origin]), item

        def palette_item(key):
            return page.locator('#palette .pitem[data-add*="lib:' + key + '"]').first

        def state():
            return page.evaluate('''() => {const n=selectedNodes()[0];return {
              id:n.id,icon:n.icon,appearance:n.appearance||null,paint:n.affiliation||null,
              uri:nodeLayout(n).icon.uri,origin:ICON_MAP[n.icon.slice(4)].originCountry};}''')

        def select(node_id):
            page.locator('#world g[data-id="' + node_id + '"]').first.click()
            assert state()['id'] == node_id

        # A foreign named platform must not leak into either national palette.
        for appearance, expected in [('generic', KEYS), ('cn', NAVAL), ('us', ['oneway_lucas'])]:
            page.select_option('#pal-appearance', appearance)
            for key in KEYS:
                page.fill('#pal-q', key)
                assert bool(palette_item(key).count()) == (key in expected), (appearance, key)

        # Only an empty document is injected as a fixture. All placement, property
        # changes, selections, save/open and export below use actual UI handlers.
        page.evaluate("doc.pages={root:{id:'root',name:'Expansion icons',nodes:[],links:[],noLegend:true}};cur='root';render()")
        page.select_option('#pal-appearance', 'generic')
        nodes = {}
        for index, key in enumerate(KEYS):
            for query in ALIASES[key]:
                page.fill('#pal-q', query)
                assert palette_item(key).count() == 1, (key, query)
            palette_item(key).click()
            current = state()
            origin = expected_origin(key)
            paint = {'ir': 'neutral', 'us': 'blue', 'cn': 'red'}[origin]
            assert current['icon'] == 'lib:' + key, current
            assert current['appearance'] == (None if origin == 'ir' else origin), current
            assert current['paint'] == paint and current['origin'] == origin, current
            assert page.locator('#p-icon-origin').inner_text() == ORIGIN_NAMES[origin]
            options = page.locator('#p-appearance option').evaluate_all('(xs)=>xs.map(x=>x.value)')
            assert set(options) == (set() if origin == 'ir' else {'generic', origin}), (key, options)
            nodes[key] = current['id']
            # Arrange via property inputs to make the production canvas inspectable.
            for prop, value in {'x': 30 + index % 4 * 205, 'y': 30 + index // 4 * 205,
                                'w': 165, 'h': 165}.items():
                page.locator('[data-geo="' + prop + '"]').fill(str(value))
            page.locator('#p-text').click()
            page.locator('#p-noBox').check()
        page.fill('#pal-q', '单程攻击无人机')
        page.click('#z-fit')
        page.screenshot(path=str(OUT / 'generic-defaults.png'))
        page.locator('#svg').screenshot(path=str(OUT / 'generic-canvas.png'))

        # Select placed objects on the canvas; changing team paint must preserve
        # both national geometry and actual origin, including Iran's generic asset.
        for key in KEYS:
            select(nodes[key])
            before = state()
            paint = 'red' if key == 'oneway_lucas' else 'blue'
            page.select_option('#p-affiliation', paint)
            after = state()
            assert after['paint'] == paint and after['uri'] != before['uri'], key
            assert after['appearance'] == before['appearance'] and after['origin'] == before['origin'], key
            assert page.locator('#p-icon-origin').inner_text() == ORIGIN_NAMES[expected_origin(key)]
            page.click('#b-undo')
            select(nodes[key])
            assert state()['uri'] == before['uri'] and state()['paint'] == before['paint'], key
            page.click('#b-redo')
            select(nodes[key])
            assert state()['uri'] == after['uri'] and state()['paint'] == paint, key

        snapshot = page.evaluate('P().nodes.map(n=>({id:n.id,icon:n.icon,appearance:n.appearance||null,paint:n.affiliation||null}))')
        with page.expect_download(timeout=90000) as download:
            page.click('#b-save')
        saved_path = OUT / 'expansion.json'
        download.value.save_as(saved_path)
        saved = json.loads(saved_path.read_text())
        saved_nodes = saved['doc']['pages']['root']['nodes']
        assert len(saved_nodes) == 10
        for n in saved_nodes:
            key = n['icon'][4:]
            assert n.get('appearance') == (None if expected_origin(key) == 'ir' else expected_origin(key)), n
            assert n['affiliation'] == ('red' if key == 'oneway_lucas' else 'blue'), n
        # Make the in-memory document different first, so a broken file-open
        # handler cannot pass by leaving the already-saved document untouched.
        page.select_option('#p-affiliation', 'neutral')
        assert state()['paint'] == 'neutral'
        # Read the downloaded file through the real file-picker event and rerender.
        with page.expect_file_chooser() as chooser:
            page.click('#b-open')
        chooser.value.set_files(saved_path)
        page.wait_for_function('''expected => JSON.stringify(P().nodes.map(n=>({
          id:n.id,icon:n.icon,appearance:n.appearance||null,paint:n.affiliation||null
        })))===JSON.stringify(expected)''', arg=snapshot)
        assert page.evaluate('P().nodes.map(n=>({id:n.id,icon:n.icon,appearance:n.appearance||null,paint:n.affiliation||null}))') == snapshot
        for key in KEYS:
            select(nodes[key])
            assert page.locator('#p-icon-origin').inner_text() == ORIGIN_NAMES[expected_origin(key)]

        with page.expect_download(timeout=90000) as download:
            page.click('#b-export')
            page.click('[data-exp="drawio"]')
        drawio_path = OUT / 'expansion.drawio'
        download.value.save_as(drawio_path)
        exported = [e.attrib for e in ET.parse(drawio_path).iter() if e.get('ht_icon', '').startswith('lib:')]
        assert len(exported) == 10, len(exported)
        for n in exported:
            key = n['ht_icon'][4:]
            assert n.get('ht_appearance', '') == ('' if expected_origin(key) == 'ir' else expected_origin(key)), n
            assert n.get('ht_affiliation') == ('red' if key == 'oneway_lucas' else 'blue'), n
        # Export a real SVG too: it must render the current independently painted
        # icons, not silently fall back to generic/default imagery.
        with page.expect_download(timeout=90000) as download:
            page.click('#b-export')
            page.click('[data-exp="svg"]')
        svg_path = OUT / 'expansion.svg'
        download.value.save_as(svg_path)
        svg_text = svg_path.read_text()
        rendered_uris = page.evaluate('P().nodes.map(n=>nodeLayout(n).icon.uri)')
        assert all(uri in svg_text for uri in rendered_uris), 'SVG lost selected national geometry or team paint'
        page.screenshot(path=str(OUT / 'independent-paint.png'))
        assert not errors, errors
        browser.close()
    print('expansion_icons_test ok: 690 icons; 7 CN naval red, Iranian Shahed neutral, US LUCAS blue; aliases, UI placement/origin, paint, undo/redo, JSON save/open, draw.io metadata and SVG')


if __name__ == '__main__':
    main()
