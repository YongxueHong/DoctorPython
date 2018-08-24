import time


def func_timer(func):
    def timer():
        start = time.perf_counter()
        result = func(*args)
        elapsed = time.perf_counter() - start
        name = func.__name__
        arg_str = ','.join(repr(arg) for arg in args)
        print('[%0.8fs] %s(%s) -> %r' % (elapsed, name, arg_str, result))
        return result
    return timer

if __name__ == '__main__':
    pass