from playwright.sync_api import sync_playwright
import os
html='''<html><body style="margin:0;font:12px 'Noto Sans CJK SC';background:#fff"><div id=r></div><script>%s</script><script>
const cats=['无人','反无人'];const over={uav_fixed:'无人',uav_male:'无人',uav_quad:'无人',uav_vtol:'无人',loitering:'无人',usv:'无人',uuv:'无人',ugv:'无人',robodog:'无人',uav_heli:'无人',hale_uav:'无人',swarm:'无人',target_drone:'无人',glider:'无人',ugv_tracked:'无人',eod_robot:'无人',usv_mother:'无人',cuas:'反无人',laser_weapon:'反无人',hpm:'反无人',jammer:'反无人',rf_detector:'反无人'};
let h='';for(const c of cats){const L=ICON_LIB.filter(i=>(over[i.key]||i.cat)===c);h+=`<h3 style="margin:8px">${c}（${L.length}）</h3><div style="display:flex;flex-wrap:wrap">`+L.map(i=>`<div style="width:96px;text-align:center;margin:2px"><img width=72 src="data:image/svg+xml;charset=utf-8,${encodeURIComponent(i.svg)}"><br>${i.name}</div>`).join('')+'</div>'}
document.getElementById('r').innerHTML=h;</script></body></html>'''
js=open('icons.js',encoding='utf-8').read()+'\n'+'\n'.join(open(f,encoding='utf-8').read() for f in sorted(x for x in os.listdir('.') if x.startswith('icons_') and x.endswith('.js')))
open('out/sheet_all.html','w',encoding='utf-8').write(html%js)
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':800}); pg.goto('file://'+os.path.abspath('out/sheet_all.html')); pg.wait_for_timeout(800); pg.screenshot(path='out/sheet_unmanned.png',full_page=True); b.close()
