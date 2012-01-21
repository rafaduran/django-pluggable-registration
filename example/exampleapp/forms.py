from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationForm, ActivationForm

class ExampleRegistrationForm(RegistrationForm):
    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']).\
            count():
            raise forms.ValidationError(_(u"This email address is already in "
                "use. Please supply a different email address."))
        return self.cleaned_data['email']


class ExampleActivationForm(ActivationForm):
    username = forms.RegexField(regex=r'^[\w.@+-]+$', max_length=30,
            widget=forms.TextInput(attrs={'class': 'required'}),
            label=_("Username"), error_messages={'invalid': _("This value "
            "must contain only letters, numbers and underscores.")})

    def clean_username(self):
        try:
            _ = User.objects.get(username__iexact=self.\
                    cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("A user with that username already "
                                        "exists."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't"
                                                " match."))
        return self.cleaned_data


REGISTRATION_FORM = ExampleRegistrationForm
ACTIVATION_FORM = ExampleActivationForm
