#!/usr/bin/env python3
import sys
sys.path = ["../src"] + sys.path
import controlpool as cp
import unittest


def sqrt(x):
    return x**0.5


def psqrt(n, x):
    return (n, x**0.5)

def rsqrt(n, x, p = 0):
    if n > 0:
        raise ValueError()
    return x**0.5

def partial_rsqrt(n, x):
    if n > 0 and x > 8:
        raise ValueError()
    return x**0.5

def all_rsqrt(n, x):
    if x > 8:
        raise ValueError()
    return x**0.5

def sqrt_test(x, n):
    pool = cp.Pool(sqrt, n)
    return pool.map(x)


def multysqrt(x, y, n):
    pool = cp.Pool(sqrt, n)
    return pool.map(x), pool.map(y)


def withsqrt(x, n):
    with cp.Pool(sqrt, n) as pool:
        return pool.map(x)


def withmultysqrt(x, y, n):
    with cp.Pool(sqrt, n) as pool:
        return pool.map(x), pool.map(y)


def withrsqrt(x, n):
    with cp.Pool(rsqrt, n, worker_params=range(n)) as pool:
        return pool.map(x)

def withprsqrt(x, n):
    with cp.Pool(partial_rsqrt, n, worker_params=range(n)) as pool:
        return pool.map(x)

def witharsqrt(x, n):
    with cp.Pool(all_rsqrt, n, worker_params=range(n)) as pool:
        return pool.map(x)

def psqrt_test(x, n):
    pool = cp.Pool(psqrt, n, worker_params=range(n))
    res = pool.map(x)
    for r in res:
        if type(r[0]) is not int or r[0] < 0 or r[0] >= n:
            raise RuntimeError("Wrong n")
    return [r[1] for r in res]


class SimpleCalc(unittest.TestCase):
    def test_sqrt(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(sqrt_test(x, 2), control)

    def test_multysqrt(self):
        x = list(range(20))
        y = list(range(0, 30, 2))
        control = list(map(sqrt, x)), list(map(sqrt, y))
        self.assertEqual(multysqrt(x, y, 2), control)

    def test_with(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(sqrt_test(x, 2), control)

    def test_withmultysqrt(self):
        x = list(range(20))
        y = list(range(0, 30, 2))
        control = list(map(sqrt, x)), list(map(sqrt, y))
        self.assertEqual(multysqrt(x, y, 2), control)

    def test_big_sqrt(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(sqrt_test(x, 200), control)

    def test_big_multysqrt(self):
        x = list(range(20))
        y = list(range(0, 30, 2))
        control = list(map(sqrt, x)), list(map(sqrt, y))
        self.assertEqual(multysqrt(x, y, 200), control)

    def test_big_with(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(sqrt_test(x, 200), control)

    def test_big_withmultysqrt(self):
        x = list(range(20))
        y = list(range(0, 30, 2))
        control = list(map(sqrt, x)), list(map(sqrt, y))
        self.assertEqual(multysqrt(x, y, 200), control)

    def test_psqrt(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(psqrt_test(x, 2), control)

    def test_rsqrt(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(withrsqrt(x, 4), control)

    def test_prsqrt(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertEqual(withprsqrt(x, 4), control)

    def test_arsqrt(self):
        x = list(range(20))
        control = list(map(sqrt, x))
        self.assertRaises(RuntimeError, witharsqrt, x, 4)


if __name__ == '__main__':
    unittest.main()
