import multiprocessing
from multiprocessing.connection import Connection


def bot_aks(conn: Connection):
    conn.send('What is your name?')
    answer1 = conn.recv()
    print('bot_aks receive ', answer1)


def bot_answer(conn: Connection):
    ask1 = conn.recv()
    print('bot_answer receive ', ask1)
    conn.send('My name is Bot')


if __name__ == '__main__':
    conn1, conn2 = multiprocessing.Pipe(True)

    p1 = multiprocessing.Process(target=bot_aks, args=(conn1,))
    p2 = multiprocessing.Process(target=bot_answer, args=(conn2,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
