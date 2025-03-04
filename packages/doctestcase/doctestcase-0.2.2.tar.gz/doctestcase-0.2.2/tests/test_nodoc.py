from doctest import ELLIPSIS
from unittest import TestCase

from doctestcase import doctestcase

from tests.util import assertPass


obj1a, obj1b = object(), object()
deco1 = doctestcase(globals=dict(obj1a=obj1a), options=ELLIPSIS, obj1b=obj1b)


class TestEmpty(TestCase):
    def test_missing_docstring(self):
        @deco1
        class Missing(TestCase):
            pass

        assertPass(self, Missing)

    def test_empty_docstring(self):
        @deco1
        class Empty(TestCase):
            """"""

        assertPass(self, Empty)

    def test_blank_docstring(self):
        @deco1
        class Blank(TestCase):
            """\n   \n"""

        assertPass(self, Blank)
