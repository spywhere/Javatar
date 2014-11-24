import unittest
from javatar.utils.javatar_utils import JavatarMergedDict as MergedDict


class TestMergedDict(unittest.TestCase):
    def test_basics(self):
        d = MergedDict(None, None)

        self.assertEquals(
            d.get_dict(),
            None
        )

        d.set('hello', 'world')
        self.assertEqual(
            d.get_dict(),
            {'hello': 'world'}
        )

    def test_override(self):
        d = MergedDict(
            local_dict={'hello': 'more important'},
            global_dict={'hello': 'less important'}
        )

        self.assertEqual(d.get('hello'), 'more important')
