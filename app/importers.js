/* ============================================================================
   importers.js — PowerPoint（.pptx）／Visio（.vsdx）架构图导入
   把用户的老图读成织图页面：层（band）、泳道（lane）、子容器（group）、
   叶子框／图标（rect…／equip）、自由文字（text）与连线（links）。

   window.Importer = {
     fromPPTX(arrayBuffer, opts) → Promise<{pages, custom, warnings, source:'pptx'}>
     fromVSDX(arrayBuffer, opts) → Promise<{…, source:'vsdx'}>
     fromFile(File)              → 按扩展名分派；.ppt/.vsd 直接拒绝
   }
   opts: { keepColors:true（默认）, rootId:'root'（可选：第一页用此 id） }

   流程（两种格式共用后半段）：
     解析器 → 中间表示 items（单位 px，左上原点）：
       {k:'box'|'text'|'line'|'pic'|'table', sid, z, x,y,w,h, geom, text, pt, bold,
        vert, fill, stroke, fillDef, strokeDef, pts, from, to, head, tail, dash, lw}
     buildPage(items) → 缩放归一 → 几何包含 → 文字归并（叶子框文字、图片题注、
       连线标注、容器标签）→ 层／泳道／子容器分类 → 连线端点吸附 → nodes/links

   依赖全局：JSZip、mkNode、uid（app.js）；THEMES 若存在用于识别“默认色”。
   ========================================================================== */
