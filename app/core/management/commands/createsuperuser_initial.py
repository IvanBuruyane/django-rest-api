from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    """
    Create a superuser
    Example:
        manage.py createsuperuser_initial
    """

    def handle(self, *args, **options):
        User = get_user_model()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")

        User.objects.create_superuser(
            password=password,
            email=email,
        )

        self.stdout.write(f'Local user "{email}" was created')
