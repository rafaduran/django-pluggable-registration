"""
Forms and validation code for user registration.

"""
import abc

from django import forms
from django.utils.translation import ugettext_lazy as _


# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = {'class': 'required'}

class RegistrationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                    maxlength=75)))

    def clean_email(self):
        pass
    clean_email = abc.abstractmethod(clean_email) 


class ActivationForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
        render_value=False), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
        render_value=False), label=_("Password (again)"))

    def clean(self):
        pass
    clean = abc.abstractmethod(clean)
