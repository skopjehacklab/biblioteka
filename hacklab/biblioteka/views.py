#!/usr/sbin/python -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.paginator import Paginator,  InvalidPage,  EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from hacklab.biblioteka.forms import RentalForm
from hacklab.biblioteka.models import Author, Book, Rental, Publisher
from hacklab.biblioteka.models import Reservation, ReservationExists
from hacklab.biblioteka.models import RentalExists


def update_user_list(request):
    if request.method == 'POST':
        a = User.objects.filter(
                Q(username__startswith=request.POST['name']) |
                Q(first_name__startswith=request.POST['name']) |
                Q(last_name__startswith=request.POST['name']) |
                Q(email__startswith=request.POST['name']))
        return HttpResponse(serializers.serialize("json", a))
    else:
        return HttpResponse("NOK")


def get_paginated_objects(request, objects):
    paginator = Paginator(objects, 15)
    try:
        page = int(request.GET.get("p", "1"))
    except:
        page = 1

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    return objects


def filter_books(request):
    books = Book.objects.all()
    try:
        if request.POST['author']:
            authors = Author.objects.filter(name__contains=request.POST['author'])
            if len(authors) > 0:
                books = authors[0].book_set.all()
        if request.POST['publisher']:
            books = books.filter(publisher__name__contains=request.POST['publisher'])
        if request.POST['ISBN']:
            books = books.filter(ISBN__contains=request.POST['ISBN'])
        if request.POST['title']:
            books = books.filter(title__contains=request.POST['title'])
        if request.POST['year']:
            books = books.filter(release_year=int(request.POST['year']))
    except Exception as e:
        raise e
        # books = None
    return books if len(books) < Book.objects.all().count() else None

# Views za gledanje na bibliotekata
def index(request):
    """
    Metod za listanje na site knigi
    """
    if request.method == 'POST':
        books = get_paginated_objects(request, filter_books(request))
    else:
        books = get_paginated_objects(request, Book.objects.all())

    data = {
        'knigi': books,
        'heading': 'Листа на сите книги во ХакЛаб КИКА'
    }
    return render(request, 'list_pages.html', data)


def view_book_details(request, k_id, _):
    """
    Metod za gledanje na detali na odredena kniga
    """
    book = get_object_or_404(Book, pk=k_id)
    tags = book.tags.split(',')
    tags = [t.strip() for t in tags if t != ''] if len(tags) > 0 else None
    heading = '"'+ book.title + u'" од ' + u', '.join([a.name for a in book.authors.all()])
    rentals = book.rental_set.filter(returned_on=None)
    return render(request, 'detali.html',
            {'kniga':book, 'heading':heading, 'tags':tags, 'rentals':rentals})


def by_year(request, godina):
    """
    Metod za listanje na site knigi od godina
    """
    books = Book.objects.filter(release_year=godina)
    books = get_paginated_objects(request, books)
    return render(request, 'list_pages.html',
            {'knigi':books, 'heading':'Листа на сите книги од ' + str(godina) +' година'})


def by_tag(request, tag):
    """
    Metod za listanje na site knigi spored odbran tag
    """
    books = Book.objects.filter(tags__contains=tag)
    books = get_paginated_objects(request, books)
    return render(request, 'list_pages.html',
            {'knigi':books, 'heading':u'Листа на сите книги со клучен збор \"'+tag+'\"'})


def by_author(request, a_id):
    """
    Metod za listanje na site knigi od avtor
    """
    author = get_object_or_404(Author, pk=a_id)
    books = get_paginated_objects(request, author.book_set.all())
    return render(request, 'list_pages.html',
            {'knigi':books, 'heading':u'Листа на сите книги од \"'+author.name+'\"'})


def by_publisher(request, p_id):
    """
    Metod za listanje na site knigi od izdavac
    """
    publisher = get_object_or_404(Publisher, pk=p_id)
    books = get_paginated_objects(request, publisher.book_set.all())
    return render(request, 'list_pages.html',
            {'knigi':books, 'heading':u'Листа на сите книги од \"'+publisher.name+'\"'})


