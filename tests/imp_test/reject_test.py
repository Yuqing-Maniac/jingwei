"""检查 .ppt/.vsd 拒绝信息与 keepColors:false。"""
import os, base64
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(); pg.goto('file://' + ROOT + '/offline.html'); pg.wait_for_timeout(1000)
    pg.add_script_tag(path=ROOT + '/importers.js')
    print(pg.evaluate("async()=>{try{await Importer.fromFile(new File([new Uint8Array(4)],'x.vsd'))}catch(e){return e.message}}"))
    print(pg.evaluate("""async b64=>{const bin=atob(b64),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
      const r=await Importer.fromPPTX(u.buffer,{keepColors:false,rootId:'root'});return [r.pages[0].id, r.pages[0].nodes.filter(n=>n.fill||n.stroke||n.status!=='base').length]}""",
      base64.b64encode(open(H + '/fx/a_layered.pptx', 'rb').read()).decode()))
    b.close()
