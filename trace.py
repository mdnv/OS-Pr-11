"""Визуальная трассировка FIFO: первые 11 обращений (слайд преподавателя)."""
from replace import REFS


def fifo_trace(refs=REFS, n_frames=3, limit=11):
    if n_frames < 1:
        raise ValueError("n_frames должен быть >= 1")
    frames = []
    hand = 0
    for index, page in enumerate(refs[:limit], start=1):
        fault = page not in frames
        if fault:
            if len(frames) < n_frames:
                frames.append(page)
            else:
                frames[hand] = page
                hand = (hand + 1) % n_frames
        state = " ".join(map(str, frames))
        print(f"{index:2d}  обр={page}  [{state:<5}] {'PF' if fault else '  '}" )


if __name__ == "__main__":
    print("FIFO — первые 11 обращений, 3 кадра. PF = page fault")
    fifo_trace()
