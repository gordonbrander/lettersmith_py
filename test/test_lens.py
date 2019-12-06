import unittest
from experimental.lens2 import key, get, put, over, compose


class TestKey(unittest.TestCase):
    def test_1(self):
        data = {
            "a": 10,
            "b": 11
        }

        a = key("a", 0)
        self.assertEqual(get(a, data), 10, "Getter gets the value at key")

    def test_2(self):
        data = {
            "b": 11
        }

        a = key("a", 0)
        self.assertEqual(
            get(a, data),
            0,
            "Getter gets the default if no value is present"
        )

    def test_3(self):
        data = {
            "b": 11
        }

        a = key("a")
        self.assertEqual(
            get(a, data),
            None,
            "Getter returns None if no default value provided"
        )

    def test_4(self):
        data = {
            "b": 11
        }

        a = key("a", 0)
        data = put(a, data, 10)
        self.assertIsInstance(data, dict, "Update returns container type")
        self.assertEqual(data["a"], 10, "Update sets the value at key")


class TestCompose(unittest.TestCase):
    def test_get(self):
        data = {
            "a": {
                "b": 10
            }
        }

        a = key("a", {})
        b = key("b", 0)
        ab = compose(a, b)
        self.assertEqual(get(ab, data), 10, "Composed getter gets the value")

    def test_deep_get(self):
        data = {
            "a": {
                "b": {
                    "c": {
                        "d": 10
                    }
                }
            }
        }

        abcd = compose(key("a"), key("b"), key("c"), key("d"))
        self.assertEqual(get(abcd, data), 10, "Composed getter gets the value")

    def test_put(self):
        data = {
            "a": {
                "b": 10
            }
        }

        a = key("a", {})
        b = key("b", 0)
        ab = compose(a, b)
        data = put(ab, data, 11)
        self.assertIsInstance(data, dict, "Setter returns container type")
        self.assertEqual(data["a"]["b"], 11, "Setter sets the value at key")

    def test_set_with_defaults(self):
        data = {}

        a = key("a", {})
        b = key("b", 0)
        ab = compose(a, b)
        data = put(ab, data, 11)
        self.assertIsInstance(data, dict, "Setter returns container type")
        self.assertEqual(data["a"]["b"], 11, "Setter sets the value at key")


class TestOver(unittest.TestCase):
    def test_1(self):
        data = {
            "a": 0
        }

        a = key("a")
        x = over(a, lambda a: a + 1, data)
        self.assertEqual(x["a"], 1, "over sets the value using functor")


if __name__ == '__main__':
    unittest.main()