from lcpv import VideoProcessor

FILENAME = "data/video.h264"


def main():
    vp = VideoProcessor()
    vp.start(filename=FILENAME, camera_params={}, window_size=32, search_area_size=32, overlap=16)


if __name__ == "__main__":
    main()
