import datetime

from django.contrib import admin
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from registration.models import RegistrationProfile


class RegistrationAdmin(admin.ModelAdmin):
    actions = ['resend_activation_email', 'delete_expired', 'delete_activated',
            'clean']
    list_display = ('email', 'activation_key_expired',
            'activation_key_already_activated', 'activation_key_invalid')
    search_fields = ('email',)


    def resend_activation_email(self, request, queryset):
        """
        Re-sends activation emails for the selected users.

        Note that this will *only* send activation emails for users
        who are eligible to activate; emails will not be sent to users
        whose activation keys have expired or who have already
        activated.
        
        """
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        for profile in queryset:
            if not profile.activation_key_invalid():
                profile.send_activation_email(site)
    resend_activation_email.short_description = _("Re-send activation emails")

    def delete_expired(self, request, queryset):
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        for profile in queryset:
            if (profile.reg_time + expiration_date) <= datetime.datetime.now():
                profile.delete()

    def delete_activated(self, request, queryset):
        for profile in queryset:
            if profile.activation_key == RegistrationProfile.ACTIVATED:
                profile.delete()

    def clean(self, request, queryset):
        self.delete_expired(request, queryset)
        self.delete_activated(request, queryset)

admin.site.register(RegistrationProfile, RegistrationAdmin)
