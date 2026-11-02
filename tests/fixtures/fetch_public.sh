#!/usr/bin/env bash
# 下载公开 Visio 样例（不入库）：dave-howard/vsdx 的 tests/*.vsdx（21 个）与 apache/poi 的 test-data/diagram/*.vsdx（13 个）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; WORK="${JW_WORK:-$ROOT/_work}"; FX="$WORK/fixtures"; mkdir -p "$FX"
sparse(){ # repo dir paths...
  local repo=$1 dir=$2; shift 2
  if [ ! -d "$FX/$dir/.git" ]; then
    git clone --depth 1 --filter=blob:none --sparse "https://github.com/$repo" "$FX/$dir"
  fi
  git -C "$FX/$dir" sparse-checkout set "$@"
}
sparse dave-howard/vsdx dh tests vsdx/media
sparse apache/poi poi test-data/diagram
find "$FX" -name '*.vsdx' | wc -l
