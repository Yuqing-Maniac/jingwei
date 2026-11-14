"""把已经装好的运行目录打成「一个文件夹 + 一个入口文件」。"""
import os
import shutil
import stat
import subprocess
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FOLDER = 'JingWeiZhiTu'
WIN_ENTRY = 'JingWeiZhiTu.exe'
LINUX_ENTRY = 'JingWeiZhiTu.sh'


def copy_icons(folder):
    src = os.path.join(ROOT, 'assets', 'brand', 'out')
    dest = os.path.join(folder, 'icons')
    os.makedirs(dest, exist_ok=True)
    found = [n for n in os.listdir(src) if n.startswith('icon_') and n.endswith('.png')]
    if 'icon_256.png' not in found:
        raise SystemExit('missing icon_256.png')
    for name in found:
        shutil.copy(os.path.join(src, name), os.path.join(dest, name))


def _tools(arch):
    if arch == 'win64':
        prefix = 'x86_64-w64-mingw32'
    elif arch == 'win32':
        prefix = 'i686-w64-mingw32'
    else:
        raise SystemExit('no launcher for ' + arch)
    gcc = prefix + '-gcc'
    windres = prefix + '-windres'
    objdump = prefix + '-objdump'
    for tool in (gcc, windres, objdump):
        if shutil.which(tool) is None:
            raise SystemExit('missing ' + tool + '（打 Windows 启动器需要 mingw-w64）')
    return gcc, windres, objdump


def compile_launcher(dest, arch, version, ico, brand):
    gcc, windres, objdump = _tools(arch)
    if not os.path.isfile(ico):
        raise SystemExit('missing icon: ' + ico)
    work = os.path.dirname(dest)
    os.makedirs(work, exist_ok=True)
    parts = version.split('.')
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise SystemExit('bad version ' + version)
    ver_comma = ','.join(parts) + ',0'
    manifest = os.path.join(work, 'app.manifest')
    text = open(os.path.join(HERE, 'app.manifest'), encoding='utf-8').read().replace('@VER@', version)
    open(manifest, 'w', encoding='utf-8', newline='\n').write(text)
    rc = os.path.join(work, 'launcher.rc')
    org = brand['org'].replace('"', "'")
    copy = brand['copyright'].replace('"', "'")
    open(rc, 'w', encoding='utf-8', newline='\n').write(
        '#pragma code_page(65001)\n'
        '1 ICON "%s"\n'
        '1 24 "%s"\n'
        '1 VERSIONINFO\n'
        'FILEVERSION %s\n'
        'PRODUCTVERSION %s\n'
        'FILEFLAGSMASK 0x3fL\n'
        'FILEFLAGS 0\n'
        'FILEOS 0x40004L\n'
        'FILETYPE 0x1L\n'
        'FILESUBTYPE 0\n'
        'BEGIN\n'
        '  BLOCK "StringFileInfo"\n'
        '  BEGIN\n'
        '    BLOCK "080404b0"\n'
        '    BEGIN\n'
        '      VALUE "CompanyName", "%s"\n'
        '      VALUE "FileDescription", "经纬织图"\n'
        '      VALUE "FileVersion", "%s"\n'
        '      VALUE "InternalName", "JingWeiZhiTu"\n'
        '      VALUE "LegalCopyright", "%s"\n'
        '      VALUE "OriginalFilename", "JingWeiZhiTu.exe"\n'
        '      VALUE "ProductName", "经纬织图"\n'
        '      VALUE "ProductVersion", "%s"\n'
        '    END\n'
        '  END\n'
        '  BLOCK "VarFileInfo"\n'
        '  BEGIN\n'
        '    VALUE "Translation", 0x804, 1200\n'
        '  END\n'
        'END\n' % (ico.replace('\\', '/'), manifest.replace('\\', '/'), ver_comma, ver_comma, org, version, copy, version)
    )
    res = os.path.join(work, 'launcher.res')
    subprocess.check_call([windres, '-O', 'coff', '-i', rc, '-o', res])
    subprocess.check_call([
        gcc, '-std=c11', '-O2', '-s', '-municode', '-mwindows', '-static',
        '-DWINVER=0x0601', '-D_WIN32_WINNT=0x0601',
        '-Wl,--major-subsystem-version,6,--minor-subsystem-version,1',
        os.path.join(HERE, 'win_launcher.c'), res, '-o', dest,
        '-lole32', '-lshell32', '-luuid', '-lcomctl32',
    ])
    dump = subprocess.check_output([objdump, '-p', dest], text=True, errors='replace')
    for line in dump.splitlines():
        if 'DLL Name:' not in line:
            continue
        name = line.split(':', 1)[1].strip().lower()
        if name.startswith('libgcc') or 'stdc++' in name or 'winpthread' in name or name.startswith('libwin'):
            raise SystemExit('launcher depends on ' + name)
    if 'MajorSubsystemVersion' in dump and '6' not in dump.split('MajorSubsystemVersion', 1)[1][:40]:
        raise SystemExit('launcher subsystem is not Windows 7 compatible')
    return dest


