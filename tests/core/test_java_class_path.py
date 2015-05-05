import unittest
from Javatar.core.java_utils import JavaClass, JavaPackage, JavaClassPath


class TestJavaClassPath(unittest.TestCase):
    def test_java_class(self):
        self.assertEqual(JavaClass().get(), "")
        self.assertEqual(JavaClass().is_empty(), True)
        self.assertEqual(JavaClass("").get(), "")
        self.assertEqual(JavaClass("").is_empty(), True)
        self.assertEqual(JavaClass("Alpha").get(), "Alpha")
        self.assertEqual(JavaClass("Alpha").is_empty(), False)

    def test_java_package(self):
        self.assertEqual(JavaPackage().as_class_path(), "")
        self.assertEqual(JavaPackage("").as_class_path(), "")
        self.assertEqual(JavaPackage("alpha.").as_class_path(), "")
        self.assertEqual(JavaPackage(".alpha.bravo").as_class_path(), "")
        self.assertEqual(JavaPackage(".alpha.bravo.").as_class_path(), "")
        self.assertEqual(JavaPackage("alpha.").as_path(), "")
        self.assertEqual(JavaPackage([]).is_empty(), True)
        self.assertEqual(JavaPackage([None]).is_empty(), True)
        self.assertEqual(JavaPackage(()).is_empty(), True)
        self.assertEqual(JavaPackage((None)).is_empty(), True)
        self.assertEqual(JavaPackage("alpha.").is_empty(), True)
        self.assertEqual(JavaPackage("alpha").is_empty(), False)
        self.assertEqual(
            JavaPackage("alpha.bravo").as_class_path(),
            "alpha.bravo"
        )
        self.assertEqual(
            JavaPackage("alpha.bravo").as_path(),
            "alpha/bravo"
        )
        self.assertEqual(
            JavaPackage(["alpha", "bravo"]).as_class_path(),
            "alpha.bravo"
        )
        self.assertEqual(
            JavaPackage(("alpha", "bravo")).as_class_path(),
            "alpha.bravo"
        )
        self.assertEqual(
            JavaPackage(["alpha", None, "bravo"]).as_class_path(),
            "alpha.bravo"
        )
        self.assertEqual(
            JavaPackage(("alpha", None, "bravo")).as_class_path(),
            "alpha.bravo"
        )

    def test_invalid_class_path(self):
        tests = [
            ".alpha", "alpha.", ".alpha.bravo", "alpha.bravo.", "alpha:,",
            "alpha<,", "alpha:,<,", "alpha<,:,", "alpha:", "alpha<", "alpha:<",
            "alpha<:", "alpha:bravo,", "alpha<bravo,", "alpha<bravo,:charlie",
            "alpha:bravo,:charlie", "alpha:bravo<charlie,",
            "alpha<bravo:charlie,", "alpha:bravo", "alpha:bravo<charlue",
            "alpha<bravo:charlie", "alpha:bravo,charlie", "alpha<bravo,charlie",
            "alpha:bravo,charlie<delta", "alpha<bravo,charlie:delta",
            "alpha:bravo,charlie<delta,echo", "alpha<bravo,charlie:delta,echo"
        ]

        for test in tests:
            self.assertEqual(JavaClassPath(test).as_class_path(), "")

    def test_valid_class_path(self):
        tests = [
            {
                "input": "Alpha",
                "expected": {
                    "class_path": "Alpha",
                    "package": "",
                    "class": "Alpha"
                }
            }, {
                "input": "alpha.Bravo",
                "expected": {
                    "class_path": "alpha.Bravo",
                    "package": "alpha",
                    "class": "Bravo"
                }
            }, {
                "input": "alpha.bravo.Charlie",
                "expected": {
                    "class_path": "alpha.bravo.Charlie",
                    "package": "alpha.bravo",
                    "class": "Charlie"
                }
            }
        ]

        for test in tests:
            class_path = JavaClassPath(test["input"])
            expected = test["expected"]
            self.assertEqual(
                class_path.as_class_path(),
                expected["class_path"]
            )
            self.assertEqual(
                class_path.get_package().as_class_path(),
                expected["package"]
            )
            self.assertEqual(
                class_path.get_class().get(),
                expected["class"]
            )
