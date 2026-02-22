"""
Service de clustering des signalements.

Regroupe automatiquement les signalements situés à ≤10m les uns des autres
dans un cluster unique avec un centroïde recalculé.
"""

from django.contrib.gis.measure import D
from django.db import transaction

from .models import Report, ReportCluster


def merge_clusters(clusters):
    """
    Fusionne plusieurs clusters en un seul (le plus ancien).

    Tous les signalements des clusters secondaires sont rattachés
    au cluster principal, puis les clusters vides sont supprimés.
    """
    # Garder le plus ancien comme cluster principal
    ordered = sorted(clusters, key=lambda c: c.created_at)
    main_cluster = ordered[0]
    others = ordered[1:]

    # Rattacher tous les signalements au cluster principal
    for cluster in others:
        cluster.reports.update(cluster=main_cluster)

    # Supprimer les clusters désormais vides
    ReportCluster.objects.filter(pk__in=[c.pk for c in others]).delete()

    return main_cluster


def assign_report_to_cluster(report):
    """
    Assigne un signalement au bon cluster (ou en crée un nouveau).

    Logique :
    - 0 cluster proche → créer un nouveau cluster
    - 1 cluster proche → ajouter au cluster existant
    - 2+ clusters proches → fusionner les clusters, puis ajouter
    """
    with transaction.atomic():
        # 1. Verrouiller les clusters proches (≤10m) pour éviter les race conditions
        nearby = list(
            ReportCluster.objects.select_for_update().filter(
                centroid__dwithin=(report.location, D(m=10)),
                waste_type=report.type,
            )
        )

        if len(nearby) == 0:
            # Aucun cluster proche → en créer un nouveau
            cluster = ReportCluster.objects.create(
                centroid=report.location,
                report_count=1,
                waste_type=report.type,
            )

        elif len(nearby) == 1:
            # Un seul cluster proche → le rejoindre
            cluster = nearby[0]

        else:
            # 2+ clusters proches → les fusionner en un seul
            cluster = merge_clusters(nearby)

        # Rattacher le report au cluster SANS .save() (évite de re-déclencher post_save)
        Report.objects.filter(pk=report.pk).update(cluster=cluster)

        # Recalculer le centroïde et les métadonnées
        cluster.recalculate()
