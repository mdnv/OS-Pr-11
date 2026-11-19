#!/usr/bin/env bash
# WARNING: only in a disposable Linux VM with swap; may trigger cgroup OOM.
set -euo pipefail
if [[ "$(uname -s)" != Linux ]]; then
  echo 'Only Linux VM supports cgroup v2; do not run this on macOS.' >&2
  exit 1
fi
if [[ ! -f /sys/fs/cgroup/cgroup.controllers ]]; then
  echo 'cgroup v2 is required.' >&2
  exit 1
fi
if ! command -v systemd-run >/dev/null 2>&1; then
  echo 'systemd-run is not available. Check the Linux VM.' >&2
  exit 1
fi
if [[ -z "$(swapon --noheadings --show 2>/dev/null)" ]]; then
  echo 'Swap not enabled; enable swap inside your test VM first.' >&2
  exit 1
fi
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
echo 'EXPERIMENT ONLY IN UBUNTU VM: caps RAM at 64 MiB, allows 256 MiB swap.'
if command -v systemd-detect-virt >/dev/null 2>&1; then
  if ! systemd-detect-virt --quiet; then
    echo 'Virtual machine not detected. Aborting for safety.' >&2
    exit 1
  fi
fi
echo 'The test may be slow or terminated by the cgroup OOM killer.'
read -r -p 'Type YES to run inside your Ubuntu VM: ' answer
if [[ "$answer" != YES ]]; then
  echo 'Cancelled.'
  exit 0
fi
sudo systemd-run --scope -p MemoryMax=64M -p MemorySwapMax=256M \
  "$(command -v python3)" "$script_dir/thrash.py" --mib 96 --passes 5
