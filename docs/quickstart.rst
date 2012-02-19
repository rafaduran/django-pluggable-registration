.. _quickstart:

Quick start guide
=================

Before installing django-pluggable-registration, you'll need to have a copy of
`Django <http://www.djangoproject.com>`_ already installed. For the
|version| release, Django 1.1 or newer is required.

For further information, consult the `Django download page
<http://www.djangoproject.com/download/>`_, which offers convenient
packaged downloads and installation instructions.


Installing django-pluggable-registration
----------------------------------------

At the time of this writing, django-pluggable-registration cab be installed
obly via `GitHub repository
<https://github.com/rafaduran/django-pluggable-registration>`_.

It is also highly recommended that you learn to use `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ for development and
deployment of Python software; ``virtualenv`` provides isolated Python
environments into which collections of software (e.g., a copy of
Django, and the necessary settings and applications for deploying a
site) can be installed, without conflicting with other installed
software. This makes installation, testing, management and deployment
far simpler than traditional site-wide installation of Python
packages.


Automatic installation via a package manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``pip``, type::

    pip install -e https://github.com/rafaduran/django-plugglabe-registration#egg=django-pluggable-registration


Manual installation from a downloaded package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer not to use an automated package installer, you can
download a copy of django-pluggable-registration and install it manually. The
latest release package can be downloaded from `django-pluggable-registration's
repository <https://github.com/rafaduran/django-pluggable-registration/tree/
master/tarball>`_.

Once you've downloaded the package, unpack it and then you can use the included
``setup.py`` installation script. From a command line type::

    python setup.py install

Note that on some systems you may need to execute this with
administrative privileges (e.g., ``sudo python setup.py install``).


Basic configuration and use
---------------------------

Once installed, you can add django-pluggable-registration to any Django-based
project you're developing. The default setup will enable user registration
with the following workflow:

1. A user signs up for an account by supplying an email.

2. An activation key is generated, associated to the given email and stored,
   and an email is sent to the user containing a link to click to activate
   the account.

3. Upon clicking the activation link, a form is diplayed, asking all extra
   required information for the new account is create.

4. Once form is properly validated an ``activation_method`` callback will
   perform any required action.

5. On succes activation user will be redirected to
   ``registration_activation_complete`` url.

Note that while using the default backend it is recommended that
``django.contrib.sites`` be installed. You will also need to have a working mail
server (for sending activation emails), and provide Django with the necessary
settings to make use of this mail server (consult `Django's
email-sending documentation
<http://docs.djangoproject.com/en/dev/topics/email/>`_ for details).


Required settings
~~~~~~~~~~~~~~~~~

Begin by adding ``registration`` to the ``INSTALLED_APPS`` setting of
your project, and specifying one required additional setting:

``ACCOUNT_ACTIVATION_DAYS``
    This is the number of days users will have to activate their
    accounts after registering. If a user does not activate within
    that period, the account will remain permanently inactive and may
    be deleted by maintenance scripts provided in django-registration.

As optional settings you can also provide:

``ACTIVATION_METHOD``
   This is the callable callback performing any required action for
   the account creation.

``REGISTRATION_FORM``
   First form displayed, usually getting just the user email.

``ACTIVATION_FORM``
   Second form displayed, getting any extra required information, usually
   at least a password.

For example, you might have something like the following in your
Django settings file::

    INSTALLED_APPS = (
        'django.contrib.sites',
        'registration',
        # ...other installed applications...
    )
    
    ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
    ACTIVATIOM_METHOD = 'exampleapp.activation.activate' # Dotted string path
    REGISTRATION_FORM = 'exampleapp.forms.ExampleRegistrationForm'
    ACTIVATION_FORM = 'exampleapp.forms.ExampleActivationForm'

Once you've done this, run ``manage.py syncdb`` to install the model
used by the default setup.


Setting up URLs
~~~~~~~~~~~~~~~

The :ref:`default backend <default-backend>` includes a Django
``URLconf`` which sets up URL patterns for :ref:`the views in
django-registration <views>`. This ``URLconf`` can be found at
``registration.backends.default.urls``, and so can simply be included
in your project's root URL configuration. For example, to place the
URLs under the prefix ``/accounts/``, you could add the following to
your project's root ``URLconf``::

    (r'^accounts/', include('registration.backends.default.urls')),

Users would then be able to register by visiting the URL
``/accounts/register/``


Required templates
~~~~~~~~~~~~~~~~~~

In the default setup, you will need to create several templates
required by django-registration. The templates requires
by django-registration are as follows; note that, with the exception
of the templates used for account activation emails, all of these are
rendered using a ``RequestContext`` and so will also receive any
additional variables provided by `context processors
<http://docs.djangoproject.com/en/dev/ref/templates/api/#id1>`_.

**registration/registration_form.html**

Used to show the form users will fill out to register. By default, has
the following context:

``form``
    The registration form. This will be an instance of some subclass
    of ``django.forms.Form``; consult `Django's forms documentation
    <http://docs.djangoproject.com/en/dev/topics/forms/>`_ for
    information on how to display this in a template.

**registration/registration_complete.html**

Used after successful completion of the registration form. This
template has no context variables of its own, and should simply inform
the user that an email containing account-activation information has
been sent.

**registration/activate.html**

Displaying the activation form (if defined). With the default setup, has the
following context:

``activation_key``
    The activation key used during the activation attempt.

``form``
   The activation form. This will be an instance of some subclass of
    ``django.forms.Form``; consult `Django's forms documentation
    <http://docs.djangoproject.com/en/dev/topics/forms/>`_ for
    information on how to display this in a template.

**registration/activation_complete.html**

Used after successful account activation. This template has no context
variables of its own, and should simply inform the user that their
account has been created.

**registration/activation_email_subject.txt**

Used to generate the subject line of the activation email. Because the
subject line of an email must be a single line of text, any output
from this template will be forcibly condensed to a single line before
being used. This template has the following context:

``activation_key``
    The activation key for the new account.

``expiration_days``
    The number of days remaining during which the account may be
    activated.

``site``
    An object representing the site on which the user registered;
    depending on whether ``django.contrib.sites`` is installed, this
    may be an instance of either ``django.contrib.sites.models.Site``
    (if the sites application is installed) or
    ``django.contrib.sites.models.RequestSite`` (if not). Consult `the
    documentation for the Django sites framework
    <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_ for
    details regarding these objects' interfaces.

**registration/activation_email.txt**

Used to generate the body of the activation email. Should display a
link the user can click to activate the account. This template has the
following context:

``activation_key``
    The activation key for the new account.

``expiration_days``
    The number of days remaining during which the account may be
    activated.

``site``
    An object representing the site on which the user registered;
    depending on whether ``django.contrib.sites`` is installed, this
    may be an instance of either ``django.contrib.sites.models.Site``
    (if the sites application is installed) or
    ``django.contrib.sites.models.RequestSite`` (if not). Consult `the
    documentation for the Django sites framework
    <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_ for
    details regarding these objects' interfaces.


Note that the templates used to generate the account activation email
use the extension ``.txt``, not ``.html``. Due to widespread antipathy
toward and interoperability problems with HTML email,
django-registration defaults to plain-text email, and so these
templates should simply output plain text rather than HTML.


The ``example`` project
_______________________

The repository includes a working example project. **Note** this project is
using ``django.contrib.auth`` just for convenience, since
django-pluggable-registration as a shortcut for applications not fitting the
django-registration default workflow, specially applications not using the
``django.contrib.auth``.
