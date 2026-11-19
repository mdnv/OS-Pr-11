"""Уровень C: измерение page faults под давлением памяти в Linux VM.

Запускать ТОЛЬКО в учебной VM с включённым swap и cgroup v2.
Обычный запуск без ограничений памяти обычно НЕ покажет пробуксовку.
"""
import argparse
import mmap
import os
import platform
import resource
import time


def main():
    parser = argparse.ArgumentParser(description="Учебный тест свопинга в изолированной Linux VM")
    parser.add_argument("--mib", type=int, default=96, help="размер рабочего набора (MiB)")
    parser.add_argument("--passes", type=int, default=5, help="число полных проходов")
    args = parser.parse_args()
    if platform.system() != "Linux":
        parser.error("Этот эксперимент предназначен для Linux VM с cgroup v2")
    if not (1 <= args.mib <= 256 and 1 <= args.passes <= 20):
        parser.error("Допустимые границы: --mib 1..256, --passes 1..20")
    page_size = os.sysconf("SC_PAGE_SIZE")
    nbytes = args.mib * 1024 * 1024
    print(f"Working set: {args.mib} MiB; page size: {page_size} B; passes: {args.passes}")
    print("Run inside a restricted cgroup with swap, NOT on the host!")
    with mmap.mmap(-1, nbytes) as memory:
        for number in range(1, args.passes + 1):
            before = resource.getrusage(resource.RUSAGE_SELF)
            start = time.monotonic()
            for pos in range(0, nbytes, page_size):
                memory[pos] = (memory[pos] + 1) & 255
            elapsed = time.monotonic() - start
            after = resource.getrusage(resource.RUSAGE_SELF)
            print(f"pass {number}: {elapsed:.3f}s ", end="")
            print(f"minor={after.ru_minflt-before.ru_minflt} ", end="")
            print(f"major={after.ru_majflt-before.ru_majflt}")
    print("More major faults and longer passes under memory pressure may indicate swapping.")


if __name__ == "__main__":
    main()
