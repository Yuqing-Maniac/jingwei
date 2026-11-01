#!/usr/bin/env bash
# 测试与视频脚本沿用了开发时的绝对路径（/home/claude/drawtool、/home/claude/vfx、/home/claude/desk/rt …）。
# 本脚本用符号链接把仓库内容摆成原来的目录结构，旧脚本无需修改即可运行。
# 用法：bash tests/legacy_layout.sh      （先 npm ci、python3 build/build_web.py --desk、bash tests/fixtures/fetch_public.sh）
# 已存在且不是本脚本建的目录会被跳过，不会覆盖。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; WORK="${JW_WORK:-$ROOT/_work}"; H="${JW_LEGACY_HOME:-$ROOT/_legacy}"
farm(){ # 目标目录；是本脚本建的才重建
  local d=$1
  if [ -e "$d" ] && [ ! -f "$d/.jw_legacy" ]; then echo "跳过：$d 已存在（非本脚本创建）" >&2; return 1; fi
  rm -rf "$d"; mkdir -p "$d"; touch "$d/.jw_legacy"
}
if farm "$H/drawtool"; then
  for f in "$ROOT"/app/* "$ROOT"/dist/* "$ROOT"/tests/* "$ROOT"/docs/*.md "$ROOT"/build/build_web.py "$ROOT"/build/downlevel.js; do ln -s "$f" "$H/drawtool/$(basename "$f")"; done
  ln -sf "$ROOT/build/build_web.py" "$H/drawtool/build.py"
  ln -s "$ROOT/node_modules" "$H/drawtool/node_modules"
fi
if farm "$H/vfx"; then
  ln -s "$ROOT/tests/fixtures/cn" "$H/vfx/cn"
  for d in dh poi; do [ -d "$WORK/fixtures/$d" ] && ln -s "$WORK/fixtures/$d" "$H/vfx/$d"; done
fi
if farm "$H/desk"; then
  mkdir -p "$H/desk/rt" "$H/desk/tools"
  # 桌面版测试（tests/desktop/etest.py）默认运行 $H/desk/rt/linux-x64/electron：解压运行时并放入 _work/stage/app
  Z="$WORK/runtime/electron-v22.3.27-linux-x64.zip"
  if [ -f "$Z" ]; then
    rm -rf "$WORK/runtime/linux-x64"; mkdir -p "$WORK/runtime/linux-x64"; unzip -q "$Z" -d "$WORK/runtime/linux-x64"
    [ -d "$WORK/stage/app" ] && cp -r "$WORK/stage/app" "$WORK/runtime/linux-x64/resources/app"
    ln -s "$WORK/runtime/linux-x64" "$H/desk/rt/linux-x64"
  fi
  for f in "$ROOT"/tests/desktop/*; do ln -s "$f" "$H/desk/tools/$(basename "$f")"; done
fi
if farm "$H/brand_jw"; then for f in "$ROOT"/assets/brand/*; do ln -s "$f" "$H/brand_jw/$(basename "$f")"; done; fi
echo "旧目录结构已就绪：$H/drawtool  $H/vfx  $H/desk  $H/brand_jw"
