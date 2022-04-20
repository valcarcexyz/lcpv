import numpy as np
import cv2

def correct_lens_distortion(img:np.ndarray, cameraMatrix: np.ndarray, distCoeff: np.ndarray):
    """Corrects the distortion introduced by the lens with the parameters given. Refer to
    the camera calibration for more information"""
    h, w = img.shape
    newmtx, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, distCoeff, (w, h), 1, (w, h))
    dst = cv2.undistort(img, cameraMatrix, distCoeff, None, newmtx)
    x, y, w, h = roi
    return dst[y:(y+h), x:(x+w)]


def correct_perspective(img:np.ndarray, originalPoints: np.ndarray, destinationPoints: np.ndarray):
    """Corrects the perspective of the image. Refer to the camera calibration for more details."""
    M = cv2.getPerspectiveTransform(originalPoints, destinationPoints)
    return cv2.warpPerspective(img, M, img.shape[:2][::-1])
