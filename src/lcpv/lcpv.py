import time

from src.lcpv.utils.lcpv_template import LowCostParticleVelocimeter
import tqdm
import cv2
import os

class VideoProcessor(LowCostParticleVelocimeter):
    def __init__(self):
        super().__int__()

    def start(self, filename: str):
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
                # TODO: TO B&W
                self.process_frames(frame0[...,0], frame1[...,0], window_size=32, overlap=16, search_area_size=32)
                print("2 complete frames ready")
                import matplotlib.pyplot as plt
                print([self.results["x"], self.results["y"]], self.results["u"], self.results["v"])
                # plt.quiver([self.results["x"], self.results["y"]], self.results["u"], self.results["v"])
                # plt.show()
                break


if __name__ == "__main__":
    processor = VideoProcessor()
    print(processor.results)
    processor.start("/home/valcarce/Documents/universidad/2021ColaboracionDepartamento/lluvia-cosas/lcpv/data/video.h264")
