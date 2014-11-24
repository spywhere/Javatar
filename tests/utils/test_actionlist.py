import unittest

from javatar.utils.javatar_actions import ActionList


class TestActionList(unittest.TestCase):
    def test_get_action(self):
        al = ActionList()

        al.actions = [
            ('utils', 'Include'),
            ('commands', 'Exclude')
        ]

        self.assertEqual(
            ['Include'],
            al.get_action(
                include=['utils'],
                exclude=['commands']
            )
        )
