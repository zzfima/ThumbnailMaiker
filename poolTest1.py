import multiprocessing
import time


def do_work(data):
    print('do_work ', multiprocessing.process.current_process().name)
    time.sleep(5)
    return data * 2


def init_func():
    print('Starts ', multiprocessing.process.current_process().name)


if __name__ == '__main__':
    pool_size = 2
    pool = multiprocessing.Pool(processes=pool_size, initializer=init_func())
    inputs = list(range(5))
    outputs = pool.map(do_work, inputs)
    print('outputs: ', outputs)

    pool.close()
    pool.join()
