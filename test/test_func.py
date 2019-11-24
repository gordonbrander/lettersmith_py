import unittest
from lettersmith.func import compose, compose_ltr, pipe


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


if __name__ == '__main__':
    unittest.main()