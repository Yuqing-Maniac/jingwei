"""图标检查。空 ico、没有图标资源的 exe，都让打包失败。"""
import struct
import sys

RT_ICON = 3
RT_GROUP_ICON = 14


def ico_count(data):
    if len(data) < 6:
        return 0
    reserved, kind, count = struct.unpack_from('<HHH', data, 0)
    if reserved != 0 or kind not in (1, 2) or count <= 0:
        return 0
    if len(data) < 6 + 16 * count:
        return 0
    return count


def _rva_to_off(sections, rva):
    for va, raw, span in sections:
        if va <= rva < va + span:
            return raw + (rva - va)
    return None


def _has_resource_type(data, want):
    if len(data) < 0x40 or data[:2] != b'MZ':
        return False
    e_lfanew = struct.unpack_from('<I', data, 0x3C)[0]
    if e_lfanew <= 0 or e_lfanew + 24 > len(data) or data[e_lfanew:e_lfanew + 4] != b'PE\0\0':
        return False
    coff = e_lfanew + 4
    nsections, size_opt = struct.unpack_from('<HH', data, coff + 2)[0], struct.unpack_from('<H', data, coff + 16)[0]
    if nsections <= 0 or nsections > 96 or size_opt < 96:
        return False
    opt = coff + 20
    if opt + size_opt > len(data):
        return False
    magic = struct.unpack_from('<H', data, opt)[0]
    if magic == 0x10B:
        dd_off = opt + 96
        num_dd = struct.unpack_from('<I', data, opt + 92)[0]
    elif magic == 0x20B:
        dd_off = opt + 112
        num_dd = struct.unpack_from('<I', data, opt + 108)[0]
    else:
        return False
    if num_dd <= 2 or dd_off + 8 * 3 > len(data):
        return False
    res_rva, res_size = struct.unpack_from('<II', data, dd_off + 16)
    if res_rva == 0 or res_size == 0:
        return False
    sections = []
    sec_off = opt + size_opt
    for i in range(nsections):
        off = sec_off + 40 * i
        if off + 40 > len(data):
            return False
        vsz, va, rsz, raw = struct.unpack_from('<IIII', data, off + 8)
        sections.append((va, raw, max(vsz, rsz) or 1))
    root = _rva_to_off(sections, res_rva)
    if root is None:
        return False

    def walk(rel, depth):
        off = root + rel
        if off < 0 or off + 16 > len(data):
            return False
        named, ids = struct.unpack_from('<HH', data, off + 12)
        count = named + ids
        if count > 4096:
            return False
        base = off + 16
        for i in range(count):
            pos = base + 8 * i
            if pos + 8 > len(data):
                return False
            nid, ent = struct.unpack_from('<II', data, pos)
            is_dir = ent & 0x80000000
            child = ent & 0x7FFFFFFF
            if depth == 0 and (nid & 0x80000000 or nid != want):
                continue
            if is_dir:
                if walk(child, depth + 1):
                    return True
                continue
            leaf = root + child
            if leaf + 16 > len(data):
                continue
            _data_rva, size = struct.unpack_from('<II', data, leaf)
            if size > 0:
                return True
        return False

    return walk(0, 0)


def exe_has_icon(path):
    data = path if isinstance(path, (bytes, bytearray)) else open(path, 'rb').read()
    return _has_resource_type(data, RT_GROUP_ICON) and _has_resource_type(data, RT_ICON)


def prove():
    if ico_count(b'\x00\x00\x01\x00\x00\x00') != 0:
        raise SystemExit('icon check did not reject an empty ico')
    if exe_has_icon(b'MZ' + b'\x00' * 256):
        raise SystemExit('icon check did not reject an exe without an icon')


if __name__ == '__main__':
    prove()
    kind, path = sys.argv[1], sys.argv[2]
    blob = open(path, 'rb').read()
    if kind == 'ico':
        if ico_count(blob) <= 0:
            raise SystemExit('ico has no images: ' + path)
    elif kind == 'exe':
        if not exe_has_icon(blob):
            raise SystemExit('exe has no icon resource: ' + path)
    else:
        raise SystemExit('usage: check_icons.py ico|exe FILE')
    print('icon ok', path)
