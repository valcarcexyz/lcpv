import numpy as np
import json

def parse(args: list) -> dict:
    """Given a list of arguments passed to a program, returns the parsed version as a dictionary.
    Recognizes the following params:
    + --resolution: tuple indicating the resolution of the image to be captured (i.e. `(1920,1080)`)
    + --framerate: int with the expected framerate
    + --seconds: int of how long to store frames
    + --camera_params: str, a path to a json file with the camera configuration (see `src/camera_calibration`)
    + --window_size: int, OpenPIV param
    + --overlap: int, OpenPIV param
    + --search_area_size: int, OpenPIV param

    :param args: list containing the result of `sys.arg`
    :return dict
    """
    configs = ["--resolution", "--framerate", "--seconds",
               "--camera_params",
               "--window_size", "--overlap", "--search_area_size"]
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
    return run_parameters