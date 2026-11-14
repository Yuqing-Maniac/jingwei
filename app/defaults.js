/* 新建默认。偏好存在 localStorage 的 hongtu.defaults，和吸附、排版同一类。
 * 只在用户新建图形或连线时抄到该元素上。已有元素保持原值，除非按「套用」。
 * 调色板或模板已经写明的字段优先，标题和容器不吃字号与填色。 */
var JwDefaults = (function () {
  var KEY = 'hongtu.defaults';

  function blank() {
    return {
      noBox: false, affiliation: 'neutral', size: 0, font: '', bold: false,
      fill: '', stroke: '', noLine: false,
      linkDir: 'one', linkRoute: 'ortho', linkColor: '', linkSw: 0
    };
  }
  function hex(v) { return typeof v === 'string' && /^#[0-9A-Fa-f]{6}$/.test(v) ? v : ''; }
  function fontOk(id) {
    if (!id) return '';
    for (var i = 0; i < FONT_CHOICES.length; i++) if (FONT_CHOICES[i].id === id) return id;
    return '';
  }
  function read() {
    var d = blank();
    var o = null;
    try { o = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { o = null; }
    if (!o || typeof o !== 'object' || Array.isArray(o)) return d;
    if (o.noBox === true) d.noBox = true;
    if (o.affiliation === 'blue' || o.affiliation === 'red') d.affiliation = o.affiliation;
    if (typeof o.size === 'number' && isFinite(o.size) && o.size >= 5 && o.size <= 72) d.size = Math.round(o.size * 10) / 10;
    d.font = fontOk(o.font);
    if (o.bold === true) d.bold = true;
    d.fill = hex(o.fill);
    d.stroke = hex(o.stroke);
    if (o.noLine === true) d.noLine = true;
    if (o.linkDir === 'both' || o.linkDir === 'none') d.linkDir = o.linkDir;
    if (o.linkRoute === 'straight') d.linkRoute = 'straight';
    d.linkColor = hex(o.linkColor);
    if (typeof o.linkSw === 'number' && isFinite(o.linkSw) && o.linkSw >= 0.5 && o.linkSw <= 12) d.linkSw = Math.round(o.linkSw * 10) / 10;
    return d;
  }
  function write(d) {
    try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) { }
  }
  function own(spec, key) { return !!(spec && Object.prototype.hasOwnProperty.call(spec, key)); }
  function libIcon(n) { return !!(n && n.icon && String(n.icon).indexOf('lib:') === 0); }
  function textBody(n) {
    return n && !isCont(n) && n.type !== 'legend' && n.type !== 'tblock' && n.role !== 'title' && n.role !== 'subtitle';
  }
  function paintBody(n) {
    return n && !isCont(n) && n.type !== 'text' && n.type !== 'tblock' && n.type !== 'legend' && !isLineArrow(n);
  }
  function inkBody(n) { return paintBody(n) || isLineArrow(n); }

  function stampNode(n, spec) {
    var d = read();
    spec = spec || {};
    if (!own(spec, 'noBox') && d.noBox && n.icon) n.noBox = true;
    if (!own(spec, 'affiliation') && libIcon(n) && d.affiliation !== 'neutral') n.affiliation = d.affiliation;
    if (textBody(n)) {
      if (!own(spec, 'size') && d.size) n.size = d.size;
      if (!own(spec, 'font') && d.font) n.font = d.font;
      if (!own(spec, 'bold') && d.bold) n.bold = true;
    }
    if (!own(spec, 'fill') && d.fill && paintBody(n)) n.fill = d.fill;
    if (inkBody(n)) {
      if (!own(spec, 'stroke') && d.stroke) n.stroke = d.stroke;
      if (!own(spec, 'noLine') && d.noLine) n.noLine = true;
    }
  }
  function stampLink(l) {
    var d = read();
    if (!l) return;
    l.dir = d.linkDir;
    l.route = d.linkRoute;
    if (d.linkColor) l.color = d.linkColor;
    if (d.linkSw) l.sw = d.linkSw;
  }
  function applyNode(n, d) {
    if (n.icon) n.noBox = !!d.noBox;
    if (libIcon(n)) {
      if (d.affiliation === 'neutral') delete n.affiliation;
      else n.affiliation = d.affiliation;
    }
    if (textBody(n)) {
      if (d.size) n.size = d.size;
      if (d.font) n.font = d.font; else delete n.font;
      n.bold = !!d.bold;
    }
    if (paintBody(n)) { if (d.fill) n.fill = d.fill; else delete n.fill; }
    if (inkBody(n)) {
      if (d.stroke) n.stroke = d.stroke; else delete n.stroke;
      if (d.noLine) n.noLine = true; else delete n.noLine;
    }
  }
  function applyLink(l, d) {
    l.dir = d.linkDir;
    l.route = d.linkRoute;
    if (d.linkColor) l.color = d.linkColor; else delete l.color;
    if (d.linkSw) l.sw = d.linkSw; else delete l.sw;
  }
  function commit(nodes, links) {
    if (!nodes.length && !links.length) { toast('先选中元素或连线'); return; }
    checkpoint();
    var before = undoS[undoS.length - 1];
    var d = read();
    for (var i = 0; i < nodes.length; i++) applyNode(nodes[i], d);
    for (var j = 0; j < links.length; j++) applyLink(links[j], d);
    if (before === snapshot()) { undoS.pop(); toast('已经是这些默认值'); return; }
    render();
    toast('已套用新建默认：' + nodes.length + ' 个元素，' + links.length + ' 条连线');
  }

  function seg(id, opts, val) {
    var h = '<div class="seg" id="' + id + '">';
    for (var i = 0; i < opts.length; i++) {
      var on = opts[i][0] === val ? ' on' : '';
      h += '<button type="button" data-v="' + opts[i][0] + '" class="' + on.trim() + '">' + opts[i][1] + '</button>';
    }
    return h + '</div>';
  }
  function sizeOptions(d) {
    var h = '<option value="0"' + (d.size ? '' : ' selected') + '>内置</option>';
    var hit = false;
    for (var i = 0; i < CN_SIZES.length; i++) {
      var on = d.size && Math.abs(CN_SIZES[i].pt - d.size) < 0.05;
      if (on) hit = true;
      h += '<option value="' + CN_SIZES[i].pt + '"' + (on ? ' selected' : '') + '>' + esc(CN_SIZES[i].name) + '</option>';
    }
    if (d.size && !hit) h += '<option value="' + d.size + '" selected>' + d.size + '</option>';
    return h;
  }
  function fontOptions(d) {
    var h = '';
    for (var i = 0; i < FONT_CHOICES.length; i++) {
      var f = FONT_CHOICES[i];
      h += '<option value="' + esc(f.id) + '"' + (f.id === d.font ? ' selected' : '') + ' style="font-family:' + f.css + '">' + esc(f.name) + '</option>';
    }
    return h;
  }
  function colorRow(label, id, val, clear) {
    return '<div class="row"><label>' + label + '</label><input type="color" id="' + id + '" value="' + (val || '#ffffff') + '"><button type="button" id="' + clear + '" style="border-color:var(--line)">主题</button></div>';
  }
  function panelHTML() {
    var d = read();
    var h = '<hr><h3>新建默认</h3>';
    h += '<div class="hint" style="margin:-4px 0 6px">只用于之后新建的图形和连线。已有内容不变，除非按下面的套用。</div>';
    h += '<div class="row" title="装备图标新建时带不带外框。调色板里写明了外框的仍以调色板为准。"><label>外框</label>' + seg('gd-box', [['0', '带框'], ['1', '不带框']], d.noBox ? '1' : '0') + '</div>';
    h += '<div class="row" title="只作用于图标库里的装备，不影响军标配色"><label>阵营</label>' + seg('gd-side', [['neutral', '原色'], ['blue', '蓝方'], ['red', '红方']], d.affiliation) + '</div>';
    h += '<div class="row" title="文字、说明框若自带字号，仍用自带字号。标题不改。"><label>字号</label><select id="gd-size">' + sizeOptions(d) + '</select></div>';
    h += '<div class="row"><label>字体</label><select id="gd-font">' + fontOptions(d) + '</select></div>';
    h += '<div class="row"><label></label><label style="width:auto;display:flex;gap:6px;align-items:center;color:var(--fg)"><input type="checkbox" id="gd-bold"' + (d.bold ? ' checked' : '') + '> 加粗</label></div>';
    h += colorRow('填充', 'gd-fill', d.fill, 'gd-fill-x');
    h += colorRow('描边', 'gd-stroke', d.stroke, 'gd-stroke-x');
    h += '<div class="row"><label></label><label style="width:auto;display:flex;gap:6px;align-items:center;color:var(--fg)"><input type="checkbox" id="gd-noline"' + (d.noLine ? ' checked' : '') + '> 无描边</label></div>';
    h += '<div class="row"><label>箭头</label>' + seg('gd-dir', [['one', '单向'], ['both', '双向'], ['none', '无']], d.linkDir) + '</div>';
    h += '<div class="row"><label>走线</label>' + seg('gd-route', [['ortho', '直角'], ['straight', '直线']], d.linkRoute) + '</div>';
    h += colorRow('线色', 'gd-lcolor', d.linkColor, 'gd-lcolor-x');
    h += '<div class="row"><label>线宽</label><input type="number" id="gd-lsw" min="0.5" max="12" step="0.5" placeholder="内置" value="' + (d.linkSw || '') + '"></div>';
    h += '<div class="row"><button type="button" id="gd-page" style="border-color:var(--line);justify-content:center">套用到本页</button></div>';
    h += '<div class="hint">选中元素或连线后，属性栏里可以「套用新建默认」。</div>';
    return h;
  }
  function applySelectedHTML() {
    return '<div class="row"><button type="button" id="gd-sel" style="border-color:var(--line);justify-content:center">套用新建默认</button></div>';
  }
  function patch(mut) {
    var d = read();
    mut(d);
    write(d);
    render();
  }
  function bind(root) {
    if (!root) return;
    var q = function (s) { return root.querySelector(s); };
    if (!q('#gd-box') && !q('#gd-sel') && !q('#gd-page')) return;
    function onSeg(id, apply) {
      var el = q('#' + id);
      if (!el) return;
      el.addEventListener('click', function (e) {
        var b = e.target.closest('[data-v]');
        if (!b) return;
        patch(function (d) { apply(d, b.dataset.v); });
      });
    }
    onSeg('gd-box', function (d, v) { d.noBox = v === '1'; });
    onSeg('gd-side', function (d, v) { d.affiliation = v === 'blue' || v === 'red' ? v : 'neutral'; });
    onSeg('gd-dir', function (d, v) { d.linkDir = v === 'both' || v === 'none' ? v : 'one'; });
    onSeg('gd-route', function (d, v) { d.linkRoute = v === 'straight' ? 'straight' : 'ortho'; });
    var size = q('#gd-size');
    if (size) size.addEventListener('change', function () {
      var n = +size.value;
      patch(function (d) { d.size = size.value === '0' || !isFinite(n) ? 0 : Math.max(5, Math.min(72, Math.round(n * 10) / 10)); });
    });
    var font = q('#gd-font');
    if (font) font.addEventListener('change', function () { patch(function (d) { d.font = fontOk(font.value); }); });
    var bold = q('#gd-bold');
    if (bold) bold.addEventListener('change', function () { patch(function (d) { d.bold = !!bold.checked; }); });
    var noline = q('#gd-noline');
    if (noline) noline.addEventListener('change', function () { patch(function (d) { d.noLine = !!noline.checked; }); });
    function onColor(id, key) {
      var el = q('#' + id);
      if (el) el.addEventListener('change', function () { var v = hex(el.value); patch(function (d) { d[key] = v; }); });
    }
    function onClear(id, key) {
      var el = q('#' + id);
      if (el) el.addEventListener('click', function () { patch(function (d) { d[key] = ''; }); });
    }
    onColor('gd-fill', 'fill');
    onColor('gd-stroke', 'stroke');
    onColor('gd-lcolor', 'linkColor');
    onClear('gd-fill-x', 'fill');
    onClear('gd-stroke-x', 'stroke');
    onClear('gd-lcolor-x', 'linkColor');
    var sw = q('#gd-lsw');
    if (sw) sw.addEventListener('change', function () {
      var raw = String(sw.value || '').trim();
      var n = +raw;
      patch(function (d) {
        d.linkSw = !raw || !isFinite(n) ? 0 : Math.max(0.5, Math.min(12, Math.round(n * 10) / 10));
      });
    });
    var page = q('#gd-page');
    if (page) page.addEventListener('click', function () {
      commit(P().nodes.slice(), P().links.slice());
    });
    var sel = q('#gd-sel');
    if (sel) sel.addEventListener('click', function () {
      commit(selectedNodes(), selectedLinks());
    });
  }

  return { read: read, stampNode: stampNode, stampLink: stampLink, panelHTML: panelHTML, applySelectedHTML: applySelectedHTML, bind: bind };
})();
