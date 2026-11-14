/* Build country appearance variants without changing stable generic icon keys. */
const fs=require('fs'),path=require('path'),sharp=require('sharp'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'assets/country-variants');
function clean(data,w,h){
 // Some generated sheets contain thin ruling at cell boundaries. Remove only
 // nearly full-width/height dark rules within the outer 4% of a cell.
 const dark=p=>data[p*4+3]>160&&Math.max(data[p*4],data[p*4+1],data[p*4+2])<110;
 for(let y=0;y<h;y++)if(y<h*.04||y>h*.96){let n=0;for(let x=0;x<w;x++)if(dark(y*w+x))n++;if(n>w*.9)for(let yy=Math.max(0,y-1);yy<=Math.min(h-1,y+1);yy++)for(let x=0;x<w;x++)data[(yy*w+x)*4+3]=0;}
 for(let x=0;x<w;x++)if(x<w*.04||x>w*.96){let n=0;for(let y=0;y<h;y++)if(dark(y*w+x))n++;if(n>h*.9)for(let xx=Math.max(0,x-1);xx<=Math.min(w-1,x+1);xx++)for(let y=0;y<h;y++)data[(y*w+xx)*4+3]=0;}

 const seen=new Uint8Array(w*h);let largest=[],components=[];
 for(let q=0;q<w*h;q++){if(seen[q]||data[q*4+3]<96)continue;const part=[q];seen[q]=1;for(let k=0;k<part.length;k++){const p=part[k],x=p%w,y=Math.floor(p/w);for(const n of [x?w*y+x-1:-1,x<w-1?p+1:-1,y?p-w:-1,y<h-1?p+w:-1])if(n>=0&&!seen[n]&&data[n*4+3]>=96){seen[n]=1;part.push(n);}}
 components.push(part); if(part.length>largest.length)largest=part;}
 // Preserve only the main connected object, with a two-pixel antialiased fringe.
 const keep=new Uint8Array(w*h);for(const p of components.filter(part=>{if(part.length<Math.max(25,largest.length*.015))return false;if(part===largest)return true;let cx=0,cy=0;for(const q of part){cx+=q%w;cy+=Math.floor(q/w);}cx/=part.length;cy/=part.length;return cx>w*.1&&cx<w*.9&&cy>h*.1&&cy<h*.9;}).flat()){const x=p%w,y=Math.floor(p/w);for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++)if(x+dx>=0&&x+dx<w&&y+dy>=0&&y+dy<h)keep[(y+dy)*w+x+dx]=1;}
 for(let p=0;p<w*h;p++)if(!keep[p])data[p*4+3]=0;
 return largest.length/(w*h);
}
function paint(buf,side){const d=Buffer.from(buf);for(let j=0;j<d.length;j+=4){let r=d[j],g=d[j+1],b=d[j+2];if(b>r*1.24&&b>g*1.13&&b-r>25&&d[j+3]){if(side==='red'){d[j]=b;d[j+1]=Math.round(g*.72);d[j+2]=r;}else if(side==='neutral'){const l=Math.round(r*.2126+g*.7152+b*.0722);d[j]=Math.round(l*.91);d[j+1]=Math.round(l*.97);d[j+2]=l;}}}return d;}

