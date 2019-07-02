import numpy as np
import cv2

def 局部二值化(img, d):
    img_bin = img.copy()
    t = cv2.blur(img_bin, (d, d), 0)
    img_bin[np.where(img_bin > t - 5)] = 255
    img_bin[np.where(img_bin <= t - 5)] = 0
    return img_bin
    
def erode(img, x, y):
    kernel = np.ones((int(x), int(y)), np.uint8)
    return cv2.erode(img, kernel)


def dilate(img, x, y):
    kernel = np.ones((int(x), int(y)), np.uint8)
    return cv2.dilate(img, kernel)
