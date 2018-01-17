import os
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.urls import reverse


class Language(models.Model):
        name = models.CharField(u"Назив", max_length=20)
        iso_name = models.CharField(u"ISO-2 Кратенка", max_length=5)

        class Meta:
                db_table = 'biblioteka_language'

        def __str__(self):
                return "Јазик: {}".format(self.name)

class Author(models.Model):
        name = models.CharField("Име", max_length=150, help_text="Име на авторот")

        class Meta:
                db_table = 'biblioteka_author'

        def __str__(self):
                return "Автор: {}".format(self.name)


class Publisher(models.Model):
        name = models.CharField("Назив", max_length=30, help_text="Назив на издавачот")

        def __str__(self):
                return "Издавач: {}".format(self.name)


        class Meta:
                db_table = 'biblioteka_publisher'


class Book(models.Model):
        ISBN = models.CharField(max_length=30)
        title = models.CharField("Наслов", max_length=250, help_text="Наслов на книгата")
        slug = models.SlugField(max_length=250)
        release_year = models.IntegerField(
                        "Година", null=True, blank=True,
                        help_text="Година на издавање")
        lang = models.ForeignKey(
                        Language, null=True, blank=True,
                        help_text="Јазик", on_delete=models.CASCADE)
        publisher = models.ForeignKey(
                        Publisher, null=True, blank=True,
                        help_text="Издавач на книгата", on_delete=models.CASCADE)
        tags = models.CharField(
                        "Тагови", max_length=300, null=True, blank=True,
                        help_text="Сепаратор=запирка(,)")
        authors = models.ManyToManyField(Author, help_text="Авотри на книгата")
        description = models.CharField(
                        "Опис", max_length=500, null=True, blank=True,
                        help_text="опис на книгата")
        image = models.ImageField(
                        "Слика", upload_to='books/', null=True, blank=True,
                        help_text="Стави права слика (не фејк)!")
        external_image_url = models.URLField(
                        "Надворешна слика", null=True, blank=True,
                        help_text="Слика која ќе се чува на серверот")
        quantity = models.IntegerField(
                        "Количина", default=1,
                        help_text="Вкупна количина на книги")
        in_stock = models.IntegerField(
                        "Преостанати копии", default=1,
                        help_text="Колку вкупно копии има преостанато во библиотеката")
        # TODO (vladan): donated_by should be FK to a registered user
        donated_by = models.CharField(
                        "Донирана од", max_length=128, null=True, blank=True,
                        help_text="Од кого е донирана книгата")

        class Meta:
                db_table = 'biblioteka_book'

        def __unicode__(self):
                return self.title

        def get_absolute_url(self):
                return reverse('biblioteka:book_details',
                               args=[self.id, self.slug])

        def __str__(self):
                return "Книга: {}".format(self.title)

        def _calculate_ratio(self, old, new):
                # if width > height take width as referent dimnsion,
                # else take height and return the ratio
                if old[0] > old[1]:
                        ratio = float(new[0]) / float(old[0])
                else:
                        ratio = float(new[1]) / float(old[1])
                return ratio

        # ******************************************************************
        # OSTANA USTE DA SE DOPRAVI ZA UPLOAD NA SLIKA
        # ******************************************************************
        def _resize_and_save(self, width, height):
                new_dims = (width, height)
                try:
                        from PIL import Image
                        import cStringIO
                        import urllib2
                        img = Image.open(cStringIO.StringIO(urllib2.urlopen(self.external_image_url).read()))
                        ratio = self._calculate_ratio(img.size, new_dims)
                        new_dims = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                        img = img.resize(new_dims)
                        filepath = '%s/books/%s' % (settings.MEDIA_ROOT, os.path.basename(self.external_image_url))
                        img.save(filepath)
                        return filepath
                except ValueError as e:
                        raise e

        def save(self, *args, **kwargs):
                if self.external_image_url:
                        try:
                                filepath = self._resize_and_save(200, 300)
                                self.external_image_url = None
                                self.image.save(filepath, File(open(filepath, "rb")))
                        except:
                                pass
                elif self.external_image_url is None and self.image is None:
                        filepath = os.path.join(settings.MEDIA_ROOT, '/books/default.png')
                        self.image.save(filepath, File(open(filepath, "rb")))
                # create slug from title
                self.slug = ""
                for c in self.title.strip():
                        if c in [" ", ".", ",", "'", "`", '"']:
                                self.slug += "-"
                                continue
                        self.slug += c
                # call original models.Model save method
                super(Book, self).save(*args, **kwargs)
