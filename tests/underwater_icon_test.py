"""A generic underwater concept has team paint, without a fictitious national model."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(os.environ.get('JW_TEST_URL',(ROOT/'dist/offline.html').as_uri()),timeout=90000)
    page.wait_for_selector('#pal-appearance')
    result=page.evaluate('''()=>{const i=ICON_MAP.underwater_prepositioned_weapon;
      return i&&{team:i.teamPaintOnly,countries:i.countries||null,paints:Object.keys(i.variants),unique:new Set(Object.values(i.variants)).size};}''')
    assert result and result['team'] and result['countries'] is None and result['unique']==3,result
    assert sorted(result['paints'])==['blue','neutral','red'],result
    for country,paint in [('generic',None),('cn','red'),('us','blue')]:
        page.select_option('#pal-appearance',country)
        page.fill('#pal-q','水下预制武器')
        icon=page.locator('#palette [data-add*="lib:underwater_prepositioned_weapon"]')
        assert icon.count()==1
        icon.click()
        state=page.evaluate('''()=>{const n=selectedNodes()[0];return {icon:n.icon,paint:n.affiliation||null,appearance:n.appearance||null};}''')
        assert state==dict(icon='lib:underwater_prepositioned_weapon',paint=paint,appearance=None),state
    page.select_option('#p-affiliation','red')
    before=page.evaluate('P().nodes.map(n=>[n.id,n.icon,n.affiliation,n.appearance||null])')
    page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
    assert page.evaluate('P().nodes.map(n=>[n.id,n.icon,n.affiliation,n.appearance||null])')==before
    assert not errors,errors
    browser.close()
print('underwater_icon_test ok: generic concept, three paints, national palette defaults, typo search and save')
