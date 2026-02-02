"""
Configuration de l'interface d'administration pour Reports.

L'ADMIN Django permet de :
- Visualiser et modifier les données en base
- Valider/rejeter les signalements
- Voir les signalements sur une carte (grâce à django-leaflet)

Pour accéder à l'admin : http://localhost:8000/admin/
(nécessite un superutilisateur : python manage.py createsuperuser)
"""

from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin  # Admin avec carte interactive

from .models import Report


@admin.register(Report)  # Enregistre le modèle dans l'admin
class ReportAdmin(LeafletGeoAdmin):
    """
    Configuration de l'interface admin pour les signalements.

    LeafletGeoAdmin ajoute automatiquement une carte interactive
    pour les champs géospatiaux (PointField, PolygonField, etc.)
    """

    # =========================================================================
    # AFFICHAGE EN LISTE
    # =========================================================================
    # Colonnes affichées dans la liste des signalements
    list_display = [
        'id',
        'description_courte',  # Méthode personnalisée (voir plus bas)
        'danger_level',
        'status',
        'created_at',
    ]

    # Filtres dans la barre latérale droite
    list_filter = [
        'status',        # Filtrer par : En attente / Validé / Rejeté
        'danger_level',  # Filtrer par type de déchets
        'created_at',    # Filtrer par date
    ]

    # Champ de recherche (recherche dans ces champs)
    search_fields = ['description']

    # Tri par défaut (- = décroissant)
    ordering = ['-created_at']

    # =========================================================================
    # FORMULAIRE D'ÉDITION
    # =========================================================================
    # Champs en lecture seule (non modifiables)
    readonly_fields = ['created_at', 'updated_at']

    # Organisation des champs dans le formulaire
    fieldsets = [
        ('Signalement', {
            'fields': ['image', 'description', 'danger_level']
        }),
        ('Localisation', {
            'fields': ['location'],  # Affiche la carte Leaflet
            'description': 'Cliquez sur la carte pour placer le marqueur'
        }),
        ('Statut', {
            'fields': ['status']
        }),
        ('Métadonnées', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']  # Section repliable
        }),
    ]

    # =========================================================================
    # MÉTHODES PERSONNALISÉES
    # =========================================================================
    @admin.display(description='Description')
    def description_courte(self, obj):
        """Affiche les 50 premiers caractères de la description."""
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description
