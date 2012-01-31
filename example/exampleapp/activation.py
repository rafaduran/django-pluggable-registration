from django.contrib.auth.models import User
import logging

LOG = logging.getLogger(__name__)

def activate(request, activation_profile, form):
    if activation_profile:
        LOG.debug(form.data)
        user = User(email=activation_profile.email,
            username=form.data['username'], password=form.data['password1'])
        user.save()
        return user, None
    return False, u"Activation key not found/expired"

