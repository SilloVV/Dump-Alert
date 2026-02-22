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
from django.contrib import messages
from leaflet.admin import LeafletGeoAdmin  # Admin avec carte interactive

from .models import Report, ReportCluster


# =============================================================================
# ACTIONS ADMIN (validation/rejet en masse)
# =============================================================================
@admin.action(description="Valider les signalements sélectionnés")
def valider_signalements(modeladmin, request, queryset):
    """Marque les signalements sélectionnés comme validés."""
    count = queryset.update(status=Report.Status.VALIDATED)
    messages.success(request, f"{count} signalement(s) validé(s).")


@admin.action(description="Rejeter les signalements sélectionnés")
def rejeter_signalements(modeladmin, request, queryset):
    """Marque les signalements sélectionnés comme rejetés."""
    count = queryset.update(status=Report.Status.REJECTED)
    messages.warning(request, f"{count} signalement(s) rejeté(s).")


@admin.action(description="Remettre en attente")
def remettre_en_attente(modeladmin, request, queryset):
    """Remet les signalements sélectionnés en attente."""
    count = queryset.update(status=Report.Status.PENDING)
    messages.info(request, f"{count} signalement(s) remis en attente.")


# =============================================================================
# ADMIN CLUSTERS
# =============================================================================
class ReportInline(admin.TabularInline):
    """Affiche les signalements d'un cluster en ligne."""

    model = Report
    extra = 0
    readonly_fields = ["id", "description", "type", "status", "created_at"]
    fields = ["id", "description", "type", "status", "created_at"]
    can_delete = False
    show_change_link = True


@admin.action(description="Recalculer les clusters sélectionnés")
def recalculer_clusters(modeladmin, request, queryset):
    """Recalcule centroïde et métadonnées des clusters sélectionnés."""
    for cluster in queryset:
        cluster.recalculate()
    messages.success(request, f"{queryset.count()} cluster(s) recalculé(s).")


@admin.register(ReportCluster)
class ReportClusterAdmin(LeafletGeoAdmin):
    """Admin des clusters avec carte du centroïde."""

    list_display = ["id", "report_count", "max_waste_type", "created_at", "updated_at"]
    list_filter = ["max_waste_type"]
    readonly_fields = ["report_count", "max_waste_type", "created_at", "updated_at"]
    inlines = [ReportInline]
    actions = [recalculer_clusters]


@admin.register(Report)  # Enregistre le modèle dans l'admin
class ReportAdmin(LeafletGeoAdmin):
    """
    Configuration de l'interface admin pour les signalements.

    LeafletGeoAdmin ajoute automatiquement une carte interactive
    pour les champs géospatiaux (PointField, PolygonField, etc.)
    """

    # =========================================================================
    # FICHIERS JS/CSS SUPPLÉMENTAIRES
    # =========================================================================
    class Media:
        # Le plugin Geocoder est chargé dynamiquement dans leaflet_geocoder.js
        # pour éviter les problèmes d'ordre de chargement avec Leaflet
        js = ("reports/js/leaflet_geocoder.js",)

    # =========================================================================
    # ACTIONS EN MASSE
    # =========================================================================
    actions = [valider_signalements, rejeter_signalements, remettre_en_attente]

    # =========================================================================
    # AFFICHAGE EN LISTE
    # =========================================================================
    # Colonnes affichées dans la liste des signalements
    list_display = [
        "id",
        "description_courte",  # Méthode personnalisée (voir plus bas)
        "type",
        "status",
        "cluster_display",  # Méthode sécurisée (gère les références orphelines)
        "created_at",
    ]

    # Colonnes cliquables pour voir les détails
    list_display_links = ["id", "description_courte"]

    # Filtres dans la barre latérale droite
    list_filter = [
        "status",  # Filtrer par : En attente / Validé / Rejeté
        "type",  # Filtrer par catégorie de déchets
        "created_at",  # Filtrer par date
    ]

    # Champ de recherche (recherche dans ces champs)
    search_fields = ["description", "type"]

    # Tri par défaut (- = décroissant)
    ordering = ["-created_at"]

    # Pré-charge les clusters en une seule requête SQL (évite N+1 et DoesNotExist)
    list_select_related = ["cluster"]

    # =========================================================================
    # FORMULAIRE D'ÉDITION
    # =========================================================================
    # Champs en lecture seule (non modifiables)
    readonly_fields = ["created_at", "updated_at", "cluster"]

    # Organisation des champs dans le formulaire
    fieldsets = [
        ("Signalement", {"fields": ["image", "description", "type"]}),
        (
            "Localisation",
            {
                "fields": ["location"],  # Affiche la carte Leaflet
                "description": "Cliquez sur la carte pour placer le marqueur",
            },
        ),
        ("Statut", {"fields": ["status"]}),
        ("Cluster", {"fields": ["cluster"], "classes": ["collapse"]}),
        (
            "Métadonnées",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],  # Section repliable
            },
        ),
    ]

    # =========================================================================
    # MÉTHODES PERSONNALISÉES
    # =========================================================================
    @admin.display(description="Description")
    def description_courte(self, obj):
        """Affiche les 50 premiers caractères de la description."""
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description

    @admin.display(description="Cluster")
    def cluster_display(self, obj):
        """Affiche le cluster en gérant les références orphelines."""
        try:
            if obj.cluster_id is None:
                return "—"
            return obj.cluster  # peut lever DoesNotExist si orphelin
        except ReportCluster.DoesNotExist:
            # Référence corrompue : on la nettoie silencieusement
            Report.objects.filter(pk=obj.pk).update(cluster=None)
            return "⚠ nettoyé"
