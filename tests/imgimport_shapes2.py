"""Draw mixed jingwei shapes, export PNG and JPG, and score type, text, and arrows.

Decision, fixed before the run:
A type hit is the same type and IoU >= 0.5. One trial. The importer is
deterministic on a fixed image, so the spread is 0. A listed family whose
clean PNG type recall is below 0.5 is a candidate for one polygon template,
and only when the dump shows it became a rect, an ellipse, or a miss.
A family at or above 0.8 is left alone. Direction rate divides by links whose
both endpoint shapes matched, so a missed shape is not a direction miss.
Raw direction rate divides by every ground-truth link. A crossing pair is
correct only when from and to match exactly. A swap is not. An elbow counts
when the endpoints and dir match. Jingwei stores no bend points. Nodes have
no rotation field, so this set has no rotated fixtures. A circle is type
ellipse.
"""
import os
import sys
import json
import pathlib
import subprocess
import collections

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'tests' / 'fixtures' / 'shapes2'
HTML = (ROOT / 'dist' / 'offline.html').resolve().as_uri()

if os.environ.get('JW_IMG_PINNED') != '1' and len(os.sched_getaffinity(0)) != 1:
    os.environ['JW_IMG_PINNED'] = '1'
    os.execvp('taskset', ['taskset', '-c', '0', sys.executable] + sys.argv)

if os.environ.get('JW_SHAPES_NOBUILD') != '1':
    subprocess.check_call([sys.executable, str(ROOT / 'build' / 'build_web.py')], cwd=str(ROOT))


def N(i, typ, x, y, w, h, text):
    return {'id': i, 'type': typ, 'x': x, 'y': y, 'w': w, 'h': h, 'text': text, 'size': 16, 'font': 'noto'}


def L(i, a, b, dir='one', cross=False):
    return {'id': i, 'from': a, 'to': b, 'dir': dir, 'cross': cross}


