from django.db import migrations


def create_builtin_thumbnail_sizes(apps, schema_editor):
    ThumbnailSize = apps.get_model("profiles", "ThumbnailSize")

    builtin_sizes = [200, 400]
    default_aspect_ratio = 16 / 9
    ThumbnailSize.objects.bulk_create(
        ThumbnailSize(height=height, width=round(height * default_aspect_ratio))
        for height in builtin_sizes
    )


def delete_builtin_thumbnail_sizes(apps, schema_editor):
    ThumbnailSize = apps.get_model("profiles", "ThumbnailSize")
    default_aspect_ratio = 16 / 9
    builtin_heights = [200, 400]
    builtin_widths = list(
        map(lambda x: round(x * default_aspect_ratio), builtin_heights)
    )
    ThumbnailSize.objects.filter(
        height__in=builtin_heights, width__in=builtin_widths
    ).delete()


def create_builtin_subscriptions(apps, schema_editor):
    Subscription = apps.get_model("profiles", "Subscription")
    ThumbnailSize = apps.get_model("profiles", "ThumbnailSize")

    subscription_params = [
        ("Basic", [200], False, False),
        ("Premium", [200, 400], True, False),
        ("Enterprise", [200, 400], True, True),
    ]

    Subscription.objects.bulk_create(
        Subscription(name=name, original_file_access=ofa, expiring_link_option=elo)
        for name, _, ofa, elo in subscription_params
    )

    linked_models = []
    for i, sub_id in enumerate(Subscription.objects.values_list("id", flat=True)):
        for thumb_id in ThumbnailSize.objects.filter(
            height__in=subscription_params[i][1]
        ).values_list("id", flat=True):
            linked_models.append(
                Subscription.thumbnail_sizes.through(
                    subscription_id=sub_id, thumbnailsize_id=thumb_id
                )
            )
    Subscription.thumbnail_sizes.through.objects.bulk_create(linked_models)


def delete_builtin_subscriptions(apps, schema_editor):
    Subscription = apps.get_model("profiles", "Subscription")
    queryset = Subscription.objects.filter(name__in=["Basic", "Premium", "Enterprise"])
    for subscription in queryset:
        subscription.thumbnail_sizes.clear()
    queryset.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_builtin_thumbnail_sizes, reverse_code=delete_builtin_thumbnail_sizes
        ),
        migrations.RunPython(
            create_builtin_subscriptions, reverse_code=delete_builtin_subscriptions
        ),
    ]
