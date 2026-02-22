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


class ReportCluster(models.Model):
    """
    Regroupement automatique de signalements proches (≤10m).

    Quand plusieurs personnes signalent le même dépôt, l'imprécision GPS
    crée des points distincts. Ce modèle les regroupe avec un centroïde unique.
    """

    centroid = models.PointField(
        verbose_name="Centroïde",
        help_text="Centre géométrique du cluster",
        srid=4326,
        geography=True,
    )

    report_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de signalements"
    )

    waste_type = models.CharField(
        max_length=20,
        choices=[
            ("green", "Déchets verts"),
            ("household", "Déchets ménagers"),
            ("bulky", "Encombrants"),
            ("building", "Construction"),
            ("chemical", "Déchets chimiques"),
            ("asbestos", "Amiante"),
        ],
        default="green",
        verbose_name="Catégorie de déchets",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Dernière modification"
    )

    class Meta:
        verbose_name = "Cluster"
        verbose_name_plural = "Clusters"
        ordering = ["-report_count"]

    def __str__(self):
        return f"Cluster #{self.id} ({self.report_count} signalement(s))"

    def recalculate_centroid(self):
        """Recalcule le centroïde via moyenne arithmétique des coordonnées.
        ST_Collect ne supporte pas le type geography — on calcule en Python.
        Pour des clusters à ≤10m, la moyenne arithmétique est une très bonne approximation."""
        from django.contrib.gis.geos import Point

        points = list(self.reports.values_list("location", flat=True))
        if points:
            avg_lon = sum(p.x for p in points) / len(points)
            avg_lat = sum(p.y for p in points) / len(points)
            self.centroid = Point(avg_lon, avg_lat, srid=4326)

    def recalculate_waste_type(self):
        """Lit la catégorie de déchets depuis les signalements du cluster (tous identiques)."""
        first_type = self.reports.values_list("type", flat=True).first()
        self.waste_type = first_type if first_type else "green"

    def recalculate(self):
        """Recalcule toutes les métadonnées du cluster."""
        self.report_count = self.reports.count()
        self.recalculate_centroid()
        self.recalculate_waste_type()
        self.save()


class Report(models.Model):
    """
    Modèle représentant un signalement de dépôt sauvage.

    Chaque signalement contient :
    - Une image du dépôt
    - Une description textuelle
    - Une catégorie de déchets
    - Une localisation GPS (PointField)
    - Un statut (en attente, validé, rejeté)
    """

    # Statuts possibles d'un signalement
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"  # Nouveau signalement
        VALIDATED = "validated", "Validé"  # Confirmé par un admin
        REJECTED = "rejected", "Rejeté"  # Faux signalement

    # Catégories de déchets
    class WasteType(models.TextChoices):
        GREEN = "green", "Déchets verts"  # Branches, tontes, feuilles
        HOUSEHOLD = "household", "Déchets ménagers"  # Sacs poubelles, ordures
        BULKY = "bulky", "Encombrants"  # Meubles, électroménager
        BUILDING = "building", "Construction"  # Déchets de chantier
        CHEMICAL = "chemical", "Déchets chimiques"  # Peintures, solvants, huiles
        ASBESTOS = "asbestos", "Amiante"  # Très dangereux - protocole

    # --- Cluster ---
    cluster = models.ForeignKey(
        ReportCluster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
        verbose_name="Cluster",
        help_text="Cluster de signalements proches",
    )

    # --- Informations du signalement ---
    image = models.ImageField(
        upload_to="reports/", verbose_name="Photo", help_text="Photo du dépôt sauvage"
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="Décrivez le dépôt (type de déchets, quantité estimée...)",
    )

    type = models.CharField(
        max_length=20,
        choices=WasteType.choices,
        verbose_name="Catégorie de déchets",
        help_text="Type de déchets déposés",
    )

    # --- Localisation géospatiale ---
    # PointField stocke des coordonnées (longitude, latitude)
    # SRID 4326 = système de coordonnées WGS84 (standard GPS)
    location = models.PointField(
        verbose_name="Localisation",
        help_text="Position GPS du dépôt",
        srid=4326,  # Système de coordonnées WGS84 (standard mondial)
        geography=True,  # Active les calculs de distance en mètres réels
    )

    # --- Statut et dates ---
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Dernière modification"
    )

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ["-created_at"]

    def __str__(self):
        """Représentation textuelle (affichée dans l'admin)."""
        return f"Signalement #{self.id} - {self.get_status_display()}"
