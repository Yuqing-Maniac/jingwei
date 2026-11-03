/* ============ 织图 · draw.io（diagrams.net）互通 ============
 * 导出：每页一个 <diagram>，分组带／层 → 竖排标题泳道（swimlane horizontal=0），容器 → 泳道容器，
 *       子元素用相对坐标挂在父容器下（在 draw.io 里拖动容器，内容随之移动）；装备卡 → 图片单元；
 *       连线保留端点、折点、箭头、线型与颜色；下钻页 → draw.io 页面链接（data:page/id,…）；
 *       图例、标题栏 → 矢量图片。每个单元附带 ht_* 属性（draw.io“编辑数据”里可见），再导入时无损还原类型、图标、状态、编号。
 * 导入：支持未压缩与压缩（deflate + base64）的 .drawio／.xml，含多页、UserObject、相对坐标、浮动端点连线、边标签单元。
 * 依赖 app.js 全局：doc, cur, T, P, mkNode, uid, pagesInOrder, contentBBox, linkPoints, iconURI, nodeLayout, stStyle,
 *                   nodeSVG, BAND_TW, GROUP_TH, laneTW, LINK_KINDS, GEO, saveFile, fname, toast, esc, snapv。 */
(function () {
  'use strict';
  const xa = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/\n/g, '&#xa;');
  const r1 = v => Math.round(v * 10) / 10;
  const b64 = s => btoa(unescape(encodeURIComponent(s)));
  const xh = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  /* draw.io 的 style 用 ; 分隔，所以图片只能写成 data:image/svg+xml,BASE64（不带 ;base64） */
  function styleImage(uri) {
    if (!uri) return null;
    let m = uri.match(/^data:image\/svg\+xml;charset=utf-8,(.*)$/);
    if (m) return 'data:image/svg+xml,' + b64(decodeURIComponent(m[1]));
    m = uri.match(/^data:image\/svg\+xml;base64,(.*)$/); if (m) return 'data:image/svg+xml,' + m[1];
    m = uri.match(/^data:(image\/[\w.+-]+);base64,(.*)$/); if (m) return `data:${m[1]},${m[2]}`;
    m = uri.match(/^data:image\/svg\+xml,(.*)$/); if (m) return 'data:image/svg+xml,' + b64(decodeURIComponent(m[1]));
    return null;
  }
  const SHAPE_OUT = {
    rect: 'rounded=0', round: 'rounded=1;arcSize=20',
    roundL: 'shape=mxgraph.basic.rect;rectStyle=square;size=10;absoluteCornerSize=1;fillColor2=none;topLeftStyle=rounded;bottomLeftStyle=rounded',
    roundR: 'shape=mxgraph.basic.rect;rectStyle=square;size=10;absoluteCornerSize=1;fillColor2=none;topRightStyle=rounded;bottomRightStyle=rounded', ellipse: 'ellipse', diamond: 'rhombus', hexagon: 'shape=hexagon;perimeter=hexagonPerimeter2;size=0.2',
    cylinder: 'shape=cylinder3;boundedLbl=1;size=8', cloud: 'ellipse;shape=cloud', document: 'shape=document;size=0.2;boundedLbl=1', triangle: 'triangle;direction=north',
    parallelogram: 'shape=parallelogram;perimeter=parallelogramPerimeter;size=0.2', trapezoid: 'shape=trapezoid;perimeter=trapezoidPerimeter;size=0.2', cube: 'shape=cube;size=10',
    octagon: 'shape=mxgraph.basic.octagon2;dx=12', pentagon: 'shape=mxgraph.basic.pentagon', star: 'shape=mxgraph.basic.star', callout: 'shape=callout;perimeter=calloutPerimeter',
    predef: 'shape=process;size=0.12', display: 'shape=display;size=0.15', chevron: 'shape=step;perimeter=stepPerimeter;size=0.2', homeplate: 'shape=mxgraph.arrows2.arrow;dy=0;dx=20;notch=0',
    donut: 'ellipse;shape=doubleEllipse', plus: 'shape=cross', terminator: 'rounded=1;arcSize=50', arrowR: 'shape=singleArrow;direction=east', arrowL: 'shape=singleArrow;direction=west',
    arrowU: 'shape=singleArrow;direction=north', arrowD: 'shape=singleArrow;direction=south', arrowLR: 'shape=doubleArrow', arrowUD: 'shape=doubleArrow;direction=north',
  };
  const DASH = { '6 4': 'dashed=1;dashPattern=6 4', '2 4': 'dashed=1;dashPattern=2 4', '10 4 2 4': 'dashed=1;dashPattern=10 4 2 4' };

  /* ================= 导出 ================= */
  /* 页面级（视图类型）与文档级（主题、标题栏、状态名称、编号显示）设置存于根单元 0 的数据属性，draw.io 编辑保存后仍保留 */
  function rootCell(p) {
    const a = {};
    if (p.view) a.ht_view = p.view;
    if (p.id === 'root') a.ht_doc = JSON.stringify({ name: doc.name, theme: doc.theme, statusLabels: doc.statusLabels, meta: doc.meta, showCodes: !!doc.showCodes, msColor: doc.msColor, jumpStyle: doc.jumpStyle, lastKind: doc.lastKind });
    const at = Object.entries(a).map(([k, v]) => ` ${k}="${xa(v)}"`).join('');
    return at ? `<object label=""${at} id="0"><mxCell/></object>` : '<mxCell id="0"/>';
  }
  function pageXML(p, pageIds) {
    const t = T(), byId = new Map(p.nodes.map(n => [n.id, n])), out = [];
    const cid = id => 'n' + id, ids = new Set();
    const abs = n => ({ x: n.x, y: n.y });
    const parentOf = n => (n.parent && byId.has(n.parent) && !['text', 'note', 'legend', 'tblock'].includes(n.type)) ? byId.get(n.parent) : null;
    const meta = (o) => Object.entries(o).filter(([, v]) => v != null && v !== '' && v !== false).map(([k, v]) => ` ${k}="${xa(typeof v === 'object' ? JSON.stringify(v) : v)}"`).join('');
    const cell = (id, label, style, geo, par, extra = {}, vertex = true) => {
      ids.add(id);
      const g = `<mxGeometry x="${r1(geo.x)}" y="${r1(geo.y)}" width="${r1(geo.w)}" height="${r1(geo.h)}" as="geometry"/>`;
      const inner = `<mxCell style="${xa(style)}" ${vertex ? 'vertex="1"' : ''} parent="${par}">${g}</mxCell>`;
      out.push(`<UserObject label="${xa(label)}" id="${id}"${meta(extra)}>${inner}</UserObject>`);
    };
    const imgSVG = (n) => {
      const pad = 2, body = nodeSVG(n, p, true);
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${n.x - pad} ${n.y - pad} ${n.w + pad * 2} ${n.h + pad * 2}" width="${n.w + pad * 2}" height="${n.h + pad * 2}">${body}</svg>`;
    };
    const code = n => (doc.showCodes && n.code) ? n.code + ' ' : '';
    /* 父容器先于子元素输出 */
    const order = [], seen = new Set();
    const visit = n => { if (seen.has(n.id)) return; const pa = parentOf(n); if (pa) visit(pa); seen.add(n.id); order.push(n); };
    p.nodes.forEach(visit);
    for (const n of order) {
      const pa = parentOf(n), pid = pa ? cid(pa.id) : '1';
      const a = abs(n), pg = pa ? abs(pa) : { x: 0, y: 0 };
      const geo = { x: a.x - pg.x, y: a.y - pg.y, w: n.w, h: n.h };
      const ht = { ht_type: n.type, ht_icon: n.icon, ht_status: n.status !== 'base' ? n.status : '', ht_etype: n.etype, ht_code: n.code, ht_attrs: n.attrs && Object.keys(n.attrs).length ? n.attrs : '', ht_role: n.role, ht_size: n.size !== 13 ? n.size : '', ht_noBox: n.noBox ? 1 : '' };
      if (n.sub && pageIds[n.sub]) ht.link = 'data:page/id,' + pageIds[n.sub];
      const st = stStyle(n, t), fs = n.size || 13, bold = n.bold ? ';fontStyle=1' : '';
      const font = `fontSize=${fs};fontFamily=Microsoft YaHei;html=1;whiteSpace=wrap`;
      const txt = (n.text || '');
      if (n.type === 'band') {
        /* 分组带 = 容器框 + 左侧标题条（中文竖排逐字，与画布一致）；标题条带 ht_part=title，再导入时并回分组带名称 */
        const head = n.status === 'base' || !n.status ? t.band.titleFill : st.stroke;
        cell(cid(n.id), '', `rounded=0;${font};fillColor=${n.fill || t.band.fill};strokeColor=${n.stroke || t.band.stroke};strokeWidth=1.5;container=1;collapsible=0;recursiveResize=0`, geo, pid, Object.assign(ht, { ht_text: txt }));
        const chars = [...(code(n) + txt)].filter(c => c.trim());
        cell(cid(n.id) + '_t', chars.map(xh).join('<br>'), `rounded=0;${font};fontSize=15;fontStyle=1;fillColor=${head};strokeColor=none;fontColor=${t.band.titleText};movable=0;resizable=0;deletable=0;connectable=0;spacing=0`, { x: 0, y: 0, w: BAND_TW, h: n.h }, cid(n.id), { ht_part: 'title' });
      } else if (n.type === 'lane') {
        const tw = laneTW(n);
        cell(cid(n.id), code(n) + txt, `rounded=0;${font};fontSize=13.5;fontStyle=1;align=center;verticalAlign=middle;spacingRight=${r1(n.w - tw)};spacingLeft=6;fillColor=${n.fill || t.lane.fill};strokeColor=${n.stroke || t.lane.stroke};fontColor=${t.lane.titleText};container=1;collapsible=0;recursiveResize=0`, geo, pid, Object.assign(ht, n.titleW ? { ht_titleW: n.titleW } : {}));
      } else if (n.type === 'group') {
        const body = st.fill === t.box.fill ? t.group.fill : st.fill, line = st.stroke === t.box.stroke ? t.group.stroke : st.stroke;
        cell(cid(n.id), code(n) + txt, `swimlane;startSize=${GROUP_TH};${font};fontSize=12.5;fontStyle=1;rounded=1;arcSize=6;fillColor=${n.status === 'base' || !n.status ? t.group.titleFill : st.title};swimlaneFillColor=${body};strokeColor=${line};strokeWidth=1.3;fontColor=${t.group.titleText};container=1;collapsible=0;swimlaneLine=0`, geo, pid, ht);
      } else if (n.type === 'text') {
        const color = n.color === 'muted' ? t.muted : (n.color || t.text);
        cell(cid(n.id), txt, `text;${font};align=${n.align === 'left' ? 'left' : 'center'};verticalAlign=middle;fontColor=${color}${bold}`, geo, pid, ht);
      } else if (n.type === 'note') {
        cell(cid(n.id), txt, `rounded=1;arcSize=4;${font};align=left;spacingLeft=8;fillColor=${t.note.fill};strokeColor=${t.note.stroke};fontColor=${t.text}`, geo, pid, ht);
      } else if (n.type === 'legend' || n.type === 'tblock') {
        if (n.type === 'legend' && typeof legendLayout === 'function') legendLayout(n, p);
        const im = 'data:image/svg+xml,' + b64(imgSVG(n));
        cell(cid(n.id), '', `shape=image;aspect=fixed;imageAspect=0;image=${im}`, { x: geo.x - 2, y: geo.y - 2, w: n.w + 4, h: n.h + 4 }, pid, ht);
      } else {
        const L = nodeLayout(n), im = L.icon ? styleImage(L.icon.uri) : null;
        const fill = n.fill || st.fill, stroke = n.stroke || st.stroke, color = t.box.text;
        if (n.type === 'equip' || (im && L.icon && L.text && L.text.cy > L.icon.y + L.icon.h)) {
          /* 图标在上、文字在下：容器框（noBox 时透明）+ 图片样式标签 */
          const boxed = !n.noBox || (n.status && n.status !== 'base');
          const sty = im ? `shape=label;image=${im};imageWidth=${r1(L.icon.w)};imageHeight=${r1(L.icon.h)};imageAlign=center;imageVerticalAlign=top;spacingTop=${r1(L.icon.y - n.y)};verticalAlign=bottom;spacingBottom=4;` : '';
          cell(cid(n.id), code(n) + txt, `${sty}rounded=1;arcSize=8;${font};fillColor=${boxed ? fill : 'none'};strokeColor=${boxed ? stroke : 'none'};fontColor=${color}${bold}`, geo, pid, ht);
        } else {
          const shp = SHAPE_OUT[n.type] || SHAPE_OUT.rect;
          const sty = im ? `shape=label;image=${im};imageWidth=${r1(L.icon.w)};imageHeight=${r1(L.icon.h)};imageAlign=left;spacingLeft=${r1(L.icon.w + 4)};` : '';
          cell(cid(n.id), code(n) + txt, `${im ? sty + 'rounded=0' : shp};${font};fillColor=${fill};strokeColor=${stroke};fontColor=${color};strokeWidth=1.2${bold}${n.align === 'left' ? ';align=left' : ''}`, geo, pid, ht);
        }
      }
    }
    for (const l of p.links) {
      if (!ids.has(cid(l.from)) || !ids.has(cid(l.to))) continue;
      const K = LINK_KINDS[l.kind] || LINK_KINDS.plain, c = t.link[l.kind] || t.link.plain;
      const end = l.dir === 'none' ? 'endArrow=none' : 'endArrow=block;endFill=1;endSize=7', start = l.dir === 'both' ? 'startArrow=block;startFill=1;startSize=7' : 'startArrow=none';
      const pts = (typeof linkPoints === 'function' ? linkPoints(l, p) : null) || [];
      const way = pts.length > 2 ? `<Array as="points">${pts.slice(1, -1).map(q => `<mxPoint x="${r1(q.x)}" y="${r1(q.y)}"/>`).join('')}</Array>` : '';
      let label = (typeof linkText === 'function' ? linkText(l, p) : l.label) || '';
      const ht = { ht_kind: l.kind, ht_dir: l.dir, ht_code: l.code, ht_attrs: l.attrs && Object.keys(l.attrs).length ? l.attrs : '' };
      if ((typeof linkDir === 'function' ? linkDir(l) : l.dir) === 'both' && l.labelBack) {
        ht.ht_labelBack = l.labelBack;
        label = label ? label + ' ⇄ ' + l.labelBack : l.labelBack;
      }
      const style = `edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;fontSize=11;fontFamily=Microsoft YaHei;labelBackgroundColor=${t.bg};${end};${start};strokeColor=${c};fontColor=${c};strokeWidth=${K.w || 1.6};${DASH[K.dash] || ''}`;
      out.push(`<UserObject label="${xa(label)}" id="e${l.id}"${meta(ht)}><mxCell style="${xa(style)}" edge="1" parent="1" source="${cid(l.from)}" target="${cid(l.to)}"><mxGeometry relative="1" as="geometry">${way}</mxGeometry></mxCell></UserObject>`);
    }
    const b = contentBBox(p);
    return { xml: `<mxGraphModel dx="${Math.round(b.w)}" dy="${Math.round(b.h)}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="${Math.round(b.w + 80)}" pageHeight="${Math.round(b.h + 80)}" background="${t.bg}" math="0" shadow="0"><root>${rootCell(p)}<mxCell id="1" parent="0"/>${out.join('')}</root></mxGraphModel>` };
  }
  function exportString(pageList) {
    const pages = pageList && pageList.length ? pageList : pagesInOrder(), pageIds = {}, saved = cur;
    pages.forEach((p, i) => pageIds[p.id] = 'ht-' + (p.id === 'root' ? 'root' : p.id));
    let body = '';
    try {
      for (const p of pages) { cur = p.id; body += `<diagram id="${xa(pageIds[p.id])}" name="${xa(p.name || '页面')}">${pageXML(p, pageIds).xml}</diagram>`; }
    } finally { cur = saved; }
    return `<?xml version="1.0" encoding="UTF-8"?>\n<mxfile host="jingwei" agent="经纬织图" version="24.0.0" type="device" pages="${pages.length}">${body}</mxfile>\n`;
  }
  async function exportFile(pageList) {
    toast('正在生成 draw.io 文件…');
    const s = exportString(pageList);
    await saveFile(docExportName('drawio'), new Blob([s], { type: 'application/xml' }));
  }

  /* ================= 导入 ================= */
  async function inflateRaw(bytes) {
    if (typeof DecompressionStream === 'function') {
      try { const ds = new DecompressionStream('deflate-raw'); const s = new Blob([bytes]).stream().pipeThrough(ds); return new Uint8Array(await new Response(s).arrayBuffer()); } catch (_) { }
    }
    return tinf(bytes);
  }
  /* 纯 JS 的 raw inflate（RFC 1951），供不支持 DecompressionStream('deflate-raw') 的旧浏览器使用 */
  function tinf(src) {
    let pos = 0, bit = 0, cnt = 0, out = new Uint8Array(Math.max(1024, src.length * 4)), op = 0;
    const need = n => { if (op + n > out.length) { const o = new Uint8Array(Math.max(out.length * 2, op + n)); o.set(out); out = o; } };
    const bits = n => { while (cnt < n) { if (pos >= src.length) throw new Error('压缩数据不完整'); bit |= src[pos++] << cnt; cnt += 8; } const v = bit & ((1 << n) - 1); bit >>>= n; cnt -= n; return v; };
    const build = lens => { const counts = new Uint16Array(16), offs = new Uint16Array(16), sym = new Uint16Array(lens.length); for (const l of lens) counts[l]++; counts[0] = 0; for (let i = 1; i < 16; i++) offs[i] = offs[i - 1] + counts[i - 1]; lens.forEach((l, i) => { if (l) sym[offs[l]++] = i; }); return { counts, sym }; };
    const decode = h => { let code = 0, first = 0, index = 0; for (let len = 1; len < 16; len++) { code |= bits(1); const c = h.counts[len]; if (code - c < first) return h.sym[index + (code - first)]; index += c; first += c; first <<= 1; code <<= 1; } throw new Error('压缩数据损坏'); };
    const LB = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258], LE = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0];
    const DB = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577], DE = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13];
    let fixL = null, fixD = null;
    const inflateBlock = (lh, dh) => {
      for (;;) {
        const s = decode(lh);
        if (s < 256) { need(1); out[op++] = s; continue; }
        if (s === 256) return;
        const li = s - 257, len = LB[li] + bits(LE[li]), di = decode(dh), dist = DB[di] + bits(DE[di]);
        need(len); for (let i = 0; i < len; i++, op++) out[op] = out[op - dist];
      }
    };
    let last = 0;
    do {
      last = bits(1); const type = bits(2);
      if (type === 0) { bit = 0; cnt = 0; const len = src[pos] | (src[pos + 1] << 8); pos += 4; need(len); out.set(src.subarray(pos, pos + len), op); op += len; pos += len; }
      else if (type === 1) {
        if (!fixL) { const l = new Array(288); for (let i = 0; i < 288; i++) l[i] = i < 144 ? 8 : i < 256 ? 9 : i < 280 ? 7 : 8; fixL = build(l); fixD = build(new Array(30).fill(5)); }
        inflateBlock(fixL, fixD);
      } else if (type === 2) {
        const hl = bits(5) + 257, hd = bits(5) + 1, hc = bits(4) + 4, ORD = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15], cl = new Array(19).fill(0);
        for (let i = 0; i < hc; i++) cl[ORD[i]] = bits(3);
        const ch = build(cl), lens = [];
        while (lens.length < hl + hd) { const sy = decode(ch); if (sy < 16) lens.push(sy); else if (sy === 16) { const p = lens[lens.length - 1], r = 3 + bits(2); for (let i = 0; i < r; i++) lens.push(p); } else { const r = sy === 17 ? 3 + bits(3) : 11 + bits(7); for (let i = 0; i < r; i++) lens.push(0); } }
        inflateBlock(build(lens.slice(0, hl)), build(lens.slice(hl)));
      } else throw new Error('压缩数据损坏');
    } while (!last);
    return out.subarray(0, op);
  }
  async function decodeDiagram(el) {
    const m = el.getElementsByTagName('mxGraphModel')[0];
    if (m) return m;
    const raw = (el.textContent || '').trim(); if (!raw) return null;
    const bin = Uint8Array.from(atob(raw), c => c.charCodeAt(0));
    const txt = new TextDecoder().decode(await inflateRaw(bin));
    const xml = decodeURIComponent(txt);
    return new DOMParser().parseFromString(xml, 'application/xml').documentElement;
  }
  function parseStyle(s) {
    const o = {}; String(s || '').split(';').forEach((kv, i) => { if (!kv) return; const j = kv.indexOf('='); if (j < 0) o[kv] = i === 0 ? '__first' : '1'; else o[kv.slice(0, j)] = kv.slice(j + 1); });
    return o;
  }
  function htmlText(v, isHtml) {
    if (v == null) return '';
    let s = String(v);
    if (isHtml || /<[a-z][\s\S]*>/i.test(s)) {
      s = s.replace(/<br\s*\/?>/gi, '\n').replace(/<(div|p|li|h\d)\b[^>]*>/gi, '\n').replace(/<\/(div|p|li|h\d)>/gi, '\n').replace(/<[^>]+>/g, '');
      const ta = document.createElement('textarea'); ta.innerHTML = s; s = ta.value;
    }
    return s.replace(/ /g, ' ').replace(/\n{2,}/g, '\n').trim();
  }
  const SHAPE_IN = [
    [/basic\.rect(?=.*topLeftStyle=rounded)(?=.*bottomLeftStyle=rounded)(?!.*(topRight|bottomRight)Style=rounded)/, 'roundL'], [/basic\.rect(?=.*topRightStyle=rounded)(?=.*bottomRightStyle=rounded)(?!.*(topLeft|bottomLeft)Style=rounded)/, 'roundR'],
    [/^swimlane$|shape=swimlane/, 'swimlane'], [/shape=cylinder|cylinder3/, 'cylinder'], [/shape=cloud/, 'cloud'], [/doubleEllipse/, 'donut'], [/^ellipse|shape=ellipse/, 'ellipse'],
    [/^rhombus|shape=rhombus/, 'diamond'], [/shape=hexagon/, 'hexagon'], [/shape=document/, 'document'], [/^triangle|shape=triangle/, 'triangle'], [/shape=parallelogram/, 'parallelogram'],
    [/shape=trapezoid/, 'trapezoid'], [/shape=cube/, 'cube'], [/shape=process/, 'predef'], [/shape=display/, 'display'], [/shape=step/, 'chevron'], [/shape=cross/, 'plus'],
    [/shape=callout/, 'callout'], [/shape=singleArrow/, 'arrowR'], [/shape=doubleArrow/, 'arrowLR'], [/octagon/, 'octagon'], [/pentagon/, 'pentagon'], [/basic\.star/, 'star'],
  ];
  const DEF_COLORS = /^(none|default|#ffffff|#FFFFFF|#000000|#dae8fc|#6c8ebf)$/;
  async function importText(text, opts = {}) {
    const dom = new DOMParser().parseFromString(text, 'application/xml');
    if (dom.getElementsByTagName('parsererror').length) throw new Error('不是有效的 draw.io 文件');
    let diags = [...dom.getElementsByTagName('diagram')];
    const single = !diags.length && dom.getElementsByTagName('mxGraphModel')[0];
    const pages = [], custom = {}, warnings = [], idMap = {}; let docSettings = null;
    const imgKey = new Map();
    const addImg = (uri, name) => {
      if (imgKey.has(uri)) return imgKey.get(uri);
      const id = uid(); custom[id] = { name: name || '导入图片', uri }; imgKey.set(uri, 'cu:' + id); return 'cu:' + id;
    };
    const fixImg = s => { if (!s) return null; let m = s.match(/^data:image\/svg\+xml,(.*)$/); if (m) return 'data:image/svg+xml;base64,' + m[1]; m = s.match(/^data:(image\/[\w.+-]+),(.*)$/); if (m) return `data:${m[1]};base64,${m[2]}`; return /^data:/.test(s) ? s : null; };
    const list = single ? [{ name: '总图', model: single, id: 'single' }] : [];
    for (const d of diags) { try { list.push({ name: d.getAttribute('name') || '页面', model: await decodeDiagram(d), id: d.getAttribute('id') }); } catch (e) { warnings.push(`页面“${d.getAttribute('name')}”无法解码：${e.message || e}`); } }
    list.forEach((d, i) => { idMap[d.id] = (i === 0 && opts.rootFirst !== false) ? 'root' : 'p' + uid(); });
    for (const d of list) {
      if (!d.model) continue;
      const rootEl = d.model.getElementsByTagName('root')[0]; if (!rootEl) continue;
      const cells = [];
      for (const el of rootEl.children) {
        let c = el, data = {};
        if (el.tagName !== 'mxCell') { c = el.getElementsByTagName('mxCell')[0]; if (!c) continue; for (const a of el.attributes) data[a.name] = a.value; }
        else for (const a of el.attributes) if (a.name === 'value') data.label = a.value;
        const g = c.getElementsByTagName('mxGeometry')[0];
        const geo = g ? { x: +g.getAttribute('x') || 0, y: +g.getAttribute('y') || 0, w: +g.getAttribute('width') || 0, h: +g.getAttribute('height') || 0, rel: g.getAttribute('relative') === '1' } : null;
        const pts = g ? [...g.getElementsByTagName('mxPoint')].map(p => ({ x: +p.getAttribute('x') || 0, y: +p.getAttribute('y') || 0, as: p.getAttribute('as') })) : [];
        cells.push({ id: data.id || c.getAttribute('id'), parent: c.getAttribute('parent'), vertex: c.getAttribute('vertex') === '1', edge: c.getAttribute('edge') === '1', source: c.getAttribute('source'), target: c.getAttribute('target'), style: c.getAttribute('style') || '', label: data.label != null ? data.label : c.getAttribute('value'), data, geo, pts });
      }
      const byId = new Map(cells.map(c => [c.id, c]));
      const rc = cells.find(c => c.id === '0' && !c.parent);
      const layers = new Set(cells.filter(c => !c.vertex && !c.edge).map(c => c.id));
      /* 绝对坐标：沿父链累加（图层不计） */
      const absOf = c => { let x = c.geo ? c.geo.x : 0, y = c.geo ? c.geo.y : 0, p = byId.get(c.parent), k = 0; while (p && !layers.has(p.id) && k++ < 30) { if (p.vertex && p.geo && !p.geo.rel) { x += p.geo.x; y += p.geo.y; } p = byId.get(p.parent); } return { x, y }; };
      const page = { id: idMap[d.id], name: d.name, nodes: [], links: [], view: (rc && rc.data.ht_view) || null };
      if (rc && rc.data.ht_doc && !docSettings) try { docSettings = JSON.parse(rc.data.ht_doc); } catch (_) { }
      const nodeOf = new Map();
      const verts = cells.filter(c => c.vertex && c.geo && !c.geo.rel);
      /* 边标签单元（父为连线） */
      const edgeLabels = new Map();
      for (const c of cells) if (c.vertex && byId.get(c.parent)?.edge) { const t = htmlText(c.label, true); if (t) edgeLabels.set(c.parent, (edgeLabels.get(c.parent) ? edgeLabels.get(c.parent) + ' ' : '') + t); }
      const transparentGroup = c => /^group(;|$)/.test(c.style) || (/(^|;)group=1/.test(c.style));
      for (const c of verts) {
        if (byId.get(c.parent)?.edge) continue;
        if (c.data.ht_part === 'title') continue;
        const st = parseStyle(c.style), a = absOf(c), D = c.data;
        if (transparentGroup(c) && !D.ht_type) continue;
        let text = htmlText(c.label, st.html === '1');
        if (D.ht_type === 'band') { const strip = cells.find(x => x.parent === c.id && x.data.ht_part === 'title'); const sv = strip ? htmlText(strip.label, true).replace(/\s/g, '') : null, ns = x => String(x || '').replace(/\s/g, ''); text = sv == null ? (D.ht_text || text) : (D.ht_text != null && (sv === ns(D.ht_text) || sv === ns((D.ht_code || '') + D.ht_text)) ? D.ht_text : sv); }
        let type = D.ht_type || null;
        const first = Object.keys(st).find(k => st[k] === '__first') || '';
        const shapeStr = (first ? first + ';' : '') + (st.shape ? 'shape=' + st.shape : '');
        let kind = 'rect';
        for (const [re, k] of SHAPE_IN) if (re.test(first) || re.test(shapeStr) || re.test(c.style)) { kind = k; break; }
        if (!type) {
          if (kind === 'swimlane' || st.container === '1') type = '__cont';
          else if (first === 'text' || (st.strokeColor === 'none' && (st.fillColor === 'none' || !st.fillColor) && !st.image && st.shape !== 'image')) type = 'text';
          else if (st.shape === 'image' || first === 'image') type = 'equip';
          else if (st.rounded === '1' && kind === 'rect') type = (+st.arcSize >= 40 ? 'terminator' : 'round');
          else type = kind;
        }
        const n = mkNode({ type, x: a.x, y: a.y, w: c.geo.w || 120, h: c.geo.h || 40, text, size: Math.max(8, Math.min(40, +(D.ht_size || st.fontSize) || 13)), bold: (+st.fontStyle & 1) === 1 });
        n._c = c; n._horiz = st.horizontal !== '0';
        if (D.ht_status) n.status = D.ht_status;
        if (D.ht_etype) n.etype = D.ht_etype; if (D.ht_code) n.code = D.ht_code;
        if (D.ht_attrs) try { n.attrs = JSON.parse(D.ht_attrs); } catch (_) { }
        if (D.ht_role) n.role = D.ht_role; if (D.ht_noBox) n.noBox = true; if (D.ht_titleW) n.titleW = +D.ht_titleW;
        if (D.link && /^data:page\/id,/.test(D.link)) n._sub = D.link.slice(13);
        /* 导出时若显示编号，标签为“编号 + 空格 + 文字”；导回时去掉前缀（与当前文档是否显示编号无关） */
        if (D.ht_code && new RegExp('^' + D.ht_code.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[\\s　]+').test(n.text)) n.text = n.text.replace(new RegExp('^' + D.ht_code.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[\\s　]+'), '');
        /* 图标 */
        if (D.ht_icon && /^(lib|ms):/.test(D.ht_icon)) n.icon = D.ht_icon;
        else { const im = fixImg(st.image); if (im) { n.icon = addImg(im, text || '导入图片'); try { const asp = c.geo.w && c.geo.h ? c.geo.w / c.geo.h : 1; if (st.shape === 'image' && Math.abs(asp - 1) > 0.15) custom[n.icon.slice(3)].aspect = +asp.toFixed(3); } catch (_) { } } }
        if (type === 'equip') { n.noBox = n.noBox || st.fillColor === 'none' || st.shape === 'image'; if (st.shape === 'image' && st.verticalLabelPosition === 'bottom') n.h += 20; n.size = Math.min(n.size, 12); }
        if (type === 'legend' || type === 'tblock') { n.icon = null; }
        if (opts.keepColors !== false && !D.ht_type && !['__cont', 'text'].includes(type)) {
          if (st.fillColor && !DEF_COLORS.test(st.fillColor)) n.fill = st.fillColor;
          if (st.strokeColor && !DEF_COLORS.test(st.strokeColor)) n.stroke = st.strokeColor;
        }
        nodeOf.set(c.id, n); page.nodes.push(n);
      }
      /* 父子：沿 draw.io 父链找到最近的已导入单元（透明 group 跳过） */
      for (const n of page.nodes) {
        let p = byId.get(n._c.parent), k = 0;
        while (p && !nodeOf.has(p.id) && !layers.has(p.id) && k++ < 30) p = byId.get(p.parent);
        if (p && nodeOf.has(p.id)) n.parent = nodeOf.get(p.id).id;
      }
      /* 未写 ht_type 的容器：顶层竖排泳道 → 分组带；其内竖排泳道 → 层；其余 → 容器 */
      const tops = page.nodes.filter(n => n.type === '__cont' && !n.parent);
      const W = Math.max(1, ...page.nodes.map(n => n.x + n.w)) - Math.min(0, ...page.nodes.map(n => n.x));
      for (const n of page.nodes) if (n.type === '__cont') {
        const pa = n.parent && page.nodes.find(x => x.id === n.parent);
        if (!pa && !n._horiz && (tops.length > 1 || n.w > W * 0.6)) n.type = 'band';
        else if (pa && !n._horiz && n.w >= pa.w * 0.7) n.type = 'lane';
        else n.type = 'group';
      }
      /* 文字：最大号的顶部文字作标题 */
      if (!page.nodes.some(n => n.role === 'title')) {
        const tx = page.nodes.filter(n => n.type === 'text' && !n.parent).sort((a, b) => b.size - a.size || a.y - b.y)[0];
        if (tx && tx.size >= 16) tx.role = 'title';
      }
      /* 连线 */
      const vById = new Map(page.nodes.map(n => [n._c.id, n]));
      const nearest = (pt) => { let best = null, bd = 40; for (const n of page.nodes) { if (['text', 'legend', 'tblock', 'note'].includes(n.type)) continue; const dx = Math.max(n.x - pt.x, 0, pt.x - n.x - n.w), dy = Math.max(n.y - pt.y, 0, pt.y - n.y - n.h); const dd = Math.hypot(dx, dy) + (['band', 'lane', 'group'].includes(n.type) ? 25 : 0); if (dd < bd) { bd = dd; best = n; } } return best; };
      for (const c of cells.filter(c => c.edge)) {
        const st = parseStyle(c.style), D = c.data;
        let a = vById.get(c.source), b = vById.get(c.target);
        const sp = c.pts.find(p => p.as === 'sourcePoint'), tp = c.pts.find(p => p.as === 'targetPoint');
        const pa = byId.get(c.parent), off = pa && pa.vertex ? absOf(pa) : { x: 0, y: 0 };
        if (!a && sp) a = nearest({ x: sp.x + off.x, y: sp.y + off.y });
        if (!b && tp) b = nearest({ x: tp.x + off.x, y: tp.y + off.y });
        if (!a || !b || a === b) { warnings.push(`连线“${htmlText(c.label, true) || c.id}”缺少端点，已忽略`); continue; }
        const endA = st.endArrow == null ? 'classic' : st.endArrow, startA = st.startArrow || 'none';
        const he = endA !== 'none' && endA !== '', hs = startA !== 'none' && startA !== '';
        let from = a, to = b, dir = he && hs ? 'both' : (he || hs) ? 'one' : 'none';
        if (!he && hs) { from = b; to = a; }
        let kind = D.ht_kind || (st.dashed === '1' ? (/^\s*[1-3]\s/.test(st.dashPattern || '') ? 'radio' : 'ctrl') : (+st.strokeWidth >= 2.2 ? 'wired' : 'data'));
        let lab = htmlText(c.label, st.html === '1') || edgeLabels.get(c.id) || '';
        let labelBack = '';
        if (D.ht_labelBack) {
          labelBack = String(D.ht_labelBack);
          const suf = ' ⇄ ' + labelBack;
          if (lab.endsWith(suf)) lab = lab.slice(0, lab.length - suf.length);
          else if (lab === labelBack) lab = '';
        }
        const lk = { id: uid(), from: from.id, to: to.id, dir: D.ht_dir || dir, kind, route: 'ortho', label: lab };
        if (labelBack) lk.labelBack = labelBack;
        if (D.ht_code) { lk.code = D.ht_code; if (lk.label.startsWith(D.ht_code)) lk.label = lk.label.slice(D.ht_code.length).replace(/^[\s　]+/, ''); }
        if (D.ht_attrs) try { lk.attrs = JSON.parse(D.ht_attrs); } catch (_) { }
        page.links.push(lk);
      }
      for (const n of page.nodes) { n.x = snapv(n.x); n.y = snapv(n.y); }
      pages.push(page);
    }
    /* 页面链接 → 下钻 */
    for (const p of pages) for (const n of p.nodes) { if (n._sub && idMap[n._sub]) n.sub = idMap[n._sub]; delete n._sub; delete n._c; delete n._horiz; }
    if (!pages.length) throw new Error('文件中没有可识别的页面');
    return { pages, custom, warnings, source: 'drawio', docSettings };
  }
  async function fromFile(f) { return importText(await f.text()); }

  window.DrawIO = { exportString, exportFile, importText, fromFile, parseStyle, _tinf: tinf };
})();
