from django.urls import path
from django.views.generic import TemplateView

from hacklab.registration import views


urlpatterns = [
    path('', views.register),
    path('success/',
         TemplateView.as_view(template_name='registration_complete.html'),
         name='registrationsuccess'),
]
