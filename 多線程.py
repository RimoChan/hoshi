import threading
import time
import random


def 并发(并发线程数, 函数组):
    sem = threading.Semaphore(并发线程数)
    线程组 = []
    for f in 函数组:
        def _f():
            with sem:
                f()
        t = threading.Thread(target=_f)
        线程组.append(t)
        t.start()

    for t in 线程组:
        t.join()


if __name__ == '__main__':
    def go():
        print(threading.current_thread().name)
        time.sleep(1)

    并发(3, [go for i in range(10)])
        
    print('好了')
