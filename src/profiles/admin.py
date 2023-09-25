from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from src.profiles.forms import CustomUserCreationForm
from src.profiles.models import Profile, Subscription, ThumbnailSize


@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = Profile
    list_display = [
        "username",
        "subscription",
        "email",
        "is_staff",
    ]
    list_display_links = ["username"]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("subscription",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("subscription",)}),)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(ThumbnailSize)
class ThumbnailSizeAdmin(admin.ModelAdmin):
    pass
