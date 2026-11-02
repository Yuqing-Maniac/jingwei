import json,sys
from playwright.sync_api import sync_playwright
CHK = r"""(tag)=>{const out=[];
 for(const p of Object.values(doc.pages)){ const saved=cur; cur=p.id;
  const byId=new Map(p.nodes.map(n=>[n.id,n]));
  for(const n of p.nodes){ if([n.x,n.y,n.w,n.h].some(v=>typeof v!=='number'||!isFinite(v))) out.push('NaN '+n.type+':'+n.text);
    if(n.w<4||n.h<4) out.push('tiny '+n.type+':'+(n.text||'')+' '+n.w+'x'+n.h);
    const par=n.parent&&byId.get(n.parent);
    if(n.parent&&!par) out.push('orphan parent '+n.text);
    if(par&&(n.x<par.x-1||n.y<par.y-1||n.x+n.w>par.x+par.w+1||n.y+n.h>par.y+par.h+1)) out.push('outside '+(n.text||n.type)+' in '+(par.text||par.type)+` [${Math.round(n.x)},${Math.round(n.y)},${Math.round(n.w)},${Math.round(n.h)}] vs [${Math.round(par.x)},${Math.round(par.y)},${Math.round(par.w)},${Math.round(par.h)}]`);}
  const leaves=p.nodes.filter(n=>!isCont(n)&&!['text','legend','tblock','note'].includes(n.type));
  for(let i=0;i<leaves.length;i++)for(let j=i+1;j<leaves.length;j++){const a=leaves[i],b=leaves[j]; if(a.parent!==b.parent) continue;
    const ox=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x), oy=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);
    if(ox>3&&oy>3) out.push('overlap '+a.text+' / '+b.text);}
  // sibling containers overlap
  const conts=p.nodes.filter(n=>isCont(n));
  for(let i=0;i<conts.length;i++)for(let j=i+1;j<conts.length;j++){const a=conts[i],b=conts[j]; if(a.parent!==b.parent) continue;
    const ox=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x), oy=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);
    if(ox>3&&oy>3) out.push('cont overlap '+a.text+' / '+b.text);}
  let R; try{R=routesFor(p);}catch(e){out.push('routes EXC '+e.message);}
  for(const l of p.links){ if(!byId.get(l.from)||!byId.get(l.to)){out.push('dangling link');continue;}
    const r=R&&R.get(l.id); if(!r) out.push('null route '+byId.get(l.from).text+'->'+byId.get(l.to).text);
    else if(r.some&&r.some(q=>!isFinite(q.x)||!isFinite(q.y))) out.push('NaN route');
    const t=linkText(l,p); if(t&&r){const pos=labelFor(l,p,linkPoints(l,p),t); const w=measure(t,11.5,false)+10;
      for(const n of leaves){ if(n.id===l.from||n.id===l.to) {} const ox=Math.min(pos.x+w/2,n.x+n.w)-Math.max(pos.x-w/2,n.x), oy=Math.min(pos.y+9,n.y+n.h)-Math.max(pos.y-9,n.y); if(ox>4&&oy>4){out.push('label on box '+t+' @ '+n.text);break;} }}
  }
  cur=saved;}
 return out;}"""
with sync_playwright() as pw:
  b=pw.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':1000})
  errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
  pg.goto('file:///home/claude/drawtool/offline.html'); pg.wait_for_timeout(1500)
  ids=pg.evaluate("()=>TEMPLATES.map(t=>t.id+'|'+t.name)")
  print(len(ids),'templates')
  for tid in ids:
    i=tid.split('|')[0]
    for lay in ['standard','compact','report']:
      errs.clear()
      pg.evaluate("(i)=>{const t=TEMPLATES.find(x=>x.id===i);const d=t.build();loadDoc(d);fit();render()}", i)
      base=pg.evaluate(CHK,'base') if lay=='standard' else []
      pg.evaluate("(l)=>{doc.layout=l; const b=document.querySelector('#d-lay [data-v='+l+']'); if(b) b.click();}", lay)
      pg.keyboard.press('Control+Shift+F'); pg.wait_for_timeout(150)
      after=pg.evaluate(CHK,'b')
      pg.keyboard.press('Control+Shift+X'); pg.wait_for_timeout(150)
      after2=pg.evaluate(CHK,'x')
      if base or after or after2 or errs:
        print('==',tid,lay)
        if base: print('  base:',base[:8])
        if after: print('  beautify:',after[:8])
        if set(after2)-set(after): print('  reduce:',list(set(after2)-set(after))[:6])
        if errs: print('  ERR',errs[:4])
  b.close()
