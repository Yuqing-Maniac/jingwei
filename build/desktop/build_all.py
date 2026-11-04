"""经纬织图 桌面版打包：Windows x64/ia32（绿色 zip + 免管理员安装包）、银河麒麟 deb 与免安装 zip。
用法：python3 build/desktop/build_all.py [win64 win32 deb-arm64 deb-amd64 kylin-amd64 kylin-arm64 ...]
前置：npm ci；bash build/fetch_runtime.sh（Electron 运行时 → _work/runtime）；apt 装 nsis、dpkg-dev。
产物：_work/dist/（可用环境变量 JW_WORK 改工作目录）"""
import os, sys, shutil, subprocess, zipfile, glob, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.environ.get('JW_WORK', os.path.join(ROOT, '_work'))
V = json.load(open(os.path.join(ROOT, 'desktop', 'package.json')))['version']
RT = os.path.join(WORK, 'runtime'); OUT = os.path.join(WORK, 'dist'); TMP = os.path.join(WORK, 'build'); TOOLS = os.path.join(ROOT, 'build', 'desktop')
sys.path.insert(0, os.path.join(ROOT, 'build')); import brand; BRAND = brand.load()   # 机构标识：brand.local.json（不入库）> brand.example.json
EV = '22.3.27'; ICO = os.path.join(ROOT, 'desktop', 'icon.ico'); PNGS = os.path.join(ROOT, 'assets', 'brand', 'out')
run = lambda *a, **k: subprocess.run(list(a), check=True, **k)
targets = sys.argv[1:] or ['win64', 'win32', 'deb-arm64', 'deb-amd64', 'kylin-amd64', 'kylin-arm64']

def stage_app():
    run('python3', os.path.join(ROOT, 'build', 'build_web.py'), '--desk', stdout=subprocess.DEVNULL)
    run('python3', f'{TOOLS}/stage.py')
    asar = f'{TMP}/app.asar'; os.makedirs(TMP, exist_ok=True)
    run('node', os.path.join(ROOT, 'node_modules', '@electron', 'asar', 'bin', 'asar.js'), 'pack', os.path.join(WORK, 'stage', 'app'), asar)
    return asar

def runtime(arch_zip, dest):
    shutil.rmtree(dest, ignore_errors=True); os.makedirs(dest)
    with zipfile.ZipFile(f'{RT}/electron-v{EV}-{arch_zip}.zip') as z: z.extractall(dest)
    for f in glob.glob(f'{dest}/locales/*.pak'):
        if os.path.basename(f) not in ('zh-CN.pak', 'en-US.pak'): os.remove(f)
    for f in ['resources/default_app.asar', 'version']:
        p = f'{dest}/{f}'
        if os.path.exists(p): os.remove(p)

def zipdir(src, zpath, top):
    if os.path.exists(zpath): os.remove(zpath)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, _, fs in os.walk(src):
            for f in sorted(fs):
                full = os.path.join(dp, f); arc = os.path.join(top, os.path.relpath(full, src))
                zi = zipfile.ZipInfo.from_file(full, arc); zi.compress_type = zipfile.ZIP_DEFLATED
                with open(full, 'rb') as fh: z.writestr(zi, fh.read(), compresslevel=9)

