.. _faq:

Frequently-asked questions
==========================

The following are miscellaneous common questions and answers related
to installing/using django-registration, culled from bug reports,
emails and other sources.


General
-------

**What license is django-registration under?**
    django-registration is offered under a three-clause BSD-style
    license; this is `an OSI-approved open-source license
    <http://www.opensource.org/licenses/bsd-license.php>`_, and allows
    you a large degree of freedom in modifiying and redistributing the
    code. For the full terms, see the file ``LICENSE`` which came with
    your copy of django-registration; if you did not receive a copy of
    this file, you can view it online at
    <http://bitbucket.org/ubernostrum/django-registration/src/tip/LICENSE>.

**Why are the forms and models for the default backend not in the default backend?**
    The model and manager used by :ref:`the default backend
    <default-backend>` are in ``registration.models``, and the default
    form class (and various subclasses) are in ``registration.forms``;
    logically, they might be expected to exist in
    ``registration.backends.default``, but there are several reasons
    why that's not such a good idea:

    1. :class:`~registration.models.RegistrationProfile` model keeps the
       minimun information possible, so it's inteded to work for all
       (or almost) situations.

    2. Due to the design of Django's ORM, the ``RegistrationProfile``
       model would end up with an ``app_label`` of ``default``, which
       isn't particularly descriptive and may conflict with other
       applications. By keeping it in ``registration.models``, it
       retains an ``app_label`` of ``registration``, which more
       accurately reflects what it does and is less likely to cause
       problems.

    3. Although the ``RegistrationProfile`` model and the various
       :ref:`form classes <forms>` are used by the default backend,
       they can and are meant to be reused as needed by other
       backend.


Installation and setup
----------------------

**How do I install django-pluggable-registration?**
    Full instructions are available in :ref:`the quick start guide <quickstart>`.

**Do I need to put a copy of django-registration in every project I use it in?**
    No; putting applications in your project directory is a very bad
    habit, and you should stop doing it. If you followed the
    instructions mentioned above, django-registration was installed
    into a location that's on your Python import path, so you'll only
    ever need to add ``registration`` to your ``INSTALLED_APPS``
    setting (in any project, or in any number of projects), and it
    will work.

**Does django-registration come with any sample templates I can use right away?**
    No, for two reasons:

    1. Providing default templates with an application is generally
       hard to impossible, because different sites can have such
       wildly different design and template structure. Any attempt to
       provide templates which would work with all the possibilities
       would probably end up working with none of them.

    2. A number of things in django-registration depend on the
       specific :ref:`registration backend <backend-api>` you use,
       including the variables which end up in template
       contexts. Since django-registration has no way of knowing in
       advance what backend you're going to be using, it also has no
       way of knowing what your templates will need to look like.
    
    Fortunately, however, django-registration has good documentation
    which explains what context variables will be available to
    templates, and so it should be easy for anyone who knows Django's
    template system to create templates which integrate with their own
    site.

**Which are the differences with django-registration?**
    There are two main differences:

    1. django-plugglable-registration **default workflow** quite different.
       Initially user need just provide an email to start registration and
       any other needed information will be taken on activation step; so we
       could say is a creation step. However you can customize this behavior
       getting a more django-registration like workflow.

    2. This is intended to be **backend free**, so just need **plug** your
       activation method/forms, allowing much more flexibility without the
       need of writing a custom backend (even you can still write it).

    3. django-pluggable-registration it's also **model free**, so default
       workflow only needs it's own :class:`~registration.RegistrationProfile`
       and it doesn't depends on :class:`django.contrib.auth.models.User` as
       django-registration default backend does. This may be extremly useful if
       you don't use built-in Django authentication.

    So almost any differnce is intended to cover where django-registration default
    behavior doesn't fit your needs but you don't want/need write a new backend. If
    are going to use built-in Django authentication or need writing a new backend
    you should stay on django-registration.


Configuration
-------------

**Do I need to rewrite the views to change the way they behave?**
    No. There are several ways you can customize behavior without
    making any changes whatsoever:

    * Pass custom arguments -- e.g., to specify forms, template names,
      etc. -- to :ref:`the registration views <views>`.

    * Write a custom :ref:`registration backend <backend-api>` which
      implements the behavior you need, and have the views use your
      backend.

    If none of these are sufficient, your best option is likely to
    simply write your own views; however, it is hoped that the level
    of customization exposed by these options will be sufficient for
    nearly all user-registration workflows.

**How do I pass custom arguments to the views?**
    Part 3 of the official Django tutorial, when it `introduces
    generic views
    <http://docs.djangoproject.com/en/dev/intro/tutorial04/#use-generic-views-less-code-is-better>`_,
    covers the necessary mechanism: simply provide a dictionary of
    keyword arguments in your URLconf.

**Does that mean I should rewrite django-pluggable-registration's default URLconf?**
    No; if you'd like to pass custom arguments to the registration
    views, simply write and include your own URLconf instead of
    including the default one provided with django-pluggable-registration.

**I don't want to write my own URLconf because I don't want to write patterns for all the auth views!**
    You're in luck, then; django-registration provides a URLconf which
    *only* contains the patterns for the auth views, and which you can
    include in your own URLconf anywhere you'd like; it lives at
    ``registration.auth_urls``.

**I don't like the names you've given to the URL patterns!**
    In that case, you should feel free to set up your own URLconf
    which uses the names you want.


Tips and tricks
---------------

**How do I re-send an activation email?**
    Assuming you're using :ref:`the default backend
    <default-backend>`, a `custom admin action
    <http://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/>`_
    is provided for this; in the admin for the
    :class:`~registration.models.RegistrationProfile` model, simply
    click the checkbox for the user(s) you'd like to re-send the email
    for, then select the "Re-send activation emails" action.
