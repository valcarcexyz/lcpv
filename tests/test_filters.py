import sys
sys.path.append("..")

from src.lcpv.filters import opening_filter, median_filter
import numpy as np
import unittest


class TestFilters(unittest.TestCase):
    """
    Will generate a full black image with a white point. Filters should (must)
    be able to filter those positions, thus return them as a True point.
    """
    size = (5, 5)
    img = np.zeros(size, dtype=np.uint8)
    not_black = np.random.randint(max(size), size=(1, 2), dtype=np.int)[0]
    img[not_black[0], not_black[1]] = 255

    def test_opening(self):
        """Checks for good behaviour of the opening filter"""
        self.assertEqual(True,
                         ((self.img != 0) == opening_filter(self.img, kernel_size=3, threshold=125)).all())

    def test_median(self):
        """Checks for good behaviour of the median filter"""
        self.assertEqual(True,
                         ((self.img != 0) == median_filter(self.img, kernel_size=3, threshold=125)).all())


if __name__ == '__main__':
    unittest.main()
