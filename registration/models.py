import datetime
import random
import re

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired/already activated profiles.
    
    """
    def activate_user(self, request, activation_key, callback, **kwargs):
        """
        Validate an activation key and calls ``callback`` in order to activate
        the corresponding user if valid. ``callback`` default value is a
        callable got from importing ``ACTIVATION_METHOD`` settings string.
        
        If the key is valid, returns ``callback`` result two-tuple: (``User``
        instance, ``None``) on success or (falsy value, errors) on failure.
        
        If the key is invalid (already activated or expired), returns a
        two-tuple (``False``, 'Your activation key is not valid').
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``RegistrationProfile.ACTIVATED``
        after successful activation.

        Args:
            ``activation_key`` SHA1 hash string.
            ``request`` activate view request needed just for passing it to
                ``callback``.
            ``callback`` callable doing the activation process.
            ``kwargs`` extra key arguments for callback.
        Returns:
            Two-tuple containing the new user/account instance and ``None`` on
            success, falsy value and message error on failure.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False, _('Your activation key is not valid')
            if not profile.activation_key_invalid():
                account, errors = callback(request, profile, **kwargs)
                if account:
                    profile.activation_key = self.model.ACTIVATED
                    profile.save()
                return account, errors
        return False, _('Your activation key is not valid')

    def create_profile(self, site, email, send_email=True):
        """
        Create a ``RegistrationProfile`` for a given email, and return the
        ``RegistrationProfile``.
        
        The activation key for the ``RegistrationProfile`` will be a SHA1 hash,
        generated from a combination of the given email and a random salt.

        Args:
            ``site`` current site object, needed for sending activation email
            ``email`` string represeting email for the new profile
            ``send_email`` boolean value which determines whether email will be
                sent or not. Default value is ``True``.
        Returns:
            The new ``RegistrationProfile`` instance.
        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        activation_key = sha_constructor(salt+email).hexdigest()
        profile = self.create(email=email, activation_key=activation_key)
        if profile and send_email:
            profile.send_activation_email(site)
        return profile

    @staticmethod
    def delete_expired(queryset=None):
        """
        Deletes expired ``RegistrationProfile`` objects based on settings
        ``ACCOUNT_ACTIVATION_DAYS`` and current date.

        Args:
            ``queryset`` If a queryset is provided then only profiles in the
                given queryset will be tested, if no value is provided then all
                profiles will be tested. Default value is ``None``.
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        if queryset is None:
            queryset = RegistrationProfile.objects.all()
        for profile in queryset:
            if (profile.reg_time + expiration_date) <= datetime.datetime.now():
                profile.delete()

    @staticmethod
    def delete_activated(queryset=None):
        """
        Deletes already activated ``RegistrationProfile`` objects based on
        activation key and ``ACTIVATED`` value comparison.

        Args:
            ``queryset`` If a queryset is provided then only profiles in the
                given queryset will be tested, if no value is provided then all
                profiles will be tested. Default value is ``None``.
        """
        if queryset is None:
            queryset = RegistrationProfile.objects.all()
        for profile in queryset:
            if profile.activation_key == RegistrationProfile.ACTIVATED:
                profile.delete()


class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key and email for use during
    user account registration.
    
    Generally, you will not want to interact directly with instances
    of this model; the provided manager includes methods
    for creating and activating new accounts, as well as for cleaning
    invalid profiles.
    
    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
    so. This model's sole purpose is to store data temporarily during
    account registration and activation.
    
    """
    ACTIVATED = u"ALREADY_ACTIVATED"
    
    email = models.EmailField()
    activation_key = models.CharField(_('activation key'), max_length=40)
    reg_time = models.DateTimeField(_('registration time'), auto_now_add=True)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    def __unicode__(self):
        return u"Registration information for %s" % self.email
    
    def activation_key_invalid(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        is invalid.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.

        Returns:
            Boolean value.
        """
        return self.activation_key_already_activated() or \
            self.activation_key_expired() or False
    activation_key_invalid.boolean = True

    def activation_key_already_activated(self):
        """
        Determines whether this ``RegistrationProfile``'s activation key has
        been activated.

        Returns:
            Boolean value.
        """
        return self.activation_key == self.ACTIVATED
    activation_key_already_activated.boolean = True

    def activation_key_expired(self):
        """
        Determines whether this ``RegistrationProfile``'s activation key has
        expired.

        Returns:
            Boolean value.
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return (self.reg_time + expiration_date) <= datetime.datetime.now()
    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        """
        Send an activation email to the user associated with this
        ``RegistrationProfile``.
        
        The activation email will make use of two templates:

        ``registration/activation_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``registration/activation_email.txt``
            This template will be used for the body of the email.

        These templates will each receive the following context
        variables:

        ``activation_key``
            The activation key for the new account.

        ``expiration_days``
            The number of days remaining during which the account may
            be activated.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.models.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        Args:
            ``site`` the above explained ``site``
        """
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('registration/activation_email.txt',
                                   ctx_dict)
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
    
