import numpy as np

from lcpv import VideoProcessor
from lcpv.utils.base import LcpvTemplate
import matplotlib.pyplot as plt
import toml
import os


def pruebas():
    f1, f2 = plt.imread("data/rectified0.png", 0), plt.imread("data/rectified1.png", 0)
    f1, f2 = (f1 * 255).astype(np.uint8), (f2 * 255).astype(np.uint8)

    l = LcpvTemplate()
    l.process_frames(f1, f2, camera_params={}, window_size=32, search_area_size=32, overlap=16)
    x, y, u, v = l.median_results
    plt.quiver(x, y, u, v)
    plt.show()


def main():
    with open("run_config.toml", "r") as f:
        run_config = toml.load(f)

    # Firstly, we read the preprocessing/processing configuration
    preprocessing = run_config.get("preprocessing", {})

    # Filter for image clearance
    preprocessing_filter = preprocessing.get("filter", "")
    filter_params = preprocessing.get("filter_params", {})

    preprocessing_filter = ""

    # Camera parameters
    camera_params = preprocessing.get("camera_calibration", {})
    camera_params = {k: np.array(v) for k, v in camera_params.items()}

    # PIV params
    piv_params = run_config.get("piv", {})

    entrypoint = run_config.get("entrypoint", None)
    if os.path.exists(entrypoint):
        # We run the video processor
        vp = VideoProcessor()
        vp.start(filename=entrypoint, camera_params=camera_params,
                 preprocessing_filter=preprocessing_filter, preprocessing_filter_params=filter_params,
                 **piv_params)

    else:
        # We should try to run the raspberry processor
        pass


if __name__ == "__main__":
    main()
