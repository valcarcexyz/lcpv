from src.lcpv.utils.lcpv_template import LowCostParticleVelocimeter

import numpy as np
import cv2
import os


class VideoProcessor(LowCostParticleVelocimeter):
    def __init__(self):
        super().__int__()

    def start(self, filename: str, camera_params: dict = {}, ):
        """Given a filename, it computes the OpenPIV with the perspective corrections (if desired)"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Could not find {filename}")
        capture = cv2.VideoCapture(filename)
        if not capture.isOpened():
            raise IOError(f"Error openning file {filename}")

        frame0, frame1 = None, None
        while capture.isOpened():
            frame0 = frame1
            ret, frame1 = capture.read()

            if (frame0 is not None) and (frame1 is not None) and ret:  # two frames and read correctly
                if len(frame0.shape) >= 3:  # (it is in rgb)
                    frame0, frame1 = cv2.cvtColor(frame0, cv2.COLOR_RGB2GRAY), cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)

                self.process_frames(frame0, frame1, camera_params=camera_params,
                                    window_size=32, overlap=16, search_area_size=32)


if __name__ == "__main__":
    import json
    with open("calibration/parameters.json") as f:
        CAMERA_PARAMS = json.load(f)["HQ_CAMERA"]
        CAMERA_PARAMS = {k: np.array(v, dtype=np.float32) for k, v in CAMERA_PARAMS.items()}

    processor = VideoProcessor()
    print(processor.results)
    processor.start(
        "/home/valcarce/Documents/universidad/2021ColaboracionDepartamento/lluvia-cosas/lcpv/data/video.h264")
