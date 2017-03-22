import httplib, json
import StringIO
import gzip, time, os, sys, MySQLdb
import paxutils as pu
from pprint import pprint


HOST='books.google.com'
PATH_TEMPLATE = '/books?bibkeys=%s&jscmd=viewapi&callback=gb'

_headers='''User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: en-us,en;q=0.5

Accept-Encoding: gzip, deflate

Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7

DNT: 1

Connection: keep-alive

'''


def get_headers_dict(s):

    headers_dict = {}

    for l in s.split('\n'):
        if len(l) < 4:
            continue
        try:
            k,v = l.split(': ')
            headers_dict[k] = v
        except ValueError:
            pass

    return headers_dict

HEADERS = get_headers_dict(_headers)


class Worker(object):
    def __init__(self, host=None, headers=None, path_template=None):
        super(Worker, self).__init__()
        self.host = host or HOST
        self.headers = headers or HEADERS
        self.path_template = path_template or PATH_TEMPLATE
        self.connect()


    def connect(self, debug=0):
        self.conn = httplib.HTTPConnection(self.host)
        #self.conn.set_debuglevel(debug)

        return self.conn

    def raw_search(self, q, cache=0, cachefile=None):
        if cache:
            cachefile = cachefile or q

            if os.path.exists(cachefile):
                f = open(cachefile,'rb')
                html = f.read()
                f.close()
                return html

        path = self.path_template % q
        self.conn.request('GET', path, headers=self.headers)
        r = self.conn.getresponse()

        if r.getheader('Content-Encoding') == 'gzip':
            compressed = r.read()
            html  = gzip.GzipFile(fileobj=StringIO.StringIO(compressed)).read()
        else:
            html = r.read()

        if cache:
            f = open(cachefile,'wb+')
            f.write(html)
            f.close()

        return html

    def parse(self, html):
        _dict = json.loads(html[3:-2])

        result = None

        keys = _dict.keys()
        if len(keys) == 1:
             _item = _dict[keys[0]]


             try:

                 result = dict(
                    site_id = _item[u'info_url'].split('&')[0].split('=')[-1], #if no id - return None
                    thumbnail_url=_item.get('thumbnail_url'),
                    embeddable = _item.get('embeddable'),
                    bib_key = _item.get('bib_key'),
                    preview = _item.get('preview'),
                 )

             except:
                return None


        return result

    def search(self, q, cache=0):
        html = self.raw_search(q, cache=cache)
        return self.parse(html)


def get_isbns(fn='bad_isbns_packt.txt'):
    isbns = [l.strip() for l in open(fn).readlines() if l.strip().replace('X','').isdigit()]
    return isbns

def search_isbns(w=None):
    w = w or Worker()
    isbns = get_isbns()
    for isbn in isbns:
        items = w.search(isbn, cache=1)
        print isbn, len(items)
        for item in items:
            print item,  '\n'

def to_django(isbns=None):

    isbns = isbns or ['0875848079'] #get_isbns()

    sys.path.insert(0,'C:\\home\\books\\work\\booksaver\\django\\booksaver')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from google.models import Book


    w = Worker()

    for isbn in isbns:
         i = w.search(isbn, cache=1)
         #print 'i=', i
         if not i:
            print isbn,  'NOT FOUND'
            continue

         i['query_isbn'] = isbn
         b = Book(**i)
         try:
             b.save()
             print b.id, b.site_id
         except Exception,e:
             print isbn, i['site_id'], 'skipped', e
             pass


def get_isbns_from_db():
    db = MySQLdb.connect("192.168.1.5","root","maxima","booksaver") #cursorclass=MySQLdb.cursors.DictCursor
    cursor = db.cursor()
    count = cursor.execute("select isbns from lnu_books where isbns !='' and isbns is not null")
    print count

    result = []

    while True:
        isbns  = cursor.fetchone()

        if not isbns:
            break;

        for isbn in isbns[0].split(','):
            if len(isbn) == 10 and isbn.replace('X','').isdigit():
                result.append(isbn)


    return result


def get_isbns_from_db_avax():
#SELECT code FROM avaxhome_isbn where LENGTH(code) = 10
#SELECT bib_key FROM google_book g LIMIT 0,1000
    import MySQLdb
    db = MySQLdb.connect("192.168.1.5","root","pw","booksaver") #cursorclass=MySQLdb.cursors.DictCursor
    cursor = db.cursor()
    cursor2 = db.cursor()
    count = cursor.execute("SELECT code FROM avaxhome_isbn") #~301K

    count2 = cursor2.execute("SELECT bib_key FROM google_book") #~301K
    print count, count2



    ids = []
    result = cursor.fetchall()
    bib_keys = [k[0] for k in cursor2.fetchall()]

    for r in result:
        isbn = r[0]
        if len(isbn) == 10 and isbn.replace('X','').isdigit() and (not isbn in bib_keys):
            ids.append(isbn)

    #print len(ids)
    #return ids

def get_isbns_from_file(fn='gb_new_isbns.txt'):
    return [l.strip() for l in open(fn).readlines() if len(l.strip()) == 10]

def dump(fn, lst):

    f = open(fn, 'w+')
    for i in lst:
        f.write(str(i) + '\n')
    f.close()



def mt_process(ids, numworkers=10, numthreads=5):
    import logging,  workerpool
    logging.basicConfig(level=logging.INFO, format='[%(threadName)-9s] %(message)s')
    logging.disable(logging.DEBUG)


    workers = []
    for i in range(numworkers):
        workers.append(Worker())

    def run(isbn):
        w = workers.pop()
        try:
            item = w.search(isbn, cache=1)
        except Exception, e:
            item = e

        logging.info(str(item))
        workers.append(w)


    pool = workerpool.WorkerPool(size=numthreads)
    pool.map(run, ids)
    pool.shutdown()
    pool.wait()


if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    #httplib.HTTPConnection.debuglevel = 1

    w = Worker()

    ids = sys.argv[1:]
    if len(ids) == 0:
        ids = get_isbns_from_file()

    #for isbn in ids:
    #    try:
    #        print isbn, len(w.raw_search(isbn, cache=1))
    #    except Exception, e:
    #        print e

    #mt_process(ids)


    to_django(ids)
