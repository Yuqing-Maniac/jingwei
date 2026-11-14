/* ============ 织图 · 作战场景模板 ============
 * 须在 templates.js 之后加载。向 window.TEMPLATES 追加可编辑的想定版式。
 * 只用已有军标（ms:）、已有图标的红蓝涂装、标准箭头、距离箭头和形状。
 */
(function () {
  'use strict';

  function withDoc(d, fn) {
    const sd = doc, sc = cur;
    doc = d; cur = 'root';
    try { return fn(); } finally { doc = sd; cur = sc; }
  }
  function newDoc(name) {
    return {
      name: name, theme: 'report',
      statusLabels: { base: '延续', new: '新增', key: '重点关注' },
      custom: {}, lastKind: 'ctrl',
      pages: { root: { id: 'root', name: '总图', nodes: [], links: [] } }
    };
  }
  function tools(page) {
    const N = o => { const n = mkNode(o); page.nodes.push(n); return n; };
    const L = (a, b, o) => { page.links.push(Object.assign({ id: uid(), from: a.id, to: b.id, dir: 'one', kind: 'ctrl', route: 'ortho', label: '' }, o || {})); };
    return { N: N, L: L };
  }
  function define(id, name, desc, fn) {
    return {
      id: id, name: name, desc: desc, group: '作战场景',
      build: function () {
        const d = newDoc(name);
        return withDoc(d, function () { fn(tools(d.pages.root), d.pages.root); return d; });
      }
    };
  }

  const BLUE = '#1F5FBF', RED = '#C0392B', INK = '#5C6B7A';
  const lib = (key, side) => ({ icon: 'lib:' + key, affiliation: side });
  const ms = sidc => ({ icon: 'ms:' + sidc });
  function equip(N, x, y, text, spec) {
    return N(Object.assign({ type: 'equip', noBox: true, x: x, y: y, w: 108, h: 116, size: 12, text: text }, spec));
  }
  function zone(N, type, x, y, w, h, fill, stroke, extra) {
    return N(Object.assign({ type: type, x: x, y: y, w: w, h: h, text: '', fill: fill, stroke: stroke }, extra || {}));
  }
  function tag(N, x, y, text) {
    return N({ type: 'text', x: x, y: y, w: 180, h: 22, size: 13, bold: true, align: 'left', text: text });
  }
  function stdArrow(N, x, y, w, rot, stroke) {
    const n = N({ type: 'stdArrow', x: x, y: y, w: w, h: 36, text: '', stroke: stroke, sw: 2.4 });
    if (rot) n.rot = rot;
    return n;
  }
  function dimArrow(N, x, y, w, text, stroke) {
    const num = parseFloat(text), unit = String(text || '').replace(/[0-9.\s]/g, '') || 'km';
    return N({ type: 'dimArrow', x: x, y: y, w: w, h: 48, text: '', stroke: stroke || INK, sw: 2, rulerStart: 0, rulerStep: isFinite(num) ? num : 0, rulerGap: Math.max(16, w), rulerMinor: 0, rulerUnit: unit });
  }
  function finish(N, page, title, sub, note, bottom) {
    N({ type: 'text', role: 'title', text: title, size: 22, bold: true, x: 24, y: 8, w: 860, h: 32 });
    N({ type: 'text', role: 'subtitle', text: sub, size: 13, color: 'muted', x: 24, y: 42, w: 980, h: 22 });
    const lg = N({ type: 'legend', role: 'legend', x: 960, y: bottom, w: 220, h: 72 });
    legendLayout(lg, page);
    const nt = N({ type: 'note', role: 'note', size: 12, text: note, x: 24, y: bottom, w: 900, h: 64 });
    nt.w = Math.max(280, lg.x - 36);
    const lines = wrap(note, nt.w - 20, 12);
    nt.h = Math.max(lg.h, lines.length * Math.round(12 * 1.38) + 16);
    lg.h = nt.h;
  }
  const NOTE = '说明：本图为虚构想定。文字、阵营涂装、箭头和距离都可直接修改，不代表真实编制或部署。';

  /* 蓝方在西、红方在东，中间一条接触间隙。 */
  const contact = define('scn-contact', '对峙接触场景', '蓝红两方隔接触间隙对峙，含军标、红蓝涂装、标准箭头与距离箭头', (T, page) => {
    const { N, L } = T;
    zone(N, 'ellipse', 28, 88, 520, 470, '#E7F1FC', BLUE);
    zone(N, 'ellipse', 652, 88, 520, 470, '#FDECEC', RED);
    zone(N, 'sector', 250, 168, 240, 240, '#D6E6FA', BLUE, { sweep: 70 });
    tag(N, 56, 104, '蓝方集结区');
    tag(N, 700, 104, '红方集结区');
    const bcp = equip(N, 56, 150, '蓝方指挥所', lib('command_post', 'blue'));
    equip(N, 300, 210, '蓝方警戒雷达', lib('radar', 'blue'));
    const bin = equip(N, 56, 330, '蓝方步兵', lib('soldier', 'blue'));
    equip(N, 190, 330, '蓝方装甲', lib('tank', 'blue'));
    equip(N, 190, 168, '友方步兵分队', ms('SFGPUCI---'));
    const rcp = equip(N, 980, 150, '红方指挥所', lib('command_post', 'red'));
    equip(N, 820, 168, '红方战斗机', lib('fighter', 'red'));
    equip(N, 700, 220, '红方防空', lib('sam', 'red'));
    const rarm = equip(N, 820, 330, '红方装甲', lib('tank', 'red'));
    equip(N, 980, 330, '对抗方步兵分队', ms('SHGPUCI---'));
    stdArrow(N, 430, 360, 150, 0, BLUE);
    stdArrow(N, 620, 360, 150, 180, RED);
    dimArrow(N, 470, 460, 260, '6 km', INK);
    tag(N, 530, 508, '接触间隙');
    L(bcp, bin, { label: '指令' });
    L(rcp, rarm, { label: '指令' });
    finish(N, page, '蓝红对峙接触想定', '蓝方自西向东，红方自东向西，中间留出接触间隙', NOTE, 590);
  });

  /* 蓝方沿区域巡逻，远端出现红方接触。 */
  const patrol = define('scn-patrol', '区域巡逻场景', '巡逻区、警戒扇区和航线箭头，蓝方平台与红方接触目标', (T, page) => {
    const { N, L } = T;
    zone(N, 'ellipse', 48, 96, 1100, 450, '#F4F7FB', '#7E93AD');
    zone(N, 'sector', 40, 150, 260, 260, '#D6E6FA', BLUE, { sweep: 80 });
    zone(N, 'round', 600, 340, 150, 64, '#FFF8E8', '#C47B2B');
    tag(N, 618, 358, '会合点');
    tag(N, 80, 108, '巡逻区');
    const ship = equip(N, 110, 230, '蓝方驱逐舰', lib('destroyer', 'blue'));
    const boat = equip(N, 110, 390, '蓝方无人艇', lib('usv', 'blue'));
    const quad = equip(N, 360, 150, '蓝方巡逻无人机', lib('uav_quad', 'blue'));
    const male = equip(N, 620, 150, '蓝方察打无人机', lib('uav_male', 'blue'));
    equip(N, 440, 370, '友方巡逻艇', Object.assign(ms('SFSPCPSB--'), { w: 84, h: 92 }));
    equip(N, 980, 360, '对抗方无人艇', ms('10063000001207000000'));
    const redAir = equip(N, 980, 160, '对抗方旋翼机', lib('helicopter', 'red'));
    stdArrow(N, 250, 190, 120, 0, BLUE);
    stdArrow(N, 490, 190, 140, 0, BLUE);
    stdArrow(N, 820, 400, 140, 180, RED);
    dimArrow(N, 240, 450, 180, '4 km', INK);
    dimArrow(N, 660, 450, 280, '12 km', INK);
    L(ship, boat, { kind: 'radio', label: '协同' });
    L(quad, male, { kind: 'radio', label: '接力' });
    L(male, redAir, { kind: 'alarm', label: '发现' });
    finish(N, page, '区域巡逻与接触想定', '蓝方平台沿巡逻区搜索，远端与红方目标接触', NOTE, 580);
  });

  /* 蓝方向东侧要点协同突击。 */
  const assault = define('scn-assault', '要点协同场景', '蓝方分队指向东侧要点，含突击箭头、距离和警戒扇区', (T, page) => {
    const { N, L } = T;
    zone(N, 'rect', 860, 150, 250, 250, '#FFF6E8', '#C47B2B');
    zone(N, 'sector', 200, 120, 220, 220, '#D6E6FA', BLUE, { sweep: 60 });
    tag(N, 910, 168, '要点');
    const ifv = equip(N, 48, 180, '蓝方步战车', lib('ifv', 'blue'));
    const tank = equip(N, 48, 360, '蓝方坦克', lib('tank', 'blue'));
    const helo = equip(N, 250, 150, '蓝方直升机', lib('helicopter', 'blue'));
    const uav = equip(N, 250, 330, '蓝方察打无人机', lib('uav_male', 'blue'));
    equip(N, 168, 470, '蓝方炮兵', lib('sp_howitzer', 'blue'));
    const hcp = equip(N, 960, 190, '对抗方指挥所', ms('SHGPUH----'));
    const harm = equip(N, 780, 250, '对抗方装甲分队', ms('SHGPUCA---'));
    equip(N, 960, 360, '红方防空', lib('sam', 'red'));
    N({ type: 'chevron', x: 430, y: 250, w: 150, h: 48, text: '突击', size: 14, bold: true, fill: '#E7F1FC', stroke: BLUE });
    stdArrow(N, 400, 180, 200, 0, BLUE);
    stdArrow(N, 400, 400, 180, 0, BLUE);
    stdArrow(N, 700, 300, 120, 180, RED);
    dimArrow(N, 620, 470, 240, '8 km', INK);
    L(ifv, helo, { label: '协同' });
    L(tank, uav, { kind: 'radio', label: '指示' });
    L(hcp, harm, { label: '指令' });
    finish(N, page, '要点协同突击想定', '蓝方地面与空中平台指向东侧要点，红方在要点附近组织抗击', NOTE, 600);
  });

  const list = [contact, patrol, assault];
  if (!window.TEMPLATES) window.TEMPLATES = [];
  for (let i = 0; i < list.length; i++) {
    const t = list[i], at = window.TEMPLATES.findIndex(x => x.id === t.id);
    if (at >= 0) window.TEMPLATES[at] = t;
    else window.TEMPLATES.push(t);
  }
})();
