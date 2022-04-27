"""
This script provides a simple example execution from the terminal args. Can be run when the package is installed
with pip or importing it from the src folder.
"""

import numpy as np
import json
import sys

# run once installed with pip
from lcpv.lcpv import LCPV

if __name__ == "__main__":
    # create the possible configs
    configs = ["--resolution", "--framerate", "--seconds",
               "--camera_params",
               "--window_size", "--overlap", "--search_area_size"]
    args = sys.argv
    run_parameters = {}  # to store the configuration

    for idx, arg in enumerate(args):
        if arg.startswith("--") and arg in configs:
            run_parameters[arg[2:]] = eval(args[idx + 1])  # as all arguments must be number, we can do it

    # the camera_params argument, must be a json file with the configuration of the camera, so we try to
    # read and parse it
    if "camera_params" in run_parameters:
        with open(run_parameters["camera_params"], "r") as f:
            camera_config = json.load(f)
        camera_config = {k: np.array(v) for k, v in camera_config.items()}
        run_parameters["camera_params"] = camera_config

    capturer = LCPV()
    capturer.start(**run_parameters)

    # what to do with the results is a job for the end user, so for now we just print it
    print(capturer.median_results)
