from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du service")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name