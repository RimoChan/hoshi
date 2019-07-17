import logging
import os

import tqdm
import pytesseract
import cv2
import numpy as np
from sklearn.cluster import KMeans

from . import 预处理
from . import 表格识别
from . import 输出doc
from . import 文字提取
from . import 旋转矫正
from . import 目录识别
from . import 多线程
from . import pdf拆包
from . import image_logging
from .OCR引擎.缓存 import 缓存



class 星:
    def __init__(self, pdf_path=None, 明度阈值=166):
        self.pdf文件名 = pdf_path
        self.明度阈值 = 明度阈值

    @缓存
    def 龙(self, dpi=600, 线程数=3):
        logging.debug('将pdf转为图片……')
        图片组 = pdf拆包.拆包(self.pdf文件名, dpi=dpi, 线程数=线程数)

        logging.debug('转word……')

        页组 = [None for _ in 图片组]
        函数组 = []
        for i, 图 in enumerate(图片组):
            def f(i=i, 图=图):
                页组[i] = self.单图片提取(图)
            函数组.append(f)
        多线程.同步进行(线程数, 函数组)
        return 页组

    def 行距提取(self, 行信息):
        行信息 = sorted(行信息, key=lambda i: i['top'])
        行距组 = [后['top'] - 前['top'] for 前, 后 in zip(行信息[:-1], 行信息[1:])]
        行高组 = [行['bottom'] - 行['top'] for 行 in 行信息]
        中位行高 = sorted(行高组)[len(行高组) // 2]
        有效行距组 = [i for i in 行距组 if i < 3 * 中位行高]
        return 有效行距组

    def 连接行距分析(self, 行距):
        estimator = KMeans(n_clusters=2)
        estimator.fit(np.array(行距).reshape(-1, 1))

        center = estimator.cluster_centers_
        小标签 = np.where(center == np.min(center))[0][0]

        label_pred = estimator.labels_

        小标签组 = [x for label, x in zip(label_pred, 行距) if label == 小标签]

        return max(小标签组)

    def 行连接(self, 行信息, 连接行距, c, 左右阈值=0.01):
        极左 = min([i['left'] for i in 行信息])
        极右 = max([i['right'] for i in 行信息])
        d = c * 左右阈值
        logging.debug({'连接行距': 连接行距, '极左': 极左, '极右': 极右})
        段落信息 = []
        for 当前行 in 行信息:
            if 当前行['left'] > 极左 + 5 * d and 当前行['right'] < 极右 - 5 * d \
                    and -5 * d < (当前行['right'] + 当前行['left']) - c < 5 * d:
                段落信息.append({
                    'top': 当前行['top'],
                    'right': 当前行['right'],
                    '行组': [当前行],
                    '样式': '居中',
                })
            else:
                当前行['缩进'] = 当前行['left'] - 极左
                if not 段落信息 \
                        or 当前行['top'] - 段落信息[-1]['行组'][-1]['top'] > 连接行距:
                    段落信息.append({
                        'top': 当前行['top'],
                        'right': 当前行['right'],
                        '行组': [当前行],
                        '样式': None,
                    })
                else:
                    最后一段 = 段落信息[-1]
                    if 当前行['left'] < 极左 + d and 最后一段['right'] > 极右 - d:
                        最后一段['行组'][-1]['内容'] += 当前行['内容']
                    else:
                        段落信息[-1]['行组'].append(当前行)
                    最后一段['right'] = 当前行['right']

        return 段落信息

    def 去除文字(self, 图, 行信息):
        alice = 图.copy()
        for d in 行信息:
            alice[d['top']:d['bottom'], d['left']:d['right']] = 255
        return alice

    def 取残(self, alice):
        imgray = cv2.cvtColor(alice, cv2.COLOR_BGR2GRAY)
        ret, imgray = cv2.threshold(imgray, 127, 255, 0)

        r, c = imgray.shape
        d = r // 50 * 2 + 1

        imgray = cv2.blur(imgray, (d, d), 0)
        ret, thresh = cv2.threshold(imgray, 253, 255, 1)
        
        image_logging.write('main', thresh=thresh)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        座标 = []
        for contour in contours:
            left, top = np.min(contour, axis=0).flatten()
            right, bottom = np.max(contour, axis=0).flatten()
            座标.append({
                'top': top,
                'bottom': bottom,
                'left': left,
                'right': right,
            })
        座标 = sorted(座标, key=lambda x: x['top'])
        return 座标

    def 单图片提取(self, img):
        r, c, _ = img.shape
        
        img = 预处理.预处理(img, 明度阈值=self.明度阈值)
        
        img = 旋转矫正.自动旋转矫正(img)

        净图, 表格组 = 表格识别.分割表格(img)

        净图, 省略号组 = 目录识别.目录识别(净图)
        行信息 = 文字提取.OCR(净图)
        目录信息, 行信息 = 目录识别.分离(省略号组, 行信息)
        有效行距组 = self.行距提取(行信息)
        if len(有效行距组) >= 2:
            连接行距 = self.连接行距分析(有效行距组)
        else:
            连接行距 = 0

        段落信息 = self.行连接(行信息, 连接行距, c)

        alice = self.去除文字(净图, 行信息 + 目录信息)

        图块组 = self.取残(alice)

        for 块 in 图块组:
            块['内容'] = img[块['top']:块['bottom'], 块['left']:块['right']]
            净图[块['top']:块['bottom'], 块['left']:块['right']] //= 2

        for d in 行信息:
            cv2.rectangle(净图, (d['left'], d['top']), (d['right'], d['bottom']), (0, 211, 211), 5)
        for d in 目录信息:
            cv2.rectangle(净图, (d['left'], d['top']), (d['right'], d['bottom']), (255, 66, 66), 5)
            
        image_logging.write('main', clean=净图)

        return {
            '目录信息': 目录信息,
            '段落信息': 段落信息,
            '表格组': 表格组,
            '图块组': 图块组
        }

