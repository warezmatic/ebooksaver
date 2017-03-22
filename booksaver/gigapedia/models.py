from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200,db_index=True)
    title_by = models.CharField(max_length=200)
    site_id = models.IntegerField(unique=True)
    author = models.CharField(max_length=100,db_index=True,null=1,blank=1)
    date = models.DateTimeField('date published',db_index=True)
    date_updated = models.DateTimeField('date updated',db_index=True,null=1,blank=1)
    bookinfo = models.CharField(max_length=200,null=1,blank=1,db_index=True)
    language = models.CharField(max_length=2,null=1,blank=1,db_index=True)


    def __unicode__(self):
        return '%s [%s]' % (self.title[:50],self.bookinfo)

    def admin_isbn(self):
        s=''
        for i in self.isbn_set.all():
            s+='<li>%s</li>' % i.code

        return '<ol>%s</ol>' % s

    admin_isbn.allow_tags = True

    def admin_link(self):
        return '<a href="http://avaxhome.ws/%s" target="_blank">%s</a>' % (self.path,  self.path[:30])
    admin_link.allow_tags = True

    def admin_links(self):
        s=''
        for l in self.link_set.all():
            s+='<li>%s</li>' % l.url

        return '<ol>%s</ol>' % s

    admin_links.allow_tags = True





class Link(models.Model):
    book = models.ForeignKey(Book)
    url = models.CharField(max_length=300)
    domain = models.CharField(max_length=50,db_index=True)
    format = models.CharField(max_length=4,blank=1,null=1,db_index=True)
    info = models.CharField(max_length=200,blank=1,null=1,db_index=True)
    date = models.DateTimeField('date published',db_index=True,null=1,blank=1)
    author = models.CharField(max_length=100,null=1,blank=1)

    def __unicode__(self):
        return '[%s] %s' % (self.domain, self.url[-40:])


class ISBN(models.Model):
    book = models.ForeignKey(Book)
    code = models.CharField(max_length=13,db_index=True)
