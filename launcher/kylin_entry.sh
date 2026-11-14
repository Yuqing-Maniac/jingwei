#!/bin/sh
# 压缩包顶层的唯一入口。程序在旁边的 JingWeiZhiTu 文件夹里。不需要管理员权限。
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
APP=$HERE/JingWeiZhiTu
BIN=$APP/jingwei-zhitu
if [ ! -x "$BIN" ]; then
  printf '%s\n' '请把 JingWeiZhiTu.sh 和旁边的 JingWeiZhiTu 文件夹放在一起，不要只拷走这一个文件。' >&2
  exit 1
fi
DESKTOP=
if command -v xdg-user-dir >/dev/null 2>&1; then
  DESKTOP=$(xdg-user-dir DESKTOP 2>/dev/null || true)
fi
if [ -z "$DESKTOP" ] || [ "$DESKTOP" = "$HOME" ]; then
  if [ -d "$HOME/桌面" ]; then DESKTOP=$HOME/桌面
  else DESKTOP=$HOME/Desktop
  fi
fi
if [ "${1:-}" = "--uninstall" ]; then
  rm -f "$HOME/.local/share/applications/jingwei-zhitu.desktop" "$DESKTOP/经纬织图.desktop"
  find "$HOME/.local/share/icons/hicolor" -name 'jingwei-zhitu.png' -delete 2>/dev/null || true
  printf '%s\n' '已去掉桌面和开始菜单里的经纬织图。程序文件夹还在，可以自行删除。'
  exit 0
fi
mach=$(od -An -tu2 -j 18 -N 2 "$BIN" | tr -d '[:space:]')
host=$(uname -m)
case "$mach:$host" in
  62:x86_64|183:aarch64|183:arm64) ;;
  *) printf '%s\n' "当前系统是 ${host}，与这个包里的程序不匹配。请改用对应架构的银河麒麟包。" >&2
     exit 1 ;;
esac
if [ ! -f "$APP/icons/icon_256.png" ]; then
  printf '%s\n' '缺少图标 icons/icon_256.png。请重新解压完整的包。' >&2
  exit 1
fi
MISS=$(ldd "$BIN" 2>/dev/null | awk '/not found/{print $1}' | tr '\n' ' ' || true)
if [ -n "$MISS" ]; then
  MSG="经纬织图无法启动：系统缺少以下运行库：$MISS"
  if command -v zenity >/dev/null 2>&1; then zenity --error --title="经纬织图" --text="$MSG" 2>/dev/null || true
  elif command -v kdialog >/dev/null 2>&1; then kdialog --title "经纬织图" --error "$MSG" 2>/dev/null || true
  fi
  printf '%s\n' "$MSG" >&2
  exit 1
fi
mkdir -p "$DESKTOP" "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor" || true
for icon in "$APP"/icons/icon_*.png; do
  [ -f "$icon" ] || continue
  base=$(basename "$icon")
  size=${base#icon_}
  size=${size%.png}
  mkdir -p "$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
  cp -f "$icon" "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/jingwei-zhitu.png"
done
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi
write_desktop() {
  dest=$1
  cat > "$dest" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=经纬织图
GenericName=体系架构绘图
Comment=经纬织图 @VER@
Exec="$HERE/JingWeiZhiTu.sh" %F
Path=$HERE
Icon=$APP/icons/icon_256.png
StartupWMClass=jingwei-zhitu
Terminal=false
Categories=Graphics;Office;
EOF
  chmod 755 "$dest" || true
  if command -v gio >/dev/null 2>&1; then
    gio set "$dest" metadata::trusted true >/dev/null 2>&1 || true
  fi
}
write_desktop "$HOME/.local/share/applications/jingwei-zhitu.desktop" || true
write_desktop "$DESKTOP/经纬织图.desktop" || true
if command -v gsettings >/dev/null 2>&1; then
  for schema in org.gnome.shell org.ukui.panel; do
    if gsettings list-schemas 2>/dev/null | grep -qx "$schema"; then
      if gsettings list-keys "$schema" 2>/dev/null | grep -qx favorite-apps; then
        current=$(gsettings get "$schema" favorite-apps 2>/dev/null || printf '%s\n' '@as []')
        case $current in
          *jingwei-zhitu.desktop*) ;;
          '@as []') gsettings set "$schema" favorite-apps "['jingwei-zhitu.desktop']" >/dev/null 2>&1 || true ;;
          *) gsettings set "$schema" favorite-apps "$(printf '%s' "$current" | sed "s/]$/, 'jingwei-zhitu.desktop']/")" >/dev/null 2>&1 || true ;;
        esac
      fi
    fi
  done
fi
cd "$APP"
exec "$BIN" --no-sandbox "$@"
