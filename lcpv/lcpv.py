from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process
import multiprocessing
from .camera import Camera
from .particle_velocimetry import compute
import os

class LCPV:
    NUM_CORES = multiprocessing.cpu_count()

    def __init__(self, resolution:tuple, framerate:int, *args, **kwargs):
        self.camera = Camera(resolution=resolution, framerate=framerate)
        self.openpiv_args = kwargs
        self.results = [] # it is thread safe, so we can use it to store the results

    def start(self, seconds:int=10):
        camera_process = Process(target = self.camera.start_recording(seconds))
        camera_process.start()

        # run the computation
        futures = []
        with ProcessPoolExecutor(max_workers=self.NUM_CORES-1) as executor:
            while self.camera.running:
                for _ in range(self.NUM_CORES-1):
                    frames = self._acquire_frames()
                    futures.append(executor.submit(self._run_computation, frames))

        camera_process.join()

    def _run_computation(self, frames):
        """"""
        compute(frames, self.results, self.openpiv_args)
        return

    def _acquire_frames(self):
        """Get 2 new frames to start processing"""
        return list(self.camera.get_frames())


class Executor:
    def __init__(self):
        self.camera = Camera()

    def _aquire_frames(self):
        return self.camera.get_frames()
    
    def run():
        while True:
            pass
        

def run():
    """
    Run all experiments
    """
    camera = Camera()
    
    

def main():
    import os
    print(os.system("which python"))

if __name__ == "__main__":
    main()
