import doctest
from unittest import TestCase

from doctestcase import doctestcase

from tests.util import assertFail, assertPass


class DefaultOptions(TestCase):
    def test_ellipsis_off_by_default(self):
        @doctestcase()
        class Default(TestCase):
            """
            >>> 111
            1...
            """

        assertFail(self, Default)

    def test_ellipsis_turned_on(self):
        @doctestcase(options=doctest.ELLIPSIS)
        class WithEllipsis(TestCase):
            """
            >>> 111
            1...
            """

        assertPass(self, WithEllipsis)
