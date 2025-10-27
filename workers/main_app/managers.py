from django.utils import timezone
from django.db import models

class IsDeletedQuerySet(models.QuerySet):
    def delete(self, hard_delete=False):
        if hard_delete:
            return super().delete()
        else:
            return self.update(is_deleted=True, deleted_at=timezone.now())

class IsDeletedManager(models.Manager):
    def get_queryset(self):
        return IsDeletedQuerySet(self.model).filter(is_deleted=False)

    def unfiltered(self):
        return IsDeletedQuerySet(self.model)

    def hard_delete(self):
        return self.unfiltered().delete(hard_delete=True)