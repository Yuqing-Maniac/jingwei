/* =========================================================================
   VsdxRaw：Visio（.vsdx）高保真读取 → 中性图元 → PowerPoint（.pptx）
   用于“格式转换 · 原样转换”：不经过织图的分层推断，逐形状还原
   位置、几何、填充、线型、箭头、图片，以及逐段文字的字体、字号、粗斜体、颜色、对齐。
   ========================================================================= */
(function () {
  'use strict';
  const NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships';
  const EMU = 914400;
  const kids = (el, n) => el ? [...el.children].filter(c => c.localName === n) : [];
  const kid = (el, n) => el ? [...el.children].find(c => c.localName === n) || null : null;
  const num = (v, d) => { const x = parseFloat(v); return isFinite(x) ? x : d; };
  const xmlEsc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '');
  const parseXML = s => new DOMParser().parseFromString(s, 'application/xml');
  async function zXML(zip, p) { const f = zip.file(p); return f ? parseXML(await f.async('string')) : null; }
  const dirOf = p => p.replace(/[^/]*$/, '');
  function normPath(base, t) { if (t.startsWith('/')) return t.slice(1); const st = (dirOf(base) + t).split('/'), out = []; for (const s of st) { if (s === '..') out.pop(); else if (s !== '.') out.push(s); } return out.join('/'); }
  async function readRels(zip, part) {
    const p = dirOf(part) + '_rels/' + part.split('/').pop() + '.rels', d = await zXML(zip, p), m = {};
    if (d) for (const r of d.getElementsByTagName('Relationship')) m[r.getAttribute('Id')] = { target: normPath(part, r.getAttribute('Target')), type: r.getAttribute('Type') || '' };
    return m;
  }
  const rId = el => el.getAttributeNS(NS_R, 'id') || el.getAttribute('r:id');
  const CJK = /[⺀-鿿豈-﫿＀-￯　-〿]/;
  const PAL = ['#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#800000', '#008000', '#000080', '#808000', '#800080', '#008080', '#C0C0C0', '#E6E6E6', '#CDCDCD', '#B3B3B3', '#9A9A9A', '#808080', '#666666', '#4D4D4D', '#333333', '#1A1A1A'];

  /* ---------------- 矩阵（仿射）：[a,b,c,d,e,f]：x' = a x + c y + e，y' = b x + d y + f ---------------- */
  const I = [1, 0, 0, 1, 0, 0];
  const mul = (m, n) => [m[0] * n[0] + m[2] * n[1], m[1] * n[0] + m[3] * n[1], m[0] * n[2] + m[2] * n[3], m[1] * n[2] + m[3] * n[3], m[0] * n[4] + m[2] * n[5] + m[4], m[1] * n[4] + m[3] * n[5] + m[5]];
  const ap = (m, x, y) => [m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]];
  const T = (x, y) => [1, 0, 0, 1, x, y];
  const R = a => [Math.cos(a), Math.sin(a), -Math.sin(a), Math.cos(a), 0, 0];
  const S = (x, y) => [x, 0, 0, y, 0, 0];

  /* ---------------- 文档级：样式表、字体名、颜色表、主题字体 ---------------- */
  function cellsOf(el) { const m = {}; if (el) for (const c of kids(el, 'Cell')) m[c.getAttribute('N')] = c; return m; }
  function secsOf(el) {
    /* { N: { IX|'_': {cells, rows:{IX:{T, cells, del}}, del} } } */
    const out = {};
    if (!el) return out;
    for (const s of kids(el, 'Section')) {
      const N = s.getAttribute('N'), ix = s.getAttribute('IX') ?? '_';
      const sec = { cells: cellsOf(s), rows: {}, del: s.getAttribute('Del') === '1' };
      let auto = 0;
      for (const r of kids(s, 'Row')) {
        const k = r.getAttribute('IX') ?? r.getAttribute('N') ?? String(auto); auto++;
        sec.rows[k] = { T: r.getAttribute('T'), cells: cellsOf(r), del: r.getAttribute('Del') === '1' };
      }
      (out[N] = out[N] || {})[ix] = sec;
    }
    return out;
  }
  function mkSheet(el) { return el ? { el, cells: cellsOf(el), secs: secsOf(el) } : null; }

  async function loadDoc(zip) {
    const D = { styles: {}, faces: {}, colors: {}, theme: { latin: 'Calibri', ea: '' }, warn: [] };
    const doc = await zXML(zip, 'visio/document.xml');
    if (doc) {
      for (const s of doc.getElementsByTagName('StyleSheet')) D.styles[s.getAttribute('ID')] = Object.assign(mkSheet(s), { L: s.getAttribute('LineStyle'), F: s.getAttribute('FillStyle'), X: s.getAttribute('TextStyle') });
      for (const f of doc.getElementsByTagName('FaceName')) D.faces[f.getAttribute('ID')] = f.getAttribute('NameU') || f.getAttribute('Name');
      for (const c of doc.getElementsByTagName('ColorEntry')) D.colors[c.getAttribute('IX')] = c.getAttribute('RGB');
    }
    const th = Object.keys(zip.files).filter(p => /^visio\/theme\/theme\d*\.xml$/.test(p)).sort()[0];
    if (th) {
      const t = await zXML(zip, th);
      const minor = t && t.getElementsByTagName('a:minorFont')[0] || (t && [...t.getElementsByTagName('*')].find(e => e.localName === 'minorFont'));
      if (minor) {
        for (const e of minor.children) {
          if (e.localName === 'latin' && e.getAttribute('typeface')) D.theme.latin = e.getAttribute('typeface');
          if (e.localName === 'ea' && e.getAttribute('typeface')) D.theme.ea = e.getAttribute('typeface');
          if (e.localName === 'font' && /^hans$/i.test(e.getAttribute('script') || '') && e.getAttribute('typeface')) D.theme.hans = e.getAttribute('typeface');
        }
      }
    }
    if (th) D.T = parseTheme(await zXML(zip, th));
    return D;
  }
  /* ---------------- 主题：配色、变体配色、填充／线条／字体样式矩阵 ---------------- */
  const els = (root, ln) => root ? [...root.getElementsByTagName('*')].filter(e => e.localName === ln) : [];
  function parseTheme(t) {
    if (!t) return null;
    const T = { clr: {}, vars: [], fills: [], lines: [], cFills: [], cLines: [], fonts: [], cFonts: [], varStyles: [] };
    const cs = els(t, 'clrScheme')[0];
    if (cs) for (const e of cs.children) { const c = e.firstElementChild; if (c && c.localName === 'srgbClr') T.clr[e.localName] = c.getAttribute('val').toUpperCase(); else if (c && c.localName === 'sysClr') T.clr[e.localName] = (c.getAttribute('lastClr') || '000000').toUpperCase(); }
    for (const v of els(t, 'variationClrScheme')) { const a = []; for (let i = 1; i <= 7; i++) { const e = [...v.children].find(x => x.localName === 'varColor' + i); const c = e && e.firstElementChild; a.push(c ? (c.getAttribute('val') || c.getAttribute('lastClr') || '').toUpperCase() : null); } T.vars.push(a); }
    const bk = els(t, 'bkgnd')[0]; if (bk && bk.firstElementChild) T.bkgnd = (bk.firstElementChild.getAttribute('val') || '').toUpperCase() || null;
    const fmt = els(t, 'fmtScheme')[0];
    const lst = (root, n) => { const l = root && [...root.children].find(x => x.localName === n); return l ? [...l.children] : []; };
    if (fmt) { T.fills = lst(fmt, 'fillStyleLst'); T.lines = lst(fmt, 'lnStyleLst'); }
    const con = els(t, 'fmtConnectorScheme')[0];
    if (con) { T.cFills = lst(con, 'fillStyleLst'); T.cLines = lst(con, 'lnStyleLst'); }
    const fsg = els(t, 'fontStylesGroup')[0];
    if (fsg) { T.fonts = lst(fsg, 'fontStyles'); T.cFonts = lst(fsg, 'connectorFontStyles'); }
    for (const v of els(t, 'variationStyleScheme')) T.varStyles.push([...v.children].filter(x => x.localName === 'varStyle').map(x => ({ fill: +x.getAttribute('fillIdx'), line: +x.getAttribute('lineIdx'), font: +x.getAttribute('fontIdx') })));
    return T;
  }
  const hex2rgb = h => [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  const rgb2hex = c => c.map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('').toUpperCase();
  function rgb2hsl([r, g, b]) { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2; let h = 0, s = 0; if (mx !== mn) { const d = mx - mn; s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn); h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; } return [h, s, l]; }
  function hsl2rgb([h, s, l]) { if (!s) return [l * 255, l * 255, l * 255]; const q = l < 0.5 ? l * (1 + s) : l + s - l * s, p = 2 * l - q; const f = t => { if (t < 0) t += 1; if (t > 1) t -= 1; return t < 1 / 6 ? p + (q - p) * 6 * t : t < 1 / 2 ? q : t < 2 / 3 ? p + (q - p) * (2 / 3 - t) * 6 : p; }; return [f(h + 1 / 3) * 255, f(h) * 255, f(h - 1 / 3) * 255]; }
  /* DrawingML 颜色元素（含 phClr 占位与修饰）→ {c, a} */
  function dmlColor(el, T, ph) {
    if (!el) return null;
    let c = null;
    if (el.localName === 'srgbClr') c = el.getAttribute('val');
    else if (el.localName === 'sysClr') c = el.getAttribute('lastClr') || '000000';
    else if (el.localName === 'schemeClr') { const v = el.getAttribute('val'); c = v === 'phClr' ? ph : T.clr[{ tx1: 'dk1', bg1: 'lt1', tx2: 'dk2', bg2: 'lt2' }[v] || v]; }
    else if (el.localName === 'prstClr') c = { black: '000000', white: 'FFFFFF' }[el.getAttribute('val')] || '808080';
    if (!c) return null;
    let rgb = hex2rgb(c.toUpperCase()), a = 1;
    for (const m of el.children) {
      const v = (+m.getAttribute('val')) / 100000;
      if (m.localName === 'tint') rgb = rgb.map(x => x * v + 255 * (1 - v));
      else if (m.localName === 'shade') rgb = rgb.map(x => x * v);
      else if (m.localName === 'alpha') a = v;
      else if (/^(lumMod|lumOff|satMod)$/.test(m.localName)) { const h = rgb2hsl(rgb); if (m.localName === 'lumMod') h[2] *= v; else if (m.localName === 'lumOff') h[2] += v; else h[1] *= v; h[1] = Math.min(1, Math.max(0, h[1])); h[2] = Math.min(1, Math.max(0, h[2])); rgb = hsl2rgb(h); }
    }
    return { c: rgb2hex(rgb), a };
  }
  function themeColor(T, v, varIdx) {
    /* MS-VSDX QuickStyle*Color：0 dk1，1 lt1，2～7 accent1～6，8 背景；100～106（200～206）变体配色 1～7 */
    if (!T || v == null || !isFinite(v)) return null;
    if (v < 100) return [T.clr.dk1, T.clr.lt1, T.clr.accent1, T.clr.accent2, T.clr.accent3, T.clr.accent4, T.clr.accent5, T.clr.accent6, T.bkgnd || T.clr.lt1][v] || null;
    const k = v % 100; if (k > 6) return null;
    const vs = T.vars[varIdx] || T.vars[0];
    return vs ? vs[k] || null : null;
  }

  /* ---------------- 单元格继承：形状 → 主控形状 → 样式链 ---------------- */
  const LINE_C = new Set(['LineWeight', 'LineColor', 'LinePattern', 'Rounding', 'EndArrowSize', 'BeginArrow', 'EndArrow', 'LineCap', 'BeginArrowSize', 'LineColorTrans', 'CompoundType']);
  const FILL_C = new Set(['FillForegnd', 'FillBkgnd', 'FillPattern', 'ShdwForegnd', 'ShdwBkgnd', 'ShdwPattern', 'FillForegndTrans', 'FillBkgndTrans', 'ShdwForegndTrans', 'ShdwBkgndTrans', 'ShapeShdwType', 'ShapeShdwOffsetX', 'ShapeShdwOffsetY', 'ShapeShdwObliqueAngle', 'ShapeShdwScaleFactor', 'ShapeShdwBlur', 'ShapeShdwShow', 'FillGradientEnabled', 'FillGradientDir', 'FillGradientAngle', 'LineGradientEnabled', 'RotateGradientWithShape']);
  const TEXT_C = new Set(['LeftMargin', 'RightMargin', 'TopMargin', 'BottomMargin', 'VerticalAlign', 'TextBkgnd', 'DefaultTabStop', 'TextDirection', 'TextBkgndTrans']);
  const kindOf = N => /^QuickStyle(Fill|Shadow)/.test(N) ? 'F' : /^QuickStyleFont/.test(N) ? 'X' : /^QuickStyle/.test(N) ? 'L' : LINE_C.has(N) ? 'L' : FILL_C.has(N) ? 'F' : TEXT_C.has(N) ? 'X' : null;
  const SEC_KIND = { Character: 'X', Paragraph: 'X', Tabs: 'X', FillGradient: 'F', LineGradient: 'L' };

  function styleChain(D, id) { const out = [], seen = new Set(); while (id != null && D.styles[id] && !seen.has(id)) { seen.add(id); out.push(D.styles[id]); id = null; } return out; }
  /* 样式本身也有父样式（按类别各自继承） */
  function styleWalk(D, id, k, fn) {
    const seen = new Set();
    while (id != null && D.styles[id] && !seen.has(id)) { seen.add(id); const s = D.styles[id]; const r = fn(s); if (r != null) return r; id = s[k]; }
    return null;
  }
  /* sh = { own: sheet, ms: [masterSheets...] } */
  function chainFor(sh, D) { return sh; }
  function cellV(sh, D, N) {
    const k = kindOf(N);
    const own = sh.own.cells[N]; if (own) return own.getAttribute('V');
    const kAttr = k ? { L: 'LineStyle', F: 'FillStyle', X: 'TextStyle' }[k] : null;
    const ownStyle = kAttr ? sh.own.el.getAttribute(kAttr) : null;
    const msStyle = kAttr && sh.ms ? sh.ms.el.getAttribute(kAttr) : null;
    /* 实例上显式套用了与主控不同的样式：样式优先于主控 */
    if (k && ownStyle != null && ownStyle !== msStyle) { const r = styleWalk(D, ownStyle, k, s => s.cells[N] ? s.cells[N].getAttribute('V') : null); if (r != null) return r; }
    if (sh.ms) { const c = sh.ms.cells[N]; if (c) return c.getAttribute('V'); }
    if (k) { const sid = ownStyle ?? msStyle; const r = styleWalk(D, sid, k, s => s.cells[N] ? s.cells[N].getAttribute('V') : null); if (r != null) return r; }
    return null;
  }
  const cellN = (sh, D, N, d) => num(cellV(sh, D, N), d);
  /* 段内行单元格：Character/Paragraph 行 IX */
  function rowV(sh, D, secN, ix, N, noRow0) {
    /* 行单元格：实例同号行 → 主控同号行 → 样式（样式只有第 0 行） */
    const k = SEC_KIND[secN];
    const get = (sheet, i) => { const s = sheet && sheet.secs[secN]; const sec = s && (s._ || s['0'] || Object.values(s)[0]); const r = sec && sec.rows[i]; const c = r && r.cells[N]; return c ? c.getAttribute('V') : null; };
    let v = get(sh.own, ix); if (v != null) return v;
    const kAttr = k ? { L: 'LineStyle', F: 'FillStyle', X: 'TextStyle' }[k] : null;
    const ownStyle = kAttr ? sh.own.el.getAttribute(kAttr) : null, msStyle = kAttr && sh.ms ? sh.ms.el.getAttribute(kAttr) : null;
    const sIx = noRow0 ? ix : '0';
    if (k && ownStyle != null && ownStyle !== msStyle) { v = styleWalk(D, ownStyle, k, s => get(s, sIx)); if (v != null) return v; }
    v = get(sh.ms, ix); if (v != null) return v;
    if (k) { v = styleWalk(D, ownStyle ?? msStyle, k, s => get(s, sIx)); if (v != null) return v; }
    return null;
  }
  function rowsCount(sh, secN) {
    let n = 0;
    for (const sheet of [sh.own, sh.ms]) { const s = sheet && sheet.secs[secN]; const sec = s && (s._ || s['0'] || Object.values(s)[0]); if (sec) n = Math.max(n, ...Object.keys(sec.rows).map(k => +k + 1).filter(isFinite), 0); }
    return n;
  }

  function color(D, v) {
    if (v == null || v === '' || v === 'Themed') return null;
    if (/^#[0-9a-f]{6}$/i.test(v)) return v.slice(1).toUpperCase();
    if (/^\d+$/.test(v)) { const c = D.colors[v] || PAL[+v]; return c ? c.replace('#', '').toUpperCase() : null; }
    const m = /RGB\((\d+),\s*(\d+),\s*(\d+)\)/i.exec(v); if (m) return [m[1], m[2], m[3]].map(x => (+x).toString(16).padStart(2, '0')).join('').toUpperCase();
    return null;
  }
  function fontName(D, v, fallback) {
    if (v == null || v === '' || v === 'Themed') return fallback;
    if (/^\d+$/.test(v)) return D.faces[v] || fallback;
    return v;
  }

  /* ---------------- 几何：Visio 行 → 路径（局部英寸，y 向上） ---------------- */
  /* 路径段：['M',x,y] ['L',x,y] ['C',x1,y1,x2,y2,x,y] ['Z'] */
  function arcBeziers(cx, cy, r, a0, sweep) {
    const out = [], n = Math.max(1, Math.ceil(Math.abs(sweep) / (Math.PI / 2))), d = sweep / n, k = 4 / 3 * Math.tan(d / 4);
    let a = a0;
    for (let i = 0; i < n; i++) {
      const c0 = Math.cos(a), s0 = Math.sin(a), c1 = Math.cos(a + d), s1 = Math.sin(a + d);
      out.push(['C', cx + r * (c0 - k * s0), cy + r * (s0 + k * c0), cx + r * (c1 + k * s1), cy + r * (s1 - k * c1), cx + r * c1, cy + r * s1]);
      a += d;
    }
    return out;
  }
  /* 过三点的圆弧（起点 p0、途经 pm、终点 p1） */
  function arc3(p0, pm, p1) {
    const [x1, y1] = p0, [x2, y2] = pm, [x3, y3] = p1;
    const dd = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2));
    if (Math.abs(dd) < 1e-12) return [['L', x3, y3]];
    const ux = ((x1 * x1 + y1 * y1) * (y2 - y3) + (x2 * x2 + y2 * y2) * (y3 - y1) + (x3 * x3 + y3 * y3) * (y1 - y2)) / dd;
    const uy = ((x1 * x1 + y1 * y1) * (x3 - x2) + (x2 * x2 + y2 * y2) * (x1 - x3) + (x3 * x3 + y3 * y3) * (x2 - x1)) / dd;
    const r = Math.hypot(x1 - ux, y1 - uy);
    const a1 = Math.atan2(y1 - uy, x1 - ux), am = Math.atan2(y2 - uy, x2 - ux), a3 = Math.atan2(y3 - uy, x3 - ux);
    const norm = a => { while (a < 0) a += 2 * Math.PI; while (a >= 2 * Math.PI) a -= 2 * Math.PI; return a; };
    const ccwM = norm(am - a1), ccw3 = norm(a3 - a1);
    const sweep = ccwM <= ccw3 ? ccw3 : ccw3 - 2 * Math.PI;
    return arcBeziers(ux, uy, r, a1, sweep);
  }
  /* 椭圆弧：先旋转、压缩成圆，求三点圆弧，再变换回去 */
  function ellArc(p0, pm, p1, ang, ratio) {
    if (!(ratio > 0)) ratio = 1;
    const fwd = mul(S(1 / ratio, 1), R(-ang)), inv = mul(R(ang), S(ratio, 1));
    const segs = arc3(ap(fwd, ...p0), ap(fwd, ...pm), ap(fwd, ...p1));
    return segs.map(s => s[0] === 'C' ? ['C', ...ap(inv, s[1], s[2]), ...ap(inv, s[3], s[4]), ...ap(inv, s[5], s[6])] : ['L', ...ap(inv, s[1], s[2])]);
  }
  function parseFn(str, name) {
    const m = new RegExp(name + '\\s*\\(([^)]*)\\)', 'i').exec(str || ''); if (!m) return null;
    return m[1].split(',').map(x => parseFloat(x));
  }
  function nurbs(ctrl, knots, weights, degree, samples) {
    /* de Boor：有理 B 样条采样 */
    const n = ctrl.length - 1, p = degree, out = [];
    const U = knots; const t0 = U[p], t1 = U[n + 1];
    if (!(t1 > t0)) return ctrl.slice(1);
    for (let s = 1; s <= samples; s++) {
      let t = t0 + (t1 - t0) * s / samples; if (s === samples) t = t1 - 1e-9;
      let k = p; while (k < n && !(t >= U[k] && t < U[k + 1])) k++;
      const d = []; for (let j = 0; j <= p; j++) { const i = k - p + j; const w = weights[i] || 1; d.push([ctrl[i][0] * w, ctrl[i][1] * w, w]); }
      for (let r = 1; r <= p; r++) for (let j = p; j >= r; j--) {
        const i = k - p + j, den = U[i + p - r + 1] - U[i]; const a = den ? (t - U[i]) / den : 0;
        d[j] = [(1 - a) * d[j - 1][0] + a * d[j][0], (1 - a) * d[j - 1][1] + a * d[j][1], (1 - a) * d[j - 1][2] + a * d[j][2]];
      }
      out.push([d[p][0] / d[p][2], d[p][1] / d[p][2]]);
    }
    return out;
  }
  /* 合并主控与实例的 Geometry 段 */
  function geomSections(sh) {
    const own = sh.own.secs.Geometry || {}, ms = (sh.ms && sh.ms.secs.Geometry) || {};
    const ixs = [...new Set([...Object.keys(ms), ...Object.keys(own)])].sort((a, b) => (+a) - (+b));
    const out = [];
    for (const ix of ixs) {
      const o = own[ix], m = ms[ix];
      if (o && o.del) continue;
      const cell = N => (o && o.cells[N] ? o.cells[N].getAttribute('V') : m && m.cells[N] ? m.cells[N].getAttribute('V') : null);
      const rk = [...new Set([...Object.keys((m && m.rows) || {}), ...Object.keys((o && o.rows) || {})])].sort((a, b) => (+a) - (+b));
      const rows = [];
      for (const k of rk) {
        const ro = o && o.rows[k], rm = m && m.rows[k];
        if (ro && ro.del) continue;
        const Tt = (ro && ro.T) || (rm && rm.T); if (!Tt) continue;
        const v = N => { const c = (ro && ro.cells[N]) || (rm && rm.cells[N]); return c ? c.getAttribute('V') : null; };
        const f = N => { const c = (ro && ro.cells[N]) || (rm && rm.cells[N]); return c ? (c.getAttribute('F') || c.getAttribute('V')) : null; };
        rows.push({ T: Tt, v, f });
      }
      out.push({ noFill: cell('NoFill') === '1', noLine: cell('NoLine') === '1', noShow: cell('NoShow') === '1', rows });
    }
    return out;
  }
  function buildPaths(secs, w, h) {
    const paths = [];
    for (const sec of secs) {
      if (sec.noShow) continue;
      const segs = []; let cur = null, start = null;
      const P = (x, y) => [x, y];
      for (const r of sec.rows) {
        const Tt = r.T, X = num(r.v('X'), 0), Y = num(r.v('Y'), 0), A = num(r.v('A'), 0), B = num(r.v('B'), 0), C = num(r.v('C'), 0), Dd = num(r.v('D'), 0);
        const rel = /^Rel/.test(Tt);
        const px = rel ? X * w : X, py = rel ? Y * h : Y;
        switch (Tt) {
          case 'MoveTo': case 'RelMoveTo': segs.push(['M', px, py]); cur = start = P(px, py); break;
          case 'LineTo': case 'RelLineTo': if (!cur) { segs.push(['M', px, py]); start = P(px, py); } else segs.push(['L', px, py]); cur = P(px, py); break;
          case 'ArcTo': {
            if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); break; }
            const dx = px - cur[0], dy = py - cur[1], len = Math.hypot(dx, dy);
            if (Math.abs(A) < 1e-9 || len < 1e-9) segs.push(['L', px, py]);
            else { const mx = (cur[0] + px) / 2 + A * dy / len, my = (cur[1] + py) / 2 - A * dx / len; segs.push(...arc3(cur, [mx, my], [px, py])); }
            cur = P(px, py); break;
          }
          case 'EllipticalArcTo': case 'RelEllipticalArcTo': {
            const ax = rel ? A * w : A, by = rel ? B * h : B;
            if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); break; }
            segs.push(...ellArc(cur, [ax, by], [px, py], C, Dd)); cur = P(px, py); break;
          }
          case 'RelCubBezTo': { if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); break; } segs.push(['C', A * w, B * h, C * w, Dd * h, px, py]); cur = P(px, py); break; }
          case 'RelQuadBezTo': { if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); break; } const qx = A * w, qy = B * h; segs.push(['C', cur[0] + 2 / 3 * (qx - cur[0]), cur[1] + 2 / 3 * (qy - cur[1]), px + 2 / 3 * (qx - px), py + 2 / 3 * (qy - py), px, py]); cur = P(px, py); break; }
          case 'Ellipse': {
            /* 中心 (X,Y)，(A,B) 一轴端点，(C,D) 另一轴端点 */
            const ux = A - X, uy = B - Y, vx = C - X, vy = Dd - Y, k = 0.5522847498;
            const pt = (c, s) => [X + c * ux + s * vx, Y + c * uy + s * vy];
            const p0 = pt(1, 0); segs.push(['M', ...p0]);
            const q = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 0]];
            for (let i = 0; i < 4; i++) { const [c0, s0] = q[i], [c1, s1] = q[i + 1]; segs.push(['C', ...pt(c0 - k * s0, s0 + k * c0), ...pt(c1 + k * s1, s1 - k * c1), ...pt(c1, s1)]); }
            segs.push(['Z']); cur = null; start = null; break;
          }
          case 'PolylineTo': {
            const a = parseFn(r.f('A'), 'POLYLINE');
            if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); break; }
            if (a && a.length >= 2) { const xr = a[0] === 0, yr = a[1] === 0; for (let i = 2; i + 1 < a.length; i += 2) segs.push(['L', xr ? a[i] * w : a[i], yr ? a[i + 1] * h : a[i + 1]]); }
            segs.push(['L', px, py]); cur = P(px, py); break;
          }
          case 'NURBSTo': {
            const e = parseFn(r.f('E'), 'NURBS');
            if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); break; }
            if (e && e.length >= 4) {
              const knotLast = e[0], deg = Math.max(1, Math.round(e[1])), xr = e[2] === 0, yr = e[3] === 0;
              const ctrl = [cur], knots = [], wts = [Dd || 1];
              for (let i = 4; i + 3 < e.length; i += 4) { ctrl.push([xr ? e[i] * w : e[i], yr ? e[i + 1] * h : e[i + 1]]); knots.push(e[i + 2]); wts.push(e[i + 3] || 1); }
              ctrl.push([px, py]); wts.push(B || 1);
              /* 结点向量（同 libvisio）：[C, 各控制点结点…, A, knotLast]，不足补末值，保证非降 */
              const U = [C, ...knots, A, knotLast];
              for (let i = 1; i < U.length; i++) if (U[i] < U[i - 1]) U[i] = U[i - 1];
              while (U.length < ctrl.length + deg + 1) U.push(U[U.length - 1]);
              const pts = nurbs(ctrl, U.slice(0, ctrl.length + deg + 1), wts, deg, Math.max(16, ctrl.length * 8));
              for (const q of pts) segs.push(['L', q[0], q[1]]);
            }
            segs.push(['L', px, py]); cur = P(px, py); break;
          }
          case 'SplineStart': case 'SplineKnot': if (!cur) { segs.push(['M', px, py]); cur = start = P(px, py); } else { segs.push(['L', px, py]); cur = P(px, py); } break;
          default: break;
        }
      }
      if (!segs.length) continue;
      /* 拆分子路径、判断闭合 */
      let sub = null; const subs = [];
      for (const s of segs) { if (s[0] === 'M') { sub = [s]; subs.push(sub); } else if (sub) sub.push(s); }
      for (const sp of subs) {
        if (sp.length < 2) continue;
        const a = sp[0], z = sp[sp.length - 1];
        const ex = z[0] === 'Z' ? a : [z[0], z[z.length - 2], z[z.length - 1]];
        const closed = z[0] === 'Z' || Math.hypot(a[1] - ex[1], a[2] - ex[2]) < 1e-6;
        paths.push({ segs: sp.filter(s => s[0] !== 'Z'), closed, noFill: sec.noFill || !closed, noLine: sec.noLine });
      }
    }
    return paths;
  }
  /* 折线圆角（Rounding）：仅对纯直线段的子路径 */
  function roundCorners(p, r) {
    if (!(r > 0) || p.segs.some(s => s[0] === 'C')) return p;
    let pts = p.segs.map(s => [s[1], s[2]]);
    if (p.closed && Math.hypot(pts[0][0] - pts[pts.length - 1][0], pts[0][1] - pts[pts.length - 1][1]) < 1e-6) pts = pts.slice(0, -1);
    const n = pts.length; if (n < 3 && p.closed || n < 3) return p;
    const out = [];
    const corner = (prev, c, next) => {
      const l1 = Math.hypot(c[0] - prev[0], c[1] - prev[1]), l2 = Math.hypot(next[0] - c[0], next[1] - c[1]);
      const rr = Math.min(r, l1 / 2, l2 / 2); if (rr < 1e-6) return [['L', ...c]];
      const a = [c[0] + (prev[0] - c[0]) * rr / l1, c[1] + (prev[1] - c[1]) * rr / l1], b = [c[0] + (next[0] - c[0]) * rr / l2, c[1] + (next[1] - c[1]) * rr / l2];
      const k = 0.5523;
      return [['L', ...a], ['C', a[0] + (c[0] - a[0]) * k, a[1] + (c[1] - a[1]) * k, b[0] + (c[0] - b[0]) * k, b[1] + (c[1] - b[1]) * k, ...b]];
    };
    if (p.closed) {
      const c0 = corner(pts[n - 1], pts[0], pts[1]);
      out.push(['M', c0[c0.length - 1][c0[c0.length - 1].length - 2], c0[c0.length - 1][c0[c0.length - 1].length - 1]]);
      for (let i = 1; i < n; i++) out.push(...corner(pts[i - 1], pts[i], pts[(i + 1) % n]));
      out.push(...c0);
    } else {
      out.push(['M', ...pts[0]]);
      for (let i = 1; i < n - 1; i++) out.push(...corner(pts[i - 1], pts[i], pts[i + 1]));
      out.push(['L', ...pts[n - 1]]);
    }
    return Object.assign({}, p, { segs: out });
  }

  /* ---------------- 文字 ---------------- */
  function textRuns(sh) {
    /* 返回 [{t, cp, pp}]（cp/pp 为 Character/Paragraph 行号） */
    const tEl = kid(sh.own.el, 'Text') || (sh.ms && !kid(sh.own.el, 'Text') ? kid(sh.ms.el, 'Text') : null);
    if (!tEl) return null;
    const out = []; let cp = '0', pp = '0';
    const rec = n => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3 || c.nodeType === 4) { if (c.nodeValue) out.push({ t: c.nodeValue, cp, pp }); }
        else if (c.nodeType === 1) {
          if (c.localName === 'cp') cp = c.getAttribute('IX') || '0';
          else if (c.localName === 'pp') pp = c.getAttribute('IX') || '0';
          else if (c.localName === 'tp') { }
          else rec(c);
        }
      }
    };
    rec(tEl);
    return out;
  }

  /* ---------------- 页面遍历 ---------------- */
  const ARROW = t => { t = +t || 0; if (!t) return null; if ([1, 2, 9].includes(t)) return 'arrow'; if ([10, 20, 23, 24, 40, 41].includes(t)) return 'oval'; if ([11, 21, 22, 42].includes(t)) return 'diamond'; if ([6, 7, 8, 14, 15].includes(t)) return 'stealth'; return 'triangle'; };
  const DASH = p => ({ 2: 'dash', 3: 'sysDot', 4: 'dashDot', 5: 'lgDashDotDot', 6: 'dashDot', 7: 'lgDash', 8: 'lgDashDot', 9: 'lgDashDotDot', 10: 'sysDot', 11: 'sysDash', 12: 'dash', 13: 'dashDot', 14: 'lgDash', 15: 'lgDashDot', 16: 'lgDash' }[p] || (p > 16 ? 'sysDash' : null));

  async function parse(buf, opts) {
    opts = opts || {};
    const zip = await JSZip.loadAsync(buf), D = await loadDoc(zip);
    const pagesPart = 'visio/pages/pages.xml', pd = await zXML(zip, pagesPart);
    if (!pd) throw new Error('不是有效的 .vsdx 文件');
    const prels = await readRels(zip, pagesPart);
    /* 主控 */
    const masters = {};
    const md = await zXML(zip, 'visio/masters/masters.xml');
    if (md) {
      const mrels = await readRels(zip, 'visio/masters/masters.xml');
      for (const m of md.documentElement.children) {
        if (m.localName !== 'Master') continue;
        const rel = kid(m, 'Rel'), tgt = rel ? mrels[rId(rel)]?.target : null;
        const mx = tgt ? await zXML(zip, tgt) : null, shapes = {}; let top = null;
        if (mx) { const shs = kid(mx.documentElement, 'Shapes'); top = shs ? kid(shs, 'Shape') : null; for (const s of mx.getElementsByTagName('Shape')) shapes[s.getAttribute('ID')] = s; }
        masters[m.getAttribute('ID')] = { shapes, top, part: tgt, rels: tgt ? await readRels(zip, tgt) : {} };
      }
    }
    const sheetCache = new Map();
    const sheet = el => { if (!el) return null; if (!sheetCache.has(el)) sheetCache.set(el, mkSheet(el)); return sheetCache.get(el); };
    const mediaCache = new Map();
    async function media(target) {
      if (!target) return null;
      if (mediaCache.has(target)) return mediaCache.get(target);
      const f = zip.file(target); let r = null;
      if (f) { const ext = (target.split('.').pop() || '').toLowerCase(); r = { ext: ext === 'jpeg' ? 'jpg' : ext === 'tif' ? 'tiff' : ext, data: await f.async('uint8array') }; }
      mediaCache.set(target, r); return r;
    }

    /* 页面元素与背景页 */
    const pageEls = [...pd.documentElement.children].filter(e => e.localName === 'Page');
    const byId = {}; for (const p of pageEls) byId[p.getAttribute('ID')] = p;
    async function pageItems(pg, ps) {
      const rel = kid(pg, 'Rel'), part = rel ? prels[rId(rel)]?.target : null;
      const d = part ? await zXML(zip, part) : null; if (!d) return [];
      const rels = await readRels(zip, part);
      const psh = mkSheet(kid(pg, 'PageSheet'));
      const PH = num(psh.cells.PageHeight?.getAttribute('V'), 8.5);
      /* 图层可见性 */
      const layers = {}; const L = psh.secs.Layer && (psh.secs.Layer._ || Object.values(psh.secs.Layer)[0]);
      if (L) for (const [ix, r] of Object.entries(L.rows)) layers[ix] = r.cells.Visible ? r.cells.Visible.getAttribute('V') !== '0' : true;
      const toSlide = [ps, 0, 0, -ps, 0, PH * ps];      // 页面英寸（y 向上）→ 幻灯片英寸（y 向下）
      /* 主题解析（Visio 2013+ 的 THEMEVAL／Themed 单元格） */
      const TT = D.T, varIdx = num(psh.cells.VariationColorIndex?.getAttribute('V'), 0), varSty = num(psh.cells.VariationStyleIndex?.getAttribute('V'), 0);
      const qsEntry = (list, m, key) => { if (!TT || !list || !isFinite(m) || m <= 0) return null; let ix = m; if (m >= 100) { const vs = (TT.varStyles[varSty] || TT.varStyles[0] || [])[m - 100]; ix = vs ? vs[key] : 0; } return list[ix - 1] || null; };
      const fc = e => e && [...e.children].find(x => /Clr$/.test(x.localName));
      function thFill(sh, oneD) {
        if (!TT) return null;
        const base = themeColor(TT, cellN(sh, D, 'QuickStyleFillColor', NaN), varIdx);
        const e = qsEntry(oneD && TT.cFills.length ? TT.cFills : TT.fills, cellN(sh, D, 'QuickStyleFillMatrix', NaN), 'fill');
        if (!e) return base ? { c: base, a: 1 } : null;
        if (e.localName === 'noFill') return 'none';
        if (e.localName === 'gradFill') {
          const stops = els(e, 'gs').map(g => { const c = dmlColor(fc(g), TT, base); return c ? { c: c.c, a: c.a, pos: (+g.getAttribute('pos')) / 100000 } : null; }).filter(Boolean);
          const lin = els(e, 'lin')[0];
          if (stops.length >= 2) return { grad: stops, ang: -((+(lin && lin.getAttribute('ang')) || 0) / 60000) * Math.PI / 180, dir: 0 };
        }
        const c = dmlColor(fc(e), TT, base); return c || (base ? { c: base, a: 1 } : null);
      }
      function thLine(sh, oneD) {
        if (!TT) return null;
        const base = themeColor(TT, cellN(sh, D, 'QuickStyleLineColor', NaN), varIdx);
        const e = qsEntry(oneD && TT.cLines.length ? TT.cLines : TT.lines, cellN(sh, D, 'QuickStyleLineMatrix', NaN), 'line');
        if (!e) return base ? { c: base, a: 1 } : null;
        const sf = [...e.children].find(x => /Fill$/.test(x.localName));
        if (sf && sf.localName === 'noFill') return 'none';
        const c = sf ? dmlColor(fc(sf), TT, base) : null, w = +e.getAttribute('w');
        return Object.assign(c || (base ? { c: base, a: 1 } : {}), w ? { w: w / 12700 } : {});
      }
      function thFont(sh, oneD) {
        if (!TT) return null;
        const base = themeColor(TT, cellN(sh, D, 'QuickStyleFontColor', NaN), varIdx);
        const e = qsEntry(oneD && TT.cFonts.length ? TT.cFonts : TT.fonts, cellN(sh, D, 'QuickStyleFontMatrix', NaN), 'font');
        const col = e && els(e, 'color')[0];
        const c = col ? dmlColor(fc(col), TT, base) : null;
        return c || (base ? { c: base, a: 1 } : null);
      }
      const items = [];
      const shs = kid(d.documentElement, 'Shapes');
      if (shs) await walk(shs, toSlide, null, items, rels, 0);
      return items;

      async function walk(container, parentM, inhMaster, out, relsMap, depth) {
        for (const el of kids(container, 'Shape')) {
          const mId = el.getAttribute('Master') || inhMaster, M = mId ? masters[mId] : null;
          const msEl = M ? (el.getAttribute('MasterShape') ? M.shapes[el.getAttribute('MasterShape')] : (el.getAttribute('Master') ? M.top : null)) : null;
          const sh = { own: sheet(el), ms: sheet(msEl) };
          const type = el.getAttribute('Type') || (msEl && msEl.getAttribute('Type')) || 'Shape';
          if (type === 'Guide') continue;
          /* 图层隐藏 */
          const lm = cellV(sh, D, 'LayerMember');
          if (lm && Object.keys(layers).length) { const ls = lm.split(';').filter(Boolean); if (ls.length && ls.every(x => layers[x] === false)) continue; }
          const w = cellN(sh, D, 'Width', 0), h = cellN(sh, D, 'Height', 0);
          const pinX = cellN(sh, D, 'PinX', 0), pinY = cellN(sh, D, 'PinY', 0);
          const lpx = cellN(sh, D, 'LocPinX', w / 2), lpy = cellN(sh, D, 'LocPinY', h / 2);
          const ang = cellN(sh, D, 'Angle', 0), fx = cellV(sh, D, 'FlipX') === '1', fy = cellV(sh, D, 'FlipY') === '1';
          const local = mul(mul(mul(T(pinX, pinY), R(ang)), S(fx ? -1 : 1, fy ? -1 : 1)), T(-lpx, -lpy));
          const Mx = mul(parentM, local);
          const name = el.getAttribute('NameU') || el.getAttribute('Name') || (msEl && (msEl.getAttribute('NameU') || msEl.getAttribute('Name'))) || '';
          const it = { id: el.getAttribute('ID'), name, M: Mx, w, h, paths: [], text: null, img: null, kids: null, oneD: cellV(sh, D, 'BeginX') != null && cellV(sh, D, 'EndX') != null };

          /* ---- 几何与样式 ---- */
          const secs = geomSections(sh);
          let paths = buildPaths(secs, w, h);
          const rounding = cellN(sh, D, 'Rounding', 0);
          if (rounding > 0) paths = paths.map(p => roundCorners(p, rounding));
          it.paths = paths;
          it.isEllipse = secs.length === 1 && secs[0].rows.length === 1 && secs[0].rows[0].T === 'Ellipse' && Math.abs(num(secs[0].rows[0].v('X')) - w / 2) < 1e-4 && Math.abs(num(secs[0].rows[0].v('Y')) - h / 2) < 1e-4 && Math.abs(num(secs[0].rows[0].v('B')) - h / 2) < 1e-4 && Math.abs(num(secs[0].rows[0].v('C')) - w / 2) < 1e-4;
          it.isRect = paths.length === 1 && paths[0].closed && !rounding && isRectPath(paths[0], w, h);
          it.round = rounding > 0 && paths.length === 1 && paths[0].closed && isRectPath(buildPaths(secs, w, h)[0] || { segs: [] }, w, h) ? rounding : 0;
          /* 填充 */
          const fgV = cellV(sh, D, 'FillForegnd'), fpV = cellV(sh, D, 'FillPattern');
          const thf = (fgV === 'Themed' || fpV === 'Themed') ? thFill(sh, it.oneD) : null;
          const fp = fpV === 'Themed' ? (thf === 'none' ? 0 : 1) : num(fpV, 1);
          const fg = color(D, fgV) || (thf && thf !== 'none' && thf.c) || (thf && thf.grad && thf.grad[0].c) || 'FFFFFF', bg = color(D, cellV(sh, D, 'FillBkgnd')) || fg;
          const ft = cellN(sh, D, 'FillForegndTrans', 0);
          if (fp === 0) it.fill = null;
          else if (cellV(sh, D, 'FillGradientEnabled') === '1') {
            const stops = [];
            const nOwn = Math.max(...[sh.own, sh.ms].map(sht => { const g = sht && sht.secs.FillGradient; const sec = g && Object.values(g)[0]; return sec ? Object.keys(sec.rows).length : 0; }));
            const nRows = nOwn || (styleWalk(D, el.getAttribute('FillStyle') ?? (msEl && msEl.getAttribute('FillStyle')), 'F', st => { const g = st.secs.FillGradient; const sec = g && Object.values(g)[0]; return sec ? Object.keys(sec.rows).length : null; }) || 0);
            for (let ix = 0; ix < nRows; ix++) {
              const gv = N => rowV(sh, D, 'FillGradient', String(ix), N, true);
              const cv0 = gv('GradientStopColor'); let c = color(D, cv0);
              if (!c && cv0 === 'Themed') { const t2 = thFill(sh, it.oneD); c = t2 && t2 !== 'none' ? (t2.c || (t2.grad && t2.grad[Math.min(ix, t2.grad.length - 1)].c)) : null; }
              if (c) stops.push({ c, a: 1 - num(gv('GradientStopColorTrans'), 0), pos: num(gv('GradientStopPosition'), ix / Math.max(1, nRows - 1)) });
            }
            it.fill = stops.length >= 2 ? { grad: stops, ang: cellN(sh, D, 'FillGradientAngle', Math.PI / 2), dir: cellN(sh, D, 'FillGradientDir', 0) } : { c: fg, a: 1 - ft };
          }
          else if (fp >= 25 && fp <= 40) it.fill = { grad: [{ c: fg, a: 1 - ft, pos: 0 }, { c: bg, a: 1 - cellN(sh, D, 'FillBkgndTrans', 0), pos: 1 }], ang: fp >= 28 && fp <= 30 ? Math.PI / 2 : 0, dir: 0 };
          else if (fgV === 'Themed' && thf && thf.grad) it.fill = thf;
          else it.fill = { c: fg, a: fgV === 'Themed' && thf && thf.a != null ? thf.a : 1 - ft };
          /* 线 */
          const lcV = cellV(sh, D, 'LineColor'), lpV = cellV(sh, D, 'LinePattern'), lwV = cellV(sh, D, 'LineWeight');
          const thl = (lcV === 'Themed' || lpV === 'Themed' || lwV === 'Themed') ? thLine(sh, it.oneD) : null;
          const lp = lpV === 'Themed' ? (thl === 'none' ? 0 : 1) : num(lpV, 1);
          if (lp === 0) it.line = null;
          else it.line = {
            c: color(D, lcV) || (thl && thl !== 'none' && thl.c) || '000000', a: lcV === 'Themed' && thl && thl.a != null ? thl.a : 1 - cellN(sh, D, 'LineColorTrans', 0), w: Math.max(0.25, lwV === 'Themed' ? ((thl && thl.w) || 0.75) : num(lwV, 0.01) * 72), dash: DASH(lp),
            head: ARROW(cellV(sh, D, 'BeginArrow')), tail: ARROW(cellV(sh, D, 'EndArrow')), hs: cellN(sh, D, 'BeginArrowSize', 2), ts: cellN(sh, D, 'EndArrowSize', 2), cap: cellN(sh, D, 'LineCap', 0)
          };
          /* 阴影 */
          const shType = cellN(sh, D, 'ShapeShdwType', 0), shShow = cellN(sh, D, 'ShapeShdwShow', 0), shPat = cellN(sh, D, 'ShdwPattern', 0);
          if (shPat > 0 && (shShow > 0 || shType > 0 || cellV(sh, D, 'ShapeShdwShow') == null)) it.shadow = { c: color(D, cellV(sh, D, 'ShdwForegnd')) || themeColor(TT, cellN(sh, D, 'QuickStyleShadowColor', NaN), varIdx) || '000000', a: 1 - cellN(sh, D, 'ShdwForegndTrans', 0), dx: cellN(sh, D, 'ShapeShdwOffsetX', 0.0625) * ps, dy: -cellN(sh, D, 'ShapeShdwOffsetY', -0.0625) * ps, blur: cellN(sh, D, 'ShapeShdwBlur', 0) * ps };

          /* ---- 图片 ---- */
          if (type === 'Foreign') {
            let fd = kid(el, 'ForeignData'), rm = relsMap;
            if (!fd && msEl) { fd = kid(msEl, 'ForeignData'); rm = M.rels; }
            if (fd) {
              const r = kid(fd, 'Rel'); let med = null;
              if (r) { const rr = rm[rId(r)]; med = rr ? await media(rr.target) : null; }
              else if (fd.textContent.trim()) {
                const ftp = (fd.getAttribute('ForeignType') || '').toLowerCase(), comp = (fd.getAttribute('CompressionType') || '').toLowerCase();
                const b64 = fd.textContent.replace(/\s+/g, ''), bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
                med = { ext: comp === 'jpeg' ? 'jpg' : comp === 'png' ? 'png' : comp === 'gif' ? 'gif' : comp === 'tiff' ? 'tiff' : /enhmeta/.test(ftp) ? 'emf' : /metafile/.test(ftp) ? 'wmf' : 'png', data: u };
              }
              if (med) it.img = { med, x: cellN(sh, D, 'ImgOffsetX', 0), y: cellN(sh, D, 'ImgOffsetY', 0), w: cellN(sh, D, 'ImgWidth', w), h: cellN(sh, D, 'ImgHeight', h) };
              else D.warn.push('有 1 个嵌入对象缺少预览图，已跳过');
            }
            it.paths = it.paths.filter(p => !p.noLine && false);   // 外部对象的几何多为隐藏边框
          }

          /* ---- 文字 ---- */
          const runs = cellV(sh, D, 'HideText') === '1' ? null : textRuns(sh);
          if (runs && runs.some(r => r.t.trim())) {
            const tw = cellN(sh, D, 'TxtWidth', w), th = cellN(sh, D, 'TxtHeight', h);
            const tpx = cellN(sh, D, 'TxtPinX', w / 2), tpy = cellN(sh, D, 'TxtPinY', h / 2);
            const tlx = cellN(sh, D, 'TxtLocPinX', tw / 2), tly = cellN(sh, D, 'TxtLocPinY', th / 2), ta = cellN(sh, D, 'TxtAngle', 0);
            const tM = mul(mul(T(tpx, tpy), R(ta)), T(-tlx, -tly));
            const paras = [];
            let para = null;
            const newPara = pp => { para = { pp, runs: [] }; paras.push(para); };
            newPara(runs[0].pp);
            for (const r of runs) {
              const parts = r.t.replace(/\r\n?/g, '\n').split(/(\n|\u2028)/);
              for (const part of parts) {
                if (part === '\n' || part === '\u2028') { newPara(r.pp); continue; }
                if (!part) continue;
                if (!para.runs.length) para.pp = r.pp;
                para.runs.push({ t: part.replace(/\uFFFC/g, ''), cp: r.cp });
              }
            }
            while (paras.length > 1 && !paras[paras.length - 1].runs.length) paras.pop();
            const thFontC = thFont(sh, it.oneD);
            const fallbackLatin = D.theme.latin || 'Calibri', fallbackEa = D.theme.hans || D.theme.ea || '宋体';
            const P = paras.map(pa => {
              const pv = N => rowV(sh, D, 'Paragraph', pa.pp, N);
              const ha = num(pv('HorzAlign'), 1), spl = num(pv('SpLine'), -1.2);
              return {
                align: ['l', 'ctr', 'r', 'just', 'dist'][ha] || 'ctr', spLine: spl, spBefore: num(pv('SpBefore'), 0) * 72, spAfter: num(pv('SpAfter'), 0) * 72,
                indLeft: num(pv('IndLeft'), 0), indFirst: num(pv('IndFirst'), 0), indRight: num(pv('IndRight'), 0), bullet: num(pv('Bullet'), 0) > 0 ? (pv('BulletStr') || '•') : null,
                runs: pa.runs.map(rn => {
                  const cv = N => rowV(sh, D, 'Character', rn.cp, N);
                  const st = num(cv('Style'), 0), sz = num(cv('Size'), 1 / 6) * 72;
                  const latin = fontName(D, cv('Font'), fallbackLatin);
                  let ea = fontName(D, cv('AsianFont'), null);
                  if (!ea) ea = CJK.test(latin) || /song|hei|kai|fang|yahei|simsun|simhei|dengxian|等线|宋|黑|楷|仿宋|雅黑/i.test(latin) ? latin : fallbackEa;
                  return { t: rn.t, sz, b: !!(st & 1), i: !!(st & 2), u: !!(st & 4), sc: !!(st & 8), strike: num(cv('Strikethru'), 0) > 0, c: color(D, cv('Color')) || (cv('Color') === 'Themed' && thFontC && thFontC.c) || '000000', themed: cv('Color') === 'Themed', ca: 1 - num(cv('ColorTrans'), 0), latin, ea, caps: num(cv('Case'), 0) === 1, pos: num(cv('Pos'), 0) };
                }),
              };
            });
            /* 主题字色与底色对比不足（如白字落在无填充形状上）时，按 Visio 的自动对比改用深色／浅色 */
            const bgHex = it.fill && it.paths.some(p => !p.noFill) ? (it.fill.c || (it.fill.grad && it.fill.grad[0].c)) : 'FFFFFF';
            const lumOf = h => { const [r, g, b] = hex2rgb(h).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
            const contrast = (a, b) => { const x = lumOf(a), y = lumOf(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
            for (const pa of P) for (const r of pa.runs) if (r.themed && bgHex && contrast(r.c, bgHex) < 1.8) r.c = lumOf(bgHex) > 0.4 ? ((TT && TT.clr.dk1) || '000000') : ((TT && TT.clr.lt1) || 'FFFFFF');
            const va = cellN(sh, D, 'VerticalAlign', 1);
            const tb = cellV(sh, D, 'TextBkgnd');
            it.text = {
              M: tM, w: tw, h: th, paras: P, anchor: ['t', 'ctr', 'b'][va] || 'ctr', vert: cellN(sh, D, 'TextDirection', 0) === 1,
              mar: ['LeftMargin', 'RightMargin', 'TopMargin', 'BottomMargin'].map(N => cellN(sh, D, N, 4 / 72) * 72),
              bg: tb && tb !== '0' ? color(D, /^\d+$/.test(tb) ? String(+tb - 1) : tb) : null, bga: 1 - cellN(sh, D, 'TextBkgndTrans', 0),
            };
          }

          /* ---- 组合 ---- */
          const subs = kid(el, 'Shapes');
          if (subs || (msEl && kid(msEl, 'Shapes') && type === 'Group')) {
            it.kids = [];
            if (subs) await walk(subs, Mx, mId, it.kids, relsMap, depth + 1);
            else {
              /* 实例未展开子形状：按主控尺寸缩放套用 */
              const mw = num(cellsOf(msEl).Width?.getAttribute('V'), w) || w, mh = num(cellsOf(msEl).Height?.getAttribute('V'), h) || h;
              await walk(kid(msEl, 'Shapes'), mul(Mx, S(w / mw, h / mh)), mId, it.kids, M.rels, depth + 1);
            }
            it.groupFront = cellN(sh, D, 'DisplayMode', 2) !== 1;
          }
          out.push(it);
        }
      }
    }
    function isRectPath(p, w, h) {
      if (!p || p.segs.length < 4 || p.segs.length > 5 || p.segs.some(s => s[0] === 'C')) return false;
      const tol = Math.max(w, h) * 1e-3 + 1e-6;
      const pts = p.segs.map(s => [s[1], s[2]]);
      const on = q => (Math.abs(q[0]) < tol || Math.abs(q[0] - w) < tol) && (Math.abs(q[1]) < tol || Math.abs(q[1] - h) < tol);
      if (!pts.every(on)) return false;
      const set = new Set(pts.map(q => (Math.abs(q[0]) < tol ? 0 : 1) + ',' + (Math.abs(q[1]) < tol ? 0 : 1)));
      return set.size === 4;
    }

    const pages = [];
    for (const pg of pageEls) {
      if (pg.getAttribute('Background') === '1') continue;
      const psh = mkSheet(kid(pg, 'PageSheet'));
      const ps = (num(psh.cells.PageScale?.getAttribute('V'), 1) / (num(psh.cells.DrawingScale?.getAttribute('V'), 1) || 1)) || 1;
      const pw = num(psh.cells.PageWidth?.getAttribute('V'), 11) * ps, ph = num(psh.cells.PageHeight?.getAttribute('V'), 8.5) * ps;
      let items = [];
      /* 背景页（可多级） */
      const bgs = []; let b = pg.getAttribute('BackPage'), guard = 0;
      while (b && byId[b] && guard++ < 5) { bgs.unshift(byId[b]); b = byId[b].getAttribute('BackPage'); }
      for (const bp of bgs) items.push(...await pageItems(bp, ps));
      items.push(...await pageItems(pg, ps));
      pages.push({ name: pg.getAttribute('Name') || pg.getAttribute('NameU') || `页-${pages.length + 1}`, w: pw, h: ph, items });
    }
    return { pages, warnings: [...new Set(D.warn)] };
  }

  /* =========================================================================
     写 PowerPoint：用 PptxGenJS 生成骨架（版式、母版、空白页），再逐页写入 DrawingML
     ========================================================================= */
  const E = v => Math.round(v * EMU);
  /* 局部框（y 向下，英寸）→ 幻灯片 xfrm：返回 {off, ext, rot, flipH, toLocal} */
  function frameOf(Mslide, w, h) {
    /* Mslide：局部（Visio，y 向上）→ 幻灯片英寸。ppt 局部坐标 p = (x, h - y) */
    const K = [1, 0, 0, -1, 0, h];
    const Q = mul(Mslide, K);
    const ux = Q[0], uy = Q[1], vx = Q[2], vy = Q[3];
    const sx = Math.hypot(ux, uy) || 1, sy = Math.hypot(vx, vy) || 1, det = ux * vy - uy * vx;
    let rot, flipH = false;
    if (det >= 0) rot = Math.atan2(uy, ux);
    else { rot = Math.atan2(-uy, -ux); flipH = true; }
    return { Q, sx, sy, rot, flipH };
  }
  function xfrmXml(fr, bx0, by0, bx1, by1) {
    /* bx/by：缩放后的 ppt 局部坐标（英寸） */
    const cl = [(bx0 + bx1) / 2, (by0 + by1) / 2];
    const O = ap(fr.Q, 0, 0);
    const c = Math.cos(fr.rot), s = Math.sin(fr.rot), fl = fr.flipH ? -1 : 1;
    const cs = [O[0] + c * fl * cl[0] - s * cl[1], O[1] + s * fl * cl[0] + c * cl[1]];
    const ew = bx1 - bx0, eh = by1 - by0;
    let deg = fr.rot * 180 / Math.PI; deg = ((deg % 360) + 360) % 360; if (Math.abs(deg - 360) < 1e-3) deg = 0;
    const box = { x: cs[0] - ew / 2, y: cs[1] - eh / 2, w: ew, h: eh, deg };
    return { xml: `<a:xfrm${deg > 0.01 ? ` rot="${Math.round(deg * 60000)}"` : ''}${fr.flipH ? ' flipH="1"' : ''}><a:off x="${E(box.x)}" y="${E(box.y)}"/><a:ext cx="${Math.max(0, E(ew))}" cy="${Math.max(0, E(eh))}"/></a:xfrm>`, box };
  }
  function aabb(box) {
    const r = box.deg * Math.PI / 180, c = Math.abs(Math.cos(r)), s = Math.abs(Math.sin(r));
    const W = box.w * c + box.h * s, H = box.w * s + box.h * c, cx = box.x + box.w / 2, cy = box.y + box.h / 2;
    return [cx - W / 2, cy - H / 2, cx + W / 2, cy + H / 2];
  }
  const clr = (c, a) => `<a:srgbClr val="${c}">${a < 0.999 ? `<a:alpha val="${Math.round(Math.max(0, a) * 100000)}"/>` : ''}</a:srgbClr>`;
  function fillXml(f) {
    if (!f) return '<a:noFill/>';
    if (f.grad) {
      const stops = f.grad.slice().sort((a, b) => a.pos - b.pos).map(g => `<a:gs pos="${Math.round(Math.min(1, Math.max(0, g.pos)) * 100000)}">${clr(g.c, g.a)}</a:gs>`).join('');
      let deg = (360 - (f.ang * 180 / Math.PI)) % 360; if (deg < 0) deg += 360;
      const path = f.dir >= 1 ? `<a:path path="${f.dir === 1 ? 'circle' : 'rect'}"><a:fillToRect l="50000" t="50000" r="50000" b="50000"/></a:path>` : `<a:lin ang="${Math.round(deg * 60000)}" scaled="0"/>`;
      return `<a:gradFill rotWithShape="1"><a:gsLst>${stops}</a:gsLst>${path}</a:gradFill>`;
    }
    return `<a:solidFill>${clr(f.c, f.a)}</a:solidFill>`;
  }
  function arrowSz(s, lw) {
    /* Visio 箭头尺寸（0 极小…6 巨大）→ PPT w/len；PPT 箭头随线宽缩放，细线时放大一档 */
    const want = [0.045, 0.06, 0.085, 0.12, 0.17, 0.24, 0.32][Math.max(0, Math.min(6, Math.round(s)))] * 72;   // 期望长度（磅）
    const opts = [['sm', 2], ['med', 3], ['lg', 5]];
    let best = opts[0]; for (const o of opts) if (Math.abs(o[1] * lw - want) < Math.abs(best[1] * lw - want)) best = o;
    return `w="${best[0]}" len="${best[0]}"`;
  }
  function lineXml(l, open) {
    if (!l) return '<a:ln><a:noFill/></a:ln>';
    let x = `<a:ln w="${Math.round(l.w * 12700)}"${l.cap === 1 ? ' cap="sq"' : l.cap === 0 ? ' cap="rnd"' : ''}><a:solidFill>${clr(l.c, l.a)}</a:solidFill>`;
    if (l.dash) x += `<a:prstDash val="${l.dash}"/>`;
    x += '<a:round/>';
    if (open && l.head) x += `<a:headEnd type="${l.head}" ${arrowSz(l.hs, l.w)}/>`;
    if (open && l.tail) x += `<a:tailEnd type="${l.tail}" ${arrowSz(l.ts, l.w)}/>`;
    return x + '</a:ln>';
  }
  function shadowXml(sd) {
    if (!sd) return '';
    const dist = Math.hypot(sd.dx, sd.dy), dir = ((Math.atan2(sd.dy, sd.dx) * 180 / Math.PI) + 360) % 360;
    return `<a:effectLst><a:outerShdw blurRad="${E(sd.blur)}" dist="${E(dist)}" dir="${Math.round(dir * 60000)}" algn="ctr" rotWithShape="0">${clr(sd.c, sd.a)}</a:outerShdw></a:effectLst>`;
  }
  function txBodyXml(t, lIns, tIns, rIns, bIns) {
    const ps = t.paras.map(p => {
      let pPr = `<a:pPr algn="${p.align}"`;
      if (p.indLeft || p.indFirst) pPr += ` marL="${E(p.indLeft)}" indent="${E(p.indFirst)}"`;
      if (p.indRight) pPr += ` marR="${E(p.indRight)}"`;
      pPr += '>';
      if (p.spLine < 0) pPr += `<a:lnSpc><a:spcPct val="${Math.round(Math.abs(p.spLine) / 1.2 * 100000)}"/></a:lnSpc>`;
      else if (p.spLine > 0) pPr += `<a:lnSpc><a:spcPts val="${Math.round(p.spLine * 72 * 100)}"/></a:lnSpc>`;
      if (p.spBefore) pPr += `<a:spcBef><a:spcPts val="${Math.round(p.spBefore * 100)}"/></a:spcBef>`;
      if (p.spAfter) pPr += `<a:spcAft><a:spcPts val="${Math.round(p.spAfter * 100)}"/></a:spcAft>`;
      pPr += p.bullet ? `<a:buFontTx/><a:buChar char="${xmlEsc(p.bullet[0] || '•')}"/>` : '<a:buNone/>';
      pPr += '</a:pPr>';
      const rPr = r => {
        const cjk = CJK.test(r.t);
        let a = `<a:rPr lang="${cjk ? 'zh-CN' : 'en-US'}" altLang="${cjk ? 'en-US' : 'zh-CN'}" sz="${Math.max(100, Math.round(r.sz * 100))}"${r.b ? ' b="1"' : ' b="0"'}${r.i ? ' i="1"' : ''}${r.u ? ' u="sng"' : ''}${r.strike ? ' strike="sngStrike"' : ''}${r.caps ? ' cap="all"' : r.sc ? ' cap="small"' : ''}${r.pos === 1 ? ' baseline="30000"' : r.pos === 2 ? ' baseline="-25000"' : ''} dirty="0">`;
        a += `<a:solidFill>${clr(r.c, r.ca)}</a:solidFill><a:latin typeface="${xmlEsc(r.latin)}"/><a:ea typeface="${xmlEsc(r.ea)}"/><a:cs typeface="${xmlEsc(r.latin)}"/></a:rPr>`;
        return a;
      };
      const runs = p.runs.map(r => {
        /* 制表符保留；文本内的换行已在解析时拆段 */
        return `<a:r>${rPr(r)}<a:t>${xmlEsc(r.t)}</a:t></a:r>`;
      }).join('');
      const last = p.runs[p.runs.length - 1] || (t.paras.find(q => q.runs.length) || { runs: [{ sz: 12, t: '', latin: 'Calibri', ea: '宋体', c: '000000', ca: 1 }] }).runs[0];
      return `<a:p>${pPr}${runs}<a:endParaRPr lang="zh-CN" sz="${Math.max(100, Math.round(last.sz * 100))}" dirty="0"><a:latin typeface="${xmlEsc(last.latin)}"/><a:ea typeface="${xmlEsc(last.ea)}"/></a:endParaRPr></a:p>`;
    }).join('');
    return `<p:txBody><a:bodyPr wrap="square" lIns="${E(lIns)}" tIns="${E(tIns)}" rIns="${E(rIns)}" bIns="${E(bIns)}" anchor="${t.anchor}"${t.vert ? ' vert="eaVert"' : ''} rtlCol="0" upright="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>${ps}</p:txBody>`;
  }

  function slideXml(page, ctx) {
    let id = 2;
    const parts = [];
    const emitShape = it => {
      const out = []; const bboxes = [];
      const fr = frameOf(it.M, it.w, it.h);
      const name = xmlEsc(it.name || ('Shape ' + it.id));
      const visiblePaths = it.paths.filter(p => !(p.noFill && p.noLine) && (p.noFill ? (it.line) : true));
      const hasGeom = visiblePaths.some(p => (!p.noFill && it.fill) || (!p.noLine && it.line));
      const t = it.text;
      /* 文字框是否与形状框重合（可直接写进形状） */
      const tSame = t && Math.abs(t.w - it.w) < 1e-3 && Math.abs(t.h - it.h) < 1e-3 && Math.abs(t.M[4]) < 1e-3 && Math.abs(t.M[5]) < 1e-3 && Math.abs(t.M[1]) < 1e-6 && t.M[0] > 0 && !it.oneD;
      const mar = t ? t.mar.map(v => v / 72) : [0, 0, 0, 0];
      if (it.img) {
        const im = it.img, rel = ctx.addMedia(im.med);
        if (rel) {
          /* 图片可见部分 = 图片框 ∩ 形状框 → 裁切 */
          const ix0 = Math.max(0, im.x), iy0 = Math.max(0, im.y), ix1 = Math.min(it.w, im.x + im.w), iy1 = Math.min(it.h, im.y + im.h);
          if (ix1 > ix0 && iy1 > iy0) {
            const crop = { l: (ix0 - im.x) / im.w, r: (im.x + im.w - ix1) / im.w, b: (iy0 - im.y) / im.h, t: (im.y + im.h - iy1) / im.h };
            const bx0 = ix0 * fr.sx, bx1 = ix1 * fr.sx, by0 = (it.h - iy1) * fr.sy, by1 = (it.h - iy0) * fr.sy;
            const xf = xfrmXml(fr, bx0, by0, bx1, by1); bboxes.push(aabb(xf.box));
            const src = ['l', 't', 'r', 'b'].filter(k => crop[k] > 1e-4).map(k => `${k}="${Math.round(crop[k] * 100000)}"`).join(' ');
            out.push(`<p:pic><p:nvPicPr><p:cNvPr id="${id++}" name="${name}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="${rel}"/>${src ? `<a:srcRect ${src}/>` : ''}<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>${xf.xml}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>${it.line && it.paths.length ? lineXml(it.line, false) : '<a:ln><a:noFill/></a:ln>'}</p:spPr></p:pic>`);
          }
        }
      }
      let textDone = false;
      if (hasGeom) {
        /* 局部 ppt 坐标（缩放后，英寸） */
        const L = (x, y) => [x * fr.sx, (it.h - y) * fr.sy];
        let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
        const tp = visiblePaths.map(p => p.segs.map(s => { const o = [s[0]]; for (let i = 1; i < s.length; i += 2) { const q = L(s[i], s[i + 1]); o.push(q[0], q[1]); x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); } return o; }));
        const combine = tSame && t;
        if (combine) { x0 = Math.min(x0, 0); y0 = Math.min(y0, 0); x1 = Math.max(x1, it.w * fr.sx); y1 = Math.max(y1, it.h * fr.sy); }
        const eps = 0.004; if (x1 - x0 < eps) { x0 -= eps / 2; x1 += eps / 2; } if (y1 - y0 < eps) { y0 -= eps / 2; y1 += eps / 2; }
        const prst = (it.isRect || it.isEllipse || it.round) && visiblePaths.length === 1 && Math.abs(x0) < 1e-4 && Math.abs(y0) < 1e-4 && Math.abs(x1 - it.w * fr.sx) < 1e-3 && Math.abs(y1 - it.h * fr.sy) < 1e-3;
        const xf = xfrmXml(fr, x0, y0, x1, y1); bboxes.push(aabb(xf.box));
        let geom;
        if (prst) geom = it.isEllipse ? '<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>' : it.round ? `<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val ${Math.round(Math.min(50000, it.round * Math.min(fr.sx, fr.sy) / Math.max(1e-6, Math.min(x1 - x0, y1 - y0)) * 100000))}"/></a:avLst></a:prstGeom>` : '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>';
        else {
          const W = E(x1 - x0), H = E(y1 - y0), P = (x, y) => `<a:pt x="${E(x - x0)}" y="${E(y - y0)}"/>`;
          const pl = visiblePaths.map((p, k) => {
            let s = `<a:path w="${W}" h="${H}"${p.noFill || !it.fill ? ' fill="none"' : ''}${p.noLine || !it.line ? ' stroke="0"' : ''}>`;
            for (const g of tp[k]) {
              if (g[0] === 'M') s += `<a:moveTo>${P(g[1], g[2])}</a:moveTo>`;
              else if (g[0] === 'L') s += `<a:lnTo>${P(g[1], g[2])}</a:lnTo>`;
              else if (g[0] === 'C') s += `<a:cubicBezTo>${P(g[1], g[2])}${P(g[3], g[4])}${P(g[5], g[6])}</a:cubicBezTo>`;
            }
            if (p.closed) s += '<a:close/>';
            return s + '</a:path>';
          }).join('');
          geom = `<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="l" t="t" r="r" b="b"/><a:pathLst>${pl}</a:pathLst></a:custGeom>`;
        }
        const open = visiblePaths.some(p => !p.closed);
        let body = '';
        if (combine) {
          /* 文字框与形状框重合但几何外延时，内边距补上外延 */
          body = txBodyXml(t, mar[0] + (0 - x0), mar[2] + (0 - y0), mar[1] + (x1 - it.w * fr.sx), mar[3] + (y1 - it.h * fr.sy));
          textDone = true;
        } else body = '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="zh-CN"/></a:p></p:txBody>';
        out.push(`<p:sp><p:nvSpPr><p:cNvPr id="${id++}" name="${name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr>${xf.xml}${geom}${visiblePaths.some(p => !p.noFill) ? fillXml(it.fill) : '<a:noFill/>'}${lineXml(visiblePaths.some(p => !p.noLine) ? it.line : null, open)}${shadowXml(it.shadow)}</p:spPr>${body}</p:sp>`);
      }
      if (t && !textDone) {
        const tM = mul(it.M, t.M);
        const tf = frameOf(tM, t.w, t.h);
        let x0 = 0, y0 = 0, x1 = t.w * tf.sx, y1 = t.h * tf.sy;
        const eps = 0.02; if (x1 - x0 < eps) { x0 -= eps / 2; x1 += eps / 2; } if (y1 - y0 < eps) { y0 -= eps / 2; y1 += eps / 2; }
        const xf = xfrmXml(Object.assign({}, tf, { flipH: false }), x0, y0, x1, y1);
        bboxes.push(aabb(xf.box));
        const fill = t.bg ? `<a:solidFill>${clr(t.bg, t.bga)}</a:solidFill>` : '<a:noFill/>';
        out.push(`<p:sp><p:nvSpPr><p:cNvPr id="${id++}" name="${name} 文字"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>${xf.xml}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>${fill}<a:ln><a:noFill/></a:ln></p:spPr>${txBodyXml(t, mar[0], mar[2], mar[1], mar[3])}</p:sp>`);
      }
      return { xml: out, bboxes };
    };
    const emit = it => {
      if (it.kids && it.kids.length) {
        const own = emitShape(it);
        const kidsOut = it.kids.map(emit).filter(k => k.xml.length);
        /* 组合自身几何：默认在成员之前（背景），文字最后 */
        const geomX = own.xml.filter(x => !/ 文字"/.test(x)), textX = own.xml.filter(x => / 文字"/.test(x));
        const all = [...(it.groupFront ? [] : geomX), ...kidsOut.flatMap(k => k.xml), ...(it.groupFront ? geomX : []), ...textX];
        const bbs = [...own.bboxes, ...kidsOut.flatMap(k => k.bboxes)];
        if (all.length <= 1 || !bbs.length) return { xml: all, bboxes: bbs };
        const gx0 = Math.min(...bbs.map(b => b[0])), gy0 = Math.min(...bbs.map(b => b[1])), gx1 = Math.max(...bbs.map(b => b[2])), gy1 = Math.max(...bbs.map(b => b[3]));
        const g = `<a:off x="${E(gx0)}" y="${E(gy0)}"/><a:ext cx="${E(gx1 - gx0)}" cy="${E(gy1 - gy0)}"/>`;
        return { xml: [`<p:grpSp><p:nvGrpSpPr><p:cNvPr id="${id++}" name="${xmlEsc(it.name || '组合 ' + it.id)}"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>${g}<a:chOff x="${E(gx0)}" y="${E(gy0)}"/><a:chExt cx="${E(gx1 - gx0)}" cy="${E(gy1 - gy0)}"/></a:xfrm></p:grpSpPr>${all.join('')}</p:grpSp>`], bboxes: [[gx0, gy0, gx1, gy1]] };
      }
      return emitShape(it);
    };
    for (const it of page.items) parts.push(...emit(it).xml);
    return parts.join('');
  }

  const CT = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', bmp: 'image/bmp', tiff: 'image/tiff', emf: 'image/x-emf', wmf: 'image/x-wmf', svg: 'image/svg+xml' };
  /* parsed：parse() 的结果；opts.fit：'page'（与原页面同尺寸，默认）| '169'（16:9 宽屏等比缩放） */
  async function toPPTX(parsed, opts) {
    opts = opts || {};
    const pages = parsed.pages; if (!pages.length) throw new Error('没有可转换的页面');
    let SW, SH;
    if (opts.fit === '169') { SW = 13.333; SH = 7.5; }
    else { SW = pages[0].w; SH = pages[0].h; }
    /* PowerPoint 幻灯片尺寸限制 1～56 英寸 */
    let lim = 1; const MAX = 56;
    if (SW > MAX || SH > MAX) { lim = MAX / Math.max(SW, SH); SW *= lim; SH *= lim; parsed.warnings.push(`页面超过 PowerPoint 上限（56 英寸），已等比缩小为 ${Math.round(lim * 100)}%，字号同比缩小`); }
    if (SW < 1) SW = 1; if (SH < 1) SH = 1;
    const pptx = new PptxGenJS();
    pptx.defineLayout({ name: 'VSD', width: SW, height: SH }); pptx.layout = 'VSD';
    for (const p of pages) pptx.addSlide();
    const ab = await pptx.write({ outputType: 'arraybuffer' });
    const zip = await JSZip.loadAsync(ab);
    const exts = new Set();
    let mediaN = 0; const mediaMap = new Map();
    for (let i = 0; i < pages.length; i++) {
      const pg = pages[i];
      /* 每页按幻灯片尺寸放置：与首页同尺寸时 1:1；否则等比缩放居中 */
      const k = Math.min(SW / pg.w, SH / pg.h, opts.fit === '169' ? Infinity : (Math.abs(pg.w - pages[0].w) < 1e-3 && Math.abs(pg.h - pages[0].h) < 1e-3 ? lim : Infinity));
      if (Math.abs(k - 1) > 1e-3 && opts.fit !== '169' && i > 0) parsed.warnings.push(`第 ${i + 1} 页尺寸与首页不同，已等比缩放为 ${Math.round(k * 100)}%`);
      const ox = (SW - pg.w * k) / 2, oy = (SH - pg.h * k) / 2;
      const scaleM = [k, 0, 0, k, ox, oy];
      const rels = [];
      const ctx = {
        addMedia(med) {
          let target = mediaMap.get(med);
          if (!target) { target = `media/vsd_${++mediaN}.${med.ext}`; mediaMap.set(med, target); zip.file('ppt/' + target, med.data); exts.add(med.ext); }
          const rid = 'rIdV' + (rels.length + 1); rels.push(`<Relationship Id="${rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../${target}"/>`);
          return rid;
        },
      };
      /* 字号随缩放调整 */
      const scaleText = it => { if (it.text && Math.abs(k - 1) > 1e-3) for (const p of it.text.paras) { p.spBefore *= k; p.spAfter *= k; for (const r of p.runs) r.sz *= k; } if (it.text && Math.abs(k - 1) > 1e-3) it.text.mar = it.text.mar.map(v => v * k); if (it.line && Math.abs(k - 1) > 1e-3) it.line.w = Math.max(0.25, it.line.w * k); if (it.kids) it.kids.forEach(scaleText); };
      const reM = it => { it.M = mul(scaleM, it.M); };   // 只改顶层，子形状矩阵已含父矩阵
      const fixAll = it => { it.M = mul(scaleM, it.M); if (it.kids) it.kids.forEach(fixAll); };
      pg.items.forEach(fixAll); pg.items.forEach(scaleText);
      const sx = slideXml(pg, ctx);
      const sp = `ppt/slides/slide${i + 1}.xml`;
      let x = await zip.file(sp).async('string');
      x = x.replace(/<\/p:spTree>/, sx + '</p:spTree>');
      if (!/xmlns:r=/.test(x.slice(0, 600))) x = x.replace('<p:sld ', '<p:sld xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ');
      zip.file(sp, x);
      if (rels.length) {
        const rp = `ppt/slides/_rels/slide${i + 1}.xml.rels`;
        let r = await zip.file(rp).async('string');
        r = r.replace('</Relationships>', rels.join('') + '</Relationships>');
        zip.file(rp, r);
      }
    }
    if (exts.size) {
      let ct = await zip.file('[Content_Types].xml').async('string');
      for (const e of exts) if (!new RegExp(`Extension="${e}"`, 'i').test(ct)) ct = ct.replace('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">', m => m + `<Default Extension="${e}" ContentType="${CT[e] || 'application/octet-stream'}"/>`);
      zip.file('[Content_Types].xml', ct);
    }
    return await zip.generateAsync({ type: 'blob', mimeType: 'application/vnd.openxmlformats-officedocument.presentationml.presentation', compression: 'DEFLATE' });
  }

  window.VsdxRaw = { parse, toPPTX };
})();
