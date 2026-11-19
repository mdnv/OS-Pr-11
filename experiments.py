"""Уровень B: график, аномалия Белади и локальность обращений."""
import argparse
import csv
from pathlib import Path
import random

from replace import ALGORITHMS, REFS, fifo, lru, optimal, clock

RESULTS_DIR = Path(__file__).resolve().parent / "results"
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def chart():
    """Построить 4 линии для 1..8 кадров и сохранить PNG + CSV."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # работает в Ubuntu VirtualBox даже без GUI
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("Установите зависимости: python3 -m pip install -r requirements.txt") from exc

    RESULTS_DIR.mkdir(exist_ok=True)
    count = list(range(1, 9))
    values = {name: [func(REFS, n) for n in count] for name, func in ALGORITHMS.items()}

    fig, ax = plt.subplots(figsize=(8.4, 4.9))
    for name, nums in values.items():
        ax.plot(count, nums, marker="o", label=name)
    ax.set(xlabel="Number of frames", ylabel="Page faults", title="Control sequence: frames vs page faults")
    ax.set_xticks(count)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = RESULTS_DIR / "frames_vs_faults.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)

    with (RESULTS_DIR / "frames_vs_faults.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["frames", *ALGORITHMS.keys()])
        for i, n in enumerate(count):
            writer.writerow([n, *(values[name][i] for name in ALGORITHMS)])

    print("График сохранён:", out.relative_to(RESULTS_DIR.parent))
    print("CSV сохранён: results/frames_vs_faults.csv")
    return values


def belady():
    """Сравнить 3/4 кадра на классической последовательности Белади."""
    print("\nАномалия Белади: 1 2 3 4 1 2 5 1 2 3 4 5")
    print(f"{'Алгоритм':<10}{'3 кадра':>9}{'4 кадра':>10}{'Рост?':>8}")
    results = {}
    for name, func in ALGORITHMS.items():
        three = func(BELADY, 3)
        four = func(BELADY, 4)
        results[name] = (three, four)
        print(f"{name:<10}{three:>9}{four:>10}{'ДА' if four > three else 'нет':>8}")
    return results


def random_and_local_refs(seed=5, length=1000, page_count=20, window=3, jump_every=30):
    """Воспроизводимые строки из 1000 обращений, из 20 страниц."""
    rng = random.Random(seed)
    random_refs = [rng.randrange(page_count) for _ in range(length)]

    local_refs = []
    start = 0
    for i in range(length):
        if i % jump_every == 0:
            start = rng.randrange(page_count - window + 1)
        # 89% внутри узкого окна, 11% из всех 20 страниц.
        if rng.random() < 0.89:
            local_refs.append(start + rng.randrange(window))
        else:
            local_refs.append(rng.randrange(page_count))
    return random_refs, local_refs


def locality():
    random_refs, local_refs = random_and_local_refs()
    print("\nСлучайность и локальность: 1000 обращений, 20 страниц, 5 кадров; seed=5")
    print(f"{'Алгоритм':<10}{'Случайно':>11}{'Локально':>11}{'Во сколько раз':>17}")
    rows = {}
    for name, func in ALGORITHMS.items():
        a, b = func(random_refs, 5), func(local_refs, 5)
        rows[name] = (a, b)
        print(f"{name:<10}{a:>11}{b:>11}{a / b:>16.2f}x")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Опыты с алгоритмами замещения страниц")
    parser.add_argument("--no-plot", action="store_true", help="пропустить построение PNG")
    args = parser.parse_args()
    if not args.no_plot:
        chart()
    belady()
    locality()
    print("\nПочему при 6+ кадрах 6 отказов? Строка использует 6 разных страниц:")
    print("каждую надо загрузить однажды, и места для всех хватает.")


if __name__ == "__main__":
    main()
