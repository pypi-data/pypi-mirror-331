import unittest
from sizeforemir import cocksize_formula

class TestCalculateRatio(unittest.TestCase):
    def test_valid_input(self):
        self.assertAlmostEqual(cocksize_formula(180, 25), 10.835, places=2)

    def test_zero_values(self):
        with self.assertRaises(ValueError):
            cocksize_formula(0, 25)

    def test_negative_values(self):
        with self.assertRaises(ValueError):
            cocksize_formula(-180, 25)

if __name__ == "__main__":
    unittest.main()
