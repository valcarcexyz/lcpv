from openpiv import piv
import numpy as np
import time


def compute(frames: list,
            output_structure: list = None,
            **kwargs):
    """
    Wrapper for the OpenPIV cross-correlation particle
    velocimetry computation.

    Params:
    =======
    frames: list. A list containing 2 frames (np.ndarray
        objects)
    output_structure: list (optional). Where the output
        should be written.
    **kwargs containing the necessary parameters to run
        the openpiv.piv.pyprocess.extended_search_area_piv
        function. For minimal functionality, it must provide:
        + window_size: int
        + overlap: int
        + search_area_size: int

    Returns:
    =======
    None: if there is a `output_structure` provided
    (x, y, u, v): tuple contaning positions x, y and
        velocities u, v
    
    Computes the cross correlation PIV...
    kwargs -> passed to the openpiv program, contaning:
    1. overlap
    2. window_size
    3, dt
    4, search_area_size
    frames -> list/array containing numpy arrays
    """
    u, v, s2n = piv.pyprocess.extended_search_area_piv(
        *frames, **kwargs
    )
    x, y = piv.pyprocess.get_coordinates(
        image_size=frames[0].shape,
        search_area_size=kwargs["search_area_size"],
        overlap=kwargs["overlap"]
    )

    valid = s2n > np.percentile(s2n, 5)
    x, y, u, v = x[valid], y[valid], u[valid], -v[valid]

    if output_structure:
        # TODO: improve (depends on the output_structure)
        output_structure.append((x, y, u, v))
        return
    else:
        return (x, y, u, v)


if __name__ == "__main__":
    img = np.random.randint(0, 255, (512, 512), dtype=np.uint8)

    start = time.time()
    compute([img] * 2, overlap=16, search_area_size=32, window_size=32)
    end = time.time()
    print(f"Took {end - start}s to process 2 frames")
