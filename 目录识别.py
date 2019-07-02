import os
import logging
import math

import tqdm
import cv2
import numpy as np
from scipy.signal import argrelextrema
import pytesseract

import util


def 检测省略号(img_bin, show_img):
    contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    点轮廓组 = []
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        if cv2.contourArea(hull) == 0:
            continue
        与凸包面积比 = cv2.contourArea(cnt) / cv2.contourArea(hull)
        x, y, w, h = cv2.boundingRect(cnt)
        边界矩形的宽高比 = w / h
        (x, y), r = cv2.minEnclosingCircle(cnt)
        与外接圆面积比 = cv2.contourArea(cnt) / (r * r * math.pi)
        if 3 / 4 < 边界矩形的宽高比 < 4 / 3 and 与凸包面积比 > 0.86 and 与外接圆面积比 > 0.6:
            点轮廓组.append(cnt)
            show_img = cv2.drawContours(show_img, [cnt], -1, (255, 45, 45), -1)

    img_b = np.zeros(img_bin.shape, dtype=np.uint8)
    for 点轮廓 in 点轮廓组:
        (x, y), radius = cv2.minEnclosingCircle(点轮廓)
        center = (int(x), int(y))
        img_b = cv2.circle(img_b, center, int(radius * 8), 255, -1)

    contours, hierarchy = cv2.findContours(img_b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    省略号组 = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w / h > 5:
            点数 = 0
            for 点轮廓 in 点轮廓组:
                (xx, yy), radius = cv2.minEnclosingCircle(点轮廓)
                if x < xx < x + w and y < yy < y + h:
                    点数 += 1
            点距 = w / (点数 + 1)
            范围 = {
                'top': int(y + h / 2 - 2 * 点距),
                'bottom': int(y + h / 2 + 2 * 点距),
                'left': int(x + 点距),
                'right': int(x + w - 点距),
            }
            省略号组.append(范围)
    cv2.imwrite('show.jpg', show_img)
    cv2.imwrite('b.jpg', img_b)
    return 省略号组


def 目录识别(ori_img, name=None):
    img = ori_img.copy()
    show_img = ori_img.copy()

    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    r, c = img.shape
    img_bin = img.copy()
    img_bin = 255 - util.局部二值化(img, r // 1024 * 2 + 1)

    省略号组 = 检测省略号(img_bin, show_img)
    img_noko = ori_img.copy()
    for d in 省略号组:
        img_noko[d['top']:d['bottom'], d['left']:d['right']] = 255

    cv2.imwrite('noko.jpg', img_noko)
    return img_noko, 省略号组


if __name__ == '__main__':
    img = cv2.imread('./data/m1.png')
    目录识别(img)
