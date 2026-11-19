#!/usr/bin/env bash
# Установка окружения для Ubuntu 22.04/24.04 внутри VirtualBox.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ "$(uname -s)" != "Linux" ]] || ! command -v apt-get >/dev/null 2>&1; then
  echo "Эта настройка предназначена для Ubuntu Linux (apt-get)." >&2
  exit 1
fi
if ! grep -qi '^ID=ubuntu$' /etc/os-release 2>/dev/null; then
  echo "Предупреждение: Ubuntu не определена; установка рассчитана на Ubuntu 22.04/24.04."
fi

echo '1/3 Устанавливаем пакеты Ubuntu (потребуется пароль sudo)...'
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip build-essential

echo '2/3 Создаём локальное виртуальное окружение Python...'
python3 -m venv .venv

echo '3/3 Устанавливаем matplotlib в .venv...'
.venv/bin/python -m pip install -r requirements.txt

echo 'Готово! Запуск: bash run_ubuntu.sh'
