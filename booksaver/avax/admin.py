from avax.models import Book, Link
from django.contrib import admin

class BookAdmin(admin.ModelAdmin):
    list_display = ('admin_image', 'isbn','title', 'admin_link', 'bookinfo', 'admin_description','admin_links', 'author', 'date')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('date','author')
    date_hierarchy = 'date'


admin.site.register(Book,BookAdmin)
admin.site.register(Link)
