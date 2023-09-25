from django.contrib.auth.forms import UserCreationForm

from src.profiles.models import Profile


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Profile
        fields = UserCreationForm.Meta.fields
