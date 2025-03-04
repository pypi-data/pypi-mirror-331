from unittest import TestCase

from doctestcase import doctestcase


@doctestcase()
class UseCase1(TestCase):
    """
    Use Case 1

    Long description of the use case.

    Usage example in doctest:

    >>> True
    True
    """
