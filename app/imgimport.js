/* 图片导入：框图照片 → 可编辑的框和连线。外部只调用 ImgImport.read。 */
(function () {
  var FACE = {
    sans: { font: 'noto', bold: false },
    'sans-bold': { font: 'noto', bold: true },
    serif: { font: 'noto-serif', bold: false }
  };
  var bookStr = (typeof window !== 'undefined' && window.__imgBook) ? String(window.__imgBook) : '';
  if (typeof window !== 'undefined') window.__imgBook = undefined;
  var bookCache = null;
  var bookTried = false;

  function read(imageData) {
    var plate = accept(imageData);
    if (!plate.ink) return blank(plate.notes);
    var marks = [];
    findFigures(plate, marks);
    peel(plate);
    classifyRest(plate, marks);
    bridge(marks, plate);
    nest(marks, plate.sw);
    recognizeGlyphs(marks);
    bindGlyphs(marks, plate.sw);
    dropBorder(marks);
    nest(marks, plate.sw);
    bindGlyphs(marks, plate.sw);
    return emit(marks, plate);
  }

  function blank(notes) {
    return { page: { id: 'root', name: '总图', nodes: [], links: [], view: null }, notes: notes || [] };
  }

  function accept(imageData) {
    if (!imageData || !imageData.data || (imageData.width * imageData.height * 4) !== imageData.data.length) throw new Error('图片无法识别');
    var sw0 = imageData.width, sh0 = imageData.height;
    if (sw0 < 8 || sh0 < 8) throw new Error('图片太小');
    if (sw0 * sh0 > 8000000) throw new Error('图片过大，请缩到 800 万像素以内再导入');
    var gray = toGray(imageData.data, sw0 * sh0);
    if (medianSample(gray, sw0, sh0, 'border') + 12 < medianSample(gray, sw0, sh0, 'center')) {
      for (var i = 0; i < gray.length; i++) gray[i] = 255 - gray[i];
    }
    var scaleX = 1, scaleY = 1, gw = sw0, gh = sh0;
    var long = sw0 > sh0 ? sw0 : sh0;
    if (long > 1600) {
      var sc = long / 1600;
      gw = Math.max(8, Math.round(sw0 / sc));
      gh = Math.max(8, Math.round(sh0 / sc));
      gray = boxDown(gray, sw0, sh0, gw, gh);
      scaleX = sw0 / gw;
      scaleY = sh0 / gh;
    }
    var thr = otsu(gray);
    var bin = new Uint8Array(gray.length);
    var ink = 0;
    for (var p = 0; p < gray.length; p++) if (gray[p] < thr) { bin[p] = 1; ink++; }
    if (ink > bin.length * 0.35) {
      ink = 0;
      var cut = thr < 170 ? thr : 170;
      for (var q = 0; q < gray.length; q++) { bin[q] = gray[q] < cut ? 1 : 0; if (bin[q]) ink++; }
    }
    if (!ink) {
      for (var r = 0; r < gray.length; r++) if (gray[r] < 210) { bin[r] = 1; ink++; }
    }
    var plate = {
      w: gw, h: gh, scaleX: scaleX, scaleY: scaleY, bin: bin, sw: 1, ink: ink,
      src: imageData.data, srcW: sw0, srcH: sh0, drop: new Uint8Array(gw * gh),
      notes: ink ? [] : ['没有可识别的线条']
    };
    if (!ink) return plate;
    plate.dt = distanceToPaper(bin, gw, gh);
    plate.sw = strokeWidth(plate.dt, bin, gw, gh);
    return plate;
  }

  function toGray(data, n) {
    var g = new Uint8Array(n);
    for (var i = 0, p = 0; i < n; i++, p += 4) {
      if (data[p + 3] < 16) { g[i] = 255; continue; }
      g[i] = (data[p] * 76 + data[p + 1] * 150 + data[p + 2] * 30) >> 8;
    }
    return g;
  }

  function medianSample(gray, w, h, which) {
    var vals = [];
    var rim = Math.max(2, Math.round(Math.min(w, h) * 0.02));
    if (which === 'border') {
      for (var y = 0; y < h; y += 2) for (var x = 0; x < w; x += 2) {
        if (x < rim || y < rim || x >= w - rim || y >= h - rim) vals.push(gray[y * w + x]);
      }
    } else {
      var x0 = (w * 0.25) | 0, x1 = (w * 0.75) | 0, y0 = (h * 0.25) | 0, y1 = (h * 0.75) | 0;
      for (var y2 = y0; y2 < y1; y2 += 3) for (var x2 = x0; x2 < x1; x2 += 3) vals.push(gray[y2 * w + x2]);
    }
    return median(vals);
  }

  function median(vals) {
    if (!vals.length) return 0;
    var a = vals.slice().sort(function (x, y) { return x - y; });
    return a[a.length >> 1];
  }

  function boxDown(gray, w, h, nw, nh) {
    var out = new Uint8Array(nw * nh);
    for (var y = 0; y < nh; y++) {
      var y0 = Math.floor(y * h / nh), y1 = Math.max(y0 + 1, Math.floor((y + 1) * h / nh));
      if (y1 > h) y1 = h;
      for (var x = 0; x < nw; x++) {
        var x0 = Math.floor(x * w / nw), x1 = Math.max(x0 + 1, Math.floor((x + 1) * w / nw));
        if (x1 > w) x1 = w;
        var s = 0, n = 0;
        for (var yy = y0; yy < y1; yy++) for (var xx = x0; xx < x1; xx++) { s += gray[yy * w + xx]; n++; }
        out[y * nw + x] = n ? (s / n) | 0 : 255;
      }
    }
    return out;
  }

  function otsu(gray) {
    var hist = new Uint32Array(256);
    for (var i = 0; i < gray.length; i++) hist[gray[i]]++;
    var total = gray.length, sum = 0;
    for (var t = 0; t < 256; t++) sum += t * hist[t];
    var sumB = 0, wB = 0, max = -1, thr = 128;
    for (var u = 0; u < 256; u++) {
      wB += hist[u];
      if (!wB) continue;
      var wF = total - wB;
      if (!wF) break;
      sumB += u * hist[u];
      var mB = sumB / wB, mF = (sum - sumB) / wF;
      var v = wB * wF * (mB - mF) * (mB - mF);
      if (v > max) { max = v; thr = u; }
    }
    return thr;
  }

  function dt1d(f) {
    var n = f.length;
    var d = new Float64Array(n);
    var v = new Int32Array(n);
    var z = new Float64Array(n + 1);
    var k = 0;
    v[0] = 0;
    z[0] = -1e15;
    z[1] = 1e15;
    for (var q = 1; q < n; q++) {
      var s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
      while (k > 0 && s <= z[k]) {
        k--;
        s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k]);
      }
      k++;
      v[k] = q;
      z[k] = s;
      z[k + 1] = 1e15;
    }
    k = 0;
    for (var q2 = 0; q2 < n; q2++) {
      while (z[k + 1] < q2) k++;
      var dx = q2 - v[k];
      d[q2] = dx * dx + f[v[k]];
    }
    return d;
  }

  function distanceToPaper(bin, w, h) {
    var INF = 1e7;
    var tmp = new Float64Array(w * h);
    var row = new Float64Array(w);
    for (var y = 0; y < h; y++) {
      for (var x = 0; x < w; x++) row[x] = bin[y * w + x] ? INF : 0;
      var d = dt1d(row);
      for (var x2 = 0; x2 < w; x2++) tmp[y * w + x2] = d[x2];
    }
    var out = new Float64Array(w * h);
    var col = new Float64Array(h);
    for (var x3 = 0; x3 < w; x3++) {
      for (var y2 = 0; y2 < h; y2++) col[y2] = tmp[y2 * w + x3];
      var d2 = dt1d(col);
      for (var y3 = 0; y3 < h; y3++) out[y3 * w + x3] = Math.sqrt(d2[y3]);
    }
    return out;
  }

  function strokeWidth(dt, bin, w, h) {
    var vals = [];
    for (var y = 1; y < h - 1; y++) for (var x = 1; x < w - 1; x++) {
      var i = y * w + x;
      if (!bin[i] || dt[i] < 0.5) continue;
      var ridge = true;
      for (var dy = -1; dy <= 1 && ridge; dy++) for (var dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        if (dt[i] < dt[i + dy * w + dx]) ridge = false;
      }
      if (ridge) vals.push(dt[i]);
    }
    if (!vals.length) return 1;
    return Math.max(1, Math.min(12, 2 * median(vals)));
  }

  function labelBinary(bin, w, h, wantInk) {
    var lab = new Int32Array(w * h);
    var areas = [0];
    var boxes = [null];
    var border = [0];
    var n = 0;
    var stack = new Int32Array(w * h);
    var dirs = wantInk
      ? [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
      : [[1, 0], [-1, 0], [0, 1], [0, -1]];
    for (var i = 0; i < w * h; i++) {
      if (wantInk ? bin[i] !== 1 : bin[i] !== 0) continue;
      if (lab[i]) continue;
      n++;
      var sp = 0;
      stack[sp++] = i;
      lab[i] = n;
      var area = 0, x0 = w, y0 = h, x1 = -1, y1 = -1, edge = 0;
      while (sp) {
        var p = stack[--sp];
        area++;
        var x = p % w, y = (p / w) | 0;
        if (x < x0) x0 = x;
        if (y < y0) y0 = y;
        if (x > x1) x1 = x;
        if (y > y1) y1 = y;
        if (x === 0 || y === 0 || x === w - 1 || y === h - 1) edge = 1;
        for (var d = 0; d < dirs.length; d++) {
          var nx = x + dirs[d][0], ny = y + dirs[d][1];
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
          var j = ny * w + nx;
          if (lab[j]) continue;
          if (wantInk ? bin[j] !== 1 : bin[j] !== 0) continue;
          lab[j] = n;
          stack[sp++] = j;
        }
      }
      areas[n] = area;
      boxes[n] = { x: x0, y: y0, w: x1 - x0 + 1, h: y1 - y0 + 1 };
      border[n] = edge;
    }
    return { lab: lab, n: n, areas: areas, boxes: boxes, border: border };
  }

  function findFigures(plate, marks) {
    var w = plate.w, h = plate.h, sw = plate.sw;
    var paper = labelBinary(plate.bin, w, h, false);
    var minArea = Math.max(48, 12 * sw * sw);
    for (var id = 1; id <= paper.n; id++) {
      if (paper.border[id]) continue;
      var box = paper.boxes[id];
      if (paper.areas[id] < minArea) continue;
      if (Math.min(box.w, box.h) <= 6 * sw) continue;
      var solid = solidify(paper.lab, id, box, w, h, sw);
      if (!solid) continue;
      if (Math.min(solid.w, solid.h) <= 6 * sw) continue;
      if (solid.w * solid.h < minArea) continue;
      var shape = bestShape(solid.mask, solid.w, solid.h);
      if (!shape) continue;
      if (ringScore(plate.bin, solid, w, h) < 0.42) continue;
      var e = sw * 0.5;
      var fx = solid.x - e, fy = solid.y - e, fw = solid.w + e * 2, fh = solid.h + e * 2;
      if (shape === 'ellipse' && Math.abs(fw - fh) / Math.max(fw, fh) < 0.12) {
        var cx = fx + fw / 2, cy = fy + fh / 2, s = (fw + fh) / 2;
        fx = cx - s / 2; fy = cy - s / 2; fw = s; fh = s;
      }
      marks.push({ kind: 'figure', shape: shape, x: fx, y: fy, w: fw, h: fh, contains: [] });
      markRing(plate, solid);
    }
    plate.dt = null;
  }

  function solidify(lab, region, box, w, h, sw) {
    var m = Math.ceil(sw) + 4;
    var x0 = Math.max(0, box.x - m), y0 = Math.max(0, box.y - m);
    var x1 = Math.min(w, box.x + box.w + m), y1 = Math.min(h, box.y + box.h + m);
    var bw = x1 - x0, bh = y1 - y0;
    if (bw < 3 || bh < 3) return null;
    var seen = new Uint8Array(bw * bh);
    var stack = new Int32Array(bw * bh);
    var sp = 0;
    function seed(x, y) {
      if (x < x0 || y < y0 || x >= x1 || y >= y1) return;
      var s = (y - y0) * bw + (x - x0);
      if (seen[s]) return;
      if (lab[y * w + x] === region) return;
      seen[s] = 1;
      stack[sp++] = s;
    }
    for (var x = x0; x < x1; x++) { seed(x, y0); seed(x, y1 - 1); }
    for (var y = y0; y < y1; y++) { seed(x0, y); seed(x1 - 1, y); }
    if (!sp) return null;
    var dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
    while (sp) {
      var s = stack[--sp];
      var lx = s % bw, ly = (s / bw) | 0;
      var gx = x0 + lx, gy = y0 + ly;
      for (var d = 0; d < 4; d++) {
        var nx = gx + dirs[d][0], ny = gy + dirs[d][1];
        if (nx < x0 || ny < y0 || nx >= x1 || ny >= y1) continue;
        var j = (ny - y0) * bw + (nx - x0);
        if (seen[j]) continue;
        if (lab[ny * w + nx] === region) continue;
        seen[j] = 1;
        stack[sp++] = j;
      }
    }
    var ax0 = bw, ay0 = bh, ax1 = -1, ay1 = -1, count = 0;
    for (var ly = 0; ly < bh; ly++) for (var lx = 0; lx < bw; lx++) {
      if (seen[ly * bw + lx]) continue;
      count++;
      if (lx < ax0) ax0 = lx;
      if (ly < ay0) ay0 = ly;
      if (lx > ax1) ax1 = lx;
      if (ly > ay1) ay1 = ly;
    }
    if (count < 10 || ax1 < 0) return null;
    if (ax0 === 0 || ay0 === 0 || ax1 === bw - 1 || ay1 === bh - 1) return null;
    var swd = ax1 - ax0 + 1, shd = ay1 - ay0 + 1;
    var mask = new Uint8Array(swd * shd);
    for (var py = ay0; py <= ay1; py++) for (var px = ax0; px <= ax1; px++) {
      if (!seen[py * bw + px]) mask[(py - ay0) * swd + (px - ax0)] = 1;
    }
    return { mask: mask, x: x0 + ax0, y: y0 + ay0, w: swd, h: shd };
  }

  function ringScore(bin, solid, imgW, imgH) {
    var mask = solid.mask, w = solid.w, h = solid.h, hit = 0, bcount = 0;
    for (var py = 0; py < h; py++) for (var px = 0; px < w; px++) {
      if (!mask[py * w + px]) continue;
      var edge = px === 0 || py === 0 || px === w - 1 || py === h - 1
        || !mask[py * w + px - 1] || !mask[py * w + px + 1] || !mask[(py - 1) * w + px] || !mask[(py + 1) * w + px];
      if (!edge) continue;
      bcount++;
      var ink = false;
      for (var dy = -2; dy <= 2 && !ink; dy++) for (var dx = -2; dx <= 2; dx++) {
        if (!dx && !dy) continue;
        var ix = solid.x + px + dx, iy = solid.y + py + dy;
        if (ix < 0 || iy < 0 || ix >= imgW || iy >= imgH) continue;
        var lx = ix - solid.x, ly = iy - solid.y;
        if (lx >= 0 && ly >= 0 && lx < w && ly < h && mask[ly * w + lx]) continue;
        if (bin[iy * imgW + ix]) ink = true;
      }
      if (ink) hit++;
    }
    return bcount ? hit / bcount : 0;
  }

  function markRing(plate, solid) {
    var rad = Math.max(2, Math.round(plate.sw + 1));
    var mask = solid.mask, w = solid.w, h = solid.h;
    var bin = plate.bin, drop = plate.drop, imgW = plate.w, imgH = plate.h;
    for (var py = 0; py < h; py++) for (var px = 0; px < w; px++) {
      if (!mask[py * w + px]) continue;
      var edge = px === 0 || py === 0 || px === w - 1 || py === h - 1
        || !mask[py * w + px - 1] || !mask[py * w + px + 1] || !mask[(py - 1) * w + px] || !mask[(py + 1) * w + px];
      if (!edge) continue;
      for (var dy = -rad; dy <= rad; dy++) for (var dx = -rad; dx <= rad; dx++) {
        if (dx * dx + dy * dy > rad * rad) continue;
        var ix = solid.x + px + dx, iy = solid.y + py + dy;
        if (ix < 0 || iy < 0 || ix >= imgW || iy >= imgH) continue;
        var lx = ix - solid.x, ly = iy - solid.y;
        if (lx >= 0 && ly >= 0 && lx < w && ly < h && mask[ly * w + lx]) continue;
        var i = iy * imgW + ix;
        if (bin[i] && plate.dt && plate.dt[i] <= plate.sw * 0.9) drop[i] = 1;
      }
    }
  }

  function peel(plate) {
    var bin = plate.bin, drop = plate.drop;
    for (var i = 0; i < bin.length; i++) if (drop[i]) bin[i] = 0;
  }

  function boundaryPoints(mask, w, h) {
    var pts = [];
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++) {
      if (!mask[y * w + x]) continue;
      if (x === 0 || y === 0 || x === w - 1 || y === h - 1 || !mask[y * w + x - 1] || !mask[y * w + x + 1] || !mask[(y - 1) * w + x] || !mask[(y + 1) * w + x]) pts.push({ x: x, y: y });
    }
    if (pts.length > 360) {
      var step = Math.ceil(pts.length / 360), slim = [];
      for (var i = 0; i < pts.length; i += step) slim.push(pts[i]);
      return slim;
    }
    return pts;
  }

  function cornerRadii(mask, w, h) {
    function walk(cx, cy, sx, sy) {
      var lim = Math.floor(Math.min(w, h) / 2);
      var r = 0;
      while (r < lim) {
        var hx = cx + sx * r, vy = cy + sy * r;
        var onH = mask[cy * w + hx], onV = mask[vy * w + cx];
        if (onH || onV) break;
        r++;
      }
      return r;
    }
    return [walk(0, 0, 1, 1), walk(w - 1, 0, -1, 1), walk(w - 1, h - 1, -1, -1), walk(0, h - 1, 1, -1)];
  }

  function meanDist(pts, fn) {
    if (!pts.length) return 1e9;
    var s = 0;
    for (var i = 0; i < pts.length; i++) s += fn(pts[i]);
    return s / pts.length;
  }

  function distSeg(px, py, ax, ay, bx, by) {
    var dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
    if (!l2) return Math.hypot(px - ax, py - ay);
    var t = ((px - ax) * dx + (py - ay) * dy) / l2;
    if (t < 0) t = 0; else if (t > 1) t = 1;
    return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
  }

  function bestShape(mask, w, h) {
    var pts = boundaryPoints(mask, w, h);
    if (pts.length < 8) return null;
    var minSide = Math.min(w, h);
    var radii = cornerRadii(mask, w, h);
    var maxR = Math.max(radii[0], radii[1], radii[2], radii[3]);
    var eRect = meanDist(pts, function (p) { return Math.min(p.x, p.y, w - 1 - p.x, h - 1 - p.y); });
    if (maxR <= 3 && eRect < 0.075 * minSide) return 'rect';
    var cands = [];
    function agree(a, b) { return Math.abs(a - b) <= 0.30 * Math.max(a, b, 1); }
    function sideOk(a, b) {
      return a >= 4 && b >= 4 && a <= 0.40 * minSide && b <= 0.40 * minSide && agree(a, b);
    }
    if (sideOk(radii[0], radii[1]) && sideOk(radii[1], radii[2]) && sideOk(radii[2], radii[3]) && agree(radii[0], radii[2])) {
      var r = (radii[0] + radii[1] + radii[2] + radii[3]) / 4;
      var eRound = meanDist(pts, function (p) { return distRound(p.x, p.y, w, h, r); });
      if (eRound < 0.12 * minSide) cands.push({ shape: 'round', err: eRound });
    }
    if (sideOk(radii[0], radii[3]) && radii[1] <= 3 && radii[2] <= 3) {
      var rl = (radii[0] + radii[3]) / 2;
      cands.push({ shape: 'roundL', err: meanDist(pts, function (p) { return distSideRound(p.x, p.y, w, h, rl, true); }) });
    }
    if (sideOk(radii[1], radii[2]) && radii[0] <= 3 && radii[3] <= 3) {
      var rr = (radii[1] + radii[2]) / 2;
      cands.push({ shape: 'roundR', err: meanDist(pts, function (p) { return distSideRound(p.x, p.y, w, h, rr, false); }) });
    }
    var cx = (w - 1) / 2, cy = (h - 1) / 2, rx = w / 2, ry = h / 2;
    cands.push({
      shape: 'ellipse',
      err: meanDist(pts, function (p) {
        var nx = (p.x - cx) / rx, ny = (p.y - cy) / ry;
        return Math.abs(Math.hypot(nx, ny) - 1) * ((rx + ry) / 2);
      })
    });
    var vx = (w - 1) / 2, vy = (h - 1) / 2;
    var dia = [[vx, 0], [w - 1, vy], [vx, h - 1], [0, vy]];
    cands.push({
      shape: 'diamond',
      err: meanDist(pts, function (p) {
        var best = 1e9;
        for (var i = 0; i < 4; i++) {
          var a = dia[i], b = dia[(i + 1) % 4];
          var d = distSeg(p.x, p.y, a[0], a[1], b[0], b[1]);
          if (d < best) best = d;
        }
        return best;
      })
    });
    if (eRect < 0.12 * minSide && maxR <= 6) cands.push({ shape: 'rect', err: eRect });
    cands.sort(function (a, b) { return a.err - b.err; });
    if (!cands.length) return null;
    var best = cands[0], second = cands[1];
    if (best.err < 0.075 * minSide && (!second || best.err < 0.72 * Math.max(second.err, 0.001))) return best.shape;
    if (best.shape === 'rect' && best.err < 0.12 * minSide && maxR <= 4) return 'rect';
    return null;
  }

  function distRound(px, py, w, h, r) {
    if (r < 1) return Math.min(px, py, w - 1 - px, h - 1 - py);
    if (r > w / 2) r = w / 2;
    if (r > h / 2) r = h / 2;
    var inX = px < r || px > w - 1 - r;
    var inY = py < r || py > h - 1 - r;
    if (inX && inY) {
      var ax = px < r ? r : w - 1 - r;
      var ay = py < r ? r : h - 1 - r;
      return Math.abs(Math.hypot(px - ax, py - ay) - r);
    }
    return Math.min(px, py, w - 1 - px, h - 1 - py);
  }

  function distSideRound(px, py, w, h, r, left) {
    if (left) {
      if (px <= r) return distRound(px, py, Math.max(w, r * 2), h, r);
      return Math.min(py, h - 1 - py, Math.abs(px - (w - 1)));
    }
    if (px >= w - 1 - r) {
      var lx = px - (w - 1 - 2 * r);
      return distRound(lx, py, Math.max(w, r * 2), h, r);
    }
    return Math.min(py, h - 1 - py, px);
  }

  function classifyRest(plate, marks) {
    var w = plate.w, h = plate.h, sw = plate.sw;
    var ink = labelBinary(plate.bin, w, h, true);
    var figs = figList(marks);
    var lim = Math.max(14, sw * 5);
    var pending = [];
    for (var id = 1; id <= ink.n; id++) {
      var box = ink.boxes[id];
      if (ink.areas[id] < 6) continue;
      var bw = box.w, bh = box.h;
      var long = Math.max(bw, bh), short = Math.min(bw, bh);
      var fill = ink.areas[id] / (bw * bh);
      var pts = pixelsOf(plate.bin, w, ink.lab, id, box);
      if (long < Math.max(36, sw * 14) && isTriangle(pts, sw)) {
        marks.push(triangleMark(pts));
        clearLabel(plate.bin, w, ink.lab, id, box);
        continue;
      }
      var bands = busyBands(plate.bin, w, ink.lab, id, box);
      var thin = short <= Math.max(sw * 3.4, 8) && long >= short * 2.2 && fill < 0.62;
      var skinny = fill < 0.28 && long > 6 * sw && long >= short * 2.4;
      var flat = bands.rows <= Math.max(6, sw * 2.6) && bw > Math.max(bh * 1.7, 6 * sw);
      var upright = bands.cols <= Math.max(6, sw * 2.6) && bh > Math.max(bw * 1.7, 6 * sw);
      var ends = axisEnds(pts);
      var a = ends ? snapFig(ends[0], figs, lim) : -1;
      var b = ends ? snapFig(ends[1], figs, lim) : -1;
      pending.push({
        id: id, box: box, bw: bw, bh: bh,
        strokeLike: thin || skinny || flat || upright,
        linked: a >= 0 && b >= 0 && a !== b
      });
    }
    var margin = Math.max(4, Math.round(sw));
    for (var i = 0; i < pending.length; i++) {
      var item = pending[i];
      if (!item.linked && !(item.strokeLike && alone(item, pending, margin))) continue;
      marks.push({
        kind: 'stroke', x: item.box.x, y: item.box.y, w: item.bw, h: item.bh,
        mask: crop(plate.bin, w, ink.lab, item.id, item.box), mw: item.bw, mh: item.bh
      });
      clearLabel(plate.bin, w, ink.lab, item.id, item.box);
      item.taken = 1;
    }
    var texts = [];
    for (var t = 0; t < pending.length; t++) if (!pending[t].taken) texts.push(pending[t].box);
    var cells = characterCells(plate.bin, w, texts, sw);
    for (var c = 0; c < cells.length; c++) {
      var grid = rasterGrid(plate.bin, w, null, 0, cells[c]);
      if (!grid) continue;
      marks.push({ kind: 'glyph', x: cells[c].x, y: cells[c].y, w: cells[c].w, h: cells[c].h, grid: grid, ch: '', face: '', host: null });
    }
  }

  function axisEnds(pts) {
    if (!pts.length) return null;
    var left = pts[0], right = pts[0], top = pts[0], bot = pts[0];
    for (var i = 1; i < pts.length; i++) {
      var p = pts[i];
      if (p.x < left.x || (p.x === left.x && p.y < left.y)) left = p;
      if (p.x > right.x || (p.x === right.x && p.y > right.y)) right = p;
      if (p.y < top.y || (p.y === top.y && p.x < top.x)) top = p;
      if (p.y > bot.y || (p.y === bot.y && p.x > bot.x)) bot = p;
    }
    var horiz = Math.hypot(right.x - left.x, right.y - left.y);
    var vert = Math.hypot(bot.x - top.x, bot.y - top.y);
    return horiz >= vert ? [left, right] : [top, bot];
  }

  function boxGap(a, b) {
    var dx = 0, dy = 0;
    if (b.x > a.x + a.w) dx = b.x - (a.x + a.w);
    else if (a.x > b.x + b.w) dx = a.x - (b.x + b.w);
    if (b.y > a.y + a.h) dy = b.y - (a.y + a.h);
    else if (a.y > b.y + b.h) dy = a.y - (b.y + b.h);
    return { dx: dx, dy: dy };
  }

  function alone(item, pending, margin) {
    for (var i = 0; i < pending.length; i++) {
      if (pending[i] === item) continue;
      var gap = boxGap(item.box, pending[i].box);
      if (gap.dx <= margin && gap.dy <= margin) return false;
    }
    return true;
  }

  function clearLabel(bin, w, lab, id, box) {
    for (var y = 0; y < box.h; y++) for (var x = 0; x < box.w; x++) {
      if (lab[(box.y + y) * w + box.x + x] === id) bin[(box.y + y) * w + box.x + x] = 0;
    }
  }

  function characterCells(bin, imgW, boxes, sw) {
    var used = new Uint8Array(boxes.length);
    var cells = [];
    var join = Math.max(4, Math.round(sw));
    for (var i = 0; i < boxes.length; i++) {
      if (used[i]) continue;
      var line = [boxes[i]];
      used[i] = 1;
      var grew = true;
      while (grew) {
        grew = false;
        for (var j = 0; j < boxes.length; j++) {
          if (used[j]) continue;
          for (var k = 0; k < line.length; k++) {
            var gap = boxGap(line[k], boxes[j]);
            var overlapY = Math.min(line[k].y + line[k].h, boxes[j].y + boxes[j].h) - Math.max(line[k].y, boxes[j].y);
            if (gap.dy <= join || overlapY > 0) { used[j] = 1; line.push(boxes[j]); grew = true; break; }
          }
        }
      }
      var sliced = sliceLine(bin, imgW, line, sw);
      for (var s = 0; s < sliced.length; s++) cells.push(sliced[s]);
    }
    return cells;
  }

  function sliceLine(bin, imgW, comps, sw) {
    var items = comps.slice().sort(function (a, b) { return a.x - b.x; });
    var groups = [[items[0]]];
    for (var i = 1; i < items.length; i++) {
      var prev = groups[groups.length - 1];
      var gx1 = prev[0].x + prev[0].w;
      for (var p = 1; p < prev.length; p++) if (prev[p].x + prev[p].w > gx1) gx1 = prev[p].x + prev[p].w;
      var gap = items[i].x - gx1;
      var gh = 0;
      for (var q = 0; q < prev.length; q++) if (prev[q].h > gh) gh = prev[q].h;
      if (gap > Math.max(8, gh * 0.45)) groups.push([items[i]]);
      else prev.push(items[i]);
    }
    var out = [];
    for (var g = 0; g < groups.length; g++) {
      var part = sliceGroup(bin, imgW, groups[g], sw);
      for (var n = 0; n < part.length; n++) out.push(part[n]);
    }
    return out;
  }

  function groupBounds(comps) {
    var x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1;
    for (var i = 0; i < comps.length; i++) {
      var c = comps[i];
      if (c.x < x0) x0 = c.x;
      if (c.y < y0) y0 = c.y;
      if (c.x + c.w - 1 > x1) x1 = c.x + c.w - 1;
      if (c.y + c.h - 1 > y1) y1 = c.y + c.h - 1;
    }
    return { x0: x0, y0: y0, x1: x1, y1: y1 };
  }

  function sliceGroup(bin, imgW, comps, sw) {
    var b = groupBounds(comps);
    var wide = b.x1 - b.x0 + 1, tall = b.y1 - b.y0 + 1;
    var n = Math.max(1, Math.round(wide / Math.max(1, tall)));
    if (tall <= Math.max(8, sw * 3.4)) n = 1;
    var whole = tightBox(bin, imgW, b.x0, b.y0, b.x1 + 1, b.y1 + 1);
    if (!whole || n <= 1) return whole ? [whole] : [];
    var proj = new Uint16Array(wide);
    for (var y = b.y0; y <= b.y1; y++) for (var x = b.x0; x <= b.x1; x++) {
      if (bin[y * imgW + x]) proj[x - b.x0]++;
    }
    var inkCols = [];
    for (var p = 0; p < wide; p++) if (proj[p]) inkCols.push(proj[p]);
    var med = median(inkCols) || 1;
    var cuts = [];
    var cellW = wide / n;
    for (var i = 1; i < n; i++) {
      var ideal = Math.round(i * cellW);
      var rad = Math.max(2, Math.round(cellW * 0.4));
      var lo = Math.max(1, ideal - rad), hi = Math.min(wide - 2, ideal + rad);
      var best = -1, bestV = 1e9;
      for (var col = lo; col <= hi; col++) if (proj[col] < bestV) { bestV = proj[col]; best = col; }
      if (best < 0 || bestV > med * 0.35) continue;
      if (!cuts.length || best > cuts[cuts.length - 1] + 2) cuts.push(best);
    }
    if (!cuts.length) return [whole];
    var bounds = [0].concat(cuts).concat([wide]);
    var cells = [];
    for (var k = 0; k < bounds.length - 1; k++) {
      var cell = tightBox(bin, imgW, b.x0 + bounds[k], b.y0, b.x0 + bounds[k + 1], b.y1 + 1);
      if (cell) cells.push(cell);
    }
    return cells.length ? cells : [whole];
  }

  function tightBox(bin, imgW, x0, y0, x1, y1) {
    var a = 1e9, b = 1e9, c = -1, d = -1, any = 0;
    var imgH = (bin.length / imgW) | 0;
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > imgW) x1 = imgW;
    if (y1 > imgH) y1 = imgH;
    for (var y = y0; y < y1; y++) for (var x = x0; x < x1; x++) {
      if (!bin[y * imgW + x]) continue;
      any++;
      if (x < a) a = x;
      if (y < b) b = y;
      if (x > c) c = x;
      if (y > d) d = y;
    }
    if (!any) return null;
    return { x: a, y: b, w: c - a + 1, h: d - b + 1 };
  }

  function busyBands(bin, w, lab, id, box) {
    var rowP = new Uint16Array(box.h), colP = new Uint16Array(box.w);
    for (var y = 0; y < box.h; y++) for (var x = 0; x < box.w; x++) {
      if (lab[(box.y + y) * w + box.x + x] === id) { rowP[y]++; colP[x]++; }
    }
    var rowCut = Math.max(3, box.w * 0.22), colCut = Math.max(3, box.h * 0.22);
    var rows = 0, cols = 0;
    for (var r = 0; r < box.h; r++) if (rowP[r] > rowCut) rows++;
    for (var c = 0; c < box.w; c++) if (colP[c] > colCut) cols++;
    return { rows: rows, cols: cols };
  }

