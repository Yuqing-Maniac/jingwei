/* Optional icon caption placement. Load after app.js; absent fields preserve legacy layout. */
var JwIconLabels = (function () {
  var baseLayout = nodeLayout, baseBBox = contentBBox;
  var cache = new Map(), dragging = null, dragMode = false, repaint = false;
  function eligible(n) {
    return !!(n && !n.imageOnly && n.icon && /^(lib|ms|cu):/.test(n.icon) && !isCont(n) &&
      ['text', 'note', 'legend', 'tblock', 'stdArrow', 'dimArrow'].indexOf(n.type) < 0);
  }
  function finite(v) { return typeof v === 'number' && isFinite(v); }
  function val(n, k) { return finite(n[k]) ? clamp(n[k], -10000, 10000) : 0; }
  function redraw() {
    if (repaint) return;
    repaint = true;
    setTimeout(function () { repaint = false; if (!dragging) render(false); }, 0);
  }
  /* Scan the actual alpha silhouette rather than the transparent square asset padding.
   * Normalize the alpha scan, then apply iconSVG's contain fit for non-square sources. */
  function bounds(uri) {
    if (cache.has(uri)) return cache.get(uri);
    var entry = { box: [0, 0, 1, 1], aspect: 1, ready: null };
    cache.set(uri, entry);
    entry.ready = new Promise(function (resolve) {
      var img = new Image(), timer;
      function finish() { clearTimeout(timer); resolve(); redraw(); }
      img.onload = function () {
        try {
          var c = document.createElement('canvas'); c.width = c.height = 160;
          var ctx = c.getContext('2d');
          entry.aspect = img.width / img.height;
          ctx.drawImage(img, 0, 0, 160, 160);
          var pixels = ctx.getImageData(0, 0, 160, 160).data;
          var x0 = 160, y0 = 160, x1 = -1, y1 = -1;
          for (var y = 0; y < 160; y++) for (var x = 0; x < 160; x++) {
            if (pixels[(y * 160 + x) * 4 + 3] <= 40) continue;
            x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
          }
          if (x1 >= 0) entry.box = [x0 / 160, y0 / 160, (x1 + 1) / 160, (y1 + 1) / 160];
        } catch (_) { /* Opaque/cross-origin assets retain their safe image bounds. */ }
        finish();
      };
      img.onerror = finish;
      timer = setTimeout(finish, 3000);
      img.src = uri;
    });
    return entry;
  }
  function visualBox(ic) {
    var entry = bounds(ic.uri), b = entry.box, w = ic.w || ic.s, h = ic.h || ic.s;
    var iw = Math.min(w, h * entry.aspect), ih = iw / entry.aspect;
    var ox = ic.x + (w - iw) / 2, oy = ic.y + (h - ih) / 2;
    var left = b[0], top = b[1], right = b[2], bottom = b[3];
    if (ic.flipX) { left = 1 - b[2]; right = 1 - b[0]; }
    if (ic.flipY) { top = 1 - b[3]; bottom = 1 - b[1]; }
    return { x: ox + left * iw, y: oy + top * ih, right: ox + right * iw, bottom: oy + bottom * ih };
  }
  function labelBox(t) {
    var w = 0, h = t.lines.length * Math.round(t.size * 1.38);
    for (var i = 0; i < t.lines.length; i++) w = Math.max(w, measure(t.lines[i], t.size, t.bold, t.family));
    return { x: t.anchor === 'start' ? t.x : t.x - w / 2, y: t.cy - h / 2, w: w, h: h };
  }
  nodeLayout = function (n) {
    var L = baseLayout(n);
    if (!eligible(n) || !L.icon || !L.text) return L;
    var t = L.text, ic = L.icon, dx = val(n, 'iconLabelDx'), dy = val(n, 'iconLabelDy');
    if (finite(n.iconLabelGap)) {
      var b = visualBox(ic), gap = clamp(n.iconLabelGap, 0, 400);
      if (t.box[1] >= ic.y + (ic.h || ic.s) - 1) dy += b.bottom + gap - t.box[1];
      else dx += b.right + gap - t.box[0];
    }
    t.x += dx; t.cy += dy;
    t.box = [t.box[0] + dx, t.box[1] + dy, t.box[2], t.box[3]];
    return L;
  };
  contentBBox = function (p) {
    p = p || P();
    var box = baseBBox(p), x0 = box.x, y0 = box.y, x1 = box.x + box.w, y1 = box.y + box.h;
    p.nodes.forEach(function (n) {
      if (!eligible(n)) return;
      /* Do not change the bounds of an untouched legacy document. */
      if (!finite(n.iconLabelGap) && !val(n, 'iconLabelDx') && !val(n, 'iconLabelDy')) return;
      var L = nodeLayout(n); if (!L.text) return;
      var b = labelBox(L.text), corners = [[b.x - 2, b.y - 2], [b.x + b.w + 2, b.y - 2],
        [b.x + b.w + 2, b.y + b.h + 2], [b.x - 2, b.y + b.h + 2]];
      corners.forEach(function (q) {
        var pt = canRotate(n) ? rotPoint(n, q[0], q[1]) : { x: q[0], y: q[1] };
        x0 = Math.min(x0, pt.x); y0 = Math.min(y0, pt.y); x1 = Math.max(x1, pt.x); y1 = Math.max(y1, pt.y);
      });
    });
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  };
  function show(items) { return items.some(eligible); }
  FIELD_CAP.iconLabelPlacement = '图标文字'; FIELD_CAP.iconLabelGap = '文字间距';
  FIELD_CAP.iconLabelDx = '文字横移'; FIELD_CAP.iconLabelDy = '文字纵移';
  FIELD_CAP.iconLabelDrag = '单独拖动文字';
  NODE_FIELDS.iconLabelPlacement = {
    id: 'iconLabelPlacement', kind: 'seg', show: show, scope: eligible,
    get: function (n) { return n.iconLabelGap === 0 && !val(n, 'iconLabelDx') && !val(n, 'iconLabelDy') ? 'tight' : ''; },
    options: function () { return [['tight', '紧贴图标'], ['reset', '重置位置']]; },
    set: function (n, v) {
      delete n.iconLabelDx; delete n.iconLabelDy;
      if (v === 'tight') n.iconLabelGap = 0; else delete n.iconLabelGap;
    }
  };
  ['iconLabelGap', 'iconLabelDx', 'iconLabelDy'].forEach(function (key) {
    NODE_FIELDS[key] = { id: key, kind: 'num', optional: true, min: key === 'iconLabelGap' ? 0 : -10000,
      max: key === 'iconLabelGap' ? 400 : 10000, show: show, scope: eligible,
      blank: function () { return key === 'iconLabelGap' ? '原有位置' : '0'; },
      get: function (n) { return finite(n[key]) ? n[key] : null; },
      set: function (n, v) { if (v === null) delete n[key]; else n[key] = v; } };
  });
  NODE_FIELDS.iconLabelDrag = { id: 'iconLabelDrag', kind: 'check', show: show, scope: eligible,
    get: function () { return dragMode; }, set: function (n, v) { dragMode = !!v; svg.style.cursor = dragMode ? 'text' : ''; } };
  function stop(e) { e.preventDefault(); e.stopImmediatePropagation(); }
  svg.addEventListener('pointerdown', function (e) {
    if (!dragMode || e.button !== 0 || spaceDown || e.shiftKey || e.ctrlKey || e.metaKey) return;
    var el = e.target.closest && e.target.closest('[data-icon-label]');
    var n = el && nodeById(el.getAttribute('data-icon-label'));
    if (!eligible(n)) return;
    stop(e);
    if ($('#editor').style.display === 'block') commitEdit();
    closeMenus(); window.__lastDown = null;
    var w = clientToWorld(e.clientX, e.clientY), p = unrotPoint(n, w.x, w.y);
    dragging = { n: n, pointer: e.pointerId, p: p, dx: val(n, 'iconLabelDx'), dy: val(n, 'iconLabelDy'),
      oldDx: n.iconLabelDx, oldDy: n.iconLabelDy, moved: false, undoLength: undoS.length, redo: redoS.slice() };
    svg.setPointerCapture(e.pointerId); selectNodes([n.id]); render();
  }, true);
  window.addEventListener('pointermove', function (e) {
    var d = dragging; if (!d || d.pointer !== e.pointerId) return;
    stop(e);
    var w = clientToWorld(e.clientX, e.clientY), p = unrotPoint(d.n, w.x, w.y), dx = p.x - d.p.x, dy = p.y - d.p.y;
    if (!d.moved && Math.hypot(dx, dy) * view.k < 3) return;
    if (!d.moved) { checkpoint(); d.moved = true; }
    d.n.iconLabelDx = clamp(Math.round((d.dx + dx) * 10) / 10, -10000, 10000);
    d.n.iconLabelDy = clamp(Math.round((d.dy + dy) * 10) / 10, -10000, 10000);
    render(false);
  }, true);
  function finish(cancel) {
    var d = dragging; if (!d) return;
    if (cancel && d.moved) {
      if (d.oldDx === undefined) delete d.n.iconLabelDx; else d.n.iconLabelDx = d.oldDx;
      if (d.oldDy === undefined) delete d.n.iconLabelDy; else d.n.iconLabelDy = d.oldDy;
      if (undoS.length === d.undoLength + 1) { undoS.pop(); redoS = d.redo; }
    }
    dragging = null;
    if (svg.hasPointerCapture(d.pointer)) svg.releasePointerCapture(d.pointer);
    render();
  }
  window.addEventListener('pointerup', function (e) { if (dragging && e.pointerId === dragging.pointer) { stop(e); finish(false); } }, true);
  window.addEventListener('pointercancel', function (e) { if (dragging && e.pointerId === dragging.pointer) { stop(e); finish(true); } }, true);
  window.addEventListener('keydown', function (e) { if (dragging && e.key === 'Escape') { stop(e); finish(true); } }, true);
  svg.addEventListener('lostpointercapture', function () { if (dragging) finish(true); });
  function ready(p) {
    var promises = [];
    (p || P()).nodes.forEach(function (n) {
      if (!eligible(n) || !finite(n.iconLabelGap)) return;
      var L = baseLayout(n); if (L.icon) promises.push(bounds(L.icon.uri).ready);
    });
    return Promise.all(promises);
  }
  var png = exportPNG, pptx = exportPPTX, vsdx = exportVSDX;
  exportPNG = async function () { var args = arguments; await ready(); return png.apply(this, args); };
  exportPPTX = async function () {
    var args = arguments; await Promise.all(Object.keys(doc.pages).map(function (id) { return ready(doc.pages[id]); }));
    return pptx.apply(this, args);
  };
  exportVSDX = async function (pages) {
    await Promise.all((pages || Object.keys(doc.pages).map(function (id) { return doc.pages[id]; })).map(ready));
    return vsdx.apply(this, arguments);
  };
  return { eligible: eligible, ready: ready, visualBox: visualBox, labelBox: labelBox,
    dragEnabled: function () { return dragMode; } };
})();
