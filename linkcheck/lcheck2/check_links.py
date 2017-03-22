import os, sys, workerpool, paxutils as pu
sys.path.insert(0, r'C:\home\books\work\booksaver\booksaver')
os.environ['DJANGO_SETTINGS_MODULE'] = 'booksaver.settings'
print sys.path
from avaxhome.models import *
from linkcheck import LinkChecker, parser_map
from traceback import format_exc

workers = []

def check(url):
    c = workers.pop()
    try:
        result = c.check(url)
        pu.info('result: %s\t%s' % (url, result))
    except Exception, e:
        print 'Exception:', e, url, format_exc()

    workers.append(c)


def process_mt(urls):

    for i in range(12):
        workers.append(LinkChecker())

    pool = workerpool.WorkerPool(size=10)
    pool.map(check, urls)
    pool.shutdown()
    pool.wait()

def process(urls):
    c = LinkChecker()
    for urls in urls:
        #url = 'http://%s' % l.url
        check(url)

stop_paths='''/list/
/folder/
/folders/
/users/'''

def filter_urls(urls, domain_list):
    result = []
    for url in urls:
        for path in stop_paths:
            if path in url:
                break

        for domain in domain_list:
            if domain in url:
                result.append(url)

    return result

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')


    links = Link.objects.all()[:120000].values('url') #order_by('-date_created')
    urls = ['http://%s' % d['url'].strip() for d in links if '/' in d['url']]
    print len(urls)
    urls = filter_urls(urls, parser_map.keys())
    print len(urls)

    process_mt(urls)
