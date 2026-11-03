/* 织图 · 体系结构规范表格导出（.xlsx，纯手写 OOXML + JSZip，离线） */
(function () {
  'use strict';
  const ET = { op_node: '作战节点', performer: '执行者', op_activity: '作战活动', resource: '装备／资源', system: '系统', subsystem: '子系统', sys_function: '系统功能' };
  const VW = { 'OV-1': '高层作战概念图', 'OV-2': '作战资源流描述', 'OV-5b': '作战活动模型', 'SV-1': '系统接口描述', 'SV-4': '系统功能描述', 'BIZ': '业务架构图', 'APP': '应用架构图', 'DATA': '数据架构图', 'TECH': '技术架构图', 'DEPLOY': '部署架构图', 'SEC': '安全架构图' };
  const IT_VIEWS = ['BIZ', 'APP', 'DATA', 'TECH', 'DEPLOY', 'SEC'];
  const isIT = v => { const S = window.Std; return S && S.VIEWS && S.VIEWS[v] ? S.VIEWS[v].family === 'it' : IT_VIEWS.includes(v); };
  /* 元素附加属性列（有值时才出列） */
  const NODE_COLS = [['level', '安全等级'], ['spec', '规格'], ['os', '操作系统'], ['ip', '地址／网段'], ['count', '数量']];
  /* 接口清单的通用属性列 */
  const LINK_GEN = [['content', '交换内容'], ['protocol', '协议／接口标准'], ['port', '端口'], ['medium', '链路／介质'], ['freq', '频度'], ['latency', '时延要求']];
  const DODAF_KEYS = ['content', 'protocol', 'medium', 'freq', 'latency'];
  const viewLinkAttrs = v => { const S = window.Std; return (S && S.VIEW_LINK_ATTRS && S.VIEW_LINK_ATTRS[v]) || null; };
  const one = s => String(s == null ? '' : s).replace(/\s*\n\s*/g, ' ');
  const etName = e => { const S = window.Std; return (S && S.ETYPES && S.ETYPES[e] && (S.ETYPES[e].name || S.ETYPES[e].zh || (typeof S.ETYPES[e] === 'string' && S.ETYPES[e]))) || ET[e] || ''; };
  const vwName = v => { const S = window.Std; return (S && S.VIEWS && S.VIEWS[v] && (S.VIEWS[v].name || S.VIEWS[v].zh)) || VW[v] || ''; };
  const kindName = k => { try { return (LINK_KINDS[k] || LINK_KINDS.plain).name; } catch (e) { return k || ''; } };
  const linkBody = l => {
    const a = l.attrs || {};
    let s = a.content || l.label || '';
    if (l.dir === 'both' && l.labelBack) s = s ? s + ' ⇄ ' + l.labelBack : l.labelBack;
    return s;
  };
  const SKIP = new Set(['text', 'note', 'legend', 'tblock']);
  const CONT = new Set(['band', 'lane', 'group']);
  const coll = new Intl.Collator('zh-Hans-CN', { numeric: true, sensitivity: 'base' });

  const esc = s => String(s == null ? '' : s).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F￾￿]/g, '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const colL = i => { let s = ''; for (i++; i > 0; i = Math.floor((i - 1) / 26)) s = String.fromCharCode(65 + (i - 1) % 26) + s; return s; };
  const cjkLen = s => { let w = 0; for (const ch of String(s == null ? '' : s)) w += ch.charCodeAt(0) > 255 ? 2 : 1; return w; };
  const lineW = s => Math.max(0, ...String(s == null ? '' : s).split('\n').map(cjkLen));
  const safeName = (s, used) => {
    let n = String(s).replace(/[\[\]:*?\/\\]/g, '·').replace(/^'+|'+$/g, '');
    n = Array.from(n).slice(0, 31).join('');
    let b = n, i = 2; while (used.has(n.toLowerCase())) { const suf = '~' + i++; n = Array.from(b).slice(0, 31 - suf.length).join('') + suf; }
    used.add(n.toLowerCase()); return n;
  };

  /* 样式索引 */
  const S = { def: 0, head: 1, body: 2, zebra: 3, diag: 4, mhead: 5, title: 6, label: 7, val: 8, rhead: 9, sub: 10, cell: 11 };
  const STYLES = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="5">
<font><sz val="11"/><name val="宋体"/><family val="3"/><charset val="134"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="宋体"/><family val="3"/><charset val="134"/></font>
<font><b/><sz val="22"/><color rgb="FF2E3B4E"/><name val="宋体"/><family val="3"/><charset val="134"/></font>
<font><b/><sz val="11"/><name val="宋体"/><family val="3"/><charset val="134"/></font>
<font><sz val="12"/><color rgb="FF55665A"/><name val="宋体"/><family val="3"/><charset val="134"/></font>
</fonts>
<fills count="6">
<fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF2E3B4E"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFF2F5F9"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFBFBFBF"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFE3EAF3"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>
<border><left style="thin"><color rgb="FF8A94A3"/></left><right style="thin"><color rgb="FF8A94A3"/></right><top style="thin"><color rgb="FF8A94A3"/></top><bottom style="thin"><color rgb="FF8A94A3"/></bottom><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="12">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" textRotation="90" wrapText="1"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="3" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="4" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>`;

  /* 工作表：rows = [[{v,s}|v...]]，选项 widths/freeze/filter/heights/merges */
  function sheetXml(sh) {
    const rows = sh.rows, nCol = Math.max(1, ...rows.map(r => r.length));
    let x = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>';
    x += `<dimension ref="A1:${colL(nCol - 1)}${Math.max(1, rows.length)}"/>`;
    x += '<sheetViews><sheetView workbookViewId="0"' + (sh.first ? ' tabSelected="1"' : '') + (sh.noGrid ? ' showGridLines="0"' : '') + '>';
    const fr = sh.freezeRow || 0, fc = sh.freezeCol || 0;
    if (fr || fc) {
      const tl = colL(fc) + (fr + 1), pane = fr && fc ? 'bottomRight' : fr ? 'bottomLeft' : 'topRight';
      x += `<pane${fc ? ` xSplit="${fc}"` : ''}${fr ? ` ySplit="${fr}"` : ''} topLeftCell="${tl}" activePane="${pane}" state="frozen"/><selection pane="${pane}" activeCell="${tl}" sqref="${tl}"/>`;
    }
    x += '</sheetView></sheetViews><sheetFormatPr defaultRowHeight="18" customHeight="1"/>';
    x += '<cols>' + sh.widths.map((w, i) => `<col min="${i + 1}" max="${i + 1}" width="${w}" customWidth="1"/>`).join('') + '</cols><sheetData>';
    rows.forEach((r, ri) => {
      const ht = sh.heights && sh.heights[ri];
      x += `<row r="${ri + 1}"${ht ? ` ht="${ht}" customHeight="1"` : ''}>`;
      r.forEach((c, ci) => {
        if (c == null) return;
        if (typeof c !== 'object') c = { v: c, s: S.body };
        const ref = colL(ci) + (ri + 1), s = c.s == null ? S.body : c.s;
        if (c.v === '' || c.v == null) x += `<c r="${ref}" s="${s}"/>`;
        else if (typeof c.v === 'number' && isFinite(c.v)) x += `<c r="${ref}" s="${s}"><v>${c.v}</v></c>`;
        else x += `<c r="${ref}" s="${s}" t="inlineStr"><is><t xml:space="preserve">${esc(c.v)}</t></is></c>`;
      });
      x += '</row>';
    });
    x += '</sheetData>';
    if (sh.filter && rows.length > 1) x += `<autoFilter ref="A${sh.filter}:${colL(nCol - 1)}${rows.length}"/>`;
    if (sh.merges && sh.merges.length) x += `<mergeCells count="${sh.merges.length}">${sh.merges.map(m => `<mergeCell ref="${m}"/>`).join('')}</mergeCells>`;
    x += `<pageMargins left="0.4" right="0.4" top="0.6" bottom="0.6" header="0.3" footer="0.3"/><pageSetup paperSize="9" orientation="${sh.noGrid ? "portrait" : "landscape"}" fitToWidth="1" fitToHeight="${sh.noGrid ? 1 : 0}"/>`;
    x += '<headerFooter><oddFooter>&amp;C第 &amp;P 页 / 共 &amp;N 页</oddFooter></headerFooter></worksheet>';
    return x;
  }

  function autoWidths(header, rows, min, max) {
    return header.map((h, i) => {
      let w = lineW(h) + 3;
      for (const r of rows) w = Math.max(w, lineW(r[i]) + 2);
      return Math.max(min || 8, Math.min(max || 40, Math.ceil(w * 1.05)));
    });
  }
  function listSheet(name, header, data, first, minW, maxW) {
    const widths = autoWidths(header, data, minW, maxW);
    const rows = [header.map(h => ({ v: h, s: S.head }))];
    data.forEach((r, i) => rows.push(r.map(v => ({ v: v, s: i % 2 ? S.zebra : S.body }))));
    const heights = { 0: 24 };
    data.forEach((r, i) => { let ln = 1; r.forEach((v, ci) => { ln = Math.max(ln, Math.ceil(lineW(v) / Math.max(4, widths[ci] - 1))); }); if (ln > 1) heights[i + 1] = Math.min(150, 18 * ln); });
    return { name, rows, widths, heights, freezeRow: 1, filter: 1, first };
  }

  function collect(doc) {
    const pages = (typeof pagesInOrder === 'function' && pagesInOrder()) || Object.values(doc.pages);
    // pagesInOrder 读的是当前画布文档。传入另一份时按 up 走子页，不能调用 childPages（它读全局 doc）。
    let list = pages;
    if (typeof doc === 'object' && doc.pages && !pages.every(p => doc.pages[p.id] === p)) {
      if (typeof adoptPages === 'function') adoptPages(doc);
      list = []; const seen = new Set();
      const by = typeof pagesByUp === 'function' ? pagesByUp(doc) : new Map();
      const walk = id => {
        if (seen.has(id) || !doc.pages[id]) return;
        seen.add(id); list.push(doc.pages[id]);
        const kids = by.get(id) || [];
        for (let i = 0; i < kids.length; i++) walk(kids[i].id);
      };
      const tops = by.get(null) || [];
      for (let i = 0; i < tops.length; i++) walk(tops[i].id);
      for (const id in doc.pages) walk(id);
    }
    return list;
  }

  async function build(doc) {
    if (typeof JSZip === 'undefined') throw new Error('JSZip 未加载');
    const meta = doc.meta || {}, pages = collect(doc), used = new Set(), sheets = [];
    const viewOf = p => p.view ? (isIT(p.view) ? (vwName(p.view) || p.view) : (p.view + (vwName(p.view) ? ' ' + vwName(p.view) : ''))) : '';
    const views = [...new Set(pages.map(p => p.view).filter(Boolean))];
    const lab = (n) => (n.code ? n.code + ' ' : '') + (n.text || '').replace(/\s*\n\s*/g, ' ');

    /* 1 元素清单 */
    const el = [];
    /* containers count as elements when they carry a type (分组带＝网络区域、子容器＝应用系统等) */
    const isEl = n => !SKIP.has(n.type) && (!CONT.has(n.type) || !!n.etype);
    const extra = NODE_COLS.filter(([k]) => pages.some(p => (p.nodes || []).some(n => isEl(n) && n.attrs && String(n.attrs[k] || '').trim())));
    pages.forEach(p => {
      const byId = {}; (p.nodes || []).forEach(n => byId[n.id] = n);
      (p.nodes || []).forEach(n => {
        if (!isEl(n)) return;
        /* 所属容器：最近的带类型容器（如网络区域、应用系统）；没有时取直接父容器 */
        let par = n.parent && byId[n.parent]; for (let c = par, i = 0; c && i < 32; c = c.parent && byId[c.parent], i++) if (c.etype) { par = c; break; }
        const a = n.attrs || {};
        el.push({ p: p.name || '', row: [p.name || '', viewOf(p), n.code || '', one(n.text), etName(n.etype) || n.etype || '未指定', par ? one(par.text) : '', a.desc || '', a.owner || ''].concat(extra.map(([k]) => a[k] || '')), idx: pages.indexOf(p) });
      });
    });
    el.sort((a, b) => a.idx - b.idx || coll.compare(a.row[2] || '\uffff', b.row[2] || '\uffff') || coll.compare(a.row[3], b.row[3]));
    sheets.push(listSheet(safeName('元素清单', used), ['页面', '视图', '编号', '名称', '元素类型', '所属容器', '说明', '责任单位'].concat(extra.map(e => e[1])), el.map(e => e.row), false, 8, 36));

    /* 2 接口清单 */
    const ifr = [], dirN = { one: '单向', both: '双向', none: '无' };
    /* columns: one information-system view → that view's own fields; otherwise the union, with generic names */
    let lcols;
    const vla = views.length === 1 && viewLinkAttrs(views[0]);
    if (vla) lcols = vla.map(([k, lab]) => [k, lab]);
    else {
      const keys = new Set();
      for (const v of views.length ? views : ['OV-1']) (viewLinkAttrs(v) || DODAF_KEYS.map(k => [k])).forEach(([k]) => keys.add(k));
      if (pages.some(p => (p.links || []).some(l => l.attrs && String(l.attrs.port || '').trim()))) keys.add('port');
      lcols = LINK_GEN.filter(([k]) => keys.has(k)).map(([k, lab]) => [k, k === 'content' && views.some(isIT) ? '交换内容／数据对象' : lab]);
    }
    if (!lcols.some(c => c[0] === 'content') && pages.some(p => (p.links || []).some(l => (l.label || '').trim() || (l.attrs && String(l.attrs.content || '').trim())))) lcols.unshift(['content', '说明']);
    pages.forEach((p, pi) => {
      const byId = {}; (p.nodes || []).forEach(n => byId[n.id] = n);
      (p.links || []).forEach(l => {
        const a = l.attrs || {}, f = byId[l.from], t = byId[l.to];
        ifr.push([pi, l.code || '', p.name || '', viewOf(p), f ? lab(f) : '', t ? lab(t) : '', dirN[l.dir] || dirN.one, kindName(l.kind)].concat(lcols.map(([k]) => k === 'content' ? linkBody(l) : (a[k] || '')), [a.security || '']));
      });
    });
    ifr.sort((a, b) => a[0] - b[0] || coll.compare(a[1] || '\uffff', b[1] || '\uffff')); ifr.forEach(r => r.shift());
    const ifName = views.length && views.every(isIT) ? (views.length === 1 ? ({ BIZ: '业务流清单', APP: '集成清单', DATA: '接口清单', TECH: '依赖清单', DEPLOY: '网络连接清单', SEC: '访问控制清单' }[views[0]] || '接口清单') : '接口清单') : '接口清单';
    sheets.push(listSheet(safeName(ifName, used), ['编号', '页面', '视图', '源元素', '目标元素', '方向', '链路类型'].concat(lcols.map(c => c[1]), ['密级']), ifr, false, 8, 34));

    /* 2b 部署清单（部署架构图）：区域 › 节点 › 部署单元 */
    const depPages = pages.filter(p => p.view === 'DEPLOY');
    if (depPages.length) {
      const multi = depPages.length > 1, rows = [];
      depPages.forEach(p => {
        const byId = {}; (p.nodes || []).forEach(n => byId[n.id] = n);
        const anc = n => { const o = []; let c = n.parent && byId[n.parent]; while (c && o.length < 32) { o.push(c); c = c.parent && byId[c.parent]; } return o; };
        const zoneOf = n => anc(n).find(a => a.etype === 'zone');
        const zoneName = n => { const zs = anc(n).filter(a => a.etype === 'zone').reverse(); return zs.map(z => one(z.text)).join(' › '); };
        const nodes = (p.nodes || []).filter(n => n.etype === 'deploy_node' || n.etype === 'net_device');
        const ord = n => { const z = zoneOf(n); return [z ? (z.code || '') : '\uffff', z ? z.y : 0]; };
        nodes.sort((a, b) => { const A = ord(a), B = ord(b); return coll.compare(A[0], B[0]) || (a.etype === b.etype ? 0 : a.etype === 'net_device' ? -1 : 1) || coll.compare(a.code || '\uffff', b.code || '\uffff'); });
        for (const n of nodes) {
          const a = n.attrs || {};
          const units = (p.nodes || []).filter(u => u.etype === 'deploy_unit' && anc(u).find(x => x.etype === 'deploy_node') === n);
          const uniq = units.map(u => (u.code ? u.code + ' ' : '') + one(u.text) + (u.attrs && u.attrs.count ? `×${u.attrs.count}` : '')).join('\n');
          rows.push((multi ? [p.name || ''] : []).concat([zoneName(n) || '（未归区域）', n.code || '', one(n.text), etName(n.etype), a.spec || '', a.os || '', a.ip || '', a.count || '', uniq]));
        }
      });
      sheets.push(listSheet(safeName('部署清单', used), (multi ? ['页面'] : []).concat(['区域', '编号', '节点', '类型', '规格', '操作系统', '地址', '数量', '部署单元']), rows, false, 8, 40));
    }
    /* 2c 数据流清单（数据架构图） */
    const dataPages = pages.filter(p => p.view === 'DATA');
    if (dataPages.length) {
      const multi = dataPages.length > 1, rows = [];
      dataPages.forEach(p => {
        const byId = {}; (p.nodes || []).forEach(n => byId[n.id] = n);
        const domOf = n => { let c = n; for (let i = 0; c && i < 32; i++, c = c.parent && byId[c.parent]) if (c.etype === 'data_domain') return one(c.text); return ''; };
        (p.links || []).forEach(l => {
          const a = l.attrs || {}, f = byId[l.from], t = byId[l.to]; if (!f || !t) return;
          rows.push((multi ? [p.name || ''] : []).concat([l.code || '', lab(f), etName(f.etype), lab(t), etName(t.etype), linkBody(l), a.protocol || '', a.freq || '', domOf(f), domOf(t), a.security || '']));
        });
      });
      sheets.push(listSheet(safeName('数据流清单', used), (multi ? ['页面'] : []).concat(['编号', '源', '源类型', '目标', '目标类型', '数据对象', '交换方式', '频度／时效', '源数据域', '目标数据域', '密级']), rows, false, 8, 34));
    }

    /* 3 信息交换矩阵 */
    pages.forEach(p => {
      const byId = {}; (p.nodes || []).forEach(n => byId[n.id] = n);
      const ls = (p.links || []).filter(l => byId[l.from] && byId[l.to]);
      if (!ls.length) return;
      const ids = []; const add = id => { if (!ids.includes(id)) ids.push(id); };
      ls.forEach(l => { add(l.from); add(l.to); });
      if (ids.length < 2 && !p.view) return;
      ids.sort((a, b) => { const A = byId[a], B = byId[b]; return coll.compare(A.code || '￿', B.code || '￿') || ((A.y || 0) - (B.y || 0)) || ((A.x || 0) - (B.x || 0)); });
      const N = Math.min(60, ids.length), ix = {}; ids.slice(0, N).forEach((id, i) => ix[id] = i);
      const cells = Array.from({ length: N }, () => Array(N).fill(null).map(() => []));
      ls.forEach(l => {
        const a = l.attrs || {}, body = a.content || l.label || '';
        const pack = text => (l.code || '') + (text ? ' ' + text : '');
        const fwd = pack(body);
        if (ix[l.from] == null || ix[l.to] == null) return;
        cells[ix[l.from]][ix[l.to]].push(fwd);
        if (l.dir === 'both') cells[ix[l.to]][ix[l.from]].push(l.labelBack ? pack(l.labelBack) : fwd);
      });
      const names = ids.slice(0, N).map(id => lab(byId[id]));
      const hdrLen = Math.max(...names.map(cjkLen));
      const rows = [], heights = {};
      rows.push([{ v: '源＼目标', s: S.head }].concat(names.map(n => ({ v: n, s: S.mhead }))));
      heights[0] = Math.min(220, Math.max(60, Math.ceil(hdrLen * 6.2) + 10));
      let w0 = Math.min(34, Math.max(12, hdrLen + 2));
      const cw = Array(N).fill(7);
      for (let i = 0; i < N; i++) {
        const r = [{ v: names[i], s: S.rhead }];
        for (let j = 0; j < N; j++) {
          if (i === j) r.push({ v: '', s: S.diag });
          else { const t = cells[i][j].join('；'); r.push({ v: t, s: S.cell }); if (t) cw[j] = Math.max(cw[j], Math.min(26, lineW(t) / 2 + 3)); }
        }
        rows.push(r);
        let ln = 1; for (let j = 0; j < N; j++) ln = Math.max(ln, Math.ceil(lineW(cells[i][j].join('；')) / Math.max(4, cw[j] * 1.8)), Math.ceil(lineW(names[i]) / (w0 - 1))); heights[i + 1] = Math.min(150, Math.max(20, 18 * ln));
      }
      const nm = '信息交换矩阵·' + (p.name || '页面');
      sheets.push({ name: safeName(nm, used), rows, widths: [w0].concat(cw.map(Math.ceil)), heights, freezeRow: 1, freezeCol: 1 });
    });

    /* 4 说明（封面，置首） */
    const now = new Date(), pad = n => String(n).padStart(2, '0');
    const ts = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const cv = [], merges = [], ch = {};
    const blank = () => cv.push([]);
    cv.push([{ v: '体系结构规范表格', s: S.title }]); ch[0] = 44; merges.push('A1:D1');
    cv.push([{ v: '织图 · 体系结构建模工具自动生成', s: S.sub }]); merges.push('A2:D2'); ch[1] = 24;
    blank();
    const info = [['项目', meta.project], ['图号', meta.drawingNo], ['版本', meta.version], ['密级', meta.classification], ['编制', meta.author], ['审核', meta.reviewer], ['批准', meta.approver], ['日期', meta.date], ['单位', meta.org], ['生成时间', ts]];
    info.forEach(([k, v]) => { const r = cv.length; cv.push([{ v: k, s: S.label }, { v: v || '', s: S.val }, { v: '', s: S.val }, { v: '', s: S.val }]); merges.push(`B${r + 1}:D${r + 1}`); ch[r] = 22; });
    blank();
    cv.push([{ v: '包含表格', s: S.head }, { v: '内容', s: S.head }, { v: '', s: S.head }, { v: '', s: S.head }]); merges.push(`B${cv.length}:D${cv.length}`);
    const desc = { '元素清单': '各页面中带类型的元素（含编号、所属容器、责任单位及部署／安全属性）', '接口清单': '全部连线的信息交换／接口要素', '业务流清单': '全部业务流（业务对象、频度）', '集成清单': '应用之间的集成关系（集成内容、方式／协议、频度、时延）', '依赖清单': '技术组件之间的依赖关系', '网络连接清单': '部署节点、网络设备之间的连接（协议、端口、链路）', '访问控制清单': '跨域访问控制关系（策略、协议端口）', '部署清单': '按网络区域列出部署节点、规格、操作系统、地址、数量及其部署单元', '数据流清单': '数据流（数据对象、交换方式、频度）及其源、目标数据域' };
    sheets.forEach(sh => { const r = cv.length; const d = desc[sh.name] || '页面「' + sh.name.replace('信息交换矩阵·', '') + '」的源－目标信息交换矩阵'; cv.push([{ v: sh.name, s: S.val }, { v: d, s: S.val }, { v: '', s: S.val }, { v: '', s: S.val }]); merges.push(`B${r + 1}:D${r + 1}`); });
    blank();
    cv.push([{ v: '视图代码', s: S.head }, { v: '视图名称', s: S.head }, { v: '视图族', s: S.head }, { v: '', s: S.head }]); merges.push(`C${cv.length}:D${cv.length}`);
    const allV = (window.Std && Std.VIEWS) ? Object.keys(Std.VIEWS) : Object.keys(VW);
    allV.forEach(k => { const r = cv.length; cv.push([{ v: k, s: S.label }, { v: vwName(k) || VW[k], s: S.val }, { v: isIT(k) ? '信息系统架构' : 'DoDAF／UAF', s: S.val }, { v: '', s: S.val }]); merges.push(`C${r + 1}:D${r + 1}`); });
    sheets.unshift({ name: safeName('说明', used), rows: cv, widths: [22, 30, 30, 30], heights: ch, merges, noGrid: true, first: true });

    /* 打包 */
    const zip = new JSZip(), N = sheets.length;
    zip.file('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>' + sheets.map((s, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('') + '</Types>');
    zip.file('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>');
    const dn = sheets.map((s, i) => s.filter ? `<definedName name="_xlnm._FilterDatabase" localSheetId="${i}" hidden="1">'${s.name.replace(/'/g, "''")}'!$A$1:$${colL(Math.max(...s.rows.map(r => r.length)) - 1)}$${s.rows.length}</definedName>` : '').join('');
    zip.file('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><bookViews><workbookView activeTab="0"/></bookViews><sheets>' + sheets.map((s, i) => `<sheet name="${esc(s.name)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('') + '</sheets>' + (dn ? `<definedNames>${dn}</definedNames>` : '') + '</workbook>');
    zip.file('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + sheets.map((s, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join('') + `<Relationship Id="rId${N + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`);
    zip.file('xl/styles.xml', STYLES);
    const iso = now.toISOString().replace(/\.\d+Z$/, 'Z');
    zip.file('docProps/core.xml', `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>${esc(meta.project || '体系结构规范表格')}</dc:title><dc:creator>${esc(meta.author || '织图')}</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">${iso}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">${iso}</dcterms:modified></cp:coreProperties>`);
    zip.file('docProps/app.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>织图</Application></Properties>');
    sheets.forEach((s, i) => zip.file(`xl/worksheets/sheet${i + 1}.xml`, sheetXml(s)));
    return zip.generateAsync({ type: 'blob', mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', compression: 'DEFLATE' });
  }
  window.StdXlsx = { build };
})();
