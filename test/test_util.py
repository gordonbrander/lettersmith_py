import unittest
from lettersmith import util


class test_compose(unittest.TestCase):
    def test_1(self):
        def a(s):
            return s + "a"

        def b(s):
            return s + "b"

        def c(s):
            return s + "c"

        abc = util.compose(c, b, a)
        s = abc("_")
        self.assertEqual(s, "_abc")


class test_merge(unittest.TestCase):
    def test_merge_value(self):
        d = {"foo": 5, "bar": 10}
        d2 = util.merge(d, {"foo": 0})
        self.assertIsNot(d, d2)
        self.assertEqual(d["foo"], 5)
        self.assertEqual(d2["foo"], 0)
        self.assertEqual(d2["bar"], 10)


class test_get_deep(unittest.TestCase):
    data = {
        "foo": {
            "bar": {
                "baz": 10
            }
        }
    }

    def test_1(self):
        """
        Can get via a string
        """
        v = util.get_deep(self.data, "foo")
        self.assertEqual(type(v), dict)


    def test_2(self):
        """
        Can return a default for properties that don't exist.
        """
        v = util.get_deep(self.data, "kablooey", default=True)
        self.assertEqual(v, True)


    def test_2(self):
        """
        The default default is None
        """
        v = util.get_deep(self.data, "kablooey")
        self.assertIsNone(v)


    def test_4(self):
        """
        Can get deep properties
        """
        v = util.get_deep(self.data, ("foo", "bar", "baz"))
        self.assertEqual(v, 10)


    def test_5(self):
        """
        Can get deep properties using dot-separated strings
        """
        v = util.get_deep(self.data, "foo.bar.baz")
        self.assertEqual(v, 10)



class test_has_key(unittest.TestCase):
    data = {
        "foo": {
            "bar": {
                "baz": 10
            }
        }
    }

    def test_1(self):
        v = util.has_key(self.data, ("foo", "bar", "baz"))
        self.assertEqual(v, True)


class test_contains(unittest.TestCase):
    data = {
        "foo": {
            "bar": {
                "baz": (5, 10, 15, 20)
            }
        }
    }

    def test_1(self):
        v = util.contains(self.data, ("foo", "bar", "baz"), 10)
        self.assertEqual(v, True)


class test_where(unittest.TestCase):
    data = [
        {"section": "foo"},
        {"section": "bar"},
        {"section": "bar"},
        {"section": "foo"},
    ]

    def test_1(self):
        res = util.where(self.data, "section", "foo")
        tuple_res = tuple(res)
        self.assertEqual(len(tuple_res), 2)


class test_where_matches(unittest.TestCase):
    data = [
        {"id_path": "foo/bar/baz/somefile.md"},
        {"id_path": "foo/bar/baz/somefile.txt"},
        {"id_path": "foo/bar/baz/somefile.md"},
        {"id_path": "foo/bling/somefile.txt"},
    ]

    def test_basic_glob(self):
        res = util.where_matches(self.data, "id_path", "*.md")
        tuple_res = tuple(res)
        self.assertEqual(len(tuple_res), 2)
        self.assertEqual(tuple_res[0]["id_path"], "foo/bar/baz/somefile.md")

    def test_prefixed_paths(self):
        res = util.where_matches(self.data, "id_path", "foo/bar/*.txt")
        tuple_res = tuple(res)
        self.assertEqual(len(tuple_res), 1)
        self.assertEqual(tuple_res[0]["id_path"], "foo/bar/baz/somefile.txt")


class test_sort_by_keys(unittest.TestCase):
    data = [
        {"weight": 0, "title": "b", "id": 0},
        {"weight": 1, "title": "b", "id": 1},
        {"weight": 1, "title": "a", "id": 2},
        {"weight": 0, "title": "a", "id": 3},
        {"title": "c"},
    ]

    def test_sort(self):
        res = util.sort_by_keys(self.data, ("weight", "title"), (0, ""))
        self.assertEqual(res[0]["id"], 3)
        self.assertEqual(res[1]["id"], 0)


if __name__ == '__main__':
    unittest.main()