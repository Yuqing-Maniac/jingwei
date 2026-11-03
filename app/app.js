'use strict';
/* ============ 经纬织图 · 核心 ============ */
const FONT = "'Noto Sans SC','Microsoft YaHei','PingFang SC','Source Han Sans SC','WenQuanYi Micro Hei',sans-serif";
const FONT_CHOICES = [
  { id: '', name: '默认', face: 'Microsoft YaHei', css: FONT },
  { id: 'song', name: '宋体', face: 'SimSun', css: "SimSun,'Noto Serif CJK SC','Noto Serif SC','Source Han Serif SC','STSong','Songti SC',serif" },
  { id: 'hei', name: '黑体', face: 'SimHei', css: "SimHei,'Noto Sans CJK SC','Noto Sans SC','Source Han Sans SC','STHeiti','Heiti SC',sans-serif" },
  { id: 'fangsong', name: '仿宋', face: 'FangSong', css: "FangSong,'FangSong_GB2312','STFangsong','FZFangSong-Z02',serif" },
  { id: 'kai', name: '楷体', face: 'KaiTi', css: "KaiTi,'KaiTi_GB2312','STKaiti','AR PL UKai CN',serif" },
  { id: 'yahei', name: '微软雅黑', face: 'Microsoft YaHei', css: "'Microsoft YaHei','Noto Sans CJK SC','PingFang SC','Noto Sans SC',sans-serif" },
  { id: 'noto', name: '思源黑体', face: 'Noto Sans CJK SC', css: "'Noto Sans CJK SC','Noto Sans SC','Source Han Sans SC','WenQuanYi Micro Hei',sans-serif" },
  { id: 'noto-serif', name: '思源宋体', face: 'Noto Serif CJK SC', css: "'Noto Serif CJK SC','Noto Serif SC','Source Han Serif SC',serif" },
  { id: 'wqy', name: '文泉驿微米黑', face: 'WenQuanYi Micro Hei', css: "'WenQuanYi Micro Hei','WenQuanYi Zen Hei','Noto Sans CJK SC',sans-serif" },
  { id: 'uming', name: '文鼎明体', face: 'AR PL UMing CN', css: "'AR PL UMing CN','AR PL UMing HK',SimSun,serif" },
  { id: 'ukai', name: '文鼎楷体', face: 'AR PL UKai CN', css: "'AR PL UKai CN','AR PL UKai HK',KaiTi,serif" },
];
const CN_SIZES = [['初号', 42], ['小初', 36], ['一号', 26], ['小一', 24], ['二号', 22], ['小二', 18], ['三号', 16], ['小三', 15], ['四号', 14], ['小四', 12], ['五号', 10.5], ['小五', 9], ['六号', 7.5], ['小六', 6.5], ['七号', 5.5], ['八号', 5]].map(([name, pt]) => ({ name, pt }));
function fontChoice(n) { const id = (n && n.font) || ''; return FONT_CHOICES.find(f => f.id === id) || FONT_CHOICES[0]; }
function fontCSS(n) { return fontChoice(n).css; }
function fontFace(n) { return fontChoice(n).face; }
function faceNamesXml() {
  const seen = {};
  let s = '';
  for (const f of FONT_CHOICES) {
    if (seen[f.face]) continue;
    seen[f.face] = 1;
    s += `<FaceName NameU='${f.face}' UnicodeRanges='-1 -369098753 63 0' CharSets='1074266271 0' Panose='2 11 5 3 2 2 4 2 2 4' Flags='325'/>`;
  }
  return s;
}
function sizeLabel(v) { const n = +v; const hit = CN_SIZES.find(s => Math.abs(s.pt - n) < 0.05); return hit ? hit.name : String(v == null || v === '' ? 13 : v); }
function parseSize(raw) {
  const s = String(raw == null ? '' : raw).trim();
  if (!s) return null;
  const hit = CN_SIZES.find(x => x.name === s);
  if (hit) return hit.pt;
  const n = Number(s);
  if (!isFinite(n)) return null;
  return clamp(Math.round(n * 10) / 10, 5, 72);
}
const GRID = 4;
const CONT = { band: 0, lane: 1, group: 2 };
const isCont = n => n && n.type in CONT;

const THEMES = {
  report: { name: '汇报蓝灰', bg: '#FFFFFF', text: '#1B2433', muted: '#5B6576',
    band: { fill: '#F4F6F9', stroke: '#2E3B4E', titleFill: '#2E3B4E', titleText: '#FFFFFF' },
    lane: { fill: '#FFFFFF', stroke: '#D3DAE3', titleText: '#1B2433' },
    group: { fill: '#F0F4F9', stroke: '#8EA2BB', titleFill: '#DCE5F0', titleText: '#1B2433' },
    box: { fill: '#FFFFFF', stroke: '#4A5A70', text: '#1B2433' },
    st: { new: { fill: '#FDE8C8', stroke: '#D4861A', title: '#F7D29A' }, key: { fill: '#DDEBFF', stroke: '#2F6FDB', title: '#BCD5FA' } },
    note: { fill: '#F7F8FA', stroke: '#C9D1DC' },
    link: { plain: '#4A5A70', data: '#2F6FDB', ctrl: '#D0562B', wired: '#2E3B4E', radio: '#7A45C9', sat: '#0E9F8E' } },
  command: { name: '指挥深色', bg: '#0B1520', text: '#E6F0FB', muted: '#8AA4BF',
    band: { fill: '#0F1E2D', stroke: '#2D5B82', titleFill: '#174069', titleText: '#DDEEFF' },
    lane: { fill: '#0E1B29', stroke: '#22405E', titleText: '#A9CDF2' },
    group: { fill: '#12273D', stroke: '#3B78B0', titleFill: '#1A3A5C', titleText: '#DDEEFF' },
    box: { fill: '#14304B', stroke: '#4C9BE0', text: '#E6F2FF' },
    st: { new: { fill: '#4A3413', stroke: '#F2A33A', title: '#6A4815' }, key: { fill: '#0F3A4A', stroke: '#2BD4C4', title: '#15505E' } },
    note: { fill: '#0F1E2D', stroke: '#2D5B82' },
    link: { plain: '#8AA4BF', data: '#4CA8FF', ctrl: '#FF8A5B', wired: '#C3D2E3', radio: '#B58CFF', sat: '#2BD4C4' } },
  ink: { name: '公文素雅', bg: '#FFFFFF', text: '#1E2A22', muted: '#5E6B61',
    band: { fill: '#F6F8F4', stroke: '#3F5B46', titleFill: '#3F5B46', titleText: '#FFFFFF' },
    lane: { fill: '#FFFFFF', stroke: '#CCD6CC', titleText: '#1E2A22' },
    group: { fill: '#EEF3EC', stroke: '#7E9A84', titleFill: '#DFE9DD', titleText: '#1E2A22' },
    box: { fill: '#FFFFFF', stroke: '#55665A', text: '#1E2A22' },
    st: { new: { fill: '#FBE6C8', stroke: '#C9822B', title: '#F3CF98' }, key: { fill: '#E3EEF8', stroke: '#3C6E9E', title: '#C9DDF0' } },
    note: { fill: '#F7F9F6', stroke: '#C9D3C9' },
    link: { plain: '#55665A', data: '#3C6E9E', ctrl: '#B5532A', wired: '#2F3D33', radio: '#7A4FA8', sat: '#1F8C7A' } },
};
const LINK_KINDS = {
  plain: { name: '关联', dash: '' }, data: { name: '数据流', dash: '' }, ctrl: { name: '指令流', dash: '6 4' },
  wired: { name: '有线／光纤', dash: '', w: 2.4 }, radio: { name: '无线／数据链', dash: '2 4' }, sat: { name: '卫通链路', dash: '10 4 2 4' },
};
const PPT_DASH = { '': 'solid', '6 4': 'dash', '2 4': 'sysDot', '10 4 2 4': 'lgDashDot' };
const VSD_PAT = { '': 1, '6 4': 2, '2 4': 3, '10 4 2 4': 4 };
/* 军标：[SIDC, 名称, 分组]；全部经 milsymbol isValid() 校验（2525C 15 位字母码；无人艇／无人潜航器／无人车用 2525D 20 位数字码） */
const MS_LIST = [
  ['SFGPUCI---', '步兵分队', '分队'], ['SFGPUCIZ--', '机械化步兵', '分队'], ['SFGPUCA---', '装甲分队', '分队'], ['SFGPUCF---', '炮兵分队', '分队'],
  ['SFGPUCFRM-', '火箭炮兵分队', '分队'], ['SFGPUCD---', '防空分队', '分队'], ['SFGPUCDM--', '防空导弹分队', '分队'], ['SFGPUCR---', '侦察分队', '分队'],
  ['SFFPG-----', '特种作战分队', '分队'], ['SFGPUCE---', '工兵分队', '分队'], ['SFGPUUS---', '通信分队', '分队'], ['SFGPUUMSE-', '电子对抗分队', '分队'],
  ['SFGPUCVU--', '无人机分队', '分队'], ['SFGPUSS---', '后勤保障分队', '分队'], ['SFGPUST---', '运输分队', '分队'], ['SFGPUSX---', '维修保障分队', '分队'],
  ['SFGPUSM---', '卫勤分队', '分队'], ['SFGPUUA---', '防化分队', '分队'], ['SFGPUCM---', '导弹分队', '分队'], ['SFGPUH----', '指挥所', '分队'],
  ['SFAPMF----', '固定翼飞机', '空中'], ['SFAPMFF---', '战斗机', '空中'], ['SFAPMFB---', '轰炸机', '空中'], ['SFAPMFC---', '运输机', '空中'],
  ['SFAPMFK---', '加油机', '空中'], ['SFAPMFRW--', '预警机', '空中'], ['SFAPMFJ---', '电子战飞机', '空中'], ['SFAPMFR---', '侦察机', '空中'],
  ['SFAPMH----', '直升机', '空中'], ['SFAPMHA---', '武装直升机', '空中'], ['SFAPMFQ---', '固定翼无人机', '空中'], ['SFAPMHQ---', '旋翼无人机', '空中'],
  ['SFAPWM----', '导弹', '空中'], ['SFAPWMS---', '地（舰）射导弹', '空中'], ['SFPPS-----', '卫星', '空中'],
  ['SFSPCLCV--', '航空母舰', '海上'], ['SFSPCLCC--', '巡洋舰', '海上'], ['SFSPCLDD--', '驱逐舰', '海上'], ['SFSPCLFF--', '护卫舰', '海上'],
  ['SFSPCALA--', '两栖攻击舰', '海上'], ['SFSPCMMS--', '扫雷舰', '海上'], ['SFSPCPSB--', '巡逻艇', '海上'], ['SFSPNR----', '综合补给舰', '海上'],
  ['10033000001207000000', '水面无人艇', '海上'], ['SFUPS-----', '潜艇', '海上'], ['SFUPSN----', '核潜艇', '海上'], ['10033500001104000000', '无人潜航器', '海上'], ['SFUPWT----', '鱼雷', '海上'],
  ['SFGPEVAT--', '坦克', '陆地装备'], ['SFGPEVAI--', '步兵战车', '陆地装备'], ['SFGPEVAA--', '装甲运兵车', '陆地装备'], ['SFGPEWHMS-', '自行火炮', '陆地装备'],
  ['SFGPEWHM--', '牵引火炮', '陆地装备'], ['SFGPEWRH--', '火箭炮', '陆地装备'], ['SFGPEWMA--', '防空导弹发射车', '陆地装备'], ['SFGPEWMS--', '地地导弹发射车', '陆地装备'],
  ['SFGPESR---', '雷达', '陆地装备'], ['SFGPESE---', '电子战设备', '陆地装备'], ['10031500001502000000', '地面无人车', '陆地装备'], ['SFGPEVE---', '工程车辆', '陆地装备'], ['SFGPEVU---', '保障车辆', '陆地装备'],
  ['SFGPIB----', '军事基地', '设施'], ['SFGPIBA---', '机场', '设施'], ['SFGPIBN---', '港口', '设施'], ['SFGPIUE---', '电力设施', '设施'],
  ['SFGPIRP---', '油料设施', '设施'], ['SFGPIUT---', '通信设施', '设施'], ['SFGPIXH---', '野战医院', '设施'],
  ['SHAPMFQ---', '敌方固定翼无人机', '敌方'], ['SHAPMHQ---', '敌方旋翼无人机', '敌方'], ['SHAPMFF---', '敌方战斗机', '敌方'], ['SHAPWM----', '敌方导弹', '敌方'],
  ['SHSPCLCV--', '敌方航母', '敌方'], ['SHSPCLDD--', '敌方驱逐舰', '敌方'], ['SHUPS-----', '敌方潜艇', '敌方'], ['10063000001207000000', '敌方无人艇', '敌方'],
  ['SHGPUCI---', '敌方步兵分队', '敌方'], ['SHGPUCA---', '敌方装甲分队', '敌方'], ['SHGPEVAT--', '敌方坦克', '敌方'], ['SHGPEWMA--', '敌方防空导弹', '敌方'],
  ['SHGPESR---', '敌方雷达', '敌方'], ['SHGPUH----', '敌方指挥所', '敌方'],
];
/* old docs used SFSPCA---- (两栖舰) for 航空母舰 — keep it resolvable */
const MS_ALIAS = { 'SFSPCA----': '航空母舰' };

/* ---------- utilities ---------- */
const $ = s => document.querySelector(s);
const uid = () => Math.random().toString(36).slice(2, 9);
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const snapv = v => Math.round(v / GRID) * GRID;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const mctx = document.createElement('canvas').getContext('2d');
const mcache = new Map();
function measure(str, size, bold, family) {
  const fam = family || FONT;
  const k = size + '|' + (bold ? 1 : 0) + '|' + fam + '|' + str;
  let v = mcache.get(k);
  if (v === undefined) { mctx.font = `${bold ? 700 : 400} ${size}px ${fam}`; v = mctx.measureText(str).width; mcache.set(k, v); }
  return v;
}
function wrap(text, maxW, size, bold, family) {
  const out = [];
  String(text ?? '').split('\n').forEach(para => {
    const toks = para.match(/[A-Za-z0-9.\-_/%+:#@]+|\s+|./gu) || [''];
    let line = '';
    for (const t of toks) {
      const cand = line + t;
      /* 行首禁则：句读与右括号不落到下一行行首，悬挂在本行末尾 */
      if (measure(cand, size, bold, family) <= maxW || !line.trim() || /^[，。、；：！？）」』”’》〉…,.;:!?)\]]+$/.test(t)) line = cand;
      else { out.push(line.trimEnd()); line = t.trimStart(); }
      while (measure(line, size, bold, family) > maxW && line.length > 1 && !(line.length >= 2 && /^[，。、；：！？）」』”’》〉…,.;:!?)\]]$/.test(line.slice(-1)) && measure(line.slice(0, -1), size, bold, family) <= maxW)) {
        let i = line.length - 1; while (i > 1 && measure(line.slice(0, i), size, bold, family) > maxW) i--;
        out.push(line.slice(0, i)); line = line.slice(i);
      }
    }
    out.push(line);
  });
  return out;
}
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toast.h); toast.h = setTimeout(() => t.classList.remove('show'), 2400); }

/* ---------- icons ---------- */
const ICONS = (typeof ICON_LIB !== 'undefined' ? ICON_LIB : []);
const ICON_MAP = Object.fromEntries(ICONS.map(i => [i.key, i]));
const uriCache = new Map();
const svgUri = s => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(s);
function iconURI(key) {
  if (!key) return null;
  const ck = key.startsWith('ms:') ? key + '|' + msMode() : key;
  if (uriCache.has(ck)) return uriCache.get(ck);
  let u = null;
  if (key.startsWith('lib:')) { const i = ICON_MAP[key.slice(4)]; if (i) u = svgUri(i.svg); }
  else if (key.startsWith('ms:')) {
    try { if (window.ms) u = svgUri(new ms.Symbol(key.slice(3), msOptions()).asSVG()); } catch (e) { }
  } else if (key.startsWith('cu:')) { const c = doc.custom[key.slice(3)]; if (c) u = c.uri; }
  if (u && !key.startsWith('cu:')) uriCache.set(ck, u);
  return u;
}
/* 军标配色：nato = 友蓝敌红（默认）；cn = 我红敌蓝 */
const msMode = () => (typeof doc !== 'undefined' && doc && doc.msColor === 'cn') ? 'cn' : 'nato';
let MS_CN = null;
function msOptions() {
  const o = { size: 60, fill: true, frame: true };
  if (msMode() === 'cn' && window.ms && ms.ColorMode) { MS_CN = MS_CN || new ms.ColorMode('rgb(128,0,128)', 'rgb(255,128,128)', 'rgb(128,224,255)', 'rgb(170,255,170)', 'rgb(255,255,128)'); o.colorMode = MS_CN; }
  return o;
}
function iconName(key) {
  if (!key) return '';
  if (key.startsWith('lib:')) return ICON_MAP[key.slice(4)]?.name || '';
  if (key.startsWith('ms:')) return (MS_LIST.find(m => m[0] === key.slice(3)) || [, MS_ALIAS[key.slice(3)] || '军标'])[1];
  if (key.startsWith('cu:')) return doc.custom[key.slice(3)]?.name || '自定义';
  return '';
}

/* ---------- document model ---------- */
let doc, cur = 'root', stack = ['root'];
let sel = new Set(), linkSel = new Set(), hoverId = null, hoverLink = null;
let undoS = [], redoS = [];
const P = () => doc.pages[cur];
const T = () => THEMES[doc.theme] || THEMES.report;
const nodeById = (id, p = P()) => p.nodes.find(n => n.id === id);
const kids = (id, p = P()) => p.nodes.filter(n => n.parent === id);
function descendants(id, p = P(), acc = []) { for (const k of kids(id, p)) { acc.push(k); descendants(k.id, p, acc); } return acc; }
function mkNode(o) {
  return Object.assign({ id: uid(), type: 'rect', x: 0, y: 0, w: 120, h: 40, text: '', status: 'base', parent: null, size: 13, bold: false, align: 'center', icon: null, noBox: false, sub: null }, o);
}
function selectNodes(ids) {
  const next = new Set();
  for (let i = 0; i < ids.length; i++) if (ids[i]) next.add(ids[i]);
  sel = next;
  linkSel = new Set();
}
function selectLinks(ids) {
  const next = new Set();
  for (let i = 0; i < ids.length; i++) if (ids[i]) next.add(ids[i]);
  linkSel = next;
  sel = new Set();
}
function clearSel() {
  sel = new Set();
  linkSel = new Set();
}
function onlyLinkId() {
  if (linkSel.size !== 1) return null;
  return [...linkSel][0];
}
function newPage(name) { const id = 'p' + uid(); doc.pages[id] = { id, name, nodes: [], links: [], view: null }; return id; }
function snapshot() { return JSON.stringify({ doc, cur, stack }); }
function checkpoint() { undoS.push(snapshot()); if (undoS.length > 120) undoS.shift(); redoS = []; }
function restore(s) { const o = JSON.parse(s); const ms0 = msMode(); doc = o.doc; cur = o.cur; stack = o.stack; clearSel(); if (ms0 !== msMode()) renderPalette(); render(); refreshDocTitle(); }
function undo() { if (!undoS.length) return; redoS.push(snapshot()); restore(undoS.pop()); }
function redo() { if (!redoS.length) return; undoS.push(snapshot()); restore(redoS.pop()); }

/* ---------- styling ---------- */
function stStyle(n, t) {
  const s = t.st[n.status];
  const basis = n.type === 'group' ? t.group : t.box;
  return { fill: n.fill || (s ? s.fill : basis.fill), stroke: n.stroke || (s ? s.stroke : basis.stroke), title: s ? s.title : t.group.titleFill };
}
function textBlock(lines, x, cy, size, bold, color, anchor = 'middle', family) {
  const lh = Math.round(size * 1.38);
  const y0 = cy - (lines.length * lh) / 2 + lh / 2 + size * 0.35;
  return `<text font-family="${esc(family || FONT)}" font-size="${size}" font-weight="${bold ? 700 : 400}" fill="${color}" text-anchor="${anchor}">` +
    lines.map((l, i) => `<tspan x="${x}" y="${(y0 + i * lh).toFixed(1)}">${esc(l)}</tspan>`).join('') + '</text>';
}
/* geometry of a node's inner parts — shared by SVG, PPTX and VSDX writers */
function iconAspect(key) { if (!key || !key.startsWith('cu:')) return 1; const c = doc.custom[key.slice(3)]; return (c && c.aspect) ? c.aspect : 1; }
function nodeLayout(n) {
  const t = T(), size = n.size || 13, lh = Math.round(size * 1.38), family = fontCSS(n);
  const L = { icon: null, text: null };
  const color = n.color === 'muted' ? t.muted : (n.color || (n.type === 'text' ? t.text : t.box.text));
  if (n.type === 'text' || n.type === 'note') {
    const pad = n.type === 'note' ? 10 : 2;
    const lines = wrap(n.text, n.w - pad * 2, size, n.bold, family);
    const left = n.align === 'left' || n.type === 'note';
    L.text = { lines, x: left ? n.x + pad : n.x + n.w / 2, cy: n.y + n.h / 2, size, bold: n.bold, color, anchor: left ? 'start' : 'middle', family, box: [n.x + pad, n.y, n.w - pad * 2, n.h] };
    return L;
  }
  const uri = iconURI(n.icon);
  const ib = innerBox(n), pd = ib ? 0 : 5;
  if (ib) n = Object.assign({}, n, ib);
  const top = uri && (n.type === 'equip' || (n.h >= 64 && n.h >= n.w * 0.6));
  if (uri && top) {
    const lines = n.text ? wrap(n.text, n.w - 8, size, n.bold, family) : [];
    const th = lines.length * lh;
    const asp = iconAspect(n.icon);
    let iw, ih;
    if (asp === 1) { iw = ih = clamp(Math.min(n.w - 10, n.h - th - 14), 16, 140); }
    else { const bw = Math.max(16, n.w - 10), bh = Math.max(16, n.h - th - 14); if (bw / bh > asp) { ih = bh; iw = bh * asp; } else { iw = bw; ih = bw / asp; } }
    const isz = ih;
    const iy = n.y + (n.h - isz - th - (th ? 4 : 0)) / 2;
    L.icon = { uri, x: n.x + (n.w - iw) / 2, y: iy, s: Math.max(iw, ih), w: iw, h: ih };
    if (lines.length) L.text = { lines, x: n.x + n.w / 2, cy: iy + isz + 4 + th / 2, size, bold: n.bold, color, anchor: 'middle', family, box: [n.x + 4, iy + isz + 4, n.w - 8, th] };
  } else if (uri) {
    const isz = clamp(n.h - 10, 14, 44);
    const ix = n.x + 8;
    L.icon = { uri, x: ix, y: n.y + (n.h - isz) / 2, s: isz, w: isz, h: isz };
    const tx0 = ix + isz + 4, tw = n.x + n.w - 6 - tx0;
    const lines = wrap(n.text, Math.max(20, tw), size, n.bold, family);
    L.text = { lines, x: tx0 + tw / 2, cy: n.y + n.h / 2, size, bold: n.bold, color, anchor: 'middle', family, box: [tx0, n.y, tw, n.h] };
  } else {
    const lines = wrap(n.text, n.w - pd * 2, size, n.bold, family);
    L.text = { lines, x: n.x + n.w / 2, cy: n.y + n.h / 2, size, bold: n.bold, color, anchor: 'middle', family, box: [n.x + pd, n.y, n.w - pd * 2, n.h] };
  }
  return L;
}
/* ---------- shape geometry (one source for SVG, VSDX and palette thumbnails) ----------
   GEO[type](w,h) → { fill:[closed point lists, even-odd], lines:[open polylines], shade:[{pts,op}], inner:[x,y,w,h] }
   Curves are sampled; the PPTX writer uses the matching native preset (SHP_DEF.ppt). */
function arcPts(cx, cy, rx, ry, a0, a1, n = 24) { const o = []; for (let i = 0; i <= n; i++) { const a = (a0 + (a1 - a0) * i / n) * Math.PI / 180; o.push([cx + rx * Math.cos(a), cy + ry * Math.sin(a)]); } return o; }
function bezPts(p0, c1, c2, p1, n = 20) { const o = []; for (let i = 1; i <= n; i++) { const t = i / n, u = 1 - t; o.push([u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p1[0], u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p1[1]]); } return o; }
const CLOUD_UNIT = (() => {
  const N = 9, pts = [], cx = 0.5, cy = 0.5;
  const P = i => { const a = (-100 + i * 360 / N) * Math.PI / 180; return [cx + 0.40 * Math.cos(a) * (i % 2 ? 1 : 1.04), cy + 0.32 * Math.sin(a) * (i % 3 ? 1 : 1.06)]; };
  for (let i = 0; i < N; i++) {
    const a = P(i), b = P((i + 1) % N), m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], dx = m[0] - cx, dy = m[1] - cy, L = Math.hypot(dx, dy), k = Math.hypot(b[0] - a[0], b[1] - a[1]) * 0.62;
    const c = [m[0] + dx / L * k, m[1] + dy / L * k];
    if (!i) pts.push(a);
    pts.push(...bezPts(a, [a[0] + (c[0] - a[0]) * 1.1, a[1] + (c[1] - a[1]) * 1.1], [b[0] + (c[0] - b[0]) * 1.1, b[1] + (c[1] - b[1]) * 1.1], b, 10));
  }
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]), x0 = Math.min(...xs), y0 = Math.min(...ys), sx = Math.max(...xs) - x0, sy = Math.max(...ys) - y0;
  return pts.map(p => [(p[0] - x0) / sx, (p[1] - y0) / sy]);
})();
const sideR = (w, h) => Math.max(0, Math.min(10, h / 3, w / 3));
const GEO = {
  rect: (w, h) => ({ fill: [[[0, 0], [w, 0], [w, h], [0, h]]], inner: [5, 0, w - 10, h] }),
  diamond: (w, h) => ({ fill: [[[w / 2, 0], [w, h / 2], [w / 2, h], [0, h / 2]]], inner: [w * 0.17, h * 0.18, w * 0.66, h * 0.64] }),
  ellipse: (w, h) => ({ fill: [arcPts(w / 2, h / 2, w / 2, h / 2, 0, 360, 48)], inner: [w * 0.11, h * 0.1, w * 0.78, h * 0.8] }),
  hexagon: (w, h) => { const d = Math.min(w / 4, h * 0.29); return { fill: [[[d, 0], [w - d, 0], [w, h / 2], [w - d, h], [d, h], [0, h / 2]]], inner: [d * 0.55, h * 0.06, w - d * 1.1, h * 0.88] }; },
  octagon: (w, h) => { const c = 0.29289 * Math.min(w, h); return { fill: [[[c, 0], [w - c, 0], [w, c], [w, h - c], [w - c, h], [c, h], [0, h - c], [0, c]]], inner: [c * 0.45, c * 0.45, w - c * 0.9, h - c * 0.9] }; },
  triangle: (w, h) => ({ fill: [[[w / 2, 0], [w, h], [0, h]]], inner: [w * 0.24, h * 0.44, w * 0.52, h * 0.52] }),
  parallelogram: (w, h) => { const o = 0.25 * Math.min(w, h); return { fill: [[[o, 0], [w, 0], [w - o, h], [0, h]]], inner: [o * 0.9, 0, w - o * 1.8, h] }; },
  trapezoid: (w, h) => { const o = 0.25 * Math.min(w, h); return { fill: [[[o, 0], [w - o, 0], [w, h], [0, h]]], inner: [o * 0.8, h * 0.06, w - o * 1.6, h * 0.9] }; },
  pentagon: (w, h) => ({ fill: [[[w / 2, 0], [w, h * 0.382], [w * 0.809, h], [w * 0.191, h], [0, h * 0.382]]], inner: [w * 0.2, h * 0.3, w * 0.6, h * 0.64] }),
  star: (w, h) => { const ry = h / 1.809, o = []; for (let i = 0; i < 10; i++) { const a = (-90 + i * 36) * Math.PI / 180, r = i % 2 ? 0.382 : 1; o.push([w / 2 + (w / 2 / 0.951) * r * Math.cos(a), ry + ry * r * Math.sin(a)]); } return { fill: [o], inner: [w * 0.3, h * 0.34, w * 0.4, h * 0.4] }; },
  cylinder: (w, h) => { const ry = Math.min(0.125 * Math.min(w, h) * 1.4, h / 4); return { fill: [[...arcPts(w / 2, ry, w / 2, ry, 180, 360), ...arcPts(w / 2, h - ry, w / 2, ry, 0, 180)]], lines: [arcPts(w / 2, ry, w / 2, ry, 0, 180)], inner: [3, ry * 2, w - 6, h - ry * 3] }; },
  document: (w, h) => ({ fill: [[[0, 0], [w, 0], [w, h * 0.802], ...bezPts([w, h * 0.802], [w * 0.5, h * 0.802], [w * 0.5, h * 1.1075], [0, h * 0.934])]], inner: [w * 0.04, h * 0.02, w * 0.92, h * 0.76] }),
  cloud: (w, h) => ({ fill: [CLOUD_UNIT.map(p => [p[0] * w, p[1] * h])], inner: [w * 0.17, h * 0.2, w * 0.66, h * 0.6] }),
  cube: (w, h) => { const d = 0.25 * Math.min(w, h); return { fill: [[[0, d], [d, 0], [w, 0], [w, h - d], [w - d, h], [0, h]]], lines: [[[0, d], [w - d, d], [w - d, h]], [[w - d, d], [w, 0]]], shade: [{ pts: [[0, d], [d, 0], [w, 0], [w - d, d]], op: 0.06 }, { pts: [[w - d, d], [w, 0], [w, h - d], [w - d, h]], op: 0.14 }], inner: [2, d, w - d - 4, h - d] }; },
  chevron: (w, h) => { const d = Math.min(0.5 * Math.min(w, h), w / 2); return { fill: [[[0, 0], [w - d, 0], [w, h / 2], [w - d, h], [0, h], [d, h / 2]]], inner: [d * 0.9, 0, Math.max(10, w - d * 1.8), h] }; },
  homeplate: (w, h) => { const d = Math.min(0.5 * Math.min(w, h), w / 2); return { fill: [[[0, 0], [w - d, 0], [w, h / 2], [w - d, h], [0, h]]], inner: [4, 0, Math.max(10, w - d * 0.7 - 4), h] }; },
  arrowR: (w, h) => { const l = Math.min(0.5 * Math.min(w, h), w); return { fill: [[[0, h * 0.25], [w - l, h * 0.25], [w - l, 0], [w, h / 2], [w - l, h], [w - l, h * 0.75], [0, h * 0.75]]], inner: [2, h * 0.25, w - l * 0.45 - 2, h * 0.5] }; },
  arrowL: (w, h) => { const l = Math.min(0.5 * Math.min(w, h), w); return { fill: [[[w, h * 0.25], [l, h * 0.25], [l, 0], [0, h / 2], [l, h], [l, h * 0.75], [w, h * 0.75]]], inner: [l * 0.45, h * 0.25, w - l * 0.45 - 2, h * 0.5] }; },
  arrowU: (w, h) => { const l = Math.min(0.5 * Math.min(w, h), h); return { fill: [[[w / 2, 0], [w, l], [w * 0.75, l], [w * 0.75, h], [w * 0.25, h], [w * 0.25, l], [0, l]]], inner: [w * 0.25, l * 0.5, w * 0.5, h - l * 0.5] }; },
  arrowD: (w, h) => { const l = Math.min(0.5 * Math.min(w, h), h); return { fill: [[[w * 0.25, 0], [w * 0.75, 0], [w * 0.75, h - l], [w, h - l], [w / 2, h], [0, h - l], [w * 0.25, h - l]]], inner: [w * 0.25, 0, w * 0.5, h - l * 0.5] }; },
  arrowLR: (w, h) => { const l = Math.min(0.5 * Math.min(w, h), w / 2); return { fill: [[[0, h / 2], [l, 0], [l, h * 0.25], [w - l, h * 0.25], [w - l, 0], [w, h / 2], [w - l, h], [w - l, h * 0.75], [l, h * 0.75], [l, h]]], inner: [l * 0.6, h * 0.25, w - l * 1.2, h * 0.5] }; },
  arrowUD: (w, h) => { const l = Math.min(0.5 * Math.min(w, h), h / 2); return { fill: [[[w / 2, 0], [w, l], [w * 0.75, l], [w * 0.75, h - l], [w, h - l], [w / 2, h], [0, h - l], [w * 0.25, h - l], [w * 0.25, l], [0, l]]], inner: [w * 0.25, l * 0.6, w * 0.5, h - l * 1.2] }; },
  callout: (w, h) => ({ fill: [[[0, 0], [w, 0], [w, h], [w * 0.4167, h], [w * 0.2917, h * 1.125], [w * 0.1667, h], [0, h]]], inner: [5, 0, w - 10, h] }),
  plus: (w, h) => { const a = 0.25 * Math.min(w, h); return { fill: [[[a, 0], [w - a, 0], [w - a, a], [w, a], [w, h - a], [w - a, h - a], [w - a, h], [a, h], [a, h - a], [0, h - a], [0, a], [a, a]]], inner: [a, a, w - 2 * a, h - 2 * a] }; },
  donut: (w, h) => { const t = 0.25 * Math.min(w, h); return { fill: [arcPts(w / 2, h / 2, w / 2, h / 2, 0, 360, 48), arcPts(w / 2, h / 2, w / 2 - t, h / 2 - t, 360, 0, 48)], inner: [t + (w / 2 - t) * 0.3, t + (h / 2 - t) * 0.3, (w / 2 - t) * 1.4, (h / 2 - t) * 1.4] }; },
  predef: (w, h) => ({ fill: [[[0, 0], [w, 0], [w, h], [0, h]]], lines: [[[w / 8, 0], [w / 8, h]], [[w * 7 / 8, 0], [w * 7 / 8, h]]], inner: [w / 8 + 3, 0, w * 0.75 - 6, h] }),
  display: (w, h) => ({ fill: [[[0, h / 2], [w / 6, 0], ...arcPts(w * 5 / 6, h / 2, w / 6, h / 2, -90, 90), [w / 6, h]]], inner: [w / 6, 0, w * 4 / 6, h] }),
  delay: (w, h) => ({ fill: [[[0, 0], ...arcPts(w / 2, h / 2, w / 2, h / 2, -90, 90), [0, h]]], inner: [4, h * 0.12, w * 0.8, h * 0.76] }),
  terminator: (w, h) => { const rx = Math.min(0.161 * w * 1.0, h * 0.75); return { fill: [[...arcPts(w - rx, h / 2, rx, h / 2, -90, 90), ...arcPts(rx, h / 2, rx, h / 2, 90, 270)]], inner: [rx * 0.5, 0, w - rx, h] }; },
  /* 单侧圆角矩形：一侧两角为圆角、另一侧为直角；圆角半径与“圆角矩形”一致 */
  roundL: (w, h) => { const r = sideR(w, h); return { fill: [[[w, 0], [w, h], ...arcPts(r, h - r, r, r, 90, 180, 8), ...arcPts(r, r, r, r, 180, 270, 8)]], inner: [5, 0, w - 10, h] }; },
  roundR: (w, h) => { const r = sideR(w, h); return { fill: [[[0, h], [0, 0], ...arcPts(w - r, r, r, r, 270, 360, 8), ...arcPts(w - r, h - r, r, r, 0, 90, 8)]], inner: [5, 0, w - 10, h] }; },
  frame: (w, h) => { const t = 0.125 * Math.min(w, h); return { fill: [[[0, 0], [w, 0], [w, h], [0, h]], [[t, t], [t, h - t], [w - t, h - t], [w - t, t]]], inner: [t + 2, t, w - 2 * t - 4, h - 2 * t] }; },
};
/* shape registry: name, palette group, native PowerPoint preset, keep = keep own size in 一键美化 */
const SHP_DEF = {
  rect: { name: '矩形', ppt: 'rect' }, round: { name: '圆角矩形', ppt: 'roundRect' }, ellipse: { name: '椭圆／圆', ppt: 'ellipse' }, diamond: { name: '菱形', ppt: 'diamond' },
  hexagon: { name: '六边形', ppt: 'hexagon' }, octagon: { name: '八边形', ppt: 'octagon', keep: 1 }, triangle: { name: '三角形', ppt: 'triangle', keep: 1 },
  parallelogram: { name: '平行四边形', ppt: 'parallelogram' }, trapezoid: { name: '梯形', ppt: 'trapezoid' }, pentagon: { name: '五边形', ppt: 'pentagon', keep: 1 },
  star: { name: '五角星', ppt: 'star5', keep: 1 }, cylinder: { name: '圆柱体', ppt: 'can', keep: 1 }, cloud: { name: '云', ppt: 'cloud', keep: 1 }, cube: { name: '立方体', ppt: 'cube', keep: 1 },
  plus: { name: '十字', ppt: 'plus', keep: 1 }, donut: { name: '圆环', ppt: 'donut', keep: 1 }, frame: { name: '边框', ppt: 'frame' },
  document: { name: '文档', ppt: 'flowChartDocument' }, predef: { name: '预定义过程', ppt: 'flowChartPredefinedProcess' }, display: { name: '显示', ppt: 'flowChartDisplay' },
  delay: { name: '延迟', ppt: 'flowChartDelay' }, terminator: { name: '起止', ppt: 'flowChartTerminator' }, callout: { name: '矩形标注', ppt: 'wedgeRectCallout' },
  roundL: { name: '左圆角矩形', ppt: 'custGeom' }, roundR: { name: '右圆角矩形', ppt: 'custGeom' },
  chevron: { name: '流程箭头', ppt: 'chevron' }, homeplate: { name: '标签箭头', ppt: 'homePlate' },
  arrowR: { name: '右箭头', ppt: 'rightArrow' }, arrowL: { name: '左箭头', ppt: 'leftArrow' }, arrowU: { name: '上箭头', ppt: 'upArrow', keep: 1 }, arrowD: { name: '下箭头', ppt: 'downArrow', keep: 1 },
  arrowLR: { name: '双向箭头', ppt: 'leftRightArrow' }, arrowUD: { name: '上下箭头', ppt: 'upDownArrow', keep: 1 },
};
/* PowerPoint 自由曲线：单侧圆角矩形（英寸，三次贝塞尔圆角，可在 PPT 中编辑顶点） */
function sideRoundPts(type, w, h, r) {
  const k = 0.5523 * r, q = v => +v.toFixed(4), P = (x, y, c) => Object.assign({ x: q(x), y: q(y) }, c ? { curve: { type: 'cubic', x1: q(c[0]), y1: q(c[1]), x2: q(c[2]), y2: q(c[3]) } } : {});
  return type === 'roundL'
    ? [P(r, 0), P(w, 0), P(w, h), P(r, h), P(0, h - r, [r - k, h, 0, h - r + k]), P(0, r), P(r, 0, [0, r - k, r - k, 0]), { close: true }]
    : [P(0, 0), P(w - r, 0), P(w, r, [w - r + k, 0, w, r - k]), P(w, h - r), P(w - r, h, [w, h - r + k, w - r + k, h]), P(0, h), { close: true }];
}
const keepsSize = n => n.type === 'equip' || !!(SHP_DEF[n.type] && SHP_DEF[n.type].keep);
function shapeGeom(type, w, h) { const g = (GEO[type] || GEO.rect)(w, h); g.lines = g.lines || []; g.shade = g.shade || []; return g; }
const ptsD = (pts, x, y, close) => 'M' + pts.map(p => `${(x + p[0]).toFixed(1)},${(y + p[1]).toFixed(1)}`).join(' L') + (close ? 'Z' : '');
function shapeMarkup(type, x, y, w, h, fill, stroke, sw = 1.2) {
  const a = `fill="${fill}" stroke="${stroke}" stroke-width="${sw}"`;
  if (type === 'ellipse') return `<ellipse cx="${x + w / 2}" cy="${y + h / 2}" rx="${w / 2}" ry="${h / 2}" ${a}/>`;
  if (type === 'diamond') return `<polygon points="${x + w / 2},${y} ${x + w},${y + h / 2} ${x + w / 2},${y + h} ${x},${y + h / 2}" ${a}/>`;
  if (GEO[type] && type !== 'rect') {
    const g = shapeGeom(type, w, h);
    let s = `<path d="${g.fill.map(p => ptsD(p, x, y, true)).join(' ')}" fill-rule="evenodd" stroke-linejoin="round" ${a}/>`;
    for (const sh of g.shade) s += `<path d="${ptsD(sh.pts, x, y, true)}" fill="#000" fill-opacity="${sh.op}" stroke="none"/>`;
    for (const l of g.lines) s += `<path d="${ptsD(l, x, y)}" fill="none" stroke="${stroke}" stroke-width="${sw}" stroke-linejoin="round"/>`;
    return s;
  }
  const rx = type === 'round' || type === 'equip' ? Math.min(10, h / 3) : 3;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" ${a}/>`;
}
/* text/icon box inside a shape (absolute coords) */
function innerBox(n) {
  if (!GEO[n.type] || n.type === 'rect' || n.noBox) return null;
  const b = shapeGeom(n.type, n.w, n.h).inner; return { x: n.x + b[0], y: n.y + b[1], w: Math.max(12, b[2]), h: Math.max(12, b[3]) };
}
const BAND_TW = 34, GROUP_TH = 26;
const laneTW = n => n.titleW || 96;

