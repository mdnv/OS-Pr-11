#!/usr/bin/env bash
# Безопасный полный прогон A+B+C для Ubuntu; swap/cgroup отдельно.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ "$(uname -s)" != "Linux" ]]; then
  echo 'Запустите этот проект в Ubuntu Linux внутри VirtualBox.' >&2
  exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
  echo 'Сначала выполните: bash setup_ubuntu.sh' >&2
  exit 1
fi
PY=.venv/bin/python
mkdir -p results

echo '=== Уровень A: FIFO / LRU / Optimal / Clock ==='
"$PY" replace.py | tee results/control_results.txt

echo -e '
=== Уровень A: трассировка FIFO ==='
"$PY" trace.py | tee results/fifo_trace.txt

echo -e '
=== Уровень B: график, Белади, локальность ==='
"$PY" experiments.py | tee results/experiment_report.txt

echo -e '
=== Уровень C: LRU-кэш O(1) ==='
"$PY" lru_cache.py

echo -e '
=== Автотесты ==='
"$PY" -m unittest discover -s tests -v

echo -e '
=== Уровень C: Linux faults.c + 2D-массив ==='
make c | tee results/linux_faults.txt

echo -e '
Готово. Итоги сохранены в results/; PNG: results/frames_vs_faults.png'
echo 'Опыт со swap запускается отдельно: bash level_c/linux_vm_demo.sh'
