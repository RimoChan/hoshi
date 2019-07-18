import logging

import pdf2image
import cv2
import numpy as np

from .OCR引擎.缓存 import 缓存

poppler_path = None


@缓存
def 奇迹拆包(pdf文件名, dpi, 线程数):
    if poppler_path:
        图片组 = pdf2image.convert_from_path(pdf文件名, dpi=dpi, thread_count=线程数, poppler_path=poppler_path)
    else:
        图片组 = pdf2image.convert_from_path(pdf文件名, dpi=dpi, thread_count=线程数)
    图片组 = [np.array(图) for 图 in 图片组]
    压缩图片组 = [cv2.imencode('.png', 图, [cv2.IMWRITE_PNG_COMPRESSION, 6])[1] for 图 in 图片组]
    return 压缩图片组


def 拆包(pdf文件名, dpi, 线程数):
    压缩图片组 = 奇迹拆包(pdf文件名, dpi, 线程数)
    图片组 = [cv2.imdecode(图, cv2.IMREAD_COLOR) for 图 in 压缩图片组]
    return 图片组
