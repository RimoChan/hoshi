import os
import logging

import tqdm
import cv2
import numpy as np
from scipy.signal import argrelextrema
import pytesseract

from 缓存 import 缓存
import util
from util import erode, dilate


class 表格:
    def __init__(self, 尺寸, 原位置):
        self.尺寸 = tuple(尺寸)
        self.原位置 = 原位置
        x, y = 尺寸
        self.格内容 = [[None for y in range(y)] for x in range(x)]
        self.格连接 = [[(False, False) for y in range(y)] for x in range(x)]

    def __repr__(self):
        s = '表格:\n'
        for 行 in self.格内容:
            for 格 in 行:
                s += 格.__str__() + (15 - len(格.__str__())) * ' '
            s += '\n'
        return s

    def 格范围(self, x, y):
        if True in self.格连接[x][y]:
            return None

        while True:
            x += 1
            if x >= len(self.格内容) or not self.格连接[x][y][0]:
                x -= 1
                break
        while True:
            y += 1
            if y >= len(self.格内容[0]) or not self.格连接[x][y][1]:
                y -= 1
                break
        return x, y


def 提取表格线(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    r, c = img.shape
    
    img_bin = util.局部二值化(img, r // 1024 * 2 + 1)
    # cv2.imwrite('bb.jpg', img_bin)
    img_bin = erode(img_bin, r // 1000, r // 1000)
    img_x = erode(dilate(img_bin, 1, r // 64), 1, r // 64)
    img_y = erode(dilate(img_bin, r // 64, 1), r // 64, 1)

    img_x = 255 - img_x
    img_y = 255 - img_y

    img_table = np.maximum(img_x, img_y)
    contours = util.屑检测(img_table, (r/16)**2)
    for cnt in contours:
        img_x = cv2.drawContours(img_x, [cnt], -1, (0), -1)
        img_y = cv2.drawContours(img_y, [cnt], -1, (0), -1)
        img_table = cv2.drawContours(img_table, [cnt], -1, (0), -1)

    return img_x, img_y, img_table


def 定极线(img, axis):
    t = np.sum(img, axis=axis).astype(np.float64)
    l = len(t)

    满线能量 = img.shape[axis] * 255
    t[np.where(t < 满线能量 // 32)] = 0

    t[np.where(t > 0)] += np.random.normal(1, 1, len(t[np.where(t > 0)]))

    t = np.reshape(t, (l, 1))
    t = cv2.GaussianBlur(t, (1, l // 512 * 2 + 1), 0)
    t = t.flatten()
    return argrelextrema(t, np.greater)[0]


def 划定(img, img_x, img_y, lx, ly):
    d = {}
    r, c = img_x.shape
    img_x = dilate(img_x, r // 256, r // 256)
    img_y = dilate(img_y, r // 256, r // 256)
    llx = [0, *lx]
    lly = [0, *ly]

    for px, x in zip(llx[:-1], llx[1:]):
        for py, y in zip(lly[:-1], lly[1:]):
            d[x, y] = [False, False]
            if img_y[px:x, y].mean() > 128:
                d[x, y][0] = True
            if img_x[x, py:y].mean() > 128:
                d[x, y][1] = True

    for px, x in zip(llx[:-1], llx[1:]):
        for py, y in zip(lly[:-1], lly[1:]):
            if d[x, y][0]:
                cv2.rectangle(img, (y, px), (y, x), (255, 0, 0), 10)
            if d[x, y][1]:
                cv2.rectangle(img, (py, x), (y, x), (255, 0, 0), 10)

    单闭合线 = []
    for i, x in enumerate(lx):
        q = w = None
        fw = None
        for j, y in enumerate(ly):
            if d[x, y][1]:
                w = j
                if q is None:
                    q = j
            if not d[x, y][1] and q is not None:
                fw = j - 1
        if q is not None and (fw is None or fw == w):
            单闭合线.append((q, w))
        else:
            单闭合线.append(None)
    logging.debug(单闭合线)
    表格块组 = []
    当前检测 = None
    for i, t in enumerate(单闭合线 + [None]):
        if 当前检测 is None and t:
            当前检测 = i
            q, w = t
        elif 当前检测 is None:
            continue
        else:
            if i != len(lx) and d[lx[i], ly[q - 1]][0] and d[lx[i], ly[w]][0]:
                None
            else:
                if 单闭合线[i - 1] == (q, w):
                    if 当前检测 != i - 1:
                        表格块组.append({
                            'top': 当前检测,
                            'bottom': i - 1,
                            'left': q - 1,
                            'right': w,
                        })
                        表 = 表格块组[-1]
                        roi = img[lx[表['top']]:lx[表['bottom']], ly[表['left']]:ly[表['right']]]
                        roi //= 5
                        roi *= 4
                        roi[:, :, 2] = 255
                    当前检测 = None
                    if t:
                        当前检测 = i
                        q, w = t
    线信息 = d
    return 表格块组, 线信息


@缓存
def 最终提取(表格块组, d, ori_img, lx, ly):
    r, c = ori_img.shape[:2]
    表格组 = []
    for 表格块 in 表格块组:
        该表格 = 表格([表格块['bottom'] - 表格块['top'], 表格块['right'] - 表格块['left']],
                 {
            'top': lx[表格块['top']],
            'bottom': lx[表格块['bottom']],
            'left': ly[表格块['left']],
            'right': ly[表格块['right']],
        }
        )
        表格组.append(该表格)
        for x in range(表格块['bottom'] - 表格块['top']):
            for y in range(表格块['right'] - 表格块['left']):
                ox = x + 表格块['top']
                oy = y + 表格块['left']
                该表格.格连接[x][y]
                d[lx[ox], ly[oy + 1]][1]
                d[lx[ox + 1], ly[oy]][0]
                该表格.格连接[x][y] = not d[lx[ox], ly[oy + 1]][1], not d[lx[ox + 1], ly[oy]][0]

        for x in range(表格块['bottom'] - 表格块['top']):
            for y in range(表格块['right'] - 表格块['left']):
                if 该表格.格范围(x, y) is not None:
                    ox = x + 表格块['top']
                    oy = y + 表格块['left']
                    xx, yy = 该表格.格范围(x, y)
                    oxx = xx + 表格块['top']
                    oyy = yy + 表格块['left']

                    dt = r // 512
                    切图 = ori_img[lx[ox] + dt:lx[oxx + 1] - dt, ly[oy] + dt:ly[oyy + 1] - dt]
                    if 0 in 切图.shape or 切图.mean() > 254:
                        该表格.格内容[x][y] = ''
                    else:
                        文字 = pytesseract.image_to_string(切图, lang='chi_sim+eng', config='--psm 7 --oem 1')
                        # 文字 = pytesseract.image_to_data(切图, lang='chi_sim+eng', config='--psm 7 --oem 1')
                        该表格.格内容[x][y] = 文字

    return 表格组


def 分割表格(ori_img, name=None):
    img = ori_img.copy()
    r, c = img.shape[:2]

    img_x, img_y, img_table = 提取表格线(img)

    lx = 定极线(img_x, axis=1)
    ly = 定极线(img_y, axis=0)

    for x in ly:
        cv2.rectangle(img, (x, 0), (x, r), (0, 255, 0), 3)
    for y in lx:
        cv2.rectangle(img, (0, y), (c, y), (0, 255, 0), 3)

    表格块组, 线信息 = 划定(img, img_x, img_y, lx, ly)

    if name:
        cv2.imwrite(f'./temp/{name}_a.png', img)
        # cv2.imwrite(f'./temp/{name}_noko.png', img_noko)
        # cv2.imwrite(f'./temp/{name}_x.png', img_x)
        # cv2.imwrite(f'./temp/{name}_y.png', img_y)
        cv2.imwrite(f'./temp/{name}_t.png', img_table)

    # 表格组 = 最终提取(表格块组, 线信息, ori_img, lx, ly)
    表格组 = []

    img_noko = ori_img.copy()
    for 表格 in 表格组:
        d = r // 512
        位 = 表格.原位置
        img_noko[位['top'] - d:位['bottom'] + d, 位['left'] - d:位['right'] + d] = 255

    return img_noko, 表格组


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # for i in ['0.png']:
    for i in tqdm.tqdm(os.listdir('./tb'), ncols=55):
        print(i)
        img = cv2.imread(f'./tb/{i}')
        黑度阈值 = 166
        img[np.where(img > 黑度阈值)] = 255

        import 旋转矫正
        img = 旋转矫正.自动旋转矫正(img)
        img_noko, 表格组 = 分割表格(img, i)
        print(表格组)
