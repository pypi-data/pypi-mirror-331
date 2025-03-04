from doctest import DocTestFinder, DocTestRunner


class doctestcase:
    """
    Class decorator that turns on evaluation of docstring doctests in subclasses of
    `unittest.TestCase`.

    Args:

        globals (``dict`` | ``None``, optional):
            dictionary of globals passed to the doctest; defaults to ``None``
            (no additional globals).

        options (``int``, optional):
            `doctest` options, passed to `doctest.DocTestRunner`; defaults to
            ``0`` (no options).

        kwargs (``dict``, optional):
            additional keyword arguments that will be stored under
            ``__doctestcase__.kwargs`` and can be used in
            :py:meth:`~unittest.TestCase.setUp`, :py:meth:`~unittest.TestCase.tearDown`,
            and custom test methods of `~unittest.TestCase`.

    Attributes:

        globals (``dict``):
            ``gobals`` passed to decorator.

        options (``int``):
            ``options`` passed to decorator.

        kwargs (``dict``):
            ``**kwargs`` passed to decorator.

    The decorator object, after being applied to the decorated class, stores its copy
    under attribute ``__doctestcase__``, including `options` and shallow copies of
    original `globals` and `kwargs`.

    New test method ``test_docstring``, implementing
    docstring evaluation, is added to the decorated class.
    If the decorated class has no docstring or the docstring is blank,
    ``test_docstring`` does nothing.

    The decorated class, as a subclass of `unittest.TestCase`, can define
    :py:meth:`~unittest.TestCase.setUp`, `~unittest.TestCase.tearDown`,
    and its own test methods (exept ``test_docstring``) that are executed
    before or after the docstring.

    If decorated class already has ``__doctestcase__`` attribute (obtained from
    decoration or inherited from parent classes), it is replaced with a copy;
    `globals` and `kwargs` are updated with values from the decorator,
    and `options` is OR'ed with decorator's `options`.
    This allows to extend test cases with multiple decoration and inheritance.
    This also ensures that ``__doctestcase__`` attributes of subsequent classes are
    independent, but *values* of `globals` and `kwargs` dictionaries reference the
    same objects.

    The `doctestcase` object, after being applied to `~unittest.TestCase` class,
    can be further reused to decorate other `~unittest.TestCase` classes. The same
    is true for ``__doctestcase__`` attribute.

    When `~unittest.TestCase` is inherited, the inherited class must be decorated
    with `doctestcase` again.

    Example:

        .. code:: python

            from doctest import ELLIPSIS
            from unittest import TestCase

            from doctestcase import doctestcase


            @doctestcase(globals={'X': 'yz'}, options=ELLIPSIS)
            class SimpleCase(TestCase):
                \"\"\"
                Title

                Paragraph.

                >>> X * 100
                'yzyz...'

                Another paragraph.

                >>> None
                >>> True
                True
                \"\"\"

    See Also:
         :ref:`usage` documentation section  contains more examples and use cases.
    """

    def __init__(self, globals=None, options=0, **kwargs):
        self.globals = globals or {}
        self.options = options
        self.kwargs = kwargs
        self.bind = None

    def __call__(self, cls):
        if not hasattr(cls, '__doctestcase__'):
            self._assign(cls)
        elif cls.__doctestcase__.bind is not cls:
            updated = cls.__doctestcase__._copy()
            updated._update(self)
            updated._assign(cls)
        else:
            cls.__doctestcase__._update(self)
        return cls

    def _assign(self, cls):
        cls.__doctestcase__ = self._copy()
        cls.__doctestcase__.bind = cls
        cls.test_docstring = test_docstring

    def _copy(self):
        return doctestcase(
            globals=self.globals.copy(), options=self.options, **self.kwargs
        )

    def _update(self, other):
        self.globals.update(other.globals)
        self.options |= other.options
        self.kwargs.update(other.kwargs)


def test_docstring(self):
    if self.__doctestcase__.bind is not self.__class__:
        errmsg = 'Class {}, inherited from {}, must be decorated'.format(
            self.__class__.__name__,
            self.__doctestcase__.bind.__name__,
        )
        raise ValueError(errmsg)

    props = self.__doctestcase__
    finder = DocTestFinder(recurse=False)
    runner = DocTestRunner(optionflags=props.options)
    if getattr(self, '__doc__', ''):
        name = self.__class__.__name__
        for test in finder.find(self.__doc__, name, globs=props.globals):
            ret = runner.run(test)
            self.assertFalse(ret.failed)
