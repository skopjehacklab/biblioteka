from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib.auth.views import password_change
from django.contrib.auth.views import password_change_done
from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_reset_done
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.views import password_reset_complete
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect

from hacklab.registration.views import edit_account


change_password = login_required(csrf_protect(password_change))
profile_view = TemplateView.as_view(template_name='account/profile.html')

urlpatterns = [
    path('', login_required(profile_view), name="account_profile"),

    path('edit_account/', edit_account),

    path('login/', csrf_protect(login),
         {'template_name': 'account/login.html'}, name="user_login"),

    path('logout/', logout,
         {'template_name': 'account/logout.html'}),

    path('reset_password/', csrf_protect(password_reset),
         {'template_name':"registration/password_reset_form.html"},
         name="reset_password"),

    path('reset_password/success/', login_required(password_reset_done),
         name="reset_password_done"),

    path('reset_password/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
         csrf_protect(password_reset_confirm),
         {'template_name':'registration/password_reset_confirm.html'},
         'reset_password_confirm'),

    path(r'^/reset_password/complete/$', password_reset_complete),

    path(r'^/change_password/$', change_password,
         {'template_name':'account/password_change.html'},
         name="changepassword"),

    path(r'^/change_password/success/$', password_change_done,
         {'template_name': 'account/password_change_done.html'}),
]
