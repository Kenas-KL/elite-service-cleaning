import io
import os

from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from datetime import date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil (optionnel, mais pratique pour les âges)
from PIL import Image


User = get_user_model()

# Import de tes modèles
from apps.accounts.models import User
from apps.cleaners.models import CleanerProfile
from apps.services.models import Service

def landing_view(request):
    # Charge uniquement les ménagères vérifiées et actives
    cleaners = (
        CleanerProfile.objects.filter(is_verified=True, status="AVAILABLE")
        .select_related("user")
        .prefetch_related("services")
        .order_by("-created_at")
    )

    # Récupération des filtres depuis la requête GET
    city_query = request.GET.get("city", "").strip()
    age_query = request.GET.get("age", "").strip()
    service_query = request.GET.get("service", "").strip()

    # Filtre par Ville ou Quartier
    if city_query:
        cleaners = cleaners.filter(
            Q(city__icontains=city_query)
            | Q(neighborhood__icontains=city_query)
        )

    # Filtre par Service sélectionné
    if service_query:
        cleaners = cleaners.filter(services__id=service_query)

    # Filtre par Tranche d'âge
    if age_query:
        today = date.today()

        def safe_date(year, month, day):
            try:
                return date(year, month, day)
            except ValueError:
                return date(year, month, day - 1)

        if age_query == "18-25":
            min_d = safe_date(today.year - 25, today.month, today.day)
            max_d = safe_date(today.year - 18, today.month, today.day)
            cleaners = cleaners.filter(date_of_birth__range=(min_d, max_d))
        elif age_query == "26-35":
            min_d = safe_date(today.year - 35, today.month, today.day)
            max_d = safe_date(today.year - 26, today.month, today.day)
            cleaners = cleaners.filter(date_of_birth__range=(min_d, max_d))
        elif age_query == "36+":
            max_d = safe_date(today.year - 36, today.month, today.day)
            cleaners = cleaners.filter(date_of_birth__lte=max_d)

    context = {
        "cleaners": cleaners.distinct(),
        "services": Service.objects.all(),
        "selected_city": city_query,
        "selected_age": age_query,
        "selected_service": service_query,
    }

    return render(request, "landing.html", context)
# ------------------------------------------------------------------
# 2. PAGE D'AIDE (FAQ)
# ------------------------------------------------------------------
def help_view(request):
    return render(request, 'help.html')


# ------------------------------------------------------------------
# 3. INSCRIPTION (CLIENT OU MÉNAGÈRE)
# ------------------------------------------------------------------
def register_view(request):
    # Si l'utilisateur est déjà connecté, on le renvoie à l'accueil
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        role = request.POST.get('role', 'client')  # 'client' par défaut
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password_')

        if password != confirm_password:
            messages.error(request, "les mots de passes ne correspondent pas.")
            return render(request, "register.html")



        # Pour générer un username unique basé sur le prénom/nom
        username = f"{first_name.lower()}.{last_name.lower()}".replace(" ", "")

        # Vérifier si l'utilisateur existe déjà (simplifié)
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce compte existe déjà. Veuillez vous connecter.")
            return render(request, "register.html")

        # 1. Création de l'utilisateur de base
        user_role = User.Role.CLEANER if role == 'cleaner' else User.Role.CLIENT
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=user_role
        )

        # 2. Si c'est une ménagère, on crée aussi son profil (non vérifié par défaut)
        if user_role == User.Role.CLEANER:
            date_of_birth = request.POST.get('date_of_birth')
            neighborhood = request.POST.get('neighborhood')

            CleanerProfile.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                neighborhood=neighborhood,
                city='Kalemie',  # Ville par défaut pour le lancement
                is_verified=False,
                status='AVAILABLE'
            )
            messages.success(request, "Compte prestataire créé ! Notre agence va vous contacter.")
        else:
            messages.success(request, "Compte client créé avec succès !")

        # Connexion automatique après inscription
        login(request, user)
        return redirect('dashboard')

    return render(request, 'register.html')


# ------------------------------------------------------------------
# 4. CONNEXION
# ------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirection dynamique : Si admin va au dashboard, sinon accueil
            if user.is_staff:
                return redirect('/admin/')
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'login.html')


@login_required
def dashboard_view(request):
    """
    Point d'entrée unique /dashboard/ : Redirige dynamiquement
    selon le rôle de l'utilisateur.
    """
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')

    if request.user.role == User.Role.CLEANER:
        return redirect('cleaner_dashboard')

    return redirect('client_dashboard')


# ------------------------------------------------------------------
# ESPACE PRESTATAIRE (MÉNAGÈRE)
# ------------------------------------------------------------------



def convert_image_to_webp(image_file, max_size=(500, 500)):
    """Redimensionne et convertit n'importe quelle image envoyée au format WebP ultra-léger."""
    img = Image.open(image_file)

    # Conversion en RGB si l'image originale est en RGBA (ex: PNG transparent)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Redimensionnement proportionnel (Ex: max 500x500 px pour un avatar)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Sauvegarde en mémoire au format WebP avec compression optimale (qualité 80%)
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=80, optimize=True)

    # Générer un nom de fichier unique au format .webp
    base_name = os.path.splitext(image_file.name)[0]
    file_name = f"{base_name}.webp"

    return ContentFile(buffer.getvalue(), name=file_name)


@login_required
def cleaner_dashboard_view(request):
    if request.user.role != User.Role.CLEANER:
        messages.error(request, "Accès refusé à l'espace prestataire.")
        return redirect("dashboard")

    profile, _ = CleanerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        status = request.POST.get("status")
        neighborhood = request.POST.get("neighborhood")
        avatar_file = request.FILES.get("avatar")

        # 1. Mise à jour du Statut & Quartier
        if status in ["AVAILABLE", "BUSY", "UNAVAILABLE"]:
            profile.status = status
        if neighborhood is not None:
            profile.neighborhood = neighborhood.strip()
        profile.save()

        # 2. Traitement et conversion de la photo en WebP s'il y en a une nouvelle
        if avatar_file:
            try:
                webp_avatar = convert_image_to_webp(avatar_file)
                # Supprimer l'ancien avatar du stockage s'il existait
                if request.user.avatar:
                    request.user.avatar.delete(save=False)

                request.user.avatar.save(
                    webp_avatar.name, webp_avatar, save=True
                )
            except Exception as e:
                messages.error(
                    request,
                    "Erreur lors du traitement de l'image. Veuillez recompiler une image valide.",
                )
                return redirect("cleaner_dashboard")

        messages.success(request, "Profil mis à jour avec succès.")
        return redirect("cleaner_dashboard")

    return render(request, "cleaner/dashboard.html", {"profile": profile})

# ------------------------------------------------------------------
# ESPACE CLIENT
# ------------------------------------------------------------------
@login_required
def client_dashboard_view(request):
    if request.user.role != User.Role.CLIENT:
        messages.error(request, "Accès refusé à l'espace client.")
        return redirect('dashboard')

    # Logique pour récupérer les réservations ou favoris du client
    return render(request, 'client/dashboard.html')


# ------------------------------------------------------------------
# 5. DÉCONNEXION
# ------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('landing')