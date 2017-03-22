from django.db import models
from djangosphinx.models import SphinxSearch


class Format(models.Model):
    name = models.CharField(max_length=5,db_index=True)
    def __unicode__(self):
        return self.name


class ISBN(models.Model):
    code = models.CharField(max_length=13,db_index=True)
    def __unicode__(self):
        return self.code


class Book(models.Model):
    site_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=200,db_index=True)
    path = models.CharField(max_length=200)
    author = models.CharField(max_length=100,db_index=True)
    date = models.DateTimeField('post date',db_index=True)
    image = models.CharField(max_length=200,blank=1,null=1,default=None)
    body = models.TextField(null=1,blank=1)
    bookinfo = models.CharField(max_length=200,null=1,blank=1,db_index=True)
    pixhost_id = models.IntegerField(unique=False,db_index=True)


    description = models.TextField(null=1,blank=1)
    lang = models.CharField(max_length=2,db_index=True)
    lang_is_reliable = models.BooleanField()
    pubdate = models.DateField('publication date',blank=1,null=1,db_index=True)
    pages = models.IntegerField(null=1,blank=1)
    size = models.CharField(max_length=50, null=1,blank=1, db_index=True)
    formats = models.ManyToManyField(Format)
    isbns = models.ManyToManyField(ISBN)

    search = SphinxSearch('test1')

    def _get_isbn(self):
        try:
            return self.isbns.all()[0].code
        except:
            return None

    def _get_media_formats(self):
        try:
            return ','.join([f.name for f in self.formats.all()])
        except:
            return None


    def _get_short_description(self, max_length=200):
        if self.description:
            if len(self.description) > max_length:
                return self.description[:max_length-3] + '...'
            else:
                return self.description

        else:
            return ''


    isbn = property(_get_isbn)
    short_description = property(_get_short_description)
    media_formats = property(_get_media_formats)


    def __unicode__(self):
        return '%s [%s] %s' % (self.title[:50], self.bookinfo, self.date.strftime('%Y-%m-%d'))

    def admin_image(self):
        return '<img src="http://%s" />' % self.image
    admin_image.allow_tags = True

    def admin_link(self):
        return '<a href="http://avaxhome.ws/%s" target="_blank">%s</a>' % (self.path,  self.path[:30])
    admin_link.allow_tags = True

    def admin_links(self):
        s=''
        for l in self.link_set.all():
            s+='<li>%s</li>' % l.url

        return '<ol>%s</ol>' % s

    admin_links.allow_tags = True

    def admin_isbns(self):
        return ','.join([unicode(i) for i in self.isbns.all()])

    def admin_formats(self):
        return ','.join([unicode(i) for i in self.formats.all()])




class Link(models.Model):
    book = models.ForeignKey(Book)
    url = models.CharField(max_length=300)
    domain = models.CharField(max_length=50,db_index=True)
    format = models.CharField(max_length=4,blank=1,null=1,db_index=True)
    info = models.CharField(max_length=200,blank=1,null=1,db_index=True)
    filename = models.CharField(max_length=100,blank=1,null=1,db_index=True)
    size_in_mb = models.FloatField(blank=1,null=1)
    is_valid = models.NullBooleanField()
    date_created = models.DateTimeField('created date',blank=1,null=1,db_index=True)
    date_checked = models.DateTimeField('checked date',blank=1,null=1,db_index=True)

    def __unicode__(self):
        return u'%s %s' % (self.domain, self.url[-20:])
