"""
Unit tests for select
"""
import unittest
from lettersmith.select import wheref, selectf, sortf, key, gt
from lettersmith.func import compose_ltr


class test_wheref(unittest.TestCase):
    def test_get_gt(self):
        data = [
            {
                "id": "a",
                "count": 1,
                "items": [1, 2, 3]
            },
            {
                "id": "b",
                "count": 2,
                "items": [1, 2, 3, 4, 5]
            },
            {
                "id": "c",
                "count": 3,
                "items": [1, 2]
            }
        ]

        f = wheref(compose_ltr(key("count"), gt(1)))
        x = tuple(f(data))
        self.assertEqual(len(x), 2)

    def test_get_len_gt(self):
        data = [
            {
                "id": "a",
                "count": 1,
                "items": [1, 2, 3]
            },
            {
                "id": "b",
                "count": 2,
                "items": [1, 2, 3, 4, 5]
            },
            {
                "id": "c",
                "count": 3,
                "items": [1, 2]
            }
        ]

        f = wheref(compose_ltr(key("items"), len, gt(3)))
        x = tuple(f(data))
        self.assertEqual(len(x), 1)


class test_selectf(unittest.TestCase):
    def test_key(self):
        data = [
            {
                "id": "a",
                "count": 1,
                "items": [1, 2, 3]
            },
            {
                "id": "b",
                "count": 2,
                "items": [1, 2, 3, 4, 5]
            },
            {
                "id": "c",
                "count": 3,
                "items": [1, 2]
            }
        ]

        f = selectf(key("id"))
        x = tuple(f(data))
        self.assertEqual(x[0], "a")


class test_sortf(unittest.TestCase):
    def test_key(self):
        data = [
            {
                "id": "a",
                "count": 1,
                "items": [1, 2, 3]
            },
            {
                "id": "b",
                "count": 2,
                "items": [1, 2, 3, 4, 5]
            },
            {
                "id": "c",
                "count": 3,
                "items": [1, 2]
            }
        ]

        f = sortf(compose_ltr(key("items"), len))
        x = tuple(f(data))
        self.assertEqual(x[0]["id"], "c")


if __name__ == '__main__':
    unittest.main()