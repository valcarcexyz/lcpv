import sys
import unittest

sys.path.append("..")

from src.lcpv.lens_corrector import correct_lens_distortion, correct_perspective
import matplotlib.pyplot as plt
import numpy as np
import cv2
import json


class TestCorrector(unittest.TestCase):
    """Test cases to check the lens correction (both introduced by the lens itself and
    the introduced by the perspective"""

    original_image = cv2.imread("../data/original_image.bmp", 0)
    corrected_image = cv2.imread("../data/corrected_image.png", 0)
    # camera params
    with open("../src/camera_calibration/parameters.json", "r") as f:
        params_camera_hq = json.load(f)["HQ_CAMERA"]
    params_camera_hq = {k: np.array(v) for k, v in params_camera_hq.items()}

    def test_lens_distortion(self):
        """Test if the lens distortion corrector works properly, with a tolerance of 1 pixel"""
        lens_corrected = correct_lens_distortion(self.original_image,
                                                 self.params_camera_hq["cameraMatrix"],
                                                 self.params_camera_hq["distCoeff"])
        self.assertEqual(True, np.isclose(lens_corrected, self.corrected_image, rtol=1).all())