# Low cost (raspberry-based) particle velocimetry

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
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install libxvidcore-dev libx264-dev
```

https://singleboardbytes.com/647/install-opencv-raspberry-pi-4.htm

+ instalación de cosas de códecs de imágenes:
sudo apt install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev

+ cosas de vídeos
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install libxvidcore-dev libx264-dev

+ gui 
sudo apt install libfontconfig1-dev libcairo2-dev
sudo apt install libgdk-pixbuf2.0-dev libpango1.0-dev
sudo apt install libgtk2.0-dev libgtk-3-dev

+ operaciones matriciales
sudo apt install libatlas-base-dev gfortran

+ extra
sudo apt install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt install libqt5gui5 libqt5webkit5 libqt5test5 python3-pyqt5


--- 

# Docker
```bash
docker build -t lcpv .
docker run -it --rm lcpv [KWARGS]
```