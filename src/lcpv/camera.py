import io
from typing import Callable

import multiprocessing as mp
import numpy as np
import picamera


class Camera:
    def __init__(self):
        self.running = mp.Value('i', 0)

    def start_recording(self,
                        resolution: tuple = (1920, 1080),
                        framerate: int = 24,
                        seconds: int = 1,
                        process_output: Callable = lambda x: x,
                        ):
        """
        Abstraction layer of the picamera interface. Captures frames using the video port (same resolution, better
        framerate). For parallel usage, it provides a `running` thread-safe variable, so different threads can check
        whether it is running or it has already stopped.

        Params:
        ======
        :param resolution: tuple. Resolution to capture video (defaults to 1080p).
        :param framerate: int, defaults to 24.
        :param seconds: int. How long to capture the images
        :param process_output: function. What to do with the captured frames (frames will be a numpy array)
        """
        self.running.value = 1  # set 'boolean' to running
        with picamera.PiCamera(resolution=resolution, framerate=framerate) as camera:
            camera.capture_sequence(
                self._gen_buffers(frames=seconds * framerate,  # number of frames to capture with the video port
                                  process_output=process_output,
                                  resolution=resolution),
                "yuv",  # fastest method tested
                use_video_port=True
            )
            print("Capture process ended. Closing the camera.")
        print("Camera closed.")
        self.running.value = 0  # no longer running
        return True

    @staticmethod
    def _gen_buffers(frames: int, process_output: Callable, resolution: tuple):
        """Yields buffers and runs the `process_output` function to the captured frames"""
        for _ in range(frames):
            # create the stream buffer (to capture the frame to)
            stream = io.BytesIO()
            yield stream
            stream.seek(0)  # we got a new frame !
            # create a numpy array from the IO buffer:
            image = np.frombuffer(
                stream.getvalue(),
                dtype=np.uint8,
                count=np.prod(resolution),
            ).reshape(resolution[::-1])
            process_output(image)
        return None
