import numpy as np 
import cv2

class Corrector:

    HQ_CAMERA = {
        "mtx": np.array([[5170.73738,         0., 2866.84263],
                         [0.,         4307.52724, 1131.25773],
                         [0.,                 0.,         1.]]),
        "dst": np.array([[-0.85745244,  0.05168725,  0.10194636, -0.10056902, -0.04326248]]),
        "rvecs": np.array([[-0.95357458],[-0.23090414],[-0.14895711]]),
        "tvecs": np.array([[-3.69480464],[-0.12774038],[ 8.80394152]])
    }

    def __init__(self):
        pass

    def correct_lens(self, img:np.ndarray, camera:dict=None):
        """
        Corrects the lens distortion of an image given the camera distortion 
        properties in `camera`. Those parameters, can be obtained via 
        OpenCV as shown in [1]. 

        Params: # TODO: COMPLETAR DOCUMENTACIÓN
        =======
        img: np.ndarray. The image to be corrected
        camera: dict. A dictionary containing the following keys:
            + mtx: 
            + dst: 
            + rvecs: 
            + tvecs: 

        Returns:
        ========
        np.ndarray: The corrected image. Be aware that the resolution
            may have dropped due to this correction.


        [1]: https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
        """
        if not camera: # no correction to be done
            return
        h,  w = img.shape[:2]
        newmtx, roi = cv2.getOptimalNewCameraMatrix(camera["mtx"], 
                                                    camera["dst"], 
                                                    (w,h), 1, (w,h))

        dst = cv2.undistort(img, camera["mtx"], camera["dst"], None, newmtx)
        # crop the image to select the correction
        x, y, w, h = roi
        return dst[y:y+h, x:x+w]

    def correct_perspective(self, img, points:dict):
        """
        points = {"original_points": [], "target_points": []}
        """
        # TODO: decide how to implement it!



if __name__ == "__main__":
    corr = Corrector()
