* Decorated `TestCase`
* Reuse `__doctestcase__` from other `TestCase`
* Parametrize test case
* Inherit from decorated `TestCase`
* Format docstring as Markdown or reStructuredText
* Integration with [docsub](https://github.com/makukha/docsub)

See [API Reference](https://doctestcase.readthedocs.io/en/latest/api.html) for details.


### Decorated `TestCase`

<!-- docsub: begin -->
<!-- docsub: include tests/usage/simple.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
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

```
<!-- docsub: end -->

All test methods are called by `unittest` in alphabetic order, including `test_docstring`, added by `@doctestcase`.


### Reuse `__doctestcase__` from other `TestCase`

Extending example above,

<!-- docsub: begin -->
<!-- docsub: include tests/usage/reuse.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
@SimpleCase.__doctestcase__
class AnotherCase(TestCase):
    """
    Title

    >>> X * 100
    'yzyz...'
    """
```
<!-- docsub: end -->

Now `AnotherCase.__doctestcase__` holds shallow copy of `globals`, `kwargs`, and same doctest options, as `SimpleCase`. These copies are independent.


### Inherit from decorated class

Inheriting from another test case decorated with `@doctestcase` allows to reuse and extend `globals` and `kwargs` and override doctest options of the base class.

Extending examples above,

<!-- docsub: begin -->
<!-- docsub: include tests/usage/inherit.py -->
<!-- docsub: lines after 1 upto -1 -->
```python
@doctestcase(globals={'A': 'bc'})
class InheritedCase(SimpleCase):
    """
    Title

    >>> (X + A) * 100
    'yzbcyzbc...'
    """
```
<!-- docsub: end -->

Notice that global variable `A` was added to `globals` defined in `SimpleCase`, and the new class reuses `doctest.ELLIPSIS` option.

For more details on how `doctestcase` properties are updated, check the [API Reference](https://doctestcase.readthedocs.io/en/latest/api.html).


### Parametrize doctest case

First, define base class parametrized with `cwd`:

<!-- docsub: begin -->
<!-- docsub: include tests/usage/param-base.py -->
<!-- docsub: lines after 1 upto -1 -->
````python
from doctest import ELLIPSIS
import os.path
import shutil
import tempfile
from unittest import TestCase

from doctestcase import doctestcase


@doctestcase(options=ELLIPSIS, cwd='.')
class ChdirTestCase(TestCase):
    def setUp(self):
        if self.__class__ is ChdirTestCase:
            self.skipTest('base class')  # no tests of the base class itself
        self.temp = tempfile.mkdtemp()
        self.prev = os.getcwd()
        cwd = os.path.join(self.temp, self.__doctestcase__.kwargs['cwd'])
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        os.chdir(cwd)

    def tearDown(self):
        os.chdir(self.prev)
        shutil.rmtree(self.temp)
````
<!-- docsub: end -->

Notice how the base class is skipped from testing.

In this example we use `os.path` module for compatibility with older Python versions only. If you use recent Python versions, use `pathlib` instead.

Now we can define test case parametrized with `cwd`:

<!-- docsub: begin -->
<!-- docsub: include tests/usage/param-child.py -->
<!-- docsub: lines after 1 upto -1 -->
````python
@doctestcase(cwd='subdir')
class Case1(ChdirTestCase):
    """
    >>> import os
    >>> os.getcwd()
    '.../subdir'
    """
````
<!-- docsub: end -->


### Inherit from decorated `TestCase`

Test cases, decorated with `@doctestcase`, can be used as base classes for other test cases. This is useful when inherited classes need to extend or change properties, passed to parent's `@doctestcase`. Parent properties will be copied and updated with values from child class decorator.

For the `SimpleCase` class above,

<!-- docsub: begin -->
<!-- docsub: include tests/usage/inherit.py -->
<!-- docsub: lines after 1 upto -1 -->
````python
@doctestcase(globals={'A': 'bc'})
class InheritedCase(SimpleCase):
    """
    Title

    >>> (X + A) * 100
    'yzbcyzbc...'
    """
````
<!-- docsub: end -->


### Format docstring as Markdown or reStructuredText

For the `SimpleCase` class above,

#### Markdown

```pycon
>>> from doctestcase import to_markdown
>>> to_markdown(SimpleCase)
```
<!-- docsub: begin -->
<!-- docsub: include tests/usage/simple.md -->
<!-- docsub: lines after 1 upto -1 -->
````markdown
## Title

Paragraph.

```pycon
>>> X * 100
'yzyz...'
```

Another paragraph.

```pycon
>>> None
>>> True
True
```
````
<!-- docsub: end -->

#### reStructuredText

```pycon
>>> from doctestcase import to_rest
>>> to_rest(SimpleCase)
```
<!-- docsub: begin -->
<!-- docsub: include tests/usage/simple.rst -->
<!-- docsub: lines after 1 upto -1 -->
````restructuredtext
Title
-----

Paragraph.

>>> X * 100
'yzyz...'

Another paragraph.

>>> None
>>> True
True
````
<!-- docsub: end -->


### Integration with [docsub](https://github.com/makukha/docsub)

When documenting packages, "Usage" section often includes doctests. It is a good practice to test all documented use cases, so why not adopt test-driven documenting approach and write tests with docs in mind?

1. Write tests with carefully crafted docstrings using doctests.
2. Include generated Markdown or reST in docs.

With [docsub](https://github.com/makukha/docsub), this can be achieved with some minimal configuration.

Just two commands to run tests and update docs:

```shell
$ pytest tests
$ docsub sync -i usage.md
```

#### usage.md

<!-- docsub: begin #usage.md -->
<!-- docsub: include tests/docsub/__result__.md -->
<!-- docsub: lines after 1 upto -1 -->
````markdown
# Usage

<!-- docsub: begin -->
<!-- docsub: x case tests/test_usage.py:UseCase1 -->
## Use Case 1

Long description of the use case.

Usage example in doctest:

```pycon
>>> True
True
```
<!-- docsub: end -->
````
<!-- docsub: end #usage.md -->

#### tests/test_usage.py

<!-- docsub: begin -->
<!-- docsub: include tests/docsub/tests/test_usage.py -->
<!-- docsub: lines after 1 upto -1 -->
````python
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
````
<!-- docsub: end -->

#### docsubfile.py

Docsub configuration file declaring project-local x-tension command:

<!-- docsub: begin -->
<!-- docsub: include tests/docsub/docsubfile.py -->
<!-- docsub: lines after 1 upto -1 -->
````python
from docsub import click
from doctestcase import to_markdown
from importloc import Location


@click.group()
def x() -> None:
    pass


@x.command()
@click.argument('case')
def case(case: str) -> None:
    text = to_markdown(Location(case).load(), title_depth=2)
    click.echo(text, nl=False)
````
<!-- docsub: end -->
