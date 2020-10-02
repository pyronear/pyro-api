import uuid
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"{self.username}"
