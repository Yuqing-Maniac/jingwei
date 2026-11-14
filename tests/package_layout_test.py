"""免安装包的形状：顶层只有一个文件夹和一个入口，缺文件或缺图标就失败。"""
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'launcher'))
import app_files
import check_icons
import package_portable


def fail(msg):
    raise SystemExit(msg)


def test_icon_gate():
    check_icons.prove()
    ico = os.path.join(ROOT, 'desktop', 'icon.ico')
    if check_icons.ico_count(open(ico, 'rb').read()) <= 0:
        fail('desktop/icon.ico has no images')


def test_required_set():
    tmp = tempfile.mkdtemp()
    try:
        zpath = os.path.join(tmp, 'rt.zip')
        with zipfile.ZipFile(zpath, 'w') as z:
            z.writestr('electron.exe', b'e')
            z.writestr('a.dll', b'd')
            z.writestr('locales/zh-CN.pak', b'z')
            z.writestr('locales/en-US.pak', b'e')
            z.writestr('locales/fr.pak', b'f')
            z.writestr('resources/default_app.asar', b'x')
            z.writestr('version', b'1')
            z.writestr('chrome-sandbox', b's')
        names = app_files.required_names(zpath, 'win')
        if 'fr.pak' in ''.join(names) or 'default_app.asar' in names or 'version' in names:
            fail('trimmed files leaked into the required set: ' + ' '.join(names))
        if 'JingWeiZhiTu.exe' not in names or 'a.dll' not in names or 'resources/app.asar' not in names:
            fail('required set lost a runtime file: ' + ' '.join(names))
        folder = os.path.join(tmp, 'JingWeiZhiTu')
        os.makedirs(os.path.join(folder, 'locales'))
        os.makedirs(os.path.join(folder, 'resources'))
        for rel in names:
            if rel == 'JingWeiZhiTu.exe':
                open(os.path.join(folder, 'JingWeiZhiTu.exe'), 'wb').write(b'e')
            else:
                path = os.path.join(folder, *rel.split('/'))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, 'wb').write(b'x')
        app_files.require_folder(folder, zpath, 'win')
        os.remove(os.path.join(folder, 'a.dll'))
        try:
            app_files.require_folder(folder, zpath, 'win')
        except SystemExit as exc:
            if 'a.dll' not in str(exc):
                fail('missing file was not named: ' + str(exc))
        else:
            fail('missing runtime file did not fail the build')
    finally:
        shutil.rmtree(tmp)


def test_archive_shape():
    tmp = tempfile.mkdtemp()
    try:
        root = os.path.join(tmp, 'root')
        folder = os.path.join(root, 'JingWeiZhiTu')
        os.makedirs(folder)
        open(os.path.join(folder, 'jingwei-zhitu'), 'wb').write(b'b')
        os.chmod(os.path.join(folder, 'jingwei-zhitu'), 0o755)
        entry = os.path.join(root, 'JingWeiZhiTu.sh')
        open(entry, 'w', encoding='utf-8').write('#!/bin/sh\n')
        os.chmod(entry, 0o755)
        good = os.path.join(tmp, 'good.zip')
        package_portable.zip_portable(root, good, 'JingWeiZhiTu.sh')
        open(os.path.join(root, 'extra.txt'), 'w', encoding='utf-8').write('x')
        bad = os.path.join(tmp, 'bad.zip')
        try:
            package_portable.zip_portable(root, bad, 'JingWeiZhiTu.sh')
        except SystemExit as exc:
            if 'outer entries' not in str(exc):
                fail('extra top-level file was not rejected: ' + str(exc))
        else:
            fail('extra top-level file was accepted')
    finally:
        shutil.rmtree(tmp)


def test_linux_entry_shortcut():
    tmp = tempfile.mkdtemp()
    home = os.path.join(tmp, 'home')
    os.makedirs(home)
    root = os.path.join(tmp, 'pkg')
    app = os.path.join(root, 'JingWeiZhiTu')
    os.makedirs(os.path.join(app, 'icons'))
    shutil.copy(os.path.join(ROOT, 'assets', 'brand', 'out', 'icon_256.png'), os.path.join(app, 'icons', 'icon_256.png'))
    shutil.copy('/bin/true', os.path.join(app, 'jingwei-zhitu'))
    os.chmod(os.path.join(app, 'jingwei-zhitu'), 0o755)
    entry = os.path.join(root, 'JingWeiZhiTu.sh')
    package_portable.write_linux_entry(entry, '3.5.2')
    env = os.environ.copy()
    env['HOME'] = home
    env['DBUS_SESSION_BUS_ADDRESS'] = 'disabled:'
    env.pop('XDG_CONFIG_HOME', None)
    proc = subprocess.run([entry], cwd=root, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        fail('linux entry failed: ' + proc.stderr + proc.stdout)
    desktop = os.path.join(home, 'Desktop', '经纬织图.desktop')
    menu = os.path.join(home, '.local', 'share', 'applications', 'jingwei-zhitu.desktop')
    text = open(desktop, encoding='utf-8').read()
    if 'Icon=' + os.path.join(app, 'icons', 'icon_256.png') not in text:
        fail('desktop file icon is wrong: ' + text)
    if 'JingWeiZhiTu.sh' not in text or '3.5.2' not in text:
        fail('desktop file does not point at the entry: ' + text)
    if not os.path.isfile(menu):
        fail('start menu entry was not written')
    proc = subprocess.run([entry, '--uninstall'], cwd=root, env=env, capture_output=True, text=True)
    if proc.returncode != 0 or os.path.exists(desktop):
        fail('uninstall left the desktop file')
    shutil.rmtree(tmp)


def test_launcher_binary():
    if not shutil.which('x86_64-w64-mingw32-gcc'):
        return
    tmp = tempfile.mkdtemp()
    try:
        dest = os.path.join(tmp, 'JingWeiZhiTu.exe')
        package_portable.compile_launcher(
            dest, 'win64', '3.5.2', os.path.join(ROOT, 'desktop', 'icon.ico'),
            {'org': '经纬织图开发组', 'copyright': '经纬织图开发组'})
        if not check_icons.exe_has_icon(dest):
            fail('compiled launcher has no icon')
        if os.path.getsize(dest) < 1000:
            fail('launcher is unexpectedly small')
    finally:
        shutil.rmtree(tmp)


def main():
    test_icon_gate()
    test_required_set()
    test_archive_shape()
    test_linux_entry_shortcut()
    test_launcher_binary()
    print('package_layout_test ok')


if __name__ == '__main__':
    main()
