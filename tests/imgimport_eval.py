"""Draw eight diagrams in jingwei, export PNG/JPG/blurred JPG, import, and score."""
import os
import sys
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'tests' / 'fixtures' / 'imgimport'
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()
COMPARE = pathlib.Path('/opt/cursor/artifacts/compare')

if os.environ.get('JW_IMG_PINNED') != '1' and len(os.sched_getaffinity(0)) != 1:
    os.environ['JW_IMG_PINNED'] = '1'
    os.execvp('taskset', ['taskset', '-c', '0', sys.executable] + sys.argv)

subprocess.check_call([sys.executable, str(ROOT / 'build' / 'build_web.py')], cwd=str(ROOT))

DIAGRAMS = [
    {
        'key': 'flow', 'name': '巡逻流程',
        'nodes': [
            {'id': 'a', 'type': 'ellipse', 'x': 40, 'y': 48, 'w': 110, 'h': 56, 'text': '开始', 'size': 16, 'font': 'noto'},
            {'id': 'b', 'type': 'rect', 'x': 210, 'y': 52, 'w': 150, 'h': 48, 'text': '发现目标', 'size': 16, 'font': 'noto'},
            {'id': 'c', 'type': 'diamond', 'x': 420, 'y': 28, 'w': 160, 'h': 96, 'text': '进入警戒', 'size': 15, 'font': 'noto'},
            {'id': 'd', 'type': 'rect', 'x': 650, 'y': 16, 'w': 140, 'h': 44, 'text': '继续巡逻', 'size': 15, 'font': 'noto'},
            {'id': 'e', 'type': 'rect', 'x': 650, 'y': 100, 'w': 140, 'h': 44, 'text': '跟踪', 'size': 16, 'font': 'noto'},
            {'id': 'f', 'type': 'ellipse', 'x': 860, 'y': 48, 'w': 110, 'h': 56, 'text': '结束', 'size': 16, 'font': 'noto'},
        ],
        'links': [
            {'id': 'l1', 'from': 'a', 'to': 'b'},
            {'id': 'l2', 'from': 'b', 'to': 'c'},
            {'id': 'l3', 'from': 'c', 'to': 'd', 'label': '否'},
            {'id': 'l4', 'from': 'c', 'to': 'e', 'label': '是'},
            {'id': 'l5', 'from': 'd', 'to': 'f'},
            {'id': 'l6', 'from': 'e', 'to': 'f'},
        ],
    },
    {
        'key': 'org', 'name': '巡逻编组',
        'nodes': [
            {'id': 'a', 'type': 'rect', 'x': 280, 'y': 24, 'w': 170, 'h': 52, 'text': '巡逻指挥', 'size': 18, 'font': 'noto'},
            {'id': 'b', 'type': 'rect', 'x': 40, 'y': 170, 'w': 150, 'h': 48, 'text': '岸基组', 'size': 16, 'font': 'noto'},
            {'id': 'c', 'type': 'rect', 'x': 290, 'y': 170, 'w': 150, 'h': 48, 'text': '海上组', 'size': 16, 'font': 'noto'},
            {'id': 'd', 'type': 'rect', 'x': 540, 'y': 170, 'w': 150, 'h': 48, 'text': '空中组', 'size': 16, 'font': 'noto'},
        ],
        'links': [
            {'id': 'l1', 'from': 'a', 'to': 'b'},
            {'id': 'l2', 'from': 'a', 'to': 'c'},
            {'id': 'l3', 'from': 'a', 'to': 'd'},
        ],
    },
    {
        'key': 'nest', 'name': '岸基站',
        'nodes': [
            {'id': 'g', 'type': 'group', 'x': 30, 'y': 30, 'w': 480, 'h': 230, 'text': '岸基站', 'size': 16, 'font': 'noto'},
            {'id': 'a', 'type': 'rect', 'x': 60, 'y': 120, 'w': 120, 'h': 48, 'text': '雷达', 'size': 16, 'font': 'noto', 'parent': 'g'},
            {'id': 'b', 'type': 'rect', 'x': 210, 'y': 120, 'w': 120, 'h': 48, 'text': '通信', 'size': 16, 'font': 'noto', 'parent': 'g'},
            {'id': 'c', 'type': 'rect', 'x': 360, 'y': 120, 'w': 120, 'h': 48, 'text': '值班', 'size': 16, 'font': 'noto', 'parent': 'g'},
            {'id': 'd', 'type': 'rect', 'x': 560, 'y': 120, 'w': 160, 'h': 48, 'text': '海上平台', 'size': 16, 'font': 'noto'},
        ],
        'links': [
            {'id': 'l1', 'from': 'b', 'to': 'd'},
        ],
    },
    {
        'key': 'zh', 'name': '中文标签',
        'nodes': [
            {'id': 'a', 'type': 'rect', 'x': 40, 'y': 40, 'w': 180, 'h': 52, 'text': '无人巡逻艇', 'size': 16, 'font': 'noto'},
            {'id': 'b', 'type': 'rect', 'x': 280, 'y': 40, 'w': 180, 'h': 52, 'text': '岸基雷达站', 'size': 16, 'font': 'noto'},
            {'id': 'c', 'type': 'rect', 'x': 520, 'y': 40, 'w': 160, 'h': 52, 'text': '值班席位', 'size': 16, 'font': 'noto'},
            {'id': 'd', 'type': 'round', 'x': 40, 'y': 160, 'w': 200, 'h': 52, 'text': '情况已通报', 'size': 16, 'font': 'noto'},
        ],
        'links': [
            {'id': 'l1', 'from': 'a', 'to': 'b'},
            {'id': 'l2', 'from': 'b', 'to': 'c'},
            {'id': 'l3', 'from': 'a', 'to': 'd'},
        ],
    },
    {
        'key': 'shapes', 'name': '混合图形',
        'nodes': [
            {'id': 'a', 'type': 'rect', 'x': 30, 'y': 50, 'w': 130, 'h': 48, 'text': '矩形', 'size': 16, 'font': 'noto'},
            {'id': 'b', 'type': 'round', 'x': 200, 'y': 50, 'w': 140, 'h': 48, 'text': '圆角', 'size': 16, 'font': 'noto'},
            {'id': 'c', 'type': 'ellipse', 'x': 380, 'y': 34, 'w': 80, 'h': 80, 'text': '圆', 'size': 16, 'font': 'noto'},
            {'id': 'd', 'type': 'diamond', 'x': 500, 'y': 24, 'w': 140, 'h': 100, 'text': '判断', 'size': 15, 'font': 'noto'},
            {'id': 'e', 'type': 'roundL', 'x': 690, 'y': 50, 'w': 160, 'h': 48, 'text': '单侧圆角', 'size': 15, 'font': 'noto'},
        ],
        'links': [
            {'id': 'l1', 'from': 'a', 'to': 'b'},
            {'id': 'l2', 'from': 'b', 'to': 'c'},
            {'id': 'l3', 'from': 'c', 'to': 'd'},
            {'id': 'l4', 'from': 'd', 'to': 'e'},
        ],
    },
    {
        'key': 'cross', 'name': '交叉连线',
        'nodes': [
            {'id': 'a', 'type': 'rect', 'x': 40, 'y': 30, 'w': 130, 'h': 48, 'text': '甲点', 'size': 16, 'font': 'noto'},
            {'id': 'b', 'type': 'rect', 'x': 340, 'y': 30, 'w': 130, 'h': 48, 'text': '乙点', 'size': 16, 'font': 'noto'},
            {'id': 'c', 'type': 'rect', 'x': 40, 'y': 210, 'w': 130, 'h': 48, 'text': '丙点', 'size': 16, 'font': 'noto'},
            {'id': 'd', 'type': 'rect', 'x': 340, 'y': 210, 'w': 130, 'h': 48, 'text': '丁点', 'size': 16, 'font': 'noto'},
        ],
        'links': [
            {'id': 'l1', 'from': 'a', 'to': 'd'},
            {'id': 'l2', 'from': 'b', 'to': 'c'},
        ],
    },
    {
        'key': 'compact', 'name': '紧凑排布',
        'nodes': [
            {'id': 'n%d' % (r * 3 + c + 1), 'type': 'rect', 'x': 24 + c * 130, 'y': 24 + r * 78, 'w': 108, 'h': 42,
             'text': '点%d' % (r * 3 + c + 1), 'size': 14, 'font': 'noto'}
            for r in range(3) for c in range(3)
        ],
        'links': [
            {'id': 'l1', 'from': 'n1', 'to': 'n2'},
            {'id': 'l2', 'from': 'n2', 'to': 'n3'},
            {'id': 'l3', 'from': 'n1', 'to': 'n4'},
            {'id': 'l4', 'from': 'n5', 'to': 'n6'},
            {'id': 'l5', 'from': 'n7', 'to': 'n8'},
            {'id': 'l6', 'from': 'n8', 'to': 'n9'},
        ],
    },
    {
        'key': 'fonts', 'name': '字体字号',
        'nodes': [
            {'id': 'a', 'type': 'rect', 'x': 30, 'y': 40, 'w': 140, 'h': 44, 'text': '巡逻', 'size': 14, 'font': 'noto'},
            {'id': 'b', 'type': 'rect', 'x': 210, 'y': 30, 'w': 160, 'h': 64, 'text': '巡逻', 'size': 22, 'font': 'noto', 'bold': True},
            {'id': 'c', 'type': 'round', 'x': 410, 'y': 36, 'w': 150, 'h': 52, 'text': '巡逻', 'size': 16, 'font': 'noto-serif'},
            {'id': 'd', 'type': 'rect', 'x': 600, 'y': 34, 'w': 160, 'h': 56, 'text': '巡逻', 'size': 18, 'font': 'wqy'},
        ],
        'links': [
            {'id': 'l1', 'from': 'a', 'to': 'b'},
            {'id': 'l2', 'from': 'b', 'to': 'c'},
            {'id': 'l3', 'from': 'c', 'to': 'd'},
        ],
    },
]

