#!/usr/bin/env bash
# 一键从零构建全部发布物 → _work/dist/ 并生成 SHA256SUMS.txt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"; WORK="${JW_WORK:-$ROOT/_work}"
[ -d node_modules ] || npm ci
bash build/fetch_runtime.sh
python3 build/build_web.py --desk          # dist/offline.html、artifact.html、desk.html
python3 build/web/package_web.py           # 网页版离线包 zip
python3 build/desktop/build_all.py         # Windows x64/x86 安装包与绿色版、麒麟 deb（arm64/amd64）
cd "$WORK/dist" && rm -f SHA256SUMS.txt && sha256sum -- * > SHA256SUMS.txt && cat SHA256SUMS.txt
