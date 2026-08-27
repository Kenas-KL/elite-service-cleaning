from django.contrib import admin
from django.utils.html import format_html
from .models import CleanerProfile, Availability


class AvailabilityInline(admin.TabularInline):
    """Permet d'ajouter/modifier les disponibilités directement dans la fiche du prestataire"""
    model = Availability
    extra = 1
    ordering = ('day_of_week', 'start_time')


@admin.register(CleanerProfile)
class CleanerProfileAdmin(admin.ModelAdmin):
    # En-têtes des colonnes dans la liste
    list_display = (
        'get_full_name',
        'city',
        'neighborhood',
        'display_age',
        'years_of_experience',
        'status_badge',
        'is_verified',
        'created_at'
    )

    list_editable = ['is_verified',]
    # Filtres latéraux très utiles pour filtrer rapidement sur le terrain
    list_filter = ('status', 'is_verified', 'city', 'services', 'created_at')

    # Barre de recherche (sur le nom, prénom, téléphone et quartier)
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__username',
        'user__phone_number',
        'neighborhood'
    )

    # Actions groupées (ex: Valider 10 prestataires en 1 clic)
    actions = ['approve_cleaners', 'disapprove_cleaners', 'set_available', 'set_busy']

    # Auto-complétion pour les relations ManyToMany et ForeignKeys lourdes
    filter_horizontal = ('services',)
    inlines = [AvailabilityInline]

    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('user', 'date_of_birth', 'address', 'city', 'neighborhood', 'bio')
        }),
        ('Statut Agence & Validation', {
            'fields': ('is_verified', 'status', 'years_of_experience')
        }),
        ('Competences', {
            'fields': ('services',)
        }),
    )

    # --- MÉTHODES D'AFFICHAGE PERSONNALISÉES ---

    @admin.display(description="Nom complet", ordering="user__first_name")
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="Âge")
    def display_age(self, obj):
        return f"{obj.age} ans"

    @admin.display(description="Statut")
    def status_badge(self, obj):
        """Affiche un badge de couleur selon le statut"""
        colors = {
            'AVAILABLE': '#10B981',  # Vert
            'BUSY': '#F59E0B',  # Orange
            'INACTIVE': '#EF4444',  # Rouge
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    # --- ACTIONS GROUPÉES (BATCH ACTIONS) ---

    @admin.action(description="✓ Valider la vérification agence")
    def approve_cleaners(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} prestataire(s) ont été vérifié(s) avec succès.")

    @admin.action(description="✗ Annuler la vérification")
    def disapprove_cleaners(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} prestataire(s) ne sont plus vérifiés.")

    @admin.action(description="Marquer comme Disponible")
    def set_available(self, request, queryset):
        queryset.update(status='AVAILABLE')

    @admin.action(description="Marquer comme Occupé(e)")
    def set_busy(self, request, queryset):
        queryset.update(status='BUSY')


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('cleaner', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'cleaner')
    ordering = ('cleaner', 'day_of_week', 'start_time')