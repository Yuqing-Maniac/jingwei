"""运行时文件清单从 Electron 压缩包推导，不手写名单。

少一个运行库或图标，打包直接失败。故意删掉的只有语言包、默认示例和沙箱助手。
"""
import os
import zipfile

TRIM = ('resources/default_app.asar', 'version', 'chrome-sandbox')
KEEP_LOCALES = ('zh-CN.pak', 'en-US.pak')
RENAME = {
    'win': {'electron.exe': 'JingWeiZhiTu.exe'},
    'linux': {'electron': 'jingwei-zhitu'},
}
EXTRA = {
    'win': ('resources/app.asar',),
    'linux': ('resources/app.asar', 'icons/icon_256.png'),
}


def keep(name):
    name = name.replace('\\', '/').lstrip('./')
    if not name or name.endswith('/'):
        return False
    if name in TRIM:
        return False
    if name.startswith('locales/') and os.path.basename(name) not in KEEP_LOCALES:
        return False
    return True


def required_names(zip_path, kind):
    rename = RENAME[kind]
    names = []
    seen = set()
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace('\\', '/')
            if not keep(name):
                continue
            name = rename.get(name, name)
            if name in seen:
                continue
            seen.add(name)
            names.append(name)
    for extra in EXTRA[kind]:
        if extra not in seen:
            names.append(extra)
    return tuple(names)


def require_folder(folder, zip_path, kind):
    missing = []
    for rel in required_names(zip_path, kind):
        if not os.path.isfile(os.path.join(folder, *rel.split('/'))):
            missing.append(rel)
    if missing:
        shown = ', '.join(missing[:12])
        more = '' if len(missing) <= 12 else ' …共 %d 个' % len(missing)
        raise SystemExit('portable package is missing: ' + shown + more)
    return missing
