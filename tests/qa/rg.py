from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:300])); pg.on('console',lambda m: errs.append('console:'+m.text[:200]) if m.type=='error' else None)
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  pg.keyboard.press('Control+Shift+L'); pg.wait_for_timeout(600)
  print('src opts', pg.evaluate("()=>[...document.querySelectorAll('#rg-src option')].map(o=>o.textContent).slice(0,8)"))
  pg.check('input[name=rg-eng][value=rule]'); 
  pg.fill('#rg-name','海岛无人值守监视系统')
  pg.fill('#rg-content','本项目建设海岛无人值守监视系统，分感知、传输、处理、应用四部分。感知部分包括岸基雷达、光电转台、系留无人机。传输部分包括微波接力、卫通备份。处理部分包括目标融合、视频分析。应用部分包括值班席、移动告警终端。')
  pg.wait_for_timeout(500)
  btn=pg.evaluate("()=>[...document.querySelectorAll('#rg button, .rg button')].filter(b=>b.offsetParent).map(b=>b.id+':'+b.textContent.trim())")
  print(btn)
  gb=[x.split(':')[0] for x in btn if '生成' in x and x.split(':')[0]]
  pg.click('#rg-gen'); pg.wait_for_timeout(2000); print('msg',pg.evaluate("()=>document.querySelector('#rg-msg').textContent")); pg.click('#rg-apply'); pg.wait_for_timeout(1500)
  print(pg.evaluate("()=>[P().nodes.length,P().links.length,(P().nodes.find(n=>n.role==='title')||{}).text]"))
  pg.screenshot(path='/tmp/claude-0/bh/rg.png')
  print(errs); b.close()
