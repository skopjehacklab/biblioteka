from django.urls import path, re_path
from django.views.decorators.csrf import csrf_protect

from hacklab.biblioteka.views import index, by_year, by_author, by_publisher
from hacklab.biblioteka.views import by_tag, rent_book, history, my_history
from hacklab.biblioteka.views import reserved_books, reserve_book
from hacklab.biblioteka.views import remove_reservation, update_user_list
from hacklab.biblioteka.views import view_book_details, return_book

urlpatterns = [
        path('', index, name='index'),
        path('results/', index, name='results'),
        path('year/(?P<godina>\d+)/$', by_year, name='by_year'),
        path('author/a_id<int:number>/', by_author, name='by_author'),
        path('publisher/p_id<int:number>)/', by_publisher,
             name='by_publisher'),
        path('rent/k_id<int:number>)/', rent_book, name='rent'),
        path('rented_books/', history, name='list-rented'),
        path('history/$', my_history, name='my-history'),
        path('reservations/', reserved_books, name='reservations'),
        path('reservations/make/', reserve_book, name='make-reservation'),
        path('reservations/remove/', remove_reservation,
             name='remove-reservation'),
        path('update/', update_user_list, name='update'),
        re_path('book/(?P<k_id>\d+)/(?P<k_slug>[\-\+\%\w\&]+)/$',
                view_book_details, name='by_author'),
        re_path('tag/(?P<tag>[a-zA-Z0-9 ]+)/$', by_tag, name='by_author'),
        re_path('rented_books/(?P<year>[0-9]{4})/$', history,
                name='rented-year'),
        re_path('rented_books/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',
                history, name='rented-month'),
        re_path('history/(?P<year>[0-9]{4})/$', my_history,
                name='my-history-year'),
        re_path('history/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',
                my_history, name='my-history-month'),
        re_path('return_book/(?P<k_id>\d+)/$', return_book, name='return-book'),
        re_path('^reservations/(?P<p>[p])/$', reserved_books,
                name='reservations'),
]
