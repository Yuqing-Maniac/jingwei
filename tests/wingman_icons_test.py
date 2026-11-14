"""Named wingmen keep their actual country of origin separate from team paint."""
import os
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = {'cn': '中国', 'us': '美国', 'au': '澳大利亚', 'tr': '土耳其', 'ru': '俄罗斯'}


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist/offline.html').as_uri()), timeout=90000)
        page.wait_for_selector('#pal-appearance')
        models = page.evaluate('''() => ICONS.filter(i=>i.key.startsWith('wingman_')).map(i=>({
          key:i.key,name:i.name,origin:i.originCountry,keywords:i.keywords||[],
          countries:Object.keys(i.countries||{}),countryNames:Object.values(i.countries||{}).map(c=>c.name)
        }))''')
        counts = Counter(m['origin'] for m in models)
        assert len(models) >= 13 and counts['us'] >= 6 and counts['cn'] >= 3, counts
        assert sum(counts[c] for c in ['au', 'tr', 'ru']) >= 4, counts
        assert all(counts[c] for c in COUNTRIES), counts
        for model in models:
            assert model['origin'] in COUNTRIES, model
            assert model['countries'] == ([model['origin']] if model['origin'] in ['cn', 'us'] else []), model
        page.evaluate("doc.pages={root:{id:'root',name:'Wingman test',nodes:[],links:[],noLegend:true}};cur='root';render()")

        def palette_item(key):
            return page.locator('#palette .pitem[data-add*="lib:' + key + '"]').first

        def select_node(node_id):
            page.evaluate('(id)=>{selectNodes([id]);render()}', node_id)

        # Generic shows every country; national palettes include matching named models only.
        for appearance in ['generic', 'cn', 'us']:
            page.select_option('#pal-appearance', appearance)
            page.fill('#pal-q', 'wingman_')
            shown = page.evaluate('''() => [...new Set(Array.from(document.querySelectorAll('#palette [data-add]'))
              .map(e=>JSON.parse(e.dataset.add).icon||'').filter(k=>k.startsWith('lib:wingman_')).map(k=>k.slice(4)))].sort()''')
            expected = sorted(m['key'] for m in models if appearance == 'generic' or m['origin'] == appearance)
            assert shown == expected, (appearance, shown, expected)
            page.fill('#pal-q', 'fighter')
            assert palette_item('fighter').count(), appearance

        page.select_option('#pal-appearance', 'generic')
        placed = []
        for model in models:
            key, origin = model['key'], model['origin']
            # Type both metadata names and keywords, then place by exact runtime key.
            for query in [model['name']] + model['keywords'][:1] + model['countryNames'][:1]:
                page.fill('#pal-q', query)
                assert palette_item(key).count(), (key, query)
            page.fill('#pal-q', key.upper().replace('_', ' '))
            assert palette_item(key).count(), key
            palette_item(key).click()
            node_id = page.evaluate('selectedNodes()[0].id')
            placed.append(node_id)
            expected_appearance = origin if origin in ['cn', 'us'] else None
            expected_paint = 'red' if origin == 'cn' else 'blue' if origin == 'us' else 'neutral'
            defaults = page.evaluate('''() => {const n=selectedNodes()[0];return {
              appearance:n.appearance||null,paint:iconSide(n.affiliation,n.appearance),
              uri:nodeLayout(n).icon.uri,expected:svgUri((ICON_MAP[n.icon.slice(4)].countries?.[n.appearance]||ICON_MAP[n.icon.slice(4)]).variants[iconSide(n.affiliation,n.appearance)])
            };}''')
            assert defaults['appearance'] == expected_appearance and defaults['paint'] == expected_paint, (model, defaults)
            assert defaults['uri'] == defaults['expected'], key
            assert page.locator('#p-icon-origin').inner_text() == COUNTRIES[origin]
            if origin not in ['cn', 'us']:
                assert page.locator('#p-appearance option[value=cn],#p-appearance option[value=us]').count() == 0
            # Independent team paint changes, then one undo restores origin defaults.
            paint = 'blue' if expected_paint != 'blue' else 'red'
            page.select_option('#p-affiliation', paint)
            changed = page.evaluate('''() => {const n=selectedNodes()[0];return [n.appearance||null,n.affiliation,nodeLayout(n).icon.uri]}''')
            assert changed[:2] == [expected_appearance, paint] and changed[2] != defaults['uri'], (key, changed)
            page.evaluate('undo()')
            restored = page.evaluate('''id=>{const n=nodeById(id);return [n.appearance||null,iconSide(n.affiliation,n.appearance),nodeLayout(n).icon.uri]}''', node_id)
            assert restored == [expected_appearance, expected_paint, defaults['uri']], (key, restored)
            select_node(node_id)
            # Replacement picker searches both country model names and keywords.
            page.click('#p-icon')
            for query in [model['name']] + model['keywords'][:1] + model['countryNames'][:1]:
                page.fill('#ic-q', query)
                assert page.locator('#ic-grid [data-ic="lib:' + key + '"]').count(), (key, query)
            page.click('#ic-close')

        # Replacing a US model with a foreign generic master clears inherited US appearance.
        us = next(m for m in models if m['origin'] == 'us')
        foreign = next(m for m in models if m['origin'] == 'au')
        us_id = placed[models.index(us)]
        select_node(us_id)
        page.click('#p-icon')
        page.fill('#ic-q', foreign['name'])
        page.locator('#ic-grid [data-ic="lib:' + foreign['key'] + '"]').click()
        assert page.evaluate('''id=>{const n=nodeById(id);return[n.icon,n.appearance||null,n.affiliation]}''', us_id) == ['lib:' + foreign['key'], None, 'neutral']
        page.evaluate('undo()')
        assert page.evaluate('''id=>{const n=nodeById(id);return[n.icon,n.appearance,n.affiliation]}''', us_id) == ['lib:' + us['key'], 'us', 'blue']
        page.evaluate('redo()')
        select_node(us_id)
        page.select_option('#p-affiliation', 'red')
        before = page.evaluate('P().nodes.map(n=>[n.id,n.icon,n.appearance||null,n.affiliation||null])')
        page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
        assert page.evaluate('P().nodes.map(n=>[n.id,n.icon,n.appearance||null,n.affiliation||null])') == before
        assert not errors, errors
        browser.close()
    print('wingman_icons_test ok:', dict(counts), 'origin defaults, filters, search, independent paint, replacement, undo, save')


if __name__ == '__main__':
    main()
