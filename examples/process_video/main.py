"""
This example provides a simple way to process a video from the command line using the functions developed in
this package. This is meant to be used when installation via `pip` is not available (for example, when we do not
want to process the video in streaming, but in a more powerful computer).
"""
import time

import numpy as np
import cv2
import sys
sys.path.append("../")
from utils.args_parser import parse

sys.path.append("../../")
from src_old.lcpv.lens_corrector import correct_lens_distortion, correct_perspective
from src_old.lcpv.filters import opening_filter

from openpiv.pyprocess import extended_search_area_piv, get_coordinates

import matplotlib.pyplot as plt

def process_frame(frame0, frame1, params):
    """Function that runs all the processing at once"""
    frame0, frame1 = frame0.astype(np.float32), frame1.astype(np.float32)
    if "camera_params" in params:
        camera_params = params.pop("camera_params")

        if ("cameraMatrix" in camera_params) and ("distCoeff" in camera_params):
            # we can safely run the lens distortion correction
            frame0, frame1 = [correct_lens_distortion(img,
                                                      camera_params["cameraMatrix"], camera_params["distCoeff"]
                                                      ) for img in [frame0, frame1]]
        # the same if we want to run the perspective correction
        if ("originalPoints" in camera_params.keys()) and ("destinationPoints" in camera_params.keys()):
            frame0, frame1 = [correct_perspective(img,
                                                  camera_params["originalPoints"].astype(np.float32),
                                                  camera_params["destinationPoints"].astype(np.float32)
                                                  ) for img in [frame0, frame1]]

    frame0, frame1 = [opening_filter(img) for img in [frame0, frame1]]
    u, v, s2n = extended_search_area_piv(frame0, frame1, **params)
    x, y = get_coordinates(image_size=frame0.shape,
                           search_area_size=params["search_area_size"],
                           overlap=params["overlap"])
    valid = s2n < np.percentile(s2n, 5)
    return x[valid], y[valid], u[valid], -v[valid]


def main(video_path, params):
    x, y, u, v = [], [], [], []
    video_capture = cv2.VideoCapture(video_path)
    frames = []
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        # convert to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        if ret:
            frames.append(frame)
        else:
            break

        if len(frames) >= 2:
            print("Processing...")
            frame0, frame1 = frames.pop(0), frames[0]
            _x, _y, _u, _v = process_frame(frame0, frame1, params)
            x.append(_x)
            y.append(_y)
            u.append(_u)
            v.append(_v)
            print("Processed")
            print(u)
            print(v)

    video_capture.release()
    sys.exit(0)


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 8:
        print("""
        usage: python main.py video 
            --window_size integer --overlap integer --search_area_size integer  
            [--camera_params file.json]
        """)
        sys.exit(1)
    video_path = args[1]
    run_parameters = parse(args[2:])
    main(video_path, run_parameters)
