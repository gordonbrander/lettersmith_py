"""
Unit tests for html
"""
import unittest
from lettersmith import html


class test_strip_html(unittest.TestCase):
    def test_1(self):
        text = """<p><a href='http://example.com'>foo</a></p>"""
        s = html.strip_html(text)
        self.assertEqual(s, 'foo')

    def test_2(self):
        text = """<H1>foo</H1>"""
        s = html.strip_html(text)
        self.assertEqual(s, 'foo')

    def test_3(self):
        text = """<img src="...">"""
        s = html.strip_html(text)
        self.assertEqual(s, '')

    def test_4(self):
        text = """<img src="..." />"""
        s = html.strip_html(text)
        self.assertEqual(s, '')