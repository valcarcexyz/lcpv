from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process
import multiprocessing
from camera import Camera
from particle_velocimetry import compute
import os

from .lens_correction import Corrector
import multiprocessing as mp
from queue import Queue
import numpy as np
import picamera
import time
import io

class LCPV:
    """"""
    NUM_CORES = mp.cpu_count()

    def __init__(self, resolution:tuple=(1920, 1080),
            framerate:int = 24, correct_distortion:bool=True,
            camera:dict = None, *args, **kwargs):
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

        

    def start(self, resolution:tuple=(1920, 1080), 
              framerate:int=24, 
              seconds:int=1, 
              *args, **kwargs):
        """Runs the experiment
        **kwargs => openpiv args"""
        if self._capture(resolution, framerate, framerate*seconds):
            print("Captured correctly")

    def _capture(self, resolution:tuple, framerate:int, frames:int):
        """Creates the camera object and calls the self.buffers"""
        self.resolution = resolution
        with picamera.PiCamera(resolution=resolution, framerate=framerate) as camera:
            camera.capture_sequence(self._buffers(frames), "yuv", use_video_port=True)
        return True

    def _buffers(self, frames:int):
        """Yields buffers and adds them to que queue"""
        for _ in range(frames):
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
            # TODO: correct perspective?
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

class _LCPV:
    NUM_CORES = multiprocessing.cpu_count()

    def __init__(self, resolution:tuple, framerate:int, *args, **kwargs):
        self.camera = Camera(resolution=resolution, framerate=framerate)
        self.openpiv_args = kwargs
        self.results = [] # it is thread safe, so we can use it to store the results

    def start(self, seconds:int=10):
        camera_process = Process(target = self.camera.start_recording, args=(seconds,))
        camera_process.start()

        # run the computation
        futures = []
        with ProcessPoolExecutor(max_workers=self.NUM_CORES-1) as executor:
            while self.camera.running:
                futures=[]
                for _ in range(self.NUM_CORES-1):
                    frames = self._acquire_frames()
                    futures.append(executor.submit(self._run_computation, frames))
                [future.result() for future in futures]
        camera_process.join()

    def close(self):
        self.camera.camera.close()

    def _run_computation(self, frames):
        """"""
        compute(frames, self.results, self.openpiv_args)
        return

    def _acquire_frames(self):
        """Get 2 new frames to start processing"""
        return list(self.camera.get_frames())



if __name__ == "__main__":
    l = LCPV((1920, 1080), 24, window_size=32, overlap=16, search_area_size=32)
