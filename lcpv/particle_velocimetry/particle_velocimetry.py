from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from typing import Union
from openpiv import piv
import numpy as np
import time

NUM_PROCESSORS = multiprocessing.cpu_count()


def _compute(*args, **kwargs):
    return piv.pyprocess.extended_search_area_piv(*args, **kwargs)


def compute(frames: Union[list, np.ndarray],
            window_size: int = 32,
            overlap: int = 16,
            dt: int = 1,
            search_area_size: int = 32,
            sig2noise_method: str = "peak2peak"):
    """
    if len(frames) > 2: run it in parallel
    else: run it just as it is
    
    Args:
        frames:
        window_size:
        overlap:
        dt:
        search_area_size:
        sig2noise_method:

    Returns:

    """
    if len(frames) == 2:  # we can compute it directly
        results = _compute(*frames,
                           window_size=window_size,
                           overlap=overlap,
                           dt=dt,
                           search_area_size=search_area_size,
                           sig2noise_method=sig2noise_method)

    else:  # run it in parallel!
        futures = []
        results = []
        with ProcessPoolExecutor(max_workers=NUM_PROCESSORS) as executor:
            for frame_x, frame_y in zip(frames[:-1], frames[1:]):
                futures.append(
                    executor.submit(
                        _compute,
                        frame_x, frame_y,
                        window_size=window_size,
                        overlap=overlap,
                        dt=dt,
                        search_area_size=search_area_size,
                        sig2noise_method=sig2noise_method
                    )
                )

            for future in futures:
                results.append(future.result())

    return results


if __name__ == "__main__":
    img = np.random.randint(0, 255, (512, 512), dtype=np.uint8)

    start = time.time()
    compute([img]*2)
    end = time.time()
    print(f"Took {end-start}s to process 2 frames, however...")

    how_many = 50
    start = time.time()
    compute([img]*how_many)
    end = time.time()
    print(f"Took {end-start}s to process 10 frames, which is about {(end-start)/(how_many-1)}s per frame")