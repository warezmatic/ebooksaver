from django.db import models
from avaxhome.models import Book as AvaxBook
from apa.models import Book as AmazonBook

class Book(models.Model):
    avax_books = models.ManyToManyField(AvaxBook)
    amazon_book = models.ForeignKey(AmazonBook, blank=1,null=1)
    synonyms = models.ManyToManyField('self')
    #there should be other sources: flazx, wowebook ...
