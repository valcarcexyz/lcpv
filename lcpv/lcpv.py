from concurrent.futures import ProcessPoolExecutor
from .camera import Camera

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
