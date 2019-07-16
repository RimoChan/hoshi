import threading
import logging

import cv2

f_string = None


def write(step, _warned=[0], **d):
    if f_string is None:
        if not _warned[0]:
            _warned[0] = 1
            logging.warning('image_logging f_string not set.')
        return
    for key, img in d.items():
        f = eval(f"f'{f_string}'")
        cv2.imwrite(f'./image_logging/{f}', img)


# if __name__ == '__main__':
#     f_string = '{key}.png'
#     write(a=1)
#     write(a=1)
#     write(a=1)
