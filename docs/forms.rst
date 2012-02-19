.. _forms:
.. module:: registration.forms

Forms for user registration
===========================

Several form classes are provided with django-registration as base classes
to be inherited. These forms were designed with django-pluggable-registration's
:ref:`default backend <default-backend>` in mind, but may also be useful in other
situations.


.. class:: RegistrationForm

   A simple form for registering an account by email. Has the following fields,
   all of which are required:

   ``email``
      The email address to use for the new account. This is
      represented as a text input which accepts email addresses up to
      75 characters in length.

   In addition the ``clean_email`` method is defined as abstract method,
   so :class:`~RegistrationForm`` can't be use by itself but must be
   inherited, providing the right validation.


.. class:: ActivationForm

   A subclass of :class:`django.forms.Form` to be used at activation time,
   required field:

   ``password1``
      The password to use for the new account. This represented as a
      password input (``input type="password"`` in the rendered HTML).

   ``password2``
      The password to use for the new account. This represented as a

   An abstract method, ``clean`` is provided for convenience, so subclasses
   must define it's own validation. This class by default only provides
   password fields, so subclasses can add any other extra field.
