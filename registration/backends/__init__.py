from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

# Python 2.7 has an importlib with import_module; for older Pythons,
# Django's bundled copy provides it.
try: # pragma: no cover
    from importlib import import_module # pragma: no cover
except ImportError: # pragma: no cover
    from django.utils.importlib import import_module # pragma: no cover

def get_object(path):
    """
    Helper method in order to import an object, given the dotted Python
    path (as a string).
    """
    if path is None:
        return None
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured("Error loading module {0}:{1}".format(
            module, e))
    try:
        obj = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '%s' does not define an attribute"
            " backend '%s'".format(module, attr))
    return obj

def get_backend(path, **kwargs):
    """
    Return an instance of a registration backend, given the dotted
    Python import path (as a string) to the backend class; in addition
    ``activation_method`` must be passed into ``kwargs`` or gotten from
    'ACTIVATION_METHOD' setting, otherwise
    ``django.core.exceptions.ImproperlyConfigured`` is raised.
    'REGISTRATION_FORM' and 'ACTIVATION_FORM' are gotten from
    settings and if defined, taking ``None`` by default. Finally **kwargs
    is specified in order to be able to pass any information to the given
    backend.

    If the backend cannot be located (e.g., because no such module
    exists, or because the module does not contain a class of the
    appropriate name), ``django.core.exceptions.ImproperlyConfigured``
    is raised.
    """
    backend = get_object(path)
    try:
        activation_method = kwargs.get('activation_method', None) or\
            get_object(getattr(settings, 'ACTIVATION_METHOD'))
    except AttributeError:
        raise ImproperlyConfigured("You didn't provide an 'ACTIVATION_METHOD'")
    registration_form=get_object(getattr(settings, 'REGISTRATION_FORM', None))
    activation_form=get_object(getattr(settings, 'ACTIVATION_FORM', None))
    # Adding required settings to kwargs
    kwargs.update({'activation_method': activation_method, 'registration_form':
        registration_form, 'activation_form': activation_form})
    return backend(**kwargs)
