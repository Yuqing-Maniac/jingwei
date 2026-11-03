/* ============ 织图 · 版式模板库（版式模板） ============
 * window.TEMPLATES: [{id,name,desc,build()}]    window.openTemplates(): 打开模板画廊
 * 依赖 app.js 的全局：doc/cur/mkNode/uid/beautify/checkpoint/loadDoc/render/fit/diagramSVG/contentBBox/legendLayout/measure/snapv
 */
(function () {
  'use strict';

  /* ---------- 图标：只用运行时存在的键 ---------- */
  const lib = () => (typeof ICON_LIB !== 'undefined' ? ICON_LIB : []);
  const has = k => lib().some(i => i.key === k);
  const ic = (k, fb) => (k && has(k) ? 'lib:' + k : (fb && has(fb) ? 'lib:' + fb : null));
  const pk = (n, o) => (has(n) ? n : o);
  const icn = (re, fb) => { const i = lib().find(x => re.test(x.name) || re.test(x.key)); return i ? 'lib:' + i.key : ic(fb); };

  /* ---------- 文档构造工具 ---------- */
  function withDoc(d, fn) { const sd = doc, sc = cur; doc = d; cur = 'root'; try { return fn(); } finally { doc = sd; cur = sc; } }
  function newDoc(name, labels) {
    return { name, theme: 'report', statusLabels: Object.assign({ base: '延续', new: '新增', key: '重点关注' }, labels), custom: {}, lastKind: 'data', pages: { root: { id: 'root', name: '总图', nodes: [], links: [] } } };
  }
  function tools(page) {
    let cx = 0, cy = 0;
    const N = o => {
      const n = mkNode(Object.assign({ x: (cx += 10) }, o));
      if (o.y == null) n.y = (o.type === 'band' || o.type === 'lane') ? (cy += 10) : 0;
      page.nodes.push(n); return n;
    };
    const L = (a, b, o) => { page.links.push(Object.assign({ id: uid(), from: a.id, to: b.id, dir: 'one', kind: 'data', route: 'ortho', label: '' }, o)); };
    /* 一排同类子元素 */
    const items = (parent, list, o = {}) => list.map(s => { const [t, x] = Array.isArray(s) ? s : [s, {}]; return N(Object.assign({ type: 'rect', size: 12, text: t, parent: parent.id }, o, x)); });
    const equips = (parent, list, o = {}) => list.map(([key, t, x]) => N(Object.assign({ type: 'equip', icon: ic(key), text: t, parent: parent.id, w: 100, h: 92, size: 12, noBox: true }, o, x || {})));
    const head = (title, sub) => {
      N({ type: 'text', role: 'title', text: title, size: 24, bold: true, w: 420, h: 36 });
      N({ type: 'text', role: 'subtitle', text: sub, size: 13, w: 640, h: 22, color: 'muted' });
    };
    const foot = note => { if (note) N({ type: 'note', role: 'note', size: 12, w: 900, h: 56, text: note }); N({ type: 'legend', role: 'legend', w: 200, h: 60 }); };
    /* 手工排版的图：自行放置标题／说明／图例 */
    const decor = (x0, W, top, bottom, title, sub, note) => {
      const sb = N({ type: 'text', role: 'subtitle', text: sub, size: 13, h: 22, color: 'muted' });
      sb.w = Math.min(W, Math.ceil(measure(sub, 13, false)) + 24); sb.x = snapv(x0 + W / 2 - sb.w / 2); sb.y = snapv(top - 12 - sb.h);
      const tt = N({ type: 'text', role: 'title', text: title, size: 24, bold: true, h: 36 });
      tt.w = Math.min(W, Math.ceil(measure(title, 24, true)) + 24); tt.x = snapv(x0 + W / 2 - tt.w / 2); tt.y = snapv(sb.y - 4 - tt.h);
      const lg = N({ type: 'legend', role: 'legend', w: 200, h: 60 }); legendLayout(lg, page);
      lg.x = snapv(x0 + W - lg.w); lg.y = snapv(bottom + 12);
      if (note) {
        const nt = N({ type: 'note', role: 'note', size: 12, text: note });
        nt.x = x0; nt.y = snapv(bottom + 12); nt.w = snapv(W - lg.w - 12);
        nt.h = snapv(Math.max(lg.h, wrap(note, nt.w - 20, 12).length * Math.round(12 * 1.38) + 16)); lg.h = nt.h;
      }
    };
    return { N, L, items, equips, head, foot, decor };
  }
  function define(id, name, desc, fn, labels) {
    return { id, name, desc, build() { const d = newDoc(name, labels); return withDoc(d, () => { fn(d, tools(d.pages.root)); return d; }); } };
  }

  /* ====================================================== 1 分层架构图 */
  const t1 = define('layered', '分层架构图', '应用／服务支撑／数据资源／网络基础设施四层，含子系统分组、状态着色与跨层调用', (d, T) => {
    const { N, L, items, head, foot } = T;
    head('无人系统综合管控平台 · 分层架构', '应用层面向指挥与保障，服务层提供通用与业务服务，数据层统一资源，网络层承载多类链路');
    const b0 = N({ type: 'band', text: '应用', w: 1240 });
    const app = items(b0, [['任务筹划', { icon: ic('app') }], ['态势监视', { icon: ic('map', 'app') }], ['协同指挥', { icon: ic('console', 'app') }], ['人在环上监督席', { icon: ic('operator'), status: 'new', bold: true }]], { type: 'round', size: 13 });
    const b1 = N({ type: 'band', text: '服务支撑', w: 1240 });
    const l11 = N({ type: 'lane', text: '业务服务', parent: b1.id });
    const g = [['任务服务', ['任务规划', '航线生成', '冲突检测'], 'new'], ['感知服务', ['目标融合', '态势生成', '威胁评估'], 'base'], ['控制服务', ['设备接入', '链路管理', '编队控制'], 'base']].map(([t, ks, st]) => {
      const gg = N({ type: 'group', text: t, status: st, parent: l11.id }); items(gg, ks); return gg;
    });
    const l12 = N({ type: 'lane', text: '通用服务', parent: b1.id });
    const com = items(l12, [['身份认证', { icon: ic('security') }], ['消息总线', { icon: ic('message_bus', 'api') }], ['电子地图', { icon: ic('map') }], ['时空基准', { icon: ic('clock') }], ['日志审计', { icon: ic('document') }]]);
    const b2 = N({ type: 'band', text: '数据资源', w: 1240 });
    const l21 = N({ type: 'lane', text: '数据资源池', parent: b2.id });
    const dat = items(l21, [['态势数据库', { icon: ic('database') }], ['装备参数库', { icon: ic('database') }], ['任务想定库', { icon: ic('storage', 'database') }], ['知识图谱', { icon: ic('knowledge_graph', 'database'), status: 'new' }], ['模型算法库', { icon: ic('algorithm', 'database') }]]);
    const l22 = N({ type: 'lane', text: '数据治理', parent: b2.id });
    const gov = items(l22, ['采集接入', '清洗融合', '标注归档', '共享交换']);
    for (let i = 0; i < 3; i++) L(gov[i], gov[i + 1]);
    const b3 = N({ type: 'band', text: '网络基础设施', w: 1240 });
    const l31 = N({ type: 'lane', text: '计算资源', parent: b3.id });
    const cmp = items(l31, [['云计算中心', { icon: ic('cloud') }], ['边缘计算节点', { icon: ic('server') }], ['终端计算单元', { icon: ic('gpu', 'server') }]]);
    const l32 = N({ type: 'lane', text: '通信链路', parent: b3.id });
    const net = items(l32, [['北斗短报文', { icon: ic('beidou', 'satellite') }], ['4G／5G', { icon: ic('comm_tower') }], ['数据链', { icon: ic('datalink') }], ['自组网', { icon: ic('mesh') }], ['卫星通信', { icon: ic('sat_station', 'satellite') }]]);
    L(app[0], g[0], { kind: 'ctrl', label: '服务调用' });
    L(app[2], g[2], { kind: 'ctrl' });
    L(g[1], com[2], { kind: 'data', label: '公共服务' });
    L(com[1], dat[1], { kind: 'data', label: '数据读写' });
    L(gov[1], cmp[1], { kind: 'wired', label: '承载' });
    foot('说明：橙色为本期新建或升级的能力；业务服务经通用服务读写数据资源，数据层与应用层之间不直连，统一经服务层调用。');
    beautify(d.pages.root);
  }, { base: '既有能力', new: '新建／升级', key: '重点建设' });

  /* ====================================================== 2 泳道流程图（手工列对齐） */
  const t2 = define('swimlane', '泳道流程图', '指挥员／任务规划系统／地面站／无人机平台四条泳道，含判断分支与跨道箭头', (d, T) => {
    const { N, L, decor } = T;
    const BW = 1280, LH = 120, TW = 100, cx = i => 140 + 56 + i * 112;
    const band = N({ type: 'band', text: '任务全流程', x: 0, y: 0, w: BW, h: 6 + 4 * (LH + 6) });
    const names = ['指挥员', '任务规划系统', '无人机地面站', '无人机平台'];
    const lanes = names.map((t, i) => N({ type: 'lane', text: t, parent: band.id, x: 40, y: 6 + i * (LH + 6), w: BW - 46, h: LH, titleW: TW }));
    const S = (li, ci, text, o = {}) => {
      const big = o.type === 'diamond', w = o.w || (big ? 124 : 88), h = o.h || (big ? 68 : 44);
      return N(Object.assign({ type: 'rect', text, size: 12, parent: lanes[li].id, w, h, x: cx(ci) - w / 2, y: lanes[li].y + (LH - h) / 2 }, o));
    };
    const s0 = S(0, 0, '任务开始', { type: 'ellipse', w: 84, h: 40, bold: true });
    const s1 = S(0, 1, '下达任务意图');
    const s2 = S(1, 2, '生成任务方案');
    const dc = S(1, 3, '是否满足条件', { type: 'diamond', status: 'key' });
    const fx = S(0, 3, '修改任务约束', { status: 'new' });
    const s4 = S(2, 4, '航线装订上传');
    const s5 = S(3, 5, '起飞执行任务');
    const s6 = S(3, 6, '回传侦察数据');
    const s7 = S(2, 7, '接收处理数据');
    const s8 = S(0, 8, '评估任务成果');
    const e = S(0, 9, '任务结束', { type: 'ellipse', w: 84, h: 40, bold: true });
    L(s0, s1); L(s1, s2); L(s2, dc);
    L(dc, s4, { label: '是' }); L(dc, fx, { kind: 'ctrl', label: '否' }); L(fx, s1, { kind: 'ctrl' });
    L(s4, s5, { kind: 'ctrl', label: '上传' }); L(s5, s6); L(s6, s7, { kind: 'radio', label: '数据链' }); L(s7, s8); L(s8, e);
    decor(0, BW, 0, band.h, '无人机侦察任务流程', '指挥员下达意图，规划系统生成并审核方案，地面站装订上传，平台执行并回传成果', '说明：黄色为本次流程新增环节，蓝色为判断节点；“否”分支退回指挥员修改任务约束后重新生成方案。');
  }, { base: '常规环节', new: '新增环节', key: '判断节点' });

  /* ====================================================== 3 装备组网图 */
  const t3 = define('equipnet', '装备组网图', '控制／空中／水面／地面四类节点，装备卡片与无线、卫通、光纤、指令链路，含下钻示例', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('无人系统装备组网图', '地面控制站经数据链、自组网与卫通链路接入空中、水面、地面各类无人节点');
    const W = 1200;
    const bc = N({ type: 'band', text: '控制节点', w: W });
    const ctl = equips(bc, [['operator', '操作员'], ['gcs', '地面控制站'], ['sat_station', '卫通站'], ['comm_tower', '自组网基站']]);
    const ba = N({ type: 'band', text: '空中节点', w: W });
    const air = equips(ba, [[has('uav_relay') ? 'uav_relay' : 'uav_fixed', '中继无人机'], ['uav_male', '察打无人机'], [pk('uav_tethered', 'hale_uav'), '系留无人机'], ['loitering', '巡飞弹', { status: 'new' }]]);
    const bs = N({ type: 'band', text: '水面节点', w: W });
    const sea = equips(bs, [['usv_mother', '无人艇母船'], [pk('usv_armed', 'usv'), '武装无人艇'], [pk('usv_interceptor', 'patrol_boat'), '高速拦截艇'], [pk('usv_survey', 'research_vessel'), '测量无人船']]);
    const bg = N({ type: 'band', text: '地面节点', w: W });
    const grd = equips(bg, [[pk('ugv_armed', 'ugv'), '武装无人车'], ['ugv_tracked', '履带无人车'], [pk('robodog_armed', 'robodog'), '武装四足机器人'], ['eod_robot', '排爆机器人']]);
    L(ctl[0], ctl[1], { kind: 'ctrl', label: '指令' });
    L(ctl[1], ctl[2], { kind: 'wired', dir: 'both', label: '光纤' });
    L(ctl[2], ctl[3], { kind: 'wired', dir: 'both', label: '光纤' });
    L(ctl[1], air[1], { kind: 'radio', dir: 'both', label: '数据链' });
    L(ctl[2], air[2], { kind: 'sat', dir: 'both', label: '卫通' });
    L(ctl[3], air[3], { kind: 'radio', dir: 'both', label: '自组网' });
    L(air[0], air[1], { kind: 'radio', dir: 'both', label: '中继' });
    L(air[0], sea[0], { kind: 'radio', dir: 'both', label: '数据链中继' });
    L(air[2], sea[2], { kind: 'sat', dir: 'both', label: '卫通' });
    L(sea[0], sea[1], { kind: 'radio', dir: 'both' }); L(sea[2], sea[3], { kind: 'radio', dir: 'both' });
    L(sea[1], grd[1], { kind: 'radio', dir: 'both', label: '自组网' });
    L(grd[0], grd[1], { kind: 'radio', dir: 'both' });
    L(grd[2], grd[3], { kind: 'radio', dir: 'both' });
    L(sea[2], grd[2], { kind: 'radio', dir: 'both', label: '自组网' });
    foot('说明：点击“地面控制站”右上角的 ⊕ 可进入其内部构成；双击连线可修改链路标签与类型。');
    /* 下钻页：地面控制站内部构成 */
    const gcs = ctl[1], id = 'pgcs'; const sp = { id, name: '地面控制站 · 内部构成', nodes: [], links: [] }; d.pages[id] = sp; gcs.sub = id;
    const S = tools(sp);
    S.head('地面控制站 · 内部构成', '操控席位、任务规划终端与链路管理单元经内部网络互联，对外接入数据链与卫通链路');
    const b1 = S.N({ type: 'band', text: '席位', w: 1000 });
    const seat = S.equips(b1, [['operator', '飞行操控席'], ['console', '载荷操作席'], ['analyst', '情报判读席'], ['commander', '任务指挥席']]);
    const b2 = S.N({ type: 'band', text: '设备', w: 1000 });
    const dev = S.equips(b2, [['laptop', '任务规划终端'], ['server', '链路管理服务器'], ['storage', '数据记录阵列'], ['clock', '时统设备']]);
    const b3 = S.N({ type: 'band', text: '外联', w: 1000 });
    const ext = S.equips(b3, [['antenna_array', '测控天线'], ['datalink', '数据链电台'], ['sat_station', '卫通终端'], ['router', '网络交换']]);
    seat.forEach((s, i) => S.L(s, dev[i], { kind: 'wired', dir: 'both' }));
    dev.forEach((s, i) => S.L(s, ext[i], { kind: 'wired', dir: 'both' }));
    S.foot();
    beautify(d.pages.root); beautify(sp);
  }, { base: '既有装备', new: '新增装备', key: '重点装备' });

  /* ====================================================== 4 杀伤链（OODA）图（手工列对齐） */
  const t4 = define('killchain', '杀伤链（OODA）图', '发现→定位→跟踪→瞄准→交战→评估环节链，每个环节下挂支撑装备，评估结果反馈回发现', (d, T) => {
    const { N, L, decor } = T;
    const W = 1320, col = i => 57 + i * 208;
    const bf = N({ type: 'band', text: '闭环反馈', x: 0, y: 0, w: W, h: 104 });
    const fg = N({ type: 'group', text: '评估反馈与再决策（OODA 闭环）', status: 'key', parent: bf.id, x: 57, y: 10, w: 1240, h: 84 });
    [['毁伤效果判定', 0], ['目标指示修正', 1], ['再次打击决策', 2]].forEach(([t, i]) => N({ type: 'rect', text: t, size: 12, parent: fg.id, x: 57 + 210 + i * 300, y: 46, w: 220, h: 34 }));
    const bs = N({ type: 'band', text: '环节链', x: 0, y: 140, w: W, h: 74 });
    const names = ['① 发现', '② 定位', '③ 跟踪', '④ 瞄准', '⑤ 交战', '⑥ 评估'];
    const st = names.map((t, i) => N({ type: 'round', text: t, size: 15, bold: true, parent: bs.id, x: col(i) + 10, y: 154, w: 180, h: 46 }));
    for (let i = 0; i < 5; i++) L(st[i], st[i + 1], { kind: 'ctrl' });
    const be = N({ type: 'band', text: '支撑装备', x: 0, y: 250, w: W, h: 252 });
    const sets = [
      ['发现手段', [['radar', '低空雷达'], ['awacs', '预警机'], ['rf_detector', '无线电侦测'], ['ir_sensor', '红外探测']], 'base'],
      ['定位手段', [['acoustic', '声学阵列'], ['laser_rangefinder', '激光测距'], ['beidou', '北斗定位'], ['antenna_array', '测向天线阵']], 'base'],
      ['跟踪手段', [['eo_turret', '光电转塔'], ['phased_radar', '相控阵雷达'], [pk('uav_tethered', 'uav_quad'), '系留无人机'], ['camera', '监控摄像机']], 'base'],
      ['瞄准手段', [['console', '火控席位'], ['algorithm', '火控解算'], ['big_screen', '指挥大屏'], ['datalink', '数据链电台']], 'new'],
      ['交战手段', [['loitering', '巡飞弹'], [pk('uav_ucav', 'uav_male'), '无人作战飞机'], ['laser_weapon', '激光武器'], ['hpm', '高能微波']], 'new'],
      ['评估手段', [['recon_aircraft', '侦察机'], ['analyst', '情报分析员'], ['video', '视频回传'], ['simulation', '毁伤仿真']], 'base'],
    ];
    const gr = sets.map(([t, es, s], i) => {
      const g = N({ type: 'group', text: t, status: s, parent: be.id, x: col(i), y: 260, w: 200, h: 232 });
      es.forEach(([k, tx], j) => N({ type: 'equip', icon: ic(k), text: tx, parent: g.id, w: 88, h: 92, size: 12, noBox: true, x: col(i) + 9 + (j % 2) * 94, y: 260 + 34 + Math.floor(j / 2) * 98 }));
      return g;
    });
    gr.forEach((g, i) => L(st[i], g, { kind: 'plain', dir: 'none' }));
    L(st[5], fg, { kind: 'data', label: '评估结论' });
    L(fg, st[0], { kind: 'ctrl', label: '修正目标指示，转入下一轮发现' });
    decor(0, W, 0, 502, '杀伤链闭环（OODA）', '发现→定位→跟踪→瞄准→交战→评估，评估结果回馈目标指示，形成闭环', '说明：①②③对应观察与判断（Observe／Orient），④对应决策（Decide），⑤对应行动（Act），⑥评估并反馈；橙色为本期重点补强的装备组。');
  }, { base: '现有手段', new: '重点补强', key: '反馈闭环' });

  /* ====================================================== 5 系统组成框图 */
  const t5 = define('compose', '系统组成框图', '顶层系统—分系统—模块三级树状包含关系，新增模块用状态色标示', (d, T) => {
    const { N, L, items, head, foot } = T;
    head('察打一体无人机系统组成框图', '系统由五个分系统组成，各分系统下列出主要组成模块，橙色为本期新增模块');
    const b0 = N({ type: 'band', text: '系统组成', w: 1240 });
    const lt = N({ type: 'lane', text: '系统', parent: b0.id });
    N({ type: 'round', text: '察打一体无人机系统', size: 16, bold: true, parent: lt.id, status: 'key' });
    const b1 = N({ type: 'lane', text: '分系统', parent: b0.id });
    const defs = [
      ['飞行器分系统', ['机体结构', '动力装置', ['飞控计算机', { status: 'new' }], ['组合导航', { status: 'new' }]]],
      ['任务载荷分系统', ['光电转塔', '合成孔径雷达', ['侦干载荷', { status: 'new' }], '弹药挂载']],
      ['测控通信分系统', ['视距数据链', ['卫通链路', { status: 'new' }], '机载中继', '抗干扰模块']],
      ['地面控制分系统', ['任务规划席', '飞行操控席', '载荷操作席', '数据处理单元']],
      ['综合保障分系统', ['检测维护设备', '电源与油料', '运输车辆', ['训练模拟器', { status: 'new' }]]],
    ];
    const gs = defs.map(([t, ks]) => { const g = N({ type: 'group', text: t, parent: b1.id }); items(g, ks); return g; });
    foot('说明：分系统之间的接口关系见接口控制文件；模块级详细组成可通过“创建内部结构”继续下钻。');
    beautify(d.pages.root);
  }, { base: '既有模块', new: '新增模块', key: '系统总体' });

  /* ====================================================== 6 演进路线图（手工列对齐） */
  const t6 = define('roadmap', '演进路线图', '四个建设阶段 × 五个能力域，区分延续与新增，阶段内以箭头表示递进', (d, T) => {
    const { N, L, decor } = T;
    const BW = 1240, LH = 84, HH = 62, X0 = 150, PITCH = 269, CW = 216;
    const band = N({ type: 'band', text: '能力演进', x: 0, y: 0, w: BW, h: 6 + HH + 6 + 5 * (LH + 6) });
    const lh = N({ type: 'lane', text: '演进阶段', parent: band.id, x: 40, y: 6, w: BW - 46, h: HH });
    const heads = ['第一阶段（2026）\n基础构建', '第二阶段（2027）\n协同增强', '第三阶段（2028）\n体系融合', '第四阶段（2029）\n智能跃升'].map((t, i) =>
      N({ type: 'round', text: t, size: 13, bold: true, parent: lh.id, x: X0 + i * PITCH, y: 6 + (HH - 46) / 2, w: CW, h: 46 }));
    for (let i = 0; i < 3; i++) L(heads[i], heads[i + 1], { kind: 'plain' });
    const rows = [
      ['感知探测', [['单站雷达＋光电探测', 'base'], ['多站协同探测与数据融合', 'new'], ['全域多源感知网络', 'new'], ['智能感知与自主识别', 'key']]],
      ['指挥控制', [['人工指令控制', 'base'], ['任务级辅助规划', 'new'], ['多平台协同指挥', 'new'], ['智能体编队自主决策', 'key']]],
      ['通信组网', [['点对点数据链', 'base'], ['自组网与中继扩展', 'new'], ['天地一体融合组网', 'new'], ['抗干扰弹性网络', 'base']]],
      ['智能决策', [['规则库辅助判断', 'base'], ['模型辅助态势研判', 'new'], ['智能体任务规划', 'new'], ['在线学习与自主博弈', 'key']]],
      ['保障运维', [['定期人工检修', 'base'], ['状态监测与预测维护', 'new'], ['数字孪生保障', 'new'], ['预测维护（延续）', 'base']]],
    ];
    rows.forEach(([t, cells], r) => {
      const y = 6 + HH + 6 + r * (LH + 6);
      const ln = N({ type: 'lane', text: t, parent: band.id, x: 40, y, w: BW - 46, h: LH });
      const cs = cells.map(([tx, s], i) => N({ type: 'rect', text: tx, size: 13, status: s, parent: ln.id, x: X0 + i * PITCH, y: y + (LH - 56) / 2, w: CW, h: 56 }));
      for (let i = 0; i < 3; i++) L(cs[i], cs[i + 1], { kind: 'plain' });
    });
    decor(0, BW, 0, band.h, '装备体系演进路线图', '按四个阶段滚动建设，逐级由单点能力走向体系融合与智能化', '说明：白色为延续能力，橙色为本阶段新增能力，蓝色为重点突破方向；箭头表示同一能力域内的逐级演进。');
  }, { base: '延续', new: '新增', key: '重点突破' });

  /* ====================================================== 7 反无人防御体系图 */
  const t7 = define('cuas', '反无人防御体系图', '探测预警／识别跟踪／指挥控制／处置拦截／防护评估五层，配反无人装备图标与层间链路', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('反无人机防御体系图', '多手段探测预警，融合识别跟踪，统一指挥控制，软硬结合处置，闭环防护评估');
    const W = 1400;
    const mk = (t) => N({ type: 'band', text: t, w: W });
    const H = { h: 88 };
    const b1 = mk('探测预警');
    const det = equips(b1, [[pk('cuas_radar_lowalt', 'radar'), '低空监视雷达'], [pk('cuas_radar_4face', 'phased_radar'), '四面阵雷达'], [pk('cuas_passive', 'rf_detector'), '无源侦测'], [pk('cuas_ads_b', 'awacs'), 'ADS-B接收'], [pk('cuas_df', 'rf_detector'), '无线电测向'], [pk('cuas_lidar', 'laser_rangefinder'), '激光雷达'], [pk('cuas_mast', 'radar_station'), '探测桅杆']], H);
    const b2 = mk('识别跟踪');
    const trk = equips(b2, [[pk('cuas_eo', 'eo_turret'), '光电转塔'], [pk('cuas_irst', 'ir_sensor'), '红外搜索跟踪'], [pk('cuas_acoustic_array', 'acoustic'), '声学阵列'], [pk('cuas_remote_id', 'datalink'), 'Remote ID'], ['algorithm', '目标融合识别'], [pk('cuas_detector_portable', 'rf_detector'), '便携侦测仪'], ['camera', '监控摄像机']], H);
    const b3 = mk('指挥控制');
    const cmd = equips(b3, [[pk('cuas_c2', 'command_post'), '反无人指控系统'], [pk('cuas_shelter', 'command_vehicle'), '指控方舱'], ['command_post', '防空指挥所'], ['console', '指控席位'], ['big_screen', '态势大屏'], ['datalink', '数据链'], ['server', '指控服务器']], H);
    const b4 = mk('处置拦截');
    const dis = equips(b4, [[pk('cuas_jammer_omni', 'jammer'), '全向干扰设备'], [pk('cuas_jammer_directional', 'jammer'), '定向干扰设备'], [pk('cuas_spoofer', 'jammer'), '导航诱骗设备'], [pk('cuas_laser_vehicle', 'laser_weapon'), '激光武器车', { status: 'new' }], [pk('cuas_hpm_vehicle', 'hpm'), '高能微波车', { status: 'new' }], [pk('cuas_interceptor_drone', 'uav_fpv'), '拦截无人机'], [pk('cuas_net_drone', 'uav_quad'), '捕网无人机']], H);
    const b5 = mk('防护评估');
    const evl = equips(b5, [[pk('cuas_shield_net', 'security'), '防护网'], [pk('cuas_fence', 'security'), '围栏'], [pk('cuas_decoy', 'security'), '诱饵'], ['analyst', '效果评估'], ['video', '视频取证'], ['maintainer', '装备保障'], ['document', '评估报告']], H);
    L(det[1], trk[1], { label: '目标提示' });
    L(det[3], trk[3], { label: '航迹' });
    L(trk[0], cmd[0], { label: '融合态势' });
    L(trk[3], cmd[3], {});
    L(cmd[0], dis[0], { kind: 'ctrl', label: '处置指令' });
    L(cmd[3], dis[3], { kind: 'ctrl' });
    L(dis[1], evl[1], { label: '处置结果' });
    L(dis[5], evl[5], {});
    L(dis[3], evl[3], {});
    foot('说明：橙色为本期新增的硬杀伤手段；处置指令由指挥控制层统一下达，防护评估结果回馈探测层调整布设。');
    beautify(d.pages.root);
  }, { base: '现有装备', new: '新增装备', key: '重点装备' });

  /* ====================================================== 8 网络拓扑图 */
  const t8 = define('topology', '网络拓扑图', '核心层／汇聚层／接入层／终端层，交换机、路由器、服务器、防火墙、云与数据库图标及有线／无线链路', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('无人系统综合网络拓扑图', '核心层承载数据中心与云平台，汇聚层统一出口与安全边界，接入层覆盖有线、5G、自组网与卫通');
    const W = 1240;
    const b1 = N({ type: 'band', text: '核心层', w: W });
    const core = equips(b1, [['cloud', '云平台'], ['server', '应用服务器'], ['switch', '核心交换机A'], ['switch', '核心交换机B'], ['database', '数据库']], { h: 88 });
    const b2 = N({ type: 'band', text: '汇聚层', w: W });
    const agg = equips(b2, [['router', '边界路由器'], ['firewall', '防火墙'], ['switch', '汇聚交换机A'], ['switch', '汇聚交换机B'], ['relay', '无线接入网关']], { h: 88 });
    const b3 = N({ type: 'band', text: '接入层', w: W });
    const acc = equips(b3, [['sat_station', '卫通站'], ['comm_tower', '5G基站'], ['switch', '接入交换机'], ['mesh', '自组网节点'], ['antenna_array', '测控天线站']], { h: 88 });
    const b4 = N({ type: 'band', text: '终端层', w: W });
    const ter = equips(b4, [['usv', '无人艇'], ['handheld', '手持终端'], ['console', '指控终端'], ['uav_quad', '无人机'], ['ugv', '无人车']], { h: 88 });
    const wd = { kind: 'wired', dir: 'both' }, rd = { kind: 'radio', dir: 'both' };
    L(core[0], core[1], wd); L(core[1], core[2], wd); L(core[2], core[3], Object.assign({ label: '堆叠' }, wd)); L(core[3], core[4], wd);
    L(core[2], agg[2], Object.assign({ label: '万兆' }, wd)); L(core[3], agg[3], Object.assign({ label: '万兆' }, wd));
    L(agg[0], agg[1], wd); L(agg[1], agg[2], wd); L(agg[3], agg[4], wd);
    L(agg[0], acc[0], { kind: 'sat', dir: 'both', label: '卫通' });
    L(agg[1], acc[1], Object.assign({ label: '回传' }, wd));
    L(agg[2], acc[2], Object.assign({ label: '千兆' }, wd));
    L(agg[3], acc[3], wd);
    L(agg[4], acc[4], wd);
    L(acc[0], ter[0], { kind: 'sat', dir: 'both' });
    L(acc[1], ter[1], Object.assign({ label: '5G' }, rd));
    L(acc[2], ter[2], Object.assign({ label: '有线' }, wd));
    L(acc[3], ter[3], Object.assign({ label: '自组网' }, rd));
    L(acc[4], ter[4], Object.assign({ label: '数传' }, rd));
    foot('说明：核心层双机热备；汇聚层统一部署安全边界；移动类终端经 5G、自组网或卫通接入，固定席位经有线接入。');
    beautify(d.pages.root);
  }, { base: '现有设备', new: '新增设备', key: '重点设备' });


  /* ====================================================== 9 复合图标示例（输入—处理—输出） */
  const t9 = define('combo', '复合图标示例', '编队与组合：多个装备合成一个元素，作为输入或输出整体连线（Ctrl+G 组合，Ctrl+Shift+B 编队）', (d, T) => {
    const { N, L, head, foot } = T;
    const C = window.Combo;
    head('无人集群任务规划 · 输入—处理—输出', '编队与跨域集群作为一个整体参与连线：输入为兵力与情报，输出为编队方案');
    const eqc = (parent, icon, text, w, h) => N({ type: 'equip', noBox: true, icon, text, parent: parent.id, w, h, size: 12 });
    const fsz = key => { const a = d.custom[key.slice(3)].aspect, z = C.sizeFor(a, 150); return [z.w, z.h]; };
    const form = (k, n, pat, name, o = {}) => { const key = C.formationIcon(ic(k, 'uav_quad'), n, pat, Object.assign({ name }, o)); return [key, ...fsz(key)]; };
    const mixed = (list, name) => { const key = C.groupIcon(list.map(([k, x, y, s]) => ({ icon: ic(k, 'uav_quad'), x, y, s: s || 1 })), name); return [key, ...fsz(key)]; };

    const b1 = N({ type: 'band', text: '输入', w: 1240, h: 200 });
    const [k1, w1, h1] = form('uav_quad', 6, 'grid', '可用兵力：四旋翼 ×6', { gap: 0.25 });
    const i1 = eqc(b1, k1, '可用兵力：四旋翼 ×6', w1, h1); i1.x = 200;
    const [k2, w2, h2] = mixed([['satellite', 0, 0, 0.9], ['cuas_radar_lowalt', 1.05, 0.25, 0.9], ['uav_male', 2.1, 0, 0.9]], '多源侦察情报');
    const i2 = eqc(b1, k2, '多源侦察情报（卫星＋雷达＋察打无人机）', w2 + 40, h2); i2.x = 600;
    const i3 = N({ type: 'round', text: '任务意图／约束条件', parent: b1.id, w: 180, h: 44, size: 13 }); i3.x = 1000;

    const b2 = N({ type: 'band', text: '处理', w: 1240, h: 140 });
    const p1 = N({ type: 'equip', noBox: true, icon: ic('ai_agent'), text: '任务规划智能体', parent: b2.id, w: 110, h: 100, size: 12, status: 'new' }); p1.x = 380;
    const p2 = N({ type: 'equip', noBox: true, icon: ic('algorithm'), text: '协同分配算法', parent: b2.id, w: 110, h: 100, size: 12 }); p2.x = 720;

    const b3 = N({ type: 'band', text: '输出', w: 1240, h: 200 });
    const [k4, w4, h4] = form('uav_ucav', 3, 'wedge', '察打编队（楔形 ×3）');
    const o1 = eqc(b3, k4, '察打编队（楔形 ×3）', w4, h4); o1.x = 160; o1.status = 'new';
    const [k5, w5, h5] = mixed([['uav_quad', 0.6, 0, 0.85], ['usv_armed', 0, 0.75, 1], ['ugv_armed', 1.15, 0.8, 0.95]], '跨域协同集群');
    const o2 = eqc(b3, k5, '跨域协同集群（空＋水面＋地面）', w5 + 40, h5); o2.x = 520;
    const [k6, w6, h6] = form('cuas_interceptor_drone', 4, 'line', '拦截编队（横队 ×4）', { gap: 0.15 });
    const o3 = eqc(b3, k6, '拦截编队（横队 ×4）', w6, h6); o3.x = 900;

    L(i1, p1, { label: '兵力' }); L(i2, p1, { label: '态势' }); L(i3, p2, { kind: 'ctrl', label: '约束' });
    L(p1, p2, { dir: 'both', label: '方案迭代' });
    L(p1, o1, { kind: 'ctrl', label: '任务分配' }); L(p2, o2, { kind: 'ctrl' }); L(p2, o3, { kind: 'ctrl', label: '拦截指令' });
    foot('说明：复合图标在图中是一个元素——连线、状态着色、下钻、导出 PPT／Visio 时均作为整体处理。选中多个装备按 Ctrl+G 组合，按 Ctrl+Shift+U 拆分；同型装备用“编队”按钮按阵型生成。');
    beautify(d.pages.root);
  }, { base: '延续', new: '本次生成', key: '重点' });

  window.TEMPLATES = [t1, t2, t3, t4, t5, t6, t7, t8, t9];

  /* ====================================================== 画廊 UI */
  const CSS = `
.tpl-gh{grid-column:1/-1;display:flex;gap:6px;align-items:baseline;font-weight:600;font-size:13px;padding:6px 2px 2px;border-bottom:1px solid var(--line)}.tpl-gh span{font-weight:400;font-size:12px;color:var(--muted)}
.tpl-ov{position:fixed;top:0;right:0;bottom:0;left:0;background:rgba(10,15,22,.5);display:flex;align-items:center;justify-content:center;z-index:25;padding:16px}
.tpl-box{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:10px;width:min(1100px,100%);max-height:92vh;display:flex;flex-direction:column;overflow:hidden;font-family:var(--ui,sans-serif);font-size:13px}
.tpl-h{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--line)}
.tpl-h h3{margin:0;font-size:15px;white-space:nowrap}
.tpl-h .sub{color:var(--muted);font-size:12px;flex:1;min-width:0}
.tpl-b{overflow:auto;padding:14px;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.tpl-card{border:1px solid var(--line);border-radius:8px;background:var(--panel);cursor:pointer;display:flex;flex-direction:column;overflow:hidden;min-width:0}
.tpl-card:hover{background:var(--hover)}
.tpl-card:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.tpl-card.sel{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent)}
.tpl-th{background:#fff;aspect-ratio:16/10;min-height:110px;display:flex;align-items:center;justify-content:center;border-bottom:1px solid var(--line)}
.tpl-th svg{width:100%;height:100%;display:block}
.tpl-t{padding:8px 10px 10px}
.tpl-t b{display:block;font-size:13px}
.tpl-t span{display:block;color:var(--muted);font-size:12px;margin-top:2px;line-height:1.5}
.tpl-bar{display:flex;gap:8px;align-items:center;padding:10px 14px;border-top:1px solid var(--line);background:var(--accent-soft);flex-wrap:wrap}
.tpl-bar .msg{flex:1;min-width:200px}
.tpl-bar .msg b{color:var(--accent)}
.tpl-bar button{font:inherit;border:1px solid var(--line);border-radius:6px;padding:5px 12px;cursor:pointer;color:var(--fg);background:var(--panel)}
.tpl-bar button:hover{background:var(--hover)}
.tpl-bar button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.tpl-x{font:inherit;border:1px solid transparent;border-radius:6px;padding:4px 9px;cursor:pointer;color:var(--fg);background:transparent}
.tpl-x:hover{background:var(--hover);border-color:var(--line)}
.tpl-err{padding:20px;color:var(--muted);font-size:12px}
`;
  let thumbs = null;
  function thumbFor(t, i) {
    try {
      const d = t.build();
      return withDoc(d, () => {
        const p = d.pages.root, b = contentBBox(p), pad = 16;
        const vb = [b.x - pad, b.y - pad, b.w + pad * 2, b.h + pad * 2].map(v => Math.round(v)).join(' ');
        return `<svg viewBox="${vb}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">${diagramSVG(p, true, 'tp' + i + '_')}</svg>`;
      });
    } catch (e) { console.error('模板缩略图失败', t.id, e); return '<div class="tpl-err">缩略图生成失败</div>'; }
  }
  function applyTemplate(t) {
    checkpoint();
    const d = t.build();
    d.theme = (doc && doc.theme) || d.theme; d.custom = Object.assign({}, doc && doc.custom);
    loadDoc(d); fit();
    toast('已应用模板：' + t.name);
  }
  function insertAsPage(t) {
    const src = t.build(), idMap = {};
    for (const k of Object.keys(src.pages)) idMap[k] = 'p' + uid();
    checkpoint();
    for (const [k, pg] of Object.entries(src.pages)) {
      pg.id = idMap[k]; if (k === 'root') pg.name = t.name;
      for (const n of pg.nodes) if (n.sub && idMap[n.sub]) n.sub = idMap[n.sub];
      doc.pages[pg.id] = pg;
    }
    const p = P(); let a = sel.size === 1 ? nodeById([...sel][0]) : null;
    if (!a || a.sub || isCont(a) || ['text', 'note', 'legend'].includes(a.type)) {
      const b = contentBBox(p);
      a = mkNode({ type: 'round', text: t.name, x: snapv(b.x), y: snapv(b.y + b.h + 40), w: 200, h: 40 }); p.nodes.push(a);
    }
    a.sub = idMap.root; selectNodes([a.id]); render();
    toast('已插入“' + t.name + '”：点击节点右上角 ⊕ 进入该页');
  }
  window.openTemplates = function () {
    if (document.getElementById('tpl-ov')) return;
    if (!document.getElementById('tpl-css')) { const s = document.createElement('style'); s.id = 'tpl-css'; s.textContent = CSS; document.head.appendChild(s); }
    if (!thumbs) thumbs = window.TEMPLATES.map(thumbFor);
    const ov = document.createElement('div'); ov.className = 'tpl-ov'; ov.id = 'tpl-ov';
    ov.innerHTML = `<div class="tpl-box" role="dialog" aria-label="版式模板"><div class="tpl-h"><h3>版式模板</h3><span class="sub">选择一个版式，在其基础上修改内容，免去从零绘制</span><button class="tpl-x" id="tpl-close" aria-label="关闭">✕</button></div>
<div class="tpl-b">${(() => { const G = []; window.TEMPLATES.forEach((t, i) => { const g = t.group || '通用版式'; let x = G.find(o => o.g === g); if (!x) G.push(x = { g, ids: [] }); x.ids.push(i); });
      return G.map(x => `<div class="tpl-gh">${esc(x.g)}<span>${x.ids.length} 个</span></div>` + x.ids.map(i => { const t = window.TEMPLATES[i]; return `<div class="tpl-card" tabindex="0" role="button" data-i="${i}"><div class="tpl-th">${thumbs[i]}</div><div class="tpl-t"><b>${esc(t.name)}</b><span>${esc(t.desc)}</span></div></div>`; }).join('')).join(''); })()}</div>
<div class="tpl-bar" id="tpl-bar" style="display:none"><span class="msg" id="tpl-msg"></span><button class="primary" id="tpl-use">使用此模板</button><button id="tpl-add">作为新页面插入</button><button id="tpl-cancel">取消</button></div></div>`;
    document.body.appendChild(ov);
    let pick = -1;
    const close = () => { document.removeEventListener('keydown', onKey, true); ov.remove(); };
    const onKey = e => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(); } };
    document.addEventListener('keydown', onKey, true);
    const select = i => {
      pick = i; ov.querySelectorAll('.tpl-card').forEach(c => c.classList.toggle('sel', +c.dataset.i === i));
      const bar = ov.querySelector('#tpl-bar'); bar.style.display = i < 0 ? 'none' : 'flex';
      if (i >= 0) ov.querySelector('#tpl-msg').innerHTML = `已选“<b>${esc(window.TEMPLATES[i].name)}</b>”：将替换当前图，可用 Ctrl+Z 撤销`;
    };
    ov.addEventListener('click', e => {
      if (e.target === ov || e.target.closest('#tpl-close')) { close(); return; }
      const c = e.target.closest('.tpl-card'); if (c) { select(+c.dataset.i); return; }
      if (e.target.closest('#tpl-cancel')) { select(-1); return; }
      if (pick < 0) return;
      const t = window.TEMPLATES[pick];
      if (e.target.closest('#tpl-use')) { close(); applyTemplate(t); }
      else if (e.target.closest('#tpl-add')) { close(); insertAsPage(t); }
    });
    ov.addEventListener('keydown', e => { const c = e.target.closest && e.target.closest('.tpl-card'); if (c && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); select(+c.dataset.i); } });
  };
})();
