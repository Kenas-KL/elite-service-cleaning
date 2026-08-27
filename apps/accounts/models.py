
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        CLEANER = 'CLEANER', 'Femme de ménage'
        ADMIN = 'ADMIN', 'Administrateur / Agence'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de téléphone")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def is_cleaner(self):
        return self.role == self.Role.CLEANER

    def is_client(self):
        return self.role == self.Role.CLIENT