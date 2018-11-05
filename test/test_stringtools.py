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


class test_truncate(unittest.TestCase):
    def test_text(self):
        s = """
Shall I compare thee to a summer’s day?
Thou art more lovely and more temperate.
Rough winds do shake the darling buds of May,
And summer’s lease hath all too short a date.
Sometime too hot the eye of heaven shines,
And often is his gold complexion dimmed;
And every fair from fair sometime declines,
By chance, or nature’s changing course, untrimmed;
But thy eternal summer shall not fade,
Nor lose possession of that fair thou ow’st,
Nor shall death brag thou wand’rest in his shade,
When in eternal lines to Time thou grow’st.
So long as men can breathe, or eyes can see,
So long lives this, and this gives life to thee.
        """
        truncated = stringtools.truncate(s, max_len=50)
        self.assertEqual(
            truncated,
            "Shall I compare thee to a summer’s day? Thou art..."
        )

    def test_html(self):
        s = """
<p>
<i>Shall I compare thee to a summer’s day?</i><br>
Thou art more lovely and more temperate.<br>
Rough winds do shake the darling buds of May,<br>
And summer’s lease hath all too short a date.<br>
Sometime too hot the eye of heaven shines,<br>
And often is his gold complexion dimmed;<br>
And every fair from fair sometime declines,<br>
By chance, or nature’s changing course, untrimmed;<br>
But thy eternal summer shall not fade,<br>
Nor lose possession of that fair thou ow’st,<br>
Nor shall death brag thou wand’rest in his shade,<br>
When in eternal lines to Time thou grow’st.<br>
So long as men can breathe, or eyes can see,<br>
So long lives this, and this gives life to thee.
</p>
        """
        truncated = stringtools.truncate(s, max_len=50)
        self.assertEqual(
            truncated,
            "Shall I compare thee to a summer’s day? Thou art..."
        )

if __name__ == '__main__':
    unittest.main()