"""网页版离线包：dist/offline.html + 说明 + 图标 → _work/dist/经纬织图_v<版本>_离线版.zip（包内文件名全部 ASCII）"""
import os, json, zipfile, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.environ.get('JW_WORK', os.path.join(ROOT, '_work')); OUT = os.path.join(WORK, 'dist'); os.makedirs(OUT, exist_ok=True)
V = json.load(open(os.path.join(ROOT, 'desktop', 'package.json')))['version']
html = f'JingWeiZhiTu_v{V}.html'
readme = open(os.path.join(ROOT, 'build', 'web', 'README.template.txt'), encoding='utf-8-sig').read()
readme = readme.replace('V3.2.1', f'V{V}').replace('v3.2.1', f'v{V}')
items = [(os.path.join(ROOT, 'dist', 'offline.html'), html), (None, 'README.txt'),
         (os.path.join(ROOT, 'assets', 'brand', 'out', 'Brand_JingWeiZhiTu.jpg'), 'Brand_JingWeiZhiTu.jpg')]
for f in sorted(glob.glob(os.path.join(ROOT, 'docs', 'release-notes', 'ReleaseNotes_v3.2.1.*'))) + sorted(glob.glob(os.path.join(ROOT, 'docs', 'release-notes', 'Guide_v3.3.*'))):
    items.append((f, os.path.basename(f)))
for f in sorted(glob.glob(os.path.join(ROOT, 'assets', 'brand', 'out', 'icon_*.png'))) + [os.path.join(ROOT, 'assets', 'brand', 'out', 'JingWeiZhiTu.ico'), os.path.join(ROOT, 'assets', 'brand', 'icon.svg')]:
    items.append((f, 'icon/' + os.path.basename(f)))
zp = os.path.join(OUT, f'经纬织图_v{V}_离线版.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for src, arc in items:
        arc.encode('ascii')   # 包内文件名必须是 ASCII（用户机器上 UTF-8／GBK 文件名都出过乱码）
        if src is None: z.writestr(arc, ('﻿' + readme).replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
        else: z.write(src, arc)
print('->', zp)
