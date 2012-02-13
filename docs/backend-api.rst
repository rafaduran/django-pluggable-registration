.. _backend-api:

User registration backends
==========================

At its core, django-pluggable-registration is built around the idea of pluggable
backends which can implement different workflows for user
registration. Although :ref:`the default backend <default-backend>`
uses a common two-phase system (registration followed by activation),
backends are generally free to implement any workflow desired by their
authors.

This is deliberately meant to be complementary to Django's own
`pluggable authentication backends
<http://docs.djangoproject.com/en/dev/topics/auth/#other-authentication-sources>`_;
a site which uses an OpenID authentication backend, for example, can
and should make use of a registration backend which handles signups
via OpenID. And, like a Django authentication backend, a registration
backend is simply a class which implements a particular standard API
(described below).

This allows for a great deal of flexibility in the actual workflow of
registration; backends can, for example, implement any of the
following (not an exhaustive list):

* One-step (register, and done) or multi-step (register and activate)
  signup.

* Invitation-based registration.

* Selectively allowing or disallowing registration (e.g., by requiring
  particular credentials to register).

* Enabling/disabling registration entirely.

* Registering via sources other than a standard username/password,
  such as OpenID.

* Selective customization of the registration process (e.g., using
  different forms or imposing different requirements for different
  types of users).


Specifying the backend to use
-----------------------------

To determine which backend to use, the :ref:`views in
django-registration <views>` accept a keyword argument ``backend``; in
all cases, this should be a string containing the full dotted Python
import path to the backend class to be used. So, for example, to use
the default backend, you'd pass the string
``'registration.backends.default.DefaultBackend'`` as the value of the
``backend`` argument (and the default URLconf included with that
backend does so). The specified backend class will then be imported
and instantiated by calling its constructor with the \*\*kwargs on
`views in django-registration <views>`, thus you can pass any argument
you need just overriding URLconf, and the resulting instance will be used
for all backend-specific functionality.

If the specified backend class cannot be imported, django-registration
will raise ``django.core.exceptions.ImproperlyConfigured``.


Backend API
-----------

To be used as a registration backend, a class must implement the
following methods. For many cases, subclassing the default backend and
selectively overriding behavior will be suitable, but for other
situations (e.g., workflows significantly different from the default)
a full implementation is needed.


register(request, \*\*kwargs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method implements the logic of actually creating a new registration
profile for the given email.

This method will only be called after a signup form has been
displayed, and the data collected by the form has been properly
validated.

Arguments to this method are:

``request``
    The Django `HttpRequest
    <http://docs.djangoproject.com/en/dev/ref/request-response/#httprequest-objects>`_
    object in which a new user is attempting to register.

``**kwargs``
    A dictionary of the ``cleaned_data`` from the signup form.

After creating the new registration profile, this method should return a
``RegistrationProfile`` instance.


activate(request, activation_key, \*\*kwargs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For workflows which require a separate activation step, this method
should implement the necessary logic for account creation and/or
activation.

Arguments to this method are:

``request``
    The Django ``HttpRequest`` object in which the account is being
    activated.

``**kwargs``
    A dictionary of any additional arguments (e.g., information
    captured from the URL, such as an activation key) received by the
    :func:`~registration.views.activate` view. The combination of the
    ``HttpRequest`` and this additional information must be sufficient
    to create the new account.

If the account cannot be successfully activated (for example, in the
default backend if the activation period has expired), this method
should return two-tuple containing (``falsy_value``, ``error_message``),
where ``falsy_value`` is any value that evaluates to ``False`` in
boolean context.

If the account is successfully created/activated, this method should return
a two-tuple (``truly_value``, ``whatever``), where ``truly_value`` is an object
that evaluates to ``True`` on boolean context and represents the activated
account; second value in this case.

For workflows which do not require a separate activation step, this
method can and should raise ``NotImplementedError``.


registration_allowed(request)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method returns a boolean value indicating whether the given
``HttpRequest`` is permitted to register a new account (``True`` if
registration is permitted, ``False`` otherwise). It may determine this
based on some aspect of the ``HttpRequest`` (e.g., the presence or
absence of an invitation code in the URL), based on a setting (in the
default backend, a setting can be used to disable registration),
information in the database or any other information it can access.

Arguments to this method are:

``request``
    The Django ``HttpRequest`` object in which a new user is
    attempting to register.

If this method returns ``False``, the
:func:`~registration.views.register` view will not display a form for
account creation; instead, it will issue a redirect to a URL
explaining that registration is not permitted.


get_form_class(request)
~~~~~~~~~~~~~~~~~~~~~~~

This method should return a form class -- a subclass of
``django.forms.Form`` -- suitable for use in registering users with
this backend. As such, it should collect and validate any information
required by the backend's ``register`` method.

Arguments to this method are:

``request``
    The Django ``HttpRequest`` object in which a new user is
    attempting to register.

get_activation_form_class(request)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method should return a form class -- a subclass of
``django.forms.Form`` -- suitable for use in activating users with
this backend. As such, it should collect and validate any information
required by the backend's ``activate`` method.

Arguments to this method are:

``request``
    The Django ``HttpRequest`` object in which a new user is
    attempting to activate.


post_registration_redirect(request, user)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method should return a location to which the user will be
redirected after successful registration. This should be a tuple of
``(to, args, kwargs)``, suitable for use as the arguments to `Django's
"redirect" shortcut
<http://docs.djangoproject.com/en/dev/topics/http/shortcuts/#redirect>`_.

Arguments to this method are:

``request``
    The Django ``HttpRequest`` object in which the user registered.

``user``
    The ``User`` instance representing the new user account.


post_activation_redirect(request, user)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For workflows which require a separate activation step, this method
should return a location to which the user will be redirected after
successful activation.  This should be a tuple of ``(to, args,
kwargs)``, suitable for use as the arguments to `Django's "redirect"
shortcut
<http://docs.djangoproject.com/en/dev/topics/http/shortcuts/#redirect>`_.

Arguments to this method are:

``request``
    The Django ``HttpRequest`` object in which the user activated.

``user``
    An object instance representing the activated user account.

For workflows which do not require a separate activation step, this
method can and should raise ``NotImplementedError``.
