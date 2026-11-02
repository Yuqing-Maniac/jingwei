/* ============ 织图 · 参照生成（好图 + 新项目内容 → 同款新图） ============
 * 思路：把参照图拆成“骨架”（分组带／层／容器／条目／连线习惯／下钻页），转成文字成图方言；
 *       大模型（内网 DeepSeek 等 OpenAI 兼容接口）按骨架改写为新项目内容，或离线按“层映射”直接套用骨架；
 *       生成后由工具继承参照图的版式样式（主题、分组带配色、视图类型、标题栏、图例）。
 * 参照来源：当前文档任一页、内置模板、织图工程文件（.json）、PowerPoint（.pptx）、Visio（.vsdx，经 importers.js）。
 * 依赖 app.js 全局：doc, cur, mkNode, uid, diagramSVG, contentBBox, T, esc, toast, checkpoint, loadDoc, render, fit, THEMES；
 * 依赖 textgen.js 暴露的 window.TextGen；可选 window.Importer、window.Std、window.TEMPLATES。 */
(function () {
  'use strict';

  const NON = ['text', 'note', 'legend', 'tblock'];
  const CONT = ['band', 'lane', 'group'];
  const firstLine = s => String(s || '').split('\n')[0].trim();
  const LS = 'hongtu.refgen.v1';
  const lsGet = () => { try { return JSON.parse(localStorage.getItem(LS) || '{}') || {}; } catch (_) { return {}; } };
  const lsSet = o => { try { localStorage.setItem(LS, JSON.stringify(Object.assign(lsGet(), o))); } catch (_) { } };
  function withDoc(d, pid, fn) { const sd = doc, sc = cur; doc = d; cur = pid; try { return fn(); } finally { doc = sd; cur = sc; } }
  function readingOrder(list) {
    const a = list.map(n => ({ n, cx: n.x + n.w / 2, cy: n.y + n.h / 2 })).sort((p, q) => p.cy - q.cy || p.cx - q.cx);
    const out = []; let row = [], ry = null;
    const flush = () => { row.sort((p, q) => p.cx - q.cx); out.push(...row.map(r => r.n)); row = []; };
    for (const it of a) { if (ry !== null && it.cy - ry > Math.max(20, it.n.h * 0.45)) flush(); if (!row.length) ry = it.cy; row.push(it); }
    flush(); return out;
  }
  /* 名称里会被方言误读的符号：顿号逗号（分隔）、冒号（容器简写）、箭头（连线）、方括号花括号（标记） */
  function safeName(s) {
    return String(s || '').replace(/\r/g, '').split('\n').map(x => x.trim()).filter(Boolean).join('<br>')
      .replace(/[、，,]/g, '／').replace(/[:：]/g, ' ').replace(/<->|<-|->|-->|==>|~>|→|←|↔|⇒/g, '至')
      .replace(/\[/g, '（').replace(/\]/g, '）').replace(/【/g, '（').replace(/】/g, '）').replace(/[{}]/g, '')
      .replace(/^[#>\-*+|\s]+/, '').replace(/\|/g, '／').replace(/\s{2,}/g, ' ').trim();
  }
  const linkName = n => safeName(firstLine(n.text)).split('<br>')[0];

  /* ================= 骨架提取 ================= */
  function skeleton(d, pid, depth = 0, seen = new Set()) {
    const p = d.pages[pid]; seen.add(pid);
    const byId = new Map(p.nodes.map(n => [n.id, n]));
    const kidsOf = id => p.nodes.filter(n => n.parent === id && byId.has(n.id) && !NON.includes(n.type));
    const isContainer = n => CONT.includes(n.type) || kidsOf(n.id).length > 0;
    const sk = { pid, name: p.name, view: p.view || null, title: '', subtitle: '', bands: [], links: [], notes: [], subs: [], hasLegend: false, hasTblock: false };
    const texts = p.nodes.filter(n => n.type === 'text' && !n.parent);
    const tt = texts.find(n => n.role === 'title') || texts.slice().sort((a, b) => (b.size || 13) - (a.size || 13) || a.y - b.y)[0];
    if (tt && (tt.role === 'title' || (tt.size || 13) >= 18)) sk.title = firstLine(tt.text);
    const st = texts.find(n => n.role === 'subtitle'); if (st) sk.subtitle = firstLine(st.text);
    sk.notes = p.nodes.filter(n => n.type === 'note').map(n => String(n.text || '').replace(/\n+/g, ' ').replace(/^\s*(说明|备注|注)\s*[:：]\s*/, '').trim()).filter(Boolean);
    sk.hasLegend = p.nodes.some(n => n.type === 'legend'); sk.hasTblock = p.nodes.some(n => n.type === 'tblock');
    const item = n => {
      const it = { node: n, name: safeName(n.text) || '（未命名）', status: n.status || 'base', icon: n.icon || null, form: n.type === 'equip' ? 'equip' : 'box', shape: n.type, children: [] };
      if (isContainer(n)) it.children = readingOrder(kidsOf(n.id)).map(item);
      if (n.sub && d.pages[n.sub] && !seen.has(n.sub) && depth < 2) sk.subs.push({ host: linkName(n) || it.name, sk: skeleton(d, n.sub, depth + 1, seen) });
      return it;
    };
    const top = readingOrder(p.nodes.filter(n => (!n.parent || !byId.has(n.parent)) && !NON.includes(n.type)));
    let bandNodes = top.filter(n => n.type === 'band');
    if (!bandNodes.length) bandNodes = top.filter(n => isContainer(n));
    const loose = top.filter(n => !bandNodes.includes(n));
    for (const b of bandNodes) {
      const band = { node: b, name: safeName(b.text) || '分组', status: b.status || 'base', lanes: [], items: [] };
      for (const k of readingOrder(kidsOf(b.id))) {
        if (k.type === 'lane') band.lanes.push({ node: k, name: safeName(k.text) || '层', items: readingOrder(kidsOf(k.id)).map(item) });
        else band.items.push(item(k));
      }
      sk.bands.push(band);
    }
    if (loose.length) sk.bands.push({ node: null, name: bandNodes.length ? '其他' : '组成', status: 'base', lanes: [], items: loose.map(item), implicit: !bandNodes.length });
    for (const l of p.links) {
      const a = byId.get(l.from), b = byId.get(l.to); if (!a || !b) continue;
      const an = linkName(a), bn = linkName(b); if (!an || !bn || an === bn) continue;
      sk.links.push({ a: an, b: bn, dir: l.dir || 'one', kind: l.kind || 'data', label: safeName(l.label || (l.attrs && l.attrs.content) || '').split('<br>')[0] });
    }
    return sk;
  }

  /* ================= 骨架 → 方言 ================= */
  const KIND_TAG = { ctrl: ' [指令]', wired: ' [有线]', radio: ' [无线]', sat: ' [卫通]', plain: ' [关联]', data: '' };
  const OP = { one: '->', both: '<->', none: '--' };
  function itemLine(it, opt) {
    let s = it.name;
    if (it.status === 'new') s += ' [新增]'; else if (it.status === 'key') s += ' [重点]';
    if (!it.children.length) {
      if (it.form === 'equip') s += ' {装备}';
      if (opt.icons !== false && it.icon && /^(lib|ms):/.test(it.icon)) s += ` {图标:${it.icon}}`;
      else if (opt.icons !== false && it.icon && /^cu:/.test(it.icon) && opt.custom !== false) s += ` {图标:${it.icon}}`;
    }
    return s;
  }
  function itemsBlock(items, indent, opt, out) {
    for (const it of items) {
      out.push(' '.repeat(indent) + '- ' + itemLine(it, opt));
      if (it.children.length) itemsBlock(it.children, indent + 2, opt, out);
    }
  }
  function toDialect(sk, opt = {}, out = []) {
    if (sk.title) out.push('# ' + safeName(sk.title).replace(/<br>/g, ' '));
    else if (out.length) out.push('# ' + (safeName(sk.name) || '内部构成'));
    if (sk.subtitle) out.push('> ' + sk.subtitle);
    out.push('');
    for (const b of sk.bands) {
      out.push('## ' + b.name + (b.status === 'new' ? ' [新增]' : b.status === 'key' ? ' [重点]' : ''));
      itemsBlock(b.items, 0, opt, out); /* 分组带直属条目须写在第一个 ### 之前 */
      for (const l of b.lanes) { out.push('### ' + l.name); itemsBlock(l.items, 0, opt, out); }
      out.push('');
    }
    if (sk.links.length) {
      out.push('## 连接');
      for (const l of sk.links) out.push(`- ${l.a} ${OP[l.dir] || '->'} ${l.b}${l.label ? ' : ' + l.label : ''}${KIND_TAG[l.kind] || ''}`);
      out.push('');
    }
    if (sk.notes.length) out.push('说明：' + sk.notes.join('；'), '');
    for (const s of sk.subs) { out.push('## 展开：' + s.host); toDialect(Object.assign({}, s.sk, { title: s.sk.title || (s.host + ' 内部构成') }), opt, out); }
    return out.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
  }
  /* 骨架要点（给大模型的“版式说明”，也显示在界面上） */
  function summary(sk) {
    const cnt = items => items.reduce((s, it) => s + (it.children.length ? cnt(it.children) : 1), 0);
    const eq = items => items.reduce((s, it) => s + (it.children.length ? eq(it.children) : it.form === 'equip' ? 1 : 0), 0);
    const lines = [`分组带 ${sk.bands.length} 个：`];
    sk.bands.forEach((b, i) => {
      const all = b.lanes.flatMap(l => l.items).concat(b.items), n = cnt(all), e = eq(all);
      const groups = all.filter(it => it.children.length).length;
      lines.push(`${i + 1}. 「${b.name}」${b.lanes.length ? `含 ${b.lanes.length} 层（${b.lanes.map(l => `${l.name}×${cnt(l.items)}`).join('、')}）` : ''}${b.lanes.length ? '，' : ''}共 ${n} 个条目${groups ? `，其中 ${groups} 个容器` : ''}${e ? `，${e === n ? '全部' : e + ' 个'}画成装备图标卡` : ''}`);
    });
    if (sk.links.length) {
      const by = {}; for (const l of sk.links) { const k = { one: '单向', both: '双向', none: '无箭头' }[l.dir] + '·' + ({ ctrl: '指令', wired: '有线', radio: '无线', sat: '卫通', plain: '关联', data: '数据' }[l.kind] || '数据'); by[k] = (by[k] || 0) + 1; }
      lines.push(`连线 ${sk.links.length} 条：` + Object.entries(by).map(([k, v]) => `${k} ${v}`).join('，'));
    } else lines.push('无连线');
    if (sk.subs.length) lines.push(`下钻内部构成页 ${sk.subs.length} 个：` + sk.subs.map(s => s.host).join('、'));
    if (sk.view) lines.push(`视图类型：${sk.view}`);
    return lines.join('\n');
  }
  /* 映射表行：每个分组带、每层一行 */
  function mapRows(sk) {
    const rows = [];
    const cnt = items => items.reduce((s, it) => s + (it.children.length ? cnt(it.children) : 1), 0);
    sk.bands.forEach((b, i) => {
      rows.push({ key: `b${i}`, kind: 'band', name: b.name, count: cnt(b.items) + b.lanes.reduce((s, l) => s + cnt(l.items), 0), sample: b.items.concat(b.lanes.flatMap(l => l.items)).slice(0, 4).map(it => it.name.split('<br>')[0]).join('、') });
      b.lanes.forEach((l, j) => rows.push({ key: `b${i}l${j}`, kind: 'lane', name: l.name, count: cnt(l.items), sample: l.items.slice(0, 4).map(it => it.name.split('<br>')[0]).join('、') }));
    });
    return rows;
  }

  /* ================= 离线：按映射套用骨架 ================= */
  const splitItems = s => String(s || '').split(/[、，,；;\n]+/).map(x => safeName(x)).filter(Boolean);
  function applyMapping(sk, map, projName) {
    const n = JSON.parse(JSON.stringify(sk, (k, v) => k === 'node' ? undefined : v));
    const keep = new Set(), allNames = items => items.forEach(it => { keep.add(it.name.split('<br>')[0]); allNames(it.children); });
    const majorityEquip = items => { const leaves = []; const w = a => a.forEach(it => it.children.length ? w(it.children) : leaves.push(it)); w(items); return leaves.length && leaves.filter(x => x.form === 'equip').length * 2 >= leaves.length; };
    const fresh = (list, equip) => list.map(name => ({ name, status: 'base', icon: null, form: equip ? 'equip' : 'box', children: [] }));
    n.bands.forEach((b, i) => {
      const m = map[`b${i}`] || {};
      if (m.name && m.name.trim()) b.name = safeName(m.name);
      if (m.items && m.items.trim()) { const eqp = majorityEquip(b.items.length ? b.items : b.lanes.flatMap(l => l.items)); b.items = fresh(splitItems(m.items), eqp); if (b.lanes.length) b.lanes = b.lanes.filter((l, j) => { const lm = map[`b${i}l${j}`] || {}; return lm.items && lm.items.trim(); }); }
      b.lanes.forEach((l, j) => {
        const lm = map[`b${i}l${j}`] || {};
        if (lm.name && lm.name.trim()) l.name = safeName(lm.name);
        if (lm.items && lm.items.trim()) l.items = fresh(splitItems(lm.items), majorityEquip(l.items));
      });
    });
    n.bands.forEach(b => { allNames(b.items); b.lanes.forEach(l => allNames(l.items)); });
    n.links = n.links.filter(l => keep.has(l.a) && keep.has(l.b));
    n.subs = n.subs.filter(s => keep.has(s.host));
    if (projName) { n.title = projName; n.subtitle = ''; }
    n.notes = [];
    return n;
  }

  /* ================= 大模型提示词 ================= */
  const REF_RULES = `
你现在执行“参照生成”任务：用户给出一张已有的优秀架构图（参照图，已转成上述方言）和新项目的内容，请仿照参照图，为新项目生成一张同类架构图。
必须遵守：
1. 保持参照图的版式骨架：分组带（##）的数量与先后顺序、每个分组带内层（###）的划分方式、每层条目数量的量级（上下浮动不超过一半）、容器嵌套方式、哪些层画成装备图标卡 {装备}、连线的类型与方向习惯（单向／双向、指令／数据／有线／无线／卫通）。
2. 分组带与层的名称按“层映射”改写；映射留空的，按新项目内容取一个与参照层作用相对应的名称。
3. 条目全部取自新项目内容，名称简洁（2～12 字），沿用新项目原有术语；不要照抄参照图的业务条目，不要编造新项目内容中没有依据的系统（通用基础设施如网络、云平台、数据库可按需保留）。新项目内容中缺少对应内容的层可以删掉。
4. 连线两端必须与上文写过的条目名称完全一致；连线数量与参照图大体相当，表达新项目真实的信息流、指令流和链路。
5. [新增]／[重点] 只在新项目内容明确说明“新增、新建、改造、重点”时使用。图标可不写（工具按名称自动匹配）；要写就写中文名称如 {图标:雷达}，lib: 开头的图标编号只能使用参照图中出现过的。
6. 条目名称后不要用冒号附加说明文字——冒号只用于“容器：子项、子项”，表示容器内含子项。
7. 参照图有“## 展开：X”内部构成页时，只为新项目中内容足够的对应系统生成展开页。
8. 只输出方言文本本身，不要解释，不要代码块围栏。`;
  function buildPrompt(ctx) {
    const mapTxt = ctx.rows.map(r => { const m = ctx.map[r.key] || {}; return `${r.kind === 'band' ? '分组带' : '　层'}「${r.name}」（${r.count} 个条目）→ ${m.name && m.name.trim() ? '「' + m.name.trim() + '」' : '（自行对应）'}${m.items && m.items.trim() ? `；指定条目：${m.items.trim()}` : ''}`; }).join('\n');
    const content = String(ctx.content || '').slice(0, 24000);
    return `【参照图（方言）】\n${ctx.dialect}\n【参照图骨架要点】\n${ctx.summary}\n\n【层映射（参照 → 新项目）】\n${mapTxt}\n\n【新项目名称】${ctx.projName || '（按内容拟定）'}\n\n【新项目内容】\n${content}${ctx.extra ? '\n\n【补充要求】\n' + ctx.extra : ''}`;
  }

  /* ================= 生成结果：继承参照样式 ================= */
  function styleTransfer(res, sk, refDoc) {
    const page = res.pages[0];
    const newBands = readingOrder(page.nodes.filter(n => n.type === 'band'));
    const refBands = sk.bands.map(b => b.node).filter(Boolean);
    const leafOf = (p, b) => p.nodes.filter(n => !CONT.includes(n.type) && !NON.includes(n.type) && isUnder(p, n, b));
    const isUnder = (p, n, b) => { const m = new Map(p.nodes.map(x => [x.id, x])); let c = n.parent && m.get(n.parent), k = 0; while (c && k++ < 20) { if (c === b) return true; c = c.parent && m.get(c.parent); } return false; };
    const refPage = refDoc.pages[sk.pid];
    newBands.forEach((nb, i) => {
      const rb = refBands[i]; if (!rb) return;
      if (rb.fill) nb.fill = rb.fill; if (rb.stroke) nb.stroke = rb.stroke;
      /* 条目配色：参照该分组带里出现最多的自定义填充色 */
      const tally = {}; for (const n of leafOf(refPage, rb)) if (n.fill && (!n.status || n.status === 'base')) { const k = n.fill + '|' + (n.stroke || ''); tally[k] = (tally[k] || 0) + 1; }
      const best = Object.entries(tally).sort((a, b) => b[1] - a[1])[0];
      if (best) { const [f, s] = best[0].split('|'); for (const n of leafOf(page, nb)) if ((!n.status || n.status === 'base') && n.type !== 'equip') { n.fill = f; if (s) n.stroke = s; } }
      const lanesR = refPage.nodes.filter(n => n.type === 'lane' && n.parent === rb.id), lanesN = page.nodes.filter(n => n.type === 'lane' && n.parent === nb.id);
      const lf = lanesR.find(l => l.fill); if (lf) lanesN.forEach(l => { l.fill = lf.fill; if (lf.stroke) l.stroke = lf.stroke; });
    });
    if (sk.view) page.view = sk.view;
    return res;
  }

  /* ================= 文件读取 ================= */
  async function docxText(buf) {
    const z = await JSZip.loadAsync(buf);
    const f = z.file('word/document.xml'); if (!f) throw new Error('不是有效的 Word 文档');
    const xml = await f.async('string');
    const out = [];
    for (const p of xml.split(/<\/w:p>/)) {
      const t = (p.match(/<w:t(?:\s[^>]*)?>([^<]*)<\/w:t>/g) || []).map(x => x.replace(/<[^>]+>/g, '')).join('');
      if (!t.trim()) continue;
      const st = (p.match(/<w:pStyle w:val="([^"]+)"/) || [])[1] || '';
      const lv = (st.match(/(?:Heading|heading|标题)\s*(\d)/) || [])[1] || (/^\d$/.test(st) ? st : '');
      const txt = t.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&apos;/g, "'");
      out.push(lv ? '#'.repeat(Math.min(+lv, 4)) + ' ' + txt : txt);
    }
    return out.join('\n');
  }
  function refDocFromImport(r, fname) {
    const d = { name: fname.replace(/\.[^.]+$/, ''), theme: (doc && doc.theme) || 'report', statusLabels: Object.assign({}, doc.statusLabels), custom: Object.assign({}, r.custom || {}), pages: {} };
    r.pages.forEach((p, i) => { if (i === 0 && !r.pages.some(x => x.id === 'root')) p.id = 'root'; d.pages[p.id] = p; });
    return d;
  }

  /* ================= 界面 ================= */
  const CSS = `
#rg{position:fixed;top:0;right:0;bottom:0;left:0;z-index:25;background:rgba(10,15,22,.5);display:none;align-items:center;justify-content:center;padding:16px}
#rg.open{display:flex}
#rg .rg-box{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:12px;width:min(1400px,100%);height:min(900px,100%);display:flex;flex-direction:column;overflow:hidden;box-shadow:0 18px 48px rgba(0,0,0,.25)}
#rg .rg-head{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap}
#rg .rg-head strong{font-size:15px;letter-spacing:.04em}
#rg .rg-sub{color:var(--muted);font-size:12px}
#rg .rg-body{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
#rg .rg-col{display:flex;flex-direction:column;min-height:0;overflow:auto;padding:10px 12px;gap:8px}
#rg .rg-col+.rg-col{border-left:1px solid var(--line)}
#rg h4{margin:4px 0 0;font-size:13px;display:flex;align-items:center;gap:6px}
#rg h4 .n{display:inline-flex;width:18px;height:18px;border-radius:50%;background:var(--accent);color:#fff;font-size:11px;align-items:center;justify-content:center;flex:none}
#rg h4 .rg-sub{font-weight:400}
#rg .rg-bar{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
#rg .rg-bar button{border-color:var(--line)}
#rg select,#rg input[type=text]{min-width:0}
#rg .rg-prev{min-height:180px;height:30vh;border:1px solid var(--line);border-radius:8px;background:var(--canvas);overflow:auto;display:flex;align-items:flex-start;justify-content:center;padding:8px}
#rg .rg-prev.big{height:auto;flex:1;min-height:240px}
#rg .rg-prev svg{width:100%;height:100%;display:block;border-radius:4px}
#rg .rg-empty{color:var(--muted);align-self:center;text-align:center;line-height:1.8;font-size:12.5px;padding:10px}
#rg .rg-sum{font-size:12px;line-height:1.7;color:var(--muted);white-space:pre-wrap;margin:0}
#rg table.rg-map{border-collapse:collapse;width:100%;font-size:12.5px}
#rg table.rg-map th{font-weight:500;color:var(--muted);text-align:left;padding:4px;border-bottom:1px solid var(--line);white-space:nowrap}
#rg table.rg-map td{padding:3px 4px;border-bottom:1px dashed var(--line);vertical-align:top}
#rg table.rg-map td.nm{white-space:nowrap}
#rg table.rg-map tr.lane td.nm{padding-left:18px;color:var(--muted)}
#rg table.rg-map td.nm small{display:block;color:var(--muted);font-size:11px;max-width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#rg table.rg-map input{width:100%;font-size:12.5px;padding:3px 6px}
#rg textarea{width:100%;font-family:var(--ui);font-size:13px;line-height:1.6;padding:8px 10px;border-radius:8px;resize:vertical}
#rg textarea.mono{font-family:Consolas,'Courier New',monospace,var(--ui);font-size:12px;line-height:1.5}
#rg details{border:1px solid var(--line);border-radius:8px;padding:6px 10px}
#rg details>summary{cursor:pointer;user-select:none;font-size:12.5px}
#rg .rg-set{display:none;border-bottom:1px solid var(--line);padding:10px 14px;background:var(--hover);gap:6px;flex-direction:column}
#rg .rg-set.open{display:flex}
#rg .rg-set .row label{width:84px}
#rg .rg-hint{color:var(--muted);font-size:12px;line-height:1.7}
#rg .rg-foot{display:flex;gap:10px;align-items:center;padding:10px 14px;border-top:1px solid var(--line);flex-wrap:wrap}
#rg .rg-modes{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
#rg .rg-modes label{display:flex;gap:4px;align-items:center;cursor:pointer;white-space:nowrap}
#rg .rg-msg{font-size:12px;color:var(--muted)}
#rg .rg-msg.err{color:var(--danger)}
#rg .rg-rep{font-size:12px;line-height:1.6;color:var(--muted)}
#rg .rg-rep ul{margin:2px 0 0;padding-left:18px;color:#B4691A;max-height:80px;overflow:auto}
#rg .rg-drop{outline:2px dashed var(--accent);outline-offset:-4px}
@media (max-width:900px){
  #rg{padding:0}
  #rg .rg-box{border-radius:0;height:100%;width:100%}
  #rg .rg-body{grid-template-columns:1fr;overflow:auto;display:block}
  #rg .rg-col{overflow:visible;padding:10px 16px}
  #rg .rg-col+.rg-col{border-left:none;border-top:1px solid var(--line)}
  #rg .rg-sub{display:none}
  #rg table.rg-map td.nm small{max-width:120px}
}`;
  const HTML = `
<div class="rg-box" role="dialog" aria-modal="true" aria-labelledby="rg-title">
  <div class="rg-head">
    <strong id="rg-title">参照生成</strong><span class="rg-sub">选一张做得好的图作参照，填入新项目内容，生成同款新图</span>
    <span style="flex:1"></span>
    <button id="rg-gear" title="大模型接口设置（与文字成图共用）">⚙ 大模型设置</button>
    <button id="rg-close" title="关闭（Esc）">关闭</button>
  </div>
  <div class="rg-set" id="rg-set">
    <div class="row"><label>接口地址</label><input type="text" id="rg-base" placeholder="如 http://10.1.2.3:8000/v1（OpenAI 兼容）"></div>
    <div class="row"><label>模型名称</label><input type="text" id="rg-model" placeholder="如 deepseek-v4-flash（以内网部署名称为准）"></div>
    <div class="row"><label>API Key</label><input type="text" id="rg-key" placeholder="无鉴权可留空" autocomplete="off" spellcheck="false"></div>
    <div class="rg-bar"><button id="rg-test">测试连接</button><span class="rg-msg" id="rg-test-msg"></span></div>
    <div class="rg-hint">调用 <code>POST {接口地址}/chat/completions</code>；设置只保存在本机浏览器，与“文字成图”共用。双击打开的离线网页访问内网接口时，接口需允许跨域（CORS），“测试连接”可直接验证。</div>
  </div>
  <div class="rg-body">
    <div class="rg-col">
      <h4><span class="n">1</span>参照图 <span class="rg-sub">当前文档、模板，或打开 PPT／Visio／draw.io／织图文件</span></h4>
      <div class="rg-bar">
        <select id="rg-src" style="flex:1"></select>
        <select id="rg-page" style="flex:1"></select>
        <button id="rg-file" title="打开 .pptx／.vsdx／.drawio／.json 作为参照，也可直接拖入下方预览区">打开文件…</button>
        <input type="file" id="rg-f" accept=".pptx,.vsdx,.drawio,.xml,.json,.ppt,.vsd" hidden>
      </div>
      <div class="rg-prev" id="rg-refprev"><div class="rg-empty">选择参照图</div></div>
      <pre class="rg-sum" id="rg-sum"></pre>
      <details><summary>参照图骨架（方言，可修改）</summary><textarea class="mono" id="rg-dialect" rows="10" spellcheck="false"></textarea>
        <label class="rg-hint" style="display:flex;gap:6px;align-items:center;margin-top:4px"><input type="checkbox" id="rg-keepicons" checked> 保留参照图的图标</label></details>
      <h4><span class="n">2</span>层映射 <span class="rg-sub">参照层 → 新项目层；留空则由大模型自行对应</span></h4>
      <table class="rg-map" id="rg-map"></table>
    </div>
    <div class="rg-col">
      <h4><span class="n">3</span>新项目内容 <span class="rg-sub">方案摘要、系统清单、需求条目均可</span></h4>
      <div class="rg-bar"><input type="text" id="rg-name" placeholder="新项目名称（作为图标题）" style="flex:1"><button id="rg-cfile" title="导入 .docx／.md／.txt，也可拖入下方文本框">导入方案文档…</button><input type="file" id="rg-cf" accept=".docx,.md,.markdown,.txt" hidden></div>
      <textarea id="rg-content" rows="9" placeholder="例如：&#10;本项目建设海岛无人值守监视系统，分感知、传输、处理、应用四部分。感知部分包括岸基雷达、光电转塔、无人机机巢……&#10;传输采用微波接力和卫通备份……&#10;&#10;可把方案 Word 文档拖到这里。"></textarea>
      <details><summary>补充要求（可选）</summary><textarea id="rg-extra" rows="2" placeholder="如：每层不超过 6 个系统；突出新增的智能分析能力"></textarea></details>
      <h4><span class="n">4</span>生成结果 <span class="rg-sub" id="rg-ressub"></span></h4>
      <div class="rg-prev big" id="rg-outprev"><div class="rg-empty">点下方“生成预览”</div></div>
      <div class="rg-rep" id="rg-rep"></div>
      <details id="rg-outbox"><summary>生成的方言（可修改，改后自动刷新预览）</summary><textarea class="mono" id="rg-out" rows="10" spellcheck="false"></textarea></details>
    </div>
  </div>
  <div class="rg-foot">
    <div class="rg-modes" id="rg-eng">
      <label title="内网 DeepSeek 等大模型按参照骨架改写新项目内容"><input type="radio" name="rg-eng" value="llm" checked> 大模型生成</label>
      <label title="不用大模型：按层映射改名、按“指定条目”替换内容，其余沿用参照图"><input type="radio" name="rg-eng" value="rule"> 离线套用骨架</label>
    </div>
    <div class="rg-modes" id="rg-ap">
      <label><input type="radio" name="rg-ap" value="doc" checked> 新建文档（继承参照主题与标题栏）</label>
      <label><input type="radio" name="rg-ap" value="page"> 作为新页面追加</label>
      <label><input type="radio" name="rg-ap" value="replace"> 替换当前页</label>
    </div>
    <span class="rg-msg" id="rg-msg"></span>
    <span style="flex:1"></span>
    <button id="rg-gen" title="Ctrl+Enter">生成预览</button>
    <button id="rg-apply" class="primary" disabled>生成到画布</button>
  </div>
</div>`;

  let root = null, refDoc = null, refPid = null, sk = null, rows = [], result = null, busy = false, extDocs = [], ptimer = null;
  const q = s => root.querySelector(s);
  const eng = () => (q('input[name=rg-eng]:checked') || {}).value || 'llm';
  const apMode = () => (q('input[name=rg-ap]:checked') || {}).value || 'doc';
  const msg = (t, err) => { const m = q('#rg-msg'); m.textContent = t || ''; m.classList.toggle('err', !!err); };

  function sources() {
    const out = [{ id: 'cur', name: '当前文档：' + (doc.name || '未命名'), get: () => doc }];
    extDocs.forEach((d, i) => out.push({ id: 'ext' + i, name: '文件：' + d.name, get: () => d }));
    (window.TEMPLATES || []).forEach((t, i) => out.push({ id: 'tpl' + i, name: '模板：' + t.name, get: () => { if (!t._doc) t._doc = t.build(); return t._doc; } }));
    return out;
  }
  function fillSources(selId) {
    const list = sources();
    q('#rg-src').innerHTML = list.map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join('');
    q('#rg-src').value = selId || 'cur';
    pickSource();
  }
  function pagesOf(d) { const out = [], seen = new Set(); const walk = (id, dep) => { const p = d.pages[id]; if (!p || seen.has(id)) return; seen.add(id); out.push({ p, dep }); for (const n of p.nodes) if (n.sub) walk(n.sub, dep + 1); }; walk(d.pages.root ? 'root' : Object.keys(d.pages)[0], 0); for (const p of Object.values(d.pages)) if (!seen.has(p.id)) out.push({ p, dep: 0 }); return out; }
  function pickSource() {
    const s = sources().find(x => x.id === q('#rg-src').value) || sources()[0];
    try { refDoc = s.get(); } catch (e) { console.error(e); msg('参照加载失败：' + (e.message || e), true); return; }
    const ps = pagesOf(refDoc);
    q('#rg-page').innerHTML = ps.map(({ p, dep }) => `<option value="${esc(p.id)}">${'　'.repeat(dep)}${dep ? '⊕ ' : ''}${esc(p.name || '页面')}${p.view ? '（' + esc(p.view) + '）' : ''}</option>`).join('');
    const want = refDoc === doc && refDoc.pages[cur] ? cur : ps[0].p.id;
    q('#rg-page').value = want; pickPage();
  }
  function pickPage() {
    refPid = q('#rg-page').value;
    if (!refDoc || !refDoc.pages[refPid]) return;
    sk = skeleton(refDoc, refPid);
    q('#rg-dialect').value = toDialect(sk, { icons: q('#rg-keepicons').checked });
    q('#rg-sum').textContent = summary(sk);
    rows = mapRows(sk); renderMap();
    drawRef();
    result = null; q('#rg-apply').disabled = true;
  }
  function renderMap() {
    const saved = lsGet().lastMap || {};
    q('#rg-map').innerHTML = `<tr><th>参照层</th><th style="width:34%">新项目对应层</th><th style="width:38%">指定条目（可选，顿号分隔）</th></tr>` +
      rows.map(r => `<tr class="${r.kind}" data-k="${r.key}"><td class="nm">${r.kind === 'lane' ? '└ ' : ''}${esc(r.name.replace(/<br>/g, ' '))} <span class="rg-hint">×${r.count}</span><small title="${esc(r.sample)}">${esc(r.sample)}</small></td><td><input type="text" data-f="name" placeholder="同名或留空" value="${esc((saved[r.name] || {}).name || '')}"></td><td><input type="text" data-f="items" placeholder="${r.kind === 'band' ? '留空沿用' : '留空沿用'}"></td></tr>`).join('');
  }
  function readMap() {
    const m = {};
    root.querySelectorAll('#rg-map tr[data-k]').forEach(tr => { m[tr.dataset.k] = { name: tr.querySelector('[data-f=name]').value, items: tr.querySelector('[data-f=items]').value }; });
    return m;
  }
  function svgOf(d, page, pre) {
    if (!page.nodes.length) return '<div class="rg-empty">（空白页）</div>';
    return withDoc(d, page.id, () => {
      const b = contentBBox(page), pad = 16;
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${b.x - pad} ${b.y - pad} ${b.w + pad * 2} ${b.h + pad * 2}" style="background:${T().bg}">${diagramSVG(page, true, pre)}</svg>`;
    });
  }
  function drawRef() {
    try { q('#rg-refprev').innerHTML = svgOf(refDoc, refDoc.pages[refPid], 'rgr'); }
    catch (e) { console.error(e); q('#rg-refprev').innerHTML = `<div class="rg-empty">预览失败：${esc(e.message || e)}</div>`; }
  }

  /* 目标文档外壳：新建文档模式继承参照的主题与配置；其他模式沿用当前文档 */
  function targetShell() {
    if (apMode() !== 'doc') return doc;
    return { name: q('#rg-name').value.trim() || '参照生成', layout: doc.layout || refDoc.layout, theme: refDoc.theme || doc.theme, statusLabels: Object.assign({}, refDoc.statusLabels || doc.statusLabels), custom: Object.assign({}, doc.custom, refDoc.custom), lastKind: refDoc.lastKind || 'data', jumpStyle: refDoc.jumpStyle, showCodes: !!refDoc.showCodes, meta: refDoc.meta ? Object.assign({}, refDoc.meta, { project: q('#rg-name').value.trim() || refDoc.meta.project }) : undefined, pages: {} };
  }
  function build(dialect) {
    const shell = targetShell();
    const custom0 = doc.custom;
    /* 解析时允许引用参照图的自定义图标（cu:） */
    return withDoc(Object.assign({}, shell, { pages: Object.assign({}, shell.pages) }), 'root', () => {
      doc.custom = Object.assign({}, custom0, refDoc.custom || {});
      const res = TextGen.buildAll(TextGen.parseDialect(dialect), 'root', {});
      styleTransfer(res, sk, refDoc);
      return { res, shell };
    });
  }
  function drawOut() {
    const box = q('#rg-outprev'), rep = q('#rg-rep');
    if (!result) { box.innerHTML = '<div class="rg-empty">点下方“生成预览”</div>'; rep.innerHTML = ''; return; }
    const { res, shell } = result, p = res.pages[0];
    const d = Object.assign({}, shell, { custom: Object.assign({}, doc.custom, refDoc.custom || {}), pages: Object.fromEntries(res.pages.map(x => [x.id, x])) });
    box.innerHTML = svgOf(d, p, 'rgo');
    const s = res.stats, w = [...new Set(res.warnings)];
    rep.innerHTML = `${s.pages > 1 ? `${s.pages} 页（含 ${s.pages - 1} 个展开页）· ` : ''}${s.bands} 个分组带 · ${s.lanes} 层 · ${s.items} 个条目 · ${s.links} 条连接` + (w.length ? `<ul>${w.slice(0, 20).map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : '');
    q('#rg-ressub').textContent = res.title ? '「' + res.title + '」' : '';
  }
  function rebuildFromOut() {
    const t = q('#rg-out').value;
    if (!t.trim()) { result = null; drawOut(); q('#rg-apply').disabled = true; return; }
    try { result = build(t); q('#rg-apply').disabled = !result.res.root.nodes.length; drawOut(); msg(''); }
    catch (e) { console.error(e); result = null; q('#rg-apply').disabled = true; q('#rg-outprev').innerHTML = `<div class="rg-empty">解析出错：${esc(e.message || e)}</div>`; }
  }
  /* 参照方言（可能被用户在 details 中改过） */
  const refDialect = () => q('#rg-dialect').value.trim() || toDialect(sk, { icons: q('#rg-keepicons').checked });

  async function generate() {
    if (busy || !sk) return;
    const content = q('#rg-content').value.trim(), projName = q('#rg-name').value.trim(), map = readMap();
    lsSet({ lastMap: Object.fromEntries(rows.map(r => [r.name, { name: (map[r.key] || {}).name || '' }])) });
    if (eng() === 'rule') {
      let s2 = sk;
      const edited = q('#rg-dialect').value.trim(), orig = toDialect(sk, { icons: q('#rg-keepicons').checked }).trim();
      if (edited && edited !== orig) {
        /* 用户改过参照方言：先按改后的方言重建骨架 */
        try { const tmp = TextGen.buildAll(TextGen.parseDialect(edited), '__rgtmp', {}); const td = { pages: Object.fromEntries(tmp.pages.map(p => [p.id, p])), custom: refDoc.custom || {} }; s2 = skeleton(td, '__rgtmp'); s2.view = sk.view; }
        catch (_) { }
      }
      const out = toDialect(applyMapping(s2, map, projName), { icons: q('#rg-keepicons').checked });
      q('#rg-out').value = out; q('#rg-outbox').open = false; rebuildFromOut();
      const anyItems = Object.values(map).some(m => m.items && m.items.trim());
      msg(anyItems ? '已按层映射套用参照骨架，可在画布上继续修改' : '已套用参照骨架（未填写“指定条目”，条目沿用参照图）');
      return;
    }
    if (!content) { msg('请先填写新项目内容（大模型生成需要依据）', true); q('#rg-content').focus(); return; }
    const cfg = TextGen.llmCfg();
    if (!cfg.base || !cfg.model) { q('#rg-set').classList.add('open'); msg('请先在“大模型设置”中填写接口地址和模型名称', true); return; }
    busy = true; const b = q('#rg-gen'); b.disabled = true; const t0 = Date.now();
    const tick = setInterval(() => msg(`正在请求大模型（${cfg.model}）… ${Math.round((Date.now() - t0) / 1000)} 秒`), 1000);
    msg(`正在请求大模型（${cfg.model}）…`);
    try {
      const user = buildPrompt({ dialect: refDialect(), summary: summary(sk), rows, map, projName, content, extra: q('#rg-extra').value.trim() });
      let out = await TextGen.callLLM(user, TextGen.LLM_SYSTEM + '\n' + REF_RULES, { timeout: 300000 });
      out = out.replace(/^\s*(方言|输出)[:：]\s*\n/, '');
      /* 不存在的图标编号去掉，交给名称自动匹配 */
      const keys = new Set((typeof ICON_LIB !== 'undefined' ? ICON_LIB : []).map(i => i.key));
      out = out.replace(/\s*\{\s*(?:图标|icon)\s*[:：=]\s*lib:([\w-]+)\s*\}/g, (m, k) => keys.has(k) ? m : '');
      if (projName && !/^#\s/m.test(out.split('\n').find(l => l.trim()) || '')) out = '# ' + projName + '\n' + out;
      q('#rg-out').value = out; rebuildFromOut();
      msg(`大模型已生成（${Math.round((Date.now() - t0) / 1000)} 秒），请核对预览，可展开“生成的方言”修改`);
    } catch (e) { msg(e.message || String(e), true); }
    finally { clearInterval(tick); busy = false; b.disabled = false; }
  }

  function applyResult() {
    if (!result) return;
    const { res, shell } = result, mode = apMode();
    Object.assign(doc.custom, refDoc.custom || {});
    const refPage = refDoc.pages[refPid];
    const finish = pg => {
      if (window.Std && (sk.hasTblock || refPage.view)) { if (sk.view) pg.view = sk.view; if (sk.hasTblock) withDoc(doc, pg.id, () => Std.placeTblock(pg)); }
    };
    if (mode === 'doc') {
      checkpoint();
      const d = Object.assign({}, shell, { custom: Object.assign({}, doc.custom, refDoc.custom || {}), pages: {} });
      if (!d.meta) delete d.meta;
      const [r0, ...subs] = res.pages; r0.id = 'root'; r0.name = res.title || shell.name || '总图';
      d.pages.root = r0; subs.forEach(p => d.pages[p.id] = p);
      d.name = res.title || shell.name;
      loadDoc(d); finish(d.pages.root); render(); fit();
    } else {
      TextGen.apply(res, mode === 'page' ? 'page' : 'replace');
      finish(P()); render(); fit();
    }
    close();
    toast(`已按参照生成：${res.stats.bands} 个分组带、${res.stats.items} 个条目、${res.stats.links} 条连接（Ctrl+Z 可撤销）`);
  }

  async function openRefFile(f) {
    if (!f) return;
    const ext = (f.name.match(/\.([^.]+)$/) || [])[1]?.toLowerCase();
    try {
      let d;
      if (ext === 'json') { const o = JSON.parse(await f.text()); d = o.doc || o; if (!d.pages) throw new Error('不是织图工程文件'); d.name = d.name || f.name.replace(/\.[^.]+$/, ''); }
      else {
        const dio = /^(drawio|xml)$/.test(ext);
        if (dio ? !window.DrawIO : !window.Importer) throw new Error('导入模块未加载');
        msg('正在解析 ' + f.name + ' …');
        const r = dio ? await DrawIO.fromFile(f) : await Importer.fromFile(f);
        if (!r.pages.length) throw new Error('文件中没有可识别的图形');
        d = refDocFromImport(r, f.name);
        if (r.warnings && r.warnings.length) console.info('导入提示', r.warnings);
      }
      d.custom = d.custom || {}; d.statusLabels = d.statusLabels || Object.assign({}, doc.statusLabels);
      extDocs.unshift(d); if (extDocs.length > 5) extDocs.pop();
      fillSources('ext0'); msg(`已打开参照：${f.name}（${Object.keys(d.pages).length} 页）`);
    } catch (e) { console.error(e); msg('无法打开：' + (e.message || e), true); }
  }
  async function readContentFile(f) {
    try {
      const t = /\.docx$/i.test(f.name) ? await docxText(await f.arrayBuffer()) : await f.text();
      const ta = q('#rg-content'); ta.value = (ta.value.trim() ? ta.value.trim() + '\n\n' : '') + t.trim();
      if (!q('#rg-name').value.trim()) { const h = t.split('\n').map(s => s.replace(/^#+\s*/, '').trim()).find(Boolean); if (h && h.length <= 30) q('#rg-name').value = h; }
      msg(`已导入：${f.name}（${t.length} 字）`);
    } catch (e) { msg('读取失败：' + (e.message || e), true); }
  }
  async function testConn() {
    const m = q('#rg-test-msg'); m.textContent = '正在测试…'; m.classList.remove('err');
    saveSet();
    try { const t = await TextGen.callLLM('请只回复两个字：连通', '你是连通性测试助手。', { timeout: 30000, maxTokens: 16 }); m.textContent = '连接正常，模型回复：' + t.slice(0, 40); }
    catch (e) { m.textContent = e.message || String(e); m.classList.add('err'); }
  }
  function saveSet() { TextGen.setLlmCfg({ base: q('#rg-base').value.trim(), model: q('#rg-model').value.trim(), key: q('#rg-key').value.trim() }); }

  function ensureUI() {
    if (root) return;
    const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    root = document.createElement('div'); root.id = 'rg'; root.innerHTML = HTML; document.body.appendChild(root);
    const c = TextGen.llmCfg(); q('#rg-base').value = c.base; q('#rg-model').value = c.model; q('#rg-key').value = c.key;
    const s = lsGet(); if (s.eng) { const r = q(`input[name=rg-eng][value=${s.eng}]`); if (r) r.checked = true; } if (s.ap) { const r = q(`input[name=rg-ap][value=${s.ap}]`); if (r) r.checked = true; }
    root.addEventListener('keydown', e => {
      e.stopPropagation();
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); generate(); }
    });
    root.addEventListener('keyup', e => e.stopPropagation());
    window.addEventListener('keydown', e => {
      if (!root.classList.contains('open') || root.contains(e.target)) return;
      e.stopPropagation();
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if (['Delete', 'Backspace', ' '].includes(e.key) || e.ctrlKey || e.metaKey) { if (!/^[cv]$/i.test(e.key)) e.preventDefault(); }
    }, true);
    root.addEventListener('mousedown', e => { if (e.target === root) close(); });
    q('#rg-close').onclick = close;
    q('#rg-gear').onclick = () => q('#rg-set').classList.toggle('open');
    ['#rg-base', '#rg-model', '#rg-key'].forEach(x => q(x).addEventListener('change', saveSet));
    q('#rg-test').onclick = testConn;
    q('#rg-src').onchange = pickSource;
    q('#rg-page').onchange = pickPage;
    q('#rg-keepicons').onchange = () => { q('#rg-dialect').value = toDialect(sk, { icons: q('#rg-keepicons').checked }); };
    q('#rg-file').onclick = () => q('#rg-f').click();
    q('#rg-f').onchange = e => { openRefFile(e.target.files[0]); e.target.value = ''; };
    q('#rg-cfile').onclick = () => q('#rg-cf').click();
    q('#rg-cf').onchange = e => { const f = e.target.files[0]; if (f) readContentFile(f); e.target.value = ''; };
    const drop = (el, fn) => {
      el.addEventListener('dragover', e => { if ([...(e.dataTransfer?.types || [])].includes('Files')) { e.preventDefault(); el.classList.add('rg-drop'); } });
      el.addEventListener('dragleave', () => el.classList.remove('rg-drop'));
      el.addEventListener('drop', e => { el.classList.remove('rg-drop'); const f = e.dataTransfer?.files?.[0]; if (f) { e.preventDefault(); fn(f); } });
    };
    drop(q('#rg-refprev'), openRefFile); drop(q('#rg-content'), readContentFile);
    q('#rg-eng').addEventListener('change', () => { lsSet({ eng: eng() }); q('#rg-gen').textContent = eng() === 'llm' ? '生成预览' : '套用骨架'; });
    q('#rg-ap').addEventListener('change', () => { lsSet({ ap: apMode() }); if (q('#rg-out').value.trim()) rebuildFromOut(); });
    q('#rg-gen').onclick = generate;
    q('#rg-apply').onclick = applyResult;
    q('#rg-out').addEventListener('input', () => { clearTimeout(ptimer); ptimer = setTimeout(rebuildFromOut, 350); });
    q('#rg-gen').textContent = eng() === 'llm' ? '生成预览' : '套用骨架';
  }
  let lastFocus = null;
  function open() {
    if (!window.TextGen) { toast('文字成图模块未加载'); return; }
    ensureUI(); lastFocus = document.activeElement;
    if ($('#editor') && $('#editor').style.display === 'block' && typeof commitEdit === 'function') commitEdit();
    root.classList.add('open');
    const keep = q('#rg-src').value && q('#rg-src').value !== 'cur';
    if (!keep) fillSources('cur'); else pickSource();
    msg('');
  }
  function close() { if (!root) return; root.classList.remove('open'); if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (_) { } }

  window.openRefGen = open;
  window.RefGen = { skeleton, toDialect, summary, mapRows, applyMapping, buildPrompt, docxText, REF_RULES, open, close, openRefFile, isOpen: () => !!(root && root.classList.contains('open')) };
})();
