/* 示例：边海防无人化巡逻体系（启动默认图，含“无人机机巢”下钻页） */
function buildDemo() {
  const d = { name: '边海防无人化巡逻体系', theme: 'report', statusLabels: { base: '已建', new: '本期新增', key: '重点建设' }, custom: {}, lastKind: 'data', pages: {} };
  doc = d;
  const has = k => typeof ICON_LIB === 'undefined' || ICON_LIB.some(i => i.key === k);
  const ic = (k, fb) => 'lib:' + (has(k) ? k : fb);
  const kit = page => {
    let X = 0, Y = 0;
    const N = o => { const n = mkNode(Object.assign({ x: (X += 10), y: (o.type === 'band' || o.type === 'lane') ? (Y += 10) : 0 }, o)); page.nodes.push(n); return n; };
    const L = (a, b, o = {}) => page.links.push(Object.assign({ id: uid(), from: a.id, to: b.id, dir: 'one', kind: 'data', route: 'ortho', label: '' }, o));
    const eq = (parent, list) => list.map(([k, fb, t, x]) => N(Object.assign({ type: 'equip', icon: ic(k, fb), text: t, parent: parent.id, w: 104, h: 96, size: 12, noBox: true }, x || {})));
    const box = (parent, list, o = {}) => list.map(([t, x]) => N(Object.assign({ type: 'rect', text: t, parent: parent.id, size: 12 }, o, x || {})));
    return { N, L, eq, box };
  };

  /* ---------------- 总图 ---------------- */
  const root = { id: 'root', name: '总图', nodes: [], links: [] }; d.pages.root = root;
  const { N, L, eq, box } = kit(root);
  const W = 1400;
  N({ type: 'text', role: 'title', text: '边海防无人化巡逻体系', size: 24, bold: true, w: 420, h: 36 });
  N({ type: 'text', role: 'subtitle', text: '空中、地面、水面无人平台经卫通、微波与自组网接入指挥中心，实现全天候无人值守巡逻与快速处置', size: 13, w: 760, h: 22, color: 'muted' });

  const bc = N({ type: 'band', text: '指挥控制', w: W, h: 200 });
  const lc2 = N({ type: 'lane', text: '智能研判层', parent: bc.id, w: W - 60, h: 110 });
  const gFuse = N({ type: 'group', text: '态势融合与智能研判', status: 'new', parent: lc2.id, x: 200, w: 520, h: 100 });
  box(gFuse, [['多源融合'], ['目标识别'], ['越界预警']]);
  const gPlan = N({ type: 'group', text: '任务规划与调度', parent: lc2.id, x: 800, w: 420, h: 100 });
  box(gPlan, [['巡逻航线规划'], ['集群任务分配']]);

  const lc1 = N({ type: 'lane', text: '指挥决策层', parent: bc.id, w: W - 60, h: 52 });
  const [hq, fwd, duty, cmdr] = box(lc1, [
    ['边海防指挥中心', { type: 'round', icon: ic('command_center', 'command_post'), status: 'key', bold: true }],
    ['一线管控站', { type: 'round', icon: ic('cmd_shelter', 'command_post') }],
    ['联合值班席', { type: 'round', icon: ic('duty_console', 'console') }],
    ['巡逻指挥员', { type: 'round', icon: ic('cmd_joint', 'commander') }],
  ]);
  const bn = N({ type: 'band', text: '通信网络', w: W, h: 130 });
  const [satst, mw, mesh, teth, leo] = eq(bn, [
    ['sat_station', 'sat_station', '卫通站'], ['microwave_relay', 'relay', '微波接力站'], ['comm_tower', 'comm_tower', '自组网基站'],
    ['uav_tethered', 'uav_quad', '系留中继无人机', { status: 'new' }], ['leo_constellation', 'satellite', '低轨卫星星座'],
  ]);

  const ba = N({ type: 'band', text: '空中巡逻', w: W, h: 130 });
  const [nest, quad, vtol, hale] = eq(ba, [
    ['drone_nest', 'uav_quad', '无人机机巢', { status: 'key' }], ['uav_quad', 'uav_quad', '四旋翼巡查无人机'],
    ['uav_vtol', 'uav_fixed', '垂起固定翼无人机'], ['hale_uav', 'uav_male', '高空长航时无人机'],
  ]);

  const bg = N({ type: 'band', text: '地面巡逻', w: W, h: 130 });
  const [ugs, tower, ugv, dog] = eq(bg, [
    ['ugs', 'acoustic', '无人值守传感器'], ['cuas_mast', 'camera', '光电监控塔'],
    ['ugv', 'ugv', '巡逻无人车', { status: 'new' }], ['robodog', 'robodog', '四足巡逻机器人'],
  ]);

  const bs = N({ type: 'band', text: '水面巡逻', w: W, h: 130 });
  const [radar, usv, intc, wave] = eq(bs, [
    ['radar_station', 'radar', '岸基雷达站'], ['usv', 'usv', '巡逻无人艇'],
    ['usv_interceptor', 'usv', '高速无人拦截艇', { status: 'new' }], ['wave_glider', 'glider', '波浪滑翔器'],
  ]);

  const bp = N({ type: 'band', text: '保障支撑', w: W, h: 130 });
  const lp1 = N({ type: 'lane', text: '数据资源层', parent: bp.id, w: W - 60, h: 52 });
  const [dc, feat, gis, llm] = box(lp1, [
    ['边海防数据中心', { type: 'round', icon: ic('data_center', 'server') }], ['目标特征库', { type: 'round', icon: ic('database', 'database') }],
    ['边境电子地图', { type: 'round', icon: ic('map', 'map') }], ['巡逻研判大模型', { type: 'round', icon: ic('llm', 'ai_agent'), status: 'new' }],
  ]);
  const lp2 = N({ type: 'lane', text: '运维保障层', parent: bp.id, w: W - 60, h: 52 });
  const [ops, pwr, mnt] = box(lp2, [
    ['运维监控', { type: 'round', icon: ic('ops_monitor', 'console') }], ['能源补给', { type: 'round', icon: ic('power_station', 'power_station') }],
    ['维修保障', { type: 'round', icon: ic('maintainer', 'engineer') }],
  ]);

  /* 链路 */
  L(hq, fwd, { kind: 'ctrl', label: '巡逻指令' });
  L(gFuse, hq, { label: '综合态势' });
  L(gPlan, fwd, { kind: 'ctrl', label: '任务下发' });
  L(hq, satst, { kind: 'wired', dir: 'both', label: '光纤' });
  L(fwd, mw, { kind: 'wired', dir: 'both' });
  L(leo, hale, { kind: 'sat', dir: 'both', label: '卫通' });
  L(mesh, quad, { kind: 'radio', dir: 'both', label: '自组网' });
  L(teth, vtol, { kind: 'radio', dir: 'both', label: '数据链' });
  L(nest, quad, { kind: 'ctrl', label: '自主起降' });
  L(quad, tower, { label: '视频回传' });
  L(ugs, tower, { label: '告警联动' });
  L(ugv, dog, { kind: 'radio', dir: 'both', label: '协同' });
  L(radar, usv, { label: '目标指示' });
  L(usv, intc, { kind: 'radio', dir: 'both', label: '编队协同' });
  L(ops, dc, { kind: 'plain', label: '运行状态' });
  L(feat, dc, { kind: 'plain' });
  L(llm, gis, { kind: 'plain' });

  N({ type: 'note', role: 'note', size: 12, w: 900, h: 56, text: '说明：机巢、无人车与无人艇按预设航线全天候自主巡逻，地面传感器与光电监控塔告警后联动无人机抵近查证；指挥中心统一研判并下达处置指令。点击“无人机机巢”右上角 ⊕ 可查看其内部构成。' });
  N({ type: 'legend', role: 'legend', w: 200, h: 60 });

  /* ---------------- 下钻页：无人机机巢 · 内部构成 ---------------- */
  const sp = { id: 'pnest', name: '无人机机巢 · 内部构成', nodes: [], links: [] }; d.pages.pnest = sp; nest.sub = 'pnest';
  const S = kit(sp);
  S.N({ type: 'text', role: 'title', text: '无人机机巢 · 内部构成', size: 22, bold: true, w: 360, h: 34 });
  S.N({ type: 'text', role: 'subtitle', text: '舱体、换电与环境感知单元由边缘计算节点统一调度，经自组网与卫通接入上级', size: 13, w: 620, h: 22, color: 'muted' });
  const s1 = S.N({ type: 'band', text: '机巢本体', w: 1100, h: 130 });
  const body = S.eq(s1, [['uav_quad', 'uav_quad', '巡查无人机'], ['drone_nest', 'uav_quad', '机巢舱体'], ['power_station', 'power_station', '自动换电单元', { status: 'new' }], ['weather', 'weather', '微气象站']]);
  const s2 = S.N({ type: 'band', text: '控制与感知', w: 1100, h: 130 });
  const ctl = S.eq(s2, [['camera', 'camera', '舱外监控'], ['edge_node', 'server', '边缘计算节点', { status: 'key' }], ['beidou', 'satellite', '北斗定位'], ['clock', 'clock', '时统单元']]);
  const s3 = S.N({ type: 'band', text: '对外链路', w: 1100, h: 130 });
  const ext = S.eq(s3, [['comm_tower', 'comm_tower', '自组网电台'], ['satcom_otm', 'sat_station', '卫通终端'], ['fiber', 'router', '光端机'], ['command_center', 'command_post', '上级指挥中心']]);
  S.L(ctl[1], body[1], { kind: 'ctrl', label: '舱门／归中' });
  S.L(body[1], body[0], { kind: 'ctrl', label: '起降' });
  S.L(ctl[1], body[2], { kind: 'ctrl', label: '换电' });
  S.L(ctl[2], ctl[3], { kind: 'plain', label: '授时' });
  S.L(ctl[0], ctl[1], { label: '视频' });
  S.L(ctl[2], ctl[1], { label: '定位' });
  S.L(ctl[1], ext[0], { kind: 'radio', dir: 'both', label: '自组网' });
  S.L(ctl[1], ext[1], { kind: 'sat', dir: 'both', label: '卫通' });
  S.L(ext[1], ext[2], { kind: 'wired', dir: 'both' });
  S.L(ext[2], ext[3], { kind: 'wired', dir: 'both', label: '光纤' });
  S.N({ type: 'legend', role: 'legend', w: 200, h: 60 });

  beautify(root); beautify(sp);
  return d;
}
