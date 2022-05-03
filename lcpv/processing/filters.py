import numpy as np
import cv2


def median_filter(img: np.ndarray,
                  kernel_size: int = 7,
                  threshold: int = 210) -> np.ndarray:
    """
    Creates a binarized image from variable `img`, using for
    so an unsharp masking technic[1]:
    1. Apply the median filter[2] to the complete image, with
        the params `kernel_size`.
    2. Where there has been a change in color intensity around
        a given `threshold`, turn on the pixel.

    Args:
        img: np.ndarray. A B&W image uint8
        kernel_size: int
        threshold: int

    Returns:
        np.ndarray: binarized image

    [1]: https://en.wikipedia.org/wiki/Unsharp_masking
    [2]: https://en.wikipedia.org/wiki/Median_filter
    """
    assert (img.dtype == np.uint8), "Image must be [0, 255], `dtype=np.uint8`"
    median_image = cv2.medianBlur(img, kernel_size)
    masked = np.logical_and(img > threshold,
                            median_image < threshold)
    return masked


def opening_filter(img: np.ndarray,
                   kernel_size: int = 7,
                   threshold: int = 220) -> np.ndarray:
    """
    Creates a binarized image from variable `img`, using for
    so an unsharp masking technic[1]:
    1. Apply the opening morphology operation[2] to the complete
        image, with the params `kernel_size`.
    2. Where there has been a change in color intensity around
        a given `threshold`, turn on the pixel.

    Args:
        img: np.ndarray. A B&W image uint8
        kernel_size: int
        threshold: int

    Returns:
        np.ndarray: binarized image

    [1]: https://en.wikipedia.org/wiki/Unsharp_masking
    [2]: https://en.wikipedia.org/wiki/Opening_(morphology)
    """
    assert (img.dtype == np.uint8), "Image must be [0, 255], `dtype=np.uint8`"
    opening = cv2.morphologyEx(
        src=img,
        op=cv2.MORPH_OPEN,
        kernel=np.ones((kernel_size, kernel_size), np.uint8),
        iterations=1
    )
    masked = np.logical_and(img > threshold,
                            opening < threshold)
    return masked