def write_linux_entry(dest, version):
    text = open(os.path.join(HERE, 'kylin_entry.sh'), encoding='utf-8').read().replace('@VER@', version)
    if '\r' in text:
        raise SystemExit('linux entry has CR')
    open(dest, 'w', encoding='utf-8', newline='\n').write(text)
    os.chmod(dest, 0o755)


def mark_exec(folder):
    for dirpath, _, files in os.walk(folder):
        for name in files:
            if name in ('jingwei-zhitu', 'chrome_crashpad_handler') or '.so' in name:
                full = os.path.join(dirpath, name)
                os.chmod(full, os.stat(full).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def zip_portable(src, zpath, entry):
    if os.path.lexists(zpath):
        os.remove(zpath)
    os.makedirs(os.path.dirname(zpath), exist_ok=True)
    with zipfile.ZipFile(zpath, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dirpath, dirnames, files in os.walk(src):
            dirnames.sort()
            for name in sorted(files):
                full = os.path.join(dirpath, name)
                if os.path.islink(full):
                    raise SystemExit('symlink in package: ' + full)
                rel = os.path.relpath(full, src).replace('\\', '/')
                rel.encode('ascii')
                info = zipfile.ZipInfo(rel)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                mode = os.stat(full).st_mode & 0o777
                info.external_attr = mode << 16
                with open(full, 'rb') as fh:
                    z.writestr(info, fh.read(), compresslevel=9)
    assert_portable(zpath, entry)
    return zpath


def assert_portable(zpath, entry):
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if n and not n.endswith('/')]
        if not names:
            raise SystemExit(zpath + ' is empty')
        tops = []
        for name in names:
            name.encode('ascii')
            parts = name.split('/')
            if name.startswith('/') or '\\' in name or '..' in parts:
                raise SystemExit('bad path ' + name)
            if parts[0] not in tops:
                tops.append(parts[0])
        if set(tops) != {FOLDER, entry}:
            raise SystemExit(os.path.basename(zpath) + ' outer entries are ' + ' '.join(sorted(set(tops))))
        if entry not in names:
            raise SystemExit('entry is not a file: ' + entry)
        if not any(n.startswith(FOLDER + '/') for n in names):
            raise SystemExit('runtime folder is empty')
        info = z.getinfo(entry)
        mode = (info.external_attr >> 16) & 0o777
        if entry.endswith('.sh') and not (mode & 0o111):
            raise SystemExit('linux entry is not executable')
        for name in names:
            base = name.rsplit('/', 1)[-1]
            if base in ('jingwei-zhitu', 'JingWeiZhiTu.sh'):
                bit = (z.getinfo(name).external_attr >> 16) & 0o111
                if not bit:
                    raise SystemExit('not executable in zip: ' + name)
    return True
