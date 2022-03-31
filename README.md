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


---
# Installation

We present two methods to run this package: (1) via python scripting and (2) with docker. _Installation expects to use
raspbian._

## Python installation

Package is not yet available in the PyPi, but it can be installed from GitHub. Firstly, we need to install one 
dependency: 
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-opencv libatlas-base-dev git
```

To be able to use the camera module (CSI-2), we need to turn legacy mode on in the raspberry configuration: run 
`sudo raspi-config` and then select `Interface options > Legacy Camera > Enable`. Then reboot to make the changes
effective.

Once installed the dependencies, we can install the package (will install also the package python dependencies):

```bash
git clone git@github.com:valcarce01/lcpv.git
cd lcpv
pip install .
```

## Docker



---
# TO REMOVE:
----
Execution times in sequential (`piv.simple_piv`):

|                          | Raspberry model | Time (seconds) |
| -----------------------: | --------------- | -------------- |
|`np.uint8 (512x512)`[+]   | Model 3B+       | 1.44s          |
|`np.uint8 (1024x1024)`[+] | Model 3B+       | 5.61s          |
|`np.uint8 (1920x1080)`[+] | Model 3B+       | 10.75s         |

`dtypes` do not matter (tested on `np.bool_`, `np.float`, and time seems to be the same). But the main conclusion is that in order to run the code in the raspberry, we need to decrease the resolution as much as possible, so we can get the time from it. We have several ways to do so, but in our case, this is much easier, as we want to perform more operations in the image that are pixel-destractive; those include:
1. performing the lens distortion correction
2. wrapping the perspective
3. masking the rain (we will reduce the number of pixels "activated")




[+]: OpenPIV defualt settings

--- 
Run it on raspbian/ubuntu based

Dependencies
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-opencv libatlas-base-dev
```

Set up camera-legacy mode. 
1. `sudo raspi-config`
2. Interface options
3. legacy camera -> enable
4. reboot


--- 

# Docker
```bash
docker build -t lcpv .
docker run -it --rm lcpv [KWARGS]
```