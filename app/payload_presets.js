/* Drawing suggestions only. No platform capability or real range certification. */
var PayloadPresets = {
  label: '常用绘图预设，可调整',
  notice: '可选示意模块，不代表具体型号实装。距离为示意图面单位，不是实际射程；型号外形和来源国不代表载荷能力认证。',
  types: [
    ['eo', '光电'], ['radar', '雷达'], ['sigint', '电子侦察'], ['magnetic', '磁探'],
    ['activeSonar', '主动声呐'], ['passiveSonar', '被动声呐'], ['emDecoy', '电磁诱饵'],
    ['effect', '作用范围'], ['mainGun', '主炮'], ['secondaryGun', '副炮'],
    ['hpm', '高功率微波'], ['laser', '激光'], ['loiteringMunition', '巡飞弹'], ['custom', '自定义']
  ],
  /* Each tuple: persistent slot, kind, name, schematic range, sweep, direction,
   * normalized mount x/y. All entries start disabled; choosing a template is opt-in. */
  profiles: {
    'uav-eo': {name: '光电无人机', slots: [
      ['eo-main','eo','光电观察',160,65,0,0,-0.12],
      ['radar-option','radar','可选雷达示意',190,110,0,0,0]
    ]},
    'uav-radar': {name: '雷达侦察无人机', slots: [
      ['radar-main','radar','雷达观察',230,120,0,0,0],
      ['eo-main','eo','光电观察',140,60,0,0,-0.12],
      ['sigint-option','sigint','可选电子侦察示意',210,360,0,0,0]
    ]},
    'uav-sigint': {name: '电子侦察无人机', slots: [
      ['sigint-main','sigint','被动电子侦察',220,360,0,0,0],
      ['eo-option','eo','可选光电示意',140,60,0,0,-0.12]
    ]},
    'uav-magnetic': {name: '磁探无人机', slots: [
      ['magnetic-main','magnetic','磁探示意',110,360,0,0,0.1],
      ['eo-main','eo','光电观察',140,60,0,0,-0.12]
    ]},
    'uav-ew': {name: '电子对抗无人机', slots: [
      ['sigint-main','sigint','电子侦察示意',210,360,0,0,0],
      ['effect-main','effect','电子对抗作用示意',170,100,0,0,0],
      ['decoy-option','emDecoy','可选电磁诱饵示意',130,360,0,0,0]
    ]},
    'wingman': {name: '无人僚机绘图构型', slots: [
      ['eo-option','eo','可选光电示意',150,65,0,0,-0.1],
      ['radar-option','radar','可选雷达示意',210,110,0,0,-0.1],
      ['sigint-option','sigint','可选电子侦察示意',190,360,0,0,0],
      ['decoy-option','emDecoy','可选电磁诱饵示意',130,360,0,0,0]
    ]},
    'air-combat': {name: '飞机绘图构型', slots: [
      ['radar-option','radar','可选机载雷达示意',210,100,0,0,-0.15],
      ['eo-option','eo','可选光电示意',150,60,0,0,-0.1],
      ['effect-option','effect','可选作用范围',170,70,0,0,0]
    ]},
    'air-support': {name: '航空平台绘图构型', slots: [
      ['eo-option','eo','可选光电示意',150,60,0,0,-0.1],
      ['radar-option','radar','可选雷达示意',210,360,0,0,0],
      ['sigint-option','sigint','可选电子侦察示意',190,360,0,0,0]
    ]},
    'air-asw': {name: '反潜航空绘图构型', slots: [
      ['radar-option','radar','海面雷达示意',210,120,0,0,0],
      ['eo-option','eo','光电示意',140,60,0,0,-0.1],
      ['magnetic-option','magnetic','可选磁探示意',100,360,0,0,0.12],
      ['sonar-option','passiveSonar','声呐布放概念示意',150,360,0,0,0]
    ]},
    'usv': {name: '无人水面平台', slots: [
      ['eo-main','eo','光电观察',140,70,0,0,-0.1],
      ['radar-option','radar','可选水面雷达示意',200,360,0,0,0],
      ['sigint-option','sigint','可选电子侦察示意',190,360,0,0,0],
      ['decoy-option','emDecoy','可选电磁诱饵示意',130,360,0,0,0.15],
      ['active-option','activeSonar','可选主动声呐示意',140,100,0,0,-0.15],
      ['passive-option','passiveSonar','可选被动声呐示意',170,360,0,0,0.15]
    ]},
    'usv-mine': {name: '扫雷无人艇绘图构型', slots: [
      ['sonar-option','activeSonar','可选猎雷声呐示意',140,90,0,0,-0.1],
      ['sweep-option','magnetic','可选扫雷作用示意',100,360,0,0,0.2],
      ['eo-main','eo','光电观察',140,65,0,0,-0.1],
      ['radar-option','radar','可选航行雷达示意',170,360,0,0,0]
    ]},
    'underwater': {name: '水下概念平台', notes: '仅作水下构型示意；电磁与水声不可相互视为等效探测能力。', slots: [
      ['active-option','activeSonar','可选主动声呐示意',150,100,0,0,-0.15],
      ['passive-option','passiveSonar','可选被动声呐示意',180,360,0,0,0.15],
      ['effect-option','effect','可选水下作用范围',110,360,0,0,0]
    ]},
    'destroyer': {name: '驱逐舰绘图构型', slots: [
      ['radar-main','radar','雷达示意',240,360,0,0,0],
      ['eo-main','eo','光电观察',150,65,0,0,-0.1],
      ['sigint-option','sigint','电子侦察示意',210,360,0,0,0],
      ['active-option','activeSonar','主动声呐示意',150,110,0,0,-0.18],
      ['passive-option','passiveSonar','被动声呐示意',190,360,0,0,0.18],
      ['main-gun','mainGun','主炮作用示意',160,100,0,0,-0.28],
      ['secondary-port','secondaryGun','左舷副炮作用示意',100,140,270,-0.2,0],
      ['secondary-starboard','secondaryGun','右舷副炮作用示意',100,140,90,0.2,0],
      ['decoy-option','emDecoy','可选电磁诱饵示意',130,360,0,0,0.15],
      ['hpm-option','hpm','可选微波作用示意',130,70,0,0,0],
      ['laser-option','laser','可选激光作用示意',130,30,0,0,-0.2],
      ['loitering-option','loiteringMunition','可选巡飞弹作用示意',150,90,0,0,0.1]
    ]},
    'surface-ship': {name: '水面船舶绘图构型', slots: [
      ['radar-option','radar','可选航行雷达示意',200,360,0,0,0],
      ['eo-option','eo','可选光电示意',140,65,0,0,-0.1],
      ['sonar-option','activeSonar','可选声呐示意',150,100,0,0,-0.15]
    ]},
    'ground-radar': {name: '雷达站／车', slots: [
      ['radar-main','radar','雷达观察',220,360,0,0,0],
      ['eo-option','eo','可选光电示意',140,65,0,0,0]
    ]},
    'ground-sigint': {name: '被动电子侦察平台', slots: [
      ['sigint-main','sigint','被动电子侦察',210,360,0,0,0],
      ['eo-option','eo','可选光电示意',140,65,0,0,0]
    ]},
    'ground-eo': {name: '光电观察平台', slots: [
      ['eo-main','eo','光电观察',150,65,0,0,0]
    ]},
    'magnetic-sensor': {name: '磁探示意设备', slots: [
      ['magnetic-main','magnetic','磁探示意',110,360,0,0,0]
    ]},
    'sonar': {name: '水声设备绘图构型', slots: [
      ['active-option','activeSonar','可选主动声呐示意',150,100,0,0,0],
      ['passive-option','passiveSonar','可选被动声呐示意',180,360,0,0,0]
    ]},
    'hpm': {name: '微波作用示意', slots: [
      ['hpm-main','hpm','微波作用示意',130,70,0,0,0],
      ['radar-option','radar','可选雷达示意',190,120,0,0,0]
    ]},
    'laser': {name: '激光作用示意', slots: [
      ['laser-main','laser','激光作用示意',130,30,0,0,0],
      ['eo-option','eo','可选光电跟踪示意',150,60,0,0,0]
    ]},
    'electronic-effect': {name: '电磁作用绘图构型', slots: [
      ['effect-main','effect','电磁作用范围',160,90,0,0,0],
      ['sigint-option','sigint','可选电子侦察示意',190,360,0,0,0],
      ['decoy-option','emDecoy','可选电磁诱饵示意',130,360,0,0,0]
    ]},
    'decoy': {name: '诱饵绘图构型', slots: [
      ['decoy-main','emDecoy','可选电磁诱饵示意',130,360,0,0,0],
      ['effect-option','effect','其他诱饵作用示意',110,360,0,0,0]
    ]},
    'ground-platform': {name: '地面平台绘图构型', slots: [
      ['eo-option','eo','可选光电示意',140,65,0,0,0],
      ['effect-option','effect','可选作用范围',130,90,0,0,0]
    ]},
    'ground-armed': {name: '地面武器平台绘图构型', slots: [
      ['eo-option','eo','可选光电示意',140,65,0,0,-0.1],
      ['main-gun-option','mainGun','可选主炮作用示意',150,90,0,0,-0.2],
      ['secondary-option','secondaryGun','可选副炮作用示意',100,110,0,0,0]
    ]},
    'usv-armed': {name: '武装无人艇绘图构型', slots: [
      ['eo-option','eo','光电观察示意',140,65,0,0,-0.1],
      ['radar-option','radar','可选航行雷达示意',180,360,0,0,0],
      ['secondary-option','secondaryGun','可选武器站作用示意',110,100,0,0,-0.2]
    ]},
    'loitering': {name: '巡飞器绘图构型', slots: [
      ['loitering-option','loiteringMunition','巡飞弹作用示意',140,90,0,0,0],
      ['eo-option','eo','可选光电示意',120,60,0,0,0]
    ]},
    'effect': {name: '作用范围绘图构型', slots: [
      ['effect-main','effect','作用范围示意',140,90,0,0,0]
    ]},
    'custom': {name: '自定义绘图构型', slots: [
      ['custom-main','custom','自定义范围',140,90,0,0,0]
    ]}
  },
  exact: {
    uav_recon_eo:'uav-eo',uav_recon_radar:'uav-radar',uav_recon_sigint:'uav-sigint',uav_magnetic:'uav-magnetic',
    uav_ew_vtol:'uav-ew',uav_ew:'uav-ew',ruav_ew:'uav-ew',loiter_ew:'uav-ew',
    wz7:'uav-radar',wz8:'uav-radar',wz10:'uav-sigint',gj2:'uav-eo',gj11:'air-combat',gj21:'air-combat',
    destroyer:'destroyer',frigate:'destroyer',usv_minesweeper:'usv-mine',minesweeper:'usv-mine',usv_armed:'usv-armed',
    tank:'ground-armed',ifv:'ground-armed',unmanned_tank:'ground-armed',ugv_armed:'ground-armed',robodog_armed:'ground-armed',
    elint_aircraft:'uav-sigint',ew_aircraft:'uav-ew',elint_ship:'ground-sigint',
    asw_patrol:'air-asw',asw_heli:'air-asw',uav_asw:'air-asw',awacs:'uav-radar',aew_heli:'uav-radar',
    mad_sensor:'magnetic-sensor',seismic_sensor:'magnetic-sensor',
    hpm:'hpm',laser_weapon:'laser',cuas_hpm_vehicle:'hpm',cuas_laser_vehicle:'laser',
    cuas_passive:'ground-sigint',cuas_df:'ground-sigint',rf_detector:'ground-sigint',rwr:'ground-sigint',
    camera:'ground-eo',eo_turret:'ground-eo',eo_composite:'ground-eo',ir_sensor:'ground-eo',
    cuas_eo:'ground-eo',cuas_irst:'ground-eo',cuas_mast:'ground-radar',cuas_detect_jam:'electronic-effect',
    underwater_prepositioned_weapon:'underwater',sonar_buoy:'sonar',hull_sonar:'sonar',towed_array:'sonar',
    sonar_station:'sonar',dipping_sonar:'sonar',wave_glider:'underwater',glider:'underwater',
    submarine:'underwater',ssbn:'underwater',rov:'underwater',auv_portable:'underwater',
    drone_launcher:'loitering',drone_nest:'custom',cuas:'ground-radar',
    main_gun:'effect',aaa_gun:'effect',spaa:'ground-radar'
  },
  previewProfiles: [
    {key:'uav_recon_eo',profile:'uav-eo',name:'光电无人机'},
    {key:'uav_recon_radar',profile:'uav-radar',name:'雷达无人机'},
    {key:'uav_recon_sigint',profile:'uav-sigint',name:'电侦无人机'},
    {key:'uav_magnetic',profile:'uav-magnetic',name:'磁探无人机'},
    {key:'usv',profile:'usv',name:'无人艇'},
    {key:'radar',profile:'ground-radar',name:'地面雷达'},
    {key:'underwater_prepositioned_weapon',profile:'underwater',name:'水下概念平台'},
    {key:'destroyer',profile:'destroyer',name:'驱逐舰'}
  ],
  colors: {eo:'#e6a23c',radar:'#3e88dd',sigint:'#aa73da',magnetic:'#35a9a0',activeSonar:'#31a4c4',passiveSonar:'#627ed5',emDecoy:'#d182ca',effect:'#d87353',mainGun:'#c86656',secondaryGun:'#b78542',hpm:'#bb6fe2',laser:'#dc667b',loiteringMunition:'#bf7f39',custom:'#71949b'},
  metadata: function (input) {
    var icon = typeof input === 'string' ? input : input && (input.icon || input.key), key = String(icon || '').replace(/^lib:/,'');
    var map = typeof ICON_MAP !== 'undefined' ? ICON_MAP : null;
    var meta = map && map[key] || (input && typeof input === 'object' && input.key ? input : {});
    return {key:key,name:meta.name || '',cat:meta.cat || '',keywords:meta.keywords || [],originCountry:meta.originCountry || ''};
  },
  profileFor: function (input) {
    var m=this.metadata(input),k=m.key,text=[m.name,m.cat].concat(m.keywords).join(' '),id=this.exact[k];
    if(!id) {
      if(/^wingman_/.test(k))id='wingman';
      else if(/^oneway_|^loiter/.test(k))id='loitering';
      else if(/^(uuv|auv)_/.test(k))id='underwater';
      else if(/^usv(?:_|$)/.test(k))id=/decoy/.test(k)?'decoy':/ew/.test(k)?'electronic-effect':'usv';
      else if(/磁探|磁异常|\bMAD\b/i.test(text))id=/无人机/.test(text)?'uav-magnetic':'magnetic-sensor';
      else if(/雷达|\bradar\b|\bSAR\b/i.test(text)||/radar/i.test(k))id=/无人机|机载|预警机/.test(text)?'uav-radar':'ground-radar';
      else if(/电子侦察|电侦|\bSIGINT\b|\bELINT\b|无线电侦测|测向/i.test(text))id=/无人机/.test(text)?'uav-sigint':'ground-sigint';
      else if(/声呐|水声/.test(text))id='sonar';
      else if(/水下|潜航器|潜艇|潜水器/.test(text)||k==='uuv')id='underwater';
      else if(/hpm|高功率微波|高能微波/i.test(k+' '+text))id='hpm';
      else if(/激光.*(武器|拦截)/.test(text))id='laser';
      else if(/decoy|诱饵/.test(k+' '+text))id='decoy';
      else if(/jammer|spoofer|takeover/.test(k)||/电子对抗|电子战|干扰器|干扰站|干扰设备|诱骗/.test(text))id='electronic-effect';
      else if(/^uav_|^ruav_|^hale_uav$|^swarm$|^target_drone$/.test(k)||/无人机|无人直升机/.test(text))id='uav-eo';
      else if(/光电|摄像|红外.*(搜索|探测)/.test(text))id='ground-eo';
      else if(/战斗机|强击机|轰炸机/.test(text))id='air-combat';
      else if(m.cat==='空中'||/飞机|直升机|浮空器/.test(text))id=/missile|^aam$|^arm$|^ashm$|interceptor/.test(k)?'effect':'air-support';
      else if(/导弹|发射器|发射架|火炮|副炮|近防炮/.test(text))id='effect';
      else if(m.cat==='海上'||/船|舰艇/.test(text))id='surface-ship';
      else if(m.cat==='陆地'||/^ugv|^robodog|^unmanned_tank$/.test(k))id='ground-platform';
      else id='custom';
    }
    return {id:id,name:this.profiles[id].name,label:this.label,notice:this.notice,notes:this.profiles[id].notes || '',iconKey:k,originCountry:m.originCountry,modelStatus:'illustrative-configuration'};
  },
  forNode: function (input) {
    if(input && input.imageOnly)return [];
    var p=this.profileFor(input),self=this;
    return this.profiles[p.id].slots.map(function(s){
      var stable=p.id+':'+s[0];
      return {id:stable,presetKey:stable,presetId:stable,kind:s[1],type:s[1],name:s[2],color:self.colors[s[1]],lineStyle:/^(eo|sigint|passiveSonar|magnetic)$/.test(s[1])?'dashed':'solid',enabled:false,direction:s[5],sweep:s[4],range:s[3],mount:{x:s[6],y:s[7]},profileId:p.id,rangeUnit:'diagram',modelStatus:'illustrative-configuration',notes:self.notice+(p.notes?' '+p.notes:'')};
    });
  }
};
