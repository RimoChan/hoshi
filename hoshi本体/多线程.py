import threading
import time
import random

import tqdm


def 同步进行(并发线程数, 函数组, 进度条=True):
    sem = threading.Semaphore(并发线程数)
    线程组 = []
    for f in 函数组:
        def _f(f=f):
            with sem:
                f()
        t = threading.Thread(target=_f)
        线程组.append(t)
    for t in 线程组:
        t.start()
    for t in tqdm.tqdm(线程组, ncols=50) if 进度条 else 线程组:
        t.join()


if __name__ == '__main__':
    def go():
        print(threading.current_thread().name)
        time.sleep(1)

    同步进行(3, [go for i in range(14)])
        
    print('好了')
