import sys
sys.path.append("..")

from src_old.lcpv.lens_corrector import correct_lens_distortion, correct_perspective
import numpy as np
import unittest
import cv2
import json


class TestCorrector(unittest.TestCase):
    """Test cases to check the lens correction (both introduced by the lens itself and
    the introduced by the perspective"""

    original_image = np.float32(cv2.imread("../data/original_image.bmp", 0))
    corrected_image = np.float32(cv2.imread("../data/corrected_image.png", 0))
    # camera params
    with open("../src/lcpv/calibration/parameters.json", "r") as f:
        params_camera_hq = json.load(f)["HQ_CAMERA"]
    params_camera_hq = {k: np.array(v) for k, v in params_camera_hq.items()}

    def test_lens_distortion(self):
        """Test if the lens distortion corrector works properly, with a tolerance of 1%"""
        lens_corrected = correct_lens_distortion(self.original_image,
                                                 self.params_camera_hq["cameraMatrix"],
                                                 self.params_camera_hq["distCoeff"])

        error = cv2.norm(self.corrected_image, lens_corrected)
        similarity = 1 - error / np.prod(lens_corrected.shape)
        self.assertGreaterEqual(similarity, 0.99)

    def test_perspective(self):
        """Tests whether the perspective correction works or not as expected. This test just checks if it runs"""
        correct_perspective(self.corrected_image,
                            self.params_camera_hq["originalPoints"].astype(np.float32),
                            self.params_camera_hq["destinationPoints"].astype(np.float32)
                            )
