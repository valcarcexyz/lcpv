import sys
sys.path.append("..")
from lcpv.particle_velocimetry import compute
import numpy as np
import time

def particle_velocimetry(img, runs:int = 10):
    """Runs default params to test performance"""
    start = time.time()
    for _ in range(runs):
        compute([img, img], None, 
                window_size=32, overlap=16, search_area_size=32)
    end = time.time()
    time_per_run = (end - start) / runs
    return time_per_run

def run():
    for res in [(512, 512), (1024, 1024), (1920, 1080)]:
        img = np.random.randint(0, 255, res, dtype=np.uint8)
        took = particle_velocimetry(img)
        print(f"Resolution {res}, took {took} seconds")

if __name__ == "__main__":
    run()