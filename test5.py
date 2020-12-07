import threading
import time

event = threading.Event()


def fnc1():
    global event
    print('wait for set event', threading.currentThread().ident, ', event state: ', event.is_set())
    event.wait()
    print('got event', threading.currentThread().ident, ', event state: ', event.is_set())
    event.clear()


def fnc2():
    global event
    print('going to sleep', threading.currentThread().ident, ', event state: ', event.is_set())
    time.sleep(5)
    print('going to wake the event', threading.currentThread().ident, ', event state: ', event.is_set())
    event.set()


threadMaster = threading.Thread(target=fnc1)
threadSlave = threading.Thread(target=fnc2)

threadSlave.start()
threadMaster.start()

threadSlave.join()
threadMaster.join()

print('Main finished. event state: ', event.is_set())
