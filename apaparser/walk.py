#!/usr/bin/env python


import os, sys
import apaparser
import paxutils as pu

from traceback import format_exc

def main(path='..'):
    for fn in os.listdir(path):
        if fn[0].isdigit() and not fn.endswith('~') and len(fn) > 9:
            apaparser.process_file('%s/%s' % (path, fn))


def to_django(path='..'):
    pu.log2file('apa_walk.log')

    subjects_cache = {}

    if sys.platform == 'win32':
        sys.path.insert(0,'C:\\home\\books\\work\\booksaver\\django\\booksaver')
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    else:
        sys.path.insert(0,'/home/books/work/booksaver/django/booksaver')
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from django.conf import settings

    settings.DEBUG=0


    from apa.models import Book, ASIN, Author, Subject, Publisher, ProductType, Language


    c = 0
    for fn in os.listdir(path):
        c += 1

        if not (fn[0].isdigit() and not fn.endswith('~') and len(fn) > 9):
            continue

        #if c > 10:
        #    break


        filepath = '%s/%s' % (path, fn)
        try:
            ab = apaparser.parse_file(filepath)
        except Exception, e:
            #pu.debug('exception: %s - %s %s' % (fn,e,format_exc()))
            print e
            continue



        try:
            asin, created = ASIN.objects.get_or_create(code=ab['asin'], defaults={'status': 0})

            similar_asins = []

            if not created: #asin exists
                similar_asins = [p.code for p in asin.similar_products.all()]

                if asin.status == 1:
                    asin.status = 0
                    for product_asin in ab['similar_products']:
                        if product_asin not in similar_asins:
                            similar_product, created = \
                                    ASIN.objects.get_or_create(code=product_asin,
                                            defaults={'status': 1})

                            asin.similar_products.add(similar_product)

                    asin.save()
                elif asin.status == 0:

                    has_book = False
                    try:
                        abook = asin.book
                        has_book = True
                    except Book.DoesNotExist:
                        pass

                    if has_book: #skip if book mis already mapped
                        continue


            for product_asin in ab['similar_products']:

                similar_product, created = \
                    ASIN.objects.get_or_create(code=product_asin,
                                                defaults={'status': 1})

                asin.similar_products.add(similar_product)




            b = Book(
                    title = ab['title'] and ab['title'][:200],
                    description = ab['description'],
                    sales_rank = ab['salesrank'],
                    pub_date = ab['pub_date'],
                    #product_type = ab['product_type'],
                    #product_group = ab['product_group'],
                    price_new = ab['price_new'],
                    price_used = ab['price_used'],
                    #currency_code = ab['currency_code'] and ab['currency_code'][:3],
                    #language = ab['language'],
                    isbn = ab['isbn'] and ab['isbn'][:10],
                    image_h = ab['image_h'],
                    image_w = ab['image_w'],
                    image_name = ab['image_name'] and ab['image_name'][:20],
                    ean = ab['ean'],
                    page_num = ab['page_num'],
                    edition = ab['edition'] and ab['edition'][:5].lower(),
                    #raw_subjects = ab['subjects'] and str(ab['subjects']) or None
                )

            b.asin = asin

            publisher_name = ab['publisher']
            if publisher_name:
                publisher, created = Publisher.objects.get_or_create(name=publisher_name[:100])
                b.publisher = publisher

            product_type_name = ab['product_type']
            if product_type_name:
                product_type, created = ProductType.objects.get_or_create(name=product_type_name[:20])
                b.product_type = product_type

            language_name = ab['language']
            if language_name:
                language, created = Language.objects.get_or_create(name=language_name[:20])
                b.language = language

            b.save()


            for author_name in ab['authors']:
                author, created = Author.objects.get_or_create(name=author_name[:100])
                b.authors.add(author)


            for subject_list in ab['subjects']:
                parent_subject = None

                for site_id, subject_name in subject_list:
                    subject_name = subject_name[:200]


                    try:
                        subject = Subject.objects.get(site_id=site_id)
                    except Subject.DoesNotExist:
                        subject = Subject.objects.create(
                                        site_id=site_id,
                                        name=subject_name,
                                        parent=parent_subject
                        )

                    parent_subject_name = subject_name
                    parent_subject = subject



                if parent_subject:
                    b.subjects.add(parent_subject)






            print '%s\t%s\t%s' % (b.id, b.asin, b.title)
        except Exception,e:
            print fn, e
            print 'exception: %s - %s %s' % (fn, e, format_exc())



if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')



    if sys.platform == 'win32':
        to_django()
    else:
        to_django('../amazon')
