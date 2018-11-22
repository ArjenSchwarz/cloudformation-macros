import unittest
import macro

class TestStringMethods(unittest.TestCase):
    identifier = "TEST"
    event = {}

    def setUp(self):
        self.event = {"requestId": "testRequest",
            "templateParameterValues": {"Identifier": self.identifier},
            "region": "ap-southeast-2"}

    def test_replacement(self):
        self.event["fragment"] = {"Description": "%s template"}
        result = macro.handler(self.event, None)
        fragment = result["fragment"]
        self.assertEqual(fragment['Description'], "TEST template")

    def test_no_replacement(self):
        self.event["fragment"] = {"Description": "static template"}
        result = macro.handler(self.event, None)
        fragment = result["fragment"]
        self.assertEqual(fragment['Description'], "static template")

if __name__ == '__main__':
    unittest.main()
