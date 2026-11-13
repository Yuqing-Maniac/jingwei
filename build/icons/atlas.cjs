const fs=require('fs'),path=require('path');
const dir=path.resolve(__dirname,'../../assets/redraw'),root=path.resolve(__dirname,'../..');
const c=JSON.parse(fs.readFileSync(path.join(dir,'catalog.json')));
for(const icon of c.icons){icon.images={};for(const side of ['neutral','blue','red'])icon.images[side]='data:image/webp;base64,'+fs.readFileSync(path.join(dir,'icons',icon.key+'-'+side+'.webp')).toString('base64');}
let s=fs.readFileSync(path.join(dir,'index.html'),'utf8');
s=s.replace("fetch('catalog.json').then(r=>r.json()).then(c=>{",'(()=>{const c='+JSON.stringify(c)+';').replace("img.src='icons/'+i.key+'-'+side.value+'.webp'","img.src=i.images[side.value]").replace('draw();});','draw();})();');
fs.mkdirSync(path.join(root,'_work/redraw-review'),{recursive:true});
fs.writeFileSync(path.join(root,'_work/redraw-review/icon-atlas-offline.html'),s);
console.log('offline icon atlas generated');
