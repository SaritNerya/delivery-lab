import unittest
from app import health_payload

class TestHealth(unittest.TestCase):
    def test_health_status(self):
        result = health_payload()
        self.assertEqual(result["status"], "ok")

    def test_health_version(self):
        result = health_payload()
        self.assertIn("version", result)

if __name__ == '__main__':
    unittest.main()