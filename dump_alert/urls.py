"""
Configuration des URLs pour le projet Dump Alert.

Ce fichier définit le ROUTAGE : quelle URL mène à quelle vue.
C'est comme un "standard téléphonique" qui redirige les requêtes.

Structure :
    URL             →  Vue/Action
    /admin/         →  Interface d'administration Django
    /reports/       →  (à venir) Vues de l'application reports
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Liste des routes URL
# Format : path('chemin/', vue, name='nom_unique')
urlpatterns = [
    # Interface d'administration Django
    # Accessible à : http://localhost:8000/admin/
    path('admin/', admin.site.urls),

    # Vues de l'application reports
    # Accessible à : http://localhost:8000/reports/
    path('reports/', include('reports.urls')),
]

# En mode DEBUG : servir les fichiers médias (images uploadées)
# /!\ En production, c'est le serveur web (Nginx/Apache) qui s'en charge
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
