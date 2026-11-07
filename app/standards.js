'use strict';
/* ============ 通用体系结构规范包（核心） ============
 * 依据 DoDAF 2.02／UAF／NAF v4 视点约定：视图类型、元素类型、编号、必填属性、规则检查、标题栏。
 * 数据约定见 STD_SPEC.md：page.view、doc.meta、doc.showCodes、node.etype/code/attrs、link.code/attrs、node.type==='tblock'。
 * 对外接口 window.Std（供 app.js 渲染／导出、std_templates.js 与 xlsxexport.js 使用）。
 */
(function () {
  /* family: 'dodaf' = DoDAF 2.02／UAF 体系结构视图；'it' = 信息系统架构（TOGAF／4A：业务、应用、数据、技术 + 部署、安全） */
  const VIEWS = {
    'OV-1': { family: 'dodaf', name: '高层作战概念图', etypes: ['op_node', 'performer', 'resource'], link: 'CN', linkName: '概念关联' },
    'OV-2': { family: 'dodaf', name: '作战资源流描述', etypes: ['op_node', 'performer'], link: 'NL', linkName: '需求线（资源流）' },
    'OV-5b': { family: 'dodaf', name: '作战活动模型', etypes: ['op_activity', 'performer'], link: 'AF', linkName: '活动流' },
    'SV-1': { family: 'dodaf', name: '系统接口描述', etypes: ['system', 'subsystem', 'op_node'], link: 'SI', linkName: '系统接口' },
    'SV-4': { family: 'dodaf', name: '系统功能描述', etypes: ['sys_function', 'system'], link: 'FF', linkName: '功能数据流' },
    'BIZ': { family: 'it', name: '业务架构图', etypes: ['biz_domain', 'biz_capability', 'biz_process', 'biz_role', 'biz_object'], link: 'BF', linkName: '业务流',
      hint: '分组带为业务域，带内子容器为业务能力，能力内为业务流程／活动；人员图标为业务角色，文档形状为业务对象。' },
    'APP': { family: 'it', name: '应用架构图', etypes: ['app_system', 'app_module', 'app_service', 'ext_system'], link: 'AI', linkName: '应用集成',
      hint: '子容器为应用系统，框内为应用模块；标题含“支撑／服务”的层内为应用服务；标题含“外部”的容器内为外部系统。集成连线须写集成方式／协议。' },
    'DATA': { family: 'it', name: '数据架构图', etypes: ['data_domain', 'data_entity', 'data_store', 'data_proc'], link: 'DF', linkName: '数据流',
      hint: '分组带为数据域；数据库类图标／圆柱体为数据存储，集成、计算类图标为数据处理，其余为数据实体／主题。数据流须写数据对象。' },
    'TECH': { family: 'it', name: '技术架构图', etypes: ['tech_layer', 'platform', 'tech_component', 'infra'], link: 'TD', linkName: '技术依赖',
      hint: '分组带为技术层，层内子容器为平台／中间件，其中为技术组件；服务器、存储、网络类图标为基础设施。' },
    'DEPLOY': { family: 'it', name: '部署架构图', etypes: ['zone', 'deploy_node', 'deploy_unit', 'net_device'], link: 'NC', linkName: '网络连接',
      hint: '分组带为网络区域／安全域（带内的层仅作排版），区域内子容器或图标为部署节点，节点内为部署单元；防火墙、网闸、交换机等为网络／边界设备。跨区域连接须经边界设备。' },
    'SEC': { family: 'it', name: '安全架构图', etypes: ['sec_domain', 'sec_control', 'protected_asset', 'sec_boundary'], link: 'AC', linkName: '访问控制关系',
      hint: '分组带为安全域（须标安全等级），域内为保护对象与安全措施；防火墙、网闸、VPN 等为边界防护设备。跨域访问须经边界防护设备。' },
  };
  const FAMILIES = [['dodaf', 'DoDAF／UAF 体系结构视图'], ['it', '信息系统架构（TOGAF／4A）']];
  const ETYPES = {
    op_node: { name: '作战节点', prefix: 'ON' },
    performer: { name: '执行者', prefix: 'PF' },
    op_activity: { name: '作战活动', prefix: 'OA' },
    resource: { name: '装备／资源', prefix: 'RS' },
    system: { name: '系统', prefix: 'SY' },
    subsystem: { name: '子系统', prefix: 'SS' },
    sys_function: { name: '系统功能', prefix: 'SF' },
    /* 信息系统架构 */
    biz_domain: { name: '业务域', prefix: 'BD' },
    biz_capability: { name: '业务能力', prefix: 'BC' },
    biz_process: { name: '业务流程／活动', prefix: 'BP' },
    biz_role: { name: '业务角色', prefix: 'BR' },
    biz_object: { name: '业务对象', prefix: 'BO' },
    app_system: { name: '应用系统', prefix: 'AP' },
    app_module: { name: '应用模块', prefix: 'AM' },
    app_service: { name: '应用服务', prefix: 'AS' },
    ext_system: { name: '外部系统', prefix: 'EX' },
    data_domain: { name: '数据域', prefix: 'DD' },
    data_entity: { name: '数据实体／主题', prefix: 'DE' },
    data_store: { name: '数据存储', prefix: 'DS' },
    data_proc: { name: '数据处理', prefix: 'DP' },
    tech_layer: { name: '技术层', prefix: 'TL' },
    platform: { name: '平台／中间件', prefix: 'PL' },
    tech_component: { name: '技术组件', prefix: 'TC' },
    infra: { name: '基础设施', prefix: 'IN' },
    zone: { name: '网络区域／安全域', prefix: 'ZN' },
    deploy_node: { name: '部署节点', prefix: 'DN' },
    deploy_unit: { name: '部署单元', prefix: 'DU' },
    net_device: { name: '网络／边界设备', prefix: 'NW' },
    sec_domain: { name: '安全域', prefix: 'SD' },
    sec_control: { name: '安全措施', prefix: 'SC' },
    protected_asset: { name: '保护对象', prefix: 'PA' },
    sec_boundary: { name: '边界防护设备', prefix: 'SB' },
  };
  const CLASSES = ['公开', '内部', '秘密'];
  const LEVELS = ['等保二级', '等保三级', '等保四级', '涉密秘密级', '涉密机密级'];
  const META_KEYS = [['project', '项目'], ['drawingNo', '图号'], ['version', '版本'], ['classification', '密级'], ['author', '编制'], ['reviewer', '审核'], ['approver', '批准'], ['date', '日期'], ['org', '单位']];
  const LINK_ATTRS = [['content', '交换内容', '如：目标航迹、控制指令'], ['protocol', '协议标准', '如：Link-16、TCP/IP、RS422'], ['medium', '链路介质', '如：光纤、超短波数据链、卫通'], ['freq', '频度', '如：1 Hz、事件触发'], ['latency', '时延要求', '如：≤100 ms']];
  /* per-view link fields (key, label, placeholder); views not listed use LINK_ATTRS. 密级 is always shown. */
  const VIEW_LINK_ATTRS = {
    'BIZ': [['content', '业务对象', '如：巡逻任务单、处置指令'], ['freq', '频度／触发', '如：每日、事件触发']],
    'APP': [['content', '集成内容', '如：任务指令、态势数据'], ['protocol', '集成方式／协议', '如：REST、消息队列、WebSocket、文件交换'], ['freq', '频度', '如：实时、5 min'], ['latency', '时延要求', '如：≤1 s']],
    'DATA': [['content', '数据对象', '如：目标航迹、装备状态'], ['protocol', '交换方式', '如：CDC 增量、批量抽取、消息订阅'], ['freq', '频度／时效', '如：实时、T+1']],
    'TECH': [['content', '依赖说明', '如：运行于、调用、存储于'], ['protocol', '接口／协议', '如：JDBC、gRPC、S3']],
    'DEPLOY': [['protocol', '协议', '如：HTTPS、TCP、UDP 组播'], ['port', '端口', '如：443、8080、5236'], ['medium', '链路／带宽', '如：万兆光纤、专线 100 Mbps']],
    'SEC': [['content', '访问策略', '如：白名单访问、单向摆渡'], ['protocol', '协议／端口', '如：HTTPS 443、SSH 22'], ['medium', '链路／介质', '如：专线、光纤']],
  };
  /* 视图是否要求连线写“交换内容”（技术、部署、安全视图的连线是依赖／网络关系，不强制） */
  const NEED_CONTENT = v => !['TECH', 'DEPLOY', 'SEC'].includes(v);
  const NODE_ATTRS = { spec: ['规格', '如：32 核／128 GB／2 TB SSD'], os: ['操作系统', '如：麒麟 V10、统信 UOS'], ip: ['地址／网段', '如：10.20.1.11、10.20.1.0/24'], count: ['数量', '如：2（主备）'], level: ['安全等级', '如：等保三级、涉密秘密级'] };
  const NODE_EXTRA = { deploy_node: ['spec', 'os', 'ip', 'count'], deploy_unit: ['spec', 'ip', 'count'], net_device: ['spec', 'ip', 'count'], zone: ['level'], sec_domain: ['level'], sec_boundary: ['spec', 'count'] };
  const NON_EL = ['text', 'note', 'legend', 'tblock'];
  const TB_W = 520, TB_H = 120;

  const viewOf = p => (p && typeof p.view === 'string' && VIEWS[p.view]) ? p.view : null;
  const familyOf = v => (v && VIEWS[v] && VIEWS[v].family) || null;
  const viewLabel = v => !VIEWS[v] ? '' : VIEWS[v].family === 'it' ? VIEWS[v].name : `${v}　${VIEWS[v].name}`;
  const linkAttrsOf = v => VIEW_LINK_ATTRS[v] || LINK_ATTRS;
  const contentLabel = v => (linkAttrsOf(v).find(a => a[0] === 'content') || [, '交换内容'])[1];
  const prefixForLink = p => { const v = viewOf(p); return v ? VIEWS[v].link : 'LK'; };
  const etypeName = e => (ETYPES[e] && ETYPES[e].name) || '';
  const ensureMeta = () => { doc.meta = Object.assign(Object.fromEntries(META_KEYS.map(([k]) => [k, ''])), doc.meta || {}); return doc.meta; };
  const firstLine = s => String(s || '').split('\n')[0].trim();
  const byIdMap = p => new Map(p.nodes.map(n => [n.id, n]));
  function ancestors(n, p, m = byIdMap(p)) { const out = []; let c = n.parent && m.get(n.parent); while (c && out.length < 32) { out.push(c); c = c.parent && m.get(c.parent); } return out; }

  /* ---------- 信息系统视图的类型推断（图标键 + 形状 + 文字线索） ---------- */
  const iconKey = n => (typeof n.icon === 'string' && n.icon.startsWith('lib:')) ? n.icon.slice(4) : '';
  const KS = s => new Set(s.split(' '));
  const NET_ICONS = KS('firewall gateway it_gap it_lb switch router it_core_switch it_vpn it_waf it_bastion it_ids');
  const NET_RE = /防火墙|网闸|隔离装置|交换机|路由器|负载均衡|网关|VPN|WAF|堡垒机|入侵检测|入侵防御|IDS|IPS|抗\s*D?DoS/i;
  const BOUND_ICONS = KS('firewall gateway it_gap it_vpn it_waf it_ids');
  const BOUND_RE = /防火墙|网闸|隔离装置|安全网关|边界网关|VPN|WAF|入侵检测|入侵防御|IDS|IPS|抗\s*D?DoS/i;
  const CTRL_ICONS = KS('security identity audit_log crypto it_ca it_backup it_bastion ops_monitor');
  const STORE_ICONS = KS('database storage data_lake it_dw it_lakehouse it_tsdb it_graphdb it_object_store it_search it_cache it_file_server it_backup it_master_data');
  const STORE_RE = /数据库|数据仓库|数仓|数据湖|湖仓|存储|贴源层|ODS|DWD|DWS|ADS|库$/i;
  const PROC_ICONS = KS('it_etl it_stream it_batch it_data_service workflow it_mq message_bus api algorithm');
  const PROC_RE = /采集|抽取|清洗|治理|集成|同步|计算|处理|加工|转换|融合|标注|ETL|服务$/i;
  const INFRA_ICONS = KS('server it_xc_server it_rack it_vm storage data_center switch router it_core_switch gpu edge_node firewall it_dr it_backup power_station');
  const PLAT_ICONS = KS('it_middleware it_mq message_bus it_cache it_k8s it_registry it_cicd it_os cloud');
  const PERSON_ICONS = KS('operator user_group commander officer_female staff_officer staff_plan staff_intel staff_info analyst expert_group engineer maintainer drone_pilot liaison');
  const DOC_SHAPES = KS('document multidoc cylinder');
  const isNet = n => NET_ICONS.has(iconKey(n)) || (!isCont(n) && NET_RE.test(firstLine(n.text)));
  const isBound = n => BOUND_ICONS.has(iconKey(n)) || (!isCont(n) && BOUND_RE.test(firstLine(n.text)));
  const CONT_T = ['band', 'lane', 'group'];
  /* effective type of an ancestor container: explicit etype, else the inferred one */
  const effEtype = (a, p, v) => a.etype || (CONT_T.includes(a.type) ? defaultEtype(a, p, v) : null);
  function itEtype(n, p, v) {
    const anc = ancestors(n, p), ae = anc.map(a => effEtype(a, p, v)), inA = (...es) => ae.some(e => es.includes(e));
    const key = iconKey(n), txt = firstLine(n.text), t = n.type, leaf = !CONT_T.includes(t);
    const ctx = re => anc.some(a => re.test(firstLine(a.text)));
    switch (v) {
      case 'BIZ':
        if (t === 'band') return 'biz_domain';
        if (t === 'lane' || t === 'group') return inA('biz_domain', 'biz_capability') ? 'biz_capability' : 'biz_domain';
        if (PERSON_ICONS.has(key)) return 'biz_role';
        if (DOC_SHAPES.has(t) || key === 'document' || key === 'it_business_obj') return 'biz_object';
        return 'biz_process';
      case 'APP': {
        const ext = ctx(/外部/);
        if (t === 'band' || t === 'lane') return null;
        if (t === 'group') { if (/外部系统|外部/.test(txt) && !inA('app_system')) return null; return ext ? 'ext_system' : inA('app_system') ? 'app_module' : 'app_system'; }
        if (ext) return 'ext_system';
        if (inA('app_module')) return 'app_service';
        if (inA('app_system')) return 'app_module';
        if (ctx(/支撑|服务|中台|公共/)) return 'app_service';
        return 'app_system';
      }
      case 'DATA':
        /* 以“层”结尾的分组带／泳道（采集层、存储层、服务层…）是数据处理分层，仅作排版，不是数据域 */
        if ((t === 'band' || t === 'lane') && /层$/.test(txt)) return null;
        if (t === 'band') return 'data_domain';
        if (t === 'lane') return inA('data_domain') ? null : 'data_domain';
        if (t === 'group') return !inA('data_domain') ? 'data_domain' : (STORE_RE.test(txt) ? 'data_store' : 'data_entity');
        if (STORE_ICONS.has(key) || t === 'cylinder' || STORE_RE.test(txt)) return 'data_store';
        if (PROC_ICONS.has(key) || PROC_RE.test(txt)) return 'data_proc';
        return 'data_entity';
      case 'TECH':
        if (t === 'band' || t === 'lane') return 'tech_layer';
        if (t === 'group') return inA('tech_layer') ? 'platform' : 'tech_layer';
        if (INFRA_ICONS.has(key)) return 'infra';
        if (PLAT_ICONS.has(key)) return 'platform';
        if (!inA('platform') && ctx(/基础设施|IaaS|硬件|机房/)) return 'infra';
        return 'tech_component';
      case 'DEPLOY':
        if (t === 'band') return 'zone';
        if (t === 'lane') return inA('zone') ? null : 'zone';
        if (t === 'group') return inA('deploy_node') ? 'deploy_node' : (!inA('zone') || /区|域|DMZ/i.test(txt)) ? 'zone' : 'deploy_node';
        if (isNet(n)) return 'net_device';
        return inA('deploy_node') ? 'deploy_unit' : 'deploy_node';
      case 'SEC':
        if (t === 'band') return 'sec_domain';
        if (t === 'lane') return inA('sec_domain') ? null : 'sec_domain';
        if (t === 'group') return !inA('sec_domain') || /域|区|DMZ/i.test(txt) ? 'sec_domain' : 'protected_asset';
        if (isBound(n)) return 'sec_boundary';
        if (CTRL_ICONS.has(key) || /审计|认证|加密|监测|防病毒|病毒防护|备份|准入|访问控制|身份|证书|密码|漏洞|态势感知|日志/.test(txt)) return 'sec_control';
        return leaf ? 'protected_asset' : null;
    }
    return null;
  }

  /* ---------- element model ---------- */
  function defaultEtype(n, p, v = viewOf(p)) {
    if (!v || NON_EL.includes(n.type)) return null;
    if (contRow(n) && n.type !== 'band' && n.type !== 'lane' && n.type !== 'group') return null;
    if (familyOf(v) === 'it') return itEtype(n, p, v);
    if (n.type === 'band') return null;
    if (n.type === 'lane') return { 'OV-2': 'performer', 'OV-5b': 'performer', 'SV-4': 'system' }[v] || null;
    if (n.type === 'group') return { 'OV-2': 'op_node', 'SV-1': 'op_node', 'SV-4': 'system' }[v] || null;
    if (v === 'OV-1') return n.type === 'equip' ? 'resource' : 'op_node';
    if (v === 'OV-2') return 'op_node';
    if (v === 'OV-5b') return 'op_activity';
    if (v === 'SV-1') return ancestors(n, p).some(a => a.etype === 'system' || a.etype === 'subsystem') ? 'subsystem' : 'system';
    if (v === 'SV-4') return 'sys_function';
    return null;
  }
  /* does this node take part in the standard (needs a type / code)? */
  function isElement(n, p, v = viewOf(p)) {
    if (NON_EL.includes(n.type)) return false;
    if (n.etype) return true;
    if (!v) return false;
    /* 流程起止符（椭圆／起止框，说明为“起止”或文字为开始／结束）不是体系元素 */
    if ((n.attrs && /起止/.test(n.attrs.desc || '')) || (['ellipse', 'terminator', 'round'].includes(n.type) && /^(开始|结束|起点|终点)$/.test((n.text || '').trim()))) return false;
    if (isCont(n)) return !!defaultEtype(n, p, v);
    return true;
  }
  /* top-to-bottom, left-to-right by centre; centres within 20 px vertically form one row */
  function readingOrder(nodes) {
    const a = nodes.map(n => ({ n, cx: n.x + n.w / 2, cy: n.y + n.h / 2 })).sort((p, q) => p.cy - q.cy || p.cx - q.cx);
    const out = []; let row = [], ry = null;
    const flush = () => { row.sort((p, q) => p.cx - q.cx); out.push(...row.map(r => r.n)); row = []; };
    for (const it of a) { if (ry !== null && it.cy - ry > 20) flush(); if (!row.length) ry = it.cy; row.push(it); }
    flush(); return out;
  }
  const fmt = (pre, k) => `${pre}-${String(k).padStart(2, '0')}`;
  function assign(list, prefixOf, renumber) {
    let n = 0; const groups = new Map();
    for (const o of list) { const pre = prefixOf(o); if (!pre) continue; if (!groups.has(pre)) groups.set(pre, []); groups.get(pre).push(o); }
    for (const [pre, items] of groups) {
      const used = new Set(), need = [];
      for (const o of items) {
        const c = (o.code || '').trim();
        if (!renumber && c && c.startsWith(pre + '-') && !used.has(c)) used.add(c); else need.push(o);
      }
      let k = 1;
      for (const o of need) { while (used.has(fmt(pre, k))) k++; o.code = fmt(pre, k); used.add(o.code); n++; }
    }
    return n;
  }
  /* returns { typed, nodes, links } — counts of newly typed elements and newly (re)numbered nodes / links */
  function autoNumber(p, renumber = false) {
    const v = viewOf(p); let typed = 0;
    if (v) for (const n of drawOrder(p)) if (!n.etype && isElement(n, p, v)) { const e = defaultEtype(n, p, v); if (e) { n.etype = e; typed++; } }
    const els = p.nodes.filter(n => n.etype && ETYPES[n.etype] && !NON_EL.includes(n.type));
    const order = readingOrder(els);
    const nodesN = assign(order, n => ETYPES[n.etype].prefix, renumber);
    let linksN = 0;
    if (v) {
      const idx = new Map(readingOrder(p.nodes.filter(n => !NON_EL.includes(n.type))).map((n, i) => [n.id, i]));
      const ls = p.links.filter(l => idx.has(l.from) && idx.has(l.to)).sort((a, b) => idx.get(a.from) - idx.get(b.from) || idx.get(a.to) - idx.get(b.to));
      linksN = assign(ls, () => VIEWS[v].link, renumber);
    }
    return { typed, nodes: nodesN, links: linksN };
  }

  /* ---------- canvas helpers shared by SVG / PPTX / VSDX ---------- */
  function codeTag(n, p) {
    if (!doc.showCodes || !n.code || NON_EL.includes(n.type)) return null;
    const t = T(), size = 9.5, text = String(n.code), w = measure(text, size, true) + 11, h = 14;
    let x = n.x + 4, y = n.y - 7;
    if (contRow(n)) { const b = contBadge(n, p, { w, h }); if (!b) return null; x = b.x; y = b.y; }
    return { x, y, w, h, text, size, bold: true, fill: t.bg, stroke: t.muted, color: t.text };
  }
  function linkLabel(l, p) {
    const lab = l.label || '';
    if (doc.showCodes && l.code) return lab ? `${l.code}　${lab}` : l.code;
    return lab;
  }
  function pageIndex(p) {
    let list = []; try { list = pagesInOrder(); } catch (_) { }
    if (!list.includes(p)) list = Object.values(doc.pages);
    return { i: Math.max(0, list.indexOf(p)), n: list.length || 1 };
  }
  function drawingNo(p) { const m = ensureMeta(), { i, n } = pageIndex(p); if (!m.drawingNo) return ''; return n > 1 ? `${m.drawingNo}-${i + 1}` : m.drawingNo; }
  /* engineering title block: left = 项目／图名／单位, right = 4 × (label | value | label | value) */
  function tblockCells(node, p) {
    const m = ensureMeta(), t = T(), v = viewOf(p), { i, n } = pageIndex(p);
    const sx = node.w / TB_W, sy = node.h / TB_H, k = Math.min(sx, sy);
    const lab = t.note.fill, val = t.bg, out = [];
    const C = (x, y, w, h, text, o = {}) => {
      const W = w * sx, H = h * sy; let size = (o.size || 10) * k;
      const lines = String(text || '').split('\n');
      const widest = Math.max(0, ...lines.map(s => measure(s, size, !!o.bold)));
      if (widest > W - 6 && widest > 0) size = Math.max(5, size * (W - 6) / widest);
      if (lines.length * size * 1.3 > H - 2) size = Math.max(5, (H - 2) / (lines.length * 1.3));
      out.push({ x: node.x + x * sx, y: node.y + y * sy, w: W, h: H, text: text || '', size: +size.toFixed(2), bold: !!o.bold, fill: o.fill === undefined ? val : o.fill, align: o.align || 'center', color: o.color || t.text, stroke: t.box.stroke, lw: o.lw || 0.6 });
    };
    const pn = firstLine(p.name) || '未命名', sq = s => s.replace(/\s/g, '');
    const title = pn + (!v ? '' : familyOf(v) === 'it' ? (sq(pn).includes(VIEWS[v].name) ? '' : `\n${VIEWS[v].name}`) : (sq(pn).includes(sq(v)) ? '' : `\n${v}　${VIEWS[v].name}`));
    C(0, 0, 44, 30, '项目', { fill: lab, size: 9 }); C(44, 0, 176, 30, m.project, { size: 10.5, bold: true });
    C(0, 30, 220, 60, title, { size: 13, bold: true });
    C(0, 90, 44, 30, '单位', { fill: lab, size: 9 }); C(44, 90, 176, 30, m.org, { size: 10 });
    const rows = [['图号', drawingNo(p), '版本', m.version], ['密级', m.classification, '页次', `第 ${i + 1}／${n} 页`], ['编制', m.author, '审核', m.reviewer], ['批准', m.approver, '日期', m.date]];
    rows.forEach((r, j) => {
      const y = j * 30;
      C(220, y, 44, 30, r[0], { fill: lab, size: 9 }); C(264, y, 106, 30, r[1], { size: 10, bold: r[0] === '密级' && !!r[1], color: r[0] === '密级' && r[1] && r[1] !== '公开' ? '#C2412D' : undefined });
      C(370, y, 44, 30, r[2], { fill: lab, size: 9 }); C(414, y, 106, 30, r[3], { size: 10 });
    });
    out.push({ x: node.x, y: node.y, w: node.w, h: node.h, text: '', size: 10, bold: false, fill: null, align: 'center', color: t.text, stroke: t.box.stroke, lw: 1.6 });
    return out;
  }
  function tblockSVG(node, p) {
    let s = '';
    for (const c of tblockCells(node, p)) {
      s += `<rect x="${c.x.toFixed(1)}" y="${c.y.toFixed(1)}" width="${c.w.toFixed(1)}" height="${c.h.toFixed(1)}" fill="${c.fill || 'none'}" stroke="${c.stroke}" stroke-width="${c.lw}"/>`;
      if (c.text) { const left = c.align === 'left'; s += textBlock(String(c.text).split('\n'), left ? c.x + 4 : c.x + c.w / 2, c.y + c.h / 2, c.size, c.bold, c.color, left ? 'start' : 'middle'); }
    }
    return s;
  }
  function codeTagSVG(n, p) {
    const g = codeTag(n, p); if (!g) return '';
    return `<g class="std-code"><rect x="${g.x.toFixed(1)}" y="${g.y.toFixed(1)}" width="${g.w.toFixed(1)}" height="${g.h}" rx="2.5" fill="${g.fill}" stroke="${g.stroke}" stroke-width="0.7"/>` + textBlock([g.text], g.x + g.w / 2, g.y + g.h / 2 - 0.5, g.size, true, g.color) + '</g>';
  }

  /* ---------- title block / legend placement ---------- */
  function bboxOf(list) {
    if (!list.length) return null; let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const n of list) { x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x + n.w); y1 = Math.max(y1, n.y + n.h); }
    return { x0, y0, x1, y1 };
  }
  const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  function placeTblock(p, create = true) {
    let tb = p.nodes.find(n => n.type === 'tblock');
    if (!tb) { if (!create) return null; tb = mkNode({ type: 'tblock', w: TB_W, h: TB_H, text: '', size: 10 }); p.nodes.push(tb); }
    tb.parent = null;
    const others = p.nodes.filter(n => n !== tb);
    for (const n of others) if (n.type === 'legend') legendLayout(n, p);
    const main = bboxOf(others.filter(n => n.type !== 'legend' && !(n.type === 'note' && !n.parent))) || bboxOf(others) || { x0: 0, y0: 0, x1: TB_W, y1: 0 };
    tb.x = snapv(Math.max(main.x1, main.x0 + tb.w) - tb.w); tb.y = snapv(main.y1 + 16);
    if (others.some(n => !n.parent && overlaps(tb, n))) { const all = bboxOf(others); tb.y = snapv(all.y1 + 16); }
    return tb;
  }
  function addLegend(p) {
    if (p.nodes.some(n => n.type === 'legend')) return null;
    const main = bboxOf(p.nodes.filter(n => n.type !== 'tblock')) || { x0: 0, y1: 0 };
    const lg = mkNode({ type: 'legend', w: 200, h: 60, x: snapv(main.x0), y: snapv(main.y1 + 16) });
    p.noLegend = false;
    p.nodes.push(lg); legendLayout(lg, p); return lg;
  }
  /* called after 一键美化: keep an existing title block below the content */
  function afterLayout(p) { if (p.nodes.some(n => n.type === 'tblock')) placeTblock(p, false); }

  /* ---------- rule checker ---------- */
  const RULES = {
    'etype-missing': '元素未指定类型', 'code-missing': '编号缺失', 'code-dup': '编号重复', 'name-empty': '名称为空', 'isolated': '孤立元素',
    'link-content': '连线未写交换内容', 'sv1-iface': 'SV-1 接口未写协议或链路', 'etype-view': '元素类型不属于该视图', 'ov5b-lane': '作战活动不在执行者泳道内',
    'legend-missing': '缺图例', 'tblock-missing': '缺标题栏或图号', 'link-code': '连线无编号',
    /* 信息系统架构 */
    'biz-scope': '业务流程不在业务域／能力内', 'app-proto': '集成未写方式／协议', 'app-isolated': '应用无集成关系',
    'data-content': '数据流未写数据对象', 'data-domain': '数据实体不在数据域内', 'tech-layer': '技术组件不在技术层内',
    'dep-zone': '部署节点不在网络区域内', 'dep-node': '部署单元不在部署节点内', 'dep-cross': '跨区直连未经边界设备', 'dep-level': '网络区域未标安全等级',
    'sec-cross': '跨域访问未经边界防护', 'sec-asset': '保护对象不在安全域内', 'sec-level': '安全域未标安全等级',
  };
  const ZONE_OF = { DEPLOY: 'zone', SEC: 'sec_domain' };
  const BOUNDARY = ['net_device', 'sec_boundary'];
  const LEVEL_RE = /(等保\s*[一二三四五1-5]\s*级|涉密\s*(?:秘密|机密|绝密)\s*级|(?:秘密|机密|绝密)级|[一二三四五]级(?:等保)?)/;
  function itNodeCheck(n, p, v, m, add, nm) {
    const anc = ancestors(n, p, m), inA = (...es) => anc.some(a => es.includes(a.etype)), e = n.etype, q = `「${nm(n)}」`;
    const lv = () => !((n.attrs && n.attrs.level) || '').trim();
    if (v === 'BIZ' && e === 'biz_process' && !inA('biz_domain', 'biz_capability')) add('warn', 'biz-scope', `业务流程／活动${q}没有放在业务域或业务能力内`, { nodeId: n.id });
    if (v === 'DATA' && e === 'data_entity' && !inA('data_domain')) add('warn', 'data-domain', `数据实体${q}没有归属数据域`, { nodeId: n.id });
    if (v === 'TECH' && e === 'tech_component' && !inA('tech_layer')) add('warn', 'tech-layer', `技术组件${q}没有放在技术层内`, { nodeId: n.id });
    if (v === 'DEPLOY') {
      if (e === 'deploy_node' && !inA('zone')) add('error', 'dep-zone', `部署节点${q}不在任何网络区域／安全域内`, { nodeId: n.id });
      if (e === 'deploy_unit' && !inA('deploy_node')) add('warn', 'dep-node', `部署单元${q}没有放在部署节点内`, { nodeId: n.id });
      if (e === 'zone' && lv()) add('info', 'dep-level', `网络区域${q}未标安全等级（如：等保三级、涉密秘密级）`, { nodeId: n.id });
    }
    if (v === 'SEC') {
      if (e === 'protected_asset' && !inA('sec_domain')) add('error', 'sec-asset', `保护对象${q}不在任何安全域内`, { nodeId: n.id });
      if (e === 'sec_domain' && lv()) add('warn', 'sec-level', `安全域${q}未标安全等级（如：等保三级、涉密秘密级）`, { nodeId: n.id });
    }
  }
  /* rules whose element must sit inside a container of one of these types (used by fix to re-parent by geometry) */
  const NEEDS_IN = { biz_process: ['biz_domain', 'biz_capability'], data_entity: ['data_domain'], tech_component: ['tech_layer'], deploy_node: ['zone'], deploy_unit: ['deploy_node'], protected_asset: ['sec_domain'] };
  function pagesForCheck(d) { let list = []; try { list = pagesInOrder(); } catch (_) { } for (const p of Object.values(d.pages)) if (!list.includes(p)) list.push(p); return list; }
  function check(d = doc) {
    const issues = [];
    for (const p of pagesForCheck(d)) {
      const v = viewOf(p); if (!v) continue;
      const m = byIdMap(p), add = (level, rule, msg, o = {}) => issues.push({ level, rule, msg, pageId: p.id, ...o });
      const nm = n => firstLine(n.text) || (n.etype ? etypeName(n.etype) : (TYPE_NAME[n.type] || '元素'));
      const els = p.nodes.filter(n => isElement(n, p, v));
      const codes = new Map();
      for (const n of els) {
        if (!firstLine(n.text)) add('error', 'name-empty', `${n.code ? n.code + ' ' : ''}${n.etype ? etypeName(n.etype) : TYPE_NAME[n.type] || '元素'}没有名称`, { nodeId: n.id });
        if (!n.etype) { add('warn', 'etype-missing', `「${nm(n)}」未指定元素类型（建议：${etypeName(defaultEtype(n, p, v)) || '按视图选择'}）`, { nodeId: n.id }); continue; }
        if (!VIEWS[v].etypes.includes(n.etype)) add('warn', 'etype-view', `「${nm(n)}」类型为${etypeName(n.etype)}，不属于 ${v} 允许的类型（${VIEWS[v].etypes.map(etypeName).join('、')}）`, { nodeId: n.id });
        if (!n.code) add('warn', 'code-missing', `「${nm(n)}」没有编号`, { nodeId: n.id });
        else { if (!codes.has(n.code)) codes.set(n.code, []); codes.get(n.code).push(n); }
        if (n.etype === 'op_activity' && v === 'OV-5b' && !ancestors(n, p, m).some(a => a.etype === 'performer' || (a.type === 'lane' && !a.etype)))
          add('error', 'ov5b-lane', `作战活动「${nm(n)}」没有放在执行者泳道内`, { nodeId: n.id });
        if (familyOf(v) === 'it') itNodeCheck(n, p, v, m, add, nm);
      }
      for (const [c, list] of codes) if (list.length > 1) list.forEach((n, i) => add('error', 'code-dup', `编号 ${c} 重复 ${list.length} 次：「${nm(n)}」`, { nodeId: n.id }));
      if (v === 'APP') {
        const touched = new Set(); for (const l of p.links) { touched.add(l.from); touched.add(l.to); }
        for (const n of els) if ((n.etype === 'app_system' || n.etype === 'ext_system') && !touched.has(n.id) && !p.nodes.some(k => touched.has(k.id) && ancestors(k, p, m).includes(n)))
          add('warn', 'app-isolated', `${etypeName(n.etype)}「${nm(n)}」没有任何集成关系（孤立应用）`, { nodeId: n.id });
      }
      if (['OV-2', 'SV-1', 'SV-4'].includes(v)) {
        const touched = new Set(); for (const l of p.links) { touched.add(l.from); touched.add(l.to); }
        for (const n of els) if (!isCont(n) && !touched.has(n.id) && !ancestors(n, p, m).some(a => touched.has(a.id))) add('warn', 'isolated', `「${nm(n)}」没有任何连线`, { nodeId: n.id });
      }
      const lcodes = new Map();
      for (const l of p.links) {
        const a = m.get(l.from), b = m.get(l.to); if (!a || !b) continue;
        const ln = `${l.code ? l.code + ' ' : ''}「${nm(a)} → ${nm(b)}」`, at = l.attrs || {};
        if (!l.code) add('warn', 'link-code', `连线${ln}没有编号`, { linkId: l.id });
        else { if (!lcodes.has(l.code)) lcodes.set(l.code, []); lcodes.get(l.code).push(l); }
        if (NEED_CONTENT(v) && !(at.content || '').trim()) {
          const rl = v === 'DATA' ? 'data-content' : 'link-content', cl = contentLabel(v), what = v === 'DATA' ? '数据流' : '连线';
          if ((l.label || '').trim()) add('info', rl, `${what}${ln}只写了标签，${cl}未填写（一键修复可从标签带入）`, { linkId: l.id }); else add('warn', rl, `${what}${ln}未写${cl}`, { linkId: l.id });
        }
        if (v === 'APP' && !(at.protocol || '').trim()) add('warn', 'app-proto', `集成${ln}未写集成方式／协议`, { linkId: l.id });
        if (ZONE_OF[v]) {
          const Z = ZONE_OF[v], zoneOf = x => [x, ...ancestors(x, p, m)].find(y => y.etype === Z), za = zoneOf(a), zb = zoneOf(b);
          if (za && zb && za !== zb && !BOUNDARY.includes(a.etype) && !BOUNDARY.includes(b.etype))
            add('error', v === 'DEPLOY' ? 'dep-cross' : 'sec-cross', `${v === 'DEPLOY' ? '跨区直连' : '跨域访问'}${ln}：「${nm(za)}」与「${nm(zb)}」之间须经网闸／防火墙等${v === 'DEPLOY' ? '边界设备' : '边界防护设备'}`, { linkId: l.id });
        }
        if (v === 'SV-1' && (!(at.protocol || '').trim() || !(at.medium || '').trim())) add('warn', 'sv1-iface', `接口${ln}未写${[!(at.protocol || '').trim() && '协议标准', !(at.medium || '').trim() && '链路介质'].filter(Boolean).join('、')}`, { linkId: l.id });
      }
      for (const [c, list] of lcodes) if (list.length > 1) list.forEach(l => add('error', 'code-dup', `连线编号 ${c} 重复 ${list.length} 次`, { linkId: l.id }));
      if (!p.nodes.some(n => n.type === 'legend')) add('warn', 'legend-missing', '本页没有图例');
      const tb = p.nodes.find(n => n.type === 'tblock');
      if (!tb) add('warn', 'tblock-missing', '本页没有标题栏');
      else if (!(d.meta && (d.meta.drawingNo || '').trim())) add('warn', 'tblock-missing', '标题栏未填写图号（在图面设置的「标题栏」中填写）', { nodeId: tb.id });
    }
    return issues;
  }
  /* mechanical fixes: type + number, label → content, legend, title block */
  function fix(d = doc) {
    const r = { typed: 0, nodes: 0, links: 0, content: 0, legend: 0, tblock: 0, parent: 0, level: 0 };
    for (const p of pagesForCheck(d)) {
      const v = viewOf(p); if (!v) continue;
      if (familyOf(v) === 'it') {
        /* 1. element lying geometrically inside the right kind of container but not attached to it → attach
              (uses the explicit or inferred type of the element and of the candidate containers) */
        const eff = n => n.etype || (isElement(n, p, v) ? defaultEtype(n, p, v) : null);
        for (const n of drawOrder(p)) {
          if (NON_EL.includes(n.type)) continue;
          const need = NEEDS_IN[eff(n)]; if (!need) continue;
          if (ancestors(n, p).some(a => need.includes(eff(a)))) continue;
          let pid = null; try { pid = findParent(n, p); } catch (_) { }
          const par = pid && p.nodes.find(x => x.id === pid);
          if (par && pid !== n.parent && [par, ...ancestors(par, p)].some(a => need.includes(eff(a)))) { n.parent = pid; r.parent++; }
        }
        /* 2. untyped elements get their type (after re-parenting, so a unit dropped on a server becomes a 部署单元) */
        for (const n of drawOrder(p)) if (!n.etype && isElement(n, p, v)) { const e = defaultEtype(n, p, v); if (e) { n.etype = e; r.typed++; } }
        /* 3. security level written in the container name (e.g. “业务专网区（等保三级）”) → attrs.level */
        for (const n of p.nodes) if ((n.etype === 'zone' || n.etype === 'sec_domain') && !((n.attrs && n.attrs.level) || '').trim()) {
          const mm = String(n.text || '').match(LEVEL_RE) || String((n.attrs && n.attrs.desc) || '').match(LEVEL_RE);
          if (mm) { n.attrs = Object.assign({}, n.attrs, { level: mm[1].replace(/\s/g, '') }); r.level++; }
        }
      }
      const a = autoNumber(p, false); r.typed += a.typed; r.nodes += a.nodes; r.links += a.links;
      for (const l of p.links) if (!(l.attrs && (l.attrs.content || '').trim()) && (l.label || '').trim()) { l.attrs = Object.assign({}, l.attrs, { content: l.label.trim() }); r.content++; }
      if (addLegend(p)) r.legend++;
      if (!p.nodes.some(n => n.type === 'tblock')) r.tblock++;
      placeTblock(p);
    }
    return r;
  }

  /* ---------- properties panel ---------- */
  const row = (label, inner, title) => `<div class="row"${title ? ` title="${esc(title)}"` : ''}><label>${label}</label>${inner}</div>`;
  const inp = (id, val, ph = '') => `<input type="text" id="${id}" value="${esc(val || '')}" placeholder="${esc(ph)}">`;
  const clsSel = (id, val) => `<select id="${id}"><option value="">（未填）</option>${CLASSES.concat(val && !CLASSES.includes(val) ? [val] : []).map(c => `<option ${c === val ? 'selected' : ''}>${esc(c)}</option>`).join('')}</select>`;
  function propsHTML(kind, o, p) {
    const v = viewOf(p); let h = '';
    if (kind === 'page') {
      const m = ensureMeta();
      h += `<hr><div class="hint" style="margin-bottom:4px"><b style="color:var(--fg)">规范</b>（DoDAF／UAF 视图 · 信息系统架构视图）</div>`;
      h += row('视图类型', `<select id="std-view"><option value="">自由绘图</option>${FAMILIES.map(([f, fl]) => `<optgroup label="${esc(fl)}">${Object.entries(VIEWS).filter(([, x]) => x.family === f).map(([k]) => `<option value="${k}" ${k === v ? 'selected' : ''}>${esc(viewLabel(k))}</option>`).join('')}</optgroup>`).join('')}</select>`);
      if (v) h += `<div class="hint" style="margin:-2px 0 4px">元素：${VIEWS[v].etypes.map(etypeName).join('、')}；连线：${VIEWS[v].linkName}（${VIEWS[v].link}）${VIEWS[v].hint ? `<br>${esc(VIEWS[v].hint)}` : ''}</div>`;
      h += row('', `<label style="width:auto;display:flex;gap:6px;align-items:center;color:var(--fg)"><input type="checkbox" id="std-codes" ${doc.showCodes ? 'checked' : ''}> 显示编号（画布与导出）</label>`);
      h += `<div class="grid2" style="margin:6px 0"><button id="std-num" title="按阅读顺序为元素和连线编号，保留已有编号">自动编号</button><button id="std-renum" title="忽略已有编号，全部重新编号">全部重编</button><button id="std-check" title="Ctrl+Shift+K">规范检查</button><button id="std-tb">插入／更新标题栏</button></div>`;
      h += `<div class="row"><button id="std-xlsx" class="primary" style="justify-content:center">导出规范表格（.xlsx）</button></div>`;
      h += `<div class="hint" style="margin:8px 0 4px">标题栏（全文档共用）</div>`;
      for (const [k, lab] of META_KEYS) h += row(lab, k === 'classification' ? clsSel('std-m-' + k, m[k]) : inp('std-m-' + k, m[k], k === 'drawingNo' ? '多页时自动加 -1、-2…' : k === 'date' ? '如：2026-10-15' : ''));
    } else if (kind === 'node') {
      if (o.type === 'tblock') return `<hr><div class="hint">标题栏内容取自图面设置中的「标题栏」各项（点画布空白处编辑），图名取页面名与视图类型。</div>`;
      if (NON_EL.includes(o.type)) return '';
      const allowed = v ? VIEWS[v].etypes : [], others = Object.keys(ETYPES).filter(k => !allowed.includes(k));
      const opt = k => `<option value="${k}" ${k === o.etype ? 'selected' : ''}>${ETYPES[k].name}（${ETYPES[k].prefix}）</option>`;
      const a = o.attrs || {};
      const vl = v ? (familyOf(v) === 'it' ? VIEWS[v].name : v) : '';
      h += `<hr><div class="hint" style="margin-bottom:4px"><b style="color:var(--fg)">规范属性</b>${v ? `（${esc(vl)}）` : ''}</div>`;
      h += row('元素类型', `<select id="std-etype"><option value="">未指定</option>${allowed.length ? `<optgroup label="${esc(vl)} 视图">${allowed.map(opt).join('')}</optgroup><optgroup label="其他">${others.map(opt).join('')}</optgroup>` : others.map(opt).join('')}</select>`);
      h += row('编号', inp('std-code', o.code, o.etype && ETYPES[o.etype] ? ETYPES[o.etype].prefix + '-01' : '先选类型或用自动编号'));
      h += row('说明', `<textarea id="std-desc" rows="2" placeholder="职能、组成或用途">${esc(a.desc || '')}</textarea>`);
      h += row('责任单位', inp('std-owner', a.owner, '如：某某研究所'));
      for (const k of NODE_EXTRA[o.etype] || []) {
        const [lab, ph] = NODE_ATTRS[k];
        h += row(lab, k === 'level' ? `<input type="text" id="std-n-level" list="std-levels" value="${esc(a.level || '')}" placeholder="${esc(ph)}"><datalist id="std-levels">${LEVELS.map(x => `<option value="${x}">`).join('')}</datalist>` : inp('std-n-' + k, a[k], ph));
      }
    } else if (kind === 'link') {
      const a = o.attrs || {};
      h += `<hr><div class="hint" style="margin-bottom:4px"><b style="color:var(--fg)">规范属性</b>${v ? `（${VIEWS[v].linkName}）` : ''}</div>`;
      h += row('编号', inp('std-lcode', o.code, prefixForLink(p) + '-01'));
      for (const [k, lab, ph] of linkAttrsOf(v)) h += row(lab, inp('std-a-' + k, a[k], ph));
      h += row('密级', clsSel('std-a-security', a.security));
    }
    return h;
  }
  function bindProps(kind, o, p) {
    const el = $('#props'), q = s => el.querySelector(s), live = () => render(false);
    const on = (s, ev, fn) => { const x = q(s); if (x) x.addEventListener(ev, fn); };
    if (kind === 'page') {
      on('#std-view', 'change', e => { p.view = e.target.value || null; render(); toast(p.view ? `本页设为 ${viewLabel(p.view)}` : '本页设为自由绘图'); });
      on('#std-codes', 'change', e => { doc.showCodes = e.target.checked; render(); });
      on('#std-num', 'click', () => doNumber(p, false));
      on('#std-renum', 'click', () => doNumber(p, true));
      on('#std-check', 'click', openCheck);
      on('#std-tb', 'click', () => { checkpoint(); const had = p.nodes.some(n => n.type === 'tblock'); const tb = placeTblock(p); selectNodes([tb.id]); render(); toast(had ? '标题栏已更新到图面右下方' : '已插入标题栏'); });
      on('#std-xlsx', 'click', exportXlsx);
      const m = ensureMeta();
      for (const [k] of META_KEYS) { on('#std-m-' + k, 'input', e => { m[k] = e.target.value; live(); }); on('#std-m-' + k, 'change', e => { m[k] = e.target.value; live(); }); }
    } else if (kind === 'node') {
      on('#std-etype', 'change', e => { o.etype = e.target.value || null; if (!o.etype) delete o.etype; render(); });
      on('#std-code', 'input', e => { o.code = e.target.value.trim(); live(); });
      on('#std-desc', 'input', e => { o.attrs = Object.assign({}, o.attrs, { desc: e.target.value }); });
      on('#std-owner', 'input', e => { o.attrs = Object.assign({}, o.attrs, { owner: e.target.value }); });
      for (const k of Object.keys(NODE_ATTRS)) { const fn = e => { o.attrs = Object.assign({}, o.attrs, { [k]: e.target.value }); }; on('#std-n-' + k, 'input', fn); on('#std-n-' + k, 'change', fn); }
    } else if (kind === 'link') {
      on('#std-lcode', 'input', e => { o.code = e.target.value.trim(); live(); });
      for (const [k] of linkAttrsOf(viewOf(p)).concat([['security']])) {
        const fn = e => { o.attrs = Object.assign({}, o.attrs, { [k]: e.target.value }); };
        on('#std-a-' + k, 'input', fn); on('#std-a-' + k, 'change', fn);
      }
    }
  }
  function doNumber(p, renumber) {
    checkpoint();
    const r = autoNumber(p, renumber);
    if (!viewOf(p) && !r.nodes) { render(); toast('本页为自由绘图：请先在「视图类型」中选择视图，或为元素指定类型'); return; }
    render(); toast(`${renumber ? '已全部重编' : '已自动编号'}：补充类型 ${r.typed} 个，元素编号 ${r.nodes} 个，连线编号 ${r.links} 条${doc.showCodes ? '' : '（勾选「显示编号」可在图上显示）'}`);
  }
  async function exportXlsx() {
    if (!window.StdXlsx || typeof StdXlsx.build !== 'function') { toast('规范表格导出模块未加载'); return; }
    try { toast('正在生成规范表格…'); const blob = await StdXlsx.build(doc); await saveFile(projectBaseName() + '-规范表格.xlsx', blob); }
    catch (err) { console.error(err); toast('导出失败：' + (err.message || err)); }
  }

  /* ---------- 规范检查 dialog ---------- */
  let dlg = null;
  const LV = { error: ['错误', 'var(--danger)'], warn: ['警告', '#D4861A'], info: ['提示', 'var(--accent)'] };
  function ensureDlg() {
    if (dlg) return dlg;
    const st = document.createElement('style');
    st.textContent = `#std-dlg{position:fixed;top:0;right:0;bottom:0;left:0;background:rgba(10,15,22,.45);display:none;align-items:center;justify-content:center;z-index:25;padding:16px}
#std-dlg .box{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:12px;width:min(820px,100%);max-height:88vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.25)}
#std-dlg .hd{display:flex;gap:8px;align-items:center;padding:12px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap}
#std-dlg .hd strong{font-size:15px;margin-right:4px}
#std-dlg .pill{display:inline-flex;align-items:center;gap:4px;border-radius:10px;padding:1px 8px;font-size:11.5px;font-variant-numeric:tabular-nums;border:1px solid currentColor;white-space:nowrap}
#std-dlg .bd{overflow:auto;padding:4px 14px 14px}
#std-dlg h5{margin:14px 0 6px;font-size:12.5px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#std-dlg h5 .vw{color:var(--muted);font-weight:400}
#std-dlg .it{display:grid;grid-template-columns:auto auto minmax(0,1fr) auto;gap:8px;align-items:center;padding:5px 0;border-bottom:1px dashed var(--line);font-size:12.5px}
#std-dlg .it .rl{color:var(--muted);font-size:11.5px;white-space:nowrap}
#std-dlg .it button{border-color:var(--line);padding:2px 8px;font-size:12px}
#std-dlg .empty{padding:28px 8px;text-align:center;color:var(--muted);line-height:1.8}
@media (max-width:640px){#std-dlg .it{grid-template-columns:auto minmax(0,1fr) auto}#std-dlg .it .rl{display:none}}`;
    document.head.appendChild(st);
    dlg = document.createElement('div'); dlg.id = 'std-dlg';
    dlg.innerHTML = `<div class="box" role="dialog" aria-label="规范检查"><div class="hd"><strong>规范检查</strong><span id="std-sum" style="display:flex;gap:6px;flex-wrap:wrap"></span><span style="flex:1"></span><button id="std-fix" class="primary" title="自动编号、补充类型、标签带入交换内容、按位置归入容器、从名称提取安全等级、补图例、插入标题栏">一键修复</button><button id="std-re">重新检查</button><button id="std-close">关闭</button></div><div class="bd" id="std-body"></div></div>`;
    document.body.appendChild(dlg);
    dlg.addEventListener('click', e => {
      if (e.target === dlg) return closeCheck();
      const b = e.target.closest('[data-go]'); if (b) { const it = lastIssues[+b.dataset.go]; if (it) locate(it); }
    });
    dlg.querySelector('#std-close').onclick = closeCheck;
    dlg.querySelector('#std-re').onclick = renderCheck;
    dlg.querySelector('#std-fix').onclick = () => {
      checkpoint(); const r = fix(doc); render(); renderCheck();
      toast(`已修复：类型 ${r.typed}、元素编号 ${r.nodes}、连线编号 ${r.links}、交换内容 ${r.content}、图例 ${r.legend}、标题栏 ${r.tblock}${r.parent ? `、归属 ${r.parent}` : ''}${r.level ? `、安全等级 ${r.level}` : ''}`);
    };
    dlg.addEventListener('keydown', e => { if (e.key === 'Escape') { e.stopPropagation(); closeCheck(); } });
    return dlg;
  }
  let lastIssues = [];
  function renderCheck() {
    const issues = check(doc); lastIssues = issues;
    const cnt = l => issues.filter(i => i.level === l).length;
    const pill = (l, n) => `<span class="pill" style="color:${LV[l][1]}">${LV[l][0]} ${n}</span>`;
    dlg.querySelector('#std-sum').innerHTML = ['error', 'warn', 'info'].map(l => pill(l, cnt(l))).join('');
    const viewed = pagesForCheck(doc).filter(p => viewOf(p));
    let h = '';
    if (!viewed.length) h = `<div class="empty">当前文档没有设置视图类型的页面。<br>点击画布空白处，在右侧「规范 › 视图类型」中选择视图后再检查：<br>DoDAF／UAF 体系结构视图（OV-1／OV-2／OV-5b／SV-1／SV-4），<br>或信息系统架构视图（业务、应用、数据、技术、部署、安全架构图）。</div>`;
    else {
      const order = { error: 0, warn: 1, info: 2 };
      for (const p of viewed) {
        const list = issues.map((it, i) => ({ it, i })).filter(x => x.it.pageId === p.id).sort((a, b) => order[a.it.level] - order[b.it.level]);
        const v = viewOf(p);
        h += `<h5>${esc(p.name)} <span class="vw">${esc(viewLabel(v))}</span>${list.length ? ['error', 'warn', 'info'].map(l => { const n = list.filter(x => x.it.level === l).length; return n ? pill(l, n) : ''; }).join('') : '<span class="pill" style="color:#0E9F8E">通过</span>'}</h5>`;
        h += list.map(({ it, i }) => `<div class="it"><span class="pill" style="color:${LV[it.level][1]}">${LV[it.level][0]}</span><span class="rl">${esc(RULES[it.rule] || it.rule)}</span><span>${esc(it.msg)}</span><button data-go="${i}">定位</button></div>`).join('');
      }
    }
    dlg.querySelector('#std-body').innerHTML = h;
  }
  function openCheck() { ensureDlg(); renderCheck(); dlg.style.display = 'flex'; setTimeout(() => dlg.querySelector('#std-close').focus(), 0); }
  function closeCheck() { if (dlg) dlg.style.display = 'none'; }
  function locate(it) {
    closeCheck();
    if (cur !== it.pageId) showPage(it.pageId);
    const p = P(); clearSel();
    let bx = null;
    if (it.nodeId) { const n = nodeById(it.nodeId, p); if (n) { selectNodes([n.id]); bx = { x: n.x, y: n.y, w: n.w, h: n.h }; } }
    else if (it.linkId) { const l = p.links.find(x => x.id === it.linkId); const pts = l && linkPoints(l, p); if (pts) { selectLinks([l.id]); const xs = pts.map(q => q.x), ys = pts.map(q => q.y); bx = { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) }; } }
    render();
    if (!bx) { fit(); return; }
    const r = svg.getBoundingClientRect(), k = clamp(Math.min(r.width / (bx.w + 320), r.height / (bx.h + 240)), 0.3, 1.2);
    view.k = k; view.x = bx.x + bx.w / 2 - r.width / 2 / k; view.y = bx.y + bx.h / 2 - r.height / 2 / k;
    applyView(); renderOverlay();
  }

  window.Std = {
    VIEWS, FAMILIES, ETYPES, CLASSES, LEVELS, META_KEYS, RULES, NODE_ATTRS, NODE_EXTRA, LINK_ATTRS, VIEW_LINK_ATTRS, linkAttrsOf, familyOf, viewLabel, viewOf, prefixForLink, etypeName, ensureMeta, defaultEtype, isElement, readingOrder,
    autoNumber, check, fix, tblockCells, tblockSVG, codeTag, codeTagSVG, linkLabel, drawingNo, placeTblock, addLegend, afterLayout,
    propsHTML, bindProps, openCheck, closeCheck, exportXlsx, isOpen: () => !!(dlg && dlg.style.display === 'flex'),
  };
})();
