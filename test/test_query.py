import unittest
from lettersmith import query


class test_filters(unittest.TestCase):
    def test_1(self):

        @query.filters
        def filter_1(x):
            return x is 1

        data = (1, 2, 3)
        value = tuple(filter_1(data))

        self.assertEqual(value, (1,))


class test_rejects(unittest.TestCase):
    def test_1(self):

        @query.rejects
        def reject_1(x):
            return x is 1

        data = (1, 2, 3)
        value = tuple(reject_1(data))

        self.assertEqual(value, (2, 3))


class test_maps(unittest.TestCase):
    def test_1(self):

        @query.maps
        def double(x):
            return x * 2

        data = (1, 2, 3)
        value = tuple(double(data))

        self.assertEqual(value, (2, 4, 6))


if __name__ == '__main__':
    unittest.main()