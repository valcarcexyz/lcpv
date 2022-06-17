import numpy as np
import cv2


def select_points(img: np.ndarray) -> np.ndarray:
    """Wrapper to select points in a B&W image. Points should be
    selected from left to right, and then top to bottom"""
    points = []

    def _select(event, x, y, *args, **kwargs):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print(x, y)
            points.append((x, y))

    cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
    cv2.setMouseCallback('image', _select)
    cv2.imshow('image', img)
    cv2.waitKey(0)

    return np.stack(points)


def get_camera_params(img: np.ndarray) -> dict:
    """

    source: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
    """
    assert len(img.shape) == 2, "`img` must be B&W"
    image_points = select_points(img).astype(np.float32)  # get the points matrix
    assert len(image_points) >= 4, "minimum 4 points required. Use double click to select any point"

    n_cols = 1
    while image_points[n_cols - 1][0] < image_points[n_cols][0]:
        print(image_points[n_cols - 1], image_points[n_cols])
        n_cols += 1
    n_rows = len(image_points) // n_cols
    assert n_rows * n_cols == len(image_points), "Points must form a matrix, select only complete rows and cols"

    objp = np.zeros((n_rows * n_cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:n_cols, 0:n_rows].T.reshape(-1, 2)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([objp], [image_points], img.shape[::-1], None, None)
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    return {"cameraMatrix": newcameramtx, "distCoeff": dist}


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import tqdm

    IMG_PATH = "../../../data/calibration/4c_cal.bmp"
    img = cv2.imread(IMG_PATH, 0)
    puntos = get_camera_params(img)
    print(puntos)

    # plt.imshow(img, cmap="gray")
    # plt.show()

    # print(len(indices))
    # MIN_DISTANCE = 100
    # for idx_i in range(len(indices)):
    #     for idx_j in indices[idx_i:]:
    #         if distancia_euclidea(indices[idx_i], idx_j) > MIN_DISTANCE:
    #             # (podemos guardar el índice)
    #
    #     break
    #
    # for idx_i in indices:
    #     for idx_j in indices:
    #         print(idx_i, idx_j)
    #         print(distancia_euclidea(idx_i, idx_j))
    #         break
    #     break
    #         # if distancia_euclidea(idx_i, idx_j) < MIN_DISTANCE:
    #         #     print(idx_i, idx_j)
    #
    #
    # # img = cv2.morphologyEx(img, cv2.MORPH_ERODE, (21, 21), iterations=10)
    # plt.imshow(img, cmap="gray")
    # # img = cv2.Canny(img, 0, img.max())
    #
    # # plt.imshow(img, cmap="gray")
    # plt.show()

    size = (3, 3)
    # ret, corners = cv2.findChessboardCorners(img, size, None)
    # print(ret, corners)
    # plt.imshow(img, cmap="gray")
    # for corner in corners:
    #     corner = corner[0]
    #     plt.scatter(*corner, color="red")
    # # cv2.drawChessboardCorners(img, size, corners, ret)
    #
    # # plt.imshow(img)
    # plt.show()

    # dlt = cv2.dilate(img, kernel)
    # plt.imshow(img, cmap="gray")
    # plt.show()
    # import sys
    # sys.exit(0)
