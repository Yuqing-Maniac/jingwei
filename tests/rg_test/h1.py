import sys, json
from playwright.sync_api import sync_playwright
mode=sys.argv[1] if len(sys.argv)>1 else 'rule'
src=sys.argv[2] if len(sys.argv)>2 else 'cur'
content=open('content.txt',encoding='utf-8').read()
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1500,'height':950})
    errs=[]; pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and errs.append(m.text))
    pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(800)
    pg.evaluate("localStorage.setItem('hongtu.textgen.v1', JSON.stringify({base:'http://127.0.0.1:8765/v1', model:'deepseek-v4-flash'}))")
    pg.keyboard.press('Control+Shift+L'); pg.wait_for_timeout(600)
    if src!='cur':
        pg.select_option('#rg-src', src); pg.wait_for_timeout(500)
    print('dialect:\n'+pg.input_value('#rg-dialect')[:3000])
    print('summary:', pg.inner_text('#rg-sum'))
    pg.fill('#rg-name','海岛无人值守监视系统'); pg.fill('#rg-content',content)
    pg.check(f'input[name=rg-eng][value={mode}]')
    if mode=='rule':
        ins=pg.query_selector_all('#rg-map input[data-f=name]')
        names=['感知层','传输层','处理层','应用层','保障层']
        for i,el in enumerate(ins[:5]): el.fill(names[i])
    pg.click('#rg-gen'); pg.wait_for_timeout(2500 if mode=='llm' else 800)
    print('msg:', pg.inner_text('#rg-msg')); print('rep:', pg.inner_text('#rg-rep'))
    pg.screenshot(path=f'dlg_{mode}_{src}.png')
    if not pg.is_disabled('#rg-apply'):
        pg.click('#rg-apply'); pg.wait_for_timeout(800); pg.screenshot(path=f'canvas_{mode}_{src}.png')
        print('pages', pg.evaluate("Object.keys(doc.pages).length"), 'view', pg.evaluate("P().view"), 'theme', pg.evaluate("doc.theme"))
    print('ERR', errs)
    b.close()
