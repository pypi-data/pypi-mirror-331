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
