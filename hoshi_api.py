import logging

import cv2

import hoshi本体.hoshi
import hoshi本体.表格识别
import hoshi本体.输出doc


logging.basicConfig(level=logging.DEBUG)


def pdf_to_word(pdf_file_name, word_file_name, brightness_threshold=166, dpi=600, thread_count=3):
    页组 = hoshi本体.hoshi.星(pdf_file_name, brightness_threshold).龙(dpi=dpi, 线程数=thread_count)
    hoshi本体.输出doc.输出(word_file_name, 页组)


def extract_form_image(image_file_name):
    img = cv2.imread(image_file_name)
    表格块组, lx, ly, _ = hoshi本体.表格识别.位置判定(img)
    表格位置组 = [(slice(lx[格块['top']], lx[格块['bottom']]), slice(ly[格块['left']], ly[格块['right']]))
             for 格块 in 表格块组]
    图片组 = [img[位置] for 位置 in 表格位置组]
    # for i, img in enumerate(图片组):
    #     cv2.imwrite(f'{i}.jpg', img)
    return 表格位置组, 图片组


if __name__=='__main__':
    pdf_to_word('.\hoshi本体\data\SYT 6662.5-2014.pdf', 'final.docx', thread_count=2)
    # pdf_to_word('.\hoshi本体\data\librian.pdf', 'final.docx', 255, thread_count=2)