(function () {
  'use strict';

  /* ---------- 小工具 / helpers ---------- */
  const EMU = 9525;                                     // 1 px = 9525 EMU
  const R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships';
  const kidsOf = (el, n) => el ? [...el.children].filter(c => c.localName === n) : [];
  const kid = (el, n) => el ? [...el.children].find(c => c.localName === n) || null : null;
  const deep = (el, n) => el ? [...el.getElementsByTagNameNS('*', n)] : [];
  const at = (el, ...ns) => { for (const n of ns) { el = kid(el, n); if (!el) return null; } return el; };
  const num = (v, d = 0) => { const x = parseFloat(v); return isFinite(x) ? x : d; };
  const xml = s => new DOMParser().parseFromString(s, 'application/xml');
  const rAttr = (el, n) => el ? (el.getAttributeNS(R_NS, n) || el.getAttribute('r:' + n) || '') : '';
  const median = a => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  const area = b => Math.max(0, b.w) * Math.max(0, b.h);
  const inter = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  const cx = b => b.x + b.w / 2, cy = b => b.y + b.h / 2;
  const inBox = (p, b, t = 0) => p[0] >= b.x - t && p[0] <= b.x + b.w + t && p[1] >= b.y - t && p[1] <= b.y + b.h + t;
  const cleanText = s => String(s || '').replace(/\r\n?/g, '\n').replace(/[\u000b\u2028]/g, '\n').split('\n').map(l => l.replace(/\s+$/, '')).join('\n').replace(/^\n+|\n+$/g, '');
  function segDist(p, a, b) {
    const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
    let t = L ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L : 0; t = Math.max(0, Math.min(1, t));
    return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
  }
  const polyDist = (p, pts) => { let d = Infinity; for (let i = 1; i < pts.length; i++) d = Math.min(d, segDist(p, pts[i - 1], pts[i])); return pts.length === 1 ? Math.hypot(p[0] - pts[0][0], p[1] - pts[0][1]) : d; };

  /* ---------- 颜色 / colours ---------- */
  const hex2 = v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0');
  const toHex = (r, g, b) => '#' + hex2(r) + hex2(g) + hex2(b);
  const parseHex = h => { h = String(h || '').replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); if (!/^[0-9a-f]{6}$/i.test(h)) return null; return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
  const lum = h => { const c = parseHex(h); return c ? (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255 : 1; };
  function rgb2hsl([r, g, b]) { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let h = 0, s = 0; const l = (mx + mn) / 2; if (mx !== mn) { const d = mx - mn; s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn); h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; } return [h, s, l]; }
  function hsl2rgb([h, s, l]) { if (!s) return [l * 255, l * 255, l * 255]; const f = (p, q, t) => { if (t < 0) t += 1; if (t > 1) t -= 1; return t < 1 / 6 ? p + (q - p) * 6 * t : t < 1 / 2 ? q : t < 2 / 3 ? p + (q - p) * (2 / 3 - t) * 6 : p; }; const q = l < 0.5 ? l * (1 + s) : l + s - l * s, p = 2 * l - q; return [f(p, q, h + 1 / 3) * 255, f(p, q, h) * 255, f(p, q, h - 1 / 3) * 255]; }
  const PRST_CLR = { black: '000000', white: 'FFFFFF', red: 'FF0000', green: '008000', blue: '0000FF', yellow: 'FFFF00', gray: '808080', grey: '808080', orange: 'FFA500', lightGray: 'D3D3D3', darkGray: 'A9A9A9', navy: '000080' };
  const VISIO_PAL = ['#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#800000', '#008000', '#000080', '#808000', '#800080', '#008080', '#C0C0C0', '#E6E6E6', '#CDCDCD', '#B3B3B3', '#9A9A9A', '#808080', '#666666', '#4D4D4D', '#333333', '#1A1A1A'];
  /* DrawingML colour element (srgbClr/schemeClr/sysClr/prstClr + lumMod/lumOff/tint/shade) → '#RRGGBB' */
  function dmlColor(holder, theme) {
    if (!holder) return null;
    const c = [...holder.children].find(e => /^(srgbClr|schemeClr|sysClr|prstClr|scrgbClr)$/.test(e.localName));
    if (!c) return null;
    let hex = null;
    if (c.localName === 'srgbClr') hex = c.getAttribute('val');
    else if (c.localName === 'sysClr') hex = c.getAttribute('lastClr') || (c.getAttribute('val') === 'window' ? 'FFFFFF' : '000000');
    else if (c.localName === 'prstClr') hex = PRST_CLR[c.getAttribute('val')] || null;
    else if (c.localName === 'schemeClr') { const v = c.getAttribute('val'); hex = (theme || {})[{ tx1: 'dk1', bg1: 'lt1', tx2: 'dk2', bg2: 'lt2' }[v] || v] || null; }
    else if (c.localName === 'scrgbClr') hex = toHex(num(c.getAttribute('r')) / 1e5 * 255, num(c.getAttribute('g')) / 1e5 * 255, num(c.getAttribute('b')) / 1e5 * 255).slice(1);
    let rgb = parseHex(hex); if (!rgb) return null;
    for (const m of c.children) {
      const v = num(m.getAttribute('val')) / 1e5;
      if (m.localName === 'lumMod' || m.localName === 'lumOff') { const h = rgb2hsl(rgb); h[2] = m.localName === 'lumMod' ? h[2] * v : h[2] + v; h[2] = Math.max(0, Math.min(1, h[2])); rgb = hsl2rgb(h); }
      else if (m.localName === 'tint') rgb = rgb.map(x => x + (255 - x) * (1 - v));
      else if (m.localName === 'shade') rgb = rgb.map(x => x * v);
    }
    return toHex(...rgb);
  }
  /* 织图各主题自带的颜色视为“默认色”，不复制；与状态色一致时改设 status */
  function themeColorInfo() {
    const def = new Set(['#FFFFFF', '#000000']), st = [];
    try {
      if (typeof THEMES !== 'undefined') for (const t of Object.values(THEMES)) {
        for (const k of ['band', 'lane', 'group', 'box', 'note']) if (t[k]) for (const v of [t[k].fill, t[k].stroke, t[k].titleFill]) if (v) def.add(String(v).toUpperCase());
        if (t.st) for (const s of ['new', 'key']) if (t.st[s]) st.push({ s, fill: String(t.st[s].fill).toUpperCase(), stroke: String(t.st[s].stroke).toUpperCase() });
      }
    } catch (e) { /* THEMES 不可用时只用黑白 */ }
    return { def, st };
  }

  /* ---------- zip / OPC ---------- */
  async function zText(zip, p) { const f = zip.file(p); return f ? f.async('string') : null; }
  async function zXML(zip, p) { const s = await zText(zip, p); return s ? xml(s) : null; }
  function resolvePath(part, target) {
    if (!target) return null;
    if (target.startsWith('/')) return target.slice(1);
    const parts = part.split('/'); parts.pop();
    for (const seg of target.split('/')) { if (seg === '..') parts.pop(); else if (seg && seg !== '.') parts.push(seg); }
    return parts.join('/');
  }
  async function readRels(zip, part) {
    const d = await zXML(zip, part.replace(/([^/]+)$/, '_rels/$1.rels')), m = {};
    if (d) for (const r of deep(d, 'Relationship')) m[r.getAttribute('Id')] = { target: r.getAttribute('TargetMode') === 'External' ? null : resolvePath(part, r.getAttribute('Target')), type: r.getAttribute('Type') || '' };
    return m;
  }
  const MIME = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', bmp: 'image/bmp', svg: 'image/svg+xml', webp: 'image/webp' };
  async function imageURI(zip, p) {
    if (!p) return null;
    const ext = (p.split('.').pop() || '').toLowerCase(), mime = MIME[ext], f = zip.file(p);
    if (!f || !mime) return null;
    return `data:${mime};base64,${await f.async('base64')}`;
  }

  /* 文档级上下文：自定义图标去重、告警 */
  function mkCtx(opts) {
    const o = Object.assign({ keepColors: true }, opts || {});
    const ctx = { opts: o, custom: {}, warnings: [], byURI: new Map(), colors: themeColorInfo() };
    ctx.warn = m => { if (!ctx.warnings.includes(m)) ctx.warnings.push(m); };
    ctx.addIcon = (uri, name, aspect) => {
      if (ctx.byURI.has(uri)) return ctx.byURI.get(uri);
      const id = 'im' + uid();
      ctx.custom[id] = { name: name || '导入图片', uri };
      if (aspect && Math.abs(aspect - 1) > 0.05) ctx.custom[id].aspect = +aspect.toFixed(3);
      ctx.byURI.set(uri, id); return id;
    };
    return ctx;
  }

  /* =========================================================================
     PPTX 解析
     ========================================================================= */
  const PRST = {
    rect: 'rect', snip1Rect: 'rect', roundRect: 'round', snipRoundRect: 'round', round1Rect: 'round', round2SameRect: 'round', round2DiagRect: 'round', plaque: 'round',
    ellipse: 'ellipse', flowChartConnector: 'ellipse', diamond: 'diamond', flowChartDecision: 'diamond', can: 'cylinder', flowChartMagneticDisk: 'cylinder', flowChartMagneticDrum: 'cylinder',
    cloud: 'cloud', cloudCallout: 'cloud', hexagon: 'hexagon', flowChartPreparation: 'hexagon', octagon: 'octagon', triangle: 'triangle', rtTriangle: 'triangle',
    parallelogram: 'parallelogram', flowChartInputOutput: 'parallelogram', trapezoid: 'trapezoid', flowChartManualOperation: 'trapezoid', pentagon: 'pentagon',
    star5: 'star', cube: 'cube', plus: 'plus', flowChartSummingJunction: 'ellipse', donut: 'donut', frame: 'frame',
    flowChartProcess: 'rect', flowChartAlternateProcess: 'round', flowChartDocument: 'document', flowChartMultidocument: 'document', flowChartPredefinedProcess: 'predef',
    flowChartDisplay: 'display', flowChartDelay: 'delay', flowChartTerminator: 'terminator', wedgeRectCallout: 'callout', wedgeRoundRectCallout: 'callout',
    chevron: 'chevron', homePlate: 'homeplate', rightArrow: 'arrowR', leftArrow: 'arrowL', upArrow: 'arrowU', downArrow: 'arrowD', leftRightArrow: 'arrowLR', upDownArrow: 'arrowUD',
    notchedRightArrow: 'arrowR', stripedRightArrow: 'arrowR',
  };
  const LINE_PRST = /^(line|straightConnector1|bentConnector[2-5]|curvedConnector[2-5])$/;
  const VERT = /^(vert|eaVert|vert270|wordArtVert|wordArtVertRtl|mongolianVert)$/;
  const SKIP_PH = /^(dt|ftr|sldNum|hdr)$/;

  /* 2-D affine with independent x/y scale: X = a*x + e, Y = d*y + f */
  const ID = { a: 1, d: 1, e: 0, f: 0 };
  const compose = (M, T) => ({ a: M.a * T.a, d: M.d * T.d, e: M.a * T.e + M.e, f: M.d * T.f + M.f });
  const apply = (M, x, y) => [M.a * x + M.e, M.d * y + M.f];

  function readXfrm(x) {
    if (!x) return null;
    const off = kid(x, 'off'), ext = kid(x, 'ext');
    if (!off || !ext) return null;
    return { x: num(off.getAttribute('x')), y: num(off.getAttribute('y')), w: num(ext.getAttribute('cx')), h: num(ext.getAttribute('cy')), rot: num(x.getAttribute('rot')) / 60000, flipH: x.getAttribute('flipH') === '1', flipV: x.getAttribute('flipV') === '1', chOff: kid(x, 'chOff'), chExt: kid(x, 'chExt') };
  }
  /* txBody → { text, pt, bold, vert, align } */
  function readText(tx) {
    if (!tx) return { text: '' };
    const lines = [], sizes = [], bolds = [];
    let align = null;
    for (const p of kidsOf(tx, 'p')) {
      let s = '';
      const pPr = kid(p, 'pPr'); if (align == null && pPr && pPr.getAttribute('algn')) align = pPr.getAttribute('algn');
      for (const r of p.children) {
        if (r.localName === 'r' || r.localName === 'fld') {
          const t = kid(r, 't'); const v = t ? t.textContent : ''; s += v;
          const rp = kid(r, 'rPr');
          if (v.trim()) { if (rp && rp.getAttribute('sz')) sizes.push(num(rp.getAttribute('sz')) / 100); bolds.push(!!(rp && rp.getAttribute('b') === '1')); }
        } else if (r.localName === 'br') s += '\n';
      }
      if (!sizes.length) { const e = kid(p, 'endParaRPr'); if (e && e.getAttribute('sz') && s.trim()) sizes.push(num(e.getAttribute('sz')) / 100); }
      lines.push(s);
    }
    const bp = kid(tx, 'bodyPr');
    return { text: cleanText(lines.join('\n')), pt: sizes.length ? Math.max(...sizes) : null, bold: bolds.length ? bolds.filter(Boolean).length * 2 >= bolds.length : false, vert: !!(bp && VERT.test(bp.getAttribute('vert') || '')), align };
  }
  /* spPr + p:style → fill / line description */
  function readFill(spPr, style, theme) {
    const nf = kid(spPr, 'noFill'); if (nf) return { has: false };
    const sf = kid(spPr, 'solidFill'); if (sf) return { has: true, color: dmlColor(sf, theme), explicit: true };
    const gf = kid(spPr, 'gradFill'); if (gf) { const gs = deep(gf, 'gs')[0]; return { has: true, color: gs ? dmlColor(gs, theme) : null, explicit: true }; }
    if (kid(spPr, 'pattFill') || kid(spPr, 'blipFill') || kid(spPr, 'grpFill')) return { has: true, color: null, explicit: true };
    const fr = at(style, 'fillRef'); if (fr && num(fr.getAttribute('idx')) > 0) return { has: true, color: dmlColor(fr, theme), explicit: false };
    return { has: false };
  }
  function readLine(spPr, style, theme) {
    const ln = kid(spPr, 'ln'), lr = at(style, 'lnRef');
    const r = { has: false, color: null, explicit: false, w: ln ? num(ln.getAttribute('w')) / EMU : 0, dash: '', head: false, tail: false };
    if (ln) {
      const pd = kid(ln, 'prstDash'); r.dash = pd ? pd.getAttribute('val') || '' : '';
      const he = kid(ln, 'headEnd'), te = kid(ln, 'tailEnd');
      r.head = !!(he && he.getAttribute('type') && he.getAttribute('type') !== 'none');
      r.tail = !!(te && te.getAttribute('type') && te.getAttribute('type') !== 'none');
    }
    if (ln && kid(ln, 'noFill')) return r;
    const sf = ln && (kid(ln, 'solidFill') || kid(ln, 'gradFill'));
    if (sf) { r.has = true; r.explicit = true; r.color = dmlColor(sf.localName === 'gradFill' ? deep(sf, 'gs')[0] : sf, theme); return r; }
    if (lr && num(lr.getAttribute('idx')) > 0) { r.has = true; r.color = dmlColor(lr, theme); }
    return r;
  }
  /* 连接线几何：按预设生成局部折线，再做翻转/旋转/组变换 */
  function linePts(prst, xf, M, av) {
    const { x, y, w, h } = xf;
    let loc;
    if (/^bentConnector2/.test(prst)) loc = [[0, 0], [w, 0], [w, h]];
    else if (/^(bent|curved)Connector[345]/.test(prst)) { const a = av != null ? av : 0.5; loc = [[0, 0], [w * a, 0], [w * a, h], [w, h]]; }
    else loc = [[0, 0], [w, h]];
    return xformPts(loc, xf, M);
  }
  function xformPts(loc, xf, M) {
    const { x, y, w, h } = xf, c = [x + w / 2, y + h / 2], r = (xf.rot || 0) * Math.PI / 180, co = Math.cos(r), si = Math.sin(r);
    return loc.map(([px, py]) => {
      if (xf.flipH) px = w - px; if (xf.flipV) py = h - py;
      let X = x + px - c[0], Y = y + py - c[1];
      [X, Y] = [X * co - Y * si + c[0], X * si + Y * co + c[1]];
      return apply(M, X, Y);
    });
  }
  /* 自定义几何：开放路径 → 折线；闭合 → 视作框 */
  function custGeomPts(cg, xf, M) {
    const out = []; let open = true, filled = false;
    for (const p of deep(cg, 'path')) {
      const pw = num(p.getAttribute('w'), xf.w) || 1, ph = num(p.getAttribute('h'), xf.h) || 1;
      if (p.getAttribute('fill') !== 'none') filled = true;
      for (const c of p.children) {
        if (c.localName === 'close') open = false;
        for (const pt of kidsOf(c, 'pt')) out.push([num(pt.getAttribute('x')) / pw * xf.w, num(pt.getAttribute('y')) / ph * xf.h]);
      }
    }
    return { open, filled, pts: out.length ? xformPts(out, xf, M) : [] };
  }
  /* 母版/版式占位符位置继承 */
  async function placeholderMap(zip, part) {
    const d = await zXML(zip, part); const m = { byIdx: {}, byType: {} };
    if (!d) return m;
    for (const sp of deep(d, 'sp')) {
      const ph = at(sp, 'nvSpPr', 'nvPr', 'ph'); if (!ph) continue;
      const xf = readXfrm(at(sp, 'spPr', 'xfrm')); if (!xf) continue;
      if (ph.getAttribute('idx')) m.byIdx[ph.getAttribute('idx')] = xf;
      m.byType[ph.getAttribute('type') || 'body'] = m.byType[ph.getAttribute('type') || 'body'] || xf;
    }
    return m;
  }
  async function readTheme(zip) {
    const t = {}; const names = Object.keys(zip.files).filter(f => /^ppt\/theme\/theme\d+\.xml$/.test(f)).sort();
    const d = names.length ? await zXML(zip, names[0]) : null;
    const cs = d && deep(d, 'clrScheme')[0];
    if (cs) for (const c of cs.children) { const v = dmlColor(c, {}); if (v) t[c.localName] = v.slice(1); }
    return t;
  }

  async function fromPPTX(buf, opts) {
    const zip = await JSZip.loadAsync(buf), ctx = mkCtx(opts);
    const pres = await zXML(zip, 'ppt/presentation.xml');
    if (!pres) throw new Error('不是有效的 .pptx 文件（缺少 ppt/presentation.xml）');
    const prels = await readRels(zip, 'ppt/presentation.xml'), theme = await readTheme(zip);
    const slides = deep(pres, 'sldId').map(s => prels[rAttr(s, 'id')]?.target).filter(Boolean);
    const pages = [];
    for (let si = 0; si < slides.length; si++) {
      const part = slides[si], d = await zXML(zip, part); if (!d) continue;
      const rels = await readRels(zip, part);
      const layout = Object.values(rels).find(r => /slideLayout$/.test(r.type))?.target;
      const lph = layout ? await placeholderMap(zip, layout) : { byIdx: {}, byType: {} };
      let mph = { byIdx: {}, byType: {} };
      if (layout) { const lr = await readRels(zip, layout); const ms = Object.values(lr).find(r => /slideMaster$/.test(r.type))?.target; if (ms) mph = await placeholderMap(zip, ms); }
      const st = { items: [], z: 0, title: null, skipped: { chart: 0, smart: 0, ole: 0, emf: 0 } };
      const tree = at(d.documentElement, 'cSld', 'spTree');
      await walkPPTX(tree, ID, { zip, rels, theme, lph, mph, ctx, st });
      if (st.skipped.chart) ctx.warn(`第 ${si + 1} 页：${st.skipped.chart} 个图表未导入`);
      if (st.skipped.smart) ctx.warn(`第 ${si + 1} 页：${st.skipped.smart} 个 SmartArt 未导入（可在 PowerPoint 中“转换为形状”后再导入）`);
      if (st.skipped.ole) ctx.warn(`第 ${si + 1} 页：${st.skipped.ole} 个嵌入对象未导入`);
      if (st.skipped.emf) ctx.warn(`第 ${si + 1} 页：${st.skipped.emf} 张 EMF/WMF 等矢量图元文件无法在浏览器显示，已以占位框代替`);
      // px
      for (const it of st.items) { for (const k of ['x', 'y', 'w', 'h']) if (it[k] != null) it[k] /= EMU; if (it.pts) it.pts = it.pts.map(p => [p[0] / EMU, p[1] / EMU]); }
      if (!st.items.length) continue;
      const pg = buildPage(st.items, ctx, `第 ${si + 1} 页`);
      if (!pg.nodes.length) continue;
      pg.name = cleanText(st.title || '').split('\n')[0] || pg.titleText || `幻灯片 ${si + 1}`;
      delete pg.titleText;
      pages.push(pg);
    }
    finishPages(pages, ctx);
    return { pages, custom: ctx.custom, warnings: ctx.warnings, source: 'pptx' };
  }

  async function walkPPTX(container, M, E) {
    const { st, theme, ctx } = E;
    for (const el of [...container.children]) {
      const ln = el.localName;
      if (ln === 'AlternateContent') {
        const ch = kid(el, 'Choice'), fb = kid(el, 'Fallback'), n0 = st.items.length;
        if (ch) await walkPPTX(ch, M, E);
        if (st.items.length === n0 && fb) await walkPPTX(fb, M, E);
        continue;
      }
      if (ln === 'grpSp') {
        const xf = readXfrm(at(el, 'grpSpPr', 'xfrm'));
        let T = ID;
        if (xf && xf.chOff && xf.chExt) {
          const cw = num(xf.chExt.getAttribute('cx')), chh = num(xf.chExt.getAttribute('cy'));
          const sx = cw ? xf.w / cw : 1, sy = chh ? xf.h / chh : 1;
          T = { a: sx, d: sy, e: xf.x - num(xf.chOff.getAttribute('x')) * sx, f: xf.y - num(xf.chOff.getAttribute('y')) * sy };
        }
        await walkPPTX(el, compose(M, T), E);
        continue;
      }
      if (ln === 'sp' || ln === 'cxnSp') {
        const nv = kid(el, ln === 'sp' ? 'nvSpPr' : 'nvCxnSpPr'), cNvPr = kid(nv, 'cNvPr');
        const ph = at(nv, 'nvPr', 'ph'), phType = ph ? (ph.getAttribute('type') || 'body') : null;
        if (phType && SKIP_PH.test(phType)) continue;
        if (cNvPr && cNvPr.getAttribute('hidden') === '1') continue;
        const spPr = kid(el, 'spPr'), style = kid(el, 'style');
        let xf = readXfrm(kid(spPr, 'xfrm'));
        if (!xf && ph) xf = E.lph.byIdx[ph.getAttribute('idx')] || E.lph.byType[phType] || E.mph.byType[phType] || (/title/i.test(phType) ? (E.lph.byType.title || E.mph.byType.title) : null);
        if (!xf) continue;
        const sid = cNvPr ? cNvPr.getAttribute('id') : null, z = st.z++;
        const tx = readText(kid(el, 'txBody'));
        if (phType && /title/i.test(phType) && tx.text && !st.title) st.title = tx.text;
        const fill = readFill(spPr, style, theme), line = readLine(spPr, style, theme);
        const pg = at(spPr, 'prstGeom'), prst = pg ? pg.getAttribute('prst') : null, cg = kid(spPr, 'custGeom');
        const lineBase = { k: 'line', sid, z, text: tx.text, pt: tx.pt, stroke: line.color, strokeDef: !line.explicit, head: line.head, tail: line.tail, dash: line.dash, lw: line.w };
        if (ln === 'cxnSp' || (prst && LINE_PRST.test(prst))) {
          const gd = pg && deep(pg, 'gd').find(g => g.getAttribute('name') === 'adj1');
          const av = gd ? num((gd.getAttribute('fmla') || '').replace(/^val\s+/, ''), 50000) / 100000 : null;
          const cx0 = at(nv, 'cNvCxnSpPr');
          const sc = cx0 && kid(cx0, 'stCxn'), ec = cx0 && kid(cx0, 'endCxn');
          st.items.push(Object.assign(lineBase, { pts: linePts(prst || 'line', xf, M, av), from: sc ? sc.getAttribute('id') : null, to: ec ? ec.getAttribute('id') : null }));
          continue;
        }
        if (cg) {
          const g = custGeomPts(cg, xf, M);
          if (g.open && !fill.has && g.pts.length >= 2) { st.items.push(Object.assign(lineBase, { pts: g.pts })); continue; }
        }
        const [X, Y] = apply(M, xf.x, xf.y);
        let w = xf.w * M.a, h = xf.h * M.d, x = X, y = Y, vert = tx.vert;
        const rq = Math.round(((xf.rot % 180) + 180) % 180);
        if (Math.abs(rq - 90) < 5) { x = X + w / 2 - h / 2; y = Y + h / 2 - w / 2; [w, h] = [h, w]; vert = vert || !!tx.text; }
        const isText = !fill.has && !line.has;
        if (isText && !tx.text) continue;                               // 不可见空形状
        let geom = PRST[prst] || 'rect';
        /* 单侧圆角矩形：本软件导出的自由曲线，或旋转 90°／270° 的“同侧圆角矩形”（round2SameRect 默认圆角在上边） */
        if (cg && !rq) { const lp = []; for (const pth of deep(cg, 'path')) { const pw = num(pth.getAttribute('w'), xf.w) || 1, ph = num(pth.getAttribute('h'), xf.h) || 1; for (const c of pth.children) for (const pt of kidsOf(c, 'pt')) lp.push([num(pt.getAttribute('x')) / pw * xf.w, num(pt.getAttribute('y')) / ph * xf.h]); } if (lp.length >= 6) geom = sideRound(lp, xf.w, xf.h) || geom; }
        if (prst === 'round2SameRect' && Math.abs(rq - 90) < 5) { const r = ((Math.round(xf.rot) % 360) + 360) % 360; geom = Math.abs(r - 270) < 5 ? 'roundL' : Math.abs(r - 90) < 5 ? 'roundR' : geom; }
        st.items.push({
          k: isText ? 'text' : 'box', sid, z, x, y, w, h, geom, text: tx.text, pt: tx.pt, bold: tx.bold, vert, align: tx.align,
          fill: fill.color, fillDef: !fill.explicit, hasFill: fill.has, stroke: line.has ? line.color : null, strokeDef: !line.explicit, ph: phType, txBox: !!at(nv, 'cNvSpPr')?.getAttribute('txBox'),
        });
        continue;
      }
      if (ln === 'pic') {
        const nv = kid(el, 'nvPicPr'), cNvPr = kid(nv, 'cNvPr');
        const xf = readXfrm(at(el, 'spPr', 'xfrm')); if (!xf) continue;
        const blip = deep(kid(el, 'blipFill'), 'blip')[0];
        const rel = blip ? E.rels[rAttr(blip, 'embed')] : null;
        const uri = rel ? await imageURI(E.zip, rel.target) : null;
        const [x, y] = apply(M, xf.x, xf.y), w = xf.w * M.a, h = xf.h * M.d;
        const name = (cNvPr && (cNvPr.getAttribute('descr') || cNvPr.getAttribute('name')) || '').replace(/\.(png|jpe?g|gif|bmp|svg|emf|wmf)$/i, '');
        if (!uri) { st.skipped.emf++; st.items.push({ k: 'box', sid: cNvPr?.getAttribute('id'), z: st.z++, x, y, w, h, geom: 'rect', text: '［图片］', pt: null, hasFill: true }); continue; }
        st.items.push({ k: 'pic', sid: cNvPr?.getAttribute('id'), z: st.z++, x, y, w, h, uri, name: /^(picture|图片|image|preencoded)\s*\d*$/i.test(name) ? '' : name });
        continue;
      }
      if (ln === 'graphicFrame') {
        const gd = at(el, 'graphic', 'graphicData'), uriT = gd ? gd.getAttribute('uri') || '' : '';
        const xf = readXfrm(kid(el, 'xfrm'));
        const tbl = gd && kid(gd, 'tbl');
        if (tbl && xf) {
          const rows = kidsOf(tbl, 'tr').map(tr => kidsOf(tr, 'tc').filter(tc => tc.getAttribute('hMerge') !== '1' && tc.getAttribute('vMerge') !== '1').map(tc => readText(kid(tc, 'txBody')).text.replace(/\n/g, ' ')));
          const [x, y] = apply(M, xf.x, xf.y);
          st.items.push({ k: 'table', sid: at(el, 'nvGraphicFramePr', 'cNvPr')?.getAttribute('id'), z: st.z++, x, y, w: xf.w * M.a, h: xf.h * M.d, rows });
        } else if (/chart/.test(uriT)) st.skipped.chart++;
        else if (/diagram/.test(uriT)) st.skipped.smart++;
        else st.skipped.ole++;
      }
    }
  }

  /* =========================================================================
     VSDX 解析
     ========================================================================= */
  const VSD_GEOM = [
    [/rounded|圆角/i, 'round'], [/decision|diamond|判定|菱形/i, 'diamond'], [/ellipse|circle|oval|椭圆|圆形/i, 'ellipse'],
    [/data\s*store|database|cylinder|磁盘|数据库|圆柱/i, 'cylinder'], [/cloud|云/i, 'cloud'], [/hexagon|preparation|六边形|准备/i, 'hexagon'],
    [/multi.?doc|document|文档/i, 'document'], [/terminator|start\/end|开始\/结束|起止/i, 'terminator'], [/predefined|子流程|预定义/i, 'predef'],
    [/^data$|^数据$|parallelogram|平行四边形/i, 'parallelogram'], [/delay|延迟/i, 'delay'], [/display|显示/i, 'display'], [/triangle|三角/i, 'triangle'],
    [/octagon|八边形/i, 'octagon'], [/pentagon|五边形/i, 'pentagon'], [/trapezoid|梯形/i, 'trapezoid'], [/star|星/i, 'star'], [/cube|立方/i, 'cube'],
  ];
  const VSD_CONN = /connector|连接线|连接符|dynamic|line-curve|^line$|^直线|arrow$/i;
  function cellMap(el) { const m = {}; if (el) for (const c of kidsOf(el, 'Cell')) m[c.getAttribute('N')] = c; return m; }
  function vColor(v) {
    if (v == null || v === '') return null;
    if (/^#[0-9a-f]{6}$/i.test(v)) return v.toUpperCase();
    if (/^\d+$/.test(v)) return VISIO_PAL[+v] || null;
    const m = /RGB\((\d+),\s*(\d+),\s*(\d+)\)/i.exec(v); return m ? toHex(+m[1], +m[2], +m[3]) : null;
  }

  async function fromVSDX(buf, opts) {
    const zip = await JSZip.loadAsync(buf), ctx = mkCtx(opts);
    const pagesPart = 'visio/pages/pages.xml', pd = await zXML(zip, pagesPart);
    if (!pd) throw new Error('不是有效的 .vsdx 文件（缺少 visio/pages/pages.xml）');
    const prels = await readRels(zip, pagesPart);
    /* 样式表：FillStyle/LineStyle/TextStyle 继承链 */
    const styles = {};
    const docx = await zXML(zip, 'visio/document.xml');
    if (docx) for (const s of deep(docx, 'StyleSheet')) styles[s.getAttribute('ID')] = { cells: cellMap(s), line: s.getAttribute('LineStyle'), fill: s.getAttribute('FillStyle'), text: s.getAttribute('TextStyle'), char: kidsOf(s, 'Section').find(x => x.getAttribute('N') === 'Character') };
    /* 主控形状 */
    const masters = {};
    const mrels = await readRels(zip, 'visio/masters/masters.xml'), md = await zXML(zip, 'visio/masters/masters.xml');
    if (md) for (const m of deep(md, 'Master')) {
      const rel = kid(m, 'Rel'), tgt = rel ? mrels[rAttr(rel, 'id')]?.target : null;
      const mx = tgt ? await zXML(zip, tgt) : null, shapes = {};
      let top = null;
      if (mx) { const sh = at(mx.documentElement, 'Shapes'); top = sh ? kid(sh, 'Shape') : null; for (const s of deep(mx, 'Shape')) shapes[s.getAttribute('ID')] = s; }
      masters[m.getAttribute('ID')] = { name: m.getAttribute('NameU') || m.getAttribute('Name') || '', name2: m.getAttribute('Name') || '', shapes, top };
    }
    const pages = [];
    let pi = 0;
    for (const pg of kidsOf(pd.documentElement, 'Page')) {
      pi++;
      if (pg.getAttribute('Background') === '1') continue;
      const rel = kid(pg, 'Rel'), part = rel ? prels[rAttr(rel, 'id')]?.target : null;
      const d = part ? await zXML(zip, part) : null; if (!d) continue;
      const rels = await readRels(zip, part);
      const ps = cellMap(kid(pg, 'PageSheet'));
      const PH = num(ps.PageHeight?.getAttribute('V'), 11);
      const st = { items: [], z: 0, owner: {}, conns: [], emf: 0 };
      const E = { zip, rels, masters, styles, st, PH, ctx };
      const shapesEl = at(d.documentElement, 'Shapes');
      if (shapesEl) await walkVSDX(shapesEl, 0, 0, null, null, E);
      /* Connects：FromSheet=连接线，ToSheet=形状 */
      for (const c of deep(d, 'Connect')) {
        const f = c.getAttribute('FromSheet'), t = c.getAttribute('ToSheet'), fc = c.getAttribute('FromCell') || '';
        const L = st.items.find(i => i.k === 'line' && i.sid === f); if (!L) continue;
        const tgt = st.owner[t] || t;
        if (/^Begin/.test(fc)) L.from = tgt; else if (/^End/.test(fc)) L.to = tgt;
      }
      if (st.emf) ctx.warn(`Visio 页“${pg.getAttribute('Name') || pi}”：${st.emf} 个 EMF/OLE 图元无法在浏览器显示，已以占位框代替`);
      for (const it of st.items) { for (const k of ['x', 'y', 'w', 'h']) if (it[k] != null) it[k] *= 96; if (it.pts) it.pts = it.pts.map(p => [p[0] * 96, p[1] * 96]); }
      if (!st.items.length) continue;
      const page = buildPage(st.items, ctx, `Visio 页 ${pi}`);
      if (!page.nodes.length) continue;
      page.name = pg.getAttribute('Name') || pg.getAttribute('NameU') || page.titleText || `Visio 页 ${pi}`;
      delete page.titleText;
      pages.push(page);
    }
    finishPages(pages, ctx);
    return { pages, custom: ctx.custom, warnings: ctx.warnings, source: 'vsdx' };
  }

  /* 取单元格：形状 → 主控形状 → 样式链 */
  function vCell(sh, N, E, kind) {
    const own = cellMap(sh.el)[N]; if (own) return own.getAttribute('V');
    if (sh.ms) { const c = cellMap(sh.ms)[N]; if (c) return c.getAttribute('V'); }
    if (kind) {
      let sid = sh.el.getAttribute(kind) ?? sh.ms?.getAttribute(kind), guard = 0;
      while (sid != null && E.styles[sid] && guard++ < 12) { const s = E.styles[sid]; if (s.cells[N]) return s.cells[N].getAttribute('V'); sid = s[kind === 'FillStyle' ? 'fill' : kind === 'LineStyle' ? 'line' : 'text']; }
    }
    return null;
  }
  const vSections = (el, N) => el ? kidsOf(el, 'Section').filter(s => s.getAttribute('N') === N) : [];
  function vText(el) {
    const t = el && kid(el, 'Text'); if (!t) return '';
    let s = ''; const rec = n => { for (const c of n.childNodes) { if (c.nodeType === 3) s += c.nodeValue; else if (c.nodeType === 1 && !/^(cp|pp|tp)$/.test(c.localName)) rec(c); } };
    rec(t); return cleanText(s);
  }
  /* 几何：返回 { closed, noFill, noLine, pts(局部英寸,y 向上), kinds } */
  /* 单侧圆角矩形识别：一侧两角为直角顶点，另一侧两角被圆弧切掉（本软件导出的左／右圆角矩形） */
  function sideRound(pts, w, h) {
    const e = Math.min(w, h) * 0.02, has = (x, y) => pts.some(p => Math.abs(p[0] - x) < e && Math.abs(p[1] - y) < e);
    const r = Math.min(w, h) * 0.45, nearEdge = pts.every(p => Math.min(p[0], w - p[0], p[1], h - p[1]) < r * 0.6 + e);
    if (!nearEdge) return null;
    const L = has(0, 0) && has(0, h), R = has(w, 0) && has(w, h);
    const span = f => { const ys = pts.filter(f).map(p => p[1]); return ys.length >= 2 ? Math.max(...ys) - Math.min(...ys) : 0; };
    if (R && !has(0, 0) && !has(0, h) && span(p => p[0] < e) >= h * 0.25 && pts.some(p => p[1] < e && p[0] <= w * 0.4)) return 'roundL';
    if (L && !has(w, 0) && !has(w, h) && span(p => p[0] > w - e) >= h * 0.25 && pts.some(p => p[1] < e && p[0] >= w * 0.6)) return 'roundR';
    return null;
  }
  function vGeom(sh, w, h) {
    let secs = vSections(sh.el, 'Geometry'); if (!secs.length && sh.ms) secs = vSections(sh.ms, 'Geometry');
    const g = { secs: 0, closed: false, open: false, noFill: true, noLine: true, pts: [], kinds: new Set() };
    for (const s of secs) {
      const cm = cellMap(s); if (cm.NoShow && cm.NoShow.getAttribute('V') === '1') continue;
      g.secs++;
      if (!(cm.NoFill && cm.NoFill.getAttribute('V') === '1')) g.noFill = false;
      if (!(cm.NoLine && cm.NoLine.getAttribute('V') === '1')) g.noLine = false;
      const pts = [];
      for (const r of kidsOf(s, 'Row')) {
        const T = r.getAttribute('T') || ''; g.kinds.add(T); const rc = cellMap(r);
        const X = rc.X ? num(rc.X.getAttribute('V')) : null, Y = rc.Y ? num(rc.Y.getAttribute('V')) : null;
        if (X == null || Y == null) { if (T === 'Ellipse') g.closed = true; continue; }
        const rel = /^Rel/.test(T); pts.push([rel ? X * w : X, rel ? Y * h : Y]);
      }
      if (pts.length >= 2) { const a = pts[0], b = pts[pts.length - 1]; if (Math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-4) g.closed = true; else g.open = true; }
      if (!g.pts.length) g.pts = pts;
    }
    return g;
  }
  async function walkVSDX(container, ox, oy, inhMaster, ownerTop, E) {
    const { st, masters, PH } = E;
    for (const el of kidsOf(container, 'Shape')) {
      const id = el.getAttribute('ID');
      const mId = el.getAttribute('Master') || inhMaster;
      const M = mId ? masters[mId] : null;
      const ms = M ? (el.getAttribute('MasterShape') ? M.shapes[el.getAttribute('MasterShape')] : (el.getAttribute('Master') ? M.top : null)) : null;
      const sh = { el, ms };
      if (ownerTop) st.owner[id] = ownerTop;
      const c = N => vCell(sh, N, E), cn = (N, d = 0) => num(c(N), d);
      const w = cn('Width'), h = cn('Height'), pinX = cn('PinX'), pinY = cn('PinY');
      const lpx = c('LocPinX') != null ? cn('LocPinX') : w / 2, lpy = c('LocPinY') != null ? cn('LocPinY') : h / 2;
      const left = ox + pinX - lpx, bottom = oy + pinY - lpy;
      const toPage = (lx, ly) => [left + lx, PH - (bottom + ly)];
      /* 文字：自身 <Text>；没有 <Text> 元素时继承主控形状的文字 */
      const mText = (e, m) => kid(e, 'Text') ? vText(e) : (m ? vText(m) : '');
      const text = mText(el, ms) || '';
      const mname = M ? (M.name + ' ' + M.name2) : '';
      const type = el.getAttribute('Type') || 'Shape';
      const z = st.z++;
      const chSz = (() => { const sec = vSections(el, 'Character')[0] || (ms && vSections(ms, 'Character')[0]); const r = sec && kid(sec, 'Row'); const cm = cellMap(r); return { pt: cm.Size ? num(cm.Size.getAttribute('V')) * 72 : null, bold: cm.Style ? (num(cm.Style.getAttribute('V')) & 1) === 1 : false }; })();
      const lineCol = vColor(vCell(sh, 'LineColor', E, 'LineStyle')), linePat = num(vCell(sh, 'LinePattern', E, 'LineStyle'), 1);
      const beginArrow = num(vCell(sh, 'BeginArrow', E, 'LineStyle')), endArrow = num(vCell(sh, 'EndArrow', E, 'LineStyle'));
      const lw = num(vCell(sh, 'LineWeight', E, 'LineStyle'), 0.01) * 96;
      const dash = linePat === 1 ? '' : linePat === 2 ? 'dash' : linePat === 3 ? 'dot' : linePat >= 4 ? 'dashDot' : '';
      const isOneD = c('BeginX') != null && c('EndX') != null;
      if (isOneD || (VSD_CONN.test(mname) && !/arrow/i.test(mname.split(' ')[0] || '') && c('BeginX') != null)) {
        const bx = cn('BeginX'), by = cn('BeginY'), ex = cn('EndX'), ey = cn('EndY');
        const g = vGeom(sh, w, h);
        let pts = g.pts.length >= 2 ? g.pts.map(p => toPage(p[0], p[1])) : [[ox + bx, PH - (oy + by)], [ox + ex, PH - (oy + ey)]];
        pts[0] = [ox + bx, PH - (oy + by)]; pts[pts.length - 1] = [ox + ex, PH - (oy + ey)];
        st.items.push({ k: 'line', sid: id, z, pts, text, pt: chSz.pt, head: beginArrow > 0, tail: endArrow > 0, dash, lw, stroke: lineCol, strokeDef: false });
        continue;
      }
      /* 图片 / OLE */
      if (type === 'Foreign') {
        const fd = kid(el, 'ForeignData');
        const ftype = fd ? fd.getAttribute('ForeignType') || '' : '', comp = fd ? (fd.getAttribute('CompressionType') || '').toLowerCase() : '';
        let uri = null;
        const r = fd && kid(fd, 'Rel');
        if (r) { const rel = E.rels[rAttr(r, 'id')]; uri = rel ? await imageURI(E.zip, rel.target) : null; }
        else if (fd && /bitmap/i.test(ftype) && fd.textContent.trim()) { const mime = MIME[comp === 'jpeg' ? 'jpg' : comp] || 'image/png'; uri = `data:${mime};base64,${fd.textContent.replace(/\s+/g, '')}`; }
        const [x, y] = toPage(0, h);
        if (!uri) { st.emf++; st.items.push({ k: 'box', sid: id, z, x, y, w, h, geom: 'rect', text: text || '［图片］', hasFill: true }); continue; }
        st.items.push({ k: 'pic', sid: id, z, x, y, w, h, uri, name: text });
        continue;
      }
      const g = vGeom(sh, w, h);
      const fillPat = num(vCell(sh, 'FillPattern', E, 'FillStyle'), 1);
      const fillCol = vColor(vCell(sh, 'FillForegnd', E, 'FillStyle'));
      const hasFill = g.secs > 0 && !g.noFill && fillPat > 0;
      const hasLine = g.secs > 0 && !g.noLine && linePat > 0;
      const subs = at(el, 'Shapes');
      /* 二维开放路径（无填充）→ 视作连线（如本软件导出的折线） */
      if (!subs && g.secs && g.open && !g.closed && !hasFill && g.pts.length >= 2) {
        st.items.push({ k: 'line', sid: id, z, pts: g.pts.map(p => toPage(p[0], p[1])), text, pt: chSz.pt, head: beginArrow > 0, tail: endArrow > 0, dash, lw, stroke: lineCol, strokeDef: false });
        continue;
      }
      let geom = 'rect';
      const mm = VSD_GEOM.find(([re]) => re.test(mname)); if (mm) geom = mm[1];
      else if (g.kinds.has('Ellipse')) geom = 'ellipse';
      else if (num(c('Rounding')) > 0) geom = 'round';
      else if (g.closed && g.pts.length >= 8 && sideRound(g.pts, w, h)) geom = sideRound(g.pts, w, h);
      else if (g.pts.length === 5 && g.closed) { const p = g.pts; const mx = v => Math.abs(v - w / 2) < w * 0.05, my = v => Math.abs(v - h / 2) < h * 0.05; if (p.slice(0, 4).every(q => mx(q[0]) || my(q[1])) && p.slice(0, 4).filter(q => mx(q[0])).length === 2) geom = 'diamond'; }
      const [x, y] = toPage(0, h);
      let txt = text;
      if (subs && el.getAttribute('Master')) {
        /* 主控形状组合（模具图形）：整体视作一个形状，文字取自身或子形状 */
        if (!txt) txt = deep(subs, 'Shape').map(e => mText(e, M && e.getAttribute('MasterShape') ? M.shapes[e.getAttribute('MasterShape')] : null)).filter(Boolean).join('\n');
        for (const s of deep(subs, 'Shape')) st.owner[s.getAttribute('ID')] = ownerTop || id;
        st.items.push({ k: 'box', sid: id, z, x, y, w, h, geom, text: txt, pt: chSz.pt, bold: chSz.bold, fill: fillCol, fillDef: false, hasFill: true, stroke: lineCol, strokeDef: false });
        continue;
      }
      const visible = hasFill || hasLine || (type === 'Group' && !!subs && !!txt);   // 用户组合带文字：视作（无框）容器
      if (visible || txt) st.items.push({ k: visible ? 'box' : 'text', sid: id, z, x, y, w, h, geom, text: txt, pt: chSz.pt, bold: chSz.bold, fill: hasFill ? fillCol : null, fillDef: false, hasFill, stroke: hasLine ? lineCol : null, strokeDef: false, vert: num(vSections(el, 'TextBlock')[0] && cellMap(vSections(el, 'TextBlock')[0]).TextDirection?.getAttribute('V')) === 1 });
      if (subs) await walkVSDX(subs, left, bottom, el.getAttribute('Master') || inhMaster, null, E);
    }
  }

  /* =========================================================================
     公共：items → 织图页面（层级推断的核心）
     ========================================================================= */
  const TOL = 12;                                         // 连线端点吸附容差（缩放后 px）
  function buildPage(items0, ctx, label) {
    const opts = ctx.opts;
    let items = items0.filter(it => it.k === 'line' ? it.pts && it.pts.length >= 2 : it.w > 0.5 && it.h > 0.5);
    if (!items.length) return { nodes: [], links: [] };
    items.forEach((it, i) => { it.i = i; it.dead = false; it.par = null; if (it.text == null) it.text = ''; });

    /* ---- 1. 缩放与归一：典型叶子框 ≈150px 宽，内容从 (0,0) 开始 ---- */
    let x0 = Infinity, y0 = Infinity;
    for (const it of items) { const ps = it.k === 'line' ? it.pts : [[it.x, it.y]]; for (const p of ps) { x0 = Math.min(x0, p[0]); y0 = Math.min(y0, p[1]); } }
    const boxes0 = items.filter(it => it.k === 'box');
    const leafW = boxes0.filter(b => b.text && !boxes0.some(o => o !== b && inter(o, b) > 0.9 * area(o) && area(o) < area(b))).map(b => b.w);
    const typical = median(leafW.length ? leafW : items.filter(it => it.k === 'pic').map(p => p.w * 1.3));
    let s = typical ? (typical >= 110 && typical <= 210 ? 1 : 150 / typical) : 1;
    s = Math.max(0.25, Math.min(8, s));
    for (const it of items) {
      if (it.k === 'line') it.pts = it.pts.map(p => [(p[0] - x0) * s, (p[1] - y0) * s]);
      else { it.x = (it.x - x0) * s; it.y = (it.y - y0) * s; it.w *= s; it.h *= s; }
      if (it.pt) it.px = it.pt * 4 / 3 * s;                // s 坐标系下的字号（px），终缩放时再取整限幅
    }
    const lines = items.filter(it => it.k === 'line');
    const shapes = items.filter(it => it.k !== 'line');
    const isBoxK = it => it.k === 'box';

    /* ---- 2. 几何包含：父 = 覆盖子框 ≥90% 的最小框（文字框 ≥60% 且中心在内） ---- */
    const setParents = () => {
      for (const it of shapes) {
        if (it.dead) continue;
        let best = null; const A = area(it);
        for (const C of shapes) {
          if (C === it || C.dead || !isBoxK(C)) continue;
          const AC = area(C), cov = inter(it, C) / (A || 1);
          if (it.k === 'text') { if (cov < 0.6 || !inBox([cx(it), cy(it)], C) || AC < A * 0.5) continue; }
          else { if (cov < 0.9) continue; if (!(AC > A * 1.02 || (AC >= A * 0.98 && C.z < it.z))) continue; }
          if (!best || AC < area(best) || (AC === area(best) && C.z > best.z)) best = C;
        }
        it.par = best;
      }
    };
    setParents();
    const childrenOf = C => shapes.filter(it => !it.dead && it.par === C);
    const alias = new Map();                                   // 被合并元素 sid → 承接元素
    const absorb = (from, into) => { from.dead = true; alias.set(from, into); };
    const nonText = C => childrenOf(C).filter(k => k.k !== 'text');

    /* ---- 3. 重叠的同尺寸框（阴影/叠放）：合并为一个 ---- */
    for (const C of shapes) {
      if (C.dead || !isBoxK(C)) continue;
      const ks = nonText(C);
      if (ks.length === 1 && isBoxK(ks[0]) && area(ks[0]) > 0.85 * area(C) && !nonText(ks[0]).length) {
        const k = ks[0]; if (!k.text) { k.text = C.text; k.pt = k.pt || C.pt; k.px = k.px || C.px; }
        if (!k.hasFill && C.hasFill) { k.hasFill = true; k.fill = C.fill; k.fillDef = C.fillDef; }
        for (const t of childrenOf(C)) if (t !== k) t.par = k;
        k.par = C.par; absorb(C, k);
      }
    }

    /* ---- 4. 叶子框里的文字框 / 小图标 → 并入该框 ---- */
    for (const B of shapes) {
      if (B.dead || !isBoxK(B)) continue;
      const ks = childrenOf(B); if (!ks.length) continue;
      const texts = ks.filter(k => k.k === 'text'), pics = ks.filter(k => k.k === 'pic');
      if (ks.length !== texts.length + pics.length || pics.length > 1) continue;
      if (texts.length) {
        texts.sort((a, b) => a.y - b.y || a.x - b.x);
        B.text = [B.text, ...texts.map(t => t.text)].filter(Boolean).join('\n');
        const big = texts.reduce((a, b) => ((b.px || 0) > (a.px || 0) ? b : a));
        if (big.px) B.px = Math.max(B.px || 0, big.px);
        B.bold = B.bold || texts.some(t => t.bold);
        texts.forEach(t => absorb(t, B));
      }
      if (pics.length) {
        const p = pics[0];
        B.icon = ctx.addIcon(p.uri, p.name || B.text.split('\n')[0], p.w / p.h);
        B.picBig = area(p) >= 0.25 * area(B);
        absorb(p, B);
      }
    }

    /* ---- 5. 图片下方的题注 → equip 文字 ---- */
    const freeTexts = () => shapes.filter(t => !t.dead && t.k === 'text');
    for (const p of shapes.filter(q => q.k === 'pic' && !q.dead)) {
      let best = null, bd = Infinity;
      for (const t of freeTexts()) {
        const gap = t.y - (p.y + p.h);
        if (gap < -0.45 * p.h || gap > Math.max(24, 0.6 * p.h)) continue;
        if (Math.abs(cx(t) - cx(p)) > Math.max(p.w, t.w) * 0.6) continue;
        if (t.h > 3 * p.h) continue;
        if (Math.abs(gap) < bd) { bd = Math.abs(gap); best = t; }
      }
      if (best) {
        p.text = best.text; p.px = best.px; p.bold = best.bold;
        const X0 = Math.min(p.x, best.x), X1 = Math.max(p.x + p.w, best.x + best.w);
        p.capH = Math.max(best.y + best.h, p.y + p.h) - p.y - p.h; p.capW = X1 - X0; p.capX = X0;
        absorb(best, p);
      }
    }

    /* ---- 6. 连线标注：线自身文字；或压在线上的小文字框／小标签框 ---- */
    /* 典型叶子框尺寸（有字、无子框），用作各种相对阈值 */
    const leafy = shapes.filter(b => isBoxK(b) && !b.dead && b.text && !childrenOf(b).some(k => k.k !== 'text'));
    const refBoxes = leafy.length >= 3 ? leafy : shapes.filter(isBoxK);
    const typH = median(refBoxes.map(b => b.h)) || 40, typW = median(refBoxes.map(b => b.w)) || 150;
    /* 文字中心到折线的距离，及其投影点在整条线上的相对位置（0..1） */
    const along = (p, pts) => {
      let tot = 0, best = Infinity, at0 = 0;
      for (let i = 1; i < pts.length; i++) {
        const a = pts[i - 1], b = pts[i], L = Math.hypot(b[0] - a[0], b[1] - a[1]), d = segDist(p, a, b);
        if (d < best) { best = d; const t = L ? Math.max(0, Math.min(1, ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (L * L))) : 0; at0 = tot + t * L; }
        tot += L;
      }
      return { d: best, r: tot ? at0 / tot : 0.5 };
    };
    /* 线段与矩形相交（Liang–Barsky 裁剪） */
    const segHits = (a, b, r, pad = 2) => {
      let t0 = 0, t1 = 1; const dx = b[0] - a[0], dy = b[1] - a[1];
      for (const [p, q] of [[-dx, a[0] - (r.x - pad)], [dx, r.x + r.w + pad - a[0]], [-dy, a[1] - (r.y - pad)], [dy, r.y + r.h + pad - a[1]]]) {
        if (p === 0) { if (q < 0) return false; } else { const t = q / p; if (p < 0) { if (t > t1) return false; if (t > t0) t0 = t; } else { if (t < t0) return false; if (t < t1) t1 = t; } }
      }
      return true;
    };
    const touches = (t, L) => L.pts.some((p, i) => i && segHits(L.pts[i - 1], p, t, Math.max(2, 0.5 * Math.min(t.h, t.w))));
    const onLine = (t, L) => {
      const q = along([cx(t), cy(t)], L.pts);
      if (q.r < 0.08 || q.r > 0.92) return false;
      if (q.d <= Math.max(8, 0.55 * Math.min(t.h, typH))) return true;
      return touches(t, L) && q.d <= (t.w + t.h) / 2 && t.w <= 0.6 * typW;   // 贴在短线旁的小标签
    };
    /* 紧贴无字容器左上角／左缘的文字：优先当容器标签，不当连线标注 */
    const cornerLabel = t => t.k === 'text' && t.par && isBoxK(t.par) && !t.par.text && childrenOf(t.par).some(k => k.k !== 'text') &&
      ((t.x - t.par.x <= 0.08 * t.par.w + 4 && t.y - t.par.y <= t.h + 4) || (t.x - t.par.x <= 4 && t.w <= 0.35 * t.par.w));
    const explicitEnds = new Set(lines.flatMap(L => [L.from, L.to]).filter(v => v != null).map(String));
    const pairs = [];
    for (const L of lines) {
      if (L.text) continue;
      for (const t of shapes) {
        if (t.dead || !t.text || t.text.length > 40) continue;
        if (t.k === 'text') { if (t.w > 3 * typW || cornerLabel(t)) continue; }
        else if (isBoxK(t)) {
          // 小标签框：比典型框小，且线“穿过”它（端点都不在它里面），自身无子元素
          if (t.w > 3 * typW || t.h > 1.5 * typH || childrenOf(t).length || explicitEnds.has(t.sid)) continue;
          if (inBox(L.pts[0], t, 2) || inBox(L.pts[L.pts.length - 1], t, 2)) continue;
        } else continue;
        if (!onLine(t, L)) continue;
        pairs.push([polyDist([cx(t), cy(t)], L.pts), L, t]);
      }
    }
    pairs.sort((a, b) => a[0] - b[0]);
    for (const [, L, t] of pairs) { if (L.text || t.dead) continue; L.text = t.text; absorb(t, null); }
    const isLineLabelish = t => lines.some(L => onLine(t, L) && !inBox(L.pts[0], t, 2) && !inBox(L.pts[L.pts.length - 1], t, 2));

    /* ---- 7. 容器标签：压在容器左缘／顶部条带上的独立文字框或竖排标签条 ---- */
    const isContainer = C => isBoxK(C) && !C.dead && (C.legend || childrenOf(C).some(k => k.k !== 'text'));
    const cands = [];
    for (const C of shapes) {
      if (!isContainer(C) || C.text) continue;
      for (const T of shapes) {
        if (T.dead || T === C || !T.text) continue;
        /* 标签条：在容器内左缘，或紧贴容器左外侧、与容器等高的同级竖条（常见的“层名竖条＋层框”画法） */
        const ovY = Math.min(T.y + T.h, C.y + C.h) - Math.max(T.y, C.y);
        const outStrip = isBoxK(T) && T.par === C.par && !childrenOf(T).length && Math.abs(T.x + T.w - C.x) <= Math.max(6, 0.01 * C.w) && ovY >= 0.8 * C.h && T.h > 1.6 * T.w;
        const isStrip = isBoxK(T) && (T.par === C || outStrip) && !childrenOf(T).length;
        if (!(T.k === 'text' || isStrip)) continue;
        if (T.k === 'text' && T.par && T.par !== C && T.par !== C.par) continue;   // 在别的框里
        if (cy(T) < C.y - T.h * 0.5 || cy(T) > C.y + C.h) continue;
        const leftStrip = T.x <= C.x + Math.max(0.12 * C.w, 10) && T.x + T.w >= C.x - 2 && T.w <= 0.35 * C.w && cy(T) >= C.y && (isStrip ? (T.h > 1.6 * T.w || T.vert) && T.h >= 0.4 * C.h : true);
        const topStrip = T.y <= C.y + Math.max(0.22 * C.h, 1.5 * T.h) && T.y + T.h >= C.y - 4 && cx(T) > C.x && cx(T) < C.x + C.w &&
          (isStrip ? T.w >= 0.55 * C.w && T.h <= 0.35 * C.h : (T.x - C.x <= 0.2 * C.w || Math.abs(cx(T) - cx(C)) <= 0.12 * C.w)) && T.h <= 0.5 * C.h;
        if (!leftStrip && !topStrip) continue;
        if (T.k === 'text' && isLineLabelish(T)) continue;
        // 不能落在容器的其它子框里
        if (T.k === 'text' && shapes.some(o => !o.dead && o !== C && o !== T && o.par === C && isBoxK(o) && inter(o, T) > 0.5 * area(T))) continue;
        cands.push({ C, T, a: area(C), d: (T.x - C.x) + (T.y - C.y) + (leftStrip ? 0 : 1e4) });
      }
    }
    cands.sort((p, q) => p.a - q.a || p.d - q.d);
    for (const { C, T } of cands) {
      if (C.text || T.dead) continue;
      C.text = T.text; C.px = T.px; C.labelFill = isBoxK(T) ? T.fill : null;
      /* 外侧标签条：容器向左扩到标签条 */
      if (isBoxK(T) && T.x + T.w <= C.x + 6 && T.x < C.x) { C.w += C.x - T.x; C.x = T.x; }
      absorb(T, C);
    }

    /* ---- 7b. 图例：标题含“图例”，或内部文字多为状态／链路类型名 → 织图图例（自动生成内容） ---- */
    const LEG = new Set(['图例', '已建', '在建', '现有', '新增', '规划', '本期新增', '重点建设', '延续', '本步新增／重构', '重点关注']);
    try { if (typeof LINK_KINDS !== 'undefined') for (const k of Object.values(LINK_KINDS)) LEG.add(k.name); } catch (e) { /* ignore */ }
    const descOf = C => { const o = []; const r = P => { for (const k of childrenOf(P)) { o.push(k); r(k); } }; r(C); return o; };
    for (const C of shapes) {
      if (!isContainer(C)) continue;
      const ds = descOf(C), tx = [C, ...ds].filter(k => k.text).map(k => k.text.trim());
      const hit = tx.filter(t => LEG.has(t)).length;
      const small = ds.filter(isBoxK).every(k => k.w < 0.5 * typW && k.h < 0.6 * typH || LEG.has((k.text || '').trim()));
      if ((small || hit >= 3) && (/^图\s*例$/.test((C.text || '').trim()) || (hit >= 2 && hit * 2 >= tx.length))) { C.legend = true; for (const k of ds) absorb(k, C); }
    }

    /* ---- 8. 整页外框：唯一的无字顶层框 → 去掉 ---- */
    const tops = shapes.filter(it => !it.dead && !it.par && it.k !== 'text');
    if (tops.length === 1 && isBoxK(tops[0]) && !tops[0].text && childrenOf(tops[0]).length >= 2) {
      const F = tops[0]; for (const k of childrenOf(F)) k.par = null; F.dead = true; ctx.warn(`${label}：已忽略无文字的整页外框`);
    }
    /* 不可见的无字叶子 / 细装饰条 → 丢弃 */
    for (const b of shapes) if (!b.dead && isBoxK(b) && !b.text && !b.icon && !childrenOf(b).length && (Math.min(b.w, b.h) < 4)) b.dead = true;

    /* ---- 9. 分类：层(band) / 泳道(lane) / 子容器(group) / 叶子 ---- */
    const live = shapes.filter(it => !it.dead);
    const bb = live.reduce((b, it) => ({ x0: Math.min(b.x0, it.x), y0: Math.min(b.y0, it.y), x1: Math.max(b.x1, it.x + it.w), y1: Math.max(b.y1, it.y + it.h) }), { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity });
    const W = bb.x1 - bb.x0, H = bb.y1 - bb.y0;
    const conts = live.filter(c => isContainer(c) && !c.legend);
    const stacked = arr => { const a = [...arr].sort((p, q) => p.y - q.y); for (let i = 1; i < a.length; i++) { const ov = a[i - 1].y + a[i - 1].h - a[i].y; if (ov > 0.3 * Math.min(a[i].h, a[i - 1].h)) return false; } return true; };
    for (const C of conts) C.cls = 'group';
    let bands = conts.filter(C => !C.par && C.w >= 0.6 * W);
    if (bands.length >= 2 && stacked(bands)) bands.forEach(b => b.cls = 'band');
    else if (bands.length === 1) {
      const B = bands[0], inner = conts.filter(C => C.par === B && C.w >= 0.7 * B.w);
      if (inner.length >= 2 && stacked(inner)) B.cls = 'band';
    }
    for (const B of conts.filter(C => C.cls === 'band')) {
      const wide = conts.filter(C => C.par === B && C.w >= 0.7 * B.w);
      if (wide.length && stacked(wide)) wide.forEach(l => l.cls = 'lane');
    }

    const legendBoxes = live.filter(c => c.legend);
    /* ---- 10. 生成节点 ---- */
    const kc = opts.keepColors !== false, CI = ctx.colors;
    const nodeOf = new Map();
    const nodes = [];
    const colorize = (it, n) => {
      if (!kc) return;
      const f = it.fill && !it.fillDef ? String(it.fill).toUpperCase() : null, k = it.stroke && !it.strokeDef ? String(it.stroke).toUpperCase() : null;
      const stm = CI.st.find(x => (f && x.fill === f) || (k && x.stroke === k && n.type !== 'band'));
      if (stm && !['text', 'note'].includes(n.type)) { n.status = stm.s; return; }
      if (f && !CI.def.has(f)) { if (lum(f) >= 0.45) n.fill = f; else if (!k) n.stroke = f; }
      if (k && !CI.def.has(k) && lum(k) < 0.92) n.stroke = k;
    };
    for (const it of live) {
      let o;
      const sz = it.px || 0;                                  // 0 = 未知字号，最后统一给默认
      if (it.legend) {
        o = { type: 'legend', role: 'legend', text: '' };
      } else if (isContainer(it)) {
        o = { type: it.cls, text: (it.text || '').replace(/\n+/g, it.cls === 'band' ? '' : ' '), size: 13, bold: true };
      } else if (it.k === 'pic') {
        const capH = it.capH || 0, w = Math.max(it.w, Math.min(it.capW || 0, it.w * 2.2)), x = it.capX != null && w > it.w ? cx(it) - w / 2 : it.x;
        o = { type: 'equip', icon: 'cu:' + ctx.addIcon(it.uri, it.name || (it.text || '').split('\n')[0], it.w / it.h), noBox: true, text: it.text || '', _px: sz, _max: 16, x, y: it.y, w: Math.max(32 / s, w), h: Math.max(32 / s, it.h + capH) };
      } else if (it.k === 'table') {
        o = { type: 'note', text: it.rows.map(r => r.filter(Boolean).join(' | ')).filter(Boolean).join('\n'), size: 12, align: 'left' };
      } else if (it.k === 'text') {
        o = { type: 'text', text: it.text, _px: sz, _max: 32, bold: !!it.bold, align: it.align === 'l' ? 'left' : 'center' };
      } else {
        o = { type: it.geom || 'rect', text: it.text, _px: sz, _max: 22, bold: !!it.bold };
        /* 长段文字的矩形 → 说明框 */
        if ((it.geom === 'rect' || it.geom === 'round') && !it.icon && it.text.replace(/\s/g, '').length > 40 && it.w > 2 * typW) Object.assign(o, { type: 'note', align: 'left', _max: 14 });
        if (it.icon) { o.icon = 'cu:' + it.icon; if (it.picBig && !it.text.includes('\n')) { o.type = 'equip'; } }
      }
      const n = mkNode(Object.assign({ x: it.x, y: it.y, w: it.w, h: it.h, imp: true }, o));
      if (it.k !== 'text' && it.k !== 'table') colorize(it, n);
      nodeOf.set(it, n); nodes.push(n);
    }
    const liveAnc = it => { let p = it.par; while (p && (p.dead || !nodeOf.has(p))) p = alias.get(p) || p.par; return p; };
    for (const it of live) { const p = liveAnc(it); const n = nodeOf.get(it); n.parent = p && isContainer(p) ? nodeOf.get(p).id : null; }
    const byId = id => nodes.find(m => m.id === id);
    /* 被包含于非容器的元素：父改为空（叶子不能当父） */
    for (const n of nodes) if (n.parent && !['band', 'lane', 'group'].includes(byId(n.parent)?.type)) n.parent = null;
    /* 泳道必须在层里；否则降为子容器 */
    for (const n of nodes) if (n.type === 'lane' && !(n.parent && byId(n.parent)?.type === 'band')) n.type = 'group';

    /* ---- 11. 连线：显式连接 → 端点吸附（仍在 s 坐标系） ---- */
    const CONT_T = new Set(['band', 'lane', 'group']);
    const leafNodes = nodes.filter(n => !CONT_T.has(n.type) && !['text', 'note', 'legend'].includes(n.type));
    const plain = leafNodes.filter(n => n.type !== 'equip' && n.text);
    const leafMed = plain.length >= 3 || !leafNodes.length ? median(plain.map(n => n.w)) : median(leafNodes.map(n => n.w)) * 1.4;
    const findNode = sid => {
      if (sid == null) return null;
      let it = items.find(q => q.sid === String(sid) && q.k !== 'line'); let g = 0;
      while (it && it.dead && g++ < 20) it = alias.get(it) || liveAnc(it);
      return it ? nodeOf.get(it) || null : null;
    };
    /* 端点吸附：① 落在（或贴近）叶子框上，或贴近容器边框 → 取最小者；
       ② 否则取附近边框最近的叶子（有箭头的一端半径大，无箭头端半径小）；③ 再否则取包含它的最小容器 */
    /* 终缩放系数 f（先算出来：吸附容差按最终像素计） */
    let f = leafMed ? (leafMed >= 110 && leafMed <= 210 ? 1 : 150 / leafMed) : 1;
    f = Math.max(0.2, Math.min(6, f));
    const tol = TOL / f;
    const RA = Math.max(24 / f, 0.35 * (leafMed || typW)), RN = Math.max(tol, 0.25 * (leafMed || typW));
    const edgeDist = (p, n) => { const dx = Math.max(n.x - p[0], 0, p[0] - n.x - n.w), dy = Math.max(n.y - p[1], 0, p[1] - n.y - n.h); return Math.hypot(dx, dy); };
    const nearBorder = (p, n) => inBox(p, n, tol) && Math.min(Math.abs(p[0] - n.x), Math.abs(p[0] - n.x - n.w), Math.abs(p[1] - n.y), Math.abs(p[1] - n.y - n.h)) <= tol;
    /* 压在线中段上的单行小文字（含导出时带底色、无边框的标签框）：视作连线标签，不参与端点吸附 */
    const lblCands = [];
    for (const it of live) {
      if (!nodeOf.has(it) || !it.text || /\n/.test(it.text.trim()) || it.icon || childrenOf(it).length || !(it.k === 'text' || (isBoxK(it) && !it.stroke)) || it.h > Math.max(1.2 * typH, 28 / f) || nodeOf.get(it).role) continue;
            let best = null;
      for (const L of lines) {
        const P = L.pts; if (!P || P.length < 2) continue;
        if (inBox(P[0], it, -1) || inBox(P[P.length - 1], it, -1)) continue;   // 线的端点落在文字上：文字是端点图形，不是标签
        /* 线到文字框的最近距离（沿线采样）：标签可压在线上，也可贴在线旁 */
        let d = Infinity;
        for (let i = 0; i + 1 < P.length; i++) { const A = P[i], B = P[i + 1], n = Math.max(2, Math.ceil(Math.hypot(B[0] - A[0], B[1] - A[1]) / Math.max(1, it.h / 4))); for (let k = 0; k <= n; k++) { const q = [A[0] + (B[0] - A[0]) * k / n, A[1] + (B[1] - A[1]) * k / n]; d = Math.min(d, Math.hypot(Math.max(it.x - q[0], 0, q[0] - it.x - it.w), Math.max(it.y - q[1], 0, q[1] - it.y - it.h))); } }
        if (d <= Math.max(it.h * 0.5, tol) && (!best || d < best.d)) best = { it, L, d };
      }
      if (best) lblCands.push(best);
    }
    const lblNodes = new Set(lblCands.map(c => nodeOf.get(c.it)));
    const snapC = nodes.filter(n => n.type !== 'legend' && n.type !== 'note' && n.type !== 'tblock' && !lblNodes.has(n));
    const snap = (p, R) => {
      let best = null;
      for (const n of snapC) {
        const leaf = !CONT_T.has(n.type);
        if (!(leaf ? inBox(p, n, n.type === 'text' ? 4 / f : tol) : nearBorder(p, n))) continue;
        const score = (n.type === 'text' ? 1e12 : 0) + n.w * n.h;
        if (!best || score < best.s) best = { n, s: score };
      }
      if (best) return best.n;
      for (const n of snapC) {
        if (CONT_T.has(n.type) || n.type === 'text') continue;
        const d = edgeDist(p, n); if (d <= R && (!best || d < best.s)) best = { n, s: d };
      }
      if (best) return best.n;
      for (const n of snapC) if (CONT_T.has(n.type) && inBox(p, n) && (!best || n.w * n.h < best.s)) best = { n, s: n.w * n.h };
      return best ? best.n : null;
    };
    const links = [], seen = new Set();
    let dropped = 0;
    const medLw = median(lines.map(L => L.lw || 0).filter(Boolean)) || 1;
    const KIND = (L, arrow) => {
      const d = L.dash || '';
      if (/dot/i.test(d) && /dash/i.test(d)) return 'sat'; if (/dot/i.test(d)) return 'radio'; if (/dash/i.test(d)) return 'ctrl';
      if ((L.lw || 0) >= 1.35 * medLw && lines.length > 2) return 'wired';
      return arrow ? 'data' : 'plain';
    };
    for (const L of lines) {
      if (legendBoxes.some(g => inBox(L.pts[0], g, 2) && inBox(L.pts[L.pts.length - 1], g, 2))) continue;   // 图例里的样例线
      const ea = findNode(L.from), eb = findNode(L.to);
      let a = ea || snap(L.pts[0], L.head ? RA : RN), b = eb || snap(L.pts[L.pts.length - 1], L.tail ? RA : RN);
      if (!a || !b || a === b) { dropped++; continue; }
      /* 无箭头、靠几何吸附到容器上的线：多为分隔线／装饰线 */
      if (!L.head && !L.tail && ((!ea && CONT_T.has(a.type)) || (!eb && CONT_T.has(b.type)))) { dropped++; continue; }
      const dir = L.head && L.tail ? 'both' : (L.head || L.tail ? 'one' : 'none');
      if (L.head && !L.tail) [a, b] = [b, a];
      const key = a.id + '>' + b.id; if (seen.has(key)) continue; seen.add(key);
      links.push({ id: uid(), from: a.id, to: b.id, dir, kind: KIND(L, dir !== 'none'), route: 'ortho', label: (L.text || '').replace(/\n+/g, ' '), _L: L });
    }
    /* 连线标签：收为压住它的那条线的标签 */
    {
      const used = new Set();
      for (const lk of links) {
        if (lk.label || !lk._L) continue;
        let best = null;
        for (const c of lblCands) if (!used.has(c) && c.L === lk._L && (!best || c.d < best.d)) best = c;
        if (best) { used.add(best); lk.label = best.it.text.trim(); }
      }
      for (const c of lblCands) { const n = nodeOf.get(c.it); if (!used.has(c)) continue; const i = nodes.indexOf(n); if (i >= 0) nodes.splice(i, 1); }
      for (const lk of links) delete lk._L;
    }
    if (dropped) ctx.warn(`${label}：${dropped} 条线段两端未连到两个不同图形（装饰线、分隔线或悬空箭头），已忽略`);

    /* ---- 12. 终缩放：真实叶子框中位宽度 → 约 150px；字号同比，限定在可读范围 ---- */
    for (const n of nodes) {
      for (const k of ['x', 'y', 'w', 'h']) n[k] = Math.round(n[k] * f);
      if ('_px' in n) { n.size = n._px ? Math.round(Math.max(11, Math.min(n._max, n._px * f))) : 13; delete n._px; delete n._max; }
    }

    /* 标题：顶部、字号最大的顶层文字；其下紧贴的小字 → 副标题 */
    let titleText = '';
    const topTexts = nodes.filter(n => n.type === 'text' && !n.parent);
    if (topTexts.length) {
      const y0n = Math.min(...nodes.map(n => n.y)), y1n = Math.max(...nodes.map(n => n.y + n.h));
      const medSz = median(nodes.filter(n => !CONT_T.has(n.type)).map(n => n.size || 13));
      const firstBox = Math.min(...nodes.filter(n => n.type !== 'text').map(n => n.y).concat([Infinity]));
      const cand = topTexts.filter(n => n.y + n.h / 2 <= y0n + (y1n - y0n) * 0.25).sort((a, b) => (b.size - a.size) || (a.y - b.y))[0];
      if (cand && (cand.size >= medSz * 1.15 || cand.y + cand.h <= firstBox + 4)) {
        cand.role = 'title'; cand.bold = true; cand.size = Math.max(cand.size, 20); titleText = cand.text.split('\n')[0];
        const sub = topTexts.filter(n => n !== cand && n.y >= cand.y + cand.h * 0.6 && n.y - (cand.y + cand.h) < Math.max(30, cand.h) && n.size < cand.size && Math.abs((n.x + n.w / 2) - (cand.x + cand.w / 2)) < Math.max(n.w, cand.w) / 2).sort((a, b) => a.y - b.y)[0];
        if (sub) { sub.role = 'subtitle'; sub.color = 'muted'; }
      }
    }
    return { id: 'p' + uid(), name: '', nodes, links, view: null, titleText };
  }

  function finishPages(pages, ctx) {
    if (pages.length && ctx.opts.rootId) pages[0].id = ctx.opts.rootId;
    if (!pages.length) ctx.warn('没有找到可导入的图形');
  }

  /* ---------- 入口 ---------- */
  async function fromFile(file) {
    const name = (file && file.name) || '', ext = (name.split('.').pop() || '').toLowerCase();
    if (ext === 'ppt' || ext === 'vsd') throw new Error('旧版二进制格式，请在 PowerPoint／Visio 中“另存为” .pptx／.vsdx 后再导入');
    const buf = await file.arrayBuffer();
    let r;
    if (ext === 'pptx' || ext === 'potx' || ext === 'ppsx') r = await fromPPTX(buf);
    else if (ext === 'vsdx' || ext === 'vssx' || ext === 'vstx') r = await fromVSDX(buf);
    else throw new Error('仅支持导入 .pptx／.vsdx 文件');
    r.name = name.replace(/\.[^.]+$/, '');
    return r;
  }

  window.Importer = { fromPPTX, fromVSDX, fromFile, _buildPage: buildPage };
})();
