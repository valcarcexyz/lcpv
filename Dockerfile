FROM python:3.9

LABEL version="0.1"
LABEL description="A Low Cost Particle Velocimetry"
LABEL mantainer="Multiple"

# install all the c-dependencies to run OpenCV
RUN apt-get update && apt-get install -y \
    python3-opencv \
    libatlas-base-dev

COPY . .
RUN pip install .

ENTRYPOINT ["python", "-c", \
    "import lcpv.lcpv as lcpv; \
    import argparse; \
    import sys; \
    parser = argparse.ArgumentParser(); \
    parser.add_argument(\"--resolution\", nargs=2, type=int); \
    parser.add_argument(\"--framerate\", type=int); \
    parser.add_argument(\"--correct_distortion\", type=bool); \
    parser.add_argument(\"--camera\", type=str); \
    parser.add_argument(\"--window_size\", type=int); \
    parser.add_argument(\"--search_area_size\", type=int); \
    parser.add_argument(\"--overlap\", type=int); \
    parser.add_argument(\"--seconds\", type=int); \
    args = dict(parser.parse_args()._get_kwargs()); \
    if \"seconds\" not in args: \
        print(\"At least, you should indicate the --seconds flags\"); \
        sys.exit(0); \
    if \"camera\" in args: \
        args[\"camera\"] = eval(args[\"camera\"]); # (read the file) \
    l = LCPV(**args); \
    output = l.start(seconds=args[\"seconds\"]); "]

# TODO: add the run command to execute the code

