# v2.5 poster asset capture
import sys
from playwright.sync_api import sync_playwright
import json
A='/home/claude/poster/a4/'
CONTENT='''本项目建设海岛无人值守监视系统，实现岛岸一体、全天候监视与异常目标快速处置。
感知：岸基对海雷达、光电转塔、AIS 接收机；海面水下布设水声浮标、波浪滑翔器和巡逻无人艇。
空中巡查：无人机机巢配垂起固定翼无人机与系留监视无人机。
传输：微波接力为主、卫通备份，岛上光纤环网，数据链终端接入无人平台。
指挥：岸基监视指挥中心、岛上值守站；新增目标融合与视频智能分析，平台由边缘计算节点和海洋态势云支撑。'''
def svg(pg,name,bg=True):
  s=pg.evaluate("bg=>{const r=exportSVGString(P(),bg);return r}",bg)
  open(A+name+'.svg','w').write(s['str']); print(name,round(s['w']),round(s['h']))
def dark(pg):
  pg.evaluate("()=>{doc.theme='command'; document.querySelector('#b-theme').value='command'; render(); fit();}"); pg.wait_for_timeout(500)
def tpl(pg,i):
  pg.evaluate("i=>{const T=TEMPLATES.find(t=>t.id===i); loadDoc(T.build()); doc.theme='command'; render(); fit();}",i); pg.wait_for_timeout(700)
if len(sys.argv)<2:
 with sync_playwright() as p:
  b=p.chromium.launch(args=['--font-render-hinting=none'])
  ctx=b.new_context(viewport={'width':1920,'height':1080},device_scale_factor=2)
  ctx.add_init_script("localStorage.setItem('hongtu.textgen.v1',JSON.stringify({base:'http://127.0.0.1:8766/v1',model:'deepseek-v4-flash'}))")
  pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  dark(pg); svg(pg,'before'); pg.screenshot(path=A+'app_before.png')
  pg.evaluate("()=>openRefGen()"); pg.wait_for_timeout(900)
  pg.fill('#rg-name','海岛无人值守监视系统'); pg.fill('#rg-content',CONTENT)
  pg.click('#rg-gen'); pg.wait_for_timeout(2500)
  pg.screenshot(path=A+'refgen.png')
  pg.click('#rg-apply'); pg.wait_for_timeout(1200)
  pg.evaluate("()=>{render();fit();}"); pg.wait_for_timeout(500)
  print('after doc', pg.evaluate("()=>[doc.name,doc.theme]"))
  svg(pg,'after'); pg.screenshot(path=A+'app_after.png')
  for t in ['it-deploy','std-sv1','std-ov1','it-app','layered','it-sec']:
    tpl(pg,t); svg(pg,t)
  tpl(pg,'it-deploy')
  pg.evaluate("()=>Std.openCheck()"); pg.wait_for_timeout(900); pg.screenshot(path=A+'stdcheck.png'); pg.keyboard.press('Escape')
  # icon catalogue
  cats=pg.evaluate("()=>{const m={};ICON_LIB.forEach(i=>{m[i.cat||i.group||'?']=(m[i.cat||i.group||'?']||0)+1});return m}")
  print(cats)
  keys=['uav_ucav','uav_quad','uav_male','uav_tiltrotor','usv_armed','uuv_xl','robodog_armed','ugv_armed','drone_nest','cuas_radar_4face','cuas_laser_vehicle','cuas_jammer_directional','cuas_interceptor_drone','cuas_c2','satellite','sat_station','command_post','big_screen','ai_agent','destroyer','fighter','cmd_joint','sof_operator','cyber_operator']
  print(errs); b.close()

# icon export (run: python3 shots4.py icons)
import sys
if len(sys.argv)>1 and sys.argv[1]=='icons':
  K=['uav_ucav','uav_quad','uav_tiltrotor','uav_male','swarm','usv_armed','uuv_xl','wave_glider','robodog_armed','ugv_armed','drone_nest','cuas_radar_4face','cuas_laser_vehicle','cuas_jammer_directional','cuas_interceptor_drone','satellite','sat_station','eo_turret','microwave_relay','cmd_hall','big_screen','ai_agent','edge_node','it_k8s','it_gap','it_xc_server','it_waf','cmd_joint','cyber_operator','sof_operator','destroyer','fighter']
  with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
    for k in K: open(A+f'ic_{k}.svg','w').write(pg.evaluate("k=>ICON_LIB.find(i=>i.key===k).svg",k))
    b.close()
