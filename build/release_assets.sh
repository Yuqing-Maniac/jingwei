#!/usr/bin/env bash
# 正式发版上传清单。
# GitHub 会把资产名里的非 ASCII 抹掉。中文包名因此撞成同一个名字
# （经纬织图_v3.3.14_离线版.zip 与 增量升级.zip 都变成 _v3.3.14_.zip），
# 上传返回 HTTP 422 ReleaseAsset.name already exists。
# 本脚本只把免安装、网页离线、增量包复制成唯一 ASCII 资产名，中文原名作为显示名。
# 不上传 .deb 与安装包 .exe。校验文件按 ASCII 资产名重算，不沿用 dist 里那份
# （那份含中文名和安装包）。
# 用法：bash build/release_assets.sh [dist目录] [输出目录]
# 默认：$JW_WORK/dist → $JW_WORK/assets
# 产出：ASCII 包、SHA256SUMS.txt、upload.list（每行「路径#显示名」，给 gh release upload）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${JW_WORK:-$ROOT/_work}"
DIST="${1:-$WORK/dist}"
OUT="${2:-$WORK/assets}"
[ -d "$DIST" ] || { echo "缺少发布目录 $DIST，先运行 build/build_all.sh" >&2; exit 1; }
rm -rf "$OUT"
mkdir -p "$OUT"
list="$OUT/upload.list"
: > "$list"
ver=""

add_asset() {
  local src=$1 en=$2 label=$3 thisver
  thisver=${en#jingwei_}
  thisver=${thisver%%_*}
  if [ -z "$ver" ]; then
    ver=$thisver
  elif [ "$ver" != "$thisver" ]; then
    echo "版本不一致：$en 与已见到的 $ver" >&2
    exit 1
  fi
  case "$en" in
    *[!A-Za-z0-9._-]*)
      echo "资产名含非 ASCII 或非法字符：$en" >&2
      exit 1
      ;;
  esac
  if [ -e "$OUT/$en" ]; then
    echo "资产名冲突：$en（来自 $label）" >&2
    exit 1
  fi
  cp "$src" "$OUT/$en"
  printf '%s#%s\n' "$OUT/$en" "$label" >> "$list"
  echo "上传 $en  ←  $label"
}

shopt -s nullglob
for f in "$DIST"/*; do
  [ -f "$f" ] || continue
  zh=$(basename "$f")
  case "$zh" in
    SHA256SUMS.txt) continue ;;
    *.deb|*.exe)
      echo "跳过安装包：$zh"
      continue
      ;;
  esac
  case "$zh" in
    经纬织图_v*_Windows_x64_绿色版.zip)
      rest=${zh#经纬织图_}; v=${rest%%_*}
      add_asset "$f" "jingwei_${v}_windows_x64_portable.zip" "$zh"
      ;;
    经纬织图_v*_Windows_x86_绿色版.zip)
      rest=${zh#经纬织图_}; v=${rest%%_*}
      add_asset "$f" "jingwei_${v}_windows_x86_portable.zip" "$zh"
      ;;
    经纬织图_v*_银河麒麟_arm64_免安装.zip)
      rest=${zh#经纬织图_}; v=${rest%%_*}
      add_asset "$f" "jingwei_${v}_kylin_arm64_portable.zip" "$zh"
      ;;
    经纬织图_v*_银河麒麟_x86_64_免安装.zip)
      rest=${zh#经纬织图_}; v=${rest%%_*}
      add_asset "$f" "jingwei_${v}_kylin_x86_64_portable.zip" "$zh"
      ;;
    经纬织图_v*_离线版.zip)
      rest=${zh#经纬织图_}; v=${rest%%_*}
      add_asset "$f" "jingwei_${v}_web_offline.zip" "$zh"
      ;;
    经纬织图_v*_增量升级.zip)
      rest=${zh#经纬织图_}; v=${rest%%_*}
      add_asset "$f" "jingwei_${v}_incremental.zip" "$zh"
      ;;
    *)
      echo "未识别的发布物（不上传，也不静默丢掉）：$zh" >&2
      exit 1
      ;;
  esac
done

[ -n "$ver" ] || { echo "$DIST 下没有可上传的免安装包" >&2; exit 1; }

required=(
  "jingwei_${ver}_windows_x64_portable.zip"
  "jingwei_${ver}_windows_x86_portable.zip"
  "jingwei_${ver}_kylin_x86_64_portable.zip"
  "jingwei_${ver}_kylin_arm64_portable.zip"
  "jingwei_${ver}_web_offline.zip"
  "jingwei_${ver}_incremental.zip"
)
for en in "${required[@]}"; do
  [ -f "$OUT/$en" ] || { echo "缺少正式发布资产：$en" >&2; exit 1; }
done

# 按资产名排序，校验文件放在清单最后。
sort -o "$list" "$list"
(
  cd "$OUT"
  sha256sum "${required[@]}" > SHA256SUMS.txt
)
printf '%s\n' "$OUT/SHA256SUMS.txt" >> "$list"

if grep -E '\.(deb|exe)(#|$)' "$list" >/dev/null; then
  echo "上传清单含安装包" >&2
  exit 1
fi
dups=$(sed 's/#.*//' "$list" | while IFS= read -r p; do basename "$p"; done | sort | uniq -d || true)
if [ -n "$dups" ]; then
  echo "资产名不唯一：" >&2
  printf '%s\n' "$dups" >&2
  exit 1
fi
cat "$list"
