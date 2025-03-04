from doctest import ELLIPSIS, REPORT_UDIFF
from unittest import TestCase

from doctestcase import doctestcase

from tests.util import (
    assertCopy,
    assertError,
    assertExtended,
    assertIndepend,
    assertPass,
)


obj1a, obj1b = object(), object()
deco1 = doctestcase(globals=dict(obj1a=obj1a), options=ELLIPSIS, obj1b=obj1b)

obj2a, obj2b = object(), object()
deco2 = doctestcase(globals=dict(obj2a=obj2a), options=REPORT_UDIFF, obj2b=obj2b)


# tests


class TestReusability(TestCase):
    def test_decoration(self):
        @deco1
        class Decorated(TestCase):
            """>>> True\nTrue\n"""

        assertIndepend(self, deco1, Decorated.__doctestcase__)  # type: ignore
        assertCopy(self, deco1, Decorated.__doctestcase__)  # type: ignore
        assertPass(self, Decorated)

    def test_double_decoration(self):
        @deco2
        @deco1
        class Decorated(TestCase):  # type: ignore  # double decoration breaks typing
            """>>> True\nTrue\n"""

        assertIndepend(self, deco1, Decorated.__doctestcase__)  # type: ignore
        assertIndepend(self, deco2, Decorated.__doctestcase__)  # type: ignore
        assertExtended(self, deco1, deco2, Decorated.__doctestcase__)  # type: ignore
        assertPass(self, Decorated)

    # blank docstring

    def test_missing_docstring(self):
        @deco1
        class Decorated(TestCase):
            pass

        assertPass(self, Decorated)

    def test_empty_docstring(self):
        @deco1
        class Decorated(TestCase):
            pass

        assertPass(self, Decorated)

    def test_blank_docstring(self):
        @deco1
        class Decorated(TestCase):
            pass

        assertPass(self, Decorated)

    # reuse

    def test_reuse_on_new(self):
        @deco1
        class Old(TestCase):
            """>>> True\nTrue\n"""

        @Old.__doctestcase__  # type: ignore
        class New(TestCase):
            """>>> True\nTrue\n"""

        assertIndepend(self, Old.__doctestcase__, New.__doctestcase__)  # type: ignore
        assertCopy(self, Old.__doctestcase__, New.__doctestcase__)  # type: ignore
        assertPass(self, Old)
        assertPass(self, New)

    # inherit

    def test_undecorated_inheritance(self):
        @deco1
        class Base(TestCase):
            """>>> True\nTrue\n"""

        class Child(Base):
            """>>> True\nTrue\n"""

        assertPass(self, Base)
        errmsg = r'Class Child, inherited from Base, must be decorated'
        assertError(self, Child, errmsg)

    def test_unaltered_inheritance(self):
        @deco1
        class Base(TestCase):
            """>>> True\nTrue\n"""

        @doctestcase()
        class Child(Base):
            """>>> True\nTrue\n"""

        assertIndepend(self, Base.__doctestcase__, Child.__doctestcase__)  # type: ignore
        assertCopy(self, Base.__doctestcase__, Child.__doctestcase__)  # type: ignore
        assertPass(self, Base)
        assertPass(self, Child)

    def test_altered_inheritance(self):
        @deco1
        class Base(TestCase):
            """>>> True\nTrue\n"""

        @deco2
        class Child(Base):
            """>>> True\nTrue\n"""

        assertExtended(self, Base.__doctestcase__, deco2, Child.__doctestcase__)  # type: ignore
        assertPass(self, Base)
        assertPass(self, Child)

    def test_inheritance_with_reuse(self):
        @deco1
        class Base1(TestCase):
            """>>> True\nTrue\n"""

        @deco2
        class Base2(TestCase):
            """>>> True\nTrue\n"""

        @Base1.__doctestcase__  # type: ignore
        class Child(Base2):
            """>>> True\nTrue\n"""

        assertIndepend(self, Base1.__doctestcase__, Child.__doctestcase__)  # type: ignore
        assertIndepend(self, Base2.__doctestcase__, Child.__doctestcase__)  # type: ignore
        assertExtended(
            self,
            Base2.__doctestcase__,  # type: ignore
            Base1.__doctestcase__,  # type: ignore
            Child.__doctestcase__,  # type: ignore
        )
        assertPass(self, Base1)
        assertPass(self, Base2)
        assertPass(self, Child)