DIAGRAMS = [
    {
        'key': 'poly', 'name': '多边形流程',
        'nodes': [
            N('t', 'triangle', 40, 36, 90, 78, '三角'),
            N('z', 'trapezoid', 190, 48, 150, 56, '梯形'),
            N('p', 'parallelogram', 400, 50, 160, 52, '并行'),
            N('h', 'hexagon', 620, 40, 140, 72, '六边'),
            N('f', 'pentagon', 70, 200, 96, 90, '五边'),
            N('o', 'octagon', 250, 206, 88, 88, '八角'),
            N('d', 'diamond', 430, 196, 130, 96, '判断'),
        ],
        'links': [
            L('l1', 't', 'z'), L('l2', 'z', 'p'), L('l3', 'p', 'h'),
            L('l4', 'f', 'o'), L('l5', 'o', 'd'), L('l6', 'z', 'o'),
        ],
    },
    {
        'key': 'rounds', 'name': '圆与圆角',
        'nodes': [
            N('c', 'ellipse', 40, 40, 64, 64, '圆形'),
            N('e', 'ellipse', 160, 46, 170, 56, '椭圆'),
            N('r', 'round', 390, 48, 120, 48, '圆角'),
            N('f', 'round', 40, 160, 210, 36, '扁圆角'),
            N('l', 'roundL', 300, 150, 150, 52, '左圆角'),
            N('g', 'roundR', 500, 146, 110, 64, '右圆角'),
            N('s', 'terminator', 40, 250, 140, 48, '开始'),
        ],
        'links': [L('l1', 'c', 'e'), L('l2', 'e', 'r'), L('l3', 'f', 'l'), L('l4', 'l', 'g'), L('l5', 'c', 's')],
    },
    {
        'key': 'flowmisc', 'name': '其它流程形',
        'nodes': [
            N('a', 'document', 30, 30, 130, 70, '文档'),
            N('b', 'delay', 210, 36, 130, 56, '延迟'),
            N('c', 'display', 390, 30, 140, 64, '显示'),
            N('d', 'predef', 580, 36, 140, 52, '过程'),
            N('e', 'cylinder', 40, 180, 110, 80, '数据'),
            N('f', 'chevron', 200, 190, 150, 56, '阶段'),
            N('g', 'cube', 400, 176, 100, 80, '立方'),
            N('h', 'cloud', 550, 170, 150, 80, '云'),
        ],
        'links': [L('l1', 'a', 'b'), L('l2', 'b', 'c'), L('l3', 'c', 'd'), L('l4', 'e', 'f'), L('l5', 'f', 'g'), L('l6', 'g', 'h')],
    },
    {
        'key': 'arrows', 'name': '箭头方向',
        'nodes': [
            N('a', 'rect', 40, 40, 130, 48, '甲点'),
            N('b', 'rect', 360, 40, 130, 48, '乙点'),
            N('c', 'rect', 40, 220, 130, 48, '丙点'),
            N('d', 'rect', 360, 220, 130, 48, '丁点'),
            N('e', 'rect', 40, 380, 130, 48, '起点'),
            N('f', 'rect', 360, 408, 130, 48, '终点'),
            N('g', 'rect', 700, 40, 130, 48, '回点'),
            N('h', 'rect', 700, 200, 130, 48, '去点'),
            N('m', 'rect', 520, 380, 130, 48, '左框'),
            N('k', 'rect', 760, 380, 130, 48, '右框'),
            N('i', 'rect', 40, 540, 130, 48, '折起'),
            N('j', 'rect', 300, 660, 130, 48, '折落'),
        ],
        'links': [
            L('x1', 'a', 'd', cross=True),
            L('x2', 'b', 'c', cross=True),
            L('both', 'e', 'f', dir='both'),
            L('up', 'h', 'g'),
            L('left', 'k', 'm'),
            L('elbow', 'i', 'j'),
        ],
    },
    {
        'key': 'sizes', 'name': '不同大小',
        'nodes': [
            N('a', 'triangle', 24, 24, 56, 48, '小三角'),
            N('b', 'triangle', 24 + 56 + 12, 24, 160, 130, '大三角'),
            N('c', 'diamond', 24, 24 + 130 + 12, 70, 48, '小菱'),
            N('d', 'diamond', 24 + 70 + 12, 24 + 130 + 12, 180, 110, '大菱'),
            N('e', 'ellipse', 24, 24 + 130 + 12 + 110 + 12, 48, 48, '小圆'),
            N('f', 'ellipse', 24 + 48 + 12, 24 + 130 + 12 + 110 + 12, 200, 70, '大椭圆'),
            N('g', 'hexagon', 24, 24 + 130 + 12 + 110 + 12 + 70 + 12, 80, 44, '小六'),
            N('h', 'hexagon', 24 + 80 + 12, 24 + 130 + 12 + 110 + 12 + 70 + 12, 180, 80, '大六'),
        ],
        'links': [L('l1', 'a', 'b'), L('l2', 'c', 'd'), L('l3', 'e', 'f'), L('l4', 'g', 'h')],
    },
    {
        'key': 'extra', 'name': '其余形状',
        'nodes': [
            N('a', 'star', 30, 30, 90, 90, '星形'),
            N('b', 'plus', 180, 40, 80, 80, '十字'),
            N('c', 'donut', 320, 30, 90, 90, '圆环'),
            N('d', 'frame', 460, 36, 120, 80, '外框'),
            N('e', 'arrowR', 640, 48, 160, 64, '右箭'),
        ],
        'links': [L('l1', 'a', 'b'), L('l2', 'b', 'c'), L('l3', 'c', 'd'), L('l4', 'd', 'e')],
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
  function mapNode(n) {
    return { id: n.id, type: n.type, text: n.text || '', x: (n.x - ox) * scale, y: (n.y - oy) * scale, w: n.w * scale, h: n.h * scale };
  }
  const gt = {
    nodes: page.nodes.map(mapNode),
    links: page.links.map(l => ({ id: l.id, from: l.from, to: l.to, dir: l.dir || 'one', cross: !!l.cross }))
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
      ms: ms, w: c.width, h: c.height,
      nodes: draft.page.nodes.map(n => ({ id: n.id, type: n.type, text: n.text || '', x: n.x, y: n.y, w: n.w, h: n.h })),
      links: draft.page.links.map(l => ({ id: l.id, from: l.from, to: l.to, dir: l.dir || 'one' }))
    };
  }
  return { gt: gt, png: pngURL, jpg: jpgURL, pred: { png: await readURL(pngURL), jpg: await readURL(jpgURL) } };
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


def text_acc(a, b):
    longer = max(len(a), len(b))
    if longer == 0:
        return 1.0
    return max(0.0, 1.0 - edit_distance(a, b) / longer)


def type_pairs(gnodes, pnodes):
    used = set()
    pairs = []
    for g in gnodes:
        best_i, best_s = None, 0
        for i, p in enumerate(pnodes):
            if i in used or p['type'] != g['type']:
                continue
            s = iou(g, p)
            if s >= 0.5 and s > best_s:
                best_i, best_s = i, s
        if best_i is not None:
            used.add(best_i)
            pairs.append((g, pnodes[best_i]))
    return pairs


def best_overlap(g, pnodes):
    best, score = None, 0
    for p in pnodes:
        s = iou(g, p)
        if s > score:
            best, score = p, s
    return best, score


def score_arrows(gt, pred, pairs):
    g2p = {g['id']: p['id'] for g, p in pairs}
    end_hit = dir_hit = both = 0
    cross_n = cross_ok = cross_swap = cross_miss = 0
    for l in gt['links']:
        a, b = g2p.get(l['from']), g2p.get(l['to'])
        matched = bool(a and b)
        if matched:
            both += 1
        ends = dirs = exact = swapped = False
        if matched:
            for pl in pred['links']:
                if {pl['from'], pl['to']} == {a, b}:
                    ends = True
                    if pl['from'] == a and pl['to'] == b and (pl.get('dir') or 'one') == l['dir']:
                        dirs = True
                    if pl['from'] == a and pl['to'] == b:
                        exact = True
                    if pl['from'] == b and pl['to'] == a:
                        swapped = True
        if ends:
            end_hit += 1
        if dirs:
            dir_hit += 1
        if l.get('cross'):
            cross_n += 1
            if exact:
                cross_ok += 1
            elif swapped:
                cross_swap += 1
            else:
                cross_miss += 1
    n = len(gt['links'])
    return {
        'n': n, 'end_hit': end_hit, 'dir_hit': dir_hit, 'both': both,
        'dir_given': (dir_hit / both) if both else None,
        'dir_raw': (dir_hit / n) if n else None,
        'cross_n': cross_n, 'cross_ok': cross_ok, 'cross_swap': cross_swap, 'cross_miss': cross_miss,
    }


def chrome_mem():
    rss = hwm_max = n = 0
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


def fmt_rate(v):
    return 'n/a' if v is None else '%.3f' % v


def main():
    print('decision type_hit=same type and IoU>=0.5; one trial; spread=0 because ImgImport.read is deterministic on a fixed image.')
    print('decision family PNG type recall < 0.5 and dump is rect, ellipse, or miss: add one polygon template. recall >= 0.8: leave the detector.')
    print('decision direction_rate = dir_hit / links whose both shapes matched. raw = dir_hit / all links. crossing pair_ok needs exact from->to. elbow = endpoints + dir, bends are not stored. no rotation field, no rotated fixtures. circle type is ellipse.')
    from playwright.sync_api import sync_playwright
    import base64
    OUT.mkdir(parents=True, exist_ok=True)
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
    rss_peak = hwm_peak = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **kw)
        page = browser.new_page(viewport={'width': 1400, 'height': 900})
        page.goto(HTML)
        page.wait_for_timeout(400)
        for spec in DIAGRAMS:
            got = page.evaluate(RUN, spec)
            (OUT / (spec['key'] + '.json')).write_text(
                json.dumps({'name': spec['name'], 'nodes': got['gt']['nodes'], 'links': got['gt']['links']}, ensure_ascii=False, indent=2),
                encoding='utf-8')
            for kind in ('png', 'jpg'):
                raw = got[kind].split(',', 1)[1]
                (OUT / ('%s.%s' % (spec['key'], kind if kind == 'png' else 'jpg'))).write_bytes(base64.b64decode(raw))
            nproc, rss, hwm = chrome_mem()
            rss_peak = max(rss_peak, rss)
            hwm_peak = max(hwm_peak, hwm)
            line = {'key': spec['key'], 'gt': got['gt']}
            for kind in ('png', 'jpg'):
                line[kind] = got['pred'][kind]
            rows.append(line)
            pred = got['pred']['png']
            print(spec['key'], 'png_ms', round(pred['ms']), 'nodes', [(n['type'], n['text']) for n in pred['nodes']], 'links', [(l['from'], l['to'], l['dir']) for l in pred['links']])
        browser.close()

    def tally(kind, dump_it):
        by_type = collections.defaultdict(lambda: {'n': 0, 'hit': 0, 'text': [], 'wrong': [], 'miss': 0})
        dumps = []
        arrow_lines = []
        cross_tot = {'n': 0, 'ok': 0, 'swap': 0, 'miss': 0}
        arrow_tot = {'n': 0, 'end': 0, 'dir': 0, 'both': 0}
        for row in rows:
            gt, pred = row['gt'], row[kind]
            pairs = type_pairs(gt['nodes'], pred['nodes'])
            hit_ids = {g['id'] for g, _p in pairs}
            for g in gt['nodes']:
                slot = by_type[g['type']]
                slot['n'] += 1
                best, score = best_overlap(g, pred['nodes'])
                if dump_it:
                    dumps.append({'key': row['key'], 'id': g['id'], 'type': g['type'], 'text': g['text'], 'iou': round(score, 3),
                                  'pred_type': best['type'] if best else '', 'pred_text': best['text'] if best else '', 'hit': g['id'] in hit_ids})
                if g['id'] in hit_ids:
                    slot['hit'] += 1
                    got = next(p for gg, p in pairs if gg['id'] == g['id'])
                    slot['text'].append(text_acc(g['text'], got['text']))
                elif best and score >= 0.5 and best['type'] != g['type']:
                    slot['wrong'].append(best['type'])
                else:
                    slot['miss'] += 1
            ar = score_arrows(gt, pred, pairs)
            arrow_lines.append((row['key'], ar))
            cross_tot['n'] += ar['cross_n']
            cross_tot['ok'] += ar['cross_ok']
            cross_tot['swap'] += ar['cross_swap']
            cross_tot['miss'] += ar['cross_miss']
            arrow_tot['n'] += ar['n']
            arrow_tot['end'] += ar['end_hit']
            arrow_tot['dir'] += ar['dir_hit']
            arrow_tot['both'] += ar['both']
        return by_type, dumps, arrow_lines, cross_tot, arrow_tot

    def emit_block(kind, by_type, arrow_lines, cross_tot, arrow_tot, lines):
        print('TYPE ' + kind)
        lines.append('TYPE ' + kind)
        hdr = 'type\tn\thit\trecall\ttext\twrong_mode\tmiss'
        print(hdr)
        lines.append(hdr)
        for typ in sorted(by_type):
            slot = by_type[typ]
            recall = slot['hit'] / slot['n'] if slot['n'] else 1
            text = sum(slot['text']) / len(slot['text']) if slot['text'] else 0
            mode = collections.Counter(slot['wrong']).most_common(1)
            mode_s = ('%s:%d' % mode[0]) if mode else '-'
            rec = '%s\t%d\t%d\t%.3f\t%.3f\t%s\t%d' % (typ, slot['n'], slot['hit'], recall, text, mode_s, slot['miss'])
            print(rec)
            lines.append(rec)
        print('ARROWS ' + kind + '  dir_given uses links with both shapes matched. dir_raw uses every link. elbow is endpoints+dir.')
        lines.append('ARROWS ' + kind)
        ah = 'key\tlinks\tend_hit\tend_rate\tdir_hit\tdir_given\tdir_raw\tcross_ok\tcross_swap\tcross_miss'
        print(ah)
        lines.append(ah)
        for key, ar in arrow_lines:
            end_rate = ar['end_hit'] / ar['n'] if ar['n'] else 1
            rec = '%s\t%d\t%d\t%.3f\t%d\t%s\t%s\t%d\t%d\t%d' % (
                key, ar['n'], ar['end_hit'], end_rate, ar['dir_hit'], fmt_rate(ar['dir_given']), fmt_rate(ar['dir_raw']),
                ar['cross_ok'], ar['cross_swap'], ar['cross_miss'])
            print(rec)
            lines.append(rec)
        end_rate = arrow_tot['end'] / arrow_tot['n'] if arrow_tot['n'] else 1
        dir_given = arrow_tot['dir'] / arrow_tot['both'] if arrow_tot['both'] else None
        dir_raw = arrow_tot['dir'] / arrow_tot['n'] if arrow_tot['n'] else None
        rec = 'ALL\t%d\t%d\t%.3f\t%d\t%s\t%s\t%d\t%d\t%d' % (
            arrow_tot['n'], arrow_tot['end'], end_rate, arrow_tot['dir'], fmt_rate(dir_given), fmt_rate(dir_raw),
            cross_tot['ok'], cross_tot['swap'], cross_tot['miss'])
        print(rec)
        lines.append(rec)
        if cross_tot['n']:
            cross_line = 'crossing_pair_rate %.3f (%d/%d) swap %d miss %d' % (
                cross_tot['ok'] / cross_tot['n'], cross_tot['ok'], cross_tot['n'], cross_tot['swap'], cross_tot['miss'])
        else:
            cross_line = 'crossing_pair_rate n/a'
        print(cross_line)
        lines.append(cross_line)

    lines = []
    by_png, dumps, arrows_png, cross_png, tot_png = tally('png', True)
    emit_block('png', by_png, arrows_png, cross_png, tot_png, lines)
    by_jpg, _d, arrows_jpg, cross_jpg, tot_jpg = tally('jpg', False)
    emit_block('jpg', by_jpg, arrows_jpg, cross_jpg, tot_jpg, lines)
    print('DUMP png best overlap regardless of type')
    lines.append('DUMP')
    for d in dumps:
        rec = '%s\t%s\t%s\t%s\t%.3f\t%s\t%s\t%s' % (d['key'], d['id'], d['type'], d['text'], d['iou'], d['pred_type'], d['pred_text'], 'hit' if d['hit'] else 'miss')
        print(rec)
        lines.append(rec)
    affinity = sorted(os.sched_getaffinity(0))
    mem_line = 'affinity=%s chrome_rss_sum_mib=%.0f chrome_hwm_max_mib=%.0f no_memory_cgroup=1 one_trial=1' % (affinity, rss_peak, hwm_peak)
    print(mem_line)
    lines.append(mem_line)
    (OUT / 'metrics.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('wrote', OUT)


if __name__ == '__main__':
    main()
