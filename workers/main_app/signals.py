from django.dispatch import receiver
from django.db.models.signals import post_save, post_migrate

from django.contrib.auth.models import Permission, Group

from .models import Worker, Position

@receiver(post_save, sender=Worker)
def broadcast_worker_created(sender, instance, created, **kwargs):
    if created:
        fn, ln, email = instance.first_name, instance.last_name, instance.email
        print(f"New Worker created: Worker({fn} {ln}, {email}) | Creator({instance.created_by})")


@receiver(post_migrate)
def create_admin_group(sender, **kwargs):
    if sender.name == "main_app":
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        admin_permissions = ("add_position", "change_position",
                             "delete_position", "view_position",
                             "add_worker", "change_worker",
                             "delete_worker", "view_worker")
        for perm in admin_permissions:
            permission = Permission.objects.get(codename=perm)
            admin_group.permissions.add(permission)
        admin_group.save()
        print("Admin group created with permissions")