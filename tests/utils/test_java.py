import shutil
from os.path import join
import unittest
from unittest.mock import patch
import tempfile

from Javatar.utils.javatar_java import is_jdk_dir

create_file = lambda filename: open(filename, 'w').write('')


class TestJava(unittest.TestCase):
    @patch('Javatar.utils.javatar_java.get_settings',
           return_value={'run': 'java', 'compile': 'javac'})
    def test_is_jdk_dir(self, get_settings):
        direct = tempfile.mkdtemp()

        self.assertFalse(is_jdk_dir(direct))

        create_file(join(direct, 'java'))
        self.assertFalse(is_jdk_dir(direct))

        create_file(join(direct, 'javac'))
        self.assertTrue(is_jdk_dir(direct))

        shutil.rmtree(direct)
