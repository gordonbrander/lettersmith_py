"""
Unit tests for stringtools
"""

import unittest
from lettersmith import stringtools


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


if __name__ == '__main__':
    unittest.main()