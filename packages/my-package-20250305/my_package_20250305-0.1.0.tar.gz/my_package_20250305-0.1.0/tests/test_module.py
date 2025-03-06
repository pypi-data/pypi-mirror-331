import unittest
from my_package import hello

class TestHello(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello(), "Hello from my_package!")

if __name__ == "__main__":
    unittest.main()
