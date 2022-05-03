from typing import Callable
import numpy as np
import picamera
import io


def _gen_buffers(resolution: tuple[int], frames: int, process_output: Callable,) -> None:
    """Private method that generates buffers (to store the frames in) and also
    executes the `process_output` function in the numpy array images

    :param resolution: tuple[int]
    :param frames: int
    :param process_output: Callable
    :return: None
    """
    for _ in range(frames):
        # create the stream buffer (to capture the frame to)
        stream = io.BytesIO()
        yield stream  # yield it so the camera can write to it
        stream.seek(0)  # we got a new frame !
        # create a numpy array from the IO buffer:
        image = np.frombuffer(
            stream.getvalue(),
            dtype=np.uint8,
            count=np.prod(resolution),
        ).reshape(resolution[::-1])  # cameras capture it with the reversed resolution
        process_output(image)  # do whatever the user asks for


def start_recording(resolution: tuple = (1920, 1080),
                    framerate: int = 24,
                    seconds: int = 1,
                    process_output: Callable = lambda _: None,
                    ) -> bool:
    """
    Function that interacts with the raspberry pi camera, using the picamera library [1]. It uses the video port
    to take images, because it keeps the native resolution of the sensor, but with the framerate of a video. It also
    uses the 'yuv' format, as it is supposedly faster than RGB capture (but this depends on how the implementation
    is done in the picamera library).

    :param resolution: tuple[int].
    :param framerate: int.
    :param seconds: int.
    :param process_output: Callable.
    :return: True if everything works fine.
    :rtype: bool.

    [1]: https://github.com/waveform80/picamera
    """
    with picamera.PiCamera(resolution=resolution, framerate=framerate) as camera:
        camera.capture_sequence(
            _gen_buffers(resolution=resolution,
                         frames=seconds * framerate,
                         process_output=process_output,
                         ),
            "yuv",  # fastest method tested
            use_video_port=True
        )

    return True
