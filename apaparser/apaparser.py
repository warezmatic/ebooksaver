#!/usr/bin/env python

import lxml.etree as etree
import amazonproduct, os, sys
from amazonproduct.processors import LxmlObjectifyProcessor
from pprint import pprint
from datetime import date
from BeautifulSoup import BeautifulSoup


def get_images():
        try:
            n=node.Items.Item.ImageSets.ImageSet.SwatchImage

            swatch_image_h = int(n.Height.text)
        except AttributeError:
            swatch_image_h = None

        try:
            n=node.Items.Item.SmallImage

            small_image_h = int(n.Height.text)
        except AttributeError:
            small_image_h = None

        try:
            n=node.Items.Item.MediumImage

            medium_image_h = int(n.Height.text)
        except AttributeError:
            medium_image_h = None




def parse(node=None):
        if node is None:
            return None
        try:
            isbn = node.Items.Item.ItemAttributes.ISBN
        except AttributeError:
            isbn = None

        try:
            ean = node.Items.Item.ItemAttributes.EAN
        except AttributeError:
            ean = None

        #try:
        #    language=node.Items.Item.ItemAttributes.Languages.Language.Name
        #except AttributeError:
        #    language = None

        try:
            salesrank=node.Items.Item.SalesRank
        except AttributeError:
            salesrank = None

        try:
            title=node.Items.Item.ItemAttributes.Title
        except AttributeError:
            title = None

        try:
            edition=node.Items.Item.ItemAttributes.Edition.text
        except AttributeError:
            edition = None

        try:
            publisher=node.Items.Item.ItemAttributes.Publisher
        except AttributeError:
            publisher = None

        try:
            page_num=int(node.Items.Item.ItemAttributes.NumberOfPages)
        except (AttributeError, ValueError):
            page_num = None

        try:
            pub_date=node.Items.Item.ItemAttributes.PublicationDate.text
        except AttributeError:
            pub_date = None

        if pub_date:
            try:
                dp = pub_date.split('-')
                if len(dp) == 3: #1995-09-18
                    pub_date = date(int(dp[0]), int(dp[1]), int(dp[2]))

                elif len(dp) == 2: #1995-09
                    pub_date = date(int(dp[0]), int(dp[1]), 1)

                elif(dp) == 1: #1995
                    pub_date = date(int(dp[0]), 1, 1)

                else:
                    pub_date = None

            except Exception, e:
                #print e
                pub_date = None


        try:
            authors = []
            for a in node.Items.Item.ItemAttributes.Author:
                authors.append(a.text.strip())
        except AttributeError:
            authors = []

        try:
            language = None
            for n in node.Items.Item.ItemAttributes.Languages.Language:

                if n.Type.text == 'Published':
                    language = n.Name.text
                    break

                if n.Type.text == 'Unknown':
                    language = n.Name.text
                    break

            if not language:
                language = node.Items.Item.ItemAttributes.Languages.Language.Name


        except AttributeError:
            language = None



        try:
            n=node.Items.Item.LargeImage

            image_h = int(n.Height.text)
            image_w = int(n.Width.text)
            image_name = n.URL.text.split('/')[-1]
        except AttributeError:
            image_h = None
            image_w = None
            image_name = None



        try:
            categories = []
            for n in node.Items.Item.BrowseNodes.BrowseNode:
                category = []
                for el in n.iterdescendants():

                    #print el.tag,  el.text
                    if el.tag.endswith('Name'):

                        if el.text not in ('Books', 'Subjects', 'New & Used Textbooks', 'Specialty Boutique', 'Products', 'All product') and not \
                                el.getparent().getparent().tag.endswith('Children'):

                            prev = el.getprevious()
                            if prev and prev.tag.endswith('BrowseNodeId'):
                                node_id = int(prev.text)

                            #465600-New & Used Textbooks
                            #2349030011-Specialty Boutique
                            #1267878011-Products
                            #1288264011-All product

                            category.insert(0, (node_id, el.text and el.text.strip()))

                if category:
                    categories.append(category)

        except AttributeError, e:
            categories = []


        try:
            n=node.Items.Item.OfferSummary.LowestNewPrice
            price_new = int(n.Amount.text)
            currency_code = n.CurrencyCode.text

        except AttributeError:
            price_new = None
            currency_code = None


        try:
            n=node.Items.Item.OfferSummary.LowestUsedPrice
            price_used = int(n.Amount.text)
        except AttributeError:
            price_used = None



        try:
            similar_products = []
            for n in node.Items.Item.SimilarProducts.SimilarProduct:
                similar_products.append(n.ASIN)
        except AttributeError:
            pass


        try:
            description = node.Items.Item.EditorialReviews.EditorialReview.Content.text
            #if description and '<' in description:
            #    description = unicode(BeautifulSoup(description))

        except AttributeError:
            description = None


        try:
            product_group=node.Items.Item.ItemAttributes.ProductGroup
        except AttributeError:
            product_group = None


        try:
            product_type=node.Items.Item.ItemAttributes.ProductTypeName
        except AttributeError:
            product_type = None



        return dict(
            page_num=page_num,
            product_group=product_group and str(product_group).strip(),
            product_type=product_type and str(product_type).strip(),
            description=description and str(description).strip(),
            similar_products = similar_products,
            title=title and str(title).strip(),
            language=language and str(language).strip(),
            isbn=isbn and str(isbn).strip(),
            ean=ean,
            asin=str(node.Items.Item.ASIN).strip(),
            salesrank=salesrank,
            publisher=publisher and str(publisher).strip(),
            authors=authors,
            image_h=image_h,
            image_w=image_w,
            image_name=image_name,
            subjects=categories,
            price_new=price_new,
            price_used=price_used,
            currency_code=currency_code and str(currency_code).strip(),
            pub_date=pub_date,
            edition=edition,
        )

def process_file(fn):
    f = open(fn,'rb')
    processor = LxmlObjectifyProcessor()
    node = processor(f)
    ab = parse(node)
    pprint(ab)
    #print ab['isbn'] and ab['isbn'][:10]

def parse_file(fn):
    f = open(fn,'rb')
    processor = LxmlObjectifyProcessor()
    node = processor(f)
    return parse(node)

if __name__ == '__main__':
    default = '002077320X.xml'

    for fn in (sys.argv[1:] or [default]):
        process_file(fn)
