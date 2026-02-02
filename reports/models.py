"""
Modèles de données pour l'application Reports.

Un MODÈLE = une table dans la base de données.
Chaque attribut de classe = une colonne dans la table.

Django crée automatiquement :
- La table SQL correspondante (via migrations)
- Un ID auto-incrémenté
- Les méthodes CRUD (Create, Read, Update, Delete)

Exemple d'utilisation :
    # Créer un signalement
    report = Report(description="Déchets sur le bord de la route", ...)
    report.save()

    # Récupérer tous les signalements
    Report.objects.all()

    # Filtrer
    Report.objects.filter(status='pending')
"""

from django.contrib.gis.db import models  # Modèles GeoDjango (avec champs spatiaux)


class Report(models.Model):
    """
    Modèle représentant un signalement de dépôt sauvage.

    Chaque signalement contient :
    - Une image du dépôt
    - Une description textuelle
    - Un niveau de dangerosité
    - Une localisation GPS (PointField)
    - Un statut (en attente, validé, rejeté)
    """



    # Statuts possibles d'un signalement
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'       # Nouveau signalement
        VALIDATED = 'validated', 'Validé'       # Confirmé par un admin
        REJECTED = 'rejected', 'Rejeté'         # Faux signalement

    # Niveaux de dangerosité (du moins au plus dangereux)
    class DangerLevel(models.TextChoices):
        GREEN = 'green', 'Déchets verts'            # Branches, tontes, feuilles
        HOUSEHOLD = 'household', 'Déchets ménagers' # Sacs poubelles, ordures
        BULKY = 'bulky', 'Encombrants'              # Meubles, électroménager
        CHEMICAL = 'chemical', 'Déchets chimiques'  # Peintures, solvants, huiles
        ASBESTOS = 'asbestos', 'Amiante'            # Très dangereux - protocole spécial


    # --- Informations du signalement ---
    image = models.ImageField(
        upload_to='reports/',       # Dossier : media/reports/
        verbose_name='Photo',
        help_text='Photo du dépôt sauvage'
    )

    description = models.TextField(
        verbose_name='Description',
        help_text='Décrivez le dépôt (type de déchets, quantité estimée...)'
    )

    danger_level = models.CharField(
        max_length=20,
        choices=DangerLevel.choices,
        verbose_name='Niveau de dangerosité',
        help_text='Type de déchets et danger associé'
    )

    # --- Localisation géospatiale ---
    # PointField stocke des coordonnées (longitude, latitude)
    # SRID 4326 = système de coordonnées WGS84 (standard GPS)
    location = models.PointField(
        verbose_name='Localisation',
        help_text='Position GPS du dépôt',
        srid=4326  # Système de coordonnées WGS84 (standard mondial)
    )

    # --- Statut et dates ---
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Statut'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,  # Rempli automatiquement à la création
        verbose_name='Date de création'
    )

    updated_at = models.DateTimeField(
        auto_now=True,  # Mis à jour automatiquement à chaque sauvegarde
        verbose_name='Dernière modification'
    )

    # =========================================================================
    # MÉTADONNÉES DU MODÈLE
    # =========================================================================
    class Meta:
        verbose_name = 'Signalement'
        verbose_name_plural = 'Signalements'
        ordering = ['-created_at']  # Plus récents en premier

    def __str__(self):
        """Représentation textuelle (affichée dans l'admin)."""
        return f"Signalement #{self.id} - {self.get_status_display()}"