def build_win(arch):
    za = {'win64': 'win32-x64', 'win32': 'win32-ia32'}[arch]; tag = {'win64': 'x64', 'win32': 'x86'}[arch]
    d = f'{TMP}/{arch}/JingWeiZhiTu'; runtime(za, d)
    shutil.copy(ASAR, f'{d}/resources/app.asar')
    run('node', f'{TOOLS}/winexe.mjs', f'{d}/electron.exe', f'{d}/JingWeiZhiTu.exe', ICO, V); os.remove(f'{d}/electron.exe')
    open(f'{d}/README.txt', 'w', encoding='utf-8-sig', newline='\r\n').write(README_WIN)
    zipdir(d, f'{OUT}/经纬织图_v{V}_Windows_{tag}_绿色版.zip', 'JingWeiZhiTu')
    nsi = NSI.replace('@VER@', V).replace('@SRC@', d).replace('@ICO@', ICO).replace('@OUT@', f'{OUT}/经纬织图_v{V}_Windows_{tag}_安装包.exe').replace('@ARCH@', tag).replace('@ORG@', BRAND['org']).replace('@COPYRIGHT@', BRAND['copyright'])
    open(f'{TMP}/{arch}/setup.nsi', 'w', encoding='utf-8-sig').write(nsi)
    run('makensis', '-V2', '-INPUTCHARSET', 'UTF8', f'{TMP}/{arch}/setup.nsi')

def build_kylin_zip(arch):
    za = {'kylin-arm64': 'linux-arm64', 'kylin-amd64': 'linux-x64'}[arch]
    da = 'arm64' if arch.endswith('arm64') else 'x86_64'
    d = f'{TMP}/{arch}/JingWeiZhiTu'; runtime(za, d)
    shutil.copy(ASAR, f'{d}/resources/app.asar')
    os.rename(f'{d}/electron', f'{d}/jingwei-zhitu')
    if os.path.exists(f'{d}/chrome-sandbox'): os.remove(f'{d}/chrome-sandbox')
    open(f'{d}/start.sh', 'w', newline='\n').write('#!/bin/sh\ncd "$(dirname "$0")"\nexec ./jingwei-zhitu --no-sandbox "$@"\n')
    os.chmod(f'{d}/start.sh', 0o755); os.chmod(f'{d}/jingwei-zhitu', 0o755)
    open(f'{d}/README.txt', 'w', encoding='utf-8').write(
        f'经纬织图 v{V} 银河麒麟免安装\n解压后在本目录执行：sh start.sh\n无需安装。整个文件夹可拷到任意位置。\n')
    zipdir(d, f'{OUT}/经纬织图_v{V}_银河麒麟_{da}_免安装.zip', 'JingWeiZhiTu')

def write_patch():
    meta = json.dumps({'format': 'jingwei-patch', 'version': 1, 'from': '3.3.13', 'to': V, 'files': ['resources/app.asar']}, ensure_ascii=False, indent=2)
    zpath = f'{OUT}/经纬织图_v{V}_增量升级.zip'
    if os.path.exists(zpath): os.remove(zpath)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr('jingwei-patch.json', meta)
        z.write(ASAR, 'resources/app.asar')

