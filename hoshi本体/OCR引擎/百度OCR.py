import logging

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
        return 新信息

    def 单行识别(self, 图):
        原始ocr信息 = self._单行识别(图)
        words_result = 原始ocr信息['words_result']
        if len(words_result) > 1:
            logging.warning('单行ocr超过一行？？？')
        if words_result:
            return words_result[0]
        else:
            return ''


if __name__ == '__main__':
    import cv2
    图 = cv2.imread('f.png')
    result = 百度OCR().全页识别(图)
    print(result)
    result = 百度OCR().单行识别(图)
    print(result)
    cv2.imwrite('_f.png', 图)
