from django.db import models

class ASIN(models.Model):
    code = models.CharField('asin', max_length=10, unique=True)
    status = models.IntegerField(db_index=True, blank=1,null=1)
    similar_products = models.ManyToManyField('self')

    def __unicode__(self):
        return u'%s' % (self.code)

class Subject(models.Model):
    site_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=200,db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return u'%d %s' % (self.site_id, self.name)


class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)
    synonims = models.ManyToManyField('self')

    def __unicode__(self):
        return u'%s' % (self.name)

class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    synonims = models.ManyToManyField('self')

    def __unicode__(self):
        return u'%s' % (self.name)


class ProductType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    synonims = models.ManyToManyField('self')

    def __unicode__(self):
        return u'%s' % (self.name)


class Language(models.Model):
    name = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=2, unique=True, blank=1,null=1)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code or 'un')





class Book(models.Model):
    asin = models.OneToOneField(ASIN)
    title = models.CharField(max_length=200,db_index=True,blank=1,null=1)
    description = models.TextField(null=1,blank=1)

    sales_rank = models.IntegerField(db_index=True, blank=1,null=1)
    pub_date = models.DateField('publication date',blank=1,null=1,db_index=True)

    #product_group = models.CharField(max_length=50, blank=1,null=1)

    price_new = models.IntegerField(blank=1,null=1)
    price_used = models.IntegerField(blank=1,null=1)
    #currency_code = models.CharField(max_length=3, blank=1,null=1)
    #page_num = models.SmallIntegerField(null=1,blank=1)

    isbn = models.CharField(max_length=10, blank=1,null=1, db_index=True)
    image_h = models.IntegerField(blank=1,null=1)
    image_w = models.IntegerField(blank=1,null=1)
    image_name = models.CharField(max_length=20,blank=1,null=1)
    ean = models.BigIntegerField(blank=1,null=1, db_index=True)

    subjects = models.ManyToManyField(Subject)
    #raw_subjects = models.TextField(null=1,blank=1)
    authors = models.ManyToManyField(Author)

    publisher = models.ForeignKey(Publisher, blank=1,null=1)
    #product_type = models.ForeignKey(ProductType, blank=1,null=1)
    #language = models.ForeignKey(Language, blank=1,null=1)

    def __unicode__(self):
        return '%s %s' % (self.asin, self.title)