@login_required
@permission_required('biblioteka.can_add_rental', login_url=settings.LOGIN_URL)
def rent_book(request, k_id):
    """
    Metod za iznajmuvanje na kniga na user.
    requestot mora da se napravi od korisnik so can_add_rental permisija
    """
    book = get_object_or_404(Book, pk=k_id)
    if request.method == 'POST':
        if book.in_stock > 0:
            # kreiranje na forma so podatocite zemeni od POST
            form = RentalForm(request.POST)
            if form.is_valid():
                # korisnikot na koj mu se iznajmuva knigata
                user = form.cleaned_data['user']
                Rental.default.rent_book(user, book)
                index_url = reverse('biblioteka_index')
                return HttpResponseRedirect(index_url)
        else:
            h = 'Нема преостанати копии :('
            return render(request, 'rent.html', {'heading':h, 'book':book})
    else:
        form = RentalForm()
        field = form.fields['user']
        qs = User.objects.exclude(rental__book=book, rental__returned_on=None)

        if qs.count() > 0:
            field.queryset = qs

    data = {
        'form': form,
        'heading': 'Изнајмување на \"'+book.title+'\"',
        'book': book,
    }
    return render(request, 'rent.html', data)


@login_required
@permission_required('biblioteka.can_change_rental')
def return_book(request, k_id):
    """
    Metod za vrakjanje na rezervirana kniga
    """
    # import na datetime za da se zapise vremeto na vrakjanje
    from datetime import datetime
    kniga = get_object_or_404(Book, pk=k_id)
    # zemanje na site korisnici koi ja imaat iznajmeno knigata (ako ima poveke kopii)
    users = User.objects.filter(rental__book=kniga, rental__returned_on=None)

    if request.method=="POST" and request.POST.has_key("return_book"):
        # kreiranje na forma so podatocite zemeni od POST
        form = RentalForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            Rental.default.return_book(user, kniga)
    else:
        form = RentalForm()
        qs = User.objects.filter(rental__book=kniga, rental__returned_on=None)

        if qs.count() > 0:
            field = form.fields['user']
            field.queryset = qs
        return render_to_response(request, 'return.html', {'kniga':kniga, 'form':form})
    return HttpResponseRedirect(reverse('biblioteka_index'))


# @permission_required('biblioteka.can_add_rental', login_url=settings.LOGIN_URL)
@login_required
def reserved_books(request, p=None):
    """
    Metod za listanje na site rezervirani knigi.
    Potrebna e permisija za dodavanje na rental.
    """
    if not p and request.user.has_perm('can_add_rental'):
        reservations = Reservation.objects.all()
    else:
        reservations = Reservation.objects.filter(reserved_by=request.user)
    if request.method == 'POST':
        try:
            reservations = reservations.filter(book__ISBN__contains=request.POST['ISBN'])
        except:
            pass
    dates = reservations.dates('reserved_on', 'month')
    return render_to_response(request, 'res_list.html',
            {'reservations':reservations, 'heading':'Листа на сите резервирани книги', 'dates':dates})


@login_required
def reserve_book(request):
    """
    Metod za rezerviranje na kniga od user-ot koj go pravi requestot.
    """
    if request.method == 'POST' and request.POST.has_key("kniga_id"):
        try:
            kniga = get_object_or_404(Book, pk=request.POST['kniga_id'])
            Reservation.objects.create(reserved_by=request.user, book=kniga)
        except ReservationExists:
            # za ovde treba da se napravi template vo koj ke stoi deka knigata e rezervirana
            pass
    return HttpResponseRedirect(reverse('hacklab.biblioteka.views.reserved_books', kwargs={'p':'p'}))


@login_required
def remove_reservation(request):
    k = {}
    import urllib2
    # check if request is comming from personal reservations or all reservations
    if urllib2.urlparse.urlsplit(request.META['HTTP_REFERER']).path == '/biblioteka/reservations/p/':
        k = {'p':'p'}

    if request.method == 'POST' and request.POST.has_key('reservation_id'):
        r = Reservation.objects.get(pk=request.POST['reservation_id'])
        if r.reserved_by == request.user or request.user.is_superuser:
            r.delete()
    return HttpResponseRedirect(reverse('hacklab.biblioteka.views.reserved_books', kwargs=k))


def history(request, rented_by=None, year=None, month=None):
    isbn = None
    if request.method == 'POST':
        try:
            isbn = request.POST['ISBN'].strip()
        except:
            pass

    if rented_by is None:
        if request.user.has_perm('can_add_rental'):
            rental_list = Rental.default.get_rental_list(year=year, month=month, ISBN=isbn)
        else:
            rental_list = Rental.default.get_rental_list(user=request.user, year=year, month=month, ISBN=isbn)
    else:
        rental_list = Rental.default.get_rental_list(user=rented_by, year=year, month=month, ISBN=isbn)
    dates = rental_list.dates('rented_on', 'month')
    path = "/".join(request.path.split('/')[1:3])
    return render_to_response(request, 'history.html', {'list':rental_list, 'dates':dates, 'path':path})


@login_required
def my_history(request, year=None, month=None):
    return history(request, rented_by=request.user, year=year, month=month)


