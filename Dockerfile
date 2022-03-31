FROM python:3.9

LABEL version="0.1"
LABEL description="A Low Cost Particle Velocimetry"
LABEL mantainer="Multiple"

# TODO: add all the variables and theck if they run
# enviroment variables to run on
ENV resolution (1920, 1080)
ENV framerate 24

# install all the c-dependencies to run OpenCV
RUN apt-get update && apt-get install -y \
    python3-opencv \
    libatlas-base-dev

COPY . .
RUN pip install .


ENTRYPOINT ["python", "./lcpv.py"]

# TODO: add the run command to execute the code

