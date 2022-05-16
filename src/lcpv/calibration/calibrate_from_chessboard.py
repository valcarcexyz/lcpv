import numpy as np
import cv2

def get_camera_params(img: np.ndarray, chessboard_size: tuple = (4, 4)) -> dict:
    """

    source: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
    """
    assert len(img.shape) == 2, "`img` must be B&W"

    chessboard_x, chessboard_y = chessboard_size
    # create the object points
    objp = np.zeros((chessboard_x*chessboard_y, 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_y, 0:chessboard_x].T.reshape(-1, 2)

    plt.imshow(img, cmap="gray")
    plt.show()

    ret, corners = cv2.findChessboardCorners(img,
                                             (chessboard_y, chessboard_x),
                                             None)
    print(ret, corners)

    return {}


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    IMG_PATH = "../../../data/calibration/4c_cal.bmp"
    img = cv2.imread(IMG_PATH, 0)

    # _, img = cv2.threshold(img, 0, img.max(), cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #
    # #
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40))
    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


    size = (3, 3)
    ret, corners = cv2.findChessboardCorners(img, size, None)
    print(ret, corners)
    plt.imshow(img, cmap="gray")
    for corner in corners:
        corner = corner[0]
        plt.scatter(*corner, color="green")
    # cv2.drawChessboardCorners(img, size, corners, ret)

    # plt.imshow(img)
    plt.show()

    # dlt = cv2.dilate(img, kernel)
    # plt.imshow(img, cmap="gray")
    # plt.show()
    # import sys
    # sys.exit(0)
