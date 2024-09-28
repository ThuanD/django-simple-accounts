from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver

User = get_user_model()


@receiver(models.signals.post_save, sender=User)
def assign_user_permission(sender, instance: User, created: bool, **kwargs):
    if created:
        # Get the content type for the User model
        user_content_type = ContentType.objects.get_for_model(User)

        # Get the specific permissions you want to assign (view, change, etc.)
        view_permission = Permission.objects.get(codename='view_user',
                                                 content_type=user_content_type)
        change_permission = Permission.objects.get(codename='change_user',
                                                   content_type=user_content_type)

        # Assign permissions to the user instance
        instance.user_permissions.add(view_permission, change_permission)
        instance.save()
