'use strict';
/* Validate matching against the actual icon metadata, without loading artwork in UI. */
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.resolve(__dirname, '..');
const ctx = {console};
vm.createContext(ctx);
for (const name of ['icons.js'].concat(fs.readdirSync(path.join(root,'app')).filter(n => /^icons_.*\.js$/.test(n)).sort())) {
  vm.runInContext(fs.readFileSync(path.join(root,'app',name),'utf8'),ctx,{filename:name});
}
vm.runInContext('var ICON_MAP = Object.fromEntries(ICON_LIB.map(i=>[i.key,i]));',ctx);
vm.runInContext(fs.readFileSync(path.join(root,'app/payload_presets.js'),'utf8'),ctx);
const p = ctx.PayloadPresets;
const plain = value => JSON.parse(JSON.stringify(value));
const expected = {
  uav_recon_eo:'uav-eo',uav_recon_radar:'uav-radar',uav_recon_sigint:'uav-sigint',uav_magnetic:'uav-magnetic',
  uav_ew_vtol:'uav-ew',usv:'usv',usv_minesweeper:'usv-mine',radar:'ground-radar',phased_radar:'ground-radar',
  cuas_radar_vehicle:'ground-radar',underwater_prepositioned_weapon:'underwater',destroyer:'destroyer',
  frigate:'destroyer',uuv:'underwater',rov:'underwater',mad_sensor:'magnetic-sensor',hpm:'hpm',
  cuas_laser_vehicle:'laser',fighter:'air-combat',transport:'air-support',asw_patrol:'air-asw',
  wz7:'uav-radar',wz8:'uav-radar',wz10:'uav-sigint',gj2:'uav-eo',gj11:'air-combat',gj21:'air-combat',
  wingman_fh97:'wingman',wingman_fh97a:'wingman',wingman_xq58:'wingman',wingman_mq28:'wingman',
  oneway_shahed136:'loitering',oneway_lucas:'loitering',uav_quad:'uav-eo',tank:'ground-armed',
  usv_armed:'usv-armed',camera:'ground-eo',hull_sonar:'sonar'
};
for(const [key,profile] of Object.entries(expected)) {
  assert(vm.runInContext('!!ICON_MAP['+JSON.stringify(key)+']',ctx),'Missing real fixture '+key);
  assert.strictEqual(p.profileFor({icon:'lib:'+key}).id,profile,key);
}
const types = new Set(p.types.map(x=>x[0]));
assert.deepStrictEqual([...types].sort(),['eo','radar','sigint','magnetic','activeSonar','passiveSonar','emDecoy','effect','mainGun','secondaryGun','hpm','laser','loiteringMunition','custom'].sort());
let checked = 0;
for(const key of vm.runInContext('Object.keys(ICON_MAP)',ctx)) {
  const node={icon:'lib:'+key,appearance:'cn',affiliation:'blue'},before=JSON.stringify(node),a=p.forNode(node),b=p.forNode({...node,appearance:'us',affiliation:'red'});
  assert.strictEqual(JSON.stringify(node),before,'Matching mutated node');
  assert.deepStrictEqual(plain(a),plain(b),'Country/team paint changed capabilities: '+key);
  const ids=new Set();
  for(const item of a){
    assert(types.has(item.kind),key);assert(!ids.has(item.presetKey));ids.add(item.presetKey);
    assert.strictEqual(item.presetKey,item.presetId);assert.strictEqual(item.presetKey,item.id);
    assert.strictEqual(item.enabled,false);assert.strictEqual(item.rangeUnit,'diagram');
    assert.strictEqual(item.modelStatus,'illustrative-configuration');
    assert(item.range>0&&item.sweep>0&&item.sweep<=360&&item.direction>=0&&item.direction<360);
    assert(Math.abs(item.mount.x)<=.5&&Math.abs(item.mount.y)<=.5);
    assert(item.notes.includes('不代表具体型号实装'));
    assert.strictEqual(item.lineStyle,/^(eo|sigint|passiveSonar|magnetic)$/.test(item.kind)?'dashed':'solid');
  }
  if(a.length){a[0].range=999;a[0].enabled=true;a[0].mount.x=.49;assert.deepStrictEqual(plain(p.forNode(node)),plain(b),'Shared mutable defaults: '+key);}
  checked++;
}
assert(checked>=690,'Expected the complete current icon library');
assert.strictEqual(p.previewProfiles.length,8);
for(const preview of p.previewProfiles)assert.strictEqual(p.profileFor(preview.key).id,preview.profile);
function kinds(key){return new Set(p.forNode('lib:'+key).map(x=>x.kind));}
for(const kind of ['eo','radar','sigint','activeSonar','passiveSonar','mainGun','secondaryGun','hpm','laser','loiteringMunition','emDecoy'])assert(kinds('destroyer').has(kind),kind);
for(const kind of ['eo','radar','sigint','emDecoy','activeSonar','passiveSonar'])assert(kinds('usv').has(kind),kind);
assert.deepStrictEqual([...kinds('uav_magnetic')].sort(),['eo','magnetic']);
assert.strictEqual(p.forNode('lib:destroyer').filter(x=>x.kind==='secondaryGun').length,2);
assert.strictEqual(p.forNode({icon:'cu:picture',imageOnly:true}).length,0);
assert.strictEqual(p.forNode('lib:unknown-future-platform')[0].kind,'custom');
// New metadata can select a profile without adding another hard-coded model name.
assert.strictEqual(p.profileFor({key:'test-eo-airframe',name:'光电巡查无人机',cat:'无人',keywords:['EO/IR']}).id,'uav-eo');
assert.strictEqual(p.profileFor({key:'test-radar-truck',name:'观察车',cat:'感知通信',keywords:['雷达']}).id,'ground-radar');
assert.strictEqual(p.profileFor({key:'test-uuv',name:'水下概念平台',originCountry:'us'}).id,p.profileFor({key:'test-uuv',name:'水下概念平台',originCountry:'cn'}).id);
console.log('PASS payload presets: '+checked+' icon keys, 8 previews, optional multi-payload schemas and origin-independent matching');
