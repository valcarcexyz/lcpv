from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process
import multiprocessing
from camera import Camera
from particle_velocimetry import compute
import os

class LCPV:
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
                frames = self._acquire_frames()
                futures.append(executor.submit(self._run_computation, frames))
        camera_process.join()
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
