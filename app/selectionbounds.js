/* Canvas-only selection geometry. Never changes saved layout during inspection.
 * Requires iconlabels.js for its shared, asynchronously scanned alpha bounds.
 * Core hooks deliberately opt in: nodeBounds/export geometry stays unchanged. */
var JwSelectionBounds = (function () {
  var opposite = { nw: 'se', ne: 'sw', sw: 'ne', se: 'nw' };
  var handles = ['nw', 'ne', 'sw', 'se'];
  function finite(x) { return typeof x === 'number' && isFinite(x); }
  function fallback(n) { return { x: n.x, y: n.y, w: n.w, h: n.h }; }
  function eligible(n) {
    // Match nodeSVG's visible-card branch. A framed icon, or an equipment
    // status highlight, still has visible geometry all the way to the node box.
    return !!(n && !n.imageOnly && window.JwIconLabels && JwIconLabels.eligible(n) && n.noBox &&
      !(n.type === 'equip' && n.status !== 'base'));
  }
  function layout(n) {
    if (!eligible(n)) return null;
    var L = nodeLayout(n);
    return L && L.icon ? L.icon : null;
  }
  /* Coordinates BEFORE the existing nodeRotationSVG transform. In particular,
   * the caption, node gutters and transparent image padding are not included. */
  function box(n) {
    var ic = layout(n);
    if (!ic) return fallback(n);
    var b = JwIconLabels.visualBox(ic);
    if (!b || !finite(b.x) || !finite(b.y) || !finite(b.right) || !finite(b.bottom) ||
        b.right <= b.x || b.bottom <= b.y) return fallback(n);
    return { x: b.x, y: b.y, w: b.right - b.x, h: b.bottom - b.y };
  }
  function point(b, h) {
    return { x: b.x + (h.indexOf('e') >= 0 ? b.w : 0),
      y: b.y + (h.indexOf('s') >= 0 ? b.h : 0) };
  }
  function world(n, p) {
    return canRotate(n) ? rotPoint(n, p.x, p.y) : { x: p.x, y: p.y };
  }
  function corners(n) {
    var b = box(n);
    return handles.map(function (h) {
      var p = world(n, point(b, h));
      return { h: h, x: p.x, y: p.y };
    });
  }
  function bounds(n) {
    var pts = corners(n), x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    pts.forEach(function (p) {
      x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y);
      x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y);
    });
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }
  function hit(n, p, padding) {
    var b = box(n), q = canRotate(n) ? unrotPoint(n, p.x, p.y) : p;
    var pad = finite(padding) ? Math.max(0, padding) : 0;
    return q.x >= b.x - pad && q.x <= b.x + b.w + pad &&
      q.y >= b.y - pad && q.y <= b.y + b.h + pad;
  }
  function contains(n, rect) {
    var b = bounds(n);
    return b.x >= rect.x && b.y >= rect.y &&
      b.x + b.w <= rect.x + rect.w && b.y + b.h <= rect.y + rect.h;
  }
  function beginResize(n, handle, pointer) {
    var ic = layout(n);
    if (!ic || !opposite[handle]) return null;
    var original = Object.assign({}, n), b = box(original);
    if (b.w <= 0 || b.h <= 0) return null;
    var grip = world(original, point(b, handle));
    return { original: original, handle: handle, opposite: opposite[handle], box: b,
      imageW: ic.w || ic.s, imageH: ic.h || ic.s,
      pointer: { x: pointer ? pointer.x : grip.x, y: pointer ? pointer.y : grip.y },
      anchor: world(original, point(b, opposite[handle])) };
  }
  /* nodeLayout uses contain-fit, fixed caption gutters, line wrapping, innerBox,
   * and lib/ms size caps. Therefore multiplying n.w/h by a silhouette ratio is
   * incorrect. Invert the actual layout along the original image's size vector.
   * This preserves contain aspect, and the existing caps/minimum node sizes.
   * Recompute the rotated fixed corner AFTER fitting: the node's rotation centre
   * moves when its dimensions change, even though the visible anchor must not. */
  function resize(session, pointer) {
    if (!session || !pointer) return null;
    var o = session.original, b0 = session.box;
    var p0 = canRotate(o) ? unrotPoint(o, session.pointer.x, session.pointer.y) : session.pointer;
    var p1 = canRotate(o) ? unrotPoint(o, pointer.x, pointer.y) : pointer;
    var dx = p1.x - p0.x, dy = p1.y - p0.y;
    if (Math.abs(dx) + Math.abs(dy) < 0.000001) return fallback(o);
    var vx = session.handle.indexOf('e') >= 0 ? b0.w : -b0.w;
    var vy = session.handle.indexOf('s') >= 0 ? b0.h : -b0.h;
    var norm = b0.w * b0.w + b0.h * b0.h;
    var wanted = Math.max(0.0001, 1 + (dx * vx + dy * vy) / norm);
    function sample(scale) {
      var n = Object.assign({}, o, {
        w: Math.max(24, o.w + (scale - 1) * session.imageW),
        h: Math.max(16, o.h + (scale - 1) * session.imageH)
      });
      var b = box(n);
      return { node: n, box: b, factor: (b.w * b0.w + b.h * b0.h) / norm };
    }
    // Legacy documents may have hundreds of pixels of surplus space around a
    // capped 140px icon. Allow the inverse search to cross that invisible-size
    // plateau all the way to the minimum node dimensions when shrinking.
    var lo = Math.min(0, 1 + (24 - o.w) / session.imageW,
      1 + (16 - o.h) / session.imageH);
    var hi = Math.max(2, wanted * 2), low = sample(lo), high = sample(hi);
    var target = Math.max(low.factor, Math.min(wanted, high.factor));
    // Already at a layout cap: outward dragging must not inflate invisible
    // padding or silently shrink an oversized legacy node to the cap threshold.
    if (wanted >= 1 && high.factor <= 1.000001) return fallback(o);
    var best = { node: Object.assign({}, o), box: b0, factor: 1 };
    function choose(value) {
      if (Math.abs(value.factor - target) < Math.abs(best.factor - target)) best = value;
    }
    choose(low); choose(high);
    for (var i = 0; i < 36; i++) {
      var mid = (lo + hi) / 2, current = sample(mid);
      choose(current);
      if (current.factor < target) lo = mid; else hi = mid;
    }
    var n = best.node, anchor = world(n, point(best.box, session.opposite));
    return { x: n.x + session.anchor.x - anchor.x, y: n.y + session.anchor.y - anchor.y,
      w: n.w, h: n.h };
  }
  function ready(value) {
    if (!window.JwIconLabels) return Promise.resolve();
    var nodes = Array.isArray(value) ? value : value && value.nodes ? value.nodes :
      value && value.icon ? [value] : P().nodes;
    /* iconlabels.ready normally scans only captions with an explicit gap.
     * Pass temporary copies to request all silhouettes through the SAME cache;
     * no field is written onto the original document, even after resolution.
     * iconlabels' alpha completion already queues a canvas redraw. */
    return JwIconLabels.ready({ nodes: nodes.filter(eligible).map(function (n) {
      return Object.assign({}, n, { iconLabelGap: 0 });
    }) });
  }
  return { eligible: eligible, box: box, corners: corners, bounds: bounds, hit: hit,
    contains: contains, beginResize: beginResize, resize: resize, ready: ready };
})();
