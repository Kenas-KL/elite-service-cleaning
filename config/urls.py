"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# Importe tes vues (ajuste le chemin selon l'endroit où tu as sauvegardé le fichier views.py)
# Exemple si tes vues sont dans apps/core/views.py :
# from apps.core import views
from apps.accounts import views

urlpatterns = [
    # Panel d'administration
    path('admin/', admin.site.urls),

    # Pages Publiques
    path('', views.landing_view, name='landing'),
    path('help/', views.help_view, name='help'),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Les 2 sous-espaces cibles
    path('dashboard/prestataire/', views.cleaner_dashboard_view, name='cleaner_dashboard'),
    path('dashboard/client/', views.client_dashboard_view, name='client_dashboard'),

    path('logout/', views.logout_view, name='logout'),
]



# Personnalisation des titres de l'administration
admin.site.site_header = "Elite Cleaning Services Administration"
admin.site.site_title = "Elite Cleaning Admin"
admin.site.index_title = "Gestion Opérationnelle de l'Agence"

# Indispensable pour afficher les Avatars (images uploadées) en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)