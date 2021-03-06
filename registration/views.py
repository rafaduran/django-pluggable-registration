"""
Views which allow users to create and activate accounts.

"""


from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from registration.backends import get_backend

import logging

LOG = logging.getLogger(__name__)

def activate(request, backend, form_class=None, activation_method=None,
             template_name='registration/activate.html',
             success_url=None, extra_context=None, **kwargs):
    """
    Activate a user's account.

    The actual activation of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    the backend's ``activate()`` method will be called, passing any
    keyword arguments captured from the URL, the request and the instance
    of the form gotten from ``get_activation_form`` backend (if any). If
    activation form is defined ``activate`` will be called only after form
    is valid. Once ``activate`` is called,it will be assumed to return a
    two-tuple (``User``, ``None``) if activation was successful, or
    (falsy_value, error_message) value if not.

    Upon successful activation, the backend's
    ``post_activation_redirect()`` method will be called, passing the
    ``HttpRequest`` and the activated ``User`` to determine the URL to
    redirect the user to. To override this, pass the argument
    ``success_url`` (see below).

    On unsuccessful activation, will render the template
    ``registration/activate.html`` to display an error message; to
    override thise, pass the argument ``template_name`` (see below).

    **Arguments**

    ``backend``
        The dotted Python import path to the backend class to
        use. Required.

    ``form_class``
        The activation form class.

    ``activation_method``
        The callback actually performing the activation. Default value is
        ``None``, so it will be taken from ``ACTIVATION_METHOD`` setting.

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context. Optional.

    ``success_url``
        The name of a URL pattern to redirect to on successful
        acivation. This is optional; if not specified, this will be
        obtained by calling the backend's
        ``post_activation_redirect()`` method.
    
    ``template_name``
        A custom template to use. This is optional; if not specified,
        this will default to ``registration/activate.html``.

    ``\*\*kwargs``
        Any keyword arguments captured from the URL, such as an
        activation key, which will be passed to the backend's
        ``activate()`` method.
    
    **Context:**
    
    The context will be populated from the keyword arguments captured
    in the URL, and any extra variables supplied in the
    ``extra_context`` argument (see above). In addition if a activation
    form (see aboce again) is defined will be added ``form`` to context
    containing current instance.
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    backend = get_backend(backend, activation_method=activation_method,
            **kwargs)
    if form_class is None:
        activation_form = backend.get_activation_form_class(request)
    if request.method == 'POST':
        form = activation_form and activation_form(data=request.POST,
                files=request.FILES)
        kwargs['form'] = form
        if not form or form.is_valid():
            account, errors = backend.activate(request, **kwargs)

            if account:
                if success_url is None:
                    to, args, kwargs = backend.post_activation_redirect(request,
                            account)
                    return redirect(to, *args, **kwargs)
                else:
                    return redirect(success_url)
            if errors:
                form._errors['__all__'] = errors

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    if activation_form is not None and 'form' not in kwargs:
        kwargs['form'] = activation_form()

    return render_to_response(template_name,
                            kwargs,
                            context_instance=context)


def register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='registration/registration_form.html',
             extra_context=None, **kwargs):
    """
    Allow a new user to register an account.

    The actual registration of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    it will be used as follows:

    1. The backend's ``registration_allowed()`` method will be called,
       passing the ``HttpRequest``, to determine whether registration
       of an account is to be allowed; if not, a redirect is issued to
       the view corresponding to the named URL pattern
       ``registration_disallowed``. To override this, see the list of
       optional arguments for this view (below).

    2. The form to use for account registration will be obtained by
       calling the backend's ``get_form_class()`` method, passing the
       ``HttpRequest``. To override this, see the list of optional
       arguments for this view (below).

    3. If valid, the form's ``cleaned_data`` will be passed (as
       keyword arguments, and along with the ``HttpRequest``) to the
       backend's ``register()`` method, which should return the new
       ``RegistrationProfile`` object.

    4. Upon successful registration, the backend's
       ``post_registration_redirect()`` method will be called, passing
       the ``HttpRequest`` and the new ``RegistrationProfile``, to determine
       the URL to redirect the user to. To override this, see the list of
       optional arguments for this view (below).
    
    **Required arguments**
    
    None.
    
    **Optional arguments**

    ``backend``
        The dotted Python import path to the backend class to use.

    ``disallowed_url``
        URL to redirect to if registration is not permitted for the
        current ``HttpRequest``. Must be a value which can legally be
        passed to ``django.shortcuts.redirect``. If not supplied, this
        will be whatever URL corresponds to the named URL pattern
        ``registration_disallowed``.
    
    ``form_class``
        The form class to use for registration. If not supplied, this
        will be retrieved from the registration backend.
    
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``success_url``
        URL to redirect to after successful registration. Must be a
        value which can legally be passed to
        ``django.shortcuts.redirect``. If not supplied, this will be
        retrieved from the registration backend.
    
    ``template_name``
        A custom template to use. If not supplied, this will default
        to ``registration/registration_form.html``.
    
    **Context:**
    
    ``form``
        The registration form.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    backend = get_backend(backend, **kwargs)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_profile = backend.register(request, **form.cleaned_data)
            if success_url is None:
                to, args, kwargs = backend.post_registration_redirect(request,
                        new_profile)
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)
    else:
        form = form_class()
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)
