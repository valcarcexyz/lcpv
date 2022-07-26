import matplotlib.pyplot as plt
from openpiv.pyprocess import extended_search_area_piv, get_coordinates
from typing import Callable
from functools import wraps
import numpy as np

from ..preprocessing import median_filter, opening_filter, correct_lens_distortion, correct_perspective_distortion


class LcpvTemplate:
    """
        Low Cost Particle Velocimeter Template used by both the edge processor and the video processor. It
    defines the common methods (the processing ones), that do not relay on how has the video been acquired.
    """

    def __init__(self, *args, **kwargs):
        self.results = {"x": [], "y": [], "u": [], "v": []}
        self.frame0 = None

    @staticmethod
    def _twice(func):
        """
        Utility decorator used to run a function on two different frames at the "same" time.
        """

        @wraps(func)
        def wrapper(frame0, frame1, *args, **kwargs):
            return func(frame0, *args, **kwargs), func(frame1, *args, **kwargs)

        return wrapper

    @_twice
    def lens_distortion(self, *args, **kwargs):
        return correct_lens_distortion(*args, **kwargs)

    @_twice
    def correct_perspective_distortion(self, *args, **kwargs):
        return correct_perspective_distortion(*args, **kwargs)

    @_twice
    def opening_filter(self, *args, **kwargs):
        return opening_filter(*args, **kwargs)

    @_twice
    def median_filter(self, *args, **kwargs):
        return median_filter(*args, **kwargs)

    def process_frames(self, frame0: np.ndarray, frame1: np.ndarray,
                       camera_params: dict = None,
                       preprocessing_filter: str = "opening_filter", preprocessing_filter_params: dict = {},
                       *args, **kwargs) -> None:
        """
        Consumer method (static) that process the frames of a video in pairs. The optional `args` and `kwargs` are
        by no means optional, they must include all the needed arguments to run the `openpiv.pyprocess_extended`
        function, that includes (but is not limited to) the following: `window_size`, `overlap` and `search_area_size`.

        To run some kind of preprocessing in the frames, `camera_params` should include:

        - if a lens distortion wants to be corrected, the dictionary must provide the following keys:
            - cameraMatrix
            - distCoeff
        - and if a perspective correction wants to be executed:
            - originalPoints
            - destinationPoints

        Args:
            frame0: np.ndarray. First frame.
            frame1: np.ndarray. Second frame.
            camera_params: dict. Dictionary containing (or not):
                `camera_matrix`, `dist_coeff`, `original_points`, `destination_points`
            preprocessing_filter: Callable. A function that takes both frames and returns them
            preprocessing_filter_params:

        Returns:
            None
        """
        assert ("window_size" in kwargs) and ("search_area_size" in kwargs) and ("overlap" in kwargs), \
            "Minimum args include window_size, search_area_size and overlap"

        # We convert the camera params keys to a set, for faster comparisons
        camera_params_set = set(camera_params)

        if {"camera_matrix", "dist_coeff"} <= camera_params_set:
            # we have the minimum requirements to run the lens correction
            frame0, frame1 = self.lens_distortion(frame0, frame1,
                                                  camera_params["camera_matrix"].astype(np.float32),
                                                  camera_params["dist_coeff"].astype(np.float32))

        if {"original_points", "destination_points"} <= camera_params_set:
            # we have the minimum requirements to run the perspective correction
            frame0, frame1 = self.correct_perspective_distortion(frame0, frame1,
                                                                 camera_params["original_points"].astype(np.float32),
                                                                 camera_params["destination_points"].astype(np.float32))

        # we store a copy of the first frame to plot the results
        if self.frame0 is None:
            self.frame0 = frame0

        # once the images are preprocessed, we can binarize them
        preprocessing_filter = getattr(self, preprocessing_filter, lambda _x, _y, **_: (_x, _y))
        frame0, frame1 = preprocessing_filter(frame0, frame1, **preprocessing_filter_params)

        u, v, s2n = extended_search_area_piv(frame0, frame1, *args, **kwargs)
        x, y = get_coordinates(image_size=frame0.shape,
                               search_area_size=kwargs["search_area_size"],
                               overlap=kwargs["overlap"])
        valid = s2n > np.percentile(s2n, 5)
        u[~valid] = np.nan
        v[~valid] = np.nan

        if len(self.results["x"]) == 0:  # so we do not add the same multiple times (as `x` and `y` are constant).
            self.results["x"].append(x)
            self.results["y"].append(y)

        self.results["u"].append(u)
        self.results["v"].append(-v)

    @property
    def median_results(self):
        """Median results of the OpenPIV process"""
        x, y = self.results["x"], self.results["y"]
        u, v = np.nanmedian(self.results["u"], axis=0), np.nanmedian(self.results["v"], axis=0)
        return x, y, u, v

    def show(self):
        if self.frame0 is not None:
            x, y, u, v = self.median_results
            plt.imshow(self.frame0, cmap="gray")
            plt.quiver(x, y, u, v)
            plt.show()
