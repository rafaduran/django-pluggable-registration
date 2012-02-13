.. _default-backend:
.. module:: registration.backends.default

The default backend
===================

A default :ref:`registration backend <backend-api>` is bundled with
django-registration, as the class
``registration.backends.default.DefaultBackend``, and implements a
simple two-step workflow in which a new user first registers, then
confirms and activates the new account by following a link sent to the
email address supplied during registration.


Default behavior and configuration
----------------------------------

This backend makes use of the following settings:

``ACCOUNT_ACTIVATION_DAYS``
    This is the number of days users will have to activate their
    accounts after registering. Failing to activate during that period
    will leave the account inactive (and possibly subject to
    deletion). This setting is required, and must be an integer.

``REGISTRATION_OPEN``
    A boolean (either ``True`` or ``False``) indicating whether
    registration of new accounts is currently permitted. This setting
    is optional, and a default of ``True`` will be assumed if it is
    not supplied.

``ACTIVATION_METHOD``
    A string representing a dotted Python import path to a callable object
    that will be passed as a ``callback`` argument to
    :meth:`~registration.models.RegistrationManager.activate_user`, which call
    it after checking and marking as already activated the
    :class:`~registration.models.RegistrationProfile` object corresponding to the
    given ``activation_key``. This can be overriden by passing the keyword
    argument ``activation_method`` to the :func:`~registration.views.activate`.

``REGISTRATION_FORM``
    A string representing a dotted Python import path to a an object that must
    be a subclass of :class:`~django.forms.Form`. This form its form class for
    user registration; this can be overridden by passing the keyword
    argument ``form_class`` to the :func:`~registration.views.register`
    view.

``ACTIVATION_FORM``
    A string representing a dotted Python import path to an object that must
    be a subclass of :class:`~django.forms.Form`. This form its form class for
    user registration; this can be overridden by passing the keyword
    argument ``form_class`` to the :func:`~registration.views.activate`
    view.

Upon successful registration -- not activation -- the default redirect
is to the URL pattern named ``registration_complete``; this can be
overridden by passing the keyword argument ``success_url`` to the
:func:`~registration.views.register` view.

Upon successful activation, the default redirect is to the URL pattern
named ``registration_activation_complete``; this can be overridden by
passing the keyword argument ``success_url`` to the
:func:`~registration.views.activate` view.


How account data is stored for activation
-----------------------------------------

During registration, a new instance of
``registration.models.RegistrationProfile`` (see below) created to keep the
email of the new account. An email is then sent to the given email address,
containing a link the user must click to activate the account; at that point
the user must be created and/or activated via the given ``activation_method``.

.. currentmodule:: registration.models

