import os
import logging
import argparse


logging.basicConfig(level=logging.DEBUG)


ag = argparse.ArgumentParser(description='使用hoshi来转换pdf文档。')
ag.add_argument('--pdf', type=str, required=True)
ag.add_argument('--docx', type=str, required=True)
ag.add_argument('--brightness_threshold', type=int, default=166)
ag.add_argument('--dpi', type=int, default=600)
ag.add_argument('--thread_count', type=int, default=3)

ag = ag.parse_args()

import hoshi_api

if os.path.isdir('./Tesseract-OCR'):
    logging.debug('使用内置tesseract。')
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"./Tesseract-OCR/tesseract.exe"

if os.path.isdir('./poppler-0.68.0'):
    logging.debug('使用内置poppler。')
    import hoshi本体.pdf拆包
    hoshi本体.pdf拆包.poppler_path = './poppler-0.68.0/bin'

hoshi_api.pdf_to_word(ag.pdf, ag.docx, ag.brightness_threshold, ag.dpi, ag.thread_count)
