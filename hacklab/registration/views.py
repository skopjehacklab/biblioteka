from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from hacklab.registration.forms import RegistrationForm, EditAccountForm
from hacklab.registration.models import RegistrationProfile


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = RegistrationProfile.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                name=form.cleaned_data['first_name'],
                surname=form.cleaned_data['last_name']
            )
            return HttpResponseRedirect(reverse('registrationsuccess'))
    else:
        form = RegistrationForm()
    return render(request, 'registration_form.html', {'form': form})


def edit_account(request):
    if request.method == 'POST':
        form = EditAccountForm(request.POST)
        if form.is_valid():
            u = User.objects.get(pk=request.user.id)
            u.first_name = form.cleaned_data['first_name']
            u.last_name = form.cleaned_data['last_name']
            u.email = form.cleaned_data['email']
            u.save()
    else:
        data = {
            'username':request.user.username,
            'first_name':request.user.first_name,
            'last_name':request.user.last_name,
            'email':request.user.email,
        }
        form = EditAccountForm(data)

    return render(request, 'edit_account.html', {'form':form})
