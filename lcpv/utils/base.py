from functools import wraps

import numpy as np
from openpiv.pyprocess import extended_search_area_piv, get_coordinates

import matplotlib.pyplot as plt

from ..preprocessing import median_filter, opening_filter, correct_lens_distortion, correct_perspective_distortion


class LcpvTemplate:
    """
        Low Cost Particle Velocimeter Template used by both the edge processor and the video processor. It
    defines the common methods (the processing ones), that do not relay on how has the video been acquired.
    """

    def __init__(self, *args, **kwargs):
        self.results = {"x": [], "y": [], "u": [], "v": []}

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

    def process_frames(self, frame0: np.ndarray, frame1: np.ndarray, camera_params: dict = None, *args,
                       **kwargs) -> None:
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
                                                  camera_params["camera_matrix"], camera_params["dist_coeff"])

        if {"original_points", "destination_points"} <= camera_params_set:
            # we have the minimum requirements to run the perspective correction
            frame0, frame1 = self.correct_perspective_distortion(frame0, frame1,
                                                                 camera_params["original_points"],
                                                                 camera_params["destination_points"])

        # once the images are preprocessed, we can binarize them
        frame0, frame1 = self.opening_filter(frame0, frame1, kernel_size=7, threshold=220)

        u, v, s2n = extended_search_area_piv(frame0, frame1, *args, **kwargs)
        x, y = get_coordinates(image_size=frame0.shape,
                               search_area_size=kwargs["search_area_size"],
                               overlap=kwargs["overlap"])
        valid = s2n < np.percentile(s2n, 5)

        if len(self.results["x"]) == 0:  # so we do not add the same multiple times (as `x` and `y` are constant).
            self.results["x"].append(x[valid])
            self.results["y"].append(y[valid])

        self.results["u"].append(u[valid])
        self.results["v"].append(-v[valid])

    @property
    def median_results(self):
        """Median results of the OpenPIV process"""
        x, y, u, v = self.results["x"], self.results["y"], self.results["u"], self.results["v"]
        assert (x and y and u and v), "Not yet computed"
        return x, y, np.nanmedian(u, axis=0), np.nanmedian(v, axis=0)
