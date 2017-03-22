from google.models import Book
from django.contrib import admin

class BookAdmin(admin.ModelAdmin):
    list_display = ('site_id', 'admin_link', 'preview', 'admin_image','query_isbn','bib_key')
    #list_display_links = ('title', 'bookinfo')
    #search_fields = ('title',)
    list_filter = ('preview',)
    #date_hierarchy = 'date'


admin.site.register(Book, BookAdmin)
