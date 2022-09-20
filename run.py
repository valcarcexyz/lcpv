from lcpv import LCPV
from lcpv.preprocessing.filters import opening_filter

## lcpv
l = LCPV(
    piv_window_size=32, piv_overlap=16, piv_search_area_size=32,
    preprocessing_filter=opening_filter,
)



