import os
import hashlib
import cloudpickle as pickle

def 缓存(f):
    def 新f(*li, **d):
        md5 = hashlib.md5(pickle.dumps((li, d))).hexdigest()
        缓存文件名 = f'_cache/[{f.__name__}]{md5}.pkl'
        if os.path.isfile(缓存文件名):
            with open(缓存文件名, 'rb') as file:
                return pickle.load(file)
        else:
            缓存值 = f(*li, **d)
            with open(缓存文件名, 'wb') as file:
                pickle.dump(缓存值, file)
            return 缓存值
    return 新f



if __name__=='__main__':
    class a():
        @缓存
        def go(self, x):
            import time
            time.sleep(2)
            return x + 1
    print(a().go(1))
    print(a().go(1))
    print(a().go(1))
