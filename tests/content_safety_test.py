"""Exercise imported project content, export, and quota failures in a real browser."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get('JW_TEST_URL', (ROOT / 'dist/offline.html').as_uri())

def main():
    with sync_playwright() as pw:
        opts = {'args': ['--no-sandbox']}
        if os.environ.get('JW_CHROME'):
            opts['executable_path'] = os.environ['JW_CHROME']
        browser = pw.chromium.launch(**opts)
        pg = browser.new_page(accept_downloads=True)
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)))
        pg.goto(URL)
        pg.wait_for_selector('#world > g')
        # Import through the real file picker. Include an id, a color and a custom URI
        # so protection cannot accidentally cover only a single injection context.
        project = pg.evaluate('''() => {
          const attack = '\\"><image href="data:image/png;base64,broken" onerror="window.__unsafe=1"/><g data-x="';
          const nodes = [mkNode({id:'id'+attack, text:"O'Reilly <测试>", x:0,y:0}),
            mkNode({id:'color',text:'颜色',color:'red'+attack,x:180,y:0}),
            mkNode({id:'custom',text:'自定义',icon:'cu:test',x:0,y:120})];
          return JSON.stringify({format:'hongtu',version:1,doc:{name:'安全回归',theme:'report',
            custom:{test:{name:'图片',uri:'data:image/png;base64,broken" onerror="window.__unsafe=2'}},
            pages:{root:{id:'root',name:'总图',nodes,links:[]}}}});
        }''')
        pg.locator('#f-open').set_input_files({'name': 'content.jingwei.json', 'mimeType': 'application/json', 'buffer': project.encode()})
        pg.wait_for_function("doc.name === '安全回归'")
        pg.wait_for_timeout(300)
        assert pg.evaluate('window.__unsafe === undefined'), 'import executed script'
        assert pg.evaluate("document.querySelector('#world > g[data-id]').getAttribute('data-id') === P().nodes[0].id"), 'id changed during rendering'
        assert pg.evaluate("document.querySelector('#world').textContent.includes(\"O'Reilly <测试>\")"), 'text was lost'
        pg.evaluate('selectNodes([P().nodes[2].id]); render();')
        assert pg.evaluate('window.__unsafe === undefined'), 'properties executed script'
        exported = pg.evaluate('''() => {
          const svg = new DOMParser().parseFromString(exportSVGString(P(),true).str, 'image/svg+xml');
          return {bad:svg.querySelectorAll('script, foreignObject, [onerror], [onload]').length,
            parse:svg.querySelectorAll('parsererror').length, images:svg.querySelectorAll('image').length};
        }''')
        assert exported['bad'] == 0 and exported['parse'] == 0, exported
        assert exported['images'] > 0, 'image disappeared'
        # Quota retry must keep the newest record; complete failure must not destroy
        # the previously persisted shelf, nor hide the warning behind later toasts.
        storage = pg.evaluate('''() => {
          const original=Storage.prototype.setItem;
          const old=[{id:'old',name:'原记录'}];
          original.call(localStorage,SHELF_KEY,JSON.stringify(old));
          try {
            Storage.prototype.setItem=function(k,v){
              if(k===SHELF_KEY && JSON.parse(v).length>1) throw new DOMException('full','QuotaExceededError');
              return original.call(this,k,v);
            };
            const retry=writeShelf([{id:'new'},{id:'old'}]);
            const kept=readShelf();
            Storage.prototype.setItem=function(){throw new DOMException('blocked','SecurityError');};
            const failed=writeShelf([{id:'lost'}]); toast('已打开');
            return {retry,kept,failed,after:readShelf(),warning:!!document.getElementById('shelf-warning')};
          } finally {Storage.prototype.setItem=original;}
        }''')
        assert storage['retry'] and storage['kept'] == [{'id': 'new'}], storage
        assert not storage['failed'] and storage['after'] == storage['kept'] and storage['warning'], storage
        assert pg.evaluate("writeShelf([{id:'recovered'}]) && !document.getElementById('shelf-warning')"), 'warning not cleared after recovery'
        pg.evaluate('loadDoc(buildDemo()); render();')
        assert pg.locator('#world image').count() > 0, 'normal icons disappeared'
        assert not errors, errors
        browser.close()
        print('content_safety_test ok: import, properties, SVG export, quota, recovery')

if __name__ == '__main__':
    main()
