#!/usr/bin/python
# -*- coding=utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from hacklab.biblioteka.models.books import Book


class ReservationExists(Exception):
    pass


class ReservationManager(models.Manager):
    """
    Manager for the active reservations
    """
    def all_ordered(self, *args, **kwargs):
        return super(ReservationManager, self).all().order_by("-reserved_on")

    def get_query_set(self):
        return super(ReservationManager, self).get_query_set().filter(active=True)

    def remove_reservation(self, r_id=None, user=None, book=None):
        """
        Function for removing a reservation.
        """
        try: # if the reservation exists remove it
            if user and book is not None:
                reservation = self.get(reserved_by=user, book=book)
            elif r_id is not None:
                reservation = self.get(pk=r_id)
            reservation.delete()
        except Exception as e:
            pass


class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reserved_by = models.ForeignKey(
            User, related_name="reservations", on_delete=models.CASCADE)
    reserved_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    objects = ReservationManager()

    class Meta:
        db_table = 'biblioteka_reservation'

    def __unicode__(self):
        return "%s - %s" % (self.reserved_by.get_full_name() or self.reserved_by, self.reserved_on.strftime("%d.%m.%Y %H:%Mh"))

    def save(self, *args, **kwargs):
        try: # if the reservation exists remove it
            r = Reservation.objects.get(
                    reserved_by=self.reserved_by, book=self.book, active=True)
            raise ReservationExists("User %s has an active reservation on %s" %
                    (self.reserved_by.username, self.book.title))
        except Reservation.DoesNotExist:
            # call original models.Model save method
            super(Reservation, self).save(*args, **kwargs)
