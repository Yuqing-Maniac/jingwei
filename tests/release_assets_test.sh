#!/usr/bin/env bash
# 正式发版资产：ASCII 名互不冲突，且安装包不进入上传清单。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/build/release_assets.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

strip_non_ascii() {
  printf '%s' "$1" | LC_ALL=C tr -cd '\000-\177'
}

# 复现 jingwei-v3.3.14 的 422：抹掉中文后，离线包和增量包变成同一个资产名。
offline_raw=$(strip_non_ascii "经纬织图_v3.3.14_离线版.zip")
incremental_raw=$(strip_non_ascii "经纬织图_v3.3.14_增量升级.zip")
[ "$offline_raw" = "_v3.3.14_.zip" ]
[ "$incremental_raw" = "$offline_raw" ]
win_x86_raw=$(strip_non_ascii "经纬织图_v3.3.14_Windows_x86_绿色版.zip")
[ "$win_x86_raw" = "_v3.3.14_Windows_x86_.zip" ]

fill_dist() {
  local d=$1
  mkdir -p "$d"
  printf 'x64' > "$d/经纬织图_v3.3.14_Windows_x64_绿色版.zip"
  printf 'x86' > "$d/经纬织图_v3.3.14_Windows_x86_绿色版.zip"
  printf 'k64' > "$d/经纬织图_v3.3.14_银河麒麟_x86_64_免安装.zip"
  printf 'karm' > "$d/经纬织图_v3.3.14_银河麒麟_arm64_免安装.zip"
  printf 'web' > "$d/经纬织图_v3.3.14_离线版.zip"
  printf 'inc' > "$d/经纬织图_v3.3.14_增量升级.zip"
  printf 'nsis64' > "$d/经纬织图_v3.3.14_Windows_x64_安装包.exe"
  printf 'nsis32' > "$d/经纬织图_v3.3.14_Windows_x86_安装包.exe"
  printf 'debarm' > "$d/经纬织图_v3.3.14_银河麒麟_飞腾arm64.deb"
  printf 'debamd' > "$d/经纬织图_v3.3.14_银河麒麟_x86_64.deb"
  printf 'not-uploaded' > "$d/SHA256SUMS.txt"
}

fill_dist "$TMP/dist"
bash "$SCRIPT" "$TMP/dist" "$TMP/out" > "$TMP/log"

expect=(
  jingwei_v3.3.14_windows_x64_portable.zip
  jingwei_v3.3.14_windows_x86_portable.zip
  jingwei_v3.3.14_kylin_x86_64_portable.zip
  jingwei_v3.3.14_kylin_arm64_portable.zip
  jingwei_v3.3.14_web_offline.zip
  jingwei_v3.3.14_incremental.zip
  SHA256SUMS.txt
)

mapfile -t lines < "$TMP/out/upload.list"
[ "${#lines[@]}" -eq "${#expect[@]}" ]

names=()
for line in "${lines[@]}"; do
  path=${line%%#*}
  label=${line#*#}
  name=$(basename "$path")
  names+=("$name")
  case "$name" in
    *[!A-Za-z0-9._-]*) echo "资产名不是 ASCII：$name" >&2; exit 1 ;;
  esac
  case "$name" in
    *darwin*|*macos*|*osx*|*mac_*) echo "不应发明 macOS 资产：$name" >&2; exit 1 ;;
  esac
  [ -f "$TMP/out/$name" ]
  if [ "$name" = "SHA256SUMS.txt" ]; then
    [ "$path" = "$line" ]
  else
    [ "$label" != "$name" ]
    case "$label" in
      经纬织图_v3.3.14_*) ;;
      *) echo "显示名应保留中文原名：$label" >&2; exit 1 ;;
    esac
  fi
  # 新名字经同样的抹字规则后保持不变，因此不会再撞车。
  [ "$(strip_non_ascii "$name")" = "$name" ]
done

uniq_count=$(printf '%s\n' "${names[@]}" | sort | uniq | wc -l)
[ "$uniq_count" -eq "${#names[@]}" ]

for en in "${expect[@]}"; do
  printf '%s\n' "${names[@]}" | grep -qx "$en"
done

if find "$TMP/out" -type f \( -name '*.deb' -o -name '*.exe' \) | grep -q .; then
  echo "输出目录含安装包" >&2
  exit 1
fi
if printf '%s\n' "${lines[@]}" | grep -E '\.(deb|exe)(#|$)' >/dev/null; then
  echo "上传清单含安装包" >&2
  exit 1
