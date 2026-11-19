"""Практическая работа №11: FIFO, LRU, Optimal и Clock.

Число отказов = число обращений к страницам, которых нет в кадрах.
"""

# 20 обращений, 6 различных страниц (контрольная строка преподавателя).
REFS = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]


def _check_frames(n_frames):
    if not isinstance(n_frames, int) or isinstance(n_frames, bool) or n_frames < 1:
        raise ValueError("Количество кадров должно быть положительным целым числом")


def fifo(refs, n_frames):
    """FIFO: заменяем страницу, которая была загружена раньше остальных."""
    _check_frames(n_frames)
    frames = []
    hand = 0
    faults = 0

    for page in refs:
        if page in frames:
            continue
        faults += 1
        if len(frames) < n_frames:
            frames.append(page)
        else:
            frames[hand] = page
            hand = (hand + 1) % n_frames
    return faults


def lru(refs, n_frames):
    """LRU: удаляем страницу, которую дольше всего не использовали."""
    _check_frames(n_frames)
    frames = []
    last_used = {}
    faults = 0

    for t, page in enumerate(refs):
        if page not in frames:
            faults += 1
            if len(frames) < n_frames:
                frames.append(page)
            else:
                victim = min(frames, key=lambda p: last_used[p])
                frames[frames.index(victim)] = page
        # Важно: обновляем при КАЖДОМ обращении, включая попадания.
        last_used[page] = t
    return faults


def optimal(refs, n_frames):
    """Optimal: удаляем страницу, которая понадобится позже всех."""
    _check_frames(n_frames)
    refs = list(refs)  # нужен просмотр будущих обращений
    frames = []
    faults = 0

    for i, page in enumerate(refs):
        if page in frames:
            continue
        faults += 1
        if len(frames) < n_frames:
            frames.append(page)
            continue
        future = refs[i + 1:]
        # Страница, которая больше не встретится, удаляется первой.
        victim = max(frames, key=lambda p: future.index(p) if p in future else float("inf"))
        frames[frames.index(victim)] = page
    return faults


def clock(refs, n_frames):
    """Clock: круговая стрелка и биты недавнего обращения (second chance)."""
    _check_frames(n_frames)
    frames = [None] * n_frames
    reference_bits = [0] * n_frames
    hand = 0
    faults = 0

    for page in refs:
        if page in frames:
            reference_bits[frames.index(page)] = 1
            continue

        faults += 1
        # Если бит = 1, даём второй шанс; при 0 заменяем.
        while frames[hand] is not None and reference_bits[hand] == 1:
            reference_bits[hand] = 0
            hand = (hand + 1) % n_frames

        frames[hand] = page
        reference_bits[hand] = 1
        hand = (hand + 1) % n_frames
    return faults


ALGORITHMS = {"FIFO": fifo, "LRU": lru, "Optimal": optimal, "Clock": clock}


def table(refs=REFS, frame_counts=(3, 4)):
    rows = []
    for n in frame_counts:
        rows.append((n, *[algorithm(refs, n) for algorithm in ALGORITHMS.values()]))
    return rows


def main():
    print("Практическая работа №11 — алгоритмы замещения страниц")
    print("Контрольная строка:", " ".join(map(str, REFS)))
    print(f"{'Кадры':<7}{'FIFO':>7}{'LRU':>7}{'Optimal':>10}{'Clock':>8}")
    for n, a, b, c, d in table():
        print(f"{n:<7}{a:>7}{b:>7}{c:>10}{d:>8}")


if __name__ == "__main__":
    main()
