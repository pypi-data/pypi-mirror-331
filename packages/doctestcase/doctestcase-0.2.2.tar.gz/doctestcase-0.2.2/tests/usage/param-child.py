@doctestcase(cwd='subdir')
class Case1(ChdirTestCase):
    """
    >>> import os
    >>> os.getcwd()
    '.../subdir'
    """