/* 规范包（standards.js）钩子：编号标签、连线标签文字 */
const linkText = (l, p) => window.Std ? Std.linkLabel(l, p) : (l.label || '');
const codeTagOf = (n, p) => window.Std ? Std.codeTag(n, p) : null;
function legendEntries(p) {
  const t = T(), out = [];
  const used = new Set(p.nodes.filter(n => !['text', 'note', 'legend', 'band', 'lane', 'tblock'].includes(n.type)).map(n => n.status || 'base'));
  for (const s of ['base', 'new', 'key']) if (used.has(s)) out.push({ kind: 'st', s, label: doc.statusLabels[s] });
  const lk = new Set(p.links.map(l => l.kind));
  for (const k of Object.keys(LINK_KINDS)) if (lk.has(k)) out.push({ kind: 'ln', k, label: LINK_KINDS[k].name });
  return out;
}
function legendLayout(n, p) {
  const e = legendEntries(p);
  const rowH = 22, colW = 150, cols = e.length > 4 ? 2 : 1, rows = Math.ceil(e.length / cols);
  n.w = Math.max(n.w || 0, cols * colW + 16); n.h = Math.max(28, rows * rowH + 14);
  return e.map((it, i) => ({ ...it, x: n.x + 10 + Math.floor(i / rows) * colW, y: n.y + 7 + (i % rows) * rowH }));
}

