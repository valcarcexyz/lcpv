import io
from typing import Callable

import multiprocessing as mp
import numpy as np
import picamera
import tqdm


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
        Params:
        ======
        resolution: tuple. Resolution to capture video (defaults to 1080p).
        framerate: int, defaults to 24.
        seconds: int. How long to capture the images
        process_output: function. What to do with the captured frames (frames will be a numpy array)
        """
        self.running.value = 1
        with picamera.PiCamera(resolution=resolution, framerate=framerate) as camera:
            camera.capture_sequence(
                    self._gen_buffers(frames=seconds * framerate,
                                      process_output=process_output,
                                      resolution=resolution),
                    "yuv",
                    use_video_port=True
            )
            print("Capture process ended. Closing the camera.")
        print("Camera closed.")
        self.running.value = 0
        return True

    def _gen_buffers(self, frames: int, process_output: Callable, resolution: tuple):
        """Yields buffers"""
        for _ in tqdm.tqdm(range(frames)):
            # create the stream buffer (to capture the frame to)
            stream = io.BytesIO()
            yield stream
            stream.seek(0)  # we got a new frame !
            # create a numpy array from the IO buffer:
            image = np.frombuffer(
                stream.getvalue(),
                dtype=np.uint8,
                count=np.prod(self.resolution),
            ).reshape(resolution[::-1])
            process_output(image)
        return
