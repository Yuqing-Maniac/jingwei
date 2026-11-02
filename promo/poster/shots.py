from playwright.sync_api import sync_playwright
import os,base64
A='/home/claude/poster/assets/'
md=open('/home/claude/video/md1.txt',encoding='utf-8').read()
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=2,accept_downloads=True)
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  pg.select_option('#b-theme','command'); pg.dispatch_event('#b-theme','change'); pg.wait_for_timeout(400)
  pg.evaluate("()=>{const T=window.TEMPLATES.find(t=>t.id==='cuas'); loadDoc(T.build()); doc.theme='command'; render(); fit();}"); pg.wait_for_timeout(800)
  pg.screenshot(path=A+'app_cuas_dark.png')
  # transparent diagram export via svg
  svg=pg.evaluate("()=>exportSVGString(P(),true).str"); open(A+'diag_cuas_dark.svg','w').write(svg)
  pg.evaluate("()=>{const T=window.TEMPLATES.find(t=>t.id==='equipnet'); loadDoc(T.build()); doc.theme='command'; render(); fit();}"); pg.wait_for_timeout(800)
  svg=pg.evaluate("()=>exportSVGString(P(),true).str"); open(A+'diag_equipnet_dark.svg','w').write(svg)
  pg.select_option('#b-theme','report'); pg.dispatch_event('#b-theme','change')
  pg.evaluate("()=>{loadDoc(buildDemo()); render(); fit();}"); pg.wait_for_timeout(600)
  pg.keyboard.press('Control+Shift+G'); pg.wait_for_timeout(400); pg.fill('#tg-in',md); pg.wait_for_timeout(1200)
  pg.screenshot(path=A+'textgen.png'); pg.keyboard.press('Escape')
  pg.keyboard.press('Control+Shift+M'); pg.wait_for_timeout(2500); pg.screenshot(path=A+'templates.png'); pg.keyboard.press('Escape')
  keys=['uav_ucav','uav_quad','uav_male','uav_tiltrotor','usv_armed','uuv_xl','robodog_armed','ugv_armed','drone_nest','cuas_radar_4face','cuas_laser_vehicle','cuas_jammer_directional','cuas_interceptor_drone','cuas_c2','satellite','sat_station','command_post','big_screen','ai_agent','destroyer','fighter','cmd_joint','sof_operator','cyber_operator']
  for k in keys:
    svg=pg.evaluate("k=>ICON_LIB.find(i=>i.key===k).svg",k)
    open(A+f'ic_{k}.svg','w').write(svg)
  b.close()
