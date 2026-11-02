/* ============ 织图 · 体系结构视图模板（OV-1／OV-2／OV-5b／SV-1／SV-4 + 信息系统架构六图） ============
 * 须在 templates.js、standards.js 之后加载；向 window.TEMPLATES 追加符合规范包数据约定的模板：
 *   group「体系结构视图」：DoDAF 五图；group「信息系统架构」：业务／应用／数据／技术／部署／安全架构图
 *   （虚构案例「边海防无人化巡逻体系·指控信息系统」）。
 * 数据约定见 STD_SPEC.md：page.view、doc.meta、doc.showCodes、node.etype／code／attrs、link.code／attrs、tblock。
 */
(function () {
  'use strict';
  if (!window.TEMPLATES) window.TEMPLATES = [];

  /* ---------- 图标与文档工具（自 templates.js 复制的小工具） ---------- */
  const lib = () => (typeof ICON_LIB !== 'undefined' ? ICON_LIB : []);
  const has = k => lib().some(i => i.key === k);
  const ic = (k, fb) => (k && has(k) ? 'lib:' + k : (fb && has(fb) ? 'lib:' + fb : null));

  function withDoc(d, fn) { const sd = doc, sc = cur; doc = d; cur = 'root'; try { return fn(); } finally { doc = sd; cur = sc; } }
  const today = () => { const t = new Date(), p = n => String(n).padStart(2, '0'); return `${t.getFullYear()}-${p(t.getMonth() + 1)}-${p(t.getDate())}`; };
  function newDoc(name, view, labels, meta) {
    return {
      name, theme: 'report', statusLabels: Object.assign({ base: '现有', new: '新增', key: '重点' }, labels), custom: {}, lastKind: 'data',
      meta: Object.assign({ project: '边海防无人化巡逻体系', drawingNo: 'HT-ZT-001', version: 'V1.0', classification: '内部', author: '[姓名]', reviewer: '[姓名]', approver: '[姓名]', date: today(), org: '[单位名称]' }, meta || {}),
      showCodes: true,
      pages: { root: { id: 'root', name: name, nodes: [], links: [], view } }
    };
  }
  function tools(page) {
    let cx = 0, cy = 0;
    const N = o => {
      const n = mkNode(Object.assign({ x: (cx += 10) }, o));
      if (o.y == null) n.y = (o.type === 'band' || o.type === 'lane') ? (cy += 10) : 0;
      page.nodes.push(n); return n;
    };
    const L = (a, b, o) => {
      const l = Object.assign({ id: uid(), from: a.id, to: b.id, dir: 'one', kind: 'data', route: 'ortho', label: '' }, o);
      const at = Object.assign({}, l.attrs || {}); if (!at.content && l.label) at.content = l.label;
      l.attrs = at; if (!l.label && at.content && o && o.showLabel) l.label = at.content;
      page.links.push(l); return l;
    };
    const equips = (parent, list, o = {}) => list.map(([key, t, x]) => N(Object.assign({ type: 'equip', icon: Array.isArray(key) ? ic(...key) : ic(key), text: t, parent: parent.id, w: 104, h: 92, size: 12, noBox: true }, o, x || {})));
    const items = (parent, list, o = {}) => list.map(s => { const [t, x] = Array.isArray(s) ? s : [s, {}]; return N(Object.assign({ type: 'rect', size: 12, text: t, parent: parent.id }, o, x)); });
    const head = (title, sub) => {
      N({ type: 'text', role: 'title', text: title, size: 24, bold: true, w: 420, h: 36 });
      N({ type: 'text', role: 'subtitle', text: sub, size: 13, w: 640, h: 22, color: 'muted' });
    };
    const foot = note => { N({ type: 'note', role: 'note', size: 12, w: 900, h: 56, text: note }); N({ type: 'legend', role: 'legend', w: 200, h: 60 }); };
    const decor = (x0, W, top, bottom, title, sub, note) => {
      const sb = N({ type: 'text', role: 'subtitle', text: sub, size: 13, h: 22, color: 'muted' });
      sb.w = Math.min(W, Math.ceil(measure(sub, 13, false)) + 24); sb.x = snapv(x0 + W / 2 - sb.w / 2); sb.y = snapv(top - 12 - sb.h);
      const tt = N({ type: 'text', role: 'title', text: title, size: 24, bold: true, h: 36 });
      tt.w = Math.min(W, Math.ceil(measure(title, 24, true)) + 24); tt.x = snapv(x0 + W / 2 - tt.w / 2); tt.y = snapv(sb.y - 4 - tt.h);
      const lg = N({ type: 'legend', role: 'legend', w: 200, h: 60 }); legendLayout(lg, page);
      lg.x = snapv(x0 + W - lg.w); lg.y = snapv(bottom + 12);
      const nt = N({ type: 'note', role: 'note', size: 12, text: note });
      nt.x = x0; nt.y = snapv(bottom + 12); nt.w = snapv(W - lg.w - 12);
      nt.h = snapv(Math.max(lg.h, wrap(note, nt.w - 20, 12).length * Math.round(12 * 1.38) + 16)); lg.h = nt.h;
    };
    return { N, L, equips, items, head, foot, decor };
  }

  /* ---------- 编码：按阅读顺序（自上而下、自左而右，以中心点计）编号 ---------- */
  const PFX = new Proxy({}, { get: (_, e) => (window.Std && Std.ETYPES[e] && Std.ETYPES[e].prefix) || undefined });
  const LPFX = new Proxy({}, { get: (_, v) => (window.Std && Std.VIEWS[v] && Std.VIEWS[v].link) || 'LK' });
  function absPos(n, p) { let x = n.x, y = n.y; return { cx: x + n.w / 2, cy: y + n.h / 2 }; }
  function codeAll(p) {
    const pos = n => absPos(n, p);
    const ord = (a, b) => { const A = pos(a), B = pos(b); return Math.abs(A.cy - B.cy) > 30 ? A.cy - B.cy : A.cx - B.cx; };
    const cnt = {};
    p.nodes.filter(n => n.etype && PFX[n.etype]).sort(ord).forEach(n => {
      const k = PFX[n.etype]; cnt[k] = (cnt[k] || 0) + 1; n.code = `${k}-${String(cnt[k]).padStart(2, '0')}`;
    });
    const byId = id => p.nodes.find(n => n.id === id);
    const lp = LPFX[p.view]; let i = 0;
    p.links.slice().sort((a, b) => { const r = ord(byId(a.from), byId(b.from)); return r || ord(byId(a.to), byId(b.to)); })
      .forEach(l => { l.code = `${lp}-${String(++i).padStart(2, '0')}`; });
  }
  /* 图框：放在整图右下角 */
  function addTblock(p) {
    const ns = p.nodes.filter(n => n.type !== 'tblock');
    const R = Math.max(...ns.map(n => n.x + n.w)), B = Math.max(...ns.map(n => n.y + n.h));
    const n = mkNode({ type: 'tblock', w: 520, h: 120, text: '' });
    n.x = snapv(R - 520); n.y = snapv(B + 16); p.nodes.push(n);
  }
  function finish(d) { const p = d.pages.root; codeAll(p); addTblock(p); }

  function define(id, view, name, desc, fn, labels, group, meta) {
    return {
      id, name, desc, group: group || '体系结构视图',
      build() { const d = newDoc(name, view, labels, meta); return withDoc(d, () => { fn(d, tools(d.pages.root), d.pages.root); finish(d); return d; }); }
    };
  }
  const NOTE = v => `说明：依据 DoDAF 2.02／UAF 视图约定绘制（${v}）；元素与连线编码按阅读顺序自动编号，属性见检查器，题签数据取自文档信息。`;
  const E = (etype, desc, extra) => Object.assign({ etype, attrs: Object.assign({ desc, owner: '总体设计组' }, extra || {}) });
  const A = (content, extra) => ({ attrs: Object.assign({ content }, extra || {}) });

  /* =========================================================== OV-1 */
  const ov1 = define('std-ov1', 'OV-1', 'OV-1 高层作战概念图', '边海防无人化巡逻的高层作战概念：指挥、空中、地面、水面四带装备卡片与概念关联线', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('边海防无人化巡逻 · 高层作战概念图（OV-1）', '指挥中心统一筹划，空地水无人平台协同巡逻、发现、识别并联动处置');
    const W = 1240;
    const bc = N({ type: 'band', text: '指挥', w: W });
    const [hq, post, duty] = equips(bc, [
      ['command_center', '边海防指挥中心', E('op_node', '统一筹划、态势研判与处置决策', { owner: '边海防指挥部' })],
      ['cmd_shelter', '前沿管控站', E('op_node', '前沿区域管控与处置协调')],
      ['operator', '值班指挥员', E('performer', '任务下达与人在环上监督')]]);
    const ba = N({ type: 'band', text: '空中', w: W });
    const [nest, quad, hale] = equips(ba, [
      ['drone_nest', '无人机机巢', E('resource', '无人机自动起降、充换电与值守')],
      ['uav_quad', '巡查无人机', E('resource', '低空巡查与目标确认')],
      ['hale_uav', '长航时无人机', E('resource', '广域监视与通信中继')]]);
    const bg = N({ type: 'band', text: '地面', w: W });
    const [tower, ugv, dog] = equips(bg, [
      ['cuas_mast', '光电监控塔', E('resource', '固定点位光电监视')],
      ['ugv', '巡逻无人车', E('resource', '沿边道路自主巡逻')],
      ['robodog', '四足巡逻机器人', E('resource', '复杂地形近距侦察')]]);
    const bs = N({ type: 'band', text: '水面', w: W });
    const [radar, usv, intc] = equips(bs, [
      ['radar_station', '岸基雷达站', E('resource', '海域目标探测与跟踪')],
      ['usv', '巡逻无人艇', E('resource', '近岸水域巡逻')],
      ['usv_interceptor', '高速无人拦截艇', Object.assign(E('resource', '可疑船只拦截处置'), { status: 'new' })]]);
    L(hq, post, { kind: 'wired', dir: 'both', label: '指挥链路', attrs: { content: '指挥关系', medium: '光纤' } });
    L(post, duty, { kind: 'ctrl', dir: 'both', label: '监督', attrs: { content: '人在环上监督' } });
    L(hq, nest, { kind: 'ctrl', label: '巡逻任务', attrs: { content: '巡逻任务指令' } });
    L(post, quad, { kind: 'ctrl', label: '任务指令', attrs: { content: '任务指令' } });
    L(duty, hale, { kind: 'ctrl', label: '广域监视', attrs: { content: '广域监视任务' } });
    L(nest, quad, { kind: 'ctrl', label: '起飞放飞', attrs: { content: '放飞指令' } });
    L(quad, ugv, { kind: 'data', label: '目标指示', attrs: { content: '目标指示' } });
    L(hale, dog, { kind: 'data', label: '态势共享', attrs: { content: '广域态势' } });
    L(ugv, dog, { kind: 'radio', dir: 'both', label: '协同', attrs: { content: '协同巡逻' } });
    L(tower, radar, { kind: 'data', label: '联动', attrs: { content: '联动提示' } });
    L(ugv, usv, { kind: 'data', label: '目标指示', attrs: { content: '目标指示' } });
    L(dog, intc, { kind: 'ctrl', label: '拦截引导', attrs: { content: '拦截引导' } });
    L(usv, intc, { kind: 'ctrl', label: '处置引导', attrs: { content: '处置引导' } });
    foot(NOTE('OV-1') + '　橙色为本期新增能力。');
    beautify(d.pages.root);
  }, { base: '现有能力', new: '本期新增', key: '重点' });

  /* =========================================================== OV-2 */
  const ov2 = define('std-ov2', 'OV-2', 'OV-2 作战资源流描述', '作战节点与需求线：目标指示、态势共享、任务指令等资源流', (d, T) => {
    const { N, L, items, head, foot } = T;
    head('边海防无人化巡逻 · 作战资源流描述（OV-2）', '作战节点之间的需求线承载任务指令、目标指示与态势信息的交换');
    const W = 1240;
    const nd = (par, t, desc, ico, x) => [t, Object.assign({ type: 'round', icon: ic(ico), h: 44 }, E('op_node', desc), x || {})];
    const b1 = N({ type: 'band', text: '决策', w: W });
    const [intel, hq] = items(b1, [
      nd(b1, '情报保障节点', '情报融合、研判与共享', 'staff_intel'),
      nd(b1, '边海防指挥中心', '统一指挥与决策', 'command_center', { status: 'key', bold: true })]);
    const b2 = N({ type: 'band', text: '管控', w: W });
    const [nav, post] = items(b2, [
      nd(b2, '通信保障节点', '链路组网与通信保障', 'comm_tower'),
      nd(b2, '前沿管控站', '前沿管控与处置协调', 'cmd_shelter')]);
    const b3 = N({ type: 'band', text: '巡逻', w: W });
    const [air, sea, gnd] = items(b3, [
      nd(b3, '空中巡逻节点', '无人机巡查与中继', 'uav_quad'),
      nd(b3, '水面巡逻节点', '无人艇与岸基雷达巡逻', 'usv'),
      nd(b3, '地面巡逻节点', '无人车与机器人巡逻', 'ugv')]);
    const b4 = N({ type: 'band', text: '处置', w: W });
    const [fast] = items(b4, [nd(b4, '快速处置力量', '拦截、驱离与抓捕', 'squad', { status: 'new' })]);
    L(hq, intel, { dir: 'both', label: '情报需求／情报产品', attrs: { content: '情报需求、情报产品', latency: '≤5 min' } });
    L(hq, post, { kind: 'ctrl', label: '任务指令', attrs: { content: '任务指令', freq: '事件触发' } });
    L(post, hq, { kind: 'data', label: '态势共享', attrs: { content: '综合态势', freq: '1 Hz', latency: '≤1 s' } });
    L(post, air, { kind: 'ctrl', dir: 'both', label: '巡逻任务／状态', attrs: { content: '巡逻任务、状态回传', freq: '1 Hz', latency: '≤100 ms' } });
    L(post, gnd, { kind: 'ctrl', dir: 'both', label: '巡逻任务／状态', attrs: { content: '巡逻任务、状态回传', freq: '1 Hz', latency: '≤200 ms' } });
    L(post, sea, { kind: 'ctrl', dir: 'both', label: '巡逻任务／状态', attrs: { content: '巡逻任务、状态回传', freq: '1 Hz', latency: '≤500 ms' } });
    L(nav, post, { kind: 'data', label: '链路保障', attrs: { content: '链路状态、频谱资源', freq: '0.2 Hz' } });
    L(air, sea, { kind: 'data', label: '目标指示', attrs: { content: '目标指示', freq: '事件触发', latency: '≤1 s' } });
    L(sea, fast, { kind: 'data', label: '处置请求', attrs: { content: '目标位置、处置请求', freq: '事件触发', latency: '≤2 s' } });
    L(gnd, fast, { kind: 'data', label: '协同处置', attrs: { content: '目标位置、协同处置信息', freq: '事件触发', latency: '≤2 s' } });
    foot(NOTE('OV-2') + '　需求线标注交换的资源（信息）类别。');
    beautify(d.pages.root);
  }, { base: '现有节点', new: '新增节点', key: '核心节点' });

  /* =========================================================== OV-5b */
  const ov5b = define('std-ov5b', 'OV-5b', 'OV-5b 作战活动模型', '按执行者分泳道的发现→识别→判定→处置→评估活动流，含判定分支', (d, T) => {
    const { N, L, decor } = T;
    const BW = 1260, LH = 118, TW = 110, cx = i => 150 + 62 + i * 126;
    const band = N({ type: 'band', text: '巡逻处置活动', x: 0, y: 0, w: BW, h: 6 + 4 * (LH + 6) });
    const defs = [['无人巡逻节点', '空地水无人平台，承担发现与持续监视'], ['情报保障节点', '目标融合识别与研判'], ['边海防指挥中心', '威胁判定、指令下达与评估'], ['快速处置力量', '抵近处置与回报']];
    const lanes = defs.map(([t, desc], i) => N(Object.assign({ type: 'lane', text: t, parent: band.id, x: 40, y: 6 + i * (LH + 6), w: BW - 46, h: LH, titleW: TW }, E('performer', desc))));
    const S = (li, ci, text, o = {}) => {
      const big = o.type === 'diamond', w = o.w || (big ? 130 : 112), h = o.h || (big ? 72 : 48);
      return N(Object.assign({ type: 'rect', text, size: 12, parent: lanes[li].id, w, h, x: cx(ci) - w / 2, y: lanes[li].y + (LH - h) / 2 }, o));
    };
    const act = (desc) => E('op_activity', desc);
    const st = S(0, 0, '开始', Object.assign({ type: 'ellipse', w: 64, h: 36, bold: true, attrs: { desc: '起止' } }));
    const a1 = S(0, 1, '巡逻探测发现目标', act('按航线巡逻，探测并发现异常目标'));
    const a2 = S(1, 2, '目标识别分类', act('多源融合，识别目标属性与意图'));
    const dc = S(2, 3, '是否构成威胁', Object.assign({ type: 'diamond', status: 'key' }, act('依据规则与指挥员判断确定是否处置')));
    const a3 = S(2, 4, '下达处置指令', act('选定处置方式并授权'));
    const a4 = S(3, 5, '抵近处置', Object.assign({ status: 'new' }, act('拦截、驱离或抓捕')));
    const a5 = S(2, 6, '处置效果评估', act('评估处置结果并归档'));
    const a6 = S(0, 4, '持续监视', act('不构成威胁时转入跟踪监视'));
    const en = S(2, 7, '结束', Object.assign({ type: 'ellipse', w: 64, h: 36, bold: true, attrs: { desc: '起止' } }));
    L(st, a1, { kind: 'plain', attrs: { content: '任务启动' } });
    L(a1, a2, { label: '目标航迹', attrs: { content: '目标航迹、图像' } });
    L(a2, dc, { label: '识别结果', attrs: { content: '目标属性、置信度' } });
    L(dc, a3, { kind: 'ctrl', label: '是', attrs: { content: '威胁判定结论：是' } });
    L(dc, a6, { kind: 'ctrl', label: '否', attrs: { content: '威胁判定结论：否' } });
    L(a6, a1, { kind: 'plain', label: '继续巡逻', attrs: { content: '继续巡逻' } });
    L(a3, a4, { kind: 'ctrl', label: '处置指令', attrs: { content: '处置指令' } });
    L(a4, a5, { label: '处置回报', attrs: { content: '处置结果回报' } });
    L(a5, en, { kind: 'plain', attrs: { content: '评估结论' } });
    decor(0, BW, 0, band.h, '边海防巡逻处置 · 作战活动模型（OV-5b）', '发现→识别→判定→处置→评估，活动按执行者分泳道，判定节点区分处置与持续监视', NOTE('OV-5b') + '　泳道为作战执行者，椭圆为起止。');
  }, { base: '常规活动', new: '新增活动', key: '判定节点' });

  /* =========================================================== SV-1 */
  const sv1 = define('std-sv1', 'SV-1', 'SV-1 系统接口描述', '按作战节点分组的系统／子系统及其接口（协议、介质、频度、时延、密级）', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('边海防无人化巡逻 · 系统接口描述（SV-1）', '系统按作战节点分组，接口标注交换内容、协议、介质、频度与时延要求');
    const W = 1300, H = { h: 96 };
    const sy = (key, t, desc, x) => [key, t, Object.assign(E('system', desc), x || {})];
    const b1 = N(Object.assign({ type: 'band', text: '指挥中心', w: W }, E('op_node', '边海防指挥中心：指挥决策与态势研判')));
    const [plan, c2, fusion, gws] = equips(b1, [
      sy('mission_planning', '任务规划系统', '巡逻航线规划与任务分配'),
      sy('cmd_software', '指挥控制系统', '任务下达与人在环上监督', { status: 'key' }),
      sy('sit_3d', '态势融合系统', '多源目标融合与态势生成'),
      sy('sat_station', '卫通地面站', '卫星通信地面接入')], H);
    const b2 = N(Object.assign({ type: 'band', text: '管控站', w: W }, E('op_node', '前沿管控站：前沿管控与链路接入')));
    const [tower, term, mesh, satt] = equips(b2, [
      sy('cuas_mast', '光电监控塔', '固定点位光电监视'),
      sy('console', '管控终端系统', '站内任务监控与处置协调'),
      sy('comm_tower', '自组网基站', '前沿自组网接入'),
      sy('satcom_otm', '卫通终端', '卫通链路站端接入')], H);
    const b3 = N(Object.assign({ type: 'band', text: '空中巡逻', w: W }, E('op_node', '空中巡逻节点：无人机巡查与中继')));
    const [nest, uav, tdl, relay] = equips(b3, [
      sy('drone_nest', '无人机机巢系统', '起降、充换电与值守'),
      sy('uav_quad', '巡查无人机系统', '低空巡查与载荷采集'),
      ['datalink', '机载数据链终端', E('subsystem', '巡查无人机机载数据链终端')],
      sy('uav_tethered', '系留中继系统', '系留无人机通信中继', { status: 'new' })], H);
    const b4 = N(Object.assign({ type: 'band', text: '地水巡逻', w: W }, E('op_node', '地面与水面巡逻节点：无人车、无人艇与岸基雷达')));
    const [rad, usv, ugv, dog] = equips(b4, [
      sy('radar_station', '岸基雷达系统', '海域目标探测'),
      sy('usv', '巡逻无人艇系统', '近岸水域巡逻'),
      sy('ugv', '巡逻无人车系统', '沿边道路自主巡逻'),
      sy('robodog', '四足机器人系统', '复杂地形近距侦察')], H);
    const I = (a, b, label, at, o) => L(a, b, Object.assign({ kind: 'data', dir: 'both', label }, o || {}, { attrs: Object.assign({ content: label, security: '内部' }, at) }));
    I(plan, c2, '任务方案', { protocol: '以太网 TCP', medium: '光纤', freq: '事件触发', latency: '≤1 s' }, { kind: 'wired' });
    I(c2, fusion, '融合态势', { protocol: 'TCP/IP 自定义报文', medium: '光纤', freq: '1 Hz', latency: '≤100 ms' }, { kind: 'wired' });
    I(fusion, gws, '遥控遥测', { protocol: 'TCP/IP 自定义报文', medium: '光纤', freq: '1 Hz', latency: '≤100 ms' }, { kind: 'wired' });
    I(c2, term, '指令／状态', { protocol: 'TCP/IP 自定义报文', medium: '光纤', freq: '1 Hz', latency: '≤100 ms' }, { kind: 'wired' });
    I(gws, satt, '卫通回传', { protocol: 'Link 数据链', medium: '卫通', freq: '1 Hz', latency: '≤500 ms' }, { kind: 'sat' });
    I(tower, term, '图像与告警', { protocol: 'UDP 组播', medium: '光纤', freq: '25 帧/s', latency: '≤200 ms' }, { kind: 'wired', dir: 'one' });
    I(term, mesh, '链路接入', { protocol: '以太网 TCP', medium: '光纤', freq: '1 Hz', latency: '≤50 ms' }, { kind: 'wired' });
    I(mesh, satt, '链路汇接', { protocol: '以太网 TCP', medium: '光纤', freq: '1 Hz', latency: '≤50 ms' }, { kind: 'wired' });
    I(mesh, tdl, '测控与图传', { protocol: 'Link 数据链', medium: '自组网', freq: '10 Hz', latency: '≤100 ms' }, { kind: 'radio' });
    I(nest, uav, '起降控制', { protocol: 'RS-422', medium: '有线', freq: '10 Hz', latency: '≤20 ms' }, { kind: 'wired' });
    I(uav, tdl, '机载总线', { protocol: 'RS-422', medium: '机载电缆', freq: '10 Hz', latency: '≤20 ms' }, { kind: 'wired' });
    I(tdl, relay, '中继转发', { protocol: 'Link 数据链', medium: '超短波', freq: '5 Hz', latency: '≤200 ms' }, { kind: 'radio' });
    I(relay, dog, '中继接入', { protocol: 'Link 数据链', medium: '超短波', freq: '5 Hz', latency: '≤200 ms' }, { kind: 'radio' });
    I(rad, usv, '目标航迹', { protocol: 'UDP 组播', medium: '4G／5G', freq: '1 Hz', latency: '≤500 ms' }, { kind: 'radio', dir: 'one' });
    I(usv, ugv, '短报文告警', { protocol: '北斗短报文', medium: '北斗', freq: '事件触发', latency: '≤10 s', security: '秘密' }, { kind: 'sat' });
    I(ugv, dog, '协同巡逻', { protocol: 'Link 数据链', medium: '自组网', freq: '5 Hz', latency: '≤200 ms' }, { kind: 'radio' });
    foot(NOTE('SV-1') + '　接口属性：协议、介质、频度、时延、密级。');
    beautify(d.pages.root);
  }, { base: '现有系统', new: '新增系统', key: '核心系统' });

  /* =========================================================== SV-4 */
  const sv4 = define('std-sv4', 'SV-4', 'SV-4 系统功能描述', '系统分组内的系统功能及功能间数据流（感知、融合、指控、处置）', (d, T) => {
    const { N, L, decor } = T;
    const GW = 250, GAP = 150, TH = 26, KH = 40, KG = 26, x0 = 0, y0 = 0, GH = TH + 14 + 3 * KH + 2 * KG + 14;
    const gx = i => x0 + i * (GW + GAP);
    const mkG = (i, t, desc, fs) => {
      const g = N(Object.assign({ type: 'group', text: t, x: gx(i), y: y0, w: GW, h: GH }, E('system', desc)));
      return fs.map(([n, d2], r) => N(Object.assign({ type: 'round', text: n, size: 12, parent: g.id, x: gx(i) + 14, y: y0 + TH + 14 + r * (KH + KG), w: GW - 28, h: KH }, E('sys_function', d2))));
    };
    const [a1, a2, a3] = mkG(0, '巡查无人机系统', '低空巡查平台', [['航线飞行', '按任务航线自主飞行'], ['光电探测', '可见光／红外探测'], ['目标检测', '机上目标检测']]);
    const [b1, b2, b3] = mkG(1, '态势融合系统', '多源信息融合', [['威胁评估', '越界意图研判'], ['目标融合', '航迹关联与融合'], ['数据接入', '多源数据接入与校时']]);
    const [c1, c2, c3] = mkG(2, '指挥控制系统', '任务指挥与处置控制', [['任务规划', '航线与任务分配'], ['指令下达', '指令生成与分发'], ['处置控制', '处置授权与效果评估']]);
    const [d1, d2, d3] = mkG(3, '拦截无人艇系统', '水面拦截处置平台', [['指令接收', '接收并解析处置指令'], ['自主航行', '自主航行与避碰'], ['拦截处置', '拦截与驱离']]);
    L(a1, a2, { label: '', attrs: { content: '飞行位姿与时统' } });
    L(a2, a3, { label: '', attrs: { content: '光电图像流' } });
    L(a3, b3, { label: '检测结果', attrs: { content: '目标检测结果', freq: '10 Hz' } });
    L(b3, b2, { label: '', attrs: { content: '多源航迹' } });
    L(b2, b1, { label: '', attrs: { content: '综合航迹' } });
    L(b1, c2, { kind: 'ctrl', label: '威胁告警', attrs: { content: '威胁等级、告警' } });
    L(c1, c2, { kind: 'ctrl', label: '', attrs: { content: '任务方案' } });
    L(c2, d1, { kind: 'ctrl', label: '处置指令', attrs: { content: '处置指令' } });
    L(d1, d2, { kind: 'ctrl', label: '', attrs: { content: '航行任务' } });
    L(d2, d3, { kind: 'ctrl', label: '', attrs: { content: '拦截引导' } });
    L(d3, c3, { label: '处置回报', attrs: { content: '处置结果回报' } });
    const W = 4 * GW + 3 * GAP;
    decor(0, W, 0, GH, '边海防无人化巡逻 · 系统功能描述（SV-4）', '各系统分解为系统功能，功能之间以数据流连接，形成发现—研判—处置闭环', NOTE('SV-4') + '　外框为系统，框内为系统功能。');
  }, { base: '现有功能', new: '新增功能', key: '关键功能' });

  /* =========================================================== 信息系统架构（TOGAF／4A） */
  const IT_GROUP = '信息系统架构';
  const IT_META = code => ({ project: '边海防无人化巡逻体系·指控信息系统', drawingNo: code, classification: '内部' });
  const ITNOTE = v => `说明：依据 TOGAF 架构开发方法及信息系统总体设计惯例绘制（${v}），案例为虚构示例；元素与连线按阅读顺序自动编号，属性见检查器，题签数据取自文档信息。`;
  const defIT = (id, view, name, desc, fn, labels, code) => define(id, view, name, desc, fn, labels, IT_GROUP, IT_META(code));
  const X = (etype, desc, extra) => ({ etype, attrs: Object.assign({ desc, owner: '总体设计组' }, extra || {}) });
  /* 右侧竖栏（如“安全保障体系”）：一键美化不移动顶层子容器，按分组带的上下沿对齐 */
  function sideColumn(p, g, kidsH, gap) {
    const bands = p.nodes.filter(n => n.type === 'band' && !n.parent);
    const top = Math.min(...bands.map(b => b.y)), bot = Math.max(...bands.map(b => b.y + b.h)), right = Math.max(...bands.map(b => b.x + b.w));
    g.x = snapv(right + (gap || 16)); g.y = top; g.h = snapv(bot - top);
    const ks = p.nodes.filter(n => n.parent === g.id), n = ks.length, room = g.h - GROUP_TH - 16, step = room / n;
    ks.forEach((k, i) => { k.x = g.x + 12; k.w = snapv(g.w - 24); k.h = kidsH; k.y = snapv(g.y + GROUP_TH + 8 + i * step + (step - kidsH) / 2); });
  }

  /* --------------------------------------------------- 业务架构图 */
  const itBiz = defIT('it-biz', 'BIZ', '业务架构图 · 巡逻任务全流程', '巡逻任务全流程四个业务域：业务能力分解为流程／活动，标注业务角色、业务对象与业务流', (d, T) => {
    const { N, L, head, foot } = T;
    head('指控信息系统 · 业务架构图', '巡逻任务全流程：任务筹划 → 巡逻实施 → 处置联动 → 评估保障，业务域分解为业务能力与流程／活动');
    const W = 1440;
    const dom = (t, desc, o) => N(Object.assign({ type: 'band', text: t, w: W }, X('biz_domain', desc), o || {}));
    const role = (b, t, ico, desc) => N(Object.assign({ type: 'round', text: t, icon: ic(ico, 'operator'), parent: b.id, size: 12 }, X('biz_role', desc)));
    const obj = (b, t, desc) => N(Object.assign({ type: 'document', text: t, parent: b.id, size: 12 }, X('biz_object', desc)));
    const cap = (b, t, desc, procs, o) => {
      const g = N(Object.assign({ type: 'group', text: t, parent: b.id }, X('biz_capability', desc), o || {}));
      procs.forEach(pp => { const [pt, pd, po] = Array.isArray(pp) ? pp : [pp, pp]; N(Object.assign({ type: 'rect', text: pt, parent: g.id, size: 12 }, X('biz_process', pd), po || {})); });
      return g;
    };
    const b1 = dom('任务筹划', '巡逻需求受理、计划编制与资源调度');
    role(b1, '任务规划员', 'staff_plan', '编制巡逻方案、分配力量');
    const c11 = cap(b1, '需求受理', '受理上级下达与前沿上报的巡逻需求', ['需求登记', '任务分级']);
    const c12 = cap(b1, '巡逻计划编制', '生成巡逻方案并报批', ['航线规划', '力量分配', ['方案审批', '值班指挥员审批', { status: 'key' }]]);
    const c13 = cap(b1, '资源调度', '平台、频谱与空域资源协调', ['平台调度', ['空域频谱协调', '空域申请与用频协调', { status: 'new' }]]);
    const o1 = obj(b1, '巡逻方案', '经审批的巡逻方案（航线、力量、时段）');
    const b2 = dom('巡逻实施', '无人平台按方案执行巡逻并发现识别目标');
    role(b2, '平台操作员', 'drone_pilot', '监控平台状态，必要时接管');
    const c21 = cap(b2, '无人平台巡逻', '空地水无人平台自主巡逻', ['自主起降', '航线巡逻', '状态监控']);
    const c22 = cap(b2, '目标发现识别', '多源探测、目标识别与情报研判', ['异常发现', '目标识别', ['情报研判', '情报分析员综合研判', { status: 'key' }]]);
    const o2 = obj(b2, '目标情报', '目标位置、属性与置信度');
    const b3 = dom('处置联动', '威胁判定、处置决策与多部门联动');
    role(b3, '值班指挥员', 'commander', '威胁判定与处置授权');
    const c31 = cap(b3, '威胁判定', '依据规则与研判结论判定威胁等级', ['威胁评估', ['处置决策', '人在环上授权', { status: 'key' }]]);
    const c32 = cap(b3, '联动处置', '指令下达与无人／有人力量协同处置', ['指令下达', ['拦截驱离', '无人艇／无人机拦截驱离', { status: 'new' }], '协同抓捕']);
    const o3 = obj(b3, '处置指令', '处置方式、目标与授权信息');
    const b4 = dom('评估保障', '处置效果评估、归档复盘与装备保障');
    role(b4, '保障工程师', 'maintainer', '装备健康管理与维修保养');
    const c41 = cap(b4, '效果评估', '评估处置结果并归档复盘', ['处置评估', '归档复盘']);
    const c42 = cap(b4, '装备保障', '装备健康管理与维修', ['健康管理', '维修保养', ['备件管理', '备件需求预测', { status: 'new' }]]);
    const o4 = obj(b4, '评估报告', '处置评估结论与改进建议');
    L(c12, c21, { label: '巡逻方案', attrs: { content: '巡逻方案', freq: '每日／临时' } });
    L(c13, c21, { kind: 'ctrl', label: '调度指令', attrs: { content: '平台调度指令', freq: '事件触发' } });
    L(c22, c31, { label: '目标情报', attrs: { content: '目标情报', freq: '事件触发' } });
    L(c32, c41, { label: '处置结果', attrs: { content: '处置结果回报', freq: '事件触发' } });
    L(c32, c42, { kind: 'plain', label: '保障需求', attrs: { content: '装备保障需求', freq: '每次处置' } });
    foot(ITNOTE('业务架构图') + '　分组带为业务域，子容器为业务能力，框内为业务流程／活动；左侧为业务角色，右侧文档形状为业务对象。');
    beautify(d.pages.root);
  }, { base: '现有业务', new: '新增业务', key: '关键环节' }, 'ZKXT-YW-01');

  /* --------------------------------------------------- 应用架构图 */
  const itApp = defIT('it-app', 'APP', '应用架构图 · 指控信息系统', '外部系统、业务应用与应用支撑服务三层：指挥控制、态势、任务规划、装备管理、运维五大应用及统一门户', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('指控信息系统 · 应用架构图', '统一门户承载五大业务应用，共用应用支撑服务，经集成接口与外部系统互联');
    const W = 1440;
    const be = N({ type: 'band', text: '外部系统', w: W });
    const ex = (k, f, t, desc) => [[k, f], t, X('ext_system', desc)];
    const [up, police, bd, wx, gcs] = equips(be, [
      ex('command_center', 'cmd_hall', '上级指挥信息系统', '上级指挥机构指挥信息系统'),
      ex('cmd_army', 'command_post', '公安边检协同系统', '公安、边检部门协同处置平台'),
      ex('beidou', 'satellite', '北斗位置服务', '北斗定位与短报文服务'),
      ex('weather', 'weather_radar', '气象海洋服务', '气象、海况预报服务'),
      ex('gcs', 'console', '无人平台地面站', '各型无人平台测控地面站')], { w: 120, h: 92 });
    const ba = N({ type: 'band', text: '业务应用', w: W });
    const app = (t, desc, mods, o) => { const g = N(Object.assign({ type: 'group', text: t, parent: ba.id }, X('app_system', desc), o || {})); return [g, mods.map(m => N(Object.assign({ type: 'rect', text: m, parent: g.id, size: 12 }, X('app_module', m))))]; };
    const [portal] = app('统一门户', '统一入口、单点登录与工作台', ['指挥工作台', '移动巡逻端', '大屏展示']);
    const [c2] = app('指挥控制系统', '任务下达、指令跟踪与人在环上监督', ['任务下达', '指令跟踪', '人在环监督'], { status: 'key' });
    const [sit] = app('态势感知系统', '多源目标融合与综合态势生成', ['目标融合', '态势生成', '告警研判']);
    const [plan] = app('任务规划系统', '巡逻航线规划与力量分配', ['航线规划', '力量分配', '方案推演']);
    const [eqp] = app('装备管理系统', '无人装备台账与健康管理', ['装备台账', '健康管理', '维修保障'], { status: 'new' });
    const [ops] = app('运维管理系统', '系统监控、配置与日志管理', ['监控告警', '配置管理', '日志管理']);
    const bs = N({ type: 'band', text: '支撑服务', w: W });
    const sv = (k, f, t, desc, o) => [[k, f], t, Object.assign(X('app_service', desc), o || {})];
    const [auth, mq, gis, vid, wf, dsv] = equips(bs, [
      sv('identity', 'security', '统一认证服务', '统一身份认证与单点登录'),
      sv('it_mq', 'message_bus', '消息服务', '消息发布订阅与可靠投递'),
      sv('map', 'spatiotemporal', 'GIS 地图服务', '二三维地图与空间分析'),
      sv('video', 'camera', '视频服务', '视频接入、转发与回放'),
      sv('workflow', 'scheduler', '工作流引擎', '审批与业务流程编排'),
      sv('it_data_service', 'api', '数据服务', '统一数据访问接口', { status: 'new' })], { w: 120, h: 92 });
    const I = (a, b, content, protocol, o, at) => L(a, b, Object.assign({ label: content }, o || {}, { attrs: Object.assign({ content, protocol }, at || {}) }));
    I(up, c2, '上级指令', '专用接口 / XML 报文', { kind: 'ctrl', dir: 'both' }, { freq: '事件触发', security: '内部' });
    I(police, sit, '协同通报', 'REST / HTTPS', { dir: 'both' }, { freq: '事件触发' });
    I(wx, plan, '气象海况', 'REST / HTTPS', {}, { freq: '1 h' });
    I(bd, sit, '位置报告', '北斗短报文', { kind: 'sat' }, { freq: '1 min' });
    I(gcs, eqp, '遥测数据', 'TCP/IP 自定义报文', { dir: 'one' }, { freq: '1 Hz', latency: '≤1 s' });
    I(portal, auth, '单点登录', 'OAuth 2.0', { kind: 'plain' });
    I(c2, mq, '指令消息', '消息队列', {}, { latency: '≤200 ms' });
    I(sit, gis, '地图服务', 'WMTS / REST', { kind: 'plain' });
    I(sit, vid, '视频流', 'RTSP / GB/T 28181', {}, { latency: '≤500 ms' });
    I(eqp, dsv, '装备数据', 'REST / HTTPS', { kind: 'plain' });
    I(ops, dsv, '运行日志', 'REST / HTTPS', { kind: 'plain' });
    I(plan, wf, '方案审批', 'REST / HTTPS', { kind: 'plain' });
    foot(ITNOTE('应用架构图') + '　子容器为应用系统，框内为应用模块；集成连线标注集成内容，集成方式／协议见属性与「集成清单」。');
    beautify(d.pages.root);
  }, { base: '现有应用', new: '新建应用', key: '核心应用' }, 'ZKXT-YY-01');

  /* --------------------------------------------------- 数据架构图 */
  const itData = defIT('it-data', 'DATA', '数据架构图 · 采集治理服务', '采集层 → 四大数据域 → 存储层（ODS／DW／ADS） → 服务层的数据流，标注数据对象与交换方式', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('指控信息系统 · 数据架构图', '数据采集 → 数据资产（感知、目标、任务、装备四个数据域）→ 分层存储（ODS → DW → ADS）→ 数据服务');
    const W = 1440;
    const bA = N({ type: 'band', text: '采集层', w: W });
    const pr = (k, f, t, desc, o) => [[k, f], t, Object.assign(X('data_proc', desc), o || {})];
    const [cRad, cInt, cTask, cTel] = equips(bA, [
      pr('it_stream', 'radar', '雷达／光电实时采集', '点迹、航迹与视频流实时接入'),
      pr('it_etl', 'workflow', '情报数据汇聚', '情报研判与协同单位通报数据汇聚'),
      pr('it_etl', 'workflow', '任务数据同步', '任务系统业务数据增量同步'),
      pr('it_stream', 'datalink', '平台遥测接入', '无人平台遥测与装备状态接入')], { w: 128, h: 88 });
    /* 名称以“层”结尾的分组带只作分层排版，不是数据域；带内子容器才是数据域 */
    const bB = N({ type: 'band', text: '资产层', w: W });
    const dd = (t, desc, ents, o) => { const g = N(Object.assign({ type: 'group', text: t, parent: bB.id }, X('data_domain', desc), o || {})); ents.forEach(e => { const [et, eo] = Array.isArray(e) ? e : [e, {}]; N(Object.assign({ type: 'rect', text: et, parent: g.id, size: 12 }, X('data_entity', et), eo)); }); return g; };
    const dSense = dd('感知数据域', '雷达、光电、遥测等原始感知数据', ['雷达点迹', '光电视频', '平台遥测']);
    const dTgt = dd('目标数据域', '目标航迹、档案与识别结果', ['目标航迹', '目标档案', ['识别结果', { status: 'key' }]], { status: 'key' });
    const dTask = dd('任务数据域', '巡逻任务、处置记录与评估', ['巡逻任务', '处置记录', '评估报告']);
    const dEq = dd('装备数据域', '装备台账、健康状态与维修记录', ['装备台账', ['健康状态', { status: 'new' }], '维修记录']);
    const bC = N({ type: 'band', text: '存储层', w: W });
    const st = (k, f, t, desc, o) => [[k, f], t, Object.assign(X('data_store', desc), o || {})];
    const [obs, ods, dw, ads, tsdb] = equips(bC, [
      st('it_object_store', 'storage', '对象存储', '视频、图像等非结构化数据'),
      st('database', 'storage', '贴源库 ODS', '原始数据贴源存储，保留 30 天'),
      st('it_dw', 'database', '数据仓库 DW', '按主题清洗整合的明细与汇总数据', { status: 'key' }),
      st('it_dw', 'database', '数据集市 ADS', '面向应用的指标与专题数据'),
      st('it_tsdb', 'database', '时序库', '遥测与装备状态时序数据')], { w: 128, h: 88 });
    const bD = N({ type: 'band', text: '服务层', w: W });
    const [sQ, sStat, sSub] = equips(bD, [
      pr('it_data_service', 'api', '目标查询服务', '目标档案与航迹查询接口'),
      pr('it_batch', 'algorithm', '统计分析服务', '巡逻与处置统计分析'),
      pr('it_stream', 'message_bus', '态势订阅服务', '实时态势数据订阅推送', { status: 'new' })], { w: 128, h: 88 });
    const F = (a, b, content, protocol, freq, o) => L(a, b, Object.assign({ label: content }, o || {}, { attrs: { content, protocol, freq } }));
    F(cRad, dSense, '点迹／视频', '流式接入', '实时');
    F(cInt, dTgt, '情报通报', '消息订阅', '事件触发');
    F(cTask, dTask, '任务记录', 'CDC 增量', '准实时');
    F(cTel, dEq, '遥测帧', '流式接入', '1 Hz');
    F(dSense, ods, '原始点迹', '批量入库', '5 min');
    F(dTgt, dw, '目标主题', '清洗整合', '准实时');
    F(dTask, ads, '任务统计', '汇总加工', 'T+1');
    F(dEq, tsdb, '状态时序', '流式写入', '1 Hz');
    F(ods, dw, '明细数据', 'ETL 清洗', '5 min');
    F(dw, ads, '指标数据', '汇总加工', 'T+1');
    F(ads, sStat, '统计指标', 'SQL 查询', '按需');
    F(dw, sQ, '目标档案', 'JDBC 查询', '按需');
    F(tsdb, sSub, '实时态势', '消息推送', '实时');
    F(dSense, obs, '视频图像', '对象写入', '实时');
    foot(ITNOTE('数据架构图') + '　带名以“层”结尾者为处理分层；子容器为数据域，框内为数据实体／主题；连线为数据流，标注数据对象。');
    beautify(d.pages.root);
  }, { base: '现有', new: '新建', key: '核心数据' }, 'ZKXT-SJ-01');

  /* --------------------------------------------------- 技术架构图 */
  const itTech = defIT('it-tech', 'TECH', '技术架构图 · 分层技术栈', '基础设施层、平台层、中间件层、应用支撑层四层技术栈及纵向安全保障体系', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('指控信息系统 · 技术架构图', '自主可控分层技术栈：基础设施 → 平台 → 中间件 → 应用支撑，安全保障体系贯穿各层');
    const W = 1260;
    const lay = (t, desc) => N(Object.assign({ type: 'band', text: t, w: W }, X('tech_layer', desc)));
    const tc = (k, f, t, desc, o) => [[k, f], t, Object.assign(X('tech_component', desc), o || {})];
    const b1 = lay('应用支撑层', '面向业务应用的公共技术能力');
    const [gw, gisE, vidE, ai, rule] = equips(b1, [
      tc('gateway', 'api', 'API 网关', '服务路由、限流与鉴权'),
      tc('map', 'spatiotemporal', 'GIS 引擎', '二三维地图渲染与空间分析'),
      tc('video', 'camera', '视频解析引擎', '视频解码、转码与结构化'),
      tc('algorithm', 'llm', 'AI 识别算法', '目标检测与识别模型推理', { status: 'new' }),
      tc('workflow', 'scheduler', '规则引擎', '威胁判定规则执行')], { w: 120, h: 88 });
    const b2 = lay('中间件层', '应用运行所需的通用中间件');
    const pl = (k, f, t, desc, o) => [[k, f], t, Object.assign(X('platform', desc), o || {})];
    const [ms, mw, mq, cache] = equips(b2, [
      pl('it_microservice', 'app', '微服务框架', '服务注册发现、配置中心'),
      pl('it_middleware', 'server', '应用中间件', '国产应用服务器'),
      pl('it_mq', 'message_bus', '消息队列', '分布式消息队列，三节点集群'),
      pl('it_cache', 'database', '分布式缓存', '内存缓存，主从＋哨兵')], { w: 120, h: 88 });
    const b3 = lay('平台层', '容器云、大数据与数据库平台');
    const plat = (t, desc, comps, o) => { const g = N(Object.assign({ type: 'group', text: t, parent: b3.id }, X('platform', desc), o || {})); comps.forEach(c => N(Object.assign({ type: 'rect', text: c, parent: g.id, size: 12 }, X('tech_component', c)))); return g; };
    const kube = plat('容器云平台', '容器编排、镜像与持续交付', ['容器编排', '镜像仓库', '持续集成']);
    const bigd = plat('大数据平台', '流批一体计算与湖仓存储', ['流计算', '批处理', '湖仓存储'], { status: 'new' });
    const dbp = plat('数据库平台', '国产关系库、时序库与图数据库', ['达梦数据库', '时序数据库', '图数据库'], { status: 'key' });
    const b4 = lay('基础设施层', '国产化计算、存储、网络与操作系统');
    const inf = (k, f, t, desc, o) => [[k, f], t, Object.assign(X('infra', desc), o || {})];
    const [srv, gpu, net, stor, os] = equips(b4, [
      inf('it_xc_server', 'server', '信创服务器集群', '国产 CPU 服务器 ×24'),
      inf('gpu', 'server', 'GPU 计算节点', '推理加速卡 ×8', { status: 'new' }),
      inf('it_core_switch', 'switch', '核心网络', '万兆核心＋千兆接入'),
      inf('storage', 'database', '分布式存储', '全闪存＋大容量存储 500 TB'),
      inf('it_os', 'server', '国产操作系统', '麒麟／统信服务器操作系统')], { w: 120, h: 88 });
    const sec = N(Object.assign({ type: 'group', text: '安全保障体系', w: 170, h: 400 }, X('tech_layer', '贯穿各层的安全技术措施')));
    ['统一身份认证', '密码服务', '安全审计', '主机加固', '数据防泄漏'].forEach(t => N(Object.assign({ type: 'rect', text: t, parent: sec.id, size: 12 }, X('tech_component', t))));
    const D = (a, b, content, protocol, o) => L(a, b, Object.assign({ kind: 'plain', label: '' }, o || {}, { attrs: { content, protocol } }));
    D(gw, ms, '服务注册', 'HTTP');
    D(gisE, mw, '部署于', 'Servlet');
    D(ai, mq, '识别结果发布', 'MQ 协议');
    D(rule, cache, '规则缓存', 'RESP');
    D(ms, kube, '容器化部署', 'CRI');
    D(mw, kube, '容器化部署', 'CRI');
    D(mq, bigd, '数据接入', 'MQ 协议');
    D(kube, srv, '运行于', '—');
    D(kube, gpu, 'GPU 调度', 'Device Plugin');
    D(bigd, stor, '存储于', 'S3 / HDFS');
    D(dbp, stor, '存储于', 'iSCSI');
    foot(ITNOTE('技术架构图') + '　分组带为技术层，层内子容器为平台，框内为技术组件；右侧为贯穿各层的安全保障体系。');
    beautify(d.pages.root);
    sideColumn(d.pages.root, sec, 40);
  }, { base: '现有技术', new: '新引入', key: '关键平台' }, 'ZKXT-JS-01');

  /* --------------------------------------------------- 部署架构图 */
  const itDeploy = defIT('it-deploy', 'DEPLOY', '部署架构图 · 分区部署', '互联网区、DMZ、业务专网区、涉密内网区分区部署，跨区连接经防火墙、网闸等边界设备，节点标注规格、系统、地址', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('指控信息系统 · 部署架构图', '按安全域分区部署：互联网区 → DMZ → 业务专网区 → 涉密内网区，跨区连接一律经防火墙／网闸等边界设备');
    const W = 1440;
    const zone = (t, level, desc) => N(Object.assign({ type: 'band', text: t, w: W }, X('zone', desc, { level })));
    /* 区域内的“层”只作排版（不是元素）；高度留足，层间连线有标注空间 */
    const row = (z, t, h) => N({ type: 'lane', text: t, parent: z.id, h, titleW: 84 });
    const dev = (key, fb, t, desc, extra, o) => [[key, fb], t, Object.assign(X('net_device', desc, extra), o || {})];
    const host = (key, fb, t, desc, extra, o) => [[key, fb], t, Object.assign(X('deploy_node', desc, extra), o || {})];
    const nodeG = (par, t, desc, extra, units, o) => {
      const g = N(Object.assign({ type: 'group', text: t, parent: par.id }, X('deploy_node', desc, extra), o || {}));
      units.forEach(([ut, uc, uo]) => N(Object.assign({ type: 'rect', text: ut, parent: g.id, size: 12 }, X('deploy_unit', ut, { count: uc }), uo || {})));
      return g;
    };
    /* 互联网区 */
    const z1 = zone('互联网区', '等保二级', '移动巡逻终端经运营商 APN 专网接入');
    const r1 = row(z1, '接入', 124);
    const [fw1, rtr, term] = equips(r1, [
      dev('firewall', 'security', '外网防火墙', '外网边界访问控制、抗 DDoS', { spec: '下一代防火墙', ip: '203.0.113.2', count: '2（主备）' }),
      dev('router', 'gateway', '边界路由器', '运营商专线／APN 接入', { spec: '万兆路由器', ip: '203.0.113.1', count: '2（主备）' }),
      host('tablet', 'laptop', '移动巡逻终端', '加固平板，安装移动巡逻端', { spec: '加固平板 8 核／8 GB', os: '国产移动操作系统', ip: 'APN 动态地址', count: '120' })]);
    /* DMZ */
    const z2 = zone('DMZ 区', '等保三级', '对外服务发布区');
    const r2 = row(z2, '服务发布', 124);
    const [waf, lb] = equips(r2, [
      dev('it_waf', 'firewall', 'Web 应用防火墙', 'Web 攻击防护', { spec: 'WAF 硬件', ip: '172.16.10.5', count: '2' }),
      dev('it_lb', 'switch', '负载均衡', '服务入口负载分担', { spec: '应用交付控制器', ip: '172.16.10.10（VIP）', count: '2' })]);
    const web = nodeG(r2, '门户服务器', '对外门户与移动接入服务', { spec: '16 核／64 GB／1 TB', os: '麒麟 V10', ip: '172.16.10.21-22', count: '2' }, [['门户前端', '2'], ['移动接入网关', '2']]);
    const [vpn] = equips(r2, [dev('it_vpn', 'gateway', 'VPN 网关', '移动终端国密 SSL VPN 接入', { spec: '国密 SSL VPN', ip: '172.16.10.30', count: '2' })]);
    /* 业务专网区 */
    const z3 = zone('业务专网区', '等保三级', '指控信息系统主体部署区');
    const r3a = row(z3, '网络', 140);
    const [fw2, core, bas] = equips(r3a, [
      dev('firewall', 'security', '内网防火墙', 'DMZ 与业务专网之间访问控制', { spec: '下一代防火墙', ip: '10.20.0.1', count: '2（主备）' }),
      dev('it_core_switch', 'switch', '核心交换机', '业务专网核心交换', { spec: '万兆核心交换机', ip: '10.20.0.0/16', count: '2（堆叠）' }, { status: 'key' }),
      dev('it_bastion', 'security', '运维堡垒机', '运维访问统一审计', { spec: '堡垒机', ip: '10.20.9.5', count: '1' })]);
    const r3b = row(z3, '计算与存储', 96);
    const k8s = nodeG(r3b, '容器云集群', '业务应用容器化部署', { spec: '3 管理＋8 工作节点，64 核／256 GB', os: '麒麟 V10', ip: '10.20.1.0/24', count: '11' }, [['指挥控制服务', '3'], ['态势感知服务', '3'], ['任务规划服务', '2'], ['装备管理服务', '2']], { status: 'key' });
    const db = nodeG(r3b, '数据库服务器', '国产关系数据库主备', { spec: '64 核／512 GB／20 TB SSD', os: '麒麟 V10', ip: '10.20.3.11-12', count: '2（主备）' }, [['达梦主库', '1'], ['达梦备库', '1']]);
    const mqn = nodeG(r3b, '消息与缓存节点', '消息队列与缓存', { spec: '32 核／128 GB', os: '麒麟 V10', ip: '10.20.2.11-16', count: '6' }, [['消息队列', '3'], ['分布式缓存', '3']]);
    const vm = nodeG(r3b, '运维虚拟机', '运维监控虚拟机', { spec: '8 核／32 GB 虚拟机', os: '统信 UOS', ip: '10.20.9.21-22', count: '2' }, [['监控告警', '1'], ['日志分析', '1']], { status: 'new' });
    /* 涉密内网区 */
    const z4 = zone('涉密内网区', '涉密秘密级', '情报研判与涉密数据处理区');
    const r4a = row(z4, '网络', 140);
    const [gap, core2] = equips(r4a, [
      dev('it_gap', 'firewall', '单向网闸', '业务专网 → 涉密内网单向摆渡', { spec: '单向光闸', count: '1' }, { status: 'key' }),
      dev('it_core_switch', 'switch', '涉密核心交换机', '涉密内网核心交换', { spec: '万兆交换机', ip: '192.168.0.0/16', count: '2' })]);
    const r4b = row(z4, '计算与存储', 96);
    const intel = nodeG(r4b, '情报研判服务器', '情报研判应用', { spec: '32 核／256 GB', os: '麒麟 V10（涉密版）', ip: '192.168.1.11-12', count: '2' }, [['情报研判服务', '2'], ['目标档案服务', '1']]);
    const sdb = nodeG(r4b, '涉密数据库服务器', '涉密数据存储', { spec: '64 核／512 GB／40 TB', os: '麒麟 V10（涉密版）', ip: '192.168.2.11', count: '1' }, [['涉密数据库', '1'], ['数据备份', '1']]);
    const C = (a, b, protocol, port, medium, o) => L(a, b, Object.assign({ kind: 'wired', dir: 'one', label: '' }, o || {}, { attrs: { protocol, port, medium } }));
    C(term, rtr, 'SSL VPN', '443', 'APN 专网', { kind: 'radio' });
    C(rtr, fw1, 'TCP/IP', '—', '万兆光纤', { dir: 'both' });
    C(fw1, waf, 'HTTPS', '443', '万兆光纤');
    C(fw1, vpn, 'SSL VPN', '443', '万兆光纤');
    C(waf, lb, 'HTTPS', '443', '万兆光纤');
    C(lb, web, 'HTTP', '8080', '万兆光纤');
    C(web, fw2, 'HTTPS', '8443', '万兆光纤');
    C(vpn, fw2, 'TCP', '9000', '万兆光纤');
    C(fw2, core, 'TCP/IP', '—', '万兆光纤', { dir: 'both' });
    C(core, k8s, 'TCP/IP', '—', '万兆光纤', { dir: 'both' });
    C(core, db, 'TCP/IP', '—', '万兆光纤', { dir: 'both' });
    C(core, mqn, 'TCP/IP', '—', '万兆光纤', { dir: 'both' });
    C(bas, vm, 'SSH', '22', '千兆网线');
    C(k8s, db, 'JDBC', '5236', '万兆光纤');
    C(db, gap, 'UDP 单向', '—', '单模光纤');
    C(gap, core2, 'UDP 单向', '—', '单模光纤');
    C(core2, intel, 'TCP/IP', '—', '万兆光纤', { dir: 'both' });
    C(intel, sdb, 'JDBC', '5236', '万兆光纤');
    foot(ITNOTE('部署架构图') + '　分组带为网络区域（标安全等级），带内的层仅作排版；子容器与图标为部署节点（规格、系统、地址见属性与「部署清单」），框内为部署单元。');
    beautify(d.pages.root);
  }, { base: '现有', new: '新增', key: '关键节点' }, 'ZKXT-BS-01');

  /* --------------------------------------------------- 安全架构图 */
  const itSec = defIT('it-sec', 'SEC', '安全架构图 · 等级保护', '按等级保护“一个中心、三重防护”划分安全域：保护对象、安全措施与边界防护设备，跨域访问经边界防护', (d, T) => {
    const { N, L, equips, head, foot } = T;
    head('指控信息系统 · 安全架构图', '“一个中心、三重防护”：安全通信网络、安全区域边界、安全计算环境，安全管理中心统一管控');
    const W = 1260;
    const dom = (t, level, desc) => N(Object.assign({ type: 'band', text: t, w: W }, X('sec_domain', desc, { level })));
    const row = (z, t) => N({ type: 'lane', text: t, parent: z.id, h: 128, titleW: 84 });
    const it = (et, key, fb, t, desc, o) => [[key, fb], t, Object.assign(X(et, desc), o || {})];
    const s1 = dom('互联网接入域', '等保二级', '移动终端接入与对外服务');
    const [nac, tm, vpn, fw] = equips(row(s1, '通信网络'), [
      it('sec_control', 'identity', 'security', '终端准入控制', '终端身份认证与合规检查'),
      it('protected_asset', 'tablet', 'laptop', '移动巡逻终端', '加固平板终端'),
      it('sec_boundary', 'it_vpn', 'gateway', '国密 VPN 网关', 'SM2／SM4 加密隧道', { status: 'key' }),
      it('sec_boundary', 'firewall', 'security', '抗 DDoS 防火墙', '外网边界防护')]);
    const s2 = dom('业务专网域', '等保三级', '指控信息系统主体运行环境');
    const [ngfw, ips, waf] = equips(row(s2, '区域边界'), [
      it('sec_boundary', 'firewall', 'security', '下一代防火墙', '区域边界访问控制'),
      it('sec_boundary', 'it_ids', 'security', '入侵防御 IPS', '入侵检测与阻断'),
      it('sec_boundary', 'it_waf', 'firewall', 'Web 应用防火墙', 'Web 攻击防护')]);
    const [dbAud, dbA, appS, harden] = equips(row(s2, '计算环境'), [
      it('sec_control', 'audit_log', 'security', '数据库审计', '数据库访问行为审计', { status: 'new' }),
      it('protected_asset', 'database', 'storage', '业务数据库', '核心业务数据'),
      it('protected_asset', 'it_microservice', 'app', '指控应用服务', '业务应用容器集群', { status: 'key' }),
      it('sec_control', 'security', 'identity', '主机加固防病毒', '主机安全基线与恶意代码防范')]);
    const s3 = dom('涉密内网域', '涉密秘密级', '情报研判与涉密数据处理');
    const [three, gap, intel, sdb] = equips(row(s3, '涉密防护'), [
      it('sec_control', 'identity', 'security', '三员分立管理', '系统、安全、审计三员分立，涉密域内独立管理'),
      it('sec_boundary', 'it_gap', 'firewall', '单向网闸', '业务专网 → 涉密内网单向摆渡', { status: 'key' }),
      it('protected_asset', 'staff_intel', 'server', '情报研判系统', '涉密情报研判应用'),
      it('protected_asset', 'database', 'storage', '涉密数据库', '涉密数据存储')]);
    /* 安全管理中心：右侧竖栏，贯穿三个安全域 */
    const mc = N(Object.assign({ type: 'group', text: '安全管理中心', w: 188, h: 400 }, X('sec_domain', '系统管理、审计管理、安全管理集中管控', { level: '等保三级' })));
    const ck = (et, key, fb, t, desc, o) => N(Object.assign({ type: 'round', text: t, icon: ic(key, fb), parent: mc.id, size: 12 }, X(et, desc), o || {}));
    const iam = ck('sec_control', 'identity', 'security', '统一身份认证', '集中身份与权限管理');
    const ca = ck('sec_control', 'it_ca', 'crypto', 'CA 证书服务', '数字证书签发与验证');
    const mfw = ck('sec_boundary', 'firewall', 'security', '管理区防火墙', '管理流量访问控制');
    const aud = ck('sec_control', 'audit_log', 'security', '集中安全审计', '日志汇聚与审计分析');
    const soc = ck('sec_control', 'ops_monitor', 'audit_log', '安全态势感知', '威胁分析与通报预警', { status: 'new' });
    const A = (a, b, content, protocol, o) => L(a, b, Object.assign({ kind: 'data', dir: 'one', label: '' }, o || {}, { attrs: { content, protocol } }));
    A(nac, tm, '终端准入认证', '802.1X', { kind: 'ctrl' });
    A(tm, vpn, '加密接入', 'SSL VPN 443');
    A(vpn, ngfw, '移动业务访问', 'TCP 9000');
    A(fw, waf, '对外服务访问', 'HTTPS 443');
    A(ngfw, ips, '边界流量', '串接');
    A(ips, appS, '白名单访问', 'HTTPS 8443');
    A(waf, appS, 'Web 防护后访问', 'HTTPS 443');
    A(harden, appS, '主机防护', 'Agent', { kind: 'ctrl' });
    A(appS, dbA, '数据访问', 'JDBC 5236');
    A(dbAud, dbA, '访问审计', '旁路镜像', { kind: 'plain' });
    A(dbA, gap, '单向摆渡', 'UDP 单向', { status: 'key' });
    A(gap, intel, '摆渡数据接收', 'UDP 单向');
    A(intel, sdb, '涉密数据访问', 'JDBC 5236');
    A(iam, ca, '证书校验', 'OCSP 80', { kind: 'ctrl' });
    A(ca, mfw, '证书下发', 'HTTPS 443', { kind: 'ctrl' });
    A(mfw, aud, '日志汇聚', 'Syslog 514', { kind: 'ctrl' });
    A(aud, soc, '审计事件', 'Kafka', { kind: 'ctrl' });
    A(mfw, harden, '集中管控', 'HTTPS 443', { kind: 'ctrl' });
    A(three, gap, '摆渡策略管理', '本地管理口', { kind: 'ctrl' });
    foot(ITNOTE('安全架构图') + '　分组带为安全域（标安全等级），带内的层仅作排版；跨域访问须经防火墙、网闸、VPN 等边界防护设备；右侧为安全管理中心。');
    beautify(d.pages.root);
    sideColumn(d.pages.root, mc, 44, 28);
  }, { base: '现有措施', new: '新增措施', key: '关键防护' }, 'ZKXT-AQ-01');

  /* ---------- 追加到画廊（去重） ---------- */
  for (const t of [ov1, ov2, ov5b, sv1, sv4, itBiz, itApp, itData, itTech, itDeploy, itSec]) { const i = window.TEMPLATES.findIndex(x => x.id === t.id); if (i >= 0) window.TEMPLATES[i] = t; else window.TEMPLATES.push(t); }
})();
