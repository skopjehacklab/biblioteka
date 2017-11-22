from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import logout
from django.contrib.auth.views import password_change
from django.contrib.auth.views import password_change_done
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect

from hacklab.registration import views


app_name = 'registration'


change_password = login_required(csrf_protect(password_change))
profile_view = TemplateView.as_view(template_name='profile.html')

urlpatterns = [
    path('', login_required(profile_view), name="account_profile"),

    path('edit/', views.edit_account),

    path('login/', LoginView.as_view(template_name='login.html')),
    path('logout/', logout, {'template_name': 'logout.html'}, name='logout'),

    path('reset_password/', csrf_protect(password_reset),
         {'template_name':"password_reset_form.html"},
         name="password_reset"),

    path('reset_password/success/', login_required(password_reset_done),
         name="password_reset_done"),

    path('reset_password/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
         csrf_protect(password_reset_confirm),
         {'template_name':'password_reset_confirm.html'},
         'password_reset_confirm'),

    path(r'^/reset_password/complete/$', password_reset_complete),

    path(r'^/change_password/$', change_password,
         {'template_name':'password_change.html'},
         name="change_password"),

    path(r'^/change_password/success/$', password_change_done,
         {'template_name': 'password_change_done.html'}),

    path('registration/', views.register, name='registration'),
    path('registration/success/',
         TemplateView.as_view(template_name='registration_complete.html'),
         name='registration_success'),
]
