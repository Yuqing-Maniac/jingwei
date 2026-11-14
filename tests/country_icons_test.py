"""Country selection must survive editing, save/load, export and grouping."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('JW_CHROME') or None,args=['--no-sandbox'])
    page=browser.new_page(accept_downloads=True)
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto(os.environ.get('JW_TEST_URL',(ROOT/'dist/offline.html').as_uri()),timeout=90000)
    page.wait_for_selector('#pal-appearance')
    page.select_option('#pal-appearance','cn')
    page.fill('#pal-q','战斗机')
    page.locator('#palette .pitem[data-add]').first.click()
    assert page.evaluate("selectedNodes()[0].appearance")=='cn'
    assert page.evaluate("selectedNodes()[0].affiliation")=='red'
    node_id=page.evaluate('selectedNodes()[0].id')
    cn=page.evaluate('nodeLayout(selectedNodes()[0]).icon.uri')
    page.select_option('#p-appearance','us')
    assert page.evaluate("selectedNodes()[0].affiliation")=='blue'
    us=page.evaluate('nodeLayout(selectedNodes()[0]).icon.uri')
    assert cn!=us
    page.select_option('#p-affiliation','neutral')
    assert page.evaluate("selectedNodes()[0].affiliation")=='neutral'
    assert page.evaluate("nodeLayout(selectedNodes()[0]).icon.uri===svgUri(ICON_MAP.fighter.countries.us.variants.neutral)")
    roundtrip=page.evaluate('''async () => {
      const n=selectedNodes()[0];n.flipX=true;n.flipY=true;render();
      const got=await DrawIO.importText(DrawIO.exportString([P()]));
      const back=got.pages[0].nodes.find(x=>x.icon==='lib:fighter'&&x.appearance==='us');
      return {appearance:back.appearance,paint:back.affiliation,x:back.flipX,y:back.flipY};
    }''')
    assert roundtrip==dict(appearance='us',paint='neutral',x=True,y=True),roundtrip
    page.select_option('#p-affiliation','blue')
    page.select_option('#p-affiliation','red')
    assert page.evaluate('nodeLayout(selectedNodes()[0]).icon.uri')!=us
    page.evaluate('undo()')
    assert page.evaluate('(id)=>nodeById(id).affiliation',node_id)=='blue'
    page.evaluate('(id)=>{selectNodes([id]);render()}',node_id)
    snapshot=page.evaluate('projectJSON()')
    page.evaluate('loadDoc(JSON.parse(projectJSON()).doc)')
    assert page.evaluate('projectJSON()')==snapshot
    assert page.evaluate("iconURI('lib:fighter')===svgUri(ICON_MAP.fighter.variants.neutral)")
    assert page.evaluate("iconURI('lib:fighter',undefined,'cn')===svgUri(ICON_MAP.fighter.countries.cn.variants.red)")
    assert page.evaluate("iconURI('lib:fighter',undefined,'us')===svgUri(ICON_MAP.fighter.countries.us.variants.blue)")
    assert page.evaluate("Combo.formationSpec({icon:'lib:fighter',appearance:'cn',affiliation:'blue',count:3,pattern:'line',gap:0.3}).members.every(m=>m.appearance==='cn'&&m.affiliation==='blue')")
    # Existing group/ungroup path must retain both appearance and paint.
    page.evaluate("""() => {const a=mkNode({icon:'lib:fighter',appearance:'cn',affiliation:'blue',x:100,y:100}),b=mkNode({icon:'lib:fighter',appearance:'us',affiliation:'red',x:300,y:100});P().nodes.push(a,b);selectNodes([a.id,b.id]);render();Combo.groupSelection();}""")
    members=page.evaluate("doc.custom[selectedNodes()[0].icon.slice(3)].combo.members.map(m=>[m.appearance,m.affiliation])")
    assert members==[['cn','blue'],['us','red']],members
    page.evaluate('Combo.ungroup()')
    assert page.evaluate('selectedNodes().map(n=>[n.appearance,n.affiliation])')==members
    assert page.evaluate("exportSVGString(P(),false).str.includes(iconURI('lib:fighter','blue','cn'))")
    # Mixed effective defaults must remain mixed when grouping; outer neutral overrides both.
    mixed=page.evaluate("""() => {
      const a=mkNode({icon:'lib:fighter',appearance:'cn',affiliation:'red',flipX:true,x:100,y:100}),b=mkNode({icon:'lib:fighter',appearance:'us',x:300,y:100});
      P().nodes.push(a,b);selectNodes([a.id,b.id]);render();Combo.groupSelection();
      const n=selectedNodes()[0],spec=doc.custom[n.icon.slice(3)].combo;
      const original=iconURI(n.icon),neu=iconURI(n.icon,'neutral');
      const expected=Combo.tinted(spec,'neutral');
      const mirrored=decodeURIComponent(original).includes('scale(-1 1)');
      const red=iconURI(n.icon,'red');checkpoint();spec.members[0].appearance='us';doc.custom[n.icon.slice(3)].uri=svgUri(Combo.buildSVG(spec).svg);const changed=iconURI(n.icon,'red');undo();
      const restored=iconURI(n.icon,'red')===red;
      selectNodes([n.id]);Combo.ungroup();
      return {mixed:!n.affiliation,neutral:neu===expected&&neu!==original,mirrored,uncached:changed!==red,restored,back:selectedNodes().map(x=>[x.appearance,x.flipX||false])};
    }""")
    assert mixed==dict(mixed=True,neutral=True,mirrored=True,uncached=True,restored=True,back=[['cn',True],['us',False]]),mixed
    out=ROOT/'_work/country-test' ;out.mkdir(parents=True,exist_ok=True)
    for kind,call in [('png','exportPNG(1,false)'),('pptx','exportPPTX()'),('vsdx','exportVSDX()')]:
        with page.expect_download(timeout=90000) as dl:
            page.evaluate('async () => { await '+call+'; }')
        dest=out/('country.'+kind);dl.value.save_as(dest)
        assert dest.stat().st_size>1000,(kind,dest.stat().st_size)
    assert not errors,errors
    browser.close()
    print('country_icons_test ok: palette defaults, model+paint, undo, save/load, group/ungroup, SVG/PNG/PPTX/VSDX')
