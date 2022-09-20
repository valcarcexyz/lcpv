"""
This is not the intended use of the library, but it will be documented just in
case someone needs to use this capability
"""
from lcpv import LCPV
from lcpv.preprocessing.filters import opening_filter
import cv2

frame0, frame1 = cv2.imread("data/rectified0.png", 0), cv2.imread("data/rectified1.png", 0)

l = LCPV(
    piv_window_size=32, piv_overlap=16, piv_search_area_size=32,
    preprocessing_filter=opening_filter,
    preprocessing_filter_args={"kernel_size": 7, "threshold": 220},
)
l._consume_frames(frame0, frame1)

# now, l.results will hold the results

