import re

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    """
    Custom forma za registracija na korisnici.
    """
    username = forms.CharField(label='Username', max_length=30)
    first_name = forms.CharField(label='Име', max_length=30)
    last_name = forms.CharField(label='Презиме', max_length=30)
    email = forms.EmailField(label='email', max_length=75)
    password1 = forms.CharField(label='Лозинка', max_length=20,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Лозинка (повторно)', max_length=20,
                                widget=forms.PasswordInput)
    tos = forms.BooleanField()

    def clean(self):
        """
        Функција за валидација на формата.
        """
        cleaned_data = self.cleaned_data
        passwd = [cleaned_data.get("password1"), cleaned_data.get("password2")]
        if passwd[0] != passwd[1]:
            raise forms.ValidationError(u"Лозинките мора да се совпаѓаат!")
            message = u"Лозинките мора да се совпаѓаат!"
            self._errors["password1"] = ErrorList([message])
        return cleaned_data


    def clean_username(self):
        """
        Validator функција која проверува дали внесениот username постои.
        """
        username = self.cleaned_data['username']
        if not re.match("[a-zA-Z0-9]", username):
            msg = "Корисничкото име треба да содржи само букви и броеви."
            raise forms.ValidationError(msg)

        try:
            # ako postoi raise exception
            u = User.objects.get(username=username)
            msg = "Корисник со корисничкото име \"{}\" веќе постои."
            raise forms.ValidationError(msg.format(u.username))
        except User.DoesNotExist:
            # ako ne postoi, t.e. ako User.objects.get(username=username)
            # frli exception User.DoesNotExist prodolzi uspesno
            return self.cleaned_data['username']

    def clean_email(self):
        """
        Validator функција која проверува дали внесениот email постои.
        """
        email = self.cleaned_data['email']
        try:
            u = User.objects.get(email=email)
            msg = "Некој друг ја користи адресата \"{}\"."
            raise forms.ValidationError(msg.format(u.username))
        except User.DoesNotExist:
            return self.cleaned_data['email']


class EditAccountForm(forms.Form):
    first_name = forms.CharField(label=u'Име', max_length=30)
    last_name = forms.CharField(label=u'Презиме', max_length=30)
    email = forms.EmailField(label=u'email', max_length=75)
