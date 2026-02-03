import os
from django.contrib.auth import get_user_model


def createsuperuser_at_start():
    """ We need this function just to handle create super user issues at docker-compose """

    User = get_user_model()
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "root")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "root")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)