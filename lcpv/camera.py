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
        self.queue[0]

    def start_recording(self, how_long:int=10):
        """
        How many seconds to record (it is an approximation)
        """
        for _ in range(how_long):
            self.camera.capture(
                self._buffer(), "yuv", use_video_port=True,
            )

    def get_frames(self):
        if self.queue.qsize >= 2:
            yield self.queue.get()
            self.queue.mutex.acquire()
            yield self.queue.queue[0]
            self.queue.mutex.release()
        else:
            time.sleep(0.01)
            self.get_frames()

    def _buffer(self) -> None:
        """
        Add 3 frames to the queue TODO: change why 10?
        """
        for _ in range(3):
            stream = io.BytesIO()
            yield stream
            # new frame:
            stream.seek(0)
            # add the frame to the queue
            self.queue.put(
                np.frombuffer(
                    stream.getvalue(),
                    dtype=np.uint8,
                    count=self.resolution
                ).reshape(self.resolution[::-1])
            )
            
        


if __name__ == "__main__":
    camera = Camera()
    

    
