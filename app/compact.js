/* ============ 织图 · 紧凑排版与报告版心（排版密度） ============
 * doc.layout = { mode:'standard'|'compact'|'report', page:'a4p'|'a4l'|'ppt', font:10.5 }
 * 缺省 mode 为 compact。文件里已有的 mode 优先；没有时用 localStorage 的 hongtu.layout。
 *  · standard：原有一键美化（铺满整幅宽度）。
 *  · compact ：条目按自然宽度紧挨排列、装备卡缩小、层标题收窄，图宽随内容收缩。
 *  · report  ：在紧凑基础上，按“报告版心宽度 × 目标字号”反推图宽，条目自动折行；
 *              导出“报告插图 PNG”时写入 DPI，插入 Word／WPS 后恰为版心宽，图内正文即为所选字号。
 * 覆盖全局 beautify()（文字成图、参照生成、模板等调用处自动生效）。依赖 app.js 全局。 */
(function () {
  'use strict';
  const PAGES = {
    a4p: { name: 'A4 竖版', cm: 15.5, hint: '版心宽 15.5 cm' },
    a4l: { name: 'A4 横版', cm: 24.7, hint: '版心宽 24.7 cm' },
    ppt: { name: 'PPT 宽屏', cm: 31.0, hint: '幻灯片内容区宽 31 cm' },
  };
  const FONTS = [[14, '四号（14 pt）'], [12, '小四（12 pt）'], [10.5, '五号（10.5 pt）'], [9, '小五（9 pt）']];
  const MODES = {
    standard: { label: '标准', toast: '已切换为标准排版' },
    compact: { label: '紧凑', toast: '已切换为紧凑排版' },
    report: { label: '报告版心' },
  };
  const FACTORY = { mode: 'compact', page: 'a4p', font: 10.5 };
  if (!MODES[FACTORY.mode] || !PAGES[FACTORY.page] || !(FACTORY.font > 0)) throw new Error('bad factory layout');
  const PREF_KEY = 'hongtu.layout';
  const BASE = 13;          /* 画布上框内正文字号（px） */
  const PAD = 24;           /* exportSVGString 的留白 */
  const G = { gap: 14, gapL: 30, vgap: 10, vgapL: 30, eqW: 88, boxMinW: 60, boxMaxW: 168 };
  function plainLayout(v) {
    if (!v || typeof v !== 'object' || Array.isArray(v)) return null;
    return v;
  }
  function readPref() {
    try { return plainLayout(JSON.parse(localStorage.getItem(PREF_KEY) || 'null')); }
    catch (_) { return null; }
  }
  function writePref(layout) {
    try { localStorage.setItem(PREF_KEY, JSON.stringify({ mode: layout.mode, page: layout.page, font: layout.font })); }
    catch (_) { }
  }
  function modeOf(L) { return L && MODES[L.mode] ? L.mode : ''; }
  function pageOf(L) { return L && PAGES[L.page] ? L.page : ''; }
  function fontOf(L) { const f = L && L.font; return typeof f === 'number' && isFinite(f) && f > 0 ? f : 0; }
  function cfg(d) {
    const src = d && typeof d === 'object' ? d : doc;
    const file = plainLayout(src && src.layout);
    const pref = readPref();
    return {
      mode: modeOf(file) || modeOf(pref) || FACTORY.mode,
      page: pageOf(file) || pageOf(pref) || FACTORY.page,
      font: fontOf(file) || fontOf(pref) || FACTORY.font,
    };
  }
  function adopt(layout) {
    doc.layout = { mode: layout.mode, page: layout.page, font: layout.font };
    return doc.layout;
  }
  const ptOf = cm => cm / 2.54 * 72;
  /* 报告模式下的总图宽（px，不含导出留白）：版心宽(pt) × 13px ÷ 目标字号(pt) */
  function targetW(c = cfg()) { return snapv(ptOf(PAGES[c.page].cm) * BASE / c.font - PAD * 2); }
  const fontAt = (wpx, cm) => +(BASE * ptOf(cm) / (wpx + PAD * 2)).toFixed(1);

  const lineH = s => Math.round(s * 1.38);
  const order = list => list.slice().sort((a, b) => (Math.round((a.y + a.h / 2) / 24) - Math.round((b.y + b.h / 2) / 24)) || a.x - b.x);
  const SHAPED = ['ellipse', 'diamond', 'hexagon', 'octagon', 'cylinder', 'cloud', 'document', 'parallelogram', 'trapezoid', 'cube', 'callout', 'display', 'predef', 'chevron', 'homeplate', 'pentagon', 'triangle', 'star', 'donut', 'plus', 'delay'];

  /* ---------- 自然尺寸（avail = 可用宽度） ---------- */
  function natural(n, avail, p) {
    if (isCont(n)) return groupNatural(n, avail, p);
    if (n.type === 'text' || n.type === 'note' || n.type === 'legend' || n.type === 'tblock') return { w: Math.min(n.w, avail), h: n.h };
    const size = n.size || BASE;
    if (n.type === 'equip') {
      const asp = typeof iconAspect === 'function' ? iconAspect(n.icon) : 1;
      const iw = asp > 1.05 ? Math.min(52 * asp, 200) : 52;
      const w = Math.min(avail, Math.max(G.eqW, iw + 12));
      const lines = n.text ? wrap(n.text, w - 8, size, n.bold).length : 0;
      return { w, h: snapv(52 + 14 + lines * lineH(size) + (lines ? 4 : 0)) };
    }
    const hasIcon = !!(n.icon && (typeof iconURI !== 'function' || iconURI(n.icon)));
    const extra = hasIcon ? 30 : 0;
    const lines0 = String(n.text || '').split('\n');
    const tw = Math.max(...lines0.map(s => measure(s, size, n.bold)), 0);
    if (SHAPED.includes(n.type)) {
      const r = n.h && n.w ? n.h / n.w : 0.5, k = n.type === 'diamond' ? 1.7 : n.type === 'ellipse' || n.type === 'cloud' ? 1.45 : 1.2;
      const w = clamp(snapv(tw * k + 28 + extra), 72, Math.min(220, avail));
      const lines = wrap(n.text, w / k - 6, size, n.bold).length;
      return { w, h: snapv(Math.max(40, Math.min(110, w * r), lines * lineH(size) * (k > 1.3 ? 1.8 : 1.3) + 14)) };
    }
    const w = clamp(snapv(tw + 22 + extra), G.boxMinW, Math.min(G.boxMaxW, avail));
    const lines = wrap(n.text, w - 10 - extra, size, n.bold).length;
    return { w, h: snapv(Math.max(32, lines * lineH(size) + 12)) };
  }
  function groupNatural(g, avail, p) {
    const eat = contEat(g);
    const ks = order(kids(g.id, p));
    const tg = codeTagOf(g, p), titleW = measure(firstLineOf(g.text), 12.5, true) + 24 + (tg ? tg.w + 8 : 0);
    if (!ks.length) return { w: Math.min(avail, Math.max(120, titleW) + eat.x), h: eat.y + 36, flow: null };
    const inner = Math.max(60, avail - 16 - eat.x);
    const fl = flow(ks, inner, g.links, p);
    return { w: Math.min(avail, Math.max(fl.w + 16, titleW) + eat.x), h: eat.y + 8 + fl.h + 8, flow: fl };
  }
  const firstLineOf = s => String(s || '').split('\n')[0];

  /* ---------- 流式排布：贪心折行 ---------- */
  /* 相邻两项之间有带标签的连线时，间距放宽到能放下标签（避免标签压在框上） */
  function pairGap(a, b, base, p) {
    if (!a || !p || !p.links) return base;
    let g = base;
    for (const l of p.links) {
      if (!((l.from === a.id && l.to === b.id) || (l.from === b.id && l.to === a.id))) continue;
      const w = linkLabelWidth(l, p); if (w) g = Math.max(g, w + 14);
    }
    return g;
  }
  function flow(items, avail, linked, p) {
    const gap = linked ? G.gapL : G.gap, vgap = linked ? G.vgapL : G.vgap;
    const lines = []; let cur = null;
    for (const n of items) {
      const s = natural(n, avail, p);
      const prev = cur && cur.items.length ? cur.items[cur.items.length - 1].n : null, g = prev ? pairGap(prev, n, gap, p) : gap;
      if (!cur || (cur.items.length && cur.w + g + s.w > avail)) { cur = { items: [], w: 0, h: 0 }; lines.push(cur); }
      const gg = cur.items.length ? g : 0;
      cur.w += gg + s.w; cur.h = Math.max(cur.h, s.h); cur.items.push({ n, s, g: gg });
    }
    const w = Math.max(0, ...lines.map(l => l.w)), h = lines.reduce((a, l) => a + l.h, 0) + vgap * Math.max(0, lines.length - 1);
    return { lines, w, h, gap, vgap };
  }
  function place(fl, x0, y0, availW, p) {
    let y = y0;
    for (const ln of fl.lines) {
      let x = x0 + (availW - ln.w) / 2;
      for (const { n, s, g } of ln.items) {
        x += g || 0;
        const nx = snapv(x), ny = snapv(y + (ln.h - s.h) / 2);
        if (isCont(n)) placeGroup(n, nx, snapv(y), s.w, ln.h, s.flow, p);
        else { n.x = nx; n.y = ny; n.w = snapv(s.w); n.h = snapv(s.h); }
        x += s.w;
      }
      y += ln.h + fl.vgap;
    }
  }
  function placeGroup(g, x, y, w, h, fl, p) {
    g.x = x; g.y = y; g.w = snapv(w); g.h = snapv(h);
    if (!fl) return;
    const box = contFrame(g).content;
    place(fl, box.x + 8, box.y + 8 + Math.max(0, (box.h - 16 - fl.h) / 2), box.w - 16, p);
  }

  /* ---------- 层与分组带 ---------- */
  function laneTitleW(l) {
    const t = firstLineOf(l.text), w = measure(t, 13.5, true) + 22;
    return snapv(clamp(w, 60, 96));
  }
  function layoutLaneC(l, p) {
    const row = contRow(l), side = sideOf(l);
    if (row && row.thick.fit && row.thick.fit.sides.indexOf(side) >= 0) l.titleW = laneTitleW(l);
    const ks = order(kids(l.id, p));
    if (!ks.length) { l.h = Math.max(l.h, 44); return; }
    const box0 = contFrame(l).content, aw = box0.w - 16;
    const fl = flow(ks, aw, l.links, p);
    if (side === 'l' || side === 'r') {
      const tw = thickness(l, row);
      const tl = wrap(l.text, tw - 12, row.size, row.bold).length * lineH(row.size) + 12;
      l.h = snapv(Math.max(44, fl.h + 14, tl));
    } else l.h = snapv(Math.max(thickness(l, row) + fl.h + 14, 44));
    const box = contFrame(l).content;
    place(fl, box.x + 8, box.y + (box.h - fl.h) / 2, box.w - 16, p);
  }
  function layoutBandC(b, p) {
    const ks = kids(b.id, p);
    const lanes = ks.filter(k => { const r = contRow(k); return r && r.layout === 'row'; }).sort((a, c) => a.y - c.y);
    const tiles = ks.filter(k => { const r = contRow(k); return r && r.layout === 'tile'; }).sort((a, c) => a.x - c.x);
    const margins = ks.filter(k => { const r = contRow(k); return r && r.layout === 'margin'; });
    const others = order(ks.filter(k => lanes.indexOf(k) < 0 && tiles.indexOf(k) < 0 && margins.indexOf(k) < 0));
    /* 跨层连线：层间留出连线与标签的位置 */
    const laneOf = id => { let n = nodeById(id, p), k = 0; while (n && n.parent && k++ < 20) { if (n.type === 'lane') return n.id; n = nodeById(n.parent, p); } return n && n.type === 'lane' ? n.id : null; };
    const ids = new Set(lanes.map(l => l.id));
    const cross = p.links.some(l => { const a = laneOf(l.from), c = laneOf(l.to); return a && c && a !== c && ids.has(a) && ids.has(c); });
    const lg = cross ? 22 : 4;
    const box = contFrame(b).content;
    const mw = margins.length ? Math.max(...margins.map(k => k.w)) : 0;
    const mainX = box.x, mainW = box.w - mw;
    let y = box.y + 4;
    for (const l of lanes) { l.x = mainX + 4; l.w = mainW - 8; l.y = snapv(y); layoutLaneC(l, p); y = l.y + l.h + lg; }
    if (lanes.length) y -= lg - 4;
    if (tiles.length) {
      const gap = 8, tw = (mainW - gap * (tiles.length - 1)) / tiles.length, y0 = y;
      let x = mainX, maxH = 0;
      for (const t of tiles) {
        const dx = x - t.x, dy = y0 - t.y;
        t.x = x; t.w = tw; t.y = snapv(y0);
        if (dx || dy) for (const d of descendants(t.id, p)) { d.x += dx; d.y += dy; }
        layoutCont(t, p, { fitTitle: true });
        maxH = Math.max(maxH, t.h); x += tw + gap;
      }
      y = y0 + maxH + 4;
    }
    if (others.length) {
      const aw = mainW - 20, fl = flow(others, aw, b.links, p);
      place(fl, mainX + 10, y + 8, aw, p); y += fl.h + 16;
    }
    for (const m of margins) {
      const nx = box.x + box.w - mw, dx = nx - m.x, dy = box.y - m.y;
      m.x = nx; m.y = box.y; m.h = Math.max(m.h, y - box.y);
      if (dx || dy) for (const d of descendants(m.id, p)) { d.x += dx; d.y += dy; }
      layoutCont(m, p, { fitTitle: true });
    }
    const side = sideOf(b), brow = contRow(b), bot = side === 'b' ? thickness(b, brow) : 0;
    b.h = snapv(Math.max(y - b.y + bot, 40));
    if ((side === 'l' || side === 'r') && brow.minChar != null) {
      const chars = [...String(b.text || '')].filter(c => c.trim()).length;
      b.h = snapv(Math.max(b.h, chars * brow.minChar + brow.minPad));
    }
  }
  /* 一行排下所需宽度（紧凑模式图宽） */
  function needW(b, p) {
    const ks = kids(b.id, p);
    const lanes = ks.filter(k => { const r = contRow(k); return r && r.layout === 'row'; });
    const others = ks.filter(k => lanes.indexOf(k) < 0 && !(contRow(k) && (contRow(k).layout === 'margin' || contRow(k).layout === 'tile')));
    const rowW = (items0, linked) => { const gap = linked ? G.gapL : G.gap, items = order(items0); return items.reduce((a, n, i) => a + natural(n, 4000, p).w + (i ? pairGap(items[i - 1], n, gap, p) : 0), 0); };
    let w = others.length ? rowW(others, b.links) + 20 : 0;
    for (const l of lanes) {
      const tw = (sideOf(l) === 'l' || sideOf(l) === 'r') ? laneTitleW(l) : 0;
      w = Math.max(w, tw + 16 + 8 + rowW(kids(l.id, p), l.links));
    }
    const eat = (sideOf(b) === 'l' || sideOf(b) === 'r') ? thickness(b, contRow(b)) : 0;
    return eat + 8 + w;
  }

  /* ---------- 报告版心：超出版心宽的元素收进版心 ---------- */
  const moveAll = (n, dx, dy, p) => { for (const d of [n, ...descendants(n.id, p)]) { d.x += dx; d.y += dy; } };
  /* 文字类元素按宽度重算高度 */
  function refit(n, w) {
    n.w = snapv(Math.max(40, w));
    if (n.type === 'note' || n.type === 'text') { const sz = n.size || 13, lines = wrap(n.text, n.w - (n.type === 'note' ? 20 : 8), sz, n.bold); n.h = snapv(Math.max(n.type === 'note' ? 32 : 20, lines.length * lineH(sz) + (n.type === 'note' ? 16 : 6))); }
  }
  /* 分层图：层之外、超出版心的顶层元素（说明、图片、旁注等）→ 排到层下方，按版心宽度折行 */
  function fitBelow(p, X, W, skip) {
    const tops = p.nodes.filter(n => !n.parent && n.type !== 'band' && !(contRow(n) && contRow(n).layout === 'inset') && !skip.includes(n) && n.role !== 'title' && n.role !== 'subtitle');
    const bandsB = Math.max(...p.nodes.filter(n => n.type === 'band' && !n.parent).map(b => b.y + b.h));
    if (!tops.some(n => n.x < X - 2 || n.x + n.w > X + W + 2)) return;
    /* 只挪动超出版心的元素：排在现有内容（层、说明、图例、标题栏）下方 */
    const out = n => n.x < X - 2 || n.x + n.w > X + W + 2;
    const below = tops.filter(out).sort((a, b) => (a.y - b.y) || (a.x - b.x));
    const stay = tops.filter(n => !out(n));
    let y = Math.max(bandsB, ...stay.map(n => n.y + n.h)) + 12, row = [], rw = 0, rh = 0;
    const flush = () => { let x = X + (W - rw) / 2; for (const n of row) { moveAll(n, snapv(x) - n.x, snapv(y) - n.y, p); x += n.w + 12; } y += rh + 10; row = []; rw = 0; rh = 0; };
    for (const n of below) {
      if (n.w > W) { if (n.type === 'equip' || n.icon) { const k = W / n.w; n.w = snapv(W); n.h = snapv(n.h * k); } else refit(n, W); }
      if (n.type === 'note' && n.role === 'note') refit(n, W);
      if (row.length && rw + 12 + n.w > W) flush();
      rw += (row.length ? 12 : 0) + n.w; rh = Math.max(rh, n.h); row.push(n);
    }
    if (row.length) flush();
  }
  /* 无分层的自由图（流程图等）：整体按比例收进版心宽，框宽同比缩小、文字自动折行，行距随框高顺延 */
  function fitFree(p, W) {
    const items = p.nodes.filter(n => !n.parent && n.type !== 'band' && !(contRow(n) && contRow(n).layout === 'inset') && !n.role && n.type !== 'legend' && n.type !== 'note' && n.type !== 'tblock');
    if (!items.length) return;
    const x0 = Math.min(...items.map(n => n.x)), x1 = Math.max(...items.map(n => n.x + n.w)), W0 = x1 - x0;
    if (W0 > W + 2) {
      const k = W / W0;
      /* 原有行距（行间空白）记下来，缩放后同比收紧 */
      const rows0 = []; for (const n of items.slice().sort((a, b) => a.y - b.y)) { const r = rows0[rows0.length - 1]; if (r && n.y < r.y1 - 4) { r.items.push(n); r.y1 = Math.max(r.y1, n.y + n.h); } else rows0.push({ items: [n], y0: n.y, y1: n.y + n.h }); }
      const gap0 = new Map(); for (let i = 1; i < rows0.length; i++) gap0.set(rows0[i].items[0], rows0[i].y0 - rows0[i - 1].y1);
      for (const n of items) {
        if (isCont(n)) {
          /* 容器：按收窄后的宽度重新流式排布内部条目（自动折行），不做简单缩放 */
          const cx = x0 + (n.x + n.w / 2 - x0) * k, s2 = groupNatural(n, Math.max(120, n.w * k), p);
          if (n.type === 'lane') { const dx = cx - n.w * k / 2 - n.x; moveAll(n, dx, 0, p); n.w = Math.max(160, n.w * k); layoutLaneC(n, p); }
          else placeGroup(n, snapv(cx - s2.w / 2), n.y, s2.w, s2.h, s2.flow, p);
          continue;
        }
        const sub = [n, ...descendants(n.id, p)];
        for (const d of sub) {
          const cx = x0 + (d.x + d.w / 2 - x0) * k;
          if (isCont(d)) { d.x = cx - d.w * k / 2; d.w = d.w * k; continue; }
          const nw = d.type === 'equip' ? Math.max(48, d.w * k) : Math.max(48, d.w * k);
          if (d.type === 'equip') { const r = nw / d.w; d.h = d.h * r; }
          d.w = nw; d.x = cx - nw / 2;
          if (!isCont(d) && d.type !== 'equip' && d.type !== 'text') d.h = Math.max(d.h, leafH(d, d.w));
          if (d.type === 'text') refit(d, d.w);
        }
      }
      /* 框变高后按行顺延，避免上下压叠 */
      const rows = []; for (const n of items.slice().sort((a, b) => a.y - b.y)) { const r = rows[rows.length - 1]; if (r && n.y < r.y1 - 4) { r.items.push(n); r.y1 = Math.max(r.y1, n.y + n.h); } else rows.push({ items: [n], y0: n.y, y1: n.y + n.h }); }
      let shift = 0;
      for (let i = 0; i < rows.length; i++) {
        const r = rows[i]; if (shift) for (const n of r.items) moveAll(n, 0, shift, p);
        r.y0 += shift; r.y1 = Math.max(...r.items.map(n => n.y + n.h));
        const nx = rows[i + 1]; if (nx) { const g0 = nx.items.map(n => gap0.get(n)).find(v => v != null); const want = g0 != null ? Math.max(40, g0 * k) : 24; shift += r.y1 + want - (nx.y0 + shift); }
      }
    }
    const ix0 = Math.min(...items.map(n => n.x)), ix1 = Math.max(...items.map(n => n.x + n.w)), iy0 = Math.min(...items.map(n => n.y)), iy1 = Math.max(...items.map(n => n.y + n.h)), cx = (ix0 + ix1) / 2;
    const title = p.nodes.find(n => !n.parent && n.role === 'title'), sub = p.nodes.find(n => !n.parent && n.role === 'subtitle');
    let ty = iy0 - 20;
    if (sub) { refit(sub, Math.min(W, measure(sub.text, sub.size || 13, sub.bold) + 20)); sub.x = snapv(cx - sub.w / 2); sub.y = snapv(ty - sub.h); ty = sub.y - 4; }
    if (title) { const tw = Math.min(W, measure(title.text, title.size || 22, true) + 24); title.w = snapv(tw); const lines = wrap(title.text, tw - 8, title.size || 22, true); title.h = snapv(Math.max(title.h, lines.length * lineH(title.size || 22) + 6)); title.x = snapv(cx - title.w / 2); title.y = snapv(ty - title.h); }
    /* 说明框通栏、图例靠右（放得下时与说明框并排），标题栏靠右置底 */
    const CW = Math.min(W, Math.max(ix1 - ix0, 320)), X = snapv(cx - CW / 2);
    const below = p.nodes.filter(m => !m.parent && (m.type === 'note' || m.type === 'legend' || m.type === 'tblock') && m.y > iy0 && m.role !== 'title' && m.role !== 'subtitle');
    const note = below.find(m => m.type === 'note'), leg = below.find(m => m.type === 'legend'), tbs = below.filter(m => m.type === 'tblock'), notes = below.filter(m => m.type === 'note' && m !== note);
    let y = iy1 + 16;
    if (leg && typeof legendLayout === 'function') legendLayout(leg, p);
    const side = leg && note && CW - leg.w - 12 >= 260;
    if (leg) { moveAll(leg, snapv(X + CW - leg.w) - leg.x, snapv(y) - leg.y, p); }
    if (note) { refit(note, side ? CW - leg.w - 12 : CW); moveAll(note, X - note.x, snapv(y + (leg && !side ? leg.h + 10 : 0)) - note.y, p); if (side) { note.h = Math.max(note.h, leg.h); leg.h = note.h; } }
    y = Math.max(y, ...[leg, note].filter(Boolean).map(m => m.y + m.h + 10));
    for (const n of notes) { refit(n, CW); moveAll(n, X - n.x, snapv(y) - n.y, p); y += n.h + 10; }
    for (const t of tbs) { if (t.w > CW) t.w = snapv(CW); moveAll(t, snapv(X + CW - t.w) - t.x, snapv(y) - t.y, p); y += t.h + 10; }
  }

  /* ---------- 覆盖一键美化 ---------- */
  const std = window.beautify;
  function beautifyC(p = P()) {
    const c = cfg();
    if (c.mode === 'standard') return std(p);
    return pack(p, c);
  }
  function pack(p, c) {
    const saved = cur; cur = p.id;
    try {
      normalizeImported(p);
      const bands0 = p.nodes.filter(n => n.type === 'band' && !n.parent), oldBottom = bands0.length ? Math.max(...bands0.map(b => b.y + b.h)) : null;
      for (const l of p.links) { const a = nodeById(l.from, p), b = nodeById(l.to, p); if (a && b && a.parent === b.parent && a.parent) { const par = nodeById(a.parent, p); if (par) par.links = true; } }
      const bands = p.nodes.filter(n => n.type === 'band' && !n.parent).sort((a, b) => a.y - b.y);
      const free = p.nodes.filter(n => !n.parent && !isCont(n));
      if (bands.length) {
        const X = Math.min(...bands.map(b => b.x));
        const W = c.mode === 'report' ? targetW(c) : snapv(clamp(Math.max(...bands.map(b => needW(b, p))), 480, 2400));
        const topOf = id => { let n = nodeById(id, p); while (n && n.parent) n = nodeById(n.parent, p); return n && n.id; };
        const bgap = p.links.some(l => topOf(l.from) !== topOf(l.to)) ? 30 : 8;
        let y = bands[0].y;
        for (const b of bands) {
          const dx = X - b.x, dy = y - b.y;
          for (const d of descendants(b.id, p)) { d.x += dx; d.y += dy; }
          b.x = X; b.y = y; b.w = W; layoutBandC(b, p); y = b.y + b.h + bgap;
        }
        const top = bands[0].y, bottom = y - bgap, cx = X + W / 2;
        const title = free.find(n => n.role === 'title'), sub = free.find(n => n.role === 'subtitle');
        let ty = top - 10;
        if (sub) { const lines = wrap(sub.text, W, sub.size); sub.w = snapv(Math.min(W, Math.max(...lines.map(s => measure(s, sub.size, sub.bold))) + 20)); sub.h = snapv(Math.max(sub.h, lines.length * lineH(sub.size) + 4)); sub.x = snapv(cx - sub.w / 2); sub.y = snapv(ty - sub.h); ty = sub.y - 4; }
        if (title) { const lines = wrap(title.text, W, title.size, true); title.w = snapv(Math.min(W, Math.max(...lines.map(s => measure(s, title.size, true))) + 24)); title.h = snapv(Math.max(title.h, lines.length * lineH(title.size) + 6)); title.x = snapv(cx - title.w / 2); title.y = snapv(ty - title.h); }
        const note = free.find(n => n.role === 'note'), leg = free.find(n => n.type === 'legend');
        if (leg) legendLayout(leg, p);
        const side = leg && note && W - leg.w - 12 >= 260;
        if (leg) { leg.x = snapv(X + W - leg.w); leg.y = snapv(bottom + 10); }
        if (note) {
          note.x = X; note.y = snapv(bottom + 10 + (leg && !side ? leg.h + 8 : 0)); note.w = snapv(side ? W - leg.w - 12 : W);
          const lines = wrap(note.text, note.w - 20, note.size); note.h = snapv(Math.max(side ? leg.h : 0, lines.length * lineH(note.size) + 16)); if (side) leg.h = note.h;
        }
        shiftBelow(p, free, oldBottom, bottom, [title, sub, note, leg]);
        if (c.mode === 'report') fitBelow(p, X, W, [title, sub]);
      } else {
        p.nodes.filter(n => !n.parent && contRow(n) && contRow(n).layout === 'inset').forEach(n => layoutInset(n, p));
        const tops = order(p.nodes.filter(n => !n.parent && (n.type === 'lane' || n.type === 'group')));
        for (const t of tops) {
          if (t.type === 'lane') { if (c.mode === 'report') t.w = targetW(c); layoutLaneC(t, p); }
          else { const s = groupNatural(t, c.mode === 'report' ? targetW(c) : 2400, p); placeGroup(t, t.x, t.y, s.w, s.h, s.flow, p); }
        }
        p.nodes.filter(n => !n.parent && contRow(n) && (contRow(n).layout === 'tile' || contRow(n).layout === 'margin' || (contRow(n).layout === 'stack' && contRow(n).stack === 'all') || (contRow(n).layout === 'flow' && n.type !== 'group'))).forEach(n => layoutCont(n, p, { fitTitle: true }));
        tidyFree(p);
        if (c.mode === 'report') fitFree(p, targetW(c));
      }
      for (const n of p.nodes) { n.x = snapv(n.x); n.y = snapv(n.y); delete n.links; }
      if (window.Std) Std.afterLayout(p);
    } finally { cur = saved; }
  }
  window.beautify = beautifyC;
  try { beautify = beautifyC; } catch (_) { }

  /* ---------- 报告插图 PNG：写入 DPI，插入 Word 即为版心宽 ---------- */
  function crc32(buf) { let c, crc = 0xFFFFFFFF; for (let n = 0; n < buf.length; n++) { c = (crc ^ buf[n]) & 0xFF; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; crc = (crc >>> 8) ^ c; } return (crc ^ 0xFFFFFFFF) >>> 0; }
  async function withDPI(blob, dpi) {
    const src = new Uint8Array(await blob.arrayBuffer()), ppm = Math.round(dpi / 0.0254);
    const chunk = new Uint8Array(21), dv = new DataView(chunk.buffer);
    dv.setUint32(0, 9); chunk.set([0x70, 0x48, 0x59, 0x73], 4); dv.setUint32(8, ppm); dv.setUint32(12, ppm); chunk[16] = 1;
    dv.setUint32(17, crc32(chunk.subarray(4, 17)));
    /* 去掉已有 pHYs，插在 IHDR（8+25 字节）之后 */
    const parts = [src.subarray(0, 33)]; let i = 33;
    while (i < src.length) { const len = new DataView(src.buffer, src.byteOffset + i).getUint32(0), type = String.fromCharCode(...src.subarray(i + 4, i + 8)); if (type !== 'pHYs') parts.push(src.subarray(i, i + 12 + len)); if (type === 'IHDR') { } i += 12 + len; }
    parts.splice(1, 0, chunk);
    return new Blob(parts, { type: 'image/png' });
  }
  async function exportReportPNG() {
    if (window.JwIconLabels) await JwIconLabels.ready(P());
    const c = cfg(), pg = PAGES[c.page];
    const { str, w, h } = exportSVGString(P(), false);
    const scale = Math.max(2, Math.min(4, 2400 / w * 1.2));
    const blob = await rasterize(str, w, h, scale);
    const dpi = (w * scale) / (pg.cm / 2.54);
    await saveFile(fname('png').replace(/\.png$/, `-报告插图-${pg.name}.png`), await withDPI(blob, dpi));
    const f = fontAt(w - PAD * 2, pg.cm);
    toast(`已导出报告插图：插入 Word／WPS 后宽 ${pg.cm} cm，框内文字约 ${f} pt${f < 7.5 ? '（偏小：建议在图面设置中把排版改为“报告版心”后再导出）' : ''}`);
  }

  /* ---------- 图面设置面板 ---------- */
  function panelHTML() {
    const c = cfg(), seg = (id, opts, v) => `<div class="seg" id="${id}">${opts.map(([k, t]) => `<button data-v="${k}" class="${k === v ? 'on' : ''}">${t}</button>`).join('')}</div>`;
    let h = `<div class="row" title="标准：铺满整幅；紧凑：条目紧挨、图宽随内容收缩；报告版心：按报告版心宽度与字号自动折行"><label>排版</label>${seg('d-lay', Object.keys(MODES).map(k => [k, MODES[k].label]), c.mode)}</div>`;
    if (c.mode === 'report') {
      h += `<div class="row"><label>版心</label><select id="d-lay-page">${Object.entries(PAGES).map(([k, v]) => `<option value="${k}" ${k === c.page ? 'selected' : ''}>${v.name}（${v.hint}）</option>`).join('')}</select></div>`;
      h += `<div class="row"><label>图内字号</label><select id="d-lay-font">${FONTS.map(([v, t]) => `<option value="${v}" ${v === c.font ? 'selected' : ''}>${t}</option>`).join('')}</select></div>`;
      h += `<div class="hint" style="margin:-2px 0 6px">图宽 ${targetW(c)} px，导出“报告插图 PNG”后插入 Word 恰为版心宽，框内文字即为所选字号。</div>`;
    } else if (c.mode === 'compact') {
      h += `<div class="hint" style="margin:-2px 0 6px">条目紧挨排列、装备卡缩小，图宽随内容收缩；按 Ctrl+Shift+F 重新排版。</div>`;
    }
    return h;
  }
  function apply(mut) {
    checkpoint();
    const next = cfg({ layout: Object.assign({}, cfg(), mut) });
    adopt(next);
    writePref(next);
    beautifyC(P()); render(); fit();
    const c = cfg();
    toast(c.mode === 'report' ? `已按${PAGES[c.page].name}版心排版：图宽 ${targetW(c)} px，导出“报告插图 PNG”插入 Word 即为 ${PAGES[c.page].cm} cm 宽` : MODES[c.mode].toast);
  }
  function bind(root) {
    const q = s => root.querySelector(s);
    const lay = q('#d-lay'); if (lay) lay.addEventListener('click', e => { const b = e.target.closest('[data-v]'); if (b) apply({ mode: b.dataset.v }); });
    const pg = q('#d-lay-page'); if (pg) pg.addEventListener('change', e => apply({ page: e.target.value }));
    const ft = q('#d-lay-font'); if (ft) ft.addEventListener('change', e => apply({ font: +e.target.value }));
  }
  function stamp() { return adopt(cfg()); }
  window.Compact = { PAGES, FONTS, cfg, targetW, fontAt, beautify: beautifyC, stamp, exportReportPNG, withDPI, panelHTML, bind, natural, flow };
})();
