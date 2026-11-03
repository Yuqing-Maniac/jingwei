#!/usr/bin/env python3
"""Fail if batch l palette rows collide or drift from the nine equipment names."""
import glob
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app'

EXPECT = [
    ('air_phased_radar', '机载相控阵雷达', '感知通信'),
    ('ship_mesh_datalink', '舰载自组网数据链', '感知通信'),
    ('air_mesh_datalink', '机载自组网数据链', '感知通信'),
    ('uav_ttc', '无人机测控站', '指控信息'),
    ('loiter_ttc', '巡飞弹测控站', '指控信息'),
    ('cuas_detect_jam', '侦测干扰一体反无人设备', '反无人'),
    ('beidou_timing', '北斗授时系统', '指控信息'),
    ('eo_composite', '复合光电系统', '感知通信'),
    ('compute_platform', '新架构算力平台', '信息技术'),
]


def page_files():
    paths = sorted(glob.glob(str(APP / 'icons_*.js')))
    return [APP / 'icons.js'] + [Path(p) for p in paths]


def load_lib():
    chunks = []
    for path in page_files():
        text = path.read_text(encoding='utf-8')
        if path.name == 'icons.js':
            prefix = 'const ICON_LIB'
            if not text.startswith(prefix):
                raise SystemExit('icons.js does not start with const ICON_LIB')
            text = 'var ICON_LIB' + text[len(prefix):]
        chunks.append(text)
    src = '\n'.join(chunks) + '\nprocess.stdout.write(JSON.stringify(ICON_LIB));\n'
    fd, tmp = tempfile.mkstemp(suffix='.js')
    os.close(fd)
    Path(tmp).write_text(src, encoding='utf-8')
    try:
        proc = subprocess.run(['node', tmp], check=True, capture_output=True, text=True)
    finally:
        os.unlink(tmp)
    if proc.stderr.strip():
        raise SystemExit(proc.stderr)
    return json.loads(proc.stdout)


def main():
    lib = load_lib()
    keys = [row['key'] for row in lib]
    names = [row['name'] for row in lib]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise SystemExit('duplicate keys: ' + ', '.join(dup))

    by_key = {}
    for row in lib:
        by_key.setdefault(row['key'], row)
    l_rows = [(row['key'], row['name'], row['cat']) for row in lib if row['key'] in {k for k, n, c in EXPECT}]
    if l_rows != EXPECT:
        raise SystemExit('batch l rows: ' + repr(l_rows))
    for key, name, cat in EXPECT:
        if names.count(name) != 1:
            raise SystemExit('name count %s %s' % (names.count(name), name))
        if by_key[key]['cat'] != cat:
            raise SystemExit('cat %s %s' % (key, by_key[key]['cat']))

    raw = (APP / 'icons_l.js').read_text(encoding='utf-8')
    if not raw.startswith('ICON_LIB.push'):
        raise SystemExit('icons_l.js does not start with ICON_LIB.push')
    if 'const ICON_LIB' in raw or 'module.exports' in raw:
        raise SystemExit('icons_l.js declares a module or const ICON_LIB')
    if '(?<' in raw or '\u2028' in raw:
        raise SystemExit('icons_l.js has a lookbehind or U+2028')

    appjs = (APP / 'app.js').read_text(encoding='utf-8')
    block = appjs[appjs.index('const ICON_CAT_OVERRIDE'):appjs.index('const iconCats')]
    for key, name, cat in EXPECT:
        if key in block:
            raise SystemExit('key registered in ICON_CAT_OVERRIDE or ICON_ALSO: ' + key)

    for key, name, cat in EXPECT:
        root = ET.fromstring(by_key[key]['svg'])
        tag = root.tag.split('}')[-1]
        if tag != 'svg' or root.get('viewBox') != '0 0 96 96':
            raise SystemExit('svg ' + key)
        for el in root.iter():
            if el.tag.split('}')[-1] in ('text', 'image'):
                raise SystemExit('svg glyph ' + key)

    print('icons', len(lib))
    print('duplicate keys 0')
    print('batch l', len(EXPECT))
    for key, name, cat in EXPECT:
        print(key, name, cat)
    print('icons_l.js ICON_LIB.push')
    print('override clear')
    print('svg xml', len(EXPECT))


if __name__ == '__main__':
    main()
