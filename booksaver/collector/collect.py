import sys, os
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


def getAmazonBook(code):
    if code.startswith('978') and len(code) == 13:
        try:
            code = int(code)
            amazon_book = AmazonBook.objects.get(ean=code)
            return amazon_book
        except AmazonBook.DoesNotExist:
            print 'AmazonBook.DoesNotExist: EAN=', code
        except ValueError:
            print 'AmazonBook.DoesNotExist: Bad EAN=', code
        except AmazonBook.MultipleObjectsReturned:
            for amazon_book in AmazonBook.objects.filter(ean=code).all():
                if not amazon_book.asin.code.startswith('B00'):
                    return amazon_book

            return amazon_book #last one

    else:
        try:
            amazon_book = AmazonBook.objects.get(asin__code=code)
            return amazon_book
        except AmazonBook.DoesNotExist:
            print 'AmazonBook.DoesNotExist: ASIN=', code
            try:
                amazon_book = AmazonBook.objects.get(isbn=code)
                return amazon_book
            except AmazonBook.DoesNotExist:
                print 'AmazonBook.DoesNotExist: ISBN=', code

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')

    sys.path.insert(0, r'C:\home\books\work\booksaver\booksaver')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from django.conf import settings

    settings.DEBUG = 0

    from avaxhome.models import Book as AvaxBook, ISBN
    from apa.models import Book as AmazonBook
    from collector.models import Book



    qs = ISBN.objects.all()

    avax_processed = []
    amazon_processed = []

    c = 0
    for isbn in queryset_iterator(qs):

        code = isbn.code

        avax_books = []

        print code

        has_amazon_book = False
        has_avax_processed = False
        for avax_book in isbn.book_set.all():
            if avax_book.pk in avax_processed:
                print 'AvaxBook already processed: %s' % avax_book
                has_avax_processed = True
                continue

            avax_books.append(avax_book)

            print avax_book.title

            if not has_amazon_book:
                amazon_book = getAmazonBook(code=code)
                if amazon_book:
                    print amazon_book
                    has_amazon_book = True
                else:
                    for other_isbn in avax_book.isbns.exclude(code=code).all():
                        amazon_book = getAmazonBook(code=other_isbn.code)
                        if amazon_book:
                            print 'other_isbn:', amazon_book
                            has_amazon_book = True

                if amazon_book:
                    if amazon_book.pk in amazon_processed:
                        print 'AmazonBook already processed: %s' % amazon_book
                    else:
                        amazon_processed.append(amazon_book.pk)


            avax_processed.append(avax_book.pk)
            #save

        if len(avax_books) > 1:
            if has_avax_processed:
                print "has_avax_processed, but others are not processed: " % avax_books

        b = Book.objects.create()
        for avax_book in avax_books:
            b.avax_books.add(avax_book)
        if amazon_book:
            b.amazon_book = amazon_book

        b.save()

        print b.pk
        print

        #c += 1
        #if c > 100000:
        #    break
