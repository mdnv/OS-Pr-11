"""Запуск: python3 -m unittest discover -s tests -v"""
import contextlib
import io
import unittest

from experiments import BELADY, random_and_local_refs
from lru_cache import LRUCache
from replace import ALGORITHMS, REFS, clock, fifo, lru, optimal
from trace import fifo_trace


class TestAlgorithms(unittest.TestCase):
    def test_control_reference_3_frames(self):
        self.assertEqual([f(REFS, 3) for f in ALGORITHMS.values()], [15, 12, 9, 14])

    def test_control_reference_4_frames(self):
        self.assertEqual([f(REFS, 4) for f in ALGORITHMS.values()], [10, 8, 8, 9])

    def test_six_unique_pages(self):
        self.assertEqual(len(set(REFS)), 6)
        for n in [6, 7, 8]:
            for f in ALGORITHMS.values():
                self.assertEqual(f(REFS, n), 6)

    def test_fifo_belady(self):
        self.assertEqual((fifo(BELADY, 3), fifo(BELADY, 4)), (9, 10))

    def test_lru_and_optimal_are_stack_algorithms_for_belady(self):
        for f in (lru, optimal):
            self.assertLessEqual(f(BELADY, 4), f(BELADY, 3))

    def test_empty_and_repeat(self):
        for f in ALGORITHMS.values():
            self.assertEqual(f([], 2), 0)
            self.assertEqual(f([1, 1, 1], 2), 1)
            self.assertEqual(f([0, 1, 2], 2), 3)

    def test_invalid_frames(self):
        for f in ALGORITHMS.values():
            for n in [0, -1, 2.5, True]:
                with self.subTest(f=f.__name__, n=n):
                    with self.assertRaises(ValueError):
                        f([1, 2], n)

    def test_fifo_trace(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            fifo_trace()
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 11)
        self.assertIn("[2 0 1] PF", lines[3])
        self.assertIn("[2 0 1]", lines[4])
        self.assertNotIn("PF", lines[4])
        self.assertIn("[0 2 3] PF", lines[10])

    def test_random_reproducible(self):
        sample = random_and_local_refs()
        self.assertEqual(sample, random_and_local_refs())
        self.assertEqual(len(sample[0]), 1000)
        self.assertEqual(len(sample[1]), 1000)
        self.assertTrue(all(0 <= p < 20 for seq in sample for p in seq))


class TestCache(unittest.TestCase):
    def test_lru_cache(self):
        c = LRUCache(2)
        c.put(1, "a")
        c.put(2, "b")
        self.assertEqual(c.get(1), "a")
        c.put(3, "c")
        self.assertEqual(c.get(2), -1)
        self.assertEqual(c.get(3), "c")
        c.put(1, "new")
        self.assertEqual(c.get(1), "new")

    def test_cache_one_slot(self):
        c = LRUCache(1)
        c.put(10, 10)
        c.put(20, 20)
        self.assertEqual(c.get(10), -1)
        self.assertEqual(c.get(20), 20)


if __name__ == "__main__":
    unittest.main()
