from django.db import models

class Book(models.Model):
    query_isbn = models.CharField(max_length=13)
    site_id = models.CharField(max_length=20,unique=True)
    bib_key = models.CharField(max_length=13)
    embeddable = models.BooleanField()
    thumbnail_url = models.CharField(max_length=200, blank=True,null=True)
    preview = models.CharField(max_length=20, blank=True,null=True)

    def admin_image(self):
        return '<img src="%s"/>' % self.thumbnail_url
    admin_image.allow_tags = True

    def admin_link(self):
        return '<a href="http://books.google.com/books?id=%s" target="_blank">preview</a>' % self.site_id
    admin_link.allow_tags = True
