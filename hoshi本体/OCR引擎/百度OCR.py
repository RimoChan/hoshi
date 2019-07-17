import logging

import cv2
import numpy as np
from aip import AipOcr

from .缓存 import 缓存


class 百度OCR:
    APP_ID = '10379743'
    API_KEY = 'QGGvDG2yYiVFvujo6rlX4SvD'
    SECRET_KEY = 'PcEAUvFO0z0TyiCdhwrbG97iVBdyb3Pk'
    aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    @缓存
    def _全页识别(self, 图):
        图数据 = cv2.imencode('.png', 图)[1]
        result = self.aipOcr.accurate(图数据, {
            'language_type': 'CHN',
        })
        return result

    @缓存
    def _单行识别(self, 图):
        图数据 = cv2.imencode('.png', 图)[1]
        result = self.aipOcr.basicAccurate(图数据, {
            'language_type': 'CHN',
        })
        return result

    def 收缩(self, 图, 行信息):
        for i in 行信息:
            roi = img[i['top']:i['bottom'], i['left']:i['right'], 0]
            有效点x = np.where(roi.mean(axis=1) < 254.9)[0]
            有效点y = np.where(roi.mean(axis=0) < 254.9)[0]
            i['top'], i['bottom'] = i['top'] + 有效点x.min(), i['top'] + 有效点x.max() + 1
            i['left'], i['right'] = i['left'] + 有效点y.min(), i['left'] + 有效点y.max() + 1
        return 行信息

    def 全页识别(self, 图):
        原始ocr信息 = self._全页识别(图)
        words_result = 原始ocr信息['words_result']
        新信息 = []
        for i in words_result:
            新信息.append({
                'left': i['location']['left'],
                'top': i['location']['top'],
                'right': i['location']['left'] + i['location']['width'],
                'bottom': i['location']['top'] + i['location']['height'],
                '内容': i['words']
            })
        return self.收缩(图, 新信息)

    def 单行识别(self, 图):
        原始ocr信息 = self._单行识别(图)
        words_result = 原始ocr信息['words_result']
        if len(words_result) > 1:
            logging.warning('单行ocr超过一行？？？')
        if words_result:
            return words_result[0]
        else:
            return ''

if __name__=='__main__':
    img = cv2.imread('2.png')
    
    a = 百度OCR().全页识别(img)
    
    for i in a:
        img[i['top']:i['bottom'], i['left']:i['right']] //= 2
        print(i['内容'])
    
    cv2.imwrite('baidu_2.png', img)
