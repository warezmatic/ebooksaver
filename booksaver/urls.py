from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail
from django.conf import settings
from avaxhome.models import Book
from avaxhome.views import SearchListView, BookDetail
import os

from django.contrib import admin
admin.autodiscover()

avax_books = {
    'queryset': Book.objects.order_by('-date')[:1728],  #144*12
    'template_name': 'index.html',
    #'paginate_by': 12,


}

urlpatterns = patterns('',
    (r'^$', list_detail.object_list, avax_books),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^search/', SearchListView.as_view(), name='search'),
    url(r'^book/(?P<pk>\d+)', BookDetail.as_view(), name='book-detail'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$',
            'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

        (r'^media/(?P<path>.*)$',
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
