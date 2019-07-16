import logging

import cv2

import hoshi本体.hoshi
import hoshi本体.表格识别
import hoshi本体.输出doc
import hoshi本体.旋转矫正
from hoshi本体 import image_logging

logging.basicConfig(level=logging.DEBUG)


def pdf_to_word(pdf_file_name, word_file_name, brightness_threshold=166, dpi=600, thread_count=3):
    image_logging.f_string = '{threading.current_thread().getName()}_{step}_{key}.png'
    页组 = hoshi本体.hoshi.星(pdf_file_name, brightness_threshold).龙(dpi=dpi, 线程数=thread_count)
    hoshi本体.输出doc.输出(word_file_name, 页组)


def image_to_word(image_file_name, word_file_name, brightness_threshold=166):
    image_logging.f_string = '{step}_{key}.png'
    img = cv2.imread(image_file_name)
    页 = hoshi本体.hoshi.星(None, brightness_threshold).单图片提取(img)
    hoshi本体.输出doc.输出(word_file_name, [页])


def extract_form_image(image_file_name):
    image_logging.f_string = '{step}_{key}.png'
    img = cv2.imread(image_file_name)
    表格块组, lx, ly, _ = hoshi本体.表格识别.位置判定(img)
    表格位置组 = [(slice(lx[格块['top']], lx[格块['bottom']]), slice(ly[格块['left']], ly[格块['right']]))
             for 格块 in 表格块组]
    图片组 = [img[位置] for 位置 in 表格位置组]
    # for i, img in enumerate(图片组):
    #     cv2.imwrite(f'{i}.jpg', img)
    return 表格位置组, 图片组


def extract_form(image_file_name):
    image_logging.f_string = '{step}_{key}.png'
    img = cv2.imread(image_file_name)
    img_noko, 表格组 = hoshi本体.表格识别.分割表格(img, 'nya')
    return 表格组


def image_rotation_correction(image_file_name):
    image_logging.f_string = '{step}_{key}.png'
    img = cv2.imread(image_file_name)
    d = hoshi本体.旋转矫正.自动旋转矫正(img)
    return d


if __name__ == '__main__':
    pdf_to_word('.\hoshi本体\data\SYT 6662.5-2014.pdf', 'final.docx', thread_count=2)
    # pdf_to_word('.\hoshi本体\data\librian.pdf', 'final.docx', 255, thread_count=2)
    # image_to_word('0.png', 'final.docx')
    
    # print(extract_form('./2.png'))
    # cv2.imwrite('r0.png', image_rotation_correction('./r-3.png'))
