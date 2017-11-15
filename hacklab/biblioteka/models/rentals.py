from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from hacklab.biblioteka.models.books import Book
from hacklab.biblioteka.models.reservations import Reservation


class RentalExists(Exception):
    pass


class BookNotInStock(Exception):
    pass


class ActiveRentalManager(models.Manager):
    """
    Manager for active rentals (Not yet returned).
    """
    def get_query_set(self):
        return super(ActiveRentalManager, self).get_query_set().filter(returned_on=None)

    def get_rental(self, user=None, book=None):
        if user is not None and book is not None:
            return self.get(rented_by=user, book=book)
        elif user is not None:
            return self.get(rented_by=user)
        elif book is not None:
            return self.get(book=book)

    class Meta:
        use_for_related_fields = True


class RentalManager(models.Manager):
    def get_rental_list(self, user=None, year=None, month=None, ISBN=None):
        if user is not None:
            rental_list = self.filter(rented_by=user)
        else:
            rental_list = self.all()
        if year is not None:
            rental_list = rental_list.filter(rented_on__year=year)
        if month is not None:
            rental_list = rental_list.filter(rented_on__month=month)
        if ISBN is not None:
            rental_list = rental_list.filter(book__ISBN__contains=ISBN.strip())
        return rental_list.order_by('-rented_on')

    def return_book(self, user, book):
        """
        Method for returning books.
        """
        r = self.get(rented_by=user, book=book, returned_on=None)
        r.returned_on = datetime.now()
        r.save()
        r.book.in_stock += 1
        r.book.save()

    def rent_book(self, user, book):
        """
        Method for renting books.
        Checks if the book is available and that the user doesn't have it at the moment.
        """
        if book.in_stock > 0:
            # check if the user has the book
            try:
                r = self.get(rented_by=user, book=book, returned_on=None)
                # if there is a rental by the user, raise a custom exception
                raise RentalExists("Book %s is already rented by %s" % (book.title, user.username))
            except Rental.DoesNotExist:
                # if the user doesn't have the book
                r = self.create(book=book, rented_by=user)
                r.save()
                # remove the reservation if it exists
                Reservation.objects.remove_reservation(user=user, book=book)
                book.in_stock -= 1
                book.save()
        else:
            # if the book isn't in stock raise a custom exception
            raise BookNotInStock("Book %s is out of stock!" % book.title)


class Rental(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    rented_on = models.DateTimeField(auto_now_add=True)
    returned_on = models.DateTimeField(null=True)

    default = RentalManager()
    objects = ActiveRentalManager()

    class Meta:
        db_table = 'biblioteka_rental'

    def __unicode__(self):
        rented_by = self.rented_by.get_full_name() or self.rented_by
        rented_on = self.rented_on.strftime("%d.%m.%Y %H:%Mh")
        return "{} - {}".format(rented_by, rented_on)