def build_deb(arch):
    za = {'deb-arm64': 'linux-arm64', 'deb-amd64': 'linux-x64'}[arch]; da = arch.split('-')[1]
    root = f'{TMP}/{arch}/root'; shutil.rmtree(f'{TMP}/{arch}', ignore_errors=True)
    app = f'{root}/opt/jingwei-zhitu'; runtime(za, app)
    shutil.copy(ASAR, f'{app}/resources/app.asar')
    os.rename(f'{app}/electron', f'{app}/jingwei-zhitu')
    os.remove(f'{app}/chrome-sandbox')
    os.makedirs(f'{root}/usr/bin'); open(f'{root}/usr/bin/jingwei-zhitu', 'w').write(LAUNCHER); os.chmod(f'{root}/usr/bin/jingwei-zhitu', 0o755)
    os.makedirs(f'{root}/usr/share/applications'); open(f'{root}/usr/share/applications/jingwei-zhitu.desktop', 'w', encoding='utf-8').write(DESKTOP)
    os.makedirs(f'{root}/usr/share/mime/packages'); open(f'{root}/usr/share/mime/packages/jingwei-zhitu.xml', 'w', encoding='utf-8').write(MIME)
    for s in (16, 32, 48, 64, 128, 256, 512):
        dd = f'{root}/usr/share/icons/hicolor/{s}x{s}/apps'; os.makedirs(dd); shutil.copy(f'{PNGS}/icon_{s}.png', f'{dd}/jingwei-zhitu.png')
    os.makedirs(f'{root}/usr/share/pixmaps'); shutil.copy(f'{PNGS}/icon_256.png', f'{root}/usr/share/pixmaps/jingwei-zhitu.png')
    os.makedirs(f'{root}/usr/share/doc/jingwei-zhitu'); open(f'{root}/usr/share/doc/jingwei-zhitu/README.txt', 'w', encoding='utf-8').write(README_DEB)
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(root) for f in fs) // 1024
    os.makedirs(f'{root}/DEBIAN')
    open(f'{root}/DEBIAN/control', 'w', encoding='utf-8').write(CONTROL.replace('@VER@', V).replace('@ARCH@', da).replace('@SIZE@', str(size)).replace('@ORG@', BRAND['org']).replace('@EMAIL@', BRAND['email']))
    for n, s in (('postinst', POSTINST), ('postrm', POSTRM)):
        open(f'{root}/DEBIAN/{n}', 'w').write(s); os.chmod(f'{root}/DEBIAN/{n}', 0o755)
    for dp, dns, fs in os.walk(root):
        for n in dns: os.chmod(os.path.join(dp, n), 0o755)
        for f in fs:
            p = os.path.join(dp, f)
            if 'DEBIAN' in p: continue
            os.chmod(p, 0o755 if (f in ('jingwei-zhitu', 'chrome_crashpad_handler') or f.endswith('.so') or f.endswith('.so.1')) else 0o644)
    deb = f'{OUT}/jingwei-zhitu_{V}_{da}.deb'
    run('dpkg-deb', '--root-owner-group', '-Zxz', '-z6', '--build', root, deb, stdout=subprocess.DEVNULL)
    shutil.copy(deb, f'{OUT}/经纬织图_v{V}_银河麒麟_{"飞腾arm64" if da == "arm64" else "x86_64"}.deb'); os.remove(deb)

