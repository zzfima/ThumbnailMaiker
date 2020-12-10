import multiprocessing


def bot_aks(jq: multiprocessing.JoinableQueue):
    jq.put('What is your name?')
    answer1 = jq.get()
    print('bot_aks receive ', answer1)
    jq.task_done()


def bot_answer(jq: multiprocessing.JoinableQueue):
    ask1 = jq.get()
    print('bot_answer receive ', ask1)
    jq.task_done()

    jq.put('My name is Bot')


if __name__ == '__main__':
    jq = multiprocessing.JoinableQueue(True)

    p1 = multiprocessing.Process(target=bot_aks, args=(jq,))
    p2 = multiprocessing.Process(target=bot_answer, args=(jq,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    jq.close()
    jq.join()
