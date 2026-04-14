
from django.db import models
from django.contrib.auth.models import User


class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)  # Masalan: Google, AWS
    url = models.URLField(max_length=200)
    username = models.CharField(max_length=100)

    # MUHIM: Bu maydon shifrlangan tekstni saqlaydi (Binary emas, TextField ma'qul)
    encrypted_password = models.TextField()

    notes = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_name} - {self.username}"