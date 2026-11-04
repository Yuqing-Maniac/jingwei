/* ============ 织图 · 文字成图（文本 → 体系图） ============
 * 规则解析（离线）为主；可选内网大模型（OpenAI 兼容接口）或 claude.ai 在线理解。
 * 依赖 app.js 中的全局：doc, cur, stack, mkNode, uid, beautify, checkpoint, loadDoc, render, fit,
 * diagramSVG, contentBBox, measure, iconURI, ICON_MAP, isCont, nodeById, enterSub, toast, esc, T, snapv。 */
(function () {
  'use strict';

  /* ---------------- 常量与工具 ---------------- */
  const LS_KEY = 'hongtu.textgen.v1';
  const NOTE_RE = /^(?:[-*+]\s*)?(说明|备注|关键变化|注释|注|小结|总结)\s*[:：]/;
  const ARROW_SRC = '<-->|<==>|<~>|<->|<=>|↔|⟷|-->|==>|~>|->|→|⟶|⇒|<-|←|——|--';
  const ARROW_SPLIT = new RegExp('\\s*(' + ARROW_SRC + ')\\s*');
  const hasArrow = s => new RegExp('(' + ARROW_SRC + ')').test(stripBraces(s));
  const OPEN = '(（[【{《“"', CLOSE = ')）]】}》”"';
  const firstLine = s => String(s || '').split('\n')[0].trim();
  const normName = s => String(s || '').toLowerCase()
    .replace(/\{[^}]*\}|\[[^\]]*\]|【[^】]*】/g, '')
    .replace(/[\s·・\-_—/／\\、,，.。:：;；'"“”‘’()（）<>《》]/g, '');
  function stripBraces(s) { return String(s).replace(/\{[^}]*\}/g, '').replace(/[\[【][^\]】]*[\]】]/g, ''); }
  function lsGet() { try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}') || {}; } catch (_) { return {}; } }
  function lsSet(o) { try { localStorage.setItem(LS_KEY, JSON.stringify(o)); } catch (_) { } }

  /* split on 、,，;； at bracket depth 0 */
  function splitList(s, extra) {
    const out = []; let depth = 0, buf = '';
    const seps = '、,，;；' + (extra || '');
    for (const ch of String(s)) {
      if (OPEN.includes(ch) && ch !== '"') depth++;
      else if (CLOSE.includes(ch) && ch !== '"') depth = Math.max(0, depth - 1);
      if (!depth && seps.includes(ch)) { out.push(buf); buf = ''; continue; }
      buf += ch;
    }
    out.push(buf);
    return out.map(x => x.trim().replace(/^(和|及|以及|与)\s*/, '').replace(/\s*等$/, '').trim()).filter(Boolean);
  }

  /* index of first ':'/'：' outside brackets/braces, or -1 */
  function colonAt(s) {
    let depth = 0, i = 0;
    for (const ch of String(s)) {
      if ('{[【(（'.includes(ch)) depth++;
      else if ('}]】)）'.includes(ch)) depth = Math.max(0, depth - 1);
      else if (!depth && (ch === ':' || ch === '：')) return i;
      i += ch.length;
    }
    return -1;
  }

  /* ---------------- 图标匹配（动态读取 ICON_LIB，后续批次新增图标自动参与） ---------------- */
  const SYN = [
    ['察打一体|察打', 'uav_male'], ['高空长航时|长航时', 'hale_uav'], ['垂起|垂直起降', 'uav_vtol'], ['无人直升机', 'uav_heli'],
    ['蜂群|集群无人机', 'swarm'], ['巡飞弹|巡飞', 'loitering'], ['四旋翼|多旋翼|旋翼无人机|旋翼|FPV|穿越机', 'uav_quad'], ['固定翼', 'uav_fixed'],
    ['靶机', 'target_drone'], ['无人机|UAV|无人飞行器', 'uav_fixed'],
    ['预警机', 'awacs'], ['直升机', 'helicopter'], ['战斗机|歼击机', 'fighter'], ['运输机', 'transport'], ['侦察机', 'recon_aircraft'], ['电子战飞机', 'ew_aircraft'], ['浮空器|系留气球|飞艇', 'airship'],
    ['巡航导弹', 'cruise_missile'], ['弹道导弹', 'ballistic_missile'], ['拦截弹', 'interceptor'], ['导弹', 'cruise_missile', 1],
    ['无人艇母船|母船', 'usv_mother'], ['无人艇|无人船|水面无人|USV', 'usv'], ['无人潜航器|潜航器|UUV|水下无人', 'uuv'], ['水下滑翔机', 'glider'], ['潜艇', 'submarine'],
    ['驱逐舰', 'destroyer'], ['护卫舰', 'frigate'], ['航母|航空母舰', 'carrier'], ['巡逻艇|作战艇|快艇', 'patrol_boat'], ['科考船', 'research_vessel'], ['补给舰', 'supply_ship'], ['扫雷', 'minesweeper'], ['声呐|浮标', 'sonar_buoy'], ['舰|船', 'frigate', 1],
    ['机器狗|无人狗|四足', 'robodog'], ['履带无人车', 'ugv_tracked'], ['排爆', 'eod_robot'], ['无人车|地面无人|UGV|无人战车', 'ugv'],
    ['坦克', 'tank'], ['步战车|步兵战车', 'ifv'], ['指挥车', 'command_vehicle'], ['通信车', 'comm_vehicle'], ['运输车|保障车', 'truck'], ['发射车', 'tel'], ['防空导弹', 'sam'], ['火炮', 'sp_howitzer'], ['火箭炮', 'mlrs'],
    ['反无人机|反无|C-UAS', 'cuas'], ['激光武器', 'laser_weapon'], ['高能微波|微波武器', 'hpm'], ['干扰机|干扰设备|干扰', 'jammer'],
    ['单兵|士兵|战士', 'soldier'],
    ['相控阵', 'phased_radar'], ['雷达', 'radar'], ['光电', 'eo_turret'], ['红外', 'ir_sensor'], ['声学', 'acoustic'], ['无线电侦测|频谱监测|侦测设备', 'rf_detector'],
    ['卫通站|卫星通信站|卫星地面站|卫通', 'sat_station'], ['卫星', 'satellite'], ['北斗', 'beidou'],
    ['基站|4G|5G|LTE|蜂窝|通信塔|铁塔', 'comm_tower'], ['中继站|中继', 'relay'], ['自组网|MESH|组网电台', 'mesh'], ['数据链|电台', 'datalink'], ['天线', 'antenna_array'],
    ['路由', 'router'], ['交换机', 'switch'], ['防火墙', 'firewall'], ['光纤|光端机', 'fiber'], ['摄像机|摄像头', 'camera'],
    ['地面控制站|地面站|控制站|测控站', 'gcs'], ['指挥中心', 'command_center'], ['指挥所|指挥部|指控中心', 'command_post'], ['指控席|席位|工作站', 'console'],
    ['操作员|操控员|操作手|监督席|值班员', 'operator'], ['飞手', 'drone_pilot'], ['指挥员|指挥官', 'commander'], ['参谋', 'staff_officer'], ['分析员', 'analyst'], ['专家组', 'expert_group'], ['用户', 'user_group', 1],
    ['智能体|Agent', 'ai_agent'], ['大屏', 'big_screen'], ['平板', 'tablet'], ['笔记本|便携计算机', 'laptop'], ['手持终端|手持', 'handheld'],
    ['数据中心', 'data_center'], ['服务器|计算节点', 'server'], ['数据库', 'database'], ['云平台|云计算|云', 'cloud'], ['GPU|算力', 'gpu'], ['存储', 'storage', 1],
    ['APP|应用程序', 'app'], ['应用', 'app', 1], ['安全', 'security', 1],
    ['知识图谱', 'knowledge_graph', 1], ['算法|模型', 'algorithm', 1], ['仿真', 'simulation', 1], ['流程编排|工作流', 'workflow', 1], ['消息总线|总线', 'message_bus', 1], ['接口|API', 'api', 1], ['电子地图|地图|底图', 'map', 1], ['视频', 'video', 1], ['文档|报告', 'document', 1], ['时统|授时', 'clock', 1],
    ['机场', 'airbase'], ['港口|码头', 'port'], ['营区', 'barracks'], ['仓库', 'depot'], ['电站', 'power_station'], ['油库', 'fuel_depot'], ['岛礁', 'island'], ['气象站', 'weather'],
  ];
  const PHYS_CATS = ['空中', '海上', '陆地', '设施', '人员', '感知通信', '反无人', '无人'];
  const MOVER_CATS = ['空中', '海上', '陆地', '反无人', '无人'];
  const PHYS_KEYS = new Set(['gcs', 'command_post', 'command_vehicle', 'big_screen', 'laptop', 'handheld', 'tablet', 'data_center', 'command_center']);
  let iconIdx = null, iconIdxN = -1;
  function lib() { return typeof ICON_LIB !== 'undefined' ? ICON_LIB : []; }
  function iconIndex() {
    const L = lib();
    if (iconIdx && iconIdxN === L.length) return iconIdx;
    const weakKeys = new Set(SYN.filter(s => s[2]).map(s => s[1]));
    const cands = [];
    L.forEach(i => {
      const nm = String(i.name || '').replace(/[（(][^）)]*[）)]/g, '').trim();
      if (nm.length >= 2) cands.push({ kw: nm, key: i.key, weak: nm.length <= 2 && weakKeys.has(i.key) || weakKeys.has(i.key), order: 0 });
    });
    SYN.forEach(([pat, key, weak], o) => pat.split('|').forEach(kw => cands.push({ kw, key, weak: !!weak, order: o + 1 })));
    const byKey = Object.fromEntries(L.map(i => [i.key, i]));
    iconIdx = { cands: cands.filter(c => byKey[c.key]), byKey }; iconIdxN = L.length;
    return iconIdx;
  }
  const iconCat = key => (iconIndex().byKey[key] || {}).cat || '';
  /* returns {key, weak} or null */
  function matchIcon(text) {
    const raw = firstLine(text).replace(/[（(][^）)]*[）)]\s*$/, '').trim();
    if (!raw) return null;
    const low = raw.toLowerCase();
    let best = null, bs = -1;
    for (const c of iconIndex().cands) {
      const kw = c.kw.toLowerCase();
      if (!low.includes(kw)) continue;
      const end = low.endsWith(kw), exact = low === kw;
      if (c.weak && !end) continue;
      const s = c.kw.length + (end ? 10 : 0) + (exact ? 20 : 0) - c.order * 0.001;
      if (s > bs) { bs = s; best = c; }
    }
    return best ? { key: best.key, weak: best.weak } : null;
  }
  function lookupIcon(spec) {
    spec = String(spec || '').trim();
    if (!spec || /^(无|none|空)$/i.test(spec)) return { none: true };
    if (/^(lib|ms|cu):/.test(spec)) return { key: spec };
    const { byKey } = iconIndex(), L = lib();
    if (byKey[spec]) return { key: 'lib:' + spec };
    let i = L.find(x => x.name === spec) || L.find(x => x.name.replace(/[（(][^）)]*[）)]/g, '') === spec) || L.find(x => x.name.includes(spec)) || L.find(x => spec.includes(x.name));
    if (i) return { key: 'lib:' + i.key };
    if (typeof MS_LIST !== 'undefined' && window.ms) { const m = MS_LIST.find(x => x[1] === spec || x[1].includes(spec)); if (m) return { key: 'ms:' + m[0] }; }
    const m = matchIcon(spec); if (m) return { key: 'lib:' + m.key };
    return { miss: true };
  }

  /* ---------------- 条目文本：状态、图标、形态标记 ---------------- */
  function parseItemText(s) {
    let text = String(s).trim(), status = 'base', icon = null, form = 'auto';
    text = text.replace(/\{\s*(?:图标|icon)\s*[:：=]\s*([^}]*)\}/gi, (_, v) => { icon = v.trim(); return ''; });
    text = text.replace(/\{\s*(装备|卡片|图标卡|框|方框|文本框)\s*\}/g, (_, v) => { form = /装备|卡片|图标卡/.test(v) ? 'equip' : 'box'; return ''; });
    text = text.replace(/[\[【（(]\s*(新增|重构|新建|改造|升级|本步新增)\s*[\]】）)]/g, () => { status = 'new'; return ''; });
    text = text.replace(/[\[【（(]\s*(重点|关键|核心|重点关注)\s*[\]】）)]/g, () => { status = 'key'; return ''; });
    text = text.replace(/[\[【]\s*(延续|保持|沿用)\s*[\]】]/g, '');
    text = text.replace(/<br\s*\/?>|\\n/gi, '\n').replace(/\*\*|__|`/g, '').replace(/[ \t]+/g, ' ').trim();
    return { text, status, icon, form, children: [] };
  }

  /* ---------------- 连接行 ---------------- */
  const KIND_MARK = [[/指令|控制|命令/, 'ctrl'], [/有线|光纤|网线|光缆|以太网/, 'wired'], [/卫通|卫星/, 'sat'], [/无线|数据链|自组网|电台|微波/, 'radio'], [/数据/, 'data'], [/关联|无类型/, 'plain']];
  function kindFromWords(s, allowCtrl = true) {
    if (/光纤|有线|网线|以太网|专线|光缆|电缆/.test(s)) return 'wired';
    if (/卫通|卫星通信|卫星链路|卫星|天通/.test(s)) return 'sat';
    if (/数据链|无线|自组网|电台|微波|4G|5G|射频|超短波|短波|WiFi|Wi-Fi|中继/.test(s)) return 'radio';
    if (allowCtrl && /指令|控制|下发|指挥|调度|管控|命令|任务分配/.test(s)) return 'ctrl';
    return null;
  }
  function opInfo(op) {
    const both = ['<-->', '<==>', '<~>', '<->', '<=>', '↔', '⟷'].includes(op);
    const none = op === '--' || op === '——';
    const rev = op === '<-' || op === '←';
    const kind = { '-->': 'ctrl', '<-->': 'ctrl', '==>': 'wired', '<==>': 'wired', '~>': 'radio', '<~>': 'radio' }[op] || null;
    return { dir: both ? 'both' : none ? 'none' : 'one', rev, kind };
  }
  /* "A -> B, C : 标签 [指令]" → {segs:[[names]], ops:[op], label, kind, dir} */
  function parseArrowLine(line) {
    let s = line, kind = null, dir = null;
    s = s.replace(/[\[【]\s*([^\]】]+?)\s*[\]】]/g, (m, v) => {
      if (/^双向$/.test(v)) { dir = 'both'; return ''; }
      if (/^单向$/.test(v)) { dir = 'one'; return ''; }
      if (/^无箭头$/.test(v)) { dir = 'none'; return ''; }
      for (const [re, k] of KIND_MARK) if (re.test(v)) { kind = k; return ''; }
      return m;
    });
    const parts = s.split(ARROW_SPLIT);
    const names = [], ops = [];
    parts.forEach((p, i) => (i % 2 ? ops : names).push(p));
    let label = '';
    const last = names[names.length - 1] || '';
    const lm = last.match(/^(.*?)\s*[:：]\s*(.*)$/);
    if (lm) { names[names.length - 1] = lm[1]; label = lm[2].trim(); }
    return { segs: names.map(n => splitList(n)), ops, label, kind, dir };
  }

  /* ---------------- 方言解析 → 中间结构 IR ---------------- */
  function newIRPage(attach) { return { attach, title: '', subtitle: '', bands: [], links: [], notes: [], warnings: [], names: new Set() }; }
  function parseDialect(src) {
    const pages = [newIRPage(null)];
    let pg = pages[0], band = null, lane = null, section = 'items', stack = [];
    const lines = String(src || '').replace(/\r/g, '').split('\n');
    const ensureBand = () => { if (!band) { band = { text: '', status: 'base', lanes: [], items: [], implicit: true }; pg.bands.push(band); } return band; };
    const target = () => lane ? lane.items : ensureBand().items;
    const resetCtx = () => { stack = []; };
    const addLinksFrom = (p, fromLine) => {
      for (let i = 0; i < p.ops.length; i++) {
        const oi = opInfo(p.ops[i]);
        let A = p.segs[i], B = p.segs[i + 1];
        if (!A.length || !B.length) continue;
        if (oi.rev) [A, B] = [B, A];
        for (const a of A) for (const b of B) {
          const ka = parseItemText(a).text, kb = parseItemText(b).text;
          const lab = p.label;
          pg.links.push({ a: ka, b: kb, dir: p.dir || oi.dir, kind: p.kind || oi.kind || (lab && kindFromWords(lab)) || 'data', label: lab, src: fromLine });
        }
      }
    };
    let inCode = false;
    for (let li = 0; li < lines.length; li++) {
      const raw = lines[li];
      if (/^\s*```/.test(raw)) { inCode = !inCode; continue; }
      if (!raw.trim()) continue;
      const indent = (raw.match(/^[ \t　]*/)[0] || '').replace(/\t/g, '    ').replace(/　/g, '  ').length;
      const line = raw.trim();
      let m;
      if ((m = line.match(/^(#{1,6})\s*(.+?)\s*#*$/))) {
        resetCtx();
        const lv = m[1].length, name = m[2].trim();
        if (lv === 1) {
          if (!pg.title) pg.title = parseItemText(name).text;
          else { band = { ...parseItemText(name), lanes: [], items: [] }; pg.bands.push(band); lane = null; section = 'items'; }
          continue;
        }
        if (lv === 2) {
          const dm = name.match(/^(?:展开|内部|下钻|内部构成|内部结构|子图)\s*[:：]\s*(.+)$/);
          if (dm) { pg = newIRPage(parseItemText(dm[1]).text); pages.push(pg); band = null; lane = null; section = 'items'; continue; }
          if (/^(连接|连线|关系|链路|接口关系|连接关系|信息流|数据流)$/.test(name)) { section = 'links'; continue; }
          section = 'items'; band = { ...parseItemText(name), lanes: [], items: [] }; pg.bands.push(band); lane = null; continue;
        }
        section = 'items'; ensureBand(); lane = { ...parseItemText(name), items: [] }; band.lanes.push(lane); continue;
      }
      if ((m = line.match(/^>\s*(.*)$/))) { const t = m[1].trim(); if (t) pg.subtitle = pg.subtitle ? pg.subtitle + ' ' + t : t; continue; }
      if (/^\|.*\|\s*$/.test(line)) {
        resetCtx();
        if (/^\|[\s:|\-—]+\|$/.test(line)) continue;
        const next = (lines[li + 1] || '').trim();
        if (/^\|[\s:|\-—]+\|$/.test(next)) continue; // header row
        const cells = line.replace(/^\||\|$/g, '').split('|').map(c => c.trim());
        if (!cells[0] && cells.slice(1).every(c => !c)) continue;
        ensureBand(); const ln = { ...parseItemText(cells[0] || '未命名层'), items: [] }; band.lanes.push(ln);
        for (const c of cells.slice(1)) for (const it of splitList(c)) { const x = parseItemText(it); ln.items.push(x); pg.names.add(x.text); }
        lane = ln; continue;
      }
      if (NOTE_RE.test(line)) { pg.notes.push(line.replace(/^[-*+]\s*/, '')); continue; }
      const bm = line.match(/^(?:[-*+•·]|\d+[.、)）])\s+(.*)$/) || line.match(/^[-*+•]\s*(.+)$/);
      const content = bm ? bm[1].trim() : line;
      if (section === 'links') { if (hasArrow(content)) addLinksFrom(parseArrowLine(content), line); else pg.warnings.push(`“连接”段中无法识别：${content}`); continue; }
      if (!bm && hasArrow(content)) { addLinksFrom(parseArrowLine(content), line); continue; }
      if (!bm && !band) {
        if (!pg.title) pg.title = content; else if (!pg.subtitle) pg.subtitle = content; else pg.notes.push(content);
        continue;
      }
      /* items (bullet, or plain line inside a band / lane) */
      while (stack.length && stack[stack.length - 1].indent >= indent) stack.pop();
      const parentItem = bm && stack.length ? stack[stack.length - 1].item : null;
      const dest = parentItem ? parentItem.children : target();
      let created = [];
      if (hasArrow(content)) {
        const p = parseArrowLine(content);
        /* chain bullet: create the boxes not declared yet, then link them */
        p.segs.forEach(seg => seg.forEach(n => { const it = parseItemText(n); if (it.text && !pg.names.has(it.text) && !created.some(c => c.text === it.text)) created.push(it); }));
        addLinksFrom(p, line);
      } else {
        const ci = colonAt(content);
        const gm = ci > 0 && ci <= 40 ? [content, content.slice(0, ci).trim(), content.slice(ci + 1).trim()] : null;
        if (gm && gm[2] && !/^https?$/i.test(gm[1])) {
          const g = parseItemText(gm[1]);
          splitList(gm[2]).forEach(x => g.children.push(parseItemText(x)));
          created.push(g);
        } else splitList(content).forEach(x => { const it = parseItemText(x); if (it.text) created.push(it); });
      }
      dest.push(...created);
      const reg = arr => arr.forEach(i => { pg.names.add(i.text); reg(i.children); }); reg(created);
      if (bm && created.length) stack.push({ indent, item: created[created.length - 1] });
    }
    return pages;
  }

  /* ---------------- 自然语言（散文）→ 方言 ---------------- */
  const CLEAN_HEAD = /^(其中|另外|此外|同时|并且|并|且|再|然后|还|也|又|而|则|最后|首先|其次|该|本|整个|整体上|总体上|总体|主要)[，,、\s]*/;
  function cleanName(s) {
    let t = String(s || '').trim();
    for (let i = 0; i < 3; i++) t = t.replace(CLEAN_HEAD, '');
    t = t.replace(/^(由|把|将|被|对|从)/, '').replace(/(的|等|之间|分别|均|都|各自|也|还|会|可以|能够|可|主要|则|将)+$/, '').replace(/[，,。.\s]+$/, '').trim();
    return t;
  }
  function splitProseList(s) {
    s = String(s).replace(/^(了|有|：|:)/, '').replace(/(等)?[\d一二三四五六七八九十几多两]+(个|类|部分|层|大类|种|型|级|个部分|个层次|大部分)[^，,、]{0,4}$/, '').replace(/(共同)?(组成|构成)(部分)?$/, '').replace(/等$/, '');
    return splitList(s, '').flatMap(x => x.split(/(?:以及|和|及|与)(?![^（(]*[)）])/)).map(x => cleanName(x)).filter(x => x && x.length <= 30);
  }
  function proseToDialect(text) {
    const sents = String(text || '').replace(/\r/g, '').split(/[。；;！!？?\n]+/).map(s => s.trim()).filter(Boolean);
    const tree = new Map(), order = [], childOf = new Set(), links = [], layers = [], notes = [];
    let reverse = false, firstSubject = null, title = '';
    const addTree = (p, items, status) => {
      if (!tree.has(p)) { tree.set(p, []); order.push(p); }
      for (const it of items) { if (!tree.get(p).includes(it)) tree.get(p).push(it); childOf.add(it); }
    };
    const statusOf = new Map();
    const markStatus = n => { let s = n; const m = s.match(/^(新增|新建|重构|升级|改造)(的)?/); if (m) { s = s.slice(m[0].length); statusOf.set(s, 'new'); } const k = s.match(/^(重点|关键|核心)(的)?/); if (k && s.length > k[0].length + 1) { s = s.slice(k[0].length); statusOf.set(s, 'key'); } return s; };
    const LAYER_RE = /^(第[一二三四五六七八九十\d]+层|顶层|最上层|上层|最顶层|中间层|中层|底层|最底层|下层|最下层|基础层|支撑层)(?:为|是|：|:|叫|即|称为)?\s*(.*)$/;
    const VIA = '(?:通过|经由|经过|借助|利用|使用|采用|依托|基于)';
    const SEND = '(?:发送|下发|上报|推送|传输|传送|提供|分发|发布|报送|回传|转发|传递|共享|同步)';
    const MUT = '(?:互联互通|互联|互通|相连|连接|双向通信|通信|交互|组网|对接|协同|联通|通联)';
    let subject = null, knownNames = [];
    const linkSents = [];
    const isKnown = x => { const q = normName(cleanName(x)); return !!q && knownNames.some(k => normName(k) === q); };
    const pushLink = (a, b, dir, kind, label) => {
      const As = splitProseList(a).map(markStatus), Bs = splitProseList(b).map(markStatus);
      for (const x of As) for (const y of Bs) if (x && y && x !== y) links.push({ a: x, b: y, dir, kind, label: (label || '').replace(/^(了|的)|(等|的)$/g, '').slice(0, 14) });
      if (As[0]) subject = As[0];
    };
    const kOf = (c, ...names) => { let t = c; names.forEach(n => { if (n) t = t.split(n).join(' '); }); return kindFromWords(t); };
    const tryLink = c => {
      let m;
      if ((m = c.match(new RegExp('^(.+?)' + VIA + '(.+?)(?:与|和|同|跟)(.+?)(?:之间)?' + MUT)))) { pushLink(m[1], m[3], 'both', kindFromWords(m[2]) || 'data', cleanName(m[2])); return true; }
      if ((m = c.match(new RegExp('^(.+?)' + VIA + '(.+?)(?:向|给|对|为)(.+?)' + SEND + '(.*)$')))) { const obj = cleanName(m[4]); pushLink(m[1], m[3], 'one', kindFromWords(m[2], false) || kOf(c, m[1], m[3]) || 'data', obj || cleanName(m[2])); return true; }
      if ((m = c.match(new RegExp('^(.+?)' + VIA + '(.+?)(连接|接入|连到|连至|链接|联接|控制|指挥|管控|访问|调用|调度|引导)(?:到|至)?(.+)$')))) { pushLink(m[1], m[4], 'one', kindFromWords(m[2], false) || (/控制|指挥|管控|调度|引导/.test(m[3]) ? 'ctrl' : 'data'), cleanName(m[2])); return true; }
      if ((m = c.match(new RegExp('^(.+?)(?:向|给|对)(.+?)' + SEND + '(.*)$')))) { pushLink(m[1], m[2], 'one', kOf(c, m[1], m[2]) || 'data', cleanName(m[3])); return true; }
      if ((m = c.match(new RegExp('^(.+?)(?:与|和|同|跟)(.+?)(?:之间)?(?:' + VIA + '(.+?))?' + MUT + '(.*)$')))) { pushLink(m[1], m[2], 'both', kindFromWords((m[3] || '') + m[4]) || 'data', cleanName(m[3] || '')); return true; }
      if ((m = c.match(new RegExp('^(.+?)' + SEND + '(.+?)(?:给|至|到)(.+)$')))) { pushLink(m[1], m[3], 'one', kOf(c, m[1], m[3]) || 'data', cleanName(m[2])); return true; }
      if ((m = c.match(/^(.+?)(?:接收|获取|接受|收到)(?:来自)?(.+?)(?:的|发来的)(.+)$/))) { pushLink(m[2], m[1], 'one', kOf(c, m[1], m[2]) || 'data', cleanName(m[3])); return true; }
      /* bare verb: try every verb position, prefer the split whose two sides are declared names */
      const VR = /(连接|接入|控制|指挥|管控|调用|调度|驱动|访问|支撑|服务于|保障)(?:到|至)?/g; let best = null, bs = -1, vm;
      while ((vm = VR.exec(c))) {
        const L = c.slice(0, vm.index), R = c.slice(vm.index + vm[0].length);
        if (L.length < 2 || R.length < 2 || L.length > 24 || R.length > 30) continue;
        const sc = (isKnown(L) ? 2 : 0) + (isKnown(R) ? 2 : 0) + vm.index * 0.001;
        if (sc > bs) { bs = sc; best = [L, R, vm[1]]; }
      }
      if (best) { pushLink(best[0], best[1], 'one', /控制|指挥|管控|调度|驱动/.test(best[2]) ? 'ctrl' : (kOf(c, best[0], best[1]) || 'data'), ''); return true; }
      return false;
    };
    for (let s of sents) {
      if (NOTE_RE.test(s)) { notes.push(s); continue; }
      if (/自下而上|由下至上|从下到上|由下往上/.test(s)) { reverse = true; s = s.replace(/[，,]?\s*(自下而上|由下至上|从下到上|由下往上)(依次)?(分为|划分为|为|是)?/, '分为'); }
      s = s.replace(/[，,]?\s*(自上而下|由上至下|从上到下)(依次)?(分为|划分为|为|是)?/, '分为');
      let m;
      if ((m = s.replace(CLEAN_HEAD, '').match(LAYER_RE))) {
        const rest = m[2];
        const sp = rest.split(/[，,]?\s*(?:主要)?(?:包括|包含|主要有|涵盖|由|部署有?|配备有?|有)\s*/);
        let name = cleanName(sp.length > 1 ? sp[0] : (/[、，,和及]/.test(rest) ? '' : rest));
        const items = sp.length > 1 ? splitProseList(sp.slice(1).join('')) : (/[、，,和及]/.test(rest) ? splitProseList(rest) : []);
        if (!name) name = m[1];
        layers.push({ key: m[1], name: markStatus(name), items: items.map(markStatus) }); continue;
      }
      const comp = s.match(/^(.{1,30}?)(?:主要|共|总体上|整体上|一般)?(?:可)?(?:分为|划分为|分成|包括|包含|涵盖|下设|下辖|配备有?|含有|设有|部署有?)[:：]?(.+)$/)
        || (function () { /* 不用后行断言：旧版火狐不支持 (?<!…) */
          const m2 = s.match(/^(.{0,31}?[^路自理缘])由(.+?)(?:共同)?(?:组成|构成)$/);
          if (!m2) return null; const g1 = m2[1].replace(/主要$/, '');
          return g1 ? [m2[0], g1, m2[2]] : null; })();
      if (comp && !new RegExp(VIA + '|向|给').test(comp[1])) {
        const parent = markStatus(cleanName(comp[1])), items = splitProseList(comp[2]).map(markStatus);
        if (parent && items.length) { addTree(parent, items); if (!firstSubject) firstSubject = parent; continue; }
      }
      if (comp && /^[^、，,和及]*[\d一二三四五六七八九十几两]+(个|类|层|部分|大类)/.test(comp[2])) continue; /* “分为三层” — layers follow */
      linkSents.push(s);
    }
    /* second pass: relations, now that declared names are known */
    knownNames = [...tree.keys(), ...[...tree.values()].flat(), ...layers.flatMap(l => [l.name, ...l.items])];
    for (const s of linkSents) {
      subject = null;
      for (let c of s.split(/[，,]/).map(x => x.trim()).filter(Boolean)) {
        c = c.replace(CLEAN_HEAD, '').replace(CLEAN_HEAD, '');
        const needsSubj = new RegExp('^(?:' + VIA.slice(3, -1) + '|向|给|对|与|同|跟|' + SEND.slice(3, -1) + '|连接|接入|控制|接收)').test(c);
        if (needsSubj && subject) c = subject + c;
        tryLink(c);
      }
    }
    /* layer ordering */
    if (layers.length) {
      const rank = k => /顶|最上/.test(k) ? 0 : /^上层/.test(k) ? 10 : /中/.test(k) ? 50 : /下层|底|基础|支撑/.test(k) ? 100 : null;
      const ranked = layers.map((l, i) => ({ l, i, r: rank(l.key) }));
      if (ranked.some(x => x.r !== null)) { ranked.forEach(x => { if (x.r === null) x.r = 20 + x.i; }); ranked.sort((a, b) => a.r - b.r || a.i - b.i); }
      else if (reverse) ranked.reverse();
      layers.splice(0, layers.length, ...ranked.map(x => x.l));
    }
    /* emit */
    const out = [];
    const tag = n => statusOf.get(n) === 'new' ? ' [新增]' : statusOf.get(n) === 'key' ? ' [重点]' : '';
    const known = [];
    const emitItem = (n, depth, seen = new Set()) => {
      known.push(n);
      out.push('  '.repeat(depth) + '- ' + n + tag(n));
      if (seen.has(n)) return; seen.add(n);
      for (const k of tree.get(n) || []) emitItem(k, depth + 1, seen);
    };
    const roots = order.filter(n => !childOf.has(n));
    let rootName = firstSubject && !childOf.has(firstSubject) ? firstSubject : roots[0] || null;
    title = rootName || (layers.length ? '体系分层架构' : '');
    if (title) out.push('# ' + title);
    const emitted = new Set();
    const isLayerish = n => /层$|层级$|域$|面$/.test(n);
    if (layers.length) {
      const layerNames = new Set(layers.map(l => l.name));
      out.push('', '## ' + (rootName && rootName.length <= 6 ? rootName : '分层架构'));
      for (const l of layers) {
        out.push('### ' + l.name + tag(l.name)); known.push(l.name);
        const items = l.items.length ? l.items : (tree.get(l.name) || []);
        items.forEach(it => { emitItem(it, 0); emitted.add(it); });
        emitted.add(l.name);
      }
      if (rootName) { emitted.add(rootName); for (const k of tree.get(rootName) || []) if (layerNames.has(k)) emitted.add(k); }
    }
    const emitBranch = (r, asBand) => {
      const kids = tree.get(r) || [];
      const deep = kids.filter(k => (tree.get(k) || []).length);
      if (!deep.length) { out.push('', '## ' + (asBand || r) + tag(r)); known.push(r); kids.forEach(k => emitItem(k, 0)); return; }
      const allLeafGrand = deep.every(k => (tree.get(k) || []).every(g => !(tree.get(g) || []).length));
      if (allLeafGrand && deep.filter(isLayerish).length >= deep.length / 2) {
        out.push('', '## ' + (asBand || r) + tag(r)); known.push(r);
        const loose = kids.filter(k => !(tree.get(k) || []).length);
        for (const k of deep) { out.push('### ' + k + tag(k)); known.push(k); tree.get(k).forEach(g => emitItem(g, 0)); }
        if (loose.length) { out.push('### 其他'); loose.forEach(k => emitItem(k, 0)); }
        return;
      }
      const loose = kids.filter(k => !(tree.get(k) || []).length);
      for (const k of deep) {
        const g = tree.get(k);
        const gdeep = g.filter(x => (tree.get(x) || []).length);
        out.push('', '## ' + k + tag(k)); known.push(k);
        if (gdeep.length) {
          for (const x of gdeep) { out.push('### ' + x + tag(x)); known.push(x); tree.get(x).forEach(y => emitItem(y, 0)); }
          const gl = g.filter(x => !(tree.get(x) || []).length); if (gl.length) { out.push('### ' + k); gl.forEach(y => emitItem(y, 0)); }
        } else g.forEach(y => emitItem(y, 0));
      }
      if (loose.length) { out.push('', '## 其他组成'); loose.forEach(k => emitItem(k, 0)); }
    };
    for (const r of [rootName, ...roots.filter(x => x !== rootName)].filter(Boolean)) {
      if (emitted.has(r)) {
        const rest = (tree.get(r) || []).filter(k => !emitted.has(k));
        if (rest.length) { out.push('', '## 其他组成'); rest.forEach(k => emitItem(k, 0)); }
        continue;
      }
      emitted.add(r);
      const leafOnly = !(tree.get(r) || []).some(k => (tree.get(k) || []).length);
      emitBranch(r, r === rootName ? (leafOnly ? '组成' : r.length <= 6 ? null : '体系构成') : null);
    }
    /* link endpoints not declared anywhere → 节点 band */
    const extra = [];
    const has = n => { const q = normName(n); return [...known, ...extra].some(k => { const t = normName(k); return t === q || (q.length >= 2 && t.includes(q)) || (t.length >= 2 && q.includes(t) && t.length / q.length >= 0.5); }); };
    for (const l of links) for (const e of [l.a, l.b]) if (!has(e)) extra.push(e);
    if (extra.length) { out.push('', '## ' + (known.length ? '其他节点' : '节点')); extra.forEach(e => out.push('- ' + e + tag(e))); }
    if (links.length) {
      out.push('', '## 连接');
      const opOf = l => l.dir === 'both' ? '<->' : l.dir === 'none' ? '--' : '->';
      const kn = { ctrl: '指令', wired: '有线', radio: '无线', sat: '卫通', data: '', plain: '关联' };
      for (const l of links) out.push(`- ${l.a} ${opOf(l)} ${l.b}${l.label ? ' : ' + l.label : ''}${kn[l.kind] ? ' [' + kn[l.kind] + ']' : ''}`);
    }
    if (notes.length) out.push('', ...notes);
    return out.join('\n').replace(/^\n+/, '');
  }
  function looksStructured(text) {
    const lines = String(text || '').split('\n');
    return lines.some(l => /^\s*(#{1,6}\s|[-*+•]\s*\S|\d+[.、)）]\s*\S|\|.+\||>\s?\S)/.test(l)) || lines.some(l => hasArrow(l));
  }

  /* ---------------- IR → 图页 ---------------- */
  function containerMode(items, pageMover) {
    const leaves = items.filter(i => !i.children.length);
    if (!leaves.length) return { equip: false };
    const phys = leaves.filter(i => i._icon && !i._icon.startsWith('lib:') ? true : i._icon && (PHYS_CATS.includes(iconCat(i._icon.slice(4))) || PHYS_KEYS.has(i._icon.slice(4))));
    const mover = leaves.some(i => i._icon && i._icon.startsWith('lib:') && MOVER_CATS.includes(iconCat(i._icon.slice(4))));
    const ratio = phys.length / leaves.length;
    return { equip: ratio >= 0.6 && (mover || pageMover) };
  }
  function assignIcons(items, warnings) {
    for (const it of items) {
      it._icon = null; it._weak = false;
      if (it.icon) {
        const r = lookupIcon(it.icon);
        if (r.key) it._icon = r.key; else if (r.miss) warnings.push(`未找到图标“${it.icon}”（${it.text}）`);
      } else if (!it.children.length) {
        const m = matchIcon(it.text);
        if (m) { it._icon = 'lib:' + m.key; it._weak = m.weak; }
      }
      if (it.children.length) assignIcons(it.children, warnings);
    }
    /* weak (concept) matches only kept when most siblings also got an icon — keeps rows consistent */
    const leaves = items.filter(i => !i.children.length);
    const withIcon = leaves.filter(i => i._icon).length;
    if (withIcon < leaves.length / 2) leaves.forEach(i => { if (i._weak && !i.icon) i._icon = null; });
  }
  function itemNeedW(it, equip) {
    if (it.children.length) { const k = it.children.length; return Math.max(200, Math.min(k, 4) * 108 + 16); }
    if (equip || it.form === 'equip') return 140;
    return clamp(measure(firstLine(it.text), 13, false) + (it._icon ? 56 : 40), 120, 210);
  }
  function buildIRPage(ir, pageId, isRoot, warnings) {
    const page = { id: pageId, name: '', nodes: [], links: [], view: null };
    const allItems = [];
    const walk = arr => arr.forEach(i => { allItems.push(i); walk(i.children); });
    for (const b of ir.bands) { walk(b.items); b.lanes.forEach(l => walk(l.items)); }
    for (const b of ir.bands) { assignIcons(b.items, warnings); b.lanes.forEach(l => assignIcons(l.items, warnings)); }
    const leaves = allItems.filter(i => !i.children.length);
    const pageMover = leaves.some(i => i._icon && i._icon.startsWith('lib:') && MOVER_CATS.includes(iconCat(i._icon.slice(4))));
    let seq = 0;
    const N = o => { const n = mkNode(Object.assign({ x: (seq += 4), y: 0 }, o)); page.nodes.push(n); return n; };
    const title = ir.title || (isRoot ? '' : (ir.attach ? ir.attach + ' 内部构成' : ''));
    if (title) N({ type: 'text', role: 'title', text: title, size: isRoot ? 24 : 22, bold: true, w: Math.ceil(measure(title, isRoot ? 24 : 22, true) + 24), h: 36, y: -80 });
    if (ir.subtitle) N({ type: 'text', role: 'subtitle', text: ir.subtitle, size: 13, color: 'muted', w: Math.ceil(measure(ir.subtitle, 13, false) + 20), h: 22, y: -40 });
    page.name = ir.title || (ir.attach ? ir.attach + ' · 内部构成' : '总图');
    /* width */
    const rowNeed = (items, equip) => items.reduce((s, it) => s + itemNeedW(it, equip), 0) + Math.max(0, items.length - 1) * 28;
    let W = 960;
    const modes = new Map();
    for (const b of ir.bands) {
      const containers = [b.items, ...b.lanes.map(l => l.items)];
      for (const items of containers) {
        const md = containerMode(items, pageMover); modes.set(items, md);
        const extra = items === b.items ? BAND_TW + 40 : BAND_TW + 12 + 96 + 24;
        W = Math.max(W, rowNeed(items, md.equip) + extra);
      }
    }
    W = snapv(Math.min(W, 2600));
    let Y = 0;
    const mkItem = (it, parent, x, y, equip) => {
      if (it.children.length) {
        const g = N({ type: 'group', text: it.text, status: it.status, parent: parent.id, x, y, w: Math.max(200, Math.min(it.children.length, 4) * 108 + 16), h: 100 });
        const sub = it.children;
        const md = containerMode(sub, pageMover);
        sub.forEach((c, j) => mkItem(c, g, x + 8 + j * 4, y + 30 + j * 0.01, md.equip));
        it._node = g; return g;
      }
      const asEquip = it.form === 'equip' || (it.form !== 'box' && equip && it._icon);
      const n = asEquip
        ? N({ type: 'equip', text: it.text, status: it.status, icon: it._icon, parent: parent.id, x, y, w: 104, h: 100, size: 12, noBox: true })
        : N({ type: 'rect', text: it.text, status: it.status, icon: it._icon, parent: parent.id, x, y, w: 120, h: 36, size: parent.type === 'group' ? 12 : 13 });
      it._node = n; return n;
    };
    for (const b of ir.bands) {
      const band = N({ type: 'band', text: b.text || (b.implicit ? (ir.bands.length > 1 ? '其他' : '组成') : '分组'), status: b.status || 'base', x: 0, y: Y, w: W, h: 100 });
      b._node = band;
      let ly = Y + 6;
      for (const l of b.lanes) {
        const lane = N({ type: 'lane', text: l.text, parent: band.id, x: 40, y: ly, w: W - 46, h: 52 });
        l._node = lane;
        const md = modes.get(l.items) || { equip: false };
        l.items.forEach((it, i) => mkItem(it, lane, 150 + i * 160, ly + 8, md.equip));
        ly += 200;
      }
      const md = modes.get(b.items) || { equip: false };
      b.items.forEach((it, i) => mkItem(it, band, 60 + i * 160, ly + 8, md.equip));
      Y = ly + 400;
    }
    /* links */
    const cands = page.nodes.filter(n => !['text', 'note', 'legend'].includes(n.type));
    const rank = n => ({ band: 3, lane: 2, group: 1 })[n.type] || 0;
    const resolve = q => {
      q = String(q || '').trim(); if (!q) return null;
      let c = cands.filter(n => firstLine(n.text) === q);
      if (!c.length) { const nq = normName(q); if (!nq) return null; c = cands.filter(n => normName(n.text) === nq);
        if (!c.length) {
          let best = null, bd = 1e9;
          for (const n of cands) {
            const t = normName(n.text); if (!t) continue;
            if (t.includes(nq) || nq.includes(t)) {
              const r = Math.min(t.length, nq.length) / Math.max(t.length, nq.length);
              if (r < 0.34 || Math.min(t.length, nq.length) < 2) continue;
              const d = Math.abs(t.length - nq.length) + rank(n) * 0.5;
              if (d < bd) { bd = d; best = n; }
            }
          }
          return best;
        }
      }
      c.sort((a, b) => rank(a) - rank(b));
      const same = c.filter(n => rank(n) === rank(c[0]));
      if (same.length > 1) c[0]._dups = same.map(n => n.id);
      return c[0];
    };
    const seen = new Set();
    for (const l of ir.links) {
      const a = resolve(l.a), b = resolve(l.b);
      if (!a || !b) { warnings.push(`连接“${l.a} → ${l.b}”：找不到“${!a ? l.a : l.b}”`); continue; }
      if (a === b) continue;
      const k = a.id + '|' + b.id + '|' + l.kind;
      if (seen.has(k)) continue; seen.add(k);
      const lk = { id: uid(), from: a.id, to: b.id, dir: l.dir, kind: l.kind, route: 'ortho', label: l.label || '' };
      if (a._dups || b._dups) lk._alt = { from: a._dups || [a.id], to: b._dups || [b.id] };
      delete a._dups; delete b._dups;
      page.links.push(lk);
    }
    if (ir.notes.length) N({ type: 'note', role: 'note', size: 12, w: 900, h: 56, text: ir.notes.join('\n') });
    const anyStatus = page.nodes.some(n => n.status && n.status !== 'base' && !['band', 'lane'].includes(n.type)) || page.nodes.some(n => n.type === 'band' && n.status !== 'base');
    if (page.links.length || anyStatus) N({ type: 'legend', role: 'legend', w: 200, h: 60 });
    ir._resolve = resolve;
    return page;
  }
  /* build every IR page; returns {pages:[page], root, warnings, stats}. Pages are beautified via a temporary registration. */
  function buildAll(irPages, rootId, opts = {}) {
    const warnings = [];
    irPages.forEach(p => warnings.push(...p.warnings));
    const built = [];
    irPages.forEach((ir, i) => {
      if (i > 0 && !ir.bands.length && !ir.title) return;
      const id = i === 0 ? rootId : 'p' + uid();
      built.push({ ir, page: buildIRPage(ir, id, i === 0, warnings) });
    });
    /* attach drill-down pages */
    for (const b of built.slice(1)) {
      let host = null;
      for (const o of built) { if (o === b) break; const n = o.ir._resolve(b.ir.attach); if (n && !['band', 'lane'].includes(n.type)) { host = n; break; } }
      if (!host) {
        warnings.push(`展开页“${b.ir.attach}”：总图中找不到同名系统，已在总图中补一个入口框`);
        const rp = built[0].page;
        let band = rp.nodes.filter(n => n.type === 'band').pop();
        if (!band) { band = mkNode({ type: 'band', text: '组成', x: 0, y: 0, w: 960, h: 100 }); rp.nodes.push(band); }
        host = mkNode({ type: 'rect', text: b.ir.attach, parent: band.id, x: 9000, y: band.y + 900, w: 120, h: 36 });
        rp.nodes.push(host);
      }
      host.sub = b.page.id;
    }
    for (const { page } of built) {
      const had = doc.pages[page.id];
      doc.pages[page.id] = page;
      try { if (opts.uncross && typeof reduceCrossings === 'function') reduceCrossings(page); else beautify(page); }
      finally { if (had) doc.pages[page.id] = had; else delete doc.pages[page.id]; }
      /* same-named boxes (e.g. three “应用 APP”): connect the closest pair */
      const byId = Object.fromEntries(page.nodes.map(n => [n.id, n]));
      const ctr = n => [n.x + n.w / 2, n.y + n.h / 2];
      for (const l of page.links) {
        if (!l._alt) continue;
        let best = null, bd = Infinity;
        for (const f of l._alt.from) for (const t of l._alt.to) {
          if (f === t) continue;
          const [ax, ay] = ctr(byId[f]), [bx, by] = ctr(byId[t]); const dd = Math.hypot(ax - bx, (ay - by) * 1.5);
          if (dd < bd) { bd = dd; best = [f, t]; }
        }
        if (best) [l.from, l.to] = best;
        delete l._alt;
      }
    }
    const pages = built.map(b => b.page);
    const st = { pages: pages.length, bands: 0, lanes: 0, items: 0, links: 0 };
    for (const p of pages) for (const n of p.nodes) { if (n.type === 'band') st.bands++; else if (n.type === 'lane') st.lanes++; else if (!['text', 'note', 'legend'].includes(n.type)) st.items++; }
    pages.forEach(p => st.links += p.links.length);
    return { pages, root: pages[0], warnings, stats: st, title: irPages[0].title };
  }

  /* ---------------- 示例 ---------------- */
  const EXAMPLES = {
    md: `# 边海防无人化巡逻体系
> 岸基指挥中心统筹，无人机巡线、无人艇巡海、无人车巡边，人在环上监督

## 指挥控制
### 指挥层
- 边海防指挥中心、前沿指挥所 [新增]
### 任务层
- 任务规划 → 巡逻调度 → 目标处置 → 效果评估
### 智能层
- 智能辅助决策 [新增]
  - 目标识别智能体、航线规划智能体、告警研判智能体

## 服务支撑
### 公共服务
- 态势服务、视频服务、地图服务、北斗时空服务
### 数据资源
- 目标数据库、巡逻记录库、装备档案库

## 网云支撑
### 计算存储
- 边海防云平台 {图标:云平台}、边缘计算节点 {图标:服务器}
### 网络通信
- 光纤专网、自组网、数据链、卫通

## 连接
- 边海防指挥中心 <-> 前沿指挥所 : 指挥协同 [指令]
- 巡逻调度 -> 智能辅助决策 : 调度请求
- 智能辅助决策 -> 态势服务 : 研判结果
- 态势服务 <-> 目标数据库 : 目标信息

说明：示例为虚构体系，可在此基础上修改为本项目内容。

## 展开：自组网
# 自组网 · 装备构成
> 地面控制站经数据链与自组网接入空中、水面、地面无人节点
## 控制节点
- 操作员、地面控制站、自组网基站、卫通站
## 空中节点
- 中继无人机、察打一体无人机、侦察四旋翼、巡飞弹
## 水面地面
- 无人艇、巡逻作战艇、无人车、无人狗
## 连接
- 操作员 -> 地面控制站 : 指令 [指令]
- 地面控制站 <==> 自组网基站 : 光纤
- 自组网基站 <==> 卫通站
- 地面控制站 <~> 察打一体无人机 : 数据链
- 自组网基站 <-> 侦察四旋翼 : 自组网 [无线]
- 卫通站 <-> 巡飞弹 : 卫通 [卫通]
- 中继无人机 <~> 无人艇 : 数据链中继
- 侦察四旋翼 <~> 无人车 : 自组网
- 无人车 <~> 无人狗`,
    equip: `# 海上无人协同组网
> 岸基控制站经卫通、数据链与自组网接入空中、水面、水下无人节点
## 控制节点
- 指挥所、地面控制站、卫通站、自组网基站
## 空中节点
- 中继无人机、四旋翼无人机、垂起固定翼无人机
## 水面水下
- 无人艇 [新增]、无人艇母船、无人潜航器
## 连接
- 指挥所 ==> 地面控制站 : 光纤
- 地面控制站 --> 中继无人机 : 任务指令
- 卫通站 <-> 无人艇母船 : 卫通 [卫通]
- 自组网基站 ~> 四旋翼无人机, 垂起固定翼无人机 : 自组网
- 中继无人机 <~> 无人艇 : 数据链中继
- 无人艇母船 -- 无人潜航器 : 水声通信`,
    prose: `无人集群指挥控制体系分为指挥控制层、网络通信层和无人平台层。指挥控制层包括指挥所、地面控制站和智能体服务器。网络通信层由卫通站、自组网基站和数据链电台组成。无人平台层包括察打一体无人机、四旋翼无人机、无人艇和无人车。指挥所通过光纤连接地面控制站，地面控制站向察打一体无人机下发任务指令。无人艇通过数据链与地面控制站互联。四旋翼无人机通过自组网与无人车交互，并向智能体服务器上报态势数据。卫通站通过卫通连接察打一体无人机。
说明：本图由文字描述自动生成，可在画布上继续调整。`,
  };

  const SYNTAX_HTML = `
<table class="tg-syn">
<tr><td><code># 标题</code></td><td>图标题；<code>&gt; 副标题</code> 为副标题</td></tr>
<tr><td><code>## 名称</code></td><td>分组带（左侧竖排标题的大分区）</td></tr>
<tr><td><code>### 名称</code></td><td>层（泳道），属于上面最近的分组带</td></tr>
<tr><td><code>- 名称</code></td><td>系统框；一行多个用 <code>、</code> 或 <code>，</code> 隔开</td></tr>
<tr><td><code>&nbsp;&nbsp;- 子项</code></td><td>缩进的子项 → 上一行变成<b>子容器</b></td></tr>
<tr><td><code>- 容器：甲、乙</code></td><td>同上的简写：容器含甲、乙</td></tr>
<tr><td><code>- 发现 → 识别 → 跟踪</code></td><td>建框并依次连线</td></tr>
<tr><td><code>[新增]</code> <code>[重构]</code> / <code>[重点]</code></td><td>状态着色（新增／重点关注）</td></tr>
<tr><td><code>{图标:无人机}</code> <code>{icon:uav_quad}</code></td><td>指定图标；<code>{图标:无}</code> 不要图标；<code>{装备}</code> 画成装备卡、<code>{框}</code> 画成文字框</td></tr>
<tr><td><code>A -&gt; B : 标签</code></td><td>单向连线（也可写 <code>→</code>），冒号后为线上文字</td></tr>
<tr><td><code>A &lt;-&gt; B</code> · <code>A -- B</code></td><td>双向（<code>↔</code>）· 无箭头</td></tr>
<tr><td><code>--&gt;</code> <code>==&gt;</code> <code>~&gt;</code></td><td>指令流 · 有线／光纤 · 无线／数据链（双向写 <code>&lt;--&gt;</code> <code>&lt;==&gt;</code> <code>&lt;~&gt;</code>）</td></tr>
<tr><td><code>[指令] [有线] [光纤] [无线] [数据链] [卫通]</code></td><td>也可用方括号指定链路类型；默认为数据流</td></tr>
<tr><td><code>A -&gt; B, C, D</code></td><td>一对多连线</td></tr>
<tr><td><code>## 连接</code></td><td>可选：把连线集中写在这一段</td></tr>
<tr><td><code>## 展开：系统名</code></td><td>之后的内容画到该系统的内部结构页（⊕ 下钻）</td></tr>
<tr><td><code>说明：…</code> / <code>关键变化：…</code></td><td>图下方说明框；图例自动生成</td></tr>
<tr><td><code>| 层名 | 系统1 | 系统2 |</code></td><td>表格：每行一层</td></tr>
</table>
<div class="tg-hint">图标按名称自动匹配（无人机、无人艇、无人车、雷达、卫星、北斗、地面站、指挥所、服务器、数据库、云、数据链、自组网、智能体、操作员…）。一层或一个分组带里大多是装备时，自动画成装备图标卡。<br>
不写任何 # 和 - 时按<b>文字描述</b>理解：“X 分为／包括／由 A、B、C 组成”“第一层／顶层／底层是…”“A 通过数据链连接 B”“A 向 B 下发指令”“A 与 B 互联”等句式。</div>`;

  const LLM_SYSTEM = `你是体系架构图助手。把用户的描述转换为“织图文字成图方言”，只输出方言文本本身，不要任何解释，不要代码块围栏。
方言规则：
# 图标题
> 副标题（可选）
## 分组带名称（大分区，通常 2～5 个，如 应用／核心功能／服务支撑／网云支撑，或 控制节点／空中节点／水面地面）
### 层名称（分组带内的层，可选；装备组网图一般不用层，直接在 ## 下列装备）
- 系统名、系统名、系统名（一行可列多个，用顿号分隔）
- 容器名：子项、子项（容器内含若干子项）
状态标记写在名称后：[新增] 或 [重点]
连线写在最后的“## 连接”段，每行一条：
- A -> B : 标签（单向数据流）
- A <-> B : 标签（双向）
- A -- B（无箭头）
- A --> B（指令流）  A ==> B（有线/光纤）  A ~> B（无线/数据链）  A -> B [卫通]（卫通链路）
连线两端必须与上面写过的系统名完全一致。
如需说明，最后一行写：说明：……
如需画某系统的内部结构，另起“## 展开：系统名”，其后按同样规则书写该系统内部（可再写 # 标题）。
要求：名称简洁（2～12 字），保持用户原有术语，不要编造用户没有提到的系统；层次清楚，同一层内条目数一般不超过 8 个。`;

  /* ---------------- 界面 ---------------- */
  const CSS = `
#tg{position:fixed;top:0;right:0;bottom:0;left:0;z-index:25;background:rgba(10,15,22,.5);display:none;align-items:center;justify-content:center;padding:16px}
#tg.open{display:flex}
#tg .tg-box{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:12px;width:min(1320px,100%);height:min(880px,100%);display:flex;flex-direction:column;overflow:hidden;box-shadow:0 18px 48px rgba(0,0,0,.25)}
#tg .tg-head{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap}
#tg .tg-head strong{font-size:15px;letter-spacing:.04em}
#tg .tg-head .tg-sub{color:var(--muted);font-size:12px}
#tg .tg-body{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr)}
#tg .tg-left{display:flex;flex-direction:column;min-height:0;border-right:1px solid var(--line);padding:10px 12px;gap:8px;overflow:auto}
#tg .tg-right{display:flex;flex-direction:column;min-height:0;padding:10px 12px;gap:8px}
#tg .tg-bar{display:flex;gap:4px;flex-wrap:wrap;align-items:center}
#tg .tg-bar button{border-color:var(--line)}
#tg textarea.tg-in{flex:1;min-height:220px;width:100%;resize:none;font-family:var(--ui);font-size:13.5px;line-height:1.65;padding:10px 12px;border-radius:8px;tab-size:2}
#tg textarea.tg-in.drag{outline:2px dashed var(--accent);outline-offset:-4px}
#tg textarea.tg-struct{width:100%;min-height:140px;font-family:Consolas,'Courier New',monospace,var(--ui);font-size:12.5px;line-height:1.55;resize:vertical}
#tg details{border:1px solid var(--line);border-radius:8px;padding:6px 10px;background:var(--panel)}
#tg details>summary{cursor:pointer;color:var(--fg);font-weight:500;user-select:none}
#tg details[open]>summary{margin-bottom:6px}
#tg .tg-syn{border-collapse:collapse;width:100%;font-size:12px}
#tg .tg-syn td{border-top:1px solid var(--line);padding:4px 6px;vertical-align:top}
#tg .tg-syn td:first-child{white-space:nowrap;width:1%}
#tg code{font-family:Consolas,'Courier New',monospace;background:var(--hover);border-radius:3px;padding:0 3px;font-size:11.5px}
#tg .tg-hint{color:var(--muted);font-size:12px;line-height:1.7;margin-top:6px}
#tg .tg-prev{flex:1;min-height:200px;border:1px solid var(--line);border-radius:8px;background:var(--canvas);overflow:auto;display:flex;align-items:flex-start;justify-content:center;padding:10px}
#tg .tg-prev svg{width:100%;height:auto;max-width:100%;display:block;border-radius:4px}
#tg .tg-prev .tg-empty{color:var(--muted);align-self:center;text-align:center;line-height:1.8}
#tg .tg-tabs{display:flex;gap:4px;flex-wrap:wrap}
#tg .tg-tabs button{font-size:12px;padding:3px 8px;border-color:var(--line)}
#tg .tg-report{font-size:12.5px;line-height:1.7}
#tg .tg-report .ok{color:var(--fg)}
#tg .tg-report ul{margin:2px 0 0;padding-left:18px;color:#B4691A;max-height:96px;overflow:auto}
#tg .tg-foot{display:flex;gap:10px;align-items:center;padding:10px 14px;border-top:1px solid var(--line);flex-wrap:wrap}
#tg .tg-modes{display:flex;gap:10px;flex-wrap:wrap}
#tg .tg-modes label{display:flex;gap:4px;align-items:center;cursor:pointer;white-space:nowrap}
#tg .tg-set{display:none;border-bottom:1px solid var(--line);padding:10px 14px;background:var(--hover);gap:8px;flex-direction:column}
#tg .tg-set.open{display:flex}
#tg .tg-set .row label{width:84px}
#tg .tg-tip{display:none;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:6px;padding:8px 10px;font-size:12.5px;line-height:1.75;background:var(--accent-soft)}
#tg .tg-tip.show{display:block}
#tg .tg-mic.rec{background:#C2412D;color:#fff;border-color:#C2412D}
#tg .tg-mic.rec::before{content:'';width:8px;height:8px;border-radius:50%;background:#fff;animation:tgpulse 1s infinite}
@keyframes tgpulse{50%{opacity:.25}}
#tg .tg-status{color:var(--muted);font-size:12px}
#tg .tg-unx{display:flex;gap:4px;align-items:center;cursor:pointer;color:var(--muted);white-space:nowrap}
#tg .tg-status.err{color:var(--danger)}
#tg .tg-menu{position:relative}
#tg .tg-menu .tg-dd{position:absolute;top:calc(100% + 4px);left:0;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:4px;display:none;flex-direction:column;min-width:220px;z-index:3;box-shadow:0 8px 24px rgba(0,0,0,.14)}
#tg .tg-menu.open .tg-dd{display:flex}
#tg .tg-menu .tg-dd button{justify-content:flex-start;border-color:transparent}
@media (max-width:860px){
  #tg{padding:0}
  #tg .tg-box{border-radius:0;height:100%;width:100%}
  #tg .tg-body{grid-template-columns:1fr;grid-template-rows:max-content max-content;overflow:auto;display:grid}
  #tg .tg-left{border-right:none;border-bottom:1px solid var(--line);overflow:visible;padding:10px 16px;min-height:auto}
  #tg .tg-right{padding:10px 16px;min-height:auto}
  #tg .tg-head .tg-sub{display:none}
  #tg textarea.tg-in{min-height:180px;flex:none;height:34vh}
  #tg .tg-prev{min-height:220px;flex:none}
  #tg .tg-foot,#tg .tg-head,#tg .tg-set{padding-left:16px;padding-right:16px}
  #tg .tg-syn td:first-child{white-space:normal}
}
@media (prefers-reduced-motion:reduce){#tg .tg-mic.rec::before{animation:none}}`;

  const HTML = `
<div class="tg-box" role="dialog" aria-modal="true" aria-labelledby="tg-title">
  <div class="tg-head">
    <strong id="tg-title">文字成图</strong><span class="tg-sub">输入、粘贴 Markdown 或语音口述，自动生成分组带、层、系统框与连线</span>
    <span class="spacer" style="flex:1"></span>
    <button id="tg-gear" title="理解方式设置">⚙ <span id="tg-mode-name">规则解析（离线）</span></button>
    <button id="tg-close" title="关闭（Esc）">关闭</button>
  </div>
  <div class="tg-set" id="tg-set">
    <div class="tg-modes" id="tg-engine">
      <label><input type="radio" name="tg-eng" value="rule" checked> 规则解析（离线）</label>
      <label><input type="radio" name="tg-eng" value="llm"> 内网大模型（OpenAI 兼容接口）</label>
      <label id="tg-eng-online" hidden><input type="radio" name="tg-eng" value="online"> 在线理解（claude.ai）</label>
    </div>
    <div id="tg-llm" hidden>
      <div class="row"><label>接口地址</label><input type="text" id="tg-base" placeholder="如 http://10.1.2.3:8000/v1"></div>
      <div class="row"><label>模型名称</label><input type="text" id="tg-model" placeholder="如 qwen2.5-72b-instruct"></div>
      <div class="row"><label>API Key</label><input type="text" id="tg-key" placeholder="无鉴权可留空" autocomplete="off" spellcheck="false"></div>
      <div class="tg-hint">调用 <code>POST {接口地址}/chat/completions</code>，返回的结构化文本先显示在“转换后的结构化文本”中，确认后再上图。设置仅保存在本机浏览器。</div>
    </div>
    <div id="tg-online-hint" class="tg-hint" hidden>使用 claude.ai 在线理解自由文字（仅在线预览版可用，首次使用会请求授权）。</div>
  </div>
  <div class="tg-body">
    <div class="tg-left">
      <div class="tg-bar">
        <div class="tg-menu" id="tg-exm"><button id="tg-ex">示例 ▾</button><div class="tg-dd">
          <button data-ex="md">Markdown：边海防无人化巡逻体系（含下钻页）</button>
          <button data-ex="equip">Markdown：海上无人协同组网（装备卡）</button>
          <button data-ex="prose">文字描述：无人集群指挥控制体系</button>
        </div></div>
        <button id="tg-clear">清空</button>
        <button id="tg-mic" class="tg-mic" title="语音输入（中文）">🎤 语音输入</button>
        <button id="tg-file" title="导入 .md / .txt 文件，也可直接拖入输入框">导入文件</button>
        <input type="file" id="tg-f" accept=".md,.markdown,.txt,text/plain,text/markdown" hidden>
      </div>
      <div class="tg-tip" id="tg-tip"></div>
      <textarea class="tg-in" id="tg-in" spellcheck="false" placeholder="# 标题&#10;## 分组带&#10;### 层&#10;- 系统甲、系统乙 [新增]&#10;- 系统甲 -> 系统乙 : 数据&#10;&#10;也可直接写一段文字，例如：&#10;指挥控制体系分为指挥层、通信层和平台层。指挥层包括指挥所和地面控制站……&#10;&#10;可把 .md／.txt 文件拖到这里。"></textarea>
      <details id="tg-structbox"><summary>转换后的结构化文本 <span class="tg-status" id="tg-struct-st"></span></summary>
        <textarea class="tg-struct" id="tg-struct" spellcheck="false"></textarea>
        <div class="tg-bar" style="margin-top:6px"><button id="tg-usestruct">用它替换输入框</button><span class="tg-hint" style="margin:0">可直接在此修改后再生成。</span></div>
      </details>
      <details id="tg-synbox"><summary>语法说明</summary>${SYNTAX_HTML}</details>
    </div>
    <div class="tg-right">
      <div class="tg-tabs" id="tg-tabs"></div>
      <div class="tg-prev" id="tg-prev"><div class="tg-empty">在左侧输入后，这里实时预览</div></div>
      <div class="tg-report" id="tg-report"></div>
    </div>
  </div>
  <div class="tg-foot">
    <div class="tg-modes" id="tg-apply">
      <label><input type="radio" name="tg-ap" value="replace" checked> 替换当前图</label>
      <label><input type="radio" name="tg-ap" value="page"> 作为新页面追加</label>
      <label><input type="radio" name="tg-ap" value="add"> 加到当前页</label>
    </div>
    <label class="tg-unx" title="按连线关系自动调整层内顺序，减少连线交叉（会改变书写顺序）"><input type="checkbox" id="tg-unx"> 自动减少交叉</label>
    <span class="tg-status" id="tg-msg"></span>
    <span style="flex:1"></span>
    <button id="tg-go" class="primary" title="Ctrl+Enter">识别并生成</button>
  </div>
</div>`;

  let root = null, timer = null, last = null, prevPage = 0, structPinned = false, aiReady = false, rec = null, sampleFn = null, busy = false;
  const q = s => root.querySelector(s);
  function ensureUI() {
    if (root) return;
    const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    root = document.createElement('div'); root.id = 'tg'; root.innerHTML = HTML; document.body.appendChild(root);
    const cfg = lsGet();
    const setEng = v => { const r = q(`input[name=tg-eng][value=${v}]`); if (r && !r.closest('[hidden]')) r.checked = true; };
    setEng(cfg.engine || 'rule');
    q('#tg-base').value = cfg.base || ''; q('#tg-model').value = cfg.model || ''; q('#tg-key').value = cfg.key || '';
    q('#tg-unx').checked = !!cfg.uncross; q('#tg-unx').addEventListener('change', () => { saveCfg(); schedule(0); });
    if (typeof reduceCrossings !== 'function') q('.tg-unx').hidden = true;
    if (cfg.apply) { const r = q(`input[name=tg-ap][value=${cfg.apply}]`); if (r) r.checked = true; }
    syncEngine();
    /* keep editor shortcuts (Delete, Ctrl+Z…) from reaching the canvas while the dialog is open */
    root.addEventListener('keydown', e => {
      e.stopPropagation();
      if (e.key === 'Escape') { e.preventDefault(); const m = q('#tg-exm'); if (m.classList.contains('open')) m.classList.remove('open'); else close(); }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); go(); }
    });
    root.addEventListener('keyup', e => e.stopPropagation());
    /* focus outside the dialog (e.g. on <body> after a menu click): still route keys here, never to the canvas */
    window.addEventListener('keydown', e => {
      if (!root.classList.contains('open') || root.contains(e.target)) return;
      e.stopPropagation();
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); go(); }
      else if (['Delete', 'Backspace', ' '].includes(e.key) || e.ctrlKey || e.metaKey) { if (!/^[cvx]$/i.test(e.key)) e.preventDefault(); }
    }, true);
    root.addEventListener('mousedown', e => { if (e.target === root) close(); });
    root.addEventListener('click', e => { if (!e.target.closest('#tg-exm')) q('#tg-exm').classList.remove('open'); });
    q('#tg-close').onclick = close;
    q('#tg-gear').onclick = () => q('#tg-set').classList.toggle('open');
    q('#tg-engine').addEventListener('change', () => { syncEngine(); saveCfg(); resetAI(); schedule(0); });
    ['#tg-base', '#tg-model', '#tg-key'].forEach(s => q(s).addEventListener('change', saveCfg));
    q('#tg-apply').addEventListener('change', saveCfg);
    q('#tg-ex').onclick = e => { e.stopPropagation(); q('#tg-exm').classList.toggle('open'); };
    q('#tg-exm .tg-dd').addEventListener('click', e => {
      const b = e.target.closest('[data-ex]'); if (!b) return;
      q('#tg-exm').classList.remove('open');
      setInput(EXAMPLES[b.dataset.ex]);
      q('#tg-in').focus(); q('#tg-in').setSelectionRange(0, 0); q('#tg-in').scrollTop = 0;
    });
    q('#tg-clear').onclick = () => { setInput(''); q('#tg-in').focus(); };
    const ta = q('#tg-in');
    ta.addEventListener('input', () => { structPinned = false; resetAI(); schedule(); });
    ta.addEventListener('keydown', e => {
      if (e.key === 'Tab' && !e.ctrlKey && !e.altKey) { e.preventDefault(); const s = ta.selectionStart, en = ta.selectionEnd; ta.setRangeText('  ', s, en, 'end'); ta.dispatchEvent(new Event('input')); }
    });
    ta.addEventListener('dragover', e => { if ([...(e.dataTransfer?.types || [])].includes('Files')) { e.preventDefault(); ta.classList.add('drag'); } });
    ta.addEventListener('dragleave', () => ta.classList.remove('drag'));
    ta.addEventListener('drop', e => { ta.classList.remove('drag'); const f = e.dataTransfer?.files?.[0]; if (f) { e.preventDefault(); readFile(f); } });
    q('#tg-file').onclick = () => q('#tg-f').click();
    q('#tg-f').addEventListener('change', e => { const f = e.target.files[0]; if (f) readFile(f); e.target.value = ''; });
    q('#tg-struct').addEventListener('input', () => { structPinned = true; schedule(); });
    q('#tg-usestruct').onclick = () => { const v = q('#tg-struct').value; if (!v.trim()) return; q('#tg-in').value = v; structPinned = false; resetAI(); schedule(0); };
    q('#tg-mic').onclick = toggleVoice;
    q('#tg-go').onclick = go;
    q('#tg-tabs').addEventListener('click', e => { const b = e.target.closest('[data-pg]'); if (b) { prevPage = +b.dataset.pg; drawPreview(); } });
  }
  function saveCfg() {
    lsSet({ engine: engine(), base: q('#tg-base').value.trim(), model: q('#tg-model').value.trim(), key: q('#tg-key').value.trim(), apply: applyMode(), uncross: uncross() });
  }
  const uncross = () => !!(root && q('#tg-unx').checked);
  const engine = () => (q('input[name=tg-eng]:checked') || {}).value || 'rule';
  const applyMode = () => (q('input[name=tg-ap]:checked') || {}).value || 'replace';
  function syncEngine() {
    const e = engine();
    q('#tg-llm').hidden = e !== 'llm'; q('#tg-online-hint').hidden = e !== 'online';
    q('#tg-mode-name').textContent = { rule: '规则解析（离线）', llm: '内网大模型', online: '在线理解' }[e];
    if (e !== 'rule' && !q('#tg-set').classList.contains('open')) q('#tg-set').classList.add('open');
    updateGoLabel();
  }
  function updateGoLabel() { q('#tg-go').textContent = engine() !== 'rule' && !aiReady ? (engine() === 'llm' ? '大模型识别' : '在线识别') : (engine() !== 'rule' ? '生成到画布' : '识别并生成'); }
  function resetAI() { if (aiReady) { aiReady = false; } updateGoLabel(); }
  function setInput(v) { const ta = q('#tg-in'); ta.value = v; structPinned = false; resetAI(); schedule(0); }
  function readFile(f) {
    if (!/\.(md|markdown|txt|text)$/i.test(f.name) && !/^text\//.test(f.type)) { msg('只支持 .md／.txt 文本文件', true); return; }
    const rd = new FileReader();
    rd.onload = () => { setInput(String(rd.result || '')); msg('已导入：' + f.name); };
    rd.onerror = () => msg('文件读取失败', true);
    rd.readAsText(f, 'utf-8');
  }
  function msg(t, err) { const m = q('#tg-msg'); m.textContent = t || ''; m.classList.toggle('err', !!err); }

  /* current dialect text (input → maybe converted) */
  function currentDialect() {
    const src = q('#tg-in').value;
    if (structPinned || aiReady) return { text: q('#tg-struct').value, converted: true };
    if (!src.trim()) return { text: '', converted: false };
    if (looksStructured(src)) return { text: src, converted: false };
    return { text: proseToDialect(src), converted: true };
  }
  function analyse() {
    const d = currentDialect();
    if (!structPinned && !aiReady) {
      q('#tg-struct').value = d.converted ? d.text : '';
      q('#tg-struct-st').textContent = d.converted ? '（文字描述已自动转换）' : '（输入已是结构化文本）';
      if (d.converted && q('#tg-in').value.trim()) q('#tg-structbox').open = true;
    }
    if (!d.text.trim()) return null;
    try { return buildAll(parseDialect(d.text), '__tgprev', { uncross: uncross() }); }
    catch (err) { console.error(err); return { error: err.message || String(err) }; }
  }
  function schedule(ms = 300) { clearTimeout(timer); timer = setTimeout(() => { last = analyse(); if (prevPage >= (last?.pages?.length || 1)) prevPage = 0; drawPreview(); }, ms); }
  function drawPreview() {
    const box = q('#tg-prev'), rep = q('#tg-report'), tabs = q('#tg-tabs');
    if (!last) { box.innerHTML = '<div class="tg-empty">在左侧输入后，这里实时预览<br><small>不会改动画布，点“识别并生成”才上图</small></div>'; rep.innerHTML = ''; tabs.innerHTML = ''; return; }
    if (last.error) { box.innerHTML = `<div class="tg-empty">解析出错：${esc(last.error)}</div>`; rep.innerHTML = ''; tabs.innerHTML = ''; return; }
    const pages = last.pages;
    tabs.innerHTML = pages.length > 1 ? pages.map((p, i) => `<button data-pg="${i}" class="${i === prevPage ? 'on' : ''}">${i ? '⊕ ' : ''}${esc(p.name || (i ? '展开页' : '总图'))}</button>`).join('') : '';
    const p = pages[prevPage] || pages[0];
    if (!p.nodes.length) { box.innerHTML = '<div class="tg-empty">没有识别到可绘制的内容</div>'; }
    else {
      const b = contentBBox(p), pad = 16;
      const saved = cur; let inner = '';
      doc.pages[p.id] = p; cur = p.id;
      try { inner = diagramSVG(p, true, 'tgp'); } finally { cur = saved; delete doc.pages[p.id]; }
      box.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${b.x - pad} ${b.y - pad} ${b.w + pad * 2} ${b.h + pad * 2}" style="background:${T().bg};aspect-ratio:${(b.w + pad * 2) / (b.h + pad * 2)}">${inner}</svg>`;
    }
    const s = last.stats;
    const w = [...new Set(last.warnings)];
    rep.innerHTML = `<div class="ok">识别结果：${s.pages > 1 ? `${s.pages} 页（含 ${s.pages - 1} 个展开页）· ` : ''}${s.bands} 个分组带 · ${s.lanes} 层 · ${s.items} 个系统 · ${s.links} 条连接</div>` +
      (w.length ? `<ul>${w.slice(0, 30).map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : '');
  }

  /* ---------------- AI 理解 ---------------- */
  function stripFence(t) {
    t = String(t || '').trim();
    const m = t.match(/```[a-zA-Z]*\n([\s\S]*?)```/); if (m) t = m[1].trim();
    return t;
  }
  function llmCfg() {
    if (root) return { base: q('#tg-base').value.trim(), model: q('#tg-model').value.trim(), key: q('#tg-key').value.trim() };
    const c = lsGet(); return { base: (c.base || '').trim(), model: (c.model || '').trim(), key: (c.key || '').trim() };
  }
  function setLlmCfg(o) {
    const c = Object.assign(lsGet(), o); lsSet(c);
    if (root) { q('#tg-base').value = c.base || ''; q('#tg-model').value = c.model || ''; q('#tg-key').value = c.key || ''; }
  }
  async function callLLM(text, system = LLM_SYSTEM, opt = {}) {
    const { base, model, key } = llmCfg();
    if (!base) throw new Error('请先在 ⚙ 设置中填写接口地址');
    if (!model) throw new Error('请先在 ⚙ 设置中填写模型名称');
    const url = /\/chat\/completions\/?$/.test(base) ? base : base.replace(/\/+$/, '') + '/chat/completions';
    const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), opt.timeout || 120000);
    let res;
    try {
      res = await fetch(url, { method: 'POST', signal: ctl.signal, headers: Object.assign({ 'Content-Type': 'application/json' }, key ? { Authorization: 'Bearer ' + key } : {}), body: JSON.stringify(Object.assign({ model, temperature: 0.2, stream: false, messages: [{ role: 'system', content: system }, { role: 'user', content: text }] }, opt.maxTokens ? { max_tokens: opt.maxTokens } : {})) });
    } catch (e) {
      clearTimeout(to);
      throw new Error(e.name === 'AbortError' ? `大模型响应超时（${Math.round((opt.timeout || 120000) / 1000)} 秒）` : '无法连接大模型接口：' + url + '（请检查地址、网络或跨域 CORS 设置）');
    }
    clearTimeout(to);
    let body = ''; try { body = await res.text(); } catch (_) { }
    if (!res.ok) throw new Error(`大模型接口返回 ${res.status}${res.status === 401 || res.status === 403 ? '（鉴权失败，请检查 API Key）' : res.status === 404 ? '（地址或模型名不正确）' : ''}：${body.slice(0, 160)}`);
    let data; try { data = JSON.parse(body); } catch (_) { throw new Error('大模型返回的不是 JSON：' + body.slice(0, 120)); }
    const out = data?.choices?.[0]?.message?.content ?? data?.choices?.[0]?.text ?? '';
    if (!String(out).trim()) throw new Error('大模型返回为空');
    return stripFence(String(out).replace(/<think>[\s\S]*?<\/think>/g, ''));
  }
  async function callOnline(text) {
    if (!sampleFn) throw new Error('在线理解不可用（仅在 claude.ai 在线预览中提供）');
    let r;
    try { r = await sampleFn(LLM_SYSTEM + '\n\n用户描述如下：\n' + text, { modelTier: 'default' }); }
    catch (e) {
      const c = e && e.code;
      throw new Error(c === 'not_granted' ? '未获授权使用在线理解' : c === 'rate_limited' ? '请求过于频繁，请稍后再试' : '在线理解失败：' + (e && e.message || e));
    }
    const t = stripFence(r && r.text);
    if (!t.trim()) throw new Error('在线理解返回为空');
    return t;
  }

  /* ---------------- 生成到画布 ---------------- */
  async function go() {
    if (busy) return;
    const src = q('#tg-in').value;
    const eng = engine();
    if (eng !== 'rule' && !aiReady && !structPinned) {
      if (!src.trim()) { msg('请先输入内容', true); return; }
      busy = true; const btn = q('#tg-go'); btn.disabled = true; msg(eng === 'llm' ? '正在请求内网大模型…' : '正在在线理解…');
      try {
        const t = eng === 'llm' ? await callLLM(src) : await callOnline(src);
        q('#tg-struct').value = t; q('#tg-structbox').open = true; q('#tg-struct-st').textContent = '（由大模型转换，可修改）';
        aiReady = true; updateGoLabel(); last = analyse(); prevPage = 0; drawPreview();
        msg('已转换，请核对右侧预览后点“生成到画布”');
      } catch (e) { msg(e.message || String(e), true); }
      finally { busy = false; btn.disabled = false; }
      return;
    }
    clearTimeout(timer);
    const d = currentDialect();
    if (!d.text.trim()) { msg('请先输入内容', true); return; }
    let res;
    try { res = buildAll(parseDialect(d.text), 'root', { uncross: uncross() }); } catch (e) { console.error(e); msg('解析出错：' + (e.message || e), true); return; }
    if (!res.root.nodes.length) { msg('没有识别到可绘制的内容', true); return; }
    apply(res, applyMode());
    close();
    const s = res.stats;
    toast(`已生成：${s.bands} 个分组带、${s.lanes} 层、${s.items} 个系统、${s.links} 条连接（Ctrl+Z 可撤销）`);
  }
  function apply(res, mode) {
    const [rootP, ...subs] = res.pages;
    checkpoint();
    if (mode === 'replace' && cur === 'root') {
      const d = { name: res.title || doc.name || '体系图', layout: Compact.cfg(), theme: doc.theme, statusLabels: { ...doc.statusLabels }, custom: doc.custom, lastKind: doc.lastKind || 'data', pages: {} };
      rootP.id = 'root'; rootP.name = '总图';
      d.pages.root = rootP; subs.forEach(p => d.pages[p.id] = p);
      loadDoc(d);
      return;
    }
    const bag = {};
    subs.forEach(p => bag[p.id] = p);
    if (mode === 'replace') {
      const P0 = doc.pages[cur];
      P0.nodes = rootP.nodes; P0.links = rootP.links; P0.view = null; if (res.title) P0.name = res.title;
      hangUnder(cur, bag);
      clearSel(); render(); fit(); return;
    }
    if (mode === 'page') {
      const pg = doc.pages[cur];
      let host = sel.size === 1 ? nodeById([...sel][0]) : null;
      if (host && (isCont(host) || ['text', 'note', 'legend'].includes(host.type) || host.sub)) host = null;
      rootP.id = 'p' + uid(); rootP.name = res.title || '文字成图';
      if (!host) {
        const b = contentBBox(pg), label = res.title || '文字成图';
        const w = snapv(clamp(measure(label, 13, true) + 40, 140, 320));
        host = mkNode({ type: 'round', text: label, bold: true, x: snapv(pg.nodes.length ? b.x + b.w - w : 0), y: snapv(pg.nodes.length ? b.y + b.h + 32 : 0), w, h: 40 });
        pg.nodes.push(host);
      }
      bag[rootP.id] = rootP;
      hangPages(bag, rootP.id, cur);
      setDoor(host, rootP.id);
      clearSel();
      showPage(rootP.id);
      return;
    }
    /* add to current page, below existing content */
    const pg = doc.pages[cur];
    const nb = contentBBox(rootP);
    let dx = 0, dy = 0;
    if (pg.nodes.length) { const b = contentBBox(pg); dx = b.x - nb.x; dy = b.y + b.h + 80 - nb.y; }
    const hasLegend = pg.nodes.some(n => n.type === 'legend'), hasNote = pg.nodes.some(n => n.role === 'note');
    const add = rootP.nodes.filter(n => !(n.type === 'legend' && hasLegend));
    for (const n of add) {
      n.x = snapv(n.x + dx); n.y = snapv(n.y + dy);
      if (n.role === 'title' || n.role === 'subtitle' || (n.role === 'note' && hasNote) || (n.type === 'legend')) { if (pg.nodes.length) delete n.role; }
    }
    pg.nodes.push(...add); pg.links.push(...rootP.links);
    hangUnder(cur, bag);
    selectNodes(add.filter(n => !n.parent).map(n => n.id));
    render(); fit();
  }

  /* ---------------- 语音输入 ---------------- */
  const VOICE_TIP = `<b>当前环境无法使用网页语音识别</b>（离线／内网浏览器不带在线语音服务），可改用系统语音输入：<br>
· <b>Windows 10／11</b>：点一下输入框，按 <code>Win</code>+<code>H</code> 开始口述；<br>
· <b>麒麟／统信等国产系统</b>：使用输入法自带的语音输入（如讯飞输入法、搜狗输入法的“语音”按钮）；<br>
· <b>macOS</b>：连按两下 <code>Fn</code> 键口述。<br>说完后点“识别并生成”。口述时可直接说“分为……包括……通过数据链连接……”，无需说符号。`;
  function voiceTip(extra) { const t = q('#tg-tip'); t.innerHTML = (extra ? `<div style="margin-bottom:4px">${esc(extra)}</div>` : '') + VOICE_TIP + ` <button id="tg-tipx" style="float:right;padding:0 6px">知道了</button>`; t.classList.add('show'); q('#tg-tipx').onclick = () => t.classList.remove('show'); }
  function setMic(on) { const b = q('#tg-mic'); b.classList.toggle('rec', on); b.textContent = on ? ' 正在听写…点此停止' : '🎤 语音输入'; }
  function toggleVoice() {
    if (rec) { try { rec.stop(); } catch (_) { } return; }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { voiceTip('此浏览器不支持网页语音识别。'); return; }
    let r; try { r = new SR(); } catch (e) { voiceTip('语音识别初始化失败。'); return; }
    const ta = q('#tg-in');
    const base = ta.value + (ta.value && !/\n$/.test(ta.value) ? '\n' : '');
    let fin = '', failed = false;
    r.lang = 'zh-CN'; r.continuous = true; r.interimResults = true;
    r.onresult = e => {
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) { const x = e.results[i]; if (x.isFinal) fin += x[0].transcript + (/[。！？]$/.test(x[0].transcript) ? '' : '。'); else interim += x[0].transcript; }
      ta.value = base + fin + interim; structPinned = false; resetAI(); schedule(500);
    };
    r.onerror = e => {
      failed = true;
      const m = { 'not-allowed': '麦克风权限被拒绝。', 'service-not-allowed': '浏览器不允许使用语音服务。', network: '语音识别需要联网，当前网络不可用。', 'audio-capture': '没有检测到麦克风。', 'no-speech': '' }[e.error];
      if (m !== '') voiceTip(m || ('语音识别出错：' + e.error));
    };
    r.onend = () => { rec = null; setMic(false); if (!failed && fin) msg('语音已转为文字，可修改后生成'); };
    let got = false; const wd = setTimeout(() => { if (rec === r && !got && !failed) voiceTip('已开始听写，但 8 秒内没有收到识别结果。'); }, 8000);
    const oe = r.onend; r.onend = () => { clearTimeout(wd); oe(); };
    const or = r.onresult; r.onresult = e => { got = true; or(e); };
    try { r.start(); rec = r; setMic(true); q('#tg-tip').classList.remove('show'); msg('正在听写，说完点“停止”'); }
    catch (e) { voiceTip('语音识别无法启动。'); }
  }

  /* ---------------- 打开／关闭 ---------------- */
  let lastFocus = null;
  function open(initial) {
    ensureUI();
    lastFocus = document.activeElement;
    if ($('#editor') && $('#editor').style.display === 'block' && typeof commitEdit === 'function') commitEdit();
    root.classList.add('open');
    if (typeof initial === 'string') setInput(initial); else schedule(0);
    msg('');
    if (!sampleFn && window.claude && typeof window.claude.use === 'function') {
      Promise.resolve().then(() => window.claude.use('sample')).then(s => {
        if (typeof s === 'function') { sampleFn = s; q('#tg-eng-online').hidden = false; const c = lsGet(); if (c.engine === 'online') { q('input[name=tg-eng][value=online]').checked = true; syncEngine(); } }
      }).catch(() => { });
    }
    setTimeout(() => q('#tg-in').focus(), 30);
  }
  function close() {
    if (!root) return;
    if (rec) { try { rec.abort(); } catch (_) { } rec = null; setMic(false); }
    root.classList.remove('open');
    q('#tg-exm').classList.remove('open');
    if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (_) { }
  }

  window.openTextGen = open;
  window.closeTextGen = close;
  /* exposed for tests / other modules */
  window.TextGen = { parseDialect, proseToDialect, buildAll, matchIcon, looksStructured, lookupIcon, parseItemText, EXAMPLES, LLM_SYSTEM, SYNTAX_HTML, callLLM, llmCfg, setLlmCfg, apply };
})();
