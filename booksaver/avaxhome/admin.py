from avaxhome.models import Book, Link, Format, ISBN
from django.contrib import admin

class BookAdmin(admin.ModelAdmin):
    list_display = ('admin_image', 'admin_isbns','title', 'admin_link', 'bookinfo', 'lang', 'pubdate','admin_formats', 'description','admin_links', 'author', 'date')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('date',)
    date_hierarchy = 'date'


admin.site.register(Book,BookAdmin)
admin.site.register(Link)
admin.site.register(Format)
admin.site.register(ISBN)
