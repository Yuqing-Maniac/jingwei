#!/usr/bin/env bash
# 核心回归。前置：bash tests/legacy_layout.sh
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
H="${JW_LEGACY_HOME:-$ROOT/_legacy}"; D="$H/drawtool"; fail=0
export JW_LEGACY_HOME="$H"
export PYTHONPATH="$ROOT/tests${PYTHONPATH:+:$PYTHONPATH}"
TMP="${TMPDIR:-/tmp}/claude-0"
mkdir -p "$TMP/rlx" "$TMP/etest"
run(){ local name=$1; shift; echo "== $name"; local out; out=$("$@" 2>&1); local rc=$?; echo "$out" | tail -3
  if [ $rc -ne 0 ] || echo "$out" | grep -qE "Traceback|ERR \[[^]]|errs \[[^]]|page errors: \[[^]]"; then echo "!! $name 失败"; fail=1; fi; }
cd "$D"
run "导出全格式 test.py"          python3 test.py
run "规范检查 stdcheck.py"        python3 stdcheck.py
run "连线路由 route_test"         bash -c "cd route_test && python3 run.py"
run "拖动吸附 route_test/snap"    bash -c "cd route_test && python3 snap.py"
mkdir -p "$D/out/cb"
run "生成转换样例 cbtest2"       python3 cbtest2.py
run "格式转换界面 conv_ui"        bash -c "cd conv_ui && python3 run.py"
run "Visio 原样转换 raw_test"     bash -c "cd raw_test && python3 run.py"
run "单侧圆角导出导回 rl2"        python3 "$D/extra/rl2.py"
run "全形状误识别检查 rl3"         python3 "$D/extra/rl3.py"
run "旧浏览器模拟 oldsim"         python3 "$D/extra/oldsim.py"
[ $fail -eq 0 ] && echo "全部通过" || { echo "有失败项"; exit 1; }
