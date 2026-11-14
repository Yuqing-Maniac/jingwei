/* Standalone offline country atlas, including generated images and source notes. */
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'assets/country-variants');
const catalog=JSON.parse(fs.readFileSync(path.join(dir,'catalog.json')));
for(const item of catalog.items)for(const side of ['neutral','red','blue'])item.files[side]='data:image/webp;base64,'+fs.readFileSync(path.join(dir,item.files[side])).toString('base64');
let html=fs.readFileSync(path.join(dir,'index.html'),'utf8');
html=html.replace("fetch('catalog.json').then(r=>r.json())",'Promise.resolve('+JSON.stringify(catalog).replace(/</g,'\\u003c')+')');
const out=process.env.JW_COUNTRY_ATLAS_OUT||path.join(root,'_work/country-atlas.html');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,html);console.log(out);
