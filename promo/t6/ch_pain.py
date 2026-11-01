import time, sys
sys.path.insert(0, '/home/claude/video/t2')
from ch_origin import tmove, tdrag, MESSY_JS
IDS = ['001', '002', '003', '004', '005', '006']
SH = '/home/claude/video/t6/shots/'

OV_JS = r"""()=>{
 const st=document.createElement('style');
 st.textContent=`
 @font-face{font-family:'SmileySans';src:url('file:///home/claude/tts/fonts/SmileySans-Oblique.ttf');}
 #ov{position:fixed;left:0;top:0;width:1920px;height:1080px;pointer-events:none;z-index:99998;font-family:'SmileySans','Noto Sans CJK SC',sans-serif;overflow:hidden}
 #ov .o{position:absolute;color:#e11d1d;font-weight:900;text-shadow:0 0 0 #fff,0 4px 18px rgba(0,0,0,.35)}
 @keyframes pop{0%{transform:scale(.2) rotate(-14deg);opacity:0}60%{transform:scale(1.18) rotate(-6deg);opacity:1}100%{transform:scale(1) rotate(-8deg);opacity:1}}
 @keyframes slam{0%{transform:scale(3.2) rotate(-22deg);opacity:0}55%{transform:scale(.92) rotate(-9deg);opacity:1}75%{transform:scale(1.06) rotate(-11deg)}100%{transform:scale(1) rotate(-10deg);opacity:1}}
 @keyframes flash{0%,100%{opacity:1}50%{opacity:.25}}
 @keyframes shake{0%,100%{transform:translate(0,0)}25%{transform:translate(-6px,3px)}50%{transform:translate(5px,-4px)}75%{transform:translate(-3px,-5px)}}
 @keyframes strike{from{width:0}to{width:100%}}
 @keyframes xin{0%{transform:scale(0) rotate(-40deg);opacity:0}70%{transform:scale(1.4) rotate(8deg);opacity:1}100%{transform:scale(1) rotate(0);opacity:1}}
 @keyframes slide{from{transform:translateX(200px);opacity:0}to{transform:none;opacity:1}}
 .clock{right:60px;top:96px;font-size:120px;background:rgba(20,0,0,.82);color:#ff3b30!important;padding:6px 34px;border-radius:18px;border:5px solid #ff3b30;font-variant-numeric:tabular-nums;animation:slide .25s ease-out,flash .6s steps(2) .3s infinite}
 .cap{left:60px;bottom:60px;font-size:68px;background:rgba(255,255,255,.92);padding:2px 26px;border-radius:12px;animation:slide .25s ease-out}
 .stamp{border:10px solid #e11d1d;border-radius:22px;padding:6px 40px;background:rgba(255,255,255,.55);letter-spacing:6px}
 .big{left:560px;top:380px;font-size:190px;animation:slam .35s cubic-bezier(.2,.8,.3,1) both}
 .day{right:70px;top:100px;font-size:170px;background:rgba(255,255,255,.93);padding:0 40px;border-radius:20px;border:8px solid #e11d1d;animation:slam .3s both;line-height:1.15}
 .day i{position:absolute;left:0;top:52%;height:14px;background:#e11d1d;width:0;animation:strike .45s .5s forwards}
 .half{right:120px;top:360px;font-size:96px;animation:pop .3s both}
 .x{font-size:96px;animation:xin .3s both;line-height:1}
 #app-dim{}
 .dimmed{transition:filter 1.8s linear,transform 2.6s ease-in;filter:grayscale(1) brightness(.45) contrast(.9)!important;transform:scale(.9);transform-origin:50% 50%}
 `;
 document.head.appendChild(st);
 const ov=document.createElement('div');ov.id='ov';document.body.appendChild(ov);
 window.OV=(cls,html,style)=>{const d=document.createElement('div');d.className='o '+cls;d.innerHTML=html;if(style)d.style.cssText+=style;ov.appendChild(d);return d;};
 window.OVclear=()=>{ov.innerHTML='';if(window._ck)clearInterval(window._ck);};
 window.OVdim=(on)=>{[...document.body.children].forEach(e=>{if(e.id!=='ov'&&e.tagName!=='STYLE'&&e.tagName!=='SCRIPT')e.classList.toggle('dimmed',on);});
   if(!on)[...document.body.children].forEach(e=>{e.style.filter='';e.style.transform='';e.classList.remove('dimmed');});};
}"""

