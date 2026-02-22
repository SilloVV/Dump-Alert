"""
Commande de management pour reconstruire tous les clusters.

Usage : python manage.py recluster_reports

Utile après un bulk_create ou pour corriger des clusters incohérents.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from reports.models import Report, ReportCluster
from reports.services import assign_report_to_cluster


class Command(BaseCommand):
    help = "Supprime tous les clusters et les reconstruit à partir des signalements existants."

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1. Détacher tous les signalements de leur cluster
            count = Report.objects.filter(cluster__isnull=False).update(cluster=None)
            self.stdout.write(f"  {count} signalement(s) détaché(s)")

            # 2. Supprimer tous les clusters
            deleted, _ = ReportCluster.objects.all().delete()
            self.stdout.write(f"  {deleted} cluster(s) supprimé(s)")

        # 3. Recréer les clusters un par un (hors transaction pour les signaux)
        reports = Report.objects.order_by("created_at")
        total = reports.count()

        for i, report in enumerate(reports, 1):
            assign_report_to_cluster(report)
            if i % 50 == 0:
                self.stdout.write(f"  {i}/{total} signalements traités...")

        cluster_count = ReportCluster.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Terminé : {total} signalement(s) → {cluster_count} cluster(s)"
            )
        )