(async()=>{
 const catalog=JSON.parse(fs.readFileSync(path.join(root,'assets/redraw/catalog.json'))).icons;
 const names=new Map(catalog.map(x=>[x.key,x]));
 const tasks=fs.readdirSync(dir).filter(x=>x.endsWith('-tasks.json')).flatMap(x=>JSON.parse(fs.readFileSync(path.join(dir,x))));
 const items=[],issues=[],seen=new Set();
 fs.mkdirSync(path.join(dir,'icons'),{recursive:true});fs.mkdirSync(path.join(dir,'masters'),{recursive:true});
 const batchFiles=fs.readdirSync(path.join(dir,'batches')).filter(x=>x.endsWith('.json')&&!x.includes('blocker')).sort();
 const winners=new Map();
 for(const file of batchFiles){const b=JSON.parse(fs.readFileSync(path.join(dir,'batches',file)));if(b.disabled)continue;for(const e of b.entries||[]){const id=e.key+'-'+e.country;if(winners.has(id)&&!file.includes('repair'))throw Error('Duplicate original entry '+id);winners.set(id,file);}}
 for(const file of batchFiles){
  const batch=JSON.parse(fs.readFileSync(path.join(dir,'batches',file)));if(batch.disabled||!batch.entries||!batch.path)continue;
  const master=path.join(dir,'masters',batch.id+'.webp');
  let source=path.resolve(root,batch.path);
  if(!fs.existsSync(source)){if(fs.existsSync(master))source=master;else throw Error('Missing source '+source);}
  if(source!==master){const digest=crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'),stamp=master+'.sha256';if(!fs.existsSync(master)||!fs.existsSync(stamp)||fs.readFileSync(stamp,'utf8').trim()!==digest){await sharp(source).webp({quality:97,alphaQuality:100}).toFile(master);fs.writeFileSync(stamp,digest+'\n');}}
  const meta=await sharp(master).metadata(),cols=batch.columns||4,rows=batch.rows||4,cw=Math.floor(meta.width/cols),ch=Math.floor(meta.height/rows);
  for(let i=0;i<batch.entries.length;i++){
   const e=batch.entries[i],id=e.key+'-'+e.country;
   if(winners.get(id)!==file)continue;
   if(e.status==='blocked'){issues.push({id,issue:'blocked',notes:e.notes});continue;}
   if(!names.has(e.key)||!['cn','us'].includes(e.country)||seen.has(id))throw Error('Unknown or duplicate entry '+id);seen.add(id);
   if(!e.model||!e.modelStatus||!e.sources?.length||e.sources.some(s=>!/^https?:\/\//.test(s.url)))throw Error('Missing public provenance '+id);
   const variants={},files={},index=e.cellIndex===undefined?i:e.cellIndex;
   if(index<0||index>=cols*rows)throw Error('Bad cell '+id);
   const rect=e.rect||{left:index%cols*cw,top:Math.floor(index/cols)*ch,width:cw,height:ch},w=rect.width,h=rect.height;
   if(!Object.values(rect).every(Number.isInteger)||rect.left<0||rect.top<0||w<1||h<1||rect.left+w>meta.width||rect.top+h>meta.height)throw Error('Bad extraction rectangle '+id);
   const cached=['blue','red','neutral'].every(s=>{const f=path.join(dir,'icons',id+'-'+s+'.webp');return fs.existsSync(f)&&fs.statSync(f).mtimeMs>=Math.max(fs.statSync(master).mtimeMs,fs.statSync(__filename).mtimeMs,fs.statSync(path.join(dir,'batches',file)).mtimeMs);});
   if(!cached){
    const raw=await sharp(master).extract(rect).ensureAlpha().raw().toBuffer();
    const area=clean(raw,w,h);if(area>.8)issues.push({id,issue:'opaque_background',area});if(area<.015)issues.push({id,issue:'empty_or_fragmented',area});
    for(const side of ['blue','red','neutral'])await sharp(paint(raw,side),{raw:{width:w,height:h,channels:4}}).resize(232,232,{fit:'contain',background:{r:0,g:0,b:0,alpha:0}}).extend({top:12,bottom:12,left:12,right:12,background:{r:0,g:0,b:0,alpha:0}}).webp({quality:90,alphaQuality:100}).toFile(path.join(dir,'icons',id+'-'+side+'.webp'));
   }
   for(const side of ['blue','red','neutral']){const filename=id+'-'+side+'.webp',buf=fs.readFileSync(path.join(dir,'icons',filename));files[side]='icons/'+filename;variants[side]='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><image width="256" height="256" href="data:image/webp;base64,'+buf.toString('base64')+'"/></svg>';}
   if(new Set(Object.values(variants)).size!==3)issues.push({id,issue:'missing_team_paint'});
   const px=await sharp(path.join(dir,files.blue)).ensureAlpha().raw().toBuffer();let opaque=0,blue=0;for(let q=0;q<px.length;q+=4)if(px[q+3]>=96){opaque++;if(px[q+2]>px[q]*1.24&&px[q+2]>px[q+1]*1.13&&px[q+2]-px[q]>25)blue++;}const corners=[[15,15],[240,15],[15,240],[240,240]];if(opaque/65536>.75&&corners.every(([x,y])=>px[(y*256+x)*4+3]>240))issues.push({id,issue:'opaque_background'});const teamPaintRatio=blue/Math.max(opaque,1);if(teamPaintRatio<.01)issues.push({id,issue:'weak_team_paint',ratio:teamPaintRatio});
   const qualityStatus=e.qualityStatus||((batch.manualReviewCells||[]).includes(index)?'awaiting-manual-review':'artistic-first-pass');
   items.push({...e,qualityStatus,qualityNotes:batch.qualityNotes||[],name:e.model,roleName:names.get(e.key).name,category:names.get(e.key).cat,files,variants,teamPaintRatio,sourceMaster:'masters/'+batch.id+'.webp'});
  }
 }
 const pairs=tasks.filter(t=>seen.has(t.key+'-cn')&&seen.has(t.key+'-us')).length;
 const blocked=batchFiles.flatMap(file=>{const b=JSON.parse(fs.readFileSync(path.join(dir,'batches',file)));return b.blocked||[];});
 for(const file of fs.readdirSync(path.join(dir,'batches')).filter(x=>x.includes('blocker')&&x.endsWith('.json'))){const b=JSON.parse(fs.readFileSync(path.join(dir,'batches',file)));blocked.push(...(b.blocked||[]));}
 const pending=tasks.flatMap(t=>['cn','us'].filter(c=>!seen.has(t.key+'-'+c)).map(c=>({key:t.key,name:t.name,country:c})));
 const data=items.map(x=>({key:x.key,country:x.country,name:x.model,modelStatus:x.modelStatus,qualityStatus:x.qualityStatus,variants:x.variants}));
 fs.writeFileSync(path.join(root,'app/country_icons.js'),'/* Generated by build/icons/package_country.cjs. Public-reference artistic appearances. */\nfor (const item of '+JSON.stringify(data)+') { const icon = ICON_LIB.find(x => x.key === item.key); if (icon) { if (!icon.countries) icon.countries = {}; icon.countries[item.country] = {name:item.name,modelStatus:item.modelStatus,qualityStatus:item.qualityStatus,variants:item.variants}; } }\n');
 const manualReview=items.filter(x=>x.qualityStatus==='awaiting-manual-review').map(x=>({key:x.key,country:x.country,model:x.model,qualityNotes:x.qualityNotes}));
 const report={manualReview,targetRoles:tasks.length,readyModels:items.length,readyPairs:pairs,pending,blocked,roles:tasks.map(t=>({key:t.key,name:t.name,category:t.category})),issues,items:items.map(({variants,...x})=>x)};
 fs.writeFileSync(path.join(dir,'catalog.json'),JSON.stringify(report,null,2)+'\n');
 console.log({target:tasks.length,models:items.length,pairs,pending:pending.length,issues});
})().catch(e=>{console.error(e);process.exit(1)});
