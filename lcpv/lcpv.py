# parallel computing:
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

# custom scripts:
from .unsharp_masking import opening_filter
from .particle_velocimetry import compute
from .lens_correction import Corrector

# utils
from typing import Callable
from queue import Queue
from PIL import Image
import numpy as np
import picamera
import tqdm
import io
import os


class LCPV:
    """Low Cost Particle Velocimetry
    
    This class works as an abstraction layer to the OpenPIV[1] particle
    velocimetry package to be run inside a Raspberry Pi. This works as 
    follows:

    1. Create all the objects needed, those include:
        - camera configuration (to be used with picamera[2])
        - create the queue to store the data
        - store the openpiv configuration
    2. A `start` method to run all the experiment with the provided
        configuration.

    Params:
    =======
    resolution: tuple.
        Resolution of the camera.
    framerate: int.
        Expected framerate (it may be lower due to raspberry power)
    correct_distortion: bool.
        Whether to correct the barrel
        distortion or not introduced by the lens. If True, 
        `camera` parameter must be provided.
    camera: dict. Lens correction parameters. Must include
        the following parameters (detailed in `lens_correction.py`):
        + mtx 
        + dst
        + rvecs 
        + tvecs
    write: bool. Whether to write results in disk or not.
    mask: function. How to mask the processed image (`None` won't
        mask it).


    Examples:
    =========

    ```python
    pv = LCPV(
        resolution = (1920, 1080),
        framerate = 24, # expected
        camera = Corrector.HQ_CAMERA,
        correct_distortion = True,
        write = False,
        window_size = 32,
        overlap = 16,
        search_window_size = 32,
        mask = lambda x: opening_filter(x)
    )
    pv.start(seconds = 10)
    ```

    [1]: http://www.openpiv.net/
    [2]: https://github.com/waveform80/picamera
    """
    NUM_CORES = mp.cpu_count()

    def __init__(self, resolution: tuple = (1920, 1080),
                 framerate: int = 24, correct_distortion: bool = True,
                 camera: dict = None,
                 write: bool = False, path: str = "~/frames/",
                 mask: Callable = lambda x: opening_filter(x, kernel_size=7, threshold=220),
                 *args, **kwargs):
        """LCPV constructor"""
        self.queue = Queue()
        self.resolution = resolution
        self.framerate = framerate
        self.correct_distortion = correct_distortion
        if correct_distortion:
            self.corrector = Corrector()
            self.camera = camera
        self.openpiv_args = kwargs
        self.write = write

        if write:
            self.path = path
            # check if frames folder exists
            if not os.path.exists(path):
                os.makedirs(path)

        self.mask = mask

        self.output = []  # where we will store the x, y, u, v

    def start(self,
              seconds: int = 1,
              *args, **kwargs):
        """Runs the experiment for `seconds`, with the constructor
        parameters as follows:
        1. First capture all the images and store them in memory.
            If lens distortion is corrected, it is corrected
            before storing it, to decrease the RAM usage.
        2. Do the OpenPIV processing and append the results
            in `self.output`
        """
        print("Starting the capture process...")
        if self._capture(seconds * self.framerate):
            print(f"Total frames captured: {self.queue.qsize()}. Starting the processing.")
            futures = []
            with ProcessPoolExecutor() as executor:
                while True:
                    # we will lock the queue to acquire the frames (otherwise nothing
                    # guarantees the frame order).
                    self.queue.mutex.acquire()
                    if len(self.queue.queue) >= 2:  # we have at least 2 frames to process remaining
                        frame0 = self.queue.queue.popleft()
                        frame1 = self.queue.queue[0]  # so we do not remove
                        self.queue.mutex.release()
                        # we can submit the job (we are in the if statement)
                        futures.append(
                            executor.submit(compute,
                                            [frame0, frame1],
                                            **self.openpiv_args)
                        )
                    else:
                        self.queue.mutex.release()
                        # we will have ended, so we compute the results.
                        for future in tqdm.tqdm(futures):
                            self.output.append(future.result())
                        break

            print(f"We have a total of {len(self.output)}")

    def _capture(self, frames: int):
        """Creates the camera object and captures the frames using the video port"""
        with picamera.PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            camera.capture_sequence(self._buffers(frames), "yuv", use_video_port=True)
            print("Capture process ended. Closing the camera.")
        print("Camera closed.")
        return True

    def _buffers(self, frames: int):
        """Yields buffers and adds them (once captured) to que queue"""
        for i in tqdm.tqdm(range(frames)):
            # create the stream buffer (to add the frame to)
            stream = io.BytesIO()
            yield stream  # return it to the camera to be used
            stream.seek(0)  # read the frame!
            # convert the buffer into a numpy array:
            image = np.frombuffer(
                stream.getvalue(),
                dtype=np.uint8,
                count=np.prod(self.resolution)
            ).reshape(self.resolution[::-1])

            # correct the images if requested
            if self.correct_distortion:
                image = self.corrector.correct_lens(image, camera=self.camera)
            # mask it if provided function to do so
            if self.mask:
                image = self.mask(image)
            # and write them if requested
            if self.write:
                Image.fromarray(image).save(f"{self.path}/frame_{str(i).zfill(frames % 10)}.png")
            # add them to the final queue
            self.queue.put(image)


if __name__ == "__main__":
    import sys
    args = sys.argv()
    # TODO: read this attributes and use them!
    print(args)
    l = LCPV(
        resolution=(1920, 1080),
        framerate=24,
        correct_distortion=True,
        camera=Corrector.HQ_CAMERA,
        window_size=32,
        search_area_size=32,
        overlap=16
    )