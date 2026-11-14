/* Coverage illustrations use existing sector/ellipse geometry and export writers.
   Values are canvas units, never equipment capabilities. Load after app.js/defaults.js. */
window.Coverage = (function () {
  'use strict';
  function isCoverage(n) { return !!n && /^(eo|radar|defense)$/.test(n.coverageKind || '') && (n.type === 'sector' || n.type === 'ellipse'); }
  function finite(v, fallback, lo, hi) { v = +v; return isFinite(v) ? Math.max(lo, Math.min(hi, v)) : fallback; }
  function normAngle(a) { return ((a % 360) + 360) % 360; }
  /* Store only true geometric rotation; derive the sector centerline from it. */
  function heading(n) { return normAngle(rotOf(n) + (n.type === 'sector' ? sectorSweep(n) / 2 : 0)); }
  function setHeading(n, value) { n.rot = normAngle(finite(value, heading(n), 0, 359) - (n.type === 'sector' ? sectorSweep(n) / 2 : 0)); }
  function radius(n) { return Math.round(Math.min(n.w, n.h) * 5) / 10; }
  function resize(n, r) {
    r = finite(r, radius(n), 8, 5000);
    const cx = n.x + n.w / 2, cy = n.y + n.h / 2;
    n.w = n.h = r * 2; n.x = cx - r; n.y = cy - r;
  }
  function displayRadius(n) { return n.coverageScaled ? radius(n) / measureSpec().px : radius(n); }
  function setDisplayRadius(n, value) { resize(n, +value * (n.coverageScaled ? measureSpec().px : 1)); }
  function radiusUnit(n) { return n.coverageScaled ? measureSpec().unit : '画布单位'; }
  function style(n) {
    return { sw: finite(n.sw == null ? 1.5 : n.sw, 1.5, 0.5, 12),
      dash: ['6 4', '2 4', '10 4 2 4'].indexOf(n.coverageDash) >= 0 ? n.coverageDash : '',
      fillAlpha: finite(n.coverageAlpha == null ? 15 : n.coverageAlpha, 15, 0, 100) / 100 };
  }
  function caption(n) {
    if (!isCoverage(n) || n.coverageLabel === false) return n.text || '';
    return (n.text ? n.text + '\n' : '') + '半径 ' + fmtNum(displayRadius(n)) + ' ' + radiusUnit(n) + (n.type === 'sector' ? '\n开角 ' + fmtNum(sectorSweep(n)) + '°' : '');
  }
  const labels = { eo: '光电扇区', radar: '雷达扇区', defense: '防御圈' };
  const defs = [
    ['coverage-eo', 'eo', 'sector', '光电扇区', '#d97706', 60, ''],
    ['coverage-radar', 'radar', 'sector', '雷达扇区', '#2563eb', 120, ''],
    ['coverage-defense', 'defense', 'ellipse', '防御圈', '#169873', 360, ''],
    ['coverage-defense-dash', 'defense', 'ellipse', '虚线防御圈', '#169873', 360, '6 4']
  ];
  defs.forEach(function (d) {
    const spec = { type: d[2], coverageKind: d[1], w: 240, h: 240, text: d[3], fill: d[4], stroke: d[4], coverageAlpha: 15, coverageDash: d[6], coverageLabel: true, sw: 1.5, sweep: d[5], rot: d[2] === 'sector' ? normAngle(-d[5] / 2) : 0 };
    const thumb = shapeMarkup(d[2], 8, 2, 26, 26, d[4], d[4], 1.5, d[5]).replace('fill="' + d[4] + '"', 'fill="' + d[4] + '" fill-opacity=".15"' + (d[6] ? ' stroke-dasharray="3 2"' : ''));
    SHAPES.push({ k: d[0], name: d[3], grp: '基础形状', spec: spec, svg: '<g transform="rotate(' + spec.rot + ' 21 15)">' + thumb + '</g>' });
  });
  function field(id, kind, get, set, more) {
    NODE_FIELDS[id] = Object.assign({ id: id, kind: kind, show: function (ns) { return ns.some(isCoverage); }, scope: isCoverage, get: get, set: function (n, v) { if (isCoverage(n)) set(n, v); } }, more || {});
  }
  Object.assign(FIELD_CAP, { coverageScaled: '按本图标尺显示半径', coverageHeading: '中心方向 °', coverageKind: '范围类型', coverageRadius: '半径', coverageAlpha: '填充不透明度 %', coverageDash: '边界线型', coverageLabel: '显示半径／开角标注' });
  field('coverageKind', 'text', function (n) { return labels[n.coverageKind]; }, function () {}, { readOnly: true, note: '纯示意范围；默认画布单位，可按本图距离标尺换算。示意尺度不代表设备性能。中心方向 0° 向上、90° 向右，顺时针；改变开角时中心方向保持不变。' });
  field('coverageHeading', 'num', heading, setHeading, { min: 0, max: 359, show: function (ns) { return ns.some(function (n) { return isCoverage(n) && n.type === 'sector'; }); }, scope: function (n) { return isCoverage(n) && n.type === 'sector'; } });
  field('coverageScaled', 'check', function (n) { return !!n.coverageScaled; }, function (n, v) { n.coverageScaled = !!v; });
  field('coverageRadius', 'num', displayRadius, setDisplayRadius, { min: 0.01, max: 5000, hint: '默认画布单位；勾选标尺换算后使用本图单位，改半径会同步宽高并保持圆心' });
  field('coverageAlpha', 'num', function (n) { return Math.round(style(n).fillAlpha * 100); }, function (n, v) { n.coverageAlpha = v; }, { min: 0, max: 100 });
  field('coverageDash', 'select', function (n) { return style(n).dash; }, function (n, v) { n.coverageDash = v; }, { options: function () { return [['', '实线'], ['6 4', '虚线'], ['2 4', '点线'], ['10 4 2 4', '点划线']]; } });
  field('coverageLabel', 'check', function (n) { return n.coverageLabel !== false; }, function (n, v) { n.coverageLabel = !!v; });
  const oldSw = NODE_FIELDS.sw;
  NODE_FIELDS.sw = Object.assign({}, oldSw, { show: function (ns) { return ns.some(isCoverage) || oldSw.show(ns); }, scope: function (n) { return isCoverage(n) || oldSw.scope(n); }, get: function (n) { return isCoverage(n) ? style(n).sw : oldSw.get(n); }, set: function (n, v) { if (isCoverage(n)) n.sw = v == null ? 1.5 : v; else oldSw.set(n, v); } });
  const oldRot = NODE_FIELDS.rot;
  NODE_FIELDS.rot = Object.assign({}, oldRot, {
    show: function (ns) { const rest = ns.filter(function (n) { return !isCoverage(n); }); return rest.length > 0 && oldRot.show(rest); },
    scope: function (n) { return !isCoverage(n) && (!oldRot.scope || oldRot.scope(n)); }
  });
  const oldSweep = NODE_FIELDS.sweep;
  NODE_FIELDS.sweep = Object.assign({}, oldSweep, { set: function (n, v) {
    if (isCoverage(n) && n.type === 'sector') {
      const center = heading(n); oldSweep.set(n, v); setHeading(n, center);
    } else oldSweep.set(n, v);
  } });
  /* Derived labels go through the same layout used by SVG, PPT and Visio. */
  const originalLayout = nodeLayout;
  nodeLayout = function (n) { return originalLayout(isCoverage(n) ? Object.assign({}, n, { text: caption(n) }) : n); };
  const originalProps = renderProps;
  renderProps = function () {
    originalProps();
    const ns = selectedNodes().filter(isCoverage);
    if (!ns.length) return;
    const host = $('#props'), panel = document.createElement('div');
    panel.id = 'coverage-preview';
    const n = ns[0], st = style(n);
    const radiusInput = $('#p-coverageRadius'); if (radiusInput) radiusInput.step = 'any';
    const geom = shapeMarkup(n.type, 8, 8, 104, 104, n.fill || '#2563eb', n.stroke || '#2563eb', st.sw, n.sweep)
      .replace(/<(path|ellipse) /, '<$1 fill-opacity="' + st.fillAlpha + '" stroke-dasharray="' + st.dash + '" ');
    setMarkup(panel, '<hr><div class="hint">范围预览 · ' + esc(radiusUnit(n)) + '</div><svg viewBox="0 0 120 120" width="120" height="120" aria-label="范围预览"><g transform="rotate(' + rotOf(n) + ' 60 60)">' + geom + '</g></svg>');
    ['coverageRadius', 'sweep', 'coverageHeading', 'coverageAlpha'].forEach(function (id) {
      const f = NODE_FIELDS[id]; if (!f || (f.show && !f.show(ns))) return;
      const row = document.createElement('div'); row.className = 'row';
      const mixed = fieldState(ns, f).mixed, v = mixed ? f.min : f.get(n);
      setMarkup(row, '<label for="coverage-slide-' + id + '">' + esc(FIELD_CAP[id] || id) + '</label><input id="coverage-slide-' + id + '" type="range" min="' + f.min + '" max="' + f.max + '" step="1" value="' + v + '" aria-label="' + esc(FIELD_CAP[id] || id) + '滑杆">');
      const input = row.querySelector('input');
      input.addEventListener('input', function () { const targets = fieldItems(ns, f); applyShared(targets, function (it) { f.set(it, +input.value); }, true); const box = $('#p-' + id); if (box) box.value = input.value; });
      input.addEventListener('change', function () { sharedArm = false; render(); });
      panel.appendChild(row);
    });
    host.insertBefore(panel, host.firstChild);
    /* Width/height inputs retain the circular radius contract too. */
    if (ns.length === 1) host.querySelectorAll('[data-geo="w"], [data-geo="h"]').forEach(function (input) {
      input.addEventListener('input', function () { const v = +input.value; if (!(v >= 16)) return; const other = input.dataset.geo === 'w' ? 'h' : 'w'; n[other] = n[input.dataset.geo]; const peer = host.querySelector('[data-geo="' + other + '"]'); if (peer) peer.value = n[other]; render(false); });
    });
  };
  return { isCoverage: isCoverage, heading: heading, displayRadius: displayRadius, radius: radius, resize: resize, style: style, caption: caption, presets: defs };
})();
