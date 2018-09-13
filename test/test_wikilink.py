import unittest
from lettersmith.doc import doc
from lettersmith import wikilink


class test_strip_doc_wikilinks(unittest.TestCase):
    def test_strip(self):
        d = doc(
            id_path="foo/bar.md",
            output_path="foo/bar.html",
            content="Foo [[bar]] baz bing."
        )
        d2 = wikilink.strip_doc_wikilinks(d)
        self.assertEqual(d2.content, "Foo bar baz bing.")


if __name__ == '__main__':
    unittest.main()