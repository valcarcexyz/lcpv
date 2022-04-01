# Low cost (raspberry-based) particle velocimetry

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

This package provides a layer abstraction between both [Raspberry PiCamera library](https://github.com/waveform80/picamera) 
and [OpenPIV](https://github.com/OpenPIV/openpiv-python) with the 
main goal of running as fast as possible within a Raspberry Pi 4. This package is meant to process the images
as follows:

1. Capture as many frames as wanted (as they can be held in memory), using the raspberry video port 
(the best performance in capturing speed and high resolution frames). It uses a thread-safe queue to store all the 
frames captured (as bytes streams -no need to write to disk-, converted to numpy arrays). While the images are being 
captured, it can compute one (or more) of the following preprocessing tasks:
   1. Correct the lens distortion introduced (see `lens_correction.py`).
   2. Correct the image perspective (TODO).
   3. Mask the image using computer vision technics (with morphological operations -see `unsharp_masking.py`).
    
Running this steps is highly encouraged as they reduce the image size, thus decreasing the RAM usage and in the next 
steps, decreasing the processing power needed to compute the particle velocimetry in each of the frames.

2. If desired, it can also write to disk the images.

3. Once captured, it starts the OpenPIV process, in parallel with as many cores as are available in the Raspberry.

4. Finally, it computes the median of each velocimetry vector, as it is very sensitive to outliers. Returns the tuple
   (x, y, u, v), being: (x, y) the points where velocimetry vector starts and (u, v) the velocimetry itself.

---
# Installation

We present two methods to run this package: (1) via python scripting and (2) with docker. _Installation expects to use
raspbian._ Before starting, we need to enable legacy mode of the Raspberry: run 
`sudo raspi-config` and then select `Interface options > Legacy Camera > Enable`. Then reboot to make the changes
effective.

## Python installation

Package is not yet available in the PyPi, but it can be installed from GitHub. Firstly, we need to install one 
dependency: 
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-opencv libatlas-base-dev git
```

Once installed the dependencies, we can install the package (will install also the package python dependencies):

```bash
git clone git@github.com:valcarce01/lcpv.git
cd lcpv
pip install .
```

### Usage example

```python
import lcpv.lcpv as lcpv
l = lcpv.LCPV(resolution=(1920, 1080), framerate=24,
              correct_distortion=True, camera=lcpv.Corrector.HQ_CAMERA,
              write=False,
              mask=lambda x: lcpv.opening_filter(x, kernel_size=7, threshold=220),
              window_size=32, overlap=16, search_area_size=32)
output = l.start(seconds=10)
if output: # just in case it does not run properly and return None.
    x, y, u, v = output
```

## Docker

# TODO: add the arguments

Install docker:
```bash
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker ${USER}
sudo systemctl --now enable docker
```

And the run the container:

```bash
git clone git@github.com:valcarce01/lcpv.git
docker build -t lcpv .
docker run -it -rm --name LCPV lcpv [KWARGS]
```