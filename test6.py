import threading
import time

event_can_produce = threading.Event()
event_can_consume = threading.Event()

is_finished = False


def producer():
    global event_can_produce, event_can_consume, is_finished
    while not is_finished:
        event_can_produce.wait()
        print('start make food...')
        time.sleep(1)
        print('finished make food!')
        event_can_produce.clear()
        event_can_consume.set()


def consumer():
    global event_can_produce, event_can_consume, is_finished
    while not is_finished:
        event_can_produce.set()
        event_can_consume.wait()
        print('start eat food...')
        time.sleep(1)
        print('finished eat food!')
        event_can_consume.clear()


event_can_produce.clear()
event_can_consume.clear()

thread_consumer = threading.Thread(target=consumer)
thread_producer = threading.Thread(target=producer)

thread_consumer.start()
thread_producer.start()

time.sleep(10)

is_finished = True

print('finish')
event_can_produce.set()
event_can_consume.set()

thread_consumer.join(5)
thread_producer.join(5)
