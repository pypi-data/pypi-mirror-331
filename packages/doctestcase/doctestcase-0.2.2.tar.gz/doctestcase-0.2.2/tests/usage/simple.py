from doctest import ELLIPSIS
from unittest import TestCase

from doctestcase import doctestcase


@doctestcase(globals={'X': 'yz'}, options=ELLIPSIS)
class SimpleCase(TestCase):
    """
    Title

    Paragraph.

    >>> X * 100
    'yzyz...'

    Another paragraph.

    >>> None
    >>> True
    True
    """

    def test_custom(self):  # called before 'test_docstring'
        self.assertTrue(True)

    def test_other(self):  # called after 'test_docstring'
        self.assertTrue(True)