README_WIN = f'''经纬织图 v{V} 桌面版（Windows）
==============================
双击 JingWeiZhiTu.exe 即可运行。无需浏览器、无需联网、无需管理员权限。
支持 Windows 7 SP1／8／10／11。

· 本文件夹可放在任意位置（U 盘、桌面、D 盘均可），整个文件夹一起拷贝。
· 建议右键 JingWeiZhiTu.exe → 发送到 → 桌面快捷方式。
· 设置与最近文件保存在 %APPDATA%\\经纬织图。
· 保存工程：Ctrl+S；另存为：Ctrl+Shift+S；全屏：F11。
'''
README_DEB = f'''经纬织图 v{V} 桌面版（银河麒麟）
安装：双击 deb 包用“软件安装器”安装，或终端执行 sudo dpkg -i 经纬织图_*.deb
启动：开始菜单 → 经纬织图；或终端执行 jingwei-zhitu
卸载：sudo dpkg -r jingwei-zhitu
如遇窗口黑屏，可尝试：jingwei-zhitu --gpu（默认关闭显卡加速，兼容国产显卡）
'''
LAUNCHER = r'''#!/bin/sh
# 经纬织图 启动脚本
APP=/opt/jingwei-zhitu/jingwei-zhitu
MISS=$(ldd "$APP" 2>/dev/null | awk '/not found/{print $1}' | tr '\n' ' ')
if [ -n "$MISS" ]; then
  MSG="经纬织图无法启动：系统缺少以下运行库：$MISS
请联系系统管理员安装（通常随系统桌面环境提供）。"
  if command -v zenity >/dev/null 2>&1; then zenity --error --title="经纬织图" --text="$MSG" 2>/dev/null
  elif command -v kdialog >/dev/null 2>&1; then kdialog --title "经纬织图" --error "$MSG" 2>/dev/null
  elif command -v notify-send >/dev/null 2>&1; then notify-send "经纬织图" "$MSG"
  fi
  echo "$MSG" >&2; exit 1
fi
exec "$APP" --no-sandbox "$@"
'''
DESKTOP = '''[Desktop Entry]
Type=Application
Name=经纬织图
Name[zh_CN]=经纬织图
GenericName=体系架构绘图
GenericName[zh_CN]=体系架构绘图
Comment=体系架构图、泳道图绘制，PPT／Visio／draw.io 互转
Exec=/usr/bin/jingwei-zhitu %F
Icon=jingwei-zhitu
Terminal=false
Categories=Graphics;Office;
MimeType=application/x-jingwei-zhitu;application/vnd.openxmlformats-officedocument.presentationml.presentation;application/vnd.ms-visio.drawing.main+xml;
StartupWMClass=经纬织图
'''
MIME = '''<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-jingwei-zhitu">
    <comment>经纬织图工程</comment>
    <comment xml:lang="zh_CN">经纬织图工程</comment>
    <glob pattern="*.jingwei.json" weight="80"/>
    <glob pattern="*.hongtu.json" weight="80"/>
    <icon name="jingwei-zhitu"/>
  </mime-type>
</mime-info>
'''
CONTROL = '''Package: jingwei-zhitu
Version: @VER@
Architecture: @ARCH@
Maintainer: @ORG@ <@EMAIL@>
Installed-Size: @SIZE@
Section: graphics
Priority: optional
Recommends: libgtk-3-0, libnss3, libgbm1, libasound2, libxss1
Description: 经纬织图 - 体系架构绘图（桌面版）
 体系架构图、泳道图绘制工具；文字成图、一键美化、参照生成；
 PPT、Visio、draw.io 打开与互转。全部组件内置，离线运行，无需浏览器。
'''
POSTINST = '''#!/bin/sh
set +e
command -v update-mime-database >/dev/null 2>&1 && update-mime-database /usr/share/mime >/dev/null 2>&1
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database -q /usr/share/applications >/dev/null 2>&1
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor >/dev/null 2>&1
exit 0
'''
POSTRM = POSTINST
NSI = r'''Unicode true
ManifestDPIAware true
SetCompressor /SOLID lzma
SetCompressorDictSize 64
RequestExecutionLevel user
!include "MUI2.nsh"
Name "经纬织图"
Caption "经纬织图 @VER@ 安装"
BrandingText "经纬织图 · 体系架构绘图"
OutFile "@OUT@"
InstallDir "$LOCALAPPDATA\Programs\JingWeiZhiTu"
InstallDirRegKey HKCU "Software\JingWeiZhiTu" "InstallDir"
VIProductVersion "@VER@.0"
VIAddVersionKey /LANG=2052 "ProductName" "经纬织图"
VIAddVersionKey /LANG=2052 "FileDescription" "经纬织图 安装程序"
VIAddVersionKey /LANG=2052 "CompanyName" "@ORG@"
VIAddVersionKey /LANG=2052 "FileVersion" "@VER@"
VIAddVersionKey /LANG=2052 "ProductVersion" "@VER@"
VIAddVersionKey /LANG=2052 "LegalCopyright" "@COPYRIGHT@"
!define MUI_ICON "@ICO@"
!define MUI_UNICON "@ICO@"
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\JingWeiZhiTu.exe"
!define MUI_FINISHPAGE_RUN_TEXT "立即运行 经纬织图"
!define MUI_WELCOMEPAGE_TITLE "欢迎安装 经纬织图 @VER@"
!define MUI_WELCOMEPAGE_TEXT "经纬织图：体系架构图、泳道图绘制，PPT／Visio／draw.io 打开与互转。$\r$\n$\r$\n本程序安装到当前用户目录，无需管理员权限，全部组件内置，离线可用。$\r$\n$\r$\n支持 Windows 7 SP1～Windows 11（@ARCH@）。"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"
Section "main"
  SetShellVarContext current
  nsExec::Exec 'taskkill /IM JingWeiZhiTu.exe /F'
  SetOutPath "$INSTDIR"
  File /r "@SRC@\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\经纬织图"
  CreateShortcut "$SMPROGRAMS\经纬织图\经纬织图.lnk" "$INSTDIR\JingWeiZhiTu.exe" "" "$INSTDIR\JingWeiZhiTu.exe" 0
  CreateShortcut "$SMPROGRAMS\经纬织图\卸载 经纬织图.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\经纬织图.lnk" "$INSTDIR\JingWeiZhiTu.exe" "" "$INSTDIR\JingWeiZhiTu.exe" 0
  WriteRegStr HKCU "Software\JingWeiZhiTu" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "DisplayName" "经纬织图"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "DisplayVersion" "@VER@"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "Publisher" "@ORG@"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "DisplayIcon" "$INSTDIR\JingWeiZhiTu.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu" "NoRepair" 1
  ; “打开方式”列表（不改变默认程序）
  WriteRegStr HKCU "Software\Classes\Applications\JingWeiZhiTu.exe" "FriendlyAppName" "经纬织图"
  WriteRegStr HKCU "Software\Classes\Applications\JingWeiZhiTu.exe\shell\open\command" "" '"$INSTDIR\JingWeiZhiTu.exe" "%1"'
  WriteRegStr HKCU "Software\Classes\Applications\JingWeiZhiTu.exe\SupportedTypes" ".json" ""
  WriteRegStr HKCU "Software\Classes\Applications\JingWeiZhiTu.exe\SupportedTypes" ".vsdx" ""
  WriteRegStr HKCU "Software\Classes\Applications\JingWeiZhiTu.exe\SupportedTypes" ".pptx" ""
  WriteRegStr HKCU "Software\Classes\Applications\JingWeiZhiTu.exe\SupportedTypes" ".drawio" ""
  WriteRegStr HKCU "Software\Classes\.vsdx\OpenWithList\JingWeiZhiTu.exe" "" ""
  WriteRegStr HKCU "Software\Classes\.pptx\OpenWithList\JingWeiZhiTu.exe" "" ""
  WriteRegStr HKCU "Software\Classes\.drawio\OpenWithList\JingWeiZhiTu.exe" "" ""
  WriteRegStr HKCU "Software\Classes\.json\OpenWithList\JingWeiZhiTu.exe" "" ""
SectionEnd
Section "Uninstall"
  SetShellVarContext current
  nsExec::Exec 'taskkill /IM JingWeiZhiTu.exe /F'
  Delete "$DESKTOP\经纬织图.lnk"
  RMDir /r "$SMPROGRAMS\经纬织图"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JingWeiZhiTu"
  DeleteRegKey HKCU "Software\JingWeiZhiTu"
  DeleteRegKey HKCU "Software\Classes\Applications\JingWeiZhiTu.exe"
  DeleteRegKey HKCU "Software\Classes\.vsdx\OpenWithList\JingWeiZhiTu.exe"
  DeleteRegKey HKCU "Software\Classes\.pptx\OpenWithList\JingWeiZhiTu.exe"
  DeleteRegKey HKCU "Software\Classes\.drawio\OpenWithList\JingWeiZhiTu.exe"
  DeleteRegKey HKCU "Software\Classes\.json\OpenWithList\JingWeiZhiTu.exe"
SectionEnd
'''
os.makedirs(OUT, exist_ok=True)
ASAR = stage_app()
for t in targets:
    t0 = time.time()
    fn = build_win if t.startswith('win') else build_kylin_zip if t.startswith('kylin') else build_deb
    fn(t)
    print('built', t, round(time.time() - t0), 's', flush=True)
write_patch()
for f in sorted(os.listdir(OUT)): print(f'{os.path.getsize(os.path.join(OUT, f)) / 2**20:7.1f} MB  {f}')
