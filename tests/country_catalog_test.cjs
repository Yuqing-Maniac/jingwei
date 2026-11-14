/* Asset registry integrity: stable roles, explicit pending, complete paints. */
const assert=require('assert'),fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'assets/country-variants');
const data=JSON.parse(fs.readFileSync(path.join(dir,'catalog.json')));
const generic=JSON.parse(fs.readFileSync(path.join(root,'assets/redraw/catalog.json'))).icons.concat(JSON.parse(fs.readFileSync(path.join(dir,'supplemental.json'))));
assert.equal(data.targetRoles,333);assert.equal(data.roles.length,333);assert.equal(new Set(data.roles.map(x=>x.key)).size,333);
assert.equal(data.issues.length,0,JSON.stringify(data.issues));
const seen=new Set();for(const x of data.items){const id=x.key+'-'+x.country;assert(!seen.has(id),id);seen.add(id);assert(['cn','us'].includes(x.country));assert(x.sources.length&&x.sources.every(s=>/^https?:\/\//.test(s.url)));assert(x.teamPaintRatio>=.01,id);assert(['reference-reviewed','illustrative-configuration'].includes(x.modelStatus),id);for(const s of ['neutral','red','blue'])assert(fs.statSync(path.join(dir,x.files[s])).size>100,id);}
assert.equal(seen.size,data.readyModels);assert.equal(data.targetAppearances,643);assert.equal(data.readyModels+data.pending.length,643);
const ICON_LIB=generic.map(x=>({key:x.key}));vm.runInNewContext(fs.readFileSync(path.join(root,'app/country_icons.js'),'utf8'),{ICON_LIB});
assert.equal(ICON_LIB.length,690);assert.equal(ICON_LIB.reduce((n,x)=>n+Object.keys(x.countries||{}).length,0),seen.size);
for(const i of ICON_LIB)for(const x of Object.values(i.countries||{})){assert.equal(new Set(Object.values(x.variants)).size,3);for(const s of ['neutral','red','blue'])assert(x.variants[s].includes('data:image/webp;base64,'));}
console.log('country_catalog_test ok:',data.readyModels,'models;',data.readyPairs,'pairs;',data.pending.length,'pending');
