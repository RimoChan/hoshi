import logging
import os

import tqdm
import pytesseract

from 缓存 import 缓存


@缓存
def ocr(img, 单行=False):
    if 单行:
        ocr信息 = pytesseract.image_to_data(img, lang='chi_sim+eng', config='--psm 7 --oem 1', output_type='dict')
    else:
        ocr信息 = pytesseract.image_to_data(img, lang='chi_sim', output_type='dict')
    return ocr信息


def 行切(ocr信息):
    a = []
    for n in range(len(ocr信息['level'])):
        a.append({})
        now = a[-1]
        for i, x in ocr信息.items():
            now[i] = x[n]
        now['h'] = (now['block_num'], now['par_num'], now['line_num'])

    dv = {}
    for i in a:
        if i['level'] <= 3:
            None
        if i['level'] == 4:
            dv[i['h']] = {
                'left': i['left'],
                'top': i['top'],
                'right': i['left'] + i['width'],
                'bottom': i['top'] + i['height'],
                '内容': [],
            }
        if i['level'] == 5:
            dv[i['h']]['内容'].append((i['text'], str(i['conf'])))

    行信息 = []
    for _, x in dv.items():
        文字 = ''.join([i for i, _ in x['内容']])
        if any([j != ' ' for j in 文字]):
            行信息.append(x)
    行信息 = sorted(行信息, key=lambda i: i['top'])
    return 行合并(行信息)


def 行合并(行信息):
    合并行信息 = []
    for 行 in 行信息:
        if not 合并行信息:
            合并行信息.append(行)
        elif 行['top'] < 合并行信息[-1]['bottom']:
            if 行['right'] > 合并行信息[-1]['right']:
                合并行信息[-1]['内容'] = 合并行信息[-1]['内容'] + 行['内容']
                合并行信息[-1]['right'] = 行['right']
            elif 行['left'] < 合并行信息[-1]['left']:
                合并行信息[-1]['内容'] = 行['内容'] + 合并行信息[-1]['内容']
                合并行信息[-1]['left'] = 行['left']
        else:
            合并行信息.append(行)
    return 合并行信息


def 组句(行内容):
    s = ''
    for i, _ in 行内容:
        if s and ('A' <= s[-1] <= 'z' or 'A' <= i[0] <= 'z'):
            s += ' '
        s += i
    return s


def 单行ocr(img):
    ocr信息 = ocr(img, 单行=True)
    行信息 = 行切(ocr信息)
    if len(行信息) > 1:
        logging.warning('单行ocr超过一行？？？')
    if 行信息:
        return 组句(行信息[0]['内容'])
    else:
        return ''
