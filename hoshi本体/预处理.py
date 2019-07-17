import logging

import numpy as np
import cv2

from . import util
from . import image_logging


def 预处理(img, 明度阈值):
    r, c = img.shape[:2]
    show_img = img.copy()
    img[np.where(img > 明度阈值)] = 255
    img_bin = util.局部二值化(img[:, :, 0], r // 1024 * 2 + 1)
    
    屑 = util.屑检测(255 - img_bin, 面积阈值=r * c // 10**6)

    test_img = cv2.drawContours(img.copy(), 屑, -1, (255, 255, 255), -1)
    test_img = cv2.blur(test_img, (r // 256, r // 256), 0)

    坏屑 = []
    for cnt in 屑:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        x, y = int(x), int(y)
        if test_img[y, x].mean() > 253:
            坏屑.append(cnt)
            cv2.circle(show_img, (x, y), int(radius * 4) + 10, (255, 0, 0), 2)

    img = cv2.drawContours(img, 坏屑, -1, (255, 255, 255), -1)

    image_logging.write('s', s=show_img)

    return img