RUN = r"""async (spec) => {
  const page = {
    id: 'root', name: '总图',
    nodes: spec.nodes.map(n => mkNode(n)),
    links: spec.links.map(l => Object.assign({ dir: 'one', kind: 'data', route: 'ortho', label: '' }, l))
  };
  loadDoc({
    name: spec.name, theme: 'report',
    statusLabels: Object.assign({}, doc.statusLabels),
    custom: {}, lastKind: 'data', pages: { root: page }
  });
  const exp = exportSVGString(page, true);
  const scale = 2;
  const box = contentBBox(page);
  const ox = box.x - 24, oy = box.y - 24;
  const painted = await new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(new Blob([exp.str], { type: 'image/svg+xml;charset=utf-8' }));
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = Math.round(exp.w * scale);
      c.height = Math.round(exp.h * scale);
      const g = c.getContext('2d');
      g.fillStyle = '#ffffff';
      g.fillRect(0, 0, c.width, c.height);
      g.scale(scale, scale);
      g.drawImage(img, 0, 0, exp.w, exp.h);
      URL.revokeObjectURL(url);
      resolve(c);
    };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('svg')); };
    img.src = url;
  });
  const pngURL = painted.toDataURL('image/png');
  const jpgURL = painted.toDataURL('image/jpeg', 0.72);
  const bw = Math.max(8, Math.round(painted.width * 0.85));
  const bh = Math.max(8, Math.round(painted.height * 0.85));
  const blurC = document.createElement('canvas');
  blurC.width = bw; blurC.height = bh;
  const bg = blurC.getContext('2d');
  bg.fillStyle = '#ffffff';
  bg.fillRect(0, 0, bw, bh);
  bg.filter = 'blur(1.2px)';
  bg.drawImage(painted, 0, 0, bw, bh);
  const blurURL = blurC.toDataURL('image/jpeg', 0.7);
  function mapNode(n, k) {
    return { type: n.type, text: n.text || '', x: (n.x - ox) * scale * k, y: (n.y - oy) * scale * k, w: n.w * scale * k, h: n.h * scale * k, id: n.id };
  }
  const gt = {
    nodes: page.nodes.map(n => mapNode(n, 1)),
    links: page.links.map(l => ({ from: l.from, to: l.to, dir: l.dir || 'one', label: l.label || '' }))
  };
  async function readURL(url) {
    const img = new Image();
    await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; img.src = url; });
    const c = document.createElement('canvas');
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    c.getContext('2d').drawImage(img, 0, 0);
    const t0 = performance.now();
    const draft = ImgImport.read(c.getContext('2d').getImageData(0, 0, c.width, c.height));
    const ms = performance.now() - t0;
    return {
      ms: ms, w: c.width, h: c.height, notes: draft.notes || [],
      nodes: draft.page.nodes.map(n => ({ id: n.id, type: n.type, text: n.text || '', x: n.x, y: n.y, w: n.w, h: n.h })),
      links: draft.page.links.map(l => ({ id: l.id, from: l.from, to: l.to, dir: l.dir || 'one', label: l.label || '' }))
    };
  }
  const pred = { png: await readURL(pngURL), jpg: await readURL(jpgURL), blur: await readURL(blurURL) };
  const back = pred.png;
  const imported = {
    id: 'root', name: '总图', view: null,
    nodes: back.nodes.map(n => mkNode(n)),
    links: back.links.map(l => ({ id: l.id, from: l.from, to: l.to, dir: l.dir, route: 'ortho', label: l.label || '' }))
  };
  loadDoc({
    name: spec.name + '-导入', theme: 'report',
    statusLabels: Object.assign({}, doc.statusLabels),
    custom: {}, lastKind: 'data', pages: { root: imported }
  });
  fit();
  return { gt: gt, pred: pred, png: pngURL, jpg: jpgURL, blur: blurURL };
}"""


