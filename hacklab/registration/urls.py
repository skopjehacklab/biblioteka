from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect

from hacklab.registration import views as reg_views


app_name = 'registration'


urlpatterns = [
    path('',
         login_required(
             TemplateView.as_view(
                 template_name='profile.html')),
         name='profile'),

    path('login/',
         auth_views.LoginView.as_view(
             template_name='login.html'),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(
             template_name='logout.html'),
         name='logout'),

    path('reset_password/',
         csrf_protect(
             auth_views.PasswordResetView.as_view(
                 template_name='password_reset_form.html')),
         name='password-reset'),

    path('reset_password/success/',
         login_required(
             auth_views.PasswordResetDoneView.as_view(
                 template_name='password_reset_done.html')),
         name='password-reset-done'),

    re_path('reset_password/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            csrf_protect(
                auth_views.PasswordResetConfirmView.as_view(
                    template_name='password_reset_confirm.html')),
            name='password-reset-confirm'),

    path('reset_password/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'),
         name='password-reset-complete'),

    path('change_password/',
         login_required(
             csrf_protect(
                 auth_views.PasswordChangeView.as_view(
                     template_name='password_change.html'))),
         name='password-change'),

    path('change_password/success/',
         login_required(
             auth_views.PasswordChangeDoneView.as_view(
                 template_name='password_change_done.html')),
         name='password-change-done'),

    path('registration/success/',
         TemplateView.as_view(
             template_name='registration_complete.html'),
         name='registration-complete'),

    path('edit/', reg_views.edit_account, name='edit-profile'),
    path('registration/', reg_views.register, name='register'),
]
