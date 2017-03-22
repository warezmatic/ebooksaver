from lnu.models import Book
from django.contrib import admin

#class LinkInline(admin.StackedInline):
#    model = Link
#    extra = 0


class BookAdmin(admin.ModelAdmin):
    list_display = ('admin_isbn', 'title', 'doc_id', 'author', 'date','admin_shelve')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('date','author')
    date_hierarchy = 'date'

    #inlines = [LinkInline]




admin.site.register(Book,BookAdmin)
#admin.site.register(Link)
