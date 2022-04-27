"""
This example provides a simple way to process a video from the command line using the functions developed in
this package. This is meant to be used when installation via `pip` is not available (for example, when we do not
want to process the video in streaming, but in a more powerful computer).
"""
import numpy as np
import json
import sys
sys.path.append("../")
from utils.args_parser import parse

sys.path.append("../../")
from src.lcpv.lens_corrector import correct_lens_distortion, correct_perspective
from src.lcpv.filters import opening_filter

from openpiv.pyprocess import extended_search_area_piv, get_coordinates

def main():
    pass


if __name__ == "__main__":

    configs = ["--camera_params", "--window_size", "--overlap", "--search_area_size"]

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
    print(run_parameters)
    main()
