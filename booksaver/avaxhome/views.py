from django.views.generic import ListView, DetailView
from models import Book, Link

class SearchListView(ListView):
    model = Book
    template_name = "search.html"
    paginate_by = 12
    search_query = None

    def get_queryset(self):
        self.search_query = self.request.GET.get('q')

        if self.search_query:
            qs = Book.search.query(self.search_query)
        else:
            qs = Book.objects.all()

        #Post.objects.filter(is_delete=False).order_by('-created_at')
        #if not self.request.user.is_authenticated():
        #    return qs.exclude(is_private=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        context['search_query'] = self.search_query
        return context

class BookDetail(DetailView):
    model = Book
    template_name = "book.html"

    #def get_context_data(self, **kwargs):
    #    context = super(BookDetail, self).get_context_data(**kwargs)
    #    context['links'] = Link.objects.filter(book=self.object)
    #    return context
