from django.db import models
from datetime import date
from apps.accounts.models import User
from apps.services.models import Service


class CleanerProfile(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Disponible'
        BUSY = 'BUSY', 'Occupée'
        INACTIVE = 'INACTIVE', 'Inactive / Suspendue'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cleaner_profile',
                                verbose_name="Utilisateur")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    address = models.CharField(max_length=255, verbose_name="Adresse de résidence")
    city = models.CharField(max_length=100, default='Kalemie', verbose_name="Ville")
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name="Quartier / Avenue")
    bio = models.TextField(blank=True, verbose_name="Présentation & Expériences")
    years_of_experience = models.PositiveIntegerField(default=0, verbose_name="Années d'expérience")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE, verbose_name="Statut")
    is_verified = models.BooleanField(default=False, verbose_name="Vérifiée par l'agence")
    services = models.ManyToManyField(Service, related_name='cleaners', blank=True, verbose_name="Services maîtrisés")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Ménagère"
        verbose_name_plural = "Profils Ménagères"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username


class Availability(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Lundi'
        TUESDAY = 2, 'Mardi'
        WEDNESDAY = 3, 'Mercredi'
        THURSDAY = 4, 'Jeudi'
        FRIDAY = 5, 'Vendredi'
        SATURDAY = 6, 'Samedi'
        SUNDAY = 7, 'Dimanche'

    cleaner = models.ForeignKey(CleanerProfile, on_delete=models.CASCADE, related_name='availabilities',
                                verbose_name="Ménagère")
    day_of_week = models.IntegerField(choices=DayOfWeek.choices, verbose_name="Jour de la semaine")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")

    class Meta:
        verbose_name = "Disponibilité"
        verbose_name_plural = "Disponibilités"
        unique_together = ('cleaner', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.cleaner} - {self.get_day_of_week_display()} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"