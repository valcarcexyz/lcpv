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