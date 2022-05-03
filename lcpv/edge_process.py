"""

"""
from processing import lens_correction
from processing import filters
from capture import camera

# other
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import multiprocessing as mp
import time

class LCPV:
    """
    Class that contains all the processing to run as edge computing in the raspberry pi.
    """
    NUM_CPU = mp.cpu_count()

    def __init__(self):
        """LCPV constructor, meant to create the common variables: the queue where Raspberry
        will write the captured frames and the results list that will store the processing
        results"""
        self.queue = mp.Queue()
        self.results = []

    def start(self,
              resolution: tuple[int] = (1920, 1080),
              framerate: int = 24,
              seconds: int = 1,
              camera_params: dict = {},
              *args, **kwargs):
        """
        Runs the complete experiment, meant to be run within the raspberry and to make use of its camera. To run
        after capturing process has ended, see `lcpv.py` # TODO: change filename

        This implementation is a batteries installed, full parallel (threads, due to the sharing complexity between
        processes). The 'logic' is the following:

        1. Start the camera capture process, with only one thread. The captured frames will be stored into a
            thread safe queue (`multiprocessing.Queue`).
        2. With the remaining three threads, process the frames in the queue and run one, some or all of the following
            image processing:
            1.
        , parallel ready. It's threaded-based due to the memory sharing
        that it's needed. The code runs the following:

        1. Run the camera capture thread, adding the frames to a thread-safe Queue
        2. While the camera is running, process the results

        :param resolution: tuple[int]
            The camera resolution
        :param framerate: int
            The framerate of the camera capture. If the frequency is too much, it just will take more seconds, i.e. if
            50fps requested, but the camera only captures@24fps, it will capture for 2 seconds.
        :param seconds: int
            How long to capture the experiment.
        :param camera_params: dict.
            If lens correction desired, must include the following keys:
                - cameraMatrix
                - distCoeff
            If perspective correction desired, must include:
                - originalPoints
                - destinationPoints
            values of the dict *must* by np.ndarray objects. If none of the keys are provided, the preprocessing
            will simply be ignored.
        :param kwargs: OpenPIV args, minimum arguments required are:
            - window_size: int
            - search_area_size: int
            - overlap: int
            Refer to (OpenPIV documentation)[1] for further details.

        [1]: http://www.openpiv.net/openpiv-python/
        """
        assert ("window_size" in kwargs) and ("search_area_size" in kwargs) and ("overlap" in kwargs), \
            "Minimum args include window_size, search_area_size and overlap"
        # Definition of the camera thread to capture the data (-data producer-)
        camera_capture_thread = Thread(
            target=self.camera.start_recording,
            args=(resolution, framerate, seconds, self.queue_frames)
        )
        # start the camera thread
        camera_capture_thread.start()

        # we need to provide some time to warm up the camera
        time.sleep(1)  # more than enough, it should be enough with 0.5 seconds.

        # full multiprocessing object
        futures = []
        with ThreadPoolExecutor(self.NUM_CPU - 1) as executor:
            while self.queue.qsize() >= 2:
                frames = [self.queue.get() for _ in range(2)]
                futures.append(executor.submit(self.consume, *frames, camera_params, **kwargs))
                # enough time to ensure camera captures 2 new frames (does not slow down the processing time
                # as there are already jobs submitted and the computation time is well above 1 second).
                time.sleep(1)

            # now let's really consume the data
            for future in tqdm.tqdm(futures):
                self.results.append(future.result())

        # we need to consume the remaining elements of the queue (if there are any) in order
        # to be able to close the `camera_capture_process`. This can't occur more than twice.
        while not self.queue.empty():
            self.queue.get()

        # wait till camera is closed
        camera_capture_thread.join()









