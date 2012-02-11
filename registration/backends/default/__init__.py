from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration.models import RegistrationProfile


class DefaultBackend(object):
    """
    A registration backend which follows a simple workflow:

    1. User signs up via email only

    2. Email is sent to user with activation link.

    3. User clicks activation link -> an activation form is shown ->
        activate (based on pluggable callable on settings.ACTIVATION_METHOD)

    Using this backend requires that

    * ``registration`` be listed in the ``INSTALLED_APPS`` setting
      (since this backend makes use of models defined in this
      application).

    * The setting ``ACCOUNT_ACTIVATION_DAYS`` be supplied, specifying
      (as an integer) the number of days from registration during
      which a user may activate their account (after that period
      expires, activation will be disallowed).

    * The creation of the templates
      ``registration/activation_email_subject.txt`` and
      ``registration/activation_email.txt``, which will be used for
      the activation email. See the notes for this backends
      ``register`` method for details regarding these templates.

    Additionally, registration can be temporarily closed by adding the
    setting ``REGISTRATION_OPEN`` and setting it to
    ``False``. Omitting this setting, or setting it to ``True``, will
    be interpreted as meaning that registration is currently open and
    permitted.

    Internally, this is accomplished via storing an activation key in
    an instance of ``registration.models.RegistrationProfile``. See
    that model and its custom manager for full documentation of its
    fields and supported operations.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def register(self, request, **kwargs):
        """
        Given an email address and password, register a new
        ``RegistrationProfile``, containing the activation key which
        will be used for this account.

        An email will be sent to the supplied email address; this
        email should contain an activation link. The email will be
        rendered using two templates. See the documentation for
        ``RegistrationProfile.send_activation_email()`` for
        information about these templates and the contexts provided to
        them.
        """
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_profile = RegistrationProfile.objects.create_profile(site,
                kwargs['email'])
        return new_profile

    def activate(self, request, activation_key, **kwargs):
        """
        Given an an activation key, the ``activate`` view request adn any
        extra keyword, will call ``RegistrationManager.activate_user``
        specifying a callback for user activation.
        
        Returns:
            ``RegistrationManager.activate_user`` result (see models for
            further information).
        """
        return RegistrationProfile.objects.activate_user(activation_key,
                request, callback=self.activation_method, **kwargs)

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.
        
        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return self.registration_form

    def get_activation_form_class(self, request):
        """
        Return the default form class used for user activation.
        """ 
        return self.activation_form

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.
        
        """
        return ('registration_complete', (), {})

    def post_activation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        account activation.
        
        """
        return ('registration_activation_complete', (), {})
