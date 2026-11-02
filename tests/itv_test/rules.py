"""Negative tests for the 信息系统架构 rules + type inference + Std.fix."""
import os
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = r"""()=>{
 const out={};
 const mk=(view,build)=>{const d={name:'t',theme:'report',statusLabels:{base:'a',new:'b',key:'c'},custom:{},meta:{drawingNo:'X-1'},pages:{root:{id:'root',name:'t',nodes:[],links:[],view}}};
   const p=d.pages.root; const N=o=>{const n=mkNode(o); p.nodes.push(n); return n;}; const L=(a,b,o)=>{const l=Object.assign({id:uid(),from:a.id,to:b.id,dir:'one',kind:'data',route:'ortho',label:''},o||{}); p.links.push(l); return l;};
   build(N,L,p); loadDoc(d); return d;};
 const rules=()=>Std.check(doc).map(i=>i.level+':'+i.rule);
 // DEPLOY: untyped free drawing → inference
 mk('DEPLOY',(N,L)=>{
   const z1=N({type:'band',text:'互联网区（等保二级）',x:0,y:0,w:900,h:160}), z2=N({type:'band',text:'业务专网区',x:0,y:200,w:900,h:200});
   const s1=N({type:'equip',icon:'lib:server',text:'Web服务器',parent:z1.id,x:100,y:30,w:100,h:90});
   const fw=N({type:'equip',icon:'lib:firewall',text:'防火墙',parent:z1.id,x:400,y:30,w:100,h:90});
   const g=N({type:'group',text:'应用服务器',parent:z2.id,x:100,y:230,w:300,h:120});
   const u=N({type:'rect',text:'指挥服务',parent:g.id,x:110,y:270,w:120,h:36});
   const loose=N({type:'rect',text:'游离单元',x:120,y:290,w:100,h:30});           // geometrically inside g, but no parent
   const out=N({type:'equip',icon:'lib:server',text:'区外服务器',x:1000,y:30,w:100,h:90}); // no zone
   L(s1,u,{label:'直连'}); L(fw,g,{label:'经防火墙'});
 });
 out.deploy_types=P().nodes.map(n=>(n.text||'')+'='+(Std.defaultEtype(n,P())||'-')).join(' | ');
 out.deploy_pre=rules();
 out.deploy_fix=Std.fix(doc); out.deploy_post=rules();
 out.deploy_levels=P().nodes.filter(n=>n.etype==='zone').map(n=>n.text+':'+((n.attrs||{}).level||''));
 out.deploy_loose_parent=(()=>{const l=P().nodes.find(n=>n.text==='游离单元'); const par=P().nodes.find(n=>n.id===l.parent); return (par?par.text:null)+' / '+l.etype})();
 // SEC
 mk('SEC',(N,L)=>{
   const d1=N({type:'band',text:'业务域',x:0,y:0,w:900,h:160}), d2=N({type:'band',text:'涉密域',x:0,y:200,w:900,h:160});
   const a=N({type:'equip',icon:'lib:database',text:'业务数据库',parent:d1.id,x:100,y:30,w:100,h:90});
   const b=N({type:'equip',icon:'lib:database',text:'涉密数据库',parent:d2.id,x:100,y:230,w:100,h:90});
   const c=N({type:'equip',icon:'lib:audit_log',text:'安全审计',parent:d1.id,x:400,y:30,w:100,h:90});
   const f=N({type:'equip',icon:'lib:firewall',text:'防火墙',parent:d2.id,x:400,y:230,w:100,h:90});
   const lone=N({type:'equip',icon:'lib:server',text:'游离资产',x:1000,y:30,w:100,h:90});
   L(a,b,{label:'跨域直连'}); L(a,f,{label:'经防火墙'}); L(c,a,{label:'审计'});
 });
 out.sec_types=P().nodes.map(n=>(n.text||'')+'='+(Std.defaultEtype(n,P())||'-')).join(' | ');
 Std.fix(doc); out.sec_post=rules();
 // APP / DATA / BIZ / TECH
 mk('APP',(N,L)=>{ const g=N({type:'group',text:'指挥系统',x:0,y:0,w:300,h:120}); const m=N({type:'rect',text:'模块A',parent:g.id,x:10,y:40,w:100,h:30});
   const g2=N({type:'group',text:'态势系统',x:400,y:0,w:300,h:120}); const lone=N({type:'group',text:'孤立系统',x:800,y:0,w:300,h:120});
   const ex=N({type:'group',text:'外部系统',x:0,y:300,w:400,h:120}); const e1=N({type:'equip',icon:'lib:weather',text:'气象',parent:ex.id,x:20,y:340,w:90,h:70});
   L(m,g2,{label:'态势'}); L(e1,g,{label:'气象',attrs:{content:'气象',protocol:'REST'}}); });
 out.app_types=P().nodes.map(n=>(n.text||'')+'='+(Std.defaultEtype(n,P())||'-')).join(' | ');
 Std.fix(doc); out.app_post=rules();
 mk('DATA',(N,L)=>{ const s=N({type:'band',text:'存储层',x:0,y:0,w:900,h:140}); const dw=N({type:'equip',icon:'lib:database',text:'数据仓库',parent:s.id,x:50,y:20,w:100,h:90});
   const e=N({type:'rect',text:'游离实体',x:0,y:300,w:100,h:36}); const pr=N({type:'rect',text:'数据清洗',x:300,y:300,w:100,h:36}); L(pr,dw); L(e,pr,{label:'目标'}); });
 out.data_types=P().nodes.map(n=>(n.text||'')+'='+(Std.defaultEtype(n,P())||'-')).join(' | ');
 Std.fix(doc); out.data_post=rules();
 mk('BIZ',(N,L)=>{ const b=N({type:'band',text:'筹划域',x:0,y:0,w:900,h:140}); const g=N({type:'group',text:'计划编制',parent:b.id,x:50,y:10,w:300,h:100});
   N({type:'rect',text:'航线规划',parent:g.id,x:60,y:50,w:100,h:30}); N({type:'rect',text:'游离流程',x:0,y:300,w:100,h:36}); N({type:'round',icon:'lib:operator',text:'规划员',parent:b.id,x:500,y:30,w:120,h:36}); N({type:'document',text:'方案',parent:b.id,x:700,y:30,w:100,h:40}); });
 out.biz_types=P().nodes.map(n=>(n.text||'')+'='+(Std.defaultEtype(n,P())||'-')).join(' | ');
 Std.fix(doc); out.biz_post=rules();
 mk('TECH',(N,L)=>{ const b=N({type:'band',text:'平台层',x:0,y:0,w:900,h:140}); const g=N({type:'group',text:'容器云',parent:b.id,x:50,y:10,w:300,h:100});
   N({type:'rect',text:'编排',parent:g.id,x:60,y:50,w:100,h:30}); N({type:'equip',icon:'lib:server',text:'服务器',parent:b.id,x:500,y:20,w:90,h:80}); N({type:'rect',text:'游离组件',x:0,y:300,w:100,h:36}); });
 out.tech_types=P().nodes.map(n=>(n.text||'')+'='+(Std.defaultEtype(n,P())||'-')).join(' | ');
 Std.fix(doc); out.tech_post=rules();
 // DoDAF regression: SV-1 template still clean
 loadDoc(TEMPLATES.find(t=>t.id==='std-sv1').build()); out.sv1=rules();
 out.tb=Std.tblockCells(P().nodes.find(n=>n.type==='tblock'),P()).find(c=>/系统接口/.test(c.text)).text;
 return out;}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 1000})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(H, 'offline.html')); pg.wait_for_timeout(1200)
    r = pg.evaluate(JS)
    for k, v in r.items(): print(k, ':', v)
    print('errs', errs); b.close()
