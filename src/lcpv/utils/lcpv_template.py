from openpiv.pyprocess import extended_search_area_piv, get_coordinates
from src.lcpv.processing import filters
from src.lcpv.processing import lens_correction
import numpy as np

from functools import wraps

class LowCostParticleVelocimeter:
    """
    Class template to be used for both the edge processing and the onsite processing (from a video file). It
    defines the common methods (process the frames and computation of the median results) with the aim of
    create simpler classes for both of them (just need to define how frames are acquired).
    """
    def __int__(self):
        self.results = {"x": [], "y": [], "u": [], "v": []}

    @staticmethod
    def twice(func):
        """Decorator to run twice a function in the two frames provided without needing to worry about writing
         loops or long lines"""
        @wraps(func)
        def wrapper(frame0, frame1, *args, **kwargs):
            return func(frame0, *args, **kwargs), func(frame1, *args, **kwargs)
        return wrapper

    @twice
    def lens_distortion(self, *args, **kwargs):
        return lens_correction.correct_lens_distortion(*args, **kwargs)

    @twice
    def perspective_correction(self, *args, **kwargs):
        return lens_correction.correct_perspective(*args, **kwargs)

    @twice
    def opening(self, *args, **kwargs):
        return filters.opening_filter(*args, **kwargs)

    def process_frames(self,
                       frame0: np.ndarray, frame1: np.ndarray,
                       camera_params: dict = {}, *args, **kwargs) -> None:
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

        :param frame0: np.ndarray. First frame.
        :param frame1: np.ndarray. Second frame.
        :param camera_params: dict [optional] The camera parameters dictionary to be used to correct both the lens and
            the perspective of the frames.
        :return: None
        """
        assert ("window_size" in kwargs) and ("search_area_size" in kwargs) and ("overlap" in kwargs), \
            "Minimum args include window_size, search_area_size and overlap"

        if {"cameraMatrix", "distCoeff"} <= set(camera_params):
            # we have the minimum requirements to run the lens correction
            frame0, frame1 = self.lens_distortion(frame0, frame1,
                                                  camera_params["cameraMatrix"], camera_params["distCoeff"])

        if {"originalPoints", "destinationPoints"} <= set(camera_params):
            # we have the minimum requirements to run the perspective correction
            frame0, frame1 = self.perspective_correction(frame0, frame1,
                                                         camera_params["originalPoints"], camera_params["destinationPoints"])

        # once the images are preprocessed, we can binarize them
        frame0, frame1 = self.opening(frame0, frame1, kernel_size=7, threshold=220)

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
        """
        Computes and returns (as a property) the median results of the
        return x, y, median(u), median(v)
        """
        x, y, u, v = self.results["x"], self.results["y"], self.results["u"], self.results["v"]
        # TODO: CHECK IF THIS IS AS IT IS WRITTEN OR IF SHOULD BE A CONCATENATED ARRAY (PREVIOUS IMPLEMENTATION)
        return x, y, np.nanmedian(u, axis=0), np.nanmedian(v, axis=0)
