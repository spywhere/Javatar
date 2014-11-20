import unittest


class TestValidator(unittest.TestCase):
    def test_is_package(self):
        from javatar.utils.javatar_validator import is_package

        self.assertTrue(
            is_package('hello.world')
        )
