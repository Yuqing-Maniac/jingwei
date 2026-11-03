/* 经纬织图 桌面版：标题栏、窗口控制、首页、本地文件读写（仅在桌面外壳中生效） */
(function () {
  const D = window.jwDesk; if (!D) return;
  document.body.classList.add('desk');
  document.documentElement.setAttribute('data-theme', 'light');   // 固定浅色界面，不受系统深色模式影响
  const $ = s => document.querySelector(s);
  const h = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstChild; };
  const IC = {
    min: '<svg viewBox="0 0 12 12"><path d="M1 6.5h10" stroke="currentColor" stroke-width="1.2"/></svg>',
    max: '<svg viewBox="0 0 12 12"><rect x="1.5" y="1.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    res: '<svg viewBox="0 0 12 12"><rect x="1.5" y="3.5" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M3.5 3.5V1.5h7v7h-2" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    close: '<svg viewBox="0 0 12 12"><path d="M1.5 1.5l9 9M10.5 1.5l-9 9" stroke="currentColor" stroke-width="1.2"/></svg>',
    home: '<svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 7.5L8 2.5l6 5M3.8 6.3V13.5h3V10h2.4v3.5h3V6.3" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>',
  };
  const wc = () => h(`<div class="jw-wc"><button data-w="min" title="最小化">${IC.min}</button><button data-w="max" title="最大化">${IC.max}</button><button data-w="close" class="x" title="关闭">${IC.close}</button></div>`);
  const bindWc = el => el.addEventListener('click', e => { const b = e.target.closest('[data-w]'); if (b) D.win(b.dataset.w); });

  /* ---------- 标题栏 ---------- */
  const H = $('header');
  const fileChip = h('<div id="jw-file" title=""></div>');
  $('.brand').after(fileChip);
  const home = h(`<button id="jw-home" title="首页（最近文件、新建、模板）">${IC.home}</button>`);
  fileChip.after(home);
  const w1 = wc(); H.appendChild(w1); bindWc(w1);
  H.addEventListener('dblclick', e => { if (e.target === H || e.target.closest('.brand,#jw-file,.spacer')) D.win('max'); });
  D.on('jw:win-state', s => {
    document.body.classList.toggle('jw-max', s.max);
    document.querySelectorAll('.jw-wc [data-w=max]').forEach(b => { b.innerHTML = s.max ? IC.res : IC.max; b.title = s.max ? '还原' : '最大化'; });
  });

  for (const id of ['b-undo', 'b-redo']) { const b = $('#' + id); if (b) { const m = b.textContent.trim().match(/^(\S+)\s+(.+)$/); if (m) b.innerHTML = `<i>${m[1]}</i><span>${m[2]}</span>`; } }
  /* 窄窗口：减少交叉、编队、规范收进“更多” */
  const more = h(`<div class="menu" id="jw-more"><button title="更多功能">更多 ▾</button><div class="dd"></div></div>`);
  for (const id of ['b-cross', 'b-form', 'b-std']) { const o = $('#' + id); if (!o) continue; const c = h(`<button>${o.textContent}<small>${(o.title.match(/Ctrl\+[^；;，]+/) || [''])[0]}</small></button>`); c.onclick = () => { more.classList.remove('open'); o.click(); }; more.querySelector('.dd').appendChild(c); }
  more.firstChild.onclick = e => { e.stopPropagation(); more.classList.toggle('open'); };
  $('#m-export').before(more);
  /* ---------- 文档状态 ---------- */
  let curPath = null, dirty = false;
  const base = p => p.split(/[\\/]/).pop();
  const docTitle = () => curPath ? base(curPath) : ((typeof doc !== 'undefined' && doc && (doc.name || (doc.pages && doc.pages.root && doc.pages.root.name))) || '未命名');
  function upd() {
    const t = docTitle();
    fileChip.textContent = t; fileChip.title = curPath || '尚未保存到文件';
    fileChip.classList.toggle('dirty', dirty);
    document.title = (dirty ? '● ' : '') + t + ' - 经纬织图'; D.title(document.title);
  }
  window.jwRefreshTitle = upd;
  /* 文档名、页面名在失焦时记撤销，不走 checkpoint，这里补未保存标记。 */
  window.jwTouch = function () { if (!dirty) { dirty = true; upd(); } };
  const _cp = window.checkpoint;
  window.checkpoint = checkpoint = function () { if (!dirty) { dirty = true; upd(); } return _cp.apply(this, arguments); };
  const _ld = window.loadDoc;
  window.loadDoc = loadDoc = function () { const r = _ld.apply(this, arguments); curPath = null; dirty = false; upd(); return r; };

  /* ---------- 保存 ---------- */
  let batchDir = null;
  const toBuf = async data => data instanceof Blob ? await data.arrayBuffer() : (typeof data === 'string' ? new TextEncoder().encode(data).buffer : data);
  window.saveFile = saveFile = async function (name, data) {
    const buf = await toBuf(data);
    try {
      if (batchDir) { const p = await D.writeIn(batchDir, name, buf); toast('已保存：' + base(p)); return p; }
      const p = await D.save(name, buf, { title: '导出' });
      if (p) toast('已保存到：' + p); else toast('已取消保存');
      return p;
    } catch (e) { toast('保存失败：' + (e && e.message || e)); return null; }
  };
  async function saveProj(asNew) {
    const name = fname('json').replace(/\.json$/, '.jingwei.json');
    const data = new TextEncoder().encode(projectJSON()).buffer;
    try {
      const p = await D.save(name, data, { path: asNew ? null : curPath, title: asNew ? '另存为' : '保存工程' });
      if (!p) { toast('已取消保存'); return null; }
      curPath = p; dirty = false; upd(); toast('已保存：' + p); return p;
    } catch (e) { toast('保存失败：' + (e && e.message || e)); return null; }
  }
  window.saveProject = saveProject = () => saveProj(false);
  window.saveProjectAs = saveProjectAs = function () { return saveProj(true); };
  $('#b-save').onclick = () => saveProj(false);
  $('#b-saveas').onclick = () => saveProj(true);
  $('#b-save').title = '保存工程（.jingwei.json）　Ctrl+S；另存为 Ctrl+Shift+S';
  document.addEventListener('keydown', e => {
    const k = e.key.toLowerCase(), mod = e.ctrlKey || e.metaKey;
    if (mod && e.shiftKey && k === 's') { e.preventDefault(); e.stopPropagation(); saveProj(true); }
    else if (e.key === 'F11') { e.preventDefault(); D.win('full'); }
  }, true);

  /* 格式转换：批量结果先选一次文件夹 */
  document.addEventListener('click', async e => {
    const go = e.target.closest('#cv-go'); if (!go || go.__jwOk) return;
    e.preventDefault(); e.stopImmediatePropagation();
    const dir = await D.pickDir('选择转换结果的保存文件夹'); if (!dir) { toast('已取消'); return; }
    batchDir = dir; go.__jwOk = true; go.click(); go.__jwOk = false;
    const msg = $('#cv-msg');
    const done = () => { batchDir = null; ob && ob.disconnect(); };
    const ob = msg ? new MutationObserver(() => { if (/已完成|失败|出错/.test(msg.textContent)) { done(); toast('转换结果已保存到：' + dir); D.reveal(dir + '/'); } }) : null;
    if (ob) ob.observe(msg, { childList: true, characterData: true, subtree: true }); else setTimeout(done, 60000);
  }, true);

  /* ---------- 打开 ---------- */
  async function openPath(p) {
    try {
      const r = await D.read(p);
      if (/\.json$/i.test(r.name)) {
        const o = JSON.parse(new TextDecoder().decode(r.data)); const d = o.doc || o;
        if (!d.pages || !d.pages.root) throw new Error('不是经纬织图工程文件');
        _cp(); loadDoc(d); curPath = r.path; dirty = false; upd(); toast('已打开：' + r.name);
      } else {
        await openForeign(new File([r.data], r.name)); upd();
      }
      hideStart();
    } catch (e) { toast('打开失败：' + (e && e.message || e)); }
  }
  async function openFlow() { const p = await D.openDialog(); if (p) openPath(p); }
  $('#b-open').onclick = openFlow;
  $('#f-open').click = openFlow;   // Ctrl+O 走同一流程
  D.on('jw:open-path', p => openPath(p));
  const drop = h('<div id="jw-drop"><div>松开即可打开</div></div>'); document.body.appendChild(drop);
  const isFileDrag = e => e.dataTransfer && [...e.dataTransfer.types].includes('Files');
  window.addEventListener('dragover', e => { if (isFileDrag(e)) { e.preventDefault(); drop.classList.add('on'); } }, true);
  window.addEventListener('dragleave', e => { if (!e.relatedTarget) drop.classList.remove('on'); }, true);
  window.addEventListener('drop', e => {
    drop.classList.remove('on');
    if (!isFileDrag(e)) return;
    const f = e.dataTransfer.files[0];
    if (f && f.path && /\.(json|pptx|vsdx|drawio|xml)$/i.test(f.name)) { e.preventDefault(); e.stopPropagation(); openPath(f.path); }
  }, true);

  /* ---------- 关闭前确认 ---------- */
  D.on('jw:before-close', async () => {
    if (!dirty) return D.closeNow();
    const r = await D.confirmClose(docTitle());
    if (r === 'discard') D.closeNow();
    else if (r === 'save') { const p = await saveProj(false); if (p) D.closeNow(); }
  });

  /* ---------- 首页 ---------- */
  const SVG = {
    new: '<svg viewBox="0 0 32 32"><rect x="6" y="4" width="20" height="24" rx="3" fill="none" stroke="#9fd0ff" stroke-width="2"/><path d="M16 11v10M11 16h10" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg>',
    open: '<svg viewBox="0 0 32 32"><path d="M4 9a2 2 0 012-2h6l3 3h11a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2z" fill="none" stroke="#9fd0ff" stroke-width="2"/><path d="M11 18h10M17 14l4 4-4 4" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    tpl: '<svg viewBox="0 0 32 32"><rect x="4" y="5" width="10" height="9" rx="2" fill="none" stroke="#9fd0ff" stroke-width="2"/><rect x="18" y="5" width="10" height="9" rx="2" fill="none" stroke="#9fd0ff" stroke-width="2"/><rect x="4" y="18" width="10" height="9" rx="2" fill="none" stroke="#9fd0ff" stroke-width="2"/><rect x="18" y="18" width="10" height="9" rx="2" fill="#2bd4c4" stroke="#2bd4c4" stroke-width="2"/></svg>',
    text: '<svg viewBox="0 0 32 32"><path d="M5 8h12M5 13h9M5 18h11M5 23h7" stroke="#9fd0ff" stroke-width="2" stroke-linecap="round"/><rect x="20" y="10" width="8" height="5" rx="1.5" fill="#2bd4c4"/><rect x="20" y="19" width="8" height="5" rx="1.5" fill="#fff"/><path d="M24 15v4" stroke="#fff" stroke-width="1.6"/></svg>',
    conv: '<svg viewBox="0 0 32 32"><rect x="3" y="7" width="11" height="14" rx="2" fill="none" stroke="#9fd0ff" stroke-width="2"/><rect x="18" y="11" width="11" height="14" rx="2" fill="none" stroke="#fff" stroke-width="2"/><path d="M12 25c4 2 8 1 10-3M20 7c-4-2-8-1-10 3" fill="none" stroke="#f2b54a" stroke-width="1.8" stroke-linecap="round"/></svg>',
    demo: '<svg viewBox="0 0 32 32"><rect x="4" y="5" width="24" height="6" rx="1.5" fill="none" stroke="#9fd0ff" stroke-width="2"/><rect x="4" y="14" width="24" height="6" rx="1.5" fill="none" stroke="#9fd0ff" stroke-width="2"/><rect x="4" y="23" width="24" height="5" rx="1.5" fill="none" stroke="#9fd0ff" stroke-width="2"/><circle cx="12" cy="17" r="2" fill="#f2b54a"/><circle cx="21" cy="8" r="2" fill="#2bd4c4"/></svg>',
  };
  const logo = $('.brand .logo') ? $('.brand .logo').src : '';
  const S = h(`<div id="jw-start"><div class="gridbg"></div><div class="bar"></div>
    <div class="col l"><img class="logo" src="${logo}" alt=""><h1>经纬织图</h1><div class="tag">纵横经纬　织网成图</div>
      <div class="ver" id="jw-ver"></div><button class="go" id="jw-go">进入画布 →</button></div>
    <div class="col r"><h2>开始</h2><div class="cards">
      <button class="card pri" data-a="new">${SVG.new}<b>新建空白图</b><span>从分层框架开始画</span></button>
      <button class="card" data-a="open">${SVG.open}<b>打开文件</b><span>工程文件、PPT、Visio、draw.io</span></button>
      <button class="card" data-a="tpl">${SVG.tpl}<b>从模板新建</b><span>20 套模板，含 11 种规范视图</span></button>
      <button class="card" data-a="text">${SVG.text}<b>文字成图</b><span>粘贴文字或 Markdown，自动成图</span></button>
      <button class="card" data-a="conv">${SVG.conv}<b>格式转换</b><span>Visio 转 PPT，字号原样还原</span></button>
      <button class="card" data-a="demo">${SVG.demo}<b>打开示例</b><span>边海防无人化巡逻体系</span></button>
    </div><h2>最近打开</h2><div class="recent" id="jw-recent"></div></div></div>`);
  document.body.appendChild(S);
  const w2 = wc(); S.querySelector('.bar').appendChild(w2); bindWc(w2);
  const fmtT = t => { const d = new Date(t), n = new Date(), p = x => String(x).padStart(2, '0'); return d.toDateString() === n.toDateString() ? `今天 ${p(d.getHours())}:${p(d.getMinutes())}` : `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`; };
  const KIND = { json: ['织图', '#2f7cf6', '#fff'], pptx: ['PPT', '#d2603a', '#fff'], vsdx: ['VSD', '#3a5fc8', '#fff'], drawio: ['DIO', '#f08705', '#fff'], xml: ['XML', '#6b7a90', '#fff'] };
  async function fillRecent() {
    const box = $('#jw-recent'); let list = [];
    try { list = await D.recent(); } catch (_) { }
    if (!list.length) { box.innerHTML = '<div class="empty">还没有最近文件。保存或打开过的文件会显示在这里。</div>'; return; }
    box.innerHTML = '';
    for (const it of list.slice(0, 8)) {
      const ext = (it.name.match(/\.([^.]+)$/) || [, ''])[1].toLowerCase(), k = KIND[ext] || KIND.xml;
      const row = h(`<div class="ri" tabindex="0"><div class="ic" style="background:${k[1]};color:${k[2]}">${k[0]}</div><div style="min-width:0"><div class="nm"></div><div class="dir"></div></div><div class="tm">${fmtT(it.t)}</div><button class="rm" title="从列表移除">×</button></div>`);
      row.querySelector('.nm').textContent = it.name.replace(/\.jingwei\.json$/i, ''); row.querySelector('.dir').textContent = it.dir;
      row.title = it.path;
      row.addEventListener('click', e => { if (e.target.closest('.rm')) { e.stopPropagation(); D.recentRemove(it.path).then(fillRecent); return; } openPath(it.path); });
      row.addEventListener('keydown', e => { if (e.key === 'Enter') openPath(it.path); });
      box.appendChild(row);
    }
  }
  function showStart() { S.classList.add('on'); fillRecent(); }
  function hideStart() { S.classList.remove('on'); }
  window.jwShowStart = showStart;
  home.onclick = showStart;
  $('#jw-go').onclick = hideStart;
  S.querySelector('.cards').addEventListener('click', e => {
    const b = e.target.closest('[data-a]'); if (!b) return; const a = b.dataset.a;
    if (a === 'open') { openFlow(); return; }
    hideStart();
    if (a === 'new') $('#b-new').click();
    else if (a === 'tpl') $('#b-tpl').click();
    else if (a === 'text') $('#b-text').click();
    else if (a === 'conv') $('#b-conv').click();
    else if (a === 'demo') { _cp(); loadDoc(buildDemo()); fit(); }
  });
  D.info().then(i => {
    const plat = i.platform === 'win32' ? 'Windows' : i.platform === 'linux' ? '银河麒麟／Linux' : i.platform;
    $('#jw-ver').innerHTML = `版本 <b>v${i.version}</b> 桌面版　·　${plat}（${i.arch}）<br>单文件离线运行，无需浏览器，无需联网`;
  });
  // 新建清空路径
  const nb = $('#b-new'), _nb = nb.onclick; nb.onclick = function () { const r = _nb.apply(this, arguments); curPath = null; dirty = false; upd(); return r; };

  upd();
  D.pending().then(list => { if (list && list.length) openPath(list[0]); else showStart(); });
})();
