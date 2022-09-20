from lcpv import LCPV
from lcpv.preprocessing.filters import opening_filter
import numpy as np

l = LCPV(
    piv_window_size=32, piv_overlap=16, piv_search_area_size=32,
    preprocessing_filter=opening_filter,
)

l.process_video("data/video.mp4")

# results will be held in l.results