function pixelsOf(bin, w, lab, id, box) {
    var pts = [];
    for (var y = box.y; y < box.y + box.h; y++) for (var x = box.x; x < box.x + box.w; x++) {
      if (lab[y * w + x] === id) pts.push({ x: x, y: y });
    }
    return pts;
  }

  function crop(bin, w, lab, id, box) {
    var mask = new Uint8Array(box.w * box.h);
    for (var y = 0; y < box.h; y++) for (var x = 0; x < box.w; x++) {
      if (lab[(box.y + y) * w + box.x + x] === id) mask[y * box.w + x] = 1;
    }
    return mask;
  }

  function cross(o, a, b) { return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x); }

  function convexHull(pts) {
    var a = pts.slice().sort(function (p, q) { return p.x - q.x || p.y - q.y; });
    if (a.length < 3) return a;
    var lo = [], hi = [];
    for (var i = 0; i < a.length; i++) {
      while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], a[i]) <= 0) lo.pop();
      lo.push(a[i]);
    }
    for (var j = a.length - 1; j >= 0; j--) {
      while (hi.length >= 2 && cross(hi[hi.length - 2], hi[hi.length - 1], a[j]) <= 0) hi.pop();
      hi.push(a[j]);
    }
    lo.pop(); hi.pop();
    return lo.concat(hi);
  }

  function isTriangle(pts, sw) {
    if (pts.length < 6) return false;
    var hull = convexHull(pts);
    var simp = [];
    for (var i = 0; i < hull.length; i++) {
      var p = hull[(i + hull.length - 1) % hull.length], c = hull[i], n = hull[(i + 1) % hull.length];
      if (Math.abs(cross(p, c, n)) > 3) simp.push(c);
    }
    if (simp.length !== 3) return false;
    var sharp = 1e9, tip = 0;
    for (var k = 0; k < 3; k++) {
      var a = simp[(k + 2) % 3], b = simp[k], c = simp[(k + 1) % 3];
      var ang = vertexAngle(a, b, c);
      if (ang < sharp) { sharp = ang; tip = k; }
    }
    if (sharp > 70 * Math.PI / 180) return false;
    var area = Math.abs(cross(simp[0], simp[1], simp[2])) / 2;
    return area > Math.max(4, 0.6 * sw * sw);
  }

  function vertexAngle(a, b, c) {
    var u = Math.atan2(a.y - b.y, a.x - b.x);
    var v = Math.atan2(c.y - b.y, c.x - b.x);
    var d = Math.abs(u - v);
    if (d > Math.PI) d = 2 * Math.PI - d;
    return d;
  }

  function triangleMark(pts) {
    var hull = convexHull(pts);
    var simp = [];
    for (var i = 0; i < hull.length; i++) {
      var p = hull[(i + hull.length - 1) % hull.length], c = hull[i], n = hull[(i + 1) % hull.length];
      if (Math.abs(cross(p, c, n)) > 3) simp.push(c);
    }
    if (simp.length < 3) simp = hull;
    var sharp = 1e9, tip = 0;
    for (var k = 0; k < simp.length; k++) {
      var ang = vertexAngle(simp[(k + simp.length - 1) % simp.length], simp[k], simp[(k + 1) % simp.length]);
      if (ang < sharp) { sharp = ang; tip = k; }
    }
    var a = simp[(tip + 1) % simp.length], b = simp[(tip + simp.length - 1) % simp.length];
    return {
      kind: 'head',
      tip: { x: simp[tip].x, y: simp[tip].y },
      base: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }
    };
  }

  function rasterGrid(bin, imgW, lab, id, box) {
    var side = Math.max(box.w, box.h);
    if (side < 2) return null;
    var ox = (side - box.w) / 2, oy = (side - box.h) / 2;
    var grid = new Uint8Array(256);
    var any = 0;
    for (var gy = 0; gy < 16; gy++) for (var gx = 0; gx < 16; gx++) {
      var x0 = box.x - ox + (gx / 16) * side;
      var y0 = box.y - oy + (gy / 16) * side;
      var x1 = box.x - ox + ((gx + 1) / 16) * side;
      var y1 = box.y - oy + ((gy + 1) / 16) * side;
      var ink = 0, tot = 0;
      var xa = Math.floor(x0), xb = Math.ceil(x1), ya = Math.floor(y0), yb = Math.ceil(y1);
      for (var y = ya; y < yb; y++) for (var x = xa; x < xb; x++) {
        if (x < box.x || y < box.y || x >= box.x + box.w || y >= box.y + box.h) { tot++; continue; }
        tot++;
        if (lab) {
          if (lab[y * imgW + x] === id) { ink++; any++; }
        } else if (bin[y * imgW + x]) { ink++; any++; }
      }
      grid[gy * 16 + gx] = tot ? Math.max(0, Math.min(15, Math.round(ink / tot * 15))) : 0;
    }
    return any ? grid : null;
  }

  function bridge(marks, plate) {
    var sw = plate.sw;
    var keep = [], heads = [], raw = [];
    for (var i = 0; i < marks.length; i++) {
      var m = marks[i];
      if (m.kind === 'head') heads.push(m);
      else if (m.kind === 'stroke') raw.push(m);
      else keep.push(m);
    }
    var polys = [];
    for (var r = 0; r < raw.length; r++) {
      var made = skeletonPolys(raw[r], sw);
      for (var k = 0; k < made.length; k++) polys.push(made[k]);
    }
    joinEnds(polys, sw);
    attachHeads(polys, heads, sw);
    for (var p = 0; p < polys.length; p++) {
      if (polyLen(polys[p].pts) < Math.max(6, sw * 2.5)) continue;
      keep.push({
        kind: 'stroke',
        pts: polys[p].pts,
        dashed: polys[p].gaps >= 3,
        h0: !!polys[p].h0,
        h1: !!polys[p].h1
      });
    }
    marks.length = 0;
    for (var n = 0; n < keep.length; n++) marks.push(keep[n]);
  }

  function polyLen(pts) {
    var s = 0;
    for (var i = 1; i < pts.length; i++) s += Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
    return s;
  }

  function zhangSuen(src, w, h) {
    var a = new Uint8Array(src);
    var del = new Int32Array(src.length);
    for (var guard = 0; guard < 64; guard++) {
      var changed = false;
      for (var step = 0; step < 2; step++) {
        var nd = 0;
        for (var y = 1; y < h - 1; y++) for (var x = 1; x < w - 1; x++) {
          var i = y * w + x;
          if (!a[i]) continue;
          var p2 = a[i - w], p3 = a[i - w + 1], p4 = a[i + 1], p5 = a[i + w + 1];
          var p6 = a[i + w], p7 = a[i + w - 1], p8 = a[i - 1], p9 = a[i - w - 1];
          var bp = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
          if (bp < 2 || bp > 6) continue;
          var seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2];
          var ap = 0;
          for (var k = 0; k < 8; k++) if (!seq[k] && seq[k + 1]) ap++;
          if (ap !== 1) continue;
          if (step === 0) {
            if (p2 * p4 * p6 !== 0) continue;
            if (p4 * p6 * p8 !== 0) continue;
          } else {
            if (p2 * p4 * p8 !== 0) continue;
            if (p2 * p6 * p8 !== 0) continue;
          }
          del[nd++] = i;
        }
        if (!nd) continue;
        changed = true;
        for (var d = 0; d < nd; d++) a[del[d]] = 0;
      }
      if (!changed) break;
    }
    return a;
  }

  function skeletonPolys(mark, sw) {
    var pad = 2;
    var mw = mark.mw, mh = mark.mh;
    var w = mw + pad * 2, h = mh + pad * 2;
    var mask = new Uint8Array(w * h);
    for (var row = 0; row < mh; row++) mask.set(mark.mask.subarray(row * mw, row * mw + mw), (row + pad) * w + pad);
    var dt = distanceToPaper(mask, w, h);
    var sk = zhangSuen(mask, w, h);
    var deg = new Uint8Array(sk.length);
    var dirs = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
    function nbs(i) {
      var x = i % w, y = (i / w) | 0, out = [];
      for (var d = 0; d < 8; d++) {
        var nx = x + dirs[d][0], ny = y + dirs[d][1];
        if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
        var j = ny * w + nx;
        if (sk[j]) out.push(j);
      }
      return out;
    }
    for (var i = 0; i < sk.length; i++) if (sk[i]) deg[i] = nbs(i).length;
    var used = {};
    function ekey(a, b) { return a < b ? a + ':' + b : b + ':' + a; }
    function consume(start, nxt) {
      var key = ekey(start, nxt);
      if (used[key]) return null;
      used[key] = 1;
      var seq = [start, nxt];
      var prev = start, cur = nxt;
      while (deg[cur] === 2) {
        var around = nbs(cur), nxt2 = -1;
        for (var k = 0; k < around.length; k++) {
          if (around[k] === prev) continue;
          if (used[ekey(cur, around[k])]) continue;
          nxt2 = around[k];
          break;
        }
        if (nxt2 < 0) break;
        used[ekey(cur, nxt2)] = 1;
        seq.push(nxt2);
        prev = cur;
        cur = nxt2;
      }
      return seq;
    }
    var branches = [];
    function consider(i) {
      var around = nbs(i);
      for (var k = 0; k < around.length; k++) {
        var seq = consume(i, around[k]);
        if (seq && seq.length > 1) branches.push(seq);
      }
    }
    for (var p = 0; p < sk.length; p++) if (sk[p] && deg[p] !== 2) consider(p);
    for (var q = 0; q < sk.length; q++) if (sk[q] && deg[q] === 2) consider(q);
    var out = [];
    for (var b = 0; b < branches.length; b++) {
      var pts = [];
      for (var t = 0; t < branches[b].length; t++) {
        var idx = branches[b][t];
        pts.push({ x: mark.x + (idx % w) - pad, y: mark.y + ((idx / w) | 0) - pad });
      }
      if (polyLen(pts) < Math.max(4, sw * 1.5)) continue;
      var fat0 = endFat(pts, false, dt, mark.x - pad, mark.y - pad, w, h, sw);
      var fat1 = endFat(pts, true, dt, mark.x - pad, mark.y - pad, w, h, sw);
      out.push({ pts: pts, gaps: 0, h0: fat0, h1: fat1 });
    }
    return out;
  }

  function endFat(pts, fromEnd, dt, ox, oy, mw, mh, sw) {
    var reach = Math.max(10, sw * 8);
    var walked = 0, maxR = 0;
    var n = pts.length;
    var start = fromEnd ? n - 1 : 0;
    var step = fromEnd ? -1 : 1;
    var mids = [];
    var a = (n * 0.3) | 0, b = (n * 0.7) | 0;
    for (var m = a; m <= b && m < n; m++) {
      var mx = Math.round(pts[m].x - ox), my = Math.round(pts[m].y - oy);
      if (mx >= 0 && my >= 0 && mx < mw && my < mh) mids.push(dt[my * mw + mx]);
    }
    for (var i = start; i >= 0 && i < n; i += step) {
      if (i !== start) walked += Math.hypot(pts[i].x - pts[i - step].x, pts[i].y - pts[i - step].y);
      if (walked > reach) break;
      var x = Math.round(pts[i].x - ox), y = Math.round(pts[i].y - oy);
      if (x < 0 || y < 0 || x >= mw || y >= mh) continue;
      if (dt[y * mw + x] > maxR) maxR = dt[y * mw + x];
    }
    var tip = fromEnd ? pts[n - 1] : pts[0];
    var ex = Math.round(tip.x - ox), ey = Math.round(tip.y - oy);
    var rad = Math.max(8, sw * 3.5);
    var yLo = Math.max(0, ey - rad), yHi = Math.min(mh - 1, ey + rad);
    var xLo = Math.max(0, ex - rad), xHi = Math.min(mw - 1, ex + rad);
    for (var yy = yLo; yy <= yHi; yy++) for (var xx = xLo; xx <= xHi; xx++) {
      if ((xx - ex) * (xx - ex) + (yy - ey) * (yy - ey) > rad * rad) continue;
      if (dt[yy * mw + xx] > maxR) maxR = dt[yy * mw + xx];
    }
    var mid = median(mids);
    return maxR > Math.max(sw * 1.05, mid * 1.55);
  }

  function endDir(pts, atStart) {
    var a = atStart ? pts[0] : pts[pts.length - 1];
    var idx = atStart ? Math.min(pts.length - 1, 5) : Math.max(0, pts.length - 1 - 5);
    var b = pts[idx];
    return Math.atan2(a.y - b.y, a.x - b.x);
  }

  function angDiff(a, b) {
    var d = Math.abs(a - b);
    if (d > Math.PI) d = 2 * Math.PI - d;
    return d;
  }

  function joinEnds(polys, sw) {
    var lim = Math.max(6, sw * 3);
    while (polys.length > 1) {
      var best = null, bestD = lim;
      for (var i = 0; i < polys.length; i++) for (var j = i + 1; j < polys.length; j++) {
        var A = polys[i], B = polys[j];
        var ends = [[0, 0], [0, 1], [1, 0], [1, 1]];
        for (var e = 0; e < 4; e++) {
          var pa = ends[e][0] ? A.pts[A.pts.length - 1] : A.pts[0];
          var pb = ends[e][1] ? B.pts[B.pts.length - 1] : B.pts[0];
          var dist = Math.hypot(pa.x - pb.x, pa.y - pb.y);
          if (dist > bestD) continue;
          var da = endDir(A.pts, !ends[e][0]);
          var db = endDir(B.pts, !ends[e][1]);
          if (Math.abs(angDiff(da, db) - Math.PI) > 30 * Math.PI / 180) continue;
          var gapDir = Math.atan2(pb.y - pa.y, pb.x - pa.x);
          if (dist > 1.5 && angDiff(da, gapDir) > 35 * Math.PI / 180) continue;
          bestD = dist;
          best = { i: i, j: j, aEnd: ends[e][0], bEnd: ends[e][1], dist: dist };
        }
      }
      if (!best) break;
      var A2 = polys[best.i], B2 = polys[best.j];
      var pa2 = best.aEnd ? A2.pts.slice() : A2.pts.slice().reverse();
      var pb2 = best.bEnd ? B2.pts.slice().reverse() : B2.pts.slice();
      var hA = best.aEnd ? A2.h0 : A2.h1;
      var hB = best.bEnd ? B2.h0 : B2.h1;
      var gaps = A2.gaps + B2.gaps;
      if (best.dist >= 0.4 * sw && best.dist <= Math.max(3 * sw, 8)) gaps++;
      var merged = { pts: pa2.concat(pb2), gaps: gaps, h0: hA, h1: hB };
      var next = [];
      for (var k = 0; k < polys.length; k++) if (k !== best.i && k !== best.j) next.push(polys[k]);
      next.push(merged);
      polys.length = 0;
      for (var n = 0; n < next.length; n++) polys.push(next[n]);
    }
  }

  function attachHeads(polys, heads, sw) {
    var lim = Math.max(8, sw * 2.5);
    for (var i = 0; i < heads.length; i++) {
      var head = heads[i];
      var best = null, bestD = lim;
      for (var p = 0; p < polys.length; p++) {
        var pts = polys[p].pts;
        var d0 = Math.hypot(pts[0].x - head.base.x, pts[0].y - head.base.y);
        var d1 = Math.hypot(pts[pts.length - 1].x - head.base.x, pts[pts.length - 1].y - head.base.y);
        if (d0 < bestD) { bestD = d0; best = { p: p, end: 0 }; }
        if (d1 < bestD) { bestD = d1; best = { p: p, end: 1 }; }
      }
      if (!best) continue;
      var poly = polys[best.p];
      if (best.end === 0) { poly.h0 = true; poly.pts[0] = { x: head.tip.x, y: head.tip.y }; }
      else { poly.h1 = true; poly.pts[poly.pts.length - 1] = { x: head.tip.x, y: head.tip.y }; }
    }
  }

  function figList(marks) {
    var a = [];
    for (var i = 0; i < marks.length; i++) if (marks[i].kind === 'figure') a.push(marks[i]);
    return a;
  }

  function nest(marks, sw) {
    var figs = figList(marks);
    var m = Math.max(1, sw);
    for (var i = 0; i < figs.length; i++) {
      var inner = [];
      for (var j = 0; j < figs.length; j++) {
        if (i === j) continue;
        var a = figs[j], b = figs[i];
        if (a.x >= b.x + m && a.y >= b.y + m && a.x + a.w <= b.x + b.w - m && a.y + a.h <= b.y + b.h - m) inner.push(j);
      }
      figs[i].contains = inner;
    }
  }

  function book() {
    if (bookTried) return bookCache;
    bookTried = true;
    if (!bookStr) return null;
    var raw = bookStr;
    bookStr = '';
    var bytes = b64(raw);
    bookCache = parseBook(bytes);
    return bookCache;
  }

  function b64(s) {
    var bin = atob(s);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i) & 255;
    return out;
  }

  function u16(b, o) { return b[o] | (b[o + 1] << 8); }

  function parseBook(bytes) {
    if (!bytes || bytes.length < 16) throw new Error('字形库无法读取');
    var magic = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3], bytes[4]);
    if (magic !== 'JWGB1') throw new Error('字形库无法读取');
    var ver = u16(bytes, 5), cell = u16(bytes, 7), fc = u16(bytes, 9), cc = u16(bytes, 11);
    if (ver !== 1 || cell !== 16 || fc < 1 || cc < 1) throw new Error('字形库无法读取');
    var o = 13, faces = [];
    for (var i = 0; i < fc; i++) {
      var name = '';
      while (o < bytes.length && bytes[o] !== 0) { name += String.fromCharCode(bytes[o]); o++; }
      if (o >= bytes.length || bytes[o] !== 0) throw new Error('字形库无法读取');
      o++;
      if (!FACE[name]) throw new Error('未知字形：' + name);
      faces.push(name);
    }
    var chars = [];
    for (var c = 0; c < cc; c++) { chars.push(String.fromCharCode(u16(bytes, o))); o += 2; }
    var glen = 128;
    if (bytes.length < o + fc * cc * glen) throw new Error('字形库无法读取');
    var buckets = new Array(4096);
    for (var b = 0; b < 4096; b++) buckets[b] = [];
    for (var f = 0; f < fc; f++) for (var ci = 0; ci < cc; ci++) {
      var off = o + (f * cc + ci) * glen;
      var sum = 0, bits = 0;
      var acc = new Uint16Array(16);
      for (var k = 0; k < 256; k++) {
        var byte = bytes[off + (k >> 1)];
        var v = (k & 1) ? (byte & 15) : (byte >> 4);
        sum += v;
        var by = (k / 16) | 0, bx = k % 16;
        acc[((by >> 2) * 4) + (bx >> 2)] += v;
      }
      for (var celln = 0; celln < 16; celln++) if (acc[celln] >= 128) bits |= 1 << (15 - celln);
      buckets[bits >>> 4].push({ off: off, face: faces[f], ch: chars[ci], sum: sum });
    }
    return { bytes: bytes, buckets: buckets, chars: chars, faces: faces };
  }

  function gridBits(grid) {
    var acc = new Uint16Array(16);
    for (var i = 0; i < 256; i++) {
      var by = (i / 16) | 0, bx = i % 16;
      acc[((by >> 2) * 4) + (bx >> 2)] += grid[i];
    }
    var bits = 0;
    for (var c = 0; c < 16; c++) if (acc[c] >= 128) bits |= 1 << (15 - c);
    return bits;
  }

  function sadAt(grid, bytes, off) {
    var s = 0;
    for (var i = 0; i < 256; i++) {
      var byte = bytes[off + (i >> 1)];
      var v = (i & 1) ? (byte & 15) : (byte >> 4);
      s += v > grid[i] ? v - grid[i] : grid[i] - v;
    }
    return s;
  }

  function recognize(grid, bk) {
    var bits = gridBits(grid);
    var bucket = bits >>> 4;
    var seen = {};
    var list = [];
    function take(id) {
      var arr = bk.buckets[id];
      if (!arr) return;
      for (var i = 0; i < arr.length; i++) {
        var key = arr[i].off;
        if (seen[key]) continue;
        seen[key] = 1;
        list.push(arr[i]);
      }
    }
    take(bucket);
    for (var bit = 0; bit < 12; bit++) take(bucket ^ (1 << (11 - bit)));
    var gsum = 0;
    for (var g = 0; g < 256; g++) gsum += grid[g];
    var best = 1e9, second = 1e9, hit = null;
    for (var c = 0; c < list.length; c++) {
      if (Math.abs(list[c].sum - gsum) > 880) continue;
      var s = sadAt(grid, bk.bytes, list[c].off);
      if (s < best) { second = best; best = s; hit = list[c]; }
      else if (s <= second) second = s;
    }
    if (hit && best <= 880 && best * 5 <= second * 4) return { ch: hit.ch, face: hit.face };
    return { ch: '\u25a1', face: '' };
  }

  function recognizeGlyphs(marks) {
    var bk = null;
    try { bk = book(); } catch (e) { throw e; }
    for (var i = 0; i < marks.length; i++) {
      if (marks[i].kind !== 'glyph') continue;
      if (!bk) { marks[i].ch = ''; marks[i].face = ''; continue; }
      var r = recognize(marks[i].grid, bk);
      marks[i].ch = r.ch;
      marks[i].face = r.face;
    }
  }

  function bindGlyphs(marks, sw) {
    var figs = figList(marks);
    var strokes = [];
    for (var i = 0; i < marks.length; i++) if (marks[i].kind === 'stroke' && marks[i].pts) strokes.push(marks[i]);
    for (var g = 0; g < marks.length; g++) {
      var glyph = marks[g];
      if (glyph.kind !== 'glyph') continue;
      var cx = glyph.x + glyph.w / 2, cy = glyph.y + glyph.h / 2;
      var best = null, bestA = 1e15;
      for (var f = 0; f < figs.length; f++) {
        var fig = figs[f];
        var x = fig.x, y = fig.y, fw = fig.w, fh = fig.h;
        if (fig.shape === 'diamond') { x += fw * 0.25; y += fh * 0.25; fw *= 0.5; fh *= 0.5; }
        else if (fig.shape === 'ellipse') { x += fw * 0.15; y += fh * 0.15; fw *= 0.7; fh *= 0.7; }
        else { x += sw; y += sw; fw -= 2 * sw; fh -= 2 * sw; }
        if (fw < 1 || fh < 1) continue;
        if (cx < x || cy < y || cx > x + fw || cy > y + fh) continue;
        var area = fig.w * fig.h;
        if (area < bestA) { bestA = area; best = fig; }
      }
      if (best && best.contains && best.contains.length && (cy - best.y) > best.h * 0.28) best = null;
      if (best) { glyph.host = { kind: 'figure', fig: best }; continue; }
      var bd = 0.8 * glyph.h, bi = null;
      for (var s = 0; s < strokes.length; s++) {
        var d = distToPoly(cx, cy, strokes[s].pts);
        if (d < bd) { bd = d; bi = strokes[s]; }
      }
      glyph.host = bi ? { kind: 'stroke', stroke: bi } : { kind: 'float' };
    }
  }

  function distToPoly(px, py, pts) {
    var best = 1e9;
    for (var i = 1; i < pts.length; i++) {
      var d = distSeg(px, py, pts[i - 1].x, pts[i - 1].y, pts[i].x, pts[i].y);
      if (d < best) best = d;
    }
    if (pts.length === 1) best = Math.hypot(px - pts[0].x, py - pts[0].y);
    return best;
  }

  function dropBorder(marks) {
    var figs = figList(marks);
    if (figs.length < 2) return;
    var best = null;
    for (var i = 0; i < figs.length; i++) {
      var f = figs[i];
      var union = null, all = true, n = 0;
      for (var j = 0; j < figs.length; j++) {
        if (figs[j] === f) continue;
        n++;
        var c = { x: figs[j].x + figs[j].w / 2, y: figs[j].y + figs[j].h / 2 };
        if (c.x < f.x || c.y < f.y || c.x > f.x + f.w || c.y > f.y + f.h) all = false;
        union = union ? {
          x: Math.min(union.x, figs[j].x), y: Math.min(union.y, figs[j].y),
          x1: Math.max(union.x1, figs[j].x + figs[j].w), y1: Math.max(union.y1, figs[j].y + figs[j].h)
        } : { x: figs[j].x, y: figs[j].y, x1: figs[j].x + figs[j].w, y1: figs[j].y + figs[j].h };
      }
      if (!all || !n || !union) continue;
      var uw = union.x1 - union.x, uh = union.y1 - union.y;
      var iw = Math.max(0, Math.min(f.x + f.w, union.x1) - Math.max(f.x, union.x));
      var ih = Math.max(0, Math.min(f.y + f.h, union.y1) - Math.max(f.y, union.y));
      if (!(uw * uh) || (iw * ih) / (uw * uh) <= 0.85) continue;
      if (hostedCount(marks, f)) continue;
      if (!best || f.w * f.h > best.w * best.h) best = f;
    }
    if (!best) return;
    var idx = marks.indexOf(best);
    if (idx >= 0) marks.splice(idx, 1);
  }

  function hostedCount(marks, fig) {
    var n = 0;
    for (var i = 0; i < marks.length; i++) {
      var g = marks[i];
      if (g.kind === 'glyph' && g.host && g.host.kind === 'figure' && g.host.fig === fig && g.ch) n++;
    }
    return n;
  }

  function emit(marks, plate) {
    var figs = figList(marks).slice().sort(function (a, b) { return a.y - b.y || a.x - b.x; });
    var recs = [];
    var squares = 0;
    for (var i = 0; i < marks.length; i++) if (marks[i].kind === 'glyph' && marks[i].ch === '\u25a1') squares++;
    for (var f = 0; f < figs.length; f++) {
      var fig = figs[f];
      var glyphs = glyphsOn(marks, fig);
      var styled = styleOf(glyphs, plate);
      var box = scaleBox(plate, fig);
      var spec = {
        id: 'tmp', type: fig.contains.length ? 'group' : fig.shape,
        x: box.x, y: box.y, w: box.w, h: box.h, text: styled.text
      };
      if (styled.size) spec.size = styled.size;
      if (styled.font) { spec.font = styled.font; spec.bold = styled.bold; }
      var fill = sampleFill(plate, fig);
      var stroke = sampleStroke(plate, fig);
      if (fill) spec.fill = fill;
      if (stroke) spec.stroke = stroke;
      recs.push({ node: mkNode(spec), fig: fig, y: box.y, x: box.x });
    }
    var floats = floatBlocks(marks);
    for (var t = 0; t < floats.length; t++) {
      var block = floats[t];
      var st = styleOf(block.glyphs, plate);
      var box2 = scaleBox(plate, block);
      var spec2 = { id: 'tmp', type: 'text', x: box2.x, y: box2.y, w: Math.max(8, box2.w), h: Math.max(8, box2.h), text: st.text };
      if (st.size) spec2.size = st.size;
      if (st.font) { spec2.font = st.font; spec2.bold = st.bold; }
      recs.push({ node: mkNode(spec2), y: box2.y, x: box2.x, block: block });
    }
    recs.sort(function (a, b) { return a.y - b.y || a.x - b.x; });
    var nodes = [];
    for (var n = 0; n < recs.length; n++) {
      recs[n].node.id = 'n' + (n + 1);
      nodes.push(recs[n].node);
    }
    var page = { id: 'root', name: '总图', nodes: nodes, links: [], view: null };
    for (var pi = 0; pi < nodes.length; pi++) nodes[pi].parent = findParent(nodes[pi], page);
    var idOf = new Map();
    for (var r = 0; r < recs.length; r++) if (recs[r].fig) idOf.set(recs[r].fig, recs[r].node.id);
    titleRole(recs, marks);
    var linkRecs = linkRecsOf(marks, plate, idOf);
    linkRecs.sort(function (a, b) { return a.y - b.y || a.x - b.x; });
    var links = [];
    for (var L = 0; L < linkRecs.length; L++) {
      var lr = linkRecs[L];
      var link = { id: 'k' + (L + 1), from: lr.from, to: lr.to, dir: lr.dir, route: lr.route, label: lr.label || '' };
      if (lr.dashed) link.kind = 'ctrl';
      links.push(link);
    }
    page.links = links;
    var notes = [];
    if (linkRecs.dropped) notes.push('有' + linkRecs.dropped + '条笔画两端没有落到两个图形上，已略过。');
    if (squares) notes.push('有' + squares + '个字未识别，以□标出。');
    return { page: page, notes: notes };
  }

  function glyphsOn(marks, fig) {
    var a = [];
    for (var i = 0; i < marks.length; i++) {
      var g = marks[i];
      if (g.kind === 'glyph' && g.host && g.host.kind === 'figure' && g.host.fig === fig) a.push(g);
    }
    return a;
  }

  function scaleBox(plate, b) {
    var x = Math.round(b.x * plate.scaleX);
    var y = Math.round(b.y * plate.scaleY);
    var w = Math.round((b.x + b.w) * plate.scaleX) - x;
    var h = Math.round((b.y + b.h) * plate.scaleY) - y;
    if (w < 1) w = 1;
    if (h < 1) h = 1;
    return { x: x, y: y, w: w, h: h };
  }

  function styleOf(glyphs, plate) {
    var usable = [];
    for (var i = 0; i < glyphs.length; i++) if (glyphs[i].ch) usable.push(glyphs[i]);
    if (!usable.length) return { text: '', size: 0, font: '', bold: false };
    var lines = clusterLines(usable);
    var text = [];
    for (var L = 0; L < lines.length; L++) text.push(joinLine(lines[L]));
    var heights = usable.map(function (g) { return g.h * plate.scaleY; });
    var size = Math.max(11, Math.min(28, Math.round(median(heights))));
    var faces = {};
    for (var f = 0; f < usable.length; f++) {
      if (!usable[f].face || usable[f].ch === '\u25a1') continue;
      faces[usable[f].face] = (faces[usable[f].face] || 0) + 1;
    }
    var face = '', best = 0;
    for (var name in faces) if (faces[name] > best) { best = faces[name]; face = name; }
    var mapped = FACE[face] || null;
    return { text: text.join('\n'), size: size, font: mapped ? mapped.font : '', bold: mapped ? mapped.bold : false };
  }

  function clusterLines(glyphs) {
    var gs = glyphs.slice().sort(function (a, b) { return a.y - b.y || a.x - b.x; });
    var lines = [];
    for (var i = 0; i < gs.length; i++) {
      var g = gs[i], cy = g.y + g.h / 2, line = null;
      for (var L = 0; L < lines.length; L++) {
        if (Math.abs(cy - lines[L].cy) <= Math.max(g.h, lines[L].h) * 0.6) { line = lines[L]; break; }
      }
      if (!line) { line = { gs: [], cy: cy, h: g.h }; lines.push(line); }
      line.gs.push(g);
      var sy = 0;
      for (var k = 0; k < line.gs.length; k++) sy += line.gs[k].y + line.gs[k].h / 2;
      line.cy = sy / line.gs.length;
      line.h = Math.max(line.h, g.h);
    }
    lines.sort(function (a, b) { return a.cy - b.cy; });
    return lines;
  }

  function joinLine(line) {
    var gs = line.gs.slice().sort(function (a, b) { return a.x - b.x; });
    var h = median(gs.map(function (g) { return g.h; }));
    var s = '', prev = null;
    for (var i = 0; i < gs.length; i++) {
      if (prev && gs[i].x - (prev.x + prev.w) > 0.45 * h) s += ' ';
      s += gs[i].ch;
      prev = gs[i];
    }
    return s;
  }

  function floatBlocks(marks) {
    var gs = [];
    for (var i = 0; i < marks.length; i++) {
      var g = marks[i];
      if (g.kind === 'glyph' && g.host && g.host.kind === 'float' && g.ch) gs.push(g);
    }
    if (!gs.length) return [];
    var lines = clusterLines(gs);
    var blocks = [];
    for (var L = 0; L < lines.length; L++) {
      var box = unionGlyphs(lines[L].gs);
      var prev = blocks.length ? blocks[blocks.length - 1] : null;
      var overlap = prev && Math.min(prev.x + prev.w, box.x + box.w) - Math.max(prev.x, box.x) > Math.min(prev.w, box.w) * 0.3;
      if (prev && overlap && box.y - (prev.y + prev.h) < lines[L].h * 0.8) {
        prev.glyphs = prev.glyphs.concat(lines[L].gs);
        var u = unionGlyphs(prev.glyphs);
        prev.x = u.x; prev.y = u.y; prev.w = u.w; prev.h = u.h;
      } else blocks.push({ glyphs: lines[L].gs.slice(), x: box.x, y: box.y, w: box.w, h: box.h });
    }
    return blocks;
  }

  function unionGlyphs(gs) {
    var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (var i = 0; i < gs.length; i++) {
      if (gs[i].x < x0) x0 = gs[i].x;
      if (gs[i].y < y0) y0 = gs[i].y;
      if (gs[i].x + gs[i].w > x1) x1 = gs[i].x + gs[i].w;
      if (gs[i].y + gs[i].h > y1) y1 = gs[i].y + gs[i].h;
    }
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }

  function titleRole(recs, marks) {
    var figs = [];
    var texts = [];
    for (var i = 0; i < recs.length; i++) {
      if (recs[i].fig) figs.push(recs[i].node);
      if (recs[i].block) texts.push(recs[i]);
    }
    if (!texts.length) return;
    var heights = [];
    for (var m = 0; m < marks.length; m++) if (marks[m].kind === 'glyph') heights.push(marks[m].h);
    var med = median(heights) || 1;
    var top = null;
    for (var t = 0; t < texts.length; t++) {
      var b = texts[t].block;
      var tall = false;
      for (var g = 0; g < b.glyphs.length; g++) if (b.glyphs[g].h > med * 1.3) tall = true;
      if (!tall) continue;
      var above = true;
      for (var f = 0; f < figs.length; f++) if (b.y + b.h > figs[f].y + 2) above = false;
      if (!above) continue;
      if (!top || b.y < top.block.y) top = texts[t];
    }
    if (top) top.node.role = 'title';
  }

  function sampleFill(plate, fig) {
    var cols = [];
    var inset = Math.max(2, plate.sw * 2);
    for (var gy = 1; gy <= 3; gy++) for (var gx = 1; gx <= 3; gx++) {
      var x = fig.x + inset + (fig.w - inset * 2) * gx / 4;
      var y = fig.y + inset + (fig.h - inset * 2) * gy / 4;
      cols.push(atSrc(plate, x, y));
    }
    return colorIf(cols, false);
  }

  function sampleStroke(plate, fig) {
    var cols = [];
    var o = Math.max(1, plate.sw * 0.4);
    var pts = [
      [fig.x + fig.w / 2, fig.y - o], [fig.x + fig.w / 2, fig.y + fig.h + o],
      [fig.x - o, fig.y + fig.h / 2], [fig.x + fig.w + o, fig.y + fig.h / 2]
    ];
    for (var i = 0; i < pts.length; i++) cols.push(atSrc(plate, pts[i][0], pts[i][1]));
    return colorIf(cols, true);
  }

  function atSrc(plate, wx, wy) {
    var sx = Math.round(wx * plate.scaleX), sy = Math.round(wy * plate.scaleY);
    if (sx < 0) sx = 0;
    if (sy < 0) sy = 0;
    if (sx >= plate.srcW) sx = plate.srcW - 1;
    if (sy >= plate.srcH) sy = plate.srcH - 1;
    var i = (sy * plate.srcW + sx) * 4;
    if (plate.src[i + 3] < 16) return [255, 255, 255];
    return [plate.src[i], plate.src[i + 1], plate.src[i + 2]];
  }

  function colorIf(cols, stroke) {
    var r = 0, g = 0, b = 0;
    for (var i = 0; i < cols.length; i++) { r += cols[i][0]; g += cols[i][1]; b += cols[i][2]; }
    r /= cols.length; g /= cols.length; b /= cols.length;
    var lum = (r * 76 + g * 150 + b * 30) >> 8;
    var spread = Math.max(r, g, b) - Math.min(r, g, b);
    if (!stroke && lum > 225 && spread <= 28) return '';
    if (stroke && spread <= 28) return '';
    function hex(v) { var s = Math.round(v).toString(16); return s.length < 2 ? '0' + s : s; }
    return '#' + hex(r) + hex(g) + hex(b);
  }

  function linkRecsOf(marks, plate, idOf) {
    var figs = figList(marks);
    var lim = Math.max(14, plate.sw * 5);
    var raw = [];
    var dropped = 0;
    for (var i = 0; i < marks.length; i++) {
      var s = marks[i];
      if (s.kind !== 'stroke' || !s.pts || s.pts.length < 2) continue;
      var a = snapFig(s.pts[0], figs, lim);
      var b = snapFig(s.pts[s.pts.length - 1], figs, lim);
      if (a < 0 || b < 0 || a === b) { dropped++; continue; }
      var from = a, to = b, dir = 'none';
      if (s.h0 && s.h1) dir = 'both';
      else if (s.h1) dir = 'one';
      else if (s.h0) { dir = 'one'; from = b; to = a; }
      var label = strokeLabel(marks, s);
      var mid = s.pts[(s.pts.length / 2) | 0];
      raw.push({
        from: from, to: to, dir: dir, dashed: !!s.dashed, label: label,
        route: routeOf(s.pts, plate.sw), y: mid.y, x: mid.x
      });
    }
    var merged = mergeLinks(raw);
    var out = [];
    for (var k = 0; k < merged.length; k++) {
      var fromId = idOf.get(figs[merged[k].from]);
      var toId = idOf.get(figs[merged[k].to]);
      if (!fromId || !toId || fromId === toId) { dropped++; continue; }
      out.push({
        from: fromId, to: toId, dir: merged[k].dir, route: merged[k].route,
        label: merged[k].label, dashed: merged[k].dashed, y: merged[k].y, x: merged[k].x
      });
    }
    out.dropped = dropped;
    return out;
  }

  function snapFig(pt, figs, lim) {
    var best = -1, bestD = lim;
    for (var i = 0; i < figs.length; i++) {
      var d = distRectBoundary(pt.x, pt.y, figs[i]);
      if (d < bestD) { bestD = d; best = i; }
    }
    return best;
  }

  function distRectBoundary(px, py, r) {
    var x0 = r.x, y0 = r.y, x1 = r.x + r.w, y1 = r.y + r.h;
    var dx = px < x0 ? x0 - px : (px > x1 ? px - x1 : 0);
    var dy = py < y0 ? y0 - py : (py > y1 ? py - y1 : 0);
    if (dx || dy) return Math.hypot(dx, dy);
    return Math.min(px - x0, x1 - px, py - y0, y1 - py);
  }

  function strokeLabel(marks, stroke) {
    var gs = [];
    for (var i = 0; i < marks.length; i++) {
      var g = marks[i];
      if (g.kind === 'glyph' && g.host && g.host.kind === 'stroke' && g.host.stroke === stroke && g.ch) gs.push(g);
    }
    if (!gs.length) return '';
    return joinLine({ gs: gs, h: median(gs.map(function (g) { return g.h; })) });
  }

  function mergeLinks(raw) {
    var used = new Uint8Array(raw.length);
    var out = [];
    for (var i = 0; i < raw.length; i++) {
      if (used[i]) continue;
      var a = raw[i];
      for (var j = i + 1; j < raw.length; j++) {
        if (used[j]) continue;
        var b = raw[j];
        var same = (a.from === b.from && a.to === b.to) || (a.from === b.to && a.to === b.from);
        if (!same) continue;
        used[j] = 1;
        if (a.dir === 'one' && b.dir === 'one' && a.from === b.to && a.to === b.from) a.dir = 'both';
        else if (b.dir === 'both') a.dir = 'both';
        else if (a.dir === 'none') { a.dir = b.dir; a.from = b.from; a.to = b.to; }
        if (b.label && !a.label) a.label = b.label;
        if (b.dashed) a.dashed = true;
      }
      out.push(a);
    }
    return out;
  }

  function routeOf(pts, sw) {
    var s = rdp(pts, Math.max(1.5, sw * 0.8));
    if (s.length < 3) return 'straight';
    var ortho = true;
    for (var i = 1; i < s.length; i++) {
      var dx = Math.abs(s[i].x - s[i - 1].x), dy = Math.abs(s[i].y - s[i - 1].y);
      if (dx > sw * 1.4 && dy > sw * 1.4) ortho = false;
    }
    for (var k = 1; k < s.length - 1; k++) {
      var a1 = Math.atan2(s[k].y - s[k - 1].y, s[k].x - s[k - 1].x);
      var a2 = Math.atan2(s[k + 1].y - s[k].y, s[k + 1].x - s[k].x);
      var turn = angDiff(a1, a2) * 180 / Math.PI;
      if (turn > 20 && Math.abs(turn - 90) > 28) ortho = false;
    }
    return ortho ? 'ortho' : 'straight';
  }

  function rdp(pts, eps) {
    if (pts.length < 3) return pts.slice();
    var keep = new Uint8Array(pts.length);
    keep[0] = 1;
    keep[pts.length - 1] = 1;
    var stack = [0, pts.length - 1];
    while (stack.length) {
      var j = stack.pop(), i = stack.pop();
      var maxD = 0, idx = -1;
      for (var k = i + 1; k < j; k++) {
        var d = distSeg(pts[k].x, pts[k].y, pts[i].x, pts[i].y, pts[j].x, pts[j].y);
        if (d > maxD) { maxD = d; idx = k; }
      }
      if (idx >= 0 && maxD > eps) {
        keep[idx] = 1;
        stack.push(i, idx, idx, j);
      }
    }
    var out = [];
    for (var p = 0; p < pts.length; p++) if (keep[p]) out.push(pts[p]);
    return out;
  }

  window.ImgImport = { read: read };
})();
