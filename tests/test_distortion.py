import sys
sys.path.append("..")
from lcpv.lens_correction import Corrector
import matplotlib.pyplot as plt
import numpy as np
import cv2
import time

def run(original_image:np.ndarray):
    corrector = Corrector()
    corrected_image = corrector.correct(original_image, corrector.HQ_CAMERA)
    
    fig, axs = plt.subplots(2, 1)
    axs[0].imshow(original_image, cmap = "gray")
    axs[0].axis("off")
    axs[0].set_title("Original image")
    axs[1].imshow(corrected_image, cmap = "gray")
    axs[1].axis("off")
    axs[1].set_title("Corrected image")
    plt.show()


if __name__ == "__main__":
    img = cv2.imread("../data/original_image.bmp", 0)
    # plt.imshow(img, cmap="gray")
    # plt.show()
    run(img)