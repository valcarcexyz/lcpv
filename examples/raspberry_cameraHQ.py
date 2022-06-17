"""
Example of how to run in the HQ camera with the parameters of src_old/camera_calibration/parameters.json

Meant to be used once installed with pip, but can run it from the src_old folder.
"""

import numpy as np
import json

# run once installed with pip
from src.lcpv.edge_process import LCPV


def main():
    # firstly, we read the camera calibration parameters
    with open("../src/lcpv/calibration/parameters.json", "r") as f:
        camera_params = dict(json.load(f))
    # and convert them to numpy arrays
    camera_params = {k: np.array(v) for k, v in camera_params.items()}

    capturer = LCPV()
    capturer.start(
        resolution=(1920, 1080),
        framerate=15,
        seconds=5,
        camera_params=camera_params,
        window_size=32, overlap=16, search_area_size=32
    )
    # and then show the median results
    print(capturer.median_results)


if __name__ == "__main__":
    main()