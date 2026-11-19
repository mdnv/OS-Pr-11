#!/usr/bin/env bash
# Диагностика готовности Ubuntu VM к опыту с cgroup и swap.
set -euo pipefail
if [[ "$(uname -s)" != "Linux" ]]; then
  echo 'Только Linux.' >&2
  exit 1
fi
printf 'OS: '
if [[ -r /etc/os-release ]]; then
  (. /etc/os-release && echo "${PRETTY_NAME:-Linux}")
else
  echo Linux
fi
printf 'VM: '
if command -v systemd-detect-virt >/dev/null 2>&1; then
  systemd-detect-virt || echo 'не обнаружена'
else
  echo 'проверка недоступна'
fi
printf 'Python: '; python3 --version
printf 'GCC: '; gcc --version | head -n 1
printf '
RAM / swap:
'; free -h
printf '
Активный swap:
'; swapon --show || true
if [[ -f /sys/fs/cgroup/cgroup.controllers ]]; then
  echo 'cgroup v2: доступна'
else
  echo 'cgroup v2: не обнаружена'
fi
