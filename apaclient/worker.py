import sys
import lxml.etree as etree
import amazonproduct, os
from amazonproduct.processors import LxmlObjectifyProcessor
from random import choice

import MySQLdb
from MySQLdb import escape_string
import MySQLdb.cursors


associate_tag = 'flazx-20'


class Worker(object):
    def __init__(self):
        super(Worker, self).__init__()
        self.apis = [
            amazonproduct.API('','', 'us', associate_tag=associate_tag),
            amazonproduct.API('','', 'us')
        ]

        self.response_processor = LxmlObjectifyProcessor()

        self.api = amazonproduct.API('','', 'us', associate_tag=associate_tag)
        self.api.TIMEOUT = 30.0
        self.last_exception = None


    def raw_search(self, q, cache=0, cachefile=None):

        self.last_exception = None

        if cache:
            cachefile = cachefile or q

            if os.path.exists(cachefile):
                if os.path.getsize(cachefile) == 0:
                    return None

                f = open(cachefile,'rb')
                node = self.response_processor(f)
                #xml = f.read()
                f.close()
                return node #.Items.Item


        api = choice(self.apis)
        #api = self.api

        try:
            if len(q) == 10 and (q.startswith('B00') or q.startswith('R00')):
                node = api.item_lookup(q, ResponseGroup='Large', IdType='ASIN')
            else:
                node = api.item_lookup(q, ResponseGroup='Large', IdType='ISBN', SearchIndex='Books')


        except amazonproduct.errors.InvalidParameterValue, e:
            self.last_exception = e
            f = open(cachefile,'wb+')
            f.write('')
            f.close()
            return None
        except amazonproduct.errors.AWSError, e:
            self.last_exception = e
            return None
        except Exception, e:
            self.last_exception = e
            return None


        if cache:
            f = open(cachefile,'wb+')
            f.write(etree.tostring(node))
            f.close()

        return node #.Items.Item

    def search(self, q, cache=0):
        node = self.raw_search(q, cache=cache)
        return self.parse(node)

    def parse(self, node=None):
        if node is None:
            return None
        try:
            isbn = node.Items.Item.ItemAttributes.ISBN
        except AttributeError:
            isbn = ''

        try:
            ean = node.Items.Item.ItemAttributes.EAN
        except AttributeError:
            ean = ''

        try:
            language=node.Items.Item.ItemAttributes.Languages.Language.Name
        except AttributeError:
            language = ''

        try:
            title=node.Items.Item.ItemAttributes.Title
        except AttributeError:
            title = ''

        try:
            salesrank=node.Items.Item.SalesRank
        except AttributeError:
            salesrank = None





        return dict(
            title=escape_string(str(title)),
            language=language,
            isbn=isbn,
            ean=ean,
            asin=node.Items.Item.ASIN,
            xml=escape_string(etree.tostring(node)),
            salesrank=salesrank
        )


def get_isbns(fn='bad_isbns_packt.txt'):
    isbns = [l.strip() for l in open(fn).readlines() if l.strip().replace('X','').isdigit()]
    return isbns

def search_isbns(w=None):
    w = w or Worker()
    isbns = get_isbns()
    for isbn in isbns:
        item = w.search(isbn, cache=1)
        print isbn, item


def format_sql(aws_item,lnu_id):
    aws_item['lnu_id'] = lnu_id
    return "update lnu_books set aws_title='%(title)s', aws_isbn='%(isbn)s', aws_asin='%(asin)s', aws_ean='%(ean)s', aws_language='%(language)s',  aws_xml='%(xml)s' where lnu_id=%(lnu_id)d;" % aws_item

def lnu_walk():
    db = MySQLdb.connect("192.168.1.5","root","maxima","booksaver") #cursorclass=MySQLdb.cursors.DictCursor
    cursor = db.cursor()
    count = cursor.execute("select lnu_id, isbns from lnu_books")
    #print count
    w = Worker()

    while True:
        try:
            lnu_id, isbns = cursor.fetchone()
        except:
            break;


        for isbn in isbns.split(','):
            aws_item = w.search(isbn, cache=1)
            if aws_item:
                print format_sql(aws_item,lnu_id)
                break;


def get_from_file(fn='avax_isbns.txt'):
    isbns = [l.strip() for l in open(fn).readlines() if len(l)> 9]
    files = os.listdir('.')
    return list(set(isbns) - set(files))

if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    #aws_item = w.search('0387495150', cache=1)
    #print format_sql(aws_item)
    #search_isbns()
    #lnu_walk()

    w = Worker()

    isbns = sys.argv[1:]
    if len(isbns) == 0:
        isbns = get_from_file('avaxhome_isbn_list.txt')


    for isbn in isbns:
        print isbn, str(w.search(isbn, cache=1))[:100]

        if w.last_exception:
            print w.last_exception
