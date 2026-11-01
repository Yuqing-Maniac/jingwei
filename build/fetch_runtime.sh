#!/usr/bin/env bash
# 下载 Electron 22.3.27 运行时（最后一个支持 Windows 7 的版本）到 _work/runtime，并校验 SHA256。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; WORK="${JW_WORK:-$ROOT/_work}"; RT="$WORK/runtime"; mkdir -p "$RT"
V=22.3.27
declare -A SUM=(
  [linux-arm64]=60279395a5ce4eaf3c08f1e717771b203830902d3fe3a7c311bc37deb1a0e15e
  [linux-x64]=631d8eb08098c48ce2b29421e74c69ac0312b1e42f445d8a805414ba1242bf3a
  [win32-ia32]=1119ac7112590cb9c10a8c9b0bb5be65c0e11648a4f1311e6b7a5a00e497c2ce
  [win32-x64]=ad723ed7dad32f9459f7a9de1fd6d718cf713c4809c2431503bea62ce8f786e6
)
for a in linux-arm64 linux-x64 win32-ia32 win32-x64; do
  f="$RT/electron-v$V-$a.zip"
  if [ ! -f "$f" ] || ! echo "${SUM[$a]}  $f" | sha256sum -c --quiet - 2>/dev/null; then
    echo "下载 $a …"; curl -fSL --retry 3 -o "$f" "https://github.com/electron/electron/releases/download/v$V/electron-v$V-$a.zip"
  fi
  echo "${SUM[$a]}  $f" | sha256sum -c -
done
