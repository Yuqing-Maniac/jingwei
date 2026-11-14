"""Recon roles and named platforms keep national geometry separate from paint."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MISSIONS = ['uav_recon_eo', 'uav_recon_radar', 'uav_recon_sigint', 'usv_minesweeper']
MODELS = ['wz7', 'wz8', 'wz10', 'gj2', 'gj11', 'gj21']


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(os.environ.get('JW_TEST_URL', (ROOT / 'dist/offline.html').as_uri()), timeout=90000)
        page.wait_for_selector('#pal-appearance')
        metadata = page.evaluate('''keys => keys.map(key => {
          const i=ICON_MAP[key];return i && {key,origin:i.originCountry,side:i.defaultAffiliation,countries:Object.keys(i.countries||{})};
        })''', MISSIONS + MODELS)
        assert all(metadata), metadata
        for item in metadata[:4]:
            assert sorted(item['countries']) == ['cn', 'us'], item
        for item in metadata[4:]:
            assert item == dict(key=item['key'], origin='cn', side='red', countries=['cn']), item
        page.evaluate("doc.pages={root:{id:'root',name:'Icon test',nodes:[],links:[],noLegend:true}};cur='root';render()")

        def search(query):
            page.fill('#pal-q', query)

        def item(key):
            return page.locator('#palette .pitem[data-add*="lib:' + key + '"]').first

        # The six Chinese platforms appear in both generic and CN libraries, but not US.
        for appearance in ['generic', 'cn', 'us']:
            page.select_option('#pal-appearance', appearance)
            for key in MODELS:
                code = key.upper().replace('WZ', 'WZ-').replace('GJ', 'GJ-')
                search(code)
                assert item(key).count() == (0 if appearance == 'us' else 1), (appearance, key)
                if appearance == 'generic':
                    item(key).click()
                    assert page.evaluate("[selectedNodes()[0].appearance,selectedNodes()[0].affiliation]") == ['cn', 'red']
                    placed = page.evaluate('selectedNodes()[0].id')
                    page.select_option('#p-affiliation', 'blue')
                    assert page.evaluate("selectedNodes()[0].appearance") == 'cn'
                    page.evaluate('undo()')
                    assert page.evaluate('(id)=>nodeById(id).affiliation', placed) == 'red'
        page.select_option('#pal-appearance', 'generic')
        for query, key in [('无侦7', 'wz7'), ('无侦-8', 'wz8'), ('攻击21', 'gj21')]:
            search(query)
            assert item(key).count(), (query, key)

        # Generic roles retain their original unspecified appearance/paint.
        assert page.evaluate("JSON.stringify(iconPlaceSpec('lib:fighter','test',96,96))") == '{"type":"equip","w":96,"h":96,"text":"test","icon":"lib:fighter"}'
        for key in MISSIONS:
            uris = []
            for country, paint in [('cn', 'red'), ('us', 'blue')]:
                page.select_option('#pal-appearance', country)
                search(key)
                assert item(key).count(), (key, country)
                item(key).click()
                assert page.evaluate("[selectedNodes()[0].appearance,selectedNodes()[0].affiliation]") == [country, paint]
                uri = page.evaluate('nodeLayout(selectedNodes()[0]).icon.uri')
                uris.append(uri)
                pixels = page.evaluate('''async uri => {
                  const img=new Image();img.src=uri;await img.decode();
                  const c=document.createElement('canvas');c.width=c.height=128;
                  const x=c.getContext('2d');x.drawImage(img,0,0,128,128);
                  const a=x.getImageData(0,0,128,128).data;let red=0,blue=0,opaque=0;
                  for(let i=0;i<a.length;i+=4)if(a[i+3]>80){opaque++;if(a[i]>a[i+2]*1.24&&a[i]-a[i+2]>25)red++;if(a[i+2]>a[i]*1.24&&a[i+2]>a[i+1]*1.13&&a[i+2]-a[i]>25)blue++;}
                  return {red,blue,opaque};
                }''', uri)
                assert pixels['opaque'] > 200 and pixels[paint] / pixels['opaque'] > .01, (key, country, pixels)
            assert uris[0] != uris[1], key
        for query in ['扫雷', '反水雷', '猎雷']:
            search(query)
            assert item('usv_minesweeper').count(), query
            assert not item('usv_minelayer').count(), query

        # Replacement search includes country-specific names and normalizes model codes.
        page.evaluate('openIconPicker(selectedNodes()[0])')
        for key in MISSIONS:
            name = page.evaluate('key=>ICON_MAP[key].countries.us.name', key)
            assert name, key
            page.fill('#ic-q', name)
            assert page.locator('#ic-grid [data-ic="lib:' + key + '"]').count(), (key, name)
        for query in ['WZ-7', '无侦7', 'GJ-21']:
            page.fill('#ic-q', query)
            key = 'gj21' if query == 'GJ-21' else 'wz7'
            assert page.locator('#ic-grid [data-ic="lib:' + key + '"]').count(), query
        # A US role replaced by a Chinese named platform changes its origin default once.
        page.locator('#ic-grid [data-ic="lib:gj21"]').click()
        target = page.evaluate('selectedNodes()[0].id')
        assert page.evaluate("[selectedNodes()[0].icon,selectedNodes()[0].appearance,selectedNodes()[0].affiliation]") == ['lib:gj21', 'cn', 'red']
        page.evaluate('undo()')
        assert page.evaluate('(id)=>[nodeById(id).icon,nodeById(id).appearance,nodeById(id).affiliation]', target) == ['lib:usv_minesweeper', 'us', 'blue']
        page.evaluate('redo()')
        page.evaluate('(id)=>{selectNodes([id]);render()}', target)
        page.select_option('#p-affiliation', 'blue')
        before = page.evaluate('P().nodes.map(n=>[n.id,n.icon,n.appearance,n.affiliation])')
        page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
        assert page.evaluate('P().nodes.map(n=>[n.id,n.icon,n.appearance,n.affiliation])') == before
        assert page.evaluate('(id)=>[nodeById(id).appearance,nodeById(id).affiliation]', target) == ['cn', 'blue']
        assert not errors, errors
        browser.close()
    print('recon_icons_test ok: ten keys, national geometry/paint, model defaults/filter/search, replacement, undo, save')


if __name__ == '__main__':
    main()
