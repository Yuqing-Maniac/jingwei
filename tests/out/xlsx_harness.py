from playwright.sync_api import sync_playwright
import base64, os
JS = r"""
async()=>{
 const mk=(id,text,etype,code,extra={})=>Object.assign({id,type:'rect',text,etype,code,x:0,y:0,w:100,h:40,parent:null,attrs:{desc:'说明 '+text+' & <b>',owner:'某单位'}},extra);
 const d={meta:{project:'某无人体系 & 项目',drawingNo:'HT-001',version:'V1.0',classification:'内部',author:'张三',reviewer:'李四',approver:'王五',date:'2026-10-15',org:'某单位'},pages:{}};
 const nodes=[mk('g','系统组','system','SY-00',{type:'group'}),mk('a','指挥控制系统','system','SY-01',{parent:'g',x:10}),mk('b','数据链子系统','subsystem','SS-02',{parent:'g',x:200,y:5}),mk('c','无人机','resource','RS-01',{x:400}),mk('d','自由节点',undefined,'',{x:600}),mk('t','文字',null,'',{type:'text'})];
 const links=[{id:'l1',from:'a',to:'b',dir:'both',kind:'data',label:'',code:'SI-01',attrs:{content:'航迹 <数据>',protocol:'Link-16',medium:'光纤',freq:'1Hz',latency:'≤50ms',security:'秘密'}},
  {id:'l2',from:'b',to:'c',dir:'one',kind:'radio',label:'遥控指令',code:'SI-02',attrs:{}},{id:'l3',from:'c',to:'d',dir:'none',kind:'plain',label:'',code:'SI-03'}];
 d.pages.root={id:'root',name:'总体视图',nodes,links,view:'SV-1'};
 d.pages.p2={id:'p2',name:'第二页/测试:很长的页面名称超过三十一个字符的页面名称ABCDEFGH',nodes:[mk('x','X','op_node','ON-01'),mk('y','Y','performer','PF-01')],links:[{id:'q',from:'x',to:'y',dir:'one',kind:'ctrl',code:'NL-01',attrs:{content:'资源'}}],view:'OV-2'};
 d.pages.root.nodes.push(Object.assign(mk('s','子页入口','op_node','ON-09'),{sub:'p2'}));
 const b=await StdXlsx.build(d); const buf=new Uint8Array(await b.arrayBuffer()); let s='';for(let i=0;i<buf.length;i+=8192)s+=String.fromCharCode.apply(null,buf.subarray(i,i+8192)); return btoa(s);
}"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file://'+os.path.abspath('xlsx_test.html')); pg.wait_for_timeout(1500)
    open('out/std_test.xlsx','wb').write(base64.b64decode(pg.evaluate(JS))); print('ERR',errs); b.close()
