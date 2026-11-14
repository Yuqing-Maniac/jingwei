import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const code = fs.readFileSync(new URL('../app/canvasbg.js', import.meta.url), 'utf8');
const calls = { linear: 0, stops: 0 };

function tiny(tag) {
  return {
    tagName: tag,
    id: '',
    type: '',
    className: '',
    textContent: '',
    title: '',
    value: '',
    style: {},
    disabled: false,
    children: [],
    setAttribute() {},
    appendChild(ch) { this.children.push(ch); return ch; },
    insertBefore(ch) { this.children.push(ch); return ch; },
    addEventListener() {},
    removeChild(ch) { this.children = this.children.filter(x => x !== ch); return ch; },
    get firstChild() { return this.children[0] || null; },
    getContext() { return null; }
  };
}

const document = {
  getElementById() { return null; },
  createElement(tag) { return tiny(tag); },
  body: tiny('body'),
  head: tiny('head'),
  querySelectorAll() { return []; }
};

const context = { console, document };
context.window = context;
vm.createContext(context);
vm.runInContext(code, context, { filename: 'canvasbg.js' });
const CanvasBg = context.window.CanvasBg;
assert.equal(typeof CanvasBg.normalize, 'function', 'window.CanvasBg.normalize');

const messy = CanvasBg.normalize({
  locked: false,
  grad: { kind: 'sweep', angle: 400, stops: [{ at: 2, color: 'blue', opacity: 4 }, { at: -1, color: '#abc', opacity: -3 }] },
  grid: { show: 1, color: 'nope', opacity: 9, gap: 1, persp: 240 }
});
assert.equal(messy.locked, true, 'normalize forces locked');
assert.ok(messy.grad.stops.length >= 2, 'at least two stops');
assert.ok(messy.grad.stops.every(s => /^#[0-9A-F]{6}$/.test(s.color)), 'hex colors');
assert.equal(messy.grid.gap >= 8, true, 'gap at least 8');
assert.equal(messy.grid.persp <= 100, true, 'persp clamped');

const linearPage = {
  canvasBg: {
    grad: {
      kind: 'linear', angle: 0,
      stops: [{ at: 0, color: '#112233', opacity: 1 }, { at: 1, color: '#abcdef', opacity: 0.25 }]
    },
    grid: { show: false, color: '#8899AA', opacity: 1, gap: 40, persp: 0 }
  }
};
const svg = CanvasBg.markup(linearPage, { x: 0, y: 0, w: 200, h: 100 });
assert.match(svg, /linearGradient/, 'linear gradient element');
assert.match(svg, /#112233/, 'first stop color');
assert.match(svg, /#ABCDEF/, 'second stop color');
assert.equal(/data-id=/.test(svg), false, 'background is not a node');
assert.match(svg, /pointer-events="none"/, 'group ignores hits');
const opacities = [...svg.matchAll(/stop-opacity="([^"]+)"/g)].map(m => +m[1]);
assert.ok(opacities.some(v => v < 1), 'a stop-opacity below 1');

function linesOf(markup) {
  return [...markup.matchAll(/<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"/g)].map(m => m.slice(1).map(Number));
}
const box = { x: 10, y: 20, w: 200, h: 100 };
function gridPage(persp) {
  return {
    canvasBg: {
      grad: { kind: 'linear', angle: 0, stops: [{ at: 0, color: '#FFFFFF', opacity: 1 }, { at: 1, color: '#DDDDDD', opacity: 1 }] },
      grid: { show: true, color: '#445566', opacity: 0.5, gap: 40, persp }
    }
  };
}
const flat = linesOf(CanvasBg.markup(gridPage(0), box));
const horizontals = flat.filter(l => l[1] === l[3]);
const verticals = flat.filter(l => l[1] !== l[3]);
assert.ok(horizontals.length >= 2 && verticals.length >= 2, 'both grid directions');
assert.ok(verticals.every(l => l[0] === l[2]), 'persp 0 verticals stay upright');
assert.ok(horizontals.every(l => l[0] === box.x && l[2] === box.x + box.w), 'persp 0 horizontals span the sheet');

const deep = linesOf(CanvasBg.markup(gridPage(100), box));
const h2 = deep.filter(l => l[1] === l[3]).sort((a, b) => a[1] - b[1]);
const v2 = deep.filter(l => l[1] !== l[3]);
const topLen = Math.abs(h2[0][2] - h2[0][0]);
const botLen = Math.abs(h2[h2.length - 1][2] - h2[h2.length - 1][0]);
assert.ok(topLen < botLen, 'persp 100 shortens the far horizontal');
const left = v2.slice().sort((a, b) => Math.min(a[0], a[2]) - Math.min(b[0], b[2]))[0];
const bottomX = left[1] > left[3] ? left[0] : left[2];
const topX = left[1] > left[3] ? left[2] : left[0];
const center = box.x + box.w / 2;
assert.ok(Math.abs(topX - center) < Math.abs(bottomX - center), 'persp 100 pulls the top of the leftmost vertical inward');

const three = {
  grad: {
    kind: 'linear', angle: 90,
    stops: [{ at: 0, color: '#112233', opacity: 1 }, { at: 0.5, color: '#445566', opacity: 1 }, { at: 1, color: '#778899', opacity: 1 }]
  },
  grid: { show: false, color: '#000000', opacity: 1, gap: 32, persp: 0 }
};
const two = {
  grad: { kind: 'linear', angle: 90, stops: [{ at: 0, color: '#112233', opacity: 1 }, { at: 1, color: '#AABBCC', opacity: 1 }] },
  grid: { show: true, color: '#334455', opacity: 0.8, gap: 48, persp: 100 }
};
assert.equal(CanvasBg.plan(three, 'drawio'), 'raster', 'draw.io raster when 3 stops');
assert.equal(CanvasBg.plan(two, 'drawio'), 'native', 'draw.io native for two opaque linear stops at 90');
assert.equal(CanvasBg.plan(two, 'pptx'), 'raster', 'pptx rasters a linear sheet');
assert.equal(CanvasBg.plan({ grad: { kind: 'radial', angle: 0, stops: two.grad.stops }, grid: two.grid }, 'pptx'), 'raster', 'pptx rasters a radial sheet');

const nativeDio = CanvasBg.drawio({ canvasBg: two });
assert.match(nativeDio.cells, /edge="1"/, 'perspective grid is a floating edge');
assert.match(nativeDio.cells, /sourcePoint/, 'edge keeps the start point');
assert.match(nativeDio.cells, /targetPoint/, 'edge keeps the end point');
assert.match(nativeDio.cells, /locked=1/, 'native grid is locked');
assert.match(nativeDio.cells, /ht_part="canvasbg"/, 'sheet cells are marked so import skips them');

document.createElement = function (tag) {
  if (tag !== 'canvas') return tiny(tag);
  return {
    width: 0,
    height: 0,
    getContext() {
      return {
        createLinearGradient() {
          calls.linear += 1;
          return { addColorStop() { calls.stops += 1; } };
        },
        createRadialGradient() {
          return { addColorStop() { calls.stops += 1; } };
        },
        fillRect() {},
        beginPath() {},
        moveTo() {},
        lineTo() {},
        stroke() {}
      };
    },
    toDataURL() { return 'data:image/png;base64,stub'; }
  };
};
const rasterDio = CanvasBg.drawio({ canvasBg: three });
assert.match(rasterDio.cells, /image=data:image\/png,[A-Za-z0-9+/=]+/, '3-stop draw.io sheet is a png');
assert.equal(/image=data:image\/png;/.test(rasterDio.cells), false, 'png style value has no semicolon');
assert.ok(calls.linear >= 1 && calls.stops >= 3, 'raster paints the gradient stops');

const saved = {
  pages: {
    root: {
      nodes: [],
      canvasBg: {
        locked: false,
        grad: { kind: 'linear', angle: 15, stops: [{ at: 0, color: '#112233', opacity: 1 }, { at: 1, color: '#445566', opacity: 0.4 }] },
        grid: { show: true, color: '#ABCDEF', opacity: 0.5, gap: 24, persp: 20 }
      }
    },
    bare: { nodes: [] }
  }
};
const round = JSON.parse(JSON.stringify(saved));
CanvasBg.lockPages(round);
assert.equal(round.pages.root.canvasBg.locked, true, 'reloaded page stays locked');
assert.equal(round.pages.root.canvasBg.grad.stops[0].color, '#112233', 'first color survives');
assert.equal(round.pages.root.canvasBg.grad.stops[1].color, '#445566', 'second color survives');
assert.equal(round.pages.bare.canvasBg, undefined, 'pages without a background stay without one');

console.log('canvasbg_logic ok');

// Scoped region beats all caller sheet boxes; offsets remain local and clipped.
const scoped = gridPage(65);
scoped.canvasBg.region = {x:120,y:230,w:240,h:140};
scoped.canvasBg.grid.offsetX = 37;
scoped.canvasBg.grid.offsetY = -19;
const scopedSvg = CanvasBg.markup(scoped,{x:-500,y:-500,w:2000,h:2000});
assert.match(scopedSvg,/x="120" y="230" width="240" height="140"/);
assert.match(scopedSvg,/clip-path=/);
assert.ok(linesOf(scopedSvg).every(l=>l[0]>=120&&l[0]<=360&&l[2]>=120&&l[2]<=360&&l[1]>=230&&l[1]<=370&&l[3]>=230&&l[3]<=370),'perspective offset grid stays strictly in owner region');
const scopedRound=CanvasBg.normalize(JSON.parse(JSON.stringify(scoped.canvasBg)));
assert.equal(scopedRound.region.x,120);assert.equal(scopedRound.grid.offsetX,37);assert.equal(scopedRound.grid.offsetY,-19);
assert.equal(CanvasBg.regionBox(linearPage),null,'old documents remain auto sheets');
const scopedSolid=gridPage(0);scopedSolid.canvasBg.region={x:5,y:7,w:100,h:80};scopedSolid.canvasBg.grad.stops=[{at:0,color:'#112233',opacity:1},{at:1,color:'#112233',opacity:1}];
assert.equal(CanvasBg.drawio(scopedSolid).background,null,'scoped solid region never changes global drawio page background');
console.log('canvasbg scoped regions ok');
const phased=gridPage(0);phased.canvasBg.region={x:100,y:350,w:480,h:180};phased.canvasBg.grid.offsetX=11;phased.canvasBg.grid.offsetY=17;
const phasedLines=linesOf(CanvasBg.markup(phased));assert.ok(phasedLines.length>5,'flat nonzero offset renders without const reassignment');assert.ok(phasedLines.every(l=>l[0]>=100&&l[0]<=580&&l[2]>=100&&l[2]<=580&&l[1]>=350&&l[1]<=530&&l[3]>=350&&l[3]<=530),'phase grid strictly scoped');
