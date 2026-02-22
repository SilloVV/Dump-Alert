"""
Signaux Django pour le clustering automatique des signalements.

- post_save : à la CRÉATION d'un Report, assigne automatiquement un cluster
- post_delete : quand un Report est supprimé, recalcule ou supprime le cluster
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Report


@receiver(post_save, sender=Report)
def auto_cluster_on_create(sender, instance, created, **kwargs):
    """Assigne un cluster au signalement lors de sa création."""
    if not created:
        return

    from .services import assign_report_to_cluster

    assign_report_to_cluster(instance)


@receiver(post_delete, sender=Report)
def update_cluster_on_delete(sender, instance, **kwargs):
    """Recalcule ou supprime le cluster quand un signalement est supprimé."""
    cluster = instance.cluster
    if cluster is None:
        return

    # Si le cluster n'a plus de signalements, le supprimer
    if cluster.reports.count() == 0:
        cluster.delete()
    else:
        cluster.recalculate()
