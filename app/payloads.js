/* Platform-attached drawing payloads. All editable values live in node.payloads.
 * Directions are clockwise degrees from WORLD north; only mounts follow n.rot.
 * Distances are diagram coordinates, never certified equipment performance. */
var payloadTypeDefs = {
  eo: {name:'光电', mode:'passive', color:'#cf8b24'},
  radar: {name:'雷达', mode:'active', color:'#347fd4'},
  sigint: {name:'电子侦察', mode:'passive', color:'#a168ce'},
  magnetic: {name:'磁探', mode:'passive', color:'#279d96'},
  activeSonar: {name:'主动声呐', mode:'active', color:'#259bb9'},
  passiveSonar: {name:'被动声呐', mode:'passive', color:'#697bd0'},
  emDecoy: {name:'电磁诱饵', mode:'emitter', color:'#ce58b7'},
  weapon: {name:'打击范围', mode:'weapon', color:'#bf6c4e'},
  effect: {name:'作用范围', mode:'effect', color:'#bc7351'},
  mainGun: {name:'主炮', mode:'weapon', color:'#c86656'},
  secondaryGun: {name:'副炮', mode:'weapon', color:'#b78542'},
  hpm: {name:'高功率微波', mode:'effect', color:'#af65d5'},
  laser: {name:'激光', mode:'effect', color:'#d75c78'},
  loiteringMunition: {name:'巡飞弹', mode:'weapon', color:'#b57b37'},
  custom: {name:'自定义范围', mode:'effect', color:'#648e9a'}
};
var payloadDashDefs = {solid:'',dashed:'6 4',longDash:'12 5',dot:'2 4',dashDot:'10 4 2 4',doubleDash:'5 3 5 8'};
var payloadSerial = 0;
var payloadDialogNodeId = null;
var payloadDialogSelection = null;

