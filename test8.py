import threading
import time
from datetime import datetime
from queue import Queue

queue = Queue(maxsize=10)


def producer(q: Queue):
    for i in range(5):
        time.sleep(5)
        print('put food ', datetime.now().time())
        q.put(i)


def consumer(q: Queue):
    while True:
        q.get()
        time.sleep(0.5)
        q.task_done()
        print('get food ', datetime.now().time())


thread_consumer = threading.Thread(target=consumer, args=(queue,))
thread_producer = threading.Thread(target=producer, args=(queue,))

thread_consumer.start()
thread_producer.start()
