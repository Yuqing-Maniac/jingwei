/* 经纬织图 桌面版：标题栏、窗口控制、首页、本地文件读写（仅在桌面外壳中生效） */
(function () {
  const D = window.jwDesk; if (!D) return;
  document.body.classList.add('desk');
  const $ = s => document.querySelector(s);
  const h = (html) => { const t = document.createElement('template'); setMarkup(t, html.trim()); return t.content.firstChild; };
  const IC = {
    min: '<svg viewBox="0 0 12 12"><path d="M1 6.5h10" stroke="currentColor" stroke-width="1.2"/></svg>',
    max: '<svg viewBox="0 0 12 12"><rect x="1.5" y="1.5" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    res: '<svg viewBox="0 0 12 12"><rect x="1.5" y="3.5" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M3.5 3.5V1.5h7v7h-2" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    close: '<svg viewBox="0 0 12 12"><path d="M1.5 1.5l9 9M10.5 1.5l-9 9" stroke="currentColor" stroke-width="1.2"/></svg>',
    home: '<svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 7.5L8 2.5l6 5M3.8 6.3V13.5h3V10h2.4v3.5h3V6.3" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>',
  };
  const wc = () => h(`<div class="jw-wc"><button data-w="full" class="jw-full" title="切换全屏（F11）">全屏</button><button data-w="min" title="最小化">${IC.min}</button><button data-w="max" title="最大化">${IC.max}</button><button data-w="close" class="x" title="关闭">${IC.close}</button></div>`);
  const bindWc = el => el.addEventListener('click', e => { const b = e.target.closest('[data-w]'); if (b) D.win(b.dataset.w); });

  /* ---------- 标题栏 ---------- */
  const H = $('header');
  const fileChip = h('<div id="jw-file" title=""></div>');
  $('.brand').after(fileChip);
  const home = h(`<button id="jw-home" title="首页（最近文件、新建、模板）">${IC.home}</button>`);
  fileChip.after(home);
  const w1 = wc(); H.appendChild(w1); bindWc(w1);
  const helpBtn = $('#b-help');
  if (helpBtn) {
    const up = h('<button id="jw-patch" title="选择增量升级包（zip），按标记替换应用目录里的文件">增量升级</button>');
    helpBtn.before(up);
    up.onclick = async () => {
      try {
        const r = await D.applyPatch();
        if (!r) return;
        toast('已替换 ' + r.files.length + ' 个文件' + (r.to ? '，版本 ' + r.to : '') + '。请重启应用。');
      } catch (e) { toast('增量升级失败：' + (e && e.message || e)); }
    };
  }
  H.addEventListener('dblclick', e => { if (e.target === H || e.target.closest('.brand,#jw-file,.spacer')) D.win('max'); });
  function updateWindowState(s) {
    document.body.classList.toggle('jw-max', s.max);
    document.querySelectorAll('.jw-wc [data-w=max]').forEach(b => { setMarkup(b, s.max || s.full ? IC.res : IC.max); b.title = s.full ? '退出全屏' : s.max ? '还原' : '最大化'; });
    document.querySelectorAll('.jw-wc [data-w=full]').forEach(b => { b.textContent = s.full ? '退出全屏' : '全屏'; });
  }
  D.on('jw:win-state', updateWindowState);

  for (const id of ['b-undo', 'b-redo']) { const b = $('#' + id); if (b) { const m = b.textContent.trim().match(/^(\S+)\s+(.+)$/); if (m) setMarkup(b, `<i>${m[1]}</i><span>${m[2]}</span>`); } }
  /* 窄窗口：减少交叉、编队、规范收进“更多” */
  const more = h(`<div class="menu" id="jw-more"><button title="更多功能">更多 ▾</button><div class="dd"></div></div>`);
  for (const id of ['b-cross', 'b-form', 'b-std', 'b-ref', 'b-text', 'b-tpl', 'b-conv', 'b-saveas']) { const o = $('#' + id); if (!o) continue; const c = h(`<button>${o.textContent}<small>${(o.title.match(/Ctrl\+[^；;，]+/) || [''])[0]}</small></button>`); c.onclick = () => { more.classList.remove('open'); o.click(); }; more.querySelector('.dd').appendChild(c); }
  more.firstChild.onclick = e => { e.stopPropagation(); more.classList.toggle('open'); };
  $('#m-export').before(more);
  /* ---------- 文档状态 ---------- */
  let curPath = null, dirty = false;
  const base = p => p.split(/[\\/]/).pop();
  window.jwProjectStem = function () { return curPath ? base(curPath) : ''; };
  const docTitle = () => curPath ? base(curPath) : ((typeof doc !== 'undefined' && doc && (doc.name || (doc.pages && doc.pages.root && doc.pages.root.name))) || '未命名');
  function upd() {
    const t = docTitle();
    fileChip.textContent = t; fileChip.title = curPath || '尚未保存到文件';
    fileChip.classList.toggle('dirty', dirty);
    document.title = (dirty ? '● ' : '') + t + ' - 经纬织图'; D.title(document.title);
  }
  window.jwRefreshTitle = upd;
  window.jwTouch = function () { if (!dirty) { dirty = true; upd(); } };
  const _cp = window.checkpoint;
  window.checkpoint = checkpoint = function () { if (!dirty) { dirty = true; upd(); } return _cp.apply(this, arguments); };
  const _ld = window.loadDoc;
  window.loadDoc = loadDoc = function () { const r = _ld.apply(this, arguments); curPath = null; dirty = true; upd(); return r; };

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
    const name = projectFileDefault();
    const savedDoc = doc, savedText = projectJSON();
    const data = new TextEncoder().encode(savedText).buffer;
    try {
      const p = await D.save(name, data, { path: asNew ? null : curPath, title: asNew ? '另存为' : '保存工程' });
      if (!p) { toast('已取消保存'); return null; }
      if (doc !== savedDoc) return p;
      curPath = p; dirty = projectJSON() !== savedText; upd();
      if (window.Backup) Backup.observeSave();
      toast('已保存：' + p); return p;
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
  async function mayReplace() {
    if (!dirty) return true;
    const answer = await D.confirmClose(docTitle());
    if (answer === 'discard') return true;
    return answer === 'save' && !!(await saveProj(false)) && !dirty;
  }
  let opening = false;
  async function openPath(p) {
    if (opening) return;
    opening = true;
    try {
      if (!(await mayReplace())) return;
      const r = await D.read(p);
      if (/\.json$/i.test(r.name)) {
        const o = JSON.parse(new TextDecoder().decode(r.data)); const d = o.doc || o;
        if (!d.pages || !d.pages.root) throw new Error('不是经纬织图工程文件');
        _cp(); loadDoc(d);
        var official = /^(.*)\.bak[\\/]bak-([1-5])\.json$/i.exec(r.path);
        if (official) { curPath = official[1]; dirty = true; }
        else { curPath = r.path; dirty = false; }
        upd(); toast('已打开：' + r.name);
      } else if (/\.(png|jpe?g)$/i.test(r.name)) {
        const ok = await openImageFile(new File([r.data], r.name));
        if (!ok) return;
        upd();
      } else {
        await openForeign(new File([r.data], r.name)); upd();
      }
      hideStart();
    } catch (e) { toast('打开失败：' + (e && e.message || e)); }
    finally { opening = false; }
  }
  async function openFlow() { const p = await D.openDialog(); if (p) openPath(p); }
  $('#b-open').onclick = openFlow;
  $('#f-open').click = openFlow;   // Ctrl+O 走同一流程
  D.on('jw:open-path', p => openPath(p));
  const drop = h('<div id="jw-drop"><div>松开即可打开</div></div>'); document.body.appendChild(drop);
  const isFileDrag = e => e.dataTransfer && [...e.dataTransfer.types].includes('Files');
  window.addEventListener('dragover', e => { if (isFileDrag(e)) { e.preventDefault(); if(typeof isCanvasImageDrop==='function'&&isCanvasImageDrop(e)){drop.classList.remove('on');return;} drop.classList.add('on'); } }, true);
  window.addEventListener('dragleave', e => { if (!e.relatedTarget) drop.classList.remove('on'); }, true);
  window.addEventListener('drop', e => {
    drop.classList.remove('on');
    if (!isFileDrag(e)) return;
    if(typeof isCanvasImageDrop==='function'&&isCanvasImageDrop(e)){e.preventDefault();e.stopPropagation();insertCanvasImages(Array.from(e.dataTransfer.files),clientToWorld(e.clientX,e.clientY));return;}
    const f = e.dataTransfer.files[0];
    if (f && f.path && /\.(json|png|jpe?g|pptx|vsdx|drawio|xml)$/i.test(f.name)) { e.preventDefault(); e.stopPropagation(); openPath(f.path); }
  }, true);

  /* ---------- 关闭前确认 ---------- */
  D.on('jw:before-close', async () => {
    if (!dirty) return D.closeNow();
    const r = await D.confirmClose(docTitle());
    if (r === 'discard') D.closeNow();
    else if (r === 'save') { const p = await saveProj(false); if (p && !dirty) D.closeNow(); }
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
    </div><div class="hist" id="jw-hist" hidden><h2>最近工程</h2><div class="recent" id="jw-recent"></div></div></div></div>`);
  document.body.appendChild(S);
  S.querySelector('.bar').appendChild(jwSkinSelect());
  const w2 = wc(); S.querySelector('.bar').appendChild(w2); bindWc(w2);
  D.winState().then(updateWindowState);
  const KIND = { json: ['织图', '#2f7cf6', '#fff'], pptx: ['PPT', '#d2603a', '#fff'], vsdx: ['VSD', '#3a5fc8', '#fff'], drawio: ['DIO', '#f08705', '#fff'], xml: ['XML', '#6b7a90', '#fff'] };
  async function fillRecent() {
    const wrap = $('#jw-hist'), box = $('#jw-recent'); let list = [];
    try { list = await D.recent(); } catch (_) { }
    if (!wrap || !box) return;
    if (!list || !list.length) { wrap.hidden = true; setMarkup(box, ''); return; }
    wrap.hidden = false; setMarkup(box, '');
    for (const it of list.slice(0, 12)) {
      const ext = (it.name.match(/\.([^.]+)$/) || [, ''])[1].toLowerCase(), k = KIND[ext] || KIND.xml;
      const shown = it.name.replace(/\.jingwei\.json$/i, '');
      const row = h(`<div class="ri" tabindex="0"><div class="ic" style="background:${k[1]};color:${k[2]}">${k[0]}</div><div class="meta"><div class="nm" title="单击改名"></div><div class="dir"></div></div><div class="tm"></div><button class="rm" title="从列表移除">×</button></div>`);
      row.querySelector('.nm').textContent = shown;
      row.querySelector('.dir').textContent = it.path;
      row.querySelector('.tm').textContent = fmtWhen(it.t);
      row.title = it.path;
      row.addEventListener('click', e => {
        if (e.target.closest('.rm')) { e.stopPropagation(); D.recentRemove(it.path).then(fillRecent); return; }
        if (e.target.closest('.nm') || e.target.closest('input')) return;
        openPath(it.path);
      });
      row.querySelector('.nm').addEventListener('click', e => {
        e.stopPropagation();
        editInline(e.currentTarget, shown, async name => {
          if (!name) { fillRecent(); return; }
          let r = null;
          try { r = await D.rename(it.path, name); } catch (err) { toast('改名失败：' + (err && err.message || err)); fillRecent(); return; }
          if (!r || r.error) { toast(r && r.error || '改名失败'); fillRecent(); return; }
          if (curPath === it.path) { curPath = r.path; upd(); }
          fillRecent();
        });
      });
      row.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.target.closest('input')) openPath(it.path); });
      box.appendChild(row);
    }
  }
  function showStart() { S.classList.add('on'); fillRecent(); }
  function hideStart() { S.classList.remove('on'); }
  window.jwShowStart = showStart;
  home.onclick = showStart;
  $('#jw-go').onclick = hideStart;
  S.querySelector('.cards').addEventListener('click', async e => {
    const b = e.target.closest('[data-a]'); if (!b) return; const a = b.dataset.a;
    if (a === 'open') { openFlow(); return; }
    hideStart();
    if (a === 'new') $('#b-new').click();
    else if (a === 'tpl') $('#b-tpl').click();
    else if (a === 'text') $('#b-text').click();
    else if (a === 'conv') $('#b-conv').click();
    else if (a === 'demo' && await mayReplace()) { _cp(); loadDoc(buildDemo()); fit(); }
  });
  D.info().then(i => {
    const plat = i.platform === 'win32' ? 'Windows' : i.platform === 'linux' ? '银河麒麟／Linux' : i.platform;
    setMarkup($('#jw-ver'), `版本 <b>v${i.version}</b> 桌面版　·　${plat}（${i.arch}）<br>单文件离线运行，无需浏览器，无需联网`);
  });
  // 新建清空路径
  const nb = $('#b-new'), _nb = nb.onclick; nb.onclick = async function () { if (!(await mayReplace())) return; const r = _nb.apply(this, arguments); curPath = null; dirty = true; upd(); return r; };

  upd();
  if (window.Backup) Backup.install({
    currentPath: function () { return curPath; },
    list: function (scope) { return D.backupList(scope, scope === 'current' ? curPath : null); },
    write: function (slot, frozen, backedAt) { return D.backupWrite(curPath, slot, frozen, backedAt); },
    drop: function (projectPath, slot) { return D.backupDrop(projectPath, slot); },
    noteSave: function () { return Promise.resolve(); }
  }, { adoptPath: function (p) { curPath = p || null; dirty = true; upd(); } });
  D.pending().then(list => {
    var opened = list && list.length;
    if (opened) openPath(list[0]); else showStart();
    if (!opened && window.Backup) Backup.offer();
  });
})();
