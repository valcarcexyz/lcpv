"""
"""

from collections.abc import Callable
from openpiv.pyprocess import extended_search_area_piv, get_coordinates
import numpy as np


class LCPV():
    def __init__(self, 
            preprocessing_filter: Callable = lambda x: x,
            preprocessing_filter_args: dict = {},

            piv_window_size: int = 32,
            piv_search_area_size: int = 32,
            piv_overlap: int = 16,
            piv_dt: int = 1,

            postprocessing_filter: Callable = lambda x: x,
            postprocessing_filter_args: dict = {},
            *args, **kwargs
        ) -> None:
        """"""
        self.preprocessing = lambda x: preprocessing_filter(x, **preprocessing_filter_args)
        self.piv_process = lambda x, y: self._piv(x, y,
            window_size = piv_window_size,
            search_area_size = piv_search_area_size,
            overlap = piv_overlap, 
            dt = piv_dt,
        )
        self.postprocessing = lambda x: postprocessing_filter(x, postprocessing_filter_args)
        self.results = {"x": [], "y": [], "u": [], "v": []}

    def _piv(self, frame0: np.ndarray, frame1, *args, **kwargs):
        u, v, s2n = extended_search_area_piv(frame0, frame1, *args, **kwargs)
        x, y = get_coordinates(
            image_size=frame0.shape,
            search_area_size=kwargs["search_area_size"],
            overlap=kwargs["overlap"],
        )
        # valid = s2n > np.percentile(s2n, 5)
        return x, y, u, -v


    def _consume_frames(self, frame1, frame2) -> None:
        """"""
        frame1, frame2 = self.preprocessing(frame1), self.preprocessing(frame2)
        x, y, u, v = self.piv_process(frame1, frame2)
        self.results["x"].append(x)
        self.results["y"].append(y)
        self.results["u"].append(u)
        self.results["v"].append(v)

    def process_camera(self,
            resolution: tuple = (1920, 1080),
            fps: int = 24,
        ) -> None:
        """"""
    
    def process_video(self) -> None:
        """"""

