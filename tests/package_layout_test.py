"""免安装包的形状：顶层只有一个文件夹和一个入口，缺文件或缺图标就失败。"""
import os
import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import zipfile
import uuid
from unittest import mock

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


def test_launcher_manifest():
    expected = {
        '35138b9a-5d96-4fbd-8e2d-a2440225f93a',
        '4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38',
        '1f676c76-80e1-4239-95bb-83d0f6d0da78',
        '8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a',
    }
    for arch, machine in [('win64', 'amd64'), ('win32', 'x86')]:
        text = package_portable.render_manifest('3.6.1', arch)
        root = package_portable.validate_manifest(text, '3.6.1', arch)
        identity = root.find('{urn:schemas-microsoft-com:asm.v1}assemblyIdentity')
        assert identity.get('processorArchitecture') == machine
        nodes = root.findall('.//{urn:schemas-microsoft-com:compatibility.v1}supportedOS')
        assert {str(uuid.UUID(node.get('Id'))) for node in nodes} == expected
        assert len(nodes) == 4
    text = package_portable.render_manifest('3.6.1', 'win64')
    win8 = '{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}'
    bad_cases = [
        text.replace(win8, '{4a2f28e3-53b9-4441-ba9c-d69d4a6e38}'),
        text.replace(win8, '{4a2f28e3-53b9-4441-ba9c-000000000000}'),
        text.replace(win8, '{35138b9a-5d96-4fbd-8e2d-a2440225f93a}'),
        text.replace('version="3.6.1.0"', 'version="3.6.0.0"'),
        text.replace('version="3.6.1.0"', 'version="3.6.65536.0"'),
        text.replace('version="3.6.1.0"', 'version="3.6.1"'),
        text.replace('processorArchitecture="amd64"', 'processorArchitecture="x86"'),
        text.replace('processorArchitecture="amd64"', 'processorArchitecture="*"'),
        text.replace('level="asInvoker"', 'level="requireAdministrator"'),
        text.replace('uiAccess="false"', 'uiAccess="true"'),
        text.replace('name="JingWeiZhiTu"', 'name="OtherApp"'),
        text.replace('urn:schemas-microsoft-com:asm.v1', 'urn:wrong'),
        text.replace('</assembly>', ''),
    ]
    for invalid in bad_cases:
        try:
            package_portable.validate_manifest(invalid, '3.6.1', 'win64')
        except SystemExit:
            pass
        else:
            fail('invalid launcher manifest was accepted')
    # The historical malformed GUID must fail before tools, directories or output files.
    with tempfile.TemporaryDirectory() as tmp:
        dest = os.path.join(tmp, 'not-created', 'JingWeiZhiTu.exe')
        with mock.patch('builtins.open', mock.mock_open(read_data=bad_cases[0])), \
                mock.patch.object(package_portable, '_tools') as tools:
            try:
                package_portable.compile_launcher(dest, 'win64', '3.6.1', 'unused.ico', {})
            except SystemExit as exc:
                assert 'supportedOS GUID' in str(exc), str(exc)
            else:
                fail('compile_launcher accepted the historical invalid GUID')
            tools.assert_not_called()
        assert not os.path.exists(os.path.dirname(dest))


def load_builder():
    spec = importlib.util.spec_from_file_location('jingwei_build_all', os.path.join(ROOT, 'build', 'desktop', 'build_all.py'))
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    return builder


def test_build_options():
    builder = load_builder()
    portable = ['win64', 'win32', 'kylin-amd64', 'kylin-arm64']
    assert builder.parse_args(['--portable-only', '--patch']).targets == portable
    assert builder.parse_args(['win64', '--patch', 'win32', '--installers']).targets == ['win64', 'win32']
    assert builder.parse_args(['--installers', '--patch']).targets == ['win64', 'win32', 'deb-arm64', 'deb-amd64', 'kylin-amd64', 'kylin-arm64']
    for argv in (['--unknown'], ['typo-target']):
        with contextlib.redirect_stderr(io.StringIO()):
            try:
                builder.parse_args(argv)
            except SystemExit as exc:
                assert exc.code == 2
            else:
                fail('invalid build option was accepted: ' + str(argv))
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.multiple(builder, OUT=tmp, ASAR=None, create=True), \
                mock.patch.object(builder, 'stage_app', return_value='test.asar'), \
                mock.patch.object(builder, 'build_win') as windows, \
                mock.patch.object(builder, 'build_deb') as deb, \
                mock.patch.object(builder, 'build_kylin_zip') as kylin, \
                mock.patch.object(builder, 'write_patch') as patch:
            builder.main(['--portable-only', '--patch', 'win64', 'kylin-arm64'])
            windows.assert_called_once_with('win64', True, False)
            kylin.assert_called_once_with('kylin-arm64')
            deb.assert_not_called()
            patch.assert_called_once_with()
            windows.reset_mock()
            patch.reset_mock()
            builder.main(['win32', '--installers'])
            windows.assert_called_once_with('win32', False, True)
            patch.assert_not_called()


def test_deb_trimmed_sandbox():
    builder = load_builder()
    with tempfile.TemporaryDirectory() as tmp:
        runtime_dir = os.path.join(tmp, 'runtime')
        os.makedirs(runtime_dir)
        asar = os.path.join(tmp, 'app.asar')
        with open(asar, 'wb') as stream:
            stream.write(b'test app')
        for target in ('linux-x64', 'linux-arm64'):
            with zipfile.ZipFile(os.path.join(runtime_dir, 'electron-v' + builder.EV + '-' + target + '.zip'), 'w') as archive:
                archive.writestr('electron', b'test binary')
                archive.writestr('chrome-sandbox', b'trim me')
                archive.writestr('resources/default_app.asar', b'trim me')
        def fake_dpkg(*args, **kwargs):
            assert args[0] == 'dpkg-deb'
            with open(args[-1], 'wb') as stream:
                stream.write(b'test deb')
        output = os.path.join(tmp, 'out')
        os.makedirs(output)
        with mock.patch.multiple(builder, RT=runtime_dir, TMP=os.path.join(tmp, 'build'), OUT=output, ASAR=asar, create=True), \
                mock.patch.object(builder, 'run', side_effect=fake_dpkg) as dpkg:
            for arch in ('deb-amd64', 'deb-arm64'):
                builder.build_deb(arch)
                app = os.path.join(builder.TMP, arch, 'root', 'opt', 'jingwei-zhitu')
                assert not os.path.exists(os.path.join(app, 'chrome-sandbox'))
                assert os.path.isfile(os.path.join(app, 'resources', 'app.asar'))
                assert os.access(os.path.join(app, 'jingwei-zhitu'), os.X_OK)
            assert dpkg.call_count == 2


def main():
    test_icon_gate()
    test_required_set()
    test_archive_shape()
    test_linux_entry_shortcut()
    test_launcher_binary()
    test_launcher_manifest()
    test_build_options()
    test_deb_trimmed_sandbox()
    print('package_layout_test ok')


if __name__ == '__main__':
    main()
