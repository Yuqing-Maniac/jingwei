#!/usr/bin/env bash
# GitHub runner 的 Azure mirrorlist 偶发 DNS 失败；使用 Ubuntu 官方 HTTPS 源。
set -euo pipefail
for f in /etc/apt/sources.list /etc/apt/sources.list.d/ubuntu.sources; do
  [ -f "$f" ] || continue
  sudo sed -i \
    -e 's|mirror+file:/etc/apt/apt-mirrors.txt|https://archive.ubuntu.com/ubuntu|g' \
    -e 's|http://azure.archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g' \
    -e 's|http://archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g' \
    -e 's|http://security.ubuntu.com/ubuntu|https://security.ubuntu.com/ubuntu|g' "$f"
done
sudo apt-get -o Acquire::Retries=3 -o Acquire::https::Timeout=30 update -q
sudo apt-get -o Acquire::Retries=3 -o Acquire::https::Timeout=30 install -y -q "$@"
