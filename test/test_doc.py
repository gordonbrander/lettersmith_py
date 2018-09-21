"""
Unit tests for Doc
"""

import unittest
from pathlib import Path
from lettersmith import doc as Doc

module_path = Path(__file__).parent
fixtures_path = Path(module_path, "package_data", "fixtures")

class test_load_bare_doc(unittest.TestCase):
    def setUp(self):
        doc_path = fixtures_path.joinpath("Bare doc.md")
        doc = Doc.load(doc_path, relative_to=fixtures_path)
        self.doc = doc

    def test_content(self):
        self.assertEqual(self.doc.content, "Lorem ipsum")

    def test_meta(self):
        """
        Meta should always be a dict
        """
        self.assertIsInstance(self.doc.meta, dict)

    def test_id_path(self):
        self.assertEqual(str(self.doc.id_path), "Bare doc.md")


class test_parse_frontmatter(unittest.TestCase):
    def setUp(self):
        doc_path = fixtures_path.joinpath("Doc with meta.md")
        doc = Doc.load(doc_path, relative_to=fixtures_path)
        doc = Doc.parse_frontmatter(doc)
        self.doc = doc

    def test_content(self):
        self.assertEqual(self.doc.content, "Lorem ipsum")

    def test_meta(self):
        """
        Meta should always be a dict
        """
        self.assertIsInstance(self.doc.meta, dict)

    def test_items(self):
        self.assertEqual(self.doc.meta["title"], "Doc title")


class test_parse_yaml(unittest.TestCase):
    def setUp(self):
        doc_path = fixtures_path.joinpath("doc.yaml")
        doc = Doc.load(doc_path, relative_to=fixtures_path)
        doc = Doc.parse_yaml(doc)
        self.doc = doc

    def test_content(self):
        self.assertEqual(self.doc.content, "")

    def test_meta(self):
        """
        Meta should always be a dict
        """
        self.assertIsInstance(self.doc.meta, dict)

    def test_items(self):
        self.assertEqual(self.doc.meta["title"], "Doc title")


class test_parse_json(unittest.TestCase):
    def setUp(self):
        doc_path = fixtures_path.joinpath("doc.json")
        doc = Doc.load(doc_path, relative_to=fixtures_path)
        doc = Doc.parse_json(doc)
        self.doc = doc

    def test_content(self):
        self.assertEqual(self.doc.content, "")

    def test_meta(self):
        """
        Meta should always be a dict
        """
        self.assertIsInstance(self.doc.meta, dict)

    def test_items(self):
        self.assertEqual(self.doc.meta["title"], "Doc title")


class test_ext(unittest.TestCase):
    def test_1(self):
        doc_1 = Doc.doc(
            id_path="fake_1.md",
            output_path="fake_1.html"
        )
        doc_2 = Doc.doc(
            id_path="fake_2.markdown",
            output_path="fake_1.html"
        )
        doc_3 = Doc.doc(
            id_path="fake_1.json",
            output_path="fake_1.html"
        )

        is_md = Doc.ext(".md", ".mdown", ".markdown")

        self.assertTrue(is_md(doc_1), "Matches by extension")
        self.assertTrue(is_md(doc_2), "Matches by extension")
        self.assertFalse(
            is_md(doc_3),
            "Does not return true for extensions that don't match."
        )


if __name__ == '__main__':
    unittest.main()