import unittest
from unittest.mock import patch

from javatar.utils.javatar_collections import JavatarSnippetsLoaderThread

SAMPLE_SNIPPET = '''\
%class:Class%
%description:Create a new empty class%
%package%

%visibility%%modifier%class %class%%inheritance% {
    %body%
}
'''


class TestSnippetsLoaderThread(unittest.TestCase):
    @patch('sublime.load_resource', return_value=SAMPLE_SNIPPET)
    def test_analyse_snippet(self, load_resource):
        inst = JavatarSnippetsLoaderThread()

        self.assertEqual(
            {
                'file': 'hello/world.txt',
                'class': 'Class',
                'description': 'Create a new empty class',
                'data': (
                    '%package%\n'
                    '\n'
                    '%visibility%%modifier%class %class%%inheritance% {\n'
                    '    %body%\n'
                    '}\n'
                )
            },
            inst.analyse_snippet('hello/world.txt')
        )

    def test_analyse_package(self):
        ...
