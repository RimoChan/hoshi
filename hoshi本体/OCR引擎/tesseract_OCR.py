import pytesseract

from .缓存 import 缓存


class tesseract_OCR:
    def 行切(self, ocr信息):
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
        return self.行合并(行信息)

    def 行合并(self, 行信息):
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
        for 行 in 合并行信息:
            行['内容'] = self.组句(行['内容'])
        return 合并行信息

    def 组句(self, 行内容):
        s = ''
        for i, _ in 行内容:
            if s and ('A' <= s[-1] <= 'z' or 'A' <= i[0] <= 'z'):
                s += ' '
            s += i
        return s

    @缓存
    def _全页识别(self, 图):
        return pytesseract.image_to_data(图, lang='chi_sim', output_type='dict')

    @缓存
    def _单行识别(self, 图):
        return pytesseract.image_to_data(图, lang='chi_sim+eng', config='--psm 7 --oem 1', output_type='dict')

    def 全页识别(self, 图):
        原始ocr信息 = self._全页识别(图)
        结果 = self.行切(原始ocr信息)
        return 结果

    def 单行识别(self, 图):
        原始ocr信息 = self._单行识别(图)
        行信息 = self.行切(原始ocr信息)
        if len(行信息) > 1:
            logging.warning('单行ocr超过一行？？？')
        if 行信息:
            return 行信息[0]['内容']
        else:
            return ''


if __name__ == '__main__':
    import cv2
    图 = cv2.imread('f.png')
    result = tesseract_OCR().全页识别(图)
    print(result)
    result = tesseract_OCR().单行识别(图)
    print(result)
    cv2.imwrite('_f.png', 图)
