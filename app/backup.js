/* 滚动备份：正式文件只由用户保存写入。这里只写备份槽。 */
(function () {
  'use strict';
  var BACKUP_SLOTS = 5;
  var BACKUP_DEBOUNCE_MS = 5000;
  var BACKUP_INTERVAL_MS = 150000;
  var port = null;
  var hook = {};
  var saveText = null;
  var backupText = null;
  var epoch = 0;
  var debounce = null;
  var timer = null;
  var busy = false;
  var queued = false;

  /* 视口 cam 每次平移都会变，不计入“图有没有改过”。page.view 是规范视图类型，保留。 */
  function canonDoc(d) {
    var copy = JSON.parse(JSON.stringify(d));
    var pages = (copy && copy.pages) || {};
    Object.keys(pages).forEach(function (id) { delete pages[id].cam; });
    return copy;
  }
  function canonText(d) { return JSON.stringify(canonDoc(d)); }

  function install(p, h) { port = p; hook = h || {}; }

  function poke() {
    if (!port) return;
    if (debounce) clearTimeout(debounce);
    debounce = setTimeout(function () { debounce = null; commit(); }, BACKUP_DEBOUNCE_MS);
  }

  function observeLoad() {
    saveText = canonText(doc);
    backupText = null;
    epoch += 1;
    if (debounce) { clearTimeout(debounce); debounce = null; }
  }

  function observeSave() {
    var text = canonText(doc);
    epoch += 1;
    saveText = text;
    backupText = text;
    if (debounce) { clearTimeout(debounce); debounce = null; }
    if (!port) return;
    var note = function () { return port.noteSave(Date.now(), text); };
    var path = port.currentPath ? port.currentPath() : null;
    if (!path) { note(); return; }
    port.list('untitled').then(function (listed) {
      var jobs = [];
      if (listed && !listed.suppressed) {
        var newest = null;
        (listed.projects || []).forEach(function (pr) {
          (pr.slots || []).forEach(function (s) {
            if (!newest || s.backedAt > newest.backedAt) newest = s;
          });
        });
        if (newest && canonText(newest.doc) === text) {
          (listed.projects || []).forEach(function (pr) {
            (pr.slots || []).forEach(function (s) { jobs.push(port.drop(pr.projectPath, s.slot)); });
          });
        }
      }
      return Promise.all(jobs);
    }).then(note, note);
  }

  function chooseSlot(slots) {
    var have = {};
    (slots || []).forEach(function (s) { have[s.slot] = s; });
    for (var i = 1; i <= BACKUP_SLOTS; i++) if (!have[i]) return i;
    var best = slots[0];
    slots.forEach(function (s) { if (s.backedAt < best.backedAt) best = s; });
    return best.slot;
  }

  function settle() {
    busy = false;
    if (queued) { queued = false; commit(); }
  }

  function commit() {
    if (!port) return Promise.resolve();
    if (busy) { queued = true; return Promise.resolve(); }
    busy = true;
    var epoch0 = epoch;
    var text;
    try { text = canonText(doc); }
    catch (e) { settle(); return Promise.resolve(); }
    if (text === saveText || text === backupText) { settle(); return Promise.resolve(); }
    return port.list('current').then(function (listed) {
      if (!listed || listed.suppressed || epoch !== epoch0) return;
      var slots = [];
      (listed.projects || []).forEach(function (pr) {
        (pr.slots || []).forEach(function (s) { slots.push(s); });
      });
      for (var i = 0; i < slots.length; i++) {
        if (canonText(slots[i].doc) === text) { backupText = text; return; }
      }
      if (canonText(doc) !== text) { poke(); return; }
      var frozen = JSON.parse(text);
      return port.write(chooseSlot(slots), frozen, Date.now()).then(function () {
        if (epoch !== epoch0 || canonText(doc) !== text) return;
        backupText = text;
      });
    }).then(settle, settle);
  }

  function offerOf(project) {
    var best = null;
    (project.slots || []).forEach(function (s) {
      if (!(s.backedAt > project.saveTime)) return;
      if (project.saveText != null && canonText(s.doc) === project.saveText) return;
      if (!best || s.backedAt > best.backedAt) best = s;
    });
    return best;
  }

  function closeBak() {
    var el = document.getElementById('jw-bak');
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function showBak(pick) {
    if (document.getElementById('jw-bak')) return;
    var el = document.createElement('div');
    el.id = 'jw-bak';
    el.innerHTML = '<div class="box"><h3>恢复未保存的工程</h3><p>上次关闭前的修改还在备份里，正式文件没有被改写。</p><div class="acts"><button type="button" id="jw-bak-restore" class="primary">恢复</button><button type="button" id="jw-bak-ignore">忽略</button></div></div>';
    document.body.appendChild(el);
    document.getElementById('jw-bak-restore').addEventListener('click', function () {
      closeBak();
      loadDoc(pick.slot.doc);
      if (hook.adoptPath) hook.adoptPath(pick.project.projectPath);
    });
    document.getElementById('jw-bak-ignore').addEventListener('click', function () {
      closeBak();
      var pr = pick.project;
      var jobs = (pr.slots || []).filter(function (s) { return s.backedAt > pr.saveTime; }).map(function (s) {
        return port.drop(pr.projectPath, s.slot);
      });
      Promise.all(jobs).then(function () {}, function () {});
    });
  }

  function offer() {
    if (!port) return Promise.resolve();
    return port.list('all').then(function (listed) {
      if (!listed || listed.suppressed) return;
      var best = null, owner = null;
      (listed.projects || []).forEach(function (pr) {
        var slot = offerOf(pr);
        if (slot && (!best || slot.backedAt > best.backedAt)) { best = slot; owner = pr; }
      });
      if (!best) return;
      showBak({ project: owner, slot: best });
    }, function () {});
  }

  function start() {
    if (timer) clearInterval(timer);
    timer = setInterval(function () { commit(); }, BACKUP_INTERVAL_MS);
  }

  var idbFailed = false;
  var openPromise = null;
  function openDb() {
    if (idbFailed) return Promise.reject(new Error('idb'));
    if (openPromise) return openPromise;
    openPromise = new Promise(function (res, rej) {
      var req;
      try { req = indexedDB.open('hongtu.backup', 1); }
      catch (e) { idbFailed = true; openPromise = null; rej(e); return; }
      req.onupgradeneeded = function () {
        var db = req.result;
        if (!db.objectStoreNames.contains('slots')) db.createObjectStore('slots', { keyPath: 'slot' });
        if (!db.objectStoreNames.contains('meta')) db.createObjectStore('meta');
      };
      req.onsuccess = function () {
        var db = req.result;
        db.onversionchange = function () { db.close(); };
        res(db);
      };
      req.onerror = function () { idbFailed = true; openPromise = null; rej(req.error || new Error('idb')); };
      req.onblocked = function () { idbFailed = true; openPromise = null; rej(new Error('idb')); };
    });
    return openPromise;
  }
  function txDone(tx) {
    return new Promise(function (res, rej) {
      tx.oncomplete = function () { res(); };
      tx.onerror = function () { rej(tx.error || new Error('idb')); };
      tx.onabort = function () { rej(tx.error || new Error('idb')); };
    });
  }
  function emptyList() { return { suppressed: false, projects: [] }; }
  function idbPort() {
    return {
      currentPath: function () { return null; },
      list: function () {
        if (idbFailed) return Promise.resolve(emptyList());
        return openDb().then(function (db) {
          return new Promise(function (res, rej) {
            var tx = db.transaction(['slots', 'meta'], 'readonly');
            var slotsReq = tx.objectStore('slots').getAll();
            var metaReq = tx.objectStore('meta').get('save');
            var raw = [], meta = null;
            slotsReq.onsuccess = function () { raw = slotsReq.result || []; };
            metaReq.onsuccess = function () { meta = metaReq.result || null; };
            tx.oncomplete = function () {
              var slots = [];
              raw.forEach(function (row) {
                if (!row || !row.doc || !row.doc.pages || !row.doc.pages.root) return;
                var at = row.backup && row.backup.backedAt;
                var n = row.backup && row.backup.slot;
                if (!isFinite(at) || at <= 0) return;
                if (n !== row.slot || n < 1 || n > BACKUP_SLOTS) return;
                slots.push({ slot: n, backedAt: at, doc: row.doc });
              });
              res({
                suppressed: false,
                projects: [{
                  projectPath: null,
                  saveTime: meta && isFinite(meta.savedAt) ? meta.savedAt : 0,
                  saveText: meta && typeof meta.saveText === 'string' ? meta.saveText : null,
                  slots: slots
                }]
              });
            };
            tx.onerror = function () { rej(tx.error || new Error('idb')); };
          });
        }, function () { return emptyList(); });
      },
      write: function (slot, frozen, backedAt) {
        if (idbFailed) return Promise.resolve();
        if (slot < 1 || slot > BACKUP_SLOTS) return Promise.reject(new Error('slot'));
        return openDb().then(function (db) {
          var tx = db.transaction('slots', 'readwrite');
          tx.objectStore('slots').put({
            slot: slot,
            format: 'hongtu',
            version: 1,
            backup: { backedAt: backedAt, slot: slot },
            doc: frozen
          });
          return txDone(tx);
        }, function () {});
      },
      drop: function (_projectPath, slot) {
        if (idbFailed) return Promise.resolve();
        return openDb().then(function (db) {
          var tx = db.transaction('slots', 'readwrite');
          tx.objectStore('slots').delete(slot);
          return txDone(tx);
        }, function () {});
      },
      noteSave: function (savedAt, text) {
        if (idbFailed) return Promise.resolve();
        return openDb().then(function (db) {
          var tx = db.transaction('meta', 'readwrite');
          tx.objectStore('meta').put({ savedAt: savedAt, saveText: text }, 'save');
          return txDone(tx);
        }, function () {});
      }
    };
  }

  start();
  if (!window.jwDesk) install(idbPort());
  window.Backup = { install: install, poke: poke, observeLoad: observeLoad, observeSave: observeSave, offer: offer, commit: commit };
})();
