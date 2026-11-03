#!/usr/bin/env python3
import glob
import json
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app'

EXPECT = [
    ('uav_decoy', '诱饵无人机', '无人'),
    ('uav_asw', '反潜无人机', '无人'),
    ('ruav_recon', '侦察无人直升机', '无人'),
    ('ruav_strike', '打击无人直升机', '无人'),
    ('ruav_ew', '电子战无人直升机', '无人'),
    ('ruav_relay', '中继无人直升机', '无人'),
    ('ruav_cargo', '运输无人直升机', '无人'),
    ('ruav_decoy', '诱饵无人直升机', '无人'),
    ('ruav_target', '靶标无人直升机', '无人'),
    ('loiter_recon', '侦察巡飞弹', '无人'),
    ('loiter_ew', '干扰巡飞弹', '无人'),
    ('loiter_relay', '中继巡飞弹', '无人'),
    ('loiter_decoy', '诱饵巡飞弹', '无人'),
    ('usv_recon', '侦察无人艇', '无人'),
    ('usv_ew', '干扰无人艇', '无人'),
    ('usv_relay', '中继无人艇', '无人'),
    ('usv_cargo', '运输无人艇', '无人'),
    ('usv_decoy', '诱饵无人艇', '无人'),
    ('usv_target', '靶标无人艇', '无人'),
    ('usv_minelayer', '布雷无人艇', '无人'),
    ('uuv_strike', '打击无人潜航器', '无人'),
    ('uuv_ew', '水声干扰潜航器', '无人'),
    ('uuv_relay', '水下中继潜航器', '无人'),
    ('uuv_cargo', '运输无人潜航器', '无人'),
    ('uuv_decoy', '声学诱饵潜航器', '无人'),
    ('uuv_target', '靶标潜航器', '无人'),
    ('ugv_ew', '干扰无人车', '无人'),
    ('ugv_relay', '中继无人车', '无人'),
    ('ugv_decoy', '诱饵无人车', '无人'),
    ('ugv_target', '靶标无人车', '无人'),
    ('asw_patrol', '反潜巡逻机', '空中'),
    ('carrier_fighter', '舰载战斗机', '空中'),
    ('attack_aircraft', '强击机', '空中'),
    ('asw_heli', '反潜直升机', '空中'),
    ('aew_heli', '预警直升机', '空中'),
    ('elint_aircraft', '电子侦察机', '空中'),
    ('ssbn', '战略导弹潜艇', '海上'),
    ('elint_ship', '电子侦察船', '海上'),
    ('lsd', '船坞登陆舰', '海上'),
    ('depth_charge_rl', '火箭深弹', '海上'),
    ('vls', '垂发装置', '陆地'),
    ('aaa_gun', '高射炮', '陆地'),
    ('atgm_vehicle', '反坦克导弹车', '陆地'),
    ('coastal_battery', '岸舰导弹', '陆地'),
    ('mad_sensor', '磁探仪', '感知通信'),
    ('dipping_sonar', '吊放声呐', '感知通信'),
    ('iff_transponder', '敌我识别', '感知通信'),
    ('rwr', '雷达告警', '感知通信'),
    ('sat_recon', '侦察卫星', '感知通信'),
    ('sat_relay', '通信中继卫星', '感知通信'),
    ('sat_nav', '导航卫星', '感知通信'),
    ('sat_ewarn', '导弹预警卫星', '感知通信'),
    ('ashm', '反舰导弹', '空中'),
    ('aam', '空空导弹', '空中'),
    ('arm', '反辐射导弹', '空中'),
    ('atc_tower', '塔台', '设施'),
    ('hangar', '机库', '设施'),
    ('ammo_bunker', '弹药库', '设施'),
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
    m_rows = [(row['key'], row['name'], row['cat']) for row in lib if row['key'] in {k for k, n, c in EXPECT}]
    if m_rows != EXPECT:
        raise SystemExit('batch m rows: ' + repr(m_rows))
    for key, name, cat in EXPECT:
        if names.count(name) != 1:
            raise SystemExit('name count %s %s' % (names.count(name), name))
        if by_key[key]['cat'] != cat:
            raise SystemExit('cat %s %s' % (key, by_key[key]['cat']))

    raw = (APP / 'icons_m.js').read_text(encoding='utf-8')
    if not raw.startswith('ICON_LIB.push'):
        raise SystemExit('icons_m.js does not start with ICON_LIB.push')
    if 'const ICON_LIB' in raw or 'module.exports' in raw:
        raise SystemExit('icons_m.js declares a module or const ICON_LIB')
    if '(?<' in raw or '\u2028' in raw:
        raise SystemExit('icons_m.js has a lookbehind or U+2028')

    appjs = (APP / 'app.js').read_text(encoding='utf-8')
    block = appjs[appjs.index('const ICON_CAT_OVERRIDE'):appjs.index('const iconCats')]
    for key, name, cat in EXPECT:
        if re.search(r'\b' + re.escape(key) + r'\b', block):
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
    print('batch m', len(EXPECT))
    for key, name, cat in EXPECT:
        print(key, name, cat)
    print('icons_m.js ICON_LIB.push')
    print('override clear')
    print('svg xml', len(EXPECT))


if __name__ == '__main__':
    main()
