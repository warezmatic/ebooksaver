from Queue import Queue
from threading import Thread
import logging, sys, os
from linkcheck import LinkChecker, parser_map
from datetime import datetime

log_format = '%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s'

logger = logging.getLogger('check_links')
debug = logger.debug

class Consumer(LinkChecker, Thread):

    def __init__(self, queue):
        debug('Consumer.__init__()')
        Thread.__init__(self)
        LinkChecker.__init__(self)

        self.queue = queue

    def run(self):
        while True:
            link = self.queue.get()
            url = 'http://' + link.url

            try:
                result = self.check(url)
                if result:
                    link.filename = result['name']
                    link.format = result['name'].split('.')[-1][:4]
                    link.size_in_mb = result['size']
                    link.is_valid = True
                    link.date_checked = datetime.now()
                    link.save()
                else:
                    link.is_valid = False
                    link.date_checked = datetime.now()
                    link.save()

            except Exception, e:
                debug('exception: #%d %s - %s' % (link.pk, link, e))
                result = None

            debug('result: #%d %s %s' % (link.pk, link, result))
            debug('task_done(): %d %s' % (link.pk, link))
            self.queue.task_done()

        debug('exit()')



class Producer(Thread):

    def __init__(self, queue, iterable):
        debug('Producer.__init__()')
        Thread.__init__(self)

        self.queue = queue
        self.iterable = iterable

    def run(self):
        for i in self.iterable:
            if is_good_url(i.url):
                self.queue.put(i)
                debug('put(): %s' % i)
            else:
                debug('SKIPPED #%d url: %s' % (i.pk, i.url))


import gc

def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


stop_paths='''/list/
/folder/
/folders/
/users/
turbobit'''.split()

def is_good_url(url, domain_list=None):
    domain_list = domain_list or parser_map.keys()

    for path in stop_paths:
        if path in url:
           return False

    for domain in domain_list:
        if domain in url:
            return True

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf8')

    logging.basicConfig(level=logging.DEBUG, format=log_format)

    debugLogger = logging.FileHandler(filename='log/debug.log')
    debugLogger.setLevel(logging.DEBUG)
    debugLogger.setFormatter(logging.Formatter(log_format))
    logger.addHandler(debugLogger)

    fetchLogger = logging.FileHandler(filename='log/fetcher.log')
    fetchLogger.setLevel(logging.INFO)
    fetchLogger.setFormatter(logging.Formatter(log_format))
    logging.getLogger('paxutils').addHandler(fetchLogger)




    sys.path.insert(0, r'C:\home\books\work\booksaver\booksaver')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from avaxhome.models import Link

    num_workers = 18
    chunk_size = 1000
    #num_links = 200000



    links_qs = Link.objects.all() #[:num_links] filter(pk__lt=num_links)
    iterator = queryset_iterator(links_qs, chunk_size)
    #iterator = links_qs


    q = Queue(chunk_size)

    workers = []
    for i in range(num_workers):
        w = Consumer(q)
        workers.append(w)
        w.daemon = True
        w.name = 'Consumer-%d' % i
        w.start()

    #p = Producer(q, iterator)
    #p.name = 'Producer'
    #p.start()

    #p.join()


    for i in iterator:
        if is_good_url(i.url):
            q.put(i)
            debug('put(): %s' % i)
        else:
            debug('SKIPPED #%d url: %s' % (i.pk, i.url))
    q.join()
    debug("DONE")
