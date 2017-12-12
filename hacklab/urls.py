from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


from hacklab.registration.urls import urlpatterns as reg_urls
from hacklab.biblioteka.urls import urlpatterns as bib_urls


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),

    path('accounts/', include((reg_urls, 'registration',))),
    path('biblioteka/', include((bib_urls, 'biblioteka',))),


    path('admin/', admin.site.urls),
]
