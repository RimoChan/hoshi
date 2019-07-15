import logging
import os


def 加载引擎(引擎):
    if 引擎 == 'tesseract':
        from .OCR引擎 import tesseract_OCR
        return tesseract_OCR.tesseract_OCR()
    elif 引擎 == 'baidu':
        from .OCR引擎 import 百度OCR
        return 百度OCR.百度OCR()


def OCR(图, 引擎='tesseract'):
    引擎 = 加载引擎(引擎)
    return 引擎.全页识别(图)


def 单行OCR(图, 引擎='tesseract'):
    引擎 = 加载引擎(引擎)
    return 引擎.单行识别(图)
