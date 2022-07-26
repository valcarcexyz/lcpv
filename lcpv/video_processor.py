from tqdm import tqdm
import cv2
import os

from .utils import base


class VideoProcessor(base.LcpvTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self, filename: str, camera_params: dict = None, *args, **kwargs):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} not found")

        capture = cv2.VideoCapture(filename)
        if not capture.isOpened():
            raise IOError(f"Error opening {filename}")

        n_frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)

        frame0, frame1 = None, None
        with tqdm(total=n_frames) as pbar:
            while capture.isOpened():
                frame0 = frame1
                ret, frame1 = capture.read()

                if ret and (frame0 is not None) and (frame1 is not None):
                    if len(frame0.shape) >= 3:
                        frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2GRAY)
                    if len(frame1.shape) >= 3:
                        frame1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)

                    self.process_frames(frame0, frame1, camera_params=camera_params, *args, **kwargs)

                pbar.update(1)
