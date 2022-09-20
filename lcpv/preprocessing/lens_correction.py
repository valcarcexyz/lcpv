import numpy as np
import cv2


def correct_lens_distortion(img: np.ndarray, camera_matrix: np.ndarray, dist_coeff: np.ndarray) -> np.ndarray:
    """
    Corrects the distortion introduced by the camera lens with the given parameters.
    Refer to `calibration` subpackage for more details, or to the OpenCV documentation [1, 2]

    Args:
        img: np.ndarray. The image to be corrected (B&W)
        camera_matrix: np.ndarray. Camera matrix.
        dist_coeff: np.ndarray. Distortion coefficients.

    Returns:
        np.ndarray: corrected image

    [1]: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
    [2]: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga3207604e4b1a1758aa66acb6ed5aa65d
    """
    assert len(img.shape) == 2, "Input image *must* be black and white"
    h, w = img.shape
    newmtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeff, (w, h), 1, (w, h))
    dst = cv2.undistort(img, camera_matrix, dist_coeff, None, newmtx)
    x, y, w, h = roi
    return dst[y:(y + h), x:(x + w)]


def correct_perspective_distortion(img: np.ndarray, original_points: np.ndarray, destination_points: np.ndarray):
    """
    Corrects the perspective of the image. Refer to the camera calibration for more details or
    to the OpenCV documentation [1]

    Args:
        img: np.ndarray. The image to be corrected.
        original_points: np.ndarray. Original points in the image.
        destination_points: np.ndarray. The places where the points should really be.

    Returns:
        np.ndarray: the corrected image

    [1]: https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html#ga20f62aa3235d869c9956436c870893ae
    """
    assert original_points.shape == destination_points.shape, \
        "Must provide the same number of points for origin and destination"

    M = cv2.getPerspectiveTransform(original_points, destination_points)
    return cv2.warpPerspective(img, M, img.shape[:2][::-1])

