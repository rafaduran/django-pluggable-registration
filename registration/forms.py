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
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        pass
    clean_email = abc.abstractmethod(clean_email) 


class ActivationForm(forms.Form):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=_("Password"))

    def clean_username(self):
        pass
    clean_username = abc.abstractmethod(clean_username)
