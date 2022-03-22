#!/usr/bin/python3

import queue # thread-safe queue

import numpy as np
import picamera
import time
import io

class Camera:
    def __init__(self,
                 max_frames:int=0,
                 resolution:tuple=(1920, 1080),
                 framerate:int = 24):
        # store the important values
        self.resolution=resolution
        self.framerate=framerate
        
        # create the camera object
        self.camera = picamera.PiCamera()
        self.camera.resolution = self.resolution
        self.camera.framerate = self.framerate

        # create the queu where the objects will be stored
        self.queue = queue.Queue(maxsize=max_frames)

    def start_recording(self, how_long:int=10):
        """
        How many seconds to record (it is an approximation)
        """
        self.camera.capture_sequence(self._buffer(how_long),
                                    "yuv",
                                    use_video_port=True,)
        self.camera.close()

    def get_frames(self):
        if self.queue.qsize >= 2:
            yield self.queue.get()
            self.queue.mutex.acquire()
            yield self.queue.queue[0]
            self.queue.mutex.release()
        else:
            time.sleep(0.01)
            self.get_frames()

    def _buffer(self, seconds:int=1) -> None:
        """
        Add the captured frames to the queue
        """
        buffers = seconds * 25 # (we get around 25fps)
        for _ in range(buffers):
            stream = io.BytesIO()
            yield stream
            stream.seek(0) # we got a new frame!
            # add the frame to the queue
            self.queue.put(
                np.frombuffer(
                    stream.getvalue(),
                    dtype=np.uint8,
                    count=np.prod(self.resolution)
                ).reshape(self.resolution[::-1])
            )
            
        


if __name__ == "__main__":
    camera = Camera()
    

    