function payloadNumber(value, fallback) {
  var n = Number(value);
  return value !== null && value !== '' && isFinite(n) ? n : fallback;
}
function payloadNorm(value) { return ((value % 360) + 360) % 360; }
function payloadKind(value) { return value === 'mag' ? 'magnetic' : payloadTypeDefs[value] ? value : 'custom'; }
function payloadMode(p) {
  var kind=payloadKind(p && (p.kind||p.type));
  return kind==='custom' && p && ['active','passive','effect'].indexOf(p.mode)>=0 ? p.mode : payloadTypeDefs[kind].mode;
}
function payloadId() {
  payloadSerial += 1;
  return 'payload-' + Date.now().toString(36) + '-' + payloadSerial.toString(36);
}
function payloadClean(value) {
  var p = value && typeof value === 'object' ? Object.assign({}, value) : {};
  p.id = String(p.id || payloadId());
  p.kind = payloadKind(p.kind || p.type);
  p.type = p.kind;
  var def = payloadTypeDefs[p.kind];
  if(p.kind==='custom')p.mode=payloadMode(p);else delete p.mode;
  var mode=payloadMode(p);
  p.name = String(p.name || def.name).slice(0, 100);
  p.enabled = typeof p.enabled === 'boolean' ? p.enabled : typeof p.on === 'boolean' ? p.on : false;
  p.direction = payloadNorm(payloadNumber(p.direction, 0));
  p.sweep = payloadNumber(p.sweep, 90);
  if (p.sweep <= 0 || p.sweep > 360) p.sweep = p.sweep > 360 ? 360 : 90;
  p.range = payloadNumber(p.range, payloadNumber(p.distance, 160));
  if (!(p.range > 0)) p.range = 160;
  p.color = /^#[0-9a-f]{6}$/i.test(p.color || '') ? p.color : def.color;
  if (!payloadDashDefs.hasOwnProperty(p.lineStyle)) p.lineStyle = mode === 'passive' ? 'dashed' : 'solid';
  if (mode === 'passive' && p.lineStyle === 'solid') p.lineStyle = 'dashed';
  if (mode === 'active' || mode === 'emitter') p.lineStyle = 'solid';
  var mx = payloadNumber(p.mount && p.mount.x, 0), my = payloadNumber(p.mount && p.mount.y, 0);
  // Legacy preview mounts were pixels. Do not silently reinterpret those values.
  p.mount = {x: Math.abs(mx) <= 0.5 ? mx : 0, y: Math.abs(my) <= 0.5 ? my : 0};
  p.showRange = p.showRange !== false;
  p.showOverlay = p.showOverlay !== false;
  if (p.kind === 'emDecoy') {
    p.simulatedTarget = 'surfaceShip';
    p.overlayScale = Math.max(.1,Math.min(20,payloadNumber(p.overlayScale,payloadNumber(p.ghostScale,1))));
    p.overlayName = String(p.overlayName || p.simulatedName || '水面舰艇').slice(0,60);
    delete p.ghostScale;
  }
  if (p.presetId || p.presetKey) {
    p.presetId = String(p.presetId || p.presetKey);
    p.presetKey = p.presetId;
  }
  delete p.on; delete p.distance;
  return p;
}
function payloadNormalizeNode(n) {
  if (!n || !Array.isArray(n.payloads)) return n;
  var ids = {};
  n.payloads = n.payloads.filter(function(p) { return p && typeof p === 'object'; }).map(function(p) {
    var clean = payloadClean(p);
    if (ids[clean.id]) clean.id = payloadId();
    ids[clean.id] = true;
    return clean;
  });
  return n;
}
function payloadNodeById(id) {
  if (typeof nodeById === 'function') {
    var current = nodeById(id);
    if (current) return current;
  }
  if (typeof doc !== 'undefined' && doc.pages) {
    var names = Object.keys(doc.pages);
    for (var i = 0; i < names.length; i++) {
      var nodes = doc.pages[names[i]].nodes || [];
      for (var j = 0; j < nodes.length; j++) if (nodes[j].id === id) return nodes[j];
    }
  }
  return null;
}
function payloadMount(n, value) {
  var m = value && value.mount || {x:0,y:0};
  var mx = payloadNumber(m.x, 0), my = payloadNumber(m.y, 0);
  if (Math.abs(mx) > 0.5) mx = 0;
  if (Math.abs(my) > 0.5) my = 0;
  var w = payloadNumber(n.w, 96), h = payloadNumber(n.h, 96);
  var t = payloadNumber(n.rot, 0) * Math.PI / 180;
  var dx = mx * w, dy = my * h;
  return {x:payloadNumber(n.x,0)+w/2+dx*Math.cos(t)-dy*Math.sin(t),
    y:payloadNumber(n.y,0)+h/2+dx*Math.sin(t)+dy*Math.cos(t)};
}
function payloadPoint(m, radius, direction) {
  var a = direction * Math.PI / 180;
  return {x:m.x+radius*Math.sin(a), y:m.y-radius*Math.cos(a)};
}
function payloadGeometry(n, value) {
  var p = payloadClean(value), m = payloadMount(n,p), a = p.direction-p.sweep/2;
  var start = payloadPoint(m,p.range,a), end = payloadPoint(m,p.range,a+p.sweep);
  var label = payloadPoint(m,p.range,p.sweep >= 360 ? 15 : p.direction);
  label.y -= 10;
  return {x:m.x,y:m.y,mount:m,radius:p.range,range:p.range,direction:p.direction,sweep:p.sweep,
    start:start,end:end,label:label,mode:payloadMode(p),payload:p};
}
function payloadBox(points, padding) {
  if (!points.length) return null;
  var x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
  points.forEach(function(p) {x0=Math.min(x0,p.x);y0=Math.min(y0,p.y);x1=Math.max(x1,p.x);y1=Math.max(y1,p.y);});
  return {x:x0-padding,y:y0-padding,w:x1-x0+padding*2,h:y1-y0+padding*2};
}
function payloadUnion(a,b) {
  if (!a) return b;
  if (!b) return a;
  var x=Math.min(a.x,b.x), y=Math.min(a.y,b.y);
  return {x:x,y:y,w:Math.max(a.x+a.w,b.x+b.w)-x,h:Math.max(a.y+a.h,b.y+b.h)-y};
}
function payloadGhost(n,p) {
  var scale=Math.max(.1,Math.min(20,payloadNumber(p.overlayScale,1)));
  var w=Math.max(40,payloadNumber(n.w,96)*2.15)*scale,h=Math.max(32,payloadNumber(n.h,96)*1.55)*scale;
  var name=String(p.overlayName || '水面舰艇').replace(/^模拟\s*/,'') || '水面舰艇';
  return {x:payloadNumber(n.x,0)+payloadNumber(n.w,96)/2,y:payloadNumber(n.y,0)+payloadNumber(n.h,96)/2,
    w:w,h:h,rot:payloadNumber(n.rot,0),scale:scale,label:'模拟'+name+' · 非真实目标'};
}
function payloadGhostBounds(n,p) {
  var g=payloadGhost(n,p), t=g.rot*Math.PI/180, points=[],halfLabel=Math.max(112,g.label.length*6+8);
  // The transformed SVG group bounds include its complete local union box.
  // Rotate that box as a whole, so nested image/text getBBox agrees with export.
  var halfWidth=Math.max(g.w/2,halfLabel),top=-g.h/2-23,bottom=g.h/2;
  [[-halfWidth,top],[halfWidth,top],[halfWidth,bottom],[-halfWidth,bottom]].forEach(function(q) {
    points.push({x:g.x+q[0]*Math.cos(t)-q[1]*Math.sin(t),y:g.y+q[0]*Math.sin(t)+q[1]*Math.cos(t)});
  });
  return payloadBox(points,4);
}
function payloadOneBounds(n,value) {
  var p=payloadClean(value);
  if (!p.enabled) return null;
  var box=null;
  if (p.showRange) {
    var g=payloadGeometry(n,p), points=[g.mount,g.start,g.end];
    for(var a=0;a<360;a+=90) if(p.sweep>=360 || payloadNorm(a-(p.direction-p.sweep/2))<=p.sweep+1e-9) points.push(payloadPoint(g.mount,p.range,a));
    if(g.mode==='active'||g.mode==='emitter'||g.mode==='passive') {
      payloadArrowAngles(p).forEach(function(angle) {
        var arrow=payloadArrowGeometry(g,p,angle,g.mode!=='passive');
        points.push(arrow.from,arrow.tip,arrow.left,arrow.right);
      });
    }
    box=payloadBox(points,5);
    var width=Math.max(30,p.name.length*12+16);
    box=payloadUnion(box,{x:g.label.x-width/2,y:g.label.y-13,w:width,h:20});
  }
  if(p.kind==='emDecoy' && p.showOverlay) box=payloadUnion(box,payloadGhostBounds(n,p));
  return box;
}
function payloadBounds(page) {
  var box=null;
  (page && page.nodes || []).forEach(function(n) {
    if(!Array.isArray(n.payloads) || n.hidden) return;
    n.payloads.forEach(function(p) {box=payloadUnion(box,payloadOneBounds(n,p));});
  });
  return box;
}
function payloadFmt(n) { return String(Math.round(n*1000000)/1000000); }
function payloadAttrs(attrs) {
  return Object.keys(attrs).map(function(k) { return ' '+k+'="'+esc(String(attrs[k]))+'"'; }).join('');
}
function payloadTag(name,attrs,body) { return '<'+name+payloadAttrs(attrs)+(body==null?'/>':'>'+body+'</'+name+'>'); }
function payloadArrowAngles(p) {
  return p.sweep>=360?[p.direction,p.direction+120,p.direction+240]:[p.direction-p.sweep*.28,p.direction,p.direction+p.sweep*.28];
}
function payloadArrowGeometry(g,p,angle,out) {
  var r=p.range, u={x:Math.sin(angle*Math.PI/180),y:-Math.cos(angle*Math.PI/180)};
  var length=Math.min(r*.2,Math.max(12,r*.045)),head=Math.min(length*.35,Math.max(3,r*.009));
  var near=Math.max(0,r*.9-length),far=r*.9;
  var from=out?near:far,to=out?far:near,sign=out?1:-1;
  var x1=g.x+u.x*from,y1=g.y+u.y*from,x2=g.x+u.x*to,y2=g.y+u.y*to;
  var vx=u.x*sign,vy=u.y*sign;
  return {from:{x:x1,y:y1},tip:{x:x2,y:y2},left:{x:x2-vx*head-vy*head*.6,y:y2-vy*head+vx*head*.6},right:{x:x2-vx*head+vy*head*.6,y:y2-vy*head-vx*head*.6}};
}
function payloadArrow(g,p,angle,out) {
  var arrow=payloadArrowGeometry(g,p,angle,out);
  var x1=arrow.from.x,y1=arrow.from.y,x2=arrow.tip.x,y2=arrow.tip.y;
  var d='M '+payloadFmt(x1)+' '+payloadFmt(y1)+' L '+payloadFmt(x2)+' '+payloadFmt(y2)+
    ' M '+payloadFmt(arrow.left.x)+' '+payloadFmt(arrow.left.y)+
    ' L '+payloadFmt(x2)+' '+payloadFmt(y2)+' L '+payloadFmt(arrow.right.x)+' '+payloadFmt(arrow.right.y);
  return payloadTag('path',{'data-flow-arrow':p.id,'data-flow':out?'out':'in','data-sensor-mode':g.mode,
    'data-x1':x1,'data-y1':y1,'data-x2':x2,'data-y2':y2,'data-origin-world-x':g.x,'data-origin-world-y':g.y,
    d:d,stroke:p.color,'stroke-width':1.4,'vector-effect':'non-scaling-stroke',fill:'none'});
}
function payloadGhostMarkup(n,p) {
  var g=payloadGhost(n,p),uri='';
  try {if(typeof iconURI==='function') uri=iconURI('lib:destroyer','neutral',n.appearance);} catch(_) {}
  var body='';
  if(uri) body+=payloadTag('image',{href:uri,'xlink:href':uri,x:-g.w/2,y:-g.h/2,width:g.w,height:g.h,opacity:.25,'preserveAspectRatio':'xMidYMid meet'});
  else body+=payloadTag('path',{d:'M '+(-g.w*.46)+' 0 L '+(-g.w*.22)+' '+(-g.h*.28)+' L '+(g.w*.38)+' '+(-g.h*.28)+' L '+(g.w*.48)+' 0 L '+(g.w*.38)+' '+(g.h*.28)+' L '+(-g.w*.22)+' '+(g.h*.28)+' Z',fill:p.color,opacity:.18});
  body+=payloadTag('rect',{x:-g.w/2,y:-g.h/2,width:g.w,height:g.h,rx:3,fill:'none',stroke:p.color,'stroke-width':1.2,'stroke-dasharray':'6 5','vector-effect':'non-scaling-stroke'});
  body+=payloadTag('text',{x:0,y:-g.h/2-10,'text-anchor':'middle','font-size':11,'font-family':'sans-serif',fill:p.color,'paint-order':'stroke',stroke:'#ffffff','stroke-opacity':.85,'stroke-width':3,'stroke-linejoin':'round'},esc(g.label));
  return payloadTag('g',{'data-simulated-target':'surfaceShip','data-simulation':'true','data-overlay-payload':p.id,
    'data-overlay-scale':g.scale,
    transform:'translate('+payloadFmt(g.x)+' '+payloadFmt(g.y)+') rotate('+payloadFmt(g.rot)+')'},body);
}
function payloadMarkup(page,opts) {
  var result='';
  (page && page.nodes || []).forEach(function(n) {
    if(!Array.isArray(n.payloads) || n.hidden) return;
    n.payloads.forEach(function(value) {
      var p=payloadClean(value);
      if(!p.enabled || !p.showRange && !(p.kind==='emDecoy' && p.showOverlay)) return;
      var g=payloadGeometry(n,p),body='';
      if(p.kind==='emDecoy' && p.showOverlay) body+=payloadGhostMarkup(n,p);
      if(p.showRange) {
        var attrs={'data-fov':p.id,'data-distance':p.range,'data-sensor-mode':g.mode,fill:p.color,'fill-opacity':.075,stroke:p.color,
          'stroke-width':1.35,'stroke-dasharray':payloadDashDefs[p.lineStyle]||'none','vector-effect':'non-scaling-stroke','stroke-linejoin':'round'};
        if(p.sweep>=360) {attrs.cx=g.x;attrs.cy=g.y;attrs.r=p.range;body+=payloadTag('circle',attrs);}
        else {attrs.d='M '+payloadFmt(g.x)+' '+payloadFmt(g.y)+' L '+payloadFmt(g.start.x)+' '+payloadFmt(g.start.y)+' A '+payloadFmt(p.range)+' '+payloadFmt(p.range)+' 0 '+(p.sweep>180?1:0)+' 1 '+payloadFmt(g.end.x)+' '+payloadFmt(g.end.y)+' Z';body+=payloadTag('path',attrs);}
        if(g.mode==='active'||g.mode==='emitter'||g.mode==='passive') {
          payloadArrowAngles(p).forEach(function(a) {body+=payloadArrow(g,p,a,g.mode!=='passive');});
        }
        body+=payloadTag('circle',{'data-mount':p.id,cx:g.x,cy:g.y,r:2.2,fill:p.color,stroke:'#ffffff','stroke-width':1,'vector-effect':'non-scaling-stroke'});
        body+=payloadTag('text',{'data-payload-label':p.id,x:g.label.x,y:g.label.y,'text-anchor':'middle','font-size':11,'font-family':'sans-serif',fill:p.color,
          'paint-order':'stroke',stroke:'#ffffff','stroke-opacity':.82,'stroke-width':3,'stroke-linejoin':'round'},esc(p.name));
      }
      result+=payloadTag('g',{'data-payload-id':p.id,'data-platform-id':n.id,'data-payload-kind':p.kind,
        'data-world-direction':p.direction,'data-origin-world-x':g.x,'data-origin-world-y':g.y,'data-range':p.range,
        'data-sensor-mode':g.mode,'pointer-events':'none'},body);
    });
  });
  return result ? payloadTag('g',{'data-payload-effects':'true'},result) : '';
}
function payloadSVG(page,opts) {
  var box=payloadBounds(page);
  if(!box) return null;
  var str='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="'+[box.x,box.y,box.w,box.h].map(payloadFmt).join(' ')+'" width="'+payloadFmt(box.w)+'" height="'+payloadFmt(box.h)+'">'+payloadMarkup(page,opts)+'</svg>';
  return {str:str,x:box.x,y:box.y,w:box.w,h:box.h,box:box};
}
function payloadPresetList(n) {
  return window.PayloadPresets && typeof PayloadPresets.forNode==='function' ? PayloadPresets.forNode(n) : [];
}
function payloadPropsHTML(n) {
  if(!n || !n.icon && !Array.isArray(n.payloads)) return '';
  var list=Array.isArray(n.payloads)?n.payloads:[],on=list.filter(function(p) {return p.enabled;}).length;
  return '<hr><div class="row"><label>载荷与范围</label><button id="p-payloads" type="button">配置'+(list.length?' · '+on+'/'+list.length:'')+'</button></div><div class="hint">随平台移动挂载，方向独立于平台朝向。距离仅为图面示意。</div>';
}
function payloadDialogNode() {return payloadDialogNodeId ? payloadNodeById(payloadDialogNodeId) : null;}
function payloadDialogActive(n) {
  var rows=n && Array.isArray(n.payloads)?n.payloads:[];
  for(var i=0;i<rows.length;i++) if(rows[i].id===payloadDialogSelection) return rows[i];
  return rows[0]||null;
}
function payloadModeLabel(p) {
  var mode=payloadMode(p);
  return mode==='passive'?'被动接收 · 虚线 / 向内箭头':mode==='active'?'主动探测 · 实线 / 向外箭头':mode==='emitter'?'主动发射 · 实线 / 向外箭头':'作用 / 打击示意 · 不标分类箭头';
}
function payloadMountUI() {
  if(document.getElementById('payloads-dialog')) return;
  var css=document.createElement('style');css.id='payloads-style';
  css.textContent='#payloads-dialog{position:fixed;left:0;top:0;right:0;bottom:0;z-index:1200;background:rgba(10,20,35,.35);display:none;align-items:center;justify-content:center;padding:16px;color:var(--fg);font-size:13px}#payloads-dialog *{box-sizing:border-box}#payloads-dialog .pl-box{background:var(--panel,var(--bg,#fff));border:1px solid var(--line);border-radius:10px;box-shadow:0 15px 55px rgba(0,0,0,.2);width:920px;max-width:100%;max-height:92vh;display:flex;flex-direction:column;overflow:hidden}#payloads-dialog .pl-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--line);gap:10px}#payloads-dialog .pl-head h3{font-size:16px;margin:0}#payloads-dialog .pl-body{overflow:auto;padding:14px 16px}#payloads-dialog .pl-info{font-size:12px;color:var(--muted);margin:5px 0 12px;line-height:1.6}#payloads-dialog .pl-grid{display:grid;grid-template-columns:250px minmax(0,1fr);gap:16px}#payloads-dialog .pl-presets{display:flex;gap:6px 14px;flex-wrap:wrap;padding:9px;border:1px solid var(--line);border-radius:6px;margin-bottom:12px}#payloads-dialog label{display:flex;align-items:center;gap:7px}#payloads-dialog input,#payloads-dialog select,#payloads-dialog button{font:inherit;color:var(--fg)}#payloads-dialog button,#payloads-dialog select,#payloads-dialog input:not([type=checkbox]){border:1px solid var(--line);border-radius:5px;background:var(--bg,#fff);padding:6px 8px;min-width:0}#payloads-dialog button{cursor:pointer}#payloads-dialog .pl-list{display:flex;flex-direction:column;gap:5px;max-height:390px;overflow:auto}#payloads-dialog .pl-item{display:flex;align-items:center;gap:4px;border:1px solid var(--line);border-radius:6px;padding:4px}#payloads-dialog .pl-item button{border:0;background:transparent;text-align:left;flex:1;min-width:0;overflow-wrap:anywhere}#payloads-dialog .pl-item[aria-current=true]{border-color:#357ed4;box-shadow:0 0 0 1px #357ed4}#payloads-dialog .pl-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}#payloads-dialog .pl-field{display:flex;flex-direction:column;gap:5px}#payloads-dialog .pl-field>label{font-size:12px;color:var(--muted)}#payloads-dialog .pl-field input,#payloads-dialog .pl-field select{width:100%}#payloads-dialog .pl-field input[type=color]{padding:3px;height:33px}#payloads-dialog .pl-wide{grid-column:1/-1}#payloads-dialog .pl-actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:11px}#payloads-dialog .pl-foot{padding:10px 16px;border-top:1px solid var(--line);display:flex;gap:8px;flex-wrap:wrap;align-items:center;justify-content:space-between}#payloads-dialog input:disabled,#payloads-dialog select:disabled{opacity:.6}#payloads-dialog .pl-empty{color:var(--muted);padding:15px 5px;line-height:1.7}@media(max-width:640px){#payloads-dialog{padding:6px}#payloads-dialog .pl-grid{grid-template-columns:1fr}#payloads-dialog .pl-list{max-height:170px}#payloads-dialog .pl-form{gap:8px}#payloads-dialog .pl-box{max-height:96vh}}';
  css.textContent+='#payloads-dialog .pl-field input[type=checkbox]{width:auto;flex:0 0 auto}#payloads-dialog .pl-field>label{flex-wrap:nowrap}';
  document.head.appendChild(css);
  var host=document.createElement('div');host.id='payloads-dialog';host.setAttribute('role','dialog');host.setAttribute('aria-modal','true');host.setAttribute('aria-labelledby','payload-title');
  setMarkup(host,'<div class="pl-box"><div class="pl-head"><h3 id="payload-title">载荷与范围</h3><button id="payload-close" type="button" aria-label="关闭载荷与范围">关闭</button></div><div class="pl-body"><div id="payload-platform-name"></div><p class="pl-info">方向以世界北向 0°、顺时针计；挂点随平台平移和旋转，范围方向保持独立。距离采用当前图面坐标单位，可输入任意正数；不代表真实射程或物理仿真。</p><strong>常用绘图预设，可调整</strong><div id="payload-presets" class="pl-presets"></div><div class="pl-grid"><section><div class="pl-actions" style="margin-top:0;margin-bottom:8px"><button id="payload-all-on" type="button">全部开启</button><button id="payload-all-off" type="button">全部关闭</button></div><div id="payload-list" class="pl-list"></div><div class="pl-actions"><button id="payload-add" type="button">＋ 自定义载荷</button><button id="payload-delete" type="button">删除当前载荷</button></div></section><section><div id="payload-empty" class="pl-empty">勾选一个预设或添加自定义载荷。关闭预设只隐藏效果，已调参数与自定义载荷均保留。</div><div id="payload-form" class="pl-form"></div></section></div></div><div class="pl-foot"><span id="payload-mode" class="pl-info" style="margin:0"></span><div class="pl-actions" style="margin:0"><button id="payload-view-platform" type="button">查看平台</button><button id="payload-fit" type="button">适配范围</button></div></div></div>');
  document.body.appendChild(host);
  host.addEventListener('click',payloadDialogClick);
  host.addEventListener('change',payloadDialogChange);
  host.addEventListener('keydown',function(e) {if(e.key==='Escape'){e.stopPropagation();payloadClose();}});
}
function payloadRefreshDialog() {
  var host=document.getElementById('payloads-dialog'),n=payloadDialogNode();
  if(!host || host.style.display==='none') return;
  if(!n) {payloadClose();return;}
  var rows=Array.isArray(n.payloads)?n.payloads:[],active=payloadDialogActive(n),presets=payloadPresetList(n);
  payloadDialogSelection=active?active.id:null;
  document.getElementById('payload-platform-name').textContent='当前平台：'+(n.text || n.icon || '平台');
  var ph='';
  presets.forEach(function(def) {
    var key=def.presetId||def.presetKey||def.id,p=rows.filter(function(q) {return (q.presetId||q.presetKey)===key;})[0];
    ph+='<label><input type="checkbox" data-payload-preset="'+esc(key)+'"'+(p&&p.enabled?' checked':'')+'>'+esc(def.name)+'</label>';
  });
  setMarkup(document.getElementById('payload-presets'),ph||'<span class="pl-info">暂无平台预设，可添加自定义载荷。</span>');
  var list='';
  rows.forEach(function(p) {
    var kind=payloadKind(p.kind||p.type);
    list+='<div class="pl-item" aria-current="'+(p.id===payloadDialogSelection?'true':'false')+'"><input type="checkbox" aria-label="开启'+esc(p.name)+'" data-payload-enabled="'+esc(p.id)+'"'+(p.enabled?' checked':'')+'><button type="button" data-payload-select="'+esc(p.id)+'">'+esc(p.name)+'<small style="display:block;color:var(--muted)">'+esc(payloadTypeDefs[kind].name)+(p.presetId||p.presetKey?' · 预设':' · 自定义')+'</small></button></div>';
  });
  setMarkup(document.getElementById('payload-list'),list||'<div class="pl-empty">尚未配置载荷</div>');
  var form=document.getElementById('payload-form');
  form.style.display=active?'grid':'none';document.getElementById('payload-empty').style.display=active?'none':'block';
  document.getElementById('payload-delete').disabled=!active;
  document.getElementById('payload-mode').textContent=active?payloadModeLabel(active):'所有范围仅为用户可调整的绘图示意';
  if(!active){setMarkup(form,'');return;}
  var p=payloadClean(active),mode=payloadMode(p);
  var field=function(id,label,control,wide) {return '<div class="pl-field'+(wide?' pl-wide':'')+'"><label for="'+id+'">'+label+'</label>'+control+'</div>';};
  var input=function(id,type,value,extra) {return '<input id="'+id+'" type="'+type+'" value="'+esc(String(value))+'" '+(extra||'')+'>';};
  var h=field('payload-name','载荷名称',input('payload-name','text',p.name,'maxlength="100"'),true);
  h+=field('payload-kind','载荷类型','<select id="payload-kind">'+Object.keys(payloadTypeDefs).map(function(k) {return '<option value="'+k+'"'+(k===p.kind?' selected':'')+'>'+esc(payloadTypeDefs[k].name)+'</option>';}).join('')+'</select>');
  h+=field('payload-color','颜色',input('payload-color','color',p.color));
  if(p.kind==='custom')h+=field('payload-custom-mode','收发 / 作用类别','<select id="payload-custom-mode">'+[['active','主动发射 / 探测'],['passive','被动接收'],['effect','作用范围']].map(function(row){return '<option value="'+row[0]+'"'+(row[0]===mode?' selected':'')+'>'+row[1]+'</option>';}).join('')+'</select>',true);
  h+=field('payload-direction','绝对方向（北 0°，顺时针）',input('payload-direction','number',p.direction,'step="any"'));
  h+=field('payload-sweep','开角（360° 为全圈）',input('payload-sweep','number',p.sweep,'min="0" max="360" step="any"'));
  h+=field('payload-range','距离（图面示意单位）',input('payload-range','number',p.range,'min="0" step="any"'),true);
  var styles=mode==='active'||mode==='emitter'?['solid']:mode==='passive'?['dashed','longDash','dot','dashDot','doubleDash']:Object.keys(payloadDashDefs);
  var names={solid:'实线',dashed:'短虚线',longDash:'长虚线',dot:'点线',dashDot:'点划线',doubleDash:'双短划'};
  h+=field('payload-line-style','线型'+(mode==='active'||mode==='emitter'?'（主动固定实线）':mode==='passive'?'（被动虚线）':''),'<select id="payload-line-style"'+(styles.length===1?' disabled':'')+'>'+styles.map(function(k) {return '<option value="'+k+'"'+(k===p.lineStyle?' selected':'')+'>'+names[k]+'</option>';}).join('')+'</select>');
  h+='<div class="pl-field"><label><input id="payload-enabled" type="checkbox"'+(p.enabled?' checked':'')+'>开启此载荷</label><label><input id="payload-show-range" type="checkbox"'+(p.showRange?' checked':'')+'>显示范围</label></div>';
  h+=field('payload-mount-x','挂点 X（相对平台宽度，−50%～50%）',input('payload-mount-x','number',p.mount.x*100,'min="-50" max="50" step="any"'));
  h+=field('payload-mount-y','挂点 Y（相对平台高度，−50%～50%）',input('payload-mount-y','number',p.mount.y*100,'min="-50" max="50" step="any"'));
  if(p.kind==='emDecoy') {
    h+='<div class="pl-wide"><label><input id="payload-show-overlay" type="checkbox"'+(p.showOverlay?' checked':'')+'>显示半透明模拟舰影（保留真实平台）</label></div>';
    h+=field('payload-overlay-name','模拟身份名称（始终带“模拟”标识）',input('payload-overlay-name','text',p.overlayName,'maxlength="60"'),true);
    h+=field('payload-overlay-scale','模拟舰影显示大小（%，10～2000）',input('payload-overlay-scale','number',p.overlayScale*100,'min="10" max="2000" step="any"'),true);
    h+='<div class="pl-wide pl-actions" style="margin:0"><button id="payload-overlay-smaller" type="button">缩小舰影</button><button id="payload-overlay-larger" type="button">放大舰影</button></div><p class="pl-wide pl-info">只调整模拟舰影的显示大小，不改变真实平台、发射范围或真实目标特征。可关闭范围，仅显示模拟叠影。</p>';
  }
  setMarkup(form,h);
}
function payloadMutate(change,refresh) {
  var n=payloadDialogNode();if(!n)return;
  var current=Array.isArray(n.payloads)?n.payloads:[],next=current.map(function(p) {return Object.assign({},p,{mount:Object.assign({},p.mount||{})});});
  change(next,n);
  if(JSON.stringify(current)===JSON.stringify(next))return;
  checkpoint();n.payloads=next;
  if(typeof render==='function')render();
  if(refresh!==false)payloadRefreshDialog();
}
function payloadOpen(n) {
  if(!n)return;
  payloadMountUI();payloadDialogNodeId=n.id;
  var rows=Array.isArray(n.payloads)?n.payloads:[];
  payloadDialogSelection=rows[0]?rows[0].id:null;
  document.getElementById('payloads-dialog').style.display='flex';
  payloadRefreshDialog();document.getElementById('payload-close').focus();
}
function payloadClose() {
  var host=document.getElementById('payloads-dialog');if(host)host.style.display='none';
  payloadDialogNodeId=null;payloadDialogSelection=null;
}
function payloadBindProps(n) {
  var b=document.getElementById('p-payloads');
  if(b)b.addEventListener('click',function() {payloadOpen(payloadNodeById(n.id)||n);});
}
function payloadFocus(n,includeEffects) {
  if(!n || typeof view==='undefined' || typeof svg==='undefined')return;
  var t=payloadNumber(n.rot,0)*Math.PI/180,cx=payloadNumber(n.x,0)+payloadNumber(n.w,96)/2,cy=payloadNumber(n.y,0)+payloadNumber(n.h,96)/2;
  var points=[];
  [[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]].forEach(function(q) {
    var x=q[0]*payloadNumber(n.w,96),y=q[1]*payloadNumber(n.h,96);
    points.push({x:cx+x*Math.cos(t)-y*Math.sin(t),y:cy+x*Math.sin(t)+y*Math.cos(t)});
  });
  var box=payloadBox(points,25);
  if(includeEffects)box=payloadUnion(box,payloadBounds({nodes:[n]}));
  var rect=svg.getBoundingClientRect(),k=Math.min(2,Math.max(1e-150,Math.min((rect.width-70)/Math.max(box.w,1),(rect.height-90)/Math.max(box.h,1))));
  view.k=k;view.x=box.x-(rect.width/k-box.w)/2;view.y=box.y-(rect.height/k-box.h)/2;
  if(typeof applyView==='function')applyView();
  if(typeof renderOverlay==='function')renderOverlay();
}
function payloadDialogClick(e) {
  var target=e.target,host=document.getElementById('payloads-dialog');
  if(target===host || target.id==='payload-close'){payloadClose();return;}
  var b=target.closest && target.closest('[data-payload-select]');
  if(b){payloadDialogSelection=b.getAttribute('data-payload-select');payloadRefreshDialog();return;}
  if(target.id==='payload-add') {
    var n=payloadDialogNode(),old=payloadDialogActive(n),kind=old?payloadKind(old.kind):'eo';
    var fresh=payloadClean({id:payloadId(),name:payloadTypeDefs[kind].name+' · 自定义',kind:kind,enabled:true,
      color:payloadTypeDefs[kind].color,direction:old?old.direction:0,sweep:old?old.sweep:90,range:old?old.range:160,mount:{x:0,y:-.12}});
    payloadDialogSelection=fresh.id;payloadMutate(function(rows){rows.push(fresh);});return;
  }
  if(target.id==='payload-delete'){payloadMutate(function(rows) {var i=rows.map(function(p){return p.id;}).indexOf(payloadDialogSelection);if(i>=0)rows.splice(i,1);});return;}
  if(target.id==='payload-overlay-smaller'||target.id==='payload-overlay-larger') {
    var factor=target.id==='payload-overlay-larger'?1.25:.8;
    payloadMutate(function(rows){rows.forEach(function(p){if(p.id===payloadDialogSelection&&p.kind==='emDecoy')p.overlayScale=Math.max(.1,Math.min(20,payloadNumber(p.overlayScale,1)*factor));});});return;
  }
  if(target.id==='payload-all-on'||target.id==='payload-all-off'){var on=target.id==='payload-all-on';payloadMutate(function(rows){rows.forEach(function(p){p.enabled=on;});});return;}
  if(target.id==='payload-fit'||target.id==='payload-view-platform') {
    var node=payloadDialogNode(),effects=target.id==='payload-fit';payloadClose();payloadFocus(node,effects);return;
  }
}
function payloadDialogChange(e) {
  var target=e.target,preset=target.getAttribute('data-payload-preset'),toggle=target.getAttribute('data-payload-enabled');
  if(preset!==null) {
    var defs=payloadPresetList(payloadDialogNode()),def=defs.filter(function(p){return (p.presetId||p.presetKey||p.id)===preset;})[0];
    var on=target.checked;
    payloadMutate(function(rows) {
      var p=rows.filter(function(q){return (q.presetId||q.presetKey)===preset;})[0];
      if(!p&&on&&def){p=payloadClean(def);p.presetId=preset;p.presetKey=preset;rows.push(p);}
      if(p){p.enabled=on;payloadDialogSelection=p.id;}
    });return;
  }
  if(toggle!==null){var enabled=target.checked;payloadMutate(function(rows){rows.forEach(function(p){if(p.id===toggle)p.enabled=enabled;});});return;}
  var field=target.id.replace(/^payload-/,''),raw=target.value;
  var number=payloadNumber(raw,NaN),valid=true;
  if(field==='range')valid=isFinite(number)&&number>0;
  if(field==='direction')valid=isFinite(number);
  if(field==='sweep')valid=isFinite(number)&&number>0&&number<=360;
  if(field==='mount-x'||field==='mount-y')valid=isFinite(number)&&Math.abs(number)<=50;
  if(field==='overlay-scale')valid=isFinite(number)&&number>=10&&number<=2000;
  if(!valid){target.setCustomValidity(field==='range'?'请输入任意正数距离':'请输入有效的范围数值');target.reportValidity();return;}
  if(target.setCustomValidity)target.setCustomValidity('');
  payloadMutate(function(rows) {rows.forEach(function(p) {
    if(p.id!==payloadDialogSelection)return;
    if(field==='name')p.name=raw.slice(0,100);
    else if(field==='kind'){p.kind=payloadKind(raw);p.type=p.kind;if(p.kind==='custom')p.mode='effect';else delete p.mode;p.color=payloadTypeDefs[p.kind].color;p.lineStyle=payloadMode(p)==='passive'?'dashed':'solid';}
    else if(field==='custom-mode'&&['active','passive','effect'].indexOf(raw)>=0){p.mode=raw;p.lineStyle=raw==='passive'?'dashed':'solid';}
    else if(field==='color'&&/^#[0-9a-f]{6}$/i.test(raw))p.color=raw;
    else if(field==='direction')p.direction=payloadNorm(number);
    else if(field==='sweep')p.sweep=number;
    else if(field==='range')p.range=number;
    else if(field==='line-style'&&payloadDashDefs.hasOwnProperty(raw))p.lineStyle=raw;
    else if(field==='mount-x'||field==='mount-y'){p.mount=Object.assign({},p.mount||{});p.mount[field==='mount-x'?'x':'y']=number/100;}
    else if(field==='enabled')p.enabled=target.checked;
    else if(field==='show-range')p.showRange=target.checked;
    else if(field==='show-overlay')p.showOverlay=target.checked;
    else if(field==='overlay-scale')p.overlayScale=number/100;
    else if(field==='overlay-name')p.overlayName=raw.slice(0,60);
  });});
}
var Payloads = {
  types:payloadTypeDefs,normalizeNode:payloadNormalizeNode,markup:payloadMarkup,bounds:payloadBounds,
  svg:payloadSVG,mount:payloadMount,geometry:payloadGeometry,propsHTML:payloadPropsHTML,bindProps:payloadBindProps,
  open:payloadOpen,close:payloadClose,refresh:payloadRefreshDialog,focus:payloadFocus,
  mode:payloadMode
};
