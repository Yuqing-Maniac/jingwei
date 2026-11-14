"""把已经装好的运行目录打成「一个文件夹 + 一个入口文件」。"""
import os
import re
import shutil
import stat
import subprocess
import zipfile
import uuid
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FOLDER = 'JingWeiZhiTu'
WIN_ENTRY = 'JingWeiZhiTu.exe'
LINUX_ENTRY = 'JingWeiZhiTu.sh'
SUPPORTED_OS_IDS = frozenset({
    '35138b9a-5d96-4fbd-8e2d-a2440225f93a',
    '4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38',
    '1f676c76-80e1-4239-95bb-83d0f6d0da78',
    '8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a',
})
MANIFEST_ARCHES = {'win64': 'amd64', 'win32': 'x86'}


def _version_parts(version, count):
    if not isinstance(version, str) or not re.fullmatch(r'[0-9]+(?:\.[0-9]+){' + str(count - 1) + '}', version):
        raise SystemExit('bad manifest version: ' + str(version))
    parts = version.split('.')
    if any(len(part) > 5 or int(part) > 65535 for part in parts):
        raise SystemExit('manifest version component exceeds 65535: ' + version)
    return parts


def validate_manifest(text, version=None, arch=None):
    """Validate rendered launcher XML, including text extracted from RT_MANIFEST."""
    try:
        root = ET.fromstring(text)
    except (ET.ParseError, ValueError) as exc:
        raise SystemExit('invalid launcher manifest XML: ' + str(exc)) from exc
    ns = {'asm': 'urn:schemas-microsoft-com:asm.v1',
          'v3': 'urn:schemas-microsoft-com:asm.v3',
          'compat': 'urn:schemas-microsoft-com:compatibility.v1'}
    if root.tag != '{' + ns['asm'] + '}assembly' or root.get('manifestVersion') != '1.0':
        raise SystemExit('invalid launcher manifest assembly namespace/version')
    identities = root.findall('asm:assemblyIdentity', ns)
    if len(identities) != 1:
        raise SystemExit('launcher manifest must have one assemblyIdentity')
    identity = identities[0]
    if identity.get('type') != 'win32' or identity.get('name') != 'JingWeiZhiTu':
        raise SystemExit('invalid launcher manifest assemblyIdentity')
    _version_parts(identity.get('version'), 4)
    if version is not None:
        _version_parts(version, 3)
        if identity.get('version') != version + '.0':
            raise SystemExit('launcher manifest version does not match ' + version)
    architecture = identity.get('processorArchitecture')
    if architecture not in MANIFEST_ARCHES.values():
        raise SystemExit('invalid launcher manifest architecture: ' + str(architecture))
    if arch is not None:
        expected = MANIFEST_ARCHES.get(arch, arch)
        if expected not in MANIFEST_ARCHES.values() or architecture != expected:
            raise SystemExit('launcher manifest architecture does not match ' + str(arch))
    levels = root.findall('v3:trustInfo/v3:security/v3:requestedPrivileges/v3:requestedExecutionLevel', ns)
    if len(levels) != 1 or levels[0].get('level') != 'asInvoker' or levels[0].get('uiAccess') != 'false':
        raise SystemExit('launcher manifest requires asInvoker and uiAccess=false')
    applications = root.findall('compat:compatibility/compat:application', ns)
    if len(applications) != 1:
        raise SystemExit('launcher manifest must have one compatibility application')
    ids = []
    for supported in applications[0].findall('compat:supportedOS', ns):
        value = supported.get('Id', '')
        if not re.fullmatch(r'\{[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\}', value):
            raise SystemExit('invalid supportedOS GUID: ' + value)
        try:
            ids.append(str(uuid.UUID(value)))
        except ValueError as exc:
            raise SystemExit('invalid supportedOS GUID: ' + value) from exc
    if len(ids) != len(set(ids)) or set(ids) != SUPPORTED_OS_IDS:
        raise SystemExit('launcher manifest supportedOS IDs must match Windows 7/8/8.1/10-11')
    return root


def render_manifest(version, arch):
    _version_parts(version, 3)
    if arch not in MANIFEST_ARCHES:
        raise SystemExit('no launcher for ' + str(arch))
    with open(os.path.join(HERE, 'app.manifest'), encoding='utf-8') as stream:
        text = stream.read().replace('@VER@', version).replace('@ARCH@', MANIFEST_ARCHES[arch])
    validate_manifest(text, version, arch)
    return text


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
    text = render_manifest(version, arch)
    gcc, windres, objdump = _tools(arch)
    if not os.path.isfile(ico):
        raise SystemExit('missing icon: ' + ico)
    work = os.path.dirname(dest)
    os.makedirs(work, exist_ok=True)
    parts = _version_parts(version, 3)
    ver_comma = ','.join(parts) + ',0'
    manifest = os.path.join(work, 'app.manifest')
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