function nodeSVG(n, p, exp) {
  const t = T(); let s = '';
  if (n.type === 'band') {
    const st = stStyle(n, t);
    s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" fill="${n.fill || t.band.fill}" stroke="${n.stroke || t.band.stroke}" stroke-width="1.5"/>`;
    s += `<rect x="${n.x}" y="${n.y}" width="${BAND_TW}" height="${n.h}" fill="${n.status === 'base' ? t.band.titleFill : st.stroke}"/>`;
    const chars = [...String(n.text || '')].filter(c => c.trim());
    s += textBlock(chars.length ? chars : [''], n.x + BAND_TW / 2, n.y + n.h / 2, 15, true, t.band.titleText);
  } else if (n.type === 'lane') {
    const tw = laneTW(n);
    s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" fill="${n.fill || t.lane.fill}" stroke="${t.lane.stroke}" stroke-width="1"/>`;
    s += `<line x1="${n.x + tw}" y1="${n.y + 6}" x2="${n.x + tw}" y2="${n.y + n.h - 6}" stroke="${t.lane.stroke}" stroke-width="1"/>`;
    s += textBlock(wrap(n.text, tw - 14, 13.5, true), n.x + tw / 2, n.y + n.h / 2, 13.5, true, t.lane.titleText);
  } else if (n.type === 'group') {
    const st = stStyle(n, t);
    s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="6" fill="${st.fill === t.box.fill ? t.group.fill : st.fill}" stroke="${st.stroke === t.box.stroke ? t.group.stroke : st.stroke}" stroke-width="1.3"/>`;
    s += `<path d="M${n.x + 0.65},${n.y + GROUP_TH} V${n.y + 6} Q${n.x + 0.65},${n.y + 0.65} ${n.x + 6},${n.y + 0.65} H${n.x + n.w - 6} Q${n.x + n.w - 0.65},${n.y + 0.65} ${n.x + n.w - 0.65},${n.y + 6} V${n.y + GROUP_TH} Z" fill="${n.status === 'base' ? t.group.titleFill : st.title}"/>`;
    /* 显示编号时，标题避开左上角的编号牌：居中放不下就右移 */
    const tg = codeTagOf(n, p), L0 = tg ? tg.x + tg.w + 6 : n.x + 6, avail = n.x + n.w - 6 - L0;
    const tl = wrap(n.text, Math.max(24, tg ? avail : n.w - 12), 12.5, true).slice(0, 1), tw0 = measure(tl[0] || '', 12.5, true);
    let tcx = n.x + n.w / 2; if (tg && tcx - tw0 / 2 < L0) tcx = Math.min(L0 + tw0 / 2, n.x + n.w - 6 - tw0 / 2);
    s += textBlock(tl, tcx, n.y + GROUP_TH / 2, 12.5, true, t.group.titleText);
  } else if (n.type === 'tblock') {
    if (window.Std) s += Std.tblockSVG(n, p);
  } else if (n.type === 'legend') {
    const items = legendLayout(n, p);
    s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="4" fill="${t.note.fill}" stroke="${t.note.stroke}"/>`;
    for (const it of items) {
      if (it.kind === 'st') {
        const ss = it.s === 'base' ? { fill: t.box.fill, stroke: t.box.stroke } : t.st[it.s];
        s += `<rect x="${it.x}" y="${it.y + 3}" width="26" height="14" rx="2" fill="${ss.fill}" stroke="${ss.stroke}"/>`;
      } else {
        const c = t.link[it.k], d = LINK_KINDS[it.k].dash;
        s += `<line x1="${it.x}" y1="${it.y + 10}" x2="${it.x + 22}" y2="${it.y + 10}" stroke="${c}" stroke-width="${LINK_KINDS[it.k].w || 1.6}" ${d ? `stroke-dasharray="${d}"` : ''}/><path d="M${it.x + 20},${it.y + 6} L${it.x + 27},${it.y + 10} L${it.x + 20},${it.y + 14} Z" fill="${c}"/>`;
      }
      s += textBlock([it.label], it.x + 34, it.y + 10, 12, false, t.text, 'start');
    }
  } else {
    if (n.type === 'note') s += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="3" fill="${t.note.fill}" stroke="${t.note.stroke}"/>`;
    else if (n.type !== 'text' && !n.noBox) { const st = stStyle(n, t); s += shapeMarkup(n.type, n.x, n.y, n.w, n.h, st.fill, st.stroke); }
    else if (n.type === 'equip' && n.noBox && n.status !== 'base') { const st = stStyle(n, t); s += shapeMarkup('equip', n.x, n.y, n.w, n.h, st.fill, st.stroke, 1); }
    const L = nodeLayout(n);
    if (L.icon) s += `<image href="${L.icon.uri}" x="${L.icon.x.toFixed(1)}" y="${L.icon.y.toFixed(1)}" width="${(L.icon.w || L.icon.s).toFixed(1)}" height="${(L.icon.h || L.icon.s).toFixed(1)}" preserveAspectRatio="xMidYMid meet"/>`;
    if (L.text) s += textBlock(L.text.lines, L.text.x, L.text.cy, L.text.size, L.text.bold, L.text.color, L.text.anchor, L.text.family);
  }
  if (window.Std) s += Std.codeTagSVG(n, p);
  if (!exp && n.sub) s += `<g data-enter="${n.id}" style="cursor:pointer"><title>进入内部结构</title><circle cx="${n.x + n.w - 2}" cy="${n.y + 2}" r="8" fill="#2F80ED"/><path d="M${n.x + n.w - 6},${n.y + 2} h8 M${n.x + n.w - 2},${n.y - 2} v8" stroke="#fff" stroke-width="1.8"/></g>`;
  return `<g data-id="${n.id}">${s}</g>`;
}

/* ---------- link routing ----------
   computeRoutes(p): for every link → { pts, jumps }.
   1) port spreading — links leaving the same side of a node get evenly spaced attachment points,
      ordered by the far end's position; a straight run is kept when both ends can share one coordinate;
   2) channel separation — overlapping middle segments of elbow links are fanned out ~7 px apart,
      in the order that gives the fewest crossings within the bundle;
   3) line jumps — every horizontal segment hops (arc) or breaks (gap) where a vertical segment of another link crosses it. */
const JUMP_R = 5;
function segCross(p1, p2, p3, p4) {
  const d = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x);
  if (Math.abs(d) < 1e-9) return false;
  const t = ((p3.x - p1.x) * (p4.y - p3.y) - (p3.y - p1.y) * (p4.x - p3.x)) / d, u = ((p3.x - p1.x) * (p2.y - p1.y) - (p3.y - p1.y) * (p2.x - p1.x)) / d;
  const e = 0.02; return t > e && t < 1 - e && u > e && u < 1 - e;
}
function segHitsBox(u, v, o) { const x0 = Math.min(u.x, v.x), x1 = Math.max(u.x, v.x), y0 = Math.min(u.y, v.y), y1 = Math.max(u.y, v.y); return x1 > o.x + 2 && x0 < o.x + o.w - 2 && y1 > o.y + 2 && y0 < o.y + o.h - 2; }
function polyCross(A, B) { let c = 0; for (let i = 0; i < A.length - 1; i++) for (let j = 0; j < B.length - 1; j++) if (segCross(A[i], A[i + 1], B[j], B[j + 1])) c++; return c; }
function routeSig(p) {
  let s = (doc && doc.jumpStyle || 'arc') + (doc && doc.avoid === false ? 'n' : 'y') + '|';
  for (const n of p.nodes) s += n.id + ',' + n.x + ',' + n.y + ',' + n.w + ',' + n.h + ';';
  for (const l of p.links) s += l.id + ',' + l.from + ',' + l.to + ',' + (l.route || '') + ';';
  return s;
}
const routeMemo = new WeakMap();
function routesFor(p = P()) {
  const sig = routeSig(p), m = routeMemo.get(p);
  if (m && m.sig === sig) return m.map;
  const map = computeRoutes(p); routeMemo.set(p, { sig, map }); return map;
}
function computeRoutes(p) {
  const map = new Map(), info = [], ends = new Map();
  const byId = new Map(p.nodes.map(n => [n.id, n]));
  const obst = p.nodes.filter(n => !isCont(n) && !['text', 'note', 'legend', 'tblock'].includes(n.type));
  const addEnd = (n, side, e) => { const k = n.id + '|' + side; if (!ends.has(k)) ends.set(k, { n, side, list: [] }); ends.get(k).list.push(e); };
  p.links.forEach((l, idx) => {
    const a = byId.get(l.from), b = byId.get(l.to); if (!a || !b) return;
    const acx = a.x + a.w / 2, acy = a.y + a.h / 2, bcx = b.x + b.w / 2, bcy = b.y + b.h / 2;
    const gapX = Math.max(b.x - (a.x + a.w), a.x - (b.x + b.w)), gapY = Math.max(b.y - (a.y + a.h), a.y - (b.y + b.h));
    if (l.route === 'straight' || (gapX < 0 && gapY < 0) || a === b) { map.set(l.id, { pts: [clipRect(a, bcx, bcy), clipRect(b, acx, acy)], jumps: [] }); return; }
    let hor = gapY < 24 ? gapX >= gapY : (gapX < 24 ? false : gapX > gapY * 2.5);
    if (gapX >= 12 && gapY >= 12) { /* both orientations feasible: pick the one whose elbow passes through fewer other boxes */
      const hits = h => { const q = h ? [{ x: acx, y: acy }, { x: (acx + bcx) / 2, y: acy }, { x: (acx + bcx) / 2, y: bcy }, { x: bcx, y: bcy }] : [{ x: acx, y: acy }, { x: acx, y: (acy + bcy) / 2 }, { x: bcx, y: (acy + bcy) / 2 }, { x: bcx, y: bcy }]; let c = 0; for (const o of obst) if (o !== a && o !== b) for (let i = 0; i < 3; i++) if (segHitsBox(q[i], q[i + 1], o)) { c++; break; } return c; };
      const hh = hits(true), hv = hits(false); if (hh !== hv) hor = hh < hv;
    }
    const fwd = hor ? bcx > acx : bcy > acy;
    const it = { l, idx, a, b, hor, fwd, lo: hor ? Math.max(a.y, b.y) : Math.max(a.x, b.x), hi: hor ? Math.min(a.y + a.h, b.y + b.h) : Math.min(a.x + a.w, b.x + b.w) };
    info.push(it);
    const sA = hor ? (fwd ? 'r' : 'l') : (fwd ? 'b' : 't'), sB = hor ? (fwd ? 'l' : 'r') : (fwd ? 't' : 'b');
  });
  const usedSegs = [];
  const sideOf = (n, q) => Math.abs(q.x - n.x) < 0.6 ? 'l' : Math.abs(q.x - n.x - n.w) < 0.6 ? 'r' : Math.abs(q.y - n.y) < 0.6 ? 't' : 'b';
  for (const it of info) {
    const { a, b, hor, fwd } = it;
    const cA = hor ? (fwd ? a.x + a.w : a.x) : (fwd ? a.y + a.h : a.y), cB = hor ? (fwd ? b.x : b.x + b.w) : (fwd ? b.y : b.y + b.h);
    const P2 = (c, t) => hor ? { x: c, y: t } : { x: t, y: c };
    /* 端口一律取边的中点：两框中点基本对齐时直连，否则走 Z 形 */
    const mA = hor ? a.y + a.h / 2 : a.x + a.w / 2, mB = hor ? b.y + b.h / 2 : b.x + b.w / 2;
    let pts;
    if (Math.abs(mA - mB) <= 4) { const t = (mA + mB) / 2; pts = [P2(cA, t), P2(cB, t)]; }
    else { const m = (cA + cB) / 2; pts = [P2(cA, mA), P2(m, mA), P2(m, mB), P2(cB, mB)]; }
    /* 自动避障：默认走线压过其他框时，按“拐弯最少、直线最长”另选出入边绕行 */
    if (doc.avoid !== false) {
      const others = obst.filter(o => o !== a && o !== b && !isAncestor(o, a, byId) && !isAncestor(o, b, byId));
      if (pathHits(pts, others)) {
        const r = detourRoute(a, b, others, usedSegs);
        if (r) { pts = r; it.detour = true; for (let k = 0; k < r.length - 1; k++) usedSegs.push([r[k], r[k + 1]]); }
      }
    }
    it.pts = pts; it.sa = sideOf(a, pts[0]); it.sb = sideOf(b, pts[pts.length - 1]);
    map.set(it.l.id, { pts, jumps: [] });
  }
  /* 1. 端口分布：同一条边上的多条连线以边中点为中心对称排布（单条即在中点） */
  const ends2 = new Map();
  for (const it of info) for (const w of ['a', 'b']) { const n = it[w], k = n.id + '|' + it['s' + w]; if (!ends2.has(k)) ends2.set(k, { n, side: it['s' + w], list: [] }); ends2.get(k).list.push({ it, w }); }
  for (const { n, side, list } of ends2.values()) {
    if (list.length < 2) continue;
    const v = side === 'l' || side === 'r', len = v ? n.h : n.w, k = list.length, sp = Math.min(len / (k + 1), 24, GEO[n.type] && !OUTLINE_RECT.has(n.type) && !n.noBox ? len * 0.18 : 1e9); /* 菱形、椭圆等端口收拢在顶点附近 */
    const ax = v ? 'y' : 'x';
    const ref = e => { const q = e.it.pts, i = e.w === 'a' ? Math.min(2, q.length - 1) : Math.max(0, q.length - 3); const o = e.w === 'a' ? e.it.b : e.it.a; return q.length > 2 ? q[i][ax] : o[ax] + o[v ? 'h' : 'w'] / 2; };
    list.sort((e1, e2) => ref(e1) - ref(e2) || e1.it.idx - e2.it.idx);
    list.forEach((e, i) => { e.it['o' + e.w] = (i - (k - 1) / 2) * sp; });
  }
  for (const it of info) {
    const oa = it.oa || 0, ob = it.ob || 0, q = it.pts, ax = (it.sa === 'l' || it.sa === 'r') ? 'y' : 'x', bx = (it.sb === 'l' || it.sb === 'r') ? 'y' : 'x';
    if (q.length === 2) {
      if (Math.abs(oa - ob) < 0.5) { q[0][ax] += oa; q[1][bx] += ob; }
      else {
        /* 直连两端偏移不同：改为中间折一下 */
        const h = ax === 'y', A = { ...q[0] }, B = { ...q[1] }; A[ax] += oa; B[bx] += ob;
        const m = h ? (A.x + B.x) / 2 : (A.y + B.y) / 2;
        it.pts = h ? [A, { x: m, y: A.y }, { x: m, y: B.y }, B] : [A, { x: A.x, y: m }, { x: B.x, y: m }, B];
        map.get(it.l.id).pts = it.pts;
      }
      continue;
    }
    if (oa) { q[0][ax] += oa; q[1][ax] += oa; }
    if (ob) { const n = q.length; q[n - 1][bx] += ob; q[n - 2][bx] += ob; }
  }
  /* 一端为多条线分布、另一端为单条线时：单条端随之对正，走直线而不是小折线 */
  const cnt = k => (ends2.get(k) || { list: [] }).list.length;
  for (const it of info) {
    const q = it.pts; if (it.detour || q.length !== 4) continue;
    const hor = Math.abs(q[0].y - q[1].y) < 0.5, ax = hor ? 'y' : 'x';
    const ka = cnt(it.a.id + '|' + it.sa), kb = cnt(it.b.id + '|' + it.sb);
    const span = (n, v) => hor ? v > n.y + 6 && v < n.y + n.h - 6 : v > n.x + 6 && v < n.x + n.w - 6;
    if (ka > 1 && kb === 1 && span(it.b, q[0][ax])) { q[3][ax] = q[0][ax]; it.pts = [q[0], q[3]]; }
    else if (kb > 1 && ka === 1 && span(it.a, q[3][ax])) { q[0][ax] = q[3][ax]; it.pts = [q[0], q[3]]; }
    else if (ka === 1 && kb === 1 && Math.abs(q[0][ax] - q[3][ax]) <= 12) { const t = (q[0][ax] + q[3][ax]) / 2; if (span(it.a, t) && span(it.b, t)) { q[0][ax] = q[3][ax] = t; it.pts = [q[0], q[3]]; } }
    map.get(it.l.id).pts = it.pts;
  }
  /* Z 形线的中段（用于通道错开） */
  const mids = [];
  for (const it of info) {
    const q = it.pts; if (it.detour || q.length !== 4) continue;
    const hor = Math.abs(q[0].y - q[1].y) < 0.5;
    mids.push({ it, hor, c: hor ? q[1].x : q[1].y, lo: Math.min(q[1][hor ? 'y' : 'x'], q[2][hor ? 'y' : 'x']), hi: Math.max(q[1][hor ? 'y' : 'x'], q[2][hor ? 'y' : 'x']), e0: Math.min(q[0][hor ? 'x' : 'y'], q[3][hor ? 'x' : 'y']), e1: Math.max(q[0][hor ? 'x' : 'y'], q[3][hor ? 'x' : 'y']) });
  }
  /* 2. channel separation */
  for (const hor of [true, false]) {
    const segs = mids.filter(m => m.hor === hor).sort((x, y) => x.c - y.c);
    const par = segs.map((_, i) => i), find = i => par[i] === i ? i : (par[i] = find(par[i]));
    for (let i = 0; i < segs.length; i++) for (let j = i + 1; j < segs.length && segs[j].c - segs[i].c < 4; j++)
      if (Math.min(segs[i].hi, segs[j].hi) - Math.max(segs[i].lo, segs[j].lo) > 2) par[find(j)] = find(i);
    const groups = new Map(); segs.forEach((s, i) => { const r = find(i); if (!groups.has(r)) groups.set(r, []); groups.get(r).push(s); });
    for (const g of groups.values()) {
      if (g.length < 2) continue;
      const k = g.length, c0 = g.reduce((t, s) => t + s.c, 0) / k;
      const room = Math.min(...g.map(s => s.e1 - s.e0)) - 12, sp = Math.max(2, Math.min(7, room / (k - 1)));
      const place = order => order.forEach((s, i) => { const c = c0 + (i - (k - 1) / 2) * sp; const q = s.it.pts; if (hor) { q[1].x = q[2].x = c; } else { q[1].y = q[2].y = c; } });
      const tA = s => s.it.pts[0][hor ? 'y' : 'x'], tB = s => s.it.pts[3][hor ? 'y' : 'x'];
      const cands = [[...g].sort((x, y) => tA(x) - tA(y)), [...g].sort((x, y) => tA(y) - tA(x)), [...g].sort((x, y) => tB(x) - tB(y)), [...g].sort((x, y) => tB(y) - tB(x))];
      let best = null, bc = Infinity;
      for (const o of cands) { place(o); let c = 0; for (let i = 0; i < k; i++) for (let j = i + 1; j < k; j++) c += polyCross(g[i].it.pts, g[j].it.pts); if (c < bc) { bc = c; best = o; } }
      place(best);
    }
  }
  /* 2b. 绕行线的重叠段错开（同一通道上的多条绕行线间隔 8 px） */
  nudgeDetours(info.filter(i => i.detour));
  /* 2c. 同一边上相邻两个端口互换能减少交叉时互换（嵌套的 U 形线外圈用外侧端口） */
  for (const { side, list } of ends2.values()) {
    if (list.length < 2) continue;
    const ax = side === 'l' || side === 'r' ? 'y' : 'x';
    const idxs = e => { const n = e.it.pts.length; return e.w === 'a' ? [0, 1] : [n - 1, n - 2]; };
    const cross = () => { let c = 0; for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++) c += polyCross(list[i].it.pts, list[j].it.pts); return c; };
    for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++) {
      const A = list[i], B = list[j]; if (A.it.pts.length < 3 || B.it.pts.length < 3) continue;
      const before = cross(), [a0, a1] = idxs(A), [b0, b1] = idxs(B), va = A.it.pts[a0][ax], vb = B.it.pts[b0][ax];
      const set = (E, i0, i1, v) => { E.it.pts[i0][ax] = v; E.it.pts[i1][ax] = v; };
      set(A, a0, a1, vb); set(B, b0, b1, va);
      if (cross() >= before) { set(A, a0, a1, va); set(B, b0, b1, vb); }
    }
  }
  /* 2d. 非矩形图形（菱形、椭圆、三角形、云等）：端点从外接框边沿连线方向推到图形轮廓上，避免线头悬空 */
  for (const it of info) {
    const q = it.pts; if (!q || q.length < 2) continue;
    for (const [n, i, j] of [[it.a, 0, 1], [it.b, q.length - 1, q.length - 2]]) {
      if (!n || n.noBox || !GEO[n.type] || OUTLINE_RECT.has(n.type)) continue;
      const e = q[i], f = q[j], v = Math.abs(e.x - f.x) < 0.5; /* 端段竖直 → 端点在上／下边 */
      const hit = outlineHit(n, v ? (e.y <= n.y + 0.6 ? 't' : 'b') : (e.x <= n.x + 0.6 ? 'l' : 'r'), e);
      if (hit) { e.x = hit.x; e.y = hit.y; }
    }
  }
  /* 3. line jumps (horizontal segments hop over vertical ones) */
  const all = [...map.entries()].map(([id, r]) => ({ id, r }));
  const verts = [];
  for (const { id, r } of all) for (let i = 0; i < r.pts.length - 1; i++) { const u = r.pts[i], v = r.pts[i + 1]; if (Math.abs(u.x - v.x) < 0.5 && Math.abs(u.y - v.y) > 1) verts.push({ id, x: u.x, y0: Math.min(u.y, v.y), y1: Math.max(u.y, v.y) }); }
  const R = JUMP_R;
  for (const { id, r } of all) {
    for (let i = 0; i < r.pts.length - 1; i++) {
      const u = r.pts[i], v = r.pts[i + 1]; if (Math.abs(u.y - v.y) >= 0.5 || Math.abs(u.x - v.x) < 2 * R + 6) continue;
      const x0 = Math.min(u.x, v.x), x1 = Math.max(u.x, v.x), y = u.y;
      let xs = verts.filter(t => t.id !== id && t.x > x0 + R + 2 && t.x < x1 - R - 2 && y > t.y0 + 0.5 && y < t.y1 - 0.5).map(t => t.x).sort((p, q) => p - q);
      if (!xs.length) continue;
      const hops = []; for (const x of xs) { const h = hops[hops.length - 1]; if (h && x - h.b < 2 * R + 3) h.b = x; else hops.push({ a: x, b: x }); }
      const list = hops.map(h => ({ c: (h.a + h.b) / 2, hw: (h.b - h.a) / 2 + R }));
      if (v.x < u.x) list.reverse();
      r.jumps.push({ seg: i, list });
    }
  }
  return map;
}
const OUTLINE_RECT = new Set(['rect', 'round', 'roundL', 'roundR', 'equip', 'predef', 'frame', 'callout', 'note']);
/* 外接框边上的点 e，沿垂直于该边的方向与图形轮廓求交（取最外侧交点）；无交点返回 null */
function outlineHit(n, side, e) {
  if (Math.abs(side === 'l' ? e.x - n.x : side === 'r' ? e.x - n.x - n.w : side === 't' ? e.y - n.y : e.y - n.y - n.h) > 0.8) return null;
  const g = shapeGeom(n.type, n.w, n.h), hz = side === 'l' || side === 'r', c = hz ? e.y - n.y : e.x - n.x, hits = [];
  for (const poly of g.fill.slice(0, 1)) for (let k = 0; k < poly.length; k++) {
    const A = poly[k], B = poly[(k + 1) % poly.length], a0 = hz ? A[1] : A[0], b0 = hz ? B[1] : B[0];
    if ((a0 - c) * (b0 - c) > 0 || a0 === b0) continue;
    const t = (c - a0) / (b0 - a0); hits.push(hz ? A[0] + (B[0] - A[0]) * t : A[1] + (B[1] - A[1]) * t);
  }
  if (!hits.length) return null;
  const d = side === 'l' || side === 't' ? Math.min(...hits) : Math.max(...hits);
  return hz ? { x: n.x + d, y: e.y } : { x: e.x, y: n.y + d };
}
/* ---------- 自动避障 ---------- */
function isAncestor(o, n, byId) { let q = n.parent ? byId.get(n.parent) : null, g = 0; while (q && g++ < 30) { if (q === o) return true; q = q.parent ? byId.get(q.parent) : null; } return false; }
function pathHits(pts, obs) { for (let i = 0; i < pts.length - 1; i++) for (const o of obs) if (segHitsBox(pts[i], pts[i + 1], o)) return true; return false; }
/* 正交可视图上的 A*：节点取各障碍物外扩边界与端口坐标的交点，代价 = 长度 + 拐弯罚分 */
function detourRoute(a, b, obs, used = []) {
  const PAD = 16, BEND = 90;
  const sides = n => [['t', { x: n.x + n.w / 2, y: n.y }, 1], ['b', { x: n.x + n.w / 2, y: n.y + n.h }, 1], ['l', { x: n.x, y: n.y + n.h / 2 }, 0], ['r', { x: n.x + n.w, y: n.y + n.h / 2 }, 0]];
  const out = (pt, s, d) => ({ x: pt.x + (s === 'r' ? d : s === 'l' ? -d : 0), y: pt.y + (s === 'b' ? d : s === 't' ? -d : 0) });
  const boxes = obs.concat([a, b]).map(o => ({ x0: o.x - PAD + 0.5, y0: o.y - PAD + 0.5, x1: o.x + o.w + PAD - 0.5, y1: o.y + o.h + PAD - 0.5 }));
  const inside = (x, y) => boxes.some(r => x > r.x0 && x < r.x1 && y > r.y0 && y < r.y1);
  const blockedH = (y, xa, xb) => { const x0 = Math.min(xa, xb), x1 = Math.max(xa, xb); return boxes.some(r => y > r.y0 && y < r.y1 && x1 > r.x0 && x0 < r.x1); };
  const blockedV = (x, ya, yb) => { const y0 = Math.min(ya, yb), y1 = Math.max(ya, yb); return boxes.some(r => x > r.x0 && x < r.x1 && y1 > r.y0 && y0 < r.y1); };
  const R2 = v => Math.round(v * 2) / 2;
  const S = sides(a).map(([s, pt, ax]) => ({ s, pt, ax, st: out(pt, s, PAD) })).filter(e => !inside(e.st.x, e.st.y));
  const Gs = sides(b).map(([s, pt, ax]) => ({ s, pt, ax, st: out(pt, s, PAD) })).filter(e => !inside(e.st.x, e.st.y));
  if (!S.length || !Gs.length) return null;
  const allp = S.concat(Gs).map(e => e.st);
  const bx0 = Math.min(...allp.map(q => q.x)), bx1 = Math.max(...allp.map(q => q.x)), by0 = Math.min(...allp.map(q => q.y)), by1 = Math.max(...allp.map(q => q.y));
  const near = boxes.filter(r => r.x1 > bx0 - 400 && r.x0 < bx1 + 400 && r.y1 > by0 - 400 && r.y0 < by1 + 400);
  const uniq = arr => [...new Set(arr.map(R2))].sort((u, v) => u - v);
  const xs = uniq([...allp.map(q => q.x), ...near.flatMap(r => [r.x0 - 0.5, r.x1 + 0.5])]), ys = uniq([...allp.map(q => q.y), ...near.flatMap(r => [r.y0 - 0.5, r.y1 + 0.5])]);
  const W = xs.length, H = ys.length; if (W * H > 40000) return null;
  const key = (i, j) => j * W + i, ix = v => xs.indexOf(R2(v)), jy = v => ys.indexOf(R2(v));
  const goal = new Map(); for (const g of Gs) { const k = key(ix(g.st.x), jy(g.st.y)); if (!goal.has(k)) goal.set(k, []); goal.get(k).push(g); }
  const dist = new Float64Array(W * H * 2).fill(Infinity), prev = new Int32Array(W * H * 2).fill(-1), startOf = new Int8Array(W * H * 2).fill(-1);
  const heap = []; const push = (c, s) => { heap.push([c, s]); let i = heap.length - 1; while (i > 0) { const q = (i - 1) >> 1; if (heap[q][0] <= heap[i][0]) break; [heap[q], heap[i]] = [heap[i], heap[q]]; i = q; } };
  const pop = () => { const t = heap[0], l = heap.pop(); if (heap.length) { heap[0] = l; let i = 0; for (;;) { const a1 = 2 * i + 1, a2 = a1 + 1; let m = i; if (a1 < heap.length && heap[a1][0] < heap[m][0]) m = a1; if (a2 < heap.length && heap[a2][0] < heap[m][0]) m = a2; if (m === i) break; [heap[m], heap[i]] = [heap[i], heap[m]]; i = m; } } return t; };
  const hx = (i, j) => Math.min(...Gs.map(g => Math.abs(xs[i] - g.st.x) + Math.abs(ys[j] - g.st.y)));
  S.forEach((e, si) => { const i = ix(e.st.x), j = jy(e.st.y); if (i < 0 || j < 0) return; const st = key(i, j) * 2 + e.ax; if (0 < dist[st]) { dist[st] = 0; startOf[st] = si; push(hx(i, j), st); } });
  let best = null, guard = 0;
  while (heap.length && guard++ < 250000) {
    const [f, st] = pop(); const k = st >> 1, dir = st & 1, i = k % W, j = (k / W) | 0, c = dist[st];
    if (best && f >= best.c) break;
    if (goal.has(k)) for (const g of goal.get(k)) { const tc = c + (dir !== g.ax ? BEND : 0); if (!best || tc < best.c) best = { c: tc, st, g }; }
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const ni = i + di, nj = j + dj; if (ni < 0 || nj < 0 || ni >= W || nj >= H) continue;
      const nd = dj ? 1 : 0;
      if (nd === 0 ? blockedH(ys[j], xs[i], xs[ni]) : blockedV(xs[i], ys[j], ys[nj])) continue;
      if (inside(xs[ni], ys[nj])) continue;
      let nc = c + Math.abs(xs[ni] - xs[i]) + Math.abs(ys[nj] - ys[j]) + (nd !== dir ? BEND : 0);
      if (used.length) { const x0 = Math.min(xs[i], xs[ni]), x1 = Math.max(xs[i], xs[ni]), y0 = Math.min(ys[j], ys[nj]), y1 = Math.max(ys[j], ys[nj]); for (const [u, v] of used) { if (nd === 0 && Math.abs(u.y - v.y) < 0.5 && Math.abs(u.y - ys[j]) < 4 && Math.min(x1, Math.max(u.x, v.x)) - Math.max(x0, Math.min(u.x, v.x)) > 2) { nc += 0.25 * (x1 - x0); break; } if (nd === 1 && Math.abs(u.x - v.x) < 0.5 && Math.abs(u.x - xs[i]) < 4 && Math.min(y1, Math.max(u.y, v.y)) - Math.max(y0, Math.min(u.y, v.y)) > 2) { nc += 0.25 * (y1 - y0); break; } } }
      const ns = key(ni, nj) * 2 + nd;
      if (nc < dist[ns]) { dist[ns] = nc; prev[ns] = st; push(nc + hx(ni, nj), ns); }
    }
  }
  if (!best) return null;
  const path = []; let st = best.st, first = st; for (; st >= 0; st = prev[st]) { const k = st >> 1; path.push({ x: xs[k % W], y: ys[(k / W) | 0] }); first = st; }
  path.reverse();
  /* 起点边：路径起点对应的出线边 */
  const p0 = path[0], sA = S.find(e => Math.abs(e.st.x - p0.x) < 0.6 && Math.abs(e.st.y - p0.y) < 0.6 && e.ax === (first & 1)) || S.find(e => Math.abs(e.st.x - p0.x) < 0.6 && Math.abs(e.st.y - p0.y) < 0.6);
  const all = [sA.pt, ...path, best.g.pt], outp = [];
  for (const q of all) { const n = outp.length; if (n && Math.abs(outp[n - 1].x - q.x) < 0.5 && Math.abs(outp[n - 1].y - q.y) < 0.5) continue; if (n >= 2) { const u = outp[n - 2], v = outp[n - 1]; if ((Math.abs(u.x - v.x) < 0.5 && Math.abs(v.x - q.x) < 0.5) || (Math.abs(u.y - v.y) < 0.5 && Math.abs(v.y - q.y) < 0.5)) { outp[n - 1] = { x: q.x, y: q.y }; continue; } } outp.push({ x: q.x, y: q.y }); }
  return outp;
}
function nudgeDetours(list) {
  const segs = [];
  for (const it of list) { const q = it.pts; for (let i = 1; i < q.length - 2; i++) { const u = q[i], v = q[i + 1], h = Math.abs(u.y - v.y) < 0.5; segs.push({ it, i, h, c: h ? u.y : u.x, lo: h ? Math.min(u.x, v.x) : Math.min(u.y, v.y), hi: h ? Math.max(u.x, v.x) : Math.max(u.y, v.y) }); } }
  for (const h of [true, false]) {
    const ss = segs.filter(s => s.h === h).sort((x, y) => x.c - y.c), used = new Set();
    for (let i = 0; i < ss.length; i++) {
      if (used.has(i)) continue;
      const g = [ss[i]]; used.add(i);
      for (let j = i + 1; j < ss.length && ss[j].c - ss[i].c < 1; j++) if (!used.has(j) && g.some(s => Math.min(s.hi, ss[j].hi) - Math.max(s.lo, ss[j].lo) > 2)) { g.push(ss[j]); used.add(j); }
      if (g.length < 2) continue;
      /* 取交叉最少的排列（≤4 条穷举） */
      const apply = (ord, sign) => ord.forEach((s, k) => { const off = sign * (k - (g.length - 1) / 2) * 8, q = s.it.pts; if (h) { q[s.i].y += off; q[s.i + 1].y += off; } else { q[s.i].x += off; q[s.i + 1].x += off; } });
      const perms = a => a.length <= 1 ? [a] : a.flatMap((x, i) => perms(a.slice(0, i).concat(a.slice(i + 1))).map(r => [x, ...r]));
      const cands = g.length <= 4 ? perms(g) : [g];
      let best = cands[0], bc = Infinity;
      for (const o of cands) { apply(o, 1); let c = 0; for (let i = 0; i < g.length; i++) for (let j = i + 1; j < g.length; j++) c += polyCross(g[i].it.pts, g[j].it.pts); apply(o, -1); if (c < bc) { bc = c; best = o; } }
      apply(best, 1);
    }
  }
}
function linkPoints(l, p = P()) { const r = routesFor(p).get(l.id); return r ? r.pts : null; }
function crossingCount(p = P()) { const rs = [...routesFor(p).values()]; let c = 0; for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) c += polyCross(rs[i].pts, rs[j].pts); return c; }
/* path ops shared by SVG / PPTX / VSDX: ['M',x,y] ['L',x,y] ['J',x1,x2,y,hw] (hop) ['G',x1,x2,y] (gap) */
function linkOps(route, style = (doc && doc.jumpStyle) || 'arc') {
  const q = route.pts, ops = [['M', q[0].x, q[0].y]];
  for (let i = 1; i < q.length; i++) {
    const j = style !== 'none' && route.jumps.find(t => t.seg === i - 1);
    if (j) for (const h of j.list) { const dir = q[i].x > q[i - 1].x ? 1 : -1; ops.push([style === 'gap' ? 'G' : 'J', h.c - dir * h.hw, h.c + dir * h.hw, q[i].y, h.hw]); }
    ops.push(['L', q[i].x, q[i].y]);
  }
  return ops;
}
function opsToD(ops) {
  const f = v => v.toFixed(1); let d = '';
  for (const o of ops) {
    if (o[0] === 'M') d += `M${f(o[1])},${f(o[2])}`;
    else if (o[0] === 'L') d += ` L${f(o[1])},${f(o[2])}`;
    else if (o[0] === 'J') d += ` L${f(o[1])},${f(o[3])} A${f(o[4])},${JUMP_R} 0 0 ${o[2] > o[1] ? 1 : 0} ${f(o[2])},${f(o[3])}`;
    else if (o[0] === 'G') { const k = o[2] > o[1] ? 1.5 : -1.5; d += ` L${f(o[1] + k)},${f(o[3])} M${f(o[2] - k)},${f(o[3])}`; }
  }
  return d;
}
function clipRect(r, tx, ty) {
  const cx = r.x + r.w / 2, cy = r.y + r.h / 2, dx = tx - cx, dy = ty - cy;
  if (!dx && !dy) return { x: cx, y: cy };
  const s = Math.min(dx ? (r.w / 2) / Math.abs(dx) : Infinity, dy ? (r.h / 2) / Math.abs(dy) : Infinity);
  return { x: cx + dx * s, y: cy + dy * s };
}
function labelPos(pts) {
  if (pts.length === 4) return { x: (pts[1].x + pts[2].x) / 2, y: (pts[1].y + pts[2].y) / 2 };
  return { x: (pts[0].x + pts[pts.length - 1].x) / 2, y: (pts[0].y + pts[pts.length - 1].y) / 2 };
}
const DIR_NEXT = { one: 'both', both: 'none', none: 'one' };
const DIR_NAME = { one: '单向', both: '双向', none: '无' };
const F2_PHRASE = 'F2 编辑文字';
const PILL_IN = 28;
function linkDir(l) { return DIR_NEXT[l.dir] ? l.dir : 'one'; }
function cycleLinkDir(l) { setLinkDir(l, DIR_NEXT[linkDir(l)]); }
function setLinkDir(l, dir) { if (!DIR_NAME[dir]) return; l.dir = dir; }
function setLabelBack(l, raw) {
  const t = String(raw || '');
  if (t) l.labelBack = t; else delete l.labelBack;
}
function swapLinkEnds(l) {
  const a = l.from; l.from = l.to; l.to = a;
}
function swapLinkCaptions(l) {
  const fwd = l.label || '', rev = l.labelBack || '';
  l.label = rev;
  setLabelBack(l, fwd);
}
function swapLink(l) {
  swapLinkEnds(l);
  if (linkDir(l) === 'both') swapLinkCaptions(l);
}
const LINK_KEYS = [
  { id: 'kind', chord: '1 – 6', label: '关联／数据流／指令流／有线／无线／卫通',
    match: function (e) { return /^[1-6]$/.test(e.key) && !e.repeat; },
    apply: function (l, e) { const kinds = Object.keys(LINK_KINDS); l.kind = kinds[+e.key - 1]; doc.lastKind = l.kind; toast('链路类型：' + LINK_KINDS[l.kind].name); } },
  { id: 'dir', chord: 'D', hint: 'D 切换箭头', label: '箭头：单向 → 双向 → 无',
    match: function (e) { return (e.key || '').toLowerCase() === 'd' && !e.repeat; },
    apply: function (l) { cycleLinkDir(l); toast('箭头：' + DIR_NAME[linkDir(l)]); } },
  { id: 'turn', chord: 'R', hint: 'R 调换方向', label: '调换方向（双向时文字跟着走）',
    match: function (e) { return (e.key || '').toLowerCase() === 'r' && !e.repeat; },
    apply: function (l) { swapLink(l); toast('已调换方向'); } }
];
function linkSelToast() {
  return LINK_KEYS.filter(function (k) { return k.hint; }).map(function (k) { return k.hint; }).concat([F2_PHRASE]).join(' · ');
}
function applyLinkChord(links, bind, e) {
  if (!links.length) return;
  if (bind.id === 'kind') {
    const knd = Object.keys(LINK_KINDS)[+e.key - 1];
    if (!knd) return;
    links.forEach(l => { l.kind = knd; });
    doc.lastKind = knd;
    toast('链路类型：' + LINK_KINDS[knd].name);
    return;
  }
  if (bind.id === 'dir') {
    links.forEach(cycleLinkDir);
    toast('箭头：' + DIR_NAME[linkDir(links[0])]);
    return;
  }
  if (bind.id === 'turn') {
    links.forEach(swapLink);
    toast('已调换方向');
  }
}
function polyLen(pts) {
  let n = 0;
  for (let i = 1; i < pts.length; i++) n += Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
  return n;
}
function pointAlong(pts, dist) {
  const last = pts[pts.length - 1];
  if (!last) return { x: 0, y: 0 };
  if (pts.length < 2) return { x: last.x, y: last.y };
  let left = dist;
  for (let i = 1; i < pts.length; i++) {
    const dx = pts[i].x - pts[i - 1].x, dy = pts[i].y - pts[i - 1].y, seg = Math.hypot(dx, dy);
    if (left <= seg || i === pts.length - 1) {
      const t = seg > 0 ? Math.min(1, Math.max(0, left / seg)) : 0;
      return { x: pts[i - 1].x + dx * t, y: pts[i - 1].y + dy * t };
    }
    left -= seg;
  }
  return { x: last.x, y: last.y };
}
function pillBox(text, pos) {
  const w = measure(text, 11.5, false) + 10;
  return { x: pos.x - w / 2, y: pos.y - 9, w: w, h: 18 };
}
const labelMemo = new WeakMap();
function placeLinkPills(l, p, taken) {
  const pts = linkPoints(l, p);
  if (!pts) return [];
  const fwd = linkText(l, p), rev = l.labelBack || '', both = linkDir(l) === 'both';
  if (both && fwd && rev) {
    const total = polyLen(pts), short = total < PILL_IN * 2;
    const posFwd = labelAt(pts, fwd, taken, pointAlong(pts, short ? total * 0.72 : Math.max(0, total - PILL_IN)));
    const posRev = labelAt(pts, rev, taken.concat([pillBox(fwd, posFwd)]), pointAlong(pts, short ? total * 0.28 : Math.min(PILL_IN, total)));
    return [{ side: 'to', text: fwd, pos: posFwd }, { side: 'from', text: rev, pos: posRev }];
  }
  if (fwd) return [{ side: 'mid', text: fwd, pos: labelAt(pts, fwd, taken) }];
  if (both && rev) return [{ side: 'mid', text: rev, pos: labelAt(pts, rev, taken) }];
  return [];
}
function labelLayout(p) {
  const sig = routeSig(p) + '|' + p.links.map(x => x.id + ':' + linkDir(x) + ':' + linkText(x, p) + ':' + (x.labelBack || '')).join(';');
  let m = labelMemo.get(p);
  if (!m || m.sig !== sig) {
    const taken = [], map = new Map();
    for (const x of p.links) {
      const pills = placeLinkPills(x, p, taken);
      map.set(x.id, pills);
      for (let i = 0; i < pills.length; i++) taken.push(pillBox(pills[i].text, pills[i].pos));
    }
    m = { sig: sig, map: map };
    labelMemo.set(p, m);
  }
  return m.map;
}
function linkPills(l, p) {
  if (!linkPoints(l, p)) return [];
  return labelLayout(p).get(l.id) || [];
}
function labelFor(l, p, pts, lab) {
  const pills = linkPills(l, p);
  for (let i = 0; i < pills.length; i++) if (pills[i].text === lab) return pills[i].pos;
  return pills.length ? pills[0].pos : labelAt(pts, lab);
}
function linkLabelWidth(l, p) {
  const fwd = linkText(l, p), rev = l.labelBack || '', both = linkDir(l) === 'both';
  let w = 0;
  if (fwd) w = Math.max(w, measure(fwd, 11.5, false) + 10);
  if (both && rev) w = Math.max(w, measure(rev, 11.5, false) + 10);
  return w;
}
function pillMarkup(pill, fill, color) {
  const w = measure(pill.text, 11.5, false) + 10;
  return `<g pointer-events="none"><rect x="${(pill.pos.x - w / 2).toFixed(1)}" y="${(pill.pos.y - 9).toFixed(1)}" width="${w.toFixed(1)}" height="18" rx="3" fill="${fill}" fill-opacity="0.92"/>${textBlock([pill.text], pill.pos.x, pill.pos.y, 11.5, false, color)}</g>`;
}
function labelAt(pts, label, taken = [], seed) {
  const lp = seed || labelPos(pts), w = measure(label, 11.5, false) + 10;
  const [a, b] = pts.length === 4 ? [pts[1], pts[2]] : [pts[0], pts[pts.length - 1]];
  const len = Math.hypot(b.x - a.x, b.y - a.y), horiz = Math.abs(b.y - a.y) < Math.abs(b.x - a.x);
  let r0 = lp;
  if (!seed) {
    if (horiz && len < w + 16) r0 = { x: lp.x, y: lp.y - 14 };
    else if (!horiz && len < 30) r0 = { x: lp.x + w / 2 + 6, y: lp.y };
  }
  /* 避让：默认位置压在框上时，沿折线另找不压框的位置 */
  let obs = null;
  try { const pg = P(); obs = pg.nodes.filter(n => !isCont(n) && n.type !== 'legend' && n.type !== 'tblock').map(n => ({ x: n.x - 2, y: n.y - 2, w: n.w + 4, h: n.h + 4 })).concat(pg.nodes.filter(n => n.type === 'group').map(n => ({ x: n.x, y: n.y, w: n.w, h: GROUP_TH }))); } catch (_) { }
  obs = (obs || []).concat(taken);
  if (!obs.length) return r0;
  const hit = c => obs.some(o => c.x - w / 2 < o.x + o.w && c.x + w / 2 > o.x && c.y - 9 < o.y + o.h && c.y + 9 > o.y);
  if (!hit(r0)) return r0;
  const segs = []; for (let i = 0; i + 1 < pts.length; i++) segs.push([pts[i], pts[i + 1], Math.hypot(pts[i + 1].x - pts[i].x, pts[i + 1].y - pts[i].y)]);
  segs.sort((u, v) => v[2] - u[2]);
  for (const [a2, b2, l2] of segs) for (const t of [0.5, 0.35, 0.65, 0.2, 0.8]) {
    const c = { x: a2.x + (b2.x - a2.x) * t, y: a2.y + (b2.y - a2.y) * t };
    if (l2 > 24 && !hit(c)) return c;
    const side = Math.abs(b2.y - a2.y) > Math.abs(b2.x - a2.x) ? { x: c.x + w / 2 + 6, y: c.y } : { x: c.x, y: c.y - 14 };
    if (l2 > 24 && !hit(side)) return side;
  }
  return r0;
}
function markerDefs(t, pre) {
  return '<defs>' + Object.keys(LINK_KINDS).map(k => {
    const c = t.link[k];
    return `<marker id="${pre}e-${k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto"><path d="M0,1 L10,5 L0,9 Z" fill="${c}"/></marker>` +
      `<marker id="${pre}s-${k}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto"><path d="M10,1 L0,5 L10,9 Z" fill="${c}"/></marker>`;
  }).join('') + '</defs>';
}
function linkPaint(l, exp) {
  const K = LINK_KINDS[l.kind] || LINK_KINDS.plain;
  const theme = T().link[l.kind] || T().link.plain;
  if (exp) return { color: theme, width: K.w || 1.6, dash: K.dash || '', ownMarker: false };
  return { color: l.color || theme, width: l.sw || K.w || 1.6, dash: K.dash || '', ownMarker: !!l.color };
}
function ownMarkerDefs(l, pre, color) {
  const id = pre + 'c' + l.id;
  const head = (mid, d) => `<marker id="${mid}" viewBox="0 0 10 10" refX="${mid.endsWith('s') ? 1 : 9}" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto"><path d="${d}" fill="${color}"/></marker>`;
  let s = '<defs>' + head(id + 'e', 'M0,1 L10,5 L0,9 Z');
  if (l.dir === 'both') s += head(id + 's', 'M10,1 L0,5 L10,9 Z');
  return s + '</defs>';
}
function linkSVG(l, p, exp, pre, part) {
  const route = routesFor(p).get(l.id); if (!route) return '';
  const pts = route.pts, t = T(), paint = linkPaint(l, exp);
  const d = opsToD(linkOps(route)), dHit = 'M' + pts.map(q => `${q.x.toFixed(1)},${q.y.toFixed(1)}`).join(' L');
  const pills = linkPills(l, p);
  if (part === 'label') return pills.map(pill => pillMarkup(pill, t.bg, paint.color)).join('');
  const mid = pre + 'c' + l.id;
  const me = l.dir === 'none' ? '' : paint.ownMarker ? `marker-end="url(#${mid}e)"` : `marker-end="url(#${pre}e-${l.kind})"`;
  const ms = l.dir !== 'both' ? '' : paint.ownMarker ? `marker-start="url(#${mid}s)"` : `marker-start="url(#${pre}s-${l.kind})"`;
  const own = paint.ownMarker && l.dir !== 'none' ? ownMarkerDefs(l, pre, paint.color) : '';
  let s = `${own}<path class="lv" d="${d}" fill="none" stroke="${paint.color}" stroke-width="${paint.width}" ${paint.dash ? `stroke-dasharray="${paint.dash}"` : ''} stroke-linejoin="round" ${me} ${ms}/>`;
  if (pills.length && part !== 'line') s += pills.map(pill => pillMarkup(pill, t.bg, paint.color)).join('');
  if (!exp) return `<g class="lk" data-lk="${l.id}" data-a="${l.from}" data-b="${l.to}"><path d="${dHit}" fill="none" stroke="transparent" stroke-width="12" data-link="${l.id}" style="cursor:pointer"/>${s}</g>`;
  return `<g>${s}</g>`;
}
function drawOrder(p) {
  const conts = p.nodes.filter(isCont).sort((a, b) => CONT[a.type] - CONT[b.type] || b.w * b.h - a.w * a.h);
  return conts.concat(p.nodes.filter(n => !isCont(n)));
}
function diagramSVG(p, exp, pre = 'm') {
  const t = T();
  /* 容器在下、连线居中、框与装备在上：连线穿过的框遮住线段，不再压字 */
  const ord = drawOrder(p), conts = ord.filter(n => isCont(n)), rest = ord.filter(n => !isCont(n));
  return markerDefs(t, pre) + conts.map(n => nodeSVG(n, p, exp)).join('') + p.links.map(l => linkSVG(l, p, exp, pre, 'line')).join('') + rest.map(n => nodeSVG(n, p, exp)).join('') + p.links.map(l => linkSVG(l, p, exp, pre, 'label')).join('');
}

/* ---------- view / render ---------- */
const svg = $('#svg'), world = $('#world'), stage = $('#stage');
let view = { x: -40, y: -40, k: 1 };
let ui = { marquee: null, temp: null };
function applyView() {
  world.setAttribute('transform', `translate(${-view.x * view.k},${-view.y * view.k}) scale(${view.k})`);
  const g = 20 * view.k;
  stage.style.backgroundSize = `${g}px ${g}px`;
  stage.style.backgroundPosition = `${-view.x * view.k}px ${-view.y * view.k}px`;
  $('#z-val').textContent = Math.round(view.k * 100) + '%';
  P().cam = { ...view };
}
function overlaySVG() {
  const A = '#2F80ED'; let s = '';
  const p = P();
  linkSel.forEach(id => {
    const l = p.links.find(x => x.id === id); const pts = l && linkPoints(l);
    if (pts) s += `<path d="M${pts.map(q => q.x + ',' + q.y).join(' L')}" fill="none" stroke="${A}" stroke-opacity=".35" stroke-width="7" pointer-events="none"/>`;
  });
  for (const id of sel) {
    const n = nodeById(id); if (!n) continue;
    s += `<rect x="${n.x - 3}" y="${n.y - 3}" width="${n.w + 6}" height="${n.h + 6}" fill="none" stroke="${A}" stroke-width="${1.4 / view.k}" stroke-dasharray="${4 / view.k} ${3 / view.k}" pointer-events="none"/>`;
  }
  const hs = 8 / view.k;
  if (sel.size === 1) {
    const n = nodeById([...sel][0]);
    if (n) for (const [h, x, y] of [['nw', n.x, n.y], ['ne', n.x + n.w, n.y], ['sw', n.x, n.y + n.h], ['se', n.x + n.w, n.y + n.h]])
      s += `<rect data-h="${h}" x="${x - hs / 2}" y="${y - hs / 2}" width="${hs}" height="${hs}" fill="#fff" stroke="${A}" stroke-width="${1.4 / view.k}" style="cursor:${h === 'nw' || h === 'se' ? 'nwse' : 'nesw'}-resize"/>`;
  }
  const portFor = hoverId && !ui.drag ? nodeById(hoverId) : (sel.size === 1 && !ui.drag ? nodeById([...sel][0]) : null);
  if (portFor && portFor.type !== 'legend' && portFor.type !== 'tblock') {
    const n = portFor, r = 5 / view.k;
    for (const [x, y] of [[n.x + n.w / 2, n.y], [n.x + n.w, n.y + n.h / 2], [n.x + n.w / 2, n.y + n.h], [n.x, n.y + n.h / 2]])
      s += `<circle data-port="${n.id}" cx="${x}" cy="${y}" r="${r}" fill="${A}" stroke="#fff" stroke-width="${1.5 / view.k}" style="cursor:crosshair"><title>拖动以连线</title></circle>`;
  }
  if (ui.marquee) { const m = ui.marquee; s += `<rect x="${Math.min(m.x0, m.x1)}" y="${Math.min(m.y0, m.y1)}" width="${Math.abs(m.x1 - m.x0)}" height="${Math.abs(m.y1 - m.y0)}" fill="${A}" fill-opacity=".08" stroke="${A}" stroke-width="${1 / view.k}"/>`; }
  s += guidesSVG();
  if (ui.temp) s += `<line x1="${ui.temp.x0}" y1="${ui.temp.y0}" x2="${ui.temp.x1}" y2="${ui.temp.y1}" stroke="${A}" stroke-width="${1.6 / view.k}" stroke-dasharray="${5 / view.k} ${4 / view.k}" pointer-events="none"/>`;
  return `<g id="overlay">${s}</g>`;
}
function render(full = true) {
  const pb = contentBBox(), pp = 28;
  world.innerHTML = `<rect x="${pb.x - pp}" y="${pb.y - pp}" width="${pb.w + pp * 2}" height="${pb.h + pp * 2}" fill="${T().bg}" stroke="rgba(120,130,145,.35)" stroke-width="${1 / view.k}" pointer-events="none"/>` + diagramSVG(P(), false, 'm') + overlaySVG();
  applyView(); applyHover();
  if (full) { renderProps(); renderCrumb(); noteLinkSelection(); }
  if (window.Backup) Backup.poke();
}
let linkNoted;
function noteLinkSelection() {
  const id = onlyLinkId();
  if (id === linkNoted) return;
  linkNoted = id;
  if (id) toast(linkSelToast());
}
let linkHit = null;
function noteLinkHit(id, cx, cy) {
  const w = clientToWorld(cx, cy);
  linkHit = { id: id, x: w.x, y: w.y };
}
function focusLinkCaption(l) {
  if (!l) return;
  render();
  setTimeout(() => {
    let field = '#p-label';
    if (linkDir(l) === 'both' && linkHit && linkHit.id === l.id) {
      const pts = linkPoints(l);
      if (pts && pts.length) {
        const a = pts[0], b = pts[pts.length - 1];
        if (Math.hypot(linkHit.x - a.x, linkHit.y - a.y) < Math.hypot(linkHit.x - b.x, linkHit.y - b.y)) field = '#p-back';
      }
    }
    const i = $(field) || $('#p-label');
    if (i) { i.focus(); i.select(); }
  }, 0);
}
function dirFieldLabel(word, node) {
  const name = node && node.text ? String(node.text).split('\n')[0] : '';
  return name ? word + ' → ' + name : word;
}
function linkCanvasKeys() {
  const bits = LINK_KEYS.map(k => {
    const chord = k.chord === '1 – 6' ? '<kbd>1</kbd>–<kbd>6</kbd>' : '<kbd>' + esc(k.chord) + '</kbd>';
    const say = k.hint ? k.hint.replace(/^[A-Z]\s+/, '') : k.label;
    return chord + ' ' + esc(say);
  });
  bits.push('<kbd>F2</kbd> ' + esc(F2_PHRASE.replace(/^F2\s+/, '')) + '（双向时点靠近的一端）');
  return '选中连线后 ' + bits.join('，');
}
function linkPanelHint() {
  return esc(linkSelToast()) + '<br><kbd>1</kbd>–<kbd>6</kbd> 切换链路类型';
}
function renderOverlay() { const o = $('#overlay'); if (o) o.outerHTML = overlaySVG(); }
/* hover highlight (canvas only): links of the hovered node / the hovered link stay vivid, the rest dim */
function applyHover() {
  let any = false;
  world.querySelectorAll('g.lk').forEach(g => { const on = !!((hoverId && (g.dataset.a === hoverId || g.dataset.b === hoverId)) || (hoverLink && g.dataset.lk === hoverLink)); g.classList.toggle('on', on); any = any || on; });
  world.classList.toggle('hl', any && !ui_drag);
}
svg.addEventListener('pointerleave', () => { if (hoverId || hoverLink) { hoverId = hoverLink = null; renderOverlay(); applyHover(); } });
function clientToWorld(cx, cy) { const r = svg.getBoundingClientRect(); return { x: (cx - r.left) / view.k + view.x, y: (cy - r.top) / view.k + view.y }; }
function contentBBox(p = P()) {
  if (!p.nodes.length) return { x: 0, y: 0, w: 400, h: 300 };
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const n of p.nodes) { if (n.type === 'legend') legendLayout(n, p); x0 = Math.min(x0, n.x); y0 = Math.min(y0, n.y); x1 = Math.max(x1, n.x + n.w); y1 = Math.max(y1, n.y + n.h); }
  /* 绕行到图外侧的连线及其标签也算在图面内 */
  try {
    for (const l of p.links) {
      const q = linkPoints(l, p); if (!q) continue;
      for (const pt of q) { x0 = Math.min(x0, pt.x - 4); y0 = Math.min(y0, pt.y - 4); x1 = Math.max(x1, pt.x + 4); y1 = Math.max(y1, pt.y + 4); }
      for (const pill of linkPills(l, p)) { const b = pillBox(pill.text, pill.pos); x0 = Math.min(x0, b.x); x1 = Math.max(x1, b.x + b.w); y0 = Math.min(y0, b.y); y1 = Math.max(y1, b.y + b.h); }
    }
  } catch (_) { }
  return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
}
function fit() {
  const b = contentBBox(), r = svg.getBoundingClientRect();
  const k = clamp(Math.min((r.width - 60) / b.w, (r.height - 80) / b.h), 0.15, 2);
  view.k = k; view.x = b.x - (r.width / k - b.w) / 2; view.y = b.y - (r.height / k - b.h) / 2 + 10 / k;
  applyView(); renderOverlay();
}
function zoomAt(k2, cx, cy) {
  const w = clientToWorld(cx, cy), r = svg.getBoundingClientRect();
  view.k = clamp(k2, 0.15, 4); view.x = w.x - (cx - r.left) / view.k; view.y = w.y - (cy - r.top) / view.k; applyView(); renderOverlay();
}

/* ---------- parent assignment ---------- */
function findParent(n, p = P()) {
  const desc = new Set(descendants(n.id, p).map(d => d.id));
  const cx = n.x + n.w / 2, cy = n.y + n.h / 2;
  let best = null;
  for (const c of p.nodes) {
    if (!isCont(c) || c.id === n.id || desc.has(c.id)) continue;
    if (n.type === 'band') continue;
    if (n.type === 'lane' && c.type !== 'band') continue;
    if (n.type === 'group' && c.type === 'group' && c.w * c.h <= n.w * n.h) continue;
    if (cx < c.x || cx > c.x + c.w || cy < c.y || cy > c.y + c.h) continue;
    if (c.w * c.h <= n.w * n.h) continue;
    if (!best || c.w * c.h < best.w * best.h) best = c;
  }
  return best ? best.id : null;
}

