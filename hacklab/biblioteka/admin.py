from hacklab.biblioteka.models import Author, Book, Language, Publisher
from django.contrib import admin


class BookAdmin(admin.ModelAdmin):
    exclude = ['slug', 'image']

admin.site.register(Book, BookAdmin)
admin.site.register(Author)
admin.site.register(Language)
admin.site.register(Publisher)
