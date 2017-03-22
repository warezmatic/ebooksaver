from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200,db_index=True)
    #title_by = models.CharField(max_length=200,null=1,blank=1)
    doc_id = models.CharField(max_length=10,unique=True)
    site_id = models.IntegerField(unique=True)
    author = models.CharField(max_length=100,db_index=True,null=1,blank=1)
    date = models.DateTimeField('date published',db_index=True)
    language = models.CharField(max_length=2,null=1,blank=1,db_index=True)
    size = models.FloatField()
    format = models.CharField(max_length=4)


    def __unicode__(self):
        return '%s [%s]' % (self.title[:50], self.doc_id)

    def admin_isbn(self):
        s=''
        for i in self.isbn_set.all():
            s+='<li>%s</li>' % i.code

        return '<ol>%s</ol>' % s

    admin_isbn.allow_tags = True

    def admin_shelve(self):
        s=''
        for i in self.shelve_set.all():
            s+='<li>%s</li>' % i.name

        return '<ol>%s</ol>' % s

    admin_shelve.allow_tags = True





class ISBN(models.Model):
    book = models.ForeignKey(Book)
    code = models.CharField(max_length=13,db_index=True)
    def __unicode__(self):
        return self.code


class Shelve(models.Model):
    book = models.ManyToManyField(Book,) #verbose_name="Books"
    name = models.CharField(max_length=100,db_index=True)
    title = models.CharField(max_length=200,db_index=True)
    site_id = models.IntegerField(unique=True)
    def __unicode__(self):
        return '%s [%s #%d]' % (self.name,  self.title, self.site_id)
