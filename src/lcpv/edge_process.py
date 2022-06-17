"""

"""
from utils.lcpv_template import LowCostParticleVelocimeter
from capture import camera

# other
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import multiprocessing as mp
import time
import tqdm

class LCPV(LowCostParticleVelocimeter):
    """
    Class that contains all the processing to run as edge computing in the raspberry pi.
    """
    NUM_CPU = mp.cpu_count()

    def __init__(self):
        """LCPV constructor, meant to create the common variables: the queue where Raspberry
        will write the captured frames and the results list that will store the processing
        results"""
        super().__init__()
        self.queue = mp.Queue()

    def start(self,
              resolution: tuple[int] = (1920, 1080),
              framerate: int = 24,
              seconds: int = 1,
              camera_params: dict = {},
              *args, **kwargs):
        """
        Runs the complete experiment, meant to be run within the raspberry and to make use of its camera. To run
        after capturing process has ended, see `src.py` # TODO: change filename

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

        # 1. Define the camera capture process and start it
        camera_capture_thread = Thread(
            target=camera.start_recording,
            args=(resolution, framerate, seconds, lambda frame: self.queue.put(frame))
        )
        camera_capture_thread.start()

        # 2. Wait a second so the cameras has already captured some frames (easier logic)
        time.sleep(1)  # it should be enough with 0.5 seconds

        # 3. Start the thread pool to process each pair of the frames
        futures = []
        with ThreadPoolExecutor(self.NUM_CPU - 1) as executor:  # (n-1) because the nth is capturing frames
            while self.queue.qsize() >= 2:  # while we have 2 frames to process (we process in pairs)
                frames = [self.queue.get() for _ in range(2)]
                # submit the job
                futures.append(executor.submit(self.process_frames, *frames, camera_params, *args, **kwargs))
                # we create a small delay so camera has enough time to capture more frames (easier logic) while
                # keeping (approximately) the performance, it only is really slower in the first two frames.
                time.sleep(1)

            # now let's ensure data is processed
            for future in tqdm.tqdm(futures):
                self.results.append(future.result())

        # we need to consume the remaining elements of the queue (if there are any) in order
        # to be able to close the `camera_capture_process`.
        while not self.queue.empty():
            self.queue.get()

        # wait till camera is closed
        camera_capture_thread.join()
