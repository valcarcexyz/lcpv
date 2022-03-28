from concurrent.futures import ProcessPoolExecutor
from .particle_velocimetry import compute
from .lens_correction import Corrector
import multiprocessing as mp
from queue import Queue
from PIL import Image
import numpy as np
import picamera
import time
import io
import os

class LCPV:
    """"""
    NUM_CORES = mp.cpu_count()

    def __init__(self, resolution:tuple=(1920, 1080),
            framerate:int = 24, correct_distortion:bool=True,
            camera:dict = None, 
            write:bool=False, path:str="~/frames/",
            *args, **kwargs):
        """Builds the queue to output the data
        
        if `correct_distortion`, `camera` argument config must be provided, 
        example:
        camera = Corrector.HQ_CAMERA (one of the provided in corrector)
        **kwargs => all the remaining openpiv args
        """
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

        self.output = [] # where we will store the x, y, u, v

    def start(self,
              seconds:int=1,
              write:bool=False,
              *args, **kwargs):
        """Runs the experiment
        **kwargs => openpiv args"""
        if self._capture():
            print("Captured correctly")
            futures = []
            with ProcessPoolExecutor() as executor:
                while True:
                    self.queue.mutex.acquire()
                    if self.queue.qsize() >= 2:
                        frame0 = self.queue.get()
                        frame1 = self.queue.queue[0] # so we do not remove it
                        print("We got 2 frames to process")
                    else:
                        print("Last iteration!")
                        for future in futures:
                            self.output.append(future.result())
                        break # we will have ended

                    self.queue.mutex.release()

                    print("Submitting jobs!")
                    # we can submit the job
                    futures.append(
                        executor.submit(compute,
                                        [frame0, frame1], 
                                        **self.openpiv_args)
                    )
            print(f"We have a total of {len(self.output)}")


    def _capture(self, frames:int):
        """Creates the camera object and calls the self.buffers"""
        with picamera.PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            camera.capture_sequence(self._buffers(frames), "yuv", use_video_port=True)
        return True

    def _buffers(self, frames:int):
        """Yields buffers and adds them to que queue"""
        for i in range(frames):
            stream = io.BytesIO()
            yield stream 
            stream.seek(0) # read the frame!
            image = np.frombuffer(
                stream.getvalue(),
                dtype=np.uint8,
                count=np.prod(self.resolution)
            ).reshape(self.resolution[::-1])
            if self.correct_distortion:
                image = self.corrector.correct_lens(image)
            if self.write:
                Image.fromarray(image).save(f"{self.path}/frame_{str(i).zfill(frames%10)}.png")
            self.queue.put(image)


if __name__ == "__main__":
    l = LCPV(
        resolution=(1920, 1080),
        framerate=24,
        correct_distortion=True,
        camera=Corrector.HQ_CAMERA,
        window_size=32, 
        search_area_size=32,
        overlap=16
    )