UGLY_JS = r"""()=>{
 const g=['#FF3CAC','#39FF14','#FFEB3B','#00E5FF','#FF6D00','#B388FF'];
 let i=0; P().nodes.forEach(n=>{ if(n.type==='rect'){ n.fill=g[i++%g.length]; n.stroke='#000'; n.size=[10,15,12,17][i%4]; }});
 const by=t=>P().nodes.find(n=>n.text===t);
 const mv=(t,dx,dy,dw,dh)=>{const n=by(t); if(n){n.x+=dx;n.y+=dy;n.w+=dw||0;n.h+=dh||0;}};
 mv('四旋翼巡查无人机',-30,-10,30,0); mv('垂起固定翼',-70,12,-20,-30); mv('高空长航时无人机',-60,-20); mv('机载雷达',-110,30,30,10);
 mv('无人值守传感器',40,-10); mv('巡逻无人车',60,20); mv('光电监控塔',50,-12); mv('充电保障站',-60,-10);
 P().links.forEach(l=>l.route='straight'); render();
}"""

def pt(r, name, w='c'): return r.node_xy(name, w)
def shot(r, n): r.page.screenshot(path=SH + n)

def drag_by(r, name, dx, dy, dur=0.45):
    if time.time() > getattr(r, '_dl', 1e18): return
    x, y = pt(r, name); tmove(r, x, y, 0.22)
    r.page.mouse.down(); tmove(r, x + dx, y + dy, dur); r.page.mouse.up()

def setup(r):
    r.page.evaluate(MESSY_JS); r.page.evaluate(UGLY_JS); r.page.evaluate(OV_JS); r.wait(0.4)
    shot(r, 'pain_setup.png')

def a001(r):
    r._dl = time.time() + 1.6
    r.page.evaluate("""()=>{OV('clock','<span id=ck>23:47</span>');OV('cap','方案明早汇报');
      let m=47,s=0;window._ck=setInterval(()=>{s+=7;if(s>=60){s-=60;m++;} document.getElementById('ck').textContent='23:'+String(m).padStart(2,'0')+(s%2?'':'');},350);}""")
    drag_by(r, '一线管控站', 40, -25, 0.3)
    drag_by(r, '任务规划调度', -35, -18, 0.3)
    #shot(r, 'pain_001.png')

def a002(r):
    r._dl = time.time() + 3.4
    r.page.evaluate("""()=>{OVclear();OV('stamp big','推倒重排');document.getElementById('ov').lastChild.style.animation='slam .35s both, flash .5s steps(2) .4s infinite';}""")
    drag_by(r, '态势融合研判', -120, 60, 0.45)
    drag_by(r, '机载雷达', 90, 40, 0.45)
    r.page.evaluate("""()=>{const q=['uav_fixed','robodog','camera','acoustic'];
      P().nodes.filter(n=>n.type==='equip').slice(0,4).forEach((n,i)=>{n.icon='lib:'+q[(i+2)%4];}); render();
      OV('cap','换图标 = 风格全乱');}""")
    drag_by(r, '四旋翼巡查无人机', 60, -40, 0.4)
    #shot(r, 'pain_002.png')

def a003(r):
    r._dl = time.time() + 1.4
    r.page.evaluate("""()=>{OVclear();OV('day','第 3 天<i></i>');OV('half','一改又是半天',null);}""")
    tmove(r, *pt(r, '态势融合研判'), 0.35)
    drag_by(r, '联合值班席', 80, 30, 0.4)
    tmove(r, *pt(r, '远程操控席'), 0.4)
    #shot(r, 'pain_003.png')

def a004(r):
    xs = [pt(r, t) for t in ['机载雷达', '四足巡逻机器人', '联合值班席', '充电保障站']]
    r.page.evaluate("""()=>{OVclear();const d=OV('stamp big','不符合视图规范 · 返工','left:260px;top:360px;font-size:130px');}""")
    for i, (x, y) in enumerate(xs):
        r.wait(0.35)
        r.page.evaluate("([x,y])=>OV('x','✕',`left:${x-45}px;top:${y-55}px`)", [x, y])
    tmove(r, 960, 700, 0.5)
    r.page.evaluate("()=>{document.body.style.animation='shake .25s 2'}")
    #shot(r, 'pain_004.png')

def a005(r):
    r.page.evaluate("()=>{document.body.style.animation='';OVdim(true);}")
    tmove(r, 960, 560, 1.0)
    r.page.evaluate("()=>{OV('cap','画图，吞掉最宝贵的时间','left:420px;bottom:90px;color:#fff!important;background:rgba(0,0,0,.6);font-size:76px')}")
    r.wait(1.6)
    #shot(r, 'pain_005.png')

def a006(r):
    r.page.evaluate("()=>{OVclear();OVdim(false);document.body.style.animation='';}")
    tmove(r, 960, 540, 0.3)
    #shot(r, 'pain_006.png')

ACTIONS = {'001': a001, '002': a002, '003': a003, '004': a004, '005': a005, '006': a006}
