FROM python:3.9

LABEL version="0.1"
LABEL description="A Low Cost (Raspberry-based) Particle Velocimetry"
LABEL mantainer="Diego Valcarce Ríos"

# copy files to container
COPY . .

# update and install the requirements
RUN apt-get update
RUN apt-get install -y python3-opencv libatlas-base-dev
RUN pip install .

ENTRYPOINT ["python", "examples/run_from_terminal.py"]
