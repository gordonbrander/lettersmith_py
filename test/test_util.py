import unittest
from lettersmith import util


class test_put(unittest.TestCase):
    def test_put(self):
        d = {"foo": 5, "bar": 10}
        d2 = util.put(d, "foo", 0)
        self.assertIsNot(d, d2)
        self.assertEqual(d["foo"], 5)
        self.assertEqual(d2["foo"], 0)
        self.assertEqual(d2["bar"], 10)


class test_merge(unittest.TestCase):
    def test_merge_value(self):
        d = {"foo": 5, "bar": 10}
        d2 = util.merge(d, {"foo": 0})
        self.assertIsNot(d, d2)
        self.assertEqual(d["foo"], 5)
        self.assertEqual(d2["foo"], 0)
        self.assertEqual(d2["bar"], 10)


class test_unset(unittest.TestCase):
    def test_delete(self):
        d = {"foo": 5, "bar": 10, "baz": 20}
        d2 = util.unset(d, ("foo", "bar"))
        self.assertRaises(KeyError, lambda: d2["foo"])
        self.assertRaises(KeyError, lambda: d2["bar"])
        self.assertEqual(d2["baz"], 20)


class test_get(unittest.TestCase):
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
        v = util.get(self.data, "foo")
        self.assertEqual(type(v), dict)


    def test_2(self):
        """
        Can return a default for properties that don't exist.
        """
        v = util.get(self.data, "kablooey", default=True)
        self.assertEqual(v, True)


    def test_2(self):
        """
        The default default is None
        """
        v = util.get(self.data, "kablooey")
        self.assertIsNone(v)


    def test_4(self):
        """
        Can get deep properties
        """
        v = util.get(self.data, ("foo", "bar", "baz"))
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
        {"simple_path": "foo/bar/baz/somefile.md"},
        {"simple_path": "foo/bar/baz/somefile.txt"},
        {"simple_path": "foo/bar/baz/somefile.md"},
        {"simple_path": "foo/bling/somefile.txt"},
    ]

    def test_basic_glob(self):
        res = util.where_matches(self.data, "simple_path", "*.md")
        tuple_res = tuple(res)
        self.assertEqual(len(tuple_res), 2)
        self.assertEqual(tuple_res[0]["simple_path"], "foo/bar/baz/somefile.md")

    def test_prefixed_paths(self):
        res = util.where_matches(self.data, "simple_path", "foo/bar/*.txt")
        tuple_res = tuple(res)
        self.assertEqual(len(tuple_res), 1)
        self.assertEqual(tuple_res[0]["simple_path"], "foo/bar/baz/somefile.txt")


if __name__ == '__main__':
    unittest.main()