def iou(a, b):
    x0 = max(a['x'], b['x'])
    y0 = max(a['y'], b['y'])
    x1 = min(a['x'] + a['w'], b['x'] + b['w'])
    y1 = min(a['y'] + a['h'], b['y'] + b['h'])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    union = a['w'] * a['h'] + b['w'] * b['h'] - inter
    return inter / union if union else 0


def edit_distance(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def score_variant(gt, pred, k):
    gnodes = [{**n, 'x': n['x'] * k, 'y': n['y'] * k, 'w': n['w'] * k, 'h': n['h'] * k} for n in gt['nodes']]
    used = set()
    pairs = []
    for g in gnodes:
        best_i, best_s = None, 0
        for i, p in enumerate(pred['nodes']):
            if i in used or p['type'] != g['type']:
                continue
            s = iou(g, p)
            if s >= 0.5 and s > best_s:
                best_i, best_s = i, s
        if best_i is not None:
            used.add(best_i)
            pairs.append((g, pred['nodes'][best_i]))
    shape_rec = len(pairs) / len(gnodes) if gnodes else 1
    shape_prec = len(pairs) / len(pred['nodes']) if pred['nodes'] else (1 if not gnodes else 0)
    chars = edits = 0
    for g, p in pairs:
        chars += len(g['text'])
        edits += edit_distance(g['text'], p['text'])
    text_acc = 1.0 if not chars else max(0.0, chars - edits) / chars
    g2p = {g['id']: p['id'] for g, p in pairs}
    p_links = {(l['from'], l['to'], l['dir']) for l in pred['links']}
    link_hit = 0
    for l in gt['links']:
        a, b = g2p.get(l['from']), g2p.get(l['to'])
        if a and b and ((a, b, l['dir']) in p_links or (b, a, l['dir']) in p_links and l['dir'] == 'both'):
            link_hit += 1
        elif a and b and (a, b, l['dir']) in p_links:
            link_hit += 1
    # direction must match; a reversed arrow is not a hit
    link_hit = 0
    matched_pred = set()
    for l in gt['links']:
        a, b = g2p.get(l['from']), g2p.get(l['to'])
        if not a or not b:
            continue
        for i, pl in enumerate(pred['links']):
            if i in matched_pred:
                continue
            if pl['from'] == a and pl['to'] == b and pl['dir'] == l['dir']:
                matched_pred.add(i)
                link_hit += 1
                break
    link_rec = link_hit / len(gt['links']) if gt['links'] else 1
    link_prec = link_hit / len(pred['links']) if pred['links'] else (1 if not gt['links'] else 0)
    return {
        'shape_recall': shape_rec, 'shape_precision': shape_prec,
        'text': text_acc, 'link_recall': link_rec, 'link_precision': link_prec,
        'ms': pred['ms'], 'nodes': len(pred['nodes']), 'links': len(pred['links']),
    }


def chrome_mem():
    rss = hwm_max = 0
    n = 0
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            cmd = open('/proc/%s/cmdline' % pid, 'rb').read().replace(b'\x00', b' ').decode('utf-8', 'ignore')
            status = open('/proc/%s/status' % pid, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        if 'chrom' not in cmd.lower():
            continue
        n += 1
        for line in status.splitlines():
            if line.startswith('VmRSS:'):
                rss += int(line.split()[1])
            elif line.startswith('VmHWM:'):
                hwm_max = max(hwm_max, int(line.split()[1]))
    return n, rss / 1024.0, hwm_max / 1024.0


def main():
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw, ImageFont
    import base64
    OUT.mkdir(parents=True, exist_ok=True)
    COMPARE.mkdir(parents=True, exist_ok=True)
    exe = os.environ.get('JW_CHROME')
    if not exe:
        for cand in ('/opt/google/chrome/chrome', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'):
            if os.path.exists(cand):
                exe = cand
                break
    kw = {'args': ['--no-sandbox', '--disable-gpu']}
    if exe:
        kw['executable_path'] = exe
    rows = []
    shots = []
    rss_peak = hwm_peak = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **kw)
        page = browser.new_page(viewport={'width': 1600, 'height': 1000})
        page.goto(HTML)
        page.wait_for_timeout(500)
        font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
        font = ImageFont.truetype(font_path, 22, index=0)
        for spec in DIAGRAMS:
            got = page.evaluate(RUN, spec)
            gt_path = OUT / (spec['key'] + '.json')
            gt_path.write_text(json.dumps({'name': spec['name'], 'nodes': got['gt']['nodes'], 'links': got['gt']['links']}, ensure_ascii=False, indent=2), encoding='utf-8')
            files = {}
            for kind, ext in (('png', 'png'), ('jpg', 'jpg'), ('blur', 'jpg')):
                raw = got[kind].split(',', 1)[1]
                dest = OUT / ('%s.%s' % (spec['key'], ext) if kind != 'blur' else spec['key'] + '.blur.jpg')
                dest.write_bytes(base64.b64decode(raw))
                files[kind] = dest
            nproc, rss, hwm = chrome_mem()
            rss_peak = max(rss_peak, rss)
            hwm_peak = max(hwm_peak, hwm)
            shot = COMPARE / ('_shot_%s.png' % spec['key'])
            page.wait_for_timeout(200)
            page.locator('#stage').screenshot(path=str(shot))
            shots.append((spec['key'], files['png'], shot))
            line = {'key': spec['key']}
            for kind in ('png', 'jpg', 'blur'):
                k = 1.0
                if kind == 'blur':
                    k = got['pred']['blur']['w'] / got['pred']['png']['w']
                line[kind] = score_variant(got['gt'], got['pred'][kind], k)
            rows.append(line)
            print(spec['key'], 'png nodes', got['pred']['png']['nodes'] and len(got['pred']['png']['nodes']), 'notes', got['pred']['png']['notes'])
        browser.close()
    headers = ('key', 'var', 'shape_rec', 'shape_prec', 'text', 'link_rec', 'link_prec', 'ms', 'pred_n', 'pred_l')
    print('\t'.join(headers))
    lines = ['\t'.join(headers)]
    for row in rows:
        for kind in ('png', 'jpg', 'blur'):
            s = row[kind]
            rec = [
                row['key'], kind,
                '%.3f' % s['shape_recall'], '%.3f' % s['shape_precision'], '%.3f' % s['text'],
                '%.3f' % s['link_recall'], '%.3f' % s['link_precision'],
                '%.0f' % s['ms'], str(s['nodes']), str(s['links']),
            ]
            print('\t'.join(rec))
            lines.append('\t'.join(rec))
    affinity = sorted(os.sched_getaffinity(0))
    mem_line = 'affinity=%s chrome_rss_sum_mib=%.0f chrome_hwm_max_mib=%.0f no_memory_cgroup=1' % (affinity, rss_peak, hwm_peak)
    print(mem_line)
    lines.append(mem_line)
    (OUT / 'metrics.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    compares = []
    for key, orig_path, shot_path in shots:
        orig = Image.open(orig_path).convert('RGB')
        shot = Image.open(shot_path).convert('RGB')
        H = 720
        def fit(im):
            r = H / im.height
            return im.resize((max(1, round(im.width * r)), H), Image.Resampling.LANCZOS)
        a, b = fit(orig), fit(shot)
        gap, header = 12, 44
        canvas = Image.new('RGB', (a.width + gap + b.width, H + header), (244, 246, 248))
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 10), key + '  原图', fill=(27, 36, 51), font=font)
        draw.text((a.width + gap + 8, 10), '导入后', fill=(27, 36, 51), font=font)
        canvas.paste(a, (0, header))
        canvas.paste(b, (a.width + gap, header))
        dest = COMPARE / (key + '.png')
        canvas.save(dest)
        compares.append(canvas)
        shot_path.unlink(missing_ok=True)
    cols = 2
    thumb_w = 960
    thumbs = []
    for im in compares:
        r = thumb_w / im.width
        thumbs.append(im.resize((thumb_w, max(1, round(im.height * r))), Image.Resampling.LANCZOS))
    rows_n = (len(thumbs) + cols - 1) // cols
    cell_h = max(t.height for t in thumbs)
    overview = Image.new('RGB', (thumb_w * cols, cell_h * rows_n), (255, 255, 255))
    for i, t in enumerate(thumbs):
        overview.paste(t, ((i % cols) * thumb_w, (i // cols) * cell_h))
    overview.save(COMPARE / 'overview.png')
    print('wrote', COMPARE)


if __name__ == '__main__':
    main()
