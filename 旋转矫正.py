import os
import logging
import math

import tqdm
import cv2
import numpy as np
from scipy.signal import argrelextrema
import pytesseract

import util
from 缓存 import 缓存


def 距离(a, b):
    return int(((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5)


def 轮廓求旋转角(cnt):
    m = cv2.moments(cnt)
    xc = m['m10'] / m['m00']
    yc = m['m01'] / m['m00']
    a = m['m20'] / m['m00'] - xc**2
    b = m['m11'] / m['m00'] - xc * yc
    c = m['m02'] / m['m00'] - yc**2
    θ = cv2.fastAtan2(2 * b, a - c) / 2

    (x, y), (w, h), _ = cv2.minAreaRect(cnt)
    power = w / h if w > h else h / w

    return θ, power - 1


@缓存
def 检测旋转角(img, img_show):
    # 有小于0.04度的偏差
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    r, c = img.shape

    img_bin = img.copy()
    print(r // 1024 * 2 + 1)
    img_bin = 255 - util.局部二值化(img, r // 512 * 2 + 1)
    # cv2.imwrite('bin.jpg', img_bin)
    
    圆组 = []
    contours, hierarchy = cv2.findContours(img_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > (r / 2048)**2]  # 去屑

    for cnt in contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        圆组.append({'center': (x, y), 'r': radius, 'cnt': cnt})
    圆组 = sorted(圆组, key=lambda i: i['r'])
    平均大小 = int(sum([i['r'] for i in 圆组]) / len(圆组))

    img_b = np.zeros(img_bin.shape, dtype=np.uint8)
    for 圆 in 圆组:
        if 圆['r'] < 5 * 平均大小:
            img_b = cv2.drawContours(img_b, [圆['cnt']], -1, 255, -1)

    while True:
        img_b = util.dilate(img_b, 平均大小 // 2, 平均大小 // 2)
        contours2, hierarchy = cv2.findContours(img_b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours2) < len(contours) / 4:
            break

    所有角度 = []
    所有权 = []
    for cnt in contours2:
        角, 角强 = 轮廓求旋转角(cnt)
        if 角 > 90:
            角 -= 180
        if -10 < 角 < 10:
            权 = cv2.contourArea(cnt)**2
            所有角度.append(权 * 角强 * 角)
            所有权.append(权 * 角强)
            
    if len(所有角度)<10:
        logging.warning('没有足够的文字样本，检测不出旋转角')
        return 0
        
    cv2.imwrite('b.jpg', img_b)
    return sum(所有角度) / sum(所有权)


def 自动旋转矫正(ori_img):
    img = ori_img.copy()
    img_show = img.copy()
    c, r = img.shape[:2]

    旋轉角 = 检测旋转角(img, img_show)
    logging.debug(f'旋转角为{旋轉角}度。')
    if -0.1 < 旋轉角 < 0.1:
        return ori_img
    M = cv2.getRotationMatrix2D((r / 2, c / 2), 旋轉角, 1)
    dst = cv2.warpAffine(img, M, (r, c), borderValue=(255, 255, 255))
    return dst


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # img = cv2.imread(f'./data/o.png')
    # d = 自动旋转矫正(img)

    # for i in range(-3, 4):
    #     print('目标:', i)
    #     img = cv2.imread(f'./data/r{i}.png')
    #     d = 自动旋转矫正(img)
    #     cv2.imwrite(f'fr{i}.jpg', d)

    for i in ['']:
        # for i in os.listdir('./3/'):
        print('文件:', i)
        img = cv2.imread(f'./3/{i}')
        黑度阈值 = 166
        img[np.where(img > 黑度阈值)] = 255
        d = 自动旋转矫正(img)
        cv2.imwrite(f'./33/_{i}', d)
