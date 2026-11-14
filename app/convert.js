/* ============ 织图 · 格式转换（PPT／Visio／draw.io／织图工程 互转） ============
 * 不改动当前画布：每个源文件读入一份临时文档，按原页面顺序（一页一张幻灯片／一页）导出为目标格式，
 * 不添加跳转入口框；可选“保持原排版”或“按织图版式美化”。多个文件逐个下载，文件名沿用源文件名。
 * 依赖：Importer（importers.js）、DrawIO（drawio.js）、app.js 的 exportPPTX／exportVSDX／exportSVGString／rasterize／saveFile／pagesInOrder 等全局。 */
(function () {
  'use strict';
  const TARGETS = [
    ['pptx', 'PowerPoint（.pptx）', '一页一张幻灯片，原生可编辑形状'],
    ['vsdx', 'Visio（.vsdx）', '一页一个 Visio 页面'],
    ['drawio', 'draw.io（.drawio）', '一页一个 draw.io 页面，可在 draw.io 继续编辑'],
    ['png', 'PNG 图片（每页一张）', '透明背景，2 倍清晰度'],
    ['json', '织图工程（.json）', '在织图中继续编辑'],
  ];
  const IN_EXT = /\.(pptx|potx|ppsx|vsdx|vssx|vstx|drawio|xml|json)$/i;
  const LS = 'hongtu.convert.v1';
  const lsGet = () => { try { return JSON.parse(localStorage.getItem(LS) || '{}') || {}; } catch (_) { return {}; } };
  const lsSet = o => { try { localStorage.setItem(LS, JSON.stringify(Object.assign(lsGet(), o))); } catch (_) { } };
  const baseName = n => String(n || '文件').replace(/\.[^.]+$/, '');

  async function readDoc(f, keepColors) {
    const ext = (f.name.split('.').pop() || '').toLowerCase();
    if (ext === 'ppt' || ext === 'vsd') throw new Error('旧版二进制格式，请先在 PowerPoint／Visio 中另存为 .pptx／.vsdx');
    let pages, custom = {}, extra = {};
    if (ext === 'json') {
      const o = JSON.parse(await f.text()), d = o.doc || o;
      if (!d.pages || !d.pages.root) throw new Error('不是织图工程文件');
      return adoptPages(Object.assign({ custom: {}, statusLabels: { base: '已建', new: '本期新增', key: '重点建设' } }, d));
    }
    if (ext === 'drawio' || ext === 'xml') { const r = await DrawIO.importText(await f.text(), { keepColors }); pages = r.pages; custom = r.custom; if (r.docSettings) extra = r.docSettings; }
    else {
      const buf = await f.arrayBuffer();
      const r = /^(pptx|potx|ppsx)$/.test(ext) ? await Importer.fromPPTX(buf, { keepColors }) : await Importer.fromVSDX(buf, { keepColors });
      pages = r.pages; custom = r.custom || {};
    }
    if (!pages || !pages.length) throw new Error('文件中没有可识别的图形');
    const d = Object.assign({ name: baseName(f.name), theme: 'report', statusLabels: { base: '已建', new: '本期新增', key: '重点建设' }, custom, lastKind: 'data', pages: {} }, extra);
    const old0 = pages[0].id; pages[0].id = 'root';
    for (const p of pages) for (const n of p.nodes) if (n.sub === old0) n.sub = 'root';
    pages.forEach(p => d.pages[p.id] = p);
    return adoptPages(d);
  }

  /* 在临时文档上执行导出：临时替换 doc／cur／saveFile，导出后原样恢复 */
  async function exportDoc(d, target, outBase, opts) {
    const sDoc = doc, sCur = cur, sStack = typeof stack !== 'undefined' ? stack : null, sSave = saveFile, sTheme = d.theme;
    const files = [];
    if (opts.theme) d.theme = opts.theme;
    if (opts.beautify && !d.layout && sDoc.layout) d.layout = sDoc.layout;
    doc = d; cur = 'root'; try { stack = ['root']; } catch (_) { }
    saveFile = async (name, data) => { files.push({ name, blob: data instanceof Blob ? data : new Blob([data]) }); };
    try {
      if (opts.beautify) for (const p of Object.values(d.pages)) { cur = p.id; beautify(p); }
      cur = 'root';
      if (target === 'pptx') await exportPPTX();
      else if (target === 'vsdx') await exportVSDX();
      else if (target === 'drawio') await DrawIO.exportFile();
      else if (target === 'json') { const o = Object.assign({}, d); delete o.pageOrder; files.push({ name: 'x.json', blob: new Blob([JSON.stringify({ format: 'hongtu', version: 1, doc: o })]) }); }
      else if (target === 'png') {
        const list = pagesInOrder();
        for (let i = 0; i < list.length; i++) {
          const p = list[i]; cur = p.id;
          const { str, w, h } = exportSVGString(p, false);
          files.push({ name: `x-${i + 1}.png`, page: p.name, blob: await rasterize(str, w, h, 2) });
        }
      }
    } finally { doc = sDoc; cur = sCur; if (sStack) try { stack = sStack; } catch (_) { } saveFile = sSave; d.theme = sTheme; }
    /* 统一用源文件名命名 */
    const ext = target === 'png' ? 'png' : target === 'json' ? 'jingwei.json' : target;
    return files.map((f, i) => ({ name: (target === 'png' && files.length > 1 ? `${outBase}-${String(i + 1).padStart(2, '0')}${f.page && f.page !== '总图' ? '-' + f.page : ''}` : outBase).replace(/[\\/:*?"<>|]/g, '_') + '.' + ext, blob: f.blob }));
  }

  /* ---------------- 界面 ---------------- */
  const CSS = `
#cv{position:fixed;top:0;right:0;bottom:0;left:0;z-index:25;background:rgba(10,15,22,.5);display:none;align-items:center;justify-content:center;padding:16px}
#cv.open{display:flex}
#cv .cv-box{background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:12px;width:min(720px,100%);max-height:min(860px,100%);display:flex;flex-direction:column;overflow:hidden;box-shadow:0 18px 48px rgba(0,0,0,.25)}
#cv .cv-head{display:flex;align-items:center;gap:8px;padding:12px 14px;border-bottom:1px solid var(--line)}
#cv .cv-head strong{font-size:15px}
#cv .cv-sub{color:var(--muted);font-size:12px}
#cv .cv-body{padding:12px 14px;overflow:auto;display:flex;flex-direction:column;gap:12px}
#cv .cv-drop{border:2px dashed var(--line);border-radius:10px;padding:18px;text-align:center;color:var(--muted);line-height:1.8;cursor:pointer}
#cv .cv-drop.on{border-color:var(--accent);background:var(--accent-soft)}
#cv .cv-drop b{color:var(--fg)}
#cv .cv-list{display:flex;flex-direction:column;gap:4px;font-size:12.5px}
#cv .cv-item{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:8px;align-items:center;padding:5px 8px;border:1px solid var(--line);border-radius:6px}
#cv .cv-item .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#cv .cv-item .st{color:var(--muted);white-space:nowrap}
#cv .cv-item .st.ok{color:#0E9F8E}
#cv .cv-item .st.err{color:var(--danger);white-space:normal}
#cv .cv-item button{padding:0 8px;border-color:var(--line)}
#cv .cv-tg{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:6px}
#cv .cv-tg label{display:flex;gap:8px;align-items:flex-start;border:1px solid var(--line);border-radius:8px;padding:8px 10px;cursor:pointer;line-height:1.4}
#cv .cv-tg label.on{border-color:var(--accent);background:var(--accent-soft)}
#cv .cv-tg small{display:block;color:var(--muted);font-size:11.5px}
#cv .cv-opt{display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:12.5px}
#cv .cv-opt label{display:flex;gap:5px;align-items:center;cursor:pointer;white-space:nowrap}
#cv h5{margin:0;font-size:12.5px;color:var(--muted);font-weight:500}
#cv .cv-foot{display:flex;gap:10px;align-items:center;padding:10px 14px;border-top:1px solid var(--line)}
#cv .cv-msg{font-size:12px;color:var(--muted)}
#cv .cv-hint{font-size:12px;color:var(--muted);line-height:1.7}
@media (max-width:640px){#cv{padding:0}#cv .cv-box{border-radius:0;height:100%;max-height:100%}}`;
  const HTML = `
<div class="cv-box" role="dialog" aria-modal="true" aria-labelledby="cv-title">
  <div class="cv-head"><strong id="cv-title">格式转换</strong><span class="cv-sub">PPT、Visio、draw.io、织图工程互转，不影响当前画布</span><span style="flex:1"></span><button id="cv-close">关闭</button></div>
  <div class="cv-body">
    <div class="cv-drop" id="cv-drop" tabindex="0"><b>点击选择文件，或把文件拖到这里</b><br>支持 .vsdx　.pptx　.drawio　.json，可一次选多个；转换完成后可直接继续添加</div>
    <input type="file" id="cv-f" multiple accept=".pptx,.potx,.ppsx,.vsdx,.vssx,.vstx,.drawio,.xml,.json,.ppt,.vsd" hidden>
    <div class="cv-list" id="cv-list"></div>
    <h5>转换为</h5>
    <div class="cv-tg" id="cv-tg">${TARGETS.map(([k, t, s]) => `<label><input type="radio" name="cv-t" value="${k}"><span>${t}<small>${s}</small></span></label>`).join('')}</div>
    <h5>选项</h5>
    <div class="cv-opt">
      <label title="逐形状还原位置、几何、字体字号、颜色与箭头"><input type="radio" name="cv-lay" value="keep" checked> 保持原排版（原样还原）</label>
      <label title="读成织图的分层、框与连线，按织图版式重新对齐、等距"><input type="radio" name="cv-lay" value="beauty"> 按织图版式美化</label>
    </div>
    <div class="cv-opt" id="cv-o-keep">
      <label>幻灯片尺寸 <select id="cv-fit"><option value="page">与原页面相同（字号不变）</option><option value="169">16:9 宽屏（等比缩放）</option></select></label>
    </div>
    <div class="cv-opt" id="cv-o-beauty" hidden>
      <label title="保留源文件中的填充色与线条色"><input type="checkbox" id="cv-color" checked> 保留原配色</label>
      <label>主题 <select id="cv-theme"></select></label>
    </div>
    <div class="cv-hint" id="cv-hint"></div>
  </div>
  <div class="cv-foot"><span class="cv-msg" id="cv-msg"></span><span style="flex:1"></span><button id="cv-clear">清空列表</button><button id="cv-go" class="primary" disabled>开始转换</button></div>
</div>`;
  let root = null, items = [], busy = false;
  const q = s => root.querySelector(s);
  const target = () => (q('input[name=cv-t]:checked') || {}).value;
  const msg = t => q('#cv-msg').textContent = t || '';
  function srcExt(name) { const e = (name.split('.').pop() || '').toLowerCase(); return /^(pptx|potx|ppsx)$/.test(e) ? 'pptx' : /^(vsdx|vssx|vstx)$/.test(e) ? 'vsdx' : /^(drawio|xml)$/.test(e) ? 'drawio' : e; }
  const HINT_KEEP = '<b>保持原排版</b>：Visio → PowerPoint 逐形状原样还原——位置、尺寸、几何、填充、线型、箭头、图片，以及每段文字的字体、字号、粗斜体、颜色、对齐与竖排；原文件一页对应一张幻灯片，不加任何入口框。其他格式组合按原位置和尺寸转换，形状换成最接近的织图形状。';
  const HINT_BEAUTY = '<b>按织图版式美化</b>：先识别为织图的分层、框与连线，再按织图版式重新排布（框按文字自动收紧、等距对齐、减少交叉），可换主题；适合需要统一风格的图。';
  const HINT_TAIL = '图表、SmartArt 不转换；.ppt／.vsd 请先另存为 .pptx／.vsdx。';
  const isBeauty = () => (q('input[name=cv-lay]:checked') || {}).value === 'beauty';
  function syncOpts() {
    const b = isBeauty();
    q('#cv-o-keep').hidden = b; q('#cv-o-beauty').hidden = !b;
    setMarkup(q('#cv-hint'), (b ? HINT_BEAUTY : HINT_KEEP) + HINT_TAIL);
  }
  /* 原样转换路径：Visio → PowerPoint 且保持原排版 */
  const rawPath = (it, t) => t === 'pptx' && !isBeauty() && srcExt(it.f.name) === 'vsdx' && window.VsdxRaw;
  function renderList() {
    setMarkup(q('#cv-list'), items.map((it, i) => `<div class="cv-item"><span class="nm" title="${esc(it.f.name)}">${esc(it.f.name)}</span><span class="st ${it.cls || ''}">${esc(it.st || '待转换')}</span><button data-rm="${i}" title="移出列表" ${busy ? 'disabled' : ''}>×</button></div>`).join(''));
    const t = target();
    q('#cv-tg').querySelectorAll('label').forEach(l => l.classList.toggle('on', l.querySelector('input').checked));
    q('#cv-go').disabled = busy || !items.length || !t;
    if (items.length && t) { const same = items.filter(it => srcExt(it.f.name) === t).length; msg(same ? `${same} 个文件已是目标格式，将按织图重新写出` : `${items.length} 个文件待转换`); }
    else msg(items.length ? '请选择目标格式' : '');
  }
  function addFiles(list) {
    const bad = [];
    if (busy) { toast('正在转换，请稍候再添加'); return; }
    /* 上一批已全部处理完：新加入文件时开始新的一批（已完成的自动移出） */
    if (items.length && items.every(it => it.cls === 'ok' || it.cls === 'err')) items = items.filter(it => it.cls === 'err');
    for (const f of list) {
      if (!IN_EXT.test(f.name) && !/\.(ppt|vsd)$/i.test(f.name)) { bad.push(f.name); continue; }
      const old = items.findIndex(it => it.f.name === f.name && it.f.size === f.size);
      if (old >= 0) items[old] = { f }; else items.push({ f });
    }
    renderList(); if (bad.length) toast('不支持的文件：' + bad.join('、'));
  }
  async function run() {
    const t = target(); if (!t || !items.length || busy) return;
    const keepColors = q('#cv-color').checked, beauty = isBeauty(), theme = q('#cv-theme').value, fit = q('#cv-fit').value;
    lsSet({ target: t, beauty, keepColors, theme, fit });
    for (const it of items) { it.cls = ''; it.st = ''; }
    busy = true; renderList();
    let ok = 0, out = 0;
    for (const it of items) {
      it.st = '正在转换…'; it.cls = ''; renderList();
      try {
        if (rawPath(it, t)) {
          const parsed = await VsdxRaw.parse(await it.f.arrayBuffer());
          const blob = await VsdxRaw.toPPTX(parsed, { fit });
          await saveFile(baseName(it.f.name) + '.pptx', blob);
          it.st = `完成 · 原样还原 ${parsed.pages.length} 页` + (parsed.warnings.length ? '（' + parsed.warnings.join('；') + '）' : ''); it.cls = 'ok'; ok++; out++;
          renderList(); continue;
        }
        const d = await readDoc(it.f, beauty ? keepColors : true);
        const files = await exportDoc(d, t, baseName(it.f.name), { beautify: beauty, theme });
        for (const f of files) await saveFile(f.name, f.blob);
        it.st = `完成 · ${Object.keys(d.pages).length} 页 → ${files.length} 个文件`; it.cls = 'ok'; ok++; out += files.length;
      } catch (e) { console.error(e); it.st = '失败：' + (typeof friendlyErr === 'function' ? friendlyErr(e) : (e.message || e)); it.cls = 'err'; }
      renderList();
    }
    busy = false; renderList();
    msg(`已完成 ${ok}／${items.length} 个，输出 ${out} 个文件（在浏览器下载目录）。可继续添加文件，或改选项后再次转换`);
  }
  function ensureUI() {
    if (root) return;
    const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    root = document.createElement('div'); root.id = 'cv'; setMarkup(root, HTML); document.body.appendChild(root);
    setMarkup(q('#cv-theme'), Object.entries(THEMES).map(([k, v]) => `<option value="${k}">${v.name}</option>`).join(''));
    const s = lsGet();
    if (s.target) { const r = q(`input[name=cv-t][value=${s.target}]`); if (r) r.checked = true; }
    if (s.beauty) q('input[name=cv-lay][value=beauty]').checked = true;
    if (s.keepColors === false) q('#cv-color').checked = false;
    if (s.fit) q('#cv-fit').value = s.fit;
    root.querySelectorAll('input[name=cv-lay]').forEach(r => r.addEventListener('change', () => { syncOpts(); renderList(); }));
    syncOpts();
    q('#cv-theme').value = s.theme && THEMES[s.theme] ? s.theme : 'report';
    const drop = q('#cv-drop');
    drop.onclick = () => q('#cv-f').click();
    drop.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); q('#cv-f').click(); } };
    q('#cv-f').onchange = e => { addFiles([...e.target.files]); e.target.value = ''; };
    drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('on'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('on'));
    drop.addEventListener('drop', e => { e.preventDefault(); drop.classList.remove('on'); addFiles([...(e.dataTransfer?.files || [])]); });
    root.addEventListener('dragover', e => e.preventDefault());
    root.addEventListener('drop', e => { if (!drop.contains(e.target)) { e.preventDefault(); addFiles([...(e.dataTransfer?.files || [])]); } });
    q('#cv-list').addEventListener('click', e => { const b = e.target.closest('[data-rm]'); if (b && !busy) { items.splice(+b.dataset.rm, 1); renderList(); } });
    q('#cv-tg').addEventListener('change', renderList);
    q('#cv-clear').onclick = () => { if (!busy) { items = []; renderList(); } };
    q('#cv-go').onclick = run;
    q('#cv-close').onclick = close;
    root.addEventListener('mousedown', e => { if (e.target === root && !busy) close(); });
    root.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Escape' && !busy) close(); });
    root.addEventListener('keyup', e => e.stopPropagation());
  }
  function open() { ensureUI(); root.classList.add('open'); renderList(); setTimeout(() => q('#cv-drop').focus(), 30); }
  function close() { if (root) root.classList.remove('open'); }
  window.openConvert = open;
  window.Convert = { open, close, readDoc, exportDoc, TARGETS, isOpen: () => !!(root && root.classList.contains('open')) };
})();
