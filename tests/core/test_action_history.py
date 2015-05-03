import unittest
from unittest.mock import patch
from Javatar.core.action_history import _ActionHistory


class TestActionHistory(unittest.TestCase):
    @patch(
        "Javatar.core.settings._Settings.ready",
        return_value=False
    )
    def test_add_action(self, ready):
        ah = _ActionHistory()
        self.assertEqual(ah.actions, [])
        ah.add_action("alpha", "beta")
        self.assertEqual(ah.actions, [("alpha", "beta")])

    def test_get_action(self):
        ah = _ActionHistory()
        ah.actions = (
            ("utils", "Utils"),
            ("utils.run", "Utils Run"),
            ("commands", "Commands"),
            ("commands.run", "Commands Run")
        )

        self.assertEqual(
            ["Utils", "Utils Run"],
            ah.get_action(
                include=["utils"]
            )
        )

        self.assertEqual(
            ["Commands", "Commands Run"],
            ah.get_action(
                exclude=["utils"]
            )
        )

        self.assertEqual(
            ["Utils", "Utils Run"],
            ah.get_action(
                include=["utils"],
                exclude=["commands"]
            )
        )

        self.assertEqual(
            [],
            ah.get_action(
                include=["utils", "commands"],
                exclude=["utils", "commands"]
            )
        )
