import httplib, json
import StringIO
import gzip, time, os, sys, MySQLdb,  time
import paxutils as pu
from pprint import pprint


HOST='www.googleapis.com'
PATH_TEMPLATE = '/books/v1/volumes?q=isbn:%s'
_PATH_VOLUME_TEMPLATE = '/books/v1/volumes/%s'
PATH_VOLUME_TEMPLATE = '/books/v1/volumes/%s?key=*key*'
PATH_VOLUME_TEMPLATE_WITH_KEY = '/books/v1/volumes/%s?key='
keys = '''key1
key2'''.split()


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
        self.conn = None
        self.connect()


    def connect(self, debug=1):
        if self.conn:
            self.conn.close()

        self.conn = httplib.HTTPSConnection(self.host)
        self.conn.set_debuglevel(debug)

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


def get_ids_from_db():
    db = MySQLdb.connect("192.168.1.5","root","pw","booksaver") #cursorclass=MySQLdb.cursors.DictCursor
    cursor = db.cursor()
    count = cursor.execute("select site_id from google_book")

    ids = []
    result = cursor.fetchall()

    for r in result:
        if  not os.path.exists(r[0]):
            ids.append(r[0])

    print len(ids)

    return ids


def walk_over_ids(w, ids):
    #ids = get_ids_from_db()
    c = 1
    for gb_id in ids:
        if os.path.exists(gb_id):
            continue

        item = w.raw_search(gb_id, cache=1)
        #time.sleep(3.0)





        gb = json.loads(item)
        error = gb.get(u'error')
        if error and error['code'] == 403:
            if os.path.exists(gb_id):
                os.remove(gb_id)
                raise Exception(gb_id, error['message'])


        if 0 and error and error['code'] == 403:
            if os.path.exists(gb_id): os.remove(gb_id)
            time.sleep(60.0 * 20)
            w.connect()
            item = w.raw_search(gb_id, cache=1)
            gb = json.loads(item)
            error = gb.get(u'error')
            if error and error['code'] == 403:
                if os.path.exists(gb_id): os.remove(gb_id)
                raise Exception(gb_id, error['message'])




        print len(item), c
        c += 1
        #if c > 2000:
        #    return

if __name__ == '__main__':
    import sys, jsonlib2 as json
    reload(sys)
    sys.setdefaultencoding('utf8')

    ids = sys.argv[1:]
    if len(ids) == 0:
        ids = get_ids_from_db()


    for k in keys:
        print k
        w = Worker(path_template=PATH_VOLUME_TEMPLATE_WITH_KEY+k)

        try:
            walk_over_ids(w, ids)
        except Exception, e:
            print e





    #item = w.raw_search('0596515138', cache=1)
    #pprint(json.loads(item))
    #item = w.raw_search('0078139449', cache=1)
    #item = w.raw_search('--dqcf_mmfEC', cache=1)

    #pprint(json.loads(item))


    #to_django(get_isbns_from_db())
