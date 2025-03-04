from unittest import TestCase, TestResult  # noqa: F401  # used for typing


def assertIndepend(self, deco1, deco2):
    self.assertIsNot(deco1, deco2)
    self.assertIsNot(deco1.globals, deco2.globals)
    self.assertIsNot(deco1.kwargs, deco2.kwargs)


def assertCopy(self, deco1, deco2):
    self.assertEqual(deco1.globals, deco2.globals)
    self.assertEqual(deco1.options, deco2.options)
    self.assertEqual(deco1.kwargs, deco2.kwargs)


def assertExtended(self, deco1, deco2, deco3):
    # deco1 + deco2 = deco3
    globals = deco1.globals.copy()
    globals.update(deco2.globals)
    self.assertEqual(globals, deco3.globals)

    self.assertEqual(deco1.options | deco2.options, deco3.options)

    kwargs = deco1.kwargs.copy()
    kwargs.update(deco2.kwargs)
    self.assertEqual(kwargs, deco3.kwargs)


def assertError(self, case, errmsg):  # type: (TestCase, type[TestCase], str) -> None
    result = TestResult()
    case('test_docstring').run(result)
    self.assertIn(errmsg, str(result.errors[0][1]))


def assertFail(self, case):  # type: (TestCase, type[TestCase]) -> None
    result = TestResult()
    case('test_docstring').run(result)
    self.assertIsNot(result, None)
    self.assertFalse(result.wasSuccessful())


def assertPass(self, case):  # type: (TestCase, type[TestCase]) -> None
    result = TestResult()
    case('test_docstring').run(result)
    self.assertIsNot(result, None)
    self.assertTrue(result.wasSuccessful())
