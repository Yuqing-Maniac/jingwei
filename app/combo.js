'use strict';
/* ============ 复合图标：编队／组合 ============
 * 一个复合图标 = 若干成员图标按相对位置合成的一张矢量图，存为 doc.custom[id]（带 combo 元数据，可再编辑），
 * 在图中就是一个普通元素：可连线、可下钻、可导出（PPT／Visio 里是一张图）。
 * 两条路：
 *   1. 选中多个元素 → 组合为复合图标（Ctrl+G）：保留它们现在的相对位置和大小；Ctrl+Shift+U 拆回原元素。
 *   2. 编队生成器：选一个图标、数量和阵型（楔形／横队／纵队／梯队／菱形／环形／方阵／蜂群），一键生成。
 */
(function () {
  const PATTERNS = [
    ['wedge', '楔形（人字）'], ['line', '横队'], ['column', '纵队'], ['echelon', '梯队'],
    ['diamond', '菱形'], ['circle', '环形'], ['grid', '方阵'], ['swarm', '蜂群（散布）'],
  ];
  const PNAME = Object.fromEntries(PATTERNS);

  /* ---------- geometry ---------- */
  function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
  /* positions in "icon units" (1 = one icon width), centred later */
  function formation(pattern, n, gap, seed = 7) {
    const P = [], g = 1 + gap;
    if (pattern === 'line') for (let i = 0; i < n; i++) P.push([i * g, 0]);
    else if (pattern === 'column') for (let i = 0; i < n; i++) P.push([0, i * g * 0.8]);
    else if (pattern === 'echelon') for (let i = 0; i < n; i++) P.push([i * g * 0.8, i * g * 0.55]);
    else if (pattern === 'wedge') { P.push([0, 0]); for (let i = 1; i < n; i++) { const k = Math.ceil(i / 2), s = i % 2 ? -1 : 1; P.push([s * k * g * 0.75, k * g * 0.6]); } }
    else if (pattern === 'diamond') {
      const ring = [[0, 0], [-1, 1], [1, 1], [0, 2], [-2, 2], [2, 2], [-1, 3], [1, 3], [0, 4], [-3, 3], [3, 3], [0, 3]];
      for (let i = 0; i < n; i++) { const r = ring[i] || [((i % 4) - 1.5) * 1.2, 5 + Math.floor(i / 4)]; P.push([r[0] * g * 0.7, r[1] * g * 0.55]); }
    } else if (pattern === 'circle') {
      const R = Math.max(1, n * g / (2 * Math.PI)); for (let i = 0; i < n; i++) { const a = -Math.PI / 2 + i * 2 * Math.PI / n; P.push([Math.cos(a) * R, Math.sin(a) * R * 0.8]); }
    } else if (pattern === 'grid') {
      const c = Math.ceil(Math.sqrt(n)); for (let i = 0; i < n; i++) P.push([(i % c) * g, Math.floor(i / c) * g * 0.8]);
    } else { /* swarm: jittered poisson-ish */
      const r = rng(seed), out = []; let tries = 0; const R = Math.sqrt(n) * g * 0.85;
      while (out.length < n && tries < 4000) { tries++; const x = (r() * 2 - 1) * R, y = (r() * 2 - 1) * R * 0.65; if (out.every(([a, b]) => Math.hypot(a - x, b - y) > g * 0.78)) out.push([x, y]); }
      P.push(...out);
    }
    return P;
  }

  /* ---------- rendering to one SVG ---------- */
  const U = 96; // one icon unit in svg px
  function innerOf(svgText) {
    const a = svgText.indexOf('>', svgText.indexOf('<svg')) + 1, b = svgText.lastIndexOf('</svg>');
    return svgText.slice(a, b);
  }
  function memberMarkup(m) {
    const x = m.x * U, y = m.y * U, s = m.s * U;
    if (m.icon && m.icon.startsWith('lib:') && ICON_MAP[m.icon.slice(4)]) {
      const sv = ICON_MAP[m.icon.slice(4)].svg;
      const vb = (sv.match(/viewBox=['"]([^'"]+)['"]/) || [, '0 0 96 96'])[1];
      return `<svg x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${s.toFixed(1)}" height="${s.toFixed(1)}" viewBox="${vb}" overflow="visible">${innerOf(sv)}</svg>`;
    }
    const u = iconURI(m.icon); if (!u) return '';
    return `<image href="${u.replace(/"/g, '&quot;')}" x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${s.toFixed(1)}" height="${s.toFixed(1)}" preserveAspectRatio="xMidYMid meet"/>`;
  }
  /* members: [{icon, x, y, s}] where x,y = top-left in icon units, s = size in icon units */
  function buildSVG(spec) {
    const ms = spec.members; if (!ms.length) return null;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const m of ms) { x0 = Math.min(x0, m.x); y0 = Math.min(y0, m.y); x1 = Math.max(x1, m.x + m.s); y1 = Math.max(y1, m.y + m.s); }
    const pad = spec.frame ? 0.18 : 0.04;
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad;
    const W = (x1 - x0) * U, H = (y1 - y0) * U;
    let body = '';
    if (spec.frame) body += `<rect x="${(x0 * U + 3).toFixed(1)}" y="${(y0 * U + 3).toFixed(1)}" width="${(W - 6).toFixed(1)}" height="${(H - 6).toFixed(1)}" rx="${Math.min(W, H) * 0.12}" fill="#4CA8FF" fill-opacity="0.07" stroke="#4C8FD6" stroke-width="3" stroke-dasharray="10 7"/>`;
    /* draw back-to-front: larger y first so nearer (lower) members overlap the far ones */
    for (const m of [...ms].sort((a, b) => a.y - b.y)) body += memberMarkup(m);
    if (spec.badge) {
      const r = Math.max(22, Math.min(W, H) * 0.11), cx = x1 * U - r * 1.05, cy = y0 * U + r * 1.05;
      body += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r.toFixed(1)}" fill="#F2A33A" stroke="#ffffff" stroke-width="3"/><path d="M${(cx - r * 0.42).toFixed(1)},${(cy - r * 0.42).toFixed(1)} L${(cx + r * 0.42).toFixed(1)},${(cy + r * 0.42).toFixed(1)} M${(cx + r * 0.42).toFixed(1)},${(cy - r * 0.42).toFixed(1)} L${(cx - r * 0.42).toFixed(1)},${(cy + r * 0.42).toFixed(1)}" stroke="#ffffff" stroke-width="${(r * 0.16).toFixed(1)}" stroke-linecap="round"/>`;
      /* the badge is an "×N" marker: draw N as small bars under the cross would be unreadable; we keep the ×, the label carries N */
    }
    const svgText = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${(x0 * U).toFixed(1)} ${(y0 * U).toFixed(1)} ${W.toFixed(1)} ${H.toFixed(1)}" width="${W.toFixed(0)}" height="${H.toFixed(0)}">${body}</svg>`;
    return { svg: svgText, aspect: W / H };
  }

  function formationSpec(o) {
    const pos = formation(o.pattern, o.count, o.gap, o.seed);
    const members = pos.map(([x, y], i) => {
      const depth = o.taper ? 1 - Math.min(0.35, (y / Math.max(1, o.count)) * 0.35) : 1;
      return { icon: o.icon, x: x - depth / 2, y: y - depth / 2, s: depth };
    });
    return { kind: 'formation', icon: o.icon, count: o.count, pattern: o.pattern, gap: o.gap, taper: !!o.taper, frame: !!o.frame, badge: false, seed: o.seed || 7, members };
  }

  /* store as custom icon; returns custom id */
  function saveCombo(spec, name, id) {
    const r = buildSVG(spec); if (!r) return null;
    id = id || ('cb' + uid());
    doc.custom[id] = { name, uri: svgUri(r.svg), combo: spec, aspect: r.aspect };
    return id;
  }
  function sizeFor(aspect, base = 150) {
    let w = base * Math.sqrt(aspect), h = base / Math.sqrt(aspect);
    w = Math.max(110, Math.min(260, w)); h = Math.max(90, Math.min(220, h));
    return { w: snapv(w), h: snapv(h + 24) };
  }

  /* ---------- 1. group selected elements ---------- */
  function groupSelection() {
    const p = P();
    const ns = [...sel].map(id => nodeById(id)).filter(n => n && !isCont(n) && n.icon);
    if (ns.length < 2) { toast('请先选中至少两个带图标的元素（Shift 点选或框选）'); return; }
    checkpoint();
    const boxes = ns.map(n => ({ n, L: nodeLayout(n) })).filter(o => o.L.icon);
    const ref = Math.min(...boxes.map(o => o.L.icon.s));
    const members = boxes.map(({ n, L }) => ({ icon: n.icon, x: L.icon.x / ref, y: L.icon.y / ref, s: L.icon.s / ref, text: n.text, w: n.w, h: n.h, status: n.status, noBox: n.noBox, type: n.type, nx: n.x, ny: n.y }));
    const spec = { kind: 'group', frame: false, badge: false, members };
    const names = [...new Set(ns.map(n => (n.text || iconName(n.icon) || '').split('\n')[0]))];
    const label = names.length <= 3 ? names.join('＋') : names.slice(0, 2).join('＋') + `等 ${ns.length} 项`;
    const cid = saveCombo(spec, label);
    const x0 = Math.min(...ns.map(n => n.x)), y0 = Math.min(...ns.map(n => n.y)), x1 = Math.max(...ns.map(n => n.x + n.w)), y1 = Math.max(...ns.map(n => n.y + n.h));
    const sz = sizeFor(doc.custom[cid].aspect, Math.min(220, Math.max(140, Math.sqrt((x1 - x0) * (y1 - y0)) * 0.7)));
    const cn = mkNode({ type: 'equip', icon: 'cu:' + cid, text: label, size: 12, w: sz.w, h: sz.h, x: snapv((x0 + x1) / 2 - sz.w / 2), y: snapv((y0 + y1) / 2 - sz.h / 2), parent: ns[0].parent });
    const ids = new Set(ns.map(n => n.id));
    p.links = p.links.filter(l => !(ids.has(l.from) && ids.has(l.to)));
    for (const l of p.links) { if (ids.has(l.from)) l.from = cn.id; if (ids.has(l.to)) l.to = cn.id; }
    /* de-duplicate links that now coincide */
    const seen = new Set(); p.links = p.links.filter(l => { const k = l.from + '>' + l.to + '|' + l.kind; if (seen.has(k)) return false; seen.add(k); return true; });
    p.nodes = p.nodes.filter(n => !ids.has(n.id)); p.nodes.push(cn);
    cn.parent = findParent(cn);
    sel = new Set([cn.id]); selLink = null; renderPalette(); render();
    toast(`已组合为复合图标：${label}（Ctrl+Shift+U 可拆分）`);
  }

  /* ---------- ungroup ---------- */
  function ungroup(n) {
    n = n || (sel.size === 1 ? nodeById([...sel][0]) : null);
    const c = n && n.icon && n.icon.startsWith('cu:') && doc.custom[n.icon.slice(3)];
    if (!c || !c.combo) { toast('所选元素不是复合图标'); return; }
    checkpoint();
    const L = nodeLayout(n), ms = c.combo.members;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const m of ms) { x0 = Math.min(x0, m.x); y0 = Math.min(y0, m.y); x1 = Math.max(x1, m.x + m.s); y1 = Math.max(y1, m.y + m.s); }
    const out = [];
    if (c.combo.kind === 'group' && ms.every(m => m.nx !== undefined)) {
      /* restore originals around the combo's current centre */
      const ox = Math.min(...ms.map(m => m.nx)), oy = Math.min(...ms.map(m => m.ny)), ow = Math.max(...ms.map(m => m.nx + m.w)) - ox, oh = Math.max(...ms.map(m => m.ny + m.h)) - oy;
      const cx = n.x + n.w / 2 - ow / 2, cy = n.y + n.h / 2 - oh / 2;
      for (const m of ms) out.push(mkNode({ type: m.type || 'equip', icon: m.icon, text: m.text || iconName(m.icon), status: m.status || 'base', noBox: m.noBox !== false, size: 12, w: m.w || 96, h: m.h || 96, x: snapv(cx + m.nx - ox), y: snapv(cy + m.ny - oy), parent: n.parent }));
    } else {
      const k = L.icon ? L.icon.s / Math.max(x1 - x0, y1 - y0) : 60;
      const cell = Math.max(72, k * 1.3);
      ms.forEach((m, i) => out.push(mkNode({ type: 'equip', icon: m.icon, text: `${iconName(m.icon)}${ms.length > 1 ? ' ' + (i + 1) : ''}`, noBox: true, size: 12, w: 96, h: 96, x: snapv(n.x + (m.x - x0) * cell), y: snapv(n.y + (m.y - y0) * cell), parent: n.parent })));
    }
    const p = P(); p.nodes = p.nodes.filter(x => x.id !== n.id); p.nodes.push(...out);
    /* links attach to the first member */
    for (const l of p.links) { if (l.from === n.id) l.from = out[0].id; if (l.to === n.id) l.to = out[0].id; }
    sel = new Set(out.map(o => o.id)); render(); toast(`已拆分为 ${out.length} 个元素`);
  }

  /* ---------- 2. formation dialog ---------- */
  let dlg = null, editNode = null, state = null;
  const iconChoices = () => ICONS.filter(i => ['无人', '空中', '海上', '陆地', '反无人', '人员'].includes(ICON_CAT_OVERRIDE[i.key] || i.cat));
  function ensureDlg() {
    if (dlg) return dlg;
    const st = document.createElement('style');
    st.textContent = `#cb-dlg{position:fixed;top:0;right:0;bottom:0;left:0;background:rgba(10,15,22,.45);display:none;align-items:center;justify-content:center;z-index:25;padding:16px}
#cb-dlg .box{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:12px;width:min(880px,100%);max-height:90vh;display:grid;grid-template-columns:300px minmax(0,1fr);overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.25)}
#cb-dlg .side{padding:14px 16px;border-right:1px solid var(--line);overflow:auto;display:flex;flex-direction:column;gap:10px}
#cb-dlg h3{margin:0 0 2px;font-size:15px}#cb-dlg .hint{color:var(--muted);font-size:12px;line-height:1.6}
#cb-dlg label.f{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--muted)}
#cb-dlg .ic-list{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;max-height:208px;overflow:auto;border:1px solid var(--line);border-radius:8px;padding:4px}
#cb-dlg .ic-list button{flex-direction:column;font-size:10.5px;padding:4px 2px;line-height:1.2;border:1px solid transparent}
#cb-dlg .ic-list button.on{border-color:var(--accent);background:var(--accent-soft)}
#cb-dlg .ic-list img{width:34px;height:34px;object-fit:contain}
#cb-dlg .pats{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}#cb-dlg .pats button{justify-content:center;border-color:var(--line);font-size:12px;padding:5px 2px}
#cb-dlg .pats button.on{background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
#cb-dlg .main{display:flex;flex-direction:column;min-width:0}
#cb-dlg .prev{flex:1;min-height:320px;display:grid;place-items:center;background-color:var(--canvas);background-image:radial-gradient(var(--dot) 1px,transparent 1.2px);background-size:20px 20px;padding:18px}
#cb-dlg .prev img{max-width:100%;max-height:360px}
#cb-dlg .foot{display:flex;gap:8px;justify-content:flex-end;align-items:center;padding:10px 14px;border-top:1px solid var(--line);flex-wrap:wrap}
#cb-dlg .row2{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:12.5px}
@media (max-width:760px){#cb-dlg .box{grid-template-columns:1fr}#cb-dlg .side{border-right:none;border-bottom:1px solid var(--line);max-height:46vh}}`;
    document.head.appendChild(st);
    dlg = document.createElement('div'); dlg.id = 'cb-dlg';
    dlg.innerHTML = `<div class="box" role="dialog" aria-label="编队与复合图标">
<div class="side">
  <div><h3>编队生成器</h3><div class="hint">把同一种装备按阵型合成一个复合图标，在图中作为一个元素使用（可连线、可下钻、可导出）。</div></div>
  <label class="f">装备图标<input type="text" id="cb-q" placeholder="搜索：四旋翼、无人艇、战斗机…"></label>
  <div class="ic-list" id="cb-icons"></div>
  <label class="f">数量 <span id="cb-nv" style="color:var(--fg);font-variant-numeric:tabular-nums"></span><input type="range" id="cb-n" min="2" max="16" step="1"></label>
  <div class="f" style="font-size:12px;color:var(--muted)">阵型<div class="pats" id="cb-pats" style="margin-top:4px"></div></div>
  <label class="f">间距<input type="range" id="cb-gap" min="0" max="1.2" step="0.05"></label>
  <div class="row2"><label><input type="checkbox" id="cb-taper"> 远小近大</label><label><input type="checkbox" id="cb-frame"> 编队框</label><button id="cb-seed" title="蜂群重新散布">↻ 重排</button></div>
  <label class="f">名称<input type="text" id="cb-name"></label>
</div>
<div class="main"><div class="prev"><img id="cb-img" alt="编队预览"></div>
<div class="foot"><span class="hint" style="margin-right:auto">也可在画布上框选多个元素后按 Ctrl+G 组合</span><button id="cb-cancel">取消</button><button id="cb-ok" class="primary">插入到画布</button></div></div>
</div>`;
    document.body.appendChild(dlg);
    const $c = s => dlg.querySelector(s);
    dlg.addEventListener('click', e => { if (e.target === dlg) close(); });
    $c('#cb-cancel').onclick = close;
    $c('#cb-q').oninput = renderIcons;
    $c('#cb-icons').onclick = e => { const b = e.target.closest('[data-k]'); if (!b) return; state.icon = b.dataset.k; if (!state.nameTouched) state.name = autoName(); syncForm(); renderIcons(); preview(); };
    $c('#cb-pats').onclick = e => { const b = e.target.closest('[data-p]'); if (!b) return; state.pattern = b.dataset.p; if (!state.nameTouched) state.name = autoName(); syncForm(); preview(); };
    $c('#cb-n').oninput = e => { state.count = +e.target.value; if (!state.nameTouched) state.name = autoName(); syncForm(); preview(); };
    $c('#cb-gap').oninput = e => { state.gap = +e.target.value; preview(); };
    $c('#cb-taper').onchange = e => { state.taper = e.target.checked; preview(); };
    $c('#cb-frame').onchange = e => { state.frame = e.target.checked; preview(); };
    $c('#cb-seed').onclick = () => { state.seed = (state.seed * 7 + 13) % 997; preview(); };
    $c('#cb-name').oninput = e => { state.name = e.target.value; state.nameTouched = true; };
    $c('#cb-ok').onclick = commit;
    dlg.addEventListener('keydown', e => { if (e.key === 'Escape') { e.stopPropagation(); close(); } if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) commit(); });
    return dlg;
  }
  const autoName = () => `${iconName(state.icon)}${PNAME[state.pattern].replace(/（.*）/, '')}编队（${state.count}）`;
  function renderIcons() {
    const q = dlg.querySelector('#cb-q').value.trim();
    const list = iconChoices().filter(i => !q || i.name.includes(q));
    dlg.querySelector('#cb-icons').innerHTML = list.map(i => `<button data-k="lib:${i.key}" class="${state.icon === 'lib:' + i.key ? 'on' : ''}" title="${esc(i.name)}"><img src="${iconURI('lib:' + i.key)}" alt=""><span>${esc(i.name)}</span></button>`).join('') || '<div class="hint" style="grid-column:1/-1;padding:6px">没有匹配的图标</div>';
  }
  function syncForm() {
    const $c = s => dlg.querySelector(s);
    $c('#cb-n').value = state.count; $c('#cb-nv').textContent = state.count + ' 个';
    $c('#cb-gap').value = state.gap; $c('#cb-taper').checked = state.taper; $c('#cb-frame').checked = state.frame; $c('#cb-name').value = state.name;
    $c('#cb-pats').innerHTML = PATTERNS.map(([k, v]) => `<button data-p="${k}" class="${k === state.pattern ? 'on' : ''}">${v.replace(/（.*）/, '')}</button>`).join('');
    $c('#cb-seed').style.visibility = state.pattern === 'swarm' ? 'visible' : 'hidden';
  }
  function preview() { const r = buildSVG(formationSpec(state)); dlg.querySelector('#cb-img').src = r ? svgUri(r.svg) : ''; }
  function open(node) {
    ensureDlg();
    editNode = null;
    const c = node && node.icon && node.icon.startsWith('cu:') && doc.custom[node.icon.slice(3)];
    if (c && c.combo && c.combo.kind === 'formation') { editNode = node; state = { ...c.combo, name: node.text || c.name, nameTouched: true }; }
    else {
      const base = node && node.icon && node.icon.startsWith('lib:') ? node.icon : 'lib:uav_quad';
      state = { icon: base, count: 5, pattern: 'wedge', gap: 0.35, taper: false, frame: false, seed: 7, nameTouched: false }; state.name = autoName();
    }
    dlg.querySelector('#cb-q').value = ''; dlg.querySelector('#cb-ok').textContent = editNode ? '更新编队' : '插入到画布';
    syncForm(); renderIcons(); preview(); dlg.style.display = 'flex';
    setTimeout(() => { const on = dlg.querySelector('#cb-icons .on'); if (on) on.scrollIntoView({ block: 'nearest' }); }, 0);
  }
  function close() { if (dlg) dlg.style.display = 'none'; }
  function commit() {
    checkpoint();
    const spec = formationSpec(state), name = state.name || autoName();
    if (editNode) {
      const id = editNode.icon.slice(3); saveCombo(spec, name, id);
      const sz = sizeFor(doc.custom[id].aspect); const cx = editNode.x + editNode.w / 2, cy = editNode.y + editNode.h / 2;
      Object.assign(editNode, { text: name, w: sz.w, h: sz.h, x: snapv(cx - sz.w / 2), y: snapv(cy - sz.h / 2) });
      uriCache.delete('cu:' + id);
    } else {
      const id = saveCombo(spec, name), sz = sizeFor(doc.custom[id].aspect);
      const r = svg.getBoundingClientRect(), c = clientToWorld(r.left + r.width / 2, r.top + r.height / 2);
      const n = mkNode({ type: 'equip', icon: 'cu:' + id, text: name, size: 12, w: sz.w, h: sz.h, x: snapv(c.x - sz.w / 2), y: snapv(c.y - sz.h / 2) });
      P().nodes.push(n); n.parent = findParent(n); sel = new Set([n.id]); selLink = null;
    }
    close(); renderPalette(); render(); toast(editNode ? '编队已更新' : '已插入编队，可拖入任意层，也可连线');
  }

  /* public API (also used by 文字成图 and 模板) */
  window.Combo = {
    PATTERNS, formation, buildSVG, formationSpec, saveCombo, sizeFor,
    /* create a formation custom icon and return its icon key ('cu:<id>') */
    formationIcon(iconKey, count, pattern = 'wedge', opt = {}) {
      const spec = formationSpec({ icon: iconKey, count, pattern, gap: opt.gap ?? 0.35, taper: !!opt.taper, frame: !!opt.frame, seed: opt.seed || 7 });
      const id = saveCombo(spec, opt.name || `${iconName(iconKey)}编队（${count}）`); return 'cu:' + id;
    },
    /* create a mixed group icon from [{icon, x, y, s}] (icon units) */
    groupIcon(members, name, opt = {}) { const id = saveCombo({ kind: 'mixed', frame: !!opt.frame, badge: false, members }, name || '复合图标'); return 'cu:' + id; },
    groupSelection, ungroup, open, isCombo: n => !!(n && n.icon && n.icon.startsWith('cu:') && doc.custom[n.icon.slice(3)]?.combo),
  };
  window.openFormation = open;
})();
