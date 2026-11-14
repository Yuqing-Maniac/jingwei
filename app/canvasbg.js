var CanvasBg = (function () {
  'use strict';

  function clamp(n, a, b) {
    n = +n;
    if (!isFinite(n)) n = a;
    return Math.max(a, Math.min(b, n));
  }
  function hexColor(c) {
    var s = String(c == null ? '' : c).trim();
    var m = /^#?([0-9a-fA-F]{6})$/.exec(s);
    if (m) return '#' + m[1].toUpperCase();
    var z = /^#?([0-9a-fA-F]{3})$/.exec(s);
    if (z) return '#' + z[1].replace(/./g, function (ch) { return ch + ch; }).toUpperCase();
    return '#808080';
  }
  function escAttr(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function fmt(n) {
    if (!isFinite(+n)) return '0';
    return String(Math.round(+n * 1000) / 1000);
  }
  function numAttr(n) {
    if (!isFinite(+n)) return '0';
    return String(Math.round(+n * 10000) / 10000);
  }
  function rgba(hex, opacity) {
    var h = hexColor(hex).slice(1);
    return 'rgba(' + parseInt(h.slice(0, 2), 16) + ',' + parseInt(h.slice(2, 4), 16) + ',' + parseInt(h.slice(4, 6), 16) + ',' + opacity + ')';
  }

  function normalize(raw) {
    if (raw == null || typeof raw !== 'object') return null;
    var gIn = raw.grad && typeof raw.grad === 'object' ? raw.grad : {};
    var src = Array.isArray(gIn.stops) ? gIn.stops : [];
    var stops = [];
    for (var i = 0; i < src.length && stops.length < 8; i++) {
      var s = src[i] || {};
      stops.push({ at: clamp(s.at, 0, 1), color: hexColor(s.color), opacity: clamp(s.opacity, 0, 1) });
    }
    stops.sort(function (a, b) { return a.at - b.at; });
    if (!stops.length) stops.push({ at: 0, color: '#E7EEF8', opacity: 1 });
    if (stops.length === 1) stops.push({ at: 1, color: stops[0].color, opacity: stops[0].opacity });
    var angle = Math.round(+gIn.angle);
    if (!isFinite(angle)) angle = 0;
    angle = ((angle % 360) + 360) % 360;
    var grid = raw.grid && typeof raw.grid === 'object' ? raw.grid : {};
    var region = raw.region;
    var fixed = region && ['x','y','w','h'].every(function (k) { return isFinite(+region[k]); }) && +region.w > 0 && +region.h > 0;
    return {
      ...(fixed ? {region:{x:+region.x,y:+region.y,w:Math.min(1000000,+region.w),h:Math.min(1000000,+region.h)}} : {}),
      locked: true,
      grad: { kind: gIn.kind === 'radial' ? 'radial' : 'linear', angle: angle, stops: stops },
      grid: {
        show: !!grid.show,
        color: hexColor(grid.color || '#8AA0B8'),
        opacity: clamp(grid.opacity == null ? 0.45 : grid.opacity, 0, 1),
        gap: Math.max(8, isFinite(+grid.gap) ? +grid.gap : 32),
        persp: clamp(grid.persp == null ? 0 : grid.persp, 0, 100),
        offsetX: isFinite(+grid.offsetX) ? +grid.offsetX : 0,
        offsetY: isFinite(+grid.offsetY) ? +grid.offsetY : 0
      }
    };
  }

  function asModel(input) {
    if (!input || typeof input !== 'object') return null;
    if (input.canvasBg) return normalize(input.canvasBg);
    if (input.grad) return normalize(input);
    return null;
  }

  function lockPages(doc) {
    if (!doc || !doc.pages) return;
    var pages = doc.pages;
    for (var k in pages) {
      if (!Object.prototype.hasOwnProperty.call(pages, k)) continue;
      var p = pages[k];
      if (!p || p.canvasBg == null) continue;
      p.canvasBg = normalize(p.canvasBg);
    }
  }

  // Far edge shortens toward the center and row spacing tightens toward the top.
  function gridSegments(box, grid) {
    const gap = Math.max(8, grid.gap);
    const cols = Math.max(1, Math.round(box.w / gap));
    const rows = Math.max(1, Math.round(box.h / gap));
    const t = Math.max(0, Math.min(100, grid.persp)) / 100;
    const pull = 0.75 * t;
    let segs = [];
    const x0 = box.x, y0 = box.y, w = box.w, h = box.h;
    const depthU = j => {
      const u = j / rows;
      if (t === 0) return u;
      return 1 - Math.pow(1 - u, 1 + 2.4 * t);
    };
    for (let j = 0; j <= rows; j++) {
      const u = depthU(j);
      const yy = y0 + h * u;
      const inset = (w / 2) * pull * (1 - u);
      segs.push([x0 + inset, yy, x0 + w - inset, yy]);
    }
    for (let i = 0; i <= cols; i++) {
      const xb = x0 + (w * i) / cols;
      const xt = x0 + w / 2 + (xb - (x0 + w / 2)) * (1 - pull);
      segs.push([xb, y0 + h, xt, y0]);
    }
    var ox = +grid.offsetX || 0, oy = +grid.offsetY || 0;
    if (!ox && !oy) return segs;
    if (!t) {
      // A flat grid's offset is a phase, so translating it leaves no blank rim.
      var gx = w / cols, gy = h / rows;
      segs = [];
      for (let xx = x0 + ((ox % gx) + gx) % gx; xx <= x0 + w; xx += gx) segs.push([xx,y0,xx,y0+h]);
      for (let yy = y0 + ((oy % gy) + gy) % gy; yy <= y0 + h; yy += gy) segs.push([x0,yy,x0+w,yy]);
      return segs;
    }
    // Translate perspective geometry then clip every export's actual segments.
    return segs.map(function (line) {
      var ax=line[0]+ox, ay=line[1]+oy, dx=line[2]-line[0], dy=line[3]-line[1], lo=0, hi=1;
      var pp=[-dx,dx,-dy,dy], qq=[ax-x0,x0+w-ax,ay-y0,y0+h-ay];
      for(var k=0;k<4;k++) { if(!pp[k]) {if(qq[k]<0)return null;} else {var z=qq[k]/pp[k];if(pp[k]<0)lo=Math.max(lo,z);else hi=Math.min(hi,z);if(lo>hi)return null;} }
      return [ax+lo*dx,ay+lo*dy,ax+hi*dx,ay+hi*dy];
    }).filter(Boolean);
  }

  function segments(box, grid, confined) {
    var lines = gridSegments(box, grid);
    if (!confined) return lines;
    // Keep the entire one-unit stroke inside the region in vector exports too.
    return lines.map(function(line){
      var x=line[0],y=line[1],dx=line[2]-x,dy=line[3]-y,lo=0,hi=1;
      var pp=[-dx,dx,-dy,dy],qq=[x-box.x-.5,box.x+box.w-.5-x,y-box.y-.5,box.y+box.h-.5-y];
      for(var i=0;i<4;i++){if(!pp[i]){if(qq[i]<0)return null;}else{var t=qq[i]/pp[i];if(pp[i]<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return null;}}
      return [x+lo*dx,y+lo*dy,x+hi*dx,y+hi*dy];
    }).filter(Boolean);
  }

  function contentBox(page) {
    var b = { x: 0, y: 0, w: 400, h: 300 };
    if (typeof contentBBox === 'function') b = contentBBox(page);
    return b;
  }
  function sheetBox(page, box, pad) {
    var model = asModel(page);
    if (model && model.region) return {...model.region};
    if (box) return { x: +box.x, y: +box.y, w: +box.w, h: +box.h };
    var b = contentBox(page);
    var p = pad == null ? 28 : pad;
    return { x: b.x - p, y: b.y - p, w: b.w + p * 2, h: b.h + p * 2 };
  }

  function linearEnds(angle) {
    var rad = angle * Math.PI / 180;
    var dx = Math.cos(rad), dy = Math.sin(rad);
    return { x1: 0.5 - dx / 2, y1: 0.5 - dy / 2, x2: 0.5 + dx / 2, y2: 0.5 + dy / 2 };
  }

  function markup(page, box, prefix) {
    var model = asModel(page);
    if (!model) return '';
    var b = sheetBox(page, box, 28);
    var pf = String(prefix || (box ? 'cbgx' : 'cbg')).replace(/[^A-Za-z0-9_-]/g, '') || 'cbg';
    var gid = pf + '-grad';
    var stops = model.grad.stops.map(function (s) {
      return '<stop offset="' + numAttr(s.at) + '" stop-color="' + escAttr(s.color) + '" stop-opacity="' + numAttr(s.opacity) + '"/>';
    }).join('');
    var grad = model.grad.kind === 'radial'
      ? '<radialGradient id="' + gid + '" gradientUnits="objectBoundingBox" cx="0.5" cy="0.5" r="0.5">' + stops + '</radialGradient>'
      : (function () {
        var e = linearEnds(model.grad.angle);
        return '<linearGradient id="' + gid + '" gradientUnits="objectBoundingBox" x1="' + numAttr(e.x1) + '" y1="' + numAttr(e.y1) + '" x2="' + numAttr(e.x2) + '" y2="' + numAttr(e.y2) + '">' + stops + '</linearGradient>';
      })();
    var body = '<rect x="' + fmt(b.x) + '" y="' + fmt(b.y) + '" width="' + fmt(b.w) + '" height="' + fmt(b.h) + '" fill="url(#' + gid + ')" stroke="none" pointer-events="none"/>';
    if (model.grid.show) {
      var segs = segments(b, model.grid, !!model.region);
      for (var i = 0; i < segs.length; i++) {
        var ln = segs[i];
        body += '<line x1="' + fmt(ln[0]) + '" y1="' + fmt(ln[1]) + '" x2="' + fmt(ln[2]) + '" y2="' + fmt(ln[3]) + '" stroke="' + escAttr(model.grid.color) + '" stroke-opacity="' + numAttr(model.grid.opacity) + '" stroke-width="1" pointer-events="none"/>';
      }
    }
    var clip = pf + '-clip';
    // Live SVG clips the stroke as well as its centerline to the region.
    var bounds = '<clipPath id="' + clip + '"><rect x="'+fmt(b.x)+'" y="'+fmt(b.y)+'" width="'+fmt(b.w)+'" height="'+fmt(b.h)+'"/></clipPath>';
    var frame = !box && editMode ? '<rect x="'+fmt(b.x)+'" y="'+fmt(b.y)+'" width="'+fmt(b.w)+'" height="'+fmt(b.h)+'" fill="none" stroke="#2F80ED" stroke-dasharray="6 4"/>' : '';
    return '<g class="cbg" pointer-events="none"><defs>' + grad + bounds + '</defs><g clip-path="url(#'+clip+')">' + body + '</g>'+frame+'</g>';
  }

  function cardinal(angle) {
    var a = ((+angle % 360) + 360) % 360;
    var cards = [0, 90, 180, 270];
    var best = null, bestD = 13;
    for (var i = 0; i < cards.length; i++) {
      var d = Math.abs(a - cards[i]);
      if (d > 180) d = 360 - d;
      if (d <= 12 && d < bestD) { bestD = d; best = cards[i]; }
    }
    return best;
  }
  var CARD_DIR = { 0: 'east', 90: 'south', 180: 'west', 270: 'north' };

  function plan(model, format) {
    var m = asModel(model);
    if (!m) return 'native';
    if (format === 'svg' || format === 'png' || format === 'vsdx') return 'native';
    if (format === 'pptx') return 'raster';
    if (format === 'drawio') {
      if (m.grad.kind !== 'linear' || m.grad.stops.length !== 2) return 'raster';
      for (var j = 0; j < m.grad.stops.length; j++) if (m.grad.stops[j].opacity < 1 - 1e-4) return 'raster';
      return cardinal(m.grad.angle) == null ? 'raster' : 'native';
    }
    return 'raster';
  }

  function raster(page, box) {
    var model = asModel(page);
    if (!model) return '';
    var canvas;
    try {
      if (typeof document === 'undefined' || typeof document.createElement !== 'function') return '';
      canvas = document.createElement('canvas');
    } catch (e) { return ''; }
    if (!canvas || typeof canvas.getContext !== 'function') return '';
    var ctx = canvas.getContext('2d');
    if (!ctx || typeof ctx.createLinearGradient !== 'function' || typeof canvas.toDataURL !== 'function') return '';
    var w = Math.max(1, Math.round(box.w)), h = Math.max(1, Math.round(box.h));
    canvas.width = w;
    canvas.height = h;
    var g;
    if (model.grad.kind === 'radial' && typeof ctx.createRadialGradient === 'function') {
      g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.hypot(w, h) / 2);
    } else {
      var e = linearEnds(model.grad.angle);
      g = ctx.createLinearGradient(e.x1 * w, e.y1 * h, e.x2 * w, e.y2 * h);
    }
    for (var i = 0; i < model.grad.stops.length; i++) {
      var st = model.grad.stops[i];
      g.addColorStop(st.at, rgba(st.color, st.opacity));
    }
    ctx.fillStyle = g;
    if (typeof ctx.fillRect === 'function') ctx.fillRect(0, 0, w, h);
    if (model.grid.show && typeof ctx.beginPath === 'function') {
      ctx.strokeStyle = rgba(model.grid.color, model.grid.opacity);
      ctx.lineWidth = 1;
      var segs = segments(box, model.grid, !!model.region);
      for (var k = 0; k < segs.length; k++) {
        ctx.beginPath();
        ctx.moveTo(segs[k][0] - box.x, segs[k][1] - box.y);
        ctx.lineTo(segs[k][2] - box.x, segs[k][3] - box.y);
        ctx.stroke();
      }
    }
    try { return canvas.toDataURL('image/png') || ''; } catch (err) { return ''; }
  }

  function paintPptx(slide, pptx, page, ctx) {
    var model = asModel(page);
    if (!model || !slide || !ctx || !ctx.box) return Promise.resolve();
    var box = sheetBox(page, ctx.box);
    /* pptxgenjs 3.12 drops fill type grad and turns a zero-width line into a 1pt outline. */
    var url = raster(page, box);
    if (url) slide.addImage({ data: url.replace(/^data:/, ''), x: ctx.X(box.x), y: ctx.Y(box.y), w: ctx.S(box.w), h: ctx.S(box.h) });
    return Promise.resolve();
  }

  function vsdxShapes(page, ctx) {
    var model = asModel(page);
    if (!model || !ctx || !ctx.box || typeof ctx.cell !== 'function') return [];
    var box = sheetBox(page, ctx.box), f = ctx.f, X = ctx.X, Y = ctx.Y, cell = ctx.cell, num = ctx.num, id = ctx.id;
    var W = box.w * f, H = box.h * f;
    var pinX = X(box.x) + W / 2, pinY = Y(box.y) - H / 2;
    /* Visio Y is up: 0 points right, and downward on the page is 3π/2, so the stored angle is negated. */
    var ang = model.grad.kind === 'radial' ? 0 : -model.grad.angle * Math.PI / 180;
    var s = "<Shape ID='" + id() + "' Type='Shape' LineStyle='0' FillStyle='0' TextStyle='0'>";
    s += cell('PinX', num(pinX)) + cell('PinY', num(pinY)) + cell('Width', num(W)) + cell('Height', num(H));
    s += cell('LocPinX', num(W / 2)) + cell('LocPinY', num(H / 2)) + cell('Angle', 0);
    s += cell('FillPattern', 1) + cell('FillGradientEnabled', 1) + cell('FillGradientAngle', num(ang));
    if (model.grad.kind === 'radial') s += cell('FillGradientDir', 1);
    s += cell('LinePattern', 0);
    s += "<Section N='FillGradient'>";
    for (var i = 0; i < model.grad.stops.length; i++) {
      var st = model.grad.stops[i];
      s += "<Row IX='" + i + "'>" + cell('GradientStopColor', st.color) + cell('GradientStopColorTrans', num(1 - st.opacity)) + cell('GradientStopPosition', num(st.at)) + '</Row>';
    }
    s += '</Section>';
    s += "<Section N='Geometry' IX='0'>" + cell('NoFill', 0) + cell('NoLine', 1);
    s += "<Row T='MoveTo' IX='1'>" + cell('X', 0) + cell('Y', 0) + '</Row>';
    s += "<Row T='LineTo' IX='2'>" + cell('X', num(W)) + cell('Y', 0) + '</Row>';
    s += "<Row T='LineTo' IX='3'>" + cell('X', num(W)) + cell('Y', num(H)) + '</Row>';
    s += "<Row T='LineTo' IX='4'>" + cell('X', 0) + cell('Y', num(H)) + '</Row>';
    s += "<Row T='LineTo' IX='5'>" + cell('X', 0) + cell('Y', 0) + '</Row></Section></Shape>';
    var out = [s];
    if (!model.grid.show) return out;
    var segs = segments(box, model.grid, !!model.region);
    if (!segs.length) return out;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    var vis = [];
    for (var k = 0; k < segs.length; k++) {
      var vx1 = X(segs[k][0]), vy1 = Y(segs[k][1]), vx2 = X(segs[k][2]), vy2 = Y(segs[k][3]);
      vis.push([vx1, vy1, vx2, vy2]);
      minX = Math.min(minX, vx1, vx2); minY = Math.min(minY, vy1, vy2);
      maxX = Math.max(maxX, vx1, vx2); maxY = Math.max(maxY, vy1, vy2);
    }
    var GW = Math.max(maxX - minX, 0.0001), GH = Math.max(maxY - minY, 0.0001);
    var g = "<Shape ID='" + id() + "' Type='Shape' LineStyle='0' FillStyle='0' TextStyle='0'>";
    g += cell('PinX', num(minX + GW / 2)) + cell('PinY', num(minY + GH / 2));
    g += cell('Width', num(GW)) + cell('Height', num(GH));
    g += cell('LocPinX', num(GW / 2)) + cell('LocPinY', num(GH / 2));
    g += cell('LineColor', model.grid.color) + cell('LineWeight', num(0.75 / 72), 'PT') + cell('LinePattern', 1);
    g += cell('LineColorTrans', num(1 - model.grid.opacity)) + cell('FillPattern', 0);
    g += cell('EndArrow', 0) + cell('BeginArrow', 0);
    for (var n = 0; n < vis.length; n++) {
      g += "<Section N='Geometry' IX='" + n + "'>" + cell('NoFill', 1) + cell('NoLine', 0);
      g += "<Row T='MoveTo' IX='1'>" + cell('X', num(vis[n][0] - minX)) + cell('Y', num(vis[n][1] - minY)) + '</Row>';
      g += "<Row T='LineTo' IX='2'>" + cell('X', num(vis[n][2] - minX)) + cell('Y', num(vis[n][3] - minY)) + '</Row></Section>';
    }
    g += '</Shape>';
    out.push(g);
    return out;
  }

  function lockStyle() {
    return 'locked=1;pointerEvents=0;movable=0;resizable=0;deletable=0;connectable=0';
  }
  function dioCell(id, style, inner, edge) {
    return '<UserObject label="" id="' + id + '" ht_part="canvasbg"><mxCell style="' + escAttr(style) + '" ' + (edge ? 'edge="1"' : 'vertex="1"') + ' parent="1">' + inner + '</mxCell></UserObject>';
  }
  function dioPng(url) {
    var s = String(url || '');
    var cut = s.indexOf(',');
    if (s.indexOf('data:image/png;base64,') === 0 && cut >= 0) return 'data:image/png,' + s.slice(cut + 1);
    return s;
  }
  function drawio(page) {
    var model = asModel(page);
    if (!model) return null;
    var b = sheetBox(page, null, 40);
    var cells = '';
    var background = null;
    var same = model.grad.stops.every(function (s) { return s.color === model.grad.stops[0].color && s.opacity >= 1 - 1e-4; });
    if (same && !model.region) background = model.grad.stops[0].color;
    if (plan(model, 'drawio') === 'raster') {
      var url = raster(page, b);
      if (!url) return { background: background, cells: '' };
      var style = 'shape=image;imageAspect=0;aspect=fixed;' + lockStyle() + ';image=' + dioPng(url);
      cells = dioCell('cbg-img', style, '<mxGeometry x="' + fmt(b.x) + '" y="' + fmt(b.y) + '" width="' + fmt(b.w) + '" height="' + fmt(b.h) + '" as="geometry"/>');
      return { background: background, cells: cells };
    }
    var dir = CARD_DIR[cardinal(model.grad.angle)];
    var c1 = model.grad.stops[0].color, c2 = model.grad.stops[1].color;
    var gst = 'rounded=0;fillColor=' + c1 + ';gradientColor=' + c2 + ';gradientDirection=' + dir + ';strokeColor=none;' + lockStyle();
    cells = dioCell('cbg-fill', gst, '<mxGeometry x="' + fmt(b.x) + '" y="' + fmt(b.y) + '" width="' + fmt(b.w) + '" height="' + fmt(b.h) + '" as="geometry"/>');
    if (model.grid.show) {
      var segs = segments(b, model.grid, !!model.region);
      var op = Math.round(model.grid.opacity * 100);
      for (var i = 0; i < segs.length; i++) {
        var x1 = segs[i][0], y1 = segs[i][1], x2 = segs[i][2], y2 = segs[i][3];
        /* mxLine paints the cell bounds and ignores the endpoints, so a perspective segment is a floating edge. */
        var st = 'endArrow=none;startArrow=none;html=1;rounded=0;strokeColor=' + model.grid.color + ';strokeOpacity=' + op + ';' + lockStyle();
        cells += dioCell('cbg-l' + i, st, '<mxGeometry relative="1" as="geometry"><mxPoint x="' + fmt(x1) + '" y="' + fmt(y1) + '" as="sourcePoint"/><mxPoint x="' + fmt(x2) + '" y="' + fmt(y2) + '" as="targetPoint"/></mxGeometry>', true);
      }
    }
    return { background: background, cells: cells };
  }

  var editMode = '', bgDrag = null;
  function stopEditing() {editMode='';bgDrag=null;var b=document.getElementById('cbg-done');if(b)b.hidden=true;if(typeof render==='function')render();}
  function bindDrag() {
    var canvas=document.getElementById('svg');if(!canvas)return;
    canvas.addEventListener('pointerdown',function(e){
      if(!editMode||e.button!==0||(typeof spaceDown!=='undefined'&&spaceDown))return;
      var page=P(),m=asModel(page),p=clientToWorld(e.clientX,e.clientY),b=m&&m.region;
      if(!b||p.x<b.x||p.x>b.x+b.w||p.y<b.y||p.y>b.y+b.h)return;
      e.preventDefault();e.stopImmediatePropagation();canvas.setPointerCapture(e.pointerId);
      bgDrag={page:page,id:e.pointerId,start:p,model:m,mode:editMode,moved:false};
    },true);
    window.addEventListener('pointermove',function(e){
      if(!bgDrag||bgDrag.id!==e.pointerId)return;e.preventDefault();e.stopImmediatePropagation();
      if(P()!==bgDrag.page){stopEditing();return;}
      var p=clientToWorld(e.clientX,e.clientY),dx=p.x-bgDrag.start.x,dy=p.y-bgDrag.start.y;
      if(!bgDrag.moved){if(!dx&&!dy)return;checkpoint();bgDrag.moved=true;}
      var m=normalize(bgDrag.model);
      if(bgDrag.mode==='region'){m.region.x+=dx;m.region.y+=dy;}else{m.grid.offsetX+=dx;m.grid.offsetY+=dy;}
      P().canvasBg=m;render();
    },true);
    window.addEventListener('pointerup',function(e){if(!bgDrag||bgDrag.id!==e.pointerId)return;e.preventDefault();e.stopImmediatePropagation();bgDrag=null;},true);
    window.addEventListener('pointercancel',function(){bgDrag=null;},true);
    document.addEventListener('keydown',function(e){if(editMode&&e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();stopEditing();}},true);
  }
  var draft = null;
  function defaults() {
    return normalize({
      grad: { kind: 'linear', angle: 90, stops: [{ at: 0, color: '#E7EEF8', opacity: 1 }, { at: 1, color: '#C5D7F2', opacity: 1 }] },
      grid: { show: false, color: '#8AA0B8', opacity: 0.45, gap: 32, persp: 0 }
    });
  }
  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    if (attrs) for (var k in attrs) if (Object.prototype.hasOwnProperty.call(attrs, k)) node[k] = attrs[k];
    if (text != null) node.textContent = text;
    return node;
  }
  function row(label, control) {
    var r = el('div', { className: 'row' });
    r.appendChild(el('label', null, label));
    r.appendChild(control);
    return r;
  }
  function readDialog() {
    var stops = [];
    var rows = document.querySelectorAll('#cbg-stops [data-i]');
    for (var i = 0; i < rows.length; i++) {
      stops.push({
        at: (+rows[i].querySelector('[data-k="at"]').value) / 100,
        color: rows[i].querySelector('[data-k="color"]').value,
        opacity: (+rows[i].querySelector('[data-k="op"]').value) / 100
      });
    }
    draft = normalize({
      ...(document.getElementById('cbg-scope').value === 'region' ? {region:{x:+document.getElementById('cbg-xpos').value,y:+document.getElementById('cbg-ypos').value,w:Math.max(1,+document.getElementById('cbg-width').value),h:Math.max(1,+document.getElementById('cbg-height').value)}} : {}),
      grad: { kind: document.getElementById('cbg-kind').value, angle: document.getElementById('cbg-angle').value, stops: stops },
      grid: {
        show: document.getElementById('cbg-grid').checked,
        color: document.getElementById('cbg-gcolor').value,
        opacity: (+document.getElementById('cbg-gop').value) / 100,
        gap: +document.getElementById('cbg-gap').value,
        persp: +document.getElementById('cbg-persp').value,
        offsetX: +document.getElementById('cbg-offset-x').value,
        offsetY: +document.getElementById('cbg-offset-y').value
      }
    });
  }
  function fillStops() {
    var host = document.getElementById('cbg-stops');
    while (host.firstChild) host.removeChild(host.firstChild);
    var stops = draft.grad.stops;
    for (var i = 0; i < stops.length; i++) {
      (function (index) {
        var wrap = el('div', { className: 'row' });
        wrap.setAttribute('data-i', String(index));
        var color = el('input');
        color.type = 'color';
        color.setAttribute('data-k', 'color');
        color.value = stops[index].color.toLowerCase();
        var at = el('input');
        at.type = 'number';
        at.min = '0';
        at.max = '100';
        at.setAttribute('data-k', 'at');
        at.value = String(Math.round(stops[index].at * 100));
        var op = el('input');
        op.type = 'number';
        op.min = '0';
        op.max = '100';
        op.setAttribute('data-k', 'op');
        op.value = String(Math.round(stops[index].opacity * 100));
        var del = el('button', { type: 'button' }, '删除');
        del.disabled = stops.length <= 2;
        del.onclick = function () {
          readDialog();
          if (draft.grad.stops.length <= 2) return;
          draft.grad.stops.splice(index, 1);
          fillStops();
        };
        wrap.appendChild(el('label', null, '色标'));
        wrap.appendChild(color);
        wrap.appendChild(at);
        wrap.appendChild(op);
        wrap.appendChild(del);
        host.appendChild(wrap);
      })(i);
    }
    var add = document.getElementById('cbg-add');
    if (add) add.disabled = stops.length >= 8;
  }
  function fillDialog() {
    var b = draft.region || sheetBox(P(), null, 28);
    document.getElementById('cbg-scope').value = draft.region ? 'region' : 'auto';
    ['xpos','ypos','width','height'].forEach(function(k,i){document.getElementById('cbg-'+k).value=b[['x','y','w','h'][i]];});
    document.getElementById('cbg-offset-x').value = draft.grid.offsetX;
    document.getElementById('cbg-offset-y').value = draft.grid.offsetY;
    document.getElementById('cbg-kind').value = draft.grad.kind;
    document.getElementById('cbg-angle').value = String(draft.grad.angle);
    document.getElementById('cbg-grid').checked = !!draft.grid.show;
    document.getElementById('cbg-gcolor').value = draft.grid.color.toLowerCase();
    document.getElementById('cbg-gop').value = String(Math.round(draft.grid.opacity * 100));
    document.getElementById('cbg-gap').value = String(draft.grid.gap);
    document.getElementById('cbg-persp').value = String(Math.round(draft.grid.persp));
    fillStops();
  }
  function openDialog() {
    stopEditing();
    var page = typeof P === 'function' ? P() : null;
    draft = page && page.canvasBg ? normalize(page.canvasBg) : defaults();
    if (!page.canvasBg) draft.region = sheetBox(page, null, 28);
    fillDialog();
    var dlg = document.getElementById('cbg-dlg');
    if (dlg) dlg.style.display = 'flex';
  }
  function closeDialog() {
    var dlg = document.getElementById('cbg-dlg');
    if (dlg) dlg.style.display = 'none';
  }
  function applyDialog() {
    readDialog();
    if (typeof checkpoint === 'function') checkpoint();
    var page = P();
    page.canvasBg = normalize(draft);
    draft = page.canvasBg;
    if (typeof render === 'function') render();
    if (typeof toast === 'function') toast('背景已锁定，点选图元时不会碰到它');
  }
  function clearDialog() {
    if (typeof checkpoint === 'function') checkpoint();
    var page = P();
    delete page.canvasBg;
    draft = defaults();
    fillDialog();
    if (typeof render === 'function') render();
  }
  function mount() {
    if (typeof document === 'undefined' || typeof document.getElementById !== 'function' || typeof document.createElement !== 'function') return;
    if (document.getElementById('b-bg')) return;
    var theme = document.getElementById('b-theme');
    if (!theme || !theme.parentNode) return;
    if (!document.getElementById('cbg-style') && document.head) {
      var css = el('style');
      css.id = 'cbg-style';
      css.textContent = '#cbg-dlg .row>label{width:84px}#cbg-dlg .box{width:min(560px,100%)}#cbg-stops .row>label{width:42px}';
      document.head.appendChild(css);
    }
    var btn = el('button', { id: 'b-bg', type: 'button', title: '设置画布背景。应用后锁定，点选图元时不会碰到它' }, '背景');
    btn.onclick = openDialog;
    theme.parentNode.insertBefore(btn, theme);
    var done=el('button',{type:'button',id:'cbg-done',hidden:true},'结束背景拖动');done.onclick=stopEditing;theme.parentNode.insertBefore(done,theme);
    bindDrag();
    var dlg = el('div', { id: 'cbg-dlg', className: 'mdl' });
    dlg.setAttribute('role', 'dialog');
    dlg.setAttribute('aria-label', '画布背景');
    var box = el('div', { className: 'box' });
    var mh = el('div', { className: 'mh' });
    mh.appendChild(el('strong', null, '画布背景'));
    var hint = el('span', { className: 'hint' }, '应用后锁定，点选图元时不会碰到它');
    hint.style.flex = '1';
    mh.appendChild(hint);
    var close = el('button', { id: 'cbg-x', type: 'button' }, '关闭');
    close.onclick = closeDialog;
    mh.appendChild(close);
    var mb = el('div', { className: 'mb' });
    var scope = el('select',{id:'cbg-scope'});
    scope.appendChild(el('option',{value:'region'},'底层背景区域（固定范围）'));
    scope.appendChild(el('option',{value:'auto'},'自动铺底（兼容旧文档）'));
    mb.appendChild(row('背景范围',scope));
    [['xpos','区域 X'],['ypos','区域 Y'],['width','区域宽度'],['height','区域高度'],['offset-x','网格偏移 X'],['offset-y','网格偏移 Y']].forEach(function(v){var input=el('input',{id:'cbg-'+v[0],type:'number'});if(v[0]==='width'||v[0]==='height')input.min='1';mb.appendChild(row(v[1],input));});
    mb.appendChild(el('div',{className:'hint'},'网格仅属于此底层背景区域；移动图元不会改变固定区域。区域移动时网格一起移动，也可单独拖动网格。'));
    var kind = el('select', { id: 'cbg-kind' });
    kind.appendChild(el('option', { value: 'linear' }, '线性'));
    kind.appendChild(el('option', { value: 'radial' }, '径向'));
    var angle = el('input', { id: 'cbg-angle', type: 'number' });
    angle.min = '0';
    angle.max = '359';
    mb.appendChild(row('渐变类型', kind));
    mb.appendChild(row('角度', angle));
    mb.appendChild(el('div', { id: 'cbg-stops' }));
    var add = el('button', { id: 'cbg-add', type: 'button' }, '添加色标');
    add.onclick = function () {
      readDialog();
      if (draft.grad.stops.length >= 8) return;
      var stops = draft.grad.stops;
      var at = stops.length >= 2 ? (stops[stops.length - 2].at + stops[stops.length - 1].at) / 2 : 0.5;
      stops.push({ at: at, color: '#88AADD', opacity: 1 });
      stops.sort(function (a, b) { return a.at - b.at; });
      fillStops();
    };
    mb.appendChild(add);
    var grid = el('input', { id: 'cbg-grid', type: 'checkbox' });
    var gcolor = el('input', { id: 'cbg-gcolor', type: 'color' });
    var gop = el('input', { id: 'cbg-gop', type: 'number' });
    gop.min = '0'; gop.max = '100';
    var gap = el('input', { id: 'cbg-gap', type: 'number' });
    gap.min = '8';
    var persp = el('input', { id: 'cbg-persp', type: 'number' });
    persp.min = '0'; persp.max = '100';
    mb.appendChild(row('网格', grid));
    mb.appendChild(row('网格颜色', gcolor));
    mb.appendChild(row('不透明度', gop));
    mb.appendChild(row('间距', gap));
    mb.appendChild(row('透视', persp));
    var acts = el('div', { className: 'row' });
    var apply = el('button', { type: 'button', className: 'primary' }, '应用并锁定');
    apply.onclick = applyDialog;
    var clear = el('button', { type: 'button' }, '清除背景');
    clear.onclick = clearDialog;
    acts.appendChild(apply);
    acts.appendChild(clear);
    [['region','拖动底层背景区域'],['grid','拖动网格']].forEach(function(item){var b=el('button',{type:'button',id:'cbg-drag-'+item[0]},item[1]);b.onclick=function(){applyDialog();if(!P().canvasBg.region){P().canvasBg.region=sheetBox(P(),null,28);}if(item[0]==='grid')P().canvasBg.grid.show=true;editMode=item[0];closeDialog();document.getElementById('cbg-done').hidden=false;render();toast(item[1]+'：在背景区域内拖动，完成后点“结束背景拖动”或 Esc');};acts.appendChild(b);});
    mb.appendChild(acts);
    box.appendChild(mh);
    box.appendChild(mb);
    dlg.appendChild(box);
    document.body.appendChild(dlg);
  }

  if (typeof document !== 'undefined') mount();

  return {
    normalize: normalize,
    regionBox: function(page){var m=asModel(page);return m&&m.region ? {...m.region} : null;},
    lockPages: lockPages,
    markup: markup,
    plan: plan,
    paintPptx: paintPptx,
    vsdxShapes: vsdxShapes,
    drawio: drawio
  };
})();
window.CanvasBg = CanvasBg;