/* ---------- auto layout (一键美化) ---------- */
/* 叶子框按文字所需高度（多行时自动加高，不再固定 36） */
const SHAPED_K = new Set(['ellipse', 'diamond', 'hexagon', 'octagon', 'cylinder', 'cloud', 'document', 'parallelogram', 'trapezoid', 'cube', 'callout', 'display', 'predef', 'chevron', 'homeplate', 'pentagon', 'triangle', 'star', 'donut', 'plus', 'delay']);
function leafH(it, w) {
  if (it.type === 'equip') return it.h;
  const size = it.size || 13, k = SHAPED_K.has(it.type) ? (it.type === 'diamond' ? 1.7 : 1.35) : 1;
  const extra = it.icon ? 30 : 0;
  const lines = it.text ? wrap(it.text, Math.max(30, w / k - 10 - extra), size, it.bold).length : 1;
  const minH = it.type === 'diamond' ? w * 0.5 : ['cylinder', 'cloud', 'cube', 'document', 'hexagon', 'octagon', 'pentagon', 'triangle', 'star', 'donut', 'plus'].includes(it.type) ? w * 0.42 : 36;
  return snapv(Math.max(36, minH, lines * Math.round(size * 1.38) * (k > 1 ? 1.25 : 1) + 12));
}
/* 导入（Visio／PPT／draw.io）的图：首次一键美化时把字号归一到织图标准字号（之后用户手调的字号保留） */
function normalizeImported(p) {
  for (const n of p.nodes) {
    if (!n.imp) continue;
    if (n.role === 'title') { n.size = 22; n.bold = true; }
    else if (n.role === 'subtitle') n.size = 13;
    else if (n.type === 'note') n.size = 12;
    else if (n.type === 'text') n.size = Math.min(16, Math.max(12, n.size || 13));
    else if (n.type === 'legend' || n.type === 'tblock') { }
    else n.size = 13;
    delete n.imp;
  }
}
function layoutRow(items, x0, x1, y0, y1, opt = {}) {
  if (!items.length) return;
  items.sort((a, b) => a.x - b.x || a.y - b.y);
  const avail = x1 - x0, n = items.length;
  if (items.some(isCont)) {
    /* 叶子取自然宽度（同行统一），其余宽度按子元素数分给容器 */
    const gap = (opt.minGap ?? 28) >= 36 ? 44 : 12;
    const leaves = items.filter(i => !isCont(i)), conts = items.filter(isCont);
    const lw = leaves.filter(i => i.type !== 'equip').length ? Math.max(...leaves.filter(i => i.type !== 'equip').map(leafNatW)) : 0;
    const leafW = i => i.type === 'equip' ? i.w : lw;
    const rest = avail - gap * (n - 1) - leaves.reduce((a, i) => a + leafW(i), 0);
    const wt = conts.map(i => Math.max(2, kids(i.id).length)), sum = wt.reduce((a, b) => a + b, 0) || 1;
    let x = x0;
    items.forEach(it => {
      const w = isCont(it) ? Math.max(120, rest * wt[conts.indexOf(it)] / sum) : leafW(it);
      if (it.type === 'equip') it.x = snapv(x); else { it.x = snapv(x); it.w = snapv(w); }
      x += w + gap;
    });
    const need = Math.max(...items.map(it => isCont(it) ? groupNeed(it) : leafH(it, it.w)));
    return need;
  }
  /* 同行相邻两框之间有带标签的连线：间距至少放得下标签，标签不压框 */
  let lg = 0;
  try { const pg = P(); for (let i = 1; i < n; i++) for (const l of pg.links) { const u = items[i - 1].id, v = items[i].id; if ((l.from === u && l.to === v) || (l.from === v && l.to === u)) { const w = linkLabelWidth(l, pg); if (w) lg = Math.max(lg, w + 16); } } } catch (_) { }
  const minGap = Math.min(Math.max(opt.minGap ?? 28, lg), Math.max(opt.minGap ?? 28, avail / n * 0.6)), cap = opt.cap ?? 210;
  for (const it of items) delete it._dy;
  /* 一行放不下（框宽会小于 72）：按网格折成多行，_dy 记录行内纵向偏移，由调用方定位 */
  if ((avail - minGap * (n - 1)) / n < 72) {
    const gw = Math.min(cap, Math.max(72, ...items.filter(i => i.type !== 'equip').map(leafNatW).concat([72])), avail);
    const cols = Math.max(1, Math.floor((avail + minGap) / (gw + minGap))), rowsN = Math.ceil(n / cols), vg = 16;
    let dy = 0;
    for (let r = 0; r < rowsN; r++) {
      const row = items.slice(r * cols, r * cols + cols), tot = row.length * gw + (row.length - 1) * minGap;
      const rh = Math.max(...row.map(i => i.type === 'equip' ? i.h : leafH(i, gw)));
      let x = x0 + (avail - tot) / 2;
      for (const it of row) {
        const h = it.type === 'equip' ? it.h : leafH(it, gw);
        if (it.type === 'equip') it.x = snapv(x + (gw - it.w) / 2); else { it.x = snapv(x); it.w = snapv(gw); }
        it._dy = dy + (rh - h) / 2; x += gw + minGap;
      }
      dy += rh + vg;
    }
    return dy - vg;
  }
  const w = Math.min(cap, (avail - minGap * (n - 1)) / n);
  const gap = n > 1 ? Math.min(Math.max(opt.maxGap ?? 72, minGap), (avail - n * w) / (n - 1)) : 0;
  const total = n * w + (n - 1) * gap; let x = x0 + (avail - total) / 2;
  for (const it of items) {
    if (it.type === 'equip') { it.x = snapv(x + (w - it.w) / 2); }
    else { it.x = snapv(x); it.w = snapv(w); }
    x += w + gap;
  }
  return Math.max(...items.map(i => leafH(i, i.type === 'equip' ? i.w : w)));
}
/* 子容器排布：按原图的行（纵向聚类）保留行结构，行内等宽、等距、居中；框按文字取自然尺寸，不再拉伸填满 */
function rowsOf(ks) {
  const list = ks.slice().sort((a, b) => (a.y + a.h / 2) - (b.y + b.h / 2)), rows = [];
  for (const k of list) {
    const c = k.y + k.h / 2, r = rows[rows.length - 1];
    if (r && c - r.cy <= Math.max(18, 0.45 * Math.min(r.h, k.h))) { r.items.push(k); r.h = Math.max(r.h, k.h); }
    else rows.push({ items: [k], cy: c, h: k.h });
  }
  rows.forEach(r => r.items.sort((a, b) => a.x - b.x));
  return rows;
}
function leafNatW(k) {
  if (k.type === 'equip') return k.w;
  const size = k.size || 13, tw = Math.max(0, ...String(k.text || '').split('\n').map(t => measure(t, size, k.bold)));
  const kk = SHAPED_K.has(k.type) ? (k.type === 'diamond' ? 1.7 : 1.35) : 1;
  return snapv(clamp(tw * kk + 28 + (k.icon ? 30 : 0), 96, 180));
}
function groupPlan(g, width) {
  const ks = kids(g.id); if (!ks.length) return { rows: [], w: Math.max(120, measure(String(g.text || '').split('\n')[0], 12.5, true) + 24), h: GROUP_TH + 40 };
  const linked = !!g.links, gap = linked ? 40 : 16, vgap = linked ? 34 : 12;
  const rows = rowsOf(ks);
  const leaves = ks.filter(k => !isCont(k) && k.type !== 'equip');
  const uw = leaves.length ? Math.max(...leaves.map(leafNatW)) : 0;
  const widthOf = k => isCont(k) ? groupPlan(k).w : k.type === 'equip' ? k.w : uw;
  let maxW = 0;
  for (const r of rows) { r.ws = r.items.map(widthOf); r.w = r.ws.reduce((a, b) => a + b, 0) + gap * (r.items.length - 1); maxW = Math.max(maxW, r.w); }
  const tg = codeTagOf(g, P()), titleW = measure(String(g.text || '').split('\n')[0], 12.5, true) + 24 + (tg ? tg.w + 8 : 0);
  const w = width || snapv(Math.max(titleW, maxW + 24));
  /* 一行放不下：按可用宽度折行（原图各子项同一高度、尚未排布时即退化为网格） */
  if (maxW > w - 24) {
    const out = [];
    for (const r of rows) {
      let cur = null;
      r.items.forEach((it, i) => {
        const x = r.ws[i];
        if (!cur || (cur.items.length && cur.w + gap + x > w - 24)) { cur = { items: [], ws: [], w: 0 }; out.push(cur); }
        cur.w += (cur.items.length ? gap : 0) + x; cur.items.push(it); cur.ws.push(x);
      });
    }
    rows.length = 0; rows.push(...out); maxW = Math.max(...rows.map(r => r.w));
  }
  /* 宽度不够时等比收窄叶子 */
  const k = Math.min(1, (w - 24) / (maxW || 1));
  for (const r of rows) {
    r.ws = r.ws.map((x, i) => { const it = r.items[i]; return it.type === 'equip' || isCont(it) ? x : snapv(Math.max(72, x * k)); });
    r.hs = r.items.map((it, i) => isCont(it) ? groupPlan(it, r.ws[i]).h : it.type === 'equip' ? it.h : leafH(it, r.ws[i]));
    r.rh = Math.max(...r.hs); r.w = r.ws.reduce((a, b) => a + b, 0) + gap * (r.items.length - 1);
  }
  const h = GROUP_TH + 12 + rows.reduce((a, r) => a + r.rh, 0) + vgap * (rows.length - 1) + 12;
  return { rows, w, h: snapv(h), gap, vgap };
}
function groupNeed(g) { return groupPlan(g, g.w).h; }
function layoutGroup(g) {
  const pl = groupPlan(g, g.w); if (!pl.rows.length) return;
  g.h = snapv(Math.max(g.h, pl.h));
  let y = g.y + GROUP_TH + 12 + Math.max(0, (g.h - pl.h) / 2);
  for (const r of pl.rows) {
    let x = g.x + (g.w - r.w) / 2;
    r.items.forEach((it, i) => {
      const w = r.ws[i], h = r.hs[i];
      const nx = snapv(x), ny = snapv(y + (r.rh - h) / 2);
      if (isCont(it)) { const dx = nx - it.x, dy = ny - it.y; for (const d of descendants(it.id)) { d.x += dx; d.y += dy; } it.x = nx; it.y = ny; it.w = snapv(w); it.h = snapv(h); layoutGroup(it); }
      else if (it.type === 'equip') { it.x = snapv(x + (w - it.w) / 2); it.y = ny; }
      else { it.x = nx; it.y = ny; it.w = snapv(w); it.h = snapv(h); }
      x += w + pl.gap;
    });
    y += r.rh + pl.vgap;
  }
}
function layoutLane(l) {
  const ks = kids(l.id); if (!ks.length) return;
  const x0 = l.x + laneTW(l) + 10, x1 = l.x + l.w - 10;
  const need = layoutRow(ks, x0, x1, 0, 0, { minGap: l.links ? 36 : 28 });
  const hasG = ks.some(isCont);
  l.h = snapv(Math.max(hasG ? need + 16 : need + 20, 56));
  for (const k of ks) {
    if (k._dy != null) { if (k.type !== 'equip') k.h = snapv(leafH(k, k.w)); k.y = snapv(l.y + (l.h - need) / 2 + k._dy); delete k._dy; continue; }
    if (isCont(k)) { k.y = snapv(l.y + 8); k.h = snapv(l.h - 16); layoutGroup(k); }
    else if (k.type === 'equip') k.y = snapv(l.y + (l.h - k.h) / 2);
    else { k.h = snapv(Math.min(leafH(k, k.w), l.h - 16)); k.y = snapv(l.y + (l.h - k.h) / 2); }
  }
}
function layoutBand(b) {
  const ks = kids(b.id);
  const lanes = ks.filter(k => k.type === 'lane').sort((a, c) => a.y - c.y);
  const others = ks.filter(k => k.type !== 'lane');
  let y = b.y + 6;
  for (const l of lanes) { l.x = b.x + BAND_TW + 6; l.w = b.w - BAND_TW - 12; l.y = snapv(y); layoutLane(l); y = l.y + l.h + 6; }
  if (others.length) {
    const need = layoutRow(others, b.x + BAND_TW + 16, b.x + b.w - 16, 0, 0, { cap: 180, maxGap: 160 });
    const rowH = Math.max(need, 40) + 20;
    for (const k of others) {
      if (k._dy != null) { if (k.type !== 'equip') k.h = snapv(leafH(k, k.w)); k.y = snapv(y + 10 + k._dy); delete k._dy; continue; }
      if (isCont(k)) { k.y = snapv(y + 4); k.h = snapv(rowH - 8); layoutGroup(k); }
      else if (k.type === 'equip') k.y = snapv(y + (rowH - k.h) / 2);
      else { k.h = leafH(k, k.w); k.y = snapv(y + (rowH - k.h) / 2); }
    }
    y += rowH;
  }
  const chars = [...String(b.text || '')].filter(c => c.trim()).length;
  b.h = snapv(Math.max(y - b.y, 40, chars * 17 + 12));
}
function bandNeedW(b, p) {
  const ks = kids(b.id, p), lanes = ks.filter(k => k.type === 'lane'), others = ks.filter(k => k.type !== 'lane');
  const rowW = items => { if (!items.length) return 0; const lw = Math.max(0, ...items.filter(i => !isCont(i) && i.type !== 'equip').map(leafNatW)); return items.reduce((a, i) => a + (isCont(i) ? groupPlan(i).w : i.type === 'equip' ? i.w : lw), 0) + 56 * (items.length - 1); };
  let w = others.length ? rowW(others) + 32 : 0;
  for (const l of lanes) w = Math.max(w, laneTW(l) + 20 + rowW(kids(l.id, p)) + 6);
  return BAND_TW + 12 + w;
}
function beautify(p = P()) {
  const saved = cur; cur = p.id;
  const imported = p.nodes.some(n => n.imp);
  normalizeImported(p);
  for (const n of p.nodes) { n.x = snapv(n.x); n.y = snapv(n.y); n.w = snapv(n.w); n.h = snapv(n.h); }
  const bands0 = p.nodes.filter(n => n.type === 'band' && !n.parent);
  const oldBottom = bands0.length ? Math.max(...bands0.map(b => b.y + b.h)) : null;
  for (const l of p.links) { const a = nodeById(l.from, p), b = nodeById(l.to, p); if (a && b && a.parent === b.parent && a.parent) { const par = nodeById(a.parent, p); if (par) par.links = true; } }
  const bands = p.nodes.filter(n => n.type === 'band' && !n.parent).sort((a, b) => a.y - b.y);
  const free = p.nodes.filter(n => !n.parent && !isCont(n));
  if (bands.length) {
    const X = Math.min(...bands.map(b => b.x));
    let W = Math.max(...bands.map(b => b.w));
    /* 导入的图：原图往往很宽，按内容收拢总宽，避免框稀疏、字显小 */
    if (imported) W = snapv(clamp(Math.max(...bands.map(b => bandNeedW(b, p))), 640, W));
    const topOf = id => { let n = nodeById(id, p); while (n && n.parent) n = nodeById(n.parent, p); return n && n.id; };
    const bgap = p.links.some(l => topOf(l.from) !== topOf(l.to)) ? 36 : 12;
    let y = bands[0].y;
    for (const b of bands) {
      const dx = X - b.x, dy = y - b.y;
      for (const d of descendants(b.id, p)) { d.x += dx; d.y += dy; }
      b.x = X; b.y = y; b.w = W; layoutBand(b); y = b.y + b.h + bgap;
    }
    const top = bands[0].y, bottom = y - bgap, cx = X + W / 2;
    const title = free.find(n => n.role === 'title'), sub = free.find(n => n.role === 'subtitle');
    let ty = top - 12;
    if (sub) { sub.w = Math.min(W, Math.max(sub.w, measure(sub.text, sub.size, sub.bold) + 20)); sub.x = snapv(cx - sub.w / 2); sub.y = snapv(ty - sub.h); ty = sub.y - 4; }
    if (title) { title.w = Math.min(W, Math.max(title.w, measure(title.text, title.size, true) + 24)); title.x = snapv(cx - title.w / 2); title.y = snapv(ty - title.h); }
    const note = free.find(n => n.role === 'note'), leg = free.find(n => n.type === 'legend');
    if (leg) { legendLayout(leg, p); leg.x = snapv(X + W - leg.w); leg.y = snapv(bottom + 12); }
    if (note) { note.x = X; note.y = snapv(bottom + 12); note.w = snapv(W - (leg ? leg.w + 12 : 0)); const lines = wrap(note.text, note.w - 20, note.size); note.h = snapv(Math.max(leg ? leg.h : 0, lines.length * Math.round(note.size * 1.38) + 16)); if (leg) leg.h = note.h; }
    shiftBelow(p, free, oldBottom, bottom, [title, sub, note, leg]);
  } else {
    p.nodes.filter(n => n.type === 'lane' && !n.parent).forEach(layoutLane);
    const linkedFlow = g => { const ks = kids(g.id, p), ids = new Set(ks.map(k => k.id)); return ks.length >= 2 && !ks.some(isCont) && p.links.some(l => ids.has(l.from) && ids.has(l.to)); };
    p.nodes.filter(n => n.type === 'group' && !n.parent && !linkedFlow(n)).forEach(g => { const pl = groupPlan(g); g.w = pl.w; g.h = pl.h; layoutGroup(g); });
    tidyFree(p);
  }
  for (const n of p.nodes) delete n.links;
  if (window.Std) Std.afterLayout(p);
  cur = saved;
}
/* 无分层的自由图（方框＋连线的流程图等）：框按文字定统一尺寸（不放大），
   按原图的行、列聚类对齐，相近的行距／列距取齐，标题居中置顶，说明框跟随到底部 */
const median = a => { if (!a.length) return 0; const b = a.slice().sort((x, y) => x - y), m = b.length >> 1; return b.length % 2 ? b[m] : (b[m - 1] + b[m]) / 2; };
function tidyItems(items, p) {
  if (items.length < 2) return;
  const leaves = items.filter(n => !isCont(n) && n.type !== 'equip');
  if (leaves.length) {
    const W = snapv(clamp(Math.max(...leaves.map(k => { const size = k.size || 13; return Math.max(0, ...String(k.text || '').split('\n').map(t => measure(t, size, k.bold))) * (SHAPED_K.has(k.type) ? 1.35 : 1) + 36 + (k.icon ? 30 : 0); })), 120, 220));
    const H = Math.max(40, ...leaves.map(k => leafH(k, W)));
    for (const k of leaves) { const cx = k.x + k.w / 2, cy = k.y + k.h / 2; k.w = W; k.h = snapv(H); k.x = cx - W / 2; k.y = cy - k.h / 2; }
  }
  const ids = new Set(items.map(n => n.id));
  const inLinks = p.links.filter(l => ids.has(l.from) && ids.has(l.to));
  const cluster = (key, size) => {
    const arr = items.slice().sort((a, b) => key(a) - key(b)), out = [];
    for (const n of arr) { const g = out[out.length - 1]; if (g && key(n) - g.c <= Math.max(16, 0.45 * Math.min(size(n), g.s))) { g.items.push(n); g.c = g.items.reduce((t, m) => t + key(m), 0) / g.items.length; g.s = Math.max(g.s, size(n)); } else out.push({ items: [n], c: key(n), s: size(n) }); }
    return out;
  };
  const rows = cluster(n => n.y + n.h / 2, n => n.h), cols = cluster(n => n.x + n.w / 2, n => n.w);
  const vLinks = inLinks.some(l => { const a = nodeById(l.from, p), b = nodeById(l.to, p); return a && b && Math.abs((a.y + a.h / 2) - (b.y + b.h / 2)) > 20; });
  if (rows.length > 1) {
    const d = []; for (let i = 1; i < rows.length; i++) d.push(rows[i].c - rows[i - 1].c);
    const m = median(d), minGap = vLinks ? 48 : 28; let c = rows[0].c;
    for (let i = 1; i < rows.length; i++) { let di = Math.abs(d[i - 1] - m) <= 0.3 * m ? m : d[i - 1]; di = Math.max(di, (rows[i - 1].s + rows[i].s) / 2 + minGap); c += di; rows[i].c = c; }
  }
  const move = (n, dx, dy) => { for (const d of [n, ...descendants(n.id, p)]) { d.x += dx; d.y += dy; } };
  for (const r of rows) for (const n of r.items) move(n, 0, snapv(r.c - n.h / 2) - n.y);
  /* 列只做对齐（同列中心取齐），不强行拉开；行内再保证最小间距 */
  for (const c of cols) for (const n of c.items) move(n, snapv(c.c - n.w / 2) - n.x, 0);
  const hg = inLinks.length ? 48 : 24;
  for (const r of rows) { const a = r.items.slice().sort((m, n) => m.x - n.x); for (let i = 1; i < a.length; i++) { const need = a[i - 1].x + a[i - 1].w + hg - a[i].x; if (need > 0) move(a[i], snapv(need), 0); } }
  /* 跨行相连的两个框：列位置接近时把下方的框对正到上方框的中线下，连线成为一条从边中点出发的直线 */
  const rowOf = new Map(), locked = new Set(); rows.forEach((r, i) => r.items.forEach(n => rowOf.set(n.id, i)));
  for (let pass = 0; pass < 2; pass++) for (const l of inLinks) {
    let a = nodeById(l.from, p), b = nodeById(l.to, p); if (!a || !b) continue;
    const ra = rowOf.get(a.id), rb = rowOf.get(b.id); if (ra === rb) continue;
    if (ra > rb) [a, b] = [b, a];
    const dx = (a.x + a.w / 2) - (b.x + b.w / 2); if (Math.abs(dx) < 1) { locked.add(a.id); locked.add(b.id); continue; } if (Math.abs(dx) > Math.max(a.w, b.w) * 1.25) continue;
    const row = rows[rowOf.get(b.id)].items.filter(n => n !== b), nx = b.x + dx;
    if (row.some(n => nx < n.x + n.w + hg && nx + b.w + hg > n.x)) {
      /* 让位：同行挡路的框（未被对正锁定的）顺势推开 */
      const dir = Math.sign(dx), side = row.filter(n => dir > 0 ? n.x > b.x : n.x < b.x).sort((m, n) => dir * (m.x - n.x));
      let edge = dir > 0 ? nx + b.w + hg : nx - hg, ok = true; const plan = [];
      for (const n of side) {
        const need = dir > 0 ? edge - n.x : n.x + n.w - edge; if (need <= 0) break;
        if (locked.has(n.id)) { ok = false; break; }
        plan.push([n, dir * need]); edge = dir > 0 ? n.x + dir * need + n.w + hg : n.x - need - hg;
      }
      if (!ok) continue;
      for (const [n, d] of plan) move(n, snapv(d), 0);
    }
    move(b, snapv(dx), 0); locked.add(b.id); locked.add(a.id);
  }
  /* 夹在两个对正框之间的其余框：等间距分布 */
  for (const r of rows) {
    const a = r.items.slice().sort((m, n) => m.x - n.x);
    let i = 0;
    while (i < a.length) {
      if (locked.has(a[i].id)) { i++; continue; }
      let j = i; while (j < a.length && !locked.has(a[j].id)) j++;
      const L = a[i - 1], R = a[j];
      if (L && R) {
        const run = a.slice(i, j), tot = run.reduce((t, n) => t + n.w, 0), gap = (R.x - (L.x + L.w) - tot) / (run.length + 1);
        if (gap >= hg * 0.6) { let x = L.x + L.w + gap; for (const n of run) { move(n, snapv(x) - n.x, 0); x += n.w + gap; } }
      }
      i = j;
    }
  }
}
function tidyFree(p) {
  const isItem = n => !n.parent && !['text', 'note', 'legend', 'tblock', 'band'].includes(n.type) && !n.role;
  const items = p.nodes.filter(isItem); if (!items.length) return;
  /* 顶层子容器内有连线的（框＋箭头的流程图被外框包住）：内部按同样规则对齐，外框随内容收拢 */
  for (const g of items.filter(n => n.type === 'group')) {
    const ks = kids(g.id, p); if (ks.length < 2 || ks.some(isCont)) continue;
    const ids = new Set(ks.map(k => k.id)); if (!p.links.some(l => ids.has(l.from) && ids.has(l.to))) continue;
    tidyItems(ks, p);
    const x0 = Math.min(...ks.map(k => k.x)), y0 = Math.min(...ks.map(k => k.y)), x1 = Math.max(...ks.map(k => k.x + k.w)), y1 = Math.max(...ks.map(k => k.y + k.h));
    const tw = measure(String(g.text || '').split('\n')[0], 12.5, true) + 24, W = Math.max(tw, x1 - x0 + 48);
    g.x = snapv((x0 + x1) / 2 - W / 2); g.w = snapv(W); g.y = snapv(y0 - GROUP_TH - 20); g.h = snapv(y1 - g.y + 20);
  }
  tidyItems(items, p);
  /* 标题、副标题、说明框 */
  const x0 = Math.min(...items.map(n => n.x)), x1 = Math.max(...items.map(n => n.x + n.w)), y0 = Math.min(...items.map(n => n.y)), y1 = Math.max(...items.map(n => n.y + n.h)), cx = (x0 + x1) / 2;
  const title = p.nodes.find(n => !n.parent && n.role === 'title'), sub = p.nodes.find(n => !n.parent && n.role === 'subtitle');
  let ty = y0 - 24;
  if (sub) { sub.w = Math.max(sub.w, measure(sub.text, sub.size || 13, sub.bold) + 20); sub.x = snapv(cx - sub.w / 2); sub.y = snapv(ty - sub.h); ty = sub.y - 4; }
  if (title) { title.w = Math.max(title.w, measure(title.text, title.size || 22, true) + 24); title.x = snapv(cx - title.w / 2); title.y = snapv(ty - title.h); }
  for (const n of p.nodes) if (!n.parent && (n.type === 'note' || n.type === 'legend') && n.y > y0) { n.y = Math.max(n.y, snapv(y1 + 20)); }
}
/* 层整体变矮／变高后，原来位于层下方的其它顶层元素（说明、图片等）跟着上移／下移，并保持相对位置 */
function shiftBelow(p, free, oldBottom, newBottom, skip) {
  if (oldBottom == null) return;
  const dy = snapv(newBottom - oldBottom); if (!dy) return;
  for (const n of p.nodes) {
    if (n.parent || n.type === 'band' || skip.includes(n)) continue;
    if (n.y >= oldBottom - 4) { for (const d of [n, ...descendants(n.id, p)]) d.y += dy; }
  }
}
function alignSel(mode) {
  const ns = [...sel].map(id => nodeById(id)).filter(Boolean); if (ns.length < 2) return;
  checkpoint();
  const moveTo = (n, x, y) => { const dx = snapv(x) - n.x, dy = snapv(y) - n.y; for (const d of [n, ...descendants(n.id)]) { d.x += dx; d.y += dy; } };
  const minx = Math.min(...ns.map(n => n.x)), maxx = Math.max(...ns.map(n => n.x + n.w)), miny = Math.min(...ns.map(n => n.y)), maxy = Math.max(...ns.map(n => n.y + n.h));
  if (mode === 'l') ns.forEach(n => moveTo(n, minx, n.y));
  if (mode === 'c') ns.forEach(n => moveTo(n, (minx + maxx) / 2 - n.w / 2, n.y));
  if (mode === 'r') ns.forEach(n => moveTo(n, maxx - n.w, n.y));
  if (mode === 't') ns.forEach(n => moveTo(n, n.x, miny));
  if (mode === 'm') ns.forEach(n => moveTo(n, n.x, (miny + maxy) / 2 - n.h / 2));
  if (mode === 'b') ns.forEach(n => moveTo(n, n.x, maxy - n.h));
  if (mode === 'dh') { ns.sort((a, b) => a.x - b.x); const tot = ns.reduce((s, n) => s + n.w, 0), g = (maxx - minx - tot) / (ns.length - 1); let x = minx; ns.forEach(n => { moveTo(n, x, n.y); x += n.w + g; }); }
  if (mode === 'dv') { ns.sort((a, b) => a.y - b.y); const tot = ns.reduce((s, n) => s + n.h, 0), g = (maxy - miny - tot) / (ns.length - 1); let y = miny; ns.forEach(n => { moveTo(n, n.x, y); y += n.h + g; }); }
  if (mode === 'size') { const w = ns[0].w, h = ns[0].h; ns.forEach(n => { n.w = w; n.h = h; }); }
  render();
}

