from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from apps.cleaners.models import CleanerProfile
from apps.services.models import Service


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CONFIRMED = 'CONFIRMED', 'Confirmée par l\'agence'
        IN_PROGRESS = 'IN_PROGRESS', 'Ménage en cours'
        COMPLETED = 'COMPLETED', 'Terminée'
        CANCELLED = 'CANCELLED', 'Annulée'

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_client', verbose_name="Client")
    cleaner = models.ForeignKey(CleanerProfile, on_delete=models.CASCADE, related_name='bookings_as_cleaner',
                                verbose_name="Ménagère")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, verbose_name="Service demandé")

    date = models.DateField(verbose_name="Date d'intervention")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")

    location_address = models.CharField(max_length=255, verbose_name="Adresse du lieu d'intervention")
    notes = models.TextField(blank=True, verbose_name="Consignes / Remarques du client")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING,
                              verbose_name="Statut de la demande")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"Réservation #{self.id} - {self.client.username} -> {self.cleaner.user.username} ({self.date})"


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review', verbose_name="Réservation")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (1 à 5)"
    )
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis / Évaluation"
        verbose_name_plural = "Avis & Évaluations"

    def __str__(self):
        return f"Avis {self.rating}/5 - {self.booking.cleaner}"