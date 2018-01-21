"""
Unit tests for stringtools
"""

import unittest
from lettersmith import stringtools


class test_strip_html(unittest.TestCase):
    def test_1(self):
        html = """<p><a href='http://example.com'>foo</a></p>"""
        s = stringtools.strip_html(html)
        self.assertEqual(s, 'foo')

    def test_2(self):
        html = """<H1>foo</H1>"""
        s = stringtools.strip_html(html)
        self.assertEqual(s, 'foo')

    def test_3(self):
        html = """<img src="...">"""
        s = stringtools.strip_html(html)
        self.assertEqual(s, '')

    def test_4(self):
        html = """<img src="..." />"""
        s = stringtools.strip_html(html)
        self.assertEqual(s, '')

if __name__ == '__main__':
    unittest.main()