/* ---------- palette ---------- */
const SHAPES0 = [
  { k: 'rect', name: '矩形', spec: { type: 'rect', w: 120, h: 40, text: '矩形' }, svg: '<rect x="4" y="6" width="30" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/>' },
  { k: 'round', name: '圆角矩形', spec: { type: 'round', w: 120, h: 40, text: '圆角矩形' }, svg: '<rect x="4" y="6" width="30" height="18" rx="7" fill="none" stroke="currentColor" stroke-width="1.6"/>' },
  { k: 'square', name: '方形', spec: { type: 'rect', w: 64, h: 64, text: '方形' }, svg: '<rect x="10" y="4" width="22" height="22" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/>' },
  { k: 'circle', name: '圆形', spec: { type: 'ellipse', w: 64, h: 64, text: '圆形' }, svg: '<circle cx="21" cy="15" r="11" fill="none" stroke="currentColor" stroke-width="1.6"/>' },
  { k: 'ellipse', name: '椭圆', spec: { type: 'ellipse', w: 120, h: 48, text: '椭圆' }, svg: '<ellipse cx="21" cy="15" rx="16" ry="9" fill="none" stroke="currentColor" stroke-width="1.6"/>' },
  { k: 'diamond', name: '菱形', spec: { type: 'diamond', w: 110, h: 64, text: '判断' }, svg: '<polygon points="21,3 37,15 21,27 5,15" fill="none" stroke="currentColor" stroke-width="1.6"/>' },
  { k: 'text', name: '文字', spec: { type: 'text', w: 160, h: 30, text: '文字', size: 16 }, svg: '<text x="21" y="21" text-anchor="middle" font-size="16" font-weight="700" fill="currentColor">T</text>' },
  { k: 'note', name: '说明框', spec: { type: 'note', w: 320, h: 56, text: '说明：', size: 12 }, svg: '<rect x="4" y="6" width="30" height="18" rx="1" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M8 12h20M8 17h14" stroke="currentColor" stroke-width="1.4"/>' },
  { k: 'legend', name: '图例', spec: { type: 'legend', w: 200, h: 60 }, svg: '<rect x="4" y="5" width="9" height="7" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M16 9h18M4 20h9M16 20h18" stroke="currentColor" stroke-width="1.4"/>' },
];
const shThumb = (type, w, h) => { const x = (42 - w) / 2, y = (30 - h) / 2; return shapeMarkup(type, x, y, w, h, 'none', 'currentColor', 1.4).replace(/fill="#000"/g, 'fill="currentColor"'); };
const SH = (k, w, h, tw, th, text, grp) => ({ k, name: SHP_DEF[k].name, grp, spec: { type: k, w, h, text: text ?? SHP_DEF[k].name.replace(/（.*）/, '') }, svg: shThumb(k, tw, th) });
const SHAPES = SHAPES0.map(s => Object.assign(s, { grp: '基础形状' })).slice(0, 6).concat([
  SH('roundL', 120, 40, 32, 18, null, '基础形状'), SH('roundR', 120, 40, 32, 18, null, '基础形状'),
  SH('hexagon', 120, 56, 32, 20, null, '基础形状'), SH('octagon', 72, 72, 22, 22, null, '基础形状'), SH('triangle', 88, 72, 26, 22, null, '基础形状'),
  SH('parallelogram', 130, 48, 34, 18, null, '基础形状'), SH('trapezoid', 120, 52, 32, 18, null, '基础形状'), SH('pentagon', 80, 76, 24, 23, null, '基础形状'),
  SH('star', 80, 76, 24, 23, '', '基础形状'), SH('cylinder', 88, 84, 22, 24, '数据库', '基础形状'), SH('cloud', 130, 80, 34, 22, null, '基础形状'),
  SH('cube', 96, 80, 26, 22, null, '基础形状'), SH('plus', 64, 64, 22, 22, '', '基础形状'), SH('donut', 72, 72, 22, 22, '', '基础形状'), SH('frame', 140, 70, 32, 20, null, '基础形状'),
], SHAPES0.slice(6).map(s => Object.assign(s, { grp: '流程与标注' })), [
  SH('document', 120, 60, 30, 22, null, '流程与标注'), SH('predef', 130, 48, 34, 18, null, '流程与标注'), SH('display', 130, 52, 34, 18, null, '流程与标注'),
  SH('delay', 110, 52, 30, 18, null, '流程与标注'), SH('terminator', 120, 44, 34, 16, '开始', '流程与标注'), SH('callout', 140, 56, 32, 16, '标注说明', '流程与标注'),
  SH('arrowR', 120, 52, 34, 18, '', '箭头'), SH('arrowL', 120, 52, 34, 18, '', '箭头'), SH('arrowU', 56, 100, 16, 26, '', '箭头'), SH('arrowD', 56, 100, 16, 26, '', '箭头'),
  SH('arrowLR', 140, 52, 36, 18, '', '箭头'), SH('arrowUD', 56, 110, 16, 26, '', '箭头'), SH('chevron', 120, 48, 32, 18, '阶段', '箭头'), SH('homeplate', 120, 48, 32, 18, '阶段', '箭头'),
]);
const CONTS = [
  { k: 'band', name: '分组带', spec: { type: 'band', w: 1000, h: 180, text: '分组' }, svg: '<rect x="3" y="5" width="36" height="22" fill="none" stroke="currentColor" stroke-width="1.4"/><rect x="3" y="5" width="7" height="22" fill="currentColor"/>' },
  { k: 'lane', name: '层（泳道）', spec: { type: 'lane', w: 900, h: 56, text: '新的一层' }, svg: '<rect x="3" y="9" width="36" height="13" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M13 9v13" stroke="currentColor" stroke-width="1.2"/>' },
  { k: 'group', name: '子容器', spec: { type: 'group', w: 360, h: 110, text: '子系统' }, svg: '<rect x="5" y="5" width="32" height="22" rx="3" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M5 11h32" stroke="currentColor" stroke-width="1.4"/>' },
];
function pitem(label, payload, inner, isImg) {
  return `<div class="pitem" draggable="true" data-add='${esc(JSON.stringify(payload))}' title="拖到画布，或点击添加">${isImg ? `<img src="${inner}" alt="">` : `<svg viewBox="0 0 42 30">${inner}</svg>`}<span>${esc(label)}</span></div>`;
}
/* palette / picker categories: ICON_LIB cat + overrides; ICON_ALSO lists an icon in extra sections */
const PAL_ORDER = ['基础形状', '流程与标注', '箭头', '容器与层级', '无人', '反无人', '空中', '海上', '陆地', '人员', '感知通信', '指控信息', '设施'];
const MS_SEC = '军标（北约体制，可切换我军配色）', CU_SEC = '自定义图标';
const ICON_CAT_OVERRIDE = {};
'uav_fixed uav_male uav_quad uav_vtol loitering usv uuv ugv robodog uav_heli hale_uav swarm target_drone glider ugv_tracked eod_robot usv_mother'.split(' ').forEach(k => ICON_CAT_OVERRIDE[k] = '无人');
'cuas laser_weapon hpm jammer rf_detector'.split(' ').forEach(k => ICON_CAT_OVERRIDE[k] = '反无人');
'operator soldier'.split(' ').forEach(k => ICON_CAT_OVERRIDE[k] = '人员');
const ICON_ALSO = { eo_turret: ['反无人'], acoustic: ['反无人'], radar: ['反无人'], phased_radar: ['反无人'], ir_sensor: ['反无人'] };
const iconCats = i => [ICON_CAT_OVERRIDE[i.key] || i.cat, ...(ICON_ALSO[i.key] || [])].filter((c, k, a) => a.indexOf(c) === k);
function iconSections() {
  const m = new Map(); for (const i of ICONS) for (const c of iconCats(i)) { if (!m.has(c)) m.set(c, []); m.get(c).push(i); }
  return PAL_ORDER.filter(c => m.has(c)).concat([...m.keys()].filter(c => !PAL_ORDER.includes(c))).map(c => [c, m.get(c)]);
}
const openSecs = new Set(['基础形状', '无人']);
function iconPlaceSpec(icon, name, w, h) {
  return { type: 'equip', w: w, h: h, text: name, icon: icon };
}
function renderPalette() {
  const q = ($('#pal-q')?.value || '').trim();
  let h = `<input class="search" id="pal-q" type="text" placeholder="搜索元素：舰、雷达、无人机…" value="${esc(q)}">`;
  const sec = (title, items, extra = []) => {
    if (!items.length && !extra.length) return ''; const c = !openSecs.has(title) && !q;
    return `<div class="psec${c ? '' : ' open'}"><h4 data-sec="${esc(title)}"><span>${esc(title)}</span><span class="cnt">${items.length}<i>${c ? '▸' : '▾'}</i></span></h4>${c ? '' : `<div class="pgrid">${items.concat(extra).join('')}</div>`}</div>`;
  };
  const m = s => !q || s.includes(q);
  for (const g of ['基础形状', '流程与标注', '箭头']) h += sec(g, SHAPES.filter(s => s.grp === g && (m(s.name) || m(g))).map(s => pitem(s.name, s.spec, s.svg)));
  h += sec('容器与层级', CONTS.filter(s => m(s.name)).map(s => pitem(s.name, s.spec, s.svg)));
  for (const [c, list] of iconSections()) h += sec(c, list.filter(i => m(i.name) || m(c)).map(i => pitem(i.name, iconPlaceSpec('lib:' + i.key, i.name, 96, 96), iconURI('lib:' + i.key), true)));
  if (window.ms) h += sec(MS_SEC, MS_LIST.filter(x => m(x[1]) || m('军标') || m(x[2] || '')).map(x => pitem(x[1], iconPlaceSpec('ms:' + x[0], x[1], 96, 92), iconURI('ms:' + x[0]), true)));
  const cu = Object.entries(doc.custom).filter(([, v]) => m(v.name));
  h += sec(CU_SEC, cu.map(([id, v]) => pitem(v.name, iconPlaceSpec('cu:' + id, v.name, 96, 96), v.uri, true)), q ? [] : [`<button class="pitem" id="pal-form" draggable="false" style="cursor:pointer"><svg viewBox="0 0 42 30"><path d="M21 5l4 4h-8zM11 15l4 4H7zM31 15l4 4h-8zM21 21l4 4h-8z" fill="currentColor"/></svg><span>新建编队</span></button>`, `<button class="pitem" id="pal-up" draggable="false" style="cursor:pointer"><svg viewBox="0 0 42 30"><path d="M21 6v18M12 15h18" stroke="currentColor" stroke-width="2"/></svg><span>上传图标</span></button>`]);
  $('#palette').innerHTML = h;
  const qi = $('#pal-q'); qi.oninput = () => { const pos = qi.selectionStart; renderPalette(); const n = $('#pal-q'); n.focus(); n.setSelectionRange(pos, pos); };
  const pf = $('#pal-form'); if (pf) pf.onclick = () => window.Combo ? Combo.open(null) : toast('复合图标模块未加载');
  const up = $('#pal-up'); if (up) up.onclick = () => { iconTarget = null; $('#f-icon').click(); };
}
$('#palette').addEventListener('click', e => {
  const h = e.target.closest('h4[data-sec]'); if (h) { const s = h.dataset.sec; openSecs.has(s) ? openSecs.delete(s) : openSecs.add(s); renderPalette(); return; }
  const it = e.target.closest('.pitem[data-add]'); if (!it) return;
  const r = svg.getBoundingClientRect(); const c = clientToWorld(r.left + r.width / 2, r.top + r.height / 2);
  addNode(JSON.parse(it.dataset.add), c.x + (Math.random() * 40 - 20), c.y + (Math.random() * 40 - 20));
});
$('#palette').addEventListener('dragstart', e => { const it = e.target.closest('.pitem[data-add]'); if (it) { e.dataTransfer.setData('text/plain', it.dataset.add); e.dataTransfer.effectAllowed = 'copy'; } });
stage.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
stage.addEventListener('drop', e => {
  e.preventDefault(); let spec; try { spec = JSON.parse(e.dataTransfer.getData('text/plain')); } catch (_) { return; }
  const w = clientToWorld(e.clientX, e.clientY); addNode(spec, w.x, w.y);
});
function addNode(spec, wx, wy) {
  checkpoint();
  const n = mkNode({ ...spec, size: spec.size || (spec.type === 'equip' ? 12 : 13) });
  n.x = snapv(wx - n.w / 2); n.y = snapv(wy - n.h / 2);
  P().nodes.push(n); n.parent = findParent(n);
  selectNodes([n.id]); render();
}

/* ---------- 拖动磁吸：对齐其他图形的边／中线、画布中轴、父容器中线，等间距提示 ---------- */
function snapOn() { try { return localStorage.getItem('hongtu.snap') !== 'off'; } catch (_) { return true; } }
function snapContext(moving) {
  const p = P(), ids = new Set(moving.keys());
  const top = [...moving.values()].filter(n => !moving.has(n.parent));
  if (!top.length) return null;
  const bx0 = Math.min(...top.map(n => n.x)), by0 = Math.min(...top.map(n => n.y)), bx1 = Math.max(...top.map(n => n.x + n.w)), by1 = Math.max(...top.map(n => n.y + n.h));
  const rects = p.nodes.filter(n => !ids.has(n.id) && n.type !== 'legend' && n.type !== 'tblock');
  const others = rects.length ? rects : [];
  let axis = null;
  if (others.length) { const x0 = Math.min(...others.map(n => n.x)), y0 = Math.min(...others.map(n => n.y)), x1 = Math.max(...others.map(n => n.x + n.w)), y1 = Math.max(...others.map(n => n.y + n.h)); axis = { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }; }
  const par = top.every(n => n.parent && n.parent === top[0].parent) ? nodeById(top[0].parent) : null;
  /* 同一容器内或同为顶层的兄弟元素用于等间距 */
  const sib = rects.filter(n => !isCont(n) || n.parent === (top[0].parent || null)).filter(n => (n.parent || null) === (top[0].parent || null));
  return { box: { x: bx0, y: by0, w: bx1 - bx0, h: by1 - by0 }, rects: others.filter(n => !(isCont(n) && top.some(t => isAncOf(n, t)))), axis, par, sib };
}
function isAncOf(c, n) { let q = n.parent ? nodeById(n.parent) : null, g = 0; while (q && g++ < 30) { if (q === c) return true; q = q.parent ? nodeById(q.parent) : null; } return false; }
const vGuide = (x, a, b) => ({ k: 'v', x, y0: Math.min(a.y, b.y) - 6, y1: Math.max(a.y + a.h, b.y + b.h) + 6 });
const hGuide = (y, a, b) => ({ k: 'h', y, x0: Math.min(a.x, b.x) - 6, x1: Math.max(a.x + a.w, b.x + b.w) + 6 });
function magnet(sc, dx, dy) {
  const T = 7 / view.k, b = sc.box, G = [];
  const mv = { x: b.x + dx, y: b.y + dy, w: b.w, h: b.h };
  const solve = horiz => {
    const pos = horiz ? mv.x : mv.y, len = horiz ? mv.w : mv.h;
    const mine = [0, len / 2, len];
    let best = null;
    const tryC = (target, off, info) => { const dd = Math.abs(target - (pos + off)); if (dd <= T && (!best || dd < best.d - 0.01 || (Math.abs(dd - best.d) < 0.01 && info.pri > best.info.pri))) best = { d: dd, shift: target - (pos + off), info }; };
    for (const r of sc.rects) {
      const rs = horiz ? [r.x, r.x + r.w / 2, r.x + r.w] : [r.y, r.y + r.h / 2, r.y + r.h];
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) tryC(rs[i], mine[j], { t: 'edge', r, v: rs[i], pri: i === 1 && j === 1 ? 2 : 1 });
    }
    if (sc.par) { const c = horiz ? sc.par.x + sc.par.w / 2 : sc.par.y + sc.par.h / 2; tryC(c, len / 2, { t: 'axis', v: c, r: sc.par, pri: 3 }); }
    if (sc.axis) { const c = horiz ? sc.axis.x + sc.axis.w / 2 : sc.axis.y + sc.axis.h / 2; tryC(c, len / 2, { t: 'axis', v: c, r: sc.axis, pri: 3 }); }
    /* 等间距：与同一行（列）左右邻居间距相等，或与邻居之间已有的间距相等 */
    const over = r => horiz ? (r.y < mv.y + mv.h && r.y + r.h > mv.y) : (r.x < mv.x + mv.w && r.x + r.w > mv.x);
    const lo = r => horiz ? r.x : r.y, hi = r => horiz ? r.x + r.w : r.y + r.h;
    const row = sc.sib.filter(over);
    const L = row.filter(r => hi(r) <= pos + T * 4).sort((u, v) => hi(v) - hi(u))[0], R = row.filter(r => lo(r) >= pos + len - T * 4).sort((u, v) => lo(u) - lo(v))[0];
    if (L && R) { const t = (hi(L) + lo(R) - len) / 2; if (t > hi(L)) tryC(t, 0, { t: 'gap', a: L, b: R, pri: 2 }); }
    if (L) { const LL = row.filter(r => r !== L && hi(r) <= lo(L) + 1).sort((u, v) => hi(v) - hi(u))[0]; if (LL) { const g = lo(L) - hi(LL); tryC(hi(L) + g, 0, { t: 'gap', a: L, ref: [LL, L], pri: 1 }); } }
    if (R) { const RR = row.filter(r => r !== R && lo(r) >= hi(R) - 1).sort((u, v) => lo(u) - lo(v))[0]; if (RR) { const g = lo(RR) - hi(R); tryC(lo(R) - g - len, 0, { t: 'gap', b: R, ref: [R, RR], pri: 1 }); } }
    return best;
  };
  const bx = solve(true), by = solve(false);
  const ox = bx ? bx.shift : snapv(mv.x) - mv.x, oy = by ? by.shift : snapv(mv.y) - mv.y;
  const fin = { x: mv.x + ox, y: mv.y + oy, w: mv.w, h: mv.h };
  const mark = (info, horiz) => {
    if (info.t === 'gap') {
      const cy = horiz ? fin.y + fin.h / 2 : null, cx = horiz ? null : fin.x + fin.w / 2;
      const segs = [];
      const add = (u, v) => segs.push(horiz ? { k: 'gh', x0: u.x + u.w, x1: v.x, y: Math.max(u.y, v.y, fin.y) + (Math.min(u.y + u.h, v.y + v.h, fin.y + fin.h) - Math.max(u.y, v.y, fin.y)) / 2 } : { k: 'gv', y0: u.y + u.h, y1: v.y, x: Math.max(u.x, v.x, fin.x) + (Math.min(u.x + u.w, v.x + v.w, fin.x + fin.w) - Math.max(u.x, v.x, fin.x)) / 2 });
      if (info.a) add(info.a, fin); if (info.b) add(fin, info.b); if (info.ref) add(info.ref[0], info.ref[1]);
      G.push(...segs); return;
    }
    if (info.t === 'axis') { G.push(horiz ? { k: 'v', x: info.v, y0: Math.min(info.r.y, fin.y) - 10, y1: Math.max(info.r.y + info.r.h, fin.y + fin.h) + 10, axis: true } : { k: 'h', y: info.v, x0: Math.min(info.r.x, fin.x) - 10, x1: Math.max(info.r.x + info.r.w, fin.x + fin.w) + 10, axis: true }); return; }
    G.push(horiz ? vGuide(info.v, fin, info.r) : hGuide(info.v, fin, info.r));
  };
  if (bx) mark(bx.info, true); if (by) mark(by.info, false);
  return { dx: Math.round((dx + ox) * 2) / 2, dy: Math.round((dy + oy) * 2) / 2, guides: G };
}
function guidesSVG() {
  if (!ui.guides || !ui.guides.length) return '';
  const C = '#E5397E', w = 1.1 / view.k, a = 4 / view.k;
  return ui.guides.map(g => {
    if (g.k === 'v') return `<line x1="${g.x}" y1="${g.y0}" x2="${g.x}" y2="${g.y1}" stroke="${C}" stroke-width="${w}" ${g.axis ? `stroke-dasharray="${6 / view.k} ${4 / view.k}"` : ''} pointer-events="none"/>`;
    if (g.k === 'h') return `<line x1="${g.x0}" y1="${g.y}" x2="${g.x1}" y2="${g.y}" stroke="${C}" stroke-width="${w}" ${g.axis ? `stroke-dasharray="${6 / view.k} ${4 / view.k}"` : ''} pointer-events="none"/>`;
    if (g.k === 'gh') return `<path d="M${g.x0},${g.y} H${g.x1} M${g.x0},${g.y - a} v${2 * a} M${g.x1},${g.y - a} v${2 * a}" stroke="${C}" stroke-width="${w}" fill="none" pointer-events="none"/>`;
    if (g.k === 'gv') return `<path d="M${g.x},${g.y0} V${g.y1} M${g.x - a},${g.y0} h${2 * a} M${g.x - a},${g.y1} h${2 * a}" stroke="${C}" stroke-width="${w}" fill="none" pointer-events="none"/>`;
    return '';
  }).join('');
}
function hitTarget(el) {
  if (!el || !el.closest) return null;
  const lk = el.closest('[data-link]');
  if (lk && lk.dataset.link) return { kind: 'link', id: lk.dataset.link };
  const nd = el.closest('[data-id]');
  if (nd && nd.dataset.id) return { kind: 'node', id: nd.dataset.id };
  return null;
}
function ensureCtx() {
  let m = document.getElementById('ctx');
  if (m) return m;
  m = document.createElement('div');
  m.id = 'ctx';
  m.innerHTML = '<button type="button" id="ctx-same">选中同类</button>';
  document.body.appendChild(m);
  m.querySelector('#ctx-same').addEventListener('click', () => {
    const hit = m._hit;
    m.style.display = 'none';
    if (hit) selectSame(hit);
  });
  return m;
}
function openSameMenu(hit, x, y) {
  const keep = hit.kind === 'node' ? sel.has(hit.id) && sel.size > 1 : linkSel.has(hit.id) && linkSel.size > 1;
  if (!keep) {
    if (hit.kind === 'node') selectNodes([hit.id]);
    else selectLinks([hit.id]);
  }
  const m = ensureCtx();
  m._hit = hit;
  m.style.left = x + 'px';
  m.style.top = y + 'px';
  m.style.display = 'block';
  render();
}
function selectSame(anchor) {
  const page = P();
  if (!anchor) {
    if (sel.size === 1 && !linkSel.size) anchor = { kind: 'node', id: [...sel][0] };
    else if (onlyLinkId()) anchor = { kind: 'link', id: onlyLinkId() };
    else { toast('请先选中一个元素或一条连线'); return; }
  }
  if (anchor.kind === 'node') {
    const n = nodeById(anchor.id, page);
    if (!n) return;
    const ids = n.icon ? page.nodes.filter(x => x.icon === n.icon).map(x => x.id) : page.nodes.filter(x => x.type === n.type).map(x => x.id);
    selectNodes(ids);
  } else {
    const l = page.links.find(x => x.id === anchor.id);
    if (!l) return;
    selectLinks(page.links.filter(x => x.kind === l.kind).map(x => x.id));
  }
  render();
}
/* ---------- pointer interaction ---------- */
let spaceDown = false;
let ui_drag = null;
Object.defineProperty(ui, 'drag', { get: () => ui_drag });
svg.addEventListener('pointerdown', e => {
  if ($('#editor').style.display === 'block') commitEdit();
  closeMenus();
  const w = clientToWorld(e.clientX, e.clientY), t = e.target;
  svg.setPointerCapture(e.pointerId);
  const enter = t.closest && t.closest('[data-enter]');
  if (enter) { enterSub(enter.dataset.enter); return; }
  /* own double-click detection: the canvas re-renders on pointerdown, so native dblclick never fires */
  {
    const hitEl = t.closest && (t.closest('[data-link]') || t.closest('[data-id]'));
    const hitKey = hitEl ? (hitEl.dataset.link ? 'L' + hitEl.dataset.link : 'N' + hitEl.dataset.id) : null;
    const nowT = performance.now(), last = window.__lastDown;
    window.__lastDown = { k: hitKey, t: nowT, x: e.clientX, y: e.clientY };
    if (hitKey && e.button === 0 && last && last.k === hitKey && nowT - last.t < 420 && Math.hypot(e.clientX - last.x, e.clientY - last.y) < 6) {
      window.__lastDown = null; ui_drag = null;
      if (hitKey[0] === 'L') { const id = hitKey.slice(1); noteLinkHit(id, e.clientX, e.clientY); selectLinks([id]); focusLinkCaption(P().links.find(x => x.id === id)); }
      else { const n = nodeById(hitKey.slice(1)); if (n && n.type !== 'legend' && n.type !== 'tblock') { selectNodes([n.id]); render(); setTimeout(() => startEdit(n), 0); } }
      return;
    }
  }
  if (e.button === 2) { const hit = hitTarget(t); if (hit) { openSameMenu(hit, e.clientX, e.clientY); return; } }
  if (e.button === 1 || spaceDown || e.button === 2) { ui_drag = { mode: 'pan', sx: e.clientX, sy: e.clientY, vx: view.x, vy: view.y }; return; }
  if (t.dataset.h) { const n = nodeById([...sel][0]); ui_drag = { mode: 'resize', h: t.dataset.h, n, o: { ...n }, w0: w, snap: snapshot(), moved: false, kidsO: descendants(n.id).map(d => ({ d, x: d.x, y: d.y })) }; return; }
  if (t.dataset.port) { const n = nodeById(t.dataset.port); ui_drag = { mode: 'link', from: n.id }; ui.temp = { x0: n.x + n.w / 2, y0: n.y + n.h / 2, x1: w.x, y1: w.y }; renderOverlay(); toast('拖到目标节点松开完成，Esc 取消'); return; }
  const lk = t.closest && t.closest('[data-link]');
  if (lk) { noteLinkHit(lk.dataset.link, e.clientX, e.clientY); selectLinks([lk.dataset.link]); render(); ui_drag = null; return; }
  const g = t.closest && t.closest('[data-id]');
  if (g) {
    const id = g.dataset.id;
    let ids;
    if (e.shiftKey || e.ctrlKey || e.metaKey) {
      ids = [...sel];
      const at = ids.indexOf(id);
      if (at >= 0) ids.splice(at, 1); else ids.push(id);
    } else if (sel.has(id) && !linkSel.size) ids = [...sel];
    else ids = [id];
    selectNodes(ids);
    const set = new Map();
    for (const sid of sel) { const n = nodeById(sid); if (!n) continue; set.set(n.id, n); for (const d of descendants(n.id)) set.set(d.id, d); }
    ui_drag = { mode: 'move', w0: w, items: [...set.values()].map(n => ({ n, x: n.x, y: n.y })), snap: snapshot(), moved: false };
    ui_drag.sc = snapContext(set);
    render(); return;
  }
  if (e.pointerType === 'touch') { ui_drag = { mode: 'pan', sx: e.clientX, sy: e.clientY, vx: view.x, vy: view.y }; }
  else {
    if (!e.shiftKey) clearSel();
    else if (linkSel.size) selectNodes([...sel]);
    ui_drag = { mode: 'marquee', base: new Set(sel) }; ui.marquee = { x0: w.x, y0: w.y, x1: w.x, y1: w.y };
  }
  render();
});
svg.addEventListener('pointermove', e => {
  const w = clientToWorld(e.clientX, e.clientY);
  if (!ui_drag) {
    const g = e.target.closest && (e.target.closest('[data-id]') || e.target.closest('[data-port]'));
    const id = g ? (g.dataset.id || g.dataset.port) : null;
    const lk = !g && e.target.closest && e.target.closest('[data-link]'); const lid = lk ? lk.dataset.link : null;
    if (lid) noteLinkHit(lid, e.clientX, e.clientY);
    if (id !== hoverId || lid !== hoverLink) { const ch = id !== hoverId; hoverId = id; hoverLink = lid; if (ch) renderOverlay(); applyHover(); }
    return;
  }
  const d = ui_drag;
  if (d.mode === 'pan') { view.x = d.vx - (e.clientX - d.sx) / view.k; view.y = d.vy - (e.clientY - d.sy) / view.k; applyView(); return; }
  if (d.mode === 'move') {
    const dx = w.x - d.w0.x, dy = w.y - d.w0.y; if (!d.moved && Math.hypot(dx, dy) * view.k < 3) return;
    d.moved = true;
    let sx, sy; ui.guides = null;
    if (snapOn() && !e.altKey && d.sc) { const r = magnet(d.sc, dx, dy); sx = r.dx; sy = r.dy; ui.guides = r.guides; }
    else { sx = snapv(dx); sy = snapv(dy); }
    for (const it of d.items) { it.n.x = it.x + sx; it.n.y = it.y + sy; }
    render(false); return;
  }
  if (d.mode === 'resize') {
    const n = d.n, o = d.o, dx = snapv(w.x - d.w0.x), dy = snapv(w.y - d.w0.y); d.moved = true;
    let x = o.x, y = o.y, ww = o.w, hh = o.h;
    if (d.h.includes('e')) ww = o.w + dx; if (d.h.includes('s')) hh = o.h + dy;
    if (d.h.includes('w')) { ww = o.w - dx; x = o.x + dx; } if (d.h.includes('n')) { hh = o.h - dy; y = o.y + dy; }
    if (ww < 24) { if (d.h.includes('w')) x -= 24 - ww; ww = 24; } if (hh < 16) { if (d.h.includes('n')) y -= 16 - hh; hh = 16; }
    ui.guides = null;
    if (snapOn() && !e.altKey) {
      if (!d.sc) d.sc = snapContext(new Map([[n.id, n], ...descendants(n.id).map(q => [q.id, q])]));
      const T = 7 / view.k, G = [], near = (v, list) => { let b = null; for (const c of list) { const dd = Math.abs(c.v - v); if (dd <= T && (!b || dd < b.d)) b = { d: dd, c }; } return b; };
      const xl = d.sc.rects.flatMap(r => [{ v: r.x, r }, { v: r.x + r.w, r }, { v: r.x + r.w / 2, r }]), yl = d.sc.rects.flatMap(r => [{ v: r.y, r }, { v: r.y + r.h, r }, { v: r.y + r.h / 2, r }]);
      if (d.h.includes('e')) { const b = near(x + ww, xl); if (b) { ww = b.c.v - x; G.push(vGuide(b.c.v, { x, y, w: ww, h: hh }, b.c.r)); } }
      if (d.h.includes('w')) { const b = near(x, xl); if (b) { ww += x - b.c.v; x = b.c.v; G.push(vGuide(b.c.v, { x, y, w: ww, h: hh }, b.c.r)); } }
      if (d.h.includes('s')) { const b = near(y + hh, yl); if (b) { hh = b.c.v - y; G.push(hGuide(b.c.v, { x, y, w: ww, h: hh }, b.c.r)); } }
      if (d.h.includes('n')) { const b = near(y, yl); if (b) { hh += y - b.c.v; y = b.c.v; G.push(hGuide(b.c.v, { x, y, w: ww, h: hh }, b.c.r)); } }
      ui.guides = G;
    }
    Object.assign(n, { x, y, w: ww, h: hh }); render(false); return;
  }
  if (d.mode === 'link') { ui.temp.x1 = w.x; ui.temp.y1 = w.y; const el = document.elementFromPoint(e.clientX, e.clientY); const g = el && el.closest && el.closest('[data-id]'); hoverId = g ? g.dataset.id : null; renderOverlay(); return; }
  if (d.mode === 'marquee') {
    const m = ui.marquee; m.x1 = w.x; m.y1 = w.y;
    const x0 = Math.min(m.x0, m.x1), x1 = Math.max(m.x0, m.x1), y0 = Math.min(m.y0, m.y1), y1 = Math.max(m.y0, m.y1);
    const ids = [...d.base];
    for (const n of P().nodes) if (n.x >= x0 && n.y >= y0 && n.x + n.w <= x1 && n.y + n.h <= y1 && ids.indexOf(n.id) < 0) ids.push(n.id);
    selectNodes(ids);
    renderOverlay();
  }
});
function endDrag(e) {
  const d = ui_drag; if (!d) return; ui_drag = null; ui.guides = null;
  if (d.mode === 'move' && d.moved) {
    undoS.push(d.snap); redoS = [];
    const top = d.items.map(i => i.n).filter(n => !d.items.some(o => o.n.id === n.parent));
    for (const n of top) n.parent = findParent(n);
  }
  if (d.mode === 'resize' && d.moved) { undoS.push(d.snap); redoS = []; }
  if (d.mode === 'link') {
    const el = document.elementFromPoint(e.clientX, e.clientY); const g = el && el.closest && el.closest('[data-id]');
    ui.temp = null;
    if (g && g.dataset.id !== d.from && !['tblock', 'legend'].includes(nodeById(g.dataset.id)?.type)) { checkpoint(); const l = { id: uid(), from: d.from, to: g.dataset.id, dir: 'one', kind: doc.lastKind || 'data', route: 'ortho', label: '' }; P().links.push(l); selectLinks([l.id]); }
  }
  if (d.mode === 'marquee') ui.marquee = null;
  render();
}
svg.addEventListener('pointerup', endDrag);
svg.addEventListener('pointercancel', endDrag);
svg.addEventListener('contextmenu', e => e.preventDefault());
svg.addEventListener('wheel', e => {
  e.preventDefault();
  if (e.ctrlKey || e.metaKey) zoomAt(view.k * Math.exp(-e.deltaY * 0.0018), e.clientX, e.clientY);
  else { view.x += (e.shiftKey ? e.deltaY : e.deltaX) / view.k; view.y += (e.shiftKey ? 0 : e.deltaY) / view.k; applyView(); }
}, { passive: false });
svg.addEventListener('dblclick', e => {
  /* pointerdown re-renders the canvas, so the event target may be detached: hit-test again */
  const hit = document.elementFromPoint(e.clientX, e.clientY) || e.target;
  e = { target: (hit && hit.closest) ? hit : e.target, clientX: e.clientX, clientY: e.clientY };
  const lk = e.target.closest('[data-link]'); if (lk) { const l = P().links.find(x => x.id === lk.dataset.link); if (!l) return; noteLinkHit(l.id, e.clientX, e.clientY); selectLinks([l.id]); focusLinkCaption(l); return; }
  const g = e.target.closest('[data-id]'); if (!g) return;
  const n = nodeById(g.dataset.id); if (!n || n.type === 'legend' || n.type === 'tblock') return;
  startEdit(n);
});
/* inline text editor */
let editing = null;
function startEdit(n) {
  if (!n || n.type === 'legend' || n.type === 'tblock') return;
  editing = n; const ed = $('#editor'), r = svg.getBoundingClientRect(), sr = stage.getBoundingClientRect();
  let x = n.x, y = n.y, w = n.w, h = n.h;
  if (n.type === 'band') { w = Math.max(160, BAND_TW); h = 60; }
  if (n.type === 'lane') { w = laneTW(n); }
  if (n.type === 'group') { h = GROUP_TH + 30; }
  Object.assign(ed.style, { display: 'block', left: ((x - view.x) * view.k + r.left - sr.left) + 'px', top: ((y - view.y) * view.k + r.top - sr.top) + 'px', width: Math.max(120, w * view.k) + 'px', height: Math.max(40, h * view.k) + 'px', fontSize: Math.max(12, (n.size || 13) * view.k) + 'px', fontFamily: fontCSS(n) });
  ed.value = n.text || ''; ed.focus(); ed.select();
}
function commitEdit(cancel) {
  const ed = $('#editor'); if (ed.style.display !== 'block') return; ed.style.display = 'none';
  if (editing && !cancel && ed.value !== editing.text) { checkpoint(); editing.text = ed.value; }
  editing = null; render();
}
$('#editor').addEventListener('keydown', e => {
  if (e.key === 'Escape') { e.preventDefault(); commitEdit(true); }
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey || !e.shiftKey && editing && editing.type !== 'note')) { e.preventDefault(); commitEdit(); }
});
$('#editor').addEventListener('blur', () => commitEdit());

