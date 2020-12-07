import threading
import time

sem = threading.Semaphore(2)


def fnc1():
    print('before acquire lock', threading.currentThread().ident)
    sem.acquire(True)
    print('inside of lock', threading.currentThread().ident)
    time.sleep(5)
    sem.release()
    print('lock released', threading.currentThread().ident)


th1 = threading.Thread(target=fnc1)
th2 = threading.Thread(target=fnc1)
th3 = threading.Thread(target=fnc1)
th4 = threading.Thread(target=fnc1)

th1.start()
th2.start()
th3.start()
th4.start()

th1.join()
th2.join()
th3.join()
th4.join()
