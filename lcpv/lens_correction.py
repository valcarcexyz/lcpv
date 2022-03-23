import numpy as np 
import cv2

class Corrector:

    HQ_CAMERA = {
        "mtx": np.array([[5.17073738e+03, 0.00000000e+00, 2.86684263e+03],
                        [0.00000000e+00, 4.30752724e+03, 1.13125773e+03],
                        [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]),
        "dst": np.array([[-0.85745244,  0.05168725,  0.10194636, -0.10056902, -0.04326248]]),
        "rvecs": np.array([[-0.95357458],[-0.23090414],[-0.14895711]]),
        "tvecs": np.array([[-3.69480464],[-0.12774038],[ 8.80394152]])
    }

    def __init__(self):
        pass

    def correct(self, img:np.ndarray, camera:dict=self.HQ_CAMERA):
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
        h,  w = img.shape[:2]
        newmtx, roi = cv2.getOptimalNewCameraMatrix(camera["mtx"], 
                                                    camera["dist"], 
                                                    (w,h), 1, (w,h))

        dst = cv2.undistort(img, mtx, dist, None, newmtx)
        # crop the image to select the correction
        x, y, w, h = roi
        return dst[y:y+h, x:x+w]


if __name__ == "__main__":
    corr = Corrector()
