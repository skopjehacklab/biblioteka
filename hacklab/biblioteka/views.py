from django.views.generic import ListView
from hacklab.biblioteka.models import Book


class BookListView(ListView):
    model = Book
    template_name = 'list_pages.html'
    context_object_name = 'books'
    paginate_by = 10