.. class:: RegistrationProfile

   A simple representation of the information needed to activate a new
   user account. This is **not** a user profile; it simply provides a
   place to temporarily store the activation key and determine whether
   a given account has been activated.

   Has the following fields:

   .. attribute:: email

      A string representing user's email.

   .. attribute:: activation_key

      A 40-character ``CharField``, storing the activation key for the
      account. Initially, the activation key is the hexdigest of a
      SHA1 hash; after activation, this is reset to :attr:`ACTIVATED`.

   Additionally, one class attribute exists:

   .. attribute:: ACTIVATED

      A constant string used as the value of :attr:`activation_key`
      for accounts which have been activated.

   And the following methods:

   .. method:: activation_key_invalid()

      Determines whether this account's activation key has expired,
      and returns a boolean (``True`` if expired, ``False``
      otherwise). Uses the following algorithm:

      1. If :attr:`activation_key` is :attr:`ACTIVATED`, the account
         has already been activated and so the key is considered to
         have expired. This test is performed by 
         :meth:`activation_key_expired`.

      2. Otherwise, the date of registration (obtained from the
         ``date_joined`` field of :attr:`user`) is compared to the
         current date; if the span between them is greater than the
         value of the setting ``ACCOUNT_ACTIVATION_DAYS``, the key is
         considered to have expired. This test is performed by
         :meth:`activation_key_already_activated`.

      :rtype: bool

   .. method:: activation_key_already_activated()
      
      See :meth:`activation_key_invalid` for further information.

      :rtype: bool

   .. method:: activation_key_expired()

      See :meth:`activation_key_invalid` for further information.

      :rtype: bool

   .. method:: send_activation_email(site)

      Sends an activation email to the email address :attr:`email`.

      The activation email will make use of two templates:
      ``registration/activation_email_subject.txt`` and
      ``registration/activation_email.txt``, which are used for the
      subject of the email and the body of the email,
      respectively. Each will receive the following context:

      ``activation_key``
          The value of :attr:`activation_key`.

      ``expiration_days``
          The number of days the user has to activate, taken from the
          setting ``ACCOUNT_ACTIVATION_DAYS``.

      ``site``
          An object representing the site on which the account was
          registered; depending on whether ``django.contrib.sites`` is
          installed, this may be an instance of either
          ``django.contrib.sites.models.Site`` (if the sites
          application is installed) or
          ``django.contrib.sites.models.RequestSite`` (if
          not). Consult `the documentation for the Django sites
          framework
          <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_
          for details regarding these objects' interfaces.

      Because email subjects must be a single line of text, the
      rendered output of ``registration/activation_email_subject.txt``
      will be forcibly condensed to a single line.

      :param site: An object representing the site on which account
         was registered.
      :type site: ``django.contrib.sites.models.Site`` or
        ``django.contrib.sites.models.RequestSite``
      :rtype: ``None``


Additionally, :class:`RegistrationProfile` has a custom manager
(accessed as ``RegistrationProfile.objects``):


.. class:: RegistrationManager

   This manager provides several convenience methods for creating and
   working with instances of :class:`RegistrationProfile`:

   .. method:: activate_user(activation_key)

      Validates ``activation_key`` and, if valid, activates the
      ``callback`` callable parameter is called, performing it the
      actions needed in order to get the new user account created and/or
      activated.field. To prevent re-activation of accounts, the
      :attr:`~RegistrationProfile.activation_key` of the
      :class:`RegistrationProfile` for the account will be set to
      :attr:`RegistrationProfile.ACTIVATED` after successful
      activation.

      Returns a two-tuple containing:
      
      1. On success returns ``callback`` result:
      
         ``User``: object representing the new user account.
         
         ``error_message``: on success this attribute will be
         ignored, however for convenience it should be ``None``.

      2. On failure:

         ``falsy_value``: any value that evaluates to ``False``
         on boolean context.

         ``error_message``: a string contatining the error message
         to be displayed.

      :param activation_key: The activation key to use for the
         activation.
      :type activation_key: string, a 40-character SHA1 hexdigest
      :param callback: The callable actually performing the activation.
      :type callback: callable
      :param \*\*kwargs: Extra keyword arguments for ``callback``.
      :type \*\*kwargs: ``dict``
      :rtype: ``tuple``

   .. method:: delete_expired(queryset=None)

      Removes expired instances of :class:`RegistrationProfile` from the
      database. This is useful as a periodic maintenance task to clean
      out profiles which registered but never activated.

      Profiles to be deleted are identified by searching for instances
      of :class:`RegistrationProfile` on the given queryset with expired
      activation keys. If no queryset is provided then all objects will
      be tested.

      :param queryset: A queryset containing :class:`RegistrationProfile`
         objects to be tested for deletion.
      :type queryset: :class:`django.db.models.query.QuerySet`
      :rtype: ``None``

   .. method:: delete_activated(queryset=None)

      Removes already activated instances of :class:`RegistrationProfile` from
      the database. This is useful as a periodic maintenance task to clean
      out activated profiles.

      Profiles to be deleted are identified by searching for instances
      of :class:`RegistrationProfile` on the given queryset activated
      activation keys. If no queryset is provided then all objects will
      be tested.

      :param queryset: A queryset containing :class:`RegistrationProfile`
         objects to be tested for deletion.
      :type queryset: :class:`django.db.models.query.QuerySet`
      :rtype: ``None``

   .. method:: create_profile(site, email, send_email=True)

      Creates and returns a :class:`RegistrationProfile` instance for
      the given ``email``.

      The :class:`RegistrationProfile` created by this method will have its
      :attr:`~RegistrationProfile.activation_key` set to a SHA1 hash
      generated from a combination of the ``email`` and a random salt.

      If ``send_email`` is ``True`` (default value) an email will be sent
      to the address ``email`` via :meth:`send_email`.

      :param site: An object representing the site on which account
         was registered.
      :type site: ``django.contrib.sites.models.Site`` or
        ``django.contrib.sites.models.RequestSite``
      :param email: An string representing the new user email address.
      :type email: ``string``
      :param send_email: Boolean object indicating wether an email should be
         sent.
      :type send_email: bool
      :rtype: :class:`RegistrationProfile`