/* ---------- keyboard ---------- */
let clipboard = null;
const SHORTCUTS = [
  ['文件', [['Ctrl+O', '打开工程／PPT／Visio'], ['Ctrl+Shift+O', '格式转换（PPT／Visio／draw.io 批量互转）'], ['Ctrl+S', '保存工程'], ['Ctrl+Shift+S', '另存为'], ['Ctrl+E', '打开导出菜单'], ['Ctrl+Shift+P', '导出透明 PNG（2 倍）']]],
  ['编辑', [['Ctrl+Z', '撤销'], ['Ctrl+Y／Ctrl+Shift+Z', '重做'], ['Ctrl+C／Ctrl+V', '复制／粘贴'], ['Ctrl+D', '原位复制一份'], ['Ctrl+A', '全选'], ['Ctrl+Shift+A', '选中同类'], ['Delete', '删除所选'], ['F2／双击', '改文字（连线改正向标签，双向时点靠近的一端）'], ['Ctrl+K', '为所选元素选图标'], ['方向键', '微移（Shift 加大步长）'], ['Alt+拖动', '临时关闭对齐吸附（吸附开关在图面设置）'], ['Esc', '取消正在拖的连线／取消选择／关闭面板']]],
  ['排版与生成', [['Ctrl+Shift+F', '一键美化（按图面设置中的排版：标准／紧凑／报告版心）'], ['Ctrl+Shift+X', '减少交叉'], ['Ctrl+Shift+G', '文字成图'], ['Ctrl+Shift+L', '参照生成（好图 + 新内容 → 同款新图）'], ['Ctrl+Shift+M', '模板']]],
  ['体系结构规范', [['Ctrl+Shift+K', '规范检查（视图类型、编号、属性、标题栏）']]],
  ['复合图标', [['Ctrl+G', '把所选元素组合为一个复合图标'], ['Ctrl+Shift+U', '拆分复合图标'], ['Ctrl+Shift+B', '编队生成器（同型装备按阵型合成）']]],
  ['连线（选中连线时）', LINK_KEYS.map(k => [k.chord, k.label]).concat([['F2／双击', '连线改正向标签，双向时点靠近的一端']])],
  ['视图', [['Ctrl+0', '适配窗口'], ['Ctrl+= ／ Ctrl+-', '放大／缩小'], ['Ctrl+滚轮', '缩放'], ['空格+拖动', '平移画布'], ['F1／?', '快捷键一览']]],
];
function openHelp() {
  const kb = k => k.split(/(\+|／| – | ／ )/).map(t => /^(\+|／| – | ／ )$/.test(t) ? `<span class="ks">${t.trim()}</span>` : `<kbd>${esc(t)}</kbd>`).join('');
  $('#help-body').innerHTML = SHORTCUTS.map(([g, list]) => `<section><h5>${g}</h5>${list.map(([k, d]) => `<div class="kr"><span class="kk">${kb(k)}</span><span>${esc(d)}</span></div>`).join('')}</section>`).join('');
  $('#help').style.display = 'flex';
}
const closeHelp = () => { $('#help').style.display = 'none'; };
function closePanels() { let c = false; for (const id of ['#modal', '#help', '#std-dlg', '#saveas']) { const x = $(id); if (x && x.style.display === 'flex') { x.style.display = 'none'; c = true; } } if (document.querySelector('.menu.open')) { closeMenus(); c = true; } return c; }
const callMod = (fn, nm) => { if (typeof window[fn] === 'function') window[fn](); else toast(nm + '模块未加载'); };
const zoomBy = f => { const r = svg.getBoundingClientRect(); zoomAt(view.k * f, r.left + r.width / 2, r.top + r.height / 2); };
function doBeautify() { checkpoint(); if (window.Compact) Compact.stamp(); beautify(); render(); toast('已按层级对齐、等距排布'); }
function doReduce() { checkpoint(); const [a, b] = reduceCrossings(); render(); toast(b < a ? `交叉 ${a} → ${b}` : `交叉 ${a} → ${b}（已是较优排布）`); }
function iconable(n) { return n && !isCont(n) && !['text', 'note', 'legend', 'tblock'].includes(n.type); }
document.addEventListener('keydown', e => {
  if (document.getElementById('jw-bak')) return;
  const saveas = $('#saveas');
  if (saveas && saveas.style.display === 'flex') {
    if (e.key === 'Escape') { e.preventDefault(); closeSaveAs(); return; }
    if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); confirmSaveAs(); return; }
    if ((e.ctrlKey || e.metaKey) && (e.key || '').toLowerCase() === 's') e.preventDefault();
    return;
  }
  const tag = (document.activeElement?.tagName || '').toLowerCase();
  if (['input', 'textarea', 'select'].includes(tag)) { if (e.key === 'Escape' && document.activeElement.id !== 'editor') { if (!closePanels()) document.activeElement.blur(); } return; }
  const ctrl = e.ctrlKey || e.metaKey, k = (e.key || '').toLowerCase(), sh = e.shiftKey;
  const go = fn => { e.preventDefault(); fn(); };
  if (e.key === 'F1' || (e.key === '?' && !ctrl)) return go(() => $('#help').style.display === 'flex' ? closeHelp() : openHelp());
  if (e.key === 'Escape') {
    if (closePanels()) return;
    if (ui_drag && ui_drag.mode === 'link') { ui_drag = null; ui.temp = null; render(); return; }
    clearSel(); render(); return;
  }
  if ($('#modal').style.display === 'flex' || $('#help').style.display === 'flex') return;
  if (document.getElementById('cb-dlg')?.style.display === 'flex') return;
  if (document.getElementById('std-dlg')?.style.display === 'flex') return;
  if (e.code === 'Space') { spaceDown = true; svg.style.cursor = 'grab'; e.preventDefault(); return; }
  if (ctrl && sh) {
    if (k === 'a') return go(selectSame);
    if (k === 's') return go(saveProjectAs);
    if (k === 'f') return go(doBeautify);
    if (k === 'x') return go(doReduce);
    if (k === 'g') return go(() => callMod('openTextGen', '文字成图'));
    if (k === 'm') return go(() => callMod('openTemplates', '模板'));
    if (k === 'l') return go(() => callMod('openRefGen', '参照生成'));
    if (k === 'o') return go(() => callMod('openConvert', '格式转换'));
    if (k === 'u') return go(() => window.Combo ? Combo.ungroup() : toast('复合图标模块未加载'));
    if (k === 'b') return go(() => window.Combo ? Combo.open(sel.size === 1 ? nodeById([...sel][0]) : null) : toast('复合图标模块未加载'));
    if (k === 'k') return go(() => window.Std ? Std.openCheck() : toast('规范模块未加载'));
    if (k === 'p') return go(() => exportPNG(2, false).catch(err => toast('导出失败：' + (err.message || err))));
    if (k === 'z') return go(redo);
  }
  if (ctrl && !sh) {
    if (k === 'z') return go(undo);
    if (k === 'g') return go(() => window.Combo ? Combo.groupSelection() : toast('复合图标模块未加载'));
    if (k === 'y') return go(redo);
    if (k === 'a') return go(() => { selectNodes(P().nodes.map(n => n.id)); render(); });
    if (k === 'c') return copySel();
    if (k === 'v') return paste();
    if (k === 'd') return go(() => { copySel(); paste(); });
    if (k === 's') return go(saveProject);
    if (k === 'o') return go(() => $('#f-open').click());
    if (k === 'e') return go(() => $('#m-export').classList.toggle('open'));
    if (k === '0' || e.code === 'Digit0' || e.code === 'Numpad0') return go(fit);
    if (k === '=' || k === '+' || e.code === 'NumpadAdd') return go(() => zoomBy(1.2));
    if (k === '-' || k === '_' || e.code === 'NumpadSubtract') return go(() => zoomBy(1 / 1.2));
    if (k === 'k') return go(() => { const n = sel.size === 1 ? nodeById([...sel][0]) : null; if (iconable(n)) openIconPicker(n); else toast('请先选中一个形状或装备卡'); });
  }
  if (ctrl || e.altKey) return;
  if (e.key === 'Delete' || e.key === 'Backspace') return go(deleteSel);
  if (e.key === 'F2') return go(() => {
    if (sel.size === 1) startEdit(nodeById([...sel][0]));
    else if (onlyLinkId()) focusLinkCaption(P().links.find(x => x.id === onlyLinkId()));
  });
  const linkBind = LINK_KEYS.filter(b => b.match(e))[0];
  if (linkBind && linkSel.size) {
    return go(() => {
      const chosen = [];
      linkSel.forEach(id => { const x = P().links.find(q => q.id === id); if (x) chosen.push(x); });
      if (!chosen.length) return;
      if (chosen.length === 1) { checkpoint(); linkBind.apply(chosen[0], e); render(); return; }
      checkpoint();
      applyLinkChord(chosen, linkBind, e);
      render();
    });
  }
  const ar = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
  if (ar && sel.size) {
    e.preventDefault(); checkpoint(); const st = sh ? 20 : GRID; const moved = new Set();
    for (const id of sel) { const n = nodeById(id); for (const d of [n, ...descendants(id)]) if (!moved.has(d.id)) { moved.add(d.id); d.x += ar[0] * st; d.y += ar[1] * st; } }
    render();
  }
});
document.addEventListener('keyup', e => { if (e.code === 'Space') { spaceDown = false; svg.style.cursor = ''; } });

/* ---------- 减少交叉: barycenter reordering of siblings inside lanes / groups / band rows ---------- */
function reduceCrossings(p = P()) {
  const saved = cur; cur = p.id;
  const before = crossingCount(p);
  const snap = () => JSON.stringify(p.nodes);
  beautify(p); let best = crossingCount(p), bestSnap = snap();
  const byId = new Map(p.nodes.map(n => [n.id, n]));
  const conts = p.nodes.filter(n => n.type === 'lane' || n.type === 'group' || n.type === 'band');
  const cxOf = id => { const n = byId.get(id); return n ? n.x + n.w / 2 : 0; };
  for (let sweep = 0; sweep < 4; sweep++) {
    const order = [...conts].sort((a, b) => sweep % 2 ? (b.y - a.y) : (a.y - b.y));
    for (const C of order) {
      const sibs = kids(C.id, p).filter(k => k.type !== 'lane' && !['text', 'note', 'legend'].includes(k.type));
      if (sibs.length < 2) continue;
      const own = new Map(); for (const sb of sibs) { own.set(sb.id, sb); for (const d of descendants(sb.id, p)) own.set(d.id, sb); }
      const ext = new Map(sibs.map(sb => [sb.id, []])), par = new Map(sibs.map(sb => [sb.id, sb.id]));
      const find = x => par.get(x) === x ? x : (par.set(x, find(par.get(x))), par.get(x));
      for (const l of p.links) {
        const a = own.get(l.from), b = own.get(l.to);
        if (a && !b) ext.get(a.id).push(cxOf(l.to)); else if (b && !a) ext.get(b.id).push(cxOf(l.from));
        else if (a && b && a !== b && C.type !== 'group') par.set(find(a.id), find(b.id));
      }
      const bary = sb => { const v = ext.get(sb.id); return v.length ? v.reduce((t, x) => t + x, 0) / v.length : sb.x + sb.w / 2; };
      const blocks = new Map(); for (const sb of sibs) { const r = find(sb.id); if (!blocks.has(r)) blocks.set(r, []); blocks.get(r).push(sb); }
      const bl = [...blocks.values()].map(m => { m.sort((a, b) => a.x - b.x || a.y - b.y); const withExt = m.filter(x => ext.get(x.id).length); return { m, key: (withExt.length ? withExt : m).reduce((t, x) => t + bary(x), 0) / (withExt.length || m.length), x0: m[0].x }; });
      bl.sort((a, b) => a.key - b.key || a.x0 - b.x0);
      const newOrder = bl.flatMap(b => b.m);
      const slots = [...sibs].sort(C.type === 'group' ? ((a, b) => a.y - b.y || a.x - b.x) : ((a, b) => a.x - b.x || a.y - b.y)).map(n => [n.x, n.y]);
      newOrder.forEach((n, i) => { const dx = slots[i][0] - n.x, dy = slots[i][1] - n.y; for (const d of [n, ...descendants(n.id, p)]) { d.x += dx; d.y += dy; } });
    }
    beautify(p);
    const c = crossingCount(p); if (c < best) { best = c; bestSnap = snap(); }
  }
  const keep = JSON.parse(bestSnap), m = new Map(keep.map(n => [n.id, n]));
  for (const n of p.nodes) { const k = m.get(n.id); if (k) Object.assign(n, { x: k.x, y: k.y, w: k.w, h: k.h }); }
  cur = saved;
  return [before, best];
}
function deleteSel() {
  const p = P();
  if (linkSel.size) {
    checkpoint();
    const drop = new Set(linkSel);
    p.links = p.links.filter(l => !drop.has(l.id));
    clearSel();
    render();
    return;
  }
  if (!sel.size) return; checkpoint();
  const kill = new Set(); for (const id of sel) { kill.add(id); descendants(id).forEach(d => kill.add(d.id)); }
  p.nodes = p.nodes.filter(n => !kill.has(n.id)); p.links = p.links.filter(l => !kill.has(l.from) && !kill.has(l.to));
  clearSel(); render();
}
function copySel() {
  if (!sel.size) return; const ids = new Set(); for (const id of sel) { ids.add(id); descendants(id).forEach(d => ids.add(d.id)); }
  clipboard = { nodes: P().nodes.filter(n => ids.has(n.id)).map(n => ({ ...n })), links: P().links.filter(l => ids.has(l.from) && ids.has(l.to)).map(l => ({ ...l })) };
  toast(`已复制 ${clipboard.nodes.length} 个元素`);
}
function paste() {
  if (!clipboard) return; checkpoint(); const map = {};
  clipboard.nodes.forEach(n => map[n.id] = uid());
  const ns = clipboard.nodes.map(n => ({ ...n, id: map[n.id], parent: map[n.parent] || n.parent, x: n.x + 24, y: n.y + 24, sub: null }));
  P().nodes.push(...ns); P().links.push(...clipboard.links.map(l => ({ ...l, id: uid(), from: map[l.from], to: map[l.to] })));
  selectNodes(ns.filter(n => !map[clipboard.nodes.find(o => map[o.id] === n.id)?.parent]).map(n => n.id));
  clipboard = { nodes: ns.map(n => ({ ...n })), links: [] };
  render();
}

/* ---------- drill-down pages ---------- */
function enterSub(id) {
  const n = nodeById(id); if (!n) return;
  if (!n.sub || !doc.pages[n.sub]) {
    checkpoint(); n.sub = newPage(`${(n.text || '系统').split('\n')[0]} · 内部构成`);
    const sp = doc.pages[n.sub];
    sp.nodes.push(mkNode({ type: 'text', role: 'title', text: `${(n.text || '系统').split('\n')[0]} 内部构成`, size: 20, bold: true, x: 0, y: -50, w: 400, h: 32 }));
    const b = mkNode({ type: 'band', text: '组成', x: 0, y: 0, w: 900, h: 140 }); sp.nodes.push(b);
    ['组成单元一', '组成单元二', '组成单元三'].forEach((t, i) => sp.nodes.push(mkNode({ type: 'round', text: t, parent: b.id, x: 100 + i * 200, y: 40 })));
    beautify(sp);
  }
  P().cam = { ...view }; stack.push(n.sub); cur = n.sub; clearSel();
  render(); if (P().cam) { view = { ...P().cam }; applyView(); } else fit();
}
function goPage(i) { P().cam = { ...view }; stack = stack.slice(0, i + 1); cur = stack[i]; clearSel(); render(); if (P().cam) { view = { ...P().cam }; applyView(); renderOverlay(); } else fit(); }
function renderCrumb() {
  $('#crumb').innerHTML = stack.map((id, i) => i === stack.length - 1 ? `<span class="cur">${esc(doc.pages[id]?.name || '')}</span>` : `<button data-crumb="${i}">${esc(doc.pages[id]?.name || '')}</button><span style="color:var(--muted)">›</span>`).join('');
}
$('#crumb').addEventListener('click', e => { const b = e.target.closest('[data-crumb]'); if (b) goPage(+b.dataset.crumb); });

/* ---------- properties panel ---------- */
const TYPE_NAME = Object.assign(Object.fromEntries(Object.entries(SHP_DEF).map(([k, v]) => [k, v.name])), { equip: '装备／图标卡', text: '文字', note: '说明框', legend: '图例', tblock: '标题栏', band: '分组带', lane: '层（泳道）', group: '子容器' });
const SHAPE_GROUPS = [['基础形状', ['rect', 'round', 'roundL', 'roundR', 'ellipse', 'diamond', 'hexagon', 'octagon', 'triangle', 'parallelogram', 'trapezoid', 'pentagon', 'star', 'cylinder', 'cloud', 'cube', 'plus', 'donut', 'frame', 'equip']],
  ['流程与标注', ['document', 'predef', 'display', 'delay', 'terminator', 'callout']], ['箭头', ['arrowR', 'arrowL', 'arrowU', 'arrowD', 'arrowLR', 'arrowUD', 'chevron', 'homeplate']]];
