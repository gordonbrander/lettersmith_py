import unittest
from lettersmith.func import compose, thrush, pipe, rest, composable


class test_compose(unittest.TestCase):
    def test_1(self):
        def a(s):
            return s + "a"

        def b(s):
            return s + "b"

        def c(s):
            return s + "c"

        abc = compose(c, b, a)
        s = abc("_")
        self.assertEqual(s, "_abc")


class test_thrush(unittest.TestCase):
    def test_1(self):
        def a(s):
            return s + "a"

        def b(s):
            return s + "b"

        def c(s):
            return s + "c"

        abc = thrush(a, b, c)
        s = abc("_")
        self.assertEqual(s, "_abc")


class test_pipe(unittest.TestCase):
    def test_1(self):
        def a(s):
            return s + "a"

        def b(s):
            return s + "b"

        def c(s):
            return s + "c"

        s = pipe("_", a, b, c)
        self.assertEqual(s, "_abc")


class test_rest(unittest.TestCase):
    def test_1(self):
        def f(a, b, c):
            return (a, b, c)

        fx = rest(f, 2, 3)
        v = fx(1)
        self.assertEqual(v, (1, 2, 3))


class test_composable(unittest.TestCase):
    def test_1(self):
        @composable
        def f(a, b, c):
            return (a, b, c)

        fx = f(2, 3)
        v = fx(1)
        self.assertEqual(v, (1, 2, 3))


if __name__ == '__main__':
    unittest.main()