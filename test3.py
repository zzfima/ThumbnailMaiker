import threading
import time

lock = threading.RLock()


def fnc1():
    print('before acquire lock', threading.currentThread().ident)
    if lock.acquire(True):
        print('inside of lock', threading.currentThread().ident)
        time.sleep(5)
        lock.release()
        print('lock released', threading.currentThread().ident)
    else:
        print('can not acquire lock', threading.currentThread().ident)


th1 = threading.Thread(target=fnc1)
th2 = threading.Thread(target=fnc1)

th1.start()
th2.start()

th1.join()
print('th1 id alive: ', th1.is_alive())
print('th2 id alive: ', th2.is_alive())
th2.join()
