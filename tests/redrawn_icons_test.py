import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None,args=['--no-sandbox'])
    page=browser.new_page(accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(os.environ.get('JW_TEST_URL',(ROOT/'dist/offline.html').as_uri()))
    result=page.evaluate('''() => {
      const icons=ICONS.filter(x=>x.variants);
      const keys=new Set(icons.map(x=>x.key));
      return {count:icons.length,unique:keys.size,all:ICONS.length,
        variants:icons.every(x=>['neutral','red','blue'].every(s=>x.variants[s].includes('data:image/webp;base64,')) && new Set(Object.values(x.variants)).size===3)};
    }''')
    assert result['count']==398 and result['unique']==398 and result['variants'],result
    page.evaluate("selectNodes([P().nodes.find(x=>x.icon && x.icon.startsWith('lib:')).id]);render();")
    node_id=page.evaluate('selectedNodes()[0].id')
    page.select_option('#p-affiliation','red')
    red=page.evaluate('nodeLayout(selectedNodes()[0]).icon.uri')
    page.select_option('#p-affiliation','blue')
    blue=page.evaluate('nodeLayout(selectedNodes()[0]).icon.uri')
    assert red!=blue
    page.evaluate('undo()')
    assert page.evaluate('(id) => nodeById(id).affiliation',node_id)=='red'
    saved=page.evaluate('projectJSON()')
    page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
    assert page.evaluate('projectJSON()')==saved
    assert not errors,errors
    browser.close()
    print('redrawn_icons_test ok: 398 icons, 3 variants, selection, undo, serialization')
