import time


def get_run_time(func):
    """
    打印方法的耗时
    """

    def call_func(*args, **kwargs):
        begin_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - begin_time
        print('function {}, args={}, kwargs={}, time = {}'.format(func.__name__, args, kwargs, run_time))
        return ret

    return call_func


def singleton(cls):
    """
    单例装饰器

    """
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner
