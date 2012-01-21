from django.contrib.auth.models import User

def activate(request, form, activation_profile):
    if activation_profile:
        import logging; logging.error(form)
        user = User(email=activation_profile.email,
            username=form.data['username'], password=form.data['password1'])
        user.save()
        return user
    return False