fi

[ "$(wc -l < "$TMP/out/SHA256SUMS.txt")" -eq "$(( ${#expect[@]} - 1 ))" ]
(cd "$TMP/out" && sha256sum -c SHA256SUMS.txt >/dev/null)
# 可选发布物也必须受校验保护，不能只列两份必选包。
printf 'tampered' >> "$TMP/out/jingwei_v3.3.14_web_offline.zip"
if (cd "$TMP/out" && sha256sum -c SHA256SUMS.txt >/dev/null 2>&1); then
  echo "可选网页包损坏时应当校验失败" >&2
  exit 1
fi
printf 'web' > "$TMP/out/jingwei_v3.3.14_web_offline.zip"
if grep -E '安装|\.deb|\.exe|经纬|免安装|离线|增量|绿色' "$TMP/out/SHA256SUMS.txt" >/dev/null; then
  echo "SHA256SUMS 应只列出 ASCII 资产名" >&2
  exit 1
fi
# dist 里那份含安装包的校验不能原样上传；复制的是包内容本身。
[ "$(cat "$TMP/out/SHA256SUMS.txt")" != "not-uploaded" ]
[ "$(cat "$TMP/out/jingwei_v3.3.14_web_offline.zip")" = "web" ]
[ "$(cat "$TMP/out/jingwei_v3.3.14_windows_x86_portable.zip")" = "x86" ]

# 缺一个免安装包时失败，避免再发出半套正式版。
mkdir -p "$TMP/partial"
cp -a "$TMP/dist/." "$TMP/partial/"
rm "$TMP/partial/经纬织图_v3.3.14_Windows_x64_绿色版.zip"
if bash "$SCRIPT" "$TMP/partial" "$TMP/partial-out" >"$TMP/partial.log" 2>&1; then
  echo "缺少资产时应当失败" >&2
  exit 1
fi
grep -q '缺少正式发布资产' "$TMP/partial.log"

# 认不出的文件失败，避免新的发布物被静默丢掉。
mkdir -p "$TMP/extra"
cp -a "$TMP/dist/." "$TMP/extra/"
printf 'x' > "$TMP/extra/notes.txt"
if bash "$SCRIPT" "$TMP/extra" "$TMP/extra-out" >"$TMP/extra.log" 2>&1; then
  echo "未识别文件时应当失败" >&2
  exit 1
fi
grep -q '未识别的发布物' "$TMP/extra.log"

# 同一目录里混入另一个版本时失败。
mkdir -p "$TMP/mixed"
cp -a "$TMP/dist/." "$TMP/mixed/"
printf 'other' > "$TMP/mixed/经纬织图_v9.9.9_离线版.zip"
if bash "$SCRIPT" "$TMP/mixed" "$TMP/mixed-out" >"$TMP/mixed.log" 2>&1; then
  echo "版本不一致时应当失败" >&2
  exit 1
fi
grep -q '版本不一致' "$TMP/mixed.log"

# 只放本次发布的两份包时也能通过。网页包、32 位、麒麟 x86_64、增量包不是必选项。
mkdir -p "$TMP/two"
printf 'x64' > "$TMP/two/经纬织图_v3.3.14_Windows_x64_绿色版.zip"
printf 'karm' > "$TMP/two/经纬织图_v3.3.14_银河麒麟_arm64_免安装.zip"
bash "$SCRIPT" "$TMP/two" "$TMP/two-out" > "$TMP/two.log"
[ -f "$TMP/two-out/jingwei_v3.3.14_windows_x64_portable.zip" ]
[ -f "$TMP/two-out/jingwei_v3.3.14_kylin_arm64_portable.zip" ]
[ ! -f "$TMP/two-out/jingwei_v3.3.14_web_offline.zip" ]
[ ! -f "$TMP/two-out/jingwei_v3.3.14_windows_x86_portable.zip" ]
two_names=$(cd "$TMP/two-out" && sha256sum -c SHA256SUMS.txt >/dev/null && awk '{print $2}' SHA256SUMS.txt)
printf '%s\n' "$two_names" | grep -qx 'jingwei_v3.3.14_windows_x64_portable.zip'
printf '%s\n' "$two_names" | grep -qx 'jingwei_v3.3.14_kylin_arm64_portable.zip'
[ "$(printf '%s\n' "$two_names" | wc -l)" -eq 2 ]

echo "release_assets_test ok"
