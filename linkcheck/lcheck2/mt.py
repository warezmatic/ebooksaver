from Queue import Queue
from threading import Thread
import logging

logging.basicConfig(level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


debug = logging.debug



class Consumer(Thread):

    def __init__(self, queue):
        debug('Consumer.__init__()')
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            i = self.queue.get()
            #print i
            debug('task_done(): %s' % i)
            self.queue.task_done()


class Producer(Thread):

    def __init__(self, queue, iterable):
        debug('Producer.__init__()')
        Thread.__init__(self)
        self.queue = queue
        self.iterable = iterable

    def run(self):
        for i in self.iterable:
            self.queue.put(i)
            debug('put(): %s' % i)


if __name__ == '__main__':
    num_workers = 3

    q = Queue(1)
    p = Producer(q, range(100))
    #p.daemon = True
    p.name = 'Producer'
    p.start()


    for i in range(num_workers):
        w = Consumer(q)
        w.name = 'Consumer-%d' % i
        w.daemon = True
        w.start()

    q.join()
