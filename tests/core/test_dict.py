import unittest
from Javatar.core.dict import JavatarDict


class TestJavatarDict(unittest.TestCase):
    def test_empty_dict(self):
        dict = JavatarDict()
        self.assertEqual(dict.has("alpha"), False)
        self.assertEqual(dict.get("alpha"), None)
        self.assertEqual(dict.get("alpha", default=True), True)
        self.assertEqual(dict.get("alpha", default=1), 1)

    def test_predefined_dict(self):
        global_dict = {
            "alpha": "bravo"
        }
        local_dict = {
            "alpha": "charlie"
        }
        dict = JavatarDict(global_dict=global_dict, local_dict=local_dict)
        self.assertEqual(dict.get("alpha"), "charlie")
        self.assertEqual(dict.get("alpha", default=False), "charlie")

    def test_set_dict(self):
        dict = JavatarDict()
        dict.set("alpha", "bravo")
        self.assertEqual(dict.get("alpha"), "bravo")
        dict.set("alpha", "charlie")
        self.assertEqual(dict.get("alpha"), "charlie")
        dict.set("alpha", "delta", to_global=True)
        self.assertEqual(dict.get("alpha"), "charlie")
        dict.set("alpha", "echo", to_global=False)
        self.assertEqual(dict.get("alpha"), "echo")
        self.assertEqual(dict.get("alpha", default=False), "echo")
        self.assertEqual(dict.get_local_dict(), {
            "alpha": "echo"
        })
        self.assertEqual(dict.get_global_dict(), {
            "alpha": "delta"
        })
        self.assertEqual(dict.get_dict(), {
            "alpha": "echo"
        })

    def test_global_dict(self):
        global_dict = {
            "alpha": "bravo",
            "charlie": "delta"
        }
        dict = JavatarDict(global_dict=global_dict)
        self.assertEqual(dict.get("echo"), None)
        self.assertEqual(dict.get("charlie"), "delta")
        self.assertEqual(dict.get_dict(), {
            "alpha": "bravo",
            "charlie": "delta"
        })

    def test_local_dict(self):
        local_dict = {
            "echo": "foxtrot",
            "charlie": "golf"
        }
        dict = JavatarDict(local_dict=local_dict)
        self.assertEqual(dict.get("echo"), "foxtrot")
        self.assertEqual(dict.get("charlie"), "golf")
        self.assertEqual(dict.get_dict(), {
            "echo": "foxtrot",
            "charlie": "golf"
        })

    def test_merged_dict(self):
        global_dict = {
            "alpha": "bravo",
            "charlie": "delta"
        }
        local_dict = {
            "echo": "foxtrot",
            "charlie": "golf"
        }
        dict = JavatarDict(global_dict=global_dict, local_dict=local_dict)
        self.assertEqual(dict.get("echo"), "foxtrot")
        self.assertEqual(dict.get("charlie"), "golf")
        self.assertEqual(dict.get_dict(), {
            "alpha": "bravo",
            "charlie": "golf",
            "echo": "foxtrot"
        })
