from django.urls import path, re_path
from django.views.decorators.csrf import csrf_protect

from hacklab.biblioteka.views import index, by_year, by_author, by_publisher
from hacklab.biblioteka.views import by_tag, rent_book, history, my_history
from hacklab.biblioteka.views import reserved_books, reserve_book
from hacklab.biblioteka.views import remove_reservation, update_user_list
from hacklab.biblioteka.views import view_book_details, return_book

urlpatterns = [
        path('', index, name='biblioteka_index'),
        path('results/', index),
        path('year/(?P<godina>\d+)/$', by_year),
        path('author/a_id<int:number>/', by_author),
        path('publisher/p_id<int:number>)/', by_publisher),
        path('rent/k_id<int:number>)/', rent_book),
        path('rented_books/', history),
        path('history/$', my_history),
        path('reservations/', reserved_books),
        path('reservations/make/', reserve_book),
        path('reservations/remove/', remove_reservation),
        path('update/', update_user_list),
        re_path('book/(?P<k_id>\d+)/(?P<k_slug>[\-\+\%\w\&]+)/$',
                view_book_details),
        re_path('tag/(?P<tag>[a-zA-Z0-9 ]+)/$', by_tag),
        re_path('rented_books/(?P<year>[0-9]{4})/$', history),
        re_path('rented_books/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',
                history),
        re_path('history/(?P<year>[0-9]{4})/$', my_history),
        re_path('history/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',
                my_history),
        re_path('return_book/(?P<k_id>\d+)/$', return_book),
        re_path('^reservations/(?P<p>[p])/$', reserved_books),
]
