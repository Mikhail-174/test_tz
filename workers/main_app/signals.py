from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Worker, Position

@receiver(post_save, sender=Worker)
def broadcast_worker_created(sender, instance, created, **kwargs):
    if created:
        fn, ln, email = instance.first_name, instance.last_name, instance.email
        print(f"New Worker created: first name({fn}), last name({ln}), email({email})")

