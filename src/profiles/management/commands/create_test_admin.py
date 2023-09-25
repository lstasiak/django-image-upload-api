from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Create admin user with superuser privileges"

    def handle(self, *args, **options):
        username = "admin"
        password = "admin"
        email = "admin@example.com"
        if not get_user_model().objects.filter(username=username).exists():
            get_user_model().objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser with username "{username}"".'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'User "{username}" already exists. Please choose a different username.'
                )
            )