function seg(id, opts, val, tip) { const t = tip ? ` title="${esc(tip)}"` : ''; return `<div class="seg" id="${id}">${opts.map(([v, l]) => `<button data-v="${v}" class="${v === val ? 'on' : ''}"${t}>${l}</button>`).join('')}</div>`; }
function selectedLinks() {
  const p = P(), out = [];
  linkSel.forEach(id => { const l = p.links.find(x => x.id === id); if (l) out.push(l); });
  return out;
}
function sameButton() {
  if (sel.size === 1 || onlyLinkId()) return '<div class="row"><button id="p-same" type="button" style="border-color:var(--line);justify-content:center">选中同类</button></div>';
  return '';
}
const FIELD_CAP = { status: '状态', font: '字体', size: '字号', bold: '加粗', noBox: '不画外框（纯装备图）', fill: '填充', stroke: '描边', dir: '箭头', kind: '链路类型', color: '颜色', sw: '线宽' };
const SHARED_REJECT = {};
const NODE_FIELDS = {
  status: {
    id: 'status', kind: 'seg',
    show: function (items) {
      if (items.length > 1) return true;
      return ['text', 'note', 'legend', 'lane', 'tblock'].indexOf(items[0].type) < 0;
    },
    get: function (n) { return n.status || 'base'; },
    set: function (n, v) { n.status = v; },
    options: function () { return [['base', doc.statusLabels.base], ['new', doc.statusLabels.new], ['key', doc.statusLabels.key]]; }
  },
  font: {
    id: 'font', kind: 'select',
    show: function (items) { return NODE_FIELDS.size.show(items); },
    get: function (n) { return n.font || ''; },
    set: function (n, v) { n.font = v || ''; },
    options: function () { return FONT_CHOICES.map(function (f) { return [f.id, f.name, f.css]; }); }
  },
  size: {
    id: 'size', kind: 'size',
    show: function (items) {
      if (items.length > 1) return true;
      return !isCont(items[0]) && items[0].type !== 'legend' && items[0].type !== 'tblock';
    },
    get: function (n) { return n.size; },
    set: function (n, v) { n.size = v; }
  },
  bold: {
    id: 'bold', kind: 'check',
    show: function (items) { return NODE_FIELDS.size.show(items); },
    get: function (n) { return !!n.bold; },
    set: function (n, v) { n.bold = !!v; }
  },
  noBox: {
    id: 'noBox', kind: 'check',
    show: function (items) { return items.length > 0 && items.every(function (n) { return !!n.icon; }); },
    get: function (n) { return !!n.noBox; },
    set: function (n, v) { n.noBox = !!v; }
  },
  fill: {
    id: 'fill', kind: 'color', optional: true,
    show: function (items) {
      if (items.length > 1) return true;
      return ['text', 'note', 'legend', 'tblock'].indexOf(items[0].type) < 0;
    },
    get: function (n) { return n.fill || null; },
    set: function (n, v) { if (v) n.fill = v; else delete n.fill; }
  },
  stroke: {
    id: 'stroke', kind: 'color', optional: true,
    show: function (items) { return NODE_FIELDS.fill.show(items); },
    get: function (n) { return n.stroke || null; },
    set: function (n, v) { if (v) n.stroke = v; else delete n.stroke; }
  }
};
const LINK_FIELDS = {
  dir: {
    id: 'dir', kind: 'seg',
    get: function (l) { return linkDir(l); },
    set: function (l, v) { setLinkDir(l, v); },
    options: function () { return [['one', '→ 单向'], ['both', '↔ 双向'], ['none', '— 无']]; }
  },
  kind: {
    id: 'kind', kind: 'select',
    get: function (l) { return l.kind; },
    set: function (l, v) { l.kind = v; doc.lastKind = v; },
    options: function () { return Object.keys(LINK_KINDS).map(function (k) { return [k, LINK_KINDS[k].name]; }); }
  },
  color: {
    id: 'color', kind: 'color', optional: true,
    get: function (l) { return l.color || null; },
    set: function (l, v) { if (v) l.color = v; else delete l.color; }
  },
  sw: {
    id: 'sw', kind: 'num', optional: true, min: 0.5, max: 12,
    get: function (l) { return l.sw || null; },
    set: function (l, v) { if (v) l.sw = v; else delete l.sw; }
  }
};
function fieldState(items, field) {
  if (!items.length) return { mixed: false, value: null };
  const first = field.get(items[0]);
  for (let i = 1; i < items.length; i++) if (!Object.is(field.get(items[i]), first)) return { mixed: true, value: null };
  return { mixed: false, value: first };
}
function fieldHTML(items, field) {
  if (field.show && !field.show(items)) return '';
  const state = fieldState(items, field), cap = FIELD_CAP[field.id] || field.id, id = 'p-' + field.id;
  if (field.kind === 'seg') {
    const buttons = field.options().map(([v, lab]) => `<button type="button" data-v="${v}" class="${!state.mixed && v === state.value ? 'on' : ''}">${lab}</button>`).join('');
    return `<div class="row sh" data-shared="${field.id}"><label>${cap}</label><div class="seg" id="${id}" data-shared="${field.id}">${buttons}</div>${state.mixed ? '<span class="hint">多值</span>' : ''}</div>`;
  }
  if (field.kind === 'select') {
    const mixed = state.mixed ? '<option value="__mixed__" selected>多值</option>' : '';
    const rest = field.options().map(opt => {
      const v = opt[0], lab = opt[1], css = opt[2];
      const on = !state.mixed && v === state.value ? ' selected' : '';
      const style = css ? ` style="font-family:${css}"` : '';
      return `<option value="${v}"${on}${style}>${lab}</option>`;
    }).join('');
    return `<div class="row sh" data-shared="${field.id}"><label>${cap}</label><select id="${id}" data-shared="${field.id}">${mixed}${rest}</select></div>`;
  }
  if (field.kind === 'size') {
    const shown = state.mixed || state.value == null ? '' : sizeLabel(state.value);
    const ph = state.mixed ? ' placeholder="多值"' : '';
    const hint = state.mixed ? '<span class="hint">多值</span>' : '';
    const list = CN_SIZES.map(s => `<option value="${s.name}"></option>`).join('');
    return `<div class="row sh" data-shared="${field.id}"><label>${cap}</label><input type="text" id="${id}" data-shared="${field.id}" list="${id}-list" autocomplete="off" value="${esc(shown)}"${ph}><datalist id="${id}-list">${list}</datalist>${hint}</div>`;
  }
  if (field.kind === 'check') {
    const label = state.mixed ? '多值' : cap;
    return `<div class="row sh" data-shared="${field.id}"><label></label><label style="width:auto;display:flex;gap:6px;align-items:center;color:var(--fg)"><input type="checkbox" id="${id}" data-shared="${field.id}"${!state.mixed && state.value ? ' checked' : ''}> ${label}</label></div>`;
  }
  if (field.kind === 'num') {
    const shown = state.mixed || state.value == null ? '' : state.value;
    const ph = state.mixed ? ' placeholder="多值"' : '';
    const hint = state.mixed ? '<span class="hint">多值</span>' : '';
    const clr = field.optional ? `<button type="button" data-clear="1" data-shared="${field.id}" style="border-color:var(--line)">默认</button>` : '';
    return `<div class="row sh" data-shared="${field.id}"><label>${cap}</label><input type="number" id="${id}" data-shared="${field.id}" min="${field.min}" max="${field.max}" value="${shown}"${ph}>${hint}${clr}</div>`;
  }
  if (field.kind === 'color') {
    const hex = !state.mixed && state.value ? state.value : '#ffffff';
    const hint = state.mixed ? '<span class="hint">多值</span>' : '';
    const clr = field.optional ? `<button type="button" data-clear="1" data-shared="${field.id}" style="border-color:var(--line)">默认</button>` : '';
    return `<div class="row sh" data-shared="${field.id}"><label>${cap}</label><input type="color" id="${id}" data-shared="${field.id}" value="${hex}">${hint}${clr}</div>`;
  }
  return '';
}
function fieldsHTML(items, table) {
  return Object.keys(table).map(k => fieldHTML(items, table[k])).join('');
}
function selectedNodes() {
  const out = [];
  sel.forEach(id => { const n = nodeById(id); if (n) out.push(n); });
  return out;
}
function parseShared(field, raw) {
  if (raw === null) return null;
  if (raw === '__mixed__') return SHARED_REJECT;
  if (field.id === 'status' && ['base', 'new', 'key'].indexOf(raw) < 0) return SHARED_REJECT;
  if (field.id === 'dir' && ['one', 'both', 'none'].indexOf(raw) < 0) return SHARED_REJECT;
  if (field.id === 'kind' && !LINK_KINDS[raw]) return SHARED_REJECT;
  if (field.kind === 'color') {
    if (raw === '') return null;
    if (!/^#[0-9A-Fa-f]{6}$/.test(String(raw))) return SHARED_REJECT;
    return String(raw);
  }
  if (field.kind === 'size') {
    const n = parseSize(raw);
    if (n == null) return SHARED_REJECT;
    return n;
  }
  if (field.kind === 'num') {
    if (raw === '' || raw == null) return field.optional ? null : SHARED_REJECT;
    const n = +raw;
    if (!isFinite(n) || n < field.min || n > field.max) return SHARED_REJECT;
    return n;
  }
  if (field.kind === 'check') return !!raw;
  return raw;
}
let sharedArm = false, sharedFocusBound = false;
function applyShared(items, write, live) {
  if (!items.length) return;
  const fresh = !sharedArm;
  if (fresh) { checkpoint(); sharedArm = true; }
  const before = fresh ? undoS[undoS.length - 1] : null;
  items.forEach(write);
  const now = snapshot();
  if (fresh && before === now) { undoS.pop(); sharedArm = false; }
  propSnap = now;
  if (!live) { sharedArm = false; render(); }
  else render(false);
}
function bindFields(items, fields) {
  const el = $('#props');
  if (!sharedFocusBound) {
    sharedFocusBound = true;
    el.addEventListener('focusout', () => { sharedArm = false; });
  }
  Object.keys(fields).forEach(id => {
    const field = fields[id];
    const row = el.querySelector('.sh[data-shared="' + field.id + '"]');
    if (!row) return;
    if (field.kind === 'check') {
      const box = row.querySelector('input');
      if (box) box.indeterminate = fieldState(items, field).mixed;
      if (box) box.addEventListener('change', () => {
        const v = parseShared(field, box.checked);
        if (v === SHARED_REJECT) return;
        applyShared(items, it => field.set(it, v), false);
      });
    } else if (field.kind === 'seg') {
      row.querySelectorAll('button[data-v]').forEach(b => b.addEventListener('click', () => {
        const v = parseShared(field, b.dataset.v);
        if (v === SHARED_REJECT) return;
        applyShared(items, it => field.set(it, v), false);
      }));
    } else if (field.kind === 'select') {
      const box = row.querySelector('select');
      if (!box) return;
      box.addEventListener('change', () => {
        if (box.value === '__mixed__') return;
        const v = parseShared(field, box.value);
        if (v === SHARED_REJECT) return;
        applyShared(items, it => field.set(it, v), false);
      });
    } else if (field.kind === 'num' || field.kind === 'color' || field.kind === 'size') {
      const input = row.querySelector('input');
      if (!input) return;
      input.addEventListener('input', () => {
        const v = parseShared(field, input.value);
        if (v === SHARED_REJECT) return;
        applyShared(items, it => field.set(it, v), true);
      });
      if (field.optional) {
        input.addEventListener('blur', () => {
          if (field.kind === 'num' && input.value === '') applyShared(items, it => field.set(it, null), false);
        });
        const clr = row.querySelector('[data-clear]');
        if (clr) clr.addEventListener('click', () => applyShared(items, it => field.set(it, null), false));
      }
    }
  });
}
function renderProps() {
  const el = $('#props'); const p = P(); let h = '';
  const links = selectedLinks();
  if (linkSel.size && !links.length) { clearSel(); return renderProps(); }
  if (links.length > 1) {
    h += `<h3>已选 ${links.length} 条连线</h3>`;
    h += fieldsHTML(links, LINK_FIELDS);
    h += `<hr><button id="p-del" type="button" style="color:var(--danger)">删除连线</button>`;
  } else if (links.length === 1) {
    const l = links[0];
    const a = nodeById(l.from), b = nodeById(l.to), both = linkDir(l) === 'both';
    h += `<div class="hint">${linkPanelHint()}</div>`;
    h += `<h3>连线 <span class="tag">${esc((a?.text || '').split('\n')[0])} → ${esc((b?.text || '').split('\n')[0])}</span></h3>`;
    h += fieldHTML(links, LINK_FIELDS.dir);
    h += `<div class="row"><label></label><button id="p-swap" style="border-color:var(--line);justify-content:center">⇄ 调换方向</button></div>`;
    h += fieldHTML(links, LINK_FIELDS.kind);
    h += fieldHTML(links, LINK_FIELDS.color);
    h += fieldHTML(links, LINK_FIELDS.sw);
    if (both) {
      h += `<div class="row"><label style="width:auto">${esc(dirFieldLabel('去向', b))}</label><input type="text" id="p-label" value="${esc(l.label)}" placeholder="如：态势上报"></div>`;
      h += `<div class="row"><label style="width:auto">${esc(dirFieldLabel('回向', a))}</label><input type="text" id="p-back" value="${esc(l.labelBack || '')}" placeholder="如：指令回执"></div>`;
    } else h += `<div class="row"><label>标签</label><input type="text" id="p-label" value="${esc(l.label)}" placeholder="如：数据链、MCP 调用"></div>`;
    h += `<div class="row"><label>走线</label>${seg('p-route', [['ortho', '直角'], ['straight', '直线']], l.route)}</div>`;
    if (window.Std) h += Std.propsHTML('link', l, p);
    h += sameButton();
    h += `<hr><button id="p-del" style="color:var(--danger)">删除连线</button>`;
  } else if (sel.size > 1) {
    const nodes = selectedNodes();
    h += `<h3>已选 ${sel.size} 个元素</h3><div class="hint">对齐与分布</div>`;
    h += `<div class="grid3">${[['l', '左对齐'], ['c', '水平居中'], ['r', '右对齐'], ['t', '顶对齐'], ['m', '垂直居中'], ['b', '底对齐'], ['dh', '水平等距'], ['dv', '垂直等距'], ['size', '等宽等高']].map(([k, n]) => `<button data-al="${k}">${n}</button>`).join('')}</div>`;
    h += fieldsHTML(nodes, NODE_FIELDS);
    h += `<hr><div class="hint">复合图标：把所选装备合成一个元素（作为输入／输出整体连线）</div><div class="row"><button id="p-group" class="primary" style="justify-content:center">⧉ 组合为复合图标（Ctrl+G）</button></div>`;
    h += `<hr><button id="p-del" style="color:var(--danger)">删除所选</button>`;
  } else if (sel.size === 1) {
    const n = nodeById([...sel][0]); if (!n) { clearSel(); return renderProps(); }
    h += `<h3>${TYPE_NAME[n.type] || '元素'}</h3>`;
    if (n.type !== 'legend' && n.type !== 'tblock') h += `<div class="row"><label>${isCont(n) ? '标题' : '文字'}</label><textarea id="p-text" rows="2">${esc(n.text)}</textarea></div>`;
    if (!isCont(n) && !['text', 'note', 'legend', 'tblock'].includes(n.type)) h += `<div class="row"><label>形状</label><select id="p-type">${SHAPE_GROUPS.map(([g, ts]) => `<optgroup label="${g}">${ts.map(t => `<option value="${t}" ${t === n.type ? 'selected' : ''}>${TYPE_NAME[t]}</option>`).join('')}</optgroup>`).join('')}</select></div>`;
    if (!isCont(n) && !['text', 'note', 'legend', 'tblock'].includes(n.type)) {
      const u = iconURI(n.icon);
      h += `<div class="row"><label>图标</label><div class="iconprev">${u ? `<img src="${u}" alt="">` : '<span style="color:var(--muted)">无</span>'}</div><button id="p-icon" style="border-color:var(--line)">${u ? '更换' : '选择'}</button>${u ? '<button id="p-noicon" style="border-color:var(--line)">清除</button>' : ''}</div>`;
    }
    h += fieldsHTML([n], NODE_FIELDS);
    if (n.type === 'lane') h += `<div class="row"><label>标题栏宽</label><input type="number" id="p-tw" min="40" max="300" value="${laneTW(n)}"></div>`;
    h += `<div class="grid2" style="margin-top:6px">${['x', 'y', 'w', 'h'].map(k => `<div class="row" style="margin:0"><label style="width:16px">${k.toUpperCase()}</label><input type="number" data-geo="${k}" value="${Math.round(n[k])}"></div>`).join('')}</div>`;
    if (window.Combo && iconable(n)) {
      const cb = Combo.isCombo(n) && doc.custom[n.icon.slice(3)].combo;
      if (cb) h += `<hr><div class="hint">复合图标（${cb.kind === 'formation' ? '编队' : '组合'}，${cb.members.length} 个成员）</div><div class="grid2">${cb.kind === 'formation' ? '<button id="p-cbedit">编辑编队</button>' : ''}<button id="p-ungroup">拆分（Ctrl+Shift+U）</button></div>`;
      else if (n.icon && n.icon.startsWith('lib:')) h += `<hr><div class="row"><button id="p-form" style="border-color:var(--line);justify-content:center">⁂ 用此装备生成编队（Ctrl+Shift+B）</button></div>`;
    }
    if (window.Std) h += Std.propsHTML('node', n, p);
    if (!['text', 'note', 'legend', 'band', 'lane', 'tblock'].includes(n.type)) h += `<hr><div class="hint">内部结构：双击进入后可继续画该系统的组成。</div><div class="row"><button id="p-sub" class="primary" style="justify-content:center">${n.sub ? '进入内部结构 ›' : '＋ 创建内部结构'}</button></div>`;
    h += sameButton();
    h += `<hr><button id="p-del" style="color:var(--danger)">删除${isCont(n) ? '（含内部元素）' : ''}</button>`;
  } else {
    const st = legendEntries(p);
    h += `<h3>图面设置</h3>`;
    h += `<div class="row"><label>文档名</label><input id="d-dname" type="text" placeholder="未命名" value="${esc(doc.name || '')}"></div>`;
    h += `<div class="row"><label>页面名</label><input type="text" id="d-pname" value="${esc(p.name)}"></div>`;
    h += `<div class="row"><label>主题</label><select id="d-theme">${Object.entries(THEMES).map(([k, v]) => `<option value="${k}" ${k === doc.theme ? 'selected' : ''}>${v.name}</option>`).join('')}</select></div>`;
    h += `<div class="row"><label>跨线</label>${seg('d-jump', [['arc', '⌒ 跨线弧'], ['gap', '断开'], ['none', '无']], doc.jumpStyle || 'arc')}</div>`;
    h += `<div class="row" title="连线遇到中间的框时自动绕开"><label>连线避障</label>${seg('d-avoid', [['on', '自动绕开'], ['off', '关闭']], doc.avoid === false ? 'off' : 'on')}</div>`;
    h += `<div class="row" title="拖动时对齐其他图形的边与中线、画布中轴，并提示等间距；按住 Alt 临时关闭"><label>拖动吸附</label>${seg('d-snapon', [['on', '对齐吸附'], ['off', '关闭']], snapOn() ? 'on' : 'off')}</div>`;
    if (window.Compact) h += Compact.panelHTML();
    h += `<div class="row" title="北约体制：友方蓝、敌方红；我军习惯：我方红、敌方蓝"><label>军标配色</label>${seg('d-ms', [['nato', '友蓝敌红'], ['cn', '我红敌蓝']], msMode())}</div>`;
    if (window.Std) h += Std.propsHTML('page', null, p);
    h += `<hr><div class="hint" style="margin-bottom:4px">状态图例名称</div>`;
    h += ['base', 'new', 'key'].map(s => { const t = T(); const c = s === 'base' ? t.box : t.st[s]; return `<div class="row"><label><span class="swatch" style="width:18px;height:12px;background:${c.fill};border:1px solid ${c.stroke}"></span></label><input type="text" data-sl="${s}" value="${esc(doc.statusLabels[s])}"></div>`; }).join('');
    h += `<hr><div class="hint">
      <b style="color:var(--fg)">操作要点</b><br>
      · 左侧元素<b>拖到画布</b>或点击添加；放进层或子容器即归属该层<br>
      · 悬停元素出现<b>蓝点</b>，拖到另一元素即连线；连线可设单向／双向箭头<br>
      · 元素右上角 <b style="color:#2F80ED">⊕</b> 进入内部结构，顶部路径返回上一级<br>
      · <b>一键美化</b> <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>F</kbd>：层内等距、统一尺寸、分组带对齐<br>
      · <b>减少交叉</b> <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>：按连线关系重排层内顺序后美化<br>
      · 同侧多条连线自动<b>分散端点</b>、并行线自动错开；交叉处画<b>跨线弧</b>（上方可改为断开／无）<br>
      · 悬停元素或连线，相关连线<b>高亮</b>、其余变淡<br>
      · ${linkCanvasKeys()}<br>
      · <kbd>双击</kbd>／<kbd>F2</kbd> 改字 · <kbd>Ctrl</kbd>+<kbd>K</kbd> 选图标 · <kbd>Delete</kbd> 删除 · <kbd>Ctrl</kbd>+<kbd>Z</kbd> 撤销 · <kbd>Ctrl</kbd>+<kbd>D</kbd> 复制<br>
      · <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>G</kbd> 文字成图 · <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>M</kbd> 模板 · <kbd>Ctrl</kbd>+<kbd>E</kbd> 导出<br>
      · 滚轮平移 · <kbd>Ctrl</kbd>+滚轮缩放 · 按住<kbd>空格</kbd>拖动画布<br>
      · 按 <kbd>F1</kbd> 或 <kbd>?</kbd> 查看全部快捷键</div>`;
  }
  el.innerHTML = h; bindProps();
}
let propSnap = null;
function bindProps() {
  const el = $('#props');
  if (!el._jwSnap) { el._jwSnap = true; el.addEventListener('focusin', () => { propSnap = snapshot(); }); }
  el.onchange = ev => {
    if (ev && ev.target && ev.target.closest && ev.target.closest('[data-shared]')) { propSnap = snapshot(); return; }
    if (propSnap && propSnap !== snapshot()) { undoS.push(propSnap); redoS = []; if (typeof window.jwTouch === 'function') window.jwTouch(); }
    propSnap = snapshot();
  };
  const links = selectedLinks();
  const n = sel.size === 1 ? nodeById([...sel][0]) : null;
  const l = links.length === 1 ? links[0] : null;
  const live = () => render(false);
  const on = (id, ev, fn) => { const x = $(id); if (x) x.addEventListener(ev, fn); };
  if (links.length) bindFields(links, LINK_FIELDS);
  else if (sel.size) bindFields(selectedNodes(), NODE_FIELDS);
  on('#p-text', 'input', e => { n.text = e.target.value; live(); });
  on('#p-type', 'change', e => { checkpoint(); n.type = e.target.value; if (n.type === 'equip' && n.h < 72) { n.w = Math.max(n.w, 96); n.h = 96; } render(); });
  on('#p-tw', 'input', e => { n.titleW = clamp(+e.target.value || 96, 40, 300); live(); });
  el.querySelectorAll('[data-geo]').forEach(i => i.addEventListener('input', e => { const k = e.target.dataset.geo, v = +e.target.value; if (isNaN(v)) return; const d = v - n[k]; if (k === 'x' || k === 'y') descendants(n.id).forEach(c => c[k] += d); n[k] = (k === 'w' || k === 'h') ? Math.max(16, v) : v; live(); }));
  el.querySelectorAll('[data-sl]').forEach(i => i.addEventListener('input', e => { doc.statusLabels[e.target.dataset.sl] = e.target.value; live(); }));
  el.querySelectorAll('[data-al]').forEach(b => b.addEventListener('click', () => alignSel(b.dataset.al)));
  on('#p-icon', 'click', () => openIconPicker(n));
  on('#p-noicon', 'click', () => { checkpoint(); n.icon = null; if (n.type === 'equip') n.type = 'round'; render(); });
  on('#p-sub', 'click', () => enterSub(n.id));
  on('#p-group', 'click', () => Combo.groupSelection());
  on('#p-ungroup', 'click', () => Combo.ungroup(n));
  on('#p-cbedit', 'click', () => Combo.open(n));
  on('#p-form', 'click', () => Combo.open(n));
  on('#p-del', 'click', deleteSel);
  on('#p-same', 'click', () => selectSame());
  on('#p-swap', 'click', () => { checkpoint(); swapLink(l); render(); });
  on('#p-label', 'input', e => { l.label = e.target.value; live(); });
  on('#p-back', 'input', e => { setLabelBack(l, e.target.value); live(); });
  on('#p-route', 'click', e => { const b = e.target.closest('[data-v]'); if (!b) return; checkpoint(); l.route = b.dataset.v; render(); });
  on('#d-dname', 'input', e => { doc.name = e.target.value; refreshDocTitle(); if (typeof window.jwTouch === 'function') window.jwTouch(); });
  on('#d-pname', 'input', e => { P().name = e.target.value; renderCrumb(); refreshDocTitle(); if (typeof window.jwTouch === 'function') window.jwTouch(); });
  on('#d-theme', 'change', e => setTheme(e.target.value));
  on('#d-jump', 'click', e => { const b = e.target.closest('[data-v]'); if (!b) return; checkpoint(); doc.jumpStyle = b.dataset.v; render(); });
  on('#d-avoid', 'click', e => { const b = e.target.closest('[data-v]'); if (!b) return; checkpoint(); doc.avoid = b.dataset.v === 'on'; render(); });
  on('#d-snapon', 'click', e => { const b = e.target.closest('[data-v]'); if (!b) return; try { localStorage.setItem('hongtu.snap', b.dataset.v); } catch (_) { } render(); });
  if (window.Compact && !l && !n && !links.length) Compact.bind($('#props'));
  if (window.Std && links.length < 2) Std.bindProps(l ? 'link' : n ? 'node' : (!sel.size ? 'page' : 'multi'), l || n || null, P());
  on('#d-ms', 'click', e => { const b = e.target.closest('[data-v]'); if (!b) return; checkpoint(); doc.msColor = b.dataset.v; renderPalette(); render(); if ($('#modal').style.display === 'flex') renderPicker(); });
}
function setTheme(k) { checkpoint(); doc.theme = k; $('#b-theme').value = k; render(); }

/* ---------- icon picker ---------- */
let iconTarget = null, icTab = null;
function openIconPicker(n) { iconTarget = n; $('#modal').style.display = 'flex'; $('#ic-q').value = ''; icTab = icTab || '无人'; renderPicker(); setTimeout(() => $('#ic-q').focus(), 0); }
function renderPicker() {
  const q = $('#ic-q').value.trim();
  const secs = iconSections(), tabs = secs.map(x => x[0]).concat(window.ms ? ['军标'] : [], ['自定义']);
  if (!tabs.includes(icTab)) icTab = tabs[0];
  $('#ic-tabs').innerHTML = tabs.map(t => `<button data-tab="${t}" class="${!q && t === icTab ? 'on' : ''}">${t}</button>`).join('');
  let items = [];
  const m = s => !q || s.includes(q);
  if (q) { for (const i of ICONS) if (m(i.name) || iconCats(i).some(m)) items.push(['lib:' + i.key, i.name]); }
  else for (const i of (secs.find(x => x[0] === icTab) || [, []])[1]) items.push(['lib:' + i.key, i.name]);
  if (window.ms && (q || icTab === '军标')) for (const x of MS_LIST) if (!q || m(x[1]) || m('军标') || m(x[2])) items.push(['ms:' + x[0], x[1]]);
  if (q || icTab === '自定义') for (const [id, v] of Object.entries(doc.custom)) if (m(v.name)) items.push(['cu:' + id, v.name]);
  let h = items.map(([k, nm]) => `<button data-ic="${k}"><img src="${iconURI(k)}" alt=""><span>${esc(nm)}</span></button>`).join('');
  if (icTab === '自定义' && !q) h += `<button id="ic-up"><svg viewBox="0 0 42 30" width="52" height="40"><path d="M21 6v18M12 15h18" stroke="currentColor" stroke-width="2"/></svg><span>上传 SVG／PNG</span></button>`;
  $('#ic-grid').innerHTML = h || '<div class="hint">没有匹配的图标</div>';
}
$('#ic-tabs').addEventListener('click', e => { const b = e.target.closest('[data-tab]'); if (b) { icTab = b.dataset.tab; $('#ic-q').value = ''; renderPicker(); } });
$('#ic-q').addEventListener('input', renderPicker);
$('#ic-close').onclick = () => $('#modal').style.display = 'none';
$('#modal').addEventListener('click', e => {
  if (e.target.id === 'modal') { $('#modal').style.display = 'none'; return; }
  if (e.target.closest('#ic-up')) { $('#f-icon').click(); return; }
  const b = e.target.closest('[data-ic]'); if (!b || !iconTarget) return;
  checkpoint(); iconTarget.icon = b.dataset.ic;
  if (!['equip'].includes(iconTarget.type) && iconTarget.h >= 72) iconTarget.type = 'equip';
  $('#modal').style.display = 'none'; render();
});
$('#f-icon').addEventListener('change', e => {
  const f = e.target.files[0]; if (!f) return; const rd = new FileReader();
  rd.onload = () => {
    const id = uid(); doc.custom[id] = { name: f.name.replace(/\.[^.]+$/, ''), uri: rd.result };
    if (iconTarget) { checkpoint(); iconTarget.icon = 'cu:' + id; $('#modal').style.display = 'none'; }
    renderPalette(); render(); toast('已加入自定义图标');
  };
  rd.readAsDataURL(f); e.target.value = '';
});

/* ---------- file save / export ---------- */
async function saveFile(name, data) {
  const blob = data instanceof Blob ? data : new Blob([data]);
  if (window.claude && typeof window.claude.use === 'function') {
    try {
      const dl = await window.claude.use('downloads');
      if (dl) { await dl.save({ filename: name, data: blob }); toast('已导出：' + name); return true; }
    } catch (e) {
      if (e && e.code === 'declined') { toast('已取消保存'); return null; }
      if (e && e.code === 'rejected_extension') { toast('在线预览不支持导出此格式，请在离线版中使用'); return null; }
      if (e && e.code === 'rate_limited') { toast('已有一个保存提示未处理'); return null; }
    }
  }
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500); toast('已导出：' + name);
  return true;
}
function projectBaseName() {
  let stem = '';
  if (typeof window.jwProjectStem === 'function') { try { stem = window.jwProjectStem() || ''; } catch (e) { stem = ''; } }
  if (!stem && doc && doc.name) stem = doc.name;
  if (!stem && doc && doc.pages && doc.pages.root && doc.pages.root.name && doc.pages.root.name !== '总图') stem = doc.pages.root.name;
  stem = String(stem || '体系图').replace(/\.jingwei\.json$/i, '').replace(/\.json$/i, '').trim();
  return stem.replace(/[\\/:*?"<>|]/g, '_').trim() || '体系图';
}
function docExportName(ext) { return projectBaseName() + '.' + ext; }
function projectFileDefault() { return projectBaseName() + '.jingwei.json'; }
const fname = ext => {
  const leaf = cur !== 'root' && P() && P().name ? '-' + String(P().name).replace(/[\\/:*?"<>|]/g, '_') : '';
  return projectBaseName() + leaf + '.' + ext;
};
function exportSVGString(p, bg) {
  const b = contentBBox(p), pad = 24, x = b.x - pad, y = b.y - pad, w = b.w + pad * 2, h = b.h + pad * 2;
  const saved = cur; cur = p.id; const inner = diagramSVG(p, true, 'x'); cur = saved;
  return { str: `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${x} ${y} ${w} ${h}" font-family="${esc(FONT)}">${bg ? `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${T().bg}"/>` : ''}${inner}</svg>`, w, h };
}
function rasterize(svgStr, w, h, scale) {
  return new Promise((res, rej) => {
    const img = new Image(); const url = URL.createObjectURL(new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' }));
    img.onload = () => { const c = document.createElement('canvas'); c.width = Math.round(w * scale); c.height = Math.round(h * scale); const g = c.getContext('2d'); g.scale(scale, scale); g.drawImage(img, 0, 0, w, h); URL.revokeObjectURL(url); c.toBlob(b => b ? res(b) : rej(new Error('PNG 生成失败')), 'image/png'); };
    img.onerror = () => { URL.revokeObjectURL(url); rej(new Error('图像渲染失败')); }; img.src = url;
  });
}
async function exportPNG(scale, bg) { const { str, w, h } = exportSVGString(P(), bg); saveFile(fname('png'), await rasterize(str, w, h, scale)); }
const ICON_PNG_MS = 2500;
function iconPNG(uri, px = 256) {
  let asp = 1; const mm = /#a([\d.]+)$/.exec(uri); if (mm) { asp = +mm[1]; uri = uri.slice(0, mm.index); }
  if (!isFinite(asp) || asp <= 0) asp = 1;
  const pw = asp >= 1 ? Math.round(px * Math.min(asp, 4)) : px, ph = asp >= 1 ? px : Math.round(px / Math.max(asp, 0.25));
  const cw = Math.max(1, Math.min(pw, 1024)), ch = Math.max(1, Math.min(ph, 1024));
  return new Promise(res => {
    let done = false, timer;
    const img = new Image();
    const finish = v => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      img.onload = null; img.onerror = null;
      try { img.src = ''; } catch (e) { }
      res(v);
    };
    timer = setTimeout(() => finish(null), ICON_PNG_MS);
    img.onload = () => {
      try {
        const c = document.createElement('canvas'); c.width = cw; c.height = ch;
        const g = c.getContext('2d'); if (!g) { finish(null); return; }
        const iw = img.width || cw, ih = img.height || ch, r = Math.min(cw / iw, ch / ih), w = iw * r, h = ih * r;
        g.drawImage(img, (cw - w) / 2, (ch - h) / 2, w, h);
        finish(c.toDataURL('image/png'));
      } catch (e) { finish(null); }
    };
    img.onerror = () => { try { finish(null); } catch (e) { res(null); } };
    try { img.src = uri; } catch (e) { finish(null); }
  });
}
function hierarchyPages() {
  const out = [], seen = new Set();
  const walk = (id, chain) => {
    if (seen.has(id) || !doc.pages[id]) return;
    seen.add(id);
    const p = doc.pages[id], name = p.name || '未命名', next = chain.concat(name);
    out.push({ page: p, depth: chain.length, chain: next });
    for (const n of p.nodes) if (n.sub) walk(n.sub, next);
  };
  walk('root', []);
  /* 无入口的页面（格式转换时按原文件页序）也要导出 */
  if (doc.pageOrder) doc.pageOrder.forEach(id => walk(id, []));
  return out;
}
function pagesInOrder() { return hierarchyPages().map(h => h.page); }
function hierarchyFileName(item, index, ext) {
  const label = item.chain.map(s => String(s || '').replace(/[\\/:*?"<>|]/g, '_').trim()).filter(Boolean).join('-') || '页面';
  return projectBaseName() + '-' + String(index + 1).padStart(2, '0') + '-' + label + '.' + ext;
}
async function captureExport(fn) {
  const got = [], prev = saveFile;
  saveFile = async (name, data) => { got.push({ name, data }); };
  try { await fn(); }
  finally { saveFile = prev; }
  return got;
}
async function saveMany(stem, files) {
  const D = window.jwDesk;
  if (D && typeof D.pickDir === 'function' && typeof D.writeIn === 'function') {
    const dir = await D.pickDir('选择整体导出的保存文件夹');
    if (!dir) { toast('已取消保存'); return; }
    for (const f of files) {
      const buf = f.data instanceof Blob ? await f.data.arrayBuffer() : (typeof f.data === 'string' ? new TextEncoder().encode(f.data).buffer : f.data);
      await D.writeIn(dir, f.name, buf);
    }
    toast('已保存 ' + files.length + ' 个文件到所选文件夹');
    return;
  }
  if (typeof JSZip === 'undefined') { toast('压缩组件未加载'); return; }
  const zip = new JSZip();
  for (const f of files) zip.file(f.name, f.data instanceof Blob ? await f.data.arrayBuffer() : f.data);
  await saveFile((projectBaseName() || stem) + '.zip', await zip.generateAsync({ type: 'blob' }));
}
async function exportHierarchy(kind) {
  const items = hierarchyPages();
  if (!items.length) { toast('没有可导出的视图'); return; }
  toast('正在整体导出…');
  const saved = cur, files = [];
  try {
    for (let i = 0; i < items.length; i++) {
      const p = items[i].page;
      cur = p.id;
      const ext = kind === 'drawio' ? 'drawio' : kind;
      const name = hierarchyFileName(items[i], i, ext);
      if (kind === 'png') {
        const o = exportSVGString(p, false);
        files.push({ name, data: await rasterize(o.str, o.w, o.h, 2) });
      } else if (kind === 'svg') files.push({ name, data: exportSVGString(p, false).str });
      else if (kind === 'vsdx') {
        const got = await captureExport(() => exportVSDX([p]));
        if (got[0]) files.push({ name, data: got[0].data });
      } else if (kind === 'drawio') {
        if (!window.DrawIO) { toast('draw.io 模块未加载'); return; }
        const got = await captureExport(() => DrawIO.exportFile([p]));
        if (got[0]) files.push({ name, data: got[0].data });
      }
    }
  } finally { cur = saved; }
  if (!files.length) { toast('没有可导出的文件'); return; }
  await saveMany(projectBaseName(), files);
}
const hex = c => String(c || '#000000').replace('#', '').slice(0, 6).toUpperCase();

/* PowerPoint: native editable shapes, one slide per page (总图 + 各系统展开页) */
const addT = (slide, text, o) => slide.addText(text, { lang: 'zh-CN', ...o });
let PPT_CUSTGEOM = true; /* false → fall back to one straight connector per segment (no hops) */
async function exportPPTX() {
  if (typeof PptxGenJS === 'undefined') { toast('PPT 组件未加载'); return; }
  toast('正在生成 PPT…');
  const pptx = new PptxGenJS(); const t = T();
  pptx.defineLayout({ name: 'W', width: 13.333, height: 7.5 }); pptx.layout = 'W';
  const iconCache = new Map(); const getIcon = async u => { if (!iconCache.has(u)) iconCache.set(u, await iconPNG(u)); return iconCache.get(u); };
  for (const p of pagesInOrder()) {
    const slide = pptx.addSlide(); if (doc.theme === 'command') slide.background = { color: hex(t.bg) };
    const saved = cur; cur = p.id;
    const b = contentBBox(p), pad = 16, f = Math.min((13.333 - 0.5) / (b.w + pad * 2), (7.5 - 0.4) / (b.h + pad * 2));
    const ox = (13.333 - (b.w + pad * 2) * f) / 2, oy = (7.5 - (b.h + pad * 2) * f) / 2;
    const X = v => ox + (v - b.x + pad) * f, Y = v => oy + (v - b.y + pad) * f, S = v => Math.max(0.001, v * f), PT = px => Math.max(5, +(px * f * 72).toFixed(1)), LW = px => Math.max(0.25, +(px * f * 72).toFixed(2));
    const txt = (lines, o) => lines.join('\n');
    for (const n of drawOrder(p)) {
      const base = { x: X(n.x), y: Y(n.y), w: S(n.w), h: S(n.h) };
      if (n.type === 'band') {
        const st = stStyle(n, t);
        slide.addShape(pptx.ShapeType.rect, { ...base, fill: { color: hex(n.fill || t.band.fill) }, line: { color: hex(t.band.stroke), width: LW(1.5) } });
        addT(slide, String(n.text || ''), { x: X(n.x), y: Y(n.y), w: S(BAND_TW), h: S(n.h), fill: { color: hex(n.status === 'base' ? t.band.titleFill : st.stroke) }, color: hex(t.band.titleText), fontFace: fontFace(n), fontSize: PT(15), bold: true, align: 'center', valign: 'middle', vert: 'eaVert', margin: 0 });
      } else if (n.type === 'lane') {
        const tw = laneTW(n);
        slide.addShape(pptx.ShapeType.rect, { ...base, fill: { color: hex(n.fill || t.lane.fill) }, line: { color: hex(t.lane.stroke), width: LW(1) } });
        addT(slide, String(n.text || ''), { x: X(n.x), y: Y(n.y), w: S(tw), h: S(n.h), color: hex(t.lane.titleText), fontFace: fontFace(n), fontSize: PT(13.5), bold: true, align: 'center', valign: 'middle', margin: 1 });
        slide.addShape(pptx.ShapeType.line, { x: X(n.x + tw), y: Y(n.y + 6), w: 0, h: S(n.h - 12), line: { color: hex(t.lane.stroke), width: LW(1) } });
      } else if (n.type === 'group') {
        const st = stStyle(n, t);
        slide.addShape(pptx.ShapeType.roundRect, { ...base, rectRadius: S(6), fill: { color: hex(st.fill === t.box.fill ? t.group.fill : st.fill) }, line: { color: hex(st.stroke === t.box.stroke ? t.group.stroke : st.stroke), width: LW(1.3) } });
        addT(slide, String(n.text || ''), { x: X(n.x), y: Y(n.y), w: S(n.w), h: S(GROUP_TH), fill: { color: hex(n.status === 'base' ? t.group.titleFill : st.title) }, color: hex(t.group.titleText), fontFace: fontFace(n), fontSize: PT(12.5), bold: true, align: 'center', valign: 'middle', margin: 1 });
      } else if (n.type === 'tblock') {
        if (window.Std) for (const c of Std.tblockCells(n, p)) {
          const o = { x: X(c.x), y: Y(c.y), w: S(c.w), h: S(c.h), line: { color: hex(c.stroke), width: LW(c.lw) }, ...(c.fill ? { fill: { color: hex(c.fill) } } : {}) };
          if (c.text) addT(slide, c.text, { ...o, shape: pptx.ShapeType.rect, color: hex(c.color), fontFace: fontFace(n), fontSize: PT(c.size), bold: c.bold, align: c.align === 'left' ? 'left' : 'center', valign: 'middle', margin: 0, wrap: false });
          else slide.addShape(pptx.ShapeType.rect, o);
        }
      } else if (n.type === 'legend') {
        const items = legendLayout(n, p);
        slide.addShape(pptx.ShapeType.rect, { x: X(n.x), y: Y(n.y), w: S(n.w), h: S(n.h), fill: { color: hex(t.note.fill) }, line: { color: hex(t.note.stroke), width: LW(1) } });
        for (const it of items) {
          if (it.kind === 'st') { const ss = it.s === 'base' ? t.box : t.st[it.s]; slide.addShape(pptx.ShapeType.rect, { x: X(it.x), y: Y(it.y + 3), w: S(26), h: S(14), fill: { color: hex(ss.fill) }, line: { color: hex(ss.stroke), width: LW(1) } }); }
          else { const K = LINK_KINDS[it.k]; slide.addShape(pptx.ShapeType.line, { x: X(it.x), y: Y(it.y + 10), w: S(27), h: 0, line: { color: hex(t.link[it.k]), width: LW(K.w || 1.6), dashType: PPT_DASH[K.dash] || 'solid', endArrowType: 'triangle' } }); }
          addT(slide, it.label, { x: X(it.x + 32), y: Y(it.y), w: S(112), h: S(20), color: hex(t.text), fontFace: fontFace(n), fontSize: PT(12), valign: 'middle', margin: 0 });
        }
      } else {
        const L = nodeLayout(n);
        const textOpt = L.text ? { color: hex(L.text.color), fontFace: fontFace(n), fontSize: PT(L.text.size), bold: !!L.text.bold, align: L.text.anchor === 'start' ? 'left' : 'center', valign: 'middle', margin: 1 } : null;
        const shp = n.type === 'equip' ? pptx.ShapeType.roundRect : SHP_DEF[n.type] ? (pptx.ShapeType[SHP_DEF[n.type].ppt] || SHP_DEF[n.type].ppt) : null;
        const st = stStyle(n, t);
        const cg = n.type === 'roundL' || n.type === 'roundR' ? { points: sideRoundPts(n.type, S(n.w), S(n.h), S(sideR(n.w, n.h))) } : {};
        const drawBox = n.type === 'note' || (shp && (!n.noBox || n.status !== 'base'));
        const boxStyle = n.type === 'note' ? { fill: { color: hex(t.note.fill) }, line: { color: hex(t.note.stroke), width: LW(1) } } : { fill: { color: hex(st.fill) }, line: { color: hex(st.stroke), width: LW(1.2) } };
        if (!L.icon && L.text) {
          /* 无框文字（标题等）：画布上不折行，PPT 中按实测宽度放宽文本框，避免折行叠字 */
          let tb = base;
          if (!drawBox) { const mw = Math.max(...L.text.lines.map(s => measure(s, L.text.size, L.text.bold))) + 12; if (mw > n.w) { const dx = L.text.anchor === 'start' ? 0 : (mw - n.w) / 2; tb = { ...base, x: X(n.x - dx), w: S(mw) }; } }
          addT(slide, txt(L.text.lines), { ...tb, ...(drawBox ? {} : { wrap: false }), ...textOpt, ...(drawBox ? { shape: n.type === 'note' ? pptx.ShapeType.rect : shp, ...cg, ...boxStyle, ...(n.type === 'round' || n.type === 'equip' ? { rectRadius: S(Math.min(10, n.h / 3)) } : {}) } : {}), ...(n.type === 'note' ? { margin: 6 } : {}) });
        } else {
          if (drawBox) slide.addShape(shp, { ...base, ...cg, ...boxStyle, ...(n.type === 'round' || n.type === 'equip' ? { rectRadius: S(Math.min(10, n.h / 3)) } : {}) });
          if (L.icon) { const asp = (L.icon.w || L.icon.s) / (L.icon.h || L.icon.s); const png = await getIcon(L.icon.uri + (asp !== 1 ? '#a' + asp.toFixed(3) : '')); if (png) slide.addImage({ data: png.replace(/^data:/, ''), x: X(L.icon.x), y: Y(L.icon.y), w: S(L.icon.w || L.icon.s), h: S(L.icon.h || L.icon.s) }); }
          if (L.text) { const [bx, by, bw, bh] = L.text.box; addT(slide, txt(L.text.lines), { x: X(bx), y: Y(by), w: S(bw), h: S(Math.max(bh, L.text.lines.length * L.text.size * 1.38)), ...textOpt, margin: 0 }); }
        }
      }
      const tg = codeTagOf(n, p);
      if (tg) addT(slide, tg.text, { x: X(tg.x), y: Y(tg.y), w: S(tg.w), h: S(tg.h), shape: pptx.ShapeType.roundRect, rectRadius: 0.02, fill: { color: hex(tg.fill) }, line: { color: hex(tg.stroke), width: LW(0.7) }, color: hex(tg.color), fontFace: fontFace(n), fontSize: PT(tg.size), bold: true, align: 'center', valign: 'middle', margin: 0, wrap: false });
    }
    for (const l of p.links) {
      const pts = linkPoints(l, p); if (!pts) continue;
      const K = LINK_KINDS[l.kind] || LINK_KINDS.plain, c = hex(t.link[l.kind]);
      const line = { color: c, width: LW(K.w || 1.6), dashType: PPT_DASH[K.dash] || 'solid' };
      if (l.dir !== 'none') line.endArrowType = 'triangle';
      if (l.dir === 'both') line.beginArrowType = 'triangle';
      if (PPT_CUSTGEOM) {
        /* one freeform per link: polyline + quadratic hops (line jumps), arrowheads on the outline ends */
        const ops = linkOps(routesFor(p).get(l.id)), R = JUMP_R;
        const xsA = [], ysA = [];
        for (const o of ops) { if (o[0] === 'M' || o[0] === 'L') { xsA.push(o[1]); ysA.push(o[2]); } else { xsA.push(o[1], o[2]); ysA.push(o[3], o[3] - (o[0] === 'J' ? R : 0)); } }
        let x0 = Math.min(...xsA), x1 = Math.max(...xsA), y0 = Math.min(...ysA), y1 = Math.max(...ysA);
        const eps = 0.012 / f; if (x1 - x0 < 2 * eps) { x0 -= eps; x1 += eps; } if (y1 - y0 < 2 * eps) { y0 -= eps; y1 += eps; }
        const rx = v => +((v - x0) * f).toFixed(4), ry = v => +((v - y0) * f).toFixed(4), gp = [];
        for (const o of ops) {
          if (o[0] === 'M') gp.push({ x: rx(o[1]), y: ry(o[2]) });
          else if (o[0] === 'L') gp.push({ x: rx(o[1]), y: ry(o[2]) });
          else if (o[0] === 'J') { const [, a1, a2, yy] = o, cx = (a1 + a2) / 2; gp.push({ x: rx(a1), y: ry(yy) }, { x: rx(cx), y: ry(yy - R), curve: { type: 'quadratic', x1: rx(a1), y1: ry(yy - R) } }, { x: rx(a2), y: ry(yy), curve: { type: 'quadratic', x1: rx(a2), y1: ry(yy - R) } }); }
          else if (o[0] === 'G') { const k = o[2] > o[1] ? 1.5 : -1.5; gp.push({ x: rx(o[1] + k), y: ry(o[3]) }, { x: rx(o[2] - k), y: ry(o[3]), moveTo: true }); }
        }
        slide.addShape(pptx.ShapeType.custGeom, { x: X(x0), y: Y(y0), w: S(x1 - x0), h: S(y1 - y0), points: gp, line });
      } else {
        for (let i = 0; i < pts.length - 1; i++) {
          const a = pts[i], z = pts[i + 1], ln = { ...line };
          if (i !== pts.length - 2) delete ln.endArrowType; if (i !== 0) delete ln.beginArrowType;
          slide.addShape(pptx.ShapeType.line, { x: X(Math.min(a.x, z.x)), y: Y(Math.min(a.y, z.y)), w: S(Math.abs(z.x - a.x)), h: S(Math.abs(z.y - a.y)), flipH: z.x < a.x, flipV: z.y < a.y, line: ln });
        }
      }
      for (const pill of linkPills(l, p)) { const w = measure(pill.text, 11.5) + 10; addT(slide, pill.text, { x: X(pill.pos.x - w / 2), y: Y(pill.pos.y - 9), w: S(w), h: S(18), fill: { color: hex(t.bg) }, color: c, fontFace: fontFace(null), fontSize: PT(11.5), align: 'center', valign: 'middle', margin: 0, wrap: false }); }
    }
    cur = saved;
  }
  const blob = await pptx.write({ outputType: 'blob' });
  saveFile(docExportName('pptx'), blob);
}

/* Visio (.vsdx, Visio 2013+): shapes with geometry, text, fills; links as polylines with arrowheads; icons embedded as PNG */
async function exportVSDX(pageList) {
  if (typeof JSZip === 'undefined') { toast('压缩组件未加载'); return; }
  toast('正在生成 Visio…');
  const t = T(), zip = new JSZip(), NS = 'http://schemas.microsoft.com/office/visio/2012/main', RNS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships';
  const pages = pageList || pagesInOrder(); let imgN = 0; const iconCache = new Map();
  const xs = s => esc(s).replace(/\n/g, '&#10;');
  const cell = (n, v, u) => `<Cell N='${n}' V='${v}'${u ? ` U='${u}'` : ''}/>`;
  const num = v => (+v).toFixed(6);
  const pageXml = [], pageRels = [];
  for (const p of pages) {
    const saved = cur; cur = p.id;
    const b = contentBBox(p), pad = 20, f = 1 / 96, PW = (b.w + pad * 2) * f, PH = (b.h + pad * 2) * f;
    const X = v => (v - b.x + pad) * f, Y = v => PH - (v - b.y + pad) * f;
    let sid = 1; const shapes = []; const rels = [];
    const charSec = (size, color, bold, face) => `<Section N='Character'><Row IX='0'>${cell('Font', face || fontFace(null))}${cell('Color', color)}${cell('Size', num(size * 0.75 / 72), 'PT')}${cell('Style', bold ? 1 : 0)}</Row></Section>`;
    const paraSec = al => `<Section N='Paragraph'><Row IX='0'>${cell('HorzAlign', al === 'left' ? 0 : 1)}</Row></Section>`;
    const rectGeom = (w, h) => `<Section N='Geometry' IX='0'>${cell('NoFill', 0)}${cell('NoLine', 0)}<Row T='MoveTo' IX='1'>${cell('X', 0)}${cell('Y', 0)}</Row><Row T='LineTo' IX='2'>${cell('X', num(w))}${cell('Y', 0)}</Row><Row T='LineTo' IX='3'>${cell('X', num(w))}${cell('Y', num(h))}</Row><Row T='LineTo' IX='4'>${cell('X', 0)}${cell('Y', num(h))}</Row><Row T='LineTo' IX='5'>${cell('X', 0)}${cell('Y', 0)}</Row></Section>`;
    const geomFor = (type, w, h) => {
      if (type === 'ellipse') return `<Section N='Geometry' IX='0'>${cell('NoFill', 0)}${cell('NoLine', 0)}<Row T='Ellipse' IX='1'>${cell('X', num(w / 2))}${cell('Y', num(h / 2))}${cell('A', num(w))}${cell('B', num(h / 2))}${cell('C', num(w / 2))}${cell('D', num(h))}</Row></Section>`;
      if (type === 'diamond') return `<Section N='Geometry' IX='0'>${cell('NoFill', 0)}${cell('NoLine', 0)}<Row T='MoveTo' IX='1'>${cell('X', num(w / 2))}${cell('Y', 0)}</Row><Row T='LineTo' IX='2'>${cell('X', num(w))}${cell('Y', num(h / 2))}</Row><Row T='LineTo' IX='3'>${cell('X', num(w / 2))}${cell('Y', num(h))}</Row><Row T='LineTo' IX='4'>${cell('X', 0)}${cell('Y', num(h / 2))}</Row><Row T='LineTo' IX='5'>${cell('X', num(w / 2))}${cell('Y', 0)}</Row></Section>`;
      if (GEO[type] && type !== 'rect') {
        /* sampled outline from GEO (px) → Visio local inches, y up; fill subpaths share one section (even-odd holes), extra strokes in a NoFill section */
        const g = shapeGeom(type, w / f, h / f), gx = v => num(v * f), gy = v => num(h - v * f);
        let sec = `<Section N='Geometry' IX='0'>${cell('NoFill', 0)}${cell('NoLine', 0)}`, ix = 1;
        for (const pl of g.fill) { pl.concat([pl[0]]).forEach((q, i) => { sec += `<Row T='${i ? 'LineTo' : 'MoveTo'}' IX='${ix++}'>${cell('X', gx(q[0]))}${cell('Y', gy(q[1]))}</Row>`; }); }
        sec += '</Section>';
        g.lines.forEach((pl, k) => { sec += `<Section N='Geometry' IX='${k + 1}'>${cell('NoFill', 1)}${cell('NoLine', 0)}`; pl.forEach((q, i) => { sec += `<Row T='${i ? 'LineTo' : 'MoveTo'}' IX='${i + 1}'>${cell('X', gx(q[0]))}${cell('Y', gy(q[1]))}</Row>`; }); sec += '</Section>'; });
        return sec;
      }
      return rectGeom(w, h);
    };
    const box = (x, y, w, h, o) => {
      const W = w * f, H = h * f;
      let s = `<Shape ID='${sid++}' Type='Shape' LineStyle='0' FillStyle='0' TextStyle='0'>${cell('PinX', num(X(x) + W / 2))}${cell('PinY', num(Y(y) - H / 2))}${cell('Width', num(W))}${cell('Height', num(H))}${cell('LocPinX', num(W / 2))}${cell('LocPinY', num(H / 2))}${cell('Angle', 0)}`;
      if (o.fill) s += cell('FillForegnd', o.fill) + cell('FillPattern', 1); else s += cell('FillPattern', 0);
      if (o.line) s += cell('LineColor', o.line) + cell('LineWeight', num((o.lw || 1) * 0.75 / 72), 'PT') + cell('LinePattern', 1); else s += cell('LinePattern', 0);
      if (o.round) s += cell('Rounding', num(o.round * f));
      s += cell('VerticalAlign', o.valign ?? 1) + cell('LeftMargin', num(2 * f)) + cell('RightMargin', num(2 * f)) + cell('TopMargin', num(1 * f)) + cell('BottomMargin', num(1 * f));
      if (o.text != null && o.type && GEO[o.type] && o.type !== 'rect') {
        const ib = shapeGeom(o.type, w, h).inner, TW = Math.max(ib[2], 8) * f, TH = Math.max(ib[3], 8) * f;
        s += cell('TxtPinX', num((ib[0] + ib[2] / 2) * f)) + cell('TxtPinY', num(H - (ib[1] + ib[3] / 2) * f)) + cell('TxtWidth', num(TW)) + cell('TxtHeight', num(TH)) + cell('TxtLocPinX', num(TW / 2)) + cell('TxtLocPinY', num(TH / 2)) + cell('TxtAngle', 0);
      }
      if (o.vert) s += `<Section N='TextBlock'>${cell('TextDirection', 1)}</Section>`;
      if (o.text != null) s += charSec(o.size || 13, o.color || '#000000', o.bold, o.face) + paraSec(o.align);
      s += geomFor(o.type || 'rect', W, H);
      if (o.text != null) s += `<Text>${xs(o.text)}</Text>`;
      return s + '</Shape>';
    };
    for (const n of drawOrder(p)) {
      if (n.type === 'band') {
        const st = stStyle(n, t);
        shapes.push(box(n.x, n.y, n.w, n.h, { fill: n.fill || t.band.fill, line: t.band.stroke, lw: 1.5 }));
        shapes.push(box(n.x, n.y, BAND_TW, n.h, { fill: n.status === 'base' ? t.band.titleFill : st.stroke, text: n.text, size: 15, bold: true, color: t.band.titleText, vert: true, face: fontFace(n) }));
      } else if (n.type === 'lane') {
        shapes.push(box(n.x, n.y, n.w, n.h, { fill: n.fill || t.lane.fill, line: t.lane.stroke }));
        shapes.push(box(n.x, n.y, laneTW(n), n.h, { text: n.text, size: 13.5, bold: true, color: t.lane.titleText, face: fontFace(n) }));
      } else if (n.type === 'group') {
        const st = stStyle(n, t);
        shapes.push(box(n.x, n.y, n.w, n.h, { fill: st.fill === t.box.fill ? t.group.fill : st.fill, line: st.stroke === t.box.stroke ? t.group.stroke : st.stroke, lw: 1.3, round: 6 }));
        shapes.push(box(n.x, n.y, n.w, GROUP_TH, { fill: n.status === 'base' ? t.group.titleFill : st.title, text: n.text, size: 12.5, bold: true, color: t.group.titleText, face: fontFace(n) }));
      } else if (n.type === 'tblock') {
        if (window.Std) for (const c of Std.tblockCells(n, p)) shapes.push(box(c.x, c.y, c.w, c.h, { fill: c.fill || null, line: c.stroke, lw: c.lw, ...(c.text ? { text: c.text, size: c.size, bold: c.bold, color: c.color, align: c.align, face: fontFace(n) } : {}) }));
      } else if (n.type === 'legend') {
        const items = legendLayout(n, p);
        shapes.push(box(n.x, n.y, n.w, n.h, { fill: t.note.fill, line: t.note.stroke }));
        for (const it of items) {
          if (it.kind === 'st') { const ss = it.s === 'base' ? t.box : t.st[it.s]; shapes.push(box(it.x, it.y + 3, 26, 14, { fill: ss.fill, line: ss.stroke })); }
          else shapes.push(polyShape([{ x: it.x, y: it.y + 10 }, { x: it.x + 27, y: it.y + 10 }], t.link[it.k], LINK_KINDS[it.k], 'one'));
          shapes.push(box(it.x + 32, it.y, 112, 20, { text: it.label, size: 12, color: t.text, align: 'left', face: fontFace(n) }));
        }
      } else {
        const L = nodeLayout(n), st = stStyle(n, t);
        const drawBox = n.type === 'note' || (n.type !== 'text' && (!n.noBox || n.status !== 'base'));
        const bs = n.type === 'note' ? { fill: t.note.fill, line: t.note.stroke } : drawBox ? { fill: st.fill, line: st.stroke, lw: 1.2, round: (n.type === 'round' || n.type === 'equip') ? Math.min(10, n.h / 3) : 0, type: n.type } : {};
        if (!L.icon && L.text) shapes.push(box(n.x, n.y, n.w, n.h, { ...bs, text: L.text.lines.join('\n'), size: L.text.size, bold: L.text.bold, color: L.text.color, align: L.text.anchor === 'start' ? 'left' : 'center', face: fontFace(n) }));
        else {
          if (drawBox) shapes.push(box(n.x, n.y, n.w, n.h, bs));
          if (L.icon) {
            const asp = (L.icon.w || L.icon.s) / (L.icon.h || L.icon.s), ik = L.icon.uri + (asp !== 1 ? '#a' + asp.toFixed(3) : '');
            let png = iconCache.get(ik); if (png === undefined) { png = await iconPNG(ik); iconCache.set(ik, png); }
            if (png) {
              imgN++; const fn = `image${imgN}.png`; zip.file('visio/media/' + fn, png.split(',')[1], { base64: true });
              const rid = 'rId' + (rels.length + 1); rels.push(`<Relationship Id='${rid}' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/image' Target='../media/${fn}'/>`);
              const W = (L.icon.w || L.icon.s) * f, HH = (L.icon.h || L.icon.s) * f;
              shapes.push(`<Shape ID='${sid++}' Type='Foreign' LineStyle='0' FillStyle='0' TextStyle='0'>${cell('PinX', num(X(L.icon.x) + W / 2))}${cell('PinY', num(Y(L.icon.y) - HH / 2))}${cell('Width', num(W))}${cell('Height', num(HH))}${cell('LocPinX', num(W / 2))}${cell('LocPinY', num(HH / 2))}${cell('ImgOffsetX', 0)}${cell('ImgOffsetY', 0)}${cell('ImgWidth', num(W))}${cell('ImgHeight', num(HH))}${cell('LinePattern', 0)}${cell('FillPattern', 0)}<Section N='Geometry' IX='0'>${cell('NoFill', 1)}${cell('NoLine', 1)}${cell('NoShow', 1)}<Row T='MoveTo' IX='1'>${cell('X', 0)}${cell('Y', 0)}</Row><Row T='LineTo' IX='2'>${cell('X', num(W))}${cell('Y', 0)}</Row><Row T='LineTo' IX='3'>${cell('X', num(W))}${cell('Y', num(HH))}</Row><Row T='LineTo' IX='4'>${cell('X', 0)}${cell('Y', num(HH))}</Row><Row T='LineTo' IX='5'>${cell('X', 0)}${cell('Y', 0)}</Row></Section><ForeignData ForeignType='Bitmap' CompressionType='PNG'><Rel r:id='${rid}'/></ForeignData></Shape>`);
            }
          }
          if (L.text) { const [bx, by, bw, bh] = L.text.box; shapes.push(box(bx, by, bw, Math.max(bh, 16), { text: L.text.lines.join('\n'), size: L.text.size, bold: L.text.bold, color: L.text.color, face: fontFace(n) })); }
        }
      }
      const tg = codeTagOf(n, p);
      if (tg) shapes.push(box(tg.x, tg.y, tg.w, tg.h, { fill: tg.fill, line: tg.stroke, lw: 0.7, round: 2, text: tg.text, size: tg.size, bold: true, color: tg.color, face: fontFace(n) }));
    }
    function polyShape(pts, color, K, dir, ops) {
      ops = ops || pts.map((q, i) => [i ? 'L' : 'M', q.x, q.y]);
      const xsP = [], ysP = [];
      for (const o of ops) { if (o[0] === 'M' || o[0] === 'L') { xsP.push(X(o[1])); ysP.push(Y(o[2])); } else { xsP.push(X(o[1]), X(o[2])); ysP.push(Y(o[3]), Y(o[3] - (o[0] === 'J' ? JUMP_R : 0))); } }
      const x0 = Math.min(...xsP), x1 = Math.max(...xsP), y0 = Math.min(...ysP), y1 = Math.max(...ysP);
      const W = Math.max(x1 - x0, 0.0001), H = Math.max(y1 - y0, 0.0001);
      const gx = v => num(X(v) - x0), gy = v => num(Y(v) - y0);
      let g = `<Section N='Geometry' IX='0'>${cell('NoFill', 1)}${cell('NoLine', 0)}`, ix = 1;
      const row = (t, x, y, extra = '') => { g += `<Row T='${t}' IX='${ix++}'>${cell('X', gx(x))}${cell('Y', gy(y))}${extra}</Row>`; };
      for (const o of ops) {
        if (o[0] === 'M') row('MoveTo', o[1], o[2]);
        else if (o[0] === 'L') row('LineTo', o[1], o[2]);
        else if (o[0] === 'J') { row('LineTo', o[1], o[3]); row('EllipticalArcTo', o[2], o[3], cell('A', gx((o[1] + o[2]) / 2)) + cell('B', gy(o[3] - JUMP_R)) + cell('C', 0) + cell('D', num(o[4] / JUMP_R))); }
        else if (o[0] === 'G') { const k = o[2] > o[1] ? 1.5 : -1.5; row('LineTo', o[1] + k, o[3]); row('MoveTo', o[2] - k, o[3]); }
      }
      g += '</Section>';
      return `<Shape ID='${sid++}' Type='Shape' LineStyle='0' FillStyle='0' TextStyle='0'>${cell('PinX', num(x0 + W / 2))}${cell('PinY', num(y0 + H / 2))}${cell('Width', num(W))}${cell('Height', num(H))}${cell('LocPinX', num(W / 2))}${cell('LocPinY', num(H / 2))}${cell('LineColor', color)}${cell('LineWeight', num((K.w || 1.6) * 0.75 / 72), 'PT')}${cell('LinePattern', VSD_PAT[K.dash] || 1)}${cell('FillPattern', 0)}${cell('EndArrow', dir !== 'none' ? 4 : 0)}${cell('BeginArrow', dir === 'both' ? 4 : 0)}${cell('EndArrowSize', 1)}${cell('BeginArrowSize', 1)}${g}</Shape>`;
    }
    for (const l of p.links) {
      const pts = linkPoints(l, p); if (!pts) continue;
      const K = LINK_KINDS[l.kind] || LINK_KINDS.plain;
      shapes.push(polyShape(pts, t.link[l.kind], K, l.dir, linkOps(routesFor(p).get(l.id))));
      for (const pill of linkPills(l, p)) { const w = measure(pill.text, 11.5) + 10; shapes.push(box(pill.pos.x - w / 2, pill.pos.y - 9, w, 18, { fill: t.bg, text: pill.text, size: 11.5, color: t.link[l.kind], face: fontFace(null) })); }
    }
    pageXml.push({ name: p.name, PW, PH, xml: `<?xml version='1.0' encoding='utf-8' ?>\n<PageContents xmlns='${NS}' xmlns:r='${RNS}' xml:space='preserve'><Shapes>${shapes.join('')}</Shapes></PageContents>` });
    pageRels.push(rels);
    cur = saved;
  }
  zip.file('[Content_Types].xml', `<?xml version='1.0' encoding='utf-8' ?>\n<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'><Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/><Default Extension='xml' ContentType='application/xml'/><Default Extension='png' ContentType='image/png'/><Override PartName='/visio/document.xml' ContentType='application/vnd.ms-visio.drawing.main+xml'/><Override PartName='/visio/pages/pages.xml' ContentType='application/vnd.ms-visio.pages+xml'/>${pageXml.map((_, i) => `<Override PartName='/visio/pages/page${i + 1}.xml' ContentType='application/vnd.ms-visio.page+xml'/>`).join('')}<Override PartName='/visio/windows.xml' ContentType='application/vnd.ms-visio.windows+xml'/><Override PartName='/docProps/core.xml' ContentType='application/vnd.openxmlformats-package.core-properties+xml'/><Override PartName='/docProps/app.xml' ContentType='application/vnd.openxmlformats-officedocument.extended-properties+xml'/></Types>`);
  zip.file('_rels/.rels', `<?xml version='1.0' encoding='utf-8' ?>\n<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'><Relationship Id='rId1' Type='http://schemas.microsoft.com/visio/2010/relationships/document' Target='visio/document.xml'/><Relationship Id='rId2' Type='http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties' Target='docProps/core.xml'/><Relationship Id='rId3' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties' Target='docProps/app.xml'/></Relationships>`);
  zip.file('docProps/core.xml', `<?xml version='1.0' encoding='utf-8' ?>\n<cp:coreProperties xmlns:cp='http://schemas.openxmlformats.org/package/2006/metadata/core-properties' xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:dcterms='http://purl.org/dc/terms/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'><dc:title>${esc(doc.name || '体系图')}</dc:title><dc:creator>经纬织图</dc:creator></cp:coreProperties>`);
  zip.file('docProps/app.xml', `<?xml version='1.0' encoding='utf-8' ?>\n<Properties xmlns='http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'><Application>Microsoft Visio</Application><AppVersion>15.0000</AppVersion></Properties>`);
  zip.file('visio/document.xml', `<?xml version='1.0' encoding='utf-8' ?>\n<VisioDocument xmlns='${NS}' xmlns:r='${RNS}' xml:space='preserve'><DocumentSettings TopPage='0' DefaultTextStyle='0' DefaultLineStyle='0' DefaultFillStyle='0' DefaultGuideStyle='0'>${cell('GlueSettings', 9)}${cell('SnapSettings', 65847)}</DocumentSettings><Colors><ColorEntry IX='0' RGB='#000000'/><ColorEntry IX='1' RGB='#FFFFFF'/></Colors><FaceNames>${faceNamesXml()}</FaceNames><StyleSheets><StyleSheet ID='0' NameU='No Style' IsCustomNameU='1' Name='No Style' IsCustomName='1'>${cell('EnableLineProps', 1)}${cell('EnableFillProps', 1)}${cell('EnableTextProps', 1)}${cell('HideForApply', 0)}${cell('LineWeight', '0.01041666666666667')}${cell('LineColor', 0)}${cell('LinePattern', 1)}${cell('Rounding', 0)}${cell('EndArrowSize', 2)}${cell('BeginArrow', 0)}${cell('EndArrow', 0)}${cell('LineCap', 0)}${cell('BeginArrowSize', 2)}${cell('LineColorTrans', 0)}${cell('FillForegnd', 1)}${cell('FillBkgnd', 0)}${cell('FillPattern', 1)}${cell('FillForegndTrans', 0)}${cell('FillBkgndTrans', 0)}${cell('LeftMargin', 0)}${cell('RightMargin', 0)}${cell('TopMargin', 0)}${cell('BottomMargin', 0)}${cell('VerticalAlign', 1)}${cell('TextBkgnd', 0)}${cell('TextDirection', 0)}<Section N='Character'><Row IX='0'>${cell('Font', fontFace(null))}${cell('Color', 0)}${cell('Style', 0)}${cell('Size', '0.1666666666666667')}</Row></Section><Section N='Paragraph'><Row IX='0'>${cell('HorzAlign', 1)}</Row></Section></StyleSheet></StyleSheets></VisioDocument>`);
  zip.file('visio/_rels/document.xml.rels', `<?xml version='1.0' encoding='utf-8' ?>\n<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'><Relationship Id='rId1' Type='http://schemas.microsoft.com/visio/2010/relationships/pages' Target='pages/pages.xml'/><Relationship Id='rId2' Type='http://schemas.microsoft.com/visio/2010/relationships/windows' Target='windows.xml'/></Relationships>`);
  zip.file('visio/windows.xml', `<?xml version='1.0' encoding='utf-8' ?>\n<Windows xmlns='${NS}' xmlns:r='${RNS}' ClientWidth='1600' ClientHeight='900'><Window ID='0' WindowType='Drawing' WindowState='1073741824' ViewScale='-1' ViewCenterX='0' ViewCenterY='0' Page='0'><ShowRulers>1</ShowRulers><ShowGrid>1</ShowGrid></Window></Windows>`);
  zip.file('visio/pages/pages.xml', `<?xml version='1.0' encoding='utf-8' ?>\n<Pages xmlns='${NS}' xmlns:r='${RNS}' xml:space='preserve'>${pageXml.map((pg, i) => `<Page ID='${i}' NameU='Page-${i + 1}' Name='${esc(pg.name)}' ViewScale='-1'><PageSheet LineStyle='0' FillStyle='0' TextStyle='0'>${cell('PageWidth', num(pg.PW))}${cell('PageHeight', num(pg.PH))}${cell('ShdwOffsetX', 0)}${cell('ShdwOffsetY', 0)}${cell('PageScale', 1, 'IN_F')}${cell('DrawingScale', 1, 'IN_F')}${cell('DrawingSizeType', 0)}${cell('DrawingScaleType', 0)}${cell('InhibitSnap', 0)}${cell('PrintPageOrientation', pg.PW > pg.PH ? 2 : 1)}</PageSheet><Rel r:id='rId${i + 1}'/></Page>`).join('')}</Pages>`);
  zip.file('visio/pages/_rels/pages.xml.rels', `<?xml version='1.0' encoding='utf-8' ?>\n<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>${pageXml.map((_, i) => `<Relationship Id='rId${i + 1}' Type='http://schemas.microsoft.com/visio/2010/relationships/page' Target='page${i + 1}.xml'/>`).join('')}</Relationships>`);
  pageXml.forEach((pg, i) => {
    zip.file(`visio/pages/page${i + 1}.xml`, pg.xml);
    if (pageRels[i].length) zip.file(`visio/pages/_rels/page${i + 1}.xml.rels`, `<?xml version='1.0' encoding='utf-8' ?>\n<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>${pageRels[i].join('')}</Relationships>`);
  });
  const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', mimeType: 'application/vnd.ms-visio.drawing' });
  saveFile(docExportName('vsdx'), blob);
}
function projectJSON() { return JSON.stringify({ format: 'hongtu', version: 1, doc }, null, 0); }
function projectFileName(raw) {
  let n = String(raw || '').replace(/[\\/:*?"<>|]/g, '').trim();
  if (!n) return '';
  if (!/\.jingwei\.json$/i.test(n)) n = /\.json$/i.test(n) ? n.replace(/\.json$/i, '.jingwei.json') : n + '.jingwei.json';
  return n;
}
function closeSaveAs() { const x = $('#saveas'); if (x) x.style.display = 'none'; }
function afterProjectSave(p) {
  Promise.resolve(p).then(function (ok) { if (ok && window.Backup) Backup.observeSave(); });
}
function confirmSaveAs() {
  const name = projectFileName($('#saveas-name') ? $('#saveas-name').value : '');
  if (!name) return;
  closeSaveAs();
  rememberShelf(name);
  afterProjectSave(saveFile(name, projectJSON()));
}
function saveProject() { rememberShelf(); afterProjectSave(saveFile(projectFileDefault(), projectJSON())); }
function saveProjectAs() {
  const box = $('#saveas'); if (!box) return;
  const inp = $('#saveas-name');
  if (inp) inp.value = projectFileDefault();
  box.style.display = 'flex';
  setTimeout(() => { if (inp) { inp.focus(); inp.select(); } }, 0);
}
function refreshDocTitle() {
  if (typeof window.jwRefreshTitle === 'function') { window.jwRefreshTitle(); return; }
  document.title = (doc && doc.name) ? doc.name + ' - 经纬织图' : '经纬织图';
}
/* ---------- header wiring ---------- */
function closeMenus() {
  document.querySelectorAll('.menu.open').forEach(m => m.classList.remove('open'));
  const ctx = document.getElementById('ctx');
  if (ctx) ctx.style.display = 'none';
}
$('#b-export').onclick = e => { e.stopPropagation(); $('#m-export').classList.toggle('open'); };
document.addEventListener('click', e => { if (!e.target.closest('.menu')) closeMenus(); });
$('#m-export .dd').addEventListener('click', async e => {
  const b = e.target.closest('[data-exp]'); if (!b) return; closeMenus();
  try {
    const k = b.dataset.exp;
    if (k === 'png') await exportPNG(2, false);
    if (k === 'png4') await exportPNG(4, false);
    if (k === 'pngbg') await exportPNG(2, true);
    if (k === 'pngrep') { if (window.Compact) await Compact.exportReportPNG(); else toast('排版模块未加载'); }
    if (k === 'svg') saveFile(fname('svg'), exportSVGString(P(), false).str);
    if (k === 'pptx') await exportPPTX();
    if (k === 'vsdx') await exportVSDX();
    if (k === 'drawio') { if (window.DrawIO) await DrawIO.exportFile(); else toast('draw.io 模块未加载'); }
    if (k === 'allpptx') await exportPPTX();
    if (k === 'allpng') await exportHierarchy('png');
    if (k === 'allsvg') await exportHierarchy('svg');
    if (k === 'allvsdx') await exportHierarchy('vsdx');
    if (k === 'alldrawio') await exportHierarchy('drawio');
  } catch (err) { console.error(err); toast('导出失败：' + (err.message || err)); }
});
$('#b-undo').onclick = undo; $('#b-redo').onclick = redo;
$('#b-beauty').onclick = doBeautify;
$('#b-form') && ($('#b-form').onclick = () => window.Combo ? Combo.open(sel.size === 1 ? nodeById([...sel][0]) : null) : toast('复合图标模块未加载'));
$('#b-cross').onclick = doReduce;
$('#b-std') && ($('#b-std').onclick = () => window.Std ? Std.openCheck() : toast('规范模块未加载'));
$('#b-text').onclick = () => callMod('openTextGen', '文字成图');
$('#b-ref').onclick = () => callMod('openRefGen', '参照生成');
$('#b-conv') && ($('#b-conv').onclick = () => callMod('openConvert', '格式转换'));
$('#b-tpl').onclick = () => callMod('openTemplates', '模板');
$('#b-help').onclick = openHelp;
$('#help-close').onclick = closeHelp;
$('#help').addEventListener('click', e => { if (e.target.id === 'help') closeHelp(); });
$('#b-theme').innerHTML = Object.entries(THEMES).map(([k, v]) => `<option value="${k}">${v.name}</option>`).join('');
$('#b-theme').onchange = e => setTheme(e.target.value);
$('#b-save').onclick = saveProject;
$('#b-saveas').onclick = saveProjectAs;
$('#saveas-ok').onclick = confirmSaveAs;
$('#saveas-cancel').onclick = closeSaveAs;
$('#saveas-x').onclick = closeSaveAs;
$('#saveas').addEventListener('click', e => { if (e.target.id === 'saveas') closeSaveAs(); });
$('#b-open').onclick = () => $('#f-open').click();
$('#f-open').addEventListener('change', e => {
  const f = e.target.files[0]; if (!f) return; const rd = new FileReader();
  e.target.value = '';
  if (/\.(pptx|vsdx|ppt|vsd|drawio|xml)$/i.test(f.name)) { openForeign(f); return; }
  rd.onload = () => { try { const o = JSON.parse(rd.result); const d = o.doc || o; if (!d.pages || !d.pages.root) throw 0; checkpoint(); loadDoc(d); shelfId = null; rememberShelf(f.name); toast('已打开：' + f.name); } catch (_) { toast('无法识别该文件，请选择织图工程文件（.json）、PowerPoint（.pptx）或 Visio（.vsdx）'); } };
  rd.readAsText(f);
});
/* PowerPoint／Visio → 可编辑的织图文档（每张幻灯片／每个 Visio 页面一页，首页为总图，其余页挂在总图右侧入口框下） */
async function openForeign(f) {
  const dio = /\.(drawio|xml)$/i.test(f.name);
  if (dio ? !window.DrawIO : !window.Importer) { toast('导入模块未加载'); return; }
  toast('正在解析 ' + f.name + ' …');
  try {
    const r = dio ? await DrawIO.fromFile(f) : await Importer.fromFile(f);
    if (!r.pages.length) { toast('文件中没有可识别的图形'); return; }
    checkpoint();
    const d = { name: f.name.replace(/\.[^.]+$/, ''), theme: doc.theme, statusLabels: { ...doc.statusLabels }, custom: Object.assign({}, r.custom || {}), lastKind: 'data', pages: {} };
    if (r.docSettings) { for (const [k, v] of Object.entries(r.docSettings)) if (v != null) d[k] = v; if (!THEMES[d.theme]) d.theme = doc.theme; }
    const [first, ...rest] = r.pages; const oldRoot = first.id; first.id = 'root'; d.pages.root = first;
    for (const p of r.pages) for (const n of p.nodes) if (n.sub === oldRoot) n.sub = 'root';
    const linked = new Set(r.pages.flatMap(p => p.nodes.map(n => n.sub).filter(Boolean)));
    rest.forEach(p => d.pages[p.id] = p);
    const orphan = rest.filter(p => !linked.has(p.id));
    if (orphan.length) {
      const b = first.nodes.length ? first.nodes.reduce((a, n) => ({ x1: Math.max(a.x1, n.x + n.w), y0: Math.min(a.y0, n.y) }), { x1: -1e9, y0: 1e9 }) : { x1: 0, y0: 0 };
      orphan.forEach((p, i) => { first.nodes.push(mkNode({ type: 'round', text: p.name || ('第 ' + (i + 2) + ' 页'), x: snapv(b.x1 + 60), y: snapv(b.y0 + i * 56), w: 180, h: 40, sub: p.id })); });
    }
    loadDoc(d);
    toast(`已导入 ${f.name}：${r.pages.length} 页${orphan.length ? '（其余页面在总图右侧入口框中，点框右上角 ⊕ 进入）' : ''}${r.warnings && r.warnings.length ? '；' + r.warnings.length + ' 条提示见控制台' : ''}，可按 Ctrl+Shift+F 一键美化`);
    if (r.warnings && r.warnings.length) console.info('导入提示', r.warnings);
  } catch (err) { console.error(err); toast('导入失败：' + friendlyErr(err)); }
}
$('#b-new').onclick = () => {
  checkpoint();
  const d = { name: '新建体系图', layout: doc.layout, theme: doc.theme, statusLabels: { ...doc.statusLabels }, custom: doc.custom, pages: { root: { id: 'root', name: '总图', nodes: [], links: [] } } };
  const p = d.pages.root;
  p.nodes.push(mkNode({ type: 'text', role: 'title', text: '体系架构图', size: 22, bold: true, x: 300, y: -60, w: 300, h: 34 }));
  const b = mkNode({ type: 'band', text: '分组', x: 0, y: 0, w: 1000, h: 140 }); p.nodes.push(b);
  p.nodes.push(mkNode({ type: 'lane', text: '第一层', parent: b.id, x: 40, y: 6, w: 950, h: 56 }));
  loadDoc(d); if (window.Compact) Compact.stamp(); beautify(); render(); fit();
};
$('#z-in').onclick = () => { const r = svg.getBoundingClientRect(); zoomAt(view.k * 1.2, r.left + r.width / 2, r.top + r.height / 2); };
$('#z-out').onclick = () => { const r = svg.getBoundingClientRect(); zoomAt(view.k / 1.2, r.left + r.width / 2, r.top + r.height / 2); };
$('#z-fit').onclick = fit;
window.addEventListener('resize', () => applyView());

/* 解压库等英文报错 → 中文说明 */
function friendlyErr(err) {
  const m = String((err && err.message) || err || '');
  if (/zip|central directory|End of data|signature|Corrupted|invalid (stored )?block|unexpected end/i.test(m)) return '文件已损坏或不完整，无法解压（请确认文件能在 Office／Visio 中正常打开，或重新另存一份再试）';
  if (/is not a valid|not well-formed|parsererror|XML/i.test(m)) return '文件内容格式有误，无法解析';
  return m;
}
function loadDoc(d) { for (const pg of Object.values(d.pages || {})) if (pg.view && typeof pg.view === 'object') { pg.cam = pg.view; delete pg.view; } /* page.view = 规范视图类型（字符串）；视口缓存在 page.cam */
  doc = d; doc.custom = doc.custom || {}; doc.statusLabels = doc.statusLabels || { base: '延续', new: '本步新增／重构', key: '重点关注' }; cur = 'root'; stack = ['root']; clearSel(); $('#b-theme').value = doc.theme; renderPalette(); render(); fit(); refreshDocTitle(); if (window.Backup) Backup.observeLoad(); }

const SHELF_KEY = 'hongtu.shelf';
let shelfId = null;
function readShelf() { try { const a = JSON.parse(localStorage.getItem(SHELF_KEY) || '[]'); return Array.isArray(a) ? a : []; } catch (_) { return []; } }
function writeShelf(a) { try { localStorage.setItem(SHELF_KEY, JSON.stringify(a.slice(0, 8))); } catch (_) { } }
function rememberShelf(nameHint) {
  if (window.jwDesk || !doc || !doc.pages) return;
  const raw = String(nameHint || doc.name || (doc.pages.root && doc.pages.root.name) || '未命名');
  const name = raw.replace(/\.jingwei\.json$/i, '').replace(/\.json$/i, '') || '未命名';
  const item = { id: shelfId || ('s' + uid()), name, path: '浏览器本地存储', t: Date.now(), doc: JSON.parse(JSON.stringify(doc)) };
  shelfId = item.id;
  writeShelf([item, ...readShelf().filter(x => x.id !== item.id && x.name !== name)]);
}
function fmtWhen(t) { const d = new Date(t), p = x => String(x).padStart(2, '0'); return isNaN(d.getTime()) ? '' : `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`; }
function editInline(host, value, onCommit) {
  const input = document.createElement('input');
  input.type = 'text'; input.value = value;
  input.addEventListener('click', e => e.stopPropagation());
  input.addEventListener('mousedown', e => e.stopPropagation());
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
    else if (e.key === 'Escape') { e.preventDefault(); input.dataset.cancel = '1'; input.blur(); }
  });
  let done = false;
  input.addEventListener('blur', () => {
    if (done) return; done = true;
    onCommit(input.dataset.cancel || input.value.trim() === value ? null : input.value.trim());
  });
  host.textContent = ''; host.appendChild(input); input.focus(); input.select();
}
function hideWebHist() { const el = $('#jw-webhist'); if (el) el.hidden = true; }
function renderWebHist() {
  if (window.jwDesk) return;
  let el = $('#jw-webhist');
  if (!el) {
    el = document.createElement('div'); el.id = 'jw-webhist'; el.hidden = true;
    el.innerHTML = '<div class="box"><h2>最近工程</h2><div class="list" id="jw-webhist-list"></div><button type="button" id="jw-webhist-go">进入画布</button></div>';
    document.body.appendChild(el);
    el.querySelector('#jw-webhist-go').onclick = hideWebHist;
  }
  const list = readShelf().filter(it => it && it.doc && it.doc.pages && it.doc.pages.root);
  const box = el.querySelector('.list');
  if (!list.length) { el.hidden = true; box.innerHTML = ''; return; }
  el.hidden = false; box.innerHTML = '';
  for (const it of list) {
    const row = document.createElement('div');
    row.className = 'ri'; row.tabIndex = 0;
    row.innerHTML = '<div class="meta"><div class="nm" title="单击改名"></div><div class="dir"></div></div><div class="tm"></div>';
    row.querySelector('.nm').textContent = it.name;
    row.querySelector('.dir').textContent = it.path;
    row.querySelector('.tm').textContent = fmtWhen(it.t);
    row.addEventListener('click', e => {
      if (e.target.closest('.nm') || e.target.closest('input')) return;
      const cur = readShelf().find(x => x.id === it.id);
      if (!cur || !cur.doc) return;
      checkpoint(); shelfId = cur.id; loadDoc(JSON.parse(JSON.stringify(cur.doc))); hideWebHist();
    });
    row.querySelector('.nm').addEventListener('click', e => {
      e.stopPropagation();
      editInline(e.currentTarget, it.name, name => {
        if (!name) { renderWebHist(); return; }
        const a = readShelf(); const hit = a.find(x => x.id === it.id);
        if (hit) { hit.name = name; if (hit.doc) hit.doc.name = name; hit.t = Date.now(); writeShelf(a); if (shelfId === it.id) doc.name = name; }
        renderWebHist();
      });
    });
    box.appendChild(row);
  }
}
renderWebHist();
