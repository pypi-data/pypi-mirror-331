import os
from subprocess import check_output
import sys
from unittest import TestCase, skipUnless


@skipUnless(sys.version_info >= (3, 9), 'Python 3.9 or higher')
class DocsubTest(TestCase):
    maxDiff = None

    def setUp(self):
        self.prev = os.getcwd()
        os.chdir('tests/docsub')

    def tearDown(self):
        os.chdir(self.prev)

    def test_docsub(self):
        with open('__result__.md') as f:
            expected = f.read()
        result = check_output(
            [sys.executable, '-m', 'docsub', 'sync', '__input__.md'],
            text=True,
        )
        self.assertEqual(expected, result)
