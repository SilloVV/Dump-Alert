"""
Routes URL de l'application Reports.

Ce fichier définit les URLs spécifiques à l'app reports.
Il sera inclus dans le fichier urls.py principal du projet.
"""

from django.urls import path
from . import views

app_name = "reports"  # Namespace pour éviter les conflits de noms

urlpatterns = [
    # Liste des signalements (tableau) — staff uniquement
    # Accessible à : /reports/
    path("", views.report_list, name="list"),
    # Formulaire public de signalement — accessible sans connexion
    # Accessible à : /reports/signaler/
    path("signaler/", views.create_report, name="create"),
    # Page de confirmation après soumission
    # Accessible à : /reports/merci/
    path("merci/", views.report_success, name="success"),
]
