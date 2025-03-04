from typing import Any, ClassVar, Optional, Type, TypeVar, Union
from unittest import TestCase

T = TypeVar('T', bound=Type[TestCase])

class DocTestCase(TestCase):
    __doctestcase__: ClassVar['doctestcase']
    def test_docstring(self) -> None: ...

class doctestcase:
    bind: Optional[TestCase]
    globals: dict[str, Any]
    options: int
    kwargs: dict[str, Any]
    def __init__(
        self,
        globals: dict[str, Any] = ...,
        options: int = ...,
        **kwargs: Any,
    ) -> None: ...
    def __call__(self: Union[T, type[T]], cls: T) -> Union[T, DocTestCase]: ...
    def _assign(self, cls: TestCase) -> None: ...
    def _copy(self) -> 'doctestcase': ...
    def _update(self, other: 'doctestcase') -> None: ...

def test_docstring(self: TestCase) -> None: ...
