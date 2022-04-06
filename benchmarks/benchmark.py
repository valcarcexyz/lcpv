# to measure performance:
import pandas as pd
# configuration to be able to print the complete dataframe:
pd.set_option("display.max_rows", 10)
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1_000)
import numpy as np
import time

# utils
import json

# import all the functions that must be measured
from src.lcpv import filters
from src.lcpv import lens_corrector

# parameters
with open("../src/camera_calibration/parameters.json") as f:
    HQ_CAMERA_PARAMS = json.load(f)["HQ_CAMERA"]

# Running configuration:
# The resolutions to be tested:
RESOLUTIONS = [(540, 480), (720, 576), (1280, 720), (1920, 1080), (2048, 1536), (2592, 1920), (3840, 2160)]
# define each one of the benchmarks to be run
def opening_filter(img): return filters.opening_filter(img, kernel_size=7, threshold=220)
def median_filter(img): return filters.median_filter(img, kernel_size=7, threshold=220)
def correct_lens_distortion(img):
    return lens_corrector.correct_lens_distortion(img,
                                                  np.array(HQ_CAMERA_PARAMS["cameraMatrix"]),
                                                  np.array(HQ_CAMERA_PARAMS["distCoeff"]))
def correct_image_perspective(img):
    return lens_corrector.correct_perspective(img,
                                              np.array(HQ_CAMERA_PARAMS["originalPoints"], dtype=np.float32),
                                              np.array(HQ_CAMERA_PARAMS["destinationPoints"], dtype=np.float32))


# store all them in a list to be run in a loop
TESTS = [opening_filter, median_filter, correct_lens_distortion, correct_image_perspective]
# define how many runs to do to average times of execution
RUNS = 10


def run():
    """
    Runs all the benchmarks and return a pandas dataframe containing the time measurement (in seconds).
    """
    df = pd.DataFrame(index=RESOLUTIONS,
                      columns=[test.__name__ for test in TESTS])

    for resolution in RESOLUTIONS:
        img = np.random.randint(low=0, high=255, size=resolution, dtype=np.uint8)
        for test in TESTS:
            start = time.time()
            [test(img) for _ in range(RUNS)]
            end = time.time()
            df.loc[[resolution], test.__name__] = (end - start) / RUNS
    print(df)


if __name__ == "__main__":
    